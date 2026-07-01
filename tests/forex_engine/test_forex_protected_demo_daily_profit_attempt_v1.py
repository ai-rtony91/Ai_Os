from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_protected_demo_daily_profit_attempt_v1 import (  # noqa: E402
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_DAILY_PROFIT_EVIDENCE_REQUIRED,
    BLOCKED_BY_EXECUTION_WINDOW,
    BLOCKED_BY_ORDER_CANDIDATE,
    BLOCKED_BY_POST_TRADE_REVIEW,
    BLOCKED_BY_RISK_LIMITS,
    BLOCKED_BY_SENSITIVE_DATA,
    CONTINUE_PROFIT_EVIDENCE_CAPTURE,
    HARD_FALSE_FIELDS,
    INCOMPLETE_INPUTS,
    NEXT_PACKET_CURRENT,
    NEXT_PACKET_LIVE_MICRO_REVIEW,
    NEXT_PACKET_OWNER_APPROVED_DEMO,
    PROTECTED_DEMO_DAILY_PROFIT_ATTEMPT_READY,
    READY_FOR_LIVE_MICRO_EXCEPTION_REVIEW_AFTER_DEMO_EVIDENCE,
    READY_FOR_OWNER_APPROVED_DEMO_ONE_ORDER_PACKET,
    SCHEMA,
    evaluate_forex_protected_demo_daily_profit_attempt_v1,
)


MODULE_PATH = (
    ROOT
    / "automation"
    / "forex_engine"
    / "forex_protected_demo_daily_profit_attempt_v1.py"
)


def _payload() -> dict:
    return {
        "daily_profit_evidence_result": {
            "daily_profit_status": "READY_FOR_PROTECTED_DEMO_PROFIT_ATTEMPT",
            "daily_profit_ready": True,
            "broker_api_called": False,
            "credential_read": False,
            "live_trade_executed": False,
            "demo_trade_executed": False,
            "money_moved": False,
        },
        "order_candidate": {
            "instrument": "EUR_USD",
            "side": "buy",
            "order_type": "market",
            "units": 1000,
            "setup_id": "setup-001",
            "evidence_id": "evidence-001",
            "expected_r_multiple": "1.8",
            "minimum_reward_risk_ratio": "1.5",
            "spread_within_limit": True,
            "slippage_within_limit": True,
            "session_allowed": True,
            "news_blackout_clear": True,
            "duplicate_candidate": False,
        },
        "risk_plan": {
            "max_risk_per_trade_pct": "0.01",
            "max_daily_loss_pct": "0.03",
            "stop_loss_present": True,
            "take_profit_present": True,
            "one_order_only": True,
            "max_order_count_this_packet": 1,
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "next_order_blocked_until_review": True,
        },
        "execution_window": {
            "execution_window_defined": True,
            "pre_trade_check_ready": True,
            "owner_can_cancel": True,
            "owner_approval_required": True,
            "credential_session_bridge_ready": True,
            "protected_runtime_gate_ready": True,
            "oanda_demo_mode_declared": True,
        },
        "protected_demo_policy": {
            "demo_only": True,
            "real_broker_call_allowed": False,
            "live_trading_allowed": False,
            "money_movement_allowed": False,
            "credential_read": False,
            "credential_stored": False,
            "broker_api_called": False,
            "dry_run_or_metadata_only": True,
            "actual_demo_execution_authorized": False,
        },
        "post_attempt_review": {
            "post_trade_review_required": True,
            "daily_pnl_record_required": True,
            "sanitized_receipt_required": True,
            "no_second_trade_without_review": True,
            "owner_review_required": True,
        },
    }


def _run(payload: dict | None = None) -> dict:
    return evaluate_forex_protected_demo_daily_profit_attempt_v1(payload)


def test_empty_payload_incomplete() -> None:
    result = _run({})
    assert result["schema"] == SCHEMA
    assert result["protected_demo_attempt_status"] == INCOMPLETE_INPUTS
    assert result["protected_demo_attempt_ready"] is False


