"""Notification gate for human-needed operator-relief events."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_NOTIFICATION_LOG = Path("telemetry/operator_relief/notifications.jsonl")
DEFAULT_ADB_SOS_SCRIPT = Path("tools/android/Send-AiosAdbSosWake.ps1")

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


def _tail(text: str, limit: int = 1200) -> str:
    return text[-limit:] if len(text) > limit else text


def send_adb_sos(
    script_path: Path | str = DEFAULT_ADB_SOS_SCRIPT,
) -> dict[str, Any]:
    path = Path(script_path)
    command = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        path.as_posix(),
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=False,
            check=False,
        )
        return {
            "enabled": True,
            "attempted": True,
            "script_path": path.as_posix(),
            "command": command,
            "exit_code": result.returncode,
            "success": result.returncode == 0,
            "stdout_tail": _tail(result.stdout),
            "stderr_tail": _tail(result.stderr),
        }
    except OSError as exc:
        return {
            "enabled": True,
            "attempted": True,
            "script_path": path.as_posix(),
            "command": command,
            "exit_code": None,
            "success": False,
            "stdout_tail": "",
            "stderr_tail": str(exc),
        }


def emit_notification(
    event: dict[str, Any],
    log_path: Path | str = DEFAULT_NOTIFICATION_LOG,
    print_to_console: bool = True,
    send_adb_sos_enabled: bool = False,
    adb_sos_runner: Any | None = None,
) -> Path | None:
    if not should_notify(event):
        return None
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    adb_sos_result = {
        "enabled": send_adb_sos_enabled,
        "attempted": False,
        "success": None,
    }
    if send_adb_sos_enabled:
        runner = adb_sos_runner or send_adb_sos
        adb_sos_result = runner()
    record = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "executable": False,
        "adb_sos": adb_sos_result,
        **event,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    if print_to_console:
        print("AI_OS operator relief notification")
        print(f"Reason: {record.get('classification')}")
        print(f"Next safe action: {record.get('safe_next_action')}")
        if send_adb_sos_enabled and not adb_sos_result.get("success"):
            print("ADB SOS wake failed or was unavailable; failure was logged.")
    return path
