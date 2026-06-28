"""Deterministic C1 demo-order intent owner-approval gate analyzer.

This module performs repo-local review-only evidence generation. It does not
access broker APIs, credentials, accounts, balances, live prices, orders,
schedulers, daemons, webhooks, production systems, or trading execution paths.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from automation.forex_engine.c1_supervised_demo_trade_readiness_review_v1 import (
    evaluate_c1_supervised_demo_trade_readiness_review,
)


CAMPAIGN_ID = "AIOS-FOREX-P6-C1-DEMO-ORDER-INTENT-OWNER-APPROVAL-GATE-V1"
CANDIDATE_ID = "c1-eur-buy"
CANDIDATE_NAME = "paper_long_run_supervisor_v2 LONG EURUSD"

TRADER_MEANING = (
    "AIOS is preparing a review-only demo-order intent card for the EUR/USD "
    "buy setup so the owner can inspect the proposed trade requirements before "
    "any demo order is allowed."
)

OWNER_ACTION_REQUIRED_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P6 C1 demo-order intent owner-approval gate is complete: "
    "c1-eur-buy has a review-only demo-order intent card prepared for owner "
    "decision, while demo-order placement, live trading, broker/API, "
    "credentials, money movement, 22/6 autonomy, vacation/luxury mode, and "
    "100-120 percent return claims remain blocked until separately proven and "
    "approved."
)

NOT_READY_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P6 C1 demo-order intent owner-approval gate is complete: "
    "c1-eur-buy is not cleared for owner action, and the next required lane is "
    "P5 repair or P6 owner-gate completion; demo-order placement, live "
    "trading, broker/API, credentials, money movement, 22/6 autonomy, "
    "vacation/luxury mode, and 100-120 percent return claims remain blocked "
    "until separately proven and approved."
)

P6_GATE_STATUSES = {
    "P6_DEMO_ORDER_INTENT_GATE_CREATED_OWNER_ACTION_REQUIRED",
    "P6_DEMO_ORDER_INTENT_GATE_BLOCKED_P5_REPAIR_REQUIRED",
    "P6_DEMO_ORDER_INTENT_GATE_BLOCKED_SAFETY_REQUIREMENTS",
}

OWNER_ACTION_STATUSES = {"OWNER_ACTION_REQUIRED", "NOT_READY"}

NEXT_REQUIRED_LANES = {
    "P6A_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_DECISION",
    "P6_CONTINUE_DEMO_ORDER_INTENT_GATE_REVIEW",
    "P5_SUPERVISED_DEMO_READINESS_REPAIR_REVIEW",
}

POST_P6_STATUSES = {
    "OWNER_ACTION_REQUIRED",
    "NEEDS_MORE_EVIDENCE",
    "REJECTED_P5_NOT_READY",
    "REJECTED_OWNER_GATE_INCOMPLETE",
    "REJECTED_DEMO_SAFETY_BOUNDARY",
}

REQUIRED_INTENT_CARD_FIELDS = [
    "candidate_id",
    "candidate_name",
    "intended_instrument",
    "intended_side",
    "order_type_status",
    "units_formula_only",
    "units_formula",
    "max_risk_per_trade_percent",
    "max_daily_loss_percent",
    "max_weekly_loss_percent",
    "max_open_positions",
    "max_orders_per_signal",
    "stop_loss_required",
    "take_profit_required",
    "minimum_reward_to_risk",
    "stop_loss_formula_required",
    "take_profit_formula_required",
    "sanitized_snapshot_required",
    "owner_approval_required",
    "owner_approval_status",
    "demo_order_placement_authorized",
    "live_trading_blocked",
    "broker_api_access_blocked",
    "credential_access_blocked",
    "money_movement_blocked",
    "one_order_rule_verification_required",
    "daily_stop_verification_required",
    "weekly_stop_verification_required",
    "kill_switch_verification_required",
    "audit_artifacts_required",
    "no_autonomy_approval",
]

P6_PASSED_REQUIREMENTS = [
    "p5_entry_condition",
    "p6_intent_card_fields",
    "sanitized_snapshot_requirement",
    "owner_approval_requirement",
    "demo_order_placement_block",
    "broker_api_credential_live_blocks",
    "one_order_verification_required",
    "tp_sl_verification_required",
    "stop_rule_verification_required",
    "kill_switch_verification_required",
    "audit_requirements_defined",
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
        "path": "automation/forex_engine/c1_supervised_demo_trade_readiness_review_v1.py",
        "use": "Provides the authoritative P5 supervised demo-readiness evaluator consumed by this P6 owner-approval gate.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_SUPERVISED_DEMO_TRADE_READINESS_REVIEW_V1.json",
        "use": "Records P5 review status, P6 readiness, score, failed requirements, and next lane.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_SUPERVISED_DEMO_TRADE_READINESS_REVIEW_V1_REPORT.md",
        "use": "Explains the source-backed P5 decision and preserves the no demo-order or live-trading boundary.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_SUPERVISED_DEMO_TRADE_READINESS_REVIEW_NEXT_ACTION_QUEUE_V1.md",
        "use": "Routes the source-cleared candidate into P6 demo-order intent owner-approval gate only.",
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


def _p5_policy(p5_result: dict[str, Any]) -> dict[str, Any]:
    return dict(p5_result.get("demo_readiness_policy", {}))


def _build_demo_order_intent_card(
    p5_result: dict[str, Any],
) -> dict[str, Any]:
    policy = _p5_policy(p5_result)
    return {
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "intended_instrument": "EUR_USD",
        "intended_side": "BUY",
        "order_type_status": "OWNER_SELECTION_REQUIRED",
        "units_formula_only": True,
        "units_formula": "units = risk_amount / stop_loss_value_per_unit",
        "max_risk_per_trade_percent": policy.get(
            "max_risk_per_trade_percent", 0.25
        ),
        "max_daily_loss_percent": policy.get("max_daily_loss_percent", 1.00),
        "max_weekly_loss_percent": policy.get("max_weekly_loss_percent", 2.00),
        "max_open_positions": policy.get("max_open_positions", 1),
        "max_orders_per_signal": policy.get("max_orders_per_signal", 1),
        "stop_loss_required": True,
        "take_profit_required": True,
        "minimum_reward_to_risk": policy.get("minimum_reward_to_risk", 1.20),
        "stop_loss_formula_required": True,
        "take_profit_formula_required": True,
        "sanitized_snapshot_required": True,
        "owner_approval_required": True,
        "owner_approval_status": "OWNER_ACTION_REQUIRED",
        "demo_order_placement_authorized": False,
        "live_trading_blocked": True,
        "broker_api_access_blocked": True,
        "credential_access_blocked": True,
        "money_movement_blocked": True,
        "one_order_rule_verification_required": True,
        "daily_stop_verification_required": True,
        "weekly_stop_verification_required": True,
        "kill_switch_verification_required": True,
        "audit_artifacts_required": [
            "P6 owner report",
            "P6 JSON evidence",
            "P6 next action queue",
            "owner-supplied sanitized broker/account snapshot",
            "owner approval decision record",
        ],
        "no_autonomy_approval": True,
    }


def _build_sanitized_snapshot_requirement() -> dict[str, Any]:
    return {
        "sanitized_broker_account_snapshot_required": True,
        "required_before_account_specific_units": True,
        "collected_in_this_packet": False,
        "requires_sanitized_broker_account_snapshot": True,
        "purpose": (
            "Provide enough demo-account state for owner review without "
            "exposing secrets, credentials, account identifiers, broker order "
            "identifiers, or private execution payloads."
        ),
        "allowed_snapshot_fields": [
            "demo-account marker",
            "sanitized equity value or bracket",
            "current open position count",
            "current same-signal order count",
            "daily realized loss percent",
            "weekly realized loss percent",
            "kill-switch state",
        ],
        "forbidden_snapshot_fields": [
            "API keys",
            "tokens",
            "passwords",
            "broker credentials",
            "account identifiers",
            "broker order identifiers",
            "raw live account data",
            "private execution payloads",
        ],
        "status": "OWNER_SUPPLIED_SANITIZED_SNAPSHOT_REQUIRED",
    }


def _build_owner_approval_requirement() -> dict[str, Any]:
    return {
        "owner_approval_required": True,
        "owner_approval_status": "OWNER_ACTION_REQUIRED",
        "approved_by_this_packet": False,
        "approval_granted": False,
        "required_before_any_demo_order": True,
        "demo_order_placement_authorized": False,
        "required_decision_fields": [
            "explicit owner approval decision",
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
        ],
        "approval_scope": "P6 demo-order intent owner-approval gate only",
    }


def _build_pre_order_safety_checks(
    card: dict[str, Any],
) -> dict[str, Any]:
    return {
        "status": "OWNER_ACTION_REQUIRED",
        "checks_required_before_any_later_demo_order": [
            "sanitized broker/account snapshot supplied by owner",
            "explicit owner approval decision recorded",
            "order type selected by owner",
            "units formula reviewed without account-specific sizing in this packet",
            "stop loss formula reviewed",
            "take profit formula reviewed",
            "reward-to-risk at or above minimum",
            "one-order rule verified",
            "daily-stop state verified",
            "weekly-stop state verified",
            "kill-switch state verified",
        ],
        "limits": {
            "max_risk_per_trade_percent": card["max_risk_per_trade_percent"],
            "max_daily_loss_percent": card["max_daily_loss_percent"],
            "max_weekly_loss_percent": card["max_weekly_loss_percent"],
            "max_open_positions": card["max_open_positions"],
            "max_orders_per_signal": card["max_orders_per_signal"],
            "minimum_reward_to_risk": card["minimum_reward_to_risk"],
        },
        "demo_order_placement_authorized": False,
        "broker_api_access_blocked": True,
        "credential_access_blocked": True,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
    }


def _build_one_order_verification(card: dict[str, Any]) -> dict[str, Any]:
    return {
        "one_order_rule_verification_required": True,
        "max_open_positions": card["max_open_positions"],
        "max_orders_per_signal": card["max_orders_per_signal"],
        "no_retry_loop": True,
        "owner_snapshot_required": True,
        "rule": (
            "Owner-supplied sanitized evidence must show no more than one open "
            "position and no more than one order for the same signal before any "
            "later demo-order authority can be considered."
        ),
    }


def _build_tp_sl_verification(card: dict[str, Any]) -> dict[str, Any]:
    return {
        "stop_loss_required": card["stop_loss_required"],
        "take_profit_required": card["take_profit_required"],
        "minimum_reward_to_risk": card["minimum_reward_to_risk"],
        "stop_loss_formula_required": card["stop_loss_formula_required"],
        "take_profit_formula_required": card["take_profit_formula_required"],
        "verification_required": True,
        "rule": (
            "Owner review must confirm stop loss, take profit, and at least "
            "1.20 reward-to-risk before any later demo-order authority can be "
            "considered."
        ),
    }


def _build_stop_rule_verification(card: dict[str, Any]) -> dict[str, Any]:
    return {
        "daily_stop_verification_required": True,
        "weekly_stop_verification_required": True,
        "max_daily_loss_percent": card["max_daily_loss_percent"],
        "max_weekly_loss_percent": card["max_weekly_loss_percent"],
        "owner_snapshot_required": True,
        "rule": (
            "Owner-supplied sanitized evidence must show daily and weekly loss "
            "state remains inside the defined limits before any later "
            "demo-order authority can be considered."
        ),
    }


def _build_kill_switch_verification() -> dict[str, Any]:
    return {
        "kill_switch_verification_required": True,
        "required_state": "active and untriggered before owner approval can continue",
        "owner_snapshot_required": True,
        "triggers": [
            "missing sanitized broker/account snapshot",
            "missing owner approval",
            "missing order type selection",
            "missing stop loss",
            "missing take profit",
            "reward-to-risk below 1.20",
            "risk per trade above 0.25 percent",
            "daily loss at or above 1.00 percent",
            "weekly loss at or above 2.00 percent",
            "more than one open position",
            "more than one order for the same signal",
            "credential, account, broker/API, order, scheduler, daemon, webhook, production, or autonomy path detected",
        ],
        "rule": (
            "Any trigger keeps the owner gate from advancing until repair "
            "evidence is generated and the relevant review lane is rerun."
        ),
    }


def _build_audit_requirements() -> dict[str, Any]:
    return {
        "audit_report_required": True,
        "manual_owner_review_required": True,
        "required_artifacts": [
            "P5 supervised demo-trade readiness JSON",
            "P5 supervised demo-trade readiness owner report",
            "P5 next action queue",
            "P6 owner report",
            "P6 JSON evidence",
            "P6 next action queue",
            "owner-supplied sanitized broker/account snapshot",
            "owner approval decision record",
        ],
        "must_exclude": [
            "secrets",
            "credentials",
            "account identifiers",
            "broker order identifiers",
            "private execution payloads",
        ],
    }


def _build_p6_entry_assessment(
    p5_result: dict[str, Any],
) -> dict[str, Any]:
    policy = _p5_policy(p5_result)
    snapshot = p5_result.get("snapshot_requirement", {})
    owner_gate = p5_result.get("owner_approval_gate", {})
    checks = {
        "p5_review_status": (
            p5_result.get("p5_review_status")
            == "P5_SUPERVISED_DEMO_READINESS_PASSED_FOR_P6_OWNER_APPROVAL"
        ),
        "p6_readiness": p5_result.get("p6_readiness") == "P6_READY",
        "post_p5_score": _safe_int(p5_result.get("post_p5_score")) == 100,
        "next_required_lane": (
            p5_result.get("next_required_lane")
            == "P6_DEMO_ORDER_INTENT_OWNER_APPROVAL_GATE"
        ),
        "failed_requirements_empty": not p5_result.get("failed_requirements", []),
        "sanitized_snapshot_required": (
            snapshot.get("sanitized_broker_account_snapshot_required") is True
            or policy.get("sanitized_broker_account_snapshot_required") is True
        ),
        "owner_approval_required": (
            owner_gate.get("owner_approval_required") is True
            or policy.get("owner_approval_required") is True
        ),
        "demo_order_placement_blocked": (
            policy.get("order_placement_blocked") is True
            and policy.get("no_demo_order_placement_in_this_packet") is True
        ),
        "broker_api_blocked": policy.get("broker_api_access_blocked") is True,
        "credential_access_blocked": (
            policy.get("credential_access_blocked") is True
        ),
        "live_trading_blocked": policy.get("live_trading_blocked") is True,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "observed": {
            "p5_review_status": p5_result.get("p5_review_status"),
            "p6_readiness": p5_result.get("p6_readiness"),
            "post_p5_score": p5_result.get("post_p5_score"),
            "next_required_lane": p5_result.get("next_required_lane"),
            "failed_requirements": list(p5_result.get("failed_requirements", [])),
            "demo_readiness_policy": deepcopy(policy),
            "snapshot_requirement": deepcopy(snapshot),
            "owner_approval_gate": deepcopy(owner_gate),
        },
    }


def _missing_intent_fields(card: dict[str, Any]) -> list[str]:
    return [field for field in REQUIRED_INTENT_CARD_FIELDS if field not in card]


def _owner_gate_safety_failures(
    card: dict[str, Any],
    snapshot_requirement: dict[str, Any],
    owner_approval_requirement: dict[str, Any],
    pre_order_safety_checks: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    missing_fields = _missing_intent_fields(card)
    if missing_fields:
        failures.append("p6_intent_card_fields")
    if snapshot_requirement.get("requires_sanitized_broker_account_snapshot") is not True:
        failures.append("sanitized_snapshot_requirement")
    if owner_approval_requirement.get("owner_approval_required") is not True:
        failures.append("owner_approval_requirement")
    if owner_approval_requirement.get("approved_by_this_packet") is not False:
        failures.append("owner_approval_not_granted_by_packet")
    if card.get("demo_order_placement_authorized") is not False:
        failures.append("demo_order_placement_block")
    if pre_order_safety_checks.get("broker_api_access_blocked") is not True:
        failures.append("broker_api_block")
    if pre_order_safety_checks.get("credential_access_blocked") is not True:
        failures.append("credential_access_block")
    if pre_order_safety_checks.get("live_trading_blocked") is not True:
        failures.append("live_trading_block")
    if pre_order_safety_checks.get("money_movement_blocked") is not True:
        failures.append("money_movement_block")
    if card.get("no_autonomy_approval") is not True:
        failures.append("no_autonomy_approval")
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


def _intent_card_lines(card: dict[str, Any]) -> str:
    rows = ["| field | value |", "|---|---|"]
    for field in REQUIRED_INTENT_CARD_FIELDS:
        rows.append(f"| `{field}` | `{card[field]}` |")
    return "\n".join(rows)


def evaluate_c1_demo_order_intent_owner_approval_gate() -> dict[str, Any]:
    """Return the source-backed C1 P6 owner-approval gate decision."""

    p5_result = evaluate_c1_supervised_demo_trade_readiness_review()
    input_score = _safe_int(p5_result.get("post_p5_score"))
    input_status = str(p5_result.get("post_p5_status", ""))
    p6_entry_assessment = _build_p6_entry_assessment(p5_result)
    demo_order_intent_card = _build_demo_order_intent_card(p5_result)
    sanitized_snapshot_requirement = _build_sanitized_snapshot_requirement()
    owner_approval_requirement = _build_owner_approval_requirement()
    pre_order_safety_checks = _build_pre_order_safety_checks(
        demo_order_intent_card
    )
    one_order_verification = _build_one_order_verification(demo_order_intent_card)
    tp_sl_verification = _build_tp_sl_verification(demo_order_intent_card)
    stop_rule_verification = _build_stop_rule_verification(demo_order_intent_card)
    kill_switch_verification = _build_kill_switch_verification()
    audit_requirements = _build_audit_requirements()
    owner_gate_failures = _owner_gate_safety_failures(
        demo_order_intent_card,
        sanitized_snapshot_requirement,
        owner_approval_requirement,
        pre_order_safety_checks,
    )

    if not p6_entry_assessment["passed"]:
        p6_gate_status = "P6_DEMO_ORDER_INTENT_GATE_BLOCKED_P5_REPAIR_REQUIRED"
        owner_action_status = "NOT_READY"
        next_required_lane = "P5_SUPERVISED_DEMO_READINESS_REPAIR_REVIEW"
        post_p6_score = min(input_score, 85)
        post_p6_status = "REJECTED_P5_NOT_READY"
        failed_requirements = [
            key
            for key, passed in p6_entry_assessment["checks"].items()
            if not passed
        ]
        passed_requirements: list[str] = []
        final_owner_sentence = NOT_READY_FINAL_OWNER_SENTENCE
    elif owner_gate_failures:
        p6_gate_status = "P6_DEMO_ORDER_INTENT_GATE_BLOCKED_SAFETY_REQUIREMENTS"
        owner_action_status = "NOT_READY"
        next_required_lane = "P6_CONTINUE_DEMO_ORDER_INTENT_GATE_REVIEW"
        post_p6_score = min(input_score, 90)
        post_p6_status = "REJECTED_OWNER_GATE_INCOMPLETE"
        failed_requirements = owner_gate_failures
        passed_requirements = [
            requirement
            for requirement in P6_PASSED_REQUIREMENTS
            if requirement not in owner_gate_failures
        ]
        final_owner_sentence = NOT_READY_FINAL_OWNER_SENTENCE
    else:
        p6_gate_status = "P6_DEMO_ORDER_INTENT_GATE_CREATED_OWNER_ACTION_REQUIRED"
        owner_action_status = "OWNER_ACTION_REQUIRED"
        next_required_lane = (
            "P6A_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_DECISION"
        )
        post_p6_score = 100
        post_p6_status = "OWNER_ACTION_REQUIRED"
        failed_requirements = []
        passed_requirements = list(P6_PASSED_REQUIREMENTS)
        final_owner_sentence = OWNER_ACTION_REQUIRED_FINAL_OWNER_SENTENCE

    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": input_score,
        "post_p6_score": post_p6_score,
        "input_status": input_status,
        "post_p6_status": post_p6_status,
        "p5_review_status": p5_result.get("p5_review_status"),
        "p5_p6_readiness": p5_result.get("p6_readiness"),
        "p6_gate_status": p6_gate_status,
        "owner_action_status": owner_action_status,
        "next_required_lane": next_required_lane,
        "p6_entry_assessment": deepcopy(p6_entry_assessment),
        "demo_order_intent_card": deepcopy(demo_order_intent_card),
        "sanitized_snapshot_requirement": deepcopy(
            sanitized_snapshot_requirement
        ),
        "owner_approval_requirement": deepcopy(owner_approval_requirement),
        "pre_order_safety_checks": deepcopy(pre_order_safety_checks),
        "one_order_verification": deepcopy(one_order_verification),
        "tp_sl_verification": deepcopy(tp_sl_verification),
        "stop_rule_verification": deepcopy(stop_rule_verification),
        "kill_switch_verification": deepcopy(kill_switch_verification),
        "audit_requirements": deepcopy(audit_requirements),
        "passed_requirements": passed_requirements,
        "failed_requirements": failed_requirements,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "forbidden_actions": list(BLOCKED_ACTIONS),
        "source_evidence": deepcopy(SOURCE_EVIDENCE),
        "trader_meaning": TRADER_MEANING,
        "final_owner_sentence": final_owner_sentence,
    }


def render_owner_report(result: dict[str, Any]) -> str:
    """Render the owner-facing P6 demo-order intent gate report."""

    card = result["demo_order_intent_card"]
    snapshot = result["sanitized_snapshot_requirement"]
    owner = result["owner_approval_requirement"]
    pre_order = result["pre_order_safety_checks"]
    one_order = result["one_order_verification"]
    tp_sl = result["tp_sl_verification"]
    stop_rules = result["stop_rule_verification"]
    kill_switch = result["kill_switch_verification"]
    audit = result["audit_requirements"]

    return f"""# AIOS Forex C1 Demo Order Intent Owner Approval Gate V1 Report

