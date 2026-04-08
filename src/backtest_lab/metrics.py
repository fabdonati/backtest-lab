from __future__ import annotations

from math import sqrt
from statistics import fmean

from backtest_lab.models import BacktestResult


def compute_metrics(result: BacktestResult) -> dict[str, float]:
    returns = _daily_returns(result)
    win_loss = _win_loss_summary(result)
    if not returns:
        return {
            "total_return": result.total_return,
            "annualized_volatility": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "average_exposure": _average_exposure(result),
            "max_exposure": _max_exposure(result),
            "max_drawdown_duration": 0.0,
            "hit_rate": win_loss["hit_rate"],
            "winning_periods": win_loss["winning_periods"],
            "losing_periods": win_loss["losing_periods"],
            "flat_periods": win_loss["flat_periods"],
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
        "hit_rate": win_loss["hit_rate"],
        "winning_periods": win_loss["winning_periods"],
        "losing_periods": win_loss["losing_periods"],
        "flat_periods": win_loss["flat_periods"],
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


def _win_loss_summary(result: BacktestResult) -> dict[str, float]:
    winning_periods = 0
    losing_periods = 0
    flat_periods = 0

    for previous_point, current_point in zip(
        result.equity_curve,
        result.equity_curve[1:],
        strict=False,
    ):
        if previous_point.position == 0.0:
            continue

        period_return = (current_point.equity / previous_point.equity) - 1.0
        if period_return > 0:
            winning_periods += 1
        elif period_return < 0:
            losing_periods += 1
        else:
            flat_periods += 1

    active_periods = winning_periods + losing_periods + flat_periods
    hit_rate = 0.0 if active_periods == 0 else winning_periods / active_periods
    return {
        "hit_rate": hit_rate,
        "winning_periods": float(winning_periods),
        "losing_periods": float(losing_periods),
        "flat_periods": float(flat_periods),
    }


def compute_win_loss_summary(result: BacktestResult) -> dict[str, float]:
    return _win_loss_summary(result)
