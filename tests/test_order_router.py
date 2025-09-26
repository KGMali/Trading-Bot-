from __future__ import annotations

import os

from leekbot.core.utils import OrderIntent
from leekbot.exec.router import OrderRouter


def test_order_router_submits_orders(tmp_path) -> None:
    os.makedirs("logs", exist_ok=True)
    accounts = [{"name": "acct", "venue": "alpaca", "strategies": ["momentum_1m"]}]
    router = OrderRouter.from_config(accounts)
    order_ids = router.submit_orders("momentum_1m", [OrderIntent("SPY", "BUY", 1, "market")])
    assert len(order_ids) == 1
