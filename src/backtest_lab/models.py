from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class DailyBar:
    date: date
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True, slots=True)
class Signal:
    date: date
    symbol: str
    target_weight: float


@dataclass(frozen=True, slots=True)
class EquityPoint:
    date: date
    equity: float
    position: float
    turnover: float


@dataclass(frozen=True, slots=True)
class BacktestResult:
    equity_curve: list[EquityPoint]
    total_return: float
    ending_equity: float
    trades: int
    symbol_count: int = 1