## Campaign Scope

This report applies the P6 C1 demo-order intent owner-approval gate for `c1-eur-buy` only. It consumes the P5 supervised demo-trade readiness output and prepares a review-only owner decision card.

This report does not execute trades, access broker/API systems, access credentials, access accounts, calculate live or account-specific position size, place demo orders, place live orders, close orders, move money, activate schedulers, activate daemons, activate webhooks, activate production, approve autonomous trading, or approve any demo-order placement.

## Trader Meaning

{TRADER_MEANING}

## Source Evidence

{_source_list(result)}

## P5 Entry Condition

- p5_review_status: `{result["p5_review_status"]}`
- p5_p6_readiness: `{result["p5_p6_readiness"]}`
- input_score: `{result["input_score"]}`
- input_status: `{result["input_status"]}`
- p6_entry_passed: `{result["p6_entry_assessment"]["passed"]}`

{_dict_lines(result["p6_entry_assessment"]["checks"])}

## Demo Order Intent Card

{_intent_card_lines(card)}

## Sanitized Snapshot Requirement

- sanitized_broker_account_snapshot_required: `{snapshot["sanitized_broker_account_snapshot_required"]}`
- required_before_account_specific_units: `{snapshot["required_before_account_specific_units"]}`
- collected_in_this_packet: `{snapshot["collected_in_this_packet"]}`
- requires_sanitized_broker_account_snapshot: `{snapshot["requires_sanitized_broker_account_snapshot"]}`
- purpose: {snapshot["purpose"]}
- allowed_snapshot_fields:
{_bullet_list(snapshot["allowed_snapshot_fields"])}
- forbidden_snapshot_fields:
{_bullet_list(snapshot["forbidden_snapshot_fields"])}
- status: `{snapshot["status"]}`

