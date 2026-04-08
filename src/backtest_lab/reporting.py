from __future__ import annotations

from backtest_lab.metrics import compute_metrics
from backtest_lab.models import BacktestResult, SymbolSummary


def generate_report(result: BacktestResult) -> str:
    metrics = compute_metrics(result)
    lines = [
        "Backtest Report",
        f"Symbols: {result.symbol_count}",
        f"Weighting: {result.weighting_mode}",
        f"Ending equity: {result.ending_equity:.2f}",
        f"Total return: {metrics['total_return']:.2%}",
        f"Annualized volatility: {metrics['annualized_volatility']:.2%}",
        f"Sharpe ratio: {metrics['sharpe_ratio']:.2f}",
        f"Max drawdown: {metrics['max_drawdown']:.2%}",
        f"Trades: {result.trades}",
        f"Average capital turnover: {_average_turnover(result):.2%}",
    ]
    if result.symbol_summaries:
        lines.append("Symbol summary:")
        lines.extend(_format_symbol_summary(summary) for summary in result.symbol_summaries)
    return "\n".join(lines)


def _average_turnover(result: BacktestResult) -> float:
    if len(result.equity_curve) <= 1:
        return 0.0
    return sum(point.turnover for point in result.equity_curve[1:]) / (len(result.equity_curve) - 1)


def _format_symbol_summary(summary: SymbolSummary) -> str:
    return (
        f"- {summary.symbol}: weight {summary.weight:.2%}, "
        f"return {summary.total_return:.2%}, "
        f"contribution {summary.contribution:.2%}, "
        f"avg capital turnover {summary.average_capital_turnover:.2%}, "
        f"trades {summary.trades}"
    )
