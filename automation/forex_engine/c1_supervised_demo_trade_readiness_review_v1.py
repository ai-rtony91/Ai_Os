"""Deterministic C1 supervised demo-trade readiness review analyzer.

This module performs repo-local evidence review only. It does not access
broker APIs, credentials, accounts, balances, live prices, orders, schedulers,
daemons, webhooks, production systems, or trading execution paths.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from automation.forex_engine.c1_risk_position_sizing_review_v1 import (
    evaluate_c1_risk_position_sizing_review,
)


CAMPAIGN_ID = "AIOS-FOREX-P5-C1-SUPERVISED-DEMO-TRADE-READINESS-REVIEW-V1"
CANDIDATE_ID = "c1-eur-buy"
CANDIDATE_NAME = "paper_long_run_supervisor_v2 LONG EURUSD"

TRADER_MEANING = (
    "AIOS is checking whether the risk-controlled EUR/USD buy setup has the "
    "safety gates needed before the owner can review a supervised demo-order "
    "intent card."
)

P6_READY_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P5 C1 supervised demo-trade readiness review is complete: "
    "c1-eur-buy is source-cleared for P6 demo-order intent and owner-approval "
    "gate only, while demo order placement, live trading, broker/API, "
    "credentials, money movement, 22/6 autonomy, vacation/luxury mode, and "
    "100-120 percent return claims remain blocked until separately proven and "
    "approved."
)

NOT_READY_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P5 C1 supervised demo-trade readiness review is complete: "
    "c1-eur-buy is not cleared for P6 demo-order intent and owner-approval "
    "gate, and the next required lane is P4 repair or P5 readiness-rule "
    "completion; demo order placement, live trading, broker/API, credentials, "
    "money movement, 22/6 autonomy, vacation/luxury mode, and 100-120 percent "
    "return claims remain blocked until separately proven and approved."
)

P5_REVIEW_STATUSES = {
    "P5_SUPERVISED_DEMO_READINESS_PASSED_FOR_P6_OWNER_APPROVAL",
    "P5_SUPERVISED_DEMO_READINESS_FAILED_RULES_REQUIRED",
    "P5_SUPERVISED_DEMO_READINESS_FAILED_P4_REPAIR_REQUIRED",
}

P6_READINESS_VALUES = {"P6_READY", "NOT_READY"}

NEXT_REQUIRED_LANES = {
    "P6_DEMO_ORDER_INTENT_OWNER_APPROVAL_GATE",
    "P5_CONTINUE_SUPERVISED_DEMO_READINESS_REVIEW",
    "P4_RISK_POSITION_SIZING_REPAIR_REVIEW",
}

POST_P5_STATUSES = {
    "P6_READY",
    "NEEDS_MORE_EVIDENCE",
    "REJECTED_P4_NOT_READY",
    "REJECTED_DEMO_READINESS_RULES_INCOMPLETE",
    "REJECTED_DEMO_SAFETY_BOUNDARY",
}

REQUIRED_READINESS_RULES = [
    "sanitized_broker_account_snapshot_required",
    "owner_approval_required",
    "demo_account_only",
    "live_trading_blocked",
    "broker_api_access_blocked",
    "credential_access_blocked",
    "order_placement_blocked",
    "money_movement_blocked",
    "one_order_rule_required",
    "tp_sl_required",
    "reward_to_risk_required",
    "daily_stop_required",
    "weekly_stop_required",
    "kill_switch_required",
    "audit_report_required",
    "manual_owner_review_required",
    "no_autonomy_approval",
    "no_demo_order_placement_in_this_packet",
    "minimum_reward_to_risk",
    "max_risk_per_trade_percent",
    "max_daily_loss_percent",
    "max_weekly_loss_percent",
    "max_open_positions",
    "max_orders_per_signal",
]

FORBIDDEN_ACTIONS = [
    "broker/API access",
    "credentials",
    "account access",
    "demo order placement",
    "live trading",
    "order placement",
    "order closure",
    "money movement",
    "scheduler activation",
    "daemon activation",
    "webhook activation",
    "production activation",
    "autonomous trading",
    "claiming demo-order placement authority",
    "claiming live trading authority",
    "claiming 22/6 autonomy readiness",
    "claiming vacation/luxury mode as active",
    "claiming 100-120 percent return as verified",
]

SOURCE_EVIDENCE = [
    {
        "path": "automation/forex_engine/c1_risk_position_sizing_review_v1.py",
        "use": "Provides the authoritative P4 risk and position-sizing evaluator consumed by this P5 readiness review.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_RISK_POSITION_SIZING_REVIEW_V1.json",
        "use": "Records P4 review status, P5 readiness, score, failed requirements, and next lane.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_RISK_POSITION_SIZING_REVIEW_V1_REPORT.md",
        "use": "Explains the source-backed P4 decision and preserves the no demo or live trading boundary.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_RISK_POSITION_SIZING_REVIEW_NEXT_ACTION_QUEUE_V1.md",
        "use": "Routes the source-cleared candidate into P5 supervised demo-trade readiness review only.",
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


def _build_demo_readiness_policy(p4_result: dict[str, Any]) -> dict[str, Any]:
    risk_policy = p4_result.get("risk_policy", {})
    return {
        "sanitized_broker_account_snapshot_required": True,
        "owner_approval_required": True,
        "demo_account_only": True,
        "live_trading_blocked": True,
        "broker_api_access_blocked": True,
        "credential_access_blocked": True,
        "order_placement_blocked": True,
        "money_movement_blocked": True,
        "one_order_rule_required": True,
        "tp_sl_required": True,
        "reward_to_risk_required": True,
        "daily_stop_required": True,
        "weekly_stop_required": True,
        "kill_switch_required": True,
        "audit_report_required": True,
        "manual_owner_review_required": True,
        "no_autonomy_approval": True,
        "no_demo_order_placement_in_this_packet": True,
        "minimum_reward_to_risk": risk_policy.get("minimum_reward_to_risk", 1.20),
        "max_risk_per_trade_percent": risk_policy.get(
            "max_risk_per_trade_percent", 0.25
        ),
        "max_daily_loss_percent": risk_policy.get("max_daily_loss_percent", 1.00),
        "max_weekly_loss_percent": risk_policy.get("max_weekly_loss_percent", 2.00),
        "max_open_positions": risk_policy.get("max_open_positions", 1),
        "max_orders_per_signal": risk_policy.get("max_orders_per_signal", 1),
    }


def _build_snapshot_requirement() -> dict[str, Any]:
    return {
        "sanitized_broker_account_snapshot_required": True,
        "required_before": (
            "P6 demo-order intent owner-approval gate can calculate or review "
            "any account-specific position size."
        ),
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
        "present_in_this_packet": False,
        "status": "REQUIRED_FOR_P6_OWNER_REVIEW",
    }


def _build_owner_approval_gate() -> dict[str, Any]:
    return {
        "owner_approval_required": True,
        "approval_scope": "P6 demo-order intent owner-approval gate only",
        "approved_by_this_packet": False,
        "required_before_any_demo_order": True,
        "required_p6_fields": [
            "instrument",
            "side",
            "order type",
            "units formula",
            "stop loss",
            "take profit",
            "reward-to-risk",
            "sanitized broker/account snapshot",
            "one-order rule verification",
            "daily-stop verification",
            "kill-switch verification",
        ],
        "rule": (
            "The owner must review a later P6 intent card before any "
            "demo-order placement can be considered."
        ),
    }


def _build_one_order_rules(policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "one_order_rule_required": policy["one_order_rule_required"],
        "max_open_positions": policy["max_open_positions"],
        "max_orders_per_signal": policy["max_orders_per_signal"],
        "no_retry_loop": True,
        "verification_required_before_p6_owner_gate": True,
        "rule": (
            "C1 may have no more than one open position and no more than one "
            "order for the same signal during later owner review."
        ),
    }


def _build_tp_sl_guardrails(policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "tp_sl_required": policy["tp_sl_required"],
        "stop_loss_required": True,
        "take_profit_required": True,
        "reward_to_risk_required": policy["reward_to_risk_required"],
        "minimum_reward_to_risk": policy["minimum_reward_to_risk"],
        "verification_required_before_p6_owner_gate": True,
        "rule": (
            "A later P6 intent card must specify stop loss, take profit, and "
            "at least 1.20 reward-to-risk before owner review can proceed."
        ),
    }


def _build_stop_rules(policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "daily_stop_required": policy["daily_stop_required"],
        "weekly_stop_required": policy["weekly_stop_required"],
        "max_daily_loss_percent": policy["max_daily_loss_percent"],
        "max_weekly_loss_percent": policy["max_weekly_loss_percent"],
        "owner_reviewed_reset_required": True,
        "verification_required_before_p6_owner_gate": True,
        "rule": (
            "P6 must prove daily and weekly loss state remains inside the "
            "0.25 percent per-trade, 1.00 percent daily, and 2.00 percent "
            "weekly limits before owner review can continue."
        ),
    }


def _build_kill_switch_rules(policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "kill_switch_required": policy["kill_switch_required"],
        "verification_required_before_p6_owner_gate": True,
        "required_state": "active and untriggered before any P6 owner decision",
        "triggers": [
            "missing sanitized broker/account snapshot",
            "missing owner approval",
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
            "Any trigger blocks P6 owner review until repair evidence is "
            "generated and P5 or P6 is rerun."
        ),
    }


def _build_audit_requirements() -> dict[str, Any]:
    return {
        "audit_report_required": True,
        "manual_owner_review_required": True,
        "required_artifacts": [
            "P4 risk and position-sizing JSON",
            "P4 risk and position-sizing owner report",
            "P5 supervised demo-trade readiness JSON",
            "P5 supervised demo-trade readiness owner report",
            "P5 next action queue",
            "P6 sanitized broker/account snapshot",
            "P6 demo-order intent owner-approval card",
        ],
        "must_exclude": [
            "secrets",
            "credentials",
            "account identifiers",
            "broker order identifiers",
            "private execution payloads",
        ],
    }


def _entry_assessment(p4_result: dict[str, Any]) -> dict[str, Any]:
    risk_policy = p4_result.get("risk_policy", {})
    formula = p4_result.get("position_sizing_formula", {})
    broker_block = p4_result.get("broker_account_dependency_block", {})
    observed_forbidden = set(p4_result.get("forbidden_actions", []))
    required_forbidden = {
        "broker/API access",
        "credentials",
        "account access",
        "live trading",
        "order placement",
        "money movement",
        "autonomous trading",
    }
    checks = {
        "p4_review_status": (
            p4_result.get("p4_review_status")
            == "P4_RISK_POSITION_SIZING_PASSED_FOR_P5_REVIEW"
        ),
        "p4_p5_readiness": p4_result.get("p5_readiness") == "P5_READY",
        "post_p4_score": _safe_int(p4_result.get("post_p4_score")) == 100,
        "next_required_lane": (
            p4_result.get("next_required_lane")
            == "P5_SUPERVISED_DEMO_TRADE_READINESS_REVIEW"
        ),
        "failed_requirements_empty": not p4_result.get("failed_requirements", []),
        "risk_policy_exists": bool(risk_policy),
        "risk_policy_conservative": (
            risk_policy.get("max_risk_per_trade_percent", 999) <= 0.25
            and risk_policy.get("max_daily_loss_percent", 999) <= 1.00
            and risk_policy.get("max_weekly_loss_percent", 999) <= 2.00
            and risk_policy.get("minimum_reward_to_risk", 0) >= 1.20
            and risk_policy.get("max_open_positions") == 1
            and risk_policy.get("max_orders_per_signal") == 1
        ),
        "position_sizing_formula_only": formula.get("formula_only") is True,
        "broker_account_dependency_blocked": (
            broker_block.get("blocked") is True
            and "sanitized broker/account snapshot"
            in broker_block.get("p5_requirement", "")
        ),
        "demo_live_trading_remains_blocked": (
            risk_policy.get("no_demo_live_approval") is True
            and required_forbidden.issubset(observed_forbidden)
        ),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "observed": {
            "p4_review_status": p4_result.get("p4_review_status"),
            "p4_p5_readiness": p4_result.get("p5_readiness"),
            "post_p4_score": p4_result.get("post_p4_score"),
            "next_required_lane": p4_result.get("next_required_lane"),
            "failed_requirements": list(p4_result.get("failed_requirements", [])),
            "risk_policy": deepcopy(risk_policy),
            "position_sizing_formula": deepcopy(formula),
            "broker_account_dependency_block": deepcopy(broker_block),
            "review_only_boundary": sorted(observed_forbidden),
        },
    }


def _safety_rule_assessments(
    p5_entry_assessment: dict[str, Any],
    policy: dict[str, Any],
    snapshot_requirement: dict[str, Any],
    owner_approval_gate: dict[str, Any],
    one_order_rules: dict[str, Any],
    tp_sl_guardrails: dict[str, Any],
    stop_rules: dict[str, Any],
    kill_switch_rules: dict[str, Any],
    audit_requirements: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    missing_rules = [rule for rule in REQUIRED_READINESS_RULES if rule not in policy]
    safety_boundary_passed = (
        policy.get("demo_account_only") is True
        and policy.get("live_trading_blocked") is True
        and policy.get("broker_api_access_blocked") is True
        and policy.get("credential_access_blocked") is True
        and policy.get("order_placement_blocked") is True
        and policy.get("money_movement_blocked") is True
        and policy.get("no_autonomy_approval") is True
        and policy.get("no_demo_order_placement_in_this_packet") is True
    )
    return {
        "p4_entry_condition": {
            "passed": p5_entry_assessment["passed"],
            "evidence": (
                "P4 must be passed for P5 review, score 100, P5-ready, "
                "with empty failed requirements and review-only boundaries."
            ),
        },
        "required_readiness_rules_present": {
            "passed": not missing_rules,
            "missing_rules": missing_rules,
            "evidence": "All required P5 readiness policy keys must exist.",
        },
        "conservative_limits": {
            "passed": (
                policy.get("max_risk_per_trade_percent", 999) <= 0.25
                and policy.get("max_daily_loss_percent", 999) <= 1.00
                and policy.get("max_weekly_loss_percent", 999) <= 2.00
                and policy.get("minimum_reward_to_risk", 0) >= 1.20
                and policy.get("max_open_positions") == 1
                and policy.get("max_orders_per_signal") == 1
            ),
            "evidence": (
                "P5 keeps P4 conservative defaults: 0.25 percent per trade, "
                "1.00 percent daily, 2.00 percent weekly, one open position, "
                "one order per signal, and at least 1.20 reward-to-risk."
            ),
        },
        "snapshot_requirement": {
            "passed": (
                snapshot_requirement.get(
                    "sanitized_broker_account_snapshot_required"
                )
                is True
                and snapshot_requirement.get("present_in_this_packet") is False
            ),
            "evidence": (
                "A sanitized broker/account snapshot is required later and "
                "is not collected in this packet."
            ),
        },
        "owner_approval_gate": {
            "passed": (
                owner_approval_gate.get("owner_approval_required") is True
                and owner_approval_gate.get("approved_by_this_packet") is False
            ),
            "evidence": (
                "Owner approval is required in P6 before any demo-order "
                "placement can be considered."
            ),
        },
        "demo_safety_boundary": {
            "passed": safety_boundary_passed,
            "evidence": (
                "Demo-only review remains bounded, while live trading, "
                "broker/API, credentials, order placement, money movement, "
                "and autonomy remain blocked."
            ),
        },
        "one_order_rule": {
            "passed": (
                one_order_rules.get("one_order_rule_required") is True
                and one_order_rules.get("max_open_positions") == 1
                and one_order_rules.get("max_orders_per_signal") == 1
            ),
            "evidence": "One open position and one order per signal are required.",
        },
        "tp_sl_guardrails": {
            "passed": (
                tp_sl_guardrails.get("stop_loss_required") is True
                and tp_sl_guardrails.get("take_profit_required") is True
                and tp_sl_guardrails.get("minimum_reward_to_risk", 0) >= 1.20
            ),
            "evidence": (
                "A stop loss, take profit, and at least 1.20 reward-to-risk "
                "are required for later owner review."
            ),
        },
        "stop_rules": {
            "passed": (
                stop_rules.get("daily_stop_required") is True
                and stop_rules.get("weekly_stop_required") is True
                and stop_rules.get("max_daily_loss_percent", 999) <= 1.00
                and stop_rules.get("max_weekly_loss_percent", 999) <= 2.00
            ),
            "evidence": "Daily and weekly stop rules remain required.",
        },
        "kill_switch_rules": {
            "passed": (
                kill_switch_rules.get("kill_switch_required") is True
                and bool(kill_switch_rules.get("triggers"))
            ),
            "evidence": "Kill-switch verification remains required before P6.",
        },
        "audit_requirements": {
            "passed": (
                audit_requirements.get("audit_report_required") is True
                and audit_requirements.get("manual_owner_review_required") is True
            ),
            "evidence": (
                "P5 requires generated evidence and manual owner review "
                "before any later demo-order intent decision."
            ),
        },
    }


def _failed_requirements(
    safety_rule_assessments: dict[str, dict[str, Any]]
) -> list[str]:
    return [
        key
        for key, assessment in safety_rule_assessments.items()
        if not assessment["passed"]
    ]


def _bullet_list(items: list[str] | tuple[str, ...]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def _source_list(result: dict[str, Any]) -> str:
    return "\n".join(
        f"- `{source['path']}`: {source['use']}" for source in result["source_evidence"]
    )


def _demo_policy_table(result: dict[str, Any]) -> str:
    policy = result["demo_readiness_policy"]
    rows = [
        "| rule | value |",
        "|---|---|",
    ]
    for key in REQUIRED_READINESS_RULES:
        rows.append(f"| `{key}` | `{policy[key]}` |")
    return "\n".join(rows)


def _assessment_table(result: dict[str, Any]) -> str:
    rows = [
        "| requirement | status | evidence |",
        "|---|---|---|",
    ]
    for key, assessment in result["safety_rule_assessments"].items():
        status = "PASS" if assessment["passed"] else "FAIL"
        rows.append(f"| `{key}` | `{status}` | {assessment['evidence']} |")
    return "\n".join(rows)


def evaluate_c1_supervised_demo_trade_readiness_review() -> dict[str, Any]:
    """Return the source-backed C1 P5 supervised demo readiness decision."""

    p4_result = evaluate_c1_risk_position_sizing_review()
    p5_entry_assessment = _entry_assessment(p4_result)
    demo_readiness_policy = _build_demo_readiness_policy(p4_result)
    snapshot_requirement = _build_snapshot_requirement()
    owner_approval_gate = _build_owner_approval_gate()
    one_order_rules = _build_one_order_rules(demo_readiness_policy)
    tp_sl_guardrails = _build_tp_sl_guardrails(demo_readiness_policy)
    stop_rules = _build_stop_rules(demo_readiness_policy)
    kill_switch_rules = _build_kill_switch_rules(demo_readiness_policy)
    audit_requirements = _build_audit_requirements()
    safety_rule_assessments = _safety_rule_assessments(
        p5_entry_assessment,
        demo_readiness_policy,
        snapshot_requirement,
        owner_approval_gate,
        one_order_rules,
        tp_sl_guardrails,
        stop_rules,
        kill_switch_rules,
        audit_requirements,
    )
    failed_requirements = _failed_requirements(safety_rule_assessments)

    input_score = _safe_int(p4_result.get("post_p4_score"))
    input_status = str(p4_result.get("post_p4_status", ""))

    if not p5_entry_assessment["passed"]:
        p5_review_status = "P5_SUPERVISED_DEMO_READINESS_FAILED_P4_REPAIR_REQUIRED"
        p6_readiness = "NOT_READY"
        next_required_lane = "P4_RISK_POSITION_SIZING_REPAIR_REVIEW"
        post_p5_score = min(input_score, 85)
        post_p5_status = "REJECTED_P4_NOT_READY"
        final_failed_requirements = ["p4_entry_condition"]
        final_owner_sentence = NOT_READY_FINAL_OWNER_SENTENCE
    elif failed_requirements:
        p5_review_status = "P5_SUPERVISED_DEMO_READINESS_FAILED_RULES_REQUIRED"
        p6_readiness = "NOT_READY"
        next_required_lane = "P5_CONTINUE_SUPERVISED_DEMO_READINESS_REVIEW"
        post_p5_score = min(input_score, 90)
        post_p5_status = (
            "REJECTED_DEMO_SAFETY_BOUNDARY"
            if "demo_safety_boundary" in failed_requirements
            else "REJECTED_DEMO_READINESS_RULES_INCOMPLETE"
        )
        final_failed_requirements = failed_requirements
        final_owner_sentence = NOT_READY_FINAL_OWNER_SENTENCE
    else:
        p5_review_status = (
            "P5_SUPERVISED_DEMO_READINESS_PASSED_FOR_P6_OWNER_APPROVAL"
        )
        p6_readiness = "P6_READY"
        next_required_lane = "P6_DEMO_ORDER_INTENT_OWNER_APPROVAL_GATE"
        post_p5_score = 100
        post_p5_status = "P6_READY"
        final_failed_requirements = []
        final_owner_sentence = P6_READY_FINAL_OWNER_SENTENCE

    passed_requirements = [
        key
        for key, assessment in safety_rule_assessments.items()
        if assessment["passed"]
    ]

    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": input_score,
        "post_p5_score": post_p5_score,
        "input_status": input_status,
        "post_p5_status": post_p5_status,
        "p4_review_status": p4_result.get("p4_review_status"),
        "p4_p5_readiness": p4_result.get("p5_readiness"),
        "p5_review_status": p5_review_status,
        "p6_readiness": p6_readiness,
        "next_required_lane": next_required_lane,
        "p5_entry_assessment": deepcopy(p5_entry_assessment),
        "demo_readiness_policy": deepcopy(demo_readiness_policy),
        "snapshot_requirement": deepcopy(snapshot_requirement),
        "owner_approval_gate": deepcopy(owner_approval_gate),
        "safety_rule_assessments": deepcopy(safety_rule_assessments),
        "passed_requirements": passed_requirements,
        "failed_requirements": final_failed_requirements,
        "one_order_rules": deepcopy(one_order_rules),
        "tp_sl_guardrails": deepcopy(tp_sl_guardrails),
        "stop_rules": deepcopy(stop_rules),
        "kill_switch_rules": deepcopy(kill_switch_rules),
        "audit_requirements": deepcopy(audit_requirements),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "source_evidence": deepcopy(SOURCE_EVIDENCE),
        "final_owner_sentence": final_owner_sentence,
    }


def render_owner_report(result: dict[str, Any]) -> str:
    """Render the owner-facing P5 supervised demo readiness report."""

    snapshot = result["snapshot_requirement"]
    owner_gate = result["owner_approval_gate"]
    one_order = result["one_order_rules"]
    tp_sl = result["tp_sl_guardrails"]
    stop_rules = result["stop_rules"]
    kill_switch = result["kill_switch_rules"]
    audit = result["audit_requirements"]

    return f"""# AIOS Forex C1 Supervised Demo Trade Readiness Review V1 Report

