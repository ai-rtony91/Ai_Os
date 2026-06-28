"""Deterministic C1 EUR BUY evidence-gap closure classifier.

This module performs no broker, network, credential, account, order, scheduler,
daemon, webhook, production, or trading action. It only returns a static
source-backed gap classification from repo-local evidence reviewed in the
packet lane.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


FINAL_OWNER_SENTENCE_NOT_READY = (
    "AIOS Forex P1 C1 EUR BUY evidence-gap closure is complete: "
    "c1-eur-buy remains the best current candidate but is not P3-ready, "
    "and the next required lane is C1 walk-forward repair and sample expansion; "
    "live trading, broker/API, credentials, money movement, 22/6 autonomy, "
    "vacation/luxury mode, and 100-120 percent return claims remain blocked "
    "until separately proven and approved."
)

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

EVIDENCE_SOURCES = [
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_PROFIT_EVIDENCE_COMPRESSION_P1_P2_V1.json",
        "use": "Sets c1-eur-buy as best candidate with score 85 and NEEDS_MORE_EVIDENCE.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_PROFIT_CANDIDATE_SCOREBOARD_P1_P2_V1.json",
        "use": "Scores C1 at 85, gives zero walk-forward/OOS credit, and requires more evidence.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_PROFIT_EVIDENCE_COMPRESSION_P1_P2_V1_REPORT.md",
        "use": "States C1 is best current candidate but not P3-ready.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_PROFIT_EVIDENCE_GAP_QUEUE_P1_P2_V1.md",
        "use": "Lists missing non-conflicting readiness, passing walk-forward/OOS proof, drawdown containment, and sample depth.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_EUR_BUY_EVIDENCE_DEPTH_SCOREBOARD_V1.md",
        "use": "Provides strong P1 anchor metrics: 30 trades, expectancy 200.00, profit factor 999.00, and drawdown 0.00.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_EUR_BUY_WALK_FORWARD_STABILITY_SCOREBOARD_V1.md",
        "use": "Reports 4 windows, 3 failing windows, stable expectancy -325.45, drawdown 75.20, and blocker clearance false.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_C1_EUR_BUY_FAILURE_REGIME_SCOREBOARD_V1.md",
        "use": "Identifies failed windows wf-02, wf-03, wf-04 and verdict REQUIRE_OPTIMIZATION.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_WALK_FORWARD_WINDOW_MATRIX_V1.md",
        "use": "Provides per-window failure metrics and walk-forward gate cleared false.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_WALK_FORWARD_FAILURE_ROOT_CAUSE_MATRIX_V1.md",
        "use": "Confirms systemic failures in expectancy, profit factor, win rate, and loss profile.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_BEFORE_AFTER_WALK_FORWARD_COMPARISON_V1.md",
        "use": "Shows optimized rows still blocked by insufficient_sample and drawdown_containment.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_WALKFORWARD_ROOT_CAUSE_DRYRUN_V2.md",
        "use": "Identifies mitigation candidate_status REJECT and walk_forward_gate_cleared false.",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_WALK_FORWARD_DEPTH_PACKET_R_V1_REPORT.md",
        "use": "Confirms 1 passing window, 3 failing windows, and remaining walk-forward blockers.",
    },
    {
        "path": "Reports/forex_delivery/readiness_state_recalculation_v1_report.json",
        "use": "Contains readiness-looking bridge fields but unresolved review-chain blockers.",
    },
    {
        "path": "Reports/forex_delivery/review_chain_end_to_end_candidate_journey.json",
        "use": "Reports candidate journey incomplete and candidate bridge rejected.",
    },
    {
        "path": "Reports/forex_delivery/proof_bundle_to_candidate_bridge_report.json",
        "use": "Reports candidate bridge rejected with missing metrics and paper evidence not ready.",
    },
]

STRICT_EVIDENCE_PRECEDENCE = [
    "Failed walk-forward/OOS evidence overrides anchor metrics.",
    "Candidate-specific failure regime overrides general best-candidate optimism.",
    "Root-cause and before/after comparison artifacts override older readiness claims.",
    "Explicit blockers override implied readiness.",
    "Paper-only evidence cannot authorize demo or live trading.",
    "Strong P1 metrics can select a best candidate but cannot create P3 readiness by themselves.",
]

GAP_ASSESSMENTS = {
    "readiness_conflict": {
        "classification": "CLOSED_AS_STRICT_NOT_READY_DECISION",
        "status": "source_precedence_resolved",
        "source_files": [
            "Reports/forex_delivery/readiness_state_recalculation_v1_report.json",
            "Reports/forex_delivery/review_chain_end_to_end_candidate_journey.json",
            "Reports/forex_delivery/proof_bundle_to_candidate_bridge_report.json",
            "Reports/forex_delivery/AIOS_FOREX_C1_EUR_BUY_WALK_FORWARD_STABILITY_SCOREBOARD_V1.md",
        ],
        "evidence": (
            "Some bridge fields present readiness-looking metrics, but review-chain, "
            "candidate bridge, and C1-specific walk-forward evidence keep the candidate "
            "in a blocked evidence state."
        ),
        "decision": "Use strict precedence and classify C1 as NOT_READY for P3.",
        "next_action": "No readiness promotion; continue to repair lane.",
    },
    "wf_02_failed_window": {
        "classification": "OPEN_REPAIR_REQUIRED",
        "status": "failed_window",
        "source_files": [
            "Reports/forex_delivery/AIOS_FOREX_WALK_FORWARD_WINDOW_MATRIX_V1.md",
            "Reports/forex_delivery/AIOS_FOREX_WALK_FORWARD_FAILURE_ROOT_CAUSE_MATRIX_V1.md",
        ],
        "evidence": "wf-02 expectancy -0.80, profit factor 0.93, blockers negative_expectancy and low_profit_factor.",
        "decision": "Cannot clear P3 while wf-02 remains failed.",
        "next_action": "Repair or replace wf-02 with source-backed passing evidence.",
    },
    "wf_03_failed_window": {
        "classification": "OPEN_REPAIR_REQUIRED",
        "status": "failed_window",
        "source_files": [
            "Reports/forex_delivery/AIOS_FOREX_WALK_FORWARD_WINDOW_MATRIX_V1.md",
            "Reports/forex_delivery/AIOS_FOREX_WALK_FORWARD_FAILURE_ROOT_CAUSE_MATRIX_V1.md",
        ],
        "evidence": "wf-03 expectancy -2.00, profit factor 0.61, blockers negative_expectancy and low_profit_factor.",
        "decision": "Cannot clear P3 while wf-03 remains failed.",
        "next_action": "Repair or replace wf-03 with source-backed passing evidence.",
    },
    "wf_04_failed_window": {
        "classification": "OPEN_REPAIR_REQUIRED",
        "status": "failed_window",
        "source_files": [
            "Reports/forex_delivery/AIOS_FOREX_WALK_FORWARD_WINDOW_MATRIX_V1.md",
            "Reports/forex_delivery/AIOS_FOREX_C1_EUR_BUY_FAILURE_REGIME_SCOREBOARD_V1.md",
        ],
        "evidence": "wf-04 expectancy -1499.00, profit factor 0.01, drawdown 75.20, and excessive_drawdown blocker.",
        "decision": "Cannot clear P3 while wf-04 remains failed.",
        "next_action": "Repair or replace wf-04 with source-backed passing evidence.",
    },
    "drawdown_containment": {
        "classification": "OPEN_REPAIR_REQUIRED",
        "status": "blocker_remaining",
        "source_files": [
            "Reports/forex_delivery/AIOS_FOREX_BEFORE_AFTER_WALK_FORWARD_COMPARISON_V1.md",
            "Reports/forex_delivery/AIOS_FOREX_C1_EUR_BUY_WALK_FORWARD_STABILITY_SCOREBOARD_V1.md",
        ],
        "evidence": "Before/after evidence leaves drawdown_containment open and wf-04 records 75.20 drawdown.",
        "decision": "Drawdown containment is not source-cleared.",
        "next_action": "Close drawdown_containment with source-backed passing evidence.",
    },
    "insufficient_sample": {
        "classification": "OPEN_REPAIR_REQUIRED",
        "status": "blocker_remaining",
        "source_files": [
            "Reports/forex_delivery/AIOS_FOREX_BEFORE_AFTER_WALK_FORWARD_COMPARISON_V1.md",
            "Reports/forex_delivery/AIOS_FOREX_PROFIT_EVIDENCE_GAP_QUEUE_P1_P2_V1.md",
        ],
        "evidence": "Optimized wf-02, wf-03, and wf-04 rows remain blocked by insufficient_sample.",
        "decision": "Anchor sample depth does not clear post-repair window sample depth.",
        "next_action": "Close insufficient_sample with source-backed passing evidence.",
    },
    "mitigation_path": {
        "classification": "ROUTED_REPAIR_REQUIRED",
        "status": "candidate_status_reject",
        "source_files": [
            "Reports/forex_delivery/AIOS_FOREX_WALKFORWARD_ROOT_CAUSE_DRYRUN_V2.md",
            "Reports/forex_delivery/AIOS_FOREX_BEFORE_AFTER_WALK_FORWARD_COMPARISON_V1.md",
        ],
        "evidence": "Root-cause evidence identifies candidate_status REJECT and walk_forward_gate_cleared false.",
        "decision": "Mitigation path cannot promote C1 until it improves real candidate performance.",
        "next_action": "Route to C1 walk-forward repair and sample expansion.",
    },
    "p3_readiness": {
        "classification": "CLOSED_AS_NOT_READY",
        "status": "not_ready",
        "source_files": [
            "Reports/forex_delivery/AIOS_FOREX_PROFIT_EVIDENCE_COMPRESSION_P1_P2_V1_REPORT.md",
            "Reports/forex_delivery/AIOS_FOREX_WALK_FORWARD_DEPTH_PACKET_R_V1_REPORT.md",
            "Reports/forex_delivery/proof_bundle_to_candidate_bridge_report.json",
        ],
        "evidence": "No source-backed non-conflicting passing walk-forward/OOS proof exists for C1.",
        "decision": "P3 walk-forward/OOS proof review is blocked until C1 repair evidence passes.",
        "next_action": "Run P1B_C1_WALK_FORWARD_REPAIR_AND_SAMPLE_EXPANSION before any P3 lane.",
    },
}

ROUTED_GAPS = [
    {
        "gap_id": "wf_02_failed_window",
        "route": "P1B_C1_WALK_FORWARD_REPAIR_AND_SAMPLE_EXPANSION",
        "required_action": "repair or replace failed wf-02 window",
    },
    {
        "gap_id": "wf_03_failed_window",
        "route": "P1B_C1_WALK_FORWARD_REPAIR_AND_SAMPLE_EXPANSION",
        "required_action": "repair or replace failed wf-03 window",
    },
    {
        "gap_id": "wf_04_failed_window",
        "route": "P1B_C1_WALK_FORWARD_REPAIR_AND_SAMPLE_EXPANSION",
        "required_action": "repair or replace failed wf-04 window",
    },
    {
        "gap_id": "drawdown_containment",
        "route": "P1B_C1_WALK_FORWARD_REPAIR_AND_SAMPLE_EXPANSION",
        "required_action": "close drawdown_containment with source-backed evidence",
    },
    {
        "gap_id": "insufficient_sample",
        "route": "P1B_C1_WALK_FORWARD_REPAIR_AND_SAMPLE_EXPANSION",
        "required_action": "close insufficient_sample with source-backed evidence",
    },
    {
        "gap_id": "mitigation_path",
        "route": "P1B_C1_WALK_FORWARD_REPAIR_AND_SAMPLE_EXPANSION",
        "required_action": "repair mitigation path without bypassing walk-forward gates",
    },
]


def evaluate_c1_eur_buy_gap_closure() -> dict[str, Any]:
    """Return the source-backed C1 evidence-gap closure decision."""

    return {
        "candidate_id": "c1-eur-buy",
        "candidate_name": "paper_long_run_supervisor_v2 LONG EURUSD",
        "input_score": 85,
        "post_closure_score": 85,
        "input_status": "NEEDS_MORE_EVIDENCE",
        "post_closure_status": "NEEDS_MORE_EVIDENCE",
        "gap_closure_status": "PARTIAL_CLOSURE_NEXT_REPAIR_REQUIRED",
        "p3_readiness": "NOT_READY",
        "next_required_lane": "P1B_C1_WALK_FORWARD_REPAIR_AND_SAMPLE_EXPANSION",
        "evidence_sources": deepcopy(EVIDENCE_SOURCES),
        "strict_evidence_precedence": list(STRICT_EVIDENCE_PRECEDENCE),
        "gap_assessments": deepcopy(GAP_ASSESSMENTS),
        "closed_gaps": [
            "readiness_conflict",
            "p3_readiness",
        ],
        "open_gaps": [
            "wf_02_failed_window",
            "wf_03_failed_window",
            "wf_04_failed_window",
            "drawdown_containment",
            "insufficient_sample",
            "mitigation_path",
        ],
        "routed_gaps": deepcopy(ROUTED_GAPS),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "final_owner_sentence": FINAL_OWNER_SENTENCE_NOT_READY,
    }


def _bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _source_list(result: dict[str, Any]) -> str:
    return "\n".join(
        f"- `{source['path']}`: {source['use']}"
        for source in result["evidence_sources"]
    )


def _gap_table(result: dict[str, Any]) -> str:
    rows = [
        "| gap | classification | decision | next action |",
        "|---|---|---|---|",
    ]
    for gap_id, gap in result["gap_assessments"].items():
        rows.append(
            "| `{}` | `{}` | {} | {} |".format(
                gap_id,
                gap["classification"],
                gap["decision"],
                gap["next_action"],
            )
        )
    return "\n".join(rows)


def render_owner_report(result: dict[str, Any]) -> str:
    """Render the owner-facing Markdown report."""

    closed = _bullet_list(f"`{gap}`" for gap in result["closed_gaps"])
    open_gaps = _bullet_list(f"`{gap}`" for gap in result["open_gaps"])
    routed = _bullet_list(
        f"`{gap['gap_id']}` -> `{gap['route']}`: {gap['required_action']}"
        for gap in result["routed_gaps"]
    )
    return f"""# AIOS Forex C1 EUR BUY Evidence Gap Closure V1 Report

