from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List


class BrokerClient(ABC):
    @abstractmethod
    def place_order(self, account: str, order: Dict) -> Dict:
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, account: str, order_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_positions(self, account: str) -> List[Dict]:
        raise NotImplementedError

    @abstractmethod
    def get_balance(self, account: str) -> Dict:
        raise NotImplementedError

    def cancel_open_orders(self, account: str) -> None:
        return None

    def flatten_positions(self, account: str) -> None:
        return None
