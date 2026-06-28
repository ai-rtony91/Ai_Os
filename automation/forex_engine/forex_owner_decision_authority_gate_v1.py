"""Owner decision authority gate for final review handoff."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from .forex_demo_readiness_handoff_builder_v1 import (
    DEMO_HANDOFF_EXTERNAL_EVIDENCE_REQUIRED,
    DEMO_HANDOFF_LOCAL_REPAIR_REQUIRED,
    DEMO_HANDOFF_OWNER_EVIDENCE_REQUIRED,
    DEMO_HANDOFF_PROTECTED_AUTHORITY_REQUIRED,
    DEMO_HANDOFF_REVIEW_READY,
    DEMO_HANDOFF_SAFETY_BLOCKED,
)
from .forex_final_review_decision_gate_v1 import (
    FINAL_REVIEW_DEFERRED_OWNER_VALIDATION,
    FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED,
    FINAL_REVIEW_LOCAL_REPAIR_REQUIRED,
    FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED,
    FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED,
    FINAL_REVIEW_READY,
    FINAL_REVIEW_SAFETY_BLOCKED,
)

OWNER_AUTHORITY_GATE_VERSION = "1.0"

OWNER_AUTHORITY_REVIEW_REQUIRED = "OWNER_AUTHORITY_REVIEW_REQUIRED"
OWNER_AUTHORITY_APPROVAL_READY = "OWNER_AUTHORITY_APPROVAL_READY"
OWNER_AUTHORITY_BLOCKED_BY_MISSING_EVIDENCE = "OWNER_AUTHORITY_BLOCKED_BY_MISSING_EVIDENCE"
OWNER_AUTHORITY_BLOCKED_BY_PROTECTED_DEPENDENCY = "OWNER_AUTHORITY_BLOCKED_BY_PROTECTED_DEPENDENCY"
OWNER_AUTHORITY_SAFETY_BLOCKED = "OWNER_AUTHORITY_SAFETY_BLOCKED"
OWNER_AUTHORITY_DEFERRED = "OWNER_AUTHORITY_DEFERRED"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _map_status(final_review_status: str) -> str:
    if final_review_status == FINAL_REVIEW_READY:
        return OWNER_AUTHORITY_APPROVAL_READY
    if final_review_status in {
        FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED,
        FINAL_REVIEW_LOCAL_REPAIR_REQUIRED,
        FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED,
    }:
        return OWNER_AUTHORITY_BLOCKED_BY_MISSING_EVIDENCE
    if final_review_status == FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED:
        return OWNER_AUTHORITY_BLOCKED_BY_PROTECTED_DEPENDENCY
    if final_review_status == FINAL_REVIEW_SAFETY_BLOCKED:
        return OWNER_AUTHORITY_SAFETY_BLOCKED
    if final_review_status == FINAL_REVIEW_DEFERRED_OWNER_VALIDATION:
        return OWNER_AUTHORITY_DEFERRED
    return OWNER_AUTHORITY_REVIEW_REQUIRED


def _collect_questions(payload: Mapping[str, Any], status: str) -> list[str]:
    questions = [
        "Does owner evidence clearly match the final packet status?",
        "Are all protected action boundaries marked as disabled?",
        "Is demo/live execution still disabled?",
        "Are credentials explicitly disallowed for this review?",
        "Has broker/API activation been explicitly rejected?",
        "Is risk summary included with owner-facing rationale?",
    ]
    if status == OWNER_AUTHORITY_APPROVAL_READY:
        questions.append("No additional protected dependency appears unresolved.")
    elif status == OWNER_AUTHORITY_BLOCKED_BY_PROTECTED_DEPENDENCY:
        questions.append("Collect owner-approved evidence on each protected dependency.")
    elif status == OWNER_AUTHORITY_BLOCKED_BY_MISSING_EVIDENCE:
        questions.append("Attach missing local/owner/external evidence items.")
    return questions


def _collect_required_items(payload: Mapping[str, Any]) -> list[str]:
    decisions = payload.get("owner_decision_checklist", [])
    required = [
        "owner approval packet",
        "decision evidence summary",
        "no-execution boundary contract",
    ]
    if decisions:
        required.extend([f"carry-forward: {item}" for item in decisions])
    return required


def evaluate_owner_decision_authority(
    final_review_decision: Mapping[str, Any] | None,
    *,
    demo_readiness_handoff: Mapping[str, Any] | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    final_status = str((final_review_decision or {}).get("status", ""))
    status = _map_status(final_status)

    handoff = demo_readiness_handoff or {}
    handoff_status = str(handoff.get("status", ""))
    protected_dependency_required = handoff_status in {
        DEMO_HANDOFF_PROTECTED_AUTHORITY_REQUIRED,
        DEMO_HANDOFF_SAFETY_BLOCKED,
    }
    safety_flags = dict((final_review_decision or {}).get("no_execution_safety_flags", {}))
    blockers = [
        "final owner approval status not ready",
        "protected dependency unresolved",
        "safety flags present",
    ]
    if status == OWNER_AUTHORITY_APPROVAL_READY:
        blockers = []
    elif status == OWNER_AUTHORITY_REVIEW_REQUIRED:
        blockers = ["final review is not ready for owner authorization"]
    elif status == OWNER_AUTHORITY_DEFERRED:
        blockers.append("owner validation deferred")
    elif status == OWNER_AUTHORITY_BLOCKED_BY_PROTECTED_DEPENDENCY:
        blockers = ["broker/API/credential/account/trade dependencies unresolved"]
    elif status == OWNER_AUTHORITY_BLOCKED_BY_MISSING_EVIDENCE:
        blockers = ["final evidence or review packet not complete"]
    elif status == OWNER_AUTHORITY_SAFETY_BLOCKED:
        blockers = ["safety violation detected by decision gate"]

    authority_questions = _collect_questions((final_review_decision or {}), status)
    required_items = _collect_required_items((final_review_decision or {}))

    return {
        "authority_gate_version": OWNER_AUTHORITY_GATE_VERSION,
        "generated_at": _now_iso(),
        "strict_mode": bool(strict),
        "status": status,
        "final_review_status": final_status,
        "handoff_status": handoff_status,
        "protected_dependency_required": bool(protected_dependency_required),
        "auto_approval_allowed": False,
        "owner_review_required": status in {
            OWNER_AUTHORITY_APPROVAL_READY,
            OWNER_AUTHORITY_REVIEW_REQUIRED,
        },
        "questions": authority_questions,
        "required_next_items": required_items,
        "owner_next_checklist": [
            "Review all evidence references for redaction boundaries",
            "Verify no order text, no broker API activation text, no credential assignment text",
            "Verify this is review-only handoff",
            "Approve owner authority route explicitly",
        ],
        "owner_blockers": blockers,
        "next_owner_actions": [
            "Confirm with owner review channel before production or demo execution",
            "Update packet status only from owner governance lane",
        ],
        "final_decision_safety_flags": {
            "broker_api_calls": bool(safety_flags.get("broker_api_calls", False)),
            "credential_access": bool(safety_flags.get("credential_access", False)),
            "money_movement": bool(safety_flags.get("money_movement", False)),
            "production_activation": bool(safety_flags.get("production_activation", False)),
            "demo_trade_authorized": bool(safety_flags.get("demo_trade_authorized", False)),
            "live_trading_authorized": bool(safety_flags.get("live_trading_authorized", False)),
        },
    }


def owner_decision_authority_to_markdown(payload: Mapping[str, Any]) -> str:
    lines = [
        "# Forex Owner Decision Authority Gate V1",
        f"Generated: {payload.get('generated_at')}",
        f"Status: {payload.get('status')}",
        f"Final Review Status: {payload.get('final_review_status')}",
        "",
        "## Authority Conditions",
        f"- auto_approval_allowed: {payload.get('auto_approval_allowed')}",
        f"- Protected dependency required: {payload.get('protected_dependency_required')}",
        f"- Owner review required: {payload.get('owner_review_required')}",
        "",
        "## Required Items",
    ]
    for item in payload.get("required_next_items", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Owner Questions")
    for question in payload.get("questions", []):
        lines.append(f"- {question}")
    lines.append("")
    lines.append("## Owner Blockers")
    for blocker in payload.get("owner_blockers", []):
        lines.append(f"- {blocker}")
    return "\n".join(lines)


def owner_decision_authority_to_jsonable_dict(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "authority_gate_version": payload.get("authority_gate_version", OWNER_AUTHORITY_GATE_VERSION),
        "generated_at": payload.get("generated_at"),
        "status": payload.get("status"),
        "final_review_status": payload.get("final_review_status"),
        "handoff_status": payload.get("handoff_status"),
        "auto_approval_allowed": bool(payload.get("auto_approval_allowed", False)),
        "owner_review_required": bool(payload.get("owner_review_required", False)),
        "protected_dependency_required": bool(payload.get("protected_dependency_required", False)),
        "questions": list(payload.get("questions", [])),
        "required_next_items": list(payload.get("required_next_items", [])),
        "owner_next_checklist": list(payload.get("owner_next_checklist", [])),
        "owner_blockers": list(payload.get("owner_blockers", [])),
        "next_owner_actions": list(payload.get("next_owner_actions", [])),
        "final_decision_safety_flags": dict(payload.get("final_decision_safety_flags", {})),
    }


__all__ = [
    "OWNER_AUTHORITY_APPROVAL_READY",
    "OWNER_AUTHORITY_BLOCKED_BY_MISSING_EVIDENCE",
    "OWNER_AUTHORITY_BLOCKED_BY_PROTECTED_DEPENDENCY",
    "OWNER_AUTHORITY_DEFERRED",
    "OWNER_AUTHORITY_REVIEW_REQUIRED",
    "OWNER_AUTHORITY_SAFETY_BLOCKED",
    "OWNER_AUTHORITY_GATE_VERSION",
    "evaluate_owner_decision_authority",
    "owner_decision_authority_to_jsonable_dict",
    "owner_decision_authority_to_markdown",
]
