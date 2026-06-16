from __future__ import annotations

from pathlib import Path

from automation.forex_engine import low_vol_edge_redesign
from automation.forex_engine import oos_expansion
from automation.forex_engine import oos_repair
from automation.forex_engine import run_low_vol_edge_redesign_demo


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "low_vol_edge_redesign.py"
DEMO_PATH = REPO_ROOT / "automation" / "forex_engine" / "run_low_vol_edge_redesign_demo.py"
ALLOWED_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}


def test_low_vol_edge_module_exists() -> None:
    assert MODULE_PATH.exists()


def test_diagnosis_identifies_holdout_low_vol_degradation() -> None:
    expanded = oos_expansion.run_expanded_oos_validation()
    repair = oos_repair.apply_oos_repair_policy(expanded)
    diagnosis = low_vol_edge_redesign.diagnose_low_vol_edge(repair, expanded)

    assert diagnosis["low_vol_split_detected"] is True
    assert diagnosis["low_vol_split_id"] == "holdout_by_regime:low_vol"
    assert diagnosis["weakest_split"] == "holdout_by_regime:low_vol"
    assert diagnosis["repaired_max_degradation_pct"] >= 0.0


def test_policy_includes_no_trade_gate_and_sizing_controls() -> None:
    policy = low_vol_edge_redesign.build_low_vol_edge_policy()

    assert policy["low_vol_no_trade_gate_enabled"] is True
    assert policy["minimum_range_proxy"] > 0.0
    assert policy["minimum_momentum_proxy"] > 0.0
    assert policy["maximum_spread_to_range_ratio"] < 1.0
    assert policy["minimum_signal_quality_score"] > 0.0
    assert policy["volatility_expansion_required"] is True
    assert policy["low_vol_size_multiplier"] == 0.0
    assert policy["reject_low_vol_chop"] is True
    assert policy["retain_audit_for_rejected_intents"] is True
    assert policy["max_allowed_degradation_pct"] == 35.0
    assert policy["security_gate_required_before_broker_paper"] is True
    assert policy["required_security_packet"] == "PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1"


def test_redesign_result_reports_degradation_rejections_and_audit() -> None:
    result = low_vol_edge_redesign.apply_low_vol_edge_redesign()

    assert result["original_max_degradation_pct"] >= result["repaired_max_degradation_pct"]
    assert result["repaired_max_degradation_pct"] >= result["redesigned_max_degradation_pct"]
    assert result["degradation_improvement_from_original_pct"] >= 0.0
    assert result["degradation_improvement_from_repair_pct"] >= 0.0
    assert result["weakest_split_before"] == "holdout_by_regime:low_vol"
    assert result["weakest_split_after"] == "holdout_by_regime:low_vol"
    assert result["low_vol_policy_action"] in {"NO_TRADE_GATE", "REDUCED_SIZE", "EDGE_REDESIGN", "WATCHLIST"}
    assert result["rejected_low_vol_intents"] > 0
    assert result["skipped_low_vol_intents"] > 0
    assert result["no_trade_low_vol_count"] == result["rejected_low_vol_intents"]
    assert result["low_vol_trade_allowed_count"] == 0
    assert result["audit_summary"]
    assert result["tradeoff_summary"]


def test_summary_and_classification_stay_inside_allowed_contract() -> None:
    result = low_vol_edge_redesign.apply_low_vol_edge_redesign()
    summary = low_vol_edge_redesign.summarize_low_vol_edge_redesign(result)

    assert result["classification"] in ALLOWED_CLASSIFICATIONS
    assert summary["classification"] in ALLOWED_CLASSIFICATIONS
    assert result["classification"] != "LIVE_READY"
    assert summary["classification"] != "LIVE_READY"
    assert result["broker_paper_contract_ready"] is False
    assert summary["broker_paper_contract_ready"] is False
    assert result["live_ready"] is False
    assert summary["live_ready"] is False
    assert result["protected_gate_required"] is True
    assert summary["protected_gate_required"] is True
    assert result["security_gate_required_before_broker_paper"] is True
    assert summary["security_gate_required_before_broker_paper"] is True


def test_boundary_summary_blocks_live_broker_network_orders_scheduler_and_daemon() -> None:
    boundary = low_vol_edge_redesign.low_vol_edge_boundary_summary()

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
    assert boundary["security_gate_required_before_broker_paper"] is True


def test_demo_module_imports_and_prints_required_lines(capsys) -> None:
    assert run_low_vol_edge_redesign_demo.main([]) == 0
    output = capsys.readouterr().out

    assert "AIOS Forex Low-Vol Edge Redesign Demo" in output
    assert "Mode: PAPER_ONLY" in output
    assert "Original max degradation pct:" in output
    assert "OOS repair max degradation pct:" in output
    assert "Redesigned max degradation pct:" in output
    assert "Low-vol action:" in output
    assert "Rejected low-vol intents:" in output
    assert "Allowed low-vol intents:" in output
    assert "Broker-paper contract ready: false" in output
    assert "Live ready: false" in output
    assert "Security gate required before broker-paper: true" in output
    assert "Safety: no broker/API/network/live execution." in output


def test_low_vol_modules_have_no_forbidden_imports_or_execution_calls() -> None:
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
