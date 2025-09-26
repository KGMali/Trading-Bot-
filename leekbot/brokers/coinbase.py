from __future__ import annotations

from .simulated import SimulatedBroker


class Broker(SimulatedBroker):
    def __init__(self) -> None:
        super().__init__("${name}")
