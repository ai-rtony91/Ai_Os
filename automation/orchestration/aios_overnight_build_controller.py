from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_OVERNIGHT_BUILD_CONTROLLER.v1"

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
        "controller_mode_dry_run": True,
        "commands_executed": False,
        "files_written": False,
        "scheduler": False,
        "daemon": False,
        "background_runtime": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "real_webhooks": False,
        "network_access": False,
        "codex_launch": False,
        "chatgpt_api_call": False,
    }


def _readiness_from_status(status: dict[str, Any]) -> dict[str, Any]:
    if isinstance(status.get("self_build_loop_readiness"), dict):
        return status["self_build_loop_readiness"]
    if status.get("schema") == "AIOS_SELF_BUILD_LOOP_READINESS.v1":
        return status
    return {
        "readiness_status": status.get("readiness_status", "not_ready"),
        "current_goal": status.get("goal", "forex-paper-bot"),
        "latest_validated_chain": status.get("selected_action", "unknown"),
        "sos_required": bool(status.get("sos_required", False)),
    }


def _first_ready_item(queue: dict[str, Any]) -> dict[str, Any] | None:
    items = queue.get("items", [])
    if not isinstance(items, list):
        return None
    for item in sorted((item for item in items if isinstance(item, dict)), key=lambda value: value.get("priority", 100)):
        if str(item.get("status", "ready")) != "ready":
            continue
        flags = item.get("protected_action_flags", {})
        if isinstance(flags, dict) and any(bool(value) for value in flags.values()):
            continue
        return item
    return None


def build_overnight_build_controller(
    status: dict[str, Any] | None = None,
    queue: dict[str, Any] | None = None,
    *,
    goal: str = "forex-paper-bot",
    current_mode: str = "generic",
    cycle_budget: int = 1,
    time_budget_minutes: int = 30,
    max_files_changed: int = 5,
    max_repairs: int = 1,
) -> dict[str, Any]:
    payload = status if isinstance(status, dict) else {}
    readiness = _readiness_from_status(payload)
    queue = queue if isinstance(queue, dict) else {}
    readiness_status = str(readiness.get("readiness_status", "not_ready"))
    sos_required = bool(readiness.get("sos_required") is True)
    selected_item = _first_ready_item(queue) if readiness_status == "ready" and not sos_required else None
    allowed_to_continue = selected_item is not None

    if sos_required:
        stop_reason = "sos_required"
        selected_next_action = "none"
    elif readiness_status == "review_required":
        stop_reason = "self_build_readiness_review_required"
        selected_next_action = "self_build_loop_readiness_review"
    elif readiness_status != "ready":
        stop_reason = "readiness_not_ready"
        selected_next_action = "none"
    elif selected_item is None:
        stop_reason = "no_safe_queue_item"
        selected_next_action = "none"
    else:
        stop_reason = "none"
        selected_next_action = str(selected_item.get("action_id", "unknown_action"))

    return {
        "schema": SCHEMA,
        "controller_mode": "DRY_RUN",
        "goal": readiness.get("current_goal", goal),
        "current_mode": current_mode,
        "readiness_status": readiness_status,
        "allowed_to_continue": allowed_to_continue,
        "cycle_budget": int(cycle_budget),
        "time_budget_minutes": int(time_budget_minutes),
        "max_files_changed": int(max_files_changed),
        "max_repairs": int(max_repairs),
        "selected_queue_item": selected_item,
        "selected_next_action": selected_next_action,
        "stop_reason": stop_reason,
        "sos_required": sos_required,
        "wake_anthony": sos_required,
        "morning_summary": (
            f"AIOS self-build DRY_RUN: readiness={readiness_status}, "
            f"allowed_to_continue={allowed_to_continue}, stop_reason={stop_reason}."
        ),
        "approval_required": PROTECTED_ACTIONS_BLOCKED.copy(),
        "safety": _safety(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview AIOS overnight self-build controller state.")
    parser.add_argument("--controller-mode", default="DRY_RUN")
    parser.add_argument("--goal", default="forex-paper-bot")
    parser.add_argument("--current-mode", default="generic")
    parser.add_argument("--status", default="{}")
    parser.add_argument("--queue", default="{}")
    parser.add_argument("--cycle-budget", type=int, default=1)
    parser.add_argument("--time-budget-minutes", type=int, default=30)
    parser.add_argument("--max-files-changed", type=int, default=5)
    parser.add_argument("--max-repairs", type=int, default=1)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    status = json.loads(args.status)
    queue = json.loads(args.queue)
    report = build_overnight_build_controller(
        status,
        queue,
        goal=args.goal,
        current_mode=args.current_mode,
        cycle_budget=args.cycle_budget,
        time_budget_minutes=args.time_budget_minutes,
        max_files_changed=args.max_files_changed,
        max_repairs=args.max_repairs,
    )
    report["controller_mode"] = "DRY_RUN"
    print(json.dumps(report, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
