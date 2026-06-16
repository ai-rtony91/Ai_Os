from __future__ import annotations

from pathlib import Path

from automation.forex_engine import oos_expansion
from automation.forex_engine import oos_repair
from automation.forex_engine import run_oos_repair_demo


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "oos_repair.py"
DEMO_PATH = REPO_ROOT / "automation" / "forex_engine" / "run_oos_repair_demo.py"
ALLOWED_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}


def test_oos_repair_module_exists() -> None:
    assert MODULE_PATH.exists()


def test_diagnosis_identifies_low_vol_degradation() -> None:
    expanded = oos_expansion.run_expanded_oos_validation()
    diagnosis = oos_repair.diagnose_oos_degradation(expanded)

    assert diagnosis["mode"] == "PAPER_ONLY"
    assert diagnosis["low_vol_split_detected"] is True
    assert diagnosis["low_vol_split_id"] == "holdout_by_regime:low_vol"
    assert diagnosis["max_degradation_pct"] >= 0.0
    assert "low-volatility" in diagnosis["diagnosis"]
    assert diagnosis["live_ready"] is False
    assert diagnosis["protected_gate_required"] is True


def test_repair_plan_includes_low_vol_filters_and_sizing_controls() -> None:
    plan = oos_repair.build_oos_repair_plan()

    assert plan["low_vol_trade_filter_enabled"] is True
    assert plan["minimum_range_proxy"] > 0.0
    assert plan["minimum_momentum_proxy"] > 0.0
    assert plan["maximum_spread_to_range_ratio"] > 0.0
    assert 0.0 < plan["low_vol_size_multiplier"] < 1.0
    assert plan["skip_low_vol_low_quality_intents"] is True
    assert plan["max_allowed_degradation_pct"] == 35.0
    assert plan["require_degradation_improvement"] is True
    assert plan["require_skipped_trade_audit"] is True
    assert plan["live_ready"] is False


def test_repair_result_reports_degradation_and_skipped_low_vol_intents() -> None:
    result = oos_repair.apply_oos_repair_policy()

    assert result["original_max_degradation_pct"] >= result["repaired_max_degradation_pct"]
    assert result["degradation_improvement_pct"] >= 0.0
    assert result["weakest_split_before"] == "holdout_by_regime:low_vol"
    assert result["weakest_split_after"]
    assert result["retained_intents"] >= 0
    assert result["skipped_intents"] >= 0
    assert result["skipped_low_vol_intents"] > 0
    assert result["skipped_intent_audit"]
    assert result["tradeoff_summary"]
    assert result["repaired_classification"] in ALLOWED_CLASSIFICATIONS
    assert result["repaired_classification"] != "LIVE_READY"
    assert result["broker_paper_ready"] is False
    assert result["broker_paper_contract_ready"] is False
    assert result["live_ready"] is False
    assert result["protected_gate_required"] is True


def test_repair_summary_is_compact_safe_and_uses_allowed_classification() -> None:
    result = oos_repair.apply_oos_repair_policy()
    summary = oos_repair.summarize_oos_repair(result)

    assert summary["classification"] in ALLOWED_CLASSIFICATIONS
    assert summary["classification"] != "LIVE_READY"
    assert summary["oos_repair_classification"] in ALLOWED_CLASSIFICATIONS
    assert summary["original_max_degradation_pct"] >= summary["repaired_max_degradation_pct"]
    assert summary["skipped_low_vol_intents"] > 0
    assert summary["broker_paper_ready"] is False
    assert summary["broker_paper_contract_ready"] is False
    assert summary["live_ready"] is False
    assert summary["protected_gate_required"] is True


def test_boundary_summary_blocks_broker_live_network_orders_scheduler_and_daemon() -> None:
    boundary = oos_repair.oos_repair_boundary_summary()

    assert boundary["local_simulation_only"] is True
    assert boundary["broker_allowed"] is False
    assert boundary["broker_paper_orders"] is False
    assert boundary["network_allowed"] is False
    assert boundary["api_ingestion"] is False
    assert boundary["credentials_allowed"] is False
    assert boundary["secrets_allowed"] is False
    assert boundary["live_trading"] is False
    assert boundary["orders_allowed"] is False
    assert boundary["scheduler_allowed"] is False
    assert boundary["daemon_allowed"] is False


def test_demo_module_imports_and_prints_safety_note(capsys) -> None:
    assert run_oos_repair_demo.main([]) == 0
    output = capsys.readouterr().out

    assert "AIOS Forex OOS Repair Demo" in output
    assert "Mode: PAPER_ONLY" in output
    assert "Original max degradation pct:" in output
    assert "Repaired max degradation pct:" in output
    assert "Skipped low-vol intents:" in output
    assert "Broker-paper contract ready: false" in output
    assert "Live ready: false" in output
    assert "Protected gate required: true" in output
    assert "Safety: no broker/API/network/live execution." in output


def test_oos_repair_modules_have_no_forbidden_imports_or_execution_calls() -> None:
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
