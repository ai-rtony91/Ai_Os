"""Deterministic C1 owner-controlled protected demo-order run handoff preparation.

This module consumes the P9 execution-gate review output and builds an inert
owner-run handoff packet for the EUR/USD BUY setup. It does not access brokers,
credentials, accounts, APIs, schedulers, daemons, webhooks, production systems,
or any order-routing path.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from automation.forex_engine.c1_protected_supervised_demo_order_execution_gate_review_v1 import (
    evaluate_c1_protected_supervised_demo_order_execution_gate_review as evaluate_p9_review,
)


CAMPAIGN_ID = (
    "AIOS-FOREX-P10-C1-OWNER-CONTROLLED-PROTECTED-DEMO-ORDER-RUN-HANDOFF"
    "-PREPARATION-V1"
)
CANDIDATE_ID = "c1-eur-buy"
CANDIDATE_NAME = "paper_long_run_supervisor_v2 LONG EURUSD"

TRADER_MEANING = (
    "AIOS is creating an owner-controlled protected demo-order run handoff "
    "preparation packet for the EUR/USD buy setup so it can verify owner-run "
    "handoff readiness before any explicit owner-approved protected demo-order "
    "run packet is considered."
)

DEFAULT_BLOCKED_OWNER_SENTENCE = (
    "P10 is waiting for validated owner input and no broker/API, credential, "
    "or demo-order authority is authorized."
)

P10_PASSED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P10 C1 owner-controlled protected demo-order run handoff "
    "preparation created an inert owner-run handoff packet for P11 review while "
    "demo-order placement, live trading, broker/API, credentials, money "
    "movement, and autonomy remain blocked."
)

P9_REPAIR_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P10 C1 owner-controlled protected demo-order run handoff "
    "preparation is blocked by prior P9 execution-gate readiness state and "
    "must return to P9_PROTECTED_EXECUTION_GATE_REPAIR_REVIEW; demo-order "
    "placement, broker/API, credential, live trading, money movement, and "
    "autonomy remain blocked."
)

P10_REPAIR_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P10 C1 owner-controlled protected demo-order run handoff "
    "preparation found owner-run handoff checks that require repair in "
    "P10_OWNER_RUN_HANDOFF_REPAIR_REVIEW; demo-order placement, broker/API, "
    "credentials, live trading, money movement, and autonomy remain blocked."
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
    "autonomy approval",
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
    "autonomy approval",
]

FORBIDDEN_P10_INPUT_FIELDS = (
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
    "live_trading_authorized",
    "money_movement_authorized",
    "autonomy_approval",
)

GATE_CHECK_NAMES = [
    "p9_execution_gate_ready",
    "handoff_packet_created",
    "candidate_id_confirmed",
    "instrument_is_eur_usd",
    "side_is_buy",
    "demo_environment_only",
    "order_type_selected",
    "owner_control_required",
    "owner_run_handoff_review_marked",
    "explicit_owner_run_packet_required",
    "credential_handling_review_marked",
    "broker_connection_review_marked",
    "broker_api_connection_authorized_now_is_false",
    "credential_access_authorized_now_is_false",
    "order_submission_authorized_now_is_false",
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
    "final_owner_run_handoff_review_marked",
    "demo_order_placement_authorized_is_false",
    "broker_api_access_authorized_is_false",
    "credential_access_authorized_is_false",
    "live_trading_blocked",
    "money_movement_blocked",
    "no_autonomy_approval",
]


def _empty_checks() -> dict[str, bool]:
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
    return all(name not in owner_input for name in FORBIDDEN_P10_INPUT_FIELDS)


def _build_owner_run_handoff_contract(owner_input: dict[str, Any]) -> dict[str, Any]:
    return {
        "handoff_packet_type": "INERT_OWNER_RUN_PREPARATION_ONLY",
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "instrument": "EUR_USD",
        "side": "BUY",
        "demo_environment_only": True,
        "broker_environment_observed": "DEMO_OR_PRACTICE_ONLY",
        "order_type_selection": "MARKET",
        "owner_control_required": True,
        "owner_run_handoff_review_required": True,
        "explicit_owner_run_packet_required": True,
        "credential_handling_review_required": True,
        "broker_connection_review_required": True,
        "broker_api_connection_authorized_now": owner_input.get(
            "broker_api_connection_authorized_now"
        )
        is False,
        "credential_access_authorized_now": owner_input.get(
            "credential_access_authorized_now"
        )
        is False,
        "order_submission_authorized_now": owner_input.get(
            "order_submission_authorized_now"
        )
        is False,
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
        "idempotency_key_required": owner_input.get("idempotency_key_required")
        is True,
        "stale_price_block_required": owner_input.get("stale_price_block_required")
        is True,
        "duplicate_order_block_required": owner_input.get(
            "duplicate_order_block_required"
        )
        is True,
        "kill_switch_verified": owner_input.get("kill_switch_verification") is True,
        "audit_record_required": owner_input.get("audit_record_ready") is True
        or owner_input.get("audit_record_required") is True,
        "final_owner_run_handoff_review_required": True,
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
        "handoff_packet_created": True,
    }


def _evaluate_p10_checks(
    owner_input: dict[str, Any], p9_result: dict[str, Any], packet: dict[str, Any]
) -> dict[str, bool]:
    return {
        "p9_execution_gate_ready": (
            p9_result.get("p9_execution_gate_status")
            == "P9_PROTECTED_SUPERVISED_DEMO_ORDER_EXECUTION_GATE_PASSED_FOR_P10_OWNER_RUN_HANDOFF"
            and p9_result.get("protected_demo_order_gate_status") == "P10_READY"
            and p9_result.get("next_required_lane")
            == "P10_OWNER_CONTROLLED_PROTECTED_DEMO_ORDER_RUN_HANDOFF_PREPARATION"
        ),
        "handoff_packet_created": bool(packet),
        "candidate_id_confirmed": (
            owner_input.get("candidate_id", CANDIDATE_ID) == CANDIDATE_ID
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
        "owner_control_required": owner_input.get("owner_control_required", True) is True,
        "owner_run_handoff_review_marked": owner_input.get("owner_run_handoff_review")
        is True,
        "explicit_owner_run_packet_required": owner_input.get("explicit_owner_run_packet_required")
        is True,
        "credential_handling_review_marked": owner_input.get(
            "credential_handling_review"
        )
        is True,
        "broker_connection_review_marked": owner_input.get("broker_connection_review")
        is True,
        "broker_api_connection_authorized_now_is_false": (
            owner_input.get("broker_api_connection_authorized_now") is False
        ),
        "credential_access_authorized_now_is_false": (
            owner_input.get("credential_access_authorized_now") is False
        ),
        "order_submission_authorized_now_is_false": (
            owner_input.get("order_submission_authorized_now") is False
        ),
        "max_orders_per_signal_one": owner_input.get("one_order_rule_verification")
        is True,
        "max_open_positions_one": _number_lte(
            owner_input.get("max_open_positions", 1), 1
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
        "slippage_guard_reviewed": owner_input.get("slippage_guard_review") is True,
        "market_open_reviewed": owner_input.get("market_open_review") is True,
        "idempotency_key_required": owner_input.get("idempotency_key_required") is True,
        "stale_price_block_required": owner_input.get("stale_price_block_required")
        is True,
        "duplicate_order_block_required": owner_input.get(
            "duplicate_order_block_required"
        )
        is True,
        "kill_switch_verified": (
            owner_input.get("kill_switch_verification") is True
            and owner_input.get("kill_switch_state") == "ARMED_UNTRIGGERED"
        ),
        "audit_record_required": owner_input.get("audit_record_ready") is True
        or owner_input.get("audit_record_required") is True,
        "final_owner_run_handoff_review_marked": owner_input.get(
            "final_owner_execution_gate_review"
        )
        is True,
        "demo_order_placement_authorized_is_false": (
            owner_input.get("demo_order_placement_authorized", False) is False
            and p9_result.get("demo_order_placement_authorized") is False
        ),
        "broker_api_access_authorized_is_false": (
            owner_input.get("broker_api_access_authorized", False) is False
            and p9_result.get("broker_api_access_authorized") is False
        ),
        "credential_access_authorized_is_false": (
            owner_input.get("credential_access_authorized", False) is False
            and p9_result.get("credential_access_authorized") is False
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


def _passed_requirements(checks: dict[str, bool]) -> list[str]:
    return [name for name, passed in checks.items() if passed]


def _failed_requirements(checks: dict[str, bool]) -> list[str]:
    return [name for name, passed in checks.items() if not passed]


def _enforce_forbidden_authorities(owner_input: dict[str, Any]) -> bool:
    return (
        owner_input.get("broker_api_access_authorized", False) is False
        and owner_input.get("credential_access_authorized", False) is False
        and owner_input.get("broker_api_connection_authorized_now", False) is False
        and owner_input.get("credential_access_authorized_now", False) is False
        and owner_input.get("order_submission_authorized_now", False) is False
        and owner_input.get("demo_order_placement_authorized", False) is False
        and owner_input.get("live_trading_authorized", False) is False
        and owner_input.get("money_movement_authorized", False) is False
        and owner_input.get("autonomy_approval", False) is False
        and _no_forbidden_inputs(owner_input)
    )


def _p10_blocked_owner_input(p9_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": p9_result.get("post_p9_score", 80),
        "post_p10_score": 100,
        "p9_execution_gate_status": p9_result.get("p9_execution_gate_status"),
        "p9_execution_gate_status_observed": p9_result.get("p9_execution_gate_status"),
        "protected_demo_order_gate_status_observed": p9_result.get(
            "protected_demo_order_gate_status"
        ),
        "p10_handoff_status": "P10_HANDOFF_BLOCKED_OWNER_INPUT_REQUIRED",
        "owner_run_handoff_status": "NOT_READY",
        "next_required_lane": "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT",
        "owner_run_handoff_packet_created": False,
        "owner_run_handoff_packet": {},
        "handoff_checks": _empty_checks(),
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
        "final_owner_sentence": DEFAULT_BLOCKED_OWNER_SENTENCE,
    }


def _p10_blocked_p9_not_ready(p9_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": p9_result.get("post_p9_score", 80),
        "post_p10_score": 80,
        "p9_execution_gate_status": p9_result.get("p9_execution_gate_status"),
        "p9_execution_gate_status_observed": p9_result.get("p9_execution_gate_status"),
        "protected_demo_order_gate_status_observed": p9_result.get(
            "protected_demo_order_gate_status"
        ),
        "p10_handoff_status": "P10_HANDOFF_BLOCKED_P9_REPAIR_REQUIRED",
        "owner_run_handoff_status": "NOT_READY",
        "next_required_lane": "P9_PROTECTED_EXECUTION_GATE_REPAIR_REVIEW",
        "owner_run_handoff_packet_created": False,
        "owner_run_handoff_packet": {},
        "handoff_checks": _empty_checks(),
        "passed_requirements": [],
        "failed_requirements": ["p9_execution_gate_ready"],
        "blocked_actions": list(BLOCKED_ACTIONS),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
        "trader_meaning": TRADER_MEANING,
        "final_owner_sentence": P9_REPAIR_FINAL_OWNER_SENTENCE,
    }


def _p10_review_failed(
    p9_result: dict[str, Any],
    packet: dict[str, Any],
    checks: dict[str, bool],
    passed_requirements: list[str],
    failed_requirements: list[str],
) -> dict[str, Any]:
    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": p9_result.get("post_p9_score", 80),
        "post_p10_score": 80,
        "p9_execution_gate_status": p9_result.get("p9_execution_gate_status"),
        "p9_execution_gate_status_observed": p9_result.get("p9_execution_gate_status"),
        "protected_demo_order_gate_status_observed": p9_result.get(
            "protected_demo_order_gate_status"
        ),
        "p10_handoff_status": "P10_HANDOFF_FAILED_REPAIR_REQUIRED",
        "owner_run_handoff_status": "NOT_READY",
        "next_required_lane": "P10_OWNER_RUN_HANDOFF_REPAIR_REVIEW",
        "owner_run_handoff_packet_created": bool(packet),
        "owner_run_handoff_packet": deepcopy(packet),
        "handoff_checks": checks,
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
        "final_owner_sentence": P10_REPAIR_FINAL_OWNER_SENTENCE,
    }


def _p10_ready(
    p9_result: dict[str, Any],
    packet: dict[str, Any],
    checks: dict[str, bool],
    passed_requirements: list[str],
    failed_requirements: list[str],
) -> dict[str, Any]:
    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": p9_result.get("post_p9_score", 80),
        "post_p10_score": 100,
        "p9_execution_gate_status": p9_result.get("p9_execution_gate_status"),
        "p9_execution_gate_status_observed": p9_result.get("p9_execution_gate_status"),
        "protected_demo_order_gate_status_observed": p9_result.get(
            "protected_demo_order_gate_status"
        ),
        "p10_handoff_status": "P10_OWNER_CONTROLLED_PROTECTED_DEMO_ORDER_RUN_HANDOFF_PREPARED_FOR_P11_REVIEW",
        "owner_run_handoff_status": "P11_READY",
        "next_required_lane": "P11_EXPLICIT_OWNER_APPROVED_PROTECTED_DEMO_ORDER_RUN_PACKET_REVIEW",
        "owner_run_handoff_packet_created": True,
        "owner_run_handoff_packet": deepcopy(packet),
        "handoff_checks": checks,
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
        "final_owner_sentence": P10_PASSED_FINAL_OWNER_SENTENCE,
    }


def evaluate_c1_owner_controlled_protected_demo_order_run_handoff_preparation(
    owner_input: dict[str, Any] | None = None
) -> dict[str, Any]:
    if owner_input is None:
        return _p10_blocked_owner_input(evaluate_p9_review())

    p9_result = evaluate_p9_review(owner_input)

    if (
        p9_result.get("p9_execution_gate_status")
        != "P9_PROTECTED_SUPERVISED_DEMO_ORDER_EXECUTION_GATE_PASSED_FOR_P10_OWNER_RUN_HANDOFF"
        or p9_result.get("protected_demo_order_gate_status") != "P10_READY"
    ):
        return _p10_blocked_p9_not_ready(p9_result)

    if not _enforce_forbidden_authorities(owner_input):
        handoff_packet = {}
        handoff_checks = _evaluate_p10_checks(owner_input, p9_result, handoff_packet)
        passed_requirements = _passed_requirements(handoff_checks)
        failed_requirements = _failed_requirements(handoff_checks)
        return _p10_review_failed(
            p9_result,
            handoff_packet,
            handoff_checks,
            passed_requirements,
            failed_requirements,
        )

    handoff_packet = _build_owner_run_handoff_contract(owner_input)
    handoff_checks = _evaluate_p10_checks(owner_input, p9_result, handoff_packet)
    passed_requirements = _passed_requirements(handoff_checks)
    failed_requirements = _failed_requirements(handoff_checks)
    if failed_requirements:
        return _p10_review_failed(
            p9_result,
            handoff_packet,
            handoff_checks,
            passed_requirements,
            failed_requirements,
        )

    return _p10_ready(
        p9_result,
        handoff_packet,
        handoff_checks,
        passed_requirements,
        failed_requirements,
    )


def _table_rows(mapping: dict[str, Any]) -> str:
    if not mapping:
        return "- none"
    lines = ["| field | value |", "|---|---|"]
    for key, value in mapping.items():
        lines.append(f"| `{key}` | `{value}` |")
    return "\n".join(lines)


def _bullet_lines(items: list[str] | tuple[str, ...]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def render_owner_report(result: dict[str, Any]) -> str:
    return f"""# AIOS Forex C1 Owner Controlled Protected Demo Order Run Handoff Preparation V1 Report

