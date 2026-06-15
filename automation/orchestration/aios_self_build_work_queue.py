from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
from typing import Any


QUEUE_SCHEMA = "AIOS_SELF_BUILD_WORK_QUEUE.v1"
ITEM_SCHEMA = "AIOS_SELF_BUILD_WORK_QUEUE_ITEM.v1"

PROTECTED_ACTION_FLAGS = {
    "git_add": False,
    "git_commit": False,
    "git_push": False,
    "merge": False,
    "scheduler_activation": False,
    "daemon_activation": False,
    "worker_dispatch": False,
    "queue_mutation": False,
    "approval_mutation": False,
    "broker_live_trading": False,
    "credentials": False,
    "real_orders": False,
    "real_webhooks": False,
    "destructive_cleanup": False,
}

CORE_STATUS_READER_PATHS = [
    "automation/orchestration/aios_self_build_core_status_reader.py",
    "tests/orchestration/test_aios_self_build_core_status_reader.py",
    "docs/orchestration/AIOS_SELF_BUILD_CORE_STATUS_READER.md",
]

RUN_SUMMARY_VIEW_PATHS = [
    "automation/orchestration/aios_self_build_run_summary_view.py",
    "tests/orchestration/test_aios_self_build_run_summary_view.py",
    "docs/orchestration/AIOS_SELF_BUILD_RUN_SUMMARY_VIEW.md",
]

RUN_SUMMARY_VIEW_VALIDATORS = [
    "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_self_build_run_summary_view.py",
]

APPLY_APPROVAL_GATE_PATHS = [
    "automation/orchestration/aios_self_build_apply_approval_gate.py",
    "tests/orchestration/test_aios_self_build_apply_approval_gate.py",
    "docs/orchestration/AIOS_SELF_BUILD_APPLY_APPROVAL_GATE.md",
]

APPLY_APPROVAL_GATE_VALIDATORS = [
    "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_self_build_apply_approval_gate.py",
]


def _safety() -> dict[str, bool]:
    return {
        "dry_run_only": True,
        "commands_executed": False,
        "files_written": False,
        "network_access": False,
        "codex_launch": False,
        "chatgpt_api_call": False,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "real_webhooks": False,
        "scheduler": False,
        "daemon": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
    }


def _bounded_path(path_text: str) -> bool:
    if not path_text or "\\" in path_text:
        return False
    path = PurePosixPath(path_text)
    return not path.is_absolute() and ".." not in path.parts


def _normalize_paths(paths: list[str] | None) -> list[str]:
    output: list[str] = []
    for path in paths or []:
        path_text = str(path)
        if _bounded_path(path_text):
            output.append(path_text)
    return output


def _normalize_flags(flags: dict[str, Any] | None) -> dict[str, bool]:
    output = PROTECTED_ACTION_FLAGS.copy()
    if isinstance(flags, dict):
        for key, value in flags.items():
            if key in output:
                output[key] = bool(value)
    return output


def build_queue_item(
    *,
    priority: int = 100,
    mode: str = "generic",
    goal: str = "forex-paper-bot",
    action_id: str,
    allowed_paths: list[str] | None = None,
    validators: list[str] | None = None,
    protected_action_flags: dict[str, Any] | None = None,
    status: str = "ready",
    reason_code: str = "bounded_dry_run_item",
) -> dict[str, Any]:
    normalized_paths = _normalize_paths(allowed_paths)
    return {
        "schema": ITEM_SCHEMA,
        "priority": int(priority),
        "mode": str(mode),
        "goal": str(goal),
        "action_id": str(action_id),
        "allowed_paths": normalized_paths,
        "validators": [str(validator) for validator in validators or []],
        "protected_action_flags": _normalize_flags(protected_action_flags),
        "status": str(status),
        "reason_code": str(reason_code if normalized_paths or allowed_paths is None else "unbounded_path_rejected"),
        "safety": _safety(),
    }


def build_self_build_work_queue(
    items: list[dict[str, Any]] | None = None,
    *,
    goal: str = "forex-paper-bot",
    mode: str = "generic",
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    normalized_items = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        queue_item = build_queue_item(
            priority=int(item.get("priority", 100)),
            mode=str(item.get("mode", mode)),
            goal=str(item.get("goal", goal)),
            action_id=str(item.get("action_id", "unknown_action")),
            allowed_paths=list(item.get("allowed_paths", [])),
            validators=list(item.get("validators", [])),
            protected_action_flags=item.get("protected_action_flags", {}),
            status=str(item.get("status", "ready")),
            reason_code=str(item.get("reason_code", "bounded_dry_run_item")),
        )
        if _all_repo_paths_exist(root, queue_item["allowed_paths"]):
            queue_item["status"] = "completed"
            queue_item["reason_code"] = "completed_allowed_paths_exist"
        normalized_items.append(queue_item)
    normalized_items.sort(key=lambda queue_item: (queue_item["priority"], queue_item["action_id"]))
    return {
        "schema": QUEUE_SCHEMA,
        "goal": goal,
        "mode": mode,
        "queue_mode": "DRY_RUN_MODEL",
        "items": normalized_items,
        "item_count": len(normalized_items),
        "mutation_performed": False,
        "safety": _safety(),
    }


def _repo_root(repo_root: str | Path | None) -> Path:
    return Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[2]


def _all_repo_paths_exist(repo_root: Path, paths: list[str]) -> bool:
    if not paths:
        return False
    return all((repo_root / path).exists() for path in paths)


def build_self_build_core_preview_queue(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = _repo_root(repo_root)
    return build_self_build_work_queue(
        [
            {
                "priority": 10,
                "mode": "platform",
                "goal": "self-build-core",
                "action_id": "build_self_build_core_status_reader",
                "allowed_paths": CORE_STATUS_READER_PATHS,
                "validators": [
                    "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_self_build_core_status_reader.py",
                ],
                "protected_action_flags": {},
                "status": "ready",
                "reason_code": "preview_scope_self_build_core",
            },
            {
                "priority": 20,
                "mode": "platform",
                "goal": "self-build-core",
                "action_id": "build_self_build_run_summary_view",
                "allowed_paths": RUN_SUMMARY_VIEW_PATHS,
                "validators": RUN_SUMMARY_VIEW_VALIDATORS,
                "protected_action_flags": {},
                "status": "ready",
                "reason_code": "next_preview_scope_self_build_core",
            },
            {
                "priority": 30,
                "mode": "platform",
                "goal": "self-build-core",
                "action_id": "build_self_build_apply_approval_gate",
                "allowed_paths": APPLY_APPROVAL_GATE_PATHS,
                "validators": APPLY_APPROVAL_GATE_VALIDATORS,
                "protected_action_flags": {},
                "status": "ready",
                "reason_code": "next_preview_scope_self_build_core",
            },
        ],
        goal="self-build-core",
        mode="platform",
        repo_root=root,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview an in-memory AIOS self-build work queue.")
    parser.add_argument("--goal", default="forex-paper-bot")
    parser.add_argument("--mode", default="generic")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(json.dumps(build_self_build_work_queue(goal=args.goal, mode=args.mode), indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
