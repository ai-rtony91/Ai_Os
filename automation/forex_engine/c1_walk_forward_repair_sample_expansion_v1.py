"""Deterministic C1 walk-forward repair and sample-expansion analyzer.

This module performs repo-local evidence analysis only. It does not access
broker APIs, credentials, accounts, orders, schedulers, daemons, webhooks,
production systems, or trading execution paths.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from automation.forex_engine import c1_eur_buy_evidence_gap_closure_v1
from automation.forex_engine import mitigation_optimization_t_v1


CAMPAIGN_ID = "AIOS-FOREX-P1B-C1-WALK-FORWARD-REPAIR-SAMPLE-EXPANSION-V1"
CANDIDATE_ID = "c1-eur-buy"
CANDIDATE_NAME = "paper_long_run_supervisor_v2 LONG EURUSD"
INPUT_SCORE = 85
INPUT_STATUS = "NEEDS_MORE_EVIDENCE"
MINIMUM_WINDOWS = 4
MINIMUM_TRADES_PER_WINDOW = 5
MINIMUM_PROFIT_FACTOR = 1.25
MINIMUM_EXPECTANCY = 0.0
MAXIMUM_DRAWDOWN = 10.0

ALLOWED_REPAIR_CLASSIFICATIONS = {
    "REPAIR_READY",
    "REPAIR_REQUIRES_SAMPLE_EXPANSION",
    "REPAIR_REQUIRES_DRAWDOWN_GUARD",
    "REPAIR_REQUIRES_MITIGATION_REWORK",
    "REPAIR_REQUIRES_CANDIDATE_REPLACEMENT",
    "SOURCE_EVIDENCE_NOT_ENOUGH",
}

SOURCE_EVIDENCE = [
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_EUR_BUY_EVIDENCE_GAP_CLOSURE_V1.json",
        "use": "Defines C1 starting blockers, score 85, P3 NOT_READY, and failed windows wf-02, wf-03, and wf-04.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_EUR_BUY_EVIDENCE_GAP_CLOSURE_V1_REPORT.md",
        "use": "Confirms C1 remains best current candidate while failed windows and drawdown, sample, and mitigation blockers remain open.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_WALK_FORWARD_WINDOW_MATRIX_V1.md",
        "use": "Provides baseline failed-window metrics before repair.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_WALK_FORWARD_FAILURE_ROOT_CAUSE_MATRIX_V1.md",
        "use": "Classifies the baseline root causes for failed windows.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_WALKFORWARD_ROOT_CAUSE_DRYRUN_V2.md",
        "use": "Identifies the prior mitigation-path reject state and walk-forward gate failure.",
    },
    {
        "path": "automation/forex_engine/mitigation_optimization_t_v1.py",
        "use": "Calculates deterministic local mitigation repair output without broker, credential, account, order, or trading action.",
    },
]

FORBIDDEN_ACTIONS = [
    "broker/API access",
    "credentials",
    "account access",
    "demo trade without evidence gate",
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

TRADER_MEANING = (
    "AIOS is testing whether the best EUR/USD buy setup can be repaired enough "
    "to survive bad market windows before risking demo or live money."
)

FINAL_OWNER_SENTENCE_P3_READY = (
    "AIOS Forex P1B C1 walk-forward repair is complete: c1-eur-buy is "
    "source-cleared for P3 walk-forward/OOS proof review only, while live "
    "trading, broker/API, credentials, money movement, 22/6 autonomy, "
    "vacation/luxury mode, and 100-120 percent return claims remain blocked "
    "until separately proven and approved."
)

FINAL_OWNER_SENTENCE_NOT_READY = (
    "AIOS Forex P1B C1 walk-forward repair is complete: c1-eur-buy remains a "
    "repair candidate, but P3 is not ready until failed windows, drawdown "
    "containment, sample sufficiency, and mitigation-path blockers are "
    "source-cleared; live trading, broker/API, credentials, money movement, "
    "22/6 autonomy, vacation/luxury mode, and 100-120 percent return claims "
    "remain blocked until separately proven and approved."
)

BASELINE_WINDOW_EVIDENCE = {
    "wf-02": "Baseline wf-02 failed with expectancy -0.80, profit factor 0.93, and negative_expectancy plus low_profit_factor blockers.",
    "wf-03": "Baseline wf-03 failed with expectancy -2.00, profit factor 0.61, and negative_expectancy plus low_profit_factor blockers.",
    "wf-04": "Baseline wf-04 failed with expectancy -1499.00, profit factor 0.01, drawdown 75.20, and excessive_drawdown blocker.",
}


def _window_map(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("window_id")): dict(row) for row in rows}


def _repair_classification(row: dict[str, Any] | None) -> str:
    if not row:
        return "SOURCE_EVIDENCE_NOT_ENOUGH"

    blockers = list(row.get("blocker_reasons", []))
    if not blockers:
        return "REPAIR_READY"
    if int(row.get("closed_trade_count", 0)) < MINIMUM_TRADES_PER_WINDOW:
        return "REPAIR_REQUIRES_SAMPLE_EXPANSION"
    if _safe_float(row.get("max_drawdown")) > MAXIMUM_DRAWDOWN:
        return "REPAIR_REQUIRES_DRAWDOWN_GUARD"
    if _safe_float(row.get("expectancy")) <= MINIMUM_EXPECTANCY:
        return "REPAIR_REQUIRES_MITIGATION_REWORK"
    if _safe_float(row.get("profit_factor")) < MINIMUM_PROFIT_FACTOR:
        return "REPAIR_REQUIRES_MITIGATION_REWORK"
    return "SOURCE_EVIDENCE_NOT_ENOUGH"


def _safe_float(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return number if number == number else 0.0


def _build_window_assessment(
    window_id: str,
    optimized_row: dict[str, Any] | None,
) -> dict[str, Any]:
    classification = _repair_classification(optimized_row)
    if optimized_row:
        blockers = list(optimized_row.get("blocker_reasons", []))
        decision = (
            f"{window_id} repair clears: optimized evidence has "
            f"{optimized_row.get('closed_trade_count')} trades, expectancy "
            f"{_safe_float(optimized_row.get('expectancy')):.2f}, profit factor "
            f"{_safe_float(optimized_row.get('profit_factor')):.2f}, drawdown "
            f"{_safe_float(optimized_row.get('max_drawdown')):.2f}, and blockers "
            f"{', '.join(blockers) if blockers else 'none'}."
        )
        calculated_repair = {
            "closed_trade_count": int(optimized_row.get("closed_trade_count", 0)),
            "expectancy": _safe_float(optimized_row.get("expectancy")),
            "profit_factor": _safe_float(optimized_row.get("profit_factor")),
            "max_drawdown": _safe_float(optimized_row.get("max_drawdown")),
            "blocker_reasons": blockers,
        }
    else:
        decision = f"{window_id} repair lacks optimized source evidence."
        calculated_repair = {}

    return {
        "target": window_id,
        "classification": classification,
        "repair_route": "deterministic_mitigation_repair",
        "starting_evidence": BASELINE_WINDOW_EVIDENCE[window_id],
        "calculated_repair": calculated_repair,
        "source_files": [
            "Reports/forex_delivery/AIOS_FOREX_WALK_FORWARD_WINDOW_MATRIX_V1.md",
            "Reports/forex_delivery/AIOS_FOREX_WALK_FORWARD_FAILURE_ROOT_CAUSE_MATRIX_V1.md",
            "automation/forex_engine/mitigation_optimization_t_v1.py",
        ],
        "decision": decision,
        "next_action": "Carry this repaired window into P3 walk-forward/OOS proof review only."
        if classification == "REPAIR_READY"
        else "Continue C1 repair before P3 review.",
    }


def _build_blocker_assessments(optimized: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = list(optimized.get("window_results", []))
    closed_counts = [int(row.get("closed_trade_count", 0)) for row in rows]
    max_drawdown = max((_safe_float(row.get("max_drawdown")) for row in rows), default=0.0)
    remaining_blockers = [
        str(blocker)
        for blocker in optimized.get("mitigation_remaining_blockers", [])
        if blocker
    ]
    gate_cleared = bool(optimized.get("walk_forward_gate_cleared"))

    sample_ready = (
        len(rows) >= MINIMUM_WINDOWS
        and all(count >= MINIMUM_TRADES_PER_WINDOW for count in closed_counts)
    )
    drawdown_ready = max_drawdown <= MAXIMUM_DRAWDOWN
    mitigation_ready = gate_cleared and not remaining_blockers

    return {
        "drawdown_containment": {
            "target": "drawdown_containment",
            "classification": "REPAIR_READY"
            if drawdown_ready
            else "REPAIR_REQUIRES_DRAWDOWN_GUARD",
            "repair_route": "drawdown_guard_verification",
            "starting_evidence": "Baseline repair queue left drawdown_containment open and wf-04 recorded 75.20 drawdown.",
            "calculated_repair": {
                "maximum_optimized_drawdown": max_drawdown,
                "drawdown_threshold": MAXIMUM_DRAWDOWN,
                "window_drawdowns": {
                    str(row.get("window_id")): _safe_float(row.get("max_drawdown"))
                    for row in rows
                },
            },
            "source_files": [
                "Reports/forex_delivery/AIOS_FOREX_BEFORE_AFTER_WALK_FORWARD_COMPARISON_V1.md",
                "automation/forex_engine/mitigation_optimization_t_v1.py",
            ],
            "decision": "Drawdown containment closes because optimized drawdown stays inside the 10.00 gate."
            if drawdown_ready
            else "Drawdown containment remains open because optimized drawdown exceeds the active gate.",
            "next_action": "Carry drawdown containment into P3 proof review only."
            if drawdown_ready
            else "Continue drawdown-guard repair before P3 review.",
        },
        "insufficient_sample": {
            "target": "insufficient_sample",
            "classification": "REPAIR_READY"
            if sample_ready
            else "REPAIR_REQUIRES_SAMPLE_EXPANSION",
            "repair_route": "sample_expansion_verification",
            "starting_evidence": "Baseline repair queue left optimized wf-02, wf-03, and wf-04 blocked by insufficient_sample.",
            "calculated_repair": {
                "minimum_windows": MINIMUM_WINDOWS,
                "minimum_trades_per_window": MINIMUM_TRADES_PER_WINDOW,
                "observed_windows": len(rows),
                "observed_closed_trades_by_window": {
                    str(row.get("window_id")): int(row.get("closed_trade_count", 0))
                    for row in rows
                },
                "observed_total_closed_trades": sum(closed_counts),
            },
            "source_files": [
                "Reports/forex_delivery/AIOS_FOREX_BEFORE_AFTER_WALK_FORWARD_COMPARISON_V1.md",
                "automation/forex_engine/mitigation_optimization_t_v1.py",
            ],
            "decision": "Sample sufficiency closes because optimized evidence has four windows with at least five closed trades each."
            if sample_ready
            else "Sample sufficiency remains open because one or more optimized windows lacks five closed trades.",
            "next_action": "Carry the 4-window and 5-trade minimum into P3 proof review only."
            if sample_ready
            else "Expand the C1 sample before P3 review.",
        },
        "mitigation_path": {
            "target": "mitigation_path",
            "classification": "REPAIR_READY"
            if mitigation_ready
            else "REPAIR_REQUIRES_MITIGATION_REWORK",
            "repair_route": "mitigation_gate_recheck",
            "starting_evidence": "Root-cause evidence previously identified candidate_status REJECT and walk_forward_gate_cleared false.",
            "calculated_repair": {
                "candidate_status": optimized.get("candidate_status", ""),
                "walk_forward_gate_cleared": gate_cleared,
                "remaining_blockers": remaining_blockers,
            },
            "source_files": [
                "Reports/forex_delivery/AIOS_FOREX_WALKFORWARD_ROOT_CAUSE_DRYRUN_V2.md",
                "automation/forex_engine/mitigation_optimization_t_v1.py",
            ],
            "decision": "Mitigation path closes because the deterministic local mitigation output reports a cleared gate and no remaining blockers."
            if mitigation_ready
            else "Mitigation path remains open because the deterministic local mitigation output does not clear the gate.",
            "next_action": "Route C1 to P3 walk-forward/OOS proof review only."
            if mitigation_ready
            else "Continue mitigation rework before P3 review.",
        },
    }


def _all_p3_requirements_clear(
    assessments: dict[str, dict[str, Any]],
    optimized_payload: dict[str, Any],
) -> bool:
    required = {
        "wf-02",
        "wf-03",
        "wf-04",
        "drawdown_containment",
        "insufficient_sample",
        "mitigation_path",
    }
    return (
        required.issubset(assessments)
        and all(
            assessments[target]["classification"] == "REPAIR_READY"
            for target in required
        )
        and optimized_payload.get("candidate_status") != "REJECT"
        and bool(optimized_payload.get("walk_forward_gate_cleared"))
    )


def _routed_repairs(
    *,
    p3_readiness: str,
    repair_assessments: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    if p3_readiness == "P3_READY":
        return [
            {
                "repair_id": "p3_walk_forward_oos_proof_review",
                "route": "P3_WALK_FORWARD_OOS_PROOF",
                "required_action": "Run P3 walk-forward/OOS proof review only with all trading and broker actions still blocked.",
            }
        ]

    routed = []
    for target, assessment in repair_assessments.items():
        classification = assessment["classification"]
        if classification == "REPAIR_READY":
            continue
        route = (
            "P1C_CANDIDATE_REPLACEMENT_REVIEW"
            if classification == "REPAIR_REQUIRES_CANDIDATE_REPLACEMENT"
            else "P1B_CONTINUE_C1_REPAIR"
        )
        routed.append(
            {
                "repair_id": target,
                "route": route,
                "required_action": assessment["next_action"],
            }
        )
    return routed


def evaluate_c1_walk_forward_repair_sample_expansion() -> dict[str, Any]:
    """Return the source-backed C1 repair and sample-expansion decision."""

    gap_closure = c1_eur_buy_evidence_gap_closure_v1.evaluate_c1_eur_buy_gap_closure()
    mitigation = mitigation_optimization_t_v1.run_mitigation_optimization(
        write_reports=False
    )
    optimized = dict(mitigation.get("optimized_results", {}))
    optimized["candidate_status"] = mitigation.get("candidate_status", "")

    optimized_by_window = _window_map(list(optimized.get("window_results", [])))
    repair_assessments: dict[str, dict[str, Any]] = {
        window_id: _build_window_assessment(window_id, optimized_by_window.get(window_id))
        for window_id in ("wf-02", "wf-03", "wf-04")
    }
    repair_assessments.update(_build_blocker_assessments(optimized))

    p3_ready = _all_p3_requirements_clear(repair_assessments, optimized)
    p3_readiness = "P3_READY" if p3_ready else "NOT_READY"
    repair_status = (
        "REPAIRED_P3_READY"
        if p3_ready
        else "PARTIAL_REPAIR_MORE_EVIDENCE_REQUIRED"
    )
    next_required_lane = (
        "P3_WALK_FORWARD_OOS_PROOF"
        if p3_ready
        else "P1B_CONTINUE_C1_REPAIR"
    )
    post_repair_score = 100 if p3_ready else INPUT_SCORE
    post_repair_status = "P3_READY" if p3_ready else INPUT_STATUS

    closed_repairs = [
        target
        for target, assessment in repair_assessments.items()
        if assessment["classification"] == "REPAIR_READY"
    ]
    open_repairs = [
        target
        for target, assessment in repair_assessments.items()
        if assessment["classification"] != "REPAIR_READY"
    ]
    routed_repairs = _routed_repairs(
        p3_readiness=p3_readiness,
        repair_assessments=repair_assessments,
    )

    observed_counts = repair_assessments["insufficient_sample"]["calculated_repair"][
        "observed_closed_trades_by_window"
    ]
    sample_expansion_target = {
        "classification": repair_assessments["insufficient_sample"]["classification"],
        "minimum_windows": MINIMUM_WINDOWS,
        "minimum_trades_per_window": MINIMUM_TRADES_PER_WINDOW,
        "minimum_total_closed_trades": MINIMUM_WINDOWS * MINIMUM_TRADES_PER_WINDOW,
        "observed_closed_trades_by_window": observed_counts,
        "observed_total_closed_trades": sum(int(value) for value in observed_counts.values()),
        "sample_status": "CLOSED_FOR_P1B_REPAIR"
        if repair_assessments["insufficient_sample"]["classification"] == "REPAIR_READY"
        else "OPEN_SAMPLE_EXPANSION_REQUIRED",
        "p3_review_requirement": "Use at least four walk-forward/OOS windows with at least five closed trades per window before any further promotion.",
    }

    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": INPUT_SCORE,
        "post_repair_score": post_repair_score,
        "input_status": INPUT_STATUS,
        "post_repair_status": post_repair_status,
        "repair_status": repair_status,
        "p3_readiness": p3_readiness,
        "next_required_lane": next_required_lane,
        "failed_windows": ["wf-02", "wf-03", "wf-04"],
        "repair_assessments": deepcopy(repair_assessments),
        "sample_expansion_target": sample_expansion_target,
        "drawdown_containment_decision": deepcopy(
            repair_assessments["drawdown_containment"]
        ),
        "mitigation_path_decision": deepcopy(repair_assessments["mitigation_path"]),
        "closed_repairs": closed_repairs,
        "open_repairs": open_repairs,
        "routed_repairs": routed_repairs,
        "source_evidence": deepcopy(SOURCE_EVIDENCE),
        "starting_gap_closure_status": gap_closure["gap_closure_status"],
        "starting_open_gaps": list(gap_closure["open_gaps"]),
        "mitigation_candidate_status": mitigation["candidate_status"],
        "mitigation_walk_forward_improved": mitigation["walk_forward_improved"],
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "final_owner_sentence": FINAL_OWNER_SENTENCE_P3_READY
        if p3_ready
        else FINAL_OWNER_SENTENCE_NOT_READY,
    }


def _bullet_list(items: list[str] | tuple[str, ...]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def _source_list(result: dict[str, Any]) -> str:
    return "\n".join(
        f"- `{source['path']}`: {source['use']}"
        for source in result["source_evidence"]
    )


def _repair_table(result: dict[str, Any]) -> str:
    rows = [
        "| target | classification | decision | next action |",
        "|---|---|---|---|",
    ]
    for target, assessment in result["repair_assessments"].items():
        rows.append(
            "| `{}` | `{}` | {} | {} |".format(
                target,
                assessment["classification"],
                assessment["decision"],
                assessment["next_action"],
            )
        )
    return "\n".join(rows)


def _failed_window_table(result: dict[str, Any]) -> str:
    rows = [
        "| window | repair classification | optimized trades | optimized expectancy | optimized profit factor | optimized drawdown | optimized blockers |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for window in result["failed_windows"]:
        assessment = result["repair_assessments"][window]
        repair = assessment["calculated_repair"]
        blockers = repair.get("blocker_reasons", [])
        rows.append(
            "| `{}` | `{}` | {} | {:.2f} | {:.2f} | {:.2f} | {} |".format(
                window,
                assessment["classification"],
                repair.get("closed_trade_count", 0),
                _safe_float(repair.get("expectancy")),
                _safe_float(repair.get("profit_factor")),
                _safe_float(repair.get("max_drawdown")),
                ", ".join(blockers) if blockers else "none",
            )
        )
    return "\n".join(rows)


def _routed_list(result: dict[str, Any]) -> str:
    return _bullet_list(
        [
            f"`{item['repair_id']}` -> `{item['route']}`: {item['required_action']}"
            for item in result["routed_repairs"]
        ]
    )


def render_owner_report(result: dict[str, Any]) -> str:
    """Render the owner-facing Markdown report."""

    sample = result["sample_expansion_target"]
    drawdown = result["drawdown_containment_decision"]
    mitigation = result["mitigation_path_decision"]
    return f"""# AIOS Forex C1 Walk-Forward Repair Sample Expansion V1 Report

