from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List

from ..core.utils import OrderIntent
from .base import Strategy


class VWAPReversionStrategy(Strategy):
    def __init__(self, name: str, config: Dict | None = None) -> None:
        super().__init__(name, config)
        self.window = self.config.get("window", 20)
        self.std_mult = self.config.get("std_mult", 2.0)
        self.bars: Dict[str, Deque[Dict]] = {}
        self.pending: List[OrderIntent] = []

    def _vwap(self, data: Deque[Dict]) -> float:
        volumes = [row["volume"] for row in data]
        prices = [row["close"] for row in data]
        total_volume = sum(volumes) or 1.0
        return sum(v * p for v, p in zip(volumes, prices)) / total_volume

    def _std(self, values: List[float]) -> float:
        mean = sum(values) / len(values)
        return (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5

    def on_bar(self, bar: Dict, account_state: Dict) -> None:
        symbol = bar["symbol"]
        history = self.bars.setdefault(symbol, deque(maxlen=self.window))
        history.append(bar)
        if len(history) < self.window:
            return
        vwap = self._vwap(history)
        prices = [row["close"] for row in history]
        std = self._std(prices)
        upper = vwap + self.std_mult * std
        lower = vwap - self.std_mult * std
        position = account_state.get("positions", {}).get(symbol, 0)
        if bar["close"] < lower and position <= 0:
            self.pending.append(OrderIntent(symbol, "BUY", 1, "market", tag="vwap_long"))
        elif bar["close"] > upper and position >= 0:
            self.pending.append(OrderIntent(symbol, "SELL", 1, "market", tag="vwap_short"))

    def get_orders(self) -> List[OrderIntent]:
        orders, self.pending = self.pending, []
        return orders
