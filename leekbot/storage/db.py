from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Iterable


class TradeDatabase:
    def __init__(self, path: str | Path = "trades.db") -> None:
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path)
        self._setup()

    def _setup(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symbol TEXT,
                side TEXT,
                qty REAL,
                price REAL,
                strategy TEXT
            )
            """
        )
        self.conn.commit()

    def insert_trades(self, trades: Iterable[Dict]) -> None:
        cur = self.conn.cursor()
        cur.executemany(
            "INSERT INTO trades(timestamp, symbol, side, qty, price, strategy) VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    trade["timestamp"],
                    trade["symbol"],
                    trade["side"],
                    trade["qty"],
                    trade["price"],
                    trade.get("strategy", ""),
                )
                for trade in trades
            ],
        )
        self.conn.commit()
