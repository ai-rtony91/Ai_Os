"""Read-only AI_OS packet lock manager for Night Supervisor V2.

This module inspects existing lock artifacts and returns lock evidence for the
shared packet routing contract. It does not claim, release, delete, clean up, or
override locks.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOCK_STATES = {"FREE", "CLAIMED", "CONFLICT", "EXPIRED", "UNKNOWN"}
LOCK_ROOTS = (
    Path("automation/orchestration/locks"),
    Path("automation/orchestration/work_packets/locks"),
    Path("telemetry/locks"),
)
ACTIVE_LOCK_STATUSES = {"ACTIVE", "CLAIMED", "LOCKED", "HELD", "OPEN"}
RELEASED_LOCK_STATUSES = {"RELEASED", "DONE", "CLOSED", "COMPLETE", "COMPLETED"}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _norm_path(value: Any) -> str:
    return str(value or "").replace("\\", "/").strip()


def _parse_time(value: Any) -> datetime | None:
    if not value:
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


def is_lock_expired(lock: dict[str, Any], now_utc: datetime) -> bool:
    """Return true if lock is stale or past expires_at."""
    now = now_utc.astimezone(timezone.utc)
    expires_at = _parse_time(lock.get("expires_at"))
    if expires_at and expires_at <= now:
        return True

    status = str(lock.get("status") or "").upper()
    if status in {"EXPIRED", "STALE"}:
        return True

    return False


def normalize_lock(raw_lock: dict[str, Any], path: Path) -> dict[str, Any]:
    """Normalize lock file fields into a consistent lock record."""
    locked_paths = _as_list(raw_lock.get("locked_paths") or raw_lock.get("claimed_paths") or raw_lock.get("paths"))
    first_path = _norm_path(raw_lock.get("packet_path") or raw_lock.get("file_path") or raw_lock.get("path"))
    if first_path:
        locked_paths.insert(0, first_path)

    owner = raw_lock.get("owner") or raw_lock.get("owner_worker") or raw_lock.get("worker_id") or raw_lock.get("worker_identity")
    timestamps = [
        raw_lock.get("updated_at"),
        raw_lock.get("claimed_at"),
        raw_lock.get("acquired_at"),
        raw_lock.get("created_at"),
    ]
    timestamp = next((str(value) for value in timestamps if value), "")

    return {
        "lock_id": str(raw_lock.get("lock_id") or path.stem),
        "packet_id": str(raw_lock.get("packet_id") or ""),
        "packet_path": _norm_path(raw_lock.get("packet_path") or raw_lock.get("file_path") or ""),
        "locked_paths": [_norm_path(item) for item in locked_paths if _norm_path(item)],
        "owner": str(owner or ""),
        "worker_id": str(raw_lock.get("worker_id") or raw_lock.get("owner_worker") or ""),
        "status": str(raw_lock.get("status") or raw_lock.get("state") or "UNKNOWN").upper(),
        "reason": str(raw_lock.get("reason") or raw_lock.get("lock_reason") or ""),
        "created_at": str(raw_lock.get("created_at") or raw_lock.get("claimed_at") or ""),
        "updated_at": str(raw_lock.get("updated_at") or raw_lock.get("claimed_at") or raw_lock.get("created_at") or ""),
        "expires_at": str(raw_lock.get("expires_at") or ""),
        "source_path": _norm_path(path),
        "timestamp": timestamp,
    }


def _iter_lock_payloads(payload: Any, path: Path) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and isinstance(payload.get("locks"), list):
        return [item for item in payload["locks"] if isinstance(item, dict)]
    if isinstance(payload, dict):
        return [payload]
    return [
        {
            "lock_id": path.stem,
            "status": "UNKNOWN",
            "reason": "Lock JSON root was not an object.",
        }
    ]


def scan_locks(repo_root: Path) -> list[dict[str, Any]]:
    """Read all lock JSON files from canonical lock folders."""
    root = Path(repo_root).resolve()
    records: list[dict[str, Any]] = []
    for relative_root in LOCK_ROOTS:
        folder = root / relative_root
        if not folder.exists() or not folder.is_dir():
            continue
        for path in sorted(folder.rglob("*.json")):
            name = path.name.lower()
            if "lock" not in name and "registry" not in name and "ownership" not in name:
                continue
            try:
                payload = json.loads(path.read_text(encoding="utf-8-sig"))
            except Exception as exc:  # noqa: BLE001 - return evidence, do not crash supervisor
                records.append(
                    {
                        "lock_id": path.stem,
                        "packet_id": "",
                        "packet_path": "",
                        "locked_paths": [],
                        "owner": "",
                        "worker_id": "",
                        "status": "UNKNOWN",
                        "reason": f"Malformed or unreadable lock file: {exc}",
                        "source_path": _norm_path(path.relative_to(root)),
                    }
                )
                continue

            for item in _iter_lock_payloads(payload, path):
                records.append(normalize_lock(item, path.relative_to(root)))
    return records


def _path_matches(packet_path: str, locked_path: str) -> bool:
    packet = _norm_path(packet_path).strip("/")
    locked = _norm_path(locked_path).strip("/")
    return bool(packet and locked and (packet == locked or packet.startswith(f"{locked}/") or locked.startswith(f"{packet}/")))


def check_packet_lock(packet_id: str, packet_path: str, locks: list[dict[str, Any]]) -> dict[str, Any]:
    """Return lock_status, lock_owner, lock_id, blocked_reason."""
    now = datetime.now(timezone.utc)
    matches = []
    for lock in locks:
        lock_packet = str(lock.get("packet_id") or "")
        lock_paths = [str(item) for item in _as_list(lock.get("locked_paths"))]
        if lock_packet and packet_id and lock_packet == packet_id:
            matches.append(lock)
            continue
        if any(_path_matches(packet_path, locked_path) for locked_path in lock_paths):
            matches.append(lock)

    if not matches:
        return {
            "lock_status": "FREE",
            "lock_owner": "",
            "lock_id": "",
            "blocked_reason": "",
            "lock_evidence": [],
        }

    active = []
    expired = []
    released = []
    unknown = []
    for lock in matches:
        status = str(lock.get("status") or "UNKNOWN").upper()
        if is_lock_expired(lock, now):
            expired.append(lock)
        elif status in RELEASED_LOCK_STATUSES:
            released.append(lock)
        elif status in ACTIVE_LOCK_STATUSES:
            active.append(lock)
        else:
            unknown.append(lock)

    if len(active) > 1:
        status = "CONFLICT"
        blocker = "Multiple active locks match this packet."
        chosen = active[0]
    elif active:
        status = "CLAIMED"
        blocker = "Active lock claims this packet or path."
        chosen = active[0]
    elif expired:
        status = "EXPIRED"
        blocker = "Expired or stale lock matches this packet or path."
        chosen = expired[0]
    elif unknown:
        status = "UNKNOWN"
        blocker = "Unknown lock state matches this packet or path."
        chosen = unknown[0]
    else:
        status = "FREE"
        blocker = ""
        chosen = released[0]

    return {
        "lock_status": status,
        "lock_owner": str(chosen.get("owner") or chosen.get("worker_id") or ""),
        "lock_id": str(chosen.get("lock_id") or ""),
        "blocked_reason": blocker,
        "lock_evidence": matches,
    }


def apply_lock_status(contract: dict[str, Any], lock_result: dict[str, Any]) -> dict[str, Any]:
    """Return updated AIOS_PACKET_ROUTING_CONTRACT_V1 object."""
    updated = dict(contract)
    lock_status = str(lock_result.get("lock_status") or "UNKNOWN")
    if lock_status not in LOCK_STATES:
        lock_status = "UNKNOWN"
    updated["lock_status"] = lock_status
    updated["lock_owner"] = str(lock_result.get("lock_owner") or "")
    updated["lock_id"] = str(lock_result.get("lock_id") or "")
    blocker = str(lock_result.get("blocked_reason") or "")
    if blocker:
        current = str(updated.get("blocked_reason") or "")
        updated["blocked_reason"] = "; ".join(item for item in [current, blocker] if item)
    return updated

