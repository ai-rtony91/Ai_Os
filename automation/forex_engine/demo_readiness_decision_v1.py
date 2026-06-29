"""Repo-safe demo readiness decision gate."""

from __future__ import annotations

from typing import Any, Mapping

from automation.forex_engine.candidate_selector_hardening_v1 import (
    run_candidate_selector_hardening_v1,
)
from automation.forex_engine.evidence_depth_walkforward_sufficiency_v1 import (
    PROTECTED_FALSE_FIELDS,
    run_evidence_depth_walkforward_sufficiency_v1,
)


PACKET_ID = "PKT-FOREX-EVIDENCE-CANDIDATE-DEMO-READINESS-CONSOLIDATED-V1"


def run_demo_readiness_decision_v1(
    owner_review_complete: bool = False,
    protected_broker_proof_complete: bool = False,
) -> dict[str, Any]:
    evidence = run_evidence_depth_walkforward_sufficiency_v1(
        {"observed_trade_count": 36, "observed_walkforward_windows": 6}
    )
    selector = run_candidate_selector_hardening_v1()
    blockers: list[str] = []
    if not evidence["promotion_allowed"]:
        blockers.append("evidence_depth_not_sufficient")
    if not selector["promotion_allowed"]:
        blockers.append("candidate_selector_not_review_ready")
    if not owner_review_complete:
        blockers.append("owner_review_required")
    if not protected_broker_proof_complete:
        blockers.append("protected_broker_connection_proof_required")

    result: dict[str, Any] = {
        "demo_readiness_status": "DEMO_READINESS_OWNER_AND_PROOF_BLOCKED"
        if blockers
        else "DEMO_READINESS_REVIEW_COMPLETE_NOT_EXECUTED",
        "selected_candidate": selector["selected_candidate"],
        "evidence_status": evidence["sufficiency_status"],
        "candidate_selector_status": selector["selector_status"],
        "demo_allowed": False,
        "owner_review_required": not owner_review_complete,
        "broker_connection_required": not protected_broker_proof_complete,
        "protected_boundary": "owner_review_and_protected_broker_connection_proof",
        "demo_blockers": blockers or ["demo_execution_not_authorized_by_repo_safe_packet"],
        "readiness_reasons": _readiness_reasons(evidence, selector),
        "safe_next_action": (
            "Complete owner review and protected broker proof outside this repo-safe packet; "
            "do not authorize demo execution here."
        ),
        "packet_id": PACKET_ID,
    }
    result.update({field: False for field in PROTECTED_FALSE_FIELDS})
    return result


def _readiness_reasons(evidence: Mapping[str, Any], selector: Mapping[str, Any]) -> list[str]:
    return [
        f"evidence_status:{evidence.get('sufficiency_status')}",
        f"candidate_selector_status:{selector.get('selector_status')}",
        "demo_execution_remains_blocked_without_owner_review_and_protected_broker_proof",
    ]


def build_report_markdown(result: Mapping[str, Any]) -> str:
    selected = result.get("selected_candidate") or {}
    return "\n".join(
        [
            "# AIOS Forex Demo Readiness Decision V1 Report",
            "",
            f"Demo readiness status: {result.get('demo_readiness_status')}",
            f"Selected candidate: {selected.get('candidate_id')}",
            f"Evidence status: {result.get('evidence_status')}",
            f"Candidate selector status: {result.get('candidate_selector_status')}",
            f"Demo allowed: {result.get('demo_allowed')}",
            "",
            "Demo blockers:",
            *[f"- {item}" for item in result.get("demo_blockers", [])],
            "",
            "Safe next action:",
            str(result.get("safe_next_action")),
            "",
        ]
    )


__all__ = ["build_report_markdown", "run_demo_readiness_decision_v1"]
