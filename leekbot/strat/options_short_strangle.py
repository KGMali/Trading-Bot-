from __future__ import annotations

from typing import Dict, List

from ..core.utils import OrderIntent
from .base import Strategy


class ShortStrangleStrategy(Strategy):
    def __init__(self, name: str, config: Dict | None = None) -> None:
        super().__init__(name, config)
        self.pending: List[OrderIntent] = []
        self.width = self.config.get("width", 50)
        self.max_loss = self.config.get("max_loss", 1000)

    def on_bar(self, bar: Dict, account_state: Dict) -> None:
        symbol = bar["symbol"]
        equity = account_state.get("equity", 0)
        if equity <= self.max_loss:
            return
        if not account_state.get("positions"):
            call_price = bar["close"] + self.width
            put_price = bar["close"] - self.width
            self.pending.append(
                OrderIntent(f"{symbol}_CALL", "SELL", 1, "limit", price=call_price, tag="strangle")
            )
            self.pending.append(
                OrderIntent(f"{symbol}_PUT", "SELL", 1, "limit", price=put_price, tag="strangle")
            )

    def get_orders(self) -> List[OrderIntent]:
        orders, self.pending = self.pending, []
        return orders
