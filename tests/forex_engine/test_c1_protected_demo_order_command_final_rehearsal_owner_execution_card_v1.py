"""Tests for P14 protected demo-order command final rehearsal owner execution card."""

from automation.forex_engine.c1_protected_demo_order_command_final_rehearsal_owner_execution_card_v1 import (
    evaluate_c1_protected_demo_order_command_final_rehearsal_owner_execution_card,
)
from scripts.forex_delivery.run_c1_protected_demo_order_command_final_rehearsal_owner_execution_card_v1 import (
    JSON_REPORT_PATH,
    QUEUE_PATH,
    REPORT_PATH,
    generate_artifacts,
)


BANNED_TOKENS = [
    "TODO",
    "TBD",
    "@filename",
    "probably",
    "roughly",
    "approximately",
    "I estimate",
    "live ready",
    "profitable trading readiness: true",
    "autonomous trading readiness: true",
    "100-120 percent verified",
    "demo order approved",
    "live order approved",
    "order placed",
    "trade executed",
    "broker connected",
    "credentials loaded",
    "approval granted",
    "snapshot collected",
    "demo trade executed",
    "live trade executed",
    "real order",
    "real trade",
    "API key accepted",
    "credentials accepted",
    "account id accepted",
    "broker connected successfully",
]


def _valid_owner_input() -> dict:
    return {
        "owner_decision": "APPROVE_DEMO_INTENT",
        "demo_account_marker": "DEMO_ONLY",
        "broker_environment": "DEMO_OR_PRACTICE_ONLY",
        "broker_name_sanitized": True,
        "sanitized_equity_value_or_bracket": "DEMO_EQUITY_BRACKET_A",
        "current_open_position_count": 0,
        "current_same_signal_order_count": 0,
        "pending_order_count": 0,
        "max_open_positions": 1,
        "daily_realized_loss_percent": 0.0,
        "weekly_realized_loss_percent": 0.0,
        "max_risk_per_trade_percent": 0.25,
        "kill_switch_state": "ARMED_UNTRIGGERED",
        "timestamp_utc": "2026-06-28T00:00:00Z",
        "owner_attestation": True,
        "intended_instrument_confirmation": "EUR_USD",
        "intended_side_confirmation": "BUY",
        "order_type_selection": "MARKET",
        "units_formula_review": True,
        "position_size_formula_sanitized": True,
        "stop_loss_review": True,
        "take_profit_review": True,
        "reward_to_risk_review": True,
        "minimum_reward_to_risk": 1.20,
        "spread_guard_review": True,
        "slippage_guard_review": True,
        "market_open_review": True,
        "one_order_rule_verification": True,
        "daily_stop_verification": True,
        "weekly_stop_verification": True,
        "kill_switch_verification": True,
        "audit_record_ready": True,
        "final_owner_execution_gate_review": True,
        "idempotency_key_required": True,
        "stale_price_block_required": True,
        "duplicate_order_block_required": True,
        "owner_run_handoff_review": True,
        "credential_handling_review": True,
        "broker_connection_review": True,
        "explicit_owner_run_packet_required": True,
        "explicit_owner_run_packet_review": True,
        "protected_run_packet_review": True,
        "final_protected_owner_run_packet_review": True,
        "protected_owner_command_release_review": True,
        "explicit_owner_command_packet_required": True,
        "protected_command_dry_run_required": True,
        "final_protected_execution_command_packet_review": True,
        "protected_command_release_review": True,
        "protected_final_rehearsal_required": True,
        "owner_execution_card_required": True,
        "final_protected_command_release_review": True,
        "final_rehearsal_reviewed": True,
        "owner_execution_card_prepared": True,
        "explicit_owner_execution_packet_review_required": True,
        "final_owner_execution_card_review": True,
        "broker_api_connection_authorized_now": False,
        "credential_access_authorized_now": False,
        "order_submission_authorized_now": False,
        "execution_command_authorized_now": False,
        "execution_command_authorized": False,
        "candidate_id": "c1-eur-buy",
        "candidate_name": "paper_long_run_supervisor_v2 LONG EURUSD",
        "owner_control_required": True,
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
    }


def test_default_owner_input_none() -> None:
    result = evaluate_c1_protected_demo_order_command_final_rehearsal_owner_execution_card()

    assert (
        result["p14_final_rehearsal_status"]
        == "P14_FINAL_REHEARSAL_BLOCKED_OWNER_INPUT_REQUIRED"
    )
    assert result["owner_execution_card_status"] == "NOT_READY"
    assert result["next_required_lane"] == "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"
    assert result["post_p14_score"] == 100
    assert result["demo_order_placement_authorized"] is False
    assert result["broker_api_access_authorized"] is False
    assert result["credential_access_authorized"] is False
    assert result["execution_command_authorized"] is False
    assert result["live_trading_blocked"] is True
    assert result["money_movement_blocked"] is True
    assert result["no_autonomy_approval"] is True


