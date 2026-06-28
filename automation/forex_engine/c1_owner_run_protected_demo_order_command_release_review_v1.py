"""Deterministic C1 owner-run protected demo-order command release review.

This module consumes P12 owner-run execution command packet preparation output and
builds an inert command release review artifact for the EUR/USD BUY setup.

It does not access brokers, credentials, accounts, APIs, schedulers, daemons,
webhooks, production systems, or any order-routing path.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from automation.forex_engine.c1_protected_owner_run_execution_command_packet_preparation_v1 import (
    evaluate_c1_protected_owner_run_execution_command_packet_preparation as evaluate_p12_packet_preparation,
)


CAMPAIGN_ID = (
    "AIOS-FOREX-P13-C1-OWNER-RUN-PROTECTED-DEMO-ORDER-COMMAND-RELEASE-REVIEW-V1"
)
CANDIDATE_ID = "c1-eur-buy"
CANDIDATE_NAME = "paper_long_run_supervisor_v2 LONG EURUSD"

TRADER_MEANING = (
    "AIOS is creating an owner-run protected demo-order command release review "
    "artifact for the EUR/USD buy setup so it can verify release-review readiness "
    "before final rehearsal and owner execution card preparation is considered."
)

DEFAULT_BLOCKED_OWNER_SENTENCE = (
    "P13 is waiting for validated owner input and no broker/API, credential, "
    "demo-order, or execution-command authority is authorized."
)

P13_RELEASE_REVIEW_BLOCKED_OWNER_INPUT_REQUIRED = (
    "P13_RELEASE_REVIEW_BLOCKED_OWNER_INPUT_REQUIRED"
)
P13_RELEASE_REVIEW_PASSED = (
    "P13_OWNER_RUN_PROTECTED_DEMO_ORDER_COMMAND_RELEASE_REVIEW_PASSED_FOR_P14_FINAL_REHEARSAL"
)
P13_RELEASE_REVIEW_BLOCKED_P12_REPAIR = (
    "P13_RELEASE_REVIEW_BLOCKED_P12_REPAIR_REQUIRED"
)
P13_RELEASE_REVIEW_FAILED_REPAIR = (
    "P13_RELEASE_REVIEW_FAILED_REPAIR_REQUIRED"
)

P12_VALID_STATUS = (
    "P12_PROTECTED_OWNER_RUN_EXECUTION_COMMAND_PACKET_PREPARED_FOR_P13_RELEASE_REVIEW"
)

P14_READY = "P14_READY"
NOT_READY = "NOT_READY"

BLOCKED_ACTIONS = [
    "demo-order placement authorization",
    "live trading",
    "broker/API access",
    "credential access",
    "execution command authorization",
    "execution command execution",
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

FORBIDDEN_P13_INPUT_FIELDS = (
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

RELEASE_CHECK_NAMES = [
    "p12_command_packet_ready",
    "protected_command_release_review_created",
    "owner_decision_approved",
    "candidate_id_confirmed",
    "instrument_is_eur_usd",
    "side_is_buy",
    "demo_environment_only",
    "order_type_selected",
    "owner_control_required",
    "protected_command_release_review_required",
    "protected_final_rehearsal_required",
    "owner_execution_card_required",
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
    "final_protected_command_release_review_marked",
    "demo_order_placement_authorized_is_false",
    "broker_api_access_authorized_is_false",
    "credential_access_authorized_is_false",
    "execution_command_authorized_is_false",
    "live_trading_blocked",
    "money_movement_blocked",
    "no_autonomy_approval",
]


def _empty_checks() -> dict[str, bool]:
    return {name: False for name in RELEASE_CHECK_NAMES}


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
    return all(name not in owner_input for name in FORBIDDEN_P13_INPUT_FIELDS)


def _enforce_forbidden_authorities(owner_input: dict[str, Any]) -> bool:
    safe_false_ok = (
        owner_input.get("broker_api_access_authorized", False) is False
        and owner_input.get("credential_access_authorized", False) is False
        and owner_input.get("broker_api_connection_authorized_now", False) is False
        and owner_input.get("credential_access_authorized_now", False) is False
        and owner_input.get("order_submission_authorized_now", False) is False
        and owner_input.get("execution_command_authorized_now", False) is False
        and owner_input.get("execution_command_authorized", False) is False
        and owner_input.get("demo_order_placement_authorized", False) is False
        and owner_input.get("live_trading_authorized", False) is False
        and owner_input.get("money_movement_authorized", False) is False
        and owner_input.get("autonomy_approval", False) is False
        and _no_forbidden_inputs(owner_input)
    )
    return safe_false_ok


def _build_release_review(owner_input: dict[str, Any]) -> dict[str, Any]:
    return {
        "protected_command_release_review_type": "INERT_PROTECTED_DEMO_ORDER_COMMAND_RELEASE_REVIEW_ONLY",
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "instrument": "EUR_USD",
        "side": "BUY",
        "demo_environment_only": True,
        "broker_environment_observed": "DEMO_OR_PRACTICE_ONLY",
        "order_type_selection": owner_input.get("order_type_selection", "MARKET"),
        "owner_control_required": owner_input.get("owner_control_required", True) is True,
        "protected_command_release_review_required": owner_input.get(
            "protected_owner_command_release_review",
            False,
        )
        is True,
        "protected_final_rehearsal_required": owner_input.get(
            "protected_final_rehearsal_required"
        )
        is True,
        "owner_execution_card_required": owner_input.get("owner_execution_card_required")
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
        "kill_switch_verified": (
            owner_input.get("kill_switch_verification") is True
            and owner_input.get("kill_switch_state") == "ARMED_UNTRIGGERED"
        ),
        "audit_record_required": owner_input.get("audit_record_ready") is True
        or owner_input.get("audit_record_required") is True,
        "final_protected_command_release_review_required": owner_input.get(
            "final_protected_command_release_review"
        )
        is True,
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "execution_command_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
    }


def _evaluate_release_checks(
    owner_input: dict[str, Any],
    p12_result: dict[str, Any],
    release_review: dict[str, Any],
) -> dict[str, bool]:
    return {
        "p12_command_packet_ready": (
            p12_result.get("p12_command_packet_status") == P12_VALID_STATUS
            and p12_result.get("protected_owner_command_status") == "P13_READY"
        ),
        "protected_command_release_review_created": bool(release_review),
        "owner_decision_approved": (
            owner_input.get("owner_decision") == "APPROVE_DEMO_INTENT"
        ),
        "candidate_id_confirmed": owner_input.get("candidate_id", CANDIDATE_ID) == CANDIDATE_ID,
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
        "protected_command_release_review_required": owner_input.get(
            "protected_owner_command_release_review"
        )
        is True,
        "protected_final_rehearsal_required": owner_input.get(
            "protected_final_rehearsal_required"
        )
        is True,
        "owner_execution_card_required": owner_input.get("owner_execution_card_required")
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
        "final_protected_command_release_review_marked": owner_input.get(
            "final_protected_command_release_review"
        )
        is True,
        "demo_order_placement_authorized_is_false": (
            owner_input.get("demo_order_placement_authorized", False) is False
            and release_review["demo_order_placement_authorized"] is False
        ),
        "broker_api_access_authorized_is_false": (
            owner_input.get("broker_api_access_authorized", False) is False
            and release_review["broker_api_access_authorized"] is False
        ),
        "credential_access_authorized_is_false": (
            owner_input.get("credential_access_authorized", False) is False
            and release_review["credential_access_authorized"] is False
        ),
        "execution_command_authorized_is_false": (
            owner_input.get("execution_command_authorized", False) is False
            and release_review["execution_command_authorized"] is False
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


def _p13_blocked_owner_input(p12_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": p12_result.get("post_p12_score", 100),
        "post_p13_score": 100,
        "p12_command_packet_status": p12_result.get("p12_command_packet_status"),
        "p12_command_packet_status_observed": p12_result.get("p12_command_packet_status"),
        "protected_owner_command_status_observed": p12_result.get(
            "protected_owner_command_status"
        ),
        "p13_release_review_status": P13_RELEASE_REVIEW_BLOCKED_OWNER_INPUT_REQUIRED,
        "protected_command_release_status": NOT_READY,
        "next_required_lane": "P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT",
        "protected_command_release_review_created": False,
        "protected_command_release_review": {},
        "release_review_checks": _empty_checks(),
        "passed_requirements": [],
        "failed_requirements": ["owner_input_required"],
        "blocked_actions": list(BLOCKED_ACTIONS),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "execution_command_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
        "trader_meaning": TRADER_MEANING,
        "final_owner_sentence": DEFAULT_BLOCKED_OWNER_SENTENCE,
    }


def _collect_p13_local_validation_failures(owner_input: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    for field_name in (
        "broker_api_access_authorized",
        "credential_access_authorized",
        "broker_api_connection_authorized_now",
        "credential_access_authorized_now",
        "order_submission_authorized_now",
        "execution_command_authorized_now",
        "execution_command_authorized",
        "demo_order_placement_authorized",
        "live_trading_authorized",
        "money_movement_authorized",
        "autonomy_approval",
    ):
        if owner_input.get(field_name, False) is True:
            failures.append(f"{field_name}_must_be_false")

    for field_name in (
        "protected_owner_command_release_review",
        "protected_command_release_review",
        "protected_final_rehearsal_required",
        "owner_execution_card_required",
        "credential_handling_review",
        "broker_connection_review",
        "final_protected_command_release_review",
    ):
        if owner_input.get(field_name, False) is not True:
            failures.append(f"{field_name}_required")

    return failures


def _p13_blocked_p12_repair(
    p12_result: dict[str, Any],
    checks: dict[str, bool] | None = None,
    failed: list[str] | None = None,
) -> dict[str, Any]:
    if checks is None:
        checks = _empty_checks()
    if failed is None:
        failed = ["p12_command_packet_ready"]
    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": p12_result.get("post_p12_score", 80),
        "post_p13_score": 80,
        "p12_command_packet_status": p12_result.get("p12_command_packet_status"),
        "p12_command_packet_status_observed": p12_result.get("p12_command_packet_status"),
        "protected_owner_command_status_observed": p12_result.get(
            "protected_owner_command_status"
        ),
        "p13_release_review_status": P13_RELEASE_REVIEW_BLOCKED_P12_REPAIR,
        "protected_command_release_status": NOT_READY,
        "next_required_lane": "P12_EXECUTION_COMMAND_PACKET_REPAIR_REVIEW",
        "protected_command_release_review_created": False,
        "protected_command_release_review": {},
        "release_review_checks": checks,
        "passed_requirements": _passed_requirements(checks),
        "failed_requirements": failed,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "execution_command_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
        "trader_meaning": TRADER_MEANING,
        "final_owner_sentence": DEFAULT_BLOCKED_OWNER_SENTENCE,
    }


def _p13_failed(
    p12_result: dict[str, Any],
    release_review: dict[str, Any],
    checks: dict[str, bool],
    failed: list[str],
) -> dict[str, Any]:
    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": p12_result.get("post_p12_score", 80),
        "post_p13_score": 80,
        "p12_command_packet_status": p12_result.get("p12_command_packet_status"),
        "p12_command_packet_status_observed": p12_result.get("p12_command_packet_status"),
        "protected_owner_command_status_observed": p12_result.get(
            "protected_owner_command_status"
        ),
        "p13_release_review_status": P13_RELEASE_REVIEW_FAILED_REPAIR,
        "protected_command_release_status": NOT_READY,
        "next_required_lane": "P13_COMMAND_RELEASE_REVIEW_REPAIR",
        "protected_command_release_review_created": bool(release_review),
        "protected_command_release_review": deepcopy(release_review),
        "release_review_checks": checks,
        "passed_requirements": _passed_requirements(checks),
        "failed_requirements": failed,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "execution_command_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
        "trader_meaning": TRADER_MEANING,
        "final_owner_sentence": (
            "P13 found release-review gaps and is blocking inert command release review "
            "until a validated owner-run packet path is repaired."
        ),
    }


def _p13_passed(
    p12_result: dict[str, Any],
    release_review: dict[str, Any],
    checks: dict[str, bool],
) -> dict[str, Any]:
    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": p12_result.get("post_p12_score", 100),
        "post_p13_score": 100,
        "p12_command_packet_status": p12_result.get("p12_command_packet_status"),
        "p12_command_packet_status_observed": p12_result.get("p12_command_packet_status"),
        "protected_owner_command_status_observed": p12_result.get(
            "protected_owner_command_status"
        ),
        "p13_release_review_status": P13_RELEASE_REVIEW_PASSED,
        "protected_command_release_status": P14_READY,
        "next_required_lane": "P14_PROTECTED_DEMO_ORDER_COMMAND_FINAL_REHEARSAL_AND_OWNER_EXECUTION_CARD",
        "protected_command_release_review_created": True,
        "protected_command_release_review": deepcopy(release_review),
        "release_review_checks": checks,
        "passed_requirements": _passed_requirements(checks),
        "failed_requirements": [],
        "blocked_actions": list(BLOCKED_ACTIONS),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "execution_command_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
        "trader_meaning": TRADER_MEANING,
        "final_owner_sentence": "AIOS Forex P13 C1 owner-run protected demo-order command release review creation is complete locally: the EUR/USD buy setup now has an inert protected command release review prepared for P14 final rehearsal and owner execution card preparation, while demo-order placement, execution command, live trading, broker/API, credentials, money movement, 22/6 autonomy, vacation/luxury mode, and 100-120 percent return claims remain blocked until separately proven and approved.",
    }


def evaluate_c1_owner_run_protected_demo_order_command_release_review(
    owner_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    p12_result = (
        evaluate_p12_packet_preparation() if owner_input is None else evaluate_p12_packet_preparation(owner_input)
    )

    if owner_input is None:
        return _p13_blocked_owner_input(p12_result)

    p13_local_failures = _collect_p13_local_validation_failures(owner_input)
    if (
        p12_result.get("p12_command_packet_status") != P12_VALID_STATUS
        or p12_result.get("protected_owner_command_status") != "P13_READY"
    ):
        if p13_local_failures:
            return _p13_failed(p12_result, {}, _empty_checks(), p13_local_failures)
        return _p13_blocked_p12_repair(p12_result)

    if not _enforce_forbidden_authorities(owner_input):
        return _p13_failed(
            p12_result,
            {},
            _empty_checks(),
            ["safety_authority_blocked"],
        )

    release_review = _build_release_review(owner_input)
    checks = _evaluate_release_checks(owner_input, p12_result, release_review)
    failed_requirements = _failed_requirements(checks)

    if failed_requirements:
        return _p13_failed(
            p12_result,
            release_review,
            checks,
            failed_requirements,
        )

    return _p13_passed(p12_result, release_review, checks)


def _table_rows(mapping: dict[str, Any]) -> str:
    if not mapping:
        return "- none"
    lines = ["| field | value |", "|---|---|"]
    for key, value in mapping.items():
        lines.append(f"| `{key}` | `{value}` |")
    return "\n".join(lines)


def _bullet_lines(items: list[str]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def render_owner_report(result: dict[str, Any]) -> str:
    return f"""# AIOS Forex C1 Owner Run Protected Demo Order Command Release Review V1 Report

