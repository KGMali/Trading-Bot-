"""Utility helpers for loading pre-defined trading styles."""

from __future__ import annotations

import json
from dataclasses import MISSING, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - fallback for environments without PyYAML
    yaml = None  # type: ignore[assignment]


@dataclass(slots=True)
class TradingStyle:
    """Describes a risk profile and execution template for a desk."""

    name: str
    label: str
    risk_score: int
    risk_level: str
    description: str
    holding_period: str
    target_markets: List[str]
    recommended_strategies: List[str]
    position_sizing: Dict[str, Any]
    risk_controls: Dict[str, Any]
    notes: str | None = None

    def to_summary(self) -> Dict[str, Any]:
        """Return a printable summary representation."""

        return {
            "name": self.name,
            "label": self.label,
            "risk_level": self.risk_level,
            "holding_period": self.holding_period,
            "target_markets": ", ".join(self.target_markets),
            "strategies": ", ".join(self.recommended_strategies),
            "risk_controls": self.risk_controls,
        }


DEFAULT_TRADING_STYLES_PATH = Path(__file__).with_name("trading_styles.yaml")


def _coerce_style(record: Dict[str, Any]) -> TradingStyle:
    missing = {
        name
        for name, field in TradingStyle.__dataclass_fields__.items()
        if field.default is MISSING
        and getattr(field, "default_factory", MISSING) is MISSING
        and name not in record
    }
    if missing:
        raise ValueError(f"Trading style definition missing required keys: {missing}")
    return TradingStyle(**record)


def load_trading_styles(path: Path | None = None) -> List[TradingStyle]:
    """Load trading styles from a YAML (or JSON) file sorted by risk score."""

    path = path or DEFAULT_TRADING_STYLES_PATH
    raw_text = path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(raw_text) or {}
    else:  # pragma: no cover - executed only when PyYAML is unavailable
        data = json.loads(raw_text) or {}
    styles: Iterable[Dict[str, Any]] = data.get("styles", [])
    trading_styles = [_coerce_style(entry) for entry in styles]
    return sorted(trading_styles, key=lambda style: style.risk_score)


def get_trading_style(name: str, styles: Iterable[TradingStyle] | None = None) -> TradingStyle:
    """Return a trading style by name, reloading definitions if necessary."""

    if styles is None:
        styles = load_trading_styles()
    normalized = name.lower()
    for style in styles:
        if style.name.lower() == normalized or style.label.lower() == normalized:
            return style
    raise KeyError(f"Trading style '{name}' not found")
