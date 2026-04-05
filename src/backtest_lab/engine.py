from __future__ import annotations

from datetime import date

from backtest_lab.models import BacktestResult, DailyBar, EquityPoint, Signal
from backtest_lab.portfolio import trading_cost


def run_backtest(
    bars: list[DailyBar],
    signals: list[Signal],
    *,
    initial_cash: float = 10_000.0,
    transaction_cost_bps: float = 5.0,
    slippage_bps: float = 1.0,
) -> BacktestResult:
    if not bars:
        raise ValueError("bars must not be empty")

    signal_map = _build_signal_map(signals)
    ordered_bars = sorted(bars, key=lambda bar: bar.date)

    equity = initial_cash
    current_position = 0.0
    equity_curve = [
        EquityPoint(
            date=ordered_bars[0].date,
            equity=initial_cash,
            position=current_position,
            turnover=0.0,
        )
    ]
    trades = 0

    for previous_bar, current_bar in zip(ordered_bars, ordered_bars[1:], strict=False):
        daily_return = (current_bar.close / previous_bar.close) - 1.0
        equity *= 1.0 + (current_position * daily_return)

        target_position = signal_map.get(previous_bar.date, current_position)
        turnover = abs(target_position - current_position)
        if turnover > 0:
            equity *= 1.0 - trading_cost(
                target_position - current_position,
                transaction_cost_bps,
                slippage_bps,
            )
            trades += 1

        current_position = target_position
        equity_curve.append(
            EquityPoint(
                date=current_bar.date,
                equity=equity,
                position=current_position,
                turnover=turnover,
            )
        )

    total_return = (equity / initial_cash) - 1.0
    return BacktestResult(
        equity_curve=equity_curve,
        total_return=total_return,
        ending_equity=equity,
        trades=trades,
    )


def _build_signal_map(signals: list[Signal]) -> dict[date, float]:
    return {signal.date: signal.target_weight for signal in signals}
