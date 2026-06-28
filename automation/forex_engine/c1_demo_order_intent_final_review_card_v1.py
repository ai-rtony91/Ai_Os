"""Deterministic C1 demo-order intent final review card gate.

This module creates final review-card evidence only after sanitized owner input
passes P6C validation. It does not access brokers, credentials, accounts,
balances, prices, orders, schedulers, daemons, webhooks, production systems, or
trading execution paths.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from automation.forex_engine.c1_owner_snapshot_approval_validation_gate_v1 import (
    evaluate_c1_owner_snapshot_approval_validation_gate,
)


CAMPAIGN_ID = "AIOS-FOREX-P6D-C1-DEMO-ORDER-INTENT-FINAL-REVIEW-CARD-V1"
CANDIDATE_ID = "c1-eur-buy"
CANDIDATE_NAME = "paper_long_run_supervisor_v2 LONG EURUSD"

TRADER_MEANING = (
    "AIOS is preparing the final review-only demo-order intent card for the "
    "EUR/USD buy setup, readying it for mock/dry-run rehearsal only after "
    "owner input validates cleanly."
)

OWNER_INPUT_REQUIRED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P6D C1 final review card is blocked until sanitized owner "
    "input validates through P6C; demo-order placement, live trading, "
    "broker/API, credentials, money movement, and autonomy remain blocked."
)

FINAL_REVIEW_READY_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P6D C1 final review card is ready for P7 mock/dry-run "
    "rehearsal routing; demo-order placement, live trading, broker/API, "
    "credentials, money movement, and autonomy remain blocked."
)

FINAL_REVIEW_BLOCKED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P6D C1 final review card remains blocked because P6C did not "
    "validate an approve-intent path; demo-order placement, live trading, "
    "broker/API, credentials, money movement, and autonomy remain blocked."
)

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


def _build_final_review_card(owner_input: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "intended_instrument": "EUR_USD",
        "intended_side": "BUY",
        "owner_decision": "APPROVE_DEMO_INTENT",
        "order_type_selection": owner_input.get("order_type_selection"),
        "units_formula": "units = risk_amount / stop_loss_value_per_unit",
        "max_risk_per_trade_percent": 0.25,
        "max_daily_loss_percent": 1.00,
        "max_weekly_loss_percent": 2.00,
        "max_open_positions": 1,
        "max_orders_per_signal": 1,
        "stop_loss_required": True,
        "take_profit_required": True,
        "minimum_reward_to_risk": 1.20,
        "one_order_rule_verified": True,
        "daily_stop_verified": True,
        "weekly_stop_verified": True,
        "kill_switch_verified": True,
        "audit_record_required": True,
        "demo_order_placement_authorized": False,
        "live_trading_blocked": True,
        "broker_api_access_blocked": True,
        "credential_access_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
    }


def _risk_limits(card: dict[str, Any]) -> dict[str, Any]:
    if not card:
        return {
            "max_risk_per_trade_percent": 0.25,
            "max_daily_loss_percent": 1.00,
            "max_weekly_loss_percent": 2.00,
            "max_open_positions": 1,
            "max_orders_per_signal": 1,
            "minimum_reward_to_risk": 1.20,
        }
    return {
        "max_risk_per_trade_percent": card["max_risk_per_trade_percent"],
        "max_daily_loss_percent": card["max_daily_loss_percent"],
        "max_weekly_loss_percent": card["max_weekly_loss_percent"],
        "max_open_positions": card["max_open_positions"],
        "max_orders_per_signal": card["max_orders_per_signal"],
        "minimum_reward_to_risk": card["minimum_reward_to_risk"],
    }


def _safety_verifications(card: dict[str, Any]) -> dict[str, Any]:
    if not card:
        return {
            "stop_loss_required": True,
            "take_profit_required": True,
            "one_order_rule_verified": False,
            "daily_stop_verified": False,
            "weekly_stop_verified": False,
            "kill_switch_verified": False,
            "audit_record_required": True,
        }
    return {
        "stop_loss_required": card["stop_loss_required"],
        "take_profit_required": card["take_profit_required"],
        "one_order_rule_verified": card["one_order_rule_verified"],
        "daily_stop_verified": card["daily_stop_verified"],
        "weekly_stop_verified": card["weekly_stop_verified"],
        "kill_switch_verified": card["kill_switch_verified"],
        "audit_record_required": card["audit_record_required"],
    }


def _bullet_list(items: list[str] | tuple[str, ...]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def _contract_lines(mapping: dict[str, Any]) -> str:
    if not mapping:
        return "- final review card is blocked until owner input validates through P6C"
    rows = ["| field | value |", "|---|---|"]
    for key, value in mapping.items():
        rows.append(f"| `{key}` | `{value}` |")
    return "\n".join(rows)


def _route_after_p6c(p6c_result: dict[str, Any]) -> str:
    status = p6c_result.get("p6c_validation_status")
    if status == "P6C_OWNER_REJECTED_INTENT":
        return "P6C_OWNER_REJECTION_CLOSURE_QUEUE"
    if status == "P6C_OWNER_REQUESTED_CHANGES":
        return "P6B_REPAIR_OWNER_INPUT"
    if status == "P6C_VALIDATION_FAILED_REPAIR_REQUIRED":
        return "P6B_REPAIR_OWNER_INPUT"
    return "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"


def evaluate_c1_demo_order_intent_final_review_card(
    owner_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the deterministic P6D final review-card result."""

    p6c_result = evaluate_c1_owner_snapshot_approval_validation_gate(owner_input)

    if owner_input is None:
        final_review_card: dict[str, Any] = {}
        p6d_final_review_status = "P6D_FINAL_REVIEW_BLOCKED_OWNER_INPUT_REQUIRED"
        final_review_status = "NOT_READY"
        next_required_lane = "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"
        post_p6d_score = 100
        final_owner_sentence = OWNER_INPUT_REQUIRED_FINAL_OWNER_SENTENCE
    elif p6c_result.get("p6c_validation_status") == (
        "P6C_OWNER_APPROVAL_VALIDATED_FOR_P6D_FINAL_REVIEW"
    ):
        final_review_card = _build_final_review_card(owner_input)
        p6d_final_review_status = (
            "P6D_FINAL_REVIEW_CARD_READY_FOR_P7_DRY_RUN_REHEARSAL"
        )
        final_review_status = "P7_DRY_RUN_REHEARSAL_READY"
        next_required_lane = "P7_DRY_RUN_MOCK_EXECUTION_REHEARSAL"
        post_p6d_score = 100
        final_owner_sentence = FINAL_REVIEW_READY_FINAL_OWNER_SENTENCE
    else:
        final_review_card = {}
        p6d_final_review_status = "P6D_FINAL_REVIEW_BLOCKED_P6C_NOT_VALIDATED"
        final_review_status = "NOT_READY"
        next_required_lane = _route_after_p6c(p6c_result)
        post_p6d_score = 80
        final_owner_sentence = FINAL_REVIEW_BLOCKED_FINAL_OWNER_SENTENCE

    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "p6c_validation_status": p6c_result.get("p6c_validation_status"),
        "p6c_owner_decision_status": p6c_result.get("owner_decision_status"),
        "p6d_final_review_status": p6d_final_review_status,
        "final_review_status": final_review_status,
        "post_p6d_score": post_p6d_score,
        "next_required_lane": next_required_lane,
        "final_review_card": deepcopy(final_review_card),
        "risk_limits": _risk_limits(final_review_card),
        "safety_verifications": _safety_verifications(final_review_card),
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
    """Render the owner-facing P6D final review-card report."""

    return f"""# AIOS Forex C1 Demo Order Intent Final Review Card V1 Report

## Campaign Scope

This report applies the P6D C1 demo-order intent final review card for `c1-eur-buy` only. It consumes the P6C owner snapshot approval validation gate and creates review-only evidence for later mock/dry-run rehearsal routing.

This report does not collect secrets, read credentials, access accounts, access brokers, calculate live or account-specific position size, place demo orders, place live orders, close orders, move money, activate schedulers, activate daemons, activate webhooks, activate production, or authorize autonomous trading.

## Trader Meaning

{TRADER_MEANING}

## P6C Validation Status

- p6c_validation_status: `{result["p6c_validation_status"]}`
- p6c_owner_decision_status: `{result["p6c_owner_decision_status"]}`

## Final Demo Intent Review Card

{_contract_lines(result["final_review_card"])}

## Risk Limits

{_contract_lines(result["risk_limits"])}

## Safety Verifications

{_contract_lines(result["safety_verifications"])}

## Blocked Actions

{_bullet_list(result["blocked_actions"])}

## Final Review Status

- p6d_final_review_status: `{result["p6d_final_review_status"]}`
- final_review_status: `{result["final_review_status"]}`
- post_p6d_score: `{result["post_p6d_score"]}`
- demo_order_placement_authorized: `{result["demo_order_placement_authorized"]}`

## Next Required Lane

`{result["next_required_lane"]}`

## What This Completes

- creates the deterministic P6D final review-card gate
- routes only validated approve-intent input to P7 mock/dry-run rehearsal
- keeps demo-order placement, live-trading, broker/API, credential, money-movement, and autonomy blocks active

## What This Does Not Approve

{_bullet_list(result["blocked_actions"])}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""


def render_next_action_queue(result: dict[str, Any]) -> str:
    """Render the next-action queue for the P6D final review-card gate."""

    if result["p6d_final_review_status"] == (
        "P6D_FINAL_REVIEW_CARD_READY_FOR_P7_DRY_RUN_REHEARSAL"
    ):
        next_actions = ["run P7 dry-run mock execution rehearsal"]
    else:
        next_actions = [
            "supply or repair sanitized owner input through P6B",
            "rerun P6C validation before rerunning P6D final review",
        ]

    remaining_blocks = [
        "demo-order placement remains blocked",
        "live trading remains blocked",
        "broker/API access remains blocked",
        "credentials remain blocked",
        "money movement remains blocked",
        "autonomous trading remains blocked",
    ]

    return f"""# AIOS Forex C1 Demo Order Intent Final Review Card Next Action Queue V1

## Purpose

This queue records the next action after the P6D C1 demo-order intent final review card gate.

## P6D Final Review Status

`{result["p6d_final_review_status"]}`

## Final Review Status

`{result["final_review_status"]}`

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
    "evaluate_c1_demo_order_intent_final_review_card",
    "render_owner_report",
    "render_next_action_queue",
]
