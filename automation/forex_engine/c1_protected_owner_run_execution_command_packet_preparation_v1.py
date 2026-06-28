"""Deterministic C1 protected owner-run execution command packet preparation.

This module consumes the P11 explicit owner-approved protected demo-order run packet
review output and prepares an inert protected owner-run execution command packet
for the EUR/USD BUY setup. It does not access brokers, credentials, accounts,
APIs, schedulers, daemons, webhooks, production systems, or any order-routing
path.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from automation.forex_engine.c1_explicit_owner_approved_protected_demo_order_run_packet_review_v1 import (
    evaluate_c1_explicit_owner_approved_protected_demo_order_run_packet_review as evaluate_p11_packet_review,
)


CAMPAIGN_ID = (
    "AIOS-FOREX-P12-C1-PROTECTED-OWNER-RUN-EXECUTION-COMMAND-PACKET-PREPARATION-V1"
)
CANDIDATE_ID = "c1-eur-buy"
CANDIDATE_NAME = "paper_long_run_supervisor_v2 LONG EURUSD"

TRADER_MEANING = (
    "AIOS is creating a protected owner-run execution command packet preparation "
    "artifact for the EUR/USD buy setup so it can verify command-packet readiness "
    "before any protected demo-order command release review is considered."
)

DEFAULT_BLOCKED_OWNER_SENTENCE = (
    "P12 is waiting for validated owner input and no broker/API, credential, or "
    "demo-order authority is authorized."
)

P12_VALID_STATUS = (
    "P12_PROTECTED_OWNER_RUN_EXECUTION_COMMAND_PACKET_PREPARED_FOR_P13_RELEASE_REVIEW"
)
P12_BLOCKED_OWNER_INPUT = "P12_COMMAND_PACKET_BLOCKED_OWNER_INPUT_REQUIRED"
P12_BLOCKED_P11_REPAIR = "P12_COMMAND_PACKET_BLOCKED_P11_REPAIR_REQUIRED"
P12_FAILED = "P12_COMMAND_PACKET_FAILED_REPAIR_REQUIRED"

P11_READY_STATUS = (
    "P11_EXPLICIT_OWNER_APPROVED_PROTECTED_DEMO_ORDER_RUN_PACKET_REVIEW_PASSED_FOR_P12_PREPARATION"
)

BLOCKED_ACTIONS = [
    "demo-order placement authorization",
    "live trading",
    "broker/API access",
    "credential access",
    "execution command authorization",
    "order-placement execution",
    "order closure",
    "money movement",
    "autonomy approval",
]

FORBIDDEN_ACTIONS = [
    "demo-order placement",
    "live trading",
    "broker/API access",
    "credential access",
    "execution command execution",
    "money movement",
    "autonomy approval",
]

FORBIDDEN_P12_INPUT_FIELDS = (
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

GATE_CHECK_NAMES = [
    "p11_packet_review_ready",
    "protected_execution_command_packet_created",
    "owner_decision_approved",
    "candidate_id_confirmed",
    "instrument_is_eur_usd",
    "side_is_buy",
    "demo_environment_only",
    "order_type_selected",
    "owner_control_required",
    "protected_owner_command_release_review_required",
    "explicit_owner_command_packet_required",
    "protected_command_dry_run_required",
    "credential_handling_review_marked",
    "broker_connection_review_marked",
    "broker_api_connection_authorized_now_is_false",
    "credential_access_authorized_now_is_false",
    "order_submission_authorized_now_is_false",
    "execution_command_authorized_now_is_false",
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
    "final_protected_execution_command_packet_review_marked",
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
    return all(name not in owner_input for name in FORBIDDEN_P12_INPUT_FIELDS)


def _enforce_forbidden_authorities(owner_input: dict[str, Any]) -> bool:
    safe_false_ok = (
        owner_input.get("broker_api_access_authorized", False) is False
        and owner_input.get("credential_access_authorized", False) is False
        and owner_input.get("broker_api_connection_authorized_now", False) is False
        and owner_input.get("credential_access_authorized_now", False) is False
        and owner_input.get("order_submission_authorized_now", False) is False
        and owner_input.get("execution_command_authorized_now", False) is False
        and owner_input.get("demo_order_placement_authorized", False) is False
        and owner_input.get("live_trading_authorized", False) is False
        and owner_input.get("money_movement_authorized", False) is False
        and owner_input.get("autonomy_approval", False) is False
        and _no_forbidden_inputs(owner_input)
    )
    return safe_false_ok


def _build_protected_execution_command_packet(owner_input: dict[str, Any]) -> dict[str, Any]:
    return {
        "protected_execution_command_packet_type": "INERT_PROTECTED_OWNER_RUN_EXECUTION_COMMAND_PACKET_PREPARATION_ONLY",
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "instrument": "EUR_USD",
        "side": "BUY",
        "demo_environment_only": True,
        "broker_environment_observed": "DEMO_OR_PRACTICE_ONLY",
        "order_type_selection": owner_input.get("order_type_selection", "MARKET"),
        "owner_control_required": owner_input.get("owner_control_required", True) is True,
        "protected_owner_command_release_review_required": owner_input.get(
            "protected_owner_command_release_review"
        )
        is True,
        "explicit_owner_command_packet_required": owner_input.get(
            "explicit_owner_command_packet_required"
        )
        is True,
        "protected_command_dry_run_required": owner_input.get("protected_command_dry_run_required")
        is True,
        "credential_handling_review_required": True,
        "broker_connection_review_required": True,
        "broker_api_connection_authorized_now": owner_input.get(
            "broker_api_connection_authorized_now"
        )
        is False,
        "credential_access_authorized_now": owner_input.get("credential_access_authorized_now")
        is False,
        "order_submission_authorized_now": owner_input.get("order_submission_authorized_now")
        is False,
        "execution_command_authorized_now": owner_input.get(
            "execution_command_authorized_now"
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
        "max_risk_per_trade_percent": owner_input.get(
            "max_risk_per_trade_percent", 0.25
        ),
        "max_daily_loss_percent": 1.00,
        "max_weekly_loss_percent": 2.00,
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
        "kill_switch_verified": owner_input.get("kill_switch_verification") is True
        and owner_input.get("kill_switch_state") == "ARMED_UNTRIGGERED",
        "audit_record_required": owner_input.get("audit_record_ready") is True
        or owner_input.get("audit_record_required") is True,
        "final_protected_execution_command_packet_review_required": owner_input.get(
            "final_protected_execution_command_packet_review"
        )
        is True,
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
    }


def _evaluate_p12_checks(
    owner_input: dict[str, Any], p11_result: dict[str, Any], packet: dict[str, Any]
) -> dict[str, bool]:
    return {
        "p11_packet_review_ready": (
            p11_result.get("p11_packet_review_status") == P11_READY_STATUS
            and p11_result.get("owner_run_packet_review_status") == "P12_READY"
        ),
        "protected_execution_command_packet_created": bool(packet),
        "owner_decision_approved": (
            owner_input.get("owner_decision") == "APPROVE_DEMO_INTENT"
        ),
        "candidate_id_confirmed": (
            owner_input.get("candidate_id", CANDIDATE_ID) == CANDIDATE_ID
        ),
        "instrument_is_eur_usd": (
            owner_input.get("intended_instrument_confirmation") == "EUR_USD"
        ),
        "side_is_buy": owner_input.get("intended_side_confirmation") == "BUY",
        "demo_environment_only": (
            owner_input.get("demo_account_marker") == "DEMO_ONLY"
            and owner_input.get("broker_environment") == "DEMO_OR_PRACTICE_ONLY"
        ),
        "order_type_selected": owner_input.get("order_type_selection") == "MARKET",
        "owner_control_required": owner_input.get("owner_control_required", True) is True,
        "protected_owner_command_release_review_required": owner_input.get(
            "protected_owner_command_release_review"
        )
        is True,
        "explicit_owner_command_packet_required": owner_input.get(
            "explicit_owner_command_packet_required"
        )
        is True,
        "protected_command_dry_run_required": owner_input.get(
            "protected_command_dry_run_required"
        )
        is True,
        "credential_handling_review_marked": owner_input.get("credential_handling_review")
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
        "execution_command_authorized_now_is_false": (
            owner_input.get("execution_command_authorized_now") is False
        ),
        "max_orders_per_signal_one": owner_input.get("one_order_rule_verification")
        is True,
        "max_open_positions_one": _number_lte(owner_input.get("max_open_positions", 1), 1),
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
        "final_protected_execution_command_packet_review_marked": owner_input.get(
            "final_protected_execution_command_packet_review"
        )
        is True,
        "demo_order_placement_authorized_is_false": (
            owner_input.get("demo_order_placement_authorized", False) is False
            and packet["demo_order_placement_authorized"] is False
        ),
        "broker_api_access_authorized_is_false": (
            owner_input.get("broker_api_access_authorized", False) is False
            and packet["broker_api_access_authorized"] is False
        ),
        "credential_access_authorized_is_false": (
            owner_input.get("credential_access_authorized", False) is False
            and packet["credential_access_authorized"] is False
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


def _p12_blocked_owner_input(p11_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": p11_result.get("post_p11_score", 100),
        "post_p12_score": 100,
        "p11_packet_review_status": p11_result.get("p11_packet_review_status"),
        "p11_packet_review_status_observed": p11_result.get("p11_packet_review_status"),
        "owner_run_packet_review_status_observed": p11_result.get(
            "owner_run_packet_review_status"
        ),
        "p12_command_packet_status": P12_BLOCKED_OWNER_INPUT,
        "protected_owner_command_status": "NOT_READY",
        "next_required_lane": "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT",
        "protected_execution_command_packet_created": False,
        "protected_execution_command_packet": {},
        "command_packet_checks": _empty_checks(),
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


def _p12_blocked_p11_not_ready(
    p11_result: dict[str, Any], checks: dict[str, bool] | None = None, failed: list[str] | None = None
) -> dict[str, Any]:
    if checks is None:
        checks = _empty_checks()
    if failed is None:
        failed = ["p11_packet_review_ready"]
    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": p11_result.get("post_p11_score", 80),
        "post_p12_score": 80,
        "p11_packet_review_status": p11_result.get("p11_packet_review_status"),
        "p11_packet_review_status_observed": p11_result.get("p11_packet_review_status"),
        "owner_run_packet_review_status_observed": p11_result.get(
            "owner_run_packet_review_status"
        ),
        "p12_command_packet_status": P12_BLOCKED_P11_REPAIR,
        "protected_owner_command_status": "NOT_READY",
        "next_required_lane": "P11_PROTECTED_OWNER_RUN_PACKET_REVIEW_REPAIR",
        "protected_execution_command_packet_created": False,
        "protected_execution_command_packet": {},
        "command_packet_checks": checks,
        "passed_requirements": [],
        "failed_requirements": failed,
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


def _p12_failed_requirements(
    p11_result: dict[str, Any],
    packet: dict[str, Any],
    checks: dict[str, bool],
    failed: list[str],
) -> dict[str, Any]:
    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": p11_result.get("post_p11_score", 80),
        "post_p12_score": 80,
        "p11_packet_review_status": p11_result.get("p11_packet_review_status"),
        "p11_packet_review_status_observed": p11_result.get("p11_packet_review_status"),
        "owner_run_packet_review_status_observed": p11_result.get(
            "owner_run_packet_review_status"
        ),
        "p12_command_packet_status": P12_FAILED,
        "protected_owner_command_status": "NOT_READY",
        "next_required_lane": "P12_EXECUTION_COMMAND_PACKET_REPAIR_REVIEW",
        "protected_execution_command_packet_created": bool(packet),
        "protected_execution_command_packet": deepcopy(packet),
        "command_packet_checks": checks,
        "passed_requirements": _passed_requirements(checks),
        "failed_requirements": failed,
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


def _p12_ready(
    p11_result: dict[str, Any],
    packet: dict[str, Any],
    checks: dict[str, bool],
) -> dict[str, Any]:
    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": p11_result.get("post_p11_score", 100),
        "post_p12_score": 100,
        "p11_packet_review_status": p11_result.get("p11_packet_review_status"),
        "p11_packet_review_status_observed": p11_result.get("p11_packet_review_status"),
        "owner_run_packet_review_status_observed": p11_result.get(
            "owner_run_packet_review_status"
        ),
        "p12_command_packet_status": P12_VALID_STATUS,
        "protected_owner_command_status": "P13_READY",
        "next_required_lane": "P13_OWNER_RUN_PROTECTED_DEMO_ORDER_COMMAND_RELEASE_REVIEW",
        "protected_execution_command_packet_created": True,
        "protected_execution_command_packet": deepcopy(packet),
        "command_packet_checks": checks,
        "passed_requirements": _passed_requirements(checks),
        "failed_requirements": [],
        "blocked_actions": list(BLOCKED_ACTIONS),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
        "trader_meaning": TRADER_MEANING,
        "final_owner_sentence": "AIOS Forex P12 C1 protected owner-run execution command packet preparation creation is complete locally: the EUR/USD buy setup now has an inert protected execution command packet prepared for P13 owner-run protected demo-order command release review, while demo-order placement, live trading, broker/API, credentials, money movement, 22/6 autonomy, vacation/luxury mode, and 100-120 percent return claims remain blocked until separately proven and approved.",
    }


def evaluate_c1_protected_owner_run_execution_command_packet_preparation(
    owner_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if owner_input is None:
        return _p12_blocked_owner_input(evaluate_p11_packet_review())

    p11_result = evaluate_p11_packet_review(owner_input)

    if (
        p11_result.get("p11_packet_review_status") != P11_READY_STATUS
        or p11_result.get("owner_run_packet_review_status") != "P12_READY"
    ):
        p12_local_failed_requirements = []
        if owner_input.get("credential_handling_review") is not True:
            p12_local_failed_requirements.append("credential_handling_review_marked")
        if owner_input.get("broker_connection_review") is not True:
            p12_local_failed_requirements.append("broker_connection_review_marked")
        for field_name in (
            "broker_api_access_authorized",
            "credential_access_authorized",
            "broker_api_connection_authorized_now",
            "credential_access_authorized_now",
            "order_submission_authorized_now",
            "execution_command_authorized_now",
            "demo_order_placement_authorized",
            "live_trading_authorized",
            "money_movement_authorized",
            "autonomy_approval",
        ):
            if owner_input.get(field_name, False) is True:
                p12_local_failed_requirements.append(f"{field_name}_must_be_false")
        if p12_local_failed_requirements:
            return _p12_failed_requirements(
                p11_result,
                {},
                _empty_checks(),
                p12_local_failed_requirements,
            )
        return _p12_blocked_p11_not_ready(p11_result)

    if not _enforce_forbidden_authorities(owner_input):
        return _p12_failed_requirements(
            p11_result,
            {},
            _empty_checks(),
            ["owner_input_authorization_blocked"],
        )

    packet = _build_protected_execution_command_packet(owner_input)
    checks = _evaluate_p12_checks(owner_input, p11_result, packet)
    failed_requirements = _failed_requirements(checks)
    if failed_requirements:
        return _p12_failed_requirements(
            p11_result,
            packet,
            checks,
            failed_requirements,
        )

    return _p12_ready(p11_result, packet, checks)


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
    return f"""# AIOS Forex C1 Protected Owner Run Execution Command Packet Preparation V1 Report

