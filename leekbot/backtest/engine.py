from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from ..core.dataframe import MiniDataFrame
from ..strat.base import Strategy, load_strategy
from .metrics import Metrics


@dataclass
class BacktestResult:
    trades: List[Dict]
    metrics: Dict[str, float]


class BacktestEngine:
    def __init__(self, data: Dict[str, MiniDataFrame], strategies: Dict[str, Strategy]) -> None:
        self.data = data
        self.strategies = strategies
        self.trades: List[Dict] = []
        self.equity = 100000.0

    def run(self) -> BacktestResult:
        symbols = list(self.data.keys())
        index = sorted(set().union(*[df.index for df in self.data.values()]))
        positions: Dict[str, float] = {sym: 0 for sym in symbols}
        for ts in index:
            account_state = {"equity": self.equity, "positions": positions}
            for name, strat in self.strategies.items():
                for symbol in symbols:
                    if ts not in self.data[symbol].index:
                        continue
                    bar = dict(self.data[symbol].loc[ts])
                    bar["symbol"] = symbol
                    strat.on_bar(bar, account_state)
                intents = strat.get_orders()
                for intent in intents:
                    price = bar["close"] if intent.price is None else intent.price
                    trade = {
                        "timestamp": ts,
                        "symbol": intent.symbol,
                        "side": intent.side,
                        "qty": intent.qty,
                        "price": price,
                        "strategy": name,
                    }
                    self.trades.append(trade)
                    qty = intent.qty if intent.side == "BUY" else -intent.qty
                    positions[intent.symbol] = positions.get(intent.symbol, 0) + qty
                    self.equity -= qty * price
        metrics = Metrics(self.trades).compute()
        return BacktestResult(self.trades, metrics)

    @classmethod
    def from_csv(cls, paths: Dict[str, Path], strategies: Dict[str, Dict]) -> BacktestEngine:
        data: Dict[str, MiniDataFrame] = {}
        for symbol, path in paths.items():
            with open(path, encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                rows: List[Dict[str, float]] = []
                index: List[datetime] = []
                for row in reader:
                    ts = datetime.fromisoformat(row[reader.fieldnames[0]])
                    index.append(ts)
                    rows.append(
                        {
                            key: float(value)
                            for key, value in row.items()
                            if key != reader.fieldnames[0]
                        }
                    )
                data[symbol] = MiniDataFrame(rows, index)
        strats = {name: load_strategy(name, cfg) for name, cfg in strategies.items()}
        return cls(data, strats)
