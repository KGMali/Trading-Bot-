from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict

import typer
import yaml

from .backtest.engine import BacktestEngine
from .config.styles import DEFAULT_TRADING_STYLES_PATH, load_trading_styles
from .core.logging import configure_logging
from .exec.router import OrderRouter
from .strat.base import load_strategy

app = typer.Typer(name="leek")


def load_config(path: Path) -> Dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@app.command()
def run(mode: str = typer.Option("paper"), config: Path = typer.Option(...)) -> None:
    cfg = load_config(config)
    configure_logging(cfg["global"]["log_dir"])
    accounts = cfg.get("accounts", [])
    router = OrderRouter.from_config(accounts)
    strategies = {
        name: load_strategy(name) for name in set(sum([acc["strategies"] for acc in accounts], []))
    }
    typer.echo(
        " ".join(
            [
                f"Running in {mode} mode",
                f"with {len(strategies)} strategies",
                f"and {len(router.routes)} routes.",
                "Live monitor available via API dashboard",
            ]
        )
    )


@app.command()
def backtest(
    config: Path = typer.Option(...),
    from_date: datetime = typer.Option(...),
    to: datetime = typer.Option(...),
) -> None:
    cfg = load_config(config)
    data_cfg = cfg.get("data", {})
    typer.echo(f"Backtesting from {from_date} to {to}")
    paths = {symbol: Path(info["path"]) for symbol, info in data_cfg.items() if "path" in info}
    engine = BacktestEngine.from_csv(paths, cfg.get("strategies", {}))
    result = engine.run()
    typer.echo(result.metrics)
    if result.trades:
        with open("backtest_trades.csv", "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=result.trades[0].keys())
            writer.writeheader()
            writer.writerows(result.trades)


@app.command()
def report(date: str = typer.Option("today")) -> None:
    typer.echo(f"Report for {date}")


@app.command()
def styles(
    path: Path = typer.Option(
        DEFAULT_TRADING_STYLES_PATH,
        exists=True,
        dir_okay=False,
        file_okay=True,
        readable=True,
        help="Path to the trading styles YAML file.",
    )
) -> None:
    """List the predefined trading styles ordered by risk score."""

    trading_styles = load_trading_styles(path)
    for style in trading_styles:
        typer.echo(
            "\n".join(
                [
                    f"[{style.risk_score}] {style.label} — {style.risk_level}",
                    f"  Markets      : {', '.join(style.target_markets)}",
                    f"  Holding Period: {style.holding_period}",
                    f"  Strategies   : {', '.join(style.recommended_strategies)}",
                    f"  Risk Controls: {style.risk_controls}",
                ]
            )
        )


if __name__ == "__main__":
    app()