def test_sensitive_data_blocked_and_value_not_echoed() -> None:
    payload = _payload()
    payload["order_candidate"]["nested"] = {"password": "DO-NOT-ECHO"}
    result = _run(payload)
    assert result["protected_demo_attempt_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "DO-NOT-ECHO" not in repr(result)


def test_banking_key_blocks() -> None:
    payload = _payload()
    payload["bank_plan"] = {"enabled": False}
    result = _run(payload)
    assert result["protected_demo_attempt_status"] == BLOCKED_BY_BANKING_FOCUS
    assert result["next_best_packet"] == NEXT_PACKET_CURRENT


def test_transfer_key_blocks() -> None:
    payload = _payload()
    payload["transfer_plan"] = {"enabled": False}
    result = _run(payload)
    assert result["protected_demo_attempt_status"] == BLOCKED_BY_BANKING_FOCUS


def test_daily_profit_evidence_missing_blocks() -> None:
    payload = _payload()
    payload.pop("daily_profit_evidence_result")
    result = _run(payload)
    assert (
        result["protected_demo_attempt_status"]
        == BLOCKED_BY_DAILY_PROFIT_EVIDENCE_REQUIRED
    )


def test_daily_profit_evidence_not_ready_blocks() -> None:
    payload = _payload()
    payload["daily_profit_evidence_result"]["daily_profit_status"] = (
        "CONTINUE_EVIDENCE_CAPTURE"
    )
    payload["daily_profit_evidence_result"]["daily_profit_ready"] = False
    result = _run(payload)
    assert (
        result["protected_demo_attempt_status"]
        == CONTINUE_PROFIT_EVIDENCE_CAPTURE
    )


def test_strong_payload_reaches_protected_demo_attempt_ready() -> None:
    result = _run(_payload())
    assert (
        result["protected_demo_attempt_status"]
        == PROTECTED_DEMO_DAILY_PROFIT_ATTEMPT_READY
    )
    assert result["protected_demo_attempt_ready"] is True
    assert result["next_best_packet"] == NEXT_PACKET_OWNER_APPROVED_DEMO


def test_owner_requested_demo_packet_routes_to_ready_packet() -> None:
    payload = _payload()
    payload["owner_requested_demo_packet"] = True
    result = _run(payload)
    assert (
        result["protected_demo_attempt_status"]
        == READY_FOR_OWNER_APPROVED_DEMO_ONE_ORDER_PACKET
    )
    assert result["next_best_packet"] == NEXT_PACKET_OWNER_APPROVED_DEMO


def test_demo_evidence_complete_routes_to_live_micro_review_after_demo_evidence() -> None:
    payload = _payload()
    payload["demo_evidence_complete"] = True
    result = _run(payload)
    assert (
        result["protected_demo_attempt_status"]
        == READY_FOR_LIVE_MICRO_EXCEPTION_REVIEW_AFTER_DEMO_EVIDENCE
    )
    assert result["next_best_packet"] == NEXT_PACKET_LIVE_MICRO_REVIEW


def test_missing_instrument_blocks_order_candidate() -> None:
    payload = _payload()
    payload["order_candidate"].pop("instrument")
    result = _run(payload)
    assert result["protected_demo_attempt_status"] == BLOCKED_BY_ORDER_CANDIDATE
    assert "missing_instrument" in result["blockers"]


def test_duplicate_candidate_blocks() -> None:
    payload = _payload()
    payload["order_candidate"]["duplicate_candidate"] = True
    result = _run(payload)
    assert result["protected_demo_attempt_status"] == BLOCKED_BY_ORDER_CANDIDATE
    assert "duplicate_candidate_clear" in result["blockers"]


def test_spread_not_within_limit_blocks() -> None:
    payload = _payload()
    payload["order_candidate"]["spread_within_limit"] = False
    result = _run(payload)
    assert result["protected_demo_attempt_status"] == BLOCKED_BY_ORDER_CANDIDATE
    assert "spread_within_limit" in result["blockers"]


def test_slippage_not_within_limit_blocks() -> None:
    payload = _payload()
    payload["order_candidate"]["slippage_within_limit"] = False
    result = _run(payload)
    assert result["protected_demo_attempt_status"] == BLOCKED_BY_ORDER_CANDIDATE
    assert "slippage_within_limit" in result["blockers"]


def test_risk_over_one_percent_blocks() -> None:
    payload = _payload()
    payload["risk_plan"]["max_risk_per_trade_pct"] = "0.011"
    result = _run(payload)
    assert result["protected_demo_attempt_status"] == BLOCKED_BY_RISK_LIMITS
    assert "risk_per_trade_gate" in result["blockers"]


def test_daily_loss_over_three_percent_blocks() -> None:
    payload = _payload()
    payload["risk_plan"]["max_daily_loss_pct"] = "0.031"
    result = _run(payload)
    assert result["protected_demo_attempt_status"] == BLOCKED_BY_RISK_LIMITS
    assert "daily_loss_gate" in result["blockers"]


def test_missing_stop_loss_blocks() -> None:
    payload = _payload()
    payload["risk_plan"]["stop_loss_present"] = False
    result = _run(payload)
    assert result["protected_demo_attempt_status"] == BLOCKED_BY_RISK_LIMITS
    assert "stop_loss_present" in result["blockers"]


def test_missing_take_profit_blocks() -> None:
    payload = _payload()
    payload["risk_plan"]["take_profit_present"] = False
    result = _run(payload)
    assert result["protected_demo_attempt_status"] == BLOCKED_BY_RISK_LIMITS
    assert "take_profit_present" in result["blockers"]


def test_kill_switch_active_blocks() -> None:
    payload = _payload()
    payload["risk_plan"]["kill_switch_active"] = True
    result = _run(payload)
    assert result["protected_demo_attempt_status"] == BLOCKED_BY_RISK_LIMITS
    assert "kill_switch_inactive" in result["blockers"]


def test_daily_loss_stop_active_blocks() -> None:
    payload = _payload()
    payload["risk_plan"]["daily_loss_stop_active"] = True
    result = _run(payload)
    assert result["protected_demo_attempt_status"] == BLOCKED_BY_RISK_LIMITS
    assert "daily_loss_stop_inactive" in result["blockers"]


def test_missing_execution_window_blocks() -> None:
    payload = _payload()
    payload["execution_window"]["execution_window_defined"] = False
    result = _run(payload)
    assert result["protected_demo_attempt_status"] == BLOCKED_BY_EXECUTION_WINDOW
    assert "execution_window_defined" in result["blockers"]


def test_missing_post_trade_review_blocks() -> None:
    payload = _payload()
    payload["post_attempt_review"]["post_trade_review_required"] = False
    result = _run(payload)
    assert result["protected_demo_attempt_status"] == BLOCKED_BY_POST_TRADE_REVIEW
    assert "post_trade_review_required" in result["blockers"]


def test_sanitized_packet_contains_no_credentials_account_or_api_keys() -> None:
    result = _run(_payload())
    packet = result["sanitized_demo_attempt_packet"]
    joined_keys = " ".join(packet).lower()
    forbidden = ["credential", "account", "api_key", "token", "password"]
    assert [marker for marker in forbidden if marker in joined_keys] == []
    assert packet["actual_demo_execution_authorized"] is False


def test_actual_demo_execution_authorized_false() -> None:
    result = _run(_payload())
    assert result["actual_demo_execution_authorized"] is False
    assert result["safety"]["actual_demo_execution_authorized"] is False
    assert result["sanitized_demo_attempt_packet"][
        "actual_demo_execution_authorized"
    ] is False


def test_all_hard_false_fields_remain_false() -> None:
    result = _run(_payload())
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False


def test_next_best_packet_routes_correctly() -> None:
    ready = _run(_payload())
    assert ready["next_best_packet"] == NEXT_PACKET_OWNER_APPROVED_DEMO
    blocked = _payload()
    blocked["order_candidate"]["spread_within_limit"] = False
    assert _run(blocked)["next_best_packet"] == NEXT_PACKET_CURRENT
    live_review = _payload()
    live_review["demo_evidence_complete"] = True
    assert _run(live_review)["next_best_packet"] == NEXT_PACKET_LIVE_MICRO_REVIEW


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
