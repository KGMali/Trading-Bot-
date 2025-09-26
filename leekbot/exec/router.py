from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..core.utils import OrderIntent
from .order_interface import create_order


@dataclass
class StrategyRoute:
    name: str
    account: str
    venue: str


@dataclass
class OrderRouter:
    routes: Dict[str, StrategyRoute]

    @classmethod
    def from_config(cls, accounts: List[Dict]) -> OrderRouter:
        routes: Dict[str, StrategyRoute] = {}
        for account in accounts:
            venue = account["venue"]
            for strat in account.get("strategies", []):
                routes[strat] = StrategyRoute(strat, account["name"], venue)
        return cls(routes)

    def submit_orders(self, strategy: str, orders: List[OrderIntent]) -> List[str]:
        route = self.routes[strategy]
        order_ids: List[str] = []
        for intent in orders:
            order = create_order(
                symbol=intent.symbol,
                side=intent.side,
                qty=intent.qty,
                order_type=intent.order_type,
                tif="DAY",
                venue=route.venue,
                price=intent.price,
                stop=intent.stop,
                tag=intent.tag,
                account=route.account,
            )
            order_ids.append(order.order_id)
        return order_ids
