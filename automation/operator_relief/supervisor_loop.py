"""One-shot supervisor loop for the CLI-everything closed loop spine."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .approval_resume_loop import run_approval_resume_loop
from .approval_station import APPROVAL_INPUT_ROOT
from .cli_bridge import CliAvailability, build_cli_handoff, discover_cli
from .engine_room_telemetry import build_engine_room_status, write_engine_room_status
from .next_mission_engine import generate_next_mission_queue
from .repo_state import collect_repo_state


@dataclass(frozen=True)
class SupervisorLoopReport:
    status: str
    selected_action: str
    next_safe_action: str
    repo_state: dict[str, Any]
    resume_status: str
    approval_status: str
    notification_status: str
    packet_queue_status: str
    cli_bridge_status: str
    engine_room_status_path: str
    codex_invoked: bool = False
    notification_sent: bool = False
    daemon_started: bool = False
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_pending_approval_count(repo_root: Path) -> int:
    pending_root = repo_root.resolve() / "approval/operator_relief/pending"
    if not pending_root.exists():
        return 0
    return len([path for path in pending_root.glob("*.json") if path.is_file()])


def _approval_decisions(repo_root: Path) -> list[Path]:
    root = repo_root.resolve() / APPROVAL_INPUT_ROOT
    if not root.exists():
        return []
    return sorted([path.resolve() for path in root.glob("*.json") if path.is_file()], key=lambda path: (path.stat().st_mtime, path.name))


def _try_resume(repo_root: Path, decisions: list[Path]) -> dict[str, Any]:
    if not decisions:
        return {"status": "NO_APPROVAL_DECISION", "report": None}
    for decision in decisions:
        report = run_approval_resume_loop(repo_root, decision).to_dict()
        if report["status"] == "RESUME_TASK_QUEUED":
            return {"status": "RESUME_TASK_QUEUED", "report": report}
    return {"status": "RESUME_BLOCKED", "report": report}


def run_supervisor_loop(
    repo_root: Path,
    repo_state: Any | None = None,
    cli: CliAvailability | None = None,
) -> SupervisorLoopReport:
    root = repo_root.resolve()
    state = repo_state or collect_repo_state(root)
    decisions = _approval_decisions(root)
    resume = _try_resume(root, decisions)
    queue = generate_next_mission_queue(root)

    first_candidate = queue.candidates[0] if queue.candidates else {}
    prompt_text = json.dumps(first_candidate, indent=2, sort_keys=True)
    cli_handoff = build_cli_handoff(
        task_id=str(first_candidate.get("packet_id", "no-candidate")),
        prompt_text=prompt_text,
        repo_root=root,
        cli=cli or discover_cli(),
        write_evidence=False,
    )

    pending_count = _read_pending_approval_count(root)
    approval_status = "APPROVAL_PENDING" if pending_count else "APPROVAL_CLEAR"
    notification_status = "NOTIFICATION_NOT_SENT"

    if resume["status"] == "RESUME_TASK_QUEUED":
        selected_action = "APPROVAL_RESUME"
        next_safe_action = "Run the runtime bridge on the queued resume task."
        active_task = str(resume["report"].get("task_id"))
    elif queue.status == "PACKET_QUEUE_READY":
        selected_action = "PACKET_QUEUE_READY"
        next_safe_action = "Review the top packet candidate or approve a bounded CLI handoff."
        active_task = str(first_candidate.get("title", "packet queue"))
    else:
        selected_action = "BLOCKED"
        next_safe_action = "Review packet queue blocker evidence."
        active_task = "blocked"
        approval_status = "APPROVAL_NEEDED"

    status = build_engine_room_status(
        repo_state=state,
        active_mission="CLI Everything Closed Loop Spine v1",
        active_worker_lane="CLI_EVERYTHING_CLOSED_LOOP_SPINE",
        active_task=active_task,
        current_action=selected_action,
        files_in_focus=[
            "automation/operator_relief/supervisor_loop.py",
            "automation/operator_relief/cli_bridge.py",
            "automation/operator_relief/packet_queue.py",
            "automation/operator_relief/engine_room_telemetry.py",
        ],
        validator_status="VALIDATOR_NOT_RUN_BY_SUPERVISOR",
        approval_status=approval_status,
        resume_status=resume["status"],
        notification_status=notification_status,
        packet_queue_status=queue.status,
        cli_bridge_status=cli_handoff.status,
        next_safe_action=next_safe_action,
    )
    status_path = write_engine_room_status(root, status)

    return SupervisorLoopReport(
        status="SUPERVISOR_LOOP_COMPLETE" if selected_action != "BLOCKED" else "SUPERVISOR_LOOP_BLOCKED",
        selected_action=selected_action,
        next_safe_action=next_safe_action,
        repo_state=state.to_dict() if hasattr(state, "to_dict") else dict(state),
        resume_status=resume["status"],
        approval_status=approval_status,
        notification_status=notification_status,
        packet_queue_status=queue.status,
        cli_bridge_status=cli_handoff.status,
        engine_room_status_path=str(status_path),
        codex_invoked=False,
        notification_sent=False,
        daemon_started=False,
        executable=False,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one AI_OS Operator Relief supervisor loop.")
    parser.parse_args(argv)
    report = run_supervisor_loop(Path.cwd())
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.status == "SUPERVISOR_LOOP_COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
