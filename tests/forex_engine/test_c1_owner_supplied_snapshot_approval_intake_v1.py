from __future__ import annotations

from pathlib import Path

from automation.forex_engine.c1_owner_supplied_snapshot_approval_intake_v1 import (
    evaluate_c1_owner_supplied_snapshot_approval_intake,
)
from scripts.forex_delivery.run_c1_owner_supplied_snapshot_approval_intake_v1 import (
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
        "Reports/forex_delivery/AIOS_FOREX_C1_OWNER_SUPPLIED_SNAPSHOT_APPROVAL_INTAKE_V1.json"
    ),
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_OWNER_SUPPLIED_SNAPSHOT_APPROVAL_INTAKE_V1_REPORT.md"
    ),
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_OWNER_SUPPLIED_SNAPSHOT_APPROVAL_INTAKE_NEXT_ACTION_QUEUE_V1.md"
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


def test_default_owner_input_none_returns_owner_input_required() -> None:
    result = evaluate_c1_owner_supplied_snapshot_approval_intake()

    assert (
        result["p6b_intake_status"]
        == "P6B_OWNER_INPUT_NOT_SUPPLIED_INPUT_REQUIRED"
    )
    assert result["owner_input_status"] == "OWNER_INPUT_REQUIRED"
    assert result["post_p6b_score"] == 100
    assert (
        result["next_required_lane"]
        == "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"
    )
    assert result["demo_order_placement_authorized"] is False


def test_valid_sanitized_sample_is_accepted_for_p6c_validation() -> None:
    result = evaluate_c1_owner_supplied_snapshot_approval_intake(
        _valid_owner_input()
    )

    assert (
        result["p6b_intake_status"]
        == "P6B_OWNER_INPUT_ACCEPTED_FOR_P6C_VALIDATION"
    )
    assert result["owner_input_status"] == "OWNER_INPUT_ACCEPTED"
    assert result["next_required_lane"] == "P6C_OWNER_SNAPSHOT_APPROVAL_VALIDATION_GATE"
    assert result["demo_order_placement_authorized"] is False


def test_forbidden_secret_like_keys_are_rejected() -> None:
    owner_input = _valid_owner_input()
    owner_input["api_key"] = "blocked_synthetic_value"

    result = evaluate_c1_owner_supplied_snapshot_approval_intake(owner_input)

    assert result["p6b_intake_status"] == "P6B_OWNER_INPUT_REJECTED_REPAIR_REQUIRED"
    assert result["owner_input_status"] == "NOT_READY"
    assert "forbidden_fields_present" in result["failed_requirements"]
    assert result["demo_order_placement_authorized"] is False


def test_demo_order_placement_authorized_is_always_false() -> None:
    default_result = evaluate_c1_owner_supplied_snapshot_approval_intake()
    accepted_result = evaluate_c1_owner_supplied_snapshot_approval_intake(
        _valid_owner_input()
    )
    rejected_input = _valid_owner_input()
    rejected_input["password"] = "blocked_synthetic_value"
    rejected_result = evaluate_c1_owner_supplied_snapshot_approval_intake(
        rejected_input
    )

    assert default_result["demo_order_placement_authorized"] is False
    assert accepted_result["demo_order_placement_authorized"] is False
    assert rejected_result["demo_order_placement_authorized"] is False


def test_generated_default_artifacts_exist_after_generate_artifacts() -> None:
    result = generate_artifacts()

    assert result["owner_input_status"] == "OWNER_INPUT_REQUIRED"
    for path in GENERATED_PATHS:
        assert path.exists(), f"Missing generated artifact: {path}"


def test_generated_outputs_contain_no_banned_tokens() -> None:
    generate_artifacts()

    for path in GENERATED_PATHS:
        text = path.read_text(encoding="utf-8")
        for token in BANNED_TOKENS:
            assert token not in text
