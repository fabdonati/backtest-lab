from __future__ import annotations

from backtest_lab.metrics import compute_metrics
from backtest_lab.models import BacktestResult


def generate_report(result: BacktestResult) -> str:
    metrics = compute_metrics(result)
    return "\n".join(
        [
            "Backtest Report",
            f"Ending equity: {result.ending_equity:.2f}",
            f"Total return: {metrics['total_return']:.2%}",
            f"Annualized volatility: {metrics['annualized_volatility']:.2%}",
            f"Sharpe ratio: {metrics['sharpe_ratio']:.2f}",
            f"Max drawdown: {metrics['max_drawdown']:.2%}",
            f"Trades: {result.trades}",
        ]
    )