## Campaign Scope

This report applies the P5 C1 supervised demo-trade readiness review lane for `c1-eur-buy` only. It consumes the P4 risk and position-sizing output and defines review-only safety gates for a later P6 demo-order intent owner-approval gate.

This report does not execute trades, access broker/API systems, access credentials, access accounts, calculate live or account-specific position size, place orders, close orders, move money, activate schedulers, activate daemons, activate webhooks, activate production, approve autonomous trading, or approve any demo-order placement.

## Trader Meaning

{TRADER_MEANING}

## Source Evidence

{_source_list(result)}

## P4 Entry Condition

- p4_review_status: `{result["p4_review_status"]}`
- p4_p5_readiness: `{result["p4_p5_readiness"]}`
- input_score: `{result["input_score"]}`
- input_status: `{result["input_status"]}`
- p5_entry_passed: `{result["p5_entry_assessment"]["passed"]}`

{_assessment_table(result)}

## Demo Readiness Policy

{_demo_policy_table(result)}

## Snapshot Requirement

- sanitized_broker_account_snapshot_required: `{snapshot["sanitized_broker_account_snapshot_required"]}`
- required_before: {snapshot["required_before"]}
- purpose: {snapshot["purpose"]}
- allowed_snapshot_fields:
{_bullet_list(snapshot["allowed_snapshot_fields"])}
- forbidden_snapshot_fields:
{_bullet_list(snapshot["forbidden_snapshot_fields"])}
- present_in_this_packet: `{snapshot["present_in_this_packet"]}`
- status: `{snapshot["status"]}`

