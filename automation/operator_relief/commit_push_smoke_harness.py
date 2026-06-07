"""Safe smoke harness for Operator Relief commit/push closeout."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .auto_commit_push_executor import (
    FEATURE_BRANCH,
    FEATURE_UPSTREAM,
    MODE_APPLY_COMMIT_PUSH,
    MODE_DRY_RUN,
    CommandRunner,
    run_auto_commit_push_executor,
)
from .full_auto_policy import FullAutoTask


MODE_APPLY_SMOKE = "APPLY_COMMIT_PUSH_SMOKE"
SMOKE_FILE = "automation/operator_relief/generated_smoke/auto_commit_push_smoke.txt"


@dataclass(frozen=True)
class CommitPushSmokeReport:
    status: str
    mode: str
    task: dict[str, Any]
    executor_report: dict[str, Any] | None
    reasons: list[str]
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_smoke_task() -> FullAutoTask:
    return FullAutoTask(
        task_id="auto-commit-push-smoke",
        description="Generated safe commit/push smoke task",
        allowed_paths=[SMOKE_FILE],
        forbidden_paths=["AGENTS.md", "README.md", "docs/governance/**"],
        changed_paths=[SMOKE_FILE],
        requested_actions=[],
        validator_targets=[SMOKE_FILE],
        expected_branch=FEATURE_BRANCH,
    )


def _smoke_repo_state(repo_root: Path) -> Any:
    class SmokeRepoState:
        branch = FEATURE_BRANCH
        git_status = f"## {FEATURE_BRANCH}...{FEATURE_UPSTREAM}\n M {SMOKE_FILE}"
        dirty_state = "DIRTY"
        executable = False

        def __init__(self, root: Path) -> None:
            self.repo_root = str(root)

    return SmokeRepoState(repo_root)


def run_commit_push_smoke_harness(
    repo_root: Path,
    mode: str = MODE_DRY_RUN,
    command_runner: CommandRunner | None = None,
) -> CommitPushSmokeReport:
    task = build_smoke_task()
    if mode == MODE_DRY_RUN:
        executor = run_auto_commit_push_executor(
            task,
            _smoke_repo_state(repo_root),
            repo_root,
            validators_passed=True,
            mode=MODE_DRY_RUN,
        ).to_dict()
        return CommitPushSmokeReport(
            status="SMOKE_DRY_RUN",
            mode=mode,
            task=task.to_dict(),
            executor_report=executor,
            reasons=["Smoke harness planned exact-file commit/push only; no commands executed."],
            executable=False,
        )

    if mode != MODE_APPLY_SMOKE:
        return CommitPushSmokeReport(
            status="SMOKE_BLOCKED",
            mode=mode,
            task=task.to_dict(),
            executor_report=None,
            reasons=["Explicit APPLY_COMMIT_PUSH_SMOKE mode is required."],
            executable=False,
        )

    if command_runner is None:
        return CommitPushSmokeReport(
            status="SMOKE_BLOCKED",
            mode=mode,
            task=task.to_dict(),
            executor_report=None,
            reasons=["APPLY smoke requires an explicit command runner in v1."],
            executable=False,
        )

    executor = run_auto_commit_push_executor(
        task,
        _smoke_repo_state(repo_root),
        repo_root,
        validators_passed=True,
        mode=MODE_APPLY_COMMIT_PUSH,
        command_runner=command_runner,
    ).to_dict()
    return CommitPushSmokeReport(
        status="SMOKE_APPLY_COMPLETE" if executor["status"] == "APPLY_COMMIT_PUSH_COMPLETE" else "SMOKE_BLOCKED",
        mode=mode,
        task=task.to_dict(),
        executor_report=executor,
        reasons=executor["reasons"],
        executable=executor["executable"] is True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Operator Relief commit/push smoke harness.")
    parser.add_argument("--mode", default=MODE_DRY_RUN, choices=[MODE_DRY_RUN, MODE_APPLY_SMOKE])
    args = parser.parse_args(argv)
    report = run_commit_push_smoke_harness(Path.cwd(), mode=args.mode)
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.status == "SMOKE_DRY_RUN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