## Campaign Scope

This report applies to P12 protected owner-run execution command packet preparation
for `c1-eur-buy` only.
It consumes the P11 explicit owner-approved protected demo-order run packet review
result and verifies command-packet readiness before protected demo-order command release
review can be prepared.

This report does not access brokers, credentials, accounts, API connections, order
placement, live routing, money movement, production, or autonomy.

## Trader Meaning

{TRADER_MEANING}

## P11 Entry Condition

- p11_packet_review_status: `{result['p11_packet_review_status']}`
- p11_packet_review_status_observed: `{result['p11_packet_review_status_observed']}`
- owner_run_packet_review_status_observed: `{result['owner_run_packet_review_status_observed']}`

## Protected Execution Command Packet

{_table_rows(result['protected_execution_command_packet'])}

## Command Packet Checks

{_table_rows(result['command_packet_checks'])}

## Passed Requirements

{_bullet_lines(result['passed_requirements'])}

## Failed Requirements

{_bullet_lines(result['failed_requirements'])}

## Blocked Actions

{_bullet_lines(result['blocked_actions'])}

## P13 Readiness Decision

- p12_command_packet_status: `{result['p12_command_packet_status']}`
- protected_owner_command_status: `{result['protected_owner_command_status']}`
- post_p12_score: `{result['post_p12_score']}`
- next_required_lane: `{result['next_required_lane']}`
- demo_order_placement_authorized: `{result['demo_order_placement_authorized']}`
- broker_api_access_authorized: `{result['broker_api_access_authorized']}`
- credential_access_authorized: `{result['credential_access_authorized']}`

