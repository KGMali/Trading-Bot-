from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Metrics:
    trades: List[Dict]

    def compute(self) -> Dict[str, float]:
        if not self.trades:
            return {"pnl": 0.0, "sharpe": 0.0, "max_dd": 0.0, "win_rate": 0.0}
        pnl_values = []
        for trade in self.trades:
            sign = 1 if trade["side"].upper() == "SELL" else -1
            pnl_values.append(sign * trade["price"] * trade["qty"])
        total_pnl = sum(pnl_values)
        mean = total_pnl / len(pnl_values)
        variance = sum((p - mean) ** 2 for p in pnl_values) / max(len(pnl_values), 1)
        std = variance**0.5 or 1e-9
        sharpe = mean / std * (252**0.5)
        cumulative = []
        running = 0.0
        max_peak = float("-inf")
        max_drawdown = 0.0
        wins = 0
        for pnl in pnl_values:
            running += pnl
            cumulative.append(running)
            if pnl > 0:
                wins += 1
            if running > max_peak:
                max_peak = running
            drawdown = running - max_peak
            if drawdown < max_drawdown:
                max_drawdown = drawdown
        win_rate = wins / len(pnl_values)
        return {
            "pnl": float(total_pnl),
            "sharpe": float(sharpe),
            "max_dd": float(max_drawdown),
            "win_rate": float(win_rate),
        }
