"""Read-only packet integrity monitor for Night Supervisor Gate 2.

Gate 2 reuses queue/routing evidence, worker health, lock evidence, and
approval evidence. It does not mutate packets, locks, approvals, worker runtime
tables, telemetry, Git state, or effector configuration.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from approval_officer import approval_required_for_packet, check_packet_approval, read_approval_inbox
from lock_manager import check_packet_lock, scan_locks
from queue_scanner import scan_queue
from worker_health_monitor import build_worker_health_summary, scan_worker_health


PACKET_STATES = {
    "HEALTHY",
    "STALE",
    "ABANDONED",
    "ORPHANED",
    "DUPLICATE_OWNER",
    "OWNERSHIP_DRIFT",
    "BLOCKED",
    "UNKNOWN",
}
BLOCKING_LOCK_STATES = {"CLAIMED", "CONFLICT", "EXPIRED", "UNKNOWN"}
BLOCKING_APPROVAL_STATES = {"PENDING", "BLOCKED", "EXPIRED", "UNKNOWN"}
WORKER_REVIEW_STATES = {"STALE", "MISSING", "CRASHED", "UNKNOWN"}
OPEN_PACKET_STATES = {"PENDING", "ASSIGNED", "STALE", "WAITING_APPROVAL", "VALIDATING", "BLOCKED", "UNKNOWN"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _string(value: Any) -> str:
    return str(value or "").strip()


def _worker_map(worker_health_summary: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    rows = []
    if worker_health_summary:
        rows = _as_list(worker_health_summary.get("worker_health"))
    return {str(row.get("worker_id") or ""): row for row in rows if isinstance(row, dict) and row.get("worker_id")}


def normalize_packet_record(raw: dict[str, Any], path: str | Path = "") -> dict[str, Any]:
    """Normalize packet or routing-contract data into Gate 2 evidence shape."""
    packet_path = _string(raw.get("packet_path") or raw.get("source_path") or path)
    packet_id = _string(raw.get("packet_id") or (Path(packet_path).stem if packet_path else ""))
    assigned_worker = _string(raw.get("assigned_worker") or raw.get("worker_id") or raw.get("worker_identity"))
    return {
        "packet_id": packet_id,
        "packet_path": packet_path,
        "packet_title": _string(raw.get("packet_title") or raw.get("title") or packet_id),
        "assigned_worker": assigned_worker,
        "recommended_worker": _string(raw.get("recommended_worker")),
        "packet_state": _string(raw.get("packet_state") or raw.get("status") or "UNKNOWN").upper(),
        "history": _as_list(raw.get("history") or raw.get("assignment_history") or raw.get("owner_history")),
        "lock_status": _string(raw.get("lock_status") or "UNKNOWN").upper(),
        "approval_required": bool(raw.get("approval_required")),
        "approval_status": _string(raw.get("approval_status") or "UNKNOWN").upper(),
        "blocked_reason": _string(raw.get("blocked_reason")),
        "evidence_paths": [item for item in [packet_path] if item],
        "raw": raw,
    }


def _duplicate_owner_map(records: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for packet in records:
        assigned = _string(packet.get("assigned_worker"))
        state = _string(packet.get("packet_state") or "UNKNOWN").upper()
        if assigned and state in OPEN_PACKET_STATES:
            counts[assigned] = counts.get(assigned, 0) + 1
    return counts


def classify_packet_integrity(
    packet: dict[str, Any],
    worker_health_summary: dict[str, Any] | None = None,
    locks: list[dict[str, Any]] | None = None,
    approvals: list[dict[str, Any]] | None = None,
    duplicate_owner_counts: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Classify one packet conservatively without side effects."""
    normalized = normalize_packet_record(packet, packet.get("packet_path") or packet.get("source_path") or "")
    worker_map = _worker_map(worker_health_summary)
    duplicate_counts = duplicate_owner_counts or {}

    packet_id = normalized["packet_id"]
    packet_path = normalized["packet_path"]
    assigned_worker = normalized["assigned_worker"]
    state = normalized["packet_state"]
    lock_status = normalized["lock_status"]
    approval_status = normalized["approval_status"]
    blocked_reason = normalized["blocked_reason"]
    evidence_paths = list(normalized["evidence_paths"])

    if locks:
        lock_result = check_packet_lock(packet_id, packet_path, locks)
        lock_status = str(lock_result.get("lock_status") or lock_status).upper()
        if lock_result.get("blocked_reason"):
            blocked_reason = "; ".join(item for item in [blocked_reason, str(lock_result["blocked_reason"])] if item)
        evidence_paths.extend(str(item.get("source_path") or "") for item in _as_list(lock_result.get("lock_evidence")) if isinstance(item, dict))

    if approvals:
        approval_required = approval_required_for_packet({**normalized, "approval_status": approval_status})
        approval_result = check_packet_approval(packet_id, packet_path, approvals, approval_required)
        approval_status = str(approval_result.get("approval_status") or approval_status).upper()
        if approval_result.get("blocked_reason"):
            blocked_reason = "; ".join(item for item in [blocked_reason, str(approval_result["blocked_reason"])] if item)
        evidence_paths.extend(str(item.get("source_path") or "") for item in _as_list(approval_result.get("approval_evidence")) if isinstance(item, dict))

    worker_status = "UNKNOWN"
    ownership_status = "UNKNOWN"
    classification_reason = ""
    packet_integrity_status = "UNKNOWN"

    history_workers = [
        _string(item.get("assigned_worker") or item.get("worker_id") or item.get("owner"))
        for item in _as_list(normalized.get("history"))
        if isinstance(item, dict)
    ]
    drift_detected = bool(assigned_worker and history_workers and history_workers[-1] and history_workers[-1] != assigned_worker)

    if not packet_id or not packet_path:
        packet_integrity_status = "UNKNOWN"
        classification_reason = "Packet identity or path is missing."
    elif lock_status in BLOCKING_LOCK_STATES or approval_status in BLOCKING_APPROVAL_STATES:
        packet_integrity_status = "BLOCKED"
        classification_reason = "Lock or approval evidence blocks packet integrity clearance."
    elif drift_detected:
        packet_integrity_status = "OWNERSHIP_DRIFT"
        classification_reason = "Packet assignment history conflicts with current assigned worker."
    elif assigned_worker and duplicate_counts.get(assigned_worker, 0) > 1:
        packet_integrity_status = "DUPLICATE_OWNER"
        classification_reason = "Multiple open packets claim the same assigned worker."
    elif assigned_worker and worker_map:
        worker_row = worker_map.get(assigned_worker)
        if not worker_row:
            packet_integrity_status = "ORPHANED"
            classification_reason = "Packet assigned worker is not present in worker health evidence."
        else:
            worker_status = str(worker_row.get("status") or "UNKNOWN").upper()
            if worker_status == "STALE":
                packet_integrity_status = "STALE"
                classification_reason = "Assigned worker heartbeat is stale; packet needs review."
            elif worker_status in {"MISSING", "CRASHED"}:
                packet_integrity_status = "ABANDONED"
                classification_reason = "Assigned worker is missing or crashed by worker health evidence."
            elif worker_status == "UNKNOWN":
                packet_integrity_status = "UNKNOWN"
                classification_reason = "Assigned worker has only unknown worker health evidence."
            else:
                packet_integrity_status = "HEALTHY"
                classification_reason = "Packet has assigned worker evidence with no current lock or approval block."
        ownership_status = "ASSIGNED"
    elif assigned_worker:
        packet_integrity_status = "UNKNOWN"
        ownership_status = "ASSIGNED"
        classification_reason = "Packet has an assigned worker but no worker health summary was available."
    elif state == "STALE":
        packet_integrity_status = "STALE"
        classification_reason = "Packet state is stale."
    elif state in {"PENDING", "UNKNOWN"}:
        packet_integrity_status = "UNKNOWN"
        classification_reason = "Packet has no assigned worker evidence yet."
    else:
        packet_integrity_status = "HEALTHY"
        classification_reason = "Packet has no blocking integrity evidence."

    return {
        "packet_id": packet_id,
        "packet_path": packet_path,
        "packet_title": normalized["packet_title"],
        "assigned_worker": assigned_worker,
        "recommended_worker": normalized["recommended_worker"],
        "packet_state": state,
        "packet_health_status": packet_integrity_status,
        "packet_integrity_status": packet_integrity_status,
        "worker_health_status": worker_status,
        "lock_status": lock_status,
        "approval_status": approval_status,
        "ownership_status": ownership_status,
        "evidence_paths": sorted({item for item in evidence_paths if item}),
        "classification_reason": classification_reason,
        "blocked_reason": blocked_reason,
        "timestamp": _utc_now(),
    }


