from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable

from ..core.dataframe import MiniDataFrame, date_range
from .base import MarketDataClient


class OandaStreamingClient(MarketDataClient):
    def __init__(self, account: str | None = None) -> None:
        self.account = account

    def get_bars(
        self, symbols: Iterable[str], timeframe: str, start: datetime, end: datetime
    ) -> Dict[str, MiniDataFrame]:
        index = date_range(start, end)
        bars: Dict[str, MiniDataFrame] = {}
        for symbol in symbols:
            rows = []
            price = 1.0
            for _ in index:
                price += 0.001
                rows.append(
                    {
                        "open": price,
                        "high": price + 0.001,
                        "low": price - 0.001,
                        "close": price,
                        "volume": 100000,
                    }
                )
            bars[symbol] = MiniDataFrame(rows, index)
        return bars

    def get_book(self, symbol: str) -> Dict[str, float]:
        return {"bid": 1.05, "ask": 1.051}
