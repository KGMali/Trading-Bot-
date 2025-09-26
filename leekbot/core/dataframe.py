from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Iterator, List


def date_range(
    start: datetime,
    end: datetime | None = None,
    periods: int | None = None,
    freq: str = "1min",
) -> List[datetime]:
    if periods is None and end is None:
        raise ValueError("Either end or periods must be provided")
    if freq != "1min":
        raise ValueError("Only 1min frequency supported in lightweight implementation")
    delta = timedelta(minutes=1)
    current = start
    result: List[datetime] = []
    if end is not None:
        while current <= end:
            result.append(current)
            current += delta
    else:
        for _ in range(periods or 0):
            result.append(current)
            current += delta
    return result


class _LocAccessor:
    def __init__(self, data: Dict[datetime, Dict[str, float]]) -> None:
        self._data = data

    def __getitem__(self, key: datetime) -> Dict[str, float]:
        return self._data[key]


@dataclass
class MiniDataFrame:
    rows: List[Dict[str, float]]
    index: List[datetime]

    def __post_init__(self) -> None:
        self._map = {idx: row for idx, row in zip(self.index, self.rows)}
        self.loc = _LocAccessor(self._map)

    def __iter__(self) -> Iterator[Dict[str, float]]:
        for idx in self.index:
            yield self._map[idx]

    def to_dicts(self) -> List[Dict[str, float]]:
        return list(self.rows)
