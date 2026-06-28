"""Deterministic C1 owner snapshot and approval decision gate analyzer.

This module creates repo-local owner-input contract evidence only. It does not
access brokers, credentials, accounts, balances, prices, orders, schedulers,
daemons, webhooks, production systems, or trading execution paths.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from automation.forex_engine.c1_demo_order_intent_owner_approval_gate_v1 import (
    evaluate_c1_demo_order_intent_owner_approval_gate,
)


CAMPAIGN_ID = "AIOS-FOREX-P6A-C1-OWNER-SNAPSHOT-APPROVAL-DECISION-GATE-V1"
CANDIDATE_ID = "c1-eur-buy"
CANDIDATE_NAME = "paper_long_run_supervisor_v2 LONG EURUSD"

TRADER_MEANING = (
    "AIOS is defining exactly what the owner must supply next before a "
    "demo-order intent can be reviewed further: a sanitized account snapshot "
    "and an explicit approve, reject, or request-changes decision."
)

OWNER_INPUT_REQUIRED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P6A C1 owner snapshot and approval decision gate is complete: "
    "c1-eur-buy has an owner-input contract ready for sanitized snapshot and "
    "explicit approve, reject, or request-changes decision, while demo-order "
    "placement, live trading, broker/API, credentials, money movement, 22/6 "
    "autonomy, vacation/luxury mode, and 100-120 percent return claims remain "
    "blocked until separately proven and approved."
)

NOT_READY_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P6A C1 owner snapshot and approval decision gate is complete: "
    "c1-eur-buy is not ready for owner input, and the next required lane is P6 "
    "repair or P6A owner-input contract completion; demo-order placement, live "
    "trading, broker/API, credentials, money movement, 22/6 autonomy, "
    "vacation/luxury mode, and 100-120 percent return claims remain blocked "
    "until separately proven and approved."
)

P6A_GATE_STATUSES = {
    "P6A_OWNER_INPUT_CONTRACT_CREATED_INPUT_REQUIRED",
    "P6A_BLOCKED_P6_REPAIR_REQUIRED",
    "P6A_BLOCKED_OWNER_INPUT_CONTRACT_INCOMPLETE",
}

OWNER_INPUT_STATUSES = {"OWNER_INPUT_REQUIRED", "NOT_READY"}

NEXT_REQUIRED_LANES = {
    "P6B_OWNER_SUPPLIED_SNAPSHOT_APPROVAL_INTAKE",
    "P6A_CONTINUE_OWNER_INPUT_CONTRACT_REVIEW",
    "P6_DEMO_ORDER_INTENT_GATE_REPAIR_REVIEW",
}

POST_P6A_STATUSES = {
    "OWNER_INPUT_REQUIRED",
    "NEEDS_MORE_EVIDENCE",
    "REJECTED_P6_NOT_READY",
    "REJECTED_OWNER_INPUT_CONTRACT_INCOMPLETE",
    "REJECTED_DEMO_SAFETY_BOUNDARY",
}

ACCEPTED_OWNER_DECISIONS = [
    "APPROVE_DEMO_INTENT",
    "REJECT_DEMO_INTENT",
    "REQUEST_CHANGES",
]

REQUIRED_SNAPSHOT_FIELDS = [
    "demo_account_marker",
    "sanitized_equity_value_or_bracket",
    "current_open_position_count",
    "current_same_signal_order_count",
    "daily_realized_loss_percent",
    "weekly_realized_loss_percent",
    "kill_switch_state",
    "timestamp_utc",
    "owner_attestation",
]

FORBIDDEN_SNAPSHOT_FIELDS = [
    "API keys",
    "tokens",
    "passwords",
    "broker credentials",
    "account identifiers",
    "broker order identifiers",
    "raw live account data",
    "private execution payloads",
]

REQUIRED_APPROVAL_FIELDS = [
    "explicit_owner_decision",
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
    "owner_attestation",
    "audit_record",
]

REQUIRED_OWNER_INPUTS = [
    "sanitized broker/account snapshot",
    "explicit owner decision",
    "intended instrument confirmation",
    "intended side confirmation",
    "order type selection",
    "units formula review",
    "stop loss review",
    "take profit review",
    "reward-to-risk review",
    "one-order rule verification",
    "daily-stop verification",
    "weekly-stop verification",
    "kill-switch verification",
    "owner attestation",
]

REQUIRED_OWNER_INPUT_CONTRACT_FIELDS = [
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
]

PASSED_REQUIREMENTS = [
    "p6_entry_condition",
    "owner_input_contract_created",
    "owner_decision_required_not_supplied",
    "sanitized_snapshot_required_not_supplied",
    "accepted_owner_decisions_defined",
    "required_snapshot_fields_defined",
    "forbidden_snapshot_fields_defined",
    "required_approval_fields_defined",
    "demo_order_placement_block",
    "broker_api_credential_live_blocks",
    "money_movement_block",
    "no_autonomy_approval",
]

BLOCKED_ACTIONS = [
    "demo-order placement",
    "live trading",
    "broker/API access",
    "credential access",
    "account access",
    "order placement",
    "order closure",
    "money movement",
    "scheduler activation",
    "daemon activation",
    "webhook activation",
    "production activation",
    "autonomous trading",
    "claiming owner approval has been granted",
    "claiming demo-order placement authority",
    "claiming live trading authority",
    "claiming 22/6 autonomy readiness",
    "claiming vacation/luxury mode as active",
    "claiming 100-120 percent return as verified",
]

SOURCE_EVIDENCE = [
    {
        "path": "automation/forex_engine/c1_demo_order_intent_owner_approval_gate_v1.py",
        "use": "Provides the authoritative P6 review-only demo-order intent owner gate consumed by this P6A contract gate.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_DEMO_ORDER_INTENT_OWNER_APPROVAL_GATE_V1.json",
        "use": "Records P6 gate status, owner action status, score, blocks, and next lane.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_DEMO_ORDER_INTENT_OWNER_APPROVAL_GATE_V1_REPORT.md",
        "use": "Explains the P6 source-backed owner action requirement and preserves safety boundaries.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_DEMO_ORDER_INTENT_OWNER_APPROVAL_GATE_NEXT_ACTION_QUEUE_V1.md",
        "use": "Routes the candidate into P6A owner-supplied snapshot and approval decision work.",
    },
    {
        "path": "RISK_POLICY.md",
        "use": "Defines the root safety boundary for trading, credentials, broker access, order action, and fail-closed behavior.",
    },
]


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _build_p6a_entry_assessment(
    p6_result: dict[str, Any],
) -> dict[str, Any]:
    p6_card = p6_result.get("demo_order_intent_card", {})
    p6_owner = p6_result.get("owner_approval_requirement", {})
    p6_snapshot = p6_result.get("sanitized_snapshot_requirement", {})
    p6_pre_order = p6_result.get("pre_order_safety_checks", {})
    checks = {
        "p6_gate_status": (
            p6_result.get("p6_gate_status")
            == "P6_DEMO_ORDER_INTENT_GATE_CREATED_OWNER_ACTION_REQUIRED"
        ),
        "p6_owner_action_status": (
            p6_result.get("owner_action_status") == "OWNER_ACTION_REQUIRED"
        ),
        "post_p6_score": _safe_int(p6_result.get("post_p6_score")) == 100,
        "next_required_lane": (
            p6_result.get("next_required_lane")
            == "P6A_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_DECISION"
        ),
        "demo_order_placement_blocked": (
            p6_card.get("demo_order_placement_authorized") is False
            and p6_pre_order.get("demo_order_placement_authorized") is False
        ),
        "owner_approval_required": (
            p6_owner.get("owner_approval_required") is True
        ),
        "owner_approval_not_supplied_by_p6": (
            p6_owner.get("approved_by_this_packet") is False
            and p6_owner.get("approval_granted") is False
        ),
        "sanitized_snapshot_required": (
            p6_snapshot.get("requires_sanitized_broker_account_snapshot") is True
            or p6_snapshot.get("sanitized_broker_account_snapshot_required") is True
        ),
        "sanitized_snapshot_not_supplied_by_p6": (
            p6_snapshot.get("collected_in_this_packet") is False
        ),
        "broker_api_blocked": (
            p6_card.get("broker_api_access_blocked") is True
            and p6_pre_order.get("broker_api_access_blocked") is True
        ),
        "credential_access_blocked": (
            p6_card.get("credential_access_blocked") is True
            and p6_pre_order.get("credential_access_blocked") is True
        ),
        "live_trading_blocked": (
            p6_card.get("live_trading_blocked") is True
            and p6_pre_order.get("live_trading_blocked") is True
        ),
        "money_movement_blocked": (
            p6_card.get("money_movement_blocked") is True
            and p6_pre_order.get("money_movement_blocked") is True
        ),
        "no_autonomy_approval": (
            p6_card.get("no_autonomy_approval") is True
            and p6_pre_order.get("no_autonomy_approval") is True
        ),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "observed": {
            "p6_gate_status": p6_result.get("p6_gate_status"),
            "p6_owner_action_status": p6_result.get("owner_action_status"),
            "post_p6_score": p6_result.get("post_p6_score"),
            "next_required_lane": p6_result.get("next_required_lane"),
            "demo_order_placement_authorized": p6_card.get(
                "demo_order_placement_authorized"
            ),
            "owner_approval_required": p6_owner.get("owner_approval_required"),
            "owner_approval_status": p6_owner.get("owner_approval_status"),
            "owner_approval_approved_by_p6": p6_owner.get(
                "approved_by_this_packet"
            ),
            "sanitized_snapshot_required": p6_snapshot.get(
                "requires_sanitized_broker_account_snapshot"
            ),
            "sanitized_snapshot_status": p6_snapshot.get("status"),
            "broker_api_access_blocked": p6_pre_order.get(
                "broker_api_access_blocked"
            ),
            "credential_access_blocked": p6_pre_order.get(
                "credential_access_blocked"
            ),
            "live_trading_blocked": p6_pre_order.get("live_trading_blocked"),
            "money_movement_blocked": p6_pre_order.get(
                "money_movement_blocked"
            ),
            "no_autonomy_approval": p6_pre_order.get("no_autonomy_approval"),
        },
    }


def _build_owner_input_contract() -> dict[str, Any]:
    return {
        "owner_decision_required": True,
        "accepted_owner_decisions": list(ACCEPTED_OWNER_DECISIONS),
        "sanitized_snapshot_required": True,
        "required_snapshot_fields": list(REQUIRED_SNAPSHOT_FIELDS),
        "forbidden_snapshot_fields": list(FORBIDDEN_SNAPSHOT_FIELDS),
        "required_approval_fields": list(REQUIRED_APPROVAL_FIELDS),
        "intended_instrument_confirmation": {
            "required": True,
            "expected_value": "EUR_USD",
        },
        "intended_side_confirmation": {
            "required": True,
            "expected_value": "BUY",
        },
        "order_type_selection_required": True,
        "units_formula_review_required": True,
        "stop_loss_review_required": True,
        "take_profit_review_required": True,
        "reward_to_risk_review_required": True,
        "one_order_rule_verification_required": True,
        "daily_stop_verification_required": True,
        "weekly_stop_verification_required": True,
        "kill_switch_verification_required": True,
        "audit_record_required": True,
        "demo_order_placement_authorized": False,
        "live_trading_blocked": True,
        "broker_api_access_blocked": True,
        "credential_access_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
    }


def _build_sanitized_snapshot_contract() -> dict[str, Any]:
    return {
        "sanitized_snapshot_required": True,
        "sanitized_snapshot_status": "SNAPSHOT_NOT_SUPPLIED",
        "provided_by_this_packet": False,
        "required_snapshot_fields": list(REQUIRED_SNAPSHOT_FIELDS),
        "forbidden_snapshot_fields": list(FORBIDDEN_SNAPSHOT_FIELDS),
        "purpose": (
            "Provide enough demo-account state for owner review without "
            "secrets, credentials, account identifiers, broker order "
            "identifiers, raw live account data, or private execution payloads."
        ),
        "demo_order_placement_authorized": False,
        "broker_api_access_blocked": True,
        "credential_access_blocked": True,
        "live_trading_blocked": True,
    }


def _build_owner_approval_decision_contract() -> dict[str, Any]:
    return {
        "owner_decision_required": True,
        "owner_decision_status": "OWNER_DECISION_NOT_SUPPLIED",
        "accepted_owner_decisions": list(ACCEPTED_OWNER_DECISIONS),
        "required_approval_fields": list(REQUIRED_APPROVAL_FIELDS),
        "provided_by_this_packet": False,
        "decision_scope": (
            "Owner review of the P6 demo-order intent only; no demo or live "
            "order authority is created by this packet."
        ),
        "demo_order_placement_authorized": False,
        "live_trading_blocked": True,
        "broker_api_access_blocked": True,
        "credential_access_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
    }


def _build_validation_rules() -> dict[str, Any]:
    return {
        "owner_decision_must_be_one_of": list(ACCEPTED_OWNER_DECISIONS),
        "snapshot_must_include": list(REQUIRED_SNAPSHOT_FIELDS),
        "snapshot_must_exclude": list(FORBIDDEN_SNAPSHOT_FIELDS),
        "owner_decision_required_but_not_supplied_by_p6a": True,
        "sanitized_snapshot_required_but_not_supplied_by_p6a": True,
        "intended_instrument_must_match": "EUR_USD",
        "intended_side_must_match": "BUY",
        "order_type_selection_required": True,
        "units_formula_review_required": True,
        "stop_loss_review_required": True,
        "take_profit_review_required": True,
        "reward_to_risk_review_required": True,
        "one_order_rule_verification_required": True,
        "daily_stop_verification_required": True,
        "weekly_stop_verification_required": True,
        "kill_switch_verification_required": True,
        "audit_record_required": True,
        "demo_order_placement_authorized": False,
        "live_trading_blocked": True,
        "broker_api_access_blocked": True,
        "credential_access_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
    }


def _owner_input_contract_failures(
    owner_input_contract: dict[str, Any],
    sanitized_snapshot_contract: dict[str, Any],
    owner_approval_decision_contract: dict[str, Any],
    validation_rules: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    missing_fields = [
        field
        for field in REQUIRED_OWNER_INPUT_CONTRACT_FIELDS
        if field not in owner_input_contract
    ]
    if missing_fields:
        failures.append("owner_input_contract_fields")
    if owner_input_contract.get("accepted_owner_decisions") != ACCEPTED_OWNER_DECISIONS:
        failures.append("accepted_owner_decisions")
    if owner_input_contract.get("required_snapshot_fields") != REQUIRED_SNAPSHOT_FIELDS:
        failures.append("required_snapshot_fields")
    if (
        owner_input_contract.get("forbidden_snapshot_fields")
        != FORBIDDEN_SNAPSHOT_FIELDS
    ):
        failures.append("forbidden_snapshot_fields")
    if sanitized_snapshot_contract.get("provided_by_this_packet") is not False:
        failures.append("sanitized_snapshot_not_supplied")
    if (
        owner_approval_decision_contract.get("owner_decision_status")
        != "OWNER_DECISION_NOT_SUPPLIED"
    ):
        failures.append("owner_decision_not_supplied")
    if validation_rules.get("demo_order_placement_authorized") is not False:
        failures.append("demo_order_placement_block")
    for key in (
        "live_trading_blocked",
        "broker_api_access_blocked",
        "credential_access_blocked",
        "money_movement_blocked",
        "no_autonomy_approval",
    ):
        if validation_rules.get(key) is not True:
            failures.append(key)
    return failures


def _bullet_list(items: list[str] | tuple[str, ...]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def _source_list(result: dict[str, Any]) -> str:
    return "\n".join(
        f"- `{source['path']}`: {source['use']}" for source in result["source_evidence"]
    )


def _dict_lines(mapping: dict[str, Any]) -> str:
    return "\n".join(f"- {key}: `{value}`" for key, value in mapping.items())


def _contract_lines(mapping: dict[str, Any]) -> str:
    rows = ["| field | value |", "|---|---|"]
    for key, value in mapping.items():
        rows.append(f"| `{key}` | `{value}` |")
    return "\n".join(rows)


def evaluate_c1_owner_snapshot_approval_decision_gate() -> dict[str, Any]:
    """Return the source-backed C1 P6A owner-input gate decision."""

    p6_result = evaluate_c1_demo_order_intent_owner_approval_gate()
    input_score = _safe_int(p6_result.get("post_p6_score"))
    input_status = str(
        p6_result.get("post_p6_status", p6_result.get("owner_action_status", ""))
    )
    p6a_entry_assessment = _build_p6a_entry_assessment(p6_result)
    owner_input_contract = _build_owner_input_contract()
    sanitized_snapshot_contract = _build_sanitized_snapshot_contract()
    owner_approval_decision_contract = _build_owner_approval_decision_contract()
    validation_rules = _build_validation_rules()
    contract_failures = _owner_input_contract_failures(
        owner_input_contract,
        sanitized_snapshot_contract,
        owner_approval_decision_contract,
        validation_rules,
    )

    if not p6a_entry_assessment["passed"]:
        p6a_gate_status = "P6A_BLOCKED_P6_REPAIR_REQUIRED"
        owner_input_status = "NOT_READY"
        next_required_lane = "P6_DEMO_ORDER_INTENT_GATE_REPAIR_REVIEW"
        post_p6a_score = min(input_score, 85)
        post_p6a_status = "REJECTED_P6_NOT_READY"
        failed_requirements = [
            key
            for key, passed in p6a_entry_assessment["checks"].items()
            if not passed
        ]
        passed_requirements: list[str] = []
        final_owner_sentence = NOT_READY_FINAL_OWNER_SENTENCE
    elif contract_failures:
        p6a_gate_status = "P6A_BLOCKED_OWNER_INPUT_CONTRACT_INCOMPLETE"
        owner_input_status = "NOT_READY"
        next_required_lane = "P6A_CONTINUE_OWNER_INPUT_CONTRACT_REVIEW"
        post_p6a_score = min(input_score, 90)
        post_p6a_status = "REJECTED_OWNER_INPUT_CONTRACT_INCOMPLETE"
        failed_requirements = contract_failures
        passed_requirements = [
            requirement
            for requirement in PASSED_REQUIREMENTS
            if requirement not in contract_failures
        ]
        final_owner_sentence = NOT_READY_FINAL_OWNER_SENTENCE
    else:
        p6a_gate_status = "P6A_OWNER_INPUT_CONTRACT_CREATED_INPUT_REQUIRED"
        owner_input_status = "OWNER_INPUT_REQUIRED"
        next_required_lane = "P6B_OWNER_SUPPLIED_SNAPSHOT_APPROVAL_INTAKE"
        post_p6a_score = 100
        post_p6a_status = "OWNER_INPUT_REQUIRED"
        failed_requirements = []
        passed_requirements = list(PASSED_REQUIREMENTS)
        final_owner_sentence = OWNER_INPUT_REQUIRED_FINAL_OWNER_SENTENCE

    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": input_score,
        "post_p6a_score": post_p6a_score,
        "input_status": input_status,
        "post_p6a_status": post_p6a_status,
        "p6_gate_status": p6_result.get("p6_gate_status"),
        "p6_owner_action_status": p6_result.get("owner_action_status"),
        "p6a_gate_status": p6a_gate_status,
        "owner_input_status": owner_input_status,
        "owner_decision_status": owner_approval_decision_contract[
            "owner_decision_status"
        ],
        "sanitized_snapshot_status": sanitized_snapshot_contract[
            "sanitized_snapshot_status"
        ],
        "next_required_lane": next_required_lane,
        "p6a_entry_assessment": deepcopy(p6a_entry_assessment),
        "owner_input_contract": deepcopy(owner_input_contract),
        "sanitized_snapshot_contract": deepcopy(sanitized_snapshot_contract),
        "owner_approval_decision_contract": deepcopy(
            owner_approval_decision_contract
        ),
        "validation_rules": deepcopy(validation_rules),
        "required_owner_inputs": list(REQUIRED_OWNER_INPUTS),
        "accepted_owner_decisions": list(ACCEPTED_OWNER_DECISIONS),
        "blocked_actions": list(BLOCKED_ACTIONS),
        "forbidden_actions": list(BLOCKED_ACTIONS),
        "passed_requirements": passed_requirements,
        "failed_requirements": failed_requirements,
        "demo_order_placement_authorized": False,
        "live_trading_blocked": True,
        "broker_api_access_blocked": True,
        "credential_access_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
        "source_evidence": deepcopy(SOURCE_EVIDENCE),
        "trader_meaning": TRADER_MEANING,
        "final_owner_sentence": final_owner_sentence,
    }


def render_owner_report(result: dict[str, Any]) -> str:
    """Render the owner-facing P6A owner-input contract report."""

    owner_contract = result["owner_input_contract"]
    snapshot_contract = result["sanitized_snapshot_contract"]
    decision_contract = result["owner_approval_decision_contract"]
    validation_rules = result["validation_rules"]

    return f"""# AIOS Forex C1 Owner Snapshot Approval Decision Gate V1 Report

