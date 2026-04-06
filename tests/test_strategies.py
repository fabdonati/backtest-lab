from __future__ import annotations

from datetime import date

from backtest_lab.models import DailyBar
from backtest_lab.strategies import MeanReversionStrategy, MovingAverageCrossStrategy


def _bars(closes: list[float]) -> list[DailyBar]:
    return [
        DailyBar(date(2025, 1, day), "AAPL", close - 1, close + 1, close - 2, close, 1_000)
        for day, close in enumerate(closes, start=2)
    ]


def test_moving_average_cross_strategy_waits_for_long_window() -> None:
    strategy = MovingAverageCrossStrategy(short_window=2, long_window=3)

    signals = strategy.generate_signals(_bars([100, 101, 105, 106]))

    assert [signal.symbol for signal in signals] == ["AAPL", "AAPL", "AAPL", "AAPL"]
    assert [signal.target_weight for signal in signals] == [0.0, 0.0, 1.0, 1.0]


def test_mean_reversion_strategy_flags_large_dips() -> None:
    strategy = MeanReversionStrategy(lookback=3, threshold=0.03)

    signals = strategy.generate_signals(_bars([100, 101, 95, 100]))

    assert [signal.target_weight for signal in signals] == [0.0, 0.0, 1.0, 0.0]


def test_strategies_handle_multiple_symbols_independently() -> None:
    strategy = MovingAverageCrossStrategy(short_window=2, long_window=3)
    bars = _bars([100, 101, 105]) + [
        DailyBar(date(2025, 1, 2), "MSFT", 49, 51, 48, 50, 1_000),
        DailyBar(date(2025, 1, 3), "MSFT", 50, 51, 49, 50, 1_000),
        DailyBar(date(2025, 1, 4), "MSFT", 50, 51, 49, 49, 1_000),
    ]

    signals = strategy.generate_signals(bars)

    assert [signal.symbol for signal in signals] == ["AAPL", "AAPL", "AAPL", "MSFT", "MSFT", "MSFT"]
