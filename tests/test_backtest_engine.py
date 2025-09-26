from __future__ import annotations

from datetime import datetime

from leekbot.backtest.engine import BacktestEngine
from leekbot.core.dataframe import MiniDataFrame, date_range
from leekbot.strat.momentum_1m import MomentumStrategy


def test_backtest_runs():
    index = date_range(datetime(2024, 1, 1, 9, 30), periods=5)
    rows = []
    price = 100
    for _ in index:
        rows.append(
            {"open": price, "high": price + 1, "low": price - 1, "close": price, "volume": 1000}
        )
        price += 1
    data = {"SPY": MiniDataFrame(rows, index)}
    strategies = {
        "momentum_1m": MomentumStrategy("momentum_1m", {"lookback": 5, "adx_threshold": 0})
    }
    engine = BacktestEngine(data, strategies)
    result = engine.run()
    assert "pnl" in result.metrics
    assert isinstance(result.trades, list)
