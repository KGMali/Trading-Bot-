from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List

from ..core.utils import OrderIntent


class Strategy(ABC):
    def __init__(self, name: str, config: Dict | None = None) -> None:
        self.name = name
        self.config = config or {}

    @abstractmethod
    def on_bar(self, bar: Dict, account_state: Dict) -> None:
        raise NotImplementedError

    def on_fill(self, fill: Dict, account_state: Dict) -> None:
        return None

    @abstractmethod
    def get_orders(self) -> List[OrderIntent]:
        raise NotImplementedError


def load_strategy(name: str, config: Dict | None = None) -> Strategy:
    from . import (
        breakout_volexp,
        momentum_1m,
        options_short_strangle,
        orb_breakout,
        pairs_stat_arb,
        vix_hedge_overlay,
        vol_reversion_vix,
        vol_trend_vix,
        vwap_reversion,
    )

    mapping = {
        "momentum_1m": momentum_1m.MomentumStrategy,
        "vwap_reversion": vwap_reversion.VWAPReversionStrategy,
        "orb_breakout": orb_breakout.ORBStrategy,
        "breakout_volexp": breakout_volexp.BreakoutVolExpansion,
        "pairs_stat_arb": pairs_stat_arb.PairsStatArb,
        "vol_trend_vix": vol_trend_vix.VolTrendStrategy,
        "vol_reversion_vix": vol_reversion_vix.VolReversionStrategy,
        "options_short_strangle": options_short_strangle.ShortStrangleStrategy,
        "vix_hedge_overlay": vix_hedge_overlay.VIXHedgeOverlay,
    }
    if name not in mapping:
        raise ValueError(f"Unknown strategy {name}")
    return mapping[name](name, config)
