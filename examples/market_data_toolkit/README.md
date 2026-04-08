# Example: `market-data-toolkit` to `backtest-lab`

This directory contains a tiny portfolio dataset in the same normalized format produced by
`market-data-toolkit`.

Files:

- `normalized.csv`: daily bars for `AAPL` and `MSFT`
- `weights.csv`: fixed symbol weights for a two-name portfolio

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
