from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_owner_approved_demo_one_order_profit_attempt_execution_v1 import (  # noqa: E402
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_DAILY_LOSS_STOP,
    BLOCKED_BY_EXISTING_RUNTIME_EXECUTION_INTERFACE_MISSING,
    BLOCKED_BY_KILL_SWITCH,
    BLOCKED_BY_OANDA_DEMO_MODE,
    BLOCKED_BY_ONE_ORDER_LIMIT,
    BLOCKED_BY_ORDER_CANDIDATE,
    BLOCKED_BY_OWNER_APPROVAL,
    BLOCKED_BY_POST_TRADE_REVIEW,
    BLOCKED_BY_RISK_GATES,
    BLOCKED_BY_RUNTIME_CREDENTIAL_SESSION_REQUIRED,
    BLOCKED_BY_SENSITIVE_DATA,
    DEMO_ONE_ORDER_EXECUTION_PREPARED_NOT_SENT,
    DEMO_ONE_ORDER_EXECUTION_READY_FOR_RUNTIME,
    HARD_FALSE_FIELDS,
    INCOMPLETE_INPUTS,
    NEXT_PACKET_CURRENT,
    NEXT_PACKET_RUNTIME_RECEIPT_AND_POST_TRADE_REVIEW,
    PACKET_ID,
    evaluate_forex_owner_approved_demo_one_order_profit_attempt_execution_v1,
    prepare_owner_approved_demo_one_order_execution_command_v1,
)


MODULE_PATH = (
    ROOT
    / "automation"
    / "forex_engine"
    / "forex_owner_approved_demo_one_order_profit_attempt_execution_v1.py"
)


def _payload() -> dict:
    return {
        "owner_approval": {
            "approval_text_present": True,
            "approval_packet_id": PACKET_ID,
            "owner_name": "Anthony",
            "approval_scope_demo_only": True,
            "approval_scope_one_order_only": True,
            "approval_scope_no_live_trade": True,
            "approval_scope_no_money_movement": True,
            "approval_scope_no_banking_transfer": True,
        },
        "protected_demo_attempt_result": {
            "protected_demo_attempt_status": "READY_FOR_OWNER_APPROVED_DEMO_ONE_ORDER_PACKET",
            "protected_demo_attempt_ready": True,
            "actual_demo_execution_authorized": False,
            "actual_live_execution_authorized": False,
            "broker_api_called": False,
            "credential_read": False,
            "money_moved": False,
        },
        "runtime_boundary": {
            "runtime_credential_session_available": True,
            "credential_values_in_payload": False,
            "account_id_in_payload": False,
            "credential_session_scope": "ONE_ORDER_DEMO_ONLY",
            "session_unexpired": True,
            "no_stored_api_key": True,
            "no_stored_account_id": True,
            "no_raw_secret_logging": True,
            "redaction_required": True,
        },
        "existing_runtime_interface": {
            "repo_runtime_interface_identified": True,
            "interface_name": "oanda_demo_owner_approved_one_order_protected_runtime_execution_v1",
            "interface_is_demo_only": True,
            "interface_supports_one_order": True,
            "interface_does_not_store_credentials": True,
            "interface_does_not_allow_live_trade": True,
        },
        "order_candidate": {
            "instrument": "EUR_USD",
            "side": "buy",
            "order_type": "market",
            "units": 1000,
            "stop_loss_present": True,
            "take_profit_present": True,
            "stop_loss_value_or_distance_present": True,
            "take_profit_value_or_distance_present": True,
            "setup_id": "setup-001",
            "evidence_id": "evidence-001",
            "duplicate_candidate": False,
        },
        "risk_plan": {
            "max_risk_per_trade_pct": "0.01",
            "max_daily_loss_pct": "0.03",
            "one_order_only": True,
            "max_order_count_this_packet": 1,
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "next_order_blocked_until_review": True,
        },
        "oanda_demo_boundary": {
            "broker_name": "OANDA",
            "mode": "OANDA_DEMO",
            "live_trading_allowed": False,
            "real_money_allowed": False,
            "money_movement_allowed": False,
            "account_id_in_payload": False,
        },
        "post_trade_review": {
            "post_trade_review_required": True,
            "daily_pnl_record_required": True,
            "sanitized_receipt_required": True,
            "owner_review_required": True,
            "no_second_trade_without_review": True,
        },
    }


