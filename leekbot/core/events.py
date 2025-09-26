from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


class EventType(str, Enum):
    TICK = "tick"
    BAR = "bar"
    SIGNAL = "signal"
    ORDER = "order"
    FILL = "fill"
    ACCOUNT = "account"


@dataclass(slots=True)
class MarketEvent:
    type: EventType
    timestamp: datetime


@dataclass(slots=True)
class BarEvent(MarketEvent):
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    timeframe: str


@dataclass(slots=True)
class TickEvent(MarketEvent):
    symbol: str
    bid: float
    ask: float
    last: float
    size: float


@dataclass(slots=True)
class SignalEvent(MarketEvent):
    symbol: str
    side: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OrderEvent(MarketEvent):
    order_id: str
    account: str
    symbol: str
    side: str
    qty: float
    order_type: str
    tif: str
    price: float | None = None
    stop: float | None = None
    tag: str | None = None


@dataclass(slots=True)
class FillEvent(MarketEvent):
    order_id: str
    account: str
    symbol: str
    side: str
    qty: float
    price: float
    commission: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AccountUpdateEvent(MarketEvent):
    account: str
    balance: float
    equity: float
    positions: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
