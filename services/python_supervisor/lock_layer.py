"""AI_OS Night Supervisor lock layer (read-only evaluation).

Schema/contract reference: schemas/aios/orchestration/LOCK_REGISTRY_SCHEMA.json
Mode: DRY_RUN
blocked_capabilities: lock_write, lock_release, file_write, git_stage_commit_push
next_safe_action: Use lock availability as evidence. Lock claim/release writes
are performed only by the approved PowerShell effectors under the dispatcher,
never by this module.
commit_performed: NO / push_performed: NO

This module answers one question without writing anything: "is the packet lock
free, held-by-me, or held-by-another?" The dispatcher uses that to decide
whether a claim_lock effector is needed, allowed, or must be blocked.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _lock_dir(repo_root: Path) -> Path:
    return repo_root / "automation" / "orchestration" / "locks"


def _read_json(path: Path) -> dict[str, Any] | None:
    for encoding in ("utf-8", "utf-8-sig", "utf-16"):
        try:
            payload = json.loads(path.read_text(encoding=encoding))
            return payload if isinstance(payload, dict) else None
        except Exception:  # noqa: BLE001 - fail-closed on parse problems
            continue
    return None


def lock_state(packet_id: str, repo_root: str | Path = ".", worker_id: str = "") -> dict[str, Any]:
    """Return read-only lock state for a packet. Never writes."""

    lock_path = _lock_dir(Path(repo_root).resolve()) / f"{packet_id}.lock.json"
    if not lock_path.exists():
        return {"packet_id": packet_id, "state": "FREE", "held_by": None, "lock_path": str(lock_path)}

    data = _read_json(lock_path) or {}
    status = str(data.get("status") or "ACTIVE").upper()
    held_by = str(data.get("worker_id") or "")
    if status == "RELEASED":
        return {"packet_id": packet_id, "state": "FREE", "held_by": None, "lock_path": str(lock_path)}
    if worker_id and held_by == worker_id:
        return {"packet_id": packet_id, "state": "HELD_BY_ME", "held_by": held_by, "lock_path": str(lock_path)}
    return {"packet_id": packet_id, "state": "HELD_BY_OTHER", "held_by": held_by, "lock_path": str(lock_path)}


def can_act_under_lock(intent: dict[str, Any], repo_root: str | Path = ".") -> dict[str, Any]:
    """Decide whether an intent is lock-clear. Fail-closed on conflicts."""

    if not intent.get("requires_lock"):
        return {"intent_id": intent.get("intent_id"), "lock_clear": True, "reason": "Effector does not require a lock."}

    packet_id = str(intent.get("packet_id") or "")
    worker_id = str(intent.get("worker_id") or "")
    state = lock_state(packet_id, repo_root, worker_id)

    if state["state"] in {"FREE", "HELD_BY_ME"}:
        return {
            "intent_id": intent.get("intent_id"),
            "lock_clear": True,
            "lock_state": state["state"],
            "reason": "Lock is free or already held by this worker.",
        }
    return {
        "intent_id": intent.get("intent_id"),
        "lock_clear": False,
        "lock_state": state["state"],
        "held_by": state["held_by"],
        "reason": "Lock is held by another worker. Fail-closed: BLOCKED.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Night Supervisor lock state (read-only).")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--packet-id", required=True, help="Packet id to check.")
    parser.add_argument("--worker-id", default="", help="Worker id checking the lock.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    args = parser.parse_args()
    print(json.dumps(lock_state(args.packet_id, args.repo_root, args.worker_id), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
