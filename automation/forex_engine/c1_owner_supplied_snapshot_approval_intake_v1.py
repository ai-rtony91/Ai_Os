"""Deterministic C1 owner-supplied snapshot approval intake gate.

This module accepts only sanitized owner-input dictionaries for local
validation routing. It does not access brokers, credentials, accounts,
balances, prices, orders, schedulers, daemons, webhooks, production systems,
or trading execution paths.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from automation.forex_engine.c1_owner_snapshot_approval_decision_gate_v1 import (
    evaluate_c1_owner_snapshot_approval_decision_gate,
)


CAMPAIGN_ID = "AIOS-FOREX-P6B-C1-OWNER-SUPPLIED-SNAPSHOT-APPROVAL-INTAKE-V1"
CANDIDATE_ID = "c1-eur-buy"
CANDIDATE_NAME = "paper_long_run_supervisor_v2 LONG EURUSD"

TRADER_MEANING = (
    "AIOS is preparing the intake gate for the owner's sanitized demo-account "
    "snapshot and approve, reject, or request-changes decision without "
    "collecting secrets or authorizing any order."
)

OWNER_INPUT_REQUIRED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P6B C1 intake is waiting for owner-supplied sanitized input; "
    "owner input is still required and demo-order placement remains blocked "
    "while live trading, broker/API, credentials, money movement, and autonomy "
    "stay blocked."
)

OWNER_INPUT_ACCEPTED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P6B C1 intake accepted sanitized owner input for P6C "
    "validation only; demo-order placement, live trading, broker/API, "
    "credentials, money movement, and autonomy remain blocked."
)

OWNER_INPUT_REJECTED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P6B C1 intake rejected the owner input for repair; "
    "demo-order placement, live trading, broker/API, credentials, money "
    "movement, and autonomy remain blocked."
)

ACCEPTED_OWNER_DECISIONS = [
    "APPROVE_DEMO_INTENT",
    "REJECT_DEMO_INTENT",
    "REQUEST_CHANGES",
]

ACCEPTED_ORDER_TYPES = ["MARKET", "LIMIT", "STOP"]

REQUIRED_OWNER_INPUT_FIELDS = [
    "owner_decision",
    "demo_account_marker",
    "sanitized_equity_value_or_bracket",
    "current_open_position_count",
    "current_same_signal_order_count",
    "daily_realized_loss_percent",
    "weekly_realized_loss_percent",
    "kill_switch_state",
    "timestamp_utc",
    "owner_attestation",
    "intended_instrument_confirmation",
    "intended_side_confirmation",
    "order_type_selection",
    "units_formula_review",
    "stop_loss_review",
    "take_profit_review",
    "reward_to_risk_review",
    "one_order_rule_verification",
    "daily_stop_verification",
    "weekly_stop_verification",
    "kill_switch_verification",
]

BOOLEAN_REVIEW_FIELDS = [
    "owner_attestation",
    "units_formula_review",
    "stop_loss_review",
    "take_profit_review",
    "reward_to_risk_review",
    "one_order_rule_verification",
    "daily_stop_verification",
    "weekly_stop_verification",
    "kill_switch_verification",
]

NUMERIC_FIELDS = [
    "current_open_position_count",
    "current_same_signal_order_count",
    "daily_realized_loss_percent",
    "weekly_realized_loss_percent",
]

STRING_FIELDS = [
    "demo_account_marker",
    "sanitized_equity_value_or_bracket",
    "kill_switch_state",
    "timestamp_utc",
    "intended_instrument_confirmation",
    "intended_side_confirmation",
]

FORBIDDEN_OWNER_INPUT_FIELDS = [
    "API keys",
    "tokens",
    "passwords",
    "broker credentials",
    "account identifiers",
    "broker order identifiers",
    "raw live account data",
    "private execution payloads",
]

FORBIDDEN_KEY_FRAGMENTS = [
    "api_key",
    "apikey",
    "api key",
    "token",
    "password",
    "credential",
    "account_id",
    "account identifier",
    "account_number",
    "broker_order_id",
    "order_identifier",
    "raw_live_account",
    "private_execution_payload",
    "secret",
]

BLOCKED_ACTIONS = [
    "demo-order placement authorization",
    "live trading",
    "broker/API access",
    "credential access",
    "account access",
    "order-placement execution",
    "order closure",
    "money movement",
    "scheduler activation",
    "daemon activation",
    "webhook activation",
    "production activation",
    "autonomous trading",
    "claiming owner approval as supplied",
    "claiming demo-order authority",
    "claiming live trading authority",
    "claiming 22/6 autonomy readiness",
    "claiming vacation/luxury mode as active",
    "claiming 100-120 percent return evidence",
]

PASSED_REQUIREMENTS = [
    "p6a_entry_condition",
    "required_fields_present",
    "forbidden_fields_absent",
    "owner_decision_accepted",
    "field_types_valid",
    "demo_order_placement_block",
    "broker_api_credential_live_blocks",
    "money_movement_block",
    "no_autonomy_approval",
]


def _safe_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _find_forbidden_fields(value: Any, path: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, nested_value in value.items():
            key_text = str(key)
            key_lower = key_text.lower()
            current_path = f"{path}.{key_text}" if path else key_text
            if any(fragment in key_lower for fragment in FORBIDDEN_KEY_FRAGMENTS):
                findings.append(current_path)
            findings.extend(_find_forbidden_fields(nested_value, current_path))
    elif isinstance(value, list):
        for index, nested_value in enumerate(value):
            findings.extend(_find_forbidden_fields(nested_value, f"{path}[{index}]"))
    return findings


def _validate_owner_input(owner_input: Any) -> tuple[bool, list[str], list[str]]:
    if not isinstance(owner_input, dict):
        return False, ["owner_input_must_be_dict"], []

    failed_requirements: list[str] = []
    missing_fields = [
        field for field in REQUIRED_OWNER_INPUT_FIELDS if field not in owner_input
    ]
    if missing_fields:
        failed_requirements.append("missing_required_fields")

    forbidden_fields = _find_forbidden_fields(owner_input)
    if forbidden_fields:
        failed_requirements.append("forbidden_fields_present")

    owner_decision = owner_input.get("owner_decision")
    if owner_decision not in ACCEPTED_OWNER_DECISIONS:
        failed_requirements.append("owner_decision_not_accepted")

    order_type = owner_input.get("order_type_selection")
    if order_type not in ACCEPTED_ORDER_TYPES:
        failed_requirements.append("order_type_not_accepted")

    for field in BOOLEAN_REVIEW_FIELDS:
        if field in owner_input and not isinstance(owner_input[field], bool):
            failed_requirements.append(f"{field}_must_be_boolean")

    for field in NUMERIC_FIELDS:
        if field in owner_input and _safe_number(owner_input[field]) is None:
            failed_requirements.append(f"{field}_must_be_numeric")

    for field in STRING_FIELDS:
        value = owner_input.get(field)
        if field in owner_input and (not isinstance(value, str) or not value.strip()):
            failed_requirements.append(f"{field}_must_be_nonempty_string")

    valid = not failed_requirements
    return valid, failed_requirements, forbidden_fields


def _bullet_list(items: list[str] | tuple[str, ...]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def _contract_lines(mapping: dict[str, Any]) -> str:
    rows = ["| field | value |", "|---|---|"]
    for key, value in mapping.items():
        rows.append(f"| `{key}` | `{value}` |")
    return "\n".join(rows)


def _build_owner_input_contract() -> dict[str, Any]:
    return {
        "required_owner_input_fields": list(REQUIRED_OWNER_INPUT_FIELDS),
        "accepted_owner_decisions": list(ACCEPTED_OWNER_DECISIONS),
        "accepted_order_types": list(ACCEPTED_ORDER_TYPES),
        "forbidden_owner_input_fields": list(FORBIDDEN_OWNER_INPUT_FIELDS),
        "demo_order_placement_authorized": False,
        "live_trading_blocked": True,
        "broker_api_access_blocked": True,
        "credential_access_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
    }


def _p6a_ready(p6a_result: dict[str, Any]) -> bool:
    return (
        p6a_result.get("p6a_gate_status")
        == "P6A_OWNER_INPUT_CONTRACT_CREATED_INPUT_REQUIRED"
        and p6a_result.get("owner_input_status") == "OWNER_INPUT_REQUIRED"
        and p6a_result.get("next_required_lane")
        == "P6B_OWNER_SUPPLIED_SNAPSHOT_APPROVAL_INTAKE"
        and p6a_result.get("demo_order_placement_authorized") is False
        and p6a_result.get("broker_api_access_blocked") is True
        and p6a_result.get("credential_access_blocked") is True
        and p6a_result.get("live_trading_blocked") is True
        and p6a_result.get("money_movement_blocked") is True
        and p6a_result.get("no_autonomy_approval") is True
    )


def evaluate_c1_owner_supplied_snapshot_approval_intake(
    owner_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the deterministic P6B owner-input intake result."""

    p6a_result = evaluate_c1_owner_snapshot_approval_decision_gate()
    owner_input_contract = _build_owner_input_contract()
    p6a_entry_ready = _p6a_ready(p6a_result)

    if owner_input is None:
        p6b_intake_status = "P6B_OWNER_INPUT_NOT_SUPPLIED_INPUT_REQUIRED"
        owner_input_status = "OWNER_INPUT_REQUIRED"
        next_required_lane = "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"
        post_p6b_score = 100
        failed_requirements: list[str] = []
        forbidden_fields: list[str] = []
        passed_requirements = ["p6a_entry_condition"] if p6a_entry_ready else []
        final_owner_sentence = OWNER_INPUT_REQUIRED_FINAL_OWNER_SENTENCE
    elif not p6a_entry_ready:
        p6b_intake_status = "P6B_OWNER_INPUT_REJECTED_REPAIR_REQUIRED"
        owner_input_status = "NOT_READY"
        next_required_lane = "P6A_OWNER_INPUT_CONTRACT_REPAIR"
        post_p6b_score = 85
        failed_requirements = ["p6a_entry_condition_not_ready"]
        forbidden_fields = []
        passed_requirements = []
        final_owner_sentence = OWNER_INPUT_REJECTED_FINAL_OWNER_SENTENCE
    else:
        valid, failed_requirements, forbidden_fields = _validate_owner_input(
            owner_input
        )
        if valid:
            p6b_intake_status = "P6B_OWNER_INPUT_ACCEPTED_FOR_P6C_VALIDATION"
            owner_input_status = "OWNER_INPUT_ACCEPTED"
            next_required_lane = "P6C_OWNER_SNAPSHOT_APPROVAL_VALIDATION_GATE"
            post_p6b_score = 100
            passed_requirements = list(PASSED_REQUIREMENTS)
            final_owner_sentence = OWNER_INPUT_ACCEPTED_FINAL_OWNER_SENTENCE
        else:
            p6b_intake_status = "P6B_OWNER_INPUT_REJECTED_REPAIR_REQUIRED"
            owner_input_status = "NOT_READY"
            next_required_lane = "P6B_REPAIR_OWNER_INPUT"
            post_p6b_score = 80
            passed_requirements = [
                requirement
                for requirement in PASSED_REQUIREMENTS
                if requirement not in failed_requirements
            ]
            final_owner_sentence = OWNER_INPUT_REJECTED_FINAL_OWNER_SENTENCE

    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "p6a_gate_status": p6a_result.get("p6a_gate_status"),
        "p6a_owner_input_status": p6a_result.get("owner_input_status"),
        "p6a_entry_ready": p6a_entry_ready,
        "p6b_intake_status": p6b_intake_status,
        "owner_input_status": owner_input_status,
        "post_p6b_score": post_p6b_score,
        "next_required_lane": next_required_lane,
        "owner_input_contract": deepcopy(owner_input_contract),
        "required_owner_input_fields": list(REQUIRED_OWNER_INPUT_FIELDS),
        "forbidden_owner_input_fields": list(FORBIDDEN_OWNER_INPUT_FIELDS),
        "accepted_owner_decisions": list(ACCEPTED_OWNER_DECISIONS),
        "accepted_order_types": list(ACCEPTED_ORDER_TYPES),
        "forbidden_fields_detected": forbidden_fields,
        "passed_requirements": passed_requirements,
        "failed_requirements": failed_requirements,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "demo_order_placement_authorized": False,
        "live_trading_blocked": True,
        "broker_api_access_blocked": True,
        "credential_access_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
        "owner_decision": owner_input.get("owner_decision") if owner_input else None,
        "trader_meaning": TRADER_MEANING,
        "final_owner_sentence": final_owner_sentence,
    }