## Campaign Scope

This report closes the P1 evidence-gap classification lane for `c1-eur-buy` only. It reviews repo-local paper evidence, applies strict evidence precedence, and decides whether C1 can enter P3 walk-forward/OOS proof review.

This report does not execute trades, access broker/API systems, access credentials, access accounts, place orders, close orders, move money, activate schedulers, activate daemons, activate webhooks, activate production, or approve autonomous trading.

## Source Evidence

{_source_list(result)}

## Strict Evidence Precedence

{_bullet_list(result["strict_evidence_precedence"])}

## Candidate Before Closure

- candidate_id: `{result["candidate_id"]}`
- candidate_name: `{result["candidate_name"]}`
- input_score: `{result["input_score"]}`
- input_status: `{result["input_status"]}`
- anchor evidence: 30 paper trades, expectancy 200.00, profit factor 999.00, max drawdown 0.00, and paper-only safety.
- blocking evidence: 4 walk-forward windows, 1 passing window, 3 failing windows, stable expectancy -325.45, controlled drawdown 75.20, and walk-forward gate cleared false.

## Gap Closure Results

gap_closure_status: `{result["gap_closure_status"]}`

Closed gaps:

{closed}

Open gaps:

{open_gaps}

Routed gaps:

{routed}

{_gap_table(result)}

