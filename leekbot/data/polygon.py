from __future__ import annotations

import random
from datetime import datetime
from typing import Dict, Iterable

from ..core.dataframe import MiniDataFrame, date_range
from .base import MarketDataClient


class PolygonClient(MarketDataClient):
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key

    def get_bars(
        self, symbols: Iterable[str], timeframe: str, start: datetime, end: datetime
    ) -> Dict[str, MiniDataFrame]:
        index = date_range(start, end)
        bars: Dict[str, MiniDataFrame] = {}
        for symbol in symbols:
            rows = []
            price = 100.0
            for _ in index:
                drift = random.uniform(-1, 1)
                price = max(1.0, price + drift)
                row = {
                    "open": price,
                    "high": price + abs(random.uniform(0, 0.5)),
                    "low": price - abs(random.uniform(0, 0.5)),
                    "close": price + random.uniform(-0.2, 0.2),
                    "volume": random.randint(1000, 10000),
                }
                rows.append(row)
            bars[symbol] = MiniDataFrame(rows, index)
        return bars

    def get_book(self, symbol: str) -> Dict[str, float]:
        mid = 100 + random.random()
        return {"bid": mid - 0.01, "ask": mid + 0.01}
