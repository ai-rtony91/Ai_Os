"""Windows overnight launch plan scaffold for Operator Relief v1."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable


MODE_DRY_RUN = "DRY_RUN"
MODE_APPLY_SCHEDULE_PLAN = "APPLY_SCHEDULE_PLAN"
TASK_NAME = "AI_OS_Operator_Relief_Night_Mission"


@dataclass(frozen=True)
class ScheduleCommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OvernightScheduleReport:
    status: str
    mode: str
    task_name: str
    launch_command: list[str]
    schedule_command: list[str]
    command_result: dict[str, Any] | None
    daemon_started: bool
    watcher_started: bool
    background_service_started: bool
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


ScheduleRunner = Callable[[list[str]], ScheduleCommandResult]


def _launch_command(max_cycles: int) -> list[str]:
    return [".\\aios.ps1", "-Mode", "night-mission", "-MaxCycles", str(max_cycles)]


def _schedule_command(max_cycles: int) -> list[str]:
    action = " ".join(_launch_command(max_cycles))
    return [
        "schtasks.exe",
        "/Create",
        "/TN",
        TASK_NAME,
        "/SC",
        "ONCE",
        "/ST",
        "23:00",
        "/TR",
        action,
    ]


def _run_schedule(command: list[str]) -> ScheduleCommandResult:
    result = subprocess.run(command, capture_output=True, text=True, shell=False, check=False)
    return ScheduleCommandResult(command, result.returncode, result.stdout[-1200:], result.stderr[-1200:], executable=False)


def plan_overnight_schedule(
    max_cycles: int = 3,
    mode: str = MODE_DRY_RUN,
    schedule_runner: ScheduleRunner | None = None,
) -> OvernightScheduleReport:
    if max_cycles <= 0:
        raise ValueError("max_cycles must be greater than zero.")
    if mode not in {MODE_DRY_RUN, MODE_APPLY_SCHEDULE_PLAN}:
        raise ValueError("Mode must be DRY_RUN or APPLY_SCHEDULE_PLAN.")

    launch = _launch_command(max_cycles)
    schedule = _schedule_command(max_cycles)
    if mode == MODE_DRY_RUN:
        return OvernightScheduleReport(
            status="SCHEDULE_PLAN_READY",
            mode=mode,
            task_name=TASK_NAME,
            launch_command=launch,
            schedule_command=schedule,
            command_result=None,
            daemon_started=False,
            watcher_started=False,
            background_service_started=False,
            executable=False,
        )

    runner = schedule_runner or _run_schedule
    result = runner(schedule)
    return OvernightScheduleReport(
        status="SCHEDULE_PLAN_APPLIED" if result.returncode == 0 else "SCHEDULE_PLAN_FAILED",
        mode=mode,
        task_name=TASK_NAME,
        launch_command=launch,
        schedule_command=schedule,
        command_result=result.to_dict(),
        daemon_started=False,
        watcher_started=False,
        background_service_started=False,
        executable=result.returncode == 0,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan Operator Relief overnight schedule launch.")
    parser.add_argument("--max-cycles", type=int, default=3)
    parser.add_argument("--mode", default=MODE_DRY_RUN, choices=[MODE_DRY_RUN, MODE_APPLY_SCHEDULE_PLAN])
    args = parser.parse_args(argv)
    report = plan_overnight_schedule(max_cycles=args.max_cycles, mode=args.mode)
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.status == "SCHEDULE_PLAN_READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
