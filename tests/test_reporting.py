from __future__ import annotations

from datetime import date

from backtest_lab.engine import run_backtest
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
