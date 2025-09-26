# Testing Guide

This document outlines how to exercise the trading bot locally, both with automated checks and a manual smoke run.

## Automated tests
1. Install project dependencies using your preferred tool:
   - `uv sync`
   - **or** `poetry install`
2. (Optional) Create a baseline environment file if you intend to run runtime commands: `cp .env.example .env`.
3. Execute the full unit-test suite:
   - `pytest`
   - **or** `poetry run pytest`
   - **or** `uv run pytest`
4. Target individual test modules or cases when debugging. For example:
   - `pytest tests/test_backtest_engine.py`
   - `pytest tests/test_risk.py::test_flatten_at_close_executes_once`

## Manual smoke run
1. After installing dependencies, launch the paper-trading CLI with the sample configuration:
   ```bash
   python -m leekbot.cli run --mode paper --config leekbot/config/sample.config.yaml
   ```
2. Optionally start the FastAPI monitor alongside it to observe streaming events in the dashboard:
   ```bash
   uvicorn leekbot.api.app:app
   ```

These steps ensure both automated coverage and an end-to-end sanity check of the trading workflow.
