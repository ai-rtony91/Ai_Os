from __future__ import annotations

import json
from pathlib import Path

from automation.forex_engine.c1_owner_snapshot_approval_decision_gate_v1 import (
    evaluate_c1_owner_snapshot_approval_decision_gate,
)
from scripts.forex_delivery.run_c1_owner_snapshot_approval_decision_gate_v1 import (
    generate_artifacts,
)


ALLOWED_P6A_GATE_STATUSES = {
    "P6A_OWNER_INPUT_CONTRACT_CREATED_INPUT_REQUIRED",
    "P6A_BLOCKED_P6_REPAIR_REQUIRED",
    "P6A_BLOCKED_OWNER_INPUT_CONTRACT_INCOMPLETE",
}

REQUIRED_OWNER_INPUT_CONTRACT_FIELDS = {
    "owner_decision_required",
    "accepted_owner_decisions",
    "sanitized_snapshot_required",
    "required_snapshot_fields",
    "forbidden_snapshot_fields",
    "required_approval_fields",
    "intended_instrument_confirmation",
    "intended_side_confirmation",
    "order_type_selection_required",
    "units_formula_review_required",
    "stop_loss_review_required",
    "take_profit_review_required",
    "reward_to_risk_review_required",
    "one_order_rule_verification_required",
    "daily_stop_verification_required",
    "weekly_stop_verification_required",
    "kill_switch_verification_required",
    "audit_record_required",
    "demo_order_placement_authorized",
    "live_trading_blocked",
    "broker_api_access_blocked",
    "credential_access_blocked",
    "money_movement_blocked",
    "no_autonomy_approval",
}

ACCEPTED_OWNER_DECISIONS = [
    "APPROVE_DEMO_INTENT",
    "REJECT_DEMO_INTENT",
    "REQUEST_CHANGES",
]

REQUIRED_SNAPSHOT_FIELDS = {
    "demo_account_marker",
    "sanitized_equity_value_or_bracket",
    "current_open_position_count",
    "current_same_signal_order_count",
    "daily_realized_loss_percent",
    "weekly_realized_loss_percent",
    "kill_switch_state",
    "timestamp_utc",
    "owner_attestation",
}

FORBIDDEN_SNAPSHOT_FIELDS = {
    "API keys",
    "tokens",
    "passwords",
    "broker credentials",
    "account identifiers",
    "broker order identifiers",
    "raw live account data",
    "private execution payloads",
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
    "approval granted",
    "snapshot collected",
]

GENERATED_PATHS = [
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_OWNER_SNAPSHOT_APPROVAL_DECISION_GATE_V1.json"
    ),
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_OWNER_SNAPSHOT_APPROVAL_DECISION_GATE_V1_REPORT.md"
    ),
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_OWNER_SNAPSHOT_APPROVAL_DECISION_GATE_NEXT_ACTION_QUEUE_V1.md"
    ),
]


def test_p6a_gate_contract_statuses() -> None:
    result = evaluate_c1_owner_snapshot_approval_decision_gate()

    assert result["candidate_id"] == "c1-eur-buy"
    assert result["input_score"] in [85, 100]
    assert result["post_p6a_score"] <= 100
    assert result["p6a_gate_status"] in ALLOWED_P6A_GATE_STATUSES
    assert result["owner_input_status"] in {"OWNER_INPUT_REQUIRED", "NOT_READY"}

    if result["owner_input_status"] == "OWNER_INPUT_REQUIRED":
        assert (
            result["next_required_lane"]
            == "P6B_OWNER_SUPPLIED_SNAPSHOT_APPROVAL_INTAKE"
        )


def test_owner_input_contract_contains_required_fields() -> None:
    result = evaluate_c1_owner_snapshot_approval_decision_gate()
    contract = result["owner_input_contract"]

    assert REQUIRED_OWNER_INPUT_CONTRACT_FIELDS.issubset(set(contract))
    assert contract["accepted_owner_decisions"] == ACCEPTED_OWNER_DECISIONS
    assert contract["owner_decision_required"] is True
    assert contract["sanitized_snapshot_required"] is True
    assert contract["demo_order_placement_authorized"] is False
    assert contract["broker_api_access_blocked"] is True
    assert contract["credential_access_blocked"] is True
    assert contract["live_trading_blocked"] is True
    assert contract["money_movement_blocked"] is True
    assert contract["no_autonomy_approval"] is True


def test_snapshot_contract_fields_and_exclusions() -> None:
    result = evaluate_c1_owner_snapshot_approval_decision_gate()
    snapshot_contract = result["sanitized_snapshot_contract"]

    assert REQUIRED_SNAPSHOT_FIELDS.issubset(
        set(snapshot_contract["required_snapshot_fields"])
    )
    assert FORBIDDEN_SNAPSHOT_FIELDS.issubset(
        set(snapshot_contract["forbidden_snapshot_fields"])
    )
    assert snapshot_contract["provided_by_this_packet"] is False
    assert snapshot_contract["demo_order_placement_authorized"] is False


def test_decision_contract_and_safety_blocks() -> None:
    result = evaluate_c1_owner_snapshot_approval_decision_gate()
    decision_contract = result["owner_approval_decision_contract"]

    assert decision_contract["accepted_owner_decisions"] == ACCEPTED_OWNER_DECISIONS
    assert decision_contract["owner_decision_status"] == "OWNER_DECISION_NOT_SUPPLIED"
    assert result["demo_order_placement_authorized"] is False
    assert result["broker_api_access_blocked"] is True
    assert result["credential_access_blocked"] is True
    assert result["live_trading_blocked"] is True
    assert result["money_movement_blocked"] is True
    assert result["no_autonomy_approval"] is True


def test_forbidden_actions_and_final_sentence_exist() -> None:
    result = evaluate_c1_owner_snapshot_approval_decision_gate()

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
    assert generated["post_p6a_score"] == result["post_p6a_score"]
    assert generated["p6a_gate_status"] == result["p6a_gate_status"]
    assert generated["owner_input_status"] == result["owner_input_status"]
    assert generated["next_required_lane"] == result["next_required_lane"]
