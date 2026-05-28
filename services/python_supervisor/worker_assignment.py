"""AI_OS Night Supervisor read-only worker assignment matcher.

Schema/contract reference: schemas/aios/orchestration/overnight_supervisor.schema.json
Mode: DRY_RUN
blocked_capabilities: worker_launch, worker_state_write, queue_mutation,
packet_movement, approval_mutation, git_stage_commit_push
next_safe_action: Treat worker matches as routing evidence only until Human Owner approval.
commit_performed: NO / push_performed: NO
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


FALLBACK_WORKER_ID = "brainstem_codex"


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _profiles_path(repo_root: Path) -> Path:
    return repo_root / "automation" / "orchestration" / "workers" / "AIOS_WORKER_PROFILES.json"


def load_worker_profiles(repo_root: str | Path = ".") -> list[dict[str, Any]]:
    path = _profiles_path(Path(repo_root).resolve())
    payload: Any = None
    for encoding in ("utf-8", "utf-8-sig", "utf-16"):
        try:
            payload = json.loads(path.read_text(encoding=encoding))
            break
        except Exception:
            payload = None
    if payload is None:
        return []
    workers = payload.get("workers", payload if isinstance(payload, list) else [])
    return [worker for worker in workers if isinstance(worker, dict)]


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip().strip("/")


def _path_owned(worker: dict[str, Any], related_files: list[str]) -> bool:
    owns_paths = [_normalize_path(str(path)) for path in _as_list(worker.get("owns_paths"))]
    for related in [_normalize_path(path) for path in related_files]:
        for owned in owns_paths:
            if related == owned or related.startswith(f"{owned}/") or owned.startswith(f"{related}/"):
                return True
    return False


def _worker_record(worker: dict[str, Any], lane: str, reason: str) -> dict[str, Any]:
    return {
        "worker_id": str(worker.get("worker_id") or FALLBACK_WORKER_ID),
        "lane": lane,
        "display_title": str(worker.get("display_title") or worker.get("worker_id") or FALLBACK_WORKER_ID),
        "default_path": str(worker.get("default_path") or ""),
        "cannot_overlap_with": [str(value) for value in _as_list(worker.get("cannot_overlap_with"))],
        "match_reason": reason,
        "worker_launch_enabled": False,
    }


def assign_worker(queue_item: dict[str, Any], workers: list[dict[str, Any]]) -> dict[str, Any]:
    lane = str(queue_item.get("lane") or "UNKNOWN")
    assigned_worker = str(queue_item.get("worker_id") or queue_item.get("assigned_worker") or "")
    related_files = [str(path) for path in _as_list(queue_item.get("related_files"))]

    by_id = {str(worker.get("worker_id")): worker for worker in workers if worker.get("worker_id")}

    if lane in by_id:
        return _worker_record(by_id[lane], lane, "matched_owner_lane")

    if assigned_worker in by_id:
        return _worker_record(by_id[assigned_worker], lane, "matched_assigned_worker")

    for worker in workers:
        if _path_owned(worker, related_files):
            return _worker_record(worker, lane, "matched_path_ownership")

    fallback = by_id.get(FALLBACK_WORKER_ID) or (workers[0] if workers else {"worker_id": FALLBACK_WORKER_ID})
    return _worker_record(fallback, lane, "fallback_brainstem_codex")


def assign_workers(queue_items: list[dict[str, Any]], repo_root: str | Path = ".") -> list[dict[str, Any]]:
    workers = load_worker_profiles(repo_root)
    return [
        {
            "packet_id": str(item.get("packet_id") or "UNKNOWN"),
            **assign_worker(item, workers),
        }
        for item in queue_items
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Match AI_OS queue items to workers without launching workers.")
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--queue-json", default=None, help="Optional queue item list JSON path.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    args = parser.parse_args()

    queue_items: list[dict[str, Any]] = []
    if args.queue_json:
        queue_items = json.loads(Path(args.queue_json).read_text(encoding="utf-8"))
    print(json.dumps(assign_workers(queue_items, args.repo_root), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
