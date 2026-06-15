from __future__ import annotations

from pathlib import Path

from automation.forex_engine import local_fixture_catalog
from automation.forex_engine import paper_forward_runner
from automation.forex_engine import run_paper_forward_demo


MODULE_PATH = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "paper_forward_runner.py"


def test_demo_bundle_returns_simulated_ledger_entries() -> None:
    bundle = paper_forward_runner.run_paper_forward_demo_bundle()

    assert bundle["mode"] == "PAPER_ONLY"
    assert bundle["session_mode"] == "LOCAL_SIMULATION_ONLY"
    assert bundle["fixture_id"] == "EURUSD_5M_PULLBACK_SAMPLE"
    assert bundle["strategy_id"] == "supertrend_pullback_v1"
    assert len(bundle["intents"]) > 0
    assert len(bundle["ledger_entries"]) == len(bundle["intents"])
    assert bundle["paper_summary"]["total_entries"] == len(bundle["ledger_entries"])


def test_runner_never_creates_broker_order_ids_live_orders_or_execution_permission() -> None:
    bundle = paper_forward_runner.run_paper_forward_demo_bundle()

    for intent in bundle["intents"]:
        assert intent["broker_order_id"] is None
        assert intent["execution_allowed"] is False
    for entry in bundle["ledger_entries"]:
        assert entry["broker_order_id"] is None
        assert entry["live_order"] is False
        assert entry["status"] == "SIMULATED_ONLY"
    assert bundle["safety"]["execution_allowed"] is False
    assert bundle["safety"]["live_order"] is False
    assert bundle["safety"]["broker_allowed"] is False


def test_run_local_session_has_no_file_writes_by_default() -> None:
    fixture = local_fixture_catalog.get_fixture_by_id("EURUSD_5M_TREND_SAMPLE")
    bundle = paper_forward_runner.run_local_paper_forward_session(fixture, "supertrend_pullback_v1")

    assert bundle["reports_written"] is False
    assert bundle["files_written"] == []
    assert bundle["paper_summary"]["reports_written"] is False
    assert bundle["paper_summary"]["files_written"] == []


def test_demo_command_main_prints_paper_only_safety_note(capsys) -> None:
    assert run_paper_forward_demo.main([]) == 0
    output = capsys.readouterr().out

    assert "AIOS Forex Paper-Forward Demo" in output
    assert "Mode: PAPER_ONLY" in output
    assert "Safety: no broker/API/network/live execution." in output


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
