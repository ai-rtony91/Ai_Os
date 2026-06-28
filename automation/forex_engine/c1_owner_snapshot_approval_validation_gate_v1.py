"""Deterministic C1 owner snapshot approval validation gate.

This module validates sanitized owner input after P6B intake. It does not
access brokers, credentials, accounts, balances, prices, orders, schedulers,
daemons, webhooks, production systems, or trading execution paths.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from automation.forex_engine.c1_owner_supplied_snapshot_approval_intake_v1 import (
    evaluate_c1_owner_supplied_snapshot_approval_intake,
)


CAMPAIGN_ID = "AIOS-FOREX-P6C-C1-OWNER-SNAPSHOT-APPROVAL-VALIDATION-GATE-V1"
CANDIDATE_ID = "c1-eur-buy"
CANDIDATE_NAME = "paper_long_run_supervisor_v2 LONG EURUSD"

TRADER_MEANING = (
    "AIOS is validating whether the owner's sanitized snapshot and decision "
    "are safe, complete, and consistent enough to move into the final "
    "demo-order intent review card."
)

OWNER_INPUT_REQUIRED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P6C C1 validation is blocked until sanitized owner input is "
    "supplied through P6B; demo-order placement, live trading, broker/API, "
    "credentials, money movement, and autonomy remain blocked."
)

OWNER_APPROVED_VALIDATED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P6C C1 validation accepted the sanitized owner decision for "
    "P6D final review only; demo-order placement, live trading, broker/API, "
    "credentials, money movement, and autonomy remain blocked."
)

OWNER_REJECTED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P6C C1 validation recorded an owner reject decision and routes "
    "to closure; demo-order placement, live trading, broker/API, credentials, "
    "money movement, and autonomy remain blocked."
)

OWNER_REQUESTED_CHANGES_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P6C C1 validation recorded an owner request-changes decision "
    "and routes back to P6B repair; demo-order placement, live trading, "
    "broker/API, credentials, money movement, and autonomy remain blocked."
)

VALIDATION_FAILED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P6C C1 validation failed one or more safety or consistency "
    "checks and routes back to owner-input repair; demo-order placement, live "
    "trading, broker/API, credentials, money movement, and autonomy remain "
    "blocked."
)

VALIDATION_RULES = {
    "demo_account_marker": "DEMO_ONLY",
    "intended_instrument_confirmation": "EUR_USD",
    "intended_side_confirmation": "BUY",
    "current_open_position_count_max": 1,
    "current_same_signal_order_count_max": 1,
    "daily_realized_loss_percent_must_be_less_than": 1.0,
    "weekly_realized_loss_percent_must_be_less_than": 2.0,
    "kill_switch_state": "ARMED_UNTRIGGERED",
    "owner_attestation": True,
    "units_formula_review": True,
    "stop_loss_review": True,
    "take_profit_review": True,
    "reward_to_risk_review": True,
    "one_order_rule_verification": True,
    "daily_stop_verification": True,
    "weekly_stop_verification": True,
    "kill_switch_verification": True,
    "demo_order_placement_authorized": False,
}

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
    "claiming owner approval as supplied by automation",
    "claiming demo-order authority",
    "claiming live trading authority",
    "claiming 22/6 autonomy readiness",
    "claiming vacation/luxury mode as active",
    "claiming 100-120 percent return evidence",
]


def _safe_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _at_most(owner_input: dict[str, Any], field: str, limit: float) -> bool:
    value = _safe_float(owner_input.get(field))
    return value is not None and value <= limit and value >= 0


def _less_than(owner_input: dict[str, Any], field: str, limit: float) -> bool:
    value = _safe_float(owner_input.get(field))
    return value is not None and value < limit and value >= 0


def _is_true(owner_input: dict[str, Any], field: str) -> bool:
    return owner_input.get(field) is True


def _build_validation_checks(
    owner_input: dict[str, Any],
    p6b_result: dict[str, Any],
) -> dict[str, bool]:
    return {
        "p6b_intake_acceptance": (
            p6b_result.get("p6b_intake_status")
            == "P6B_OWNER_INPUT_ACCEPTED_FOR_P6C_VALIDATION"
        ),
        "demo_account_marker": owner_input.get("demo_account_marker")
        == "DEMO_ONLY",
        "intended_instrument_confirmation": owner_input.get(
            "intended_instrument_confirmation"
        )
        == "EUR_USD",
        "intended_side_confirmation": owner_input.get("intended_side_confirmation")
        == "BUY",
        "current_open_position_count": _at_most(
            owner_input,
            "current_open_position_count",
            1,
        ),
        "current_same_signal_order_count": _at_most(
            owner_input,
            "current_same_signal_order_count",
            1,
        ),
        "daily_realized_loss_percent": _less_than(
            owner_input,
            "daily_realized_loss_percent",
            1.0,
        ),
        "weekly_realized_loss_percent": _less_than(
            owner_input,
            "weekly_realized_loss_percent",
            2.0,
        ),
        "kill_switch_state": owner_input.get("kill_switch_state")
        == "ARMED_UNTRIGGERED",
        "owner_attestation": _is_true(owner_input, "owner_attestation"),
        "units_formula_review": _is_true(owner_input, "units_formula_review"),
        "stop_loss_review": _is_true(owner_input, "stop_loss_review"),
        "take_profit_review": _is_true(owner_input, "take_profit_review"),
        "reward_to_risk_review": _is_true(owner_input, "reward_to_risk_review"),
        "one_order_rule_verification": _is_true(
            owner_input,
            "one_order_rule_verification",
        ),
        "daily_stop_verification": _is_true(owner_input, "daily_stop_verification"),
        "weekly_stop_verification": _is_true(
            owner_input,
            "weekly_stop_verification",
        ),
        "kill_switch_verification": _is_true(
            owner_input,
            "kill_switch_verification",
        ),
        "forbidden_fields_absent": not p6b_result.get("forbidden_fields_detected"),
        "demo_order_placement_block": (
            p6b_result.get("demo_order_placement_authorized") is False
        ),
    }


def _bullet_list(items: list[str] | tuple[str, ...]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def _contract_lines(mapping: dict[str, Any]) -> str:
    rows = ["| field | value |", "|---|---|"]
    for key, value in mapping.items():
        rows.append(f"| `{key}` | `{value}` |")
    return "\n".join(rows)


def evaluate_c1_owner_snapshot_approval_validation_gate(
    owner_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the deterministic P6C owner decision validation result."""

    p6b_result = evaluate_c1_owner_supplied_snapshot_approval_intake(owner_input)

    if owner_input is None:
        p6c_validation_status = "P6C_VALIDATION_BLOCKED_OWNER_INPUT_REQUIRED"
        owner_decision_status = "OWNER_DECISION_NOT_SUPPLIED"
        next_required_lane = "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"
        post_p6c_score = 100
        failed_checks: list[str] = []
        validation_checks: dict[str, bool] = {}
        final_owner_sentence = OWNER_INPUT_REQUIRED_FINAL_OWNER_SENTENCE
    elif p6b_result.get("p6b_intake_status") != (
        "P6B_OWNER_INPUT_ACCEPTED_FOR_P6C_VALIDATION"
    ):
        p6c_validation_status = "P6C_VALIDATION_FAILED_REPAIR_REQUIRED"
        owner_decision_status = "NOT_READY"
        next_required_lane = "P6B_REPAIR_OWNER_INPUT"
        post_p6c_score = 80
        validation_checks = {}
        failed_checks = list(p6b_result.get("failed_requirements", [])) or [
            "p6b_intake_not_accepted"
        ]
        final_owner_sentence = VALIDATION_FAILED_FINAL_OWNER_SENTENCE
    else:
        owner_decision = owner_input.get("owner_decision")
        if owner_decision == "REJECT_DEMO_INTENT":
            p6c_validation_status = "P6C_OWNER_REJECTED_INTENT"
            owner_decision_status = "OWNER_REJECTED_INTENT"
            next_required_lane = "P6C_OWNER_REJECTION_CLOSURE_QUEUE"
            post_p6c_score = 100
            validation_checks = {}
            failed_checks = []
            final_owner_sentence = OWNER_REJECTED_FINAL_OWNER_SENTENCE
        elif owner_decision == "REQUEST_CHANGES":
            p6c_validation_status = "P6C_OWNER_REQUESTED_CHANGES"
            owner_decision_status = "OWNER_REQUESTED_CHANGES"
            next_required_lane = "P6B_REPAIR_OWNER_INPUT"
            post_p6c_score = 100
            validation_checks = {}
            failed_checks = []
            final_owner_sentence = OWNER_REQUESTED_CHANGES_FINAL_OWNER_SENTENCE
        else:
            validation_checks = _build_validation_checks(owner_input, p6b_result)
            failed_checks = [
                key for key, passed in validation_checks.items() if not passed
            ]
            if failed_checks:
                p6c_validation_status = "P6C_VALIDATION_FAILED_REPAIR_REQUIRED"
                owner_decision_status = "NOT_READY"
                next_required_lane = "P6B_REPAIR_OWNER_INPUT"
                post_p6c_score = 80
                final_owner_sentence = VALIDATION_FAILED_FINAL_OWNER_SENTENCE
            else:
                p6c_validation_status = (
                    "P6C_OWNER_APPROVAL_VALIDATED_FOR_P6D_FINAL_REVIEW"
                )
                owner_decision_status = "OWNER_APPROVED_INTENT_VALIDATED"
                next_required_lane = "P6D_DEMO_ORDER_INTENT_FINAL_REVIEW_CARD"
                post_p6c_score = 100
                final_owner_sentence = OWNER_APPROVED_VALIDATED_FINAL_OWNER_SENTENCE

    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "p6b_intake_status": p6b_result.get("p6b_intake_status"),
        "p6b_owner_input_status": p6b_result.get("owner_input_status"),
        "p6c_validation_status": p6c_validation_status,
        "owner_decision_status": owner_decision_status,
        "owner_decision": owner_input.get("owner_decision") if owner_input else None,
        "post_p6c_score": post_p6c_score,
        "next_required_lane": next_required_lane,
        "validation_rules": deepcopy(VALIDATION_RULES),
        "validation_checks": validation_checks,
        "failed_checks": failed_checks,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "demo_order_placement_authorized": False,
        "live_trading_blocked": True,
        "broker_api_access_blocked": True,
        "credential_access_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
        "trader_meaning": TRADER_MEANING,
        "final_owner_sentence": final_owner_sentence,
    }