## Campaign Scope

This report applies the P1B C1 walk-forward repair and sample-expansion lane for `c1-eur-buy` only. It converts the prior gap-closure blockers into deterministic repo-local repair assessments and decides whether C1 can enter P3 walk-forward/OOS proof review.

This report does not execute trades, access broker/API systems, access credentials, access accounts, place orders, close orders, move money, activate schedulers, activate daemons, activate webhooks, activate production, or approve autonomous trading.

## Trader Meaning

{TRADER_MEANING}

## Source Evidence

{_source_list(result)}

## Failed Windows

{_failed_window_table(result)}

## Repair Assessments

{_repair_table(result)}

## Sample Expansion Target

- minimum_windows: `{sample["minimum_windows"]}`
- minimum_trades_per_window: `{sample["minimum_trades_per_window"]}`
- minimum_total_closed_trades: `{sample["minimum_total_closed_trades"]}`
- observed_closed_trades_by_window: `{sample["observed_closed_trades_by_window"]}`
- observed_total_closed_trades: `{sample["observed_total_closed_trades"]}`
- sample_status: `{sample["sample_status"]}`
- p3_review_requirement: {sample["p3_review_requirement"]}

## Drawdown Containment Decision

- classification: `{drawdown["classification"]}`
- decision: {drawdown["decision"]}

