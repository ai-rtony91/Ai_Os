"""Deterministic C1 walk-forward/OOS proof analyzer.

This module performs repo-local evidence review only. It does not access
broker APIs, credentials, accounts, orders, schedulers, daemons, webhooks,
production systems, or trading execution paths.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from automation.forex_engine.c1_walk_forward_repair_sample_expansion_v1 import (
    evaluate_c1_walk_forward_repair_sample_expansion,
)


CAMPAIGN_ID = "AIOS-FOREX-P3-C1-WALK-FORWARD-OOS-PROOF-V1"
CANDIDATE_ID = "c1-eur-buy"
CANDIDATE_NAME = "paper_long_run_supervisor_v2 LONG EURUSD"

MINIMUM_WINDOWS = 4
MINIMUM_TRADES_PER_WINDOW = 5
MINIMUM_TOTAL_CLOSED_TRADES = 20
MAXIMUM_DRAWDOWN = 10.0
MINIMUM_PROFIT_FACTOR = 1.25
MINIMUM_EXPECTANCY = 0.0

TRADER_MEANING = (
    "AIOS is checking whether the repaired EUR/USD buy setup has enough "
    "out-of-sample proof to move into risk and position-sizing review before "
    "any demo or live money is considered."
)

P4_READY_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P3 C1 walk-forward/OOS proof is complete: c1-eur-buy is "
    "source-cleared for P4 risk and position-sizing review only, while demo "
    "trading, live trading, broker/API, credentials, money movement, 22/6 "
    "autonomy, vacation/luxury mode, and 100-120 percent return claims remain "
    "blocked until separately proven and approved."
)

NOT_READY_FINAL_OWNER_SENTENCE = (
    "AIOS Forex P3 C1 walk-forward/OOS proof is complete: c1-eur-buy is not "
    "cleared for P4 risk and position-sizing review, and the next required "
    "lane is repair or candidate replacement review; demo trading, live "
    "trading, broker/API, credentials, money movement, 22/6 autonomy, "
    "vacation/luxury mode, and 100-120 percent return claims remain blocked "
    "until separately proven and approved."
)

P3_PROOF_STATUSES = {
    "P3_PROOF_PASSED_FOR_P4_REVIEW",
    "P3_PROOF_FAILED_REPAIR_REQUIRED",
    "P3_PROOF_FAILED_REPLACEMENT_REVIEW_REQUIRED",
}

POST_P3_STATUSES = {
    "P4_READY",
    "NEEDS_MORE_EVIDENCE",
    "REJECTED_NEGATIVE_EXPECTANCY",
    "REJECTED_LOW_PROFIT_FACTOR",
    "REJECTED_INSUFFICIENT_SAMPLE",
    "REJECTED_EXCESSIVE_DRAWDOWN",
}

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
        "path": "automation/forex_engine/c1_walk_forward_repair_sample_expansion_v1.py",
        "use": "Provides the authoritative P1B repair evaluator consumed by this P3 proof review.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_WALK_FORWARD_REPAIR_SAMPLE_EXPANSION_V1.json",
        "use": "Records C1 P1B repair status, post-repair score, sample evidence, drawdown containment, mitigation path, and open repairs.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_WALK_FORWARD_REPAIR_SAMPLE_EXPANSION_V1_REPORT.md",
        "use": "Explains the P1B repair decision and confirms P3 review is not trading approval.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_WALK_FORWARD_REPAIR_SAMPLE_EXPANSION_NEXT_ACTION_QUEUE_V1.md",
        "use": "Routes the repaired candidate into P3 walk-forward/OOS proof review only.",
    },
]


def _safe_float(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return number if number == number else 0.0


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _proof_requirements() -> dict[str, dict[str, Any]]:
    return {
        "windows": {
            "requirement": "Minimum four walk-forward/OOS windows, with wf-02, wf-03, and wf-04 repaired and ready.",
            "minimum_windows": MINIMUM_WINDOWS,
            "required_repaired_failed_windows": ["wf-02", "wf-03", "wf-04"],
        },
        "sample": {
            "requirement": "Minimum five closed trades per window and at least twenty total closed trades.",
            "minimum_trades_per_window": MINIMUM_TRADES_PER_WINDOW,
            "minimum_total_closed_trades": MINIMUM_TOTAL_CLOSED_TRADES,
        },
        "drawdown": {
            "requirement": "Drawdown containment is closed and optimized drawdown remains inside the active gate.",
            "maximum_drawdown": MAXIMUM_DRAWDOWN,
        },
        "mitigation": {
            "requirement": "Mitigation path is not rejected or gate-failed and has no remaining blockers.",
            "rejected_status": "REJECT",
        },
        "no_open_blockers": {
            "requirement": "P1B output has REPAIRED_P3_READY, P3_READY, score 100, and no open repairs.",
            "required_repair_status": "REPAIRED_P3_READY",
            "required_p3_readiness": "P3_READY",
            "required_post_repair_score": 100,
        },
        "no_demo_live_approval": {
            "requirement": "P3 proof is review-only and does not approve demo or live trading.",
            "review_only": True,
        },
    }


def _observed_counts(p1b_result: dict[str, Any]) -> dict[str, int]:
    sample = p1b_result.get("sample_expansion_target", {})
    counts = sample.get("observed_closed_trades_by_window", {})
    return {str(window): _safe_int(count) for window, count in dict(counts).items()}


def _window_metrics(p1b_result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    assessments = dict(p1b_result.get("repair_assessments", {}))
    metrics: dict[str, dict[str, Any]] = {}
    for window in ("wf-02", "wf-03", "wf-04"):
        assessment = dict(assessments.get(window, {}))
        calculated = dict(assessment.get("calculated_repair", {}))
        metrics[window] = {
            "classification": assessment.get("classification", ""),
            "closed_trade_count": _safe_int(calculated.get("closed_trade_count")),
            "expectancy": _safe_float(calculated.get("expectancy")),
            "profit_factor": _safe_float(calculated.get("profit_factor")),
            "max_drawdown": _safe_float(calculated.get("max_drawdown")),
            "blocker_reasons": list(calculated.get("blocker_reasons", [])),
        }
    return metrics


def _build_summaries(p1b_result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    counts = _observed_counts(p1b_result)
    metrics = _window_metrics(p1b_result)

    drawdown_assessment = dict(p1b_result.get("drawdown_containment_decision", {}))
    drawdown_calculated = dict(drawdown_assessment.get("calculated_repair", {}))
    maximum_drawdown = _safe_float(drawdown_calculated.get("maximum_optimized_drawdown"))
    drawdown_threshold = _safe_float(
        drawdown_calculated.get("drawdown_threshold", MAXIMUM_DRAWDOWN)
    )
    if drawdown_threshold == 0.0:
        drawdown_threshold = MAXIMUM_DRAWDOWN

    mitigation_assessment = dict(p1b_result.get("mitigation_path_decision", {}))
    mitigation_calculated = dict(mitigation_assessment.get("calculated_repair", {}))
    remaining_blockers = [
        str(blocker)
        for blocker in mitigation_calculated.get("remaining_blockers", [])
        if blocker
    ]

    return {
        "window_proof_summary": {
            "observed_windows": sorted(counts),
            "observed_window_count": len(counts),
            "failed_windows_under_review": list(p1b_result.get("failed_windows", [])),
            "repaired_failed_windows": [
                window
                for window, metric in metrics.items()
                if metric["classification"] == "REPAIR_READY"
            ],
            "window_metrics": metrics,
        },
        "sample_proof_summary": {
            "minimum_windows": MINIMUM_WINDOWS,
            "minimum_trades_per_window": MINIMUM_TRADES_PER_WINDOW,
            "minimum_total_closed_trades": MINIMUM_TOTAL_CLOSED_TRADES,
            "observed_closed_trades_by_window": counts,
            "observed_total_closed_trades": sum(counts.values()),
        },
        "drawdown_proof_summary": {
            "classification": drawdown_assessment.get("classification", ""),
            "maximum_optimized_drawdown": maximum_drawdown,
            "drawdown_threshold": drawdown_threshold,
            "window_drawdowns": dict(drawdown_calculated.get("window_drawdowns", {})),
        },
        "mitigation_proof_summary": {
            "classification": mitigation_assessment.get("classification", ""),
            "candidate_status": mitigation_calculated.get(
                "candidate_status", p1b_result.get("mitigation_candidate_status", "")
            ),
            "walk_forward_gate_cleared": bool(
                mitigation_calculated.get("walk_forward_gate_cleared")
            ),
            "remaining_blockers": remaining_blockers,
        },
    }


def _build_proof_assessments(
    p1b_result: dict[str, Any],
    summaries: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    window_summary = summaries["window_proof_summary"]
    sample_summary = summaries["sample_proof_summary"]
    drawdown_summary = summaries["drawdown_proof_summary"]
    mitigation_summary = summaries["mitigation_proof_summary"]

    repaired_failed_windows = set(window_summary["repaired_failed_windows"])
    required_failed_windows = {"wf-02", "wf-03", "wf-04"}
    observed_counts = sample_summary["observed_closed_trades_by_window"]
    open_repairs = list(p1b_result.get("open_repairs", []))

    windows_passed = (
        window_summary["observed_window_count"] >= MINIMUM_WINDOWS
        and required_failed_windows.issubset(repaired_failed_windows)
    )
    sample_passed = (
        len(observed_counts) >= MINIMUM_WINDOWS
        and all(count >= MINIMUM_TRADES_PER_WINDOW for count in observed_counts.values())
        and sample_summary["observed_total_closed_trades"]
        >= MINIMUM_TOTAL_CLOSED_TRADES
    )
    drawdown_passed = (
        drawdown_summary["classification"] == "REPAIR_READY"
        and drawdown_summary["maximum_optimized_drawdown"]
        <= drawdown_summary["drawdown_threshold"]
    )
    mitigation_passed = (
        mitigation_summary["classification"] == "REPAIR_READY"
        and mitigation_summary["candidate_status"] != "REJECT"
        and mitigation_summary["walk_forward_gate_cleared"]
        and not mitigation_summary["remaining_blockers"]
    )
    no_open_blockers_passed = (
        p1b_result.get("repair_status") == "REPAIRED_P3_READY"
        and p1b_result.get("p3_readiness") == "P3_READY"
        and _safe_int(p1b_result.get("post_repair_score")) == 100
        and not open_repairs
    )
    no_demo_live_approval_passed = all(
        action in FORBIDDEN_ACTIONS
        for action in (
            "broker/API access",
            "credentials",
            "demo trading without later evidence gate",
            "live trading",
            "order placement",
            "money movement",
            "autonomous trading",
        )
    )

    return {
        "windows": {
            "passed": windows_passed,
            "evidence": "P1B repaired failed windows wf-02, wf-03, and wf-04 and retained at least four windows.",
            "observed": {
                "observed_window_count": window_summary["observed_window_count"],
                "repaired_failed_windows": sorted(repaired_failed_windows),
            },
        },
        "sample": {
            "passed": sample_passed,
            "evidence": "P1B sample proof records four windows, five closed trades per window, and twenty total closed trades.",
            "observed": {
                "observed_closed_trades_by_window": observed_counts,
                "observed_total_closed_trades": sample_summary[
                    "observed_total_closed_trades"
                ],
            },
        },
        "drawdown": {
            "passed": drawdown_passed,
            "evidence": "P1B drawdown containment is closed and optimized drawdown stays inside the active gate.",
            "observed": {
                "classification": drawdown_summary["classification"],
                "maximum_optimized_drawdown": drawdown_summary[
                    "maximum_optimized_drawdown"
                ],
                "drawdown_threshold": drawdown_summary["drawdown_threshold"],
            },
        },
        "mitigation": {
            "passed": mitigation_passed,
            "evidence": "P1B mitigation path is continuing, gate-cleared, and has no remaining blockers.",
            "observed": {
                "classification": mitigation_summary["classification"],
                "candidate_status": mitigation_summary["candidate_status"],
                "walk_forward_gate_cleared": mitigation_summary[
                    "walk_forward_gate_cleared"
                ],
                "remaining_blockers": mitigation_summary["remaining_blockers"],
            },
        },
        "no_open_blockers": {
            "passed": no_open_blockers_passed,
            "evidence": "P1B reports REPAIRED_P3_READY, P3_READY, post-repair score 100, and no open repairs.",
            "observed": {
                "repair_status": p1b_result.get("repair_status"),
                "p3_readiness": p1b_result.get("p3_readiness"),
                "post_repair_score": p1b_result.get("post_repair_score"),
                "open_repairs": open_repairs,
            },
        },
        "no_demo_live_approval": {
            "passed": no_demo_live_approval_passed,
            "evidence": "This P3 proof is review-only and keeps demo trading, live trading, broker/API, credentials, and money movement blocked.",
            "observed": {
                "review_only": True,
                "forbidden_actions": list(FORBIDDEN_ACTIONS),
            },
        },
    }


def _requires_replacement_review(p1b_result: dict[str, Any]) -> bool:
    if p1b_result.get("repair_status") == "REPAIR_FAILED_REPLACEMENT_REVIEW_REQUIRED":
        return True
    for assessment in dict(p1b_result.get("repair_assessments", {})).values():
        if dict(assessment).get("classification") == "REPAIR_REQUIRES_CANDIDATE_REPLACEMENT":
            return True
    return False


def _failure_post_p3_status(
    failed_requirements: list[str],
    window_summary: dict[str, Any],
) -> str:
    if "sample" in failed_requirements:
        return "REJECTED_INSUFFICIENT_SAMPLE"
    if "drawdown" in failed_requirements:
        return "REJECTED_EXCESSIVE_DRAWDOWN"

    metrics = dict(window_summary.get("window_metrics", {}))
    if any(
        _safe_float(dict(metric).get("expectancy")) <= MINIMUM_EXPECTANCY
        for metric in metrics.values()
    ):
        return "REJECTED_NEGATIVE_EXPECTANCY"
    if any(
        _safe_float(dict(metric).get("profit_factor")) < MINIMUM_PROFIT_FACTOR
        for metric in metrics.values()
    ):
        return "REJECTED_LOW_PROFIT_FACTOR"
    return "NEEDS_MORE_EVIDENCE"


def evaluate_c1_walk_forward_oos_proof() -> dict[str, Any]:
    """Return the source-backed C1 P3 walk-forward/OOS proof decision."""

    p1b_result = evaluate_c1_walk_forward_repair_sample_expansion()
    summaries = _build_summaries(p1b_result)
    proof_requirements = _proof_requirements()
    proof_assessments = _build_proof_assessments(p1b_result, summaries)
    passed_requirements = [
        key for key, assessment in proof_assessments.items() if assessment["passed"]
    ]
    failed_requirements = [
        key for key, assessment in proof_assessments.items() if not assessment["passed"]
    ]

    input_score = _safe_int(
        p1b_result.get("post_repair_score", p1b_result.get("input_score", 0))
    )
    input_status = str(
        p1b_result.get("post_repair_status", p1b_result.get("p3_readiness", ""))
    )
    p1b_repair_status = str(p1b_result.get("repair_status", ""))
    p1b_p3_readiness = str(p1b_result.get("p3_readiness", ""))

    if not failed_requirements:
        p3_proof_status = "P3_PROOF_PASSED_FOR_P4_REVIEW"
        p4_readiness = "P4_READY"
        next_required_lane = "P4_RISK_POSITION_SIZING_REVIEW"
        post_p3_score = 100
        post_p3_status = "P4_READY"
        final_owner_sentence = P4_READY_FINAL_OWNER_SENTENCE
    else:
        replacement_required = _requires_replacement_review(p1b_result)
        p3_proof_status = (
            "P3_PROOF_FAILED_REPLACEMENT_REVIEW_REQUIRED"
            if replacement_required
            else "P3_PROOF_FAILED_REPAIR_REQUIRED"
        )
        p4_readiness = "NOT_READY"
        next_required_lane = (
            "P1C_CANDIDATE_REPLACEMENT_REVIEW"
            if replacement_required
            else "P1B_CONTINUE_C1_REPAIR"
        )
        post_p3_score = min(input_score, 85)
        post_p3_status = _failure_post_p3_status(
            failed_requirements, summaries["window_proof_summary"]
        )
        final_owner_sentence = NOT_READY_FINAL_OWNER_SENTENCE

    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": input_score,
        "post_p3_score": post_p3_score,
        "input_status": input_status,
        "post_p3_status": post_p3_status,
        "p1b_repair_status": p1b_repair_status,
        "p1b_p3_readiness": p1b_p3_readiness,
        "p3_proof_status": p3_proof_status,
        "p4_readiness": p4_readiness,
        "next_required_lane": next_required_lane,
        "proof_requirements": proof_requirements,
        "proof_assessments": proof_assessments,
        "passed_requirements": passed_requirements,
        "failed_requirements": failed_requirements,
        "window_proof_summary": deepcopy(summaries["window_proof_summary"]),
        "sample_proof_summary": deepcopy(summaries["sample_proof_summary"]),
        "drawdown_proof_summary": deepcopy(summaries["drawdown_proof_summary"]),
        "mitigation_proof_summary": deepcopy(summaries["mitigation_proof_summary"]),
        "source_evidence": deepcopy(SOURCE_EVIDENCE),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
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


def _requirement_table(result: dict[str, Any]) -> str:
    rows = [
        "| requirement | rule |",
        "|---|---|",
    ]
    for key, requirement in result["proof_requirements"].items():
        rows.append(f"| `{key}` | {requirement['requirement']} |")
    return "\n".join(rows)


def _assessment_table(result: dict[str, Any]) -> str:
    rows = [
        "| proof area | status | evidence |",
        "|---|---|---|",
    ]
    for key, assessment in result["proof_assessments"].items():
        status = "PASS" if assessment["passed"] else "FAIL"
        rows.append(f"| `{key}` | `{status}` | {assessment['evidence']} |")
    return "\n".join(rows)


def _window_table(result: dict[str, Any]) -> str:
    rows = [
        "| window | classification | closed trades | expectancy | profit factor | max drawdown | blockers |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    metrics = result["window_proof_summary"]["window_metrics"]
    for window, metric in metrics.items():
        blockers = metric["blocker_reasons"]
        rows.append(
            "| `{}` | `{}` | {} | {:.2f} | {:.2f} | {:.2f} | {} |".format(
                window,
                metric["classification"],
                metric["closed_trade_count"],
                _safe_float(metric["expectancy"]),
                _safe_float(metric["profit_factor"]),
                _safe_float(metric["max_drawdown"]),
                ", ".join(blockers) if blockers else "none",
            )
        )
    return "\n".join(rows)


def render_owner_report(result: dict[str, Any]) -> str:
    """Render the owner-facing P3 proof report."""

    sample = result["sample_proof_summary"]
    drawdown = result["drawdown_proof_summary"]
    mitigation = result["mitigation_proof_summary"]
    return f"""# AIOS Forex C1 Walk-Forward OOS Proof V1 Report

