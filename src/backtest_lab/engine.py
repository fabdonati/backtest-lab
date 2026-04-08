from __future__ import annotations

from datetime import date

from backtest_lab.models import BacktestResult, DailyBar, EquityPoint, Signal, SymbolSummary
from backtest_lab.portfolio import trading_cost


def run_backtest(
    bars: list[DailyBar],
    signals: list[Signal],
    *,
    initial_cash: float = 10_000.0,
    transaction_cost_bps: float = 5.0,
    slippage_bps: float = 1.0,
    capital_base: float | None = None,
) -> BacktestResult:
    if not bars:
        raise ValueError("bars must not be empty")

    capital_base = initial_cash if capital_base is None else capital_base
    symbol = bars[0].symbol
    symbol_signals = [signal for signal in signals if signal.symbol == symbol]
    signal_map = _build_signal_map(symbol_signals)
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
        target_position = signal_map.get(previous_bar.date, current_position)
        position_turnover = abs(target_position - current_position)
        capital_turnover = position_turnover * (equity / capital_base)
        if position_turnover > 0:
            equity *= 1.0 - trading_cost(
                target_position - current_position,
                transaction_cost_bps,
                slippage_bps,
            )
            trades += 1

        current_position = target_position
        daily_return = (current_bar.close / previous_bar.close) - 1.0
        equity *= 1.0 + (current_position * daily_return)
        equity_curve.append(
            EquityPoint(
                date=current_bar.date,
                equity=equity,
                position=current_position,
                turnover=capital_turnover,
            )
        )

    total_return = (equity / initial_cash) - 1.0
    return BacktestResult(
        equity_curve=equity_curve,
        total_return=total_return,
        ending_equity=equity,
        trades=trades,
        symbol_count=1,
    )


def run_portfolio_backtest(
    bars: list[DailyBar],
    signals: list[Signal],
    *,
    initial_cash: float = 10_000.0,
    transaction_cost_bps: float = 5.0,
    slippage_bps: float = 1.0,
    symbol_weights: dict[str, float] | None = None,
) -> BacktestResult:
    if not bars:
        raise ValueError("bars must not be empty")

    bars_by_symbol = _group_bars_by_symbol(bars)
    symbols = sorted(bars_by_symbol)
    resolved_weights = _resolve_symbol_weights(symbols, symbol_weights)
    symbol_results = {
        symbol: run_backtest(
            symbol_bars,
            signals,
            initial_cash=initial_cash * resolved_weights[symbol],
            transaction_cost_bps=transaction_cost_bps,
            slippage_bps=slippage_bps,
            capital_base=initial_cash,
        )
        for symbol, symbol_bars in bars_by_symbol.items()
    }

    combined_curve = _combine_equity_curves(symbol_results)
    symbol_summaries = _build_symbol_summaries(
        symbol_results,
        resolved_weights,
        initial_cash,
    )
    total_return = (combined_curve[-1].equity / initial_cash) - 1.0
    trades = sum(result.trades for result in symbol_results.values())
    return BacktestResult(
        equity_curve=combined_curve,
        total_return=total_return,
        ending_equity=combined_curve[-1].equity,
        trades=trades,
        symbol_count=len(symbols),
        weighting_mode="custom" if symbol_weights is not None else "equal-weight",
        symbol_summaries=symbol_summaries,
    )


def _build_signal_map(signals: list[Signal]) -> dict[date, float]:
    return {signal.date: signal.target_weight for signal in signals}


def _group_bars_by_symbol(bars: list[DailyBar]) -> dict[str, list[DailyBar]]:
    grouped: dict[str, list[DailyBar]] = {}
    for bar in bars:
        grouped.setdefault(bar.symbol, []).append(bar)
    return grouped


def _resolve_symbol_weights(
    symbols: list[str],
    symbol_weights: dict[str, float] | None,
) -> dict[str, float]:
    if symbol_weights is None:
        equal_weight = 1.0 / len(symbols)
        return {symbol: equal_weight for symbol in symbols}

    missing = [symbol for symbol in symbols if symbol not in symbol_weights]
    extras = [symbol for symbol in symbol_weights if symbol not in symbols]
    if missing:
        raise ValueError(f"Weight file is missing symbols: {', '.join(missing)}")
    if extras:
        raise ValueError(f"Weight file contains unknown symbols: {', '.join(sorted(extras))}")
    return {symbol: symbol_weights[symbol] for symbol in symbols}


def _combine_equity_curves(symbol_results: dict[str, BacktestResult]) -> list[EquityPoint]:
    calendar = sorted(
        {
            point.date
            for result in symbol_results.values()
            for point in result.equity_curve
        }
    )
    latest_points = {
        symbol: result.equity_curve[0]
        for symbol, result in symbol_results.items()
    }
    result_indices = {symbol: 0 for symbol in symbol_results}
    combined_curve: list[EquityPoint] = []

    for current_date in calendar:
        for symbol, result in symbol_results.items():
            next_index = result_indices[symbol] + 1
            while (
                next_index < len(result.equity_curve)
                and result.equity_curve[next_index].date <= current_date
            ):
                latest_points[symbol] = result.equity_curve[next_index]
                result_indices[symbol] = next_index
                next_index += 1

        combined_curve.append(
            EquityPoint(
                date=current_date,
                equity=sum(point.equity for point in latest_points.values()),
                position=sum(point.position for point in latest_points.values())
                / len(latest_points),
                turnover=sum(point.turnover for point in latest_points.values()),
            )
        )

    return combined_curve


def _build_symbol_summaries(
    symbol_results: dict[str, BacktestResult],
    resolved_weights: dict[str, float],
    initial_cash: float,
) -> list[SymbolSummary]:
    summaries: list[SymbolSummary] = []
    for symbol in sorted(symbol_results):
        result = symbol_results[symbol]
        starting_equity = initial_cash * resolved_weights[symbol]
        average_capital_turnover = sum(point.turnover for point in result.equity_curve[1:]) / max(
            len(result.equity_curve) - 1,
            1,
        )
        summaries.append(
            SymbolSummary(
                symbol=symbol,
                starting_equity=starting_equity,
                ending_equity=result.ending_equity,
                total_return=result.total_return,
                contribution=(result.ending_equity - starting_equity) / initial_cash,
                weight=resolved_weights[symbol],
                average_capital_turnover=average_capital_turnover,
                trades=result.trades,
            )
        )
    return summaries
