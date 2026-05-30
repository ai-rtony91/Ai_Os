"""AI_OS Night Supervisor read-only queue scanner.

Schema/contract reference: schemas/aios/orchestration/supervisor_queue.schema.json
Mode: DRY_RUN
blocked_capabilities: packet_movement, packet_state_write, approval_mutation,
worker_launch, telemetry_append, git_stage_commit_push
next_safe_action: Review ranked packet intake before approving any routing or mutation.
commit_performed: NO / push_performed: NO
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from freshness_scoring import score_evidence_freshness
from packet_risk_classifier import classify_packet_risk


QUEUE_SCHEMA = "AIOS_SUPERVISOR_QUEUE.v1"
DEFAULT_STALE_AFTER_SECONDS = 24 * 60 * 60
QUEUE_STATUS_PRIORITY = {
    "BLOCKED":          100,
    "FAILED":           100,
    "STALE":             80,
    "WAITING_APPROVAL":  60,
    "VALIDATING":        45,
    "PENDING":           40,
    "ASSIGNED":          20,
    "COMPLETE":           5,
    "UNKNOWN":           10,
}
# Backward-compatible alias — internal callers use QUEUE_STATUS_PRIORITY.
QUEUE_PRIORITY = QUEUE_STATUS_PRIORITY


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _read_json(path: Path) -> dict[str, Any]:
    last_error = ""
    for encoding in ("utf-8", "utf-8-sig", "utf-16"):
        try:
            return json.loads(path.read_text(encoding=encoding))
        except Exception as exc:  # noqa: BLE001 - try common local JSON encodings
            last_error = str(exc)
    try:
        return json.loads(path.read_bytes().decode())
    except Exception:  # noqa: BLE001 - fail-closed packet evidence wrapper
        return {
            "packet_id": path.stem,
            "status": "UNKNOWN",
            "parse_error": last_error,
            "source_path": str(path),
        }


def _packet_text(packet: dict[str, Any]) -> str:
    parts = [
        packet.get("packet_id"),
        packet.get("lane"),
        packet.get("owner_lane"),
        packet.get("worker_lane"),
        packet.get("status"),
        packet.get("mode"),
        packet.get("title"),
        packet.get("task_label"),
        packet.get("next_action"),
    ]
    parts.extend(str(path) for path in _as_list(packet.get("related_files")))
    return " ".join(str(part) for part in parts if part is not None)


def _queue_status(packet: dict[str, Any], risk: dict[str, Any], freshness: dict[str, Any]) -> tuple[str, str]:
    raw_status = str(packet.get("status") or packet.get("state") or "").lower()
    primary_class = str(risk.get("primary_class") or "").lower()
    freshness_class = str(freshness.get("freshness") or freshness.get("freshness_class") or freshness.get("class") or "").lower()

    if primary_class == "blocked" or "block" in raw_status:
        return "BLOCKED", "Packet or risk classifier indicates blocked state."
    if "fail" in raw_status or "error" in raw_status:
        return "FAILED", "Packet status indicates failed state."
    if freshness_class == "stale":
        return "STALE", "Packet evidence is stale."
    if "approval" in raw_status or "awaiting" in raw_status:
        return "WAITING_APPROVAL", "Packet is waiting for human approval."
    if "validat" in raw_status:
        return "VALIDATING", "Packet is in validator flow."
    if "complete" in raw_status or raw_status in {"done", "closed"}:
        return "COMPLETE", "Packet is complete."
    if packet.get("assigned_worker") or packet.get("worker_identity"):
        return "ASSIGNED", "Packet has an assigned worker."
    if raw_status in {"pending", "ready", "active", "open", ""}:
        return "PENDING", "Packet is available for read-only review."
    return "PENDING", "Packet status was not canonical; treated as pending review evidence."


def _next_safe_action(status: str) -> str:
    if status in {"BLOCKED", "FAILED"}:
        return "Escalate to Human Owner before any mutation."
    if status == "STALE":
        return "Refresh evidence in a future approved DRY_RUN collection pass."
    if status == "WAITING_APPROVAL":
        return "Surface approval requirement to the operator."
    if status == "VALIDATING":
        return "Review validator evidence before further action."
    return "Keep packet in read-only Night Supervisor review."


def _packet_file_root(repo_root: Path) -> Path:
    active = repo_root / "automation" / "orchestration" / "work_packets" / "active"
    if active.exists():
        return active
    return repo_root / "automation" / "orchestration" / "work_packets"


def scan_queue(repo_root: str | Path = ".") -> list[dict[str, Any]]:
    """Read active packet JSON files and return ranked queue intake evidence."""

    root = Path(repo_root).resolve()
    packet_root = _packet_file_root(root)
    if not packet_root.exists():
        return []

    items: list[dict[str, Any]] = []
    for packet_path in sorted(packet_root.glob("*.json")):
        packet = _read_json(packet_path)
        packet_id = str(packet.get("packet_id") or packet_path.stem)
        lane = str(packet.get("lane") or packet.get("owner_lane") or packet.get("worker_lane") or "UNKNOWN")
        worker_id = str(packet.get("worker_identity") or packet.get("assigned_worker") or "UNASSIGNED")
        related_files = [str(path) for path in _as_list(packet.get("related_files")) if str(path).strip()]
        risk = classify_packet_risk(text=_packet_text(packet), paths=related_files, mode=packet.get("mode"))
        freshness = score_evidence_freshness(packet, expected=True)
        status, status_reason = _queue_status(packet, risk, freshness)
        approval_required = bool(risk.get("requires_human_approval")) or status == "WAITING_APPROVAL"

        queue_item = {
            "schema": QUEUE_SCHEMA,
            "queue_id": f"queue:{packet_id}",
            "packet_id": packet_id,
            "worker_id": worker_id,
            "lane": lane,
            "status": status,
            "priority": QUEUE_STATUS_PRIORITY.get(status, QUEUE_STATUS_PRIORITY["UNKNOWN"]),
            "dependency_ids": [str(value) for value in _as_list(packet.get("dependency_ids"))],
            "lock_id": packet.get("lock_id"),
            "validator_required": status in {"PENDING", "VALIDATING", "ASSIGNED"},
            "approval_required": approval_required,
            "created_at": str(packet.get("created_at") or packet.get("created_utc") or packet.get("operator_start_time") or ""),
            "assigned_at": packet.get("assigned_at"),
            "completed_at": packet.get("completed_at"),
            "stale_after_seconds": int(packet.get("stale_after_seconds") or DEFAULT_STALE_AFTER_SECONDS),
            "escalation_target": str(packet.get("escalation_target") or "Human Owner"),
            "telemetry_event_id": packet.get("telemetry_event_id"),
            "risk": risk,
            "risk_class": risk.get("primary_class", "unknown"),
            "freshness": freshness,
            "source_path": str(packet_path.relative_to(root)).replace("\\", "/"),
            "related_files": related_files,
            "status_reason": status_reason,
            "next_safe_action": _next_safe_action(status),
        }
        items.append(queue_item)

    return sorted(items, key=lambda item: (-int(item["priority"]), str(item["packet_id"])))


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan AI_OS work packet queue in DRY_RUN mode.")
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    args = parser.parse_args()
    print(json.dumps(scan_queue(args.repo_root), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