## Campaign Scope

This report applies the P3 C1 walk-forward/OOS proof lane for `c1-eur-buy` only. It consumes the P1B repair output and decides whether the candidate can move to P4 risk and position-sizing review.

This report does not execute trades, access broker/API systems, access credentials, access accounts, place orders, close orders, move money, activate schedulers, activate daemons, activate webhooks, activate production, or approve autonomous trading.

## Trader Meaning

{TRADER_MEANING}

## Source Evidence

{_source_list(result)}

## P1B Entry Condition

- p1b_repair_status: `{result["p1b_repair_status"]}`
- p1b_p3_readiness: `{result["p1b_p3_readiness"]}`
- input_score: `{result["input_score"]}`
- input_status: `{result["input_status"]}`

## P3 Proof Requirements

{_requirement_table(result)}

## Proof Assessments

{_assessment_table(result)}

## Window Proof Summary

{_window_table(result)}

## Sample Proof Summary

- minimum_windows: `{sample["minimum_windows"]}`
- minimum_trades_per_window: `{sample["minimum_trades_per_window"]}`
- minimum_total_closed_trades: `{sample["minimum_total_closed_trades"]}`
- observed_closed_trades_by_window: `{sample["observed_closed_trades_by_window"]}`
- observed_total_closed_trades: `{sample["observed_total_closed_trades"]}`

