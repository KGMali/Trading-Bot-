from __future__ import annotations

import asyncio
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List

from ..core.utils import utcnow


@dataclass(slots=True)
class MonitorEvent:
    """Represents a single event emitted by the trading platform."""

    id: int
    timestamp: datetime
    category: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "category": self.category,
            "payload": self.payload,
        }


class LiveTradeMonitor:
    """Thread-safe event bus feeding the live dashboard and API."""

    def __init__(self, max_events: int = 1000) -> None:
        self._max_events = max_events
        self._events: List[MonitorEvent] = []
        self._counter = 0
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)

    def record_event(self, category: str, payload: Dict[str, Any]) -> MonitorEvent:
        with self._condition:
            self._counter += 1
            event = MonitorEvent(
                id=self._counter,
                timestamp=utcnow(),
                category=category,
                payload=payload,
            )
            self._events.append(event)
            if len(self._events) > self._max_events:
                # keep the newest max_events entries
                self._events = self._events[-self._max_events :]
            self._condition.notify_all()
            return event

    def snapshot(self) -> List[MonitorEvent]:
        with self._lock:
            return list(self._events)

    def reset(self) -> None:
        with self._condition:
            self._events.clear()
            self._counter = 0
            self._condition.notify_all()

    def _wait_for_event(self, last_id: int) -> MonitorEvent:
        with self._condition:
            while not self._events or self._events[-1].id <= last_id:
                self._condition.wait()
            for event in self._events:
                if event.id > last_id:
                    return event
            return self._events[-1]

    async def stream(self, after_id: int = 0) -> AsyncGenerator[MonitorEvent, None]:
        last_id = after_id
        loop = asyncio.get_running_loop()
        while True:
            event = await loop.run_in_executor(None, self._wait_for_event, last_id)
            last_id = event.id
            yield event
