from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _write_dataset(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "date,symbol,open,high,low,close,volume",
                "2025-01-02,AAPL,99,101,98,100,1000",
                "2025-01-03,AAPL,100,102,99,101,1000",
                "2025-01-04,AAPL,101,104,100,103,1000",
                "2025-01-05,AAPL,103,104,101,102,1000",
                "2025-01-06,AAPL,102,105,101,104,1000",
            ]
        ),
        encoding="utf-8",
    )


def test_cli_runs_backtest_and_prints_report(tmp_path: Path) -> None:
    source = tmp_path / "prices.csv"
    _write_dataset(source)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "backtest_lab.cli",
            str(source),
            "--strategy",
            "moving-average",
            "--short-window",
            "2",
            "--long-window",
            "3",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Backtest Report" in result.stdout
    assert "Ending equity" in result.stdout
