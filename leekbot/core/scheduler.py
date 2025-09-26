from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List

from croniter import croniter

from .clock import next_open_close


@dataclass(slots=True)
class ScheduledTask:
    name: str
    cron: str
    callback: Callable[[], None]
    next_run: datetime


class Scheduler:
    def __init__(self) -> None:
        self.tasks: Dict[str, ScheduledTask] = {}

    def add_cron(self, name: str, cron_expr: str, callback: Callable[[], None]) -> None:
        base = datetime.utcnow()
        self.tasks[name] = ScheduledTask(
            name, cron_expr, callback, croniter(cron_expr, base).get_next(datetime)
        )

    def due_tasks(self, now: datetime | None = None) -> List[ScheduledTask]:
        current = now or datetime.utcnow()
        due: List[ScheduledTask] = []
        for task in self.tasks.values():
            if current >= task.next_run:
                due.append(task)
                task.next_run = croniter(task.cron, current).get_next(datetime)
        return due

    def schedule_rollover(
        self, symbol: str, calendar: str, callback: Callable[[str], None]
    ) -> None:
        open_dt, close_dt = next_open_close(calendar)
        name = f"rollover:{symbol}"
        self.tasks[name] = ScheduledTask(name, "0 17 * * 5", lambda: callback(symbol), close_dt)
