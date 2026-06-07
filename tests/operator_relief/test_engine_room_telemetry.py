from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from automation.operator_relief.engine_room_telemetry import build_engine_room_status, write_engine_room_status


@dataclass(frozen=True)
class FakeRepoState:
    repo_root: str
    branch: str = "feature/full-operator-relief-closed-loop-v1"
    dirty_state: str = "CLEAN"


def test_engine_room_telemetry_writes_current_status_json(tmp_path: Path) -> None:
    status = build_engine_room_status(
        repo_state=FakeRepoState(repo_root=str(tmp_path)),
        active_mission="mission",
        active_worker_lane="lane",
        active_task="task",
        current_action="action",
        files_in_focus=["automation/operator_relief/supervisor_loop.py"],
        validator_status="PASS",
        approval_status="APPROVAL_CLEAR",
        resume_status="NO_APPROVAL_DECISION",
        notification_status="NOTIFICATION_NOT_SENT",
        packet_queue_status="PACKET_QUEUE_READY",
        cli_bridge_status="CLI_HANDOFF_READY",
        next_safe_action="Continue.",
    )

    path = write_engine_room_status(tmp_path, status)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert path.name == "current_status.json"
    assert payload["executable"] is False
    assert payload["resume_status"] == "NO_APPROVAL_DECISION"
    assert payload["next_safe_action"] == "Continue."
