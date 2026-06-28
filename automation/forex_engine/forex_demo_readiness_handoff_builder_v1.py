"""Demo readiness owner handoff composer for final review decision state."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from .forex_final_review_decision_gate_v1 import (
    FINAL_REVIEW_DEFERRED_OWNER_VALIDATION,
    FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED,
    FINAL_REVIEW_LOCAL_REPAIR_REQUIRED,
    FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED,
    FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED,
    FINAL_REVIEW_READY,
    FINAL_REVIEW_SAFETY_BLOCKED,
)

DEMO_HANDOFF_VERSION = "1.0"

DEMO_HANDOFF_REVIEW_READY = "DEMO_HANDOFF_REVIEW_READY"
DEMO_HANDOFF_OWNER_EVIDENCE_REQUIRED = "DEMO_HANDOFF_OWNER_EVIDENCE_REQUIRED"
DEMO_HANDOFF_LOCAL_REPAIR_REQUIRED = "DEMO_HANDOFF_LOCAL_REPAIR_REQUIRED"
DEMO_HANDOFF_EXTERNAL_EVIDENCE_REQUIRED = "DEMO_HANDOFF_EXTERNAL_EVIDENCE_REQUIRED"
DEMO_HANDOFF_PROTECTED_AUTHORITY_REQUIRED = "DEMO_HANDOFF_PROTECTED_AUTHORITY_REQUIRED"
DEMO_HANDOFF_SAFETY_BLOCKED = "DEMO_HANDOFF_SAFETY_BLOCKED"
DEMO_HANDOFF_DEFERRED_OWNER_VALIDATION = "DEMO_HANDOFF_DEFERRED_OWNER_VALIDATION"

SAFETY_BOUNDARY_TEXT = "This handoff does not place trades and does not authorize trading."


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _map_status(status: str | None) -> str:
    mapping = {
        FINAL_REVIEW_READY: DEMO_HANDOFF_REVIEW_READY,
        FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED: DEMO_HANDOFF_OWNER_EVIDENCE_REQUIRED,
        FINAL_REVIEW_LOCAL_REPAIR_REQUIRED: DEMO_HANDOFF_LOCAL_REPAIR_REQUIRED,
        FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED: DEMO_HANDOFF_EXTERNAL_EVIDENCE_REQUIRED,
        FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED: DEMO_HANDOFF_PROTECTED_AUTHORITY_REQUIRED,
        FINAL_REVIEW_SAFETY_BLOCKED: DEMO_HANDOFF_SAFETY_BLOCKED,
        FINAL_REVIEW_DEFERRED_OWNER_VALIDATION: DEMO_HANDOFF_DEFERRED_OWNER_VALIDATION,
    }
    return mapping.get(status or "", DEMO_HANDOFF_REVIEW_READY)


def _default_candidate_summary() -> dict[str, Any]:
    return {
        "candidate_id": "candidate-id-placeholder",
        "candidate_label": "DEMO_READY_CANDIDATE_PLACEHOLDER",
        "risk_profile": "not_computed",
        "evidence_pack": "placeholder-pack",
    }


def build_demo_readiness_handoff(
    final_review_decision: Mapping[str, Any] | None,
    *,
    strict: bool = False,
    candidate_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    final_status = str((final_review_decision or {}).get("status", ""))
    summary = _map_status(final_status)
    candidate = dict(_default_candidate_summary())
    if candidate_summary:
        candidate.update({str(k): v for k, v in candidate_summary.items()})
    decision_summary = (final_review_decision or {}).get("evidence_summary", {})
    safety_flags = (final_review_decision or {}).get("no_execution_safety_flags", {})

    owner_checklist = [
        "Evidence reviewed",
        "Risk reviewed",
        "Broker/API still disabled",
        "Credential access not granted",
        "Demo/live execution not authorized",
        "Next action is review only",
    ]

    next_step = {
        DEMO_HANDOFF_REVIEW_READY: "Route package to owner for review and policy signoff only.",
        DEMO_HANDOFF_OWNER_EVIDENCE_REQUIRED: "Collect owner evidence and resubmit the lane.",
        DEMO_HANDOFF_LOCAL_REPAIR_REQUIRED: "Repair local evidence and rerun the gate.",
        DEMO_HANDOFF_EXTERNAL_EVIDENCE_REQUIRED: "Attach approved external evidence before handoff.",
        DEMO_HANDOFF_PROTECTED_AUTHORITY_REQUIRED: "Route through owner protected-authority workflow before handoff.",
        DEMO_HANDOFF_SAFETY_BLOCKED: "Resolve safety violations before any readiness handoff.",
        DEMO_HANDOFF_DEFERRED_OWNER_VALIDATION: "Wait for owner manual deferral closure.",
    }.get(summary, "Review owner handoff requirements.")

    return {
        "handoff_version": DEMO_HANDOFF_VERSION,
        "generated_at": _now_iso(),
        "status": summary,
        "strict_mode": bool(strict),
        "candidate_summary": candidate,
        "final_review_status": final_status,
        "no_trade_no_broker_no_credentials": True,
        "owner_checklist": owner_checklist,
        "handoff_statement": SAFETY_BOUNDARY_TEXT,
        "next_action": next_step,
        "decision_evidence_summary": decision_summary,
        "decision_safety_flags": {
            "broker_api_calls": bool(safety_flags.get("broker_api_calls", False)),
            "credential_access": bool(safety_flags.get("credential_access", False)),
            "money_movement": bool(safety_flags.get("money_movement", False)),
            "production_activation": bool(safety_flags.get("production_activation", False)),
            "live_trading_authorized": bool(safety_flags.get("live_trading_authorized", False)),
            "demo_trade_authorized": bool(safety_flags.get("demo_trade_authorized", False)),
        },
    }


def demo_readiness_handoff_to_markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# Forex Demo Readiness Handoff Builder V1",
        f"Generated: {result.get('generated_at')}",
        f"Status: {result.get('status')}",
        f"Final review status: {result.get('final_review_status')}",
        f"No-trade boundary active: {result.get('no_trade_no_broker_no_credentials')}",
        f"Owner checklist completed: {False if result.get('status') == DEMO_HANDOFF_REVIEW_READY else False}",
        "",
        f"{result.get('handoff_statement')}",
        "",
        "## Candidate summary placeholder",
    ]
    candidate = result.get("candidate_summary", {})
    if isinstance(candidate, Mapping):
        for key, value in candidate.items():
            lines.append(f"- {key}: {value}")

    lines.append("")
    lines.append("## Owner checklist")
    for item in result.get("owner_checklist", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Next action")
    lines.append(str(result.get("next_action")))
    return "\n".join(lines)


def demo_readiness_handoff_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "handoff_version": result.get("handoff_version", DEMO_HANDOFF_VERSION),
        "generated_at": result.get("generated_at"),
        "status": result.get("status"),
        "final_review_status": result.get("final_review_status"),
        "strict_mode": bool(result.get("strict_mode", False)),
        "no_trade_no_broker_no_credentials": bool(result.get("no_trade_no_broker_no_credentials", False)),
        "next_action": result.get("next_action"),
        "candidate_summary": dict(result.get("candidate_summary", {})),
        "owner_checklist": list(result.get("owner_checklist", [])),
        "handoff_statement": result.get("handoff_statement"),
        "decision_evidence_summary": result.get("decision_evidence_summary"),
        "decision_safety_flags": dict(result.get("decision_safety_flags", {})),
    }


__all__ = [
    "DEMO_HANDOFF_DEFERRED_OWNER_VALIDATION",
    "DEMO_HANDOFF_EXTERNAL_EVIDENCE_REQUIRED",
    "DEMO_HANDOFF_LOCAL_REPAIR_REQUIRED",
    "DEMO_HANDOFF_OWNER_EVIDENCE_REQUIRED",
    "DEMO_HANDOFF_PROTECTED_AUTHORITY_REQUIRED",
    "DEMO_HANDOFF_REVIEW_READY",
    "DEMO_HANDOFF_SAFETY_BLOCKED",
    "build_demo_readiness_handoff",
    "demo_readiness_handoff_to_jsonable_dict",
    "demo_readiness_handoff_to_markdown",
    "DEMO_HANDOFF_VERSION",
    "SAFETY_BOUNDARY_TEXT",
]
