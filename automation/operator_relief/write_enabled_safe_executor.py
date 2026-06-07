"""Write-enabled safe executor for Operator Relief v1.

The only v1 write is one JSON DRY_RUN evidence report under
reports/operator_relief/. Source files, telemetry jsonl, approval queue files,
and protected paths are never written by this module.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .bounded_executor import BoundedExecutorReport, MODE_DRY_RUN, run_bounded_executor
from .full_auto_policy import FullAutoTask


REPORT_ROOT = Path("reports/operator_relief")


@dataclass(frozen=True)
class SafeWriteExecutorReport:
    task_id: str
    status: str
    bounded_executor: dict[str, Any]
    report_path: str | None
    write_performed: bool
    write_allowed: bool
    reasons: list[str]
    safety: dict[str, bool]
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _safety(write_performed: bool) -> dict[str, bool]:
    return {
        "report_json_written": write_performed,
        "source_files_mutated": False,
        "telemetry_jsonl_written": False,
        "approval_queue_files_written": False,
        "openai_api_invoked": False,
        "codex_invoked": False,
        "daemon_started": False,
        "watcher_started": False,
        "service_started": False,
        "commit_executed": False,
        "push_executed": False,
        "merge_executed": False,
        "executable": False,
    }


def _resolve_report_path(repo_root: Path, output_path: str | Path) -> Path:
    root = repo_root.resolve()
    report_root = (root / REPORT_ROOT).resolve()
    raw_path = Path(output_path)
    candidate = raw_path if raw_path.is_absolute() else root / raw_path
    resolved = candidate.resolve()

    if resolved.suffix.lower() != ".json":
        raise ValueError("Write-enabled safe executor can write only .json reports.")
    if not (resolved == report_root or report_root in resolved.parents):
        raise ValueError("Report path must stay inside reports/operator_relief/.")
    if any(part in {"telemetry", "approval", "automation", "docs", "services", "apps"} for part in resolved.parts):
        if REPORT_ROOT.as_posix() not in resolved.as_posix().replace("\\", "/"):
            raise ValueError("Report path resolves outside the approved report root.")
    return resolved


def _write_json_create_new(path: Path, payload: dict[str, Any], overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    mode = "w" if overwrite else "x"
    with path.open(mode, encoding="utf-8") as handle:
        handle.write(content)


def run_write_enabled_safe_executor(
    task: FullAutoTask,
    repo_state: Any,
    repo_root: Path,
    output_path: str | Path,
    overwrite: bool = False,
    allow_failure_report: bool = False,
) -> SafeWriteExecutorReport:
    bounded = run_bounded_executor(task, repo_state, repo_root, mode=MODE_DRY_RUN)
    bounded_dict = bounded.to_dict()
    reasons: list[str] = []
    write_allowed = bounded.status == "DRY_RUN_COMPLETE" or allow_failure_report

    try:
        report_path = _resolve_report_path(repo_root, output_path)
    except ValueError as exc:
        return SafeWriteExecutorReport(
            task_id=task.task_id,
            status="WRITE_BLOCKED",
            bounded_executor=bounded_dict,
            report_path=None,
            write_performed=False,
            write_allowed=False,
            reasons=[str(exc)],
            safety=_safety(False),
            executable=False,
        )

    if not write_allowed:
        reasons.append("Report write blocked because task did not pass bounded executor gates.")
        return SafeWriteExecutorReport(
            task_id=task.task_id,
            status="WRITE_SKIPPED",
            bounded_executor=bounded_dict,
            report_path=str(report_path),
            write_performed=False,
            write_allowed=False,
            reasons=reasons,
            safety=_safety(False),
            executable=False,
        )

    payload = {
        "task_id": task.task_id,
        "mode": MODE_DRY_RUN,
        "bounded_executor": bounded_dict,
        "report_type": "operator_relief_write_enabled_safe_executor_v1",
        "executable": False,
    }

    try:
        _write_json_create_new(report_path, payload, overwrite=overwrite)
    except FileExistsError:
        return SafeWriteExecutorReport(
            task_id=task.task_id,
            status="WRITE_BLOCKED",
            bounded_executor=bounded_dict,
            report_path=str(report_path),
            write_performed=False,
            write_allowed=True,
            reasons=["Report already exists and overwrite was not explicitly allowed."],
            safety=_safety(False),
            executable=False,
        )

    return SafeWriteExecutorReport(
        task_id=task.task_id,
        status="WRITE_COMPLETE",
        bounded_executor=bounded_dict,
        report_path=str(report_path),
        write_performed=True,
        write_allowed=True,
        reasons=reasons,
        safety=_safety(True),
        executable=False,
    )