## Campaign Scope

This report applies the P6A C1 owner snapshot and approval decision gate for `c1-eur-buy` only. It consumes the P6 review-only demo-order intent owner gate and creates the deterministic owner-input contract for the next lane.

This report does not collect account data, read credentials, access brokers, calculate live or account-specific position size, place demo orders, place live orders, close orders, move money, activate schedulers, activate daemons, activate webhooks, activate production, approve autonomous trading, or approve any demo-order placement.

## Trader Meaning

{TRADER_MEANING}

## Source Evidence

{_source_list(result)}

## P6 Entry Condition

- p6_gate_status: `{result["p6_gate_status"]}`
- p6_owner_action_status: `{result["p6_owner_action_status"]}`
- input_score: `{result["input_score"]}`
- input_status: `{result["input_status"]}`
- p6a_entry_passed: `{result["p6a_entry_assessment"]["passed"]}`

{_dict_lines(result["p6a_entry_assessment"]["checks"])}

## Owner Input Contract

{_contract_lines(owner_contract)}

## Sanitized Snapshot Contract

{_contract_lines(snapshot_contract)}

## Owner Approval Decision Contract

{_contract_lines(decision_contract)}

## Validation Rules

{_contract_lines(validation_rules)}

## Required Owner Inputs

{_bullet_list(result["required_owner_inputs"])}