## Mitigation Path Decision

- classification: `{mitigation["classification"]}`
- candidate_status: `{mitigation["calculated_repair"]["candidate_status"]}`
- walk_forward_gate_cleared: `{mitigation["calculated_repair"]["walk_forward_gate_cleared"]}`
- remaining_blockers: `{mitigation["calculated_repair"]["remaining_blockers"]}`
- decision: {mitigation["decision"]}

## Post-Repair Status

- input_score: `{result["input_score"]}`
- post_repair_score: `{result["post_repair_score"]}`
- input_status: `{result["input_status"]}`
- post_repair_status: `{result["post_repair_status"]}`
- repair_status: `{result["repair_status"]}`

## P3 Readiness Decision

p3_readiness: `{result["p3_readiness"]}`

The P3 readiness decision is limited to walk-forward/OOS proof review. It does not approve demo, broker/API, credential, account, order, money movement, production, or autonomous trading actions.

## Next Required Lane

`{result["next_required_lane"]}`

## What This Completes

- converts the C1 failed-window gap closure into deterministic repair assessments
- tests wf-02, wf-03, and wf-04 against current local mitigation output
- checks drawdown containment, sample sufficiency, and mitigation-path state
- records closed repairs: `{result["closed_repairs"]}`
- records open repairs: `{result["open_repairs"]}`
- routes next review: `{result["next_required_lane"]}`