## Campaign Scope

This report applies to the P10 owner-controlled protected demo-order run handoff
preparation lane for `c1-eur-buy` only. It consumes the P9 execution-gate review
result and prepares an inert owner-run handoff packet for later explicit owner
approval.

This report does not access brokers, credentials, accounts, API connections, order
placement, live routing, money movement, production, or autonomy.

## Trader Meaning

{TRADER_MEANING}

## P9 Entry Condition

- p9_execution_gate_status: `{result['p9_execution_gate_status']}`
- p9_execution_gate_status_observed: `{result['p9_execution_gate_status_observed']}`
- protected_demo_order_gate_status_observed: `{result['protected_demo_order_gate_status_observed']}`

## Owner Run Handoff Packet

{_table_rows(result['owner_run_handoff_packet'])}

## Handoff Checks

{_table_rows(result['handoff_checks'])}

## Passed Requirements

{_bullet_lines(result['passed_requirements'])}

## Failed Requirements

{_bullet_lines(result['failed_requirements'])}

## Blocked Actions

{_bullet_lines(result['blocked_actions'])}

## P11 Readiness Decision

- p10_handoff_status: `{result['p10_handoff_status']}`
- owner_run_handoff_status: `{result['owner_run_handoff_status']}`
- post_p10_score: `{result['post_p10_score']}`
- next_required_lane: `{result['next_required_lane']}`
- demo_order_placement_authorized: `{result['demo_order_placement_authorized']}`
- broker_api_access_authorized: `{result['broker_api_access_authorized']}`
- credential_access_authorized: `{result['credential_access_authorized']}`

