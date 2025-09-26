from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Dict

from ..brokers.base import BrokerClient
from ..core.logging import audit_log, get_logger
from ..core.utils import utcnow
from ..monitor import monitor


@dataclass(slots=True)
class Order:
    order_id: str
    symbol: str
    side: str
    qty: float
    order_type: str
    tif: str
    venue: str
    price: float | None = None
    stop: float | None = None
    tag: str | None = None


_LOG = get_logger(__name__)


class BrokerRegistry:
    def __init__(self) -> None:
        modules = {
            "alpaca": "leekbot.brokers.alpaca",
            "ibkr": "leekbot.brokers.ibkr",
            "oanda": "leekbot.brokers.oanda",
            "kraken": "leekbot.brokers.kraken",
            "coinbase": "leekbot.brokers.coinbase",
            "tradovate": "leekbot.brokers.tradovate",
            "deribit": "leekbot.brokers.deribit",
        }
        self._brokers: Dict[str, BrokerClient] = {}
        for venue, path in modules.items():
            module = importlib.import_module(path)
            self._brokers[venue] = module.Broker()

    def get(self, venue: str) -> BrokerClient:
        if venue not in self._brokers:
            raise ValueError(f"Venue {venue} not configured")
        return self._brokers[venue]


_REGISTRY = BrokerRegistry()


def create_order(
    symbol: str,
    side: str,
    qty: float,
    order_type: str,
    tif: str = "DAY",
    venue: str | None = None,
    price: float | None = None,
    stop: float | None = None,
    tag: str | None = None,
    account: str | None = None,
) -> Order:
    if venue is None:
        raise ValueError("Venue must be provided")
    broker = _REGISTRY.get(venue)
    payload = {
        "symbol": symbol,
        "side": side,
        "qty": qty,
        "type": order_type,
        "tif": tif,
        "price": price,
        "stop": stop,
        "tag": tag,
    }
    response = broker.place_order(account or venue, payload)
    order = Order(
        order_id=response.get("order_id", ""),
        symbol=symbol,
        side=side,
        qty=qty,
        order_type=order_type,
        tif=tif,
        venue=venue,
        price=price,
        stop=stop,
        tag=tag,
    )
    record = {"ts": utcnow().isoformat(), "event": "create_order", "order": payload}
    audit_log("logs/audit.log", record)
    monitor.record_event(
        "order.submitted",
        {
            "venue": venue,
            "account": account or venue,
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "type": order_type,
            "tag": tag,
        },
    )
    _LOG.info("order.create", venue=venue, symbol=symbol, side=side, qty=qty, order_type=order_type)
    return order


def cancel_order(order_id: str, venue: str | None = None, account: str | None = None) -> bool:
    if venue is None:
        raise ValueError("Venue required for cancel")
    broker = _REGISTRY.get(venue)
    result = broker.cancel_order(account or venue, order_id)
    audit_log(
        "logs/audit.log",
        {"ts": utcnow().isoformat(), "event": "cancel_order", "order_id": order_id, "venue": venue},
    )
    monitor.record_event(
        "order.cancelled",
        {"venue": venue, "account": account or venue, "order_id": order_id, "status": result},
    )
    return result


def get_positions(account: str, venue: str | None = None) -> list:
    if venue is None:
        raise ValueError("Venue required")
    broker = _REGISTRY.get(venue)
    return broker.get_positions(account)


def get_balance(account: str, venue: str | None = None) -> dict:
    if venue is None:
        raise ValueError("Venue required")
    broker = _REGISTRY.get(venue)
    return broker.get_balance(account)
