from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_daily_profit_execution_evidence_v1 import (  # noqa: E402
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_EXECUTION_READINESS,
    BLOCKED_BY_NO_PROFIT_EDGE_EVIDENCE,
    BLOCKED_BY_POST_TRADE_REVIEW,
    BLOCKED_BY_RISK_LIMITS,
    BLOCKED_BY_SENSITIVE_DATA,
    DAILY_PROFIT_EXECUTION_EVIDENCE_READY,
    FIFTY_PERCENT_REVIEW_BAND,
    HARD_FALSE_FIELDS,
    INCOMPLETE_INPUTS,
    NEXT_PACKET_CURRENT,
    NEXT_PACKET_PROTECTED_DEMO,
    ONE_HUNDRED_PERCENT_REVIEW_BAND,
    ONE_HUNDRED_TWENTY_PERCENT_STRESS_REVIEW_BAND,
    SCHEMA,
    TWENTY_PERCENT_REVIEW_BAND,
    evaluate_forex_daily_profit_execution_evidence_v1,
)


MODULE_PATH = (
    ROOT
    / "automation"
    / "forex_engine"
    / "forex_daily_profit_execution_evidence_v1.py"
)


def _payload() -> dict:
    return {
        "evidence_sample_count": 80,
        "min_evidence_sample_count": 50,
        "expectancy_positive": True,
        "profit_factor": "1.65",
        "min_profit_factor": "1.25",
        "max_drawdown_pct": "0.08",
        "max_allowed_drawdown_pct": "0.12",
        "walk_forward_gate_cleared": True,
        "out_of_sample_passed": True,
        "spread_slippage_model_present": True,
        "daily_profit_target_defined": True,
        "guaranteed_profit_claimed": False,
        "fixed_return_target_promised": False,
        "protected_runtime_gate_ready": True,
        "credential_session_bridge_ready": True,
        "post_trade_review_ready": True,
        "twenty_two_hour_six_day_ready": True,
        "broker_mode_declared": "OANDA_DEMO",
        "one_order_gate_ready": True,
        "owner_approval_required": True,
        "broker_api_called": False,
        "credential_read": False,
        "live_trade_executed": False,
        "demo_trade_executed": False,
        "max_risk_per_trade_pct": "0.01",
        "max_daily_loss_pct": "0.03",
        "stop_loss_required": True,
        "take_profit_required": True,
        "kill_switch_ready": True,
        "kill_switch_active": False,
        "daily_loss_stop_ready": True,
        "daily_loss_stop_active": False,
        "one_order_only": True,
        "next_order_blocked_until_review": True,
        "pre_trade_check_ready": True,
        "execution_window_defined": True,
        "post_trade_review_required": True,
        "daily_pnl_record_required": True,
        "no_second_trade_without_review": True,
        "owner_can_stop": True,
    }


def _run(payload: dict | None = None) -> dict:
    return evaluate_forex_daily_profit_execution_evidence_v1(payload)


def test_empty_payload_incomplete() -> None:
    result = _run({})
    assert result["schema"] == SCHEMA
    assert result["daily_profit_status"] == INCOMPLETE_INPUTS
    assert result["daily_profit_ready"] is False


