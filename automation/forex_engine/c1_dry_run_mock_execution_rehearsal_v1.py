"""Deterministic C1 dry-run mock execution rehearsal gate.

This module consumes the P6D final review card and creates inert local
rehearsal evidence only. It does not access brokers, credentials, accounts,
balances, prices, orders, schedulers, daemons, webhooks, production systems, or
trading execution paths.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from automation.forex_engine.c1_demo_order_intent_final_review_card_v1 import (
    evaluate_c1_demo_order_intent_final_review_card,
)


CAMPAIGN_ID = "AIOS-FOREX-P7-C1-DRY-RUN-MOCK-EXECUTION-REHEARSAL-V1"
CANDIDATE_ID = "c1-eur-buy"
CANDIDATE_NAME = "paper_long_run_supervisor_v2 LONG EURUSD"

TRADER_MEANING = (
    "AIOS is rehearsing the EUR/USD buy setup as an inert local mock order "
    "plan so it can verify safety checks before any supervised demo "
    "broker/account readiness bridge is considered."
)

OWNER_INPUT_REQUIRED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P7 C1 dry-run/mock execution rehearsal is waiting for "
    "validated owner input through P6B, P6C, and P6D; no demo order is "
    "authorized, and broker/API, credentials, live trading, money movement, "
    "and autonomy remain blocked."
)

P8_READY_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P7 C1 dry-run/mock execution rehearsal passed for P8 review "
    "using an inert local mock order plan; demo-order placement, live trading, "
    "broker/API, credentials, money movement, and autonomy remain blocked."
)

P6D_REPAIR_REQUIRED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P7 C1 dry-run/mock execution rehearsal is blocked because P6D "
    "is not ready for rehearsal; demo-order placement, live trading, "
    "broker/API, credentials, money movement, and autonomy remain blocked."
)

P7_REPAIR_REQUIRED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P7 C1 dry-run/mock execution rehearsal failed a local safety "
    "check and must be repaired before P8 review; demo-order placement, live "
    "trading, broker/API, credentials, money movement, and autonomy remain "
    "blocked."
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

FORBIDDEN_ACTIONS = [
    "broker/API access",
    "credential access",
    "account access",
    "demo-order placement",
    "live trading",
    "order-placement execution",
    "order closure",
    "money movement",
    "scheduler activation",
    "daemon activation",
    "webhook activation",
    "production activation",
    "autonomous trading",
]

REHEARSAL_CHECK_NAMES = [
    "p6d_final_review_ready",
    "mock_order_plan_created",
    "instrument_is_eur_usd",
    "side_is_buy",
    "order_type_selected",
    "units_formula_only",
    "max_risk_per_trade_percent",
    "max_daily_loss_percent",
    "max_weekly_loss_percent",
    "max_open_positions",
    "max_orders_per_signal",
    "stop_loss_required",
    "take_profit_required",
    "minimum_reward_to_risk",
    "one_order_rule_verified",
    "daily_stop_verified",
    "weekly_stop_verified",
    "kill_switch_verified",
    "audit_record_required",
    "demo_order_placement_authorized",
    "broker_api_access_blocked",
    "credential_access_blocked",
    "live_trading_blocked",
    "money_movement_blocked",
    "no_autonomy_approval",
]


def _empty_rehearsal_checks() -> dict[str, bool]:
    return {name: False for name in REHEARSAL_CHECK_NAMES}


def _build_mock_order_plan(final_review_card: dict[str, Any]) -> dict[str, Any]:
    return {
        "mock_order_plan_type": "INERT_LOCAL_REHEARSAL_ONLY",
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "instrument": "EUR_USD",
        "side": "BUY",
        "order_type_selection": final_review_card.get("order_type_selection"),
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
        "broker_api_access_blocked": True,
        "credential_access_blocked": True,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "demo_order_placement_authorized": False,
        "no_autonomy_approval": True,
    }


def _evaluate_rehearsal_checks(
    p6d_result: dict[str, Any],
    mock_order_plan: dict[str, Any],
) -> dict[str, bool]:
    return {
        "p6d_final_review_ready": p6d_result.get("p6d_final_review_status")
        == "P6D_FINAL_REVIEW_CARD_READY_FOR_P7_DRY_RUN_REHEARSAL",
        "mock_order_plan_created": bool(mock_order_plan),
        "instrument_is_eur_usd": mock_order_plan.get("instrument") == "EUR_USD",
        "side_is_buy": mock_order_plan.get("side") == "BUY",
        "order_type_selected": bool(mock_order_plan.get("order_type_selection")),
        "units_formula_only": mock_order_plan.get("units_formula")
        == "units = risk_amount / stop_loss_value_per_unit",
        "max_risk_per_trade_percent": (
            mock_order_plan.get("max_risk_per_trade_percent", 999) <= 0.25
        ),
        "max_daily_loss_percent": (
            mock_order_plan.get("max_daily_loss_percent", 999) <= 1.00
        ),
        "max_weekly_loss_percent": (
            mock_order_plan.get("max_weekly_loss_percent", 999) <= 2.00
        ),
        "max_open_positions": mock_order_plan.get("max_open_positions") == 1,
        "max_orders_per_signal": mock_order_plan.get("max_orders_per_signal") == 1,
        "stop_loss_required": mock_order_plan.get("stop_loss_required") is True,
        "take_profit_required": mock_order_plan.get("take_profit_required") is True,
        "minimum_reward_to_risk": (
            mock_order_plan.get("minimum_reward_to_risk", 0) >= 1.20
        ),
        "one_order_rule_verified": (
            mock_order_plan.get("one_order_rule_verified") is True
        ),
        "daily_stop_verified": mock_order_plan.get("daily_stop_verified") is True,
        "weekly_stop_verified": mock_order_plan.get("weekly_stop_verified") is True,
        "kill_switch_verified": mock_order_plan.get("kill_switch_verified") is True,
        "audit_record_required": mock_order_plan.get("audit_record_required") is True,
        "demo_order_placement_authorized": (
            mock_order_plan.get("demo_order_placement_authorized") is False
        ),
        "broker_api_access_blocked": (
            mock_order_plan.get("broker_api_access_blocked") is True
        ),
        "credential_access_blocked": (
            mock_order_plan.get("credential_access_blocked") is True
        ),
        "live_trading_blocked": mock_order_plan.get("live_trading_blocked") is True,
        "money_movement_blocked": (
            mock_order_plan.get("money_movement_blocked") is True
        ),
        "no_autonomy_approval": mock_order_plan.get("no_autonomy_approval") is True,
    }


def _passed_requirements(rehearsal_checks: dict[str, bool]) -> list[str]:
    return [name for name, passed in rehearsal_checks.items() if passed]


def _failed_requirements(rehearsal_checks: dict[str, bool]) -> list[str]:
    return [name for name, passed in rehearsal_checks.items() if not passed]


def _bullet_list(items: list[str] | tuple[str, ...]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def _contract_lines(mapping: dict[str, Any]) -> str:
    if not mapping:
        return "- inert local mock order plan is blocked until P6D is ready"
    rows = ["| field | value |", "|---|---|"]
    for key, value in mapping.items():
        rows.append(f"| `{key}` | `{value}` |")
    return "\n".join(rows)


def evaluate_c1_dry_run_mock_execution_rehearsal(
    owner_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the deterministic P7 dry-run/mock execution rehearsal result."""

    p6d_result = evaluate_c1_demo_order_intent_final_review_card(owner_input)
    p6d_status = p6d_result.get("p6d_final_review_status")
    final_review_status = p6d_result.get("final_review_status")
    p6d_next_lane = p6d_result.get("next_required_lane")
    p6d_demo_authorized = p6d_result.get("demo_order_placement_authorized")
    input_score = p6d_result.get("post_p6d_score")

    p6d_ready = (
        p6d_status == "P6D_FINAL_REVIEW_CARD_READY_FOR_P7_DRY_RUN_REHEARSAL"
        and final_review_status == "P7_DRY_RUN_REHEARSAL_READY"
        and p6d_next_lane == "P7_DRY_RUN_MOCK_EXECUTION_REHEARSAL"
        and p6d_demo_authorized is False
    )

    if owner_input is None:
        rehearsal_checks = _empty_rehearsal_checks()
        return {
            "campaign_id": CAMPAIGN_ID,
            "candidate_id": CANDIDATE_ID,
            "candidate_name": CANDIDATE_NAME,
            "input_score": input_score,
            "post_p7_score": 100,
            "p6d_final_review_status": p6d_status,
            "p6d_final_review_status_observed": p6d_status,
            "p7_rehearsal_status": (
                "P7_DRY_RUN_REHEARSAL_BLOCKED_OWNER_INPUT_REQUIRED"
            ),
            "mock_rehearsal_status": "NOT_READY",
            "next_required_lane": (
                "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"
            ),
            "mock_order_plan_created": False,
            "mock_order_plan": {},
            "rehearsal_checks": rehearsal_checks,
            "passed_requirements": [],
            "failed_requirements": ["owner_input_required"],
            "blocked_actions": list(BLOCKED_ACTIONS),
            "forbidden_actions": list(FORBIDDEN_ACTIONS),
            "demo_order_placement_authorized": False,
            "live_trading_blocked": True,
            "broker_api_access_blocked": True,
            "credential_access_blocked": True,
            "money_movement_blocked": True,
            "no_autonomy_approval": True,
            "trader_meaning": TRADER_MEANING,
            "final_owner_sentence": OWNER_INPUT_REQUIRED_FINAL_OWNER_SENTENCE,
        }

    if not p6d_ready:
        rehearsal_checks = _empty_rehearsal_checks()
        rehearsal_checks["p6d_final_review_ready"] = False
        return {
            "campaign_id": CAMPAIGN_ID,
            "candidate_id": CANDIDATE_ID,
            "candidate_name": CANDIDATE_NAME,
            "input_score": input_score,
            "post_p7_score": 80,
            "p6d_final_review_status": p6d_status,
            "p6d_final_review_status_observed": p6d_status,
            "p7_rehearsal_status": "P7_DRY_RUN_REHEARSAL_BLOCKED_P6D_REPAIR_REQUIRED",
            "mock_rehearsal_status": "NOT_READY",
            "next_required_lane": "P6B_P6C_P6D_REPAIR_REVIEW",
            "mock_order_plan_created": False,
            "mock_order_plan": {},
            "rehearsal_checks": rehearsal_checks,
            "passed_requirements": [],
            "failed_requirements": ["p6d_final_review_ready"],
            "blocked_actions": list(BLOCKED_ACTIONS),
            "forbidden_actions": list(FORBIDDEN_ACTIONS),
            "demo_order_placement_authorized": False,
            "live_trading_blocked": True,
            "broker_api_access_blocked": True,
            "credential_access_blocked": True,
            "money_movement_blocked": True,
            "no_autonomy_approval": True,
            "trader_meaning": TRADER_MEANING,
            "final_owner_sentence": P6D_REPAIR_REQUIRED_FINAL_OWNER_SENTENCE,
        }

    mock_order_plan = _build_mock_order_plan(p6d_result["final_review_card"])
    rehearsal_checks = _evaluate_rehearsal_checks(p6d_result, mock_order_plan)
    passed_requirements = _passed_requirements(rehearsal_checks)
    failed_requirements = _failed_requirements(rehearsal_checks)

    if failed_requirements:
        p7_rehearsal_status = "P7_DRY_RUN_MOCK_REHEARSAL_FAILED_REPAIR_REQUIRED"
        mock_rehearsal_status = "NOT_READY"
        post_p7_score = 80
        next_required_lane = "P7_REPAIR_DRY_RUN_MOCK_REHEARSAL"
        final_owner_sentence = P7_REPAIR_REQUIRED_FINAL_OWNER_SENTENCE
    else:
        p7_rehearsal_status = "P7_DRY_RUN_MOCK_REHEARSAL_PASSED_FOR_P8_REVIEW"
        mock_rehearsal_status = "P8_READY"
        post_p7_score = 100
        next_required_lane = "P8_SUPERVISED_DEMO_BROKER_ACCOUNT_READINESS_BRIDGE"
        final_owner_sentence = P8_READY_FINAL_OWNER_SENTENCE

    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": input_score,
        "post_p7_score": post_p7_score,
        "p6d_final_review_status": p6d_status,
        "p6d_final_review_status_observed": p6d_status,
        "p7_rehearsal_status": p7_rehearsal_status,
        "mock_rehearsal_status": mock_rehearsal_status,
        "next_required_lane": next_required_lane,
        "mock_order_plan_created": True,
        "mock_order_plan": deepcopy(mock_order_plan),
        "rehearsal_checks": rehearsal_checks,
        "passed_requirements": passed_requirements,
        "failed_requirements": failed_requirements,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
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
    """Render the owner-facing P7 dry-run/mock rehearsal report."""

    return f"""# AIOS Forex C1 Dry Run Mock Execution Rehearsal V1 Report

## Campaign Scope

This report applies the P7 C1 dry-run/mock execution rehearsal for `c1-eur-buy` only. It consumes the P6D final review card and creates inert local rehearsal evidence for later supervised demo broker/account readiness bridge review.

This report does not collect secrets, read credentials, access accounts, access brokers, calculate live or account-specific position size, place demo orders, place live orders, close orders, move money, activate schedulers, activate daemons, activate webhooks, activate production, or authorize autonomous trading.

## Trader Meaning

{TRADER_MEANING}

## P6D Entry Condition

- p6d_final_review_status: `{result["p6d_final_review_status"]}`
- p6d_final_review_status_observed: `{result["p6d_final_review_status_observed"]}`

## Mock Order Plan

{_contract_lines(result["mock_order_plan"])}

## Rehearsal Checks

{_contract_lines(result["rehearsal_checks"])}

## Passed Requirements

{_bullet_list(result["passed_requirements"])}

## Failed Requirements

{_bullet_list(result["failed_requirements"])}

## Blocked Actions

{_bullet_list(result["blocked_actions"])}

## P8 Readiness Decision

- p7_rehearsal_status: `{result["p7_rehearsal_status"]}`
- mock_rehearsal_status: `{result["mock_rehearsal_status"]}`
- post_p7_score: `{result["post_p7_score"]}`
- demo_order_placement_authorized: `{result["demo_order_placement_authorized"]}`

## Next Required Lane

`{result["next_required_lane"]}`

## What This Completes

- creates the deterministic P7 dry-run/mock execution rehearsal gate
- verifies inert local mock order-plan safety checks only after P6D is ready
- routes only a passed dry-run/mock rehearsal toward P8 review
- keeps demo-order placement, live-trading, broker/API, credential, money-movement, and autonomy blocks active

## What This Does Not Approve

{_bullet_list(result["blocked_actions"])}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""


def render_next_action_queue(result: dict[str, Any]) -> str:
    """Render the next-action queue for the P7 dry-run/mock rehearsal gate."""

    if result["mock_rehearsal_status"] == "P8_READY":
        required_next_actions = [
            "start P8 supervised demo broker/account readiness bridge",
            "keep broker/API access blocked until P8 explicitly reviews it",
            "keep credentials blocked",
            "keep demo-order placement blocked",
            "keep live trading blocked",
            "keep money movement blocked",
        ]
    else:
        required_next_actions = [
            "supply sanitized owner input through P6B",
            "validate owner input through P6C",
            "build final review card through P6D",
            "rerun P7 dry-run/mock rehearsal",
            "keep demo-order placement blocked",
        ]

    remaining_blocks = [
        "demo-order placement remains blocked",
        "live trading remains blocked",
        "broker/API access remains blocked",
        "credentials remain blocked",
        "money movement remains blocked",
        "autonomous trading remains blocked",
    ]

    return f"""# AIOS Forex C1 Dry Run Mock Execution Rehearsal Next Action Queue V1

## Purpose

This queue records the next action after the P7 C1 dry-run/mock execution rehearsal gate.

## P7 Rehearsal Status

`{result["p7_rehearsal_status"]}`

## Mock Rehearsal Status

`{result["mock_rehearsal_status"]}`

## Passed Requirements

{_bullet_list(result["passed_requirements"])}

## Failed Requirements

{_bullet_list(result["failed_requirements"])}

## Next Required Lane

`{result["next_required_lane"]}`

## Required Next Actions

{_bullet_list(required_next_actions)}

## Remaining Blocks

{_bullet_list(remaining_blocks)}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""


__all__ = [
    "evaluate_c1_dry_run_mock_execution_rehearsal",
    "render_owner_report",
    "render_next_action_queue",
]
