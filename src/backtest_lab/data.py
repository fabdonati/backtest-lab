from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from backtest_lab.models import DailyBar

REQUIRED_COLUMNS = ("date", "symbol", "open", "high", "low", "close", "volume")
MARKET_DATA_TOOLKIT_COLUMNS = ("symbol", "timestamp", "open", "high", "low", "close", "volume")
WEIGHT_COLUMNS = ("symbol", "weight")


def load_bars_from_csv(path: str | Path) -> list[DailyBar]:
    csv_path = Path(path)
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV file is missing a header row.")
        missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise ValueError(f"CSV file is missing required columns: {', '.join(missing)}")

        bars: list[DailyBar] = []
        for row in reader:
            bars.append(
                DailyBar(
                    date=date.fromisoformat(_required_value(row, "date")),
                    symbol=_required_value(row, "symbol").upper(),
                    open=float(_required_value(row, "open")),
                    high=float(_required_value(row, "high")),
                    low=float(_required_value(row, "low")),
                    close=float(_required_value(row, "close")),
                    volume=float(_required_value(row, "volume")),
                )
            )
    return bars


def load_bars_from_market_data_csv(path: str | Path) -> list[DailyBar]:
    csv_path = Path(path)
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV file is missing a header row.")
        missing = [
            column
            for column in MARKET_DATA_TOOLKIT_COLUMNS
            if column not in reader.fieldnames
        ]
        if missing:
            raise ValueError(
                "Market-data-toolkit CSV file is missing required columns: "
                f"{', '.join(missing)}"
            )

        bars: list[DailyBar] = []
        for row in reader:
            timestamp = _required_value(row, "timestamp")
            bars.append(
                DailyBar(
                    date=date.fromisoformat(timestamp[:10]),
                    symbol=_required_value(row, "symbol").upper(),
                    open=float(_required_value(row, "open")),
                    high=float(_required_value(row, "high")),
                    low=float(_required_value(row, "low")),
                    close=float(_required_value(row, "close")),
                    volume=float(_required_value(row, "volume")),
                )
            )
    return bars


def load_symbol_weights(path: str | Path) -> dict[str, float]:
    csv_path = Path(path)
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV file is missing a header row.")
        missing = [column for column in WEIGHT_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise ValueError(f"Weight file is missing required columns: {', '.join(missing)}")

        weights: dict[str, float] = {}
        for row in reader:
            symbol = _required_value(row, "symbol").upper()
            weight = float(_required_value(row, "weight"))
            if weight < 0:
                raise ValueError(f"Weight for {symbol} must be non-negative.")
            weights[symbol] = weight

    total_weight = sum(weights.values())
    if total_weight <= 0:
        raise ValueError("Weight file must contain at least one positive weight.")
    if abs(total_weight - 1.0) > 1e-6:
        raise ValueError(
            f"Weight file must sum to 1.0. Received {total_weight:.6f}."
        )
    return weights


def _required_value(row: dict[str, str | None], key: str) -> str:
    value = row.get(key)
    if value is None or value == "":
        raise ValueError(f"Missing required value for column '{key}'.")
    return value
