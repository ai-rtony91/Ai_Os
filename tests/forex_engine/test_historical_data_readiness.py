import csv
from pathlib import Path

import pytest

from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.historical_data_readiness import HistoricalDataReadinessEngine
from automation.forex_engine.models import (
    DatasetIssueSeverity,
    HistoricalDataReadinessStatus,
)


def _engine():
    return HistoricalDataReadinessEngine(ForexEngineConfig())


def _write_csv(path, rows, fields=None):
    fields = fields or ("timestamp", "symbol", "timeframe", "open", "high", "low", "close", "volume")
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    return Path(path)


def _valid_rows(count=400):
    symbols = ("EURUSD", "GBPUSD", "USDJPY", "XAUUSD")
    rows = []
    for index in range(count):
        symbol = symbols[index % len(symbols)]
        step = index // len(symbols)
        price = 1.08 + (step * 0.0001)
        if symbol == "USDJPY":
            price = 155 + (step * 0.01)
        if symbol == "XAUUSD":
            price = 2350 + (step * 0.01)
        rows.append(
            {
                "timestamp": f"2026-01-05T00:{step:02d}:00Z",
                "symbol": symbol,
                "timeframe": "5m",
                "open": price,
                "high": price + 0.01,
                "low": price - 0.01,
                "close": price + 0.001,
                "volume": 1000,
            }
        )
    return rows


def test_manifest_creation_from_valid_csv(tmp_path):
    path = _write_csv(tmp_path / "valid.csv", _valid_rows())
    summary = _engine().inspect_dataset(path)
    assert summary.manifest.dataset_name == "valid.csv"
    assert summary.manifest.row_count == 400
    assert set(summary.manifest.symbols) == {"EURUSD", "GBPUSD", "USDJPY", "XAUUSD"}


def test_valid_dataset_ready_or_sufficient(tmp_path):
    path = _engine().generate_synthetic_dataset(tmp_path / "synthetic.csv", row_count=1000)
    summary = _engine().inspect_dataset(path)
    assert summary.readiness_status == HistoricalDataReadinessStatus.READY_FOR_LOCAL_IMPORT


def test_missing_required_field_invalid_dataset(tmp_path):
    fields = ("timestamp", "symbol", "timeframe", "open", "high", "low", "close")
    path = _write_csv(tmp_path / "missing.csv", _valid_rows(4), fields)
    summary = _engine().inspect_dataset(path)
    assert summary.readiness_status == HistoricalDataReadinessStatus.INVALID_DATASET
    assert any(issue.code == "MISSING_REQUIRED_FIELD" for issue in summary.quality_score.issues)


def test_invalid_symbol_detected(tmp_path):
    rows = _valid_rows(4)
    rows[0]["symbol"] = "BADPAIR"
    path = _write_csv(tmp_path / "invalid_symbol.csv", rows)
    summary = _engine().inspect_dataset(path)
    assert any(issue.code == "INVALID_SYMBOL" for issue in summary.quality_score.issues)


def test_invalid_timeframe_detected(tmp_path):
    rows = _valid_rows(4)
    rows[0]["timeframe"] = "99m"
    path = _write_csv(tmp_path / "invalid_timeframe.csv", rows)
    summary = _engine().inspect_dataset(path)
    assert any(issue.code == "INVALID_TIMEFRAME" for issue in summary.quality_score.issues)


def test_negative_price_detected(tmp_path):
    rows = _valid_rows(4)
    rows[0]["open"] = -1
    path = _write_csv(tmp_path / "negative.csv", rows)
    summary = _engine().inspect_dataset(path)
    assert any(issue.code == "INVALID_PRICE" for issue in summary.quality_score.issues)


def test_bad_ohlc_relationship_detected(tmp_path):
    rows = _valid_rows(4)
    rows[0]["high"] = 0.5
    path = _write_csv(tmp_path / "bad_ohlc.csv", rows)
    summary = _engine().inspect_dataset(path)
    assert any(issue.code == "INVALID_OHLC_RELATIONSHIP" for issue in summary.quality_score.issues)


