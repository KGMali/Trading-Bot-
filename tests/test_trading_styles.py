from pathlib import Path

import pytest

from leekbot.config.styles import (
    DEFAULT_TRADING_STYLES_PATH,
    TradingStyle,
    get_trading_style,
    load_trading_styles,
)


def test_load_trading_styles_returns_seven_sorted_styles() -> None:
    styles = load_trading_styles()
    assert len(styles) == 7
    assert styles == sorted(styles, key=lambda style: style.risk_score)
    assert styles[0].risk_level == "Conservative"
    assert styles[-1].risk_level == "Very Aggressive"


@pytest.mark.parametrize(
    "name",
    [
        "intraday_precision_day_trading",
        "Intraday Precision (Day Trading)",
        "OPPORTUNISTIC_HYPERDRIVE",
    ],
)
def test_get_trading_style_lookup_is_case_insensitive(name: str) -> None:
    styles = load_trading_styles()
    style = get_trading_style(name, styles)
    assert isinstance(style, TradingStyle)


def test_trading_styles_file_exists() -> None:
    assert Path(DEFAULT_TRADING_STYLES_PATH).exists()
