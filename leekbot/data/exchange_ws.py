from __future__ import annotations

import asyncio
import random
from datetime import datetime
from typing import Dict, Iterable, List

from ..core.dataframe import MiniDataFrame, date_range
from .base import MarketDataClient


class CryptoWebSocketClient(MarketDataClient):
    def __init__(self, venues: List[str]) -> None:
        self.venues = venues

    def get_bars(
        self, symbols: Iterable[str], timeframe: str, start: datetime, end: datetime
    ) -> Dict[str, MiniDataFrame]:
        index = date_range(start, end)
        bars: Dict[str, MiniDataFrame] = {}
        for symbol in symbols:
            rows = []
            price = 20000.0
            for _ in index:
                price += random.uniform(-5, 5)
                rows.append(
                    {
                        "open": price,
                        "high": price + 2,
                        "low": price - 2,
                        "close": price + random.uniform(-1, 1),
                        "volume": 1.0,
                    }
                )
            bars[symbol] = MiniDataFrame(rows, index)
        return bars

    def get_book(self, symbol: str) -> Dict[str, float]:
        mid = 30000 + random.random() * 10
        return {"bid": mid - 0.5, "ask": mid + 0.5}

    async def subscribe(self, symbols: List[str]) -> None:
        await asyncio.sleep(0.01)

    async def stream(self):
        while True:
            await asyncio.sleep(1)
            yield {"symbol": random.choice(["BTCUSD", "ETHUSD"]), "price": random.random()}
