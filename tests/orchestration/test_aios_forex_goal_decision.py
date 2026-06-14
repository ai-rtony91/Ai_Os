from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_forex_goal_decision.py"
POLICY_SOURCE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_decision_policy.py"


def load_bridge_module():
    spec = importlib.util.spec_from_file_location("aios_forex_goal_decision", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def seed_required_components(repo_root: Path) -> None:
    module = load_bridge_module()
    for name, relative_path in module.FOREX_COMPONENT_PATHS.items():
        target = repo_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if name == "forex_decision_policy":
            target.write_text(POLICY_SOURCE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            target.write_text("# paper component placeholder\n", encoding="utf-8")


def acceptable_report() -> dict[str, object]:
    return {
        "allowed": True,
        "paper_only": True,
        "report_type": "paper_scorecard",
        "trade_count": 10,
        "win_rate": 60.0,
        "total_pnl": 125.0,
        "risk_flags": [],
    }


def test_goal_decision_bridge_imports():
    module = load_bridge_module()
    assert module.SCHEMA == "AIOS_FOREX_GOAL_DECISION.v1"
    assert callable(module.build_goal_decision)


def test_required_components_detected(tmp_path):
    module = load_bridge_module()
    seed_required_components(tmp_path)
    status = module.component_status(tmp_path)
    assert status
    assert all(status.values())


def test_missing_required_component_blocks(tmp_path):
    module = load_bridge_module()
    decision = module.build_goal_decision(tmp_path)
    assert decision["decision_bridge_passed"] is False
    assert decision["reason_code"] == "missing_required_components"


def test_acceptable_report_returns_continue_build(tmp_path):
    module = load_bridge_module()
    seed_required_components(tmp_path)
    decision = module.build_goal_decision(tmp_path, report=acceptable_report())
    assert decision["decision_bridge_passed"] is True
    assert decision["decision"] == "continue_build"
    assert decision["reason_code"] == "acceptable_report"
    assert decision["next_build_recommendation"].startswith("Continue")


def test_risk_flag_returns_stop_for_human_review(tmp_path):
    module = load_bridge_module()
    seed_required_components(tmp_path)
    report = acceptable_report()
    report["risk_flags"] = ["negative_total_pnl"]
    decision = module.build_goal_decision(tmp_path, report=report)
    assert decision["decision_bridge_passed"] is True
    assert decision["decision"] == "stop_for_human_review"
    assert decision["reason_code"] == "risk_flags_present"


def test_no_trades_returns_improve_data(tmp_path):
    module = load_bridge_module()
    seed_required_components(tmp_path)
    report = acceptable_report()
    report["trade_count"] = 0
    decision = module.build_goal_decision(tmp_path, report=report)
    assert decision["decision"] == "improve_data"
    assert decision["reason_code"] == "no_trades"


def test_low_win_rate_returns_improve_strategy(tmp_path):
    module = load_bridge_module()
    seed_required_components(tmp_path)
    report = acceptable_report()
    report["win_rate"] = 49.0
    decision = module.build_goal_decision(tmp_path, report=report)
    assert decision["decision"] == "improve_strategy"
    assert decision["reason_code"] == "low_win_rate"


def test_negative_pnl_returns_improve_risk_controls(tmp_path):
    module = load_bridge_module()
    seed_required_components(tmp_path)
    report = acceptable_report()
    report["total_pnl"] = -25.0
    decision = module.build_goal_decision(tmp_path, report=report)
    assert decision["decision"] == "improve_risk_controls"
    assert decision["reason_code"] == "negative_total_pnl"


def test_unsafe_fields_blocked_with_scanner_safe_placeholders(tmp_path):
    module = load_bridge_module()
    seed_required_components(tmp_path)
    assert module.build_goal_decision(tmp_path, report=acceptable_report(), broker_order=True)["reason_code"] == "broker_order_blocked"
    assert module.build_goal_decision(tmp_path, report=acceptable_report(), live_execution=True)["reason_code"] == "live_execution_blocked"
    assert module.build_goal_decision(tmp_path, report=acceptable_report(), credentials={"sample": "safe-placeholder"})["reason_code"] == "credentials_blocked"
    assert module.build_goal_decision(tmp_path, report=acceptable_report(), api_key="placeholder-safe")["reason_code"] == "api_key_blocked"
    assert module.build_goal_decision(tmp_path, report=acceptable_report(), real_order=True)["reason_code"] == "real_order_blocked"
    assert module.build_goal_decision(tmp_path, report=acceptable_report(), webhook_url="https://example.invalid/hook")["reason_code"] == "webhook_url_blocked"
    assert module.build_goal_decision(tmp_path, report=acceptable_report(), network=True)["reason_code"] == "network_blocked"


def test_safety_flags_block_mutation_and_execution():
    module = load_bridge_module()
    flags = module.safety_flags()
    assert flags
    assert all(value is False for value in flags.values())


def test_no_file_writes_or_network_usage_in_bridge_source():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["open(", "write_text", "write_bytes", "with open", "requests", "socket", "urllib", "http.client"]:
        assert forbidden not in source
