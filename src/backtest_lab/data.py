from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from backtest_lab.models import DailyBar

REQUIRED_COLUMNS = ("date", "symbol", "open", "high", "low", "close", "volume")
MARKET_DATA_TOOLKIT_COLUMNS = ("symbol", "timestamp", "open", "high", "low", "close", "volume")


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


def _required_value(row: dict[str, str | None], key: str) -> str:
    value = row.get(key)
    if value is None or value == "":
        raise ValueError(f"Missing required value for column '{key}'.")
    return value