def _run(payload: dict | None = None) -> dict:
    return evaluate_forex_owner_approved_demo_one_order_profit_attempt_execution_v1(
        payload
    )


def test_empty_payload_incomplete() -> None:
    assert _run({})["demo_one_order_execution_status"] == INCOMPLETE_INPUTS


def test_sensitive_data_blocked_and_value_not_echoed() -> None:
    payload = _payload()
    payload["nested"] = {"password": "DO-NOT-ECHO"}
    result = _run(payload)
    assert result["demo_one_order_execution_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "DO-NOT-ECHO" not in repr(result)


def test_banking_key_blocks() -> None:
    payload = _payload()
    payload["bank_plan"] = {"enabled": False}
    assert _run(payload)["demo_one_order_execution_status"] == BLOCKED_BY_BANKING_FOCUS


def test_approval_missing_blocks() -> None:
    payload = _payload()
    payload.pop("owner_approval")
    assert _run(payload)["demo_one_order_execution_status"] == BLOCKED_BY_OWNER_APPROVAL


def test_wrong_packet_id_blocks() -> None:
    payload = _payload()
    payload["owner_approval"]["approval_packet_id"] = "WRONG"
    assert _run(payload)["demo_one_order_execution_status"] == BLOCKED_BY_OWNER_APPROVAL


def test_protected_demo_attempt_missing_blocks() -> None:
    payload = _payload()
    payload.pop("protected_demo_attempt_result")
    assert _run(payload)["demo_one_order_execution_status"] == INCOMPLETE_INPUTS


def test_protected_demo_attempt_not_ready_blocks() -> None:
    payload = _payload()
    payload["protected_demo_attempt_result"]["protected_demo_attempt_ready"] = False
    assert _run(payload)["demo_one_order_execution_status"] == INCOMPLETE_INPUTS


def test_runtime_credential_session_missing_blocks() -> None:
    payload = _payload()
    payload["runtime_boundary"]["runtime_credential_session_available"] = False
    assert (
        _run(payload)["demo_one_order_execution_status"]
        == BLOCKED_BY_RUNTIME_CREDENTIAL_SESSION_REQUIRED
    )


def test_existing_runtime_interface_missing_blocks() -> None:
    payload = _payload()
    payload["existing_runtime_interface"]["repo_runtime_interface_identified"] = False
    assert (
        _run(payload)["demo_one_order_execution_status"]
        == BLOCKED_BY_EXISTING_RUNTIME_EXECUTION_INTERFACE_MISSING
    )


def test_oanda_demo_mode_missing_blocks() -> None:
    payload = _payload()
    payload["oanda_demo_boundary"]["mode"] = ""
    assert _run(payload)["demo_one_order_execution_status"] == BLOCKED_BY_OANDA_DEMO_MODE


def test_live_mode_blocks() -> None:
    payload = _payload()
    payload["oanda_demo_boundary"]["mode"] = "LIVE"
    assert _run(payload)["demo_one_order_execution_status"] == BLOCKED_BY_OANDA_DEMO_MODE


def test_account_id_in_payload_blocks() -> None:
    payload = _payload()
    payload["account_id"] = "DO-NOT-ECHO"
    result = _run(payload)
    assert result["demo_one_order_execution_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "DO-NOT-ECHO" not in repr(result)


def test_missing_instrument_blocks() -> None:
    payload = _payload()
    payload["order_candidate"].pop("instrument")
    assert _run(payload)["demo_one_order_execution_status"] == BLOCKED_BY_ORDER_CANDIDATE


def test_missing_stop_loss_blocks() -> None:
    payload = _payload()
    payload["order_candidate"]["stop_loss_present"] = False
    assert _run(payload)["demo_one_order_execution_status"] == BLOCKED_BY_RISK_GATES


def test_missing_take_profit_blocks() -> None:
    payload = _payload()
    payload["order_candidate"]["take_profit_present"] = False
    assert _run(payload)["demo_one_order_execution_status"] == BLOCKED_BY_RISK_GATES


def test_missing_stop_loss_value_or_distance_blocks() -> None:
    payload = _payload()
    payload["order_candidate"]["stop_loss_value_or_distance_present"] = False
    assert _run(payload)["demo_one_order_execution_status"] == BLOCKED_BY_RISK_GATES


def test_missing_take_profit_value_or_distance_blocks() -> None:
    payload = _payload()
    payload["order_candidate"]["take_profit_value_or_distance_present"] = False
    assert _run(payload)["demo_one_order_execution_status"] == BLOCKED_BY_RISK_GATES


def test_risk_over_one_percent_blocks() -> None:
    payload = _payload()
    payload["risk_plan"]["max_risk_per_trade_pct"] = "0.011"
    assert _run(payload)["demo_one_order_execution_status"] == BLOCKED_BY_RISK_GATES


def test_daily_loss_over_three_percent_blocks() -> None:
    payload = _payload()
    payload["risk_plan"]["max_daily_loss_pct"] = "0.031"
    assert _run(payload)["demo_one_order_execution_status"] == BLOCKED_BY_RISK_GATES


def test_kill_switch_active_blocks() -> None:
    payload = _payload()
    payload["risk_plan"]["kill_switch_active"] = True
    assert _run(payload)["demo_one_order_execution_status"] == BLOCKED_BY_KILL_SWITCH


def test_daily_loss_stop_active_blocks() -> None:
    payload = _payload()
    payload["risk_plan"]["daily_loss_stop_active"] = True
    assert _run(payload)["demo_one_order_execution_status"] == BLOCKED_BY_DAILY_LOSS_STOP


def test_max_order_count_over_one_blocks() -> None:
    payload = _payload()
    payload["risk_plan"]["max_order_count_this_packet"] = 2
    assert _run(payload)["demo_one_order_execution_status"] == BLOCKED_BY_ONE_ORDER_LIMIT


def test_post_trade_review_missing_blocks() -> None:
    payload = _payload()
    payload["post_trade_review"]["post_trade_review_required"] = False
    assert _run(payload)["demo_one_order_execution_status"] == BLOCKED_BY_POST_TRADE_REVIEW


def test_strong_payload_reaches_ready_for_runtime() -> None:
    result = _run(_payload())
    assert (
        result["demo_one_order_execution_status"]
        == DEMO_ONE_ORDER_EXECUTION_READY_FOR_RUNTIME
    )
    assert result["demo_one_order_execution_ready"] is True
    assert result["next_best_packet"] == NEXT_PACKET_RUNTIME_RECEIPT_AND_POST_TRADE_REVIEW


def test_sanitized_execution_intent_has_no_credentials_account_or_api_keys() -> None:
    intent = _run(_payload())["sanitized_execution_intent"]
    joined_keys = " ".join(intent).lower()
    forbidden = ["credential", "account", "api_key", "token", "password"]
    assert [marker for marker in forbidden if marker in joined_keys] == []


def test_all_hard_false_fields_remain_false() -> None:
    result = _run(_payload())
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False


def test_next_best_packet_routes_correctly() -> None:
    ready = _run(_payload())
    assert ready["next_best_packet"] == NEXT_PACKET_RUNTIME_RECEIPT_AND_POST_TRADE_REVIEW
    blocked = _payload()
    blocked["risk_plan"]["daily_loss_stop_active"] = True
    assert _run(blocked)["next_best_packet"] == NEXT_PACKET_CURRENT
    prepared = prepare_owner_approved_demo_one_order_execution_command_v1(_payload())
    assert prepared["demo_one_order_execution_status"] == DEMO_ONE_ORDER_EXECUTION_PREPARED_NOT_SENT
    assert prepared["next_best_packet"] == NEXT_PACKET_RUNTIME_RECEIPT_AND_POST_TRADE_REVIEW


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
