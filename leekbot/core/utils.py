from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def ema(values: Iterable[float], period: int) -> List[float]:
    values_list = list(values)
    if not values_list:
        return []
    alpha = 2 / (period + 1)
    ema_values = [values_list[0]]
    for value in values_list[1:]:
        ema_values.append(alpha * value + (1 - alpha) * ema_values[-1])
    return ema_values


def rolling_mean(values: Iterable[float], window: int) -> List[float]:
    arr = list(values)
    if len(arr) < window:
        return []
    means = []
    for i in range(len(arr) - window + 1):
        window_slice = arr[i : i + window]
        means.append(sum(window_slice) / window)
    return means


def rolling_std(values: Iterable[float], window: int) -> List[float]:
    arr = list(values)
    if len(arr) < window:
        return []
    stds = []
    for i in range(len(arr) - window + 1):
        window_slice = arr[i : i + window]
        mean = sum(window_slice) / window
        variance = sum((v - mean) ** 2 for v in window_slice) / window
        stds.append(variance**0.5)
    return stds


@dataclass(slots=True)
class OrderIntent:
    symbol: str
    side: str
    qty: float
    order_type: str
    price: float | None = None
    stop: float | None = None
    tag: str | None = None
