"""AI_OS repo-state evidence bridge.

Generates a deterministic read-only JSON report for the Autonomy Decision
Governor. It runs safe git inspection commands only and mutates nothing except
the declared report output path.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


DEFAULT_OUTPUT = Path("Reports") / "repo_state" / "AIOS_REPO_STATE_LATEST.json"
Runner = Callable[..., subprocess.CompletedProcess[str]]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _completed(
    *,
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
    args: list[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=args or [], returncode=returncode, stdout=stdout, stderr=stderr)


def _run_git(repo_root: Path, args: list[str], runner: Runner = subprocess.run) -> subprocess.CompletedProcess[str]:
    try:
        return runner(
            ["git", *args],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            shell=False,
            check=False,
            timeout=20,
        )
    except FileNotFoundError:
        return _completed(returncode=127, stderr="git executable not found", args=["git", *args])
    except subprocess.TimeoutExpired:
        return _completed(returncode=124, stderr="git command timed out", args=["git", *args])


def _status_path(line: str) -> str:
    if len(line) < 4 or line.startswith("##"):
        return ""
    path = line[3:].strip()
    if " -> " in path:
        path = path.split(" -> ")[-1].strip()
    return path.replace("\\", "/")


def _parse_ahead_behind(branch_line: str) -> dict[str, Any]:
    ahead = None
    behind = None
    ahead_match = re.search(r"ahead\s+(\d+)", branch_line)
    behind_match = re.search(r"behind\s+(\d+)", branch_line)
    if ahead_match:
        ahead = int(ahead_match.group(1))
    if behind_match:
        behind = int(behind_match.group(1))
    return {"ahead": ahead, "behind": behind, "raw": branch_line}


def _base_report(repo_root: Path, generated_at_utc: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "system": "AI_OS",
        "component": "repo_state_evidence",
        "generated_at_utc": generated_at_utc,
        "repo_root": str(repo_root),
        "branch": "",
        "git_available": False,
        "inside_worktree": False,
        "is_clean": None,
        "status_short": [],
        "tracked_dirty_files": [],
        "untracked_files": [],
        "staged_files": [],
        "ahead_behind": {"ahead": None, "behind": None, "raw": ""},
        "safe_for_apply": False,
        "blocked_reason": "git_unavailable",
        "evidence_quality": "missing",
    }


def collect_repo_state(
    repo_root: str | Path | None = None,
    *,
    generated_at_utc: str | None = None,
    runner: Runner = subprocess.run,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    report = _base_report(root, generated_at_utc or utc_now())

    git_root_result = _run_git(root, ["rev-parse", "--show-toplevel"], runner)
    if git_root_result.returncode == 127:
        return report
    report["git_available"] = True
    if git_root_result.returncode != 0:
        report["blocked_reason"] = "not_inside_git_worktree"
        report["evidence_quality"] = "missing"
        return report

    git_root = Path(git_root_result.stdout.strip()).resolve()
    report["repo_root"] = str(git_root)
    report["inside_worktree"] = True

    branch_result = _run_git(git_root, ["branch", "--show-current"], runner)
    branch = branch_result.stdout.strip() if branch_result.returncode == 0 else ""
    report["branch"] = branch

    status_result = _run_git(git_root, ["status", "--short", "--branch", "--untracked-files=all"], runner)
    if status_result.returncode != 0:
        report["blocked_reason"] = "git_status_failed"
        report["evidence_quality"] = "partial"
        return report

    status_lines = [line.rstrip() for line in status_result.stdout.splitlines() if line.strip()]
    branch_line = next((line for line in status_lines if line.startswith("##")), "")
    file_lines = [line for line in status_lines if not line.startswith("##")]
    tracked_dirty: list[str] = []
    untracked: list[str] = []
    staged: list[str] = []

    for line in file_lines:
        path = _status_path(line)
        if not path:
            continue
        code = line[:2]
        if code == "??":
            untracked.append(path)
            continue
        tracked_dirty.append(path)
        if code[0] not in {" ", "?"}:
            staged.append(path)

    is_clean = len(tracked_dirty) == 0 and len(untracked) == 0 and len(staged) == 0
    branch_known = bool(branch)
    safe_for_apply = bool(report["inside_worktree"] and branch_known and is_clean)

    report.update(
        {
            "status_short": status_lines,
            "tracked_dirty_files": tracked_dirty,
            "untracked_files": untracked,
            "staged_files": staged,
            "ahead_behind": _parse_ahead_behind(branch_line),
            "is_clean": is_clean,
            "safe_for_apply": safe_for_apply,
            "evidence_quality": "strong" if branch_known else "partial",
            "blocked_reason": None,
        }
    )

    if not branch_known:
        report["safe_for_apply"] = False
        report["blocked_reason"] = "branch_unknown"
        report["evidence_quality"] = "partial"
    elif not is_clean:
        report["blocked_reason"] = "dirty_working_tree"

    return report


def write_repo_state_report(
    repo_root: str | Path,
    report: dict[str, Any],
    output_path: str | Path | None = None,
) -> Path:
    root = Path(repo_root).resolve()
    target = Path(output_path) if output_path is not None else root / DEFAULT_OUTPUT
    if not target.is_absolute():
        target = root / target
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(target.parent), prefix=f".{target.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(report, indent=2, sort_keys=True))
            handle.write("\n")
        os.replace(tmp_name, target)
    except Exception:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise
    return target


def main(repo_root: str | Path | None = None, output_path: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    report = collect_repo_state(root)
    write_repo_state_report(root, report, output_path)
    return report


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Emit AI_OS repo-state evidence JSON.")
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--output-path", default=None, help="Optional report output path.")
    args = parser.parse_args()
    report = main(repo_root=args.repo_root, output_path=args.output_path)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
