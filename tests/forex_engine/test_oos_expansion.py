from __future__ import annotations

from pathlib import Path

from automation.forex_engine import broker_paper_sandbox_readiness
from automation.forex_engine import local_fixture_catalog
from automation.forex_engine import oos_expansion
from automation.forex_engine import oos_repair
from automation.forex_engine import run_oos_expansion_demo


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "oos_expansion.py"
DEMO_PATH = REPO_ROOT / "automation" / "forex_engine" / "run_oos_expansion_demo.py"
ALLOWED_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}
REQUIRED_SPLIT_TYPES = {
    "holdout_by_regime",
    "holdout_by_symbol",
    "holdout_by_timeframe",
    "leave_one_regime_out",
    "leave_one_symbol_out",
    "leave_one_timeframe_out",
    "weak_regime_holdout",
    "stress_repaired_holdout",
    "rotating_train_test_windows",
}


def test_expanded_oos_plan_includes_required_split_types() -> None:
    plan = oos_expansion.build_expanded_oos_plan()

    assert plan["mode"] == "PAPER_ONLY"
    assert plan["fixture_count"] == len(local_fixture_catalog.REQUIRED_FIXTURE_IDS)
    assert plan["fixture_count"] >= 14
    assert REQUIRED_SPLIT_TYPES.issubset(set(plan["split_types"]))
    assert plan["splits"]
    assert plan["network_allowed"] is False
    assert plan["broker_allowed"] is False
    assert plan["live_ready"] is False
    assert plan["protected_gate_required"] is True


def test_expanded_oos_validation_runs_locally_and_reports_degradation() -> None:
    result = oos_expansion.run_expanded_oos_validation()
    summary = oos_expansion.summarize_expanded_oos(result)

    assert result["mode"] == "PAPER_ONLY"
    assert result["fixture_count"] == len(local_fixture_catalog.REQUIRED_FIXTURE_IDS)
    assert result["split_count"] >= 6
    assert result["split_results"]
    assert result["heldout_consistency_pct"] >= 0.0
    assert result["degradation_pct"] >= 0.0
    assert result["max_degradation_pct"] >= 0.0
    assert result["weakest_split"]["split_id"]
    assert result["classification"] in ALLOWED_CLASSIFICATIONS
    assert result["classification"] != "LIVE_READY"
    assert result["broker_paper_contract_ready"] is False
    assert result["live_ready"] is False
    assert result["protected_gate_required"] is True
    assert summary["classification"] in ALLOWED_CLASSIFICATIONS
    assert summary["weakest_split_id"]


def test_each_expanded_oos_split_is_simulated_only() -> None:
    result = oos_expansion.run_expanded_oos_validation()

    for split in result["split_results"]:
        assert split["split_id"]
        assert split["split_type"] in REQUIRED_SPLIT_TYPES
        assert split["train_fixture_count"] >= 0
        assert split["heldout_fixture_count"] > 0
        assert split["heldout_pnl"] >= 0.0
        assert split["heldout_return_pct"] >= 0.0
        assert split["heldout_consistency_pct"] >= 0.0
        assert split["degradation_pct"] >= 0.0
        assert split["classification"] in ALLOWED_CLASSIFICATIONS
        assert split["classification"] != "LIVE_READY"
        assert split["live_ready"] is False
        assert split["protected_gate_required"] is True


def test_broker_paper_ready_remains_false_when_expanded_oos_is_watchlist() -> None:
    expanded = oos_expansion.run_expanded_oos_validation()
    expanded["classification"] = "WATCHLIST"
    expanded["blockers"] = ["expanded_oos_degradation_exceeds_policy"]

    readiness = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness(
        expanded_oos=expanded,
    )

    assert readiness["readiness_status"] == "WATCHLIST"
    assert readiness["broker_paper_sandbox_contract_ready"] is False
    assert readiness["expanded_oos_classification"] == "WATCHLIST"
    assert readiness["live_trade_ready"] is False
    assert readiness["protected_gate_required"] is True