## Next Required Lane

`{result['next_required_lane']}`

## What This Completes

- creates the deterministic P10 owner-controlled protected demo-order run handoff preparation layer
- verifies owner-run handoff controls for EUR/USD BUY in demo-only conditions
- routes a passing handoff packet to P11 for explicit owner review
- keeps broker/API, credentials, demo-order placement, live trading, money movement, and autonomy blocked until explicit review

## What This Does Not Approve

- actual order placement
- live order authorization
- real account access
- broker/API access
- credential access
- scheduler or daemon execution
- webhook or production activation
- autonomy approval

## Final Owner Sentence

{result['final_owner_sentence']}
"""


def render_next_action_queue(result: dict[str, Any]) -> str:
    if result["p10_handoff_status"] == (
        "P10_OWNER_CONTROLLED_PROTECTED_DEMO_ORDER_RUN_HANDOFF_PREPARED_FOR_P11_REVIEW"
    ):
        required_next_actions = [
            "start P11 explicit owner-approved protected demo-order run packet review",
            "keep broker/API access blocked until P11 explicitly reviews and authorizes connection handling",
            "keep credentials blocked until P11 explicitly reviews credential-handling requirements",
            "keep demo-order placement blocked until P11 and owner-run packet authorize the run",
            "keep live trading blocked",
            "keep money movement blocked",
        ]
    else:
        required_next_actions = [
            "supply sanitized owner input through P6B",
            "validate owner input through P6C",
            "build final review card through P6D",
            "rerun P7 dry-run/mock rehearsal",
            "rerun P8 broker/account readiness bridge",
            "rerun P9 protected execution gate review",
            "rerun P10 owner-run handoff preparation",
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

    return f"""# AIOS Forex C1 Owner Controlled Protected Demo Order Run Handoff Preparation Next Action Queue V1

## Purpose

This queue records the next action after the P10 owner-controlled protected demo-order
run handoff preparation step.

## P10 Handoff Status

`{result['p10_handoff_status']}`

## Owner Run Handoff Status

`{result['owner_run_handoff_status']}`

## Passed Requirements

{_bullet_lines(result['passed_requirements'])}

## Failed Requirements

{_bullet_lines(result['failed_requirements'])}

## Next Required Lane

`{result['next_required_lane']}`

## Required Next Actions

{_bullet_lines(required_next_actions)}

## Remaining Blocks

{_bullet_lines(remaining_blocks)}

## Final Owner Sentence

{result['final_owner_sentence']}
"""


__all__ = [
    "evaluate_c1_owner_controlled_protected_demo_order_run_handoff_preparation",
    "render_owner_report",
    "render_next_action_queue",
]

