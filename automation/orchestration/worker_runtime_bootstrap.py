"""System 2 worker runtime table bootstrap for Night Supervisor Gate 1.

Default mode is DRY_RUN. APPLY creates only the four canonical worker runtime
tables under Reports/dispatcher/runtime/workers when they are missing. It never
launches workers, starts loops, schedules tasks, writes the qualification
ledger, runs backups, stages Git files, commits, pushes, or enables effectors.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any


RUNTIME_ROOT = Path("Reports/dispatcher/runtime/workers")
ACTIVE_WORKER_TABLE = RUNTIME_ROOT / "active_worker_table.json"
WORKER_HEARTBEAT_TABLE = RUNTIME_ROOT / "worker_heartbeat_table.json"
WORKER_REGISTRATION_STATUS = RUNTIME_ROOT / "worker_registration_status.json"
WORKER_SESSION_LEDGER = RUNTIME_ROOT / "worker_session_ledger.json"
WORKER_PROFILE_PATH = Path("automation/orchestration/workers/AIOS_WORKER_PROFILES.json")
WORKER_REGISTRY_PATH = Path("automation/orchestration/workers/AIOS_WORKER_REGISTRY.json")
RUNTIME_FILES = (
    ACTIVE_WORKER_TABLE,
    WORKER_HEARTBEAT_TABLE,
    WORKER_REGISTRATION_STATUS,
    WORKER_SESSION_LEDGER,
)
FORBIDDEN_ACTIVE_STATES = {"ACTIVE", "APPLY_RUNNING", "VALIDATING", "HEALTHY"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _relative(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:  # noqa: BLE001 - caller falls back conservatively
        return None
    return payload if isinstance(payload, dict) else None


def _safe_worker_id(value: Any) -> str:
    return str(value or "").strip()


def _normalize_worker(raw: dict[str, Any], source: str, repo_root: Path) -> dict[str, str]:
    worker_id = _safe_worker_id(raw.get("worker_id"))
    display_name = str(raw.get("display_title") or raw.get("display_name") or raw.get("window_marker") or worker_id)
    worker_type = str(raw.get("worker_type") or raw.get("type") or "")
    role = str(raw.get("role") or raw.get("purpose") or worker_type)
    lane = str(raw.get("lane") or raw.get("guard_policy") or "")
    branch = str(raw.get("default_branch") or raw.get("branch") or "")
    host = str(raw.get("host") or "")
    return {
        "worker_id": worker_id,
        "display_name": display_name,
        "worker_type": worker_type,
        "role": role,
        "lane": lane,
        "branch": branch,
        "host": host,
        "source": source,
        "repo_root": str(repo_root),
    }


def _fallback_workers(repo_root: Path) -> list[dict[str, str]]:
    return [
        {
            "worker_id": f"AIOS-{index:02d}",
            "display_name": f"AIOS-{index:02d}",
            "worker_type": "unknown",
            "role": "fallback_worker_identity",
            "lane": "",
            "branch": "",
            "host": "",
            "source": "fallback_aios_01_10",
            "repo_root": str(repo_root),
        }
        for index in range(1, 11)
    ]


def load_worker_source(repo_root: str | Path = ".") -> dict[str, Any]:
    """Return canonical worker rows from profiles, registry, or fallback."""
    root = Path(repo_root).resolve()
    for relative_path, key in (
        (WORKER_PROFILE_PATH, "profiles"),
        (WORKER_REGISTRY_PATH, "registry"),
    ):
        payload = _read_json(root / relative_path)
        workers = payload.get("workers") if payload else None
        if not isinstance(workers, list):
            continue
        normalized = [
            _normalize_worker(item, str(relative_path).replace("\\", "/"), root)
            for item in workers
            if isinstance(item, dict) and _safe_worker_id(item.get("worker_id"))
        ]
        if normalized:
            return {
                "worker_source": str(relative_path).replace("\\", "/"),
                "worker_source_kind": key,
                "fallback_used": False,
                "workers": normalized,
                "blocked_reason": "",
            }

    return {
        "worker_source": "fallback_aios_01_10",
        "worker_source_kind": "fallback",
        "fallback_used": True,
        "workers": _fallback_workers(root),
        "blocked_reason": "Canonical worker profile/registry was unavailable or incompatible.",
    }


def _event_id(worker_id: str, timestamp: str) -> str:
    seed = f"{worker_id}|{timestamp}|system2_runtime_bootstrap"
    return f"runtime_bootstrap_{sha256(seed.encode('utf-8')).hexdigest()[:16]}"


def build_runtime_tables(repo_root: str | Path = ".", timestamp: str | None = None) -> dict[str, Any]:
    """Build all four runtime table payloads without writing them."""
    root = Path(repo_root).resolve()
    now = timestamp or _utc_now()
    source = load_worker_source(root)
    workers: list[dict[str, str]] = source["workers"]
    runtime_root = str(RUNTIME_ROOT).replace("\\", "/")

    active_workers = []
    heartbeats = []
    registrations = []
    events = []
    for worker in workers:
        worker_id = worker["worker_id"]
        evidence_path = str(WORKER_HEARTBEAT_TABLE).replace("\\", "/")
        active_workers.append(
            {
                "worker_id": worker_id,
                "display_name": worker["display_name"],
                "worker_type": worker["worker_type"],
                "role": worker["role"],
                "lane": worker["lane"],
                "branch": worker["branch"],
                "host": worker["host"],
                "current_state": "REVIEW_REQUIRED",
                "status": "REVIEW_REQUIRED",
                "packet_id": "",
                "last_seen": "",
                "heartbeat_time": "",
                "last_heartbeat": "",
                "heartbeat_source": "system2_runtime_bootstrap",
                "progress_marker": "",
                "lock_corroboration": "",
                "approval_context": "NOT_REQUESTED",
                "evidence_path": str(ACTIVE_WORKER_TABLE).replace("\\", "/"),
                "blocked_reason": "Worker known from registry/profile; no live runtime heartbeat observed yet.",
                "created_at": now,
                "updated_at": now,
            }
        )
        heartbeats.append(
            {
                "heartbeat_id": f"bootstrap:{worker_id}",
                "worker_id": worker_id,
                "worker_type": worker["worker_type"],
                "current_state": "UNKNOWN",
                "status": "UNKNOWN",
                "last_seen": "",
                "heartbeat_time": "",
                "last_heartbeat": "",
                "packet_id": "",
                "branch": worker["branch"],
                "runtime_seconds": 0,
                "host": worker["host"],
                "heartbeat_source": "system2_runtime_bootstrap",
                "evidence_path": evidence_path,
                "blocked_reason": "Bootstrap row only. No live heartbeat observed.",
                "progress_marker": "",
                "lock_corroboration": "",
                "approval_context": "NOT_REQUESTED",
                "stale_after_seconds": 1800,
                "stale_status": "UNKNOWN",
                "heartbeat_age_seconds": None,
            }
        )
        registrations.append(
            {
                "worker_id": worker_id,
                "registered": True,
                "expected": True,
                "runtime_seen": False,
                "registration_status": "REGISTERED_NOT_STARTED",
                "review_required": True,
                "blocked_reason": "Worker known but no live heartbeat evidence exists yet.",
                "registration_source": source["worker_source"],
                "updated_at": now,
            }
        )
        events.append(
            {
                "event_id": _event_id(worker_id, now),
                "event_type": "RUNTIME_TABLE_BOOTSTRAPPED",
                "worker_id": worker_id,
                "timestamp": now,
                "status": "UNKNOWN",
                "notes": "Bootstrap created runtime table row; no live worker started.",
            }
        )

    return {
        str(ACTIVE_WORKER_TABLE): {
            "schema": "AIOS_ACTIVE_WORKER_TABLE.v1",
            "generated_by": "worker_runtime_bootstrap",
            "repo_root": str(root),
            "runtime_root": runtime_root,
            "created_at": now,
            "updated_at": now,
            "workers": active_workers,
        },
        str(WORKER_HEARTBEAT_TABLE): {
            "schema": "AIOS_WORKER_HEARTBEAT_TABLE.v1",
            "generated_by": "worker_runtime_bootstrap",
            "created_at": now,
            "updated_at": now,
            "heartbeats": heartbeats,
        },
        str(WORKER_REGISTRATION_STATUS): {
            "schema": "AIOS_WORKER_REGISTRATION_STATUS.v1",
            "created_at": now,
            "updated_at": now,
            "registration_source": source["worker_source"],
            "registrations": registrations,
        },
        str(WORKER_SESSION_LEDGER): {
            "schema": "AIOS_WORKER_SESSION_LEDGER.v1",
            "created_at": now,
            "events": events,
        },
        "_worker_source": source,
    }


def initialize_worker_runtime_tables(
    repo_root: str | Path = ".",
    *,
    apply: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    """Preview or create missing System 2 runtime worker tables."""
    root = Path(repo_root).resolve()
    mode = "APPLY" if apply else "DRY_RUN"
    tables = build_runtime_tables(root)
    worker_source = tables.pop("_worker_source")
    created_files: list[str] = []
    existing_files: list[str] = []
    skipped_files: list[str] = []
    blocked_reason = str(worker_source.get("blocked_reason") or "")

    if force:
        blocked_reason = "Force overwrite is not enabled for Gate 1/2 runtime bootstrap."

    for relative_path in RUNTIME_FILES:
        path = root / relative_path
        rel = _relative(root, path)
        if path.exists():
            existing_files.append(rel)
            skipped_files.append(rel)
            continue
        if apply and not force:
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = tables[str(relative_path)]
            path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            created_files.append(rel)
        else:
            skipped_files.append(rel)

    workers = worker_source["workers"]
    initial_status_summary = {
        "UNKNOWN": len(workers),
        "ACTIVE": 0,
        "IDLE": 0,
        "STALE": 0,
        "MISSING": 0,
        "CRASHED": 0,
    }
    safety_flags = {
        "worker_launch_enabled": False,
        "daemon_enabled": False,
        "scheduler_enabled": False,
        "effector_enabled": False,
        "qualification_ledger_write_enabled": False,
        "git_write_enabled": False,
    }
    active_marked = any(
        str(row.get("current_state") or row.get("status") or "").upper() in FORBIDDEN_ACTIVE_STATES
        for row in tables[str(ACTIVE_WORKER_TABLE)]["workers"]
    )
    if active_marked:
        blocked_reason = "Bootstrap attempted to mark an initial worker as active."

    return {
        "schema": "AIOS_WORKER_RUNTIME_BOOTSTRAP_RESULT.v1",
        "mode": mode,
        "repo_root": str(root),
        "runtime_root": str(root / RUNTIME_ROOT),
        "created_files": created_files,
        "existing_files": existing_files,
        "skipped_files": skipped_files,
        "worker_source": worker_source["worker_source"],
        "worker_source_kind": worker_source["worker_source_kind"],
        "fallback_used": bool(worker_source["fallback_used"]),
        "worker_count": len(workers),
        "worker_ids": [worker["worker_id"] for worker in workers],
        "initial_status_summary": initial_status_summary,
        "write_performed": bool(created_files),
        "blocked_reason": blocked_reason,
        "timestamp": _utc_now(),
        **safety_flags,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap System 2 worker runtime tables.")
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--apply", action="store_true", help="Create missing runtime tables.")
    parser.add_argument("--force", action="store_true", help="Blocked by design for this bootstrap workload.")
    parser.add_argument("--output-json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args()
    result = initialize_worker_runtime_tables(args.repo_root, apply=args.apply, force=args.force)
    if args.output_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"{result['schema']} {result['mode']} worker_count={result['worker_count']} write_performed={result['write_performed']}")
    return 1 if result.get("blocked_reason") and args.force else 0


if __name__ == "__main__":
    raise SystemExit(main())