## Next Required Lane

`{result['next_required_lane']}`

## What This Completes

- creates the deterministic P12 protected owner-run execution command packet preparation layer
- verifies owner-run command packet controls for EUR/USD BUY in demo-only conditions
- routes a passing packet to P13 owner-run protected demo-order command release review
- keeps broker/API, credentials, demo-order placement, live trading, money movement, and autonomy blocked until explicit command-path approval

## What This Does Not Approve

- actual order placement
- demo-order placement authorization
- live trading
- broker/API access
- credential access
- scheduler or daemon execution
- webhook or production activation
- autonomy approval

## Final Owner Sentence

{result['final_owner_sentence']}
"""


def render_next_action_queue(result: dict[str, Any]) -> str:
    if result["p12_command_packet_status"] == P12_VALID_STATUS:
        required_next_actions = [
            "start P13 owner-run protected demo-order command release review",
            "keep broker/API access blocked until P13 explicitly reviews connection release requirements",
            "keep credentials blocked until P13 explicitly reviews credential-handling requirements",
            "keep demo-order placement blocked until P13 and a later owner-run command authorize the command",
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
            "rerun P11 protected owner-run packet review",
            "rerun P12 protected command packet preparation",
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

    return f"""# AIOS Forex C1 Protected Owner Run Execution Command Packet Preparation Next Action Queue V1

## Purpose

This queue records the next action after the P12 protected owner-run execution command
packet preparation step.

## P12 Command Packet Status

`{result['p12_command_packet_status']}`

## Protected Owner Command Status

`{result['protected_owner_command_status']}`

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
    "evaluate_c1_protected_owner_run_execution_command_packet_preparation",
    "render_owner_report",
    "render_next_action_queue",
]
