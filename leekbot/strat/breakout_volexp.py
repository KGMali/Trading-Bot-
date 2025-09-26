from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List

from ..core.utils import OrderIntent
from .base import Strategy


class BreakoutVolExpansion(Strategy):
    def __init__(self, name: str, config: Dict | None = None) -> None:
        super().__init__(name, config)
        self.window = self.config.get("window", 30)
        self.pending: List[OrderIntent] = []
        self.bars: Dict[str, Deque[Dict]] = {}

    def _std(self, values: List[float]) -> float:
        mean = sum(values) / len(values)
        return (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5

    def on_bar(self, bar: Dict, account_state: Dict) -> None:
        symbol = bar["symbol"]
        history = self.bars.setdefault(symbol, deque(maxlen=self.window))
        history.append(bar)
        if len(history) < self.window:
            return
        closes = [row["close"] for row in history]
        volatility = self._std(closes)
        diffs = [abs(history[i]["close"] - history[i - 1]["close"]) for i in range(1, len(history))]
        avg_vol = sum(diffs) / len(diffs)
        squeeze = volatility < avg_vol * 0.5
        expansion = volatility > avg_vol * 1.5
        position = account_state.get("positions", {}).get(symbol, 0)
        if squeeze and closes[-1] > max(closes) and position <= 0:
            self.pending.append(OrderIntent(symbol, "BUY", 1, "market", tag="volexp_breakout"))
        elif expansion and closes[-1] < min(closes) and position >= 0:
            self.pending.append(OrderIntent(symbol, "SELL", 1, "market", tag="volexp_breakdown"))

    def get_orders(self) -> List[OrderIntent]:
        orders, self.pending = self.pending, []
        return orders