def render_owner_report(result: dict[str, Any]) -> str:
    """Render the owner-facing P6C validation report."""

    return f"""# AIOS Forex C1 Owner Snapshot Approval Validation Gate V1 Report

## Campaign Scope

This report applies the P6C C1 owner snapshot approval validation gate for `c1-eur-buy` only. It consumes the P6B owner-supplied snapshot approval intake and validates sanitized owner input for final review routing.

This report does not collect secrets, read credentials, access accounts, access brokers, calculate live or account-specific position size, place demo orders, place live orders, close orders, move money, activate schedulers, activate daemons, activate webhooks, activate production, or authorize autonomous trading.

## Trader Meaning

{TRADER_MEANING}

## P6B Intake Status

- p6b_intake_status: `{result["p6b_intake_status"]}`
- p6b_owner_input_status: `{result["p6b_owner_input_status"]}`

## Validation Rules

{_contract_lines(result["validation_rules"])}

## Owner Decision Status

`{result["owner_decision_status"]}`

## Validation Result

- p6c_validation_status: `{result["p6c_validation_status"]}`
- post_p6c_score: `{result["post_p6c_score"]}`
- demo_order_placement_authorized: `{result["demo_order_placement_authorized"]}`

## Failed Checks

{_bullet_list([f"`{item}`" for item in result["failed_checks"]])}

## Next Required Lane

`{result["next_required_lane"]}`

## What This Completes

- validates sanitized owner input after P6B intake
- routes approved intent to P6D final review only when all P6C checks pass
- routes reject or request-changes decisions away from P7 rehearsal
- preserves demo-order placement, live-trading, broker/API, credential, money-movement, and autonomy blocks

## What This Does Not Approve

{_bullet_list(result["blocked_actions"])}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""


def render_next_action_queue(result: dict[str, Any]) -> str:
    """Render the next-action queue for the P6C validation gate."""

    if result["p6c_validation_status"] == (
        "P6C_OWNER_APPROVAL_VALIDATED_FOR_P6D_FINAL_REVIEW"
    ):
        next_actions = ["run P6D final demo-order intent review card"]
    elif result["p6c_validation_status"] == "P6C_OWNER_REJECTED_INTENT":
        next_actions = ["close the owner rejection queue for this candidate"]
    elif result["p6c_validation_status"] == "P6C_OWNER_REQUESTED_CHANGES":
        next_actions = ["repair owner input through P6B"]
    else:
        next_actions = [
            "supply or repair sanitized owner input",
            "rerun P6B intake before rerunning P6C validation",
        ]

    remaining_blocks = [
        "demo-order placement remains blocked",
        "live trading remains blocked",
        "broker/API access remains blocked",
        "credentials remain blocked",
        "money movement remains blocked",
        "autonomous trading remains blocked",
    ]

    return f"""# AIOS Forex C1 Owner Snapshot Approval Validation Gate Next Action Queue V1

## Purpose

This queue records the next action after the P6C C1 owner snapshot approval validation gate.

## P6C Validation Status

`{result["p6c_validation_status"]}`

## Owner Decision Status

`{result["owner_decision_status"]}`

## Failed Checks

{_bullet_list([f"`{item}`" for item in result["failed_checks"]])}

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
    "evaluate_c1_owner_snapshot_approval_validation_gate",
    "render_owner_report",
    "render_next_action_queue",
]
