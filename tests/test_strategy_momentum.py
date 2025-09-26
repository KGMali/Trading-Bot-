from __future__ import annotations

from leekbot.strat.momentum_1m import MomentumStrategy


def test_momentum_generates_orders():
    strat = MomentumStrategy(
        "momentum_1m", {"lookback": 5, "fast": 2, "slow": 4, "adx_threshold": 0}
    )
    account_state = {"positions": {}}
    for price in [100, 101, 102, 103, 104]:
        strat.on_bar({"symbol": "SPY", "close": price}, account_state)
    orders = strat.get_orders()
    assert any(order.side == "BUY" for order in orders)