## Post-Closure Candidate Status

- post_closure_score: `{result["post_closure_score"]}`
- post_closure_status: `{result["post_closure_status"]}`
- c1-eur-buy remains the best current candidate because its P1 anchor score is still strongest.
- c1-eur-buy remains blocked from P3 because failed walk-forward/OOS evidence and mitigation blockers override the anchor metrics.

## P3 Readiness Decision

p3_readiness: `{result["p3_readiness"]}`

C1 is not source-cleared for P3 walk-forward/OOS proof review. The P3 decision is closed as `NOT_READY` because failed windows `wf-02`, `wf-03`, and `wf-04` remain open, `drawdown_containment` remains open, `insufficient_sample` remains open after optimization, and the mitigation path still reports a rejected gate state.

## Next Required Lane

`{result["next_required_lane"]}`

## What This Completes

- completes source-backed evidence-gap classification for `c1-eur-buy`
- resolves readiness-looking source conflict through strict evidence precedence
- preserves `c1-eur-buy` as best current candidate
- routes failed walk-forward windows and blockers to the repair lane
- preserves all trading, broker/API, credential, account, money movement, production, autonomy, 22/6, vacation/luxury, and 100-120 percent return blocks

## What This Does Not Approve

{_bullet_list(result["forbidden_actions"])}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""


