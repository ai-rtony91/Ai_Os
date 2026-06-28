"""Deterministic C1 risk and position-sizing review analyzer.

This module performs repo-local evidence review only. It does not access
broker APIs, credentials, accounts, balances, live prices, orders, schedulers,
daemons, webhooks, production systems, or trading execution paths.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from automation.forex_engine.c1_walk_forward_oos_proof_v1 import (
    evaluate_c1_walk_forward_oos_proof,
)


CAMPAIGN_ID = "AIOS-FOREX-P4-C1-RISK-POSITION-SIZING-REVIEW-V1"
CANDIDATE_ID = "c1-eur-buy"
CANDIDATE_NAME = "paper_long_run_supervisor_v2 LONG EURUSD"

TRADER_MEANING = (
    "AIOS is defining how much the proven EUR/USD buy setup is allowed to "
    "risk, how position size must be calculated, and which stop rules must "
    "protect the account before any supervised demo-trade readiness review."
)

P5_READY_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P4 C1 risk and position-sizing review is complete: "
    "c1-eur-buy is source-cleared for P5 supervised demo-trade readiness "
    "review only, while demo trading, live trading, broker/API, credentials, "
    "money movement, 22/6 autonomy, vacation/luxury mode, and 100-120 percent "
    "return claims remain blocked until separately proven and approved."
)

NOT_READY_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P4 C1 risk and position-sizing review is complete: "
    "c1-eur-buy is not cleared for P5 supervised demo-trade readiness review, "
    "and the next required lane is P3 repair or P4 risk-rule completion; demo "
    "trading, live trading, broker/API, credentials, money movement, 22/6 "
    "autonomy, vacation/luxury mode, and 100-120 percent return claims remain "
    "blocked until separately proven and approved."
)

P4_REVIEW_STATUSES = {
    "P4_RISK_POSITION_SIZING_PASSED_FOR_P5_REVIEW",
    "P4_RISK_POSITION_SIZING_FAILED_RULES_REQUIRED",
    "P4_RISK_POSITION_SIZING_FAILED_P3_REPAIR_REQUIRED",
}

P5_READINESS_VALUES = {"P5_READY", "NOT_READY"}

NEXT_REQUIRED_LANES = {
    "P5_SUPERVISED_DEMO_TRADE_READINESS_REVIEW",
    "P4_CONTINUE_RISK_POSITION_SIZING_REVIEW",
    "P3_WALK_FORWARD_OOS_PROOF_REPAIR_REVIEW",
}

POST_P4_STATUSES = {
    "P5_READY",
    "NEEDS_MORE_EVIDENCE",
    "REJECTED_P3_NOT_READY",
    "REJECTED_RISK_RULES_INCOMPLETE",
    "REJECTED_EXCESSIVE_RISK",
}

REQUIRED_RISK_RULES = [
    "max_risk_per_trade_percent",
    "max_daily_loss_percent",
    "max_weekly_loss_percent",
    "max_consecutive_losses",
    "max_open_positions",
    "max_orders_per_signal",
    "stop_loss_required",
    "take_profit_required",
    "minimum_reward_to_risk",
    "max_strategy_drawdown_percent",
    "one_order_rule",
    "daily_stop_rule",
    "weekly_stop_rule",
    "kill_switch_triggers",
    "position_size_formula",
    "broker_account_dependency_block",
    "no_demo_live_approval",
]

FORBIDDEN_ACTIONS = [
    "broker/API access",
    "credentials",
    "account access",
    "demo trading without later evidence gate",
    "live trading",
    "order placement",
    "order closure",
    "money movement",
    "scheduler activation",
    "daemon activation",
    "webhook activation",
    "production activation",
    "autonomous trading",
    "claiming 22/6 autonomy readiness",
    "claiming vacation/luxury mode as active",
    "claiming 100-120 percent return as verified",
]

SOURCE_EVIDENCE = [
    {
        "path": "automation/forex_engine/c1_walk_forward_oos_proof_v1.py",
        "use": "Provides the authoritative P3 proof evaluator consumed by this P4 risk review.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_WALK_FORWARD_OOS_PROOF_V1.json",
        "use": "Records P3 proof status, P4 readiness, score, failed requirements, and next lane.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_WALK_FORWARD_OOS_PROOF_V1_REPORT.md",
        "use": "Explains the source-backed P3 decision and preserves the no demo or live trading boundary.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_WALK_FORWARD_OOS_PROOF_NEXT_ACTION_QUEUE_V1.md",
        "use": "Routes the source-cleared candidate into P4 risk and position-sizing review only.",
    },
]


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _build_position_sizing_formula() -> dict[str, Any]:
    return {
        "formula_only": True,
        "risk_amount_formula": (
            "risk_amount = account_equity * "
            "(max_risk_per_trade_percent / 100)"
        ),
        "position_size_formula": (
            "position_size = risk_amount / stop_loss_value_per_unit"
        ),
        "required_inputs": [
            "account_equity",
            "max_risk_per_trade_percent",
            "stop_loss_value_per_unit",
        ],
        "blocked_inputs": [
            "real account equity in this P4 review",
            "broker balances",
            "broker credentials",
            "live prices",
            "account identifiers",
        ],
        "real_sizing_block": (
            "Real sizing is blocked until a later supervised demo-readiness "
            "review supplies a sanitized broker/account snapshot."
        ),
    }


def _build_broker_account_dependency_block() -> dict[str, Any]:
    return {
        "blocked": True,
        "reason": (
            "This P4 review defines formulas and guardrails only; it must not "
            "read credentials, balances, account identifiers, broker data, or "
            "live prices."
        ),
        "p5_requirement": (
            "A later supervised demo-readiness review must supply a sanitized "
            "broker/account snapshot before any real position size can be "
            "calculated."
        ),
    }


def _build_risk_policy(
    position_sizing_formula: dict[str, Any],
    broker_account_dependency_block: dict[str, Any],
) -> dict[str, Any]:
    return {
        "max_risk_per_trade_percent": 0.25,
        "max_daily_loss_percent": 1.00,
        "max_weekly_loss_percent": 2.00,
        "max_consecutive_losses": 3,
        "max_open_positions": 1,
        "max_orders_per_signal": 1,
        "stop_loss_required": True,
        "take_profit_required": True,
        "minimum_reward_to_risk": 1.20,
        "max_strategy_drawdown_percent": 5.00,
        "one_order_rule": True,
        "daily_stop_rule": True,
        "weekly_stop_rule": True,
        "kill_switch_triggers": [
            "missing stop loss",
            "missing take profit",
            "risk per trade above 0.25 percent",
            "daily loss at or above 1.00 percent",
            "weekly loss at or above 2.00 percent",
            "three consecutive losses",
            "more than one open position",
            "more than one order for the same signal",
            "strategy drawdown above 5.00 percent",
            "broker/account dependency requested before sanitized P5 snapshot",
            "credential, account, broker/API, order, scheduler, daemon, webhook, production, or autonomy path detected",
        ],
        "position_size_formula": position_sizing_formula["position_size_formula"],
        "broker_account_dependency_block": broker_account_dependency_block,
        "no_demo_live_approval": True,
    }


def _build_max_loss_rules(risk_policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "max_risk_per_trade_percent": risk_policy["max_risk_per_trade_percent"],
        "max_daily_loss_percent": risk_policy["max_daily_loss_percent"],
        "max_weekly_loss_percent": risk_policy["max_weekly_loss_percent"],
        "max_consecutive_losses": risk_policy["max_consecutive_losses"],
        "max_strategy_drawdown_percent": risk_policy[
            "max_strategy_drawdown_percent"
        ],
        "rule": (
            "Loss exposure must stay inside the per-trade, daily, weekly, "
            "consecutive-loss, and strategy-drawdown gates before P5 can "
            "review supervised demo-trade readiness."
        ),
    }


def _build_daily_stop_rules(risk_policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "daily_stop_rule": risk_policy["daily_stop_rule"],
        "max_daily_loss_percent": risk_policy["max_daily_loss_percent"],
        "trigger": (
            "Stop new orders for the review day if realized loss plus open "
            "risk reaches 1.00 percent of account equity."
        ),
        "reset_condition": "Owner-reviewed next-session reset is required.",
        "calculation_dependency": (
            "Requires a sanitized broker/account snapshot in P5 before "
            "account-specific calculation."
        ),
    }


def _build_one_order_rules(risk_policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "one_order_rule": risk_policy["one_order_rule"],
        "max_open_positions": risk_policy["max_open_positions"],
        "max_orders_per_signal": risk_policy["max_orders_per_signal"],
        "no_retry_loop": True,
        "rule": (
            "The C1 signal may have no more than one open position and no "
            "more than one order per signal during later supervised review."
        ),
    }


def _build_tp_sl_guardrails(risk_policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "stop_loss_required": risk_policy["stop_loss_required"],
        "take_profit_required": risk_policy["take_profit_required"],
        "minimum_reward_to_risk": risk_policy["minimum_reward_to_risk"],
        "rule": (
            "Every later supervised demo-trade review candidate must include "
            "a stop loss, take profit, and at least 1.20 reward-to-risk before "
            "any order approval can be considered."
        ),
    }


def _build_kill_switch_rules(risk_policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "kill_switch_required": True,
        "triggers": list(risk_policy["kill_switch_triggers"]),
        "rule": (
            "Any trigger blocks progression until the issue is reviewed and "
            "the P4 or P5 evidence is rerun."
        ),
    }


def _entry_assessment(p3_result: dict[str, Any]) -> dict[str, Any]:
    required_forbidden = {
        "broker/API access",
        "credentials",
        "live trading",
        "order placement",
        "money movement",
        "autonomous trading",
    }
    observed_forbidden = set(p3_result.get("forbidden_actions", []))
    checks = {
        "p3_proof_status": (
            p3_result.get("p3_proof_status")
            == "P3_PROOF_PASSED_FOR_P4_REVIEW"
        ),
        "p4_readiness": p3_result.get("p4_readiness") == "P4_READY",
        "post_p3_score": _safe_int(p3_result.get("post_p3_score")) == 100,
        "next_required_lane": (
            p3_result.get("next_required_lane")
            == "P4_RISK_POSITION_SIZING_REVIEW"
        ),
        "failed_requirements_empty": not p3_result.get("failed_requirements", []),
        "review_only_boundary": required_forbidden.issubset(observed_forbidden),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "observed": {
            "p3_proof_status": p3_result.get("p3_proof_status"),
            "p4_readiness": p3_result.get("p4_readiness"),
            "post_p3_score": p3_result.get("post_p3_score"),
            "next_required_lane": p3_result.get("next_required_lane"),
            "failed_requirements": list(p3_result.get("failed_requirements", [])),
            "review_only_boundary": sorted(observed_forbidden),
        },
    }


def _risk_rule_assessments(
    risk_policy: dict[str, Any],
    position_sizing_formula: dict[str, Any],
    broker_account_dependency_block: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    missing_rules = [rule for rule in REQUIRED_RISK_RULES if rule not in risk_policy]
    assessments = {
        "required_risk_rules_present": {
            "passed": not missing_rules,
            "missing_rules": missing_rules,
            "evidence": "All required P4 risk policy keys must exist.",
        },
        "conservative_defaults": {
            "passed": (
                risk_policy.get("max_risk_per_trade_percent", 999) <= 0.25
                and risk_policy.get("max_daily_loss_percent", 999) <= 1.00
                and risk_policy.get("max_weekly_loss_percent", 999) <= 2.00
                and risk_policy.get("max_consecutive_losses", 999) <= 3
                and risk_policy.get("max_open_positions") == 1
                and risk_policy.get("max_orders_per_signal") == 1
                and risk_policy.get("stop_loss_required") is True
                and risk_policy.get("take_profit_required") is True
                and risk_policy.get("minimum_reward_to_risk", 0) >= 1.20
                and risk_policy.get("max_strategy_drawdown_percent", 999) <= 5.00
            ),
            "evidence": (
                "Risk defaults cap exposure at 0.25 percent per trade, "
                "1.00 percent daily, 2.00 percent weekly, three consecutive "
                "losses, one open position, one order per signal, mandatory "
                "TP/SL, at least 1.20 reward-to-risk, and 5.00 percent "
                "strategy drawdown."
            ),
        },
        "formula_only_position_sizing": {
            "passed": (
                position_sizing_formula.get("formula_only") is True
                and "account_equity"
                in position_sizing_formula.get("risk_amount_formula", "")
                and "stop_loss_value_per_unit"
                in position_sizing_formula.get("position_size_formula", "")
            ),
            "evidence": (
                "Position sizing is formula-only and requires account_equity "
                "and stop_loss_value_per_unit without reading broker data."
            ),
        },
        "broker_account_dependency_block": {
            "passed": broker_account_dependency_block.get("blocked") is True,
            "evidence": (
                "Real sizing is blocked until P5 supplies a sanitized "
                "broker/account snapshot."
            ),
        },
        "no_demo_live_approval": {
            "passed": risk_policy.get("no_demo_live_approval") is True,
            "evidence": (
                "P4 defines review policy only and does not approve demo "
                "trading, live trading, broker/API access, credentials, order "
                "placement, or money movement."
            ),
        },
    }
    return assessments


def _failed_risk_requirements(
    risk_rule_assessments: dict[str, dict[str, Any]]
) -> list[str]:
    return [
        key
        for key, assessment in risk_rule_assessments.items()
        if not assessment["passed"]
    ]


def _risk_failure_is_excessive(
    risk_rule_assessments: dict[str, dict[str, Any]]
) -> bool:
    failed = _failed_risk_requirements(risk_rule_assessments)
    return "conservative_defaults" in failed and len(failed) == 1


def evaluate_c1_risk_position_sizing_review() -> dict[str, Any]:
    """Return the source-backed C1 P4 risk and position-sizing decision."""

    p3_result = evaluate_c1_walk_forward_oos_proof()
    p4_entry_assessment = _entry_assessment(p3_result)
    position_sizing_formula = _build_position_sizing_formula()
    broker_account_dependency_block = _build_broker_account_dependency_block()
    risk_policy = _build_risk_policy(
        position_sizing_formula,
        broker_account_dependency_block,
    )
    risk_rule_assessments = _risk_rule_assessments(
        risk_policy,
        position_sizing_formula,
        broker_account_dependency_block,
    )
    failed_risk_requirements = _failed_risk_requirements(risk_rule_assessments)

    input_score = _safe_int(p3_result.get("post_p3_score"))
    input_status = str(p3_result.get("post_p3_status", ""))

    if not p4_entry_assessment["passed"]:
        p4_review_status = "P4_RISK_POSITION_SIZING_FAILED_P3_REPAIR_REQUIRED"
        p5_readiness = "NOT_READY"
        next_required_lane = "P3_WALK_FORWARD_OOS_PROOF_REPAIR_REVIEW"
        post_p4_score = min(input_score, 85)
        post_p4_status = "REJECTED_P3_NOT_READY"
        failed_requirements = ["p3_entry_condition"]
        final_owner_sentence = NOT_READY_FINAL_OWNER_SENTENCE
    elif failed_risk_requirements:
        p4_review_status = "P4_RISK_POSITION_SIZING_FAILED_RULES_REQUIRED"
        p5_readiness = "NOT_READY"
        next_required_lane = "P4_CONTINUE_RISK_POSITION_SIZING_REVIEW"
        post_p4_score = min(input_score, 90)
        post_p4_status = (
            "REJECTED_EXCESSIVE_RISK"
            if _risk_failure_is_excessive(risk_rule_assessments)
            else "REJECTED_RISK_RULES_INCOMPLETE"
        )
        failed_requirements = failed_risk_requirements
        final_owner_sentence = NOT_READY_FINAL_OWNER_SENTENCE
    else:
        p4_review_status = "P4_RISK_POSITION_SIZING_PASSED_FOR_P5_REVIEW"
        p5_readiness = "P5_READY"
        next_required_lane = "P5_SUPERVISED_DEMO_TRADE_READINESS_REVIEW"
        post_p4_score = 100
        post_p4_status = "P5_READY"
        failed_requirements = []
        final_owner_sentence = P5_READY_FINAL_OWNER_SENTENCE

    passed_requirements = []
    if p4_entry_assessment["passed"]:
        passed_requirements.append("p3_entry_condition")
    passed_requirements.extend(
        key
        for key, assessment in risk_rule_assessments.items()
        if assessment["passed"]
    )

    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": input_score,
        "post_p4_score": post_p4_score,
        "input_status": input_status,
        "post_p4_status": post_p4_status,
        "p3_proof_status": p3_result.get("p3_proof_status"),
        "p3_p4_readiness": p3_result.get("p4_readiness"),
        "p4_review_status": p4_review_status,
        "p5_readiness": p5_readiness,
        "next_required_lane": next_required_lane,
        "p4_entry_assessment": deepcopy(p4_entry_assessment),
        "risk_policy": deepcopy(risk_policy),
        "position_sizing_formula": deepcopy(position_sizing_formula),
        "risk_rule_assessments": deepcopy(risk_rule_assessments),
        "passed_requirements": passed_requirements,
        "failed_requirements": failed_requirements,
        "max_loss_rules": _build_max_loss_rules(risk_policy),
        "daily_stop_rules": _build_daily_stop_rules(risk_policy),
        "one_order_rules": _build_one_order_rules(risk_policy),
        "tp_sl_guardrails": _build_tp_sl_guardrails(risk_policy),
        "kill_switch_rules": _build_kill_switch_rules(risk_policy),
        "broker_account_dependency_block": deepcopy(
            broker_account_dependency_block
        ),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "source_evidence": deepcopy(SOURCE_EVIDENCE),
        "final_owner_sentence": final_owner_sentence,
    }


def _bullet_list(items: list[str] | tuple[str, ...]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def _source_list(result: dict[str, Any]) -> str:
    return "\n".join(
        f"- `{source['path']}`: {source['use']}" for source in result["source_evidence"]
    )


def _risk_policy_table(result: dict[str, Any]) -> str:
    policy = result["risk_policy"]
    rows = [
        "| rule | value |",
        "|---|---|",
        f"| `max_risk_per_trade_percent` | `{policy['max_risk_per_trade_percent']}` |",
        f"| `max_daily_loss_percent` | `{policy['max_daily_loss_percent']}` |",
        f"| `max_weekly_loss_percent` | `{policy['max_weekly_loss_percent']}` |",
        f"| `max_consecutive_losses` | `{policy['max_consecutive_losses']}` |",
        f"| `max_open_positions` | `{policy['max_open_positions']}` |",
        f"| `max_orders_per_signal` | `{policy['max_orders_per_signal']}` |",
        f"| `stop_loss_required` | `{policy['stop_loss_required']}` |",
        f"| `take_profit_required` | `{policy['take_profit_required']}` |",
        f"| `minimum_reward_to_risk` | `{policy['minimum_reward_to_risk']}` |",
        f"| `max_strategy_drawdown_percent` | `{policy['max_strategy_drawdown_percent']}` |",
        f"| `one_order_rule` | `{policy['one_order_rule']}` |",
        f"| `daily_stop_rule` | `{policy['daily_stop_rule']}` |",
        f"| `weekly_stop_rule` | `{policy['weekly_stop_rule']}` |",
    ]
    return "\n".join(rows)


def _assessment_table(result: dict[str, Any]) -> str:
    rows = [
        "| requirement | status | evidence |",
        "|---|---|---|",
    ]
    if result["p4_entry_assessment"]["passed"]:
        entry_status = "PASS"
    else:
        entry_status = "FAIL"
    rows.append(
        "| `p3_entry_condition` | `{}` | P3 must be P4-ready, score 100, "
        "without failed requirements, and review-only. |".format(entry_status)
    )
    for key, assessment in result["risk_rule_assessments"].items():
        status = "PASS" if assessment["passed"] else "FAIL"
        rows.append(f"| `{key}` | `{status}` | {assessment['evidence']} |")
    return "\n".join(rows)


def render_owner_report(result: dict[str, Any]) -> str:
    """Render the owner-facing P4 risk and position-sizing report."""

    formula = result["position_sizing_formula"]
    max_loss = result["max_loss_rules"]
    daily_stop = result["daily_stop_rules"]
    one_order = result["one_order_rules"]
    tp_sl = result["tp_sl_guardrails"]
    kill_switch = result["kill_switch_rules"]
    broker_block = result["broker_account_dependency_block"]

    return f"""# AIOS Forex C1 Risk Position Sizing Review V1 Report

