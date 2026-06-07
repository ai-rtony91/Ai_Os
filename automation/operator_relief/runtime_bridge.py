"""One-shot runtime bridge for Operator Relief v1."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .inbox_outbox_bridge import INBOX_ROOT, OUTBOX_ROOT, run_inbox_outbox_bridge
from .repo_state import collect_repo_state


ARCHIVE_ROOT = Path("reports/operator_relief/archive/processed")
PIPELINE_STAGES = (
    "task_discovery",
    "policy_evaluation",
    "approval_processing",
    "validator_planning",
    "bounded_executor",
    "write_enabled_safe_executor",
    "outbox_result",
)


@dataclass(frozen=True)
class RuntimeBridgeReport:
    status: str
    selected_inbox_path: str | None
    outbox_path: str | None
    archive_path: str | None
    bridge_report: dict[str, Any] | None
    pipeline: list[str]
    processed_count: int
    reasons: list[str]
    safety: dict[str, bool]
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _safety(outbox_written: bool = False, inbox_archived: bool = False) -> dict[str, bool]:
    return {
        "outbox_json_written": outbox_written,
        "inbox_task_archived": inbox_archived,
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


def _resolve_inside(repo_root: Path, root_path: Path, candidate_path: str | Path, label: str) -> Path:
    root = repo_root.resolve()
    allowed_root = (root / root_path).resolve()
    raw_candidate = Path(candidate_path)
    candidate = raw_candidate if raw_candidate.is_absolute() else root / raw_candidate
    resolved = candidate.resolve()
    if not (resolved == allowed_root or allowed_root in resolved.parents):
        raise ValueError(f"{label} path must stay inside {root_path.as_posix()}/.")
    return resolved


def _oldest_inbox_task(repo_root: Path) -> Path | None:
    inbox_root = (repo_root.resolve() / INBOX_ROOT).resolve()
    if not inbox_root.exists():
        return None
    candidates = [path for path in inbox_root.glob("*.json") if path.is_file()]
    if not candidates:
        return None
    return sorted(candidates, key=lambda path: (path.stat().st_mtime, path.name))[0].resolve()


def _default_outbox_path(repo_root: Path, inbox_path: Path) -> Path:
    return (repo_root.resolve() / OUTBOX_ROOT / f"{inbox_path.stem}.result.json").resolve()


def _archive_inbox_task(repo_root: Path, inbox_path: Path) -> Path:
    archive_root = (repo_root.resolve() / ARCHIVE_ROOT).resolve()
    archive_root.mkdir(parents=True, exist_ok=True)
    archive_path = archive_root / f"{inbox_path.stem}.processed.json"
    if archive_path.exists():
        raise FileExistsError("Archive target already exists and overwrite is not allowed.")
    inbox_path.replace(archive_path)
    return archive_path.resolve()


def _bounded_status(bridge_report: dict[str, Any] | None) -> str | None:
    if not bridge_report:
        return None
    executor = bridge_report.get("executor_report") or {}
    bounded = executor.get("bounded_executor") or {}
    return bounded.get("status")


def _runtime_status(bridge_report: dict[str, Any]) -> str:
    bounded_status = _bounded_status(bridge_report)
    if bounded_status == "DRY_RUN_COMPLETE":
        return "RUNTIME_COMPLETE"
    if bounded_status == "STOPPED_BLOCKED":
        return "RUNTIME_BLOCKED_REPORTED"
    if bounded_status == "STOPPED_APPROVAL_REQUIRED":
        return "RUNTIME_APPROVAL_REQUIRED_REPORTED"
    if bounded_status == "STOPPED_UNSUPPORTED_VALIDATOR":
        return "RUNTIME_UNSUPPORTED_VALIDATOR_REPORTED"
    if bounded_status == "STOPPED_VALIDATOR_FAILED":
        return "RUNTIME_VALIDATOR_FAILED_REPORTED"
    return "RUNTIME_BLOCKED"


def run_runtime_bridge(
    repo_root: Path,
    inbox_task_path: str | Path | None = None,
    repo_state: Any | None = None,
) -> RuntimeBridgeReport:
    root = repo_root.resolve()

    try:
        selected = (
            _resolve_inside(root, INBOX_ROOT, inbox_task_path, "Inbox")
            if inbox_task_path is not None
            else _oldest_inbox_task(root)
        )
    except ValueError as exc:
        return RuntimeBridgeReport(
            status="RUNTIME_BLOCKED",
            selected_inbox_path=str(inbox_task_path),
            outbox_path=None,
            archive_path=None,
            bridge_report=None,
            pipeline=list(PIPELINE_STAGES),
            processed_count=0,
            reasons=[str(exc)],
            safety=_safety(),
            executable=False,
        )

    if selected is None:
        return RuntimeBridgeReport(
            status="RUNTIME_NO_TASKS",
            selected_inbox_path=None,
            outbox_path=None,
            archive_path=None,
            bridge_report=None,
            pipeline=list(PIPELINE_STAGES),
            processed_count=0,
            reasons=["No inbox task JSON files found."],
            safety=_safety(),
            executable=False,
        )

    outbox_path = _default_outbox_path(root, selected)
    if outbox_path.exists():
        return RuntimeBridgeReport(
            status="RUNTIME_BLOCKED",
            selected_inbox_path=str(selected),
            outbox_path=str(outbox_path),
            archive_path=None,
            bridge_report=None,
            pipeline=list(PIPELINE_STAGES),
            processed_count=0,
            reasons=["Outbox result already exists and overwrite is not allowed."],
            safety=_safety(),
            executable=False,
        )

    state = repo_state if repo_state is not None else collect_repo_state(root)
    bridge = run_inbox_outbox_bridge(
        root,
        selected,
        outbox_path=outbox_path,
        overwrite=False,
        allow_failure_report=True,
        repo_state=state,
    ).to_dict()

    if bridge["status"] != "BRIDGE_COMPLETE":
        return RuntimeBridgeReport(
            status="RUNTIME_BLOCKED",
            selected_inbox_path=str(selected),
            outbox_path=bridge["outbox_path"],
            archive_path=None,
            bridge_report=bridge,
            pipeline=list(PIPELINE_STAGES),
            processed_count=0,
            reasons=bridge["reasons"],
            safety=_safety(),
            executable=False,
        )

    try:
        archive_path = _archive_inbox_task(root, selected)
    except FileExistsError as exc:
        return RuntimeBridgeReport(
            status="RUNTIME_BLOCKED",
            selected_inbox_path=str(selected),
            outbox_path=bridge["outbox_path"],
            archive_path=None,
            bridge_report=bridge,
            pipeline=list(PIPELINE_STAGES),
            processed_count=0,
            reasons=[str(exc)],
            safety=_safety(outbox_written=True, inbox_archived=False),
            executable=False,
        )

    return RuntimeBridgeReport(
        status=_runtime_status(bridge),
        selected_inbox_path=str(selected),
        outbox_path=bridge["outbox_path"],
        archive_path=str(archive_path),
        bridge_report=bridge,
        pipeline=list(PIPELINE_STAGES),
        processed_count=1,
        reasons=bridge["reasons"],
        safety=_safety(outbox_written=True, inbox_archived=True),
        executable=False,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one Operator Relief runtime bridge task.")
    parser.add_argument("--task-json", default=None, help="Optional task JSON path under reports/operator_relief/inbox/.")
    args = parser.parse_args(argv)

    report = run_runtime_bridge(Path.cwd(), inbox_task_path=args.task_json)
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.processed_count == 1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