def render_next_action_queue(result: dict[str, Any]) -> str:
    """Render the next-action queue for the repair lane."""

    closed = _bullet_list(f"`{gap}`" for gap in result["closed_gaps"])
    open_gaps = _bullet_list(f"`{gap}`" for gap in result["open_gaps"])
    routed = _bullet_list(
        f"`{gap['gap_id']}` -> `{gap['route']}`: {gap['required_action']}"
        for gap in result["routed_gaps"]
    )
    required_repairs = [
        "repair or replace failed wf-02 window",
        "repair or replace failed wf-03 window",
        "repair or replace failed wf-04 window",
        "close drawdown_containment with source-backed evidence",
        "close insufficient_sample with source-backed evidence",
        "rerun P1/P2 candidate scoring after repair",
    ]
    remaining_blocks = [
        "P3 walk-forward/OOS proof review is blocked until C1 repair evidence passes.",
        "Demo, broker/API, credential, account, order, money movement, production, and autonomous trading actions remain blocked.",
        "22/6 autonomy, vacation/luxury mode, and 100-120 percent return claims remain blocked.",
    ]
    return f"""# AIOS Forex C1 EUR BUY Evidence Gap Closure Next Action Queue V1

## Purpose

This queue records the next source-backed repair actions after P1 C1 EUR BUY evidence-gap closure.

## Closure Status

- gap_closure_status: `{result["gap_closure_status"]}`
- p3_readiness: `{result["p3_readiness"]}`
- post_closure_status: `{result["post_closure_status"]}`
- post_closure_score: `{result["post_closure_score"]}`

## Closed Gaps

{closed}

## Open Gaps

{open_gaps}

## Routed Gaps

{routed}

## Next Required Lane

`{result["next_required_lane"]}`

## Required Repair Actions

{_bullet_list(required_repairs)}

## Remaining Blocks

{_bullet_list(remaining_blocks)}

## Final Owner Sentence

{result["final_owner_sentence"]}
"""