## Campaign Scope

This report applies the P4 C1 risk and position-sizing review lane for `c1-eur-buy` only. It consumes the P3 walk-forward/OOS proof output and defines conservative review-only risk rules for a later P5 supervised demo-trade readiness review.

This report does not execute trades, access broker/API systems, access credentials, access accounts, calculate real order size from live data, place orders, close orders, move money, activate schedulers, activate daemons, activate webhooks, activate production, or approve autonomous trading.

## Trader Meaning

{TRADER_MEANING}

## Source Evidence

{_source_list(result)}

## P3 Entry Condition

- p3_proof_status: `{result["p3_proof_status"]}`
- p3_p4_readiness: `{result["p3_p4_readiness"]}`
- input_score: `{result["input_score"]}`
- input_status: `{result["input_status"]}`
- p4_entry_passed: `{result["p4_entry_assessment"]["passed"]}`

## P4 Risk Policy

{_risk_policy_table(result)}

## Position-Sizing Formula

- formula_only: `{formula["formula_only"]}`
- risk_amount: `{formula["risk_amount_formula"]}`
- position_size: `{formula["position_size_formula"]}`
- required_inputs: `{formula["required_inputs"]}`
- blocked_inputs: `{formula["blocked_inputs"]}`
- real_sizing_block: `{formula["real_sizing_block"]}`

