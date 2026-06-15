from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_NEXT_ACTION_SELECTOR.v1"


def _safety() -> dict[str, bool]:
    return {
        "dry_run_only": True,
        "commands_executed": False,
        "protected_action_allowed": False,
        "network_access": False,
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
    }


def _blocked(reason_code: str, next_safe_action: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "selector_status": "stopped",
        "selected_queue_item": None,
        "selected_next_action": "none",
        "reason_code": reason_code,
        "next_safe_action": next_safe_action,
        "safety": _safety(),
    }


def _protected_required(item: dict[str, Any]) -> bool:
    flags = item.get("protected_action_flags", {})
    if not isinstance(flags, dict):
        return True
    return any(bool(value) for value in flags.values())


def select_next_action(readiness: dict[str, Any] | None, queue: dict[str, Any] | None) -> dict[str, Any]:
    readiness = readiness if isinstance(readiness, dict) else {}
    queue = queue if isinstance(queue, dict) else {}

    if readiness.get("sos_required") is True:
        return _blocked("sos_required", "Stop and resolve SOS before selecting self-build work.")
    readiness_status = str(readiness.get("readiness_status", "not_ready"))
    if readiness_status == "review_required":
        return _blocked("readiness_review_required", "Stop for Anthony self-build readiness review.")
    if readiness_status != "ready":
        return _blocked("readiness_not_ready", "Stop until self-build readiness returns ready.")

    items = queue.get("items", [])
    if not isinstance(items, list) or not items:
        return _blocked("queue_empty", "Add a bounded DRY_RUN-safe queue item before continuing.")

    for item in sorted((item for item in items if isinstance(item, dict)), key=lambda value: value.get("priority", 100)):
        if str(item.get("status", "ready")) != "ready":
            continue
        if str(item.get("queue_item_mode", item.get("execution_mode", "DRY_RUN"))).upper() != "DRY_RUN":
            return _blocked("non_dry_run_item_rejected", "Only DRY_RUN-safe queue items are selectable in v0.")
        if _protected_required(item):
            return _blocked("protected_action_required", "Stop because the selected item requires protected action approval.")
        return {
            "schema": SCHEMA,
            "selector_status": "selected",
            "selected_queue_item": item,
            "selected_next_action": item.get("action_id", "unknown_action"),
            "reason_code": "selected_bounded_dry_run_action",
            "next_safe_action": "Preview the selected bounded DRY_RUN action. Do not execute protected actions.",
            "safety": _safety(),
        }

    return _blocked("no_ready_queue_item", "Add a ready bounded DRY_RUN-safe queue item before continuing.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview the next AIOS self-build queue action.")
    parser.add_argument("--readiness", default="{}")
    parser.add_argument("--queue", default="{}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    readiness = json.loads(args.readiness)
    queue = json.loads(args.queue)
    print(json.dumps(select_next_action(readiness, queue), indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
