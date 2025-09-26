from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .base import BrokerClient


@dataclass
class OrderRecord:
    id: str
    symbol: str
    side: str
    qty: float
    price: float | None
    status: str = "open"


class SimulatedBroker(BrokerClient):
    def __init__(self, name: str) -> None:
        self.name = name
        self.orders: Dict[str, OrderRecord] = {}
        self.positions: Dict[str, List[Dict]] = {}
        self.balances: Dict[str, Dict] = {}
        self._id = 0

    def _next_id(self) -> str:
        self._id += 1
        return f"{self.name}-{self._id}"

    def place_order(self, account: str, order: Dict) -> Dict:
        order_id = self._next_id()
        record = OrderRecord(
            id=order_id,
            symbol=order["symbol"],
            side=order["side"],
            qty=order["qty"],
            price=order.get("price"),
        )
        self.orders[order_id] = record
        pos_list = self.positions.setdefault(account, [])
        pos_list.append({"symbol": record.symbol, "qty": record.qty, "side": record.side})
        balance = self.balances.setdefault(account, {"cash": 100000.0, "equity": 100000.0})
        balance["equity"] -= record.qty * (record.price or 100)
        return {"order_id": order_id, "status": record.status}

    def cancel_order(self, account: str, order_id: str) -> bool:
        record = self.orders.get(order_id)
        if record:
            record.status = "cancelled"
            return True
        return False

    def get_positions(self, account: str) -> List[Dict]:
        return self.positions.get(account, [])

    def get_balance(self, account: str) -> Dict:
        return self.balances.get(account, {"cash": 100000.0, "equity": 100000.0})

    def cancel_open_orders(self, account: str) -> None:
        for order in self.orders.values():
            order.status = "cancelled"

    def flatten_positions(self, account: str) -> None:
        self.positions[account] = []