## Max Loss Rules

- max_risk_per_trade_percent: `{max_loss["max_risk_per_trade_percent"]}`
- max_daily_loss_percent: `{max_loss["max_daily_loss_percent"]}`
- max_weekly_loss_percent: `{max_loss["max_weekly_loss_percent"]}`
- max_consecutive_losses: `{max_loss["max_consecutive_losses"]}`
- max_strategy_drawdown_percent: `{max_loss["max_strategy_drawdown_percent"]}`
- rule: {max_loss["rule"]}

## Daily Stop Rules

- daily_stop_rule: `{daily_stop["daily_stop_rule"]}`
- max_daily_loss_percent: `{daily_stop["max_daily_loss_percent"]}`
- trigger: {daily_stop["trigger"]}
- reset_condition: {daily_stop["reset_condition"]}
- calculation_dependency: {daily_stop["calculation_dependency"]}

## One-Order Rules

- one_order_rule: `{one_order["one_order_rule"]}`
- max_open_positions: `{one_order["max_open_positions"]}`
- max_orders_per_signal: `{one_order["max_orders_per_signal"]}`
- no_retry_loop: `{one_order["no_retry_loop"]}`
- rule: {one_order["rule"]}

## TP/SL Guardrails

- stop_loss_required: `{tp_sl["stop_loss_required"]}`
- take_profit_required: `{tp_sl["take_profit_required"]}`
- minimum_reward_to_risk: `{tp_sl["minimum_reward_to_risk"]}`
- rule: {tp_sl["rule"]}

