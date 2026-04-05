from __future__ import annotations

from collections import deque
from statistics import fmean
from typing import Protocol

from backtest_lab.models import DailyBar, Signal


class Strategy(Protocol):
    def generate_signals(self, bars: list[DailyBar]) -> list[Signal]:
        ...


class MovingAverageCrossStrategy:
    def __init__(self, short_window: int = 3, long_window: int = 5) -> None:
        if short_window >= long_window:
            raise ValueError("short_window must be smaller than long_window")
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, bars: list[DailyBar]) -> list[Signal]:
        short: deque[float] = deque(maxlen=self.short_window)
        long: deque[float] = deque(maxlen=self.long_window)
        signals: list[Signal] = []

        for bar in sorted(bars, key=lambda item: item.date):
            short.append(bar.close)
            long.append(bar.close)
            if len(long) < self.long_window:
                signals.append(Signal(date=bar.date, target_weight=0.0))
                continue

            target = 1.0 if fmean(short) > fmean(long) else 0.0
            signals.append(Signal(date=bar.date, target_weight=target))

        return signals


class MeanReversionStrategy:
    def __init__(self, lookback: int = 3, threshold: float = 0.02) -> None:
        if lookback <= 1:
            raise ValueError("lookback must be greater than 1")
        self.lookback = lookback
        self.threshold = threshold

    def generate_signals(self, bars: list[DailyBar]) -> list[Signal]:
        window: deque[float] = deque(maxlen=self.lookback)
        signals: list[Signal] = []

        for bar in sorted(bars, key=lambda item: item.date):
            window.append(bar.close)
            if len(window) < self.lookback:
                signals.append(Signal(date=bar.date, target_weight=0.0))
                continue

            mean_close = fmean(window)
            target = 1.0 if bar.close <= mean_close * (1.0 - self.threshold) else 0.0
            signals.append(Signal(date=bar.date, target_weight=target))

        return signals
