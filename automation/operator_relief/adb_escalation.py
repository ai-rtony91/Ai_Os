"""Gated ADB alert planning for Operator Relief night missions."""

from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from .notification_gate import DEFAULT_ADB_SOS_SCRIPT


MODE_DRY_RUN = "DRY_RUN"
MODE_APPLY_ADB_ALERT = "APPLY_ADB_ALERT"
ALERT_TRIGGERS = {
    "approval_required",
    "blocked",
    "validator_failed",
    "bridge_failed",
    "dirty_state",
}


@dataclass(frozen=True)
class AdbAlertCommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AdbEscalationReport:
    status: str
    mode: str
    trigger: str
    alert_required: bool
    script_path: str
    command: list[str]
    command_result: dict[str, Any] | None
    reasons: list[str]
    external_messaging_dependency: bool
    credential_material_required: bool
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


CommandRunner = Callable[[list[str]], AdbAlertCommandResult]


def _command(script_path: Path) -> list[str]:
    return [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        script_path.as_posix(),
    ]


def _run_command(command: list[str]) -> AdbAlertCommandResult:
    result = subprocess.run(command, capture_output=True, text=True, shell=False, check=False)
    return AdbAlertCommandResult(command, result.returncode, result.stdout[-1200:], result.stderr[-1200:], executable=False)


def plan_adb_escalation(
    trigger: str,
    mode: str = MODE_DRY_RUN,
    script_path: Path | str = DEFAULT_ADB_SOS_SCRIPT,
    command_runner: CommandRunner | None = None,
) -> AdbEscalationReport:
    if mode not in {MODE_DRY_RUN, MODE_APPLY_ADB_ALERT}:
        raise ValueError("Mode must be DRY_RUN or APPLY_ADB_ALERT.")

    normalized_trigger = trigger.strip().lower()
    path = Path(script_path)
    command = _command(path)
    alert_required = normalized_trigger in ALERT_TRIGGERS

    if not alert_required:
        return AdbEscalationReport(
            status="ADB_ALERT_NOT_REQUIRED",
            mode=mode,
            trigger=normalized_trigger,
            alert_required=False,
            script_path=path.as_posix(),
            command=command,
            command_result=None,
            reasons=["Trigger does not require ADB escalation."],
            external_messaging_dependency=False,
            credential_material_required=False,
            executable=False,
        )

    if mode == MODE_DRY_RUN:
        return AdbEscalationReport(
            status="ADB_ALERT_PLANNED",
            mode=mode,
            trigger=normalized_trigger,
            alert_required=True,
            script_path=path.as_posix(),
            command=command,
            command_result=None,
            reasons=["ADB alert command planned only; no command executed."],
            external_messaging_dependency=False,
            credential_material_required=False,
            executable=False,
        )

    runner = command_runner or _run_command
    result = runner(command)
    return AdbEscalationReport(
        status="ADB_ALERT_SENT" if result.returncode == 0 else "ADB_ALERT_FAILED",
        mode=mode,
        trigger=normalized_trigger,
        alert_required=True,
        script_path=path.as_posix(),
        command=command,
        command_result=result.to_dict(),
        reasons=[] if result.returncode == 0 else ["ADB alert command failed."],
        external_messaging_dependency=False,
        credential_material_required=False,
        executable=result.returncode == 0,
    )
