from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_BOUNDED_LOCAL_APPLY_RUNNER.v1"

PROTECTED_ACTIONS_BLOCKED = {
    "git_add": True,
    "git_commit": True,
    "git_push": True,
    "merge": True,
    "scheduler_activation": True,
    "daemon_activation": True,
    "worker_dispatch": True,
    "queue_mutation": True,
    "approval_mutation": True,
    "broker_live_trading": True,
    "credentials": True,
    "real_orders": True,
    "real_webhooks": True,
    "destructive_cleanup": True,
}


def _safety() -> dict[str, bool]:
    return {
        "runner_mode_dry_run": True,
        "commands_executed": False,
        "files_written": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
        "scheduler": False,
        "daemon": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "real_webhooks": False,
        "network_access": False,
    }


def build_bounded_local_apply_preview(
    queue_item: dict[str, Any] | None,
    *,
    max_repairs: int = 1,
    max_files_changed: int = 5,
) -> dict[str, Any]:
    item = queue_item if isinstance(queue_item, dict) else {}
    action = str(item.get("action_id", "unknown_action"))
    goal = str(item.get("goal", "forex-paper-bot"))
    allowed_paths = [str(path) for path in item.get("allowed_paths", [])]
    validators = [str(command) for command in item.get("validators", [])]
    command_preview = [
        (
            "python automation/orchestration/aios_productive_bounded_executor.py "
            f"--goal {goal} --action {action} --apply --max-repairs {int(max_repairs)}"
        )
    ]
    return {
        "schema": SCHEMA,
        "runner_mode": "DRY_RUN",
        "runner_status": "preview_only",
        "command_preview": command_preview,
        "allowed_paths": allowed_paths,
        "validators": validators,
        "max_repairs": int(max_repairs),
        "max_files_changed": int(max_files_changed),
        "protected_actions_blocked": PROTECTED_ACTIONS_BLOCKED.copy(),
        "commands_executed": False,
        "files_written": [],
        "next_safe_action": "Review this preview only. Do not run local APPLY until Anthony approves.",
        "safety": _safety(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview a bounded local APPLY runner invocation.")
    parser.add_argument("--queue-item", default="{}")
    parser.add_argument("--max-repairs", type=int, default=1)
    parser.add_argument("--max-files-changed", type=int, default=5)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    item = json.loads(args.queue_item)
    print(
        json.dumps(
            build_bounded_local_apply_preview(
                item,
                max_repairs=args.max_repairs,
                max_files_changed=args.max_files_changed,
            ),
            indent=2,
            sort_keys=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
