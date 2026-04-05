from __future__ import annotations

from math import sqrt
from statistics import fmean

from backtest_lab.models import BacktestResult


def compute_metrics(result: BacktestResult) -> dict[str, float]:
    returns = _daily_returns(result)
    if not returns:
        return {
            "total_return": result.total_return,
            "annualized_volatility": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
        }

    mean_return = fmean(returns)
    variance = sum((value - mean_return) ** 2 for value in returns) / len(returns)
    volatility = sqrt(variance) * sqrt(252)
    sharpe = 0.0 if volatility == 0 else (mean_return * 252) / volatility

    return {
        "total_return": result.total_return,
        "annualized_volatility": volatility,
        "sharpe_ratio": sharpe,
        "max_drawdown": _max_drawdown(result),
    }


def _daily_returns(result: BacktestResult) -> list[float]:
    returns: list[float] = []
    curve = result.equity_curve
    for previous_point, current_point in zip(curve, curve[1:], strict=False):
        returns.append((current_point.equity / previous_point.equity) - 1.0)
    return returns


def _max_drawdown(result: BacktestResult) -> float:
    peak = result.equity_curve[0].equity
    max_drawdown = 0.0
    for point in result.equity_curve:
        peak = max(peak, point.equity)
        drawdown = (point.equity / peak) - 1.0
        max_drawdown = min(max_drawdown, drawdown)
    return abs(max_drawdown)
