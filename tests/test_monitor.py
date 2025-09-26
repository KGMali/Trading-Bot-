from __future__ import annotations

import asyncio
from contextlib import suppress

from leekbot.monitor import monitor


def test_monitor_snapshot_records_events() -> None:
    monitor.reset()
    event = monitor.record_event("order", {"symbol": "SPY"})
    snapshot = monitor.snapshot()
    assert snapshot[-1].id == event.id
    assert snapshot[-1].payload["symbol"] == "SPY"


def test_monitor_stream_emits_new_events() -> None:
    monitor.reset()

    async def runner() -> None:
        async def publish() -> None:
            await asyncio.sleep(0.01)
            monitor.record_event("risk", {"account": "acct", "reason": "max_dd"})

        publisher = asyncio.create_task(publish())
        stream = monitor.stream()
        try:
            event = await asyncio.wait_for(stream.__anext__(), timeout=1)
            assert event.category == "risk"
            assert event.payload["reason"] == "max_dd"
        finally:
            publisher.cancel()
            with suppress(asyncio.CancelledError):
                await publisher

    asyncio.run(runner())
