from __future__ import annotations

from pathlib import Path

from tests.forex_engine.forex_evidence_cache import get_paper_forward_v2_bundle
from automation.forex_engine import local_fixture_catalog
from automation.forex_engine import paper_forward_evidence_v2
from automation.forex_engine import run_paper_forward_evidence_v2_demo
from automation.forex_engine import schema_contracts as schemas


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "paper_forward_evidence_v2.py"
DEMO_PATH = REPO_ROOT / "automation" / "forex_engine" / "run_paper_forward_evidence_v2_demo.py"
ALLOWED_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}


def test_required_v2_fixtures_exist_and_validate() -> None:
    catalog = local_fixture_catalog.build_deterministic_fixture_catalog()

    for fixture_id in local_fixture_catalog.REQUIRED_FIXTURE_IDS:
        assert fixture_id in catalog
        fixture = catalog[fixture_id]
        assert schemas.validate_market_fixture_schema(fixture) is True
        assert fixture.network_allowed is False
        assert fixture.source == "deterministic_local_fixture"


def test_fixture_catalog_is_local_only() -> None:
    validation = local_fixture_catalog.validate_fixture_catalog()

    assert validation["valid"] is True
    assert validation["local_only"] is True
    assert validation["network_allowed"] is False
    assert validation["broker_allowed"] is False
    assert validation["reports_written"] is False
    assert validation["files_written"] == []


def test_evidence_v2_bundle_includes_fixture_summary_and_regime_consistency() -> None:
    bundle = get_paper_forward_v2_bundle()

    assert bundle["mode"] == "PAPER_ONLY"
    assert bundle["fixture_catalog_summary"]["fixture_count"] == len(local_fixture_catalog.REQUIRED_FIXTURE_IDS)
    assert bundle["multi_fixture_paper_forward_summary"]["fixture_count"] == len(local_fixture_catalog.REQUIRED_FIXTURE_IDS)
    assert bundle["regime_consistency"]["total_regimes"] >= 6
    assert bundle["risk_gate_result"]
    assert bundle["opportunity_capture"]
    assert bundle["opportunity_capture_summary"]
    assert bundle["risk_governor"]
    assert bundle["stress_scenarios"]
    assert bundle["paper_forward_stress"]
    assert bundle["out_of_sample_validation"]
    assert bundle["combined_stress_oos_gate"]
    assert bundle["expanded_oos"]
    assert bundle["expanded_oos_summary"]
    assert bundle["oos_repair"]
    assert bundle["oos_repair_summary"]
    assert bundle["low_vol_edge_redesign"]
    assert bundle["low_vol_edge_summary"]
    assert bundle["starting_balance"] == 500.0
    assert bundle["ending_balance"] >= 500.0
    assert bundle["return_pct"] >= 0.0
    assert bundle["month_end_readiness_review"]
    assert bundle["forex_dashboard_v2"]
    assert bundle["classification"] in ALLOWED_CLASSIFICATIONS
    assert bundle["classification"] != "LIVE_READY"
    assert bundle["live_ready"] is False
    assert bundle["protected_gate_required"] is True


def test_multi_fixture_v2_ledgers_are_simulated_only() -> None:
    bundle = get_paper_forward_v2_bundle()
    per_fixture = bundle["multi_fixture_paper_forward"]["per_fixture_results"]

    assert per_fixture
    for item in per_fixture:
        assert item["ledger_entry_count"] > 0
        assert all(order_id is None for order_id in item["broker_order_ids"])
        assert all(live_order is False for live_order in item["live_orders"])
        assert item["safety"]["broker_allowed"] is False
        assert item["safety"]["live_order"] is False


def test_evidence_v2_summary_is_compact_and_never_live_ready() -> None:
    bundle = get_paper_forward_v2_bundle()
    summary = paper_forward_evidence_v2.summarize_paper_forward_evidence_v2(bundle)

    assert summary["fixture_count"] == len(local_fixture_catalog.REQUIRED_FIXTURE_IDS)
    assert summary["regime_count"] >= 6
    assert summary["total_intents"] > 0
    assert summary["simulated_ledger_entries"] == summary["total_intents"]
    assert summary["classification"] in ALLOWED_CLASSIFICATIONS
    assert summary["classification"] != "LIVE_READY"
    assert summary["starting_balance"] == 500.0
    assert summary["ending_balance"] >= 500.0
    assert summary["return_pct"] >= 0.0
    assert summary["cost_drag_pct"] >= 0.0
    assert summary["capture_rate_pct"] >= 0.0
    assert summary["opportunity_quality_score"] >= 0.0
    assert summary["risk_governor_classification"] in ALLOWED_CLASSIFICATIONS
    assert summary["stress_classification"] in {*ALLOWED_CLASSIFICATIONS, "not_run"}
    assert summary["oos_classification"] in {*ALLOWED_CLASSIFICATIONS, "not_run"}
    assert summary["combined_stress_oos_classification"] in {*ALLOWED_CLASSIFICATIONS, "not_run"}
    assert summary["stress_survived_scenarios_pct"] >= 0.0
    assert summary["heldout_consistency_pct"] >= 0.0
    assert summary["degradation_pct"] >= 0.0
    assert summary["expanded_oos_classification"] in {*ALLOWED_CLASSIFICATIONS, "not_run"}
    assert summary["expanded_oos_heldout_consistency_pct"] >= 0.0
    assert summary["expanded_oos_degradation_pct"] >= 0.0
    assert summary["oos_repair_classification"] in {*ALLOWED_CLASSIFICATIONS, "not_run"}
    assert summary["low_vol_edge_classification"] in {*ALLOWED_CLASSIFICATIONS, "not_run"}
    assert summary["low_vol_policy_action"] in {"NO_TRADE_GATE", "REDUCED_SIZE", "EDGE_REDESIGN", "WATCHLIST", "not_run"}
    assert summary["redesigned_max_degradation_pct"] >= 0.0
    assert summary["low_vol_rejected_intents"] >= 0
    assert summary["original_max_degradation_pct"] >= summary["repaired_max_degradation_pct"]
    assert summary["degradation_improvement_pct"] >= 0.0
    assert summary["weakest_oos_split"]
    assert summary["stress_oos_ready"] in {True, False}
    assert summary["live_ready"] is False
    assert summary["live_trade_ready"] is False
    assert summary["protected_gate_required"] is True


