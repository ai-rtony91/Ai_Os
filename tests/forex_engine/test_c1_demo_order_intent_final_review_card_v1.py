from __future__ import annotations

from pathlib import Path

from automation.forex_engine.c1_demo_order_intent_final_review_card_v1 import (
    evaluate_c1_demo_order_intent_final_review_card,
)
from scripts.forex_delivery.run_c1_demo_order_intent_final_review_card_v1 import (
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
        "Reports/forex_delivery/AIOS_FOREX_C1_DEMO_ORDER_INTENT_FINAL_REVIEW_CARD_V1.json"
    ),
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_DEMO_ORDER_INTENT_FINAL_REVIEW_CARD_V1_REPORT.md"
    ),
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_DEMO_ORDER_INTENT_FINAL_REVIEW_CARD_NEXT_ACTION_QUEUE_V1.md"
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
    result = evaluate_c1_demo_order_intent_final_review_card()

    assert (
        result["p6d_final_review_status"]
        == "P6D_FINAL_REVIEW_BLOCKED_OWNER_INPUT_REQUIRED"
    )
    assert result["final_review_status"] == "NOT_READY"
    assert result["post_p6d_score"] == 100
    assert (
        result["next_required_lane"]
        == "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"
    )
    assert result["demo_order_placement_authorized"] is False


def test_valid_approved_sanitized_sample_routes_to_p7_rehearsal() -> None:
    result = evaluate_c1_demo_order_intent_final_review_card(_valid_owner_input())

    assert (
        result["p6d_final_review_status"]
        == "P6D_FINAL_REVIEW_CARD_READY_FOR_P7_DRY_RUN_REHEARSAL"
    )
    assert result["final_review_status"] == "P7_DRY_RUN_REHEARSAL_READY"
    assert result["next_required_lane"] == "P7_DRY_RUN_MOCK_EXECUTION_REHEARSAL"
    assert result["final_review_card"]["candidate_id"] == "c1-eur-buy"
    assert result["final_review_card"]["intended_instrument"] == "EUR_USD"
    assert result["final_review_card"]["intended_side"] == "BUY"
    assert result["demo_order_placement_authorized"] is False


def test_rejected_request_changes_or_invalid_sample_does_not_route_to_p7() -> None:
    rejected_input = _valid_owner_input()
    rejected_input["owner_decision"] = "REJECT_DEMO_INTENT"
    request_changes_input = _valid_owner_input()
    request_changes_input["owner_decision"] = "REQUEST_CHANGES"
    invalid_input = _valid_owner_input()
    invalid_input["daily_realized_loss_percent"] = 1.0

    for owner_input in (rejected_input, request_changes_input, invalid_input):
        result = evaluate_c1_demo_order_intent_final_review_card(owner_input)
        assert result["next_required_lane"] != "P7_DRY_RUN_MOCK_EXECUTION_REHEARSAL"
        assert result["final_review_status"] == "NOT_READY"
        assert result["demo_order_placement_authorized"] is False


def test_demo_order_placement_authorized_is_always_false() -> None:
    default_result = evaluate_c1_demo_order_intent_final_review_card()
    approved_result = evaluate_c1_demo_order_intent_final_review_card(
        _valid_owner_input()
    )
    invalid_input = _valid_owner_input()
    invalid_input["kill_switch_state"] = "TRIGGERED"
    invalid_result = evaluate_c1_demo_order_intent_final_review_card(invalid_input)

    assert default_result["demo_order_placement_authorized"] is False
    assert approved_result["demo_order_placement_authorized"] is False
    assert invalid_result["demo_order_placement_authorized"] is False


def test_broker_credentials_live_money_and_autonomy_blocks_remain_active() -> None:
    result = evaluate_c1_demo_order_intent_final_review_card(_valid_owner_input())

    assert result["broker_api_access_blocked"] is True
    assert result["credential_access_blocked"] is True
    assert result["live_trading_blocked"] is True
    assert result["money_movement_blocked"] is True
    assert result["no_autonomy_approval"] is True
    assert result["final_review_card"]["broker_api_access_blocked"] is True
    assert result["final_review_card"]["credential_access_blocked"] is True
    assert result["final_review_card"]["live_trading_blocked"] is True
    assert result["final_review_card"]["money_movement_blocked"] is True
    assert result["final_review_card"]["no_autonomy_approval"] is True


def test_generated_default_artifacts_exist_after_generate_artifacts() -> None:
    result = generate_artifacts()

    assert result["final_review_status"] == "NOT_READY"
    for path in GENERATED_PATHS:
        assert path.exists(), f"Missing generated artifact: {path}"


def test_generated_outputs_contain_no_banned_tokens() -> None:
    generate_artifacts()

    for path in GENERATED_PATHS:
        text = path.read_text(encoding="utf-8")
        for token in BANNED_TOKENS:
            assert token not in text
