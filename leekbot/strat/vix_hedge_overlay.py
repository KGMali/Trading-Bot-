from __future__ import annotations

from typing import Dict, List

from ..core.utils import OrderIntent
from .base import Strategy


class VIXHedgeOverlay(Strategy):
    def __init__(self, name: str, config: Dict | None = None) -> None:
        super().__init__(name, config)
        self.beta_threshold = self.config.get("beta_threshold", 1.2)
        self.pending: List[OrderIntent] = []

    def on_bar(self, bar: Dict, account_state: Dict) -> None:
        beta = account_state.get("portfolio_beta", 1.0)
        if beta > self.beta_threshold:
            self.pending.append(OrderIntent("UVXY", "BUY", 1, "market", tag="vix_hedge"))
        elif beta < 1.0:
            self.pending.append(OrderIntent("UVXY", "SELL", 1, "market", tag="vix_unwind"))

    def get_orders(self) -> List[OrderIntent]:
        orders, self.pending = self.pending, []
        return orders
