# backtest-lab

`backtest-lab` is a compact Python backtesting engine for daily strategy research.

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
- Metrics and text report generation with exposure, drawdown, hit-rate, per-symbol win/loss summaries, raw signal turnover, and capital-turnover summaries
- Exportable portfolio equity curves, benchmark comparison curves, per-symbol sleeve curves, and PNG charts
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

Write the same portfolio metrics to a CSV file for later inspection:

```bash
python -m backtest_lab.cli data/normalized.csv \
  --input-format market-data-toolkit \
  --strategy moving-average \
  --weights-file data/weights.csv \
  --metrics-output data/report_metrics.csv
```

Export the portfolio curve, per-symbol sleeve curves, a benchmark comparison curve, and a PNG chart:

```bash
python -m backtest_lab.cli data/normalized.csv \
  --input-format market-data-toolkit \
  --strategy moving-average \
  --weights-file data/weights.csv \
  --equity-output data/equity_curve.csv \
  --sleeve-output-dir data/sleeves \
  --comparison-output data/comparison_curve.csv \
  --chart-output data/equity_chart.png
```

## Outputs

The terminal report and exported files serve different purposes:

- terminal report
  - `Average exposure` and `Max exposure` show how much portfolio capital was deployed over time
  - `Max drawdown` and `Max drawdown duration` show the worst peak-to-trough pain and how long recovery took
  - `Hit rate`, `Winning periods`, `Losing periods`, and `Flat periods` summarize realized active periods
  - `Average raw signal turnover` shows how often signals changed without regard to position sizing
  - `Average capital turnover` shows how much capital actually moved after weights are applied
- `--metrics-output`
  - writes the same summary information in row form for spreadsheets or later analysis
- `--equity-output`
  - writes the portfolio equity curve over time
- `--comparison-output`
  - writes strategy equity beside the weighted buy-and-hold benchmark
- `--sleeve-output-dir`
  - writes one sleeve curve per symbol so you can inspect which allocation drove the result
- `--chart-output`
  - creates a single PNG overlay for a quick performance read without opening a notebook

Typical inspection order:

1. read the terminal report for aggregate behavior
2. inspect `comparison_curve.csv` to see whether the strategy added value relative to buy-and-hold
3. inspect sleeve curves to see whether performance came from one symbol or from broad participation
4. open the PNG chart for a fast visual check of path shape and drawdown clustering

Run a mean-reversion backtest:

```bash
btlab data/prices.csv --strategy mean-reversion --lookback 4 --threshold 0.03
```

## Quick weighted example

This example uses four bars so the moving-average strategy has enough history to generate a
signal and one additional bar on which to apply it.

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

## End-to-end example with `market-data-toolkit`

The repo now includes a small ready-to-run example under
[`examples/market_data_toolkit`](/Users/fabrizio/Dev/Finance/backtest-lab/examples/market_data_toolkit/README.md).

From the repo root:

```bash
python -m backtest_lab.cli examples/market_data_toolkit/normalized.csv \
  --input-format market-data-toolkit \
  --strategy moving-average \
  --short-window 2 \
  --long-window 3 \
  --weights-file examples/market_data_toolkit/weights.csv
```

That example uses the same normalized column layout produced by `market-data-toolkit`,
so it mirrors the real workflow without requiring a live data fetch each time.

If you want a plot-ready artifact check from the terminal, this is the fastest one:

```bash
sed -n '1,10p' data/comparison_curve.csv
```

You should see date-aligned columns for the strategy curve and the benchmark curve. That file is the
right starting point for any later notebook or dashboard work.

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
