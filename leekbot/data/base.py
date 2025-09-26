from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Iterable, List, Protocol

from ..core.dataframe import MiniDataFrame


class MarketDataClient(ABC):
    @abstractmethod
    def get_bars(
        self, symbols: Iterable[str], timeframe: str, start: datetime, end: datetime
    ) -> Dict[str, MiniDataFrame]:
        raise NotImplementedError

    @abstractmethod
    def get_book(self, symbol: str) -> Dict[str, float]:
        raise NotImplementedError

    def get_greeks(self, symbol: str) -> Dict[str, float]:
        raise NotImplementedError

    def get_iv_surface(self, symbol: str):
        raise NotImplementedError


class WebSocketHandler(Protocol):
    async def subscribe(self, symbols: List[str]) -> None: ...

    async def stream(self) -> None: ...
