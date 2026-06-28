from __future__ import annotations

import json
from pathlib import Path

from automation.forex_engine.c1_demo_order_intent_owner_approval_gate_v1 import (
    evaluate_c1_demo_order_intent_owner_approval_gate,
)
from scripts.forex_delivery.run_c1_demo_order_intent_owner_approval_gate_v1 import (
    generate_artifacts,
)


ALLOWED_P6_GATE_STATUSES = {
    "P6_DEMO_ORDER_INTENT_GATE_CREATED_OWNER_ACTION_REQUIRED",
    "P6_DEMO_ORDER_INTENT_GATE_BLOCKED_P5_REPAIR_REQUIRED",
    "P6_DEMO_ORDER_INTENT_GATE_BLOCKED_SAFETY_REQUIREMENTS",
}

REQUIRED_INTENT_CARD_FIELDS = {
    "candidate_id",
    "candidate_name",
    "intended_instrument",
    "intended_side",
    "order_type_status",
    "units_formula_only",
    "units_formula",
    "max_risk_per_trade_percent",
    "max_daily_loss_percent",
    "max_weekly_loss_percent",
    "max_open_positions",
    "max_orders_per_signal",
    "stop_loss_required",
    "take_profit_required",
    "minimum_reward_to_risk",
    "stop_loss_formula_required",
    "take_profit_formula_required",
    "sanitized_snapshot_required",
    "owner_approval_required",
    "owner_approval_status",
    "demo_order_placement_authorized",
    "live_trading_blocked",
    "broker_api_access_blocked",
    "credential_access_blocked",
    "money_movement_blocked",
    "one_order_rule_verification_required",
    "daily_stop_verification_required",
    "weekly_stop_verification_required",
    "kill_switch_verification_required",
    "audit_artifacts_required",
    "no_autonomy_approval",
}

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
]

GENERATED_PATHS = [
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_DEMO_ORDER_INTENT_OWNER_APPROVAL_GATE_V1.json"
    ),
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_DEMO_ORDER_INTENT_OWNER_APPROVAL_GATE_V1_REPORT.md"
    ),
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_DEMO_ORDER_INTENT_OWNER_APPROVAL_GATE_NEXT_ACTION_QUEUE_V1.md"
    ),
]


def test_p6_gate_contract() -> None:
    result = evaluate_c1_demo_order_intent_owner_approval_gate()

    assert result["candidate_id"] == "c1-eur-buy"
    assert result["input_score"] in [85, 100]
    assert result["post_p6_score"] <= 100
    assert result["p6_gate_status"] in ALLOWED_P6_GATE_STATUSES
    assert result["owner_action_status"] in {"OWNER_ACTION_REQUIRED", "NOT_READY"}

    if result["owner_action_status"] == "OWNER_ACTION_REQUIRED":
        assert (
            result["next_required_lane"]
            == "P6A_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_DECISION"
        )


def test_demo_order_intent_card_contains_required_fields() -> None:
    result = evaluate_c1_demo_order_intent_owner_approval_gate()
    card = result["demo_order_intent_card"]

    assert REQUIRED_INTENT_CARD_FIELDS.issubset(set(card))
    assert card["candidate_id"] == "c1-eur-buy"
    assert card["intended_instrument"] == "EUR_USD"
    assert card["intended_side"] == "BUY"
    assert card["order_type_status"] == "OWNER_SELECTION_REQUIRED"
    assert card["units_formula_only"] is True
    assert card["units_formula"] == "units = risk_amount / stop_loss_value_per_unit"
    assert card["demo_order_placement_authorized"] is False
    assert card["max_risk_per_trade_percent"] <= 0.25
    assert card["max_daily_loss_percent"] <= 1.00
    assert card["max_weekly_loss_percent"] <= 2.00
    assert card["max_open_positions"] == 1
    assert card["max_orders_per_signal"] == 1


def test_owner_snapshot_and_safety_blocks() -> None:
    result = evaluate_c1_demo_order_intent_owner_approval_gate()
    snapshot = result["sanitized_snapshot_requirement"]
    owner = result["owner_approval_requirement"]
    pre_order = result["pre_order_safety_checks"]
    card = result["demo_order_intent_card"]

    assert snapshot["requires_sanitized_broker_account_snapshot"] is True
    assert snapshot["collected_in_this_packet"] is False
    assert owner["owner_approval_required"] is True
    assert owner["approved_by_this_packet"] is False
    assert owner["approval_granted"] is False
    assert owner["demo_order_placement_authorized"] is False
    assert pre_order["broker_api_access_blocked"] is True
    assert pre_order["credential_access_blocked"] is True
    assert pre_order["live_trading_blocked"] is True
    assert pre_order["money_movement_blocked"] is True
    assert pre_order["no_autonomy_approval"] is True
    assert card["no_autonomy_approval"] is True


def test_verifications_forbidden_actions_and_final_sentence_exist() -> None:
    result = evaluate_c1_demo_order_intent_owner_approval_gate()

    assert result["one_order_verification"]["one_order_rule_verification_required"]
    assert result["tp_sl_verification"]["stop_loss_required"] is True
    assert result["tp_sl_verification"]["take_profit_required"] is True
    assert result["stop_rule_verification"]["daily_stop_verification_required"]
    assert result["stop_rule_verification"]["weekly_stop_verification_required"]
    assert result["kill_switch_verification"]["kill_switch_verification_required"]
    assert "broker/API access" in result["forbidden_actions"]
    assert "credential access" in result["forbidden_actions"]
    assert "live trading" in result["forbidden_actions"]
    assert "money movement" in result["forbidden_actions"]
    assert "autonomous trading" in result["forbidden_actions"]
    assert result["final_owner_sentence"]


def test_generated_artifacts_are_present_and_clean() -> None:
    generate_artifacts()

    for path in GENERATED_PATHS:
        assert path.exists(), f"Missing generated artifact: {path}"
        text = path.read_text(encoding="utf-8")
        for token in BANNED_TOKENS:
            assert token not in text


def test_generated_json_matches_evaluator() -> None:
    result = generate_artifacts()
    generated = json.loads(GENERATED_PATHS[0].read_text(encoding="utf-8"))

    assert generated["campaign_id"] == result["campaign_id"]
    assert generated["candidate_id"] == result["candidate_id"]
    assert generated["input_score"] == result["input_score"]
    assert generated["post_p6_score"] == result["post_p6_score"]
    assert generated["p6_gate_status"] == result["p6_gate_status"]
    assert generated["owner_action_status"] == result["owner_action_status"]
    assert generated["next_required_lane"] == result["next_required_lane"]
