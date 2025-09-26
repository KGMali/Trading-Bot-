from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List

from ..core.utils import OrderIntent
from .base import Strategy


class ORBStrategy(Strategy):
    def __init__(self, name: str, config: Dict | None = None) -> None:
        super().__init__(name, config)
        self.open_window = self.config.get("open_window", 5)
        self.atr_window = self.config.get("atr_window", 14)
        self.bars: Dict[str, Deque[Dict]] = {}
        self.pending: List[OrderIntent] = []

    def _atr(self, history: List[Dict]) -> float:
        if len(history) < self.atr_window:
            return 0.0
        window = history[-self.atr_window :]
        ranges = [bar["high"] - bar["low"] for bar in window]
        return sum(ranges) / len(ranges)

    def on_bar(self, bar: Dict, account_state: Dict) -> None:
        symbol = bar["symbol"]
        history = self.bars.setdefault(symbol, deque(maxlen=100))
        history.append(bar)
        if len(history) < self.open_window:
            return
        prices = list(history)
        highs = [b["high"] for b in prices]
        lows = [b["low"] for b in prices]
        closes = [b["close"] for b in prices]
        atr = self._atr(prices)
        open_high = max(highs[: self.open_window])
        open_low = min(lows[: self.open_window])
        position = account_state.get("positions", {}).get(symbol, 0)
        if closes[-1] > open_high + atr and position <= 0:
            trigger = open_high + atr
            self.pending.append(
                OrderIntent(symbol, "BUY", 1, "stop", price=trigger, tag="orb_long")
            )
        elif closes[-1] < open_low - atr and position >= 0:
            trigger = open_low - atr
            self.pending.append(
                OrderIntent(symbol, "SELL", 1, "stop", price=trigger, tag="orb_short")
            )

    def get_orders(self) -> List[OrderIntent]:
        orders, self.pending = self.pending, []
        return orders
