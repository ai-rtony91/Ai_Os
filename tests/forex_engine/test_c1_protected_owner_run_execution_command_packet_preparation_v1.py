from __future__ import annotations

from pathlib import Path

from automation.forex_engine.c1_protected_owner_run_execution_command_packet_preparation_v1 import (
    evaluate_c1_protected_owner_run_execution_command_packet_preparation,
)
from scripts.forex_delivery.run_c1_protected_owner_run_execution_command_packet_preparation_v1 import (
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
    "guaranteed profit",
    "guaranteed returns",
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

GENERATED_PATHS = [
    Path(
        "Reports/forex_delivery/"
        "AIOS_FOREX_C1_PROTECTED_OWNER_RUN_EXECUTION_COMMAND_PACKET_PREPARATION_V1.json"
    ),
    Path(
        "Reports/forex_delivery/"
        "AIOS_FOREX_C1_PROTECTED_OWNER_RUN_EXECUTION_COMMAND_PACKET_PREPARATION_V1_REPORT.md"
    ),
    Path(
        "Reports/forex_delivery/"
        "AIOS_FOREX_C1_PROTECTED_OWNER_RUN_EXECUTION_COMMAND_PACKET_PREPARATION_NEXT_ACTION_QUEUE_V1.md"
    ),
]


def _valid_owner_input() -> dict[str, object]:
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
        "broker_api_connection_authorized_now": False,
        "credential_access_authorized_now": False,
        "order_submission_authorized_now": False,
        "execution_command_authorized_now": False,
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


def test_default_owner_input_none_blocks_owner_input_required() -> None:
    result = (
        evaluate_c1_protected_owner_run_execution_command_packet_preparation()
    )

    assert (
        result["p12_command_packet_status"]
        == "P12_COMMAND_PACKET_BLOCKED_OWNER_INPUT_REQUIRED"
    )
    assert result["protected_owner_command_status"] == "NOT_READY"
    assert result["post_p12_score"] == 100
    assert (
        result["next_required_lane"]
        == "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"
    )
    assert result["protected_execution_command_packet_created"] is False
    assert result["demo_order_placement_authorized"] is False
    assert result["broker_api_access_authorized"] is False
    assert result["credential_access_authorized"] is False
    assert result["live_trading_blocked"] is True
    assert result["money_movement_blocked"] is True
    assert result["no_autonomy_approval"] is True
    assert (
        result["final_owner_sentence"]
        == "P12 is waiting for validated owner input and no broker/API, credential, or demo-order authority is authorized."
    )


def test_default_next_lane_is_p6b() -> None:
    result = (
        evaluate_c1_protected_owner_run_execution_command_packet_preparation()
    )
    assert (
        result["next_required_lane"]
        == "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"
    )


def test_valid_sanitized_owner_input_prepares_for_p13() -> None:
    result = evaluate_c1_protected_owner_run_execution_command_packet_preparation(
        _valid_owner_input()
    )

    assert (
        result["p12_command_packet_status"]
        == "P12_PROTECTED_OWNER_RUN_EXECUTION_COMMAND_PACKET_PREPARED_FOR_P13_RELEASE_REVIEW"
    )
    assert result["protected_owner_command_status"] == "P13_READY"
    assert (
        result["next_required_lane"]
        == "P13_OWNER_RUN_PROTECTED_DEMO_ORDER_COMMAND_RELEASE_REVIEW"
    )
    assert result["protected_execution_command_packet_created"] is True
    assert (
        result["protected_execution_command_packet"][
            "protected_execution_command_packet_type"
        ]
        == "INERT_PROTECTED_OWNER_RUN_EXECUTION_COMMAND_PACKET_PREPARATION_ONLY"
    )
    assert result["protected_execution_command_packet"]["candidate_id"] == "c1-eur-buy"


def test_ready_only_valid_path_creates_execution_packet() -> None:
    valid_result = evaluate_c1_protected_owner_run_execution_command_packet_preparation(
        _valid_owner_input()
    )
    bad_input = _valid_owner_input()
    bad_input["owner_decision"] = "REQUEST_CHANGES"

    invalid_result = (
        evaluate_c1_protected_owner_run_execution_command_packet_preparation(
            bad_input
        )
    )

    assert valid_result["protected_execution_command_packet_created"] is True
    assert invalid_result["protected_execution_command_packet_created"] is False


def test_authorization_flags_are_blocked_by_default() -> None:
    default_result = (
        evaluate_c1_protected_owner_run_execution_command_packet_preparation()
    )
    valid_result = evaluate_c1_protected_owner_run_execution_command_packet_preparation(
        _valid_owner_input()
    )

    for result in (default_result, valid_result):
        assert result["demo_order_placement_authorized"] is False
        assert result["broker_api_access_authorized"] is False
        assert result["credential_access_authorized"] is False
        assert result["live_trading_blocked"] is True
        assert result["money_movement_blocked"] is True
        assert result["no_autonomy_approval"] is True


def test_rejected_request_changes_invalid_owner_input_does_not_route_to_p13() -> None:
    rejected_input = _valid_owner_input()
    rejected_input["owner_decision"] = "REJECT_DEMO_INTENT"
    request_changes_input = _valid_owner_input()
    request_changes_input["owner_decision"] = "REQUEST_CHANGES"
    invalid_input = _valid_owner_input()
    invalid_input["daily_realized_loss_percent"] = 2.0

    for owner_input in (rejected_input, request_changes_input, invalid_input):
        result = evaluate_c1_protected_owner_run_execution_command_packet_preparation(
            owner_input
        )
        assert (
            result["next_required_lane"]
            != "P13_OWNER_RUN_PROTECTED_DEMO_ORDER_COMMAND_RELEASE_REVIEW"
        )
        assert result["protected_owner_command_status"] == "NOT_READY"


def test_missing_protected_owner_command_release_review_marker_fails_p12() -> None:
    owner_input = _valid_owner_input()
    owner_input["protected_owner_command_release_review"] = False

    result = evaluate_c1_protected_owner_run_execution_command_packet_preparation(
        owner_input
    )

    assert (
        result["p12_command_packet_status"]
        == "P12_COMMAND_PACKET_FAILED_REPAIR_REQUIRED"
    )


def test_missing_explicit_owner_command_packet_marker_fails_p12() -> None:
    owner_input = _valid_owner_input()
    owner_input["explicit_owner_command_packet_required"] = False

    result = evaluate_c1_protected_owner_run_execution_command_packet_preparation(
        owner_input
    )

    assert (
        result["p12_command_packet_status"]
        == "P12_COMMAND_PACKET_FAILED_REPAIR_REQUIRED"
    )


def test_missing_protected_command_dry_run_marker_fails_p12() -> None:
    owner_input = _valid_owner_input()
    owner_input["protected_command_dry_run_required"] = False

    result = evaluate_c1_protected_owner_run_execution_command_packet_preparation(
        owner_input
    )

    assert (
        result["p12_command_packet_status"]
        == "P12_COMMAND_PACKET_FAILED_REPAIR_REQUIRED"
    )


def test_missing_credential_handling_review_marker_fails_p12() -> None:
    owner_input = _valid_owner_input()
    owner_input["credential_handling_review"] = False

    result = evaluate_c1_protected_owner_run_execution_command_packet_preparation(
        owner_input
    )

    assert (
        result["p12_command_packet_status"]
        == "P12_COMMAND_PACKET_FAILED_REPAIR_REQUIRED"
    )


def test_missing_broker_connection_review_marker_fails_p12() -> None:
    owner_input = _valid_owner_input()
    owner_input["broker_connection_review"] = False

    result = evaluate_c1_protected_owner_run_execution_command_packet_preparation(
        owner_input
    )

    assert (
        result["p12_command_packet_status"]
        == "P12_COMMAND_PACKET_FAILED_REPAIR_REQUIRED"
    )


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
        owner_input[field_name] = "SANITIZED_FORBIDDEN_VALUE"
        result = evaluate_c1_protected_owner_run_execution_command_packet_preparation(
            owner_input
        )
        assert result["protected_owner_command_status"] == "NOT_READY"
        assert result["next_required_lane"] != (
            "P13_OWNER_RUN_PROTECTED_DEMO_ORDER_COMMAND_RELEASE_REVIEW"
        )


def test_safe_false_authorization_fields_do_not_fail_p12() -> None:
    safe_false_fields = [
        "broker_api_access_authorized",
        "credential_access_authorized",
        "broker_api_connection_authorized_now",
        "credential_access_authorized_now",
        "order_submission_authorized_now",
        "execution_command_authorized_now",
        "demo_order_placement_authorized",
    ]

    for field_name in safe_false_fields:
        owner_input = _valid_owner_input()
        owner_input[field_name] = False
        result = evaluate_c1_protected_owner_run_execution_command_packet_preparation(
            owner_input
        )
        assert result["p12_command_packet_status"] == (
            "P12_PROTECTED_OWNER_RUN_EXECUTION_COMMAND_PACKET_PREPARED_FOR_P13_RELEASE_REVIEW"
        )


def test_authorization_fields_true_fails_p12() -> None:
    true_fail_fields = [
        "broker_api_access_authorized",
        "credential_access_authorized",
        "broker_api_connection_authorized_now",
        "credential_access_authorized_now",
        "order_submission_authorized_now",
        "execution_command_authorized_now",
        "demo_order_placement_authorized",
    ]

    for field_name in true_fail_fields:
        owner_input = _valid_owner_input()
        owner_input[field_name] = True
        result = evaluate_c1_protected_owner_run_execution_command_packet_preparation(
            owner_input
        )
        assert result["p12_command_packet_status"] == (
            "P12_COMMAND_PACKET_FAILED_REPAIR_REQUIRED"
        )

    for field_name in ("live_trading_authorized", "money_movement_authorized", "autonomy_approval"):
        owner_input = _valid_owner_input()
        owner_input[field_name] = True
        result = evaluate_c1_protected_owner_run_execution_command_packet_preparation(
            owner_input
        )
        assert result["p12_command_packet_status"] in {
            "P12_COMMAND_PACKET_FAILED_REPAIR_REQUIRED",
            "P12_COMMAND_PACKET_BLOCKED_P11_REPAIR_REQUIRED",
        }


def test_generate_artifacts_default_outputs_exist() -> None:
    result = generate_artifacts()

    assert result["p12_command_packet_status"] == (
        "P12_COMMAND_PACKET_BLOCKED_OWNER_INPUT_REQUIRED"
    )
    assert result["protected_owner_command_status"] == "NOT_READY"
    assert (
        result["next_required_lane"]
        == "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"
    )
    for path in GENERATED_PATHS:
        assert path.exists(), f"Missing generated artifact: {path}"


def test_generated_outputs_contain_no_banned_tokens() -> None:
    generate_artifacts()

    for path in GENERATED_PATHS:
        text = path.read_text(encoding="utf-8")
        for token in BANNED_TOKENS:
            assert token not in text
