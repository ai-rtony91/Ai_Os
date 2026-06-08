"""Approval resume loop for Operator Relief.

This module consumes a bounded local approval decision, verifies it against an
approval-required outbox report and archived inbox task, then requeues the task
with resume metadata. It does not execute Codex, notify, commit, push, merge, or
mutate approval files.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .approval_station import APPROVAL_INPUT_ROOT, read_approval_decision
from .inbox_outbox_bridge import INBOX_ROOT, OUTBOX_ROOT
from .runtime_bridge import ARCHIVE_ROOT


RESUME_ROOT = Path("reports/operator_relief/resume")
APPROVE_DECISIONS = {"APPROVE", "CONTINUE_MISSION"}
STOP_DECISIONS = {"REJECT", "HOLD"}


@dataclass(frozen=True)
class ApprovalResumeReport:
    status: str
    decision_path: str
    task_id: str | None
    outbox_path: str | None
    archive_path: str | None
    resume_inbox_path: str | None
    resume_report_path: str | None
    reasons: list[str]
    safety: dict[str, bool]
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _safety(resume_task_written: bool = False, resume_report_written: bool = False) -> dict[str, bool]:
    return {
        "resume_task_written": resume_task_written,
        "resume_report_written": resume_report_written,
        "approval_files_mutated": False,
        "telemetry_jsonl_written": False,
        "source_files_mutated": False,
        "codex_invoked": False,
        "openai_api_invoked": False,
        "adb_sos_sent": False,
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


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed {label} JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} payload must be a JSON object.")
    return payload


def _bounded_executor_payload(outbox_payload: dict[str, Any]) -> dict[str, Any]:
    bounded = outbox_payload.get("bounded_executor")
    if isinstance(bounded, dict):
        return bounded
    bridge = outbox_payload.get("bridge_report")
    if isinstance(bridge, dict):
        executor = bridge.get("executor_report")
        if isinstance(executor, dict) and isinstance(executor.get("bounded_executor"), dict):
            return executor["bounded_executor"]
    raise ValueError("Outbox report does not contain bounded executor evidence.")


def _approval_is_expired(decision_payload: dict[str, Any]) -> bool:
    expires_at = decision_payload.get("expires_at")
    if not isinstance(expires_at, str) or not expires_at.strip():
        return False
    try:
        parsed = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except ValueError:
        return True
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc) <= datetime.now(timezone.utc)


def _with_resume_metadata(
    task_payload: dict[str, Any],
    decision_payload: dict[str, Any],
    decision_path: Path,
    outbox_path: Path,
    archive_path: Path,
) -> dict[str, Any]:
    metadata = task_payload.get("metadata") if isinstance(task_payload.get("metadata"), dict) else {}
    metadata = dict(metadata)
    metadata["approval_resume"] = {
        "human_approved": True,
        "decision": decision_payload["decision"],
        "task_id": task_payload["task_id"],
        "approval_path": decision_path.as_posix(),
        "source_outbox_path": outbox_path.as_posix(),
        "source_archive_path": archive_path.as_posix(),
        "validator_pass_is_not_approval": True,
    }
    updated = dict(task_payload)
    updated["metadata"] = metadata
    return updated


def run_approval_resume_loop(
    repo_root: Path,
    decision_path: str | Path,
    overwrite: bool = False,
) -> ApprovalResumeReport:
    root = repo_root.resolve()
    station = read_approval_decision(root, decision_path)
    if station.status != "APPROVAL_DECISION_ACCEPTED":
        return ApprovalResumeReport(
            status="RESUME_BLOCKED",
            decision_path=station.approval_path,
            task_id=station.task_id,
            outbox_path=None,
            archive_path=None,
            resume_inbox_path=None,
            resume_report_path=None,
            reasons=station.reasons,
            safety=_safety(),
            executable=False,
        )

    try:
        resolved_decision = _resolve_inside(root, APPROVAL_INPUT_ROOT, decision_path, "Approval decision")
        decision_payload = _load_json(resolved_decision, "approval decision")
    except ValueError as exc:
        return ApprovalResumeReport(
            status="RESUME_BLOCKED",
            decision_path=str(decision_path),
            task_id=station.task_id,
            outbox_path=None,
            archive_path=None,
            resume_inbox_path=None,
            resume_report_path=None,
            reasons=[str(exc)],
            safety=_safety(),
            executable=False,
        )

    decision = station.decision
    task_id = station.task_id
    if decision in STOP_DECISIONS:
        return ApprovalResumeReport(
            status="RESUME_STOPPED_BY_HUMAN",
            decision_path=str(resolved_decision),
            task_id=task_id,
            outbox_path=None,
            archive_path=None,
            resume_inbox_path=None,
            resume_report_path=None,
            reasons=[f"Human decision {decision} does not resume the task."],
            safety=_safety(),
            executable=False,
        )
    if decision not in APPROVE_DECISIONS:
        return ApprovalResumeReport(
            status="RESUME_BLOCKED",
            decision_path=str(resolved_decision),
            task_id=task_id,
            outbox_path=None,
            archive_path=None,
            resume_inbox_path=None,
            resume_report_path=None,
            reasons=["Approval decision is not a resume decision."],
            safety=_safety(),
            executable=False,
        )
    if not task_id:
        return ApprovalResumeReport(
            status="RESUME_BLOCKED",
            decision_path=str(resolved_decision),
            task_id=None,
            outbox_path=None,
            archive_path=None,
            resume_inbox_path=None,
            resume_report_path=None,
            reasons=["Approval decision must include task_id."],
            safety=_safety(),
            executable=False,
        )
    if decision_payload.get("consumed") is True:
        return ApprovalResumeReport(
            status="RESUME_BLOCKED",
            decision_path=str(resolved_decision),
            task_id=task_id,
            outbox_path=None,
            archive_path=None,
            resume_inbox_path=None,
            resume_report_path=None,
            reasons=["Approval decision is already consumed."],
            safety=_safety(),
            executable=False,
        )
    if _approval_is_expired(decision_payload):
        return ApprovalResumeReport(
            status="RESUME_BLOCKED",
            decision_path=str(resolved_decision),
            task_id=task_id,
            outbox_path=None,
            archive_path=None,
            resume_inbox_path=None,
            resume_report_path=None,
            reasons=["Approval decision is expired or has an invalid expires_at value."],
            safety=_safety(),
            executable=False,
        )

    try:
        outbox_path = _resolve_inside(root, OUTBOX_ROOT, decision_payload["outbox_path"], "Outbox")
        archive_path = _resolve_inside(root, ARCHIVE_ROOT, decision_payload["archive_path"], "Archive")
        outbox_payload = _load_json(outbox_path, "outbox")
        task_payload = _load_json(archive_path, "archived task")
        bounded = _bounded_executor_payload(outbox_payload)
    except KeyError as exc:
        return ApprovalResumeReport(
            status="RESUME_BLOCKED",
            decision_path=str(resolved_decision),
            task_id=task_id,
            outbox_path=None,
            archive_path=None,
            resume_inbox_path=None,
            resume_report_path=None,
            reasons=[f"Approval decision missing required field: {exc.args[0]}"],
            safety=_safety(),
            executable=False,
        )
    except ValueError as exc:
        return ApprovalResumeReport(
            status="RESUME_BLOCKED",
            decision_path=str(resolved_decision),
            task_id=task_id,
            outbox_path=str(decision_payload.get("outbox_path")),
            archive_path=str(decision_payload.get("archive_path")),
            resume_inbox_path=None,
            resume_report_path=None,
            reasons=[str(exc)],
            safety=_safety(),
            executable=False,
        )

    if bounded.get("status") != "STOPPED_APPROVAL_REQUIRED":
        return ApprovalResumeReport(
            status="RESUME_BLOCKED",
            decision_path=str(resolved_decision),
            task_id=task_id,
            outbox_path=str(outbox_path),
            archive_path=str(archive_path),
            resume_inbox_path=None,
            resume_report_path=None,
            reasons=["Outbox report is not stopped at approval-required state."],
            safety=_safety(),
            executable=False,
        )
    if bounded.get("task_id") != task_id or task_payload.get("task_id") != task_id:
        return ApprovalResumeReport(
            status="RESUME_BLOCKED",
            decision_path=str(resolved_decision),
            task_id=task_id,
            outbox_path=str(outbox_path),
            archive_path=str(archive_path),
            resume_inbox_path=None,
            resume_report_path=None,
            reasons=["Approval decision task_id does not match outbox and archive evidence."],
            safety=_safety(),
            executable=False,
        )

    resume_task = _with_resume_metadata(task_payload, decision_payload, resolved_decision, outbox_path, archive_path)
    inbox_path = (root / INBOX_ROOT / f"{task_id}.resume.json").resolve()
    resume_report_path = (root / RESUME_ROOT / f"{task_id}.resume.json").resolve()

    if not overwrite and (inbox_path.exists() or resume_report_path.exists()):
        return ApprovalResumeReport(
            status="RESUME_BLOCKED",
            decision_path=str(resolved_decision),
            task_id=task_id,
            outbox_path=str(outbox_path),
            archive_path=str(archive_path),
            resume_inbox_path=str(inbox_path),
            resume_report_path=str(resume_report_path),
            reasons=["Resume output already exists and overwrite was not explicitly allowed."],
            safety=_safety(),
            executable=False,
        )

    inbox_path.parent.mkdir(parents=True, exist_ok=True)
    resume_report_path.parent.mkdir(parents=True, exist_ok=True)
    inbox_path.write_text(json.dumps(resume_task, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = ApprovalResumeReport(
        status="RESUME_TASK_QUEUED",
        decision_path=str(resolved_decision),
        task_id=task_id,
        outbox_path=str(outbox_path),
        archive_path=str(archive_path),
        resume_inbox_path=str(inbox_path),
        resume_report_path=str(resume_report_path),
        reasons=[],
        safety=_safety(resume_task_written=True, resume_report_written=True),
        executable=False,
    )
    resume_report_path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resume one approval-required Operator Relief task.")
    parser.add_argument("--decision-json", required=True, help="Approval JSON under automation/operator_relief/approval_input/.")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting existing resume outputs.")
    args = parser.parse_args(argv)
    report = run_approval_resume_loop(Path.cwd(), args.decision_json, overwrite=args.overwrite)
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.status == "RESUME_TASK_QUEUED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
