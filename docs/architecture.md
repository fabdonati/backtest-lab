# Architecture Notes

## Design goals

- Keep the backtest path deterministic and easy to audit
- Separate strategy logic from execution/accounting
- Avoid hidden lookahead assumptions

## Components

- `data.py`: parses daily OHLCV CSV inputs
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

## Trading friction

The current model uses basis-point transaction costs and slippage. Those costs are charged
when the target position changes, scaled by turnover.

## Scope

This repo is intentionally small. The focus is correctness, signal alignment, and clear APIs,
not production-grade brokerage modeling.
