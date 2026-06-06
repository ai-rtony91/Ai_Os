"""Notification gate for human-needed operator-relief events."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_NOTIFICATION_LOG = Path("telemetry/operator_relief/notifications.jsonl")

NOTIFICATION_TRIGGERS = {
    "approval_needed",
    "validator_failure",
    "packet_missing_fields",
    "branch_mismatch",
    "dirty_worktree",
    "protected_path_touched",
    "forbidden_action_requested",
    "loop_failure",
    "blocked_action",
}


def should_notify(classification: dict[str, Any]) -> bool:
    if not classification.get("approval_needed"):
        return False
    label = str(classification.get("classification", ""))
    return label in NOTIFICATION_TRIGGERS or classification.get("blocked_action") is True


def emit_notification(
    event: dict[str, Any],
    log_path: Path | str = DEFAULT_NOTIFICATION_LOG,
    print_to_console: bool = True,
) -> Path | None:
    if not should_notify(event):
        return None
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "executable": False,
        **event,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    if print_to_console:
        print("AI_OS operator relief notification")
        print(f"Reason: {record.get('classification')}")
        print(f"Next safe action: {record.get('safe_next_action')}")
    return path
