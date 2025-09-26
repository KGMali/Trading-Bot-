from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List, Tuple

from ..core.utils import OrderIntent
from .base import Strategy


class PairsStatArb(Strategy):
    def __init__(self, name: str, config: Dict | None = None) -> None:
        super().__init__(name, config)
        self.window = self.config.get("window", 60)
        self.threshold = self.config.get("threshold", 2.0)
        self.pairs: List[Tuple[str, str]] = self.config.get("pairs", [("SPY", "QQQ")])
        self.history: Dict[str, Deque[float]] = {
            sym: deque(maxlen=self.window) for pair in self.pairs for sym in pair
        }
        self.pending: List[OrderIntent] = []

    def _mean(self, values: List[float]) -> float:
        return sum(values) / len(values)

    def _std(self, values: List[float]) -> float:
        mean = self._mean(values)
        return (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5

    def on_bar(self, bar: Dict, account_state: Dict) -> None:
        symbol = bar["symbol"]
        if symbol not in self.history:
            return
        self.history[symbol].append(bar["close"])
        for a, b in self.pairs:
            if len(self.history[a]) == self.window and len(self.history[b]) == self.window:
                spread = [pa - pb for pa, pb in zip(self.history[a], self.history[b])]
                mean = self._mean(spread)
                std = self._std(spread)
                if std == 0:
                    continue
                z_score = (spread[-1] - mean) / std
                position_a = account_state.get("positions", {}).get(a, 0)
                position_b = account_state.get("positions", {}).get(b, 0)
                if z_score > self.threshold and position_a <= 0 and position_b >= 0:
                    self.pending.append(OrderIntent(a, "SELL", 1, "market", tag="pairs_short_a"))
                    self.pending.append(OrderIntent(b, "BUY", 1, "market", tag="pairs_long_b"))
                elif z_score < -self.threshold and position_a >= 0 and position_b <= 0:
                    self.pending.append(OrderIntent(a, "BUY", 1, "market", tag="pairs_long_a"))
                    self.pending.append(OrderIntent(b, "SELL", 1, "market", tag="pairs_short_b"))

    def get_orders(self) -> List[OrderIntent]:
        orders, self.pending = self.pending, []
        return orders
