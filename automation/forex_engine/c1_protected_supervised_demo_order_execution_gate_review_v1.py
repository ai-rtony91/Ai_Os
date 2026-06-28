"""Deterministic C1 protected supervised demo-order execution gate review.

This module consumes the P8 broker/account readiness bridge output and creates
an inert execution-control review artifact for EUR/USD BUY only. It never accesses
brokers, credentials, accounts, schedulers, daemons, webhooks, production systems,
or order-routing paths.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from automation.forex_engine.c1_supervised_demo_broker_account_readiness_bridge_v1 import (
    evaluate_c1_supervised_demo_broker_account_readiness_bridge as evaluate_p8_bridge,
)


CAMPAIGN_ID = (
    "AIOS-FOREX-P9-C1-PROTECTED-SUPERVISED-DEMO-ORDER-EXECUTION-GATE-"
    "REVIEW-V1"
)
CANDIDATE_ID = "c1-eur-buy"
CANDIDATE_NAME = "paper_long_run_supervisor_v2 LONG EURUSD"

TRADER_MEANING = (
    "AIOS is creating a protected supervised demo-order execution gate review "
    "for the EUR/USD buy setup so it can verify execution-control readiness "
    "before any owner-controlled demo-order run handoff is considered."
)

OWNER_INPUT_REQUIRED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P9 C1 protected supervised demo-order execution gate review "
    "is waiting for validated owner input; no broker/API, credential, or demo-"
    "order authority is authorized."
)

P9_PASSED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P9 C1 protected supervised demo-order execution gate review "
    "has created an inert execution gate checklist for P10 owner-run handoff "
    "preparation while demo-order placement, live trading, broker/API, "
    "credential access, money movement, and autonomy remain blocked."
)

P8_REPAIR_REQUIRED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P9 C1 protected supervised demo-order execution gate review is "
    "blocked by the prior P8 readiness state and must return to "
    "P8_BROKER_ACCOUNT_READINESS_REPAIR_REVIEW; demo-order placement, live "
    "trading, broker/API, credentials, money movement, and autonomy remain "
    "blocked."
)

P9_REPAIR_REQUIRED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P9 C1 protected supervised demo-order execution gate review "
    "found execution-check failures and must enter "
    "P9_PROTECTED_EXECUTION_GATE_REPAIR_REVIEW; demo-order placement, live "
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
    "claiming demo-order placement authority",
    "claiming broker/API access authority",
    "claiming credential authority",
    "claiming money movement authority",
    "claiming autonomy approval",
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

GATE_CHECK_NAMES = [
    "owner_decision_approved",
    "p8_broker_account_ready",
    "execution_gate_created",
    "candidate_id_confirmed",
    "instrument_is_eur_usd",
    "side_is_buy",
    "demo_environment_only",
    "order_type_selected",
    "max_orders_per_signal_one",
    "max_open_positions_one",
    "current_position_count_within_limit",
    "same_signal_order_count_within_limit",
    "pending_order_count_within_limit",
    "stop_loss_reviewed",
    "take_profit_reviewed",
    "reward_to_risk_reviewed",
    "risk_per_trade_within_limit",
    "daily_loss_within_limit",
    "weekly_loss_within_limit",
    "spread_guard_reviewed",
    "slippage_guard_reviewed",
    "market_open_reviewed",
    "idempotency_key_required",
    "stale_price_block_required",
    "duplicate_order_block_required",
    "kill_switch_verified",
    "audit_record_required",
    "final_owner_execution_gate_review_marked",
    "demo_order_placement_authorized is false",
    "broker_api_access_authorized is false",
    "credential_access_authorized is false",
    "live_trading_blocked",
    "money_movement_blocked",
    "no_autonomy_approval",
]

FORBIDDEN_P9_INPUT_FIELDS = (
    "account_identifier",
    "account_id",
    "broker_account_id",
    "account_number",
    "credentials",
    "credential",
    "password",
    "token",
    "secret",
    "api_key",
    "api_keys",
    "api_token",
    "broker_api_key",
    "raw_live_account_data",
    "live_account_data",
    "live_balance",
    "live_position_data",
)


def _empty_gate_checks() -> dict[str, bool]:
    return {name: False for name in GATE_CHECK_NAMES}


def _number_lte(value: Any, limit: float) -> bool:
    try:
        return float(value) <= limit
    except (TypeError, ValueError):
        return False


def _number_gte(value: Any, limit: float) -> bool:
    try:
        return float(value) >= limit
    except (TypeError, ValueError):
        return False


def _no_forbidden_inputs(owner_input: dict[str, Any]) -> bool:
    return all(name not in owner_input for name in FORBIDDEN_P9_INPUT_FIELDS)


def _build_execution_gate_contract(owner_input: dict[str, Any]) -> dict[str, Any]:
    return {
        "protected_execution_gate_review_created": True,
        "execution_gate_type": "INERT_REVIEW_ONLY",
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "instrument": "EUR_USD",
        "side": "BUY",
        "demo_environment_only": True,
        "broker_environment_observed": "DEMO_OR_PRACTICE_ONLY",
        "order_type_selection": "MARKET",
        "max_orders_per_signal": 1,
        "max_open_positions": 1,
        "current_open_position_count_max": 1,
        "current_same_signal_order_count_max": 1,
        "pending_order_count_max": 1,
        "stop_loss_required": True,
        "take_profit_required": True,
        "minimum_reward_to_risk": 1.20,
        "max_risk_per_trade_percent": 0.25,
        "max_daily_loss_percent": 1.00,
        "max_weekly_loss_percent": 2.00,
        "spread_guard_reviewed": owner_input.get("spread_guard_review") is True,
        "slippage_guard_reviewed": owner_input.get("slippage_guard_review") is True,
        "market_open_reviewed": owner_input.get("market_open_review") is True,
        "idempotency_key_required": owner_input.get("idempotency_key_required") is True,
        "stale_price_block_required": owner_input.get(
            "stale_price_block_required"
        )
        is True,
        "duplicate_order_block_required": owner_input.get(
            "duplicate_order_block_required"
        )
        is True,
        "kill_switch_verified": owner_input.get("kill_switch_verification") is True,
        "audit_record_required": owner_input.get("audit_record_ready") is True,
        "final_owner_execution_gate_review_required": True,
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
    }


def _evaluate_gate_checks(
    owner_input: dict[str, Any],
    p8_result: dict[str, Any],
    gate_contract: dict[str, Any],
) -> dict[str, bool]:
    return {
        "p8_broker_account_ready": (
            p8_result.get("p8_bridge_status")
            == "P8_SUPERVISED_DEMO_BROKER_ACCOUNT_BRIDGE_PASSED_FOR_P9_REVIEW"
            and p8_result.get("broker_account_readiness_status") == "P9_READY"
        ),
        "owner_decision_approved": owner_input.get("owner_decision")
        == "APPROVE_DEMO_INTENT",
        "execution_gate_created": bool(gate_contract),
        "candidate_id_confirmed": (
            p8_result.get("candidate_id") == CANDIDATE_ID
            or owner_input.get("candidate_id") == CANDIDATE_ID
        ),
        "instrument_is_eur_usd": (
            owner_input.get("intended_instrument_confirmation") == "EUR_USD"
        ),
        "side_is_buy": owner_input.get("intended_side_confirmation") == "BUY",
        "demo_environment_only": (
            owner_input.get("demo_account_marker") == "DEMO_ONLY"
            and owner_input.get("broker_environment")
            == "DEMO_OR_PRACTICE_ONLY"
        ),
        "order_type_selected": owner_input.get("order_type_selection") == "MARKET",
        "max_orders_per_signal_one": (
            owner_input.get("one_order_rule_verification") is True
        ),
        "max_open_positions_one": _number_lte(
            owner_input.get("current_open_position_count"), 1
        ),
        "current_position_count_within_limit": _number_lte(
            owner_input.get("current_open_position_count"), 1
        ),
        "same_signal_order_count_within_limit": _number_lte(
            owner_input.get("current_same_signal_order_count"), 1
        ),
        "pending_order_count_within_limit": _number_lte(
            owner_input.get("pending_order_count"), 1
        ),
        "stop_loss_reviewed": owner_input.get("stop_loss_review") is True,
        "take_profit_reviewed": owner_input.get("take_profit_review") is True,
        "reward_to_risk_reviewed": (
            owner_input.get("reward_to_risk_review") is True
            and _number_gte(owner_input.get("minimum_reward_to_risk"), 1.20)
        ),
        "risk_per_trade_within_limit": _number_lte(
            owner_input.get("max_risk_per_trade_percent"), 0.25
        ),
        "daily_loss_within_limit": _number_lte(
            owner_input.get("daily_realized_loss_percent"), 1.00
        ),
        "weekly_loss_within_limit": _number_lte(
            owner_input.get("weekly_realized_loss_percent"), 2.00
        ),
        "spread_guard_reviewed": owner_input.get("spread_guard_review") is True,
        "slippage_guard_reviewed": (
            owner_input.get("slippage_guard_review") is True
        ),
        "market_open_reviewed": owner_input.get("market_open_review") is True,
        "idempotency_key_required": (
            owner_input.get("idempotency_key_required") is True
        ),
        "stale_price_block_required": (
            owner_input.get("stale_price_block_required") is True
        ),
        "duplicate_order_block_required": (
            owner_input.get("duplicate_order_block_required") is True
        ),
        "kill_switch_verified": (
            owner_input.get("kill_switch_verification") is True
            and owner_input.get("kill_switch_state") == "ARMED_UNTRIGGERED"
        ),
        "audit_record_required": (
            owner_input.get("audit_record_ready") is True
            or owner_input.get("audit_record_required") is True
        ),
        "final_owner_execution_gate_review_marked": (
            owner_input.get("final_owner_execution_gate_review") is True
        ),
        "demo_order_placement_authorized is false": (
            owner_input.get("demo_order_placement_authorized", False) is False
            and p8_result.get("demo_order_placement_authorized") is False
        ),
        "broker_api_access_authorized is false": (
            owner_input.get("broker_api_access_authorized", False) is False
            and p8_result.get("broker_api_access_authorized") is False
        ),
        "credential_access_authorized is false": (
            owner_input.get("credential_access_authorized", False) is False
            and p8_result.get("credential_access_authorized") is False
        ),
        "live_trading_blocked": (
            owner_input.get("live_trading_authorized", False) is False
            and owner_input.get("live_trading_blocked", True) is True
        ),
        "money_movement_blocked": (
            owner_input.get("money_movement_authorized", False) is False
            and owner_input.get("money_movement_blocked", True) is True
        ),
        "no_autonomy_approval": (
            owner_input.get("autonomy_approval", False) is False
            and owner_input.get("no_autonomy_approval", True) is True
        ),
    }


def _p9_gate_contract_complete(gate_checks: dict[str, bool]) -> bool:
    return all(gate_checks.values())


def _enforce_forbidden_authorities(owner_input: dict[str, Any]) -> bool:
    return (
        owner_input.get("broker_api_access_authorized", False) is False
        and owner_input.get("credential_access_authorized", False) is False
        and owner_input.get("demo_order_placement_authorized", False) is False
        and owner_input.get("live_trading_authorized", False) is False
        and owner_input.get("money_movement_authorized", False) is False
        and owner_input.get("autonomy_approval", False) is False
        and _no_forbidden_inputs(owner_input)
    )


def _passed_requirements(gate_checks: dict[str, bool]) -> list[str]:
    return [name for name, passed in gate_checks.items() if passed]


def _failed_requirements(gate_checks: dict[str, bool]) -> list[str]:
    return [name for name, passed in gate_checks.items() if not passed]


def _bullet_list(items: list[str] | tuple[str, ...]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def _table_lines(mapping: dict[str, Any]) -> str:
    if not mapping:
        return "- no execution gate review was created"
    rows = ["| field | value |", "|---|---|"]
    for key, value in mapping.items():
        rows.append(f"| `{key}` | `{value}` |")
    return "\n".join(rows)


def _default_blocked_result(p8_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": p8_result.get("post_p8_score", 80),
        "post_p9_score": 100,
        "p8_bridge_status": p8_result.get("p8_bridge_status"),
        "p8_bridge_status_observed": p8_result.get("p8_bridge_status"),
        "broker_account_readiness_status_observed": p8_result.get(
            "broker_account_readiness_status"
        ),
        "p9_execution_gate_status": (
            "P9_EXECUTION_GATE_BLOCKED_OWNER_INPUT_REQUIRED"
        ),
        "protected_demo_order_gate_status": "NOT_READY",
        "next_required_lane": (
            "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"
        ),
        "protected_execution_gate_review_created": False,
        "protected_execution_gate_review": {},
        "execution_gate_checks": _empty_gate_checks(),
        "passed_requirements": [],
        "failed_requirements": ["owner_input_required"],
        "blocked_actions": list(BLOCKED_ACTIONS),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
        "trader_meaning": TRADER_MEANING,
        "final_owner_sentence": OWNER_INPUT_REQUIRED_FINAL_OWNER_SENTENCE,
    }


def _p8_not_ready_result(
    p8_result: dict[str, Any]
) -> dict[str, Any]:
    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": p8_result.get("post_p8_score", 80),
        "post_p9_score": 80,
        "p8_bridge_status": p8_result.get("p8_bridge_status"),
        "p8_bridge_status_observed": p8_result.get("p8_bridge_status"),
        "broker_account_readiness_status_observed": p8_result.get(
            "broker_account_readiness_status"
        ),
        "p9_execution_gate_status": "P9_EXECUTION_GATE_BLOCKED_P8_REPAIR_REQUIRED",
        "protected_demo_order_gate_status": "NOT_READY",
        "next_required_lane": "P8_BROKER_ACCOUNT_READINESS_REPAIR_REVIEW",
        "protected_execution_gate_review_created": False,
        "protected_execution_gate_review": {},
        "execution_gate_checks": _empty_gate_checks(),
        "passed_requirements": [],
        "failed_requirements": ["p8_broker_account_ready"],
        "blocked_actions": list(BLOCKED_ACTIONS),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
        "trader_meaning": TRADER_MEANING,
        "final_owner_sentence": P8_REPAIR_REQUIRED_FINAL_OWNER_SENTENCE,
    }


def _review_failed_result(
    p8_result: dict[str, Any],
    gate_contract: dict[str, Any],
    gate_checks: dict[str, bool],
    passed_requirements: list[str],
    failed_requirements: list[str],
) -> dict[str, Any]:
    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": p8_result.get("post_p8_score", 80),
        "post_p9_score": 80,
        "p8_bridge_status": p8_result.get("p8_bridge_status"),
        "p8_bridge_status_observed": p8_result.get("p8_bridge_status"),
        "broker_account_readiness_status_observed": p8_result.get(
            "broker_account_readiness_status"
        ),
        "p9_execution_gate_status": "P9_EXECUTION_GATE_FAILED_REPAIR_REQUIRED",
        "protected_demo_order_gate_status": "NOT_READY",
        "next_required_lane": (
            "P9_PROTECTED_EXECUTION_GATE_REPAIR_REVIEW"
        ),
        "protected_execution_gate_review_created": bool(
            _p9_gate_contract_complete(gate_checks)
        ),
        "protected_execution_gate_review": deepcopy(gate_contract),
        "execution_gate_checks": gate_checks,
        "passed_requirements": passed_requirements,
        "failed_requirements": failed_requirements,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
        "trader_meaning": TRADER_MEANING,
        "final_owner_sentence": P9_REPAIR_REQUIRED_FINAL_OWNER_SENTENCE,
    }


def evaluate_c1_protected_supervised_demo_order_execution_gate_review(
    owner_input: dict[str, Any] | None = None
) -> dict[str, Any]:
    if owner_input is None:
        return _default_blocked_result(
            evaluate_p8_bridge()
        )

    p8_result = evaluate_p8_bridge(
        owner_input
    )

    if (
        p8_result.get("p8_bridge_status")
        != "P8_SUPERVISED_DEMO_BROKER_ACCOUNT_BRIDGE_PASSED_FOR_P9_REVIEW"
        or p8_result.get("broker_account_readiness_status") != "P9_READY"
    ):
        return _p8_not_ready_result(p8_result)

    if not _enforce_forbidden_authorities(owner_input):
        return _p8_not_ready_result(p8_result)

    execution_gate_review = _build_execution_gate_contract(owner_input)
    execution_gate_checks = _evaluate_gate_checks(
        owner_input, p8_result, execution_gate_review
    )
    passed_requirements = _passed_requirements(execution_gate_checks)
    failed_requirements = _failed_requirements(execution_gate_checks)

    if failed_requirements:
        return _review_failed_result(
            p8_result,
            execution_gate_review,
            execution_gate_checks,
            passed_requirements,
            failed_requirements,
        )

    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": p8_result.get("post_p8_score", 80),
        "post_p9_score": 100,
        "p8_bridge_status": p8_result.get("p8_bridge_status"),
        "p8_bridge_status_observed": p8_result.get("p8_bridge_status"),
        "broker_account_readiness_status_observed": p8_result.get(
            "broker_account_readiness_status"
        ),
        "p9_execution_gate_status": (
            "P9_PROTECTED_SUPERVISED_DEMO_ORDER_EXECUTION_GATE_PASSED_FOR_P10"
            "_OWNER_RUN_HANDOFF"
        ),
        "protected_demo_order_gate_status": "P10_READY",
        "next_required_lane": (
            "P10_OWNER_CONTROLLED_PROTECTED_DEMO_ORDER_RUN_HANDOFF_PREPARATION"
        ),
        "protected_execution_gate_review_created": True,
        "protected_execution_gate_review": deepcopy(execution_gate_review),
        "execution_gate_checks": execution_gate_checks,
        "passed_requirements": passed_requirements,
        "failed_requirements": failed_requirements,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
        "trader_meaning": TRADER_MEANING,
        "final_owner_sentence": P9_PASSED_FINAL_OWNER_SENTENCE,
    }


def render_owner_report(result: dict[str, Any]) -> str:
    """Render the owner-facing P9 gate review report."""

    return f"""# AIOS Forex C1 Protected Supervised Demo Order Execution Gate Review V1 Report

