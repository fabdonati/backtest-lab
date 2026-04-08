# Example: `market-data-toolkit` to `backtest-lab`

This directory contains a tiny portfolio dataset in the same normalized format produced by
`market-data-toolkit`.

Files:

- `normalized.csv`: daily bars for `AAPL` and `MSFT`
- `weights.csv`: fixed symbol weights for a two-name portfolio
- `diagnostics_normalized.csv`: longer daily bars chosen to exercise exposure and hit-rate metrics
- `diagnostics_weights.csv`: fixed weights for the diagnostics example

Run it from the repo root:

```bash
python -m backtest_lab.cli examples/market_data_toolkit/normalized.csv \
  --input-format market-data-toolkit \
  --strategy moving-average \
  --short-window 2 \
  --long-window 3 \
  --weights-file examples/market_data_toolkit/weights.csv
```

You should see:

- a non-zero trade count
- average capital turnover
- one summary line per symbol

For a longer diagnostics-focused sample, run:

```bash
python -m backtest_lab.cli examples/market_data_toolkit/diagnostics_normalized.csv \
  --input-format market-data-toolkit \
  --strategy moving-average \
  --short-window 2 \
  --long-window 3 \
  --weights-file examples/market_data_toolkit/diagnostics_weights.csv
```

That example is designed so the report shows:

- non-zero hit rate
- non-zero winning and losing periods
- non-zero drawdown duration
- non-zero raw and capital turnover

You can also export the analysis artifacts from the same sample:

```bash
python -m backtest_lab.cli examples/market_data_toolkit/diagnostics_normalized.csv \
  --input-format market-data-toolkit \
  --strategy moving-average \
  --short-window 2 \
  --long-window 3 \
  --weights-file examples/market_data_toolkit/diagnostics_weights.csv \
  --equity-output data/equity_curve.csv \
  --sleeve-output-dir data/sleeves \
  --comparison-output data/comparison_curve.csv \
  --chart-output data/equity_chart.png
```

This will create:

- `data/equity_curve.csv`: portfolio equity path
- `data/sleeves/*.csv`: one equity curve per symbol sleeve
- `data/comparison_curve.csv`: strategy vs benchmark equity series
- `data/equity_chart.png`: ready-to-view plot of strategy, benchmark, and sleeve curves
