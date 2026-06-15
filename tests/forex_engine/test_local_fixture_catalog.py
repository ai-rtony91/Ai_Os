from __future__ import annotations

from pathlib import Path

from automation.forex_engine import local_fixture_catalog
from automation.forex_engine import schema_contracts as schemas


MODULE_PATH = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "local_fixture_catalog.py"


def test_catalog_contains_required_fixtures() -> None:
    fixture_ids = local_fixture_catalog.list_fixture_ids()

    assert fixture_ids == [
        "EURUSD_5M_TREND_SAMPLE",
        "EURUSD_5M_CHOP_SAMPLE",
        "EURUSD_5M_PULLBACK_SAMPLE",
    ]


def test_catalog_fixtures_validate_through_schema_contracts() -> None:
    catalog = local_fixture_catalog.build_deterministic_fixture_catalog()

    for fixture in catalog.values():
        assert schemas.validate_market_fixture_schema(fixture) is True
        assert fixture.mode == schemas.LOCAL_ONLY
        assert fixture.network_allowed is False
        assert fixture.source == "deterministic_python_fixture_catalog"


def test_fixture_catalog_summary_is_local_only_and_reportless() -> None:
    summary = local_fixture_catalog.fixture_catalog_summary()

    assert summary["local_python_data_only"] is True
    assert summary["csv_ingestion"] is False
    assert summary["file_reads"] is False
    assert summary["network_allowed"] is False
    assert summary["broker_allowed"] is False
    assert summary["live_ready"] is False
    assert summary["reports_written"] is False


def test_get_fixture_by_id_returns_valid_fixture() -> None:
    fixture = local_fixture_catalog.get_fixture_by_id("EURUSD_5M_PULLBACK_SAMPLE")

    assert fixture.fixture_id == "EURUSD_5M_PULLBACK_SAMPLE"
    assert len(fixture.candles) >= 8
    assert schemas.validate_market_fixture_schema(fixture) is True


def test_module_has_no_network_broker_env_file_read_or_file_write_behavior() -> None:
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