def test_duplicate_timestamp_detected(tmp_path):
    rows = _valid_rows(8)
    rows[1]["symbol"] = rows[0]["symbol"]
    rows[1]["timeframe"] = rows[0]["timeframe"]
    rows[1]["timestamp"] = rows[0]["timestamp"]
    path = _write_csv(tmp_path / "duplicate.csv", rows)
    summary = _engine().inspect_dataset(path)
    assert summary.duplicate_count == 1


def test_unsorted_timestamps_detected(tmp_path):
    rows = _valid_rows(8)
    rows[4]["timestamp"] = "2026-01-04T00:00:00Z"
    path = _write_csv(tmp_path / "unsorted.csv", rows)
    summary = _engine().inspect_dataset(path)
    assert any(issue.code == "UNSORTED_TIMESTAMP" for issue in summary.quality_score.issues)


def test_small_dataset_insufficient_data(tmp_path):
    path = _write_csv(tmp_path / "tiny.csv", _valid_rows(4))
    summary = _engine().inspect_dataset(path)
    assert summary.readiness_status == HistoricalDataReadinessStatus.INSUFFICIENT_DATA


def test_score_clamped_between_zero_and_100(tmp_path):
    rows = _valid_rows(2)
    rows[0]["symbol"] = "BADPAIR"
    rows[0]["timeframe"] = "99m"
    rows[0]["open"] = -1
    path = _write_csv(tmp_path / "bad.csv", rows, fields=("timestamp", "symbol", "timeframe", "open"))
    summary = _engine().inspect_dataset(path)
    assert 0 <= summary.quality_score.score <= 100


def test_rejects_url_path():
    with pytest.raises(ValueError, match="URL"):
        _engine().inspect_dataset("https://example.invalid/EURUSD.csv")


def test_generate_synthetic_dataset_creates_local_csv(tmp_path):
    path = _engine().generate_synthetic_dataset(tmp_path, row_count=20)
    assert path.exists()
    assert path.suffix == ".csv"


def test_format_readiness_summary_contains_status(tmp_path):
    path = _engine().generate_synthetic_dataset(tmp_path / "synthetic.csv", row_count=1000)
    summary = _engine().inspect_dataset(path)
    formatted = _engine().format_readiness_summary(summary)
    assert "Quality score:" in formatted
    assert "Readiness status:" in formatted


def test_historical_data_readiness_demo_imports_without_network():
    import automation.forex_engine.run_historical_data_readiness_demo as demo

    assert demo.main


def test_existing_demos_still_import():
    import automation.forex_engine.run_backtest_demo as backtest_demo
    import automation.forex_engine.run_broker_sandbox_demo as broker_sandbox_demo
    import automation.forex_engine.run_confidence_demo as confidence_demo
    import automation.forex_engine.run_market_data_demo as market_data_demo
    import automation.forex_engine.run_paper_demo as paper_demo
    import automation.forex_engine.run_paper_operator_demo as paper_operator_demo
    import automation.forex_engine.run_parameter_optimization_demo as parameter_demo
    import automation.forex_engine.run_portfolio_optimization_demo as portfolio_demo
    import automation.forex_engine.run_risk_management_demo as risk_management_demo
    import automation.forex_engine.run_signal_rules_demo as signal_rules_demo
    import automation.forex_engine.run_strategy_comparison_demo as strategy_comparison_demo
    import automation.forex_engine.run_walk_forward_demo as walk_forward_demo

    assert backtest_demo.main
    assert broker_sandbox_demo.main
    assert confidence_demo.main
    assert market_data_demo.main
    assert paper_demo.main
    assert paper_operator_demo.main
    assert parameter_demo.main
    assert portfolio_demo.main
    assert risk_management_demo.main
    assert signal_rules_demo.main
    assert strategy_comparison_demo.main
    assert walk_forward_demo.main


def test_no_live_trading_demo_created():
    assert not Path("automation/forex_engine/run_live_trading_demo.py").exists()


def test_issue_severity_values_exist():
    assert DatasetIssueSeverity.INFO == "INFO"
    assert DatasetIssueSeverity.WARNING == "WARNING"
    assert DatasetIssueSeverity.ERROR == "ERROR"