def render_owner_report(result: dict[str, Any]) -> str:
    """Render the owner-facing P6B intake report."""

    return f"""# AIOS Forex C1 Owner Supplied Snapshot Approval Intake V1 Report

## Campaign Scope

This report applies the P6B C1 owner-supplied snapshot approval intake for `c1-eur-buy` only. It consumes the P6A owner-input contract and prepares sanitized owner input for deterministic P6C validation.

This report does not collect secrets, read credentials, access accounts, access brokers, calculate live or account-specific position size, place demo orders, place live orders, close orders, move money, activate schedulers, activate daemons, activate webhooks, activate production, or authorize autonomous trading.

## Trader Meaning

{TRADER_MEANING}

## P6A Entry Condition

- p6a_gate_status: `{result["p6a_gate_status"]}`
- p6a_owner_input_status: `{result["p6a_owner_input_status"]}`
- p6a_entry_ready: `{result["p6a_entry_ready"]}`

## Owner Input Intake Contract

{_contract_lines(result["owner_input_contract"])}

## Required Owner Input Fields

{_bullet_list(result["required_owner_input_fields"])}

## Forbidden Owner Input Fields

{_bullet_list(result["forbidden_owner_input_fields"])}

## Intake Result

- p6b_intake_status: `{result["p6b_intake_status"]}`
- owner_input_status: `{result["owner_input_status"]}`
- post_p6b_score: `{result["post_p6b_score"]}`
- demo_order_placement_authorized: `{result["demo_order_placement_authorized"]}`
- forbidden_fields_detected: `{result["forbidden_fields_detected"]}`
- failed_requirements: `{result["failed_requirements"]}`

## Next Required Lane

`{result["next_required_lane"]}`

## What This Completes

- creates the deterministic P6B intake result for sanitized owner input
- routes accepted sanitized input to P6C validation
- preserves demo-order placement, live-trading, broker/API, credential, money-movement, and autonomy blocks

## What This Does Not Approve

{_bullet_list(result["blocked_actions"])}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""


def render_next_action_queue(result: dict[str, Any]) -> str:
    """Render the next-action queue for the P6B intake gate."""

    if result["owner_input_status"] == "OWNER_INPUT_REQUIRED":
        next_actions = [
            "owner supplies sanitized demo-only snapshot fields",
            "owner supplies approve, reject, or request-changes decision",
            "rerun P6B intake outside Codex with sanitized input only",
        ]
    elif result["owner_input_status"] == "OWNER_INPUT_ACCEPTED":
        next_actions = ["run P6C owner snapshot approval validation gate"]
    else:
        next_actions = [
            "repair owner input so it matches the sanitized intake contract",
            "rerun P6B intake before P6C validation",
        ]

    remaining_blocks = [
        "demo-order placement remains blocked",
        "live trading remains blocked",
        "broker/API access remains blocked",
        "credentials remain blocked",
        "money movement remains blocked",
        "autonomous trading remains blocked",
    ]

    return f"""# AIOS Forex C1 Owner Supplied Snapshot Approval Intake Next Action Queue V1

## Purpose

This queue records the next action after the P6B C1 owner-supplied snapshot approval intake.

## P6B Intake Status

`{result["p6b_intake_status"]}`

## Owner Input Status

`{result["owner_input_status"]}`

## Passed Requirements

{_bullet_list([f"`{item}`" for item in result["passed_requirements"]])}

## Failed Requirements

{_bullet_list([f"`{item}`" for item in result["failed_requirements"]])}

## Next Required Lane

`{result["next_required_lane"]}`

## Next Actions

{_bullet_list(next_actions)}

## Remaining Blocks

{_bullet_list(remaining_blocks)}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""


__all__ = [
    "evaluate_c1_owner_supplied_snapshot_approval_intake",
    "render_owner_report",
    "render_next_action_queue",
]