## Campaign Scope

This report applies to P13 owner-run protected demo-order command release review
for `c1-eur-buy` only.

It consumes the P12 owner-run protected execution command packet preparation
result and checks release-review readiness before the protected demo-order
command can move toward final rehearsal and owner execution card preparation.

This layer does not access brokers, credentials, accounts, API connections,
order placement, live routing, money movement, production, or autonomy.

## Trader Meaning

{TRADER_MEANING}

## P12 Entry Condition

- p12_command_packet_status: `{result['p12_command_packet_status']}`
- p12_command_packet_status_observed: `{result['p12_command_packet_status_observed']}`
- protected_owner_command_status_observed: `{result['protected_owner_command_status_observed']}`

## Protected Command Release Review

{_table_rows(result['protected_command_release_review'])}

## Release Review Checks

{_table_rows(result['release_review_checks'])}

## Passed Requirements

{_bullet_lines(result['passed_requirements'])}

## Failed Requirements

{_bullet_lines(result['failed_requirements'])}

## Blocked Actions

{_bullet_lines(result['blocked_actions'])}

## P14 Readiness Decision

- p13_release_review_status: `{result['p13_release_review_status']}`
- protected_command_release_status: `{result['protected_command_release_status']}`
- post_p13_score: `{result['post_p13_score']}`
- next_required_lane: `{result['next_required_lane']}`
- demo_order_placement_authorized: `{result['demo_order_placement_authorized']}`
- broker_api_access_authorized: `{result['broker_api_access_authorized']}`
- credential_access_authorized: `{result['credential_access_authorized']}`
- execution_command_authorized: `{result['execution_command_authorized']}`
- live_trading_blocked: `{result['live_trading_blocked']}`
- money_movement_blocked: `{result['money_movement_blocked']}`

