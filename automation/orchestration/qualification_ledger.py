"""Qualification ledger preview helpers for Night Supervisor Gate 7."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


ALLOWED_FINAL_STATUSES = {"PROVISIONAL", "TESTED_PENDING_REVIEW", "BLOCKED", "NOT_QUALIFIED"}
FORBIDDEN_FINAL_STATUSES = {"TRUSTED", "QUALIFIED", "AUTONOMOUS", "GRAVEYARD_OPERATOR"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_qualification_entry(
    gate: str,
    status: str,
    *,
    evidence_paths: list[str] | None = None,
    metrics: dict[str, Any] | None = None,
    notes: str = "",
    blocked_reason: str = "",
) -> dict[str, Any]:
    return {
        "schema": "AIOS_QUALIFICATION_LEDGER_ENTRY.v1",
        "gate": gate,
        "attempt_id": f"{gate}:{_utc_now()}",
        "date_utc": _utc_now(),
        "status": status,
        "score": metrics.get("score") if metrics else None,
        "evidence_paths": list(evidence_paths or []),
        "metrics": metrics or {},
        "approved_by": None,
        "approval_time": None,
        "approval_status": "PENDING_HUMAN_OWNER",
        "qualification_status": "PROVISIONAL",
        "notes": notes,
        "blocked_reason": blocked_reason,
        "next_gate": "",
        "demotion_trigger": "",
        "write_performed": False,
    }


def validate_qualification_entry(entry: dict[str, Any]) -> dict[str, Any]:
    approval_forged = bool(entry.get("approved_by") or entry.get("approval_time"))
    forbidden_status = str(entry.get("qualification_status") or "") in FORBIDDEN_FINAL_STATUSES
    valid = not approval_forged and not forbidden_status
    return {
        "valid": valid,
        "approval_forged": approval_forged,
        "forbidden_status": forbidden_status,
        "reason": "Preview entry is promotion-safe." if valid else "Entry attempts approval or forbidden status.",
    }


def summarize_gate_status(entries: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = {entry["gate"]: entry["status"] for entry in entries}
    blockers = [entry.get("blocked_reason") for entry in entries if entry.get("blocked_reason")]
    return {
        "schema": "AIOS_QUALIFICATION_GATE_SUMMARY.v1",
        "gate_status": statuses,
        "blockers": blockers,
        "approved_by": None,
        "approval_status": "PENDING_HUMAN_OWNER",
        "write_performed": False,
    }


def build_promotion_package(entries: list[dict[str, Any]], *, requested_status: str = "TESTED_PENDING_REVIEW") -> dict[str, Any]:
    final_status = requested_status if requested_status in ALLOWED_FINAL_STATUSES else "BLOCKED"
    validations = [validate_qualification_entry(entry) for entry in entries]
    if any(not item["valid"] for item in validations):
        final_status = "BLOCKED"
    gate_summary = summarize_gate_status(entries)
    scores = [entry.get("score") for entry in entries if isinstance(entry.get("score"), (int, float))]
    score = round(sum(scores) / len(scores), 2) if scores else 0
    return {
        "schema": "AIOS_NIGHT_SUPERVISOR_PROMOTION_PACKAGE.v1",
        "final_qualification_status": final_status,
        "requested_status": requested_status,
        "score": score,
        "gate_summary": gate_summary,
        "evidence_paths": sorted({path for entry in entries for path in entry.get("evidence_paths", [])}),
        "blockers": gate_summary["blockers"],
        "next_safe_action": "Human Owner reviews promotion package; no authority expands automatically.",
        "human_owner_decision_required": True,
        "approved_by": None,
        "approval_status": "PENDING_HUMAN_OWNER",
        "forbidden_statuses": sorted(FORBIDDEN_FINAL_STATUSES),
        "write_performed": False,
    }
