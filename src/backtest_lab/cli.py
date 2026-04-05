from __future__ import annotations

import argparse
from pathlib import Path

from backtest_lab.data import load_bars_from_csv
from backtest_lab.engine import run_backtest
from backtest_lab.reporting import generate_report
from backtest_lab.strategies import MeanReversionStrategy, MovingAverageCrossStrategy, Strategy


def main() -> None:
    parser = argparse.ArgumentParser(prog="btlab", description="Run simple strategy backtests")
    parser.add_argument("source", type=Path, help="CSV file containing daily OHLCV data")
    parser.add_argument(
        "--strategy",
        choices=("moving-average", "mean-reversion"),
        default="moving-average",
    )
    parser.add_argument("--short-window", type=int, default=3)
    parser.add_argument("--long-window", type=int, default=5)
    parser.add_argument("--lookback", type=int, default=3)
    parser.add_argument("--threshold", type=float, default=0.02)
    args = parser.parse_args()

    bars = load_bars_from_csv(args.source)
    strategy = _build_strategy(
        args.strategy,
        args.short_window,
        args.long_window,
        args.lookback,
        args.threshold,
    )
    result = run_backtest(bars, strategy.generate_signals(bars))
    print(generate_report(result))


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
