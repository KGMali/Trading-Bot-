from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Position:
    symbol: str
    qty: float
    avg_price: float


@dataclass
class PortfolioAccount:
    name: str
    base_ccy: str
    cash: float = 100000.0
    equity: float = 100000.0
    positions: Dict[str, Position] = field(default_factory=dict)

    def update_fill(self, symbol: str, qty: float, price: float) -> None:
        pos = self.positions.get(symbol)
        if pos is None:
            self.positions[symbol] = Position(symbol, qty, price)
        else:
            total_qty = pos.qty + qty
            if total_qty == 0:
                self.positions.pop(symbol)
            else:
                pos.avg_price = (pos.avg_price * pos.qty + price * qty) / total_qty
                pos.qty = total_qty
        self.cash -= qty * price
        self.equity = self.cash + sum(p.qty * p.avg_price for p in self.positions.values())


class PortfolioTracker:
    def __init__(self, accounts: List[Dict]) -> None:
        self.accounts: Dict[str, PortfolioAccount] = {
            cfg["name"]: PortfolioAccount(cfg["name"], cfg.get("base_ccy", "USD"))
            for cfg in accounts
        }

    def on_fill(self, account: str, symbol: str, qty: float, price: float) -> None:
        self.accounts[account].update_fill(symbol, qty, price)

    def account_state(self, account: str) -> PortfolioAccount:
        return self.accounts[account]
