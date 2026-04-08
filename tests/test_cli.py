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


def _write_market_data_toolkit_dataset(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "symbol,timestamp,open,high,low,close,volume",
                "AAPL,2025-01-02T00:00:00,99,101,98,100,1000",
                "AAPL,2025-01-03T00:00:00,100,102,99,101,1000",
                "AAPL,2025-01-04T00:00:00,101,104,100,103,1000",
                "MSFT,2025-01-02T00:00:00,199,201,198,200,1000",
                "MSFT,2025-01-03T00:00:00,200,203,199,202,1000",
                "MSFT,2025-01-04T00:00:00,202,204,201,203,1000",
            ]
        ),
        encoding="utf-8",
    )


def _write_weights_file(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "symbol,weight",
                "AAPL,0.75",
                "MSFT,0.25",
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


def test_cli_runs_on_market_data_toolkit_exports(tmp_path: Path) -> None:
    source = tmp_path / "normalized.csv"
    _write_market_data_toolkit_dataset(source)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "backtest_lab.cli",
            str(source),
            "--input-format",
            "market-data-toolkit",
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
    assert "Symbols: 2" in result.stdout


def test_cli_accepts_custom_weights_file(tmp_path: Path) -> None:
    source = tmp_path / "normalized.csv"
    weights = tmp_path / "weights.csv"
    _write_market_data_toolkit_dataset(source)
    _write_weights_file(weights)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "backtest_lab.cli",
            str(source),
            "--input-format",
            "market-data-toolkit",
            "--strategy",
            "moving-average",
            "--short-window",
            "2",
            "--long-window",
            "3",
            "--weights-file",
            str(weights),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Weighting: custom" in result.stdout


def test_cli_writes_metrics_csv(tmp_path: Path) -> None:
    source = tmp_path / "normalized.csv"
    weights = tmp_path / "weights.csv"
    metrics_output = tmp_path / "metrics" / "report.csv"
    _write_market_data_toolkit_dataset(source)
    _write_weights_file(weights)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "backtest_lab.cli",
            str(source),
            "--input-format",
            "market-data-toolkit",
            "--strategy",
            "moving-average",
            "--short-window",
            "2",
            "--long-window",
            "3",
            "--weights-file",
            str(weights),
            "--metrics-output",
            str(metrics_output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Backtest Report" in result.stdout
    assert metrics_output.exists()
    metrics_csv = metrics_output.read_text(encoding="utf-8")
    assert "scope,name,value" in metrics_csv
    assert "portfolio,weighting_mode,custom" in metrics_csv
    assert "symbol:AAPL,weight,0.750000" in metrics_csv
    assert "symbol:AAPL,hit_rate,0.000000" in metrics_csv


def test_cli_writes_equity_benchmark_and_chart_outputs(tmp_path: Path) -> None:
    source = tmp_path / "normalized.csv"
    weights = tmp_path / "weights.csv"
    equity_output = tmp_path / "exports" / "equity_curve.csv"
    sleeve_output_dir = tmp_path / "exports" / "sleeves"
    comparison_output = tmp_path / "exports" / "comparison_curve.csv"
    chart_output = tmp_path / "exports" / "equity_chart.png"
    _write_market_data_toolkit_dataset(source)
    _write_weights_file(weights)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "backtest_lab.cli",
            str(source),
            "--input-format",
            "market-data-toolkit",
            "--strategy",
            "moving-average",
            "--short-window",
            "2",
            "--long-window",
            "3",
            "--weights-file",
            str(weights),
            "--equity-output",
            str(equity_output),
            "--sleeve-output-dir",
            str(sleeve_output_dir),
            "--comparison-output",
            str(comparison_output),
            "--chart-output",
            str(chart_output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Backtest Report" in result.stdout
    assert equity_output.exists()
    assert "date,equity,position,turnover" in equity_output.read_text(encoding="utf-8")
    assert (sleeve_output_dir / "aapl_equity_curve.csv").exists()
    assert (sleeve_output_dir / "msft_equity_curve.csv").exists()
    comparison_csv = comparison_output.read_text(encoding="utf-8")
    assert "date,strategy_equity,benchmark_equity" in comparison_csv
    assert chart_output.exists()
    assert chart_output.stat().st_size > 0
