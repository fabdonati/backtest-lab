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
- Optional custom portfolio weights via CSV
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

Run a custom-weighted portfolio backtest:

```bash
btlab data/normalized.csv --input-format market-data-toolkit --strategy moving-average --weights-file data/weights.csv
```

with a weights file like:

```csv
symbol,weight
AAPL,0.5
MSFT,0.3
NVDA,0.2
```

If you prefer not to rely on the installed CLI entrypoint, you can run the module directly:

```bash
python -m backtest_lab.cli data/normalized.csv --input-format market-data-toolkit --strategy moving-average --weights-file data/weights.csv
```

Run a mean-reversion backtest:

```bash
btlab data/prices.csv --strategy mean-reversion --lookback 4 --threshold 0.03
```

## Quick weighted example

This example is intentionally four bars long so the moving-average strategy has enough history
to generate a signal and one additional bar to act on it.

```csv
symbol,timestamp,open,high,low,close,volume
AAPL,2025-01-02T00:00:00,99,101,98,100,1000
AAPL,2025-01-03T00:00:00,100,103,99,102,1000
AAPL,2025-01-04T00:00:00,102,104,101,103,1000
AAPL,2025-01-05T00:00:00,103,106,102,105,1000
MSFT,2025-01-02T00:00:00,199,201,198,200,1000
MSFT,2025-01-03T00:00:00,200,202,199,201,1000
MSFT,2025-01-04T00:00:00,201,203,200,202,1000
MSFT,2025-01-05T00:00:00,202,205,201,204,1000
```

With a weights file like:

```csv
symbol,weight
AAPL,0.75
MSFT,0.25
```

run:

```bash
python -m backtest_lab.cli data/portfolio.csv \
  --input-format market-data-toolkit \
  --strategy moving-average \
  --short-window 2 \
  --long-window 3 \
  --weights-file data/weights.csv
```

You should now see a non-zero trade count and equity that moves away from the initial cash balance.

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
- Portfolio weighting supports equal-weight or explicit fixed symbol weights
- Signals are applied on the following bar, so very short samples may produce zero trades
