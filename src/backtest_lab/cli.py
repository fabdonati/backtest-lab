from __future__ import annotations

import argparse
from pathlib import Path

from backtest_lab.data import (
    load_bars_from_csv,
    load_bars_from_market_data_csv,
    load_symbol_weights,
)
from backtest_lab.engine import run_portfolio_backtest
from backtest_lab.models import DailyBar
from backtest_lab.reporting import generate_report, write_metrics_csv
from backtest_lab.strategies import MeanReversionStrategy, MovingAverageCrossStrategy, Strategy


def main() -> None:
    parser = argparse.ArgumentParser(prog="btlab", description="Run simple strategy backtests")
    parser.add_argument("source", type=Path, help="CSV file containing daily OHLCV data")
    parser.add_argument(
        "--input-format",
        choices=("daily-csv", "market-data-toolkit"),
        default="daily-csv",
    )
    parser.add_argument(
        "--strategy",
        choices=("moving-average", "mean-reversion"),
        default="moving-average",
    )
    parser.add_argument("--short-window", type=int, default=3)
    parser.add_argument("--long-window", type=int, default=5)
    parser.add_argument("--lookback", type=int, default=3)
    parser.add_argument("--threshold", type=float, default=0.02)
    parser.add_argument("--weights-file", type=Path)
    parser.add_argument("--metrics-output", type=Path)
    args = parser.parse_args()

    bars = _load_bars(args.source, args.input_format)
    weights = load_symbol_weights(args.weights_file) if args.weights_file is not None else None
    strategy = _build_strategy(
        args.strategy,
        args.short_window,
        args.long_window,
        args.lookback,
        args.threshold,
    )
    result = run_portfolio_backtest(
        bars,
        strategy.generate_signals(bars),
        symbol_weights=weights,
    )
    if args.metrics_output is not None:
        write_metrics_csv(result, args.metrics_output)
    print(generate_report(result))


def _load_bars(source: Path, input_format: str) -> list[DailyBar]:
    if input_format == "market-data-toolkit":
        return load_bars_from_market_data_csv(source)
    return load_bars_from_csv(source)


def _build_strategy(
    strategy_name: str,
    short_window: int,
    long_window: int,
    lookback: int,
    threshold: float,
) -> Strategy:
    if strategy_name == "mean-reversion":
        return MeanReversionStrategy(lookback=lookback, threshold=threshold)
    return MovingAverageCrossStrategy(short_window=short_window, long_window=long_window)


if __name__ == "__main__":
    main()
