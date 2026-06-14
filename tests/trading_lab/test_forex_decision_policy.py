from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_decision_policy.py"


def load_policy_module():
    spec = importlib.util.spec_from_file_location("forex_decision_policy", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def acceptable_report():
    return {
        "allowed": True,
        "paper_only": True,
        "trade_count": 10,
        "win_rate": 60.0,
        "total_pnl": 125.0,
        "risk_flags": [],
    }


def test_module_imports():
    policy = load_policy_module()
    assert callable(policy.decide_next_action)


def test_acceptable_report_returns_continue_build():
    policy = load_policy_module()
    decision = policy.decide_next_action(acceptable_report())
    assert decision["allowed"] is True
    assert decision["decision"] == "continue_build"
    assert decision["reason_code"] == "acceptable_report"
    assert decision["execution_allowed"] is False
    assert decision["broker_execution"] is False


def test_risk_flag_returns_stop_for_human_review():
    policy = load_policy_module()
    report = acceptable_report()
    report["risk_flags"] = ["negative_total_pnl"]
    decision = policy.decide_next_action(report)
    assert decision["decision"] == "stop_for_human_review"
    assert decision["reason_code"] == "risk_flags_present"


def test_no_trades_returns_improve_data():
    policy = load_policy_module()
    report = acceptable_report()
    report["trade_count"] = 0
    decision = policy.decide_next_action(report)
    assert decision["decision"] == "improve_data"
    assert decision["reason_code"] == "no_trades"


def test_low_win_rate_returns_improve_strategy():
    policy = load_policy_module()
    report = acceptable_report()
    report["win_rate"] = 49.0
    decision = policy.decide_next_action(report)
    assert decision["decision"] == "improve_strategy"
    assert decision["reason_code"] == "low_win_rate"


def test_negative_pnl_returns_improve_risk_controls():
    policy = load_policy_module()
    report = acceptable_report()
    report["total_pnl"] = -25.0
    decision = policy.decide_next_action(report)
    assert decision["decision"] == "improve_risk_controls"
    assert decision["reason_code"] == "negative_total_pnl"


def test_missing_or_invalid_report_blocked():
    policy = load_policy_module()
    assert policy.decide_next_action({})["reason_code"] == "invalid_report"
    assert policy.decide_next_action("not-a-report")["reason_code"] == "invalid_report"


def test_unsafe_scope_fields_are_blocked_with_safe_placeholders():
    policy = load_policy_module()
    assert policy.decide_next_action(acceptable_report(), broker_order=True)["reason_code"] == "broker_order_blocked"
    assert policy.decide_next_action(acceptable_report(), live_execution=True)["reason_code"] == "live_execution_blocked"
    assert policy.decide_next_action(acceptable_report(), credentials={"sample": "safe-placeholder"})["reason_code"] == "credentials_blocked"
    assert policy.decide_next_action(acceptable_report(), api_key="placeholder-safe")["reason_code"] == "api_key_blocked"
    assert policy.decide_next_action(acceptable_report(), real_order=True)["reason_code"] == "real_order_blocked"
    assert policy.decide_next_action(acceptable_report(), webhook_url="https://example.invalid/hook")["reason_code"] == "webhook_url_blocked"
    assert policy.decide_next_action(acceptable_report(), network=True)["reason_code"] == "network_blocked"


def test_no_file_writes_or_network_usage():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["open(", "write_text", "write_bytes", "with open", "pathlib", "requests", "socket"]:
        assert forbidden not in source
