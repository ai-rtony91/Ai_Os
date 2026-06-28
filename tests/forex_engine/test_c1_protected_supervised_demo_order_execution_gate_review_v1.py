from __future__ import annotations

from pathlib import Path

from automation.forex_engine.c1_protected_supervised_demo_order_execution_gate_review_v1 import (
    evaluate_c1_protected_supervised_demo_order_execution_gate_review,
)
from scripts.forex_delivery.run_c1_protected_supervised_demo_order_execution_gate_review_v1 import (
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
        "AIOS_FOREX_C1_PROTECTED_SUPERVISED_DEMO_ORDER_EXECUTION_GATE_REVIEW_V1.json"
    ),
    Path(
        "Reports/forex_delivery/"
        "AIOS_FOREX_C1_PROTECTED_SUPERVISED_DEMO_ORDER_EXECUTION_GATE_REVIEW_V1_REPORT.md"
    ),
    Path(
        "Reports/forex_delivery/"
        "AIOS_FOREX_C1_PROTECTED_SUPERVISED_DEMO_ORDER_EXECUTION_GATE_REVIEW_NEXT_ACTION_QUEUE_V1.md"
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
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
    }


def test_default_owner_input_none_blocks_on_owner_input_required() -> None:
    result = (
        evaluate_c1_protected_supervised_demo_order_execution_gate_review()
    )

    assert (
        result["p9_execution_gate_status"]
        == "P9_EXECUTION_GATE_BLOCKED_OWNER_INPUT_REQUIRED"
    )
    assert result["protected_demo_order_gate_status"] == "NOT_READY"
    assert result["post_p9_score"] == 100
    assert (
        result["next_required_lane"]
        == "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"
    )
    assert result["protected_execution_gate_review_created"] is False
    assert result["demo_order_placement_authorized"] is False


def test_default_next_required_lane_is_p6b() -> None:
    result = (
        evaluate_c1_protected_supervised_demo_order_execution_gate_review()
    )
    assert (
        result["next_required_lane"]
        == "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"
    )


def test_valid_sanitized_owner_input_routes_to_p10_owner_handoff() -> None:
    result = evaluate_c1_protected_supervised_demo_order_execution_gate_review(
        _valid_owner_input()
    )

    assert (
        result["p9_execution_gate_status"]
        == "P9_PROTECTED_SUPERVISED_DEMO_ORDER_EXECUTION_GATE_PASSED_FOR_P10_OWNER_RUN_HANDOFF"
    )
    assert result["protected_demo_order_gate_status"] == "P10_READY"
    assert (
        result["next_required_lane"]
        == "P10_OWNER_CONTROLLED_PROTECTED_DEMO_ORDER_RUN_HANDOFF_PREPARATION"
    )
    assert result["protected_execution_gate_review_created"] is True


def test_protected_execution_gate_review_created_only_for_valid_validated_path() -> None:
    base_input = _valid_owner_input()
    bad_input = _valid_owner_input()
    bad_input["owner_decision"] = "REQUEST_CHANGES"

    default_result = (
        evaluate_c1_protected_supervised_demo_order_execution_gate_review()
    )
    invalid_result = (
        evaluate_c1_protected_supervised_demo_order_execution_gate_review(bad_input)
    )
    passed_result = (
        evaluate_c1_protected_supervised_demo_order_execution_gate_review(base_input)
    )

    assert default_result["protected_execution_gate_review_created"] is False
    assert invalid_result["protected_execution_gate_review_created"] is False
    assert passed_result["protected_execution_gate_review_created"] is True


def test_blocked_authorization_flags_stay_active() -> None:
    default_result = (
        evaluate_c1_protected_supervised_demo_order_execution_gate_review()
    )
    valid_result = (
        evaluate_c1_protected_supervised_demo_order_execution_gate_review(
            _valid_owner_input()
        )
    )

    for result in (default_result, valid_result):
        assert result["demo_order_placement_authorized"] is False
        assert result["broker_api_access_authorized"] is False
        assert result["credential_access_authorized"] is False
        assert result["live_trading_blocked"] is True
        assert result["money_movement_blocked"] is True
        assert result["no_autonomy_approval"] is True


def test_rejected_or_request_changes_or_invalid_input_does_not_route_to_p10() -> None:
    rejected_input = _valid_owner_input()
    rejected_input["owner_decision"] = "REJECT_DEMO_INTENT"

    request_changes_input = _valid_owner_input()
    request_changes_input["owner_decision"] = "REQUEST_CHANGES"

    invalid_input = _valid_owner_input()
    invalid_input["daily_realized_loss_percent"] = 1.5

    for owner_input in (rejected_input, request_changes_input, invalid_input):
        result = (
            evaluate_c1_protected_supervised_demo_order_execution_gate_review(
                owner_input
            )
        )
        assert (
            result["next_required_lane"]
            != "P10_OWNER_CONTROLLED_PROTECTED_DEMO_ORDER_RUN_HANDOFF_PREPARATION"
        )
        assert result["protected_demo_order_gate_status"] == "NOT_READY"


def test_forbidden_credential_account_or_api_fields_fail_or_stay_blocked() -> None:
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
        "broker_api_access_authorized",
        "credential_access_authorized",
        "demo_order_placement_authorized",
        "live_trading_authorized",
        "money_movement_authorized",
        "autonomy_approval",
    ]

    for field_name in forbidden_fields:
        owner_input = _valid_owner_input()
        owner_input[field_name] = "SANITIZED_FORBIDDEN_VALUE"
        result = (
            evaluate_c1_protected_supervised_demo_order_execution_gate_review(
                owner_input
            )
        )
        assert result["protected_demo_order_gate_status"] == "NOT_READY"
        assert (
            result["next_required_lane"]
            != "P10_OWNER_CONTROLLED_PROTECTED_DEMO_ORDER_RUN_HANDOFF_PREPARATION"
        )


def test_missing_final_execution_gate_review_marker_fails_p9() -> None:
    owner_input = _valid_owner_input()
    owner_input["final_owner_execution_gate_review"] = False

    result = (
        evaluate_c1_protected_supervised_demo_order_execution_gate_review(
            owner_input
        )
    )

    assert (
        result["p9_execution_gate_status"]
        == "P9_EXECUTION_GATE_FAILED_REPAIR_REQUIRED"
    )


def test_generate_artifacts_default_outputs_exist() -> None:
    result = generate_artifacts()

    assert result["p9_execution_gate_status"] == "P9_EXECUTION_GATE_BLOCKED_OWNER_INPUT_REQUIRED"
    assert result["protected_demo_order_gate_status"] == "NOT_READY"
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
