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
            "average_exposure": _average_exposure(result),
            "max_exposure": _max_exposure(result),
            "max_drawdown_duration": 0.0,
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
        "average_exposure": _average_exposure(result),
        "max_exposure": _max_exposure(result),
        "max_drawdown_duration": float(_max_drawdown_duration(result)),
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


def _average_exposure(result: BacktestResult) -> float:
    if len(result.equity_curve) <= 1:
        return abs(result.equity_curve[0].position)
    invested_points = result.equity_curve[1:]
    return sum(abs(point.position) for point in invested_points) / len(invested_points)


def _max_exposure(result: BacktestResult) -> float:
    return max(abs(point.position) for point in result.equity_curve)


def _max_drawdown_duration(result: BacktestResult) -> int:
    peak = result.equity_curve[0].equity
    current_duration = 0
    max_duration = 0
    for point in result.equity_curve:
        if point.equity >= peak:
            peak = point.equity
            current_duration = 0
        else:
            current_duration += 1
            max_duration = max(max_duration, current_duration)
    return max_duration