## Owner Approval Requirement

- owner_approval_required: `{owner["owner_approval_required"]}`
- owner_approval_status: `{owner["owner_approval_status"]}`
- approved_by_this_packet: `{owner["approved_by_this_packet"]}`
- approval_granted: `{owner["approval_granted"]}`
- required_before_any_demo_order: `{owner["required_before_any_demo_order"]}`
- demo_order_placement_authorized: `{owner["demo_order_placement_authorized"]}`
- approval_scope: {owner["approval_scope"]}
- required_decision_fields:
{_bullet_list(owner["required_decision_fields"])}

## Pre-Order Safety Checks

- status: `{pre_order["status"]}`
- demo_order_placement_authorized: `{pre_order["demo_order_placement_authorized"]}`
- broker_api_access_blocked: `{pre_order["broker_api_access_blocked"]}`
- credential_access_blocked: `{pre_order["credential_access_blocked"]}`
- live_trading_blocked: `{pre_order["live_trading_blocked"]}`
- money_movement_blocked: `{pre_order["money_movement_blocked"]}`
- no_autonomy_approval: `{pre_order["no_autonomy_approval"]}`
- checks_required_before_any_later_demo_order:
{_bullet_list(pre_order["checks_required_before_any_later_demo_order"])}

## One-Order Verification

