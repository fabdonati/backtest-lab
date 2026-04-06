# backtest-lab

`backtest-lab` is a compact Python backtesting engine for daily strategy research.

## Why this project

Backtests often start as one-off notebooks and end up carrying real decision-making weight.
This project packages a small, deterministic research loop with reusable strategies,
transaction-cost handling, metrics, and CLI execution.

## Features

- Daily-bar CSV loader
- Loader for normalized `market-data-toolkit` exports
- Deterministic backtest engine with position changes applied on the following session
- Trading-friction model using transaction cost and slippage basis points
- Two sample strategies:
  - moving-average crossover
  - mean reversion
- Equal-weight multi-asset portfolio backtesting
- Metrics and text report generation
- CLI entrypoint for running local datasets

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## CLI usage

Run a moving-average crossover backtest:

```bash
btlab data/prices.csv --strategy moving-average --short-window 3 --long-window 5
```

Run a portfolio backtest directly from `market-data-toolkit` output:

```bash
btlab data/normalized.csv --input-format market-data-toolkit --strategy moving-average --short-window 3 --long-window 5
```

Run a mean-reversion backtest:

```bash
btlab data/prices.csv --strategy mean-reversion --lookback 4 --threshold 0.03
```

## Package usage

```python
from backtest_lab.data import load_bars_from_csv
from backtest_lab.engine import run_backtest
from backtest_lab.strategies import MovingAverageCrossStrategy

bars = load_bars_from_csv("data/prices.csv")
strategy = MovingAverageCrossStrategy(short_window=3, long_window=5)
result = run_backtest(bars, strategy.generate_signals(bars))
```

For multi-symbol workflows, use `run_portfolio_backtest()` with a dataset that includes multiple
symbols.

## Limitations

- v0.1.0 assumes a single daily dataset at a time
- Only long/flat target weights are supported in the bundled strategies
- Reporting is text-first rather than chart-first
- Portfolio aggregation is currently equal-weight rather than risk-weighted
