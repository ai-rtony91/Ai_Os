"""Bounded commit and push executor for Operator Relief v1."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from .full_auto_policy import BLOCKED_PATH_KEYWORDS, FullAutoTask
from .task_classifier import PROTECTED_PATH_PREFIXES


FEATURE_BRANCH = "feature/full-operator-relief-closed-loop-v1"
FEATURE_UPSTREAM = f"origin/{FEATURE_BRANCH}"
MODE_DRY_RUN = "DRY_RUN"
MODE_APPLY_COMMIT_PUSH = "APPLY_COMMIT_PUSH"
ALLOWED_MODES = {MODE_DRY_RUN, MODE_APPLY_COMMIT_PUSH}


@dataclass(frozen=True)
class GitCommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AutoCommitPushReport:
    task_id: str
    mode: str
    status: str
    approved_files: list[str]
    dirty_files: list[str]
    commands: list[list[str]]
    command_results: list[dict[str, Any]]
    commit_message: str
    push_target: str
    reasons: list[str]
    safety: dict[str, bool]
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


CommandRunner = Callable[[Path, list[str]], GitCommandResult]


def _safety(commit_executed: bool = False, push_executed: bool = False) -> dict[str, bool]:
    return {
        "exact_files_staged": commit_executed,
        "commit_executed": commit_executed,
        "push_executed": push_executed,
        "merge_executed": False,
        "rebase_executed": False,
        "force_push_executed": False,
        "main_branch_push": False,
        "tag_push": False,
        "broad_add_used": False,
        "shell_passthrough_used": False,
        "openai_api_invoked": False,
        "codex_invoked": False,
    }


def _run_git(repo_root: Path, command: list[str]) -> GitCommandResult:
    result = subprocess.run(
        command,
        cwd=repo_root,
        capture_output=True,
        text=True,
        shell=False,
        check=False,
    )
    return GitCommandResult(command, result.returncode, result.stdout, result.stderr, executable=False)


def _normalize(path_text: str) -> str:
    return Path(path_text).as_posix().lstrip("./")


def _path_matches(path_text: str, pattern: str) -> bool:
    path = _normalize(path_text)
    prefix = _normalize(pattern).rstrip("/")
    if prefix.endswith("**"):
        prefix = prefix[:-2].rstrip("/")
    return path == prefix or path.startswith(prefix + "/")


def _inside_any(path_text: str, patterns: list[str]) -> bool:
    return any(_path_matches(path_text, pattern) for pattern in patterns)


def _touches_protected(path_text: str) -> bool:
    return any(_path_matches(path_text, prefix) for prefix in PROTECTED_PATH_PREFIXES)


def _touches_blocked_keyword(path_text: str) -> bool:
    normalized = _normalize(path_text).lower()
    return any(keyword in normalized for keyword in BLOCKED_PATH_KEYWORDS)


def _dirty_files_from_status(git_status: str) -> list[str]:
    dirty: list[str] = []
    for line in git_status.splitlines():
        if not line.strip() or line.startswith("##"):
            continue
        if " -> " in line:
            dirty.append(line.split(" -> ", 1)[1].strip())
            continue
        dirty.append(line[3:].strip())
    return sorted({_normalize(path) for path in dirty if path})


def _upstream_matches(git_status: str) -> bool:
    first_line = next((line.strip() for line in git_status.splitlines() if line.startswith("##")), "")
    return first_line.startswith(f"## {FEATURE_BRANCH}...{FEATURE_UPSTREAM}")


def _generated_commit_message(task: FullAutoTask) -> str:
    safe_task_id = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in task.task_id).strip("-")
    return f"operator relief: {safe_task_id or 'approved-task'}"


def _commands(approved_files: list[str], commit_message: str) -> list[list[str]]:
    return [
        ["git", "add", "--", *approved_files],
        ["git", "commit", "-m", commit_message],
        ["git", "push", "origin", FEATURE_BRANCH],
    ]


def _gate_reasons(task: FullAutoTask, repo_state: Any, validators_passed: bool, dirty_files: list[str]) -> list[str]:
    reasons: list[str] = []
    approved = sorted({_normalize(path) for path in task.changed_paths})
    branch = getattr(repo_state, "branch", "")
    git_status = getattr(repo_state, "git_status", "")

    if not validators_passed:
        reasons.append("Validators must pass before commit and push can run.")
    if branch != FEATURE_BRANCH:
        reasons.append(f"Branch must be {FEATURE_BRANCH}.")
    if not _upstream_matches(git_status):
        reasons.append(f"Upstream must be {FEATURE_UPSTREAM}.")
    if sorted(dirty_files) != approved:
        reasons.append("Dirty files must exactly match approved changed paths.")
    for path in approved:
        if not _inside_any(path, task.allowed_paths):
            reasons.append(f"Changed file is outside allowed paths: {path}")
        if _inside_any(path, task.forbidden_paths):
            reasons.append(f"Changed file overlaps forbidden paths: {path}")
        if _touches_protected(path):
            reasons.append(f"Protected path is blocked: {path}")
        if _touches_blocked_keyword(path):
            reasons.append(f"Secret, broker/API, or live-trading path is blocked: {path}")
    if task.live_trading or task.secrets or task.broker_api:
        reasons.append("Live trading, secrets, and broker/API tasks are blocked.")
    blocked_actions = {"merge", "rebase", "force_push"}
    if any(action in blocked_actions for action in task.requested_actions):
        reasons.append("Merge, rebase, and force-push actions are blocked.")
    return reasons


def run_auto_commit_push_executor(
    task: FullAutoTask,
    repo_state: Any,
    repo_root: Path,
    validators_passed: bool,
    mode: str = MODE_DRY_RUN,
    command_runner: CommandRunner | None = None,
) -> AutoCommitPushReport:
    if mode not in ALLOWED_MODES:
        raise ValueError("Mode must be DRY_RUN or APPLY_COMMIT_PUSH.")

    approved_files = sorted({_normalize(path) for path in task.changed_paths})
    dirty_files = _dirty_files_from_status(getattr(repo_state, "git_status", ""))
    commit_message = _generated_commit_message(task)
    commands = _commands(approved_files, commit_message)
    push_target = FEATURE_UPSTREAM
    reasons = _gate_reasons(task, repo_state, validators_passed, dirty_files)

    if reasons:
        return AutoCommitPushReport(
            task_id=task.task_id,
            mode=mode,
            status="BLOCKED",
            approved_files=approved_files,
            dirty_files=dirty_files,
            commands=commands if mode == MODE_DRY_RUN else [],
            command_results=[],
            commit_message=commit_message,
            push_target=push_target,
            reasons=reasons,
            safety=_safety(),
            executable=False,
        )

    if mode == MODE_DRY_RUN:
        return AutoCommitPushReport(
            task_id=task.task_id,
            mode=mode,
            status="DRY_RUN_RECOMMENDED",
            approved_files=approved_files,
            dirty_files=dirty_files,
            commands=commands,
            command_results=[],
            commit_message=commit_message,
            push_target=push_target,
            reasons=["Commit and push are eligible; no commands were executed in DRY_RUN."],
            safety=_safety(),
            executable=False,
        )

    runner = command_runner or _run_git
    results: list[GitCommandResult] = []
    for command in commands:
        result = runner(repo_root.resolve(), command)
        results.append(result)
        if result.returncode != 0:
            return AutoCommitPushReport(
                task_id=task.task_id,
                mode=mode,
                status="APPLY_FAILED",
                approved_files=approved_files,
                dirty_files=dirty_files,
                commands=commands,
                command_results=[item.to_dict() for item in results],
                commit_message=commit_message,
                push_target=push_target,
                reasons=[f"Command failed: {' '.join(command)}"],
                safety=_safety(
                    commit_executed=any(item.command[:2] == ["git", "commit"] and item.returncode == 0 for item in results),
                    push_executed=False,
                ),
                executable=False,
            )

    return AutoCommitPushReport(
        task_id=task.task_id,
        mode=mode,
        status="APPLY_COMMIT_PUSH_COMPLETE",
        approved_files=approved_files,
        dirty_files=dirty_files,
        commands=commands,
        command_results=[item.to_dict() for item in results],
        commit_message=commit_message,
        push_target=push_target,
        reasons=[],
        safety=_safety(commit_executed=True, push_executed=True),
        executable=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate Operator Relief Auto Commit Push Executor v1.")
    parser.add_argument("--task-json", required=True, help="FullAutoTask JSON file.")
    parser.add_argument("--mode", choices=sorted(ALLOWED_MODES), default=MODE_DRY_RUN)
    parser.add_argument("--validators-passed", action="store_true")
    args = parser.parse_args(argv)

    payload = json.loads(Path(args.task_json).read_text(encoding="utf-8"))
    task = FullAutoTask(**payload)
    from .repo_state import collect_repo_state

    report = run_auto_commit_push_executor(
        task,
        collect_repo_state(Path.cwd()),
        Path.cwd(),
        validators_passed=args.validators_passed,
        mode=args.mode,
    )
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.status in {"DRY_RUN_RECOMMENDED", "APPLY_COMMIT_PUSH_COMPLETE"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