## Next Required Lane

`{result['next_required_lane']}`

## What This Completes

- creates the deterministic P13 owner-run protected demo-order command release review artifact
- verifies release-review controls for EUR/USD BUY in demo-only conditions
- routes a passing review to P14 final rehearsal and owner execution card preparation
- keeps broker/API, credentials, demo-order placement, execution command, live trading,
  money movement, and autonomy blocked until explicit later packet approval

## What This Does Not Approve

- actual demo-order placement
- execution command authorization
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
    if result["p13_release_review_status"] == P13_RELEASE_REVIEW_PASSED:
        required_next_actions = [
            "start P14 protected demo-order command final rehearsal and owner execution card preparation",
            "keep broker/API access blocked until P14 explicitly reviews final command-card requirements",
            "keep credentials blocked until P14 explicitly reviews credential-handling requirements",
            "keep demo-order placement blocked until a later separately approved owner-run execution packet",
            "keep execution command blocked until a later separately approved owner-run execution packet",
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
            "rerun P13 protected command release review",
            "keep broker/API access blocked",
            "keep credentials blocked",
            "keep demo-order placement blocked",
            "keep execution command blocked",
        ]

    remaining_blocks = [
        "demo-order placement remains blocked",
        "execution command remains blocked",
        "live trading remains blocked",
        "broker/API access remains blocked",
        "credentials remain blocked",
        "money movement remains blocked",
        "autonomy approval remains false",
    ]

    return f"""# AIOS Forex C1 Owner Run Protected Demo Order Command Release Review Next Action Queue V1

## Purpose

This queue records the next action after the P13 owner-run protected demo-order
command release review step.

## P13 Release Review Status

`{result['p13_release_review_status']}`

## Protected Command Release Status

`{result['protected_command_release_status']}`

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
    "evaluate_c1_owner_run_protected_demo_order_command_release_review",
    "render_owner_report",
    "render_next_action_queue",
]