def test_default_next_lane_is_p6b() -> None:
    result = evaluate_c1_protected_demo_order_command_final_rehearsal_owner_execution_card()
    assert (
        result["next_required_lane"]
        == "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"
    )


def test_valid_sanitized_owner_input_passes_for_p15() -> None:
    result = evaluate_c1_protected_demo_order_command_final_rehearsal_owner_execution_card(_valid_owner_input())

    assert (
        result["p14_final_rehearsal_status"]
        == "P14_PROTECTED_DEMO_ORDER_COMMAND_FINAL_REHEARSAL_OWNER_EXECUTION_CARD_PREPARED_FOR_P15_EXECUTION_PACKET_REVIEW"
    )
    assert (
        result["owner_execution_card_status"]
        == "P15_READY"
    )
    assert (
        result["next_required_lane"]
        == "P15_EXPLICIT_OWNER_APPROVED_PROTECTED_DEMO_ORDER_EXECUTION_PACKET_REVIEW"
    )
    assert result["final_rehearsal_owner_execution_card_created"] is True
    assert result["final_rehearsal_owner_execution_card"]["final_rehearsal_card_type"] == (
        "INERT_PROTECTED_DEMO_ORDER_FINAL_REHEARSAL_OWNER_EXECUTION_CARD_ONLY"
    )
    assert result["demo_order_placement_authorized"] is False
    assert result["broker_api_access_authorized"] is False
    assert result["credential_access_authorized"] is False
    assert result["execution_command_authorized"] is False
    assert result["live_trading_blocked"] is True
    assert result["money_movement_blocked"] is True
    assert result["no_autonomy_approval"] is True


def test_rejected_or_request_changes_do_not_route_to_p15() -> None:
    rejected = _valid_owner_input()
    rejected["owner_decision"] = "REJECT_DEMO_INTENT"
    request_changes = _valid_owner_input()
    request_changes["owner_decision"] = "REQUEST_CHANGES"
    invalid_losses = _valid_owner_input()
    invalid_losses["daily_realized_loss_percent"] = 2.0

    for owner_input in (rejected, request_changes, invalid_losses):
        result = evaluate_c1_protected_demo_order_command_final_rehearsal_owner_execution_card(owner_input)
        assert (
            result["next_required_lane"]
            != "P15_EXPLICIT_OWNER_APPROVED_PROTECTED_DEMO_ORDER_EXECUTION_PACKET_REVIEW"
        )
        assert result["owner_execution_card_status"] == "NOT_READY"
        assert result["p14_final_rehearsal_status"] != "P14_PROTECTED_DEMO_ORDER_COMMAND_FINAL_REHEARSAL_OWNER_EXECUTION_CARD_PREPARED_FOR_P15_EXECUTION_PACKET_REVIEW"


def test_forbidden_credential_account_api_fields_fail_or_stay_blocked() -> None:
    forbidden_fields = [
        "account_identifier",
        "account_id",
        "broker_account_id",
        "account_number",
        "credentials",
        "credential",
        "password",
        "token",
        "secret",
        "api_key",
        "api_keys",
        "api_token",
        "broker_api_key",
        "raw_live_account_data",
        "live_account_data",
        "live_balance",
        "live_position_data",
    ]

    for field_name in forbidden_fields:
        owner_input = _valid_owner_input()
        owner_input[field_name] = "SANITIZED_BLOCKED_VALUE"
        result = evaluate_c1_protected_demo_order_command_final_rehearsal_owner_execution_card(owner_input)
        assert result["owner_execution_card_status"] == "NOT_READY"
        assert result["next_required_lane"] != "P15_EXPLICIT_OWNER_APPROVED_PROTECTED_DEMO_ORDER_EXECUTION_PACKET_REVIEW"


def test_safe_false_authorization_fields_do_not_fail_p14() -> None:
    safe_false_fields = [
        "broker_api_access_authorized",
        "credential_access_authorized",
        "broker_api_connection_authorized_now",
        "credential_access_authorized_now",
        "order_submission_authorized_now",
        "execution_command_authorized_now",
        "execution_command_authorized",
        "demo_order_placement_authorized",
    ]

    for field_name in safe_false_fields:
        owner_input = _valid_owner_input()
        owner_input[field_name] = False
        result = evaluate_c1_protected_demo_order_command_final_rehearsal_owner_execution_card(owner_input)
        assert (
            result["p14_final_rehearsal_status"]
            == "P14_PROTECTED_DEMO_ORDER_COMMAND_FINAL_REHEARSAL_OWNER_EXECUTION_CARD_PREPARED_FOR_P15_EXECUTION_PACKET_REVIEW"
        )
        assert (
            result["owner_execution_card_status"]
            == "P15_READY"
        )


