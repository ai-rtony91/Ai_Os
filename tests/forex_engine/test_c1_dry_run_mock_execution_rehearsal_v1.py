from __future__ import annotations

from pathlib import Path

from automation.forex_engine.c1_dry_run_mock_execution_rehearsal_v1 import (
    evaluate_c1_dry_run_mock_execution_rehearsal,
)
from scripts.forex_delivery.run_c1_dry_run_mock_execution_rehearsal_v1 import (
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
]

GENERATED_PATHS = [
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_DRY_RUN_MOCK_EXECUTION_REHEARSAL_V1.json"
    ),
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_DRY_RUN_MOCK_EXECUTION_REHEARSAL_V1_REPORT.md"
    ),
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_DRY_RUN_MOCK_EXECUTION_REHEARSAL_NEXT_ACTION_QUEUE_V1.md"
    ),
]


def _valid_owner_input() -> dict[str, object]:
    return {
        "owner_decision": "APPROVE_DEMO_INTENT",
        "demo_account_marker": "DEMO_ONLY",
        "sanitized_equity_value_or_bracket": "DEMO_EQUITY_BRACKET_A",
        "current_open_position_count": 0,
        "current_same_signal_order_count": 0,
        "daily_realized_loss_percent": 0.0,
        "weekly_realized_loss_percent": 0.0,
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
        "one_order_rule_verification": True,
        "daily_stop_verification": True,
        "weekly_stop_verification": True,
        "kill_switch_verification": True,
    }


def test_default_owner_input_none_blocks_on_owner_input_required() -> None:
    result = evaluate_c1_dry_run_mock_execution_rehearsal()

    assert (
        result["p7_rehearsal_status"]
        == "P7_DRY_RUN_REHEARSAL_BLOCKED_OWNER_INPUT_REQUIRED"
    )
    assert result["mock_rehearsal_status"] == "NOT_READY"
    assert result["post_p7_score"] == 100
    assert (
        result["next_required_lane"]
        == "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"
    )
    assert result["mock_order_plan_created"] is False
    assert result["demo_order_placement_authorized"] is False


def test_valid_approved_sanitized_sample_routes_to_p8_review() -> None:
    result = evaluate_c1_dry_run_mock_execution_rehearsal(_valid_owner_input())

    assert (
        result["p7_rehearsal_status"]
        == "P7_DRY_RUN_MOCK_REHEARSAL_PASSED_FOR_P8_REVIEW"
    )
    assert result["mock_rehearsal_status"] == "P8_READY"
    assert (
        result["next_required_lane"]
        == "P8_SUPERVISED_DEMO_BROKER_ACCOUNT_READINESS_BRIDGE"
    )
    assert result["mock_order_plan_created"] is True
    assert result["mock_order_plan"]["candidate_id"] == "c1-eur-buy"
    assert result["mock_order_plan"]["candidate_name"] == (
        "paper_long_run_supervisor_v2 LONG EURUSD"
    )
    assert result["mock_order_plan"]["instrument"] == "EUR_USD"
    assert result["mock_order_plan"]["side"] == "BUY"
    assert result["mock_order_plan"]["order_type_selection"] == "MARKET"
    assert result["mock_order_plan"]["mock_order_plan_type"] == (
        "INERT_LOCAL_REHEARSAL_ONLY"
    )
    assert result["failed_requirements"] == []


def test_valid_approved_sanitized_sample_preserves_rehearsal_guardrails() -> None:
    result = evaluate_c1_dry_run_mock_execution_rehearsal(_valid_owner_input())
    plan = result["mock_order_plan"]

    assert plan["units_formula"] == "units = risk_amount / stop_loss_value_per_unit"
    assert plan["max_risk_per_trade_percent"] == 0.25
    assert plan["max_daily_loss_percent"] == 1.00
    assert plan["max_weekly_loss_percent"] == 2.00
    assert plan["max_open_positions"] == 1
    assert plan["max_orders_per_signal"] == 1
    assert plan["stop_loss_required"] is True
    assert plan["take_profit_required"] is True
    assert plan["minimum_reward_to_risk"] == 1.20
    assert plan["one_order_rule_verified"] is True
    assert plan["daily_stop_verified"] is True
    assert plan["weekly_stop_verified"] is True
    assert plan["kill_switch_verified"] is True
    assert plan["audit_record_required"] is True
    assert all(result["rehearsal_checks"].values())


def test_demo_broker_credential_live_money_and_autonomy_blocks_remain_active() -> None:
    default_result = evaluate_c1_dry_run_mock_execution_rehearsal()
    approved_result = evaluate_c1_dry_run_mock_execution_rehearsal(
        _valid_owner_input()
    )

    for result in (default_result, approved_result):
        assert result["demo_order_placement_authorized"] is False
        assert result["broker_api_access_blocked"] is True
        assert result["credential_access_blocked"] is True
        assert result["live_trading_blocked"] is True
        assert result["money_movement_blocked"] is True
        assert result["no_autonomy_approval"] is True


def test_rejected_request_changes_or_invalid_sample_does_not_route_to_p8() -> None:
    rejected_input = _valid_owner_input()
    rejected_input["owner_decision"] = "REJECT_DEMO_INTENT"
    request_changes_input = _valid_owner_input()
    request_changes_input["owner_decision"] = "REQUEST_CHANGES"
    invalid_input = _valid_owner_input()
    invalid_input["daily_realized_loss_percent"] = 1.0

    for owner_input in (rejected_input, request_changes_input, invalid_input):
        result = evaluate_c1_dry_run_mock_execution_rehearsal(owner_input)
        assert (
            result["next_required_lane"]
            != "P8_SUPERVISED_DEMO_BROKER_ACCOUNT_READINESS_BRIDGE"
        )
        assert (
            result["p7_rehearsal_status"]
            == "P7_DRY_RUN_REHEARSAL_BLOCKED_P6D_REPAIR_REQUIRED"
        )
        assert result["mock_rehearsal_status"] == "NOT_READY"
        assert result["mock_order_plan_created"] is False
        assert result["demo_order_placement_authorized"] is False


def test_generated_default_artifacts_exist_after_generate_artifacts() -> None:
    result = generate_artifacts()

    assert (
        result["p7_rehearsal_status"]
        == "P7_DRY_RUN_REHEARSAL_BLOCKED_OWNER_INPUT_REQUIRED"
    )
    assert result["mock_rehearsal_status"] == "NOT_READY"
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
