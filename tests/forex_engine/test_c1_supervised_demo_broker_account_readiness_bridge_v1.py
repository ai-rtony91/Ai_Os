from __future__ import annotations

from pathlib import Path

from automation.forex_engine.c1_supervised_demo_broker_account_readiness_bridge_v1 import (
    evaluate_c1_supervised_demo_broker_account_readiness_bridge,
)
from scripts.forex_delivery.run_c1_supervised_demo_broker_account_readiness_bridge_v1 import (
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
        "AIOS_FOREX_C1_SUPERVISED_DEMO_BROKER_ACCOUNT_READINESS_BRIDGE_V1.json"
    ),
    Path(
        "Reports/forex_delivery/"
        "AIOS_FOREX_C1_SUPERVISED_DEMO_BROKER_ACCOUNT_READINESS_BRIDGE_V1_REPORT.md"
    ),
    Path(
        "Reports/forex_delivery/"
        "AIOS_FOREX_C1_SUPERVISED_DEMO_BROKER_ACCOUNT_READINESS_BRIDGE_NEXT_ACTION_QUEUE_V1.md"
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
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
    }


def test_default_owner_input_none_blocks_on_owner_input_required() -> None:
    result = evaluate_c1_supervised_demo_broker_account_readiness_bridge()

    assert result["p8_bridge_status"] == "P8_BRIDGE_BLOCKED_OWNER_INPUT_REQUIRED"
    assert result["broker_account_readiness_status"] == "NOT_READY"
    assert result["post_p8_score"] == 100
    assert (
        result["next_required_lane"]
        == "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"
    )
    assert result["supervised_demo_broker_account_bridge_created"] is False
    assert result["demo_order_placement_authorized"] is False


def test_valid_sanitized_approved_owner_input_routes_to_p9_review() -> None:
    result = evaluate_c1_supervised_demo_broker_account_readiness_bridge(
        _valid_owner_input()
    )

    assert (
        result["p8_bridge_status"]
        == "P8_SUPERVISED_DEMO_BROKER_ACCOUNT_BRIDGE_PASSED_FOR_P9_REVIEW"
    )
    assert result["broker_account_readiness_status"] == "P9_READY"
    assert (
        result["next_required_lane"]
        == "P9_PROTECTED_SUPERVISED_DEMO_ORDER_EXECUTION_GATE_REVIEW"
    )
    assert result["supervised_demo_broker_account_bridge_created"] is True
    assert result["broker_account_readiness_contract"]["candidate_id"] == "c1-eur-buy"
    assert result["broker_account_readiness_contract"]["candidate_name"] == (
        "paper_long_run_supervisor_v2 LONG EURUSD"
    )
    assert result["broker_account_readiness_contract"]["instrument"] == "EUR_USD"
    assert result["broker_account_readiness_contract"]["side"] == "BUY"
    assert result["failed_requirements"] == []
    assert all(result["bridge_checks"].values())


def test_demo_broker_credential_live_money_and_autonomy_blocks_remain_active() -> None:
    default_result = evaluate_c1_supervised_demo_broker_account_readiness_bridge()
    approved_result = evaluate_c1_supervised_demo_broker_account_readiness_bridge(
        _valid_owner_input()
    )

    for result in (default_result, approved_result):
        assert result["demo_order_placement_authorized"] is False
        assert result["broker_api_access_authorized"] is False
        assert result["credential_access_authorized"] is False
        assert result["live_trading_blocked"] is True
        assert result["money_movement_blocked"] is True
        assert result["no_autonomy_approval"] is True


def test_bridge_is_created_only_for_valid_approved_path() -> None:
    rejected_input = _valid_owner_input()
    rejected_input["owner_decision"] = "REJECT_DEMO_INTENT"
    forbidden_input = _valid_owner_input()
    forbidden_input["api_key"] = "SANITIZED_FORBIDDEN_VALUE"

    default_result = evaluate_c1_supervised_demo_broker_account_readiness_bridge()
    rejected_result = evaluate_c1_supervised_demo_broker_account_readiness_bridge(
        rejected_input
    )
    forbidden_result = evaluate_c1_supervised_demo_broker_account_readiness_bridge(
        forbidden_input
    )
    approved_result = evaluate_c1_supervised_demo_broker_account_readiness_bridge(
        _valid_owner_input()
    )

    assert default_result["supervised_demo_broker_account_bridge_created"] is False
    assert rejected_result["supervised_demo_broker_account_bridge_created"] is False
    assert forbidden_result["supervised_demo_broker_account_bridge_created"] is False
    assert approved_result["supervised_demo_broker_account_bridge_created"] is True


def test_rejected_request_changes_or_invalid_owner_input_does_not_route_to_p9() -> None:
    rejected_input = _valid_owner_input()
    rejected_input["owner_decision"] = "REJECT_DEMO_INTENT"
    request_changes_input = _valid_owner_input()
    request_changes_input["owner_decision"] = "REQUEST_CHANGES"
    invalid_input = _valid_owner_input()
    invalid_input["daily_realized_loss_percent"] = 1.0

    for owner_input in (rejected_input, request_changes_input, invalid_input):
        result = evaluate_c1_supervised_demo_broker_account_readiness_bridge(
            owner_input
        )
        assert (
            result["next_required_lane"]
            != "P9_PROTECTED_SUPERVISED_DEMO_ORDER_EXECUTION_GATE_REVIEW"
        )
        assert result["broker_account_readiness_status"] == "NOT_READY"
        assert result["demo_order_placement_authorized"] is False


def test_forbidden_credential_account_or_api_fields_fail_or_stay_blocked() -> None:
    forbidden_fields = [
        "account_identifier",
        "credentials",
        "api_key",
        "raw_live_account_data",
    ]

    for field_name in forbidden_fields:
        owner_input = _valid_owner_input()
        owner_input[field_name] = "SANITIZED_FORBIDDEN_VALUE"
        result = evaluate_c1_supervised_demo_broker_account_readiness_bridge(
            owner_input
        )
        assert result["broker_account_readiness_status"] == "NOT_READY"
        assert (
            result["p8_bridge_status"] == "P8_BRIDGE_FAILED_REPAIR_REQUIRED"
        )
        assert (
            result["next_required_lane"]
            == "P8_BROKER_ACCOUNT_READINESS_REPAIR_REVIEW"
        )
        assert result["demo_order_placement_authorized"] is False
        assert result["broker_api_access_authorized"] is False
        assert result["credential_access_authorized"] is False


def test_generated_default_artifacts_exist_after_generate_artifacts() -> None:
    result = generate_artifacts()

    assert result["p8_bridge_status"] == "P8_BRIDGE_BLOCKED_OWNER_INPUT_REQUIRED"
    assert result["broker_account_readiness_status"] == "NOT_READY"
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
