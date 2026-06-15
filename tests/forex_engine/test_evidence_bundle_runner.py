from __future__ import annotations

from pathlib import Path

from automation.forex_engine import evidence_bundle_runner
from automation.forex_engine import run_evidence_bundle_demo
from automation.forex_engine import run_month_end_readiness_demo


MODULE_PATH = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "evidence_bundle_runner.py"


def test_evidence_bundle_contains_required_local_evidence_sections() -> None:
    bundle = evidence_bundle_runner.build_local_evidence_bundle()

    assert bundle["mode"] == "PAPER_ONLY"
    assert bundle["fixture_id"] == "EURUSD_5M_PULLBACK_SAMPLE"
    assert bundle["backtest_result"]
    assert bundle["walk_forward_summary"]
    assert bundle["paper_forward_summary"]
    assert bundle["risk_gate_result"]
    assert bundle["evidence_aggregator_output"]
    assert bundle["forex_dashboard_state"]
    assert bundle["month_end_readiness_review"]


def test_evidence_bundle_classification_is_local_only_and_never_live_ready() -> None:
    bundle = evidence_bundle_runner.build_local_evidence_bundle()

    assert bundle["classification"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}
    assert bundle["classification"] != "LIVE_READY"
    assert bundle["live_ready"] is False
    assert evidence_bundle_runner.classify_local_evidence_bundle({"classification": "LIVE_READY", "live_ready": True}) == "FAIL"


def test_evidence_bundle_summary_is_compact_operator_proof() -> None:
    bundle = evidence_bundle_runner.build_local_evidence_bundle()
    summary = evidence_bundle_runner.evidence_bundle_summary(bundle)

    assert summary["fixture_id"] == "EURUSD_5M_PULLBACK_SAMPLE"
    assert summary["strategy_id"] == "supertrend_pullback_v1"
    assert summary["backtest_status"] == "ready"
    assert summary["paper_forward_entries"] > 0
    assert summary["risk_gate_status"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}
    assert summary["evidence_classification"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}
    assert summary["live_ready"] is False
    assert "no broker/API/network/live execution" in summary["safety"]


def test_evidence_bundle_has_no_file_writes_by_default() -> None:
    bundle = evidence_bundle_runner.build_local_evidence_bundle()

    assert bundle["reports_written"] is False
    assert bundle["files_written"] == []
    assert bundle["safety"]["reports_written"] is False
    assert bundle["safety"]["files_written"] == []


def test_dashboard_lines_include_fixture_strategy_paper_and_readiness() -> None:
    bundle = evidence_bundle_runner.build_local_evidence_bundle()
    text = "\n".join(bundle["dashboard_lines"])

    assert "Fixture: EURUSD_5M_PULLBACK_SAMPLE" in text
    assert "Strategy: supertrend_pullback_v1" in text
    assert "Paper-forward:" in text
    assert "Readiness:" in text
    assert "Safety: no broker/live/secrets/orders/webhooks" in text


def test_demo_command_mains_print_paper_only_and_safety_notes(capsys) -> None:
    assert run_evidence_bundle_demo.main([]) == 0
    evidence_output = capsys.readouterr().out
    assert "AIOS Forex Evidence Bundle Demo" in evidence_output
    assert "Mode: PAPER_ONLY" in evidence_output
    assert "Safety: no broker/API/network/live execution." in evidence_output

    assert run_month_end_readiness_demo.main([]) == 0
    readiness_output = capsys.readouterr().out
    assert "AIOS Forex Month-End Readiness Demo" in readiness_output
    assert "Live ready: false" in readiness_output
    assert "Safety: no broker/API/network/live execution." in readiness_output


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
