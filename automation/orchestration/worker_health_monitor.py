"""Read-only worker health monitor for Night Supervisor Gate 1.

System 2 is the canonical heartbeat direction:
Reports/dispatcher/runtime/workers/worker_heartbeat_table.json and related
runtime worker tables. System 1 scripts remain legacy/reference-only.

This module reads evidence and returns normalized health summaries. It never
writes heartbeat files, launches workers, starts loops, moves packets, changes
approvals, changes locks, stages files, commits, pushes, or enables effectors.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CANONICAL_HEARTBEAT_PATH = Path("Reports/dispatcher/runtime/workers/worker_heartbeat_table.json")
CANONICAL_ACTIVE_WORKER_PATH = Path("Reports/dispatcher/runtime/workers/active_worker_table.json")
DEFAULT_STALE_SECONDS = 30 * 60
WORKER_STATES = {"ACTIVE", "IDLE", "STARTING", "STOPPING", "STALE", "MISSING", "CRASHED", "UNKNOWN"}
ACTIVE_LIKE_STATES = {
    "ASSIGNED",
    "DRY_RUN_STARTED",
    "APPLY_RUNNING",
    "VALIDATING",
    "VALIDATED",
    "WAITING_APPROVAL",
    "BLOCKED",
    "REVIEW_REQUIRED",
}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso_now() -> str:
    return _utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _repo_path(repo_root: str | Path, relative_path: str | Path) -> Path:
    return Path(repo_root).resolve() / Path(relative_path)


def _relative(repo_root: str | Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path(repo_root).resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _parse_time(value: Any) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _string_field(record: dict[str, Any], *names: str) -> str:
    for name in names:
        value = record.get(name)
        if value is not None and str(value).strip():
            return str(value)
    return ""


def _int_field(record: dict[str, Any], *names: str, default: int = 0) -> int:
    for name in names:
        value = record.get(name)
        if value is None or str(value).strip() == "":
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return default


def _iter_heartbeat_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and isinstance(payload.get("heartbeats"), list):
        return [item for item in payload["heartbeats"] if isinstance(item, dict)]
    if isinstance(payload, dict) and isinstance(payload.get("workers"), list):
        return [item for item in payload["workers"] if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        return [payload]
    return []


def classify_worker_health(record: dict[str, Any], now_utc: datetime | None = None) -> dict[str, Any]:
    """Classify one normalized or raw heartbeat record without side effects."""
    now = (now_utc or _utc_now()).astimezone(timezone.utc)
    raw_state = _string_field(record, "status", "current_state", "state").upper()
    stale_status = _string_field(record, "stale_status").upper()
    last_seen_text = _string_field(record, "last_seen", "heartbeat_time", "last_heartbeat")
    last_seen = _parse_time(last_seen_text)
    stale_after = _int_field(record, "stale_after_seconds", "stale_timeout_seconds", default=DEFAULT_STALE_SECONDS)

    if not _string_field(record, "worker_id"):
        return {"status": "UNKNOWN", "observed_age_seconds": 0, "classification_reason": "Missing worker_id."}
    if stale_status == "STALE" or raw_state == "STALE":
        age = int((now - last_seen).total_seconds()) if last_seen else 0
        return {"status": "STALE", "observed_age_seconds": max(age, 0), "classification_reason": "Heartbeat evidence is marked stale."}
    if raw_state in {"MISSING", "CRASHED", "UNKNOWN"}:
        return {"status": raw_state, "observed_age_seconds": 0, "classification_reason": f"Worker state is {raw_state}."}
    if raw_state in {"STARTING", "STOPPING", "IDLE", "ACTIVE"}:
        mapped = raw_state
    elif raw_state in ACTIVE_LIKE_STATES:
        mapped = "ACTIVE"
    elif raw_state in {"STOPPED"}:
        mapped = "IDLE"
    elif not raw_state:
        mapped = "UNKNOWN"
    else:
        mapped = "UNKNOWN"

    if last_seen is None:
        return {"status": "UNKNOWN", "observed_age_seconds": 0, "classification_reason": "Heartbeat timestamp is missing or invalid."}

    age_seconds = max(int((now - last_seen).total_seconds()), 0)
    if age_seconds > stale_after and mapped not in {"STOPPING"}:
        return {
            "status": "STALE",
            "observed_age_seconds": age_seconds,
            "classification_reason": f"Heartbeat age {age_seconds}s exceeds stale_after_seconds {stale_after}.",
        }
    return {
        "status": mapped,
        "observed_age_seconds": age_seconds,
        "classification_reason": "Heartbeat evidence is current.",
    }


def normalize_worker_heartbeat(
    record: dict[str, Any],
    *,
    evidence_path: str = "",
    heartbeat_source: str = "system2",
    now_utc: datetime | None = None,
) -> dict[str, Any]:
    """Normalize a raw System 2 heartbeat record to the Gate 1 evidence shape."""
    classification = classify_worker_health(record, now_utc=now_utc)
    last_seen = _string_field(record, "last_seen", "heartbeat_time", "last_heartbeat")
    worker_id = _string_field(record, "worker_id")
    return {
        "heartbeat_id": _string_field(record, "heartbeat_id", "event_id") or f"heartbeat:{worker_id or 'UNKNOWN'}",
        "worker_id": worker_id,
        "worker_type": _string_field(record, "worker_type", "assigned_role", "role"),
        "last_seen": last_seen,
        "status": classification["status"],
        "packet_id": _string_field(record, "packet_id", "assigned_packet_id"),
        "branch": _string_field(record, "branch"),
        "runtime_seconds": _int_field(record, "runtime_seconds", default=0),
        "host": _string_field(record, "host", "terminal_window_name"),
        "heartbeat_source": _string_field(record, "heartbeat_source") or heartbeat_source,
        "evidence_path": evidence_path,
        "blocked_reason": _string_field(record, "blocked_reason"),
        "progress_marker": _string_field(record, "progress_marker", "next_safe_action"),
        "lock_corroboration": _string_field(record, "lock_corroboration", "lock_status"),
        "approval_context": _string_field(record, "approval_context", "approval_state", "approval_status"),
        "stale_after_seconds": _int_field(record, "stale_after_seconds", "stale_timeout_seconds", default=DEFAULT_STALE_SECONDS),
        "observed_age_seconds": classification["observed_age_seconds"],
        "classification_reason": classification["classification_reason"],
    }


def scan_worker_health(
    repo_root: str | Path = ".",
    *,
    heartbeat_paths: list[str | Path] | None = None,
    now_utc: datetime | None = None,
) -> list[dict[str, Any]]:
    """Read canonical heartbeat evidence and return normalized worker health rows."""
    root = Path(repo_root).resolve()
    paths = heartbeat_paths or [CANONICAL_HEARTBEAT_PATH]
    rows: list[dict[str, Any]] = []
    for relative_path in paths:
        path = _repo_path(root, relative_path)
        evidence_path = _relative(root, path)
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc:  # noqa: BLE001 - malformed evidence becomes UNKNOWN
            rows.append(
                {
                    "heartbeat_id": f"malformed:{Path(relative_path).name}",
                    "worker_id": "UNKNOWN",
                    "worker_type": "",
                    "last_seen": "",
                    "status": "UNKNOWN",
                    "packet_id": "",
                    "branch": "",
                    "runtime_seconds": 0,
                    "host": "",
                    "heartbeat_source": "system2",
                    "evidence_path": evidence_path,
                    "blocked_reason": f"Malformed heartbeat evidence: {exc}",
                    "progress_marker": "",
                    "lock_corroboration": "",
                    "approval_context": "",
                    "stale_after_seconds": DEFAULT_STALE_SECONDS,
                    "observed_age_seconds": 0,
                    "classification_reason": "Heartbeat table could not be parsed.",
                }
            )
            continue
        for record in _iter_heartbeat_records(payload):
            rows.append(
                normalize_worker_heartbeat(
                    record,
                    evidence_path=evidence_path,
                    heartbeat_source="system2",
                    now_utc=now_utc,
                )
            )
    return rows


def build_worker_health_summary(worker_health: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Build a non-blocking Gate 1 health summary."""
    rows = list(worker_health or [])
    counts = {state: 0 for state in sorted(WORKER_STATES)}
    for row in rows:
        status = str(row.get("status") or "UNKNOWN").upper()
        if status not in counts:
            status = "UNKNOWN"
        counts[status] += 1

    evidence_count = len(rows)
    review_count = counts["STALE"] + counts["MISSING"] + counts["CRASHED"] + counts["UNKNOWN"]
    bootstrap_only = bool(rows) and all(
        str(row.get("heartbeat_source") or "").lower() == "system2_runtime_bootstrap"
        or "bootstrap" in str(row.get("blocked_reason") or "").lower()
        for row in rows
    )

    if evidence_count == 0:
        status = "NO_EVIDENCE"
        hint = "GATE_1_NEEDS_CANONICAL_HEARTBEAT_EVIDENCE"
    elif bootstrap_only:
        status = "BOOTSTRAP_ONLY"
        hint = "GATE_1_BOOTSTRAP_EVIDENCE_PRESENT_BUT_NEEDS_LIVE_HEARTBEAT"
    elif review_count > 0:
        status = "REVIEW_REQUIRED"
        hint = "GATE_1_REVIEW_WORKER_HEALTH_EVIDENCE"
    else:
        status = "READY_FOR_GATE_1_TEST"
        hint = "GATE_1_READY_FOR_CONTROLLED_TESTS"

    return {
        "schema": "AIOS_WORKER_HEALTH_SUMMARY.v1",
        "generated_at": _iso_now(),
        "canonical_heartbeat_authority": "system2",
        "legacy_heartbeat_authority": "system1_reference_only",
        "daemon_heartbeat_loops_allowed": False,
        "worker_health_status": status,
        "worker_health_evidence_count": evidence_count,
        "counts_by_status": counts,
        "worker_health": rows,
        "qualification_gate_hint": hint,
        "write_performed": False,
        "dispatch_blocking": False,
    }


def apply_worker_health_to_report(report: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    """Attach worker health evidence to a supervisor report without blocking dispatch."""
    updated = dict(report)
    updated["worker_health"] = list(summary.get("worker_health", []))
    updated["worker_health_status"] = str(summary.get("worker_health_status") or "UNKNOWN")
    updated["worker_health_evidence_count"] = int(summary.get("worker_health_evidence_count") or 0)
    updated["qualification_gate_hint"] = str(summary.get("qualification_gate_hint") or "GATE_1_UNKNOWN")
    updated["worker_health_summary"] = summary
    return updated
