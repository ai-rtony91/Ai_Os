"""Morning handoff preview builder for Night Supervisor Gate 6."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_morning_handoff_preview(
    *,
    worker_health_summary: dict[str, Any] | None = None,
    packet_integrity_summary: dict[str, Any] | None = None,
    recovery_summary: dict[str, Any] | None = None,
    overnight_summary: dict[str, Any] | None = None,
    qualification_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    worker = worker_health_summary or {}
    packet = packet_integrity_summary or {}
    recovery = recovery_summary or {}
    overnight = overnight_summary or {}
    qualification = qualification_summary or {}
    return {
        "schema": "AIOS_MORNING_HANDOFF_PREVIEW.v1",
        "generated_at": _utc_now(),
        "night_summary": {
            "simulation_result": overnight.get("simulation_result", "UNKNOWN"),
            "cycle_count": overnight.get("cycle_count", 0),
            "actions_taken": "NONE",
        },
        "worker_health": worker,
        "packet_integrity": packet,
        "ownership_issues": packet.get("counts_by_status", {}),
        "crash_recovery_awareness": recovery,
        "backup_status": {
            "status": "NOT_RUN",
            "reason": "Backup execution is out of scope for Gate 1-7 evidence closure.",
        },
        "approval_status": {
            "status": "FAIL_CLOSED",
            "human_owner_approval_forged": False,
        },
        "lock_status": {
            "status": "READ_ONLY_REVIEW",
            "auto_clear_enabled": False,
        },
        "effector_status": {
            "effectors_enabled": False,
            "allowlist_changed": False,
        },
        "unsafe_action_count": int(overnight.get("unsafe_actions") or 0),
        "qualification_gate_status": qualification,
        "recommended_next_safe_action": "Human Owner reviews controlled Gate 1-7 evidence before any promotion.",
        "human_owner_decisions_needed": [
            "Review whether controlled Gate 1 and Gate 2 evidence is sufficient for TESTED_PENDING_REVIEW.",
            "Decide whether to authorize live heartbeat evidence collection without daemon or scheduler authority.",
        ],
        "night_supervisor_status": "PROVISIONAL",
        "actions_taken": "NONE",
        "effectors_enabled": False,
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "write_performed": False,
    }