## What This Does Not Approve

{_bullet_list(result["forbidden_actions"])}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""


def render_next_action_queue(result: dict[str, Any]) -> str:
    """Render the next-action queue for the repair lane."""

    if result["p3_readiness"] == "P3_READY":
        required_actions = [
            "run P3 walk-forward/OOS proof review only",
            "preserve the four-window and five-trade-per-window evidence target",
            "rerun P1/P2 scoring after P3 proof review",
            "keep demo/live trading blocked",
        ]
        remaining_blocks = [
            "P3 proof review is not live trading approval.",
            "Broker/API, credentials, account access, order action, money movement, production, and autonomous trading remain blocked.",
            "22/6 autonomy, vacation/luxury mode, and 100-120 percent return claims remain blocked.",
        ]
    else:
        required_actions = [
            "continue C1 repair if evidence can still improve",
            "route to candidate replacement review if C1 remains unstable",
            "rerun P1/P2 scoring after repair changes",
            "keep demo/live trading blocked",
        ]
        remaining_blocks = [
            "failed windows remain open",
            "drawdown containment remains open",
            "sample sufficiency remains open",
            "mitigation path remains open",
        ]

    return f"""# AIOS Forex C1 Walk-Forward Repair Sample Expansion Next Action Queue V1

## Purpose

This queue records the next action after P1B C1 walk-forward repair and sample-expansion analysis.

## Repair Status

- repair_status: `{result["repair_status"]}`
- p3_readiness: `{result["p3_readiness"]}`
- post_repair_score: `{result["post_repair_score"]}`

## Closed Repairs

{_bullet_list([f"`{item}`" for item in result["closed_repairs"]])}

## Open Repairs

{_bullet_list([f"`{item}`" for item in result["open_repairs"]])}

## Routed Repairs

{_routed_list(result)}

## Sample Expansion Target

- minimum_windows: `{result["sample_expansion_target"]["minimum_windows"]}`
- minimum_trades_per_window: `{result["sample_expansion_target"]["minimum_trades_per_window"]}`
- minimum_total_closed_trades: `{result["sample_expansion_target"]["minimum_total_closed_trades"]}`
- observed_total_closed_trades: `{result["sample_expansion_target"]["observed_total_closed_trades"]}`
- sample_status: `{result["sample_expansion_target"]["sample_status"]}`

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
    "evaluate_c1_walk_forward_repair_sample_expansion",
    "render_owner_report",
    "render_next_action_queue",
]
