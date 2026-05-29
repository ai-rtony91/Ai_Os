"""Controlled single-overnight simulation preview for Night Supervisor Gate 4."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


def _iso(base: datetime, minutes: int) -> str:
    return (base + timedelta(minutes=minutes)).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_overnight_simulation(cycles: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Return a fixed evidence-only overnight simulation report."""
    base = datetime(2026, 5, 29, 0, 0, tzinfo=timezone.utc)
    cycle_rows = cycles or [
        ("cycle_001", "BOOTSTRAP_ONLY", "NO_EVIDENCE", "PASS"),
        ("cycle_002", "READY_FOR_GATE_1_TEST", "READY_FOR_GATE_2_TEST", "PASS"),
        ("cycle_003", "REVIEW_REQUIRED", "READY_FOR_GATE_2_TEST", "WARN"),
        ("cycle_004", "REVIEW_REQUIRED", "REVIEW_REQUIRED", "WARN"),
        ("cycle_005", "REVIEW_REQUIRED", "REVIEW_REQUIRED", "WARN"),
        ("cycle_006", "REVIEW_REQUIRED", "REVIEW_REQUIRED", "WARN"),
    ]
    normalized = []
    for index, row in enumerate(cycle_rows):
        if isinstance(row, dict):
            item = dict(row)
        else:
            cycle_id, worker_status, packet_status, recovery_status = row
            item = {
                "cycle_id": cycle_id,
                "timestamp": _iso(base, index * 10),
                "worker_health_status": worker_status,
                "packet_integrity_status": packet_status,
                "recovery_status": recovery_status,
            }
        item.setdefault("actions_taken", "NONE")
        item.setdefault("unsafe_actions", 0)
        item.setdefault("effectors_enabled", False)
        item.setdefault("scheduler_enabled", False)
        item.setdefault("daemon_enabled", False)
        normalized.append(item)

    unsafe_total = sum(int(item.get("unsafe_actions") or 0) for item in normalized)
    missing_required = any(not item.get("cycle_id") or not item.get("timestamp") for item in normalized)
    if unsafe_total:
        result = "FAIL"
    elif missing_required:
        result = "FAIL"
    elif any(str(item.get("recovery_status") or "").upper() in {"FAIL", "FAILED_RECOVERY"} for item in normalized):
        result = "FAIL"
    elif any(
        str(item.get("worker_health_status") or "").upper() == "REVIEW_REQUIRED"
        or str(item.get("packet_integrity_status") or "").upper() == "REVIEW_REQUIRED"
        or str(item.get("recovery_status") or "").upper() == "WARN"
        for item in normalized
    ):
        result = "WARN"
    else:
        result = "PASS"

    return {
        "schema": "AIOS_NIGHT_SUPERVISOR_OVERNIGHT_SIMULATION.v1",
        "simulation_result": result,
        "cycle_count": len(normalized),
        "cycles": normalized,
        "actions_taken": "NONE",
        "unsafe_actions": unsafe_total,
        "effectors_enabled": False,
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "write_performed": False,
    }
