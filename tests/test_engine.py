from __future__ import annotations

from datetime import date

import pytest

from backtest_lab.engine import run_backtest, run_portfolio_backtest
from backtest_lab.models import DailyBar, Signal


@pytest.fixture
def bars() -> list[DailyBar]:
    closes = [100.0, 101.0, 103.0, 102.0, 104.0]
    return [
        DailyBar(date(2025, 1, day), "AAPL", close - 1, close + 1, close - 2, close, 1_000)
        for day, close in enumerate(closes, start=2)
    ]


def test_run_backtest_applies_previous_day_signal(bars: list[DailyBar]) -> None:
    signals = [
        Signal(date(2025, 1, 2), "AAPL", 1.0),
        Signal(date(2025, 1, 4), "AAPL", 0.0),
    ]

    result = run_backtest(bars, signals, transaction_cost_bps=0.0, slippage_bps=0.0)

    assert result.trades == 2
    assert result.equity_curve[1].position == pytest.approx(1.0)
    assert result.equity_curve[1].equity == pytest.approx(10_100.0)
    assert result.equity_curve[3].position == pytest.approx(0.0)
    assert result.ending_equity == pytest.approx(10_300.0)


def test_run_backtest_charges_trading_friction(bars: list[DailyBar]) -> None:
    signals = [Signal(bar.date, bar.symbol, 1.0) for bar in bars[:1]]

    frictionless = run_backtest(bars, signals, transaction_cost_bps=0.0, slippage_bps=0.0)
    with_costs = run_backtest(bars, signals, transaction_cost_bps=10.0, slippage_bps=5.0)

    assert with_costs.ending_equity < frictionless.ending_equity


def test_run_backtest_rejects_empty_bar_sequences() -> None:
    with pytest.raises(ValueError, match="bars must not be empty"):
        run_backtest([], [])


def test_run_portfolio_backtest_combines_symbol_equity_curves() -> None:
    portfolio_bars = [
        DailyBar(date(2025, 1, 2), "AAPL", 99, 101, 98, 100, 1_000),
        DailyBar(date(2025, 1, 3), "AAPL", 100, 103, 99, 102, 1_000),
        DailyBar(date(2025, 1, 2), "MSFT", 199, 201, 198, 200, 1_000),
        DailyBar(date(2025, 1, 3), "MSFT", 200, 202, 199, 201, 1_000),
    ]
    signals = [
        Signal(date(2025, 1, 2), "AAPL", 1.0),
        Signal(date(2025, 1, 2), "MSFT", 1.0),
    ]

    result = run_portfolio_backtest(
        portfolio_bars,
        signals,
        transaction_cost_bps=0.0,
        slippage_bps=0.0,
    )

    assert result.symbol_count == 2
    assert result.trades == 2
    assert result.ending_equity == pytest.approx(10_125.0)
    assert result.weighting_mode == "equal-weight"


def test_run_portfolio_backtest_respects_custom_weights() -> None:
    portfolio_bars = [
        DailyBar(date(2025, 1, 2), "AAPL", 99, 101, 98, 100, 1_000),
        DailyBar(date(2025, 1, 3), "AAPL", 100, 103, 99, 102, 1_000),
        DailyBar(date(2025, 1, 2), "MSFT", 199, 201, 198, 200, 1_000),
        DailyBar(date(2025, 1, 3), "MSFT", 200, 202, 199, 201, 1_000),
    ]
    signals = [
        Signal(date(2025, 1, 2), "AAPL", 1.0),
        Signal(date(2025, 1, 2), "MSFT", 1.0),
    ]

    result = run_portfolio_backtest(
        portfolio_bars,
        signals,
        transaction_cost_bps=0.0,
        slippage_bps=0.0,
        symbol_weights={"AAPL": 0.75, "MSFT": 0.25},
    )

    assert result.weighting_mode == "custom"
    assert result.ending_equity == pytest.approx(10_162.5)


def test_run_portfolio_backtest_rejects_missing_weight_symbols() -> None:
    portfolio_bars = [
        DailyBar(date(2025, 1, 2), "AAPL", 99, 101, 98, 100, 1_000),
        DailyBar(date(2025, 1, 3), "AAPL", 100, 103, 99, 102, 1_000),
        DailyBar(date(2025, 1, 2), "MSFT", 199, 201, 198, 200, 1_000),
        DailyBar(date(2025, 1, 3), "MSFT", 200, 202, 199, 201, 1_000),
    ]
    signals = [
        Signal(date(2025, 1, 2), "AAPL", 1.0),
        Signal(date(2025, 1, 2), "MSFT", 1.0),
    ]

    with pytest.raises(ValueError, match="missing symbols"):
        run_portfolio_backtest(portfolio_bars, signals, symbol_weights={"AAPL": 1.0})
