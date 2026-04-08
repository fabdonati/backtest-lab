from __future__ import annotations

from datetime import date

from backtest_lab.engine import run_backtest, run_portfolio_backtest
from backtest_lab.models import DailyBar, Signal
from backtest_lab.reporting import generate_report


def test_generate_report_includes_key_metrics() -> None:
    bars = [
        DailyBar(date(2025, 1, 2), "AAPL", 99, 101, 98, 100, 1_000),
        DailyBar(date(2025, 1, 3), "AAPL", 100, 102, 99, 101, 1_000),
        DailyBar(date(2025, 1, 4), "AAPL", 101, 103, 100, 102, 1_000),
    ]
    result = run_backtest(bars, [Signal(date(2025, 1, 2), "AAPL", 1.0)])

    report = generate_report(result)

    assert "Backtest Report" in report
    assert "Symbols: 1" in report
    assert "Weighting: equal-weight" in report
    assert "Ending equity" in report
    assert "Sharpe ratio" in report


def test_generate_report_includes_symbol_summary_for_portfolios() -> None:
    bars = [
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
        bars,
        signals,
        transaction_cost_bps=0.0,
        slippage_bps=0.0,
        symbol_weights={"AAPL": 0.75, "MSFT": 0.25},
    )

    report = generate_report(result)

    assert "Average capital turnover" in report
    assert "Symbol summary:" in report
    assert "- AAPL: weight 75.00%" in report
    assert "contribution 1.50%" in report
    assert "avg capital turnover 75.00%" in report