- one_order_rule_verification_required: `{one_order["one_order_rule_verification_required"]}`
- max_open_positions: `{one_order["max_open_positions"]}`
- max_orders_per_signal: `{one_order["max_orders_per_signal"]}`
- no_retry_loop: `{one_order["no_retry_loop"]}`
- owner_snapshot_required: `{one_order["owner_snapshot_required"]}`
- rule: {one_order["rule"]}

## TP/SL Verification

- stop_loss_required: `{tp_sl["stop_loss_required"]}`
- take_profit_required: `{tp_sl["take_profit_required"]}`
- minimum_reward_to_risk: `{tp_sl["minimum_reward_to_risk"]}`
- stop_loss_formula_required: `{tp_sl["stop_loss_formula_required"]}`
- take_profit_formula_required: `{tp_sl["take_profit_formula_required"]}`
- verification_required: `{tp_sl["verification_required"]}`
- rule: {tp_sl["rule"]}

## Stop Rule Verification

- daily_stop_verification_required: `{stop_rules["daily_stop_verification_required"]}`
- weekly_stop_verification_required: `{stop_rules["weekly_stop_verification_required"]}`
- max_daily_loss_percent: `{stop_rules["max_daily_loss_percent"]}`
- max_weekly_loss_percent: `{stop_rules["max_weekly_loss_percent"]}`
- owner_snapshot_required: `{stop_rules["owner_snapshot_required"]}`
- rule: {stop_rules["rule"]}

