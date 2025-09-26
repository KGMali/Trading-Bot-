# LeekBot

LeekBot is a modular, multi-market trading platform designed for the L.E.E.K. server. The codebase
ships with a unified order interface, strategy framework, backtesting, and observability tooling so
you can run the same code in paper, live, and simulated modes.

## Quickstart

```bash
uv sync  # or: poetry install
cp .env.example .env
python -m leekbot.cli run --mode paper --config leekbot/config/sample.config.yaml
```

With the API service running (`uvicorn leekbot.api.app:app`), open http://localhost:8000/ to view the
real-time monitor streaming every order, cancellation, and risk event.

## Features

- Unified market data clients for equities, crypto, FX, futures, and options
- Order routing with configurable risk controls and kill switch
- Intraday day-trading protections with trade-count limits, drawdown caps, and auto-flattening
- Seven pre-defined trading styles spanning conservative to aggressive playbooks
- Event-driven backtester with performance metrics and trade log export
- Live web monitor with streaming trade, risk, and lifecycle events
- FastAPI control plane and CLI utilities for live operations

## Development

Formatting and linting use `black` and `ruff`. Tests run with `pytest` and `pytest-asyncio`.

```bash
ruff check .
black --check .
pytest
```

## Trading Styles

Review the included trading playbooks and select the profile that matches your desk's mandate:

```bash
python -m leekbot.cli styles
```

The command prints seven styles ranked by risk score, covering conservative capital preservation through
hyper-aggressive, intraday-focused deployments. Each profile lists suggested markets, strategies, and
go-to risk controls so you can wire accounts quickly across equities, ETFs, crypto, FX, futures, options,
and dedicated day-trading mandates.

## Disclaimer

This repository is provided for educational purposes only. Trading involves substantial risk.