## Accepted Owner Decisions

{_bullet_list(result["accepted_owner_decisions"])}

## Blocked Actions

{_bullet_list(result["blocked_actions"])}

## Owner Input Status

`{result["owner_input_status"]}`

## Next Required Lane

`{result["next_required_lane"]}`

## What This Completes

- creates the P6A owner-input contract for `c1-eur-buy`
- defines sanitized snapshot fields, forbidden snapshot fields, accepted owner decisions, approval fields, and validation rules
- preserves the demo-order placement, live-trading, broker/API, credential, money-movement, and autonomy blocks

## What This Does Not Approve

{_bullet_list(result["forbidden_actions"])}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""


def render_next_action_queue(result: dict[str, Any]) -> str:
    """Render the next-action queue for the P6A owner-input gate."""

    if result["owner_input_status"] == "OWNER_INPUT_REQUIRED":
        required_owner_inputs = list(REQUIRED_OWNER_INPUTS)
    else:
        required_owner_inputs = [
            "repair P6 owner-gate evidence or complete the P6A owner-input contract",
            "rerun this P6A gate after repair",
        ]

    remaining_blocks = [
        "demo-order placement remains blocked",
        "live trading remains blocked",
        "broker/API access remains blocked",
        "credentials remain blocked",
        "money movement remains blocked",
        "autonomous trading remains blocked",
    ]

    return f"""# AIOS Forex C1 Owner Snapshot Approval Decision Gate Next Action Queue V1

## Purpose

This queue records the owner input required after P6A C1 owner snapshot and approval decision gate creation.

## P6A Gate Status

`{result["p6a_gate_status"]}`

## Owner Input Status

`{result["owner_input_status"]}`

## Passed Requirements

{_bullet_list([f"`{item}`" for item in result["passed_requirements"]])}

## Failed Requirements

{_bullet_list([f"`{item}`" for item in result["failed_requirements"]])}

## Next Required Lane

`{result["next_required_lane"]}`

## Required Owner Inputs

{_bullet_list(required_owner_inputs)}

## Accepted Owner Decisions

{_bullet_list(result["accepted_owner_decisions"])}

## Remaining Blocks

{_bullet_list(remaining_blocks)}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""


__all__ = [
    "evaluate_c1_owner_snapshot_approval_decision_gate",
    "render_owner_report",
    "render_next_action_queue",
]
