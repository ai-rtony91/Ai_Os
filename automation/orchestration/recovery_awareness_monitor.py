"""Read-only recovery awareness monitor for Night Supervisor Gate 3."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lock_manager import scan_locks
from worker_health_monitor import build_worker_health_summary, scan_worker_health


RECOVERY_STATES = {"RECOVERABLE", "PARTIAL_RECOVERY", "FAILED_RECOVERY", "UNKNOWN_RECOVERY"}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _worker_map(worker_health_summary: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    rows = _as_list((worker_health_summary or {}).get("worker_health"))
    return {str(row.get("worker_id") or ""): row for row in rows if isinstance(row, dict) and row.get("worker_id")}


def classify_recovery_awareness(case: dict[str, Any], worker_health_summary: dict[str, Any] | None = None) -> dict[str, Any]:
    """Classify one recovery case without executing recovery."""
    worker_id = str(case.get("worker_id") or "")
    packet_id = str(case.get("packet_id") or "")
    lock_status = str(case.get("lock_status") or "").upper()
    approval_status = str(case.get("approval_status") or "").upper()
    runtime_table_status = str(case.get("runtime_table_status") or "UNKNOWN").upper()
    progress_status = str(case.get("progress_status") or "").upper()
    clean_stop = bool(case.get("clean_stop")) or str(case.get("status") or "").upper() in {"STOPPING", "STOPPED"}
    worker_status = str(case.get("worker_status") or "").upper()
    worker_row = _worker_map(worker_health_summary).get(worker_id)
    if worker_row and not worker_status:
        worker_status = str(worker_row.get("status") or "UNKNOWN").upper()

    if runtime_table_status in {"MISSING", "MALFORMED"}:
        state = "UNKNOWN_RECOVERY"
        reason = "Runtime evidence is missing or malformed."
        safe_next_action = "Review runtime evidence before recovery."
    elif clean_stop and lock_status in {"", "FREE"}:
        state = "RECOVERABLE"
        reason = "Worker stopped cleanly with no lock or packet ownership conflict."
        safe_next_action = "Continue read-only monitoring."
    elif approval_status in {"PENDING", "BLOCKED", "EXPIRED", "UNKNOWN"}:
        state = "PARTIAL_RECOVERY"
        reason = "Approval evidence remains fail-closed and requires review."
        safe_next_action = "Escalate approval state to Human Owner."
    elif lock_status in {"CLAIMED", "CONFLICT", "EXPIRED"} and worker_status in {"STALE", "MISSING", "CRASHED"}:
        state = "PARTIAL_RECOVERY"
        reason = "Lock recovery is needed for stale, missing, or crashed owner evidence."
        safe_next_action = "Do not clear lock automatically; review lock ownership."
    elif packet_id and worker_status in {"STALE", "MISSING", "CRASHED"}:
        state = "PARTIAL_RECOVERY"
        reason = "Packet remains assigned to worker health evidence that needs recovery review."
        safe_next_action = "Review packet ownership before reassignment."
    elif worker_status == "CRASHED" and progress_status == "UNCHANGED":
        state = "FAILED_RECOVERY"
        reason = "Crash evidence and unchanged progress indicate recovery did not complete."
        safe_next_action = "Stop qualification and review recovery path."
    elif worker_status in {"UNKNOWN", ""}:
        state = "UNKNOWN_RECOVERY"
        reason = "Recovery evidence is incomplete or unknown."
        safe_next_action = "Collect missing recovery evidence."
    else:
        state = "RECOVERABLE"
        reason = "No recovery blocker detected in controlled evidence."
        safe_next_action = "Continue read-only monitoring."

    return {
        "case_id": str(case.get("case_id") or "UNKNOWN"),
        "worker_id": worker_id,
        "packet_id": packet_id,
        "recovery_status": state,
        "worker_status": worker_status or "UNKNOWN",
        "lock_status": lock_status or "UNKNOWN",
        "approval_status": approval_status or "UNKNOWN",
        "runtime_table_status": runtime_table_status,
        "classification_reason": reason,
        "safe_next_action": safe_next_action,
        "evidence_paths": [str(item) for item in _as_list(case.get("evidence_paths")) if str(item)],
        "write_performed": False,
    }


def build_recovery_awareness_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {state: 0 for state in sorted(RECOVERY_STATES)}
    for record in records:
        state = str(record.get("recovery_status") or "UNKNOWN_RECOVERY")
        if state not in counts:
            state = "UNKNOWN_RECOVERY"
        counts[state] += 1
    if not records:
        status = "NO_EVIDENCE"
    elif counts["FAILED_RECOVERY"]:
        status = "FAIL"
    elif counts["PARTIAL_RECOVERY"] or counts["UNKNOWN_RECOVERY"]:
        status = "WARN"
    else:
        status = "PASS"
    return {
        "schema": "AIOS_RECOVERY_AWARENESS_SUMMARY.v1",
        "recovery_status": status,
        "recovery_evidence_count": len(records),
        "counts_by_status": counts,
        "recovery_awareness": records,
        "write_performed": False,
        "recovery_executor_enabled": False,
    }


def scan_recovery_awareness(
    repo_root: str | Path = ".",
    *,
    cases: list[dict[str, Any]] | None = None,
    worker_health_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    worker_summary = worker_health_summary or build_worker_health_summary(scan_worker_health(root))
    if cases is None:
        runtime_table = root / "Reports" / "dispatcher" / "runtime" / "workers" / "worker_heartbeat_table.json"
        runtime_status = "PRESENT"
        try:
            json.loads(runtime_table.read_text(encoding="utf-8-sig"))
        except FileNotFoundError:
            runtime_status = "MISSING"
        except Exception:  # noqa: BLE001 - malformed runtime state is evidence
            runtime_status = "MALFORMED"
        locks = scan_locks(root)
        cases = [
            {
                "case_id": "runtime_table_parse",
                "runtime_table_status": runtime_status,
                "lock_status": "FREE" if not locks else "CLAIMED",
                "evidence_paths": ["Reports/dispatcher/runtime/workers/worker_heartbeat_table.json"],
            }
        ]
    return build_recovery_awareness_summary([classify_recovery_awareness(case, worker_summary) for case in cases])