## Owner Approval Gate

- owner_approval_required: `{owner_gate["owner_approval_required"]}`
- approval_scope: {owner_gate["approval_scope"]}
- approved_by_this_packet: `{owner_gate["approved_by_this_packet"]}`
- required_before_any_demo_order: `{owner_gate["required_before_any_demo_order"]}`
- required_p6_fields:
{_bullet_list(owner_gate["required_p6_fields"])}
- rule: {owner_gate["rule"]}

## One-Order Rules

- one_order_rule_required: `{one_order["one_order_rule_required"]}`
- max_open_positions: `{one_order["max_open_positions"]}`
- max_orders_per_signal: `{one_order["max_orders_per_signal"]}`
- no_retry_loop: `{one_order["no_retry_loop"]}`
- verification_required_before_p6_owner_gate: `{one_order["verification_required_before_p6_owner_gate"]}`
- rule: {one_order["rule"]}

## TP/SL Guardrails

- tp_sl_required: `{tp_sl["tp_sl_required"]}`
- stop_loss_required: `{tp_sl["stop_loss_required"]}`
- take_profit_required: `{tp_sl["take_profit_required"]}`
- reward_to_risk_required: `{tp_sl["reward_to_risk_required"]}`
- minimum_reward_to_risk: `{tp_sl["minimum_reward_to_risk"]}`
- verification_required_before_p6_owner_gate: `{tp_sl["verification_required_before_p6_owner_gate"]}`
- rule: {tp_sl["rule"]}