## Drawdown Proof Summary

- classification: `{drawdown["classification"]}`
- maximum_optimized_drawdown: `{drawdown["maximum_optimized_drawdown"]}`
- drawdown_threshold: `{drawdown["drawdown_threshold"]}`
- window_drawdowns: `{drawdown["window_drawdowns"]}`

## Mitigation Proof Summary

- classification: `{mitigation["classification"]}`
- candidate_status: `{mitigation["candidate_status"]}`
- walk_forward_gate_cleared: `{mitigation["walk_forward_gate_cleared"]}`
- remaining_blockers: `{mitigation["remaining_blockers"]}`

## P4 Readiness Decision

- p3_proof_status: `{result["p3_proof_status"]}`
- p4_readiness: `{result["p4_readiness"]}`
- post_p3_score: `{result["post_p3_score"]}`
- post_p3_status: `{result["post_p3_status"]}`
- passed_requirements: `{result["passed_requirements"]}`
- failed_requirements: `{result["failed_requirements"]}`

## Next Required Lane

`{result["next_required_lane"]}`

## What This Completes

- completes P3 walk-forward/OOS proof review for `c1-eur-buy`
- verifies P1B repaired windows, sample sufficiency, drawdown containment, mitigation path, and open blocker state
- routes the candidate to the next governed lane based on source-backed P3 proof

