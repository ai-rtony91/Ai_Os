"""Inbox/outbox CLI bridge for Operator Relief v1.

The bridge reads one FullAutoTask JSON from reports/operator_relief/inbox/,
runs the write-enabled safe executor, and writes one JSON result under
reports/operator_relief/outbox/. It never mutates source files, telemetry
jsonl, approval queue files, Git state, or external systems.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .autonomy_task_discovery import discover_tasks
from .repo_state import collect_repo_state
from .write_enabled_safe_executor import run_write_enabled_safe_executor


INBOX_ROOT = Path("reports/operator_relief/inbox")
OUTBOX_ROOT = Path("reports/operator_relief/outbox")


@dataclass(frozen=True)
class InboxOutboxBridgeReport:
    status: str
    inbox_path: str
    outbox_path: str | None
    discovery: dict[str, Any] | None
    executor_report: dict[str, Any] | None
    reasons: list[str]
    safety: dict[str, bool]
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _safety() -> dict[str, bool]:
    return {
        "source_files_mutated": False,
        "telemetry_jsonl_written": False,
        "approval_queue_files_written": False,
        "commit_executed": False,
        "push_executed": False,
        "merge_executed": False,
        "openai_api_invoked": False,
        "codex_invoked": False,
        "daemon_started": False,
        "watcher_started": False,
        "service_started": False,
        "executable": False,
    }


def _resolve_inside(repo_root: Path, root_path: Path, candidate_path: str | Path, label: str) -> Path:
    root = repo_root.resolve()
    allowed_root = (root / root_path).resolve()
    raw_candidate = Path(candidate_path)
    candidate = raw_candidate if raw_candidate.is_absolute() else root / raw_candidate
    resolved = candidate.resolve()
    if not (resolved == allowed_root or allowed_root in resolved.parents):
        raise ValueError(f"{label} path must stay inside {root_path.as_posix()}/.")
    return resolved


def _default_outbox_path(repo_root: Path, inbox_path: Path) -> Path:
    stem = inbox_path.stem
    return (repo_root / OUTBOX_ROOT / f"{stem}.result.json").resolve()


def run_inbox_outbox_bridge(
    repo_root: Path,
    inbox_task_path: str | Path,
    outbox_path: str | Path | None = None,
    overwrite: bool = False,
    allow_failure_report: bool = False,
    repo_state: Any | None = None,
) -> InboxOutboxBridgeReport:
    root = repo_root.resolve()
    try:
        inbox_path = _resolve_inside(root, INBOX_ROOT, inbox_task_path, "Inbox")
    except ValueError as exc:
        return InboxOutboxBridgeReport(
            status="BRIDGE_BLOCKED",
            inbox_path=str(inbox_task_path),
            outbox_path=None,
            discovery=None,
            executor_report=None,
            reasons=[str(exc)],
            safety=_safety(),
            executable=False,
        )

    if inbox_path.suffix.lower() != ".json":
        return InboxOutboxBridgeReport(
            status="BRIDGE_BLOCKED",
            inbox_path=str(inbox_path),
            outbox_path=None,
            discovery=None,
            executor_report=None,
            reasons=["Inbox task must be a .json file."],
            safety=_safety(),
            executable=False,
        )

    discovery = discover_tasks(task_file=inbox_path)
    discovery_dict = discovery.to_dict()
    if discovery.status == "BLOCKED" or not discovery.tasks:
        return InboxOutboxBridgeReport(
            status="BRIDGE_BLOCKED",
            inbox_path=str(inbox_path),
            outbox_path=None,
            discovery=discovery_dict,
            executor_report=None,
            reasons=[item["reason"] for item in discovery.rejected],
            safety=_safety(),
            executable=False,
        )

    target_outbox = Path(outbox_path) if outbox_path else _default_outbox_path(root, inbox_path)
    try:
        resolved_outbox = _resolve_inside(root, OUTBOX_ROOT, target_outbox, "Outbox")
    except ValueError as exc:
        return InboxOutboxBridgeReport(
            status="BRIDGE_BLOCKED",
            inbox_path=str(inbox_path),
            outbox_path=str(target_outbox),
            discovery=discovery_dict,
            executor_report=None,
            reasons=[str(exc)],
            safety=_safety(),
            executable=False,
        )

    if resolved_outbox.suffix.lower() != ".json":
        return InboxOutboxBridgeReport(
            status="BRIDGE_BLOCKED",
            inbox_path=str(inbox_path),
            outbox_path=str(resolved_outbox),
            discovery=discovery_dict,
            executor_report=None,
            reasons=["Outbox result must be a .json file."],
            safety=_safety(),
            executable=False,
        )

    state = repo_state if repo_state is not None else collect_repo_state(root)
    executor_report = run_write_enabled_safe_executor(
        discovery.tasks[0].task,
        state,
        root,
        resolved_outbox,
        overwrite=overwrite,
        allow_failure_report=allow_failure_report,
    ).to_dict()

    status = "BRIDGE_COMPLETE" if executor_report["status"] == "WRITE_COMPLETE" else "BRIDGE_BLOCKED"
    return InboxOutboxBridgeReport(
        status=status,
        inbox_path=str(inbox_path),
        outbox_path=str(resolved_outbox),
        discovery=discovery_dict,
        executor_report=executor_report,
        reasons=executor_report["reasons"],
        safety=_safety(),
        executable=False,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one Operator Relief inbox/outbox bridge task.")
    parser.add_argument("--inbox-task", required=True, help="Task JSON path under reports/operator_relief/inbox/.")
    parser.add_argument("--outbox", default=None, help="Optional result JSON path under reports/operator_relief/outbox/.")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing outbox result JSON.")
    parser.add_argument(
        "--allow-failure-report",
        action="store_true",
        help="Allow report-only failure evidence for blocked or approval-required tasks.",
    )
    args = parser.parse_args(argv)
    report = run_inbox_outbox_bridge(
        Path.cwd(),
        args.inbox_task,
        outbox_path=args.outbox,
        overwrite=args.overwrite,
        allow_failure_report=args.allow_failure_report,
    )
    import json

    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.status == "BRIDGE_COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
