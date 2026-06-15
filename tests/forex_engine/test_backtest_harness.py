from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import pytest

from automation.forex_engine import backtest_harness
from automation.forex_engine import schema_contracts as schemas


MODULE_PATH = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "backtest_harness.py"


def test_backtest_harness_runs_deterministically() -> None:
    fixture = backtest_harness.build_sample_backtest_fixture()

    first = backtest_harness.run_local_backtest_harness(fixture)
    second = backtest_harness.run_local_backtest_harness(fixture)

    assert asdict(first) == asdict(second)
    assert first.mode == "PAPER_ONLY"
    assert first.total_trades > 0
    assert schemas.validate_backtest_result_schema(first) is True


def test_backtest_harness_uses_local_fixtures_only() -> None:
    fixture = backtest_harness.build_sample_backtest_fixture()
    result = backtest_harness.run_local_backtest_harness(fixture)
    summary = backtest_harness.backtest_harness_summary(result)

    assert fixture.mode == "LOCAL_ONLY"
    assert fixture.network_allowed is False
    assert fixture.source == "deterministic_local_fixture"
    assert summary["local_fixtures_only"] is True
    assert summary["network_allowed"] is False
    assert summary["broker_allowed"] is False
    assert summary["live_ready"] is False


def test_backtest_harness_rejects_live_or_broker_config() -> None:
    fixture = backtest_harness.build_sample_backtest_fixture()

    with pytest.raises(ValueError, match="broker_allowed"):
        backtest_harness.run_local_backtest_harness(fixture, {"broker_allowed": True})

    with pytest.raises(ValueError, match="execution_allowed"):
        backtest_harness.run_local_backtest_harness(fixture, {"execution_allowed": True})


def test_backtest_harness_summary_validates_schema_payload() -> None:
    result = backtest_harness.run_local_backtest_harness()
    summary = backtest_harness.backtest_harness_summary(result)

    assert summary["schema"] == "AIOS_FOREX_BUILDER_BACKTEST_HARNESS_SUMMARY.v1"
    assert summary["total_trades"] == result.total_trades
    assert summary["mode"] == "PAPER_ONLY"


def test_module_has_no_network_broker_env_or_file_write_behavior() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    import_lines = "\n".join(
        line.strip()
        for line in source.splitlines()
        if line.startswith("import ") or line.startswith("from ")
    )

    for forbidden_import in ("subprocess", "socket", "urllib", "requests", "http", "os", "dotenv"):
        assert forbidden_import not in import_lines
    for forbidden_call in ("open(", "write_text(", "write_bytes(", "getenv", "environ", "start-process"):
        assert forbidden_call not in source