def test_sensitive_data_blocked_and_value_not_echoed() -> None:
    payload = _payload()
    payload["nested"] = {"password": "DO-NOT-ECHO"}
    result = _run(payload)
    assert result["daily_profit_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "DO-NOT-ECHO" not in repr(result)


def test_banking_focus_requested_blocks() -> None:
    payload = _payload()
    payload["banking_focus_requested"] = True
    result = _run(payload)
    assert result["daily_profit_status"] == BLOCKED_BY_BANKING_FOCUS
    assert result["next_best_packet"] == NEXT_PACKET_CURRENT
    assert "Banking deferred until realized profit exists" in repr(result)


def test_bank_key_blocks_as_banking_focus() -> None:
    payload = _payload()
    payload["bank_plan"] = {"enabled": False}
    assert _run(payload)["daily_profit_status"] == BLOCKED_BY_BANKING_FOCUS


def test_withdrawal_key_blocks_as_banking_focus() -> None:
    payload = _payload()
    payload["withdrawal_plan"] = {"enabled": False}
    assert _run(payload)["daily_profit_status"] == BLOCKED_BY_BANKING_FOCUS


def test_transfer_key_blocks_as_banking_focus() -> None:
    payload = _payload()
    payload["transfer_plan"] = {"enabled": False}
    assert _run(payload)["daily_profit_status"] == BLOCKED_BY_BANKING_FOCUS


def test_safe_strong_payload_reaches_daily_profit_evidence_ready() -> None:
    result = _run(_payload())
    assert (
        result["daily_profit_status"]
        == DAILY_PROFIT_EXECUTION_EVIDENCE_READY
    )
    assert result["daily_profit_ready"] is True
    assert result["next_best_packet"] == NEXT_PACKET_PROTECTED_DEMO


def test_insufficient_sample_blocks() -> None:
    payload = _payload()
    payload["evidence_sample_count"] = 10
    result = _run(payload)
    assert result["daily_profit_status"] == BLOCKED_BY_NO_PROFIT_EDGE_EVIDENCE
    assert "sample_gate_cleared" in result["blockers"]


def test_negative_expectancy_blocks() -> None:
    payload = _payload()
    payload["expectancy_positive"] = False
    result = _run(payload)
    assert result["daily_profit_status"] == BLOCKED_BY_NO_PROFIT_EDGE_EVIDENCE
    assert "expectancy_positive" in result["blockers"]


def test_low_profit_factor_blocks() -> None:
    payload = _payload()
    payload["profit_factor"] = "1.05"
    result = _run(payload)
    assert result["daily_profit_status"] == BLOCKED_BY_NO_PROFIT_EDGE_EVIDENCE
    assert "profit_factor_gate_cleared" in result["blockers"]


def test_excessive_drawdown_blocks() -> None:
    payload = _payload()
    payload["max_drawdown_pct"] = "0.20"
    result = _run(payload)
    assert result["daily_profit_status"] == BLOCKED_BY_RISK_LIMITS
    assert "drawdown_limit_exceeded" in result["blockers"]


def test_guaranteed_profit_claim_blocks() -> None:
    payload = _payload()
    payload["guaranteed_profit_claimed"] = True
    result = _run(payload)
    assert result["daily_profit_status"] == BLOCKED_BY_NO_PROFIT_EDGE_EVIDENCE
    assert "guaranteed_profit_claim_detected" in result["blockers"]


def test_fixed_return_promise_blocks() -> None:
    payload = _payload()
    payload["fixed_return_target_promised"] = True
    result = _run(payload)
    assert result["daily_profit_status"] == BLOCKED_BY_NO_PROFIT_EDGE_EVIDENCE
    assert "fixed_return_promise_detected" in result["blockers"]


def test_missing_protected_runtime_gate_blocks_execution_readiness() -> None:
    payload = _payload()
    payload["protected_runtime_gate_ready"] = False
    result = _run(payload)
    assert result["daily_profit_status"] == BLOCKED_BY_EXECUTION_READINESS
    assert "protected_runtime_gate_ready" in result["blockers"]


def test_risk_over_limit_blocks() -> None:
    payload = _payload()
    payload["max_risk_per_trade_pct"] = "0.02"
    result = _run(payload)
    assert result["daily_profit_status"] == BLOCKED_BY_RISK_LIMITS
    assert "risk_per_trade_gate" in result["blockers"]


def test_kill_switch_active_blocks() -> None:
    payload = _payload()
    payload["kill_switch_active"] = True
    result = _run(payload)
    assert result["daily_profit_status"] == BLOCKED_BY_RISK_LIMITS
    assert "kill_switch_inactive" in result["blockers"]


def test_daily_loss_stop_active_blocks() -> None:
    payload = _payload()
    payload["daily_loss_stop_active"] = True
    result = _run(payload)
    assert result["daily_profit_status"] == BLOCKED_BY_RISK_LIMITS
    assert "daily_loss_stop_inactive" in result["blockers"]


def test_missing_post_trade_review_blocks() -> None:
    payload = _payload()
    payload["post_trade_review_ready"] = False
    result = _run(payload)
    assert result["daily_profit_status"] == BLOCKED_BY_POST_TRADE_REVIEW
    assert "post_trade_review_not_ready" in result["blockers"]


def test_twenty_percent_band_assigned_correctly() -> None:
    payload = _payload()
    payload["observed_return_pct"] = "0.20"
    result = _run(payload)
    assert result["return_discovery_band"] == TWENTY_PERCENT_REVIEW_BAND


def test_fifty_percent_band_assigned_correctly() -> None:
    payload = _payload()
    payload["observed_return_pct"] = "0.50"
    result = _run(payload)
    assert result["return_discovery_band"] == FIFTY_PERCENT_REVIEW_BAND


def test_one_hundred_percent_band_assigned_as_stress_review_band() -> None:
    payload = _payload()
    payload["observed_return_pct"] = "1.00"
    result = _run(payload)
    assert result["return_discovery_band"] == ONE_HUNDRED_PERCENT_REVIEW_BAND
    assert result["daily_profit_status"] == BLOCKED_BY_RISK_LIMITS


def test_one_hundred_twenty_percent_band_assigned_as_stress_review_band() -> None:
    payload = _payload()
    payload["observed_return_pct"] = "1.20"
    result = _run(payload)
    assert (
        result["return_discovery_band"]
        == ONE_HUNDRED_TWENTY_PERCENT_STRESS_REVIEW_BAND
    )
    assert result["daily_profit_status"] == BLOCKED_BY_RISK_LIMITS


def test_all_hard_false_fields_remain_false() -> None:
    result = _run(_payload())
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False


def test_next_best_packet_routes_correctly() -> None:
    ready = _run(_payload())
    assert ready["next_best_packet"] == NEXT_PACKET_PROTECTED_DEMO
    sensitive = _payload()
    sensitive["api_key"] = "sk-DO-NOT-ECHO"
    assert _run(sensitive)["next_best_packet"] == NEXT_PACKET_CURRENT
    banking = _payload()
    banking["transfer_plan"] = {"enabled": False}
    assert _run(banking)["next_best_packet"] == NEXT_PACKET_CURRENT


def test_production_source_has_no_forbidden_runtime_markers() -> None:
    text = MODULE_PATH.read_text(encoding="utf-8").lower()
    forbidden = [
        "requests",
        "socket",
        "urllib",
        "subprocess",
        "os.environ",
        "broker_sdk",
        "schedule.every",
        "start-process",
    ]
    assert [marker for marker in forbidden if marker in text] == []