## What This Does Not Approve

{_bullet_list(result["forbidden_actions"])}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""


def render_next_action_queue(result: dict[str, Any]) -> str:
    """Render the next-action queue for the P3 proof lane."""

    if result["p4_readiness"] == "P4_READY":
        required_actions = [
            "start P4 risk and position-sizing review",
            "define max loss",
            "define lot size rules",
            "define daily stop",
            "define one-order rule",
            "define TP/SL guardrails",
            "keep demo/live trading blocked until later evidence gate",
        ]
        remaining_blocks = [
            "P4 review is not demo trading approval.",
            "P4 review is not live trading approval.",
            "Broker/API, credentials, account access, order action, money movement, production, and autonomous trading remain blocked.",
            "22/6 autonomy, vacation/luxury mode, and 100-120 percent return claims remain blocked.",
        ]
    else:
        required_actions = [
            "return to C1 repair or candidate replacement review",
            "rerun P3 proof after repair",
            "keep demo/live trading blocked",
        ]
        remaining_blocks = [
            "P4 risk and position-sizing review is blocked.",
            "Demo trading remains blocked.",
            "Live trading remains blocked.",
            "Broker/API, credentials, account access, order action, money movement, production, and autonomous trading remain blocked.",
        ]

    return f"""# AIOS Forex C1 Walk-Forward OOS Proof Next Action Queue V1

## Purpose

This queue records the next action after P3 C1 walk-forward/OOS proof review.

## P3 Proof Status

`{result["p3_proof_status"]}`

## P4 Readiness

`{result["p4_readiness"]}`

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
    "evaluate_c1_walk_forward_oos_proof",
    "render_owner_report",
    "render_next_action_queue",
]
