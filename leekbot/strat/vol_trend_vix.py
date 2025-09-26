from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List

from ..core.utils import OrderIntent
from .base import Strategy


class VolTrendStrategy(Strategy):
    def __init__(self, name: str, config: Dict | None = None) -> None:
        super().__init__(name, config)
        self.window = self.config.get("window", 15)
        self.pending: List[OrderIntent] = []
        self.history: Dict[str, Deque[float]] = {}

    def on_bar(self, bar: Dict, account_state: Dict) -> None:
        symbol = bar["symbol"]
        closes = self.history.setdefault(symbol, deque(maxlen=self.window))
        closes.append(bar["close"])
        if len(closes) < self.window:
            return
        prices = list(closes)
        trend = prices[-1] - prices[0]
        position = account_state.get("positions", {}).get(symbol, 0)
        if trend > 0 and position <= 0:
            self.pending.append(OrderIntent(symbol, "BUY", 1, "market", tag="vol_trend_long"))
        elif trend < 0 and position >= 0:
            self.pending.append(OrderIntent(symbol, "SELL", 1, "market", tag="vol_trend_flatten"))

    def get_orders(self) -> List[OrderIntent]:
        orders, self.pending = self.pending, []
        return orders
