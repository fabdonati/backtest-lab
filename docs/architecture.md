# Architecture Notes

## Design goals

- Keep the backtest path deterministic and easy to audit
- Separate strategy logic from execution/accounting
- Avoid hidden lookahead assumptions

## Components

- `data.py`: parses daily OHLCV CSV inputs
- `data.py`: parses both native daily CSVs and normalized `market-data-toolkit` exports
- `strategies.py`: produces target-weight signals from price history
- `engine.py`: applies signals to a daily equity curve
- `portfolio.py`: houses trading-friction helpers
- `metrics.py`: computes risk and performance summaries
- `reporting.py`: renders a text report

## Execution model

Signals are generated from information available on a bar's date, then applied to the next
return step. That keeps the basic loop closer to a realistic end-of-day workflow:

1. observe the close for day `t`
2. generate a target weight for day `t`
3. apply that position over the return from `t` to `t+1`

This also means tiny toy datasets can legitimately show zero trades. For example, with a
3-day moving-average setup and only 3 bars of data, the strategy can produce its first
non-zero signal on day 3, but there is no day 4 return on which to apply it.

## Trading friction

The current model uses basis-point transaction costs and slippage. Those costs are charged
when the target position changes, scaled by turnover.

## Scope

This repo is intentionally small. The focus is correctness, signal alignment, and clear APIs,
not production-grade brokerage modeling.

## Multi-asset behavior

The portfolio path groups bars by symbol, runs the single-name execution logic per symbol, and
then combines the resulting equity curves into a portfolio result. By default this is equal-weight,
but the CLI can also load explicit fixed symbol weights from a small CSV file. That keeps the
execution semantics simple while still allowing cross-symbol strategy evaluation from one dataset.
The reporting layer surfaces exposure, drawdown duration, hit rate, per-symbol return
contribution, raw signal turnover, and capital turnover so the portfolio summary is easier to
inspect without opening the underlying CSV inputs. Turnover is expressed in capital terms, so
larger symbol allocations contribute more to the reported turnover when they rebalance, while raw
signal turnover remains useful for debugging how often a strategy actually flips its target weights.
The CLI can also export these same diagnostics to a simple CSV file for downstream analysis.
