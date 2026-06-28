"""Deterministic C1 supervised demo broker/account readiness bridge.

This module consumes the P7 dry-run/mock execution rehearsal and creates
sanitized local readiness evidence only. It does not access brokers,
credentials, accounts, balances, prices, orders, schedulers, daemons,
webhooks, production systems, or trading execution paths.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from automation.forex_engine.c1_dry_run_mock_execution_rehearsal_v1 import (
    evaluate_c1_dry_run_mock_execution_rehearsal,
)


CAMPAIGN_ID = (
    "AIOS-FOREX-P8-C1-SUPERVISED-DEMO-BROKER-ACCOUNT-READINESS-BRIDGE-V1"
)
CANDIDATE_ID = "c1-eur-buy"
CANDIDATE_NAME = "paper_long_run_supervisor_v2 LONG EURUSD"

TRADER_MEANING = (
    "AIOS is creating a sanitized broker/account readiness bridge for the "
    "EUR/USD buy setup so it can verify demo-only account readiness before "
    "any protected supervised demo-order execution gate is considered."
)

OWNER_INPUT_REQUIRED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P8 C1 supervised demo broker/account readiness bridge is "
    "waiting for validated owner input; no broker/API, credential, or "
    "demo-order authority is authorized."
)

P9_READY_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P8 C1 supervised demo broker/account readiness bridge passed "
    "for P9 protected supervised demo-order execution gate review using "
    "sanitized review-only evidence; demo-order placement, live trading, "
    "broker/API, credentials, money movement, and autonomy remain blocked."
)

P7_REPAIR_REQUIRED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P8 C1 supervised demo broker/account readiness bridge is "
    "blocked because P7 dry-run/mock rehearsal is not ready; demo-order "
    "placement, live trading, broker/API, credentials, money movement, and "
    "autonomy remain blocked."
)

P8_REPAIR_REQUIRED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P8 C1 supervised demo broker/account readiness bridge failed "
    "local sanitized readiness checks and must be repaired before P9 review; "
    "demo-order placement, live trading, broker/API, credentials, money "
    "movement, and autonomy remain blocked."
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
    "claiming owner input as validated by automation",
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

BRIDGE_CHECK_NAMES = [
    "p7_mock_rehearsal_ready",
    "bridge_created",
    "demo_account_marker_confirmed",
    "broker_environment_demo_only",
    "broker_name_sanitized",
    "no_account_identifier",
    "no_credentials",
    "no_api_keys",
    "no_raw_live_account_data",
    "sanitized_equity_present",
    "open_position_count_within_limit",
    "same_signal_order_count_within_limit",
    "pending_order_count_within_limit",
    "risk_per_trade_within_limit",
    "daily_loss_within_limit",
    "weekly_loss_within_limit",
    "stop_loss_reviewed",
    "take_profit_reviewed",
    "reward_to_risk_reviewed",
    "spread_guard_reviewed",
    "slippage_guard_reviewed",
    "market_open_reviewed",
    "one_order_rule_verified",
    "daily_stop_verified",
    "weekly_stop_verified",
    "kill_switch_verified",
    "audit_record_required",
    "owner_attestation_true",
    "demo_order_placement_authorized is false",
    "broker_api_access_authorized is false",
    "credential_access_authorized is false",
    "live_trading_blocked",
    "money_movement_blocked",
    "no_autonomy_approval",
]

ACCOUNT_IDENTIFIER_FIELDS = (
    "account_identifier",
    "account_id",
    "broker_account_id",
    "account_number",
)
CREDENTIAL_FIELDS = (
    "credentials",
    "credential",
    "password",
    "token",
    "secret",
)
API_KEY_FIELDS = (
    "api_key",
    "api_keys",
    "api_token",
    "broker_api_key",
)
RAW_LIVE_ACCOUNT_FIELDS = (
    "raw_live_account_data",
    "live_account_data",
    "live_balance",
    "live_position_data",
)


def _empty_bridge_checks() -> dict[str, bool]:
    return {name: False for name in BRIDGE_CHECK_NAMES}


def _field_absent(owner_input: dict[str, Any], field_names: tuple[str, ...]) -> bool:
    return all(name not in owner_input for name in field_names)


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


def _p7_ready(p7_result: dict[str, Any]) -> bool:
    return (
        p7_result.get("p7_rehearsal_status")
        == "P7_DRY_RUN_MOCK_REHEARSAL_PASSED_FOR_P8_REVIEW"
        and p7_result.get("mock_rehearsal_status") == "P8_READY"
        and p7_result.get("next_required_lane")
        == "P8_SUPERVISED_DEMO_BROKER_ACCOUNT_READINESS_BRIDGE"
        and p7_result.get("demo_order_placement_authorized") is False
    )


def _build_bridge_contract(owner_input: dict[str, Any]) -> dict[str, Any]:
    return {
        "supervised_demo_broker_account_bridge_created": True,
        "bridge_type": "SANITIZED_REVIEW_ONLY",
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "instrument": "EUR_USD",
        "side": "BUY",
        "demo_account_marker_required": True,
        "demo_account_marker_observed": owner_input.get("demo_account_marker"),
        "broker_environment_required": "DEMO_OR_PRACTICE_ONLY",
        "broker_environment_observed": owner_input.get("broker_environment"),
        "broker_name_sanitized_required": True,
        "account_identifier_forbidden": True,
        "credentials_forbidden": True,
        "api_keys_forbidden": True,
        "raw_live_account_data_forbidden": True,
        "sanitized_equity_value_or_bracket_required": True,
        "current_open_position_count_max": 1,
        "current_same_signal_order_count_max": 1,
        "pending_order_count_max": 1,
        "max_risk_per_trade_percent": 0.25,
        "max_daily_loss_percent": 1.00,
        "max_weekly_loss_percent": 2.00,
        "stop_loss_required": True,
        "take_profit_required": True,
        "minimum_reward_to_risk": 1.20,
        "spread_guard_required": True,
        "slippage_guard_required": True,
        "market_open_review_required": True,
        "one_order_rule_verified": True,
        "daily_stop_verified": True,
        "weekly_stop_verified": True,
        "kill_switch_verified": True,
        "audit_record_required": True,
        "owner_attestation_required": True,
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
    }


def _evaluate_bridge_checks(
    p7_result: dict[str, Any],
    owner_input: dict[str, Any],
    bridge_contract: dict[str, Any],
) -> dict[str, bool]:
    return {
        "p7_mock_rehearsal_ready": _p7_ready(p7_result),
        "bridge_created": bool(bridge_contract),
        "demo_account_marker_confirmed": (
            owner_input.get("demo_account_marker") == "DEMO_ONLY"
        ),
        "broker_environment_demo_only": (
            owner_input.get("broker_environment") == "DEMO_OR_PRACTICE_ONLY"
        ),
        "broker_name_sanitized": (
            owner_input.get("broker_name_sanitized") is True
            and "broker_name" not in owner_input
        ),
        "no_account_identifier": _field_absent(
            owner_input, ACCOUNT_IDENTIFIER_FIELDS
        ),
        "no_credentials": _field_absent(owner_input, CREDENTIAL_FIELDS),
        "no_api_keys": _field_absent(owner_input, API_KEY_FIELDS),
        "no_raw_live_account_data": _field_absent(
            owner_input, RAW_LIVE_ACCOUNT_FIELDS
        ),
        "sanitized_equity_present": bool(
            owner_input.get("sanitized_equity_value_or_bracket")
        ),
        "open_position_count_within_limit": _number_lte(
            owner_input.get("current_open_position_count"), 1
        ),
        "same_signal_order_count_within_limit": _number_lte(
            owner_input.get("current_same_signal_order_count"), 1
        ),
        "pending_order_count_within_limit": _number_lte(
            owner_input.get("pending_order_count"), 1
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
        "stop_loss_reviewed": owner_input.get("stop_loss_review") is True,
        "take_profit_reviewed": owner_input.get("take_profit_review") is True,
        "reward_to_risk_reviewed": (
            owner_input.get("reward_to_risk_review") is True
            and _number_gte(owner_input.get("minimum_reward_to_risk"), 1.20)
        ),
        "spread_guard_reviewed": owner_input.get("spread_guard_review") is True,
        "slippage_guard_reviewed": (
            owner_input.get("slippage_guard_review") is True
        ),
        "market_open_reviewed": owner_input.get("market_open_review") is True,
        "one_order_rule_verified": (
            owner_input.get("one_order_rule_verification") is True
        ),
        "daily_stop_verified": owner_input.get("daily_stop_verification") is True,
        "weekly_stop_verified": (
            owner_input.get("weekly_stop_verification") is True
        ),
        "kill_switch_verified": (
            owner_input.get("kill_switch_verification") is True
            and owner_input.get("kill_switch_state") == "ARMED_UNTRIGGERED"
        ),
        "audit_record_required": (
            owner_input.get("audit_record_required") is True
            or owner_input.get("audit_record_ready") is True
        ),
        "owner_attestation_true": owner_input.get("owner_attestation") is True,
        "demo_order_placement_authorized is false": (
            owner_input.get("demo_order_placement_authorized", False) is False
            and p7_result.get("demo_order_placement_authorized") is False
        ),
        "broker_api_access_authorized is false": (
            owner_input.get("broker_api_access_authorized", False) is False
        ),
        "credential_access_authorized is false": (
            owner_input.get("credential_access_authorized", False) is False
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


def _passed_requirements(bridge_checks: dict[str, bool]) -> list[str]:
    return [name for name, passed in bridge_checks.items() if passed]


def _failed_requirements(bridge_checks: dict[str, bool]) -> list[str]:
    return [name for name, passed in bridge_checks.items() if not passed]


def _bullet_list(items: list[str] | tuple[str, ...]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def _contract_lines(mapping: dict[str, Any]) -> str:
    if not mapping:
        return (
            "- sanitized broker/account readiness bridge is blocked until "
            "validated owner input and P7 readiness are available"
        )
    rows = ["| field | value |", "|---|---|"]
    for key, value in mapping.items():
        rows.append(f"| `{key}` | `{value}` |")
    return "\n".join(rows)


def evaluate_c1_supervised_demo_broker_account_readiness_bridge(
    owner_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the deterministic P8 broker/account readiness bridge result."""

    p7_result = evaluate_c1_dry_run_mock_execution_rehearsal(owner_input)
    p7_status = p7_result.get("p7_rehearsal_status")
    mock_status = p7_result.get("mock_rehearsal_status")
    input_score = p7_result.get("post_p7_score")

    if owner_input is None:
        bridge_checks = _empty_bridge_checks()
        return {
            "campaign_id": CAMPAIGN_ID,
            "candidate_id": CANDIDATE_ID,
            "candidate_name": CANDIDATE_NAME,
            "input_score": input_score,
            "post_p8_score": 100,
            "p7_rehearsal_status": p7_status,
            "p7_rehearsal_status_observed": p7_status,
            "mock_rehearsal_status_observed": mock_status,
            "p8_bridge_status": "P8_BRIDGE_BLOCKED_OWNER_INPUT_REQUIRED",
            "broker_account_readiness_status": "NOT_READY",
            "next_required_lane": (
                "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT"
            ),
            "supervised_demo_broker_account_bridge_created": False,
            "broker_account_readiness_contract": {},
            "bridge_checks": bridge_checks,
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

    if not _p7_ready(p7_result):
        bridge_checks = _empty_bridge_checks()
        return {
            "campaign_id": CAMPAIGN_ID,
            "candidate_id": CANDIDATE_ID,
            "candidate_name": CANDIDATE_NAME,
            "input_score": input_score,
            "post_p8_score": 80,
            "p7_rehearsal_status": p7_status,
            "p7_rehearsal_status_observed": p7_status,
            "mock_rehearsal_status_observed": mock_status,
            "p8_bridge_status": "P8_BRIDGE_BLOCKED_P7_REPAIR_REQUIRED",
            "broker_account_readiness_status": "NOT_READY",
            "next_required_lane": "P7_DRY_RUN_MOCK_REHEARSAL_REPAIR_REVIEW",
            "supervised_demo_broker_account_bridge_created": False,
            "broker_account_readiness_contract": {},
            "bridge_checks": bridge_checks,
            "passed_requirements": [],
            "failed_requirements": ["p7_mock_rehearsal_ready"],
            "blocked_actions": list(BLOCKED_ACTIONS),
            "forbidden_actions": list(FORBIDDEN_ACTIONS),
            "demo_order_placement_authorized": False,
            "broker_api_access_authorized": False,
            "credential_access_authorized": False,
            "live_trading_blocked": True,
            "money_movement_blocked": True,
            "no_autonomy_approval": True,
            "trader_meaning": TRADER_MEANING,
            "final_owner_sentence": P7_REPAIR_REQUIRED_FINAL_OWNER_SENTENCE,
        }

    bridge_contract = _build_bridge_contract(owner_input)
    bridge_checks = _evaluate_bridge_checks(p7_result, owner_input, bridge_contract)
    passed_requirements = _passed_requirements(bridge_checks)
    failed_requirements = _failed_requirements(bridge_checks)

    if failed_requirements:
        p8_bridge_status = "P8_BRIDGE_FAILED_REPAIR_REQUIRED"
        broker_account_readiness_status = "NOT_READY"
        post_p8_score = 80
        next_required_lane = "P8_BROKER_ACCOUNT_READINESS_REPAIR_REVIEW"
        bridge_created = False
        final_owner_sentence = P8_REPAIR_REQUIRED_FINAL_OWNER_SENTENCE
    else:
        p8_bridge_status = (
            "P8_SUPERVISED_DEMO_BROKER_ACCOUNT_BRIDGE_PASSED_FOR_P9_REVIEW"
        )
        broker_account_readiness_status = "P9_READY"
        post_p8_score = 100
        next_required_lane = (
            "P9_PROTECTED_SUPERVISED_DEMO_ORDER_EXECUTION_GATE_REVIEW"
        )
        bridge_created = True
        final_owner_sentence = P9_READY_FINAL_OWNER_SENTENCE

    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": input_score,
        "post_p8_score": post_p8_score,
        "p7_rehearsal_status": p7_status,
        "p7_rehearsal_status_observed": p7_status,
        "mock_rehearsal_status_observed": mock_status,
        "p8_bridge_status": p8_bridge_status,
        "broker_account_readiness_status": broker_account_readiness_status,
        "next_required_lane": next_required_lane,
        "supervised_demo_broker_account_bridge_created": bridge_created,
        "broker_account_readiness_contract": deepcopy(bridge_contract),
        "bridge_checks": bridge_checks,
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
        "final_owner_sentence": final_owner_sentence,
    }