def test_expanded_oos_accepts_repair_result_and_preserves_watchlist_when_repair_is_watchlist() -> None:
    expanded = oos_expansion.run_expanded_oos_validation()
    repair = oos_repair.apply_oos_repair_policy(expanded)
    repaired = oos_expansion.run_expanded_oos_validation(oos_repair_result=repair)
    summary = oos_expansion.summarize_expanded_oos(repaired)

    assert repaired["oos_repair_classification"] == repair["repaired_classification"]
    assert repaired["original_max_degradation_pct"] >= repaired["repaired_max_degradation_pct"]
    assert repaired["degradation_improvement_pct"] >= 0.0
    assert repaired["classification"] == "WATCHLIST"
    assert "oos_repair_degradation_exceeds_policy" in repaired["blockers"]
    assert summary["oos_repair_classification"] == repair["repaired_classification"]
    assert summary["repaired_max_degradation_pct"] == repaired["repaired_max_degradation_pct"]
    assert repaired["broker_paper_contract_ready"] is False
    assert repaired["live_ready"] is False
    assert repaired["protected_gate_required"] is True


def test_expanded_oos_can_advance_to_paper_forward_ready_only_when_repair_clears_policy() -> None:
    expanded = oos_expansion.run_expanded_oos_validation()
    repair = {
        "repaired_classification": "PAPER_FORWARD_READY",
        "classification": "PAPER_FORWARD_READY",
        "original_max_degradation_pct": expanded["max_degradation_pct"],
        "repaired_max_degradation_pct": 20.0,
        "degradation_improvement_pct": expanded["max_degradation_pct"] - 20.0,
        "blockers": [],
        "broker_paper_ready": False,
        "broker_paper_contract_ready": False,
        "live_ready": False,
        "protected_gate_required": True,
    }
    repaired = oos_expansion.run_expanded_oos_validation(oos_repair_result=repair)

    assert repaired["classification"] == "PAPER_FORWARD_READY"
    assert repaired["max_degradation_pct"] == 20.0
    assert repaired["live_ready"] is False


def test_boundary_summary_blocks_broker_network_orders_and_live() -> None:
    boundary = oos_expansion.oos_expansion_boundary_summary()

    assert boundary["local_simulation_only"] is True
    assert boundary["deterministic_fixtures_only"] is True
    assert boundary["broker_allowed"] is False
    assert boundary["broker_paper_orders"] is False
    assert boundary["network_allowed"] is False
    assert boundary["api_ingestion"] is False
    assert boundary["credentials_allowed"] is False
    assert boundary["live_trading"] is False
    assert boundary["live_ready"] is False
    assert boundary["orders_allowed"] is False
    assert boundary["scheduler_allowed"] is False
    assert boundary["daemon_allowed"] is False


def test_compact_oos_expansion_demo_function_exists_and_prints_safety_note(capsys) -> None:
    assert run_oos_expansion_demo.main([]) == 0
    output = capsys.readouterr().out

    assert "AIOS Forex OOS Expansion Demo" in output
    assert "Mode: PAPER_ONLY" in output
    assert "Fixtures:" in output
    assert "Splits:" in output
    assert "Broker-paper contract ready:" in output
    assert "Live ready: false" in output
    assert "Protected gate required: true" in output
    assert "Safety: no broker/API/network/live execution." in output


def test_oos_expansion_modules_have_no_forbidden_imports_or_execution_calls() -> None:
    for path in (MODULE_PATH, DEMO_PATH):
        source = path.read_text(encoding="utf-8").lower()
        import_lines = "\n".join(
            line.strip()
            for line in source.splitlines()
            if line.startswith("import ") or line.startswith("from ")
        )

        for forbidden_import in ("requests", "socket", "urllib", "subprocess", "schedule", "daemon"):
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