## Kill Switch Rules

- kill_switch_required: `{kill_switch["kill_switch_required"]}`
- triggers:
{_bullet_list(kill_switch["triggers"])}
- rule: {kill_switch["rule"]}

## Broker Account Dependency Block

- blocked: `{broker_block["blocked"]}`
- reason: {broker_block["reason"]}
- p5_requirement: {broker_block["p5_requirement"]}

## P5 Readiness Decision

- p4_review_status: `{result["p4_review_status"]}`
- p5_readiness: `{result["p5_readiness"]}`
- post_p4_score: `{result["post_p4_score"]}`
- post_p4_status: `{result["post_p4_status"]}`
- passed_requirements: `{result["passed_requirements"]}`
- failed_requirements: `{result["failed_requirements"]}`

## Next Required Lane

`{result["next_required_lane"]}`

## What This Completes

- completes P4 risk and position-sizing review for `c1-eur-buy`
- defines the conservative risk policy, max loss gates, daily stop, one-order rule, TP/SL guardrails, position-sizing formula, broker/account dependency block, and kill-switch triggers
- decides whether the candidate can move to P5 supervised demo-trade readiness review only

## What This Does Not Approve

{_bullet_list(result["forbidden_actions"])}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""


def render_next_action_queue(result: dict[str, Any]) -> str:
    """Render the next-action queue for the P4 risk review lane."""

    if result["p5_readiness"] == "P5_READY":
        required_actions = [
            "start P5 supervised demo-trade readiness review",
            "require sanitized broker/account snapshot before real sizing",
            "require owner approval before any demo order",
            "require TP/SL guardrail verification",
            "require one-order rule verification",
            "require daily-stop and kill-switch verification",
            "keep live trading blocked",
        ]
        remaining_blocks = [
            "P4 review is not demo trading approval.",
            "P4 review is not live trading approval.",
            "Broker/API, credentials, account access, order action, money movement, production, and autonomous trading remain blocked.",
            "22/6 autonomy, vacation/luxury mode, and 100-120 percent return claims remain blocked.",
        ]
    else:
        required_actions = [
            "return to P3 proof repair or P4 risk-rule completion",
            "rerun P4 review after repair",
            "keep demo/live trading blocked",
        ]
        remaining_blocks = [
            "P5 supervised demo-trade readiness review is blocked.",
            "Demo trading remains blocked.",
            "Live trading remains blocked.",
            "Broker/API, credentials, account access, order action, money movement, production, and autonomous trading remain blocked.",
        ]

    return f"""# AIOS Forex C1 Risk Position Sizing Review Next Action Queue V1

## Purpose

This queue records the next action after P4 C1 risk and position-sizing review.

## P4 Review Status

`{result["p4_review_status"]}`

## P5 Readiness

`{result["p5_readiness"]}`

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
    "evaluate_c1_risk_position_sizing_review",
    "render_owner_report",
    "render_next_action_queue",
]