def render_owner_report(result: dict[str, Any]) -> str:
    """Render the owner-facing P8 broker/account readiness bridge report."""

    return f"""# AIOS Forex C1 Supervised Demo Broker Account Readiness Bridge V1 Report

## Campaign Scope

This report applies the P8 C1 supervised demo broker/account readiness bridge for `c1-eur-buy` only. It consumes the P7 dry-run/mock execution rehearsal and creates sanitized broker/account readiness evidence for later protected P9 review.

This report does not collect secrets, read credentials, access accounts, access brokers, calculate live or account-specific position size, place demo orders, place live orders, close orders, move money, activate schedulers, activate daemons, activate webhooks, activate production, or authorize autonomous trading.

## Trader Meaning

{TRADER_MEANING}

## P7 Entry Condition

- p7_rehearsal_status: `{result["p7_rehearsal_status"]}`
- p7_rehearsal_status_observed: `{result["p7_rehearsal_status_observed"]}`
- mock_rehearsal_status_observed: `{result["mock_rehearsal_status_observed"]}`

## Broker Account Readiness Contract

{_contract_lines(result["broker_account_readiness_contract"])}

## Bridge Checks

{_contract_lines(result["bridge_checks"])}

## Passed Requirements

{_bullet_list(result["passed_requirements"])}

## Failed Requirements

{_bullet_list(result["failed_requirements"])}

## Blocked Actions

{_bullet_list(result["blocked_actions"])}

## P9 Readiness Decision

- p8_bridge_status: `{result["p8_bridge_status"]}`
- broker_account_readiness_status: `{result["broker_account_readiness_status"]}`
- post_p8_score: `{result["post_p8_score"]}`
- demo_order_placement_authorized: `{result["demo_order_placement_authorized"]}`
- broker_api_access_authorized: `{result["broker_api_access_authorized"]}`
- credential_access_authorized: `{result["credential_access_authorized"]}`

## Next Required Lane

`{result["next_required_lane"]}`

## What This Completes

- creates the deterministic P8 supervised demo broker/account readiness bridge gate
- verifies sanitized demo-only account readiness evidence only after P7 is ready
- routes only a passed broker/account readiness bridge toward P9 review
- keeps demo-order placement, live-trading, broker/API, credential, money-movement, and autonomy blocks active

## What This Does Not Approve

{_bullet_list(result["blocked_actions"])}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""


def render_next_action_queue(result: dict[str, Any]) -> str:
    """Render the next-action queue for the P8 readiness bridge."""

    if result["broker_account_readiness_status"] == "P9_READY":
        required_next_actions = [
            "start P9 protected supervised demo-order execution gate review",
            "keep broker/API access blocked until P9 explicitly reviews it",
            "keep credentials blocked until P9 explicitly reviews credential-handling requirements",
            "keep demo-order placement blocked until later owner approval and execution gate",
            "keep live trading blocked",
            "keep money movement blocked",
        ]
    elif result["p8_bridge_status"] == "P8_BRIDGE_BLOCKED_OWNER_INPUT_REQUIRED":
        required_next_actions = [
            "supply sanitized owner input through P6B",
            "validate owner input through P6C",
            "build final review card through P6D",
            "rerun P7 dry-run/mock rehearsal",
            "rerun P8 broker/account readiness bridge",
            "keep broker/API access blocked",
            "keep credentials blocked",
            "keep demo-order placement blocked",
        ]
    elif result["p8_bridge_status"] == "P8_BRIDGE_BLOCKED_P7_REPAIR_REQUIRED":
        required_next_actions = [
            "repair or rerun P7 dry-run/mock rehearsal",
            "confirm P7 routes to P8 readiness bridge review",
            "rerun P8 broker/account readiness bridge",
            "keep broker/API access blocked",
            "keep credentials blocked",
            "keep demo-order placement blocked",
        ]
    else:
        required_next_actions = [
            "repair failed P8 broker/account readiness fields",
            "rerun P8 broker/account readiness bridge",
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
        "autonomous trading remains blocked",
    ]

    return f"""# AIOS Forex C1 Supervised Demo Broker Account Readiness Bridge Next Action Queue V1

## Purpose

This queue records the next action after the P8 C1 supervised demo broker/account readiness bridge gate.

## P8 Bridge Status

`{result["p8_bridge_status"]}`

## Broker Account Readiness Status

`{result["broker_account_readiness_status"]}`

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
    "evaluate_c1_supervised_demo_broker_account_readiness_bridge",
    "render_owner_report",
    "render_next_action_queue",
]