def test_authorization_fields_true_fails_p14() -> None:
    true_fail_fields = [
        "broker_api_access_authorized",
        "credential_access_authorized",
        "broker_api_connection_authorized_now",
        "credential_access_authorized_now",
        "order_submission_authorized_now",
        "execution_command_authorized_now",
        "execution_command_authorized",
        "demo_order_placement_authorized",
        "live_trading_authorized",
        "money_movement_authorized",
        "autonomy_approval",
    ]

    for field_name in true_fail_fields:
        owner_input = _valid_owner_input()
        owner_input[field_name] = True
        result = evaluate_c1_protected_demo_order_command_final_rehearsal_owner_execution_card(owner_input)
        assert result["owner_execution_card_status"] == "NOT_READY"
        assert (
            result["next_required_lane"]
            != "P15_EXPLICIT_OWNER_APPROVED_PROTECTED_DEMO_ORDER_EXECUTION_PACKET_REVIEW"
        )


def test_missing_final_rehearsal_marker_fails_p14() -> None:
    owner_input = _valid_owner_input()
    owner_input["final_rehearsal_reviewed"] = False
    result = evaluate_c1_protected_demo_order_command_final_rehearsal_owner_execution_card(owner_input)
    assert result["p14_final_rehearsal_status"] != (
        "P14_PROTECTED_DEMO_ORDER_COMMAND_FINAL_REHEARSAL_OWNER_EXECUTION_CARD_PREPARED_FOR_P15_EXECUTION_PACKET_REVIEW"
    )
    assert result["owner_execution_card_status"] == "NOT_READY"


def test_missing_owner_execution_card_marker_fails_p14() -> None:
    owner_input = _valid_owner_input()
    owner_input["owner_execution_card_required"] = False
    result = evaluate_c1_protected_demo_order_command_final_rehearsal_owner_execution_card(owner_input)
    assert result["p14_final_rehearsal_status"] != (
        "P14_PROTECTED_DEMO_ORDER_COMMAND_FINAL_REHEARSAL_OWNER_EXECUTION_CARD_PREPARED_FOR_P15_EXECUTION_PACKET_REVIEW"
    )
    assert result["owner_execution_card_status"] == "NOT_READY"


def test_missing_explicit_owner_execution_packet_review_marker_fails_p14() -> None:
    owner_input = _valid_owner_input()
    owner_input["explicit_owner_execution_packet_review_required"] = False
    result = evaluate_c1_protected_demo_order_command_final_rehearsal_owner_execution_card(owner_input)
    assert result["p14_final_rehearsal_status"] != (
        "P14_PROTECTED_DEMO_ORDER_COMMAND_FINAL_REHEARSAL_OWNER_EXECUTION_CARD_PREPARED_FOR_P15_EXECUTION_PACKET_REVIEW"
    )
    assert result["owner_execution_card_status"] == "NOT_READY"


def test_missing_credential_handling_review_marker_fails_p14() -> None:
    owner_input = _valid_owner_input()
    owner_input["credential_handling_review"] = False
    result = evaluate_c1_protected_demo_order_command_final_rehearsal_owner_execution_card(owner_input)
    assert result["p14_final_rehearsal_status"] != (
        "P14_PROTECTED_DEMO_ORDER_COMMAND_FINAL_REHEARSAL_OWNER_EXECUTION_CARD_PREPARED_FOR_P15_EXECUTION_PACKET_REVIEW"
    )
    assert result["owner_execution_card_status"] == "NOT_READY"


def test_missing_broker_connection_review_marker_fails_p14() -> None:
    owner_input = _valid_owner_input()
    owner_input["broker_connection_review"] = False
    result = evaluate_c1_protected_demo_order_command_final_rehearsal_owner_execution_card(owner_input)
    assert result["p14_final_rehearsal_status"] != (
        "P14_PROTECTED_DEMO_ORDER_COMMAND_FINAL_REHEARSAL_OWNER_EXECUTION_CARD_PREPARED_FOR_P15_EXECUTION_PACKET_REVIEW"
    )
    assert result["owner_execution_card_status"] == "NOT_READY"


def test_missing_final_owner_execution_card_review_marker_fails_p14() -> None:
    owner_input = _valid_owner_input()
    owner_input["final_owner_execution_card_review"] = False
    result = evaluate_c1_protected_demo_order_command_final_rehearsal_owner_execution_card(owner_input)
    assert result["p14_final_rehearsal_status"] != (
        "P14_PROTECTED_DEMO_ORDER_COMMAND_FINAL_REHEARSAL_OWNER_EXECUTION_CARD_PREPARED_FOR_P15_EXECUTION_PACKET_REVIEW"
    )
    assert result["owner_execution_card_status"] == "NOT_READY"


def test_generate_artifacts_default_outputs_exist_and_clean() -> None:
    generate_artifacts()
    for path in (JSON_REPORT_PATH, REPORT_PATH, QUEUE_PATH):
        assert path.exists(), f"Missing artifact {path}"


def test_generated_outputs_contain_no_banned_tokens() -> None:
    generate_artifacts()
    for path in (JSON_REPORT_PATH, REPORT_PATH, QUEUE_PATH):
        text = path.read_text(encoding="utf-8")
        for token in BANNED_TOKENS:
            assert token not in text