## Stop Rules

- daily_stop_required: `{stop_rules["daily_stop_required"]}`
- weekly_stop_required: `{stop_rules["weekly_stop_required"]}`
- max_daily_loss_percent: `{stop_rules["max_daily_loss_percent"]}`
- max_weekly_loss_percent: `{stop_rules["max_weekly_loss_percent"]}`
- owner_reviewed_reset_required: `{stop_rules["owner_reviewed_reset_required"]}`
- verification_required_before_p6_owner_gate: `{stop_rules["verification_required_before_p6_owner_gate"]}`
- rule: {stop_rules["rule"]}

## Kill Switch Rules

- kill_switch_required: `{kill_switch["kill_switch_required"]}`
- verification_required_before_p6_owner_gate: `{kill_switch["verification_required_before_p6_owner_gate"]}`
- required_state: {kill_switch["required_state"]}
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

## P6 Readiness Decision

- p5_review_status: `{result["p5_review_status"]}`
- p6_readiness: `{result["p6_readiness"]}`
- post_p5_score: `{result["post_p5_score"]}`
- post_p5_status: `{result["post_p5_status"]}`
- passed_requirements: `{result["passed_requirements"]}`
- failed_requirements: `{result["failed_requirements"]}`

## Next Required Lane

`{result["next_required_lane"]}`

