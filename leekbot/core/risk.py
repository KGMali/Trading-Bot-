from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from typing import Deque, Dict, List, Protocol
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ..monitor import monitor
from .logging import get_logger

logger = get_logger(__name__)


class BrokerInterface(Protocol):
    def cancel_open_orders(self, account: str) -> None: ...

    def flatten_positions(self, account: str) -> None: ...


@dataclass(slots=True)
class RiskRuleConfig:
    max_daily_loss_pct: float | None = None
    max_pos_value_pct: float | None = None
    max_orders_per_min: int | None = None
    max_positions: int | None = None
    contracts_per_symbol: int | None = None
    max_leverage: float | None = None
    hard_stop_pct: float | None = None
    allow_short_vol: bool | None = None
    max_day_trades: int | None = None
    max_intraday_loss_pct: float | None = None
    flatten_at_close: bool | None = None
    day_trade_close_time: str | None = None
    day_trade_timezone: str | None = None


@dataclass
class AccountState:
    balance: float
    equity: float
    positions: List[Dict[str, float]]
    timestamp: datetime | None = None


class RiskManager:
    def __init__(self, account: str, rules: RiskRuleConfig, broker: BrokerInterface) -> None:
        self.account = account
        self.rules = rules
        self.broker = broker
        self.order_timestamps: Deque[datetime] = deque(maxlen=1000)
        self.kill_switch = False
        self.session_date: date | None = None
        self.trade_count: int = 0
        self._intraday_peak_equity: float | None = None
        self._flattened_today = False
        self._close_time: time | None = None
        self._tz: ZoneInfo | None = None
        if self.rules.day_trade_close_time:
            try:
                self._close_time = datetime.strptime(
                    self.rules.day_trade_close_time, "%H:%M"
                ).time()
            except ValueError:
                logger.warning(
                    "Invalid close time string provided",
                    account=account,
                    close_time=self.rules.day_trade_close_time,
                )
        if self.rules.day_trade_timezone:
            try:
                self._tz = ZoneInfo(self.rules.day_trade_timezone)
            except ZoneInfoNotFoundError:
                logger.warning(
                    "Timezone not found for day trading config",
                    timezone=self.rules.day_trade_timezone,
                )

    def _trip(self, reason: str) -> None:
        if self.kill_switch:
            return
        self.kill_switch = True
        logger.error("Risk breach", account=self.account, reason=reason)
        monitor.record_event(
            "risk.breach",
            {
                "account": self.account,
                "reason": reason,
            },
        )
        self.broker.cancel_open_orders(self.account)
        self.broker.flatten_positions(self.account)

    def _reset_session(self, session_date: date) -> None:
        self.session_date = session_date
        self.trade_count = 0
        self._intraday_peak_equity = None
        self._flattened_today = False
        self.kill_switch = False

    def _ensure_session(self, now: datetime | None = None) -> None:
        current_dt = now or datetime.now(UTC)
        current = current_dt.date()
        if self.session_date != current:
            self._reset_session(current)

    def check_orders_per_minute(self, now: datetime | None = None) -> bool:
        if self.rules.max_orders_per_min is None:
            return True
        ts = now or datetime.now(UTC)
        self.order_timestamps.append(ts)
        while self.order_timestamps and (ts - self.order_timestamps[0]) > timedelta(minutes=1):
            self.order_timestamps.popleft()
        if len(self.order_timestamps) > self.rules.max_orders_per_min:
            self._trip("max_orders_per_min")
            return False
        return True

    def evaluate(self, account_state: AccountState) -> bool:
        self._ensure_session(account_state.timestamp)
        if self.kill_switch:
            return False
        if self.rules.max_daily_loss_pct is not None and account_state.balance > 0:
            dd = (account_state.balance - account_state.equity) / account_state.balance * 100
            if dd > self.rules.max_daily_loss_pct:
                self._trip("max_daily_loss_pct")
                return False
        if self.rules.max_intraday_loss_pct is not None and account_state.equity > 0:
            if (
                self._intraday_peak_equity is None
                or account_state.equity > self._intraday_peak_equity
            ):
                self._intraday_peak_equity = account_state.equity
            elif self._intraday_peak_equity > 0:
                dd = (
                    (self._intraday_peak_equity - account_state.equity)
                    / self._intraday_peak_equity
                    * 100
                )
                if dd > self.rules.max_intraday_loss_pct:
                    self._trip("max_intraday_loss_pct")
                    return False
        if (
            self.rules.max_positions is not None
            and len(account_state.positions) > self.rules.max_positions
        ):
            self._trip("max_positions")
            return False
        if self.rules.contracts_per_symbol is not None:
            for pos in account_state.positions:
                if abs(pos.get("qty", 0)) > self.rules.contracts_per_symbol:
                    self._trip("contracts_per_symbol")
                    return False
        return True

    def record_trade(self, now: datetime | None = None) -> bool:
        self._ensure_session(now)
        if self.rules.max_day_trades is None:
            return True
        self.trade_count += 1
        if self.trade_count > self.rules.max_day_trades:
            self._trip("max_day_trades")
            return False
        return True

    def should_flatten_for_close(self, now: datetime | None = None) -> bool:
        self._ensure_session(now)
        if not self.rules.flatten_at_close or self._close_time is None:
            return False
        moment = now or datetime.now(UTC)
        localized = moment
        if moment.tzinfo is None:
            if self._tz is not None:
                localized = moment.replace(tzinfo=UTC).astimezone(self._tz)
        elif self._tz is not None:
            localized = moment.astimezone(self._tz)
        if self._tz is None and localized.tzinfo is None:
            # Assume UTC if no timezone provided
            localized = localized.replace(tzinfo=UTC)
        if self._flattened_today:
            return False
        if localized.time() >= self._close_time:
            self._flattened_today = True
            logger.info("Day trading flatten triggered", account=self.account)
            self.broker.cancel_open_orders(self.account)
            self.broker.flatten_positions(self.account)
            return True
        return False