## Campaign Scope

This report applies to the P9 protected supervised demo-order execution gate review for
`c1-eur-buy` only. It consumes the P8 broker/account readiness bridge output and
creates an inert execution gate review before any owner-controlled demo-order run handoff
is considered.

This report does not collect secrets, read credentials, access accounts, access brokers, calculate
real account-specific position size, place demo orders, place live orders, close orders,
move money, activate schedulers, activate daemons, activate webhooks, activate production,
or authorize autonomous trading.

## Trader Meaning

{TRADER_MEANING}

## P8 Entry Condition

- p8_bridge_status: `{result["p8_bridge_status"]}`
- p8_bridge_status_observed: `{result["p8_bridge_status_observed"]}`
- broker_account_readiness_status_observed: `{result["broker_account_readiness_status_observed"]}`

## Protected Execution Gate Review

{_table_lines(result["protected_execution_gate_review"])}

## Execution Gate Checks

{_table_lines(result["execution_gate_checks"])}

## Passed Requirements

{_bullet_list(result["passed_requirements"])}

## Failed Requirements

{_bullet_list(result["failed_requirements"])}

## Blocked Actions

{_bullet_list(result["blocked_actions"])}

## P10 Readiness Decision

- p9_execution_gate_status: `{result["p9_execution_gate_status"]}`
- protected_demo_order_gate_status: `{result["protected_demo_order_gate_status"]}`
- post_p9_score: `{result["post_p9_score"]}`
- demo_order_placement_authorized: `{result["demo_order_placement_authorized"]}`
- broker_api_access_authorized: `{result["broker_api_access_authorized"]}`
- credential_access_authorized: `{result["credential_access_authorized"]}`

