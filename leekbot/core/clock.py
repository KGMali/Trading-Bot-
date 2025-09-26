from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Dict

import pytz


@dataclass(slots=True)
class MarketSession:
    open_time: time
    close_time: time
    timezone: str
    weekend: bool = False

    def is_open(self, ts: datetime) -> bool:
        tz = pytz.timezone(self.timezone)
        local = ts.astimezone(tz)
        if not self.weekend and local.weekday() >= 5:
            return False
        return self.open_time <= local.time() <= self.close_time


DEFAULT_SESSIONS: Dict[str, MarketSession] = {
    "CRYPTO": MarketSession(time(0, 0), time(23, 59, 59), "UTC", weekend=True),
    "FX": MarketSession(time(17, 0), time(17, 0), "America/New_York", weekend=False),
    "XNYS": MarketSession(time(9, 30), time(16, 0), "America/New_York"),
    "CME": MarketSession(time(18, 0), time(17, 0), "America/Chicago", weekend=False),
}


def is_market_open(calendar: str, timestamp: datetime | None = None) -> bool:
    ts = timestamp or datetime.utcnow().replace(tzinfo=pytz.utc)
    session = DEFAULT_SESSIONS.get(calendar)
    if session is None:
        return True
    return session.is_open(ts)


def next_open_close(calendar: str, timestamp: datetime | None = None) -> tuple[datetime, datetime]:
    ts = timestamp or datetime.utcnow().replace(tzinfo=pytz.utc)
    session = DEFAULT_SESSIONS.get(calendar)
    if session is None:
        return ts, ts
    tz = pytz.timezone(session.timezone)
    local = ts.astimezone(tz)
    open_dt = tz.localize(datetime.combine(local.date(), session.open_time))
    close_dt = tz.localize(datetime.combine(local.date(), session.close_time))
    if local.time() > session.close_time:
        next_day = local + timedelta(days=1)
        open_dt = tz.localize(datetime.combine(next_day.date(), session.open_time))
        close_dt = tz.localize(datetime.combine(next_day.date(), session.close_time))
    return open_dt.astimezone(pytz.utc), close_dt.astimezone(pytz.utc)
