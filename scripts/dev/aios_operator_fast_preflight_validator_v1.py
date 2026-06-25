"""AI_OS operator fast preflight and validator lane.

This script is local-only and read-only. It summarizes repo state and, when
requested, runs a small allowlisted validator set for the Forex loss-review
metrics gate.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence, TextIO


PACKET_ID = "AIOS-DEV-OPERATOR-FAST-PREFLIGHT-VALIDATOR-LANE-LOCAL-APPLY-V1"
MODE = "READ_ONLY_FAST_PREFLIGHT_VALIDATOR"

FOREX_LOSS_GATE_TEST_COMMAND = (
    "python",
    "-m",
    "pytest",
    "tests/forex_engine/test_demo_loss_review_metrics_gate_v1.py",
    "-q",
)
FOREX_LOSS_GATE_COMPILE_COMMAND = (
    "python",
    "-m",
    "py_compile",
    "automation/forex_engine/demo_loss_review_metrics_gate_v1.py",
    "tests/forex_engine/test_demo_loss_review_metrics_gate_v1.py",
)

READ_ONLY_GIT_COMMANDS = (
    ("git", "status", "--short", "--branch"),
    ("git", "branch", "--show-current"),
    ("git", "remote", "-v"),
)

PACKET_ALLOWED_DIRTY_FILES = {
    "scripts/dev/aios_operator_fast_preflight_validator_v1.py",
    "tests/dev/test_aios_operator_fast_preflight_validator_v1.py",
    "Reports/dev/AIOS_OPERATOR_FAST_PREFLIGHT_VALIDATOR_V1_REPORT.md",
}

FORBIDDEN_MUTATION_WORDS = {
    "add",
    "commit",
    "push",
    "merge",
    "rm",
    "clean",
    "reset",
    "stash",
    "checkout",
    "switch",
    "rebase",
    "tag",
    "worktree",
}

OPERATOR_BENEFIT = (
    "Saves Anthony repeated command copying, reduces waiting, gives one clean "
    "continue/stop answer, helps recover faster when Codex shell fails, and "
    "keeps him from babysitting validator steps."
)

SAFETY = {
    "local_only": True,
    "network_used": False,
    "credentials_used": False,
    "repo_mutation_performed": False,
    "broker_calls_allowed": False,
    "order_placement_allowed": False,
    "commit_allowed": False,
    "push_allowed": False,
}


@dataclass(frozen=True)
class CommandResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str = ""
    stderr: str = ""


CommandRunner = Callable[[Sequence[str], Path, int], CommandResult]


def command_plan(run_forex_loss_gate_tests: bool = False) -> list[tuple[str, ...]]:
    """Return the complete allowlisted command plan for this invocation."""

    plan = list(READ_ONLY_GIT_COMMANDS)
    if run_forex_loss_gate_tests:
        plan.append(FOREX_LOSS_GATE_TEST_COMMAND)
        plan.append(FOREX_LOSS_GATE_COMPILE_COMMAND)
    return plan


def evaluate_operator_fast_preflight(
    repo_root: str | Path = ".",
    expected_branch: str = "main",
    run_forex_loss_gate_tests: bool = False,
    command_runner: CommandRunner | None = None,
) -> dict:
    """Collect local repo state and approved validator results."""

    runner = command_runner or _run_command
    root = Path(repo_root).expanduser()
    safety = dict(SAFETY)
    validators_run: list[dict] = []
    validators_failed: list[dict] = []
    command_failures: list[dict] = []
    git_status_lines: list[str] = []
    remote_lines: list[str] = []
    actual_branch = ""
    dirty_files: list[str] = []
    tracking_marker_present = False
    unsafe_git_state = False

    if not root.exists():
        return _result(
            repo_root=root,
            expected_branch=expected_branch,
            actual_branch=actual_branch,
            branch_ok=False,
            git_status=git_status_lines,
            dirty_files=dirty_files,
            remote_summary=remote_lines,
            tracking_marker_present=False,
            unsafe_git_state=False,
            validators_requested=run_forex_loss_gate_tests,
            validators_run=validators_run,
            validators_failed=validators_failed,
            safe_to_continue=False,
            next_safe_action=(
                "Stop: repo root is missing; reopen the correct AIOS folder "
                "before continuing."
            ),
            safety=safety,
            command_failures=command_failures,
        )

    if not (root / ".git").exists():
        return _result(
            repo_root=root,
            expected_branch=expected_branch,
            actual_branch=actual_branch,
            branch_ok=False,
            git_status=git_status_lines,
            dirty_files=dirty_files,
            remote_summary=remote_lines,
            tracking_marker_present=False,
            unsafe_git_state=False,
            validators_requested=run_forex_loss_gate_tests,
            validators_run=validators_run,
            validators_failed=validators_failed,
            safe_to_continue=False,
            next_safe_action=(
                "Stop: this folder is not a git repo; switch to C:\\Dev\\Ai.Os "
                "before continuing."
            ),
            safety=safety,
            command_failures=command_failures,
        )

    status_result = runner(READ_ONLY_GIT_COMMANDS[0], root, 30)
    branch_result = runner(READ_ONLY_GIT_COMMANDS[1], root, 30)
    remote_result = runner(READ_ONLY_GIT_COMMANDS[2], root, 30)

    for result in (status_result, branch_result, remote_result):
        if result.returncode != 0:
            command_failures.append(_command_result_dict(result))

    git_status_lines = _split_output(status_result.stdout)
    actual_branch = branch_result.stdout.strip()
    remote_lines = _split_output(remote_result.stdout)
    dirty_files = _dirty_files_from_status(git_status_lines)
    tracking_marker_present = any(
        line.startswith("##") and "..." in line for line in git_status_lines
    )
    unsafe_git_state = _detect_unsafe_git_state(git_status_lines)
    branch_ok = bool(actual_branch) and actual_branch == expected_branch

    if run_forex_loss_gate_tests:
        for command in (
            FOREX_LOSS_GATE_TEST_COMMAND,
            FOREX_LOSS_GATE_COMPILE_COMMAND,
        ):
            result = runner(command, root, 120)
            result_dict = _command_result_dict(result)
            validators_run.append(result_dict)
            if result.returncode != 0:
                validators_failed.append(result_dict)

    unrelated_dirty = _unrelated_dirty_files(dirty_files)
    validators_passed = not validators_failed
    safe_to_continue = (
        not command_failures
        and branch_ok
        and not unsafe_git_state
        and not unrelated_dirty
        and validators_passed
    )
    next_safe_action = _next_safe_action(
        command_failures=command_failures,
        branch_ok=branch_ok,
        actual_branch=actual_branch,
        expected_branch=expected_branch,
        unsafe_git_state=unsafe_git_state,
        unrelated_dirty=unrelated_dirty,
        validators_failed=validators_failed,
        validators_requested=run_forex_loss_gate_tests,
        safe_to_continue=safe_to_continue,
    )

    return _result(
        repo_root=root,
        expected_branch=expected_branch,
        actual_branch=actual_branch,
        branch_ok=branch_ok,
        git_status=git_status_lines,
        dirty_files=dirty_files,
        remote_summary=remote_lines,
        tracking_marker_present=tracking_marker_present,
        unsafe_git_state=unsafe_git_state,
        validators_requested=run_forex_loss_gate_tests,
        validators_run=validators_run,
        validators_failed=validators_failed,
        safe_to_continue=safe_to_continue,
        next_safe_action=next_safe_action,
        safety=safety,
        command_failures=command_failures,
    )


def main(
    argv: Sequence[str] | None = None,
    command_runner: CommandRunner | None = None,
    stdout: TextIO | None = None,
) -> int:
    parser = argparse.ArgumentParser(
        description="Run the local AI_OS operator fast preflight validator."
    )
    parser.add_argument("--repo-root", default=".", help="Repo root to inspect.")
    parser.add_argument("--branch", default="main", help="Expected branch.")
    parser.add_argument(
        "--run-forex-loss-gate-tests",
        action="store_true",
        help="Run the allowlisted Forex loss-review metrics gate validators.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    args = parser.parse_args(argv)
    out = stdout or sys.stdout

    result = evaluate_operator_fast_preflight(
        repo_root=args.repo_root,
        expected_branch=args.branch,
        run_forex_loss_gate_tests=args.run_forex_loss_gate_tests,
        command_runner=command_runner,
    )
    if args.json:
        json.dump(result, out, indent=2, sort_keys=True)
        out.write("\n")
    else:
        _print_plain(result, out)
    return 0 if result["safe_to_continue"] else 1


def _run_command(command: Sequence[str], cwd: Path, timeout: int) -> CommandResult:
    if tuple(command) not in command_plan(run_forex_loss_gate_tests=True):
        return CommandResult(
            command=tuple(command),
            returncode=2,
            stderr="command is not allowlisted",
        )

    try:
        completed = subprocess.run(
            list(command),
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            shell=False,
        )
        return CommandResult(
            command=tuple(command),
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
    except Exception as exc:
        return CommandResult(command=tuple(command), returncode=1, stderr=str(exc))


def _result(
    *,
    repo_root: Path,
    expected_branch: str,
    actual_branch: str,
    branch_ok: bool,
    git_status: list[str],
    dirty_files: list[str],
    remote_summary: list[str],
    tracking_marker_present: bool,
    unsafe_git_state: bool,
    validators_requested: bool,
    validators_run: list[dict],
    validators_failed: list[dict],
    safe_to_continue: bool,
    next_safe_action: str,
    safety: dict,
    command_failures: list[dict],
) -> dict:
    return {
        "packet_id": PACKET_ID,
        "mode": MODE,
        "repo_root": str(repo_root),
        "expected_branch": expected_branch,
        "actual_branch": actual_branch,
        "branch_ok": branch_ok,
        "git_status": git_status,
        "dirty_files": dirty_files,
        "dirty_count": len(dirty_files),
        "remote_summary": remote_summary,
        "tracking_marker_present": tracking_marker_present,
        "unsafe_git_state": unsafe_git_state,
        "command_failures": command_failures,
        "validators_requested": validators_requested,
        "validators_run": validators_run,
        "validators_passed": not validators_failed,
        "validators_failed": validators_failed,
        "safe_to_continue": safe_to_continue,
        "next_safe_action": next_safe_action,
        "operator_benefit": OPERATOR_BENEFIT,
        "safety": safety,
    }


def _split_output(output: str) -> list[str]:
    return [line.rstrip() for line in output.splitlines() if line.strip()]


def _dirty_files_from_status(status_lines: Iterable[str]) -> list[str]:
    dirty_files: list[str] = []
    for line in status_lines:
        if line.startswith("##") or not line.strip():
            continue
        path = line[3:].strip() if len(line) > 3 else line.strip()
        dirty_files.append(_normalize_git_path(path))
    return dirty_files


def _normalize_git_path(path: str) -> str:
    return path.strip().strip('"').replace("\\", "/")


def _unrelated_dirty_files(dirty_files: Iterable[str]) -> list[str]:
    return [
        path
        for path in dirty_files
        if _normalize_git_path(path) not in PACKET_ALLOWED_DIRTY_FILES
    ]


def _detect_unsafe_git_state(status_lines: Iterable[str]) -> bool:
    conflict_codes = {"UU", "AA", "DD", "DU", "UD", "UA", "AU"}
    state_markers = ("merge", "rebase", "cherry-pick", "bisect")
    for line in status_lines:
        lowered = line.lower()
        if any(marker in lowered for marker in state_markers):
            return True
        if len(line) >= 2 and line[:2] in conflict_codes:
            return True
    return False


def _command_result_dict(result: CommandResult) -> dict:
    return {
        "command": " ".join(result.command),
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def _next_safe_action(
    *,
    command_failures: list[dict],
    branch_ok: bool,
    actual_branch: str,
    expected_branch: str,
    unsafe_git_state: bool,
    unrelated_dirty: list[str],
    validators_failed: list[dict],
    validators_requested: bool,
    safe_to_continue: bool,
) -> str:
    if command_failures:
        return "Stop: one or more read-only repo commands failed; review the command failure before continuing."
    if not branch_ok:
        return (
            f"Stop: expected branch {expected_branch!r} but found "
            f"{actual_branch!r}; do not continue until branch state is resolved."
        )
    if unsafe_git_state:
        return "Stop: git status suggests an unresolved merge, rebase, cherry-pick, or conflict."
    if unrelated_dirty:
        return "Stop: unrelated dirty files exist; review or preserve them before continuing."
    if validators_failed:
        return "Stop: at least one approved validator failed; fix validation before continuing."
    if safe_to_continue and validators_requested:
        return "Safe to continue with local review; protected actions still require explicit approval."
    if safe_to_continue:
        return "Safe to continue with read-only work; run requested validators before any commit packet."
    return "Stop: repo state is not ready for the next protected action."


def _print_plain(result: dict, out: TextIO) -> None:
    out.write("AIOS Operator Fast Preflight Validator V1\n")
    out.write(f"safe_to_continue: {str(result['safe_to_continue']).upper()}\n")
    out.write(f"repo_root: {result['repo_root']}\n")
    out.write(f"expected_branch: {result['expected_branch']}\n")
    out.write(f"actual_branch: {result['actual_branch']}\n")
    out.write(f"branch_ok: {str(result['branch_ok']).upper()}\n")
    out.write(f"dirty_count: {result['dirty_count']}\n")
    if result["dirty_files"]:
        out.write("dirty_files:\n")
        for path in result["dirty_files"]:
            out.write(f"  - {path}\n")
    out.write(
        f"tracking_marker_present: {str(result['tracking_marker_present']).upper()}\n"
    )
    out.write(f"validators_requested: {str(result['validators_requested']).upper()}\n")
    out.write(f"validators_passed: {str(result['validators_passed']).upper()}\n")
    if result["validators_failed"]:
        out.write("validators_failed:\n")
        for failure in result["validators_failed"]:
            out.write(f"  - {failure['command']}\n")
    out.write(f"next_safe_action: {result['next_safe_action']}\n")
    out.write(f"operator_benefit: {result['operator_benefit']}\n")


if __name__ == "__main__":
    raise SystemExit(main())
