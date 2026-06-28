from __future__ import annotations

from pathlib import Path

from automation.forex_engine.c1_owner_snapshot_approval_validation_gate_v1 import (
    evaluate_c1_owner_snapshot_approval_validation_gate,
)
from scripts.forex_delivery.run_c1_owner_snapshot_approval_validation_gate_v1 import (
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
]

GENERATED_PATHS = [
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_OWNER_SNAPSHOT_APPROVAL_VALIDATION_GATE_V1.json"
    ),
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_OWNER_SNAPSHOT_APPROVAL_VALIDATION_GATE_V1_REPORT.md"
    ),
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_OWNER_SNAPSHOT_APPROVAL_VALIDATION_GATE_NEXT_ACTION_QUEUE_V1.md"
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
    result = evaluate_c1_owner_snapshot_approval_validation_gate()

    assert (
        result["p6c_validation_status"]
        == "P6C_VALIDATION_BLOCKED_OWNER_INPUT_REQUIRED"
    )
    assert result["owner_decision_status"] == "OWNER_DECISION_NOT_SUPPLIED"
    assert result["post_p6c_score"] == 100
    assert (
        result["next_required_lane"]
        == "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"
    )
    assert result["demo_order_placement_authorized"] is False


def test_valid_approve_demo_intent_routes_to_p6d_final_review() -> None:
    result = evaluate_c1_owner_snapshot_approval_validation_gate(
        _valid_owner_input()
    )

    assert (
        result["p6c_validation_status"]
        == "P6C_OWNER_APPROVAL_VALIDATED_FOR_P6D_FINAL_REVIEW"
    )
    assert result["owner_decision_status"] == "OWNER_APPROVED_INTENT_VALIDATED"
    assert result["next_required_lane"] == "P6D_DEMO_ORDER_INTENT_FINAL_REVIEW_CARD"
    assert result["failed_checks"] == []
    assert result["demo_order_placement_authorized"] is False


def test_reject_demo_intent_routes_to_rejection_closure_queue() -> None:
    owner_input = _valid_owner_input()
    owner_input["owner_decision"] = "REJECT_DEMO_INTENT"

    result = evaluate_c1_owner_snapshot_approval_validation_gate(owner_input)

    assert result["p6c_validation_status"] == "P6C_OWNER_REJECTED_INTENT"
    assert result["owner_decision_status"] == "OWNER_REJECTED_INTENT"
    assert result["next_required_lane"] == "P6C_OWNER_REJECTION_CLOSURE_QUEUE"
    assert result["demo_order_placement_authorized"] is False


def test_request_changes_routes_to_owner_input_repair() -> None:
    owner_input = _valid_owner_input()
    owner_input["owner_decision"] = "REQUEST_CHANGES"

    result = evaluate_c1_owner_snapshot_approval_validation_gate(owner_input)

    assert result["p6c_validation_status"] == "P6C_OWNER_REQUESTED_CHANGES"
    assert result["owner_decision_status"] == "OWNER_REQUESTED_CHANGES"
    assert result["next_required_lane"] == "P6B_REPAIR_OWNER_INPUT"
    assert result["demo_order_placement_authorized"] is False


def test_kill_switch_or_loss_breach_fails_validation() -> None:
    kill_switch_input = _valid_owner_input()
    kill_switch_input["kill_switch_state"] = "TRIGGERED"
    daily_loss_input = _valid_owner_input()
    daily_loss_input["daily_realized_loss_percent"] = 1.0
    weekly_loss_input = _valid_owner_input()
    weekly_loss_input["weekly_realized_loss_percent"] = 2.0

    for owner_input in (kill_switch_input, daily_loss_input, weekly_loss_input):
        result = evaluate_c1_owner_snapshot_approval_validation_gate(owner_input)
        assert result["p6c_validation_status"] == "P6C_VALIDATION_FAILED_REPAIR_REQUIRED"
        assert result["owner_decision_status"] == "NOT_READY"
        assert result["next_required_lane"] == "P6B_REPAIR_OWNER_INPUT"
        assert result["demo_order_placement_authorized"] is False


def test_demo_order_placement_authorized_is_always_false() -> None:
    default_result = evaluate_c1_owner_snapshot_approval_validation_gate()
    approved_result = evaluate_c1_owner_snapshot_approval_validation_gate(
        _valid_owner_input()
    )
    rejected_input = _valid_owner_input()
    rejected_input["owner_decision"] = "REJECT_DEMO_INTENT"
    rejected_result = evaluate_c1_owner_snapshot_approval_validation_gate(
        rejected_input
    )

    assert default_result["demo_order_placement_authorized"] is False
    assert approved_result["demo_order_placement_authorized"] is False
    assert rejected_result["demo_order_placement_authorized"] is False


def test_generated_default_artifacts_exist_after_generate_artifacts() -> None:
    result = generate_artifacts()

    assert result["owner_decision_status"] == "OWNER_DECISION_NOT_SUPPLIED"
    for path in GENERATED_PATHS:
        assert path.exists(), f"Missing generated artifact: {path}"


def test_generated_outputs_contain_no_banned_tokens() -> None:
    generate_artifacts()

    for path in GENERATED_PATHS:
        text = path.read_text(encoding="utf-8")
        for token in BANNED_TOKENS:
            assert token not in text
