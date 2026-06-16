from __future__ import annotations

from pathlib import Path

from automation.forex_engine import local_fixture_catalog
from automation.forex_engine import paper_forward_evidence_v2
from automation.forex_engine import run_stress_repair_demo
from automation.forex_engine import stress_repair


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "stress_repair.py"
DEMO_PATH = REPO_ROOT / "automation" / "forex_engine" / "run_stress_repair_demo.py"
ALLOWED_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}


def test_stress_repair_module_diagnoses_current_watchlist_blockers() -> None:
    bundle = paper_forward_evidence_v2.build_paper_forward_evidence_v2()
    diagnosis = stress_repair.diagnose_stress_blockers(
        bundle["paper_forward_stress"],
        bundle["broker_paper_sandbox_readiness"],
    )

    assert diagnosis["mode"] == "PAPER_ONLY"
    assert diagnosis["stress_classification"] in ALLOWED_CLASSIFICATIONS
    assert diagnosis["worst_scenario_id"] == "disaster_case"
    assert diagnosis["half_capture_status"]["scenario_id"] == "half_capture_rate"
    assert "capture" in diagnosis["half_capture_status"]["failure_reason"]
    assert diagnosis["live_ready"] is False
    assert diagnosis["protected_gate_required"] is True


def test_repair_plan_includes_half_capture_repair_and_conservative_knobs() -> None:
    bundle = paper_forward_evidence_v2.build_paper_forward_evidence_v2()
    plan = stress_repair.build_stress_repair_plan(
        bundle["paper_forward_stress"],
        bundle["opportunity_capture"],
    )

    assert plan["mode"] == "PAPER_ONLY"
    assert plan["half_capture_survival_floor"] == 0.0
    assert plan["minimum_stress_survived_pct"] >= 80.0
    assert plan["reduce_size_on_high_cost_regime"] is True
    assert plan["skip_low_quality_intents"] is True
    assert plan["skip_high_slippage_regime"] is True
    assert plan["cap_position_size_multiplier"] < 1.0
    assert any("half-capture" in action for action in plan["repair_actions"])
    assert plan["live_ready"] is False
    assert plan["protected_gate_required"] is True


def test_stress_repair_output_reports_tradeoff_and_keeps_live_blocked() -> None:
    bundle = paper_forward_evidence_v2.build_paper_forward_evidence_v2()
    result = stress_repair.apply_local_stress_repair_policy(bundle)

    assert result["mode"] == "PAPER_ONLY"
    assert result["original_classification"] in ALLOWED_CLASSIFICATIONS
    assert result["repaired_classification"] in ALLOWED_CLASSIFICATIONS
    assert result["repaired_classification"] != "LIVE_READY"
    assert result["skipped_intents"] >= 0
    assert result["retained_intents"] > 0
    assert result["retained_fixture_count"] == len(local_fixture_catalog.REQUIRED_FIXTURE_IDS)
    assert result["retained_regime_count"] >= 7
    assert result["tradeoff_summary"]
    assert result["repaired_worst_stress_pnl"] >= 0.0
    assert result["repaired_stress_survived_pct"] >= 80.0
    assert result["half_capture_repair"]["scenario_id"] == "half_capture_rate"
    assert result["broker_paper_ready"] is False
    assert result["live_ready"] is False
    assert result["protected_gate_required"] is True


def test_stress_repair_summary_is_compact_and_safe() -> None:
    result = stress_repair.apply_local_stress_repair_policy()
    summary = stress_repair.summarize_stress_repair(result)

    assert summary["stress_repair_status"] in ALLOWED_CLASSIFICATIONS
    assert summary["repaired_stress_classification"] in ALLOWED_CLASSIFICATIONS
    assert summary["repaired_stress_survived_pct"] >= 0.0
    assert summary["repaired_worst_stress_pnl"] >= 0.0
    assert summary["tradeoff_summary"]
    assert summary["retained_intents"] > 0
    assert summary["skipped_intents"] >= 0
    assert summary["broker_paper_ready"] is False
    assert summary["live_ready"] is False
    assert summary["protected_gate_required"] is True


def test_stress_repair_boundary_blocks_broker_live_network_and_orders() -> None:
    boundary = stress_repair.stress_repair_boundary_summary()

    assert boundary["local_simulation_only"] is True
    assert boundary["broker_allowed"] is False
    assert boundary["broker_paper_orders"] is False
    assert boundary["network_allowed"] is False
    assert boundary["api_ingestion"] is False
    assert boundary["credentials_allowed"] is False
    assert boundary["live_trading"] is False
    assert boundary["orders_allowed"] is False
    assert boundary["scheduler_allowed"] is False
    assert boundary["daemon_allowed"] is False
    assert boundary["protected_gate_required"] is True


def test_compact_stress_repair_demo_function_exists_and_prints_safety_note(capsys) -> None:
    assert run_stress_repair_demo.main([]) == 0
    output = capsys.readouterr().out

    assert "AIOS Forex Stress Repair Demo" in output
    assert "Mode: PAPER_ONLY" in output
    assert "Original stress classification:" in output
    assert "Repaired stress classification:" in output
    assert "Broker-paper ready: false" in output
    assert "Live ready: false" in output
    assert "Protected gate required: true" in output
    assert "Safety: no broker/API/network/live execution." in output


def test_stress_repair_modules_have_no_forbidden_imports_or_execution_calls() -> None:
    for path in (MODULE_PATH, DEMO_PATH):
        source = path.read_text(encoding="utf-8").lower()
        import_lines = "\n".join(
            line.strip()
            for line in source.splitlines()
            if line.startswith("import ") or line.startswith("from ")
        )

        for forbidden_import in ("requests", "socket", "urllib", "subprocess", "os", "schedule", "daemon"):
            assert forbidden_import not in import_lines
        for line in import_lines.splitlines():
            assert not line.startswith("import broker")
            assert not line.startswith("from broker")
            assert not line.startswith("import oanda")
            assert not line.startswith("from oanda")
        for forbidden_call in (
            "os.environ",
            "getenv",
            "broker_sdk",
            "oanda",
            "schedule.every",
            "daemon.daemoncontext",
            "open(",
            "write_text(",
            "write_bytes(",
            "start-process",
        ):
            assert forbidden_call not in source