def build_packet_integrity_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Build Gate 2 summary without claiming qualification."""
    counts = {state: 0 for state in sorted(PACKET_STATES)}
    for record in records:
        state = str(record.get("packet_integrity_status") or "UNKNOWN").upper()
        if state not in counts:
            state = "UNKNOWN"
        counts[state] += 1

    evidence_count = len(records)
    if evidence_count == 0:
        status = "NO_EVIDENCE"
        hint = "GATE_2_NEEDS_PACKET_INTEGRITY_EVIDENCE"
    elif any(counts[state] for state in ("BLOCKED", "UNKNOWN", "ORPHANED", "DUPLICATE_OWNER", "OWNERSHIP_DRIFT", "ABANDONED")):
        status = "REVIEW_REQUIRED"
        hint = "GATE_2_REVIEW_PACKET_INTEGRITY_EVIDENCE"
    else:
        status = "READY_FOR_GATE_2_TEST"
        hint = "GATE_2_READY_FOR_CONTROLLED_TESTS"

    return {
        "schema": "AIOS_PACKET_INTEGRITY_SUMMARY.v1",
        "generated_at": _utc_now(),
        "packet_integrity_status": status,
        "packet_integrity_evidence_count": evidence_count,
        "counts_by_status": counts,
        "packet_integrity": records,
        "qualification_gate_2_hint": hint,
        "write_performed": False,
        "dispatch_blocking": False,
    }


def scan_packet_integrity(
    repo_root: str | Path = ".",
    *,
    worker_health_summary: dict[str, Any] | None = None,
    routing_contracts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Read packet integrity evidence and return a summary."""
    root = Path(repo_root).resolve()
    packets = [normalize_packet_record(item) for item in (routing_contracts if routing_contracts is not None else scan_queue(root))]
    worker_summary = worker_health_summary or build_worker_health_summary(scan_worker_health(root))
    locks = scan_locks(root)
    approvals = read_approval_inbox(root)
    duplicate_counts = _duplicate_owner_map(packets)
    records = [
        classify_packet_integrity(
            packet,
            worker_summary,
            locks,
            approvals,
            duplicate_owner_counts=duplicate_counts,
        )
        for packet in packets
    ]
    return build_packet_integrity_summary(records)


def apply_packet_integrity_to_report(report: dict[str, Any], packet_summary: dict[str, Any]) -> dict[str, Any]:
    """Attach packet integrity evidence to a supervisor report."""
    updated = dict(report)
    updated["packet_integrity"] = list(packet_summary.get("packet_integrity", []))
    updated["packet_integrity_status"] = str(packet_summary.get("packet_integrity_status") or "UNKNOWN")
    updated["packet_integrity_evidence_count"] = int(packet_summary.get("packet_integrity_evidence_count") or 0)
    updated["packet_integrity_summary"] = packet_summary
    updated["qualification_gate_2_hint"] = str(packet_summary.get("qualification_gate_2_hint") or "GATE_2_UNKNOWN")
    return updated
