from __future__ import annotations

from pathlib import Path

from backtest_lab.data import load_bars_from_csv, load_bars_from_market_data_csv


def test_load_bars_from_csv_parses_daily_rows(tmp_path: Path) -> None:
    source = tmp_path / "prices.csv"
    source.write_text(
        "\n".join(
            [
                "date,symbol,open,high,low,close,volume",
                "2025-01-02,aapl,99,101,98,100,1000",
            ]
        ),
        encoding="utf-8",
    )

    bars = load_bars_from_csv(source)

    assert len(bars) == 1
    assert bars[0].symbol == "AAPL"
    assert bars[0].close == 100.0


def test_load_bars_from_market_data_csv_converts_timestamp_to_date(tmp_path: Path) -> None:
    source = tmp_path / "normalized.csv"
    source.write_text(
        "\n".join(
            [
                "symbol,timestamp,open,high,low,close,volume",
                "AAPL,2025-01-02T00:00:00,99,101,98,100,1000",
            ]
        ),
        encoding="utf-8",
    )

    bars = load_bars_from_market_data_csv(source)

    assert len(bars) == 1
    assert bars[0].date.isoformat() == "2025-01-02"