def test_month_end_readiness_v2_keeps_live_trade_ready_false() -> None:
    bundle = get_paper_forward_v2_bundle()
    review = bundle["month_end_readiness_review"]

    assert review["classification"] in ALLOWED_CLASSIFICATIONS
    assert review["paper_forward_ready"] in {True, False}
    assert review["v2_evidence_ready"] in {True, False}
    assert review["live_trade_ready"] is False
    assert review["protected_gate_required"] is True
    assert review["evidence_summary"]["fixture_count"] == len(local_fixture_catalog.REQUIRED_FIXTURE_IDS)
    assert review["evidence_summary"]["starting_balance"] == 500.0
    assert review["evidence_summary"]["capture_rate_pct"] >= 0.0
    assert review["evidence_summary"]["risk_governor_classification"] in ALLOWED_CLASSIFICATIONS
    assert review["evidence_summary"]["stress_classification"] in {*ALLOWED_CLASSIFICATIONS, "not_run"}
    assert review["evidence_summary"]["oos_classification"] in {*ALLOWED_CLASSIFICATIONS, "not_run"}
    assert review["evidence_summary"]["combined_stress_oos_classification"] in {*ALLOWED_CLASSIFICATIONS, "not_run"}
    assert review["evidence_summary"]["heldout_consistency_pct"] >= 0.0
    assert review["evidence_summary"]["degradation_pct"] >= 0.0
    assert review["evidence_summary"]["expanded_oos_classification"] in {*ALLOWED_CLASSIFICATIONS, "not_run"}
    assert review["evidence_summary"]["expanded_oos_heldout_consistency_pct"] >= 0.0
    assert review["evidence_summary"]["expanded_oos_degradation_pct"] >= 0.0
    assert review["evidence_summary"]["oos_repair_classification"] in {*ALLOWED_CLASSIFICATIONS, "not_run"}
    assert review["evidence_summary"]["low_vol_edge_classification"] in {*ALLOWED_CLASSIFICATIONS, "not_run"}
    assert review["evidence_summary"]["low_vol_policy_action"] in {
        "NO_TRADE_GATE",
        "REDUCED_SIZE",
        "EDGE_REDESIGN",
        "WATCHLIST",
        "not_run",
    }
    assert review["evidence_summary"]["redesigned_max_degradation_pct"] >= 0.0
    assert review["evidence_summary"]["low_vol_rejected_intents"] >= 0
    assert (
        review["evidence_summary"]["original_max_degradation_pct"]
        >= review["evidence_summary"]["repaired_max_degradation_pct"]
    )
    assert review["evidence_summary"]["degradation_improvement_pct"] >= 0.0
    assert review["evidence_summary"]["weakest_oos_split"]
    assert review["evidence_summary"]["broker_paper_sandbox_ready"] is False
    assert review["next_safe_action"]


def test_compact_demo_function_exists_and_prints_safety_note(capsys) -> None:
    assert run_paper_forward_evidence_v2_demo.main([]) == 0
    output = capsys.readouterr().out

    assert "AIOS Forex Paper-Forward Evidence V2" in output
    assert "Mode: PAPER_ONLY" in output
    assert "Protected gate required: true" in output
    assert "Safety: no broker/API/network/live execution." in output


def test_v2_boundary_summary_blocks_live_broker_network_and_orders() -> None:
    boundary = paper_forward_evidence_v2.paper_forward_v2_boundary_summary()

    assert boundary["local_simulation_only"] is True
    assert boundary["broker_allowed"] is False
    assert boundary["broker_paper_orders"] is False
    assert boundary["network_allowed"] is False
    assert boundary["api_ingestion"] is False
    assert boundary["credentials_allowed"] is False
    assert boundary["live_trading"] is False
    assert boundary["live_order"] is False
    assert boundary["execution_allowed"] is False
    assert boundary["orders_allowed"] is False
    assert boundary["webhooks_allowed"] is False
    assert boundary["scheduler_allowed"] is False
    assert boundary["daemon_allowed"] is False


def test_v2_modules_have_no_forbidden_imports_or_calls() -> None:
    for path in (MODULE_PATH, DEMO_PATH):
        source = path.read_text(encoding="utf-8").lower()
        import_lines = "\n".join(
            line.strip()
            for line in source.splitlines()
            if line.startswith("import ") or line.startswith("from ")
        )

        for forbidden_import in ("requests", "socket", "urllib", "subprocess"):
            assert forbidden_import not in import_lines
        for forbidden_call in ("os.environ", "getenv", "open(", "write_text(", "write_bytes(", "start-process"):
            assert forbidden_call not in source
        for forbidden_call in ("broker sdk", "broker_sdk", "schedule.every", "daemon.daemoncontext"):
            assert forbidden_call not in source
