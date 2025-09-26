from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List

from ..core.utils import OrderIntent
from .base import Strategy


class MomentumStrategy(Strategy):
    def __init__(self, name: str, config: Dict | None = None) -> None:
        super().__init__(name, config)
        self.lookback = self.config.get("lookback", 30)
        self.fast = self.config.get("fast", 12)
        self.slow = self.config.get("slow", 26)
        self.adx_threshold = self.config.get("adx_threshold", 20)
        self.bars: Dict[str, Deque[float]] = {}
        self.pending: List[OrderIntent] = []

    def on_bar(self, bar: Dict, account_state: Dict) -> None:
        symbol = bar["symbol"]
        closes = self.bars.setdefault(symbol, deque(maxlen=self.lookback))
        closes.append(bar["close"])
        if len(closes) < self.lookback:
            return
        prices = list(closes)
        fast_window = prices[-self.fast :]
        slow_window = prices[-self.slow :]
        fast_avg = sum(fast_window) / len(fast_window)
        slow_avg = sum(slow_window) / len(slow_window)
        momentum = fast_avg - slow_avg
        diffs = [abs(prices[i] - prices[i - 1]) for i in range(1, len(prices))][-5:]
        adx = (sum(diffs) / max(len(diffs), 1)) * 100
        position = account_state.get("positions", {}).get(symbol, 0)
        if momentum > 0 and adx > self.adx_threshold and position <= 0:
            self.pending.append(OrderIntent(symbol, "BUY", 1, "market", tag="momentum_long"))
        elif momentum < 0 and adx > self.adx_threshold and position >= 0:
            self.pending.append(OrderIntent(symbol, "SELL", 1, "market", tag="momentum_short"))

    def on_fill(self, fill: Dict, account_state: Dict) -> None:
        return None

    def get_orders(self) -> List[OrderIntent]:
        orders, self.pending = self.pending, []
        return orders
