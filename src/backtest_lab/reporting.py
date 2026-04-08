from __future__ import annotations

import csv
from pathlib import Path

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
        f"Average exposure: {metrics['average_exposure']:.2%}",
        f"Max exposure: {metrics['max_exposure']:.2%}",
        f"Max drawdown: {metrics['max_drawdown']:.2%}",
        f"Max drawdown duration: {int(metrics['max_drawdown_duration'])} bars",
        f"Hit rate: {metrics['hit_rate']:.2%}",
        f"Winning periods: {int(metrics['winning_periods'])}",
        f"Losing periods: {int(metrics['losing_periods'])}",
        f"Flat periods: {int(metrics['flat_periods'])}",
        f"Trades: {result.trades}",
        f"Average raw signal turnover: {result.average_raw_signal_turnover:.2%}",
        f"Average capital turnover: {_average_turnover(result):.2%}",
    ]
    if result.symbol_summaries:
        lines.append("Symbol summary:")
        lines.extend(_format_symbol_summary(summary) for summary in result.symbol_summaries)
    return "\n".join(lines)


def write_metrics_csv(result: BacktestResult, destination: Path) -> None:
    rows = _metrics_rows(result)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["scope", "name", "value"])
        writer.writeheader()
        writer.writerows(rows)


def _average_turnover(result: BacktestResult) -> float:
    if len(result.equity_curve) <= 1:
        return 0.0
    return sum(point.turnover for point in result.equity_curve[1:]) / (len(result.equity_curve) - 1)


def _format_symbol_summary(summary: SymbolSummary) -> str:
    return (
        f"- {summary.symbol}: weight {summary.weight:.2%}, "
        f"return {summary.total_return:.2%}, "
        f"contribution {summary.contribution:.2%}, "
        f"hit rate {summary.hit_rate:.2%}, "
        f"wins {summary.winning_periods}, "
        f"losses {summary.losing_periods}, "
        f"flats {summary.flat_periods}, "
        f"avg raw turnover {summary.average_raw_signal_turnover:.2%}, "
        f"avg capital turnover {summary.average_capital_turnover:.2%}, "
        f"trades {summary.trades}"
    )


def _metrics_rows(result: BacktestResult) -> list[dict[str, str]]:
    metrics = compute_metrics(result)
    rows = [
        {"scope": "portfolio", "name": "symbols", "value": str(result.symbol_count)},
        {"scope": "portfolio", "name": "weighting_mode", "value": result.weighting_mode},
        {"scope": "portfolio", "name": "ending_equity", "value": f"{result.ending_equity:.6f}"},
        {"scope": "portfolio", "name": "total_return", "value": f"{metrics['total_return']:.6f}"},
        {
            "scope": "portfolio",
            "name": "annualized_volatility",
            "value": f"{metrics['annualized_volatility']:.6f}",
        },
        {"scope": "portfolio", "name": "sharpe_ratio", "value": f"{metrics['sharpe_ratio']:.6f}"},
        {
            "scope": "portfolio",
            "name": "average_exposure",
            "value": f"{metrics['average_exposure']:.6f}",
        },
        {"scope": "portfolio", "name": "max_exposure", "value": f"{metrics['max_exposure']:.6f}"},
        {"scope": "portfolio", "name": "max_drawdown", "value": f"{metrics['max_drawdown']:.6f}"},
        {
            "scope": "portfolio",
            "name": "max_drawdown_duration",
            "value": str(int(metrics["max_drawdown_duration"])),
        },
        {"scope": "portfolio", "name": "hit_rate", "value": f"{metrics['hit_rate']:.6f}"},
        {
            "scope": "portfolio",
            "name": "winning_periods",
            "value": str(int(metrics["winning_periods"])),
        },
        {
            "scope": "portfolio",
            "name": "losing_periods",
            "value": str(int(metrics["losing_periods"])),
        },
        {"scope": "portfolio", "name": "flat_periods", "value": str(int(metrics["flat_periods"]))},
        {"scope": "portfolio", "name": "trades", "value": str(result.trades)},
        {
            "scope": "portfolio",
            "name": "average_raw_signal_turnover",
            "value": f"{result.average_raw_signal_turnover:.6f}",
        },
        {
            "scope": "portfolio",
            "name": "average_capital_turnover",
            "value": f"{_average_turnover(result):.6f}",
        },
    ]
    if result.symbol_summaries:
        rows.extend(_symbol_summary_rows(result.symbol_summaries))
    return rows


def _symbol_summary_rows(summaries: list[SymbolSummary]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for summary in summaries:
        scope = f"symbol:{summary.symbol}"
        rows.extend(
            [
                {"scope": scope, "name": "weight", "value": f"{summary.weight:.6f}"},
                {"scope": scope, "name": "total_return", "value": f"{summary.total_return:.6f}"},
                {"scope": scope, "name": "contribution", "value": f"{summary.contribution:.6f}"},
                {"scope": scope, "name": "hit_rate", "value": f"{summary.hit_rate:.6f}"},
                {"scope": scope, "name": "winning_periods", "value": str(summary.winning_periods)},
                {"scope": scope, "name": "losing_periods", "value": str(summary.losing_periods)},
                {"scope": scope, "name": "flat_periods", "value": str(summary.flat_periods)},
                {
                    "scope": scope,
                    "name": "average_raw_signal_turnover",
                    "value": f"{summary.average_raw_signal_turnover:.6f}",
                },
                {
                    "scope": scope,
                    "name": "average_capital_turnover",
                    "value": f"{summary.average_capital_turnover:.6f}",
                },
                {"scope": scope, "name": "trades", "value": str(summary.trades)},
            ]
        )
    return rows
