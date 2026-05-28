"""Read-only AI_OS clean-state verifier bridge.

Standard library only. Emits JSON to stdout. No file writes, telemetry writes,
network calls, queue mutation, approval mutation, worker launch, commit, push,
merge, broker work, trading work, or live execution.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_PYTHON_CLEAN_STATE_VERIFIER.v1"

DEFAULT_BLOCKED_PREFIXES = (
    "telemetry/",
    "trading/",
    "broker/",
    "OANDA/",
    "secrets/",
    "credentials/",
    "automation/orchestration/terminal_workstations/",
)

DEFAULT_BLOCKED_EXACT = (
    "services/python_supervisor/morning_brief_writer.py",
)


@dataclass
class GitStatusEntry:
    status: str
    path: str
    original_path: str = ""


@dataclass
class CleanStateReport:
    schema: str
    mode: str
    generated_at: str
    repo_root: str
    branch: str = "UNKNOWN"
    dirty: bool = True
    clean: bool = False
    blocked: bool = True
    reason: str = "not_evaluated"
    changed_files: list[str] = field(default_factory=list)
    untracked_files: list[str] = field(default_factory=list)
    blocked_paths: list[str] = field(default_factory=list)
    git_status_line: str = ""
    git_error: str = ""
    blocked_capabilities: list[str] = field(
        default_factory=lambda: [
            "file_writes",
            "telemetry_writes",
            "network_calls",
            "queue_mutation",
            "approval_mutation",
            "worker_launch",
            "commit",
            "push",
            "merge",
            "broker_or_trading_execution",
        ]
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip().strip('"')


def _run_git_status(repo_root: Path) -> tuple[int, str, str]:
    completed = subprocess.run(
        ["git", "status", "--porcelain=v1", "--branch"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def _parse_branch(line: str) -> str:
    if not line.startswith("## "):
        return "UNKNOWN"
    branch_part = line[3:].split("...", maxsplit=1)[0].strip()
    return branch_part or "UNKNOWN"


def _parse_status_line(line: str) -> GitStatusEntry:
    status = line[:2]
    raw_path = line[3:].strip()
    original_path = ""

    if " -> " in raw_path:
        original_path, raw_path = raw_path.split(" -> ", maxsplit=1)

    return GitStatusEntry(
        status=status,
        path=_normalize_path(raw_path),
        original_path=_normalize_path(original_path),
    )


def _is_blocked_path(path: str) -> bool:
    normalized = _normalize_path(path)
    if normalized in DEFAULT_BLOCKED_EXACT:
        return True
    return any(normalized.startswith(prefix) for prefix in DEFAULT_BLOCKED_PREFIXES)


def build_clean_state_report(repo_root: str | Path) -> CleanStateReport:
    resolved_root = Path(repo_root).resolve()
    report = CleanStateReport(
        schema=SCHEMA,
        mode="DRY_RUN",
        generated_at=_utc_now(),
        repo_root=str(resolved_root),
    )

    if not resolved_root.exists() or not resolved_root.is_dir():
        report.reason = "repo_root_missing"
        report.git_error = f"Repository root not found: {resolved_root}"
        return report

    try:
        returncode, stdout, stderr = _run_git_status(resolved_root)
    except Exception as exc:  # noqa: BLE001 - fail-closed JSON evidence
        report.reason = "git_status_exception"
        report.git_error = str(exc)
        return report

    if returncode != 0:
        report.reason = "git_status_failed"
        report.git_error = stderr.strip() or stdout.strip() or f"git status returned {returncode}"
        return report

    entries: list[GitStatusEntry] = []
    for line in stdout.splitlines():
        if line.startswith("## "):
            report.git_status_line = line
            report.branch = _parse_branch(line)
            continue
        if line.strip():
            entries.append(_parse_status_line(line))

    changed_files = sorted({entry.path for entry in entries if entry.status != "??"})
    untracked_files = sorted({entry.path for entry in entries if entry.status == "??"})
    blocked_paths = sorted(
        {
            path
            for path in [*changed_files, *untracked_files]
            if _is_blocked_path(path)
        }
    )

    report.changed_files = changed_files
    report.untracked_files = untracked_files
    report.blocked_paths = blocked_paths
    report.dirty = bool(changed_files or untracked_files)
    report.clean = not report.dirty
    report.blocked = bool(blocked_paths)

    if report.clean:
        report.reason = "working_tree_clean"
    elif report.blocked:
        report.reason = "blocked_paths_present"
    else:
        report.reason = "working_tree_dirty_no_blocked_paths_detected"

    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Emit read-only AI_OS git clean-state evidence.")
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_clean_state_report(args.repo_root)
    print(json.dumps(asdict(report), indent=2 if args.pretty else None, sort_keys=True))
    return 1 if report.git_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