## Kill Switch Verification

- kill_switch_verification_required: `{kill_switch["kill_switch_verification_required"]}`
- required_state: {kill_switch["required_state"]}
- owner_snapshot_required: `{kill_switch["owner_snapshot_required"]}`
- triggers:
{_bullet_list(kill_switch["triggers"])}
- rule: {kill_switch["rule"]}

## Audit Requirements

- audit_report_required: `{audit["audit_report_required"]}`
- manual_owner_review_required: `{audit["manual_owner_review_required"]}`
- required_artifacts:
{_bullet_list(audit["required_artifacts"])}
- must_exclude:
{_bullet_list(audit["must_exclude"])}

## Owner Action Status

`{result["owner_action_status"]}`

## Next Required Lane

`{result["next_required_lane"]}`

## What This Completes

- creates the P6 review-only demo-order intent card for `c1-eur-buy`
- defines the sanitized snapshot requirement and owner approval requirement
- preserves the one-order, TP/SL, stop-rule, kill-switch, audit, broker/API, credential, live-trading, money-movement, and autonomy blocks

## What This Does Not Approve

{_bullet_list(result["blocked_actions"])}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""


def render_next_action_queue(result: dict[str, Any]) -> str:
    """Render the next-action queue for the P6 owner-approval gate."""

    if result["owner_action_status"] == "OWNER_ACTION_REQUIRED":
        required_owner_inputs = [
            "sanitized broker/account snapshot",
            "explicit owner approval decision",
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
        ]
    else:
        required_owner_inputs = [
            "repair P5 readiness evidence or complete the P6 owner gate",
            "rerun this P6 gate after repair",
        ]

    remaining_blocks = [
        "demo-order placement remains blocked",
        "live trading remains blocked",
        "broker/API access remains blocked",
        "credentials remain blocked",
        "money movement remains blocked",
        "autonomous trading remains blocked",
    ]

    return f"""# AIOS Forex C1 Demo Order Intent Owner Approval Gate Next Action Queue V1

## Purpose

This queue records the owner action required after P6 C1 demo-order intent owner-approval gate creation.

## P6 Gate Status

`{result["p6_gate_status"]}`

## Owner Action Status

`{result["owner_action_status"]}`

## Passed Requirements

{_bullet_list([f"`{item}`" for item in result["passed_requirements"]])}

## Failed Requirements

{_bullet_list([f"`{item}`" for item in result["failed_requirements"]])}

## Next Required Lane

`{result["next_required_lane"]}`

## Required Owner Inputs

{_bullet_list(required_owner_inputs)}

## Remaining Blocks

{_bullet_list(remaining_blocks)}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""


__all__ = [
    "evaluate_c1_demo_order_intent_owner_approval_gate",
    "render_owner_report",
    "render_next_action_queue",
]
