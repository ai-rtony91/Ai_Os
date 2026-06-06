"""Bounded in-memory multi-step loop for Operator Relief autonomy spine v1."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .autonomy_controller import run_autonomy_controller
from .full_auto_policy import FullAutoTask


STOP_STATUSES = {
    "STOPPED_BLOCKED",
    "STOPPED_APPROVAL_REQUIRED",
    "STOPPED_VALIDATOR_FAILED",
    "STOPPED_UNSUPPORTED_VALIDATOR",
}


@dataclass(frozen=True)
class AutonomyLoopReport:
    status: str
    max_steps: int
    processed_count: int
    stop_reason: str
    task_reports: list[dict[str, Any]]
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_bounded_autonomy_loop(
    tasks: list[FullAutoTask],
    repo_state: Any,
    repo_root: Path | None = None,
    max_steps: int = 3,
) -> AutonomyLoopReport:
    reports: list[dict[str, Any]] = []
    stop_reason = "MAX_STEPS_REACHED"

    for task in tasks[:max_steps]:
        report = run_autonomy_controller(task, repo_state, repo_root).to_dict()
        reports.append(report)
        if report["approval"]["status"] == "APPROVAL_REQUIRED":
            stop_reason = "APPROVAL_REQUIRED"
            break
        if report["status"] in STOP_STATUSES:
            stop_reason = report["status"]
            break
    else:
        if len(tasks) <= max_steps:
            stop_reason = "TASKS_EXHAUSTED"

    return AutonomyLoopReport(
        status="DRY_RUN_STOPPED",
        max_steps=max_steps,
        processed_count=len(reports),
        stop_reason=stop_reason,
        task_reports=reports,
        executable=False,
    )