## What This Completes

- completes P5 supervised demo-trade readiness review for `c1-eur-buy`
- defines the sanitized snapshot requirement, owner approval gate, one-order rules, TP/SL guardrails, stop rules, kill-switch rules, and audit requirements
- decides whether the candidate can move to P6 demo-order intent and owner-approval gate only

## What This Does Not Approve

{_bullet_list(result["forbidden_actions"])}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""


def render_next_action_queue(result: dict[str, Any]) -> str:
    """Render the next-action queue for the P5 readiness review lane."""

    if result["p6_readiness"] == "P6_READY":
        required_actions = [
            "start P6 demo-order intent owner-approval gate",
            "require sanitized broker/account snapshot",
            "require owner approval before any demo order",
            "require exact intended instrument, side, order type, units formula, TP, SL, and reward-to-risk",
            "require one-order rule verification",
            "require daily-stop and kill-switch verification",
            "keep live trading blocked",
            "keep autonomous trading blocked",
        ]
        remaining_blocks = [
            "P5 review is not demo-order placement authority.",
            "P5 review is not live trading authority.",
            "Broker/API, credentials, account access, order action, money movement, production, and autonomous trading remain blocked.",
            "22/6 autonomy, vacation/luxury mode, and 100-120 percent return claims remain blocked.",
        ]
    else:
        required_actions = [
            "return to P4 repair or P5 readiness-rule completion",
            "rerun P5 review after repair",
            "keep demo/live trading blocked",
        ]
        remaining_blocks = [
            "P6 demo-order intent owner-approval gate is blocked.",
            "Demo-order placement remains blocked.",
            "Live trading remains blocked.",
            "Broker/API, credentials, account access, order action, money movement, production, and autonomous trading remain blocked.",
        ]

    return f"""# AIOS Forex C1 Supervised Demo Trade Readiness Review Next Action Queue V1

## Purpose

This queue records the next action after P5 C1 supervised demo-trade readiness review.

## P5 Review Status

`{result["p5_review_status"]}`

## P6 Readiness

`{result["p6_readiness"]}`

## Passed Requirements

{_bullet_list([f"`{item}`" for item in result["passed_requirements"]])}

## Failed Requirements

{_bullet_list([f"`{item}`" for item in result["failed_requirements"]])}

## Next Required Lane

`{result["next_required_lane"]}`

## Required Next Actions

{_bullet_list(required_actions)}

## Remaining Blocks

{_bullet_list(remaining_blocks)}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""


__all__ = [
    "evaluate_c1_supervised_demo_trade_readiness_review",
    "render_owner_report",
    "render_next_action_queue",
]
