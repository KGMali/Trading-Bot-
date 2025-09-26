from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List

from ..core.utils import OrderIntent
from .base import Strategy


class VolReversionStrategy(Strategy):
    def __init__(self, name: str, config: Dict | None = None) -> None:
        super().__init__(name, config)
        self.window = self.config.get("window", 20)
        self.limit = self.config.get("limit", 3.0)
        self.pending: List[OrderIntent] = []
        self.history: Dict[str, Deque[float]] = {}

    def _mean(self, values: List[float]) -> float:
        return sum(values) / len(values)

    def _std(self, values: List[float]) -> float:
        mean = self._mean(values)
        return (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5

    def on_bar(self, bar: Dict, account_state: Dict) -> None:
        symbol = bar["symbol"]
        closes = self.history.setdefault(symbol, deque(maxlen=self.window))
        closes.append(bar["close"])
        if len(closes) < self.window:
            return
        arr = list(closes)
        mean = self._mean(arr)
        std = self._std(arr) + 1e-9
        z = (arr[-1] - mean) / std
        position = account_state.get("positions", {}).get(symbol, 0)
        if z > self.limit and position >= 0:
            self.pending.append(OrderIntent(symbol, "SELL", 1, "market", tag="vol_fade_short"))
        elif z < -self.limit and position <= 0:
            self.pending.append(OrderIntent(symbol, "BUY", 1, "market", tag="vol_fade_long"))

    def get_orders(self) -> List[OrderIntent]:
        orders, self.pending = self.pending, []
        return orders
