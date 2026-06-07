"""One-shot bounded night mission runner for Operator Relief v1."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from .adb_escalation import plan_adb_escalation
from .repo_state import collect_repo_state
from .runtime_bridge import RuntimeBridgeReport, run_runtime_bridge


MODE_DRY_RUN = "DRY_RUN"
MODE_APPLY_ADB_ALERT = "APPLY_ADB_ALERT"
STOP_STATUSES = {
    "RUNTIME_APPROVAL_REQUIRED_REPORTED": "approval_required",
    "RUNTIME_BLOCKED_REPORTED": "blocked",
    "RUNTIME_UNSUPPORTED_VALIDATOR_REPORTED": "validator_failed",
    "RUNTIME_VALIDATOR_FAILED_REPORTED": "validator_failed",
    "RUNTIME_BLOCKED": "bridge_failed",
}


@dataclass(frozen=True)
class UnattendedMissionReport:
    status: str
    mode: str
    processed_cycles: int
    max_cycles: int
    stop_reason: str
    runtime_reports: list[dict[str, Any]]
    adb_escalation: dict[str, Any] | None
    commit_push_attempted: bool
    commit_executed: bool
    push_executed: bool
    protected_git_action_executed: bool
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


RuntimeRunner = Callable[[Path, Any], RuntimeBridgeReport]
RepoStateProvider = Callable[[Path], Any]


def _runtime_runner(repo_root: Path, repo_state: Any) -> RuntimeBridgeReport:
    return run_runtime_bridge(repo_root, repo_state=repo_state)


def run_unattended_mission(
    repo_root: Path,
    max_cycles: int = 3,
    mode: str = MODE_DRY_RUN,
    runtime_runner: RuntimeRunner | None = None,
    repo_state_provider: RepoStateProvider | None = None,
) -> UnattendedMissionReport:
    if max_cycles <= 0:
        raise ValueError("max_cycles must be greater than zero.")
    if mode not in {MODE_DRY_RUN, MODE_APPLY_ADB_ALERT}:
        raise ValueError("Mode must be DRY_RUN or APPLY_ADB_ALERT.")

    root = repo_root.resolve()
    run_once = runtime_runner or _runtime_runner
    state_provider = repo_state_provider or collect_repo_state
    reports: list[dict[str, Any]] = []

    for _cycle in range(max_cycles):
        repo_state = state_provider(root)
        if getattr(repo_state, "dirty_state", "") == "DIRTY":
            escalation = plan_adb_escalation("dirty_state", mode=mode)
            return UnattendedMissionReport(
                status="MISSION_STOPPED",
                mode=mode,
                processed_cycles=len(reports),
                max_cycles=max_cycles,
                stop_reason="DIRTY_REPO",
                runtime_reports=reports,
                adb_escalation=escalation.to_dict(),
                commit_push_attempted=False,
                commit_executed=False,
                push_executed=False,
                protected_git_action_executed=False,
                executable=False,
            )

        runtime_report = run_once(root, repo_state).to_dict()
        reports.append(runtime_report)
        status = runtime_report["status"]

        if status == "RUNTIME_NO_TASKS":
            return UnattendedMissionReport(
                status="MISSION_STOPPED",
                mode=mode,
                processed_cycles=len(reports),
                max_cycles=max_cycles,
                stop_reason="NO_INBOX_TASK",
                runtime_reports=reports,
                adb_escalation=None,
                commit_push_attempted=False,
                commit_executed=False,
                push_executed=False,
                protected_git_action_executed=False,
                executable=False,
            )

        if status in STOP_STATUSES:
            trigger = STOP_STATUSES[status]
            escalation = plan_adb_escalation(trigger, mode=mode)
            return UnattendedMissionReport(
                status="MISSION_STOPPED",
                mode=mode,
                processed_cycles=len(reports),
                max_cycles=max_cycles,
                stop_reason=status,
                runtime_reports=reports,
                adb_escalation=escalation.to_dict(),
                commit_push_attempted=False,
                commit_executed=False,
                push_executed=False,
                protected_git_action_executed=False,
                executable=False,
            )

    return UnattendedMissionReport(
        status="MISSION_STOPPED",
        mode=mode,
        processed_cycles=len(reports),
        max_cycles=max_cycles,
        stop_reason="MAX_CYCLES_REACHED",
        runtime_reports=reports,
        adb_escalation=None,
        commit_push_attempted=False,
        commit_executed=False,
        push_executed=False,
        protected_git_action_executed=False,
        executable=False,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one bounded Operator Relief night mission.")
    parser.add_argument("--max-cycles", type=int, default=3)
    parser.add_argument("--mode", choices=[MODE_DRY_RUN, MODE_APPLY_ADB_ALERT], default=MODE_DRY_RUN)
    args = parser.parse_args(argv)
    report = run_unattended_mission(Path.cwd(), max_cycles=args.max_cycles, mode=args.mode)
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.status == "MISSION_STOPPED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
