from __future__ import annotations

from dataclasses import dataclass

from leekbot.core import risk
from leekbot.monitor import monitor


@dataclass
class DummyBroker:
    cancelled: bool = False
    flattened: bool = False

    def cancel_open_orders(self, account: str) -> None:
        self.cancelled = True

    def flatten_positions(self, account: str) -> None:
        self.flattened = True


def test_risk_trips_kill_switch():
    monitor.reset()
    broker = DummyBroker()
    manager = risk.RiskManager("acct", risk.RiskRuleConfig(max_daily_loss_pct=1.0), broker)
    state = risk.AccountState(balance=100.0, equity=80.0, positions=[])
    assert manager.evaluate(state) is False
    assert broker.cancelled is True
    assert broker.flattened is True


def test_day_trade_limit_triggers_kill_switch():
    monitor.reset()
    broker = DummyBroker()
    manager = risk.RiskManager("acct", risk.RiskRuleConfig(max_day_trades=2), broker)
    assert manager.record_trade() is True
    assert manager.record_trade() is True
    assert manager.record_trade() is False
    assert broker.cancelled is True
    assert broker.flattened is True


def test_intraday_drawdown_trips_risk():
    monitor.reset()
    broker = DummyBroker()
    manager = risk.RiskManager(
        "acct",
        risk.RiskRuleConfig(max_intraday_loss_pct=1.0),
        broker,
    )
    start_state = risk.AccountState(balance=100.0, equity=100.0, positions=[])
    assert manager.evaluate(start_state) is True
    drop_state = risk.AccountState(balance=100.0, equity=98.0, positions=[])
    assert manager.evaluate(drop_state) is False
    assert broker.cancelled is True
    assert broker.flattened is True


def test_flatten_at_close_executes_once():
    monitor.reset()
    broker = DummyBroker()
    manager = risk.RiskManager(
        "acct",
        risk.RiskRuleConfig(
            flatten_at_close=True,
            day_trade_close_time="15:55",
            day_trade_timezone="UTC",
        ),
        broker,
    )
    before_close = risk.datetime(2024, 1, 1, 15, 54, tzinfo=risk.ZoneInfo("UTC"))
    assert manager.should_flatten_for_close(before_close) is False
    after_close = risk.datetime(2024, 1, 1, 15, 56, tzinfo=risk.ZoneInfo("UTC"))
    assert manager.should_flatten_for_close(after_close) is True
    # Subsequent calls should not trigger again
    assert manager.should_flatten_for_close(after_close) is False
