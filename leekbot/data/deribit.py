from __future__ import annotations

import random
from datetime import datetime
from typing import Dict, Iterable

from ..core.dataframe import MiniDataFrame, date_range
from .base import MarketDataClient


class DeribitClient(MarketDataClient):
    def __init__(self, client_id: str | None = None, client_secret: str | None = None) -> None:
        self.client_id = client_id
        self.client_secret = client_secret

    def get_bars(
        self, symbols: Iterable[str], timeframe: str, start: datetime, end: datetime
    ) -> Dict[str, MiniDataFrame]:
        index = date_range(start, end)
        bars: Dict[str, MiniDataFrame] = {}
        for symbol in symbols:
            rows = []
            price = 50.0
            for _ in index:
                price += random.uniform(-1, 1)
                rows.append(
                    {
                        "open": price,
                        "high": price + random.random(),
                        "low": price - random.random(),
                        "close": price + random.uniform(-0.2, 0.2),
                        "volume": random.randint(10, 100),
                    }
                )
            bars[symbol] = MiniDataFrame(rows, index)
        return bars

    def get_book(self, symbol: str) -> Dict[str, float]:
        return {"bid": 10.0, "ask": 10.5}

    def get_greeks(self, symbol: str) -> Dict[str, float]:
        return {"delta": 0.5, "gamma": 0.1, "theta": -0.01, "vega": 0.2}

    def get_iv_surface(self, symbol: str):
        expiries = date_range(datetime.utcnow(), periods=5)
        strikes = [0.8, 0.9, 1.0, 1.1, 1.2]
        surface = {}
        for expiry in expiries:
            surface[str(expiry)] = {
                str(strike): 0.5 + 0.1 * idx for idx, strike in enumerate(strikes)
            }
        return surface