## Next Required Lane

`{result["next_required_lane"]}`

## What This Completes

- creates the deterministic P9 protected supervised demo-order execution gate review checklist
- verifies execution-control readiness only for EUR/USD BUY in demo-only conditions
- routes only a passing gate review toward P10 owner-run handoff preparation
- keeps demo-order placement, live trading, broker/API, credentials, money movement, and autonomy blocked

## What This Does Not Approve

{_bullet_list(result["blocked_actions"])}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""


def render_next_action_queue(result: dict[str, Any]) -> str:
    """Render the next-action queue for P9 execution gate review."""

    if result["p9_execution_gate_status"] == (
        "P9_PROTECTED_SUPERVISED_DEMO_ORDER_EXECUTION_GATE_PASSED_FOR_P10"
        "_OWNER_RUN_HANDOFF"
    ):
        required_next_actions = [
            "start P10 owner-controlled protected demo-order run handoff preparation",
            "keep broker/API access blocked until P10 explicitly reviews credential-handling and connection requirements",
            "keep credentials blocked until P10 explicitly reviews credential-handling requirements",
            "keep demo-order placement blocked until later owner-run handoff approval",
            "keep live trading blocked",
            "keep money movement blocked",
        ]
    elif result["p9_execution_gate_status"] == (
        "P9_EXECUTION_GATE_BLOCKED_OWNER_INPUT_REQUIRED"
    ):
        required_next_actions = [
            "supply sanitized owner input through P6B",
            "validate owner input through P6C",
            "build final review card through P6D",
            "rerun P7 dry-run/mock rehearsal",
            "rerun P8 broker/account readiness bridge",
            "rerun P9 protected execution gate review",
            "keep broker/API access blocked",
            "keep credentials blocked",
            "keep demo-order placement blocked",
        ]
    elif result["p9_execution_gate_status"] == (
        "P9_EXECUTION_GATE_BLOCKED_P8_REPAIR_REQUIRED"
    ):
        required_next_actions = [
            "rerun P8 broker/account readiness bridge",
            "rerun P9 protected execution gate review",
            "keep broker/API access blocked",
            "keep credentials blocked",
            "keep demo-order placement blocked",
        ]
    else:
        required_next_actions = [
            "repair execution-control requirements identified by P9 gate checks",
            "rerun P9 protected execution gate review",
            "keep broker/API access blocked",
            "keep credentials blocked",
            "keep demo-order placement blocked",
        ]

    remaining_blocks = [
        "demo-order placement remains blocked",
        "live trading remains blocked",
        "broker/API access remains blocked",
        "credentials remain blocked",
        "money movement remains blocked",
        "autonomy approval remains false",
    ]

    return f"""# AIOS Forex C1 Protected Supervised Demo Order Execution Gate Review Next Action Queue V1

## Purpose

This queue records the next action after the P9 protected supervised demo-order execution
execution gate review.

## P9 Execution Gate Status

`{result["p9_execution_gate_status"]}`

## Protected Demo Order Gate Status

`{result["protected_demo_order_gate_status"]}`

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
    "evaluate_c1_protected_supervised_demo_order_execution_gate_review",
    "render_owner_report",
    "render_next_action_queue",
]
