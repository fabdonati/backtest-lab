from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt

from backtest_lab.models import BacktestResult, DailyBar, EquityPoint


def write_equity_curve_csv(curve: list[EquityPoint], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "equity", "position", "turnover"])
        writer.writeheader()
        for point in curve:
            writer.writerow(
                {
                    "date": point.date.isoformat(),
                    "equity": f"{point.equity:.6f}",
                    "position": f"{point.position:.6f}",
                    "turnover": f"{point.turnover:.6f}",
                }
            )


def write_sleeve_curves_csv(result: BacktestResult, destination_dir: Path) -> None:
    if not result.sleeve_curves:
        return
    destination_dir.mkdir(parents=True, exist_ok=True)
    for symbol, curve in sorted(result.sleeve_curves.items()):
        write_equity_curve_csv(curve, destination_dir / f"{symbol.lower()}_equity_curve.csv")


def build_buy_and_hold_benchmark(
    bars: list[DailyBar],
    *,
    initial_cash: float = 10_000.0,
    symbol_weights: dict[str, float] | None = None,
) -> list[EquityPoint]:
    bars_by_symbol = _group_bars_by_symbol(bars)
    symbols = sorted(bars_by_symbol)
    resolved_weights = _resolve_symbol_weights(symbols, symbol_weights)
    sleeve_curves = {
        symbol: _build_symbol_benchmark_curve(
            bars_by_symbol[symbol],
            initial_cash * resolved_weights[symbol],
        )
        for symbol in symbols
    }
    return _combine_curves(sleeve_curves, resolved_weights)


def write_comparison_curve_csv(
    strategy_curve: list[EquityPoint],
    benchmark_curve: list[EquityPoint],
    destination: Path,
) -> None:
    strategy_by_date = {point.date: point for point in strategy_curve}
    benchmark_by_date = {point.date: point for point in benchmark_curve}
    calendar = sorted(set(strategy_by_date) | set(benchmark_by_date))
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["date", "strategy_equity", "benchmark_equity"],
        )
        writer.writeheader()
        for current_date in calendar:
            writer.writerow(
                {
                    "date": current_date.isoformat(),
                    "strategy_equity": f"{strategy_by_date[current_date].equity:.6f}",
                    "benchmark_equity": f"{benchmark_by_date[current_date].equity:.6f}",
                }
            )


def write_equity_chart_png(
    result: BacktestResult,
    benchmark_curve: list[EquityPoint],
    destination: Path,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.plot(
        [point.date.isoformat() for point in result.equity_curve],
        [point.equity for point in result.equity_curve],
        label="strategy",
        linewidth=2.2,
    )
    axis.plot(
        [point.date.isoformat() for point in benchmark_curve],
        [point.equity for point in benchmark_curve],
        label="benchmark",
        linewidth=2.0,
        linestyle="--",
    )
    if result.sleeve_curves:
        for symbol, curve in sorted(result.sleeve_curves.items()):
            axis.plot(
                [point.date.isoformat() for point in curve],
                [point.equity for point in curve],
                label=f"{symbol} sleeve",
                linewidth=1.4,
                alpha=0.7,
            )
    axis.set_title("Backtest Equity Curves")
    axis.set_xlabel("Date")
    axis.set_ylabel("Equity")
    axis.grid(True, alpha=0.3)
    axis.legend()
    figure.autofmt_xdate()
    figure.tight_layout()
    figure.savefig(destination, dpi=160)
    plt.close(figure)


def _build_symbol_benchmark_curve(bars: list[DailyBar], initial_cash: float) -> list[EquityPoint]:
    ordered_bars = sorted(bars, key=lambda bar: bar.date)
    curve = [
        EquityPoint(
            date=ordered_bars[0].date,
            equity=initial_cash,
            position=1.0,
            turnover=0.0,
        )
    ]
    equity = initial_cash
    for previous_bar, current_bar in zip(ordered_bars, ordered_bars[1:], strict=False):
        equity *= current_bar.close / previous_bar.close
        curve.append(
            EquityPoint(
                date=current_bar.date,
                equity=equity,
                position=1.0,
                turnover=0.0,
            )
        )
    return curve


def _combine_curves(
    sleeve_curves: dict[str, list[EquityPoint]],
    resolved_weights: dict[str, float],
) -> list[EquityPoint]:
    calendar = sorted({point.date for curve in sleeve_curves.values() for point in curve})
    latest_points = {symbol: curve[0] for symbol, curve in sleeve_curves.items()}
    indices = {symbol: 0 for symbol in sleeve_curves}
    combined: list[EquityPoint] = []

    for current_date in calendar:
        for symbol, curve in sleeve_curves.items():
            next_index = indices[symbol] + 1
            while next_index < len(curve) and curve[next_index].date <= current_date:
                latest_points[symbol] = curve[next_index]
                indices[symbol] = next_index
                next_index += 1
        combined.append(
            EquityPoint(
                date=current_date,
                equity=sum(point.equity for point in latest_points.values()),
                position=sum(resolved_weights[symbol] for symbol in latest_points),
                turnover=0.0,
            )
        )
    return combined


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

    return {symbol: symbol_weights[symbol] for symbol in symbols}
