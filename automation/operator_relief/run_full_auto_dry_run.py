"""Non-mutating Full-Auto Runner DRY_RUN v1.

This runner evaluates a FullAutoTask against repo state, builds a non-executing
handoff summary only when policy allows it or requires approval, and returns a
machine-readable report. It does not write repo files, invoke Codex/OpenAI,
commit, push, merge, or recurse into another worker.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .full_auto_handoff import FullAutoHandoffPacket, build_full_auto_handoff
from .full_auto_policy import (
    FULL_AUTO_BLOCKED,
    FULL_AUTO_REQUIRES_APPROVAL,
    FullAutoTask,
    evaluate_full_auto_policy,
)
from .repo_state import RepoState, collect_repo_state


RUNNER_NAME = "full_auto_runner_dry_run_v1"


@dataclass(frozen=True)
class FullAutoDryRunReport:
    runner: str
    mode: str
    task_id: str
    policy: dict[str, Any]
    repo_state: dict[str, Any]
    handoff_summary: dict[str, Any] | None
    approval_needed: bool
    blocked: bool
    final_status: str
    safety: dict[str, bool]
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _handoff_summary(handoff: FullAutoHandoffPacket) -> dict[str, Any]:
    return {
        "task_id": handoff.task_id,
        "mode": handoff.mode,
        "lane": handoff.lane,
        "worktree": handoff.worktree,
        "branch": handoff.branch,
        "allowed_paths": handoff.allowed_paths,
        "forbidden_paths": handoff.forbidden_paths,
        "validator_chain": handoff.validator_chain,
        "stop_condition": handoff.stop_condition,
        "evidence_output_path": handoff.evidence_output_path,
        "notification_triggers": handoff.notification_triggers,
        "human_review_required": handoff.human_review_required,
        "executable": False,
    }


def run_full_auto_dry_run(task: FullAutoTask, repo_state: RepoState | Any) -> FullAutoDryRunReport:
    decision = evaluate_full_auto_policy(task, repo_state)
    handoff = None

    if decision.status != FULL_AUTO_BLOCKED:
        handoff = build_full_auto_handoff(task, decision, repo_state)

    repo_state_dict = repo_state.to_dict() if hasattr(repo_state, "to_dict") else dict(vars(repo_state))
    final_status = "DRY_RUN_BLOCKED" if decision.blocked else "DRY_RUN_REQUIRES_APPROVAL" if decision.requires_approval else "DRY_RUN_READY"

    return FullAutoDryRunReport(
        runner=RUNNER_NAME,
        mode="DRY_RUN",
        task_id=task.task_id,
        policy=decision.to_dict(),
        repo_state=repo_state_dict,
        handoff_summary=_handoff_summary(handoff) if handoff else None,
        approval_needed=decision.status == FULL_AUTO_REQUIRES_APPROVAL,
        blocked=decision.blocked,
        final_status=final_status,
        safety={
            "repo_files_written": False,
            "approval_files_written": False,
            "telemetry_files_written": False,
            "codex_invoked": False,
            "openai_api_invoked": False,
            "commit_attempted": False,
            "push_attempted": False,
            "merge_attempted": False,
            "recursive_worker_invoked": False,
        },
        executable=False,
    )


def _load_task(path: Path | None) -> FullAutoTask:
    raw = sys.stdin.read() if path is None else path.read_text(encoding="utf-8")
    return FullAutoTask(**json.loads(raw))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Full-Auto Runner DRY_RUN v1 without mutating repo files.")
    parser.add_argument(
        "--task-json",
        type=Path,
        help="Path to a JSON FullAutoTask payload. If omitted, JSON is read from stdin.",
    )
    parser.add_argument("--repo-root", type=Path, default=None, help="Repository root for read-only state collection.")
    args = parser.parse_args(argv)

    task = _load_task(args.task_json)
    repo_state = collect_repo_state(args.repo_root)
    report = run_full_auto_dry_run(task, repo_state)
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
