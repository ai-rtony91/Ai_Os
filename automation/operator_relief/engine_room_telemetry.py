"""Engine Room telemetry writer for the one-shot Operator Relief spine."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_ENGINE_ROOM_STATUS = Path("telemetry/operator_relief/engine_room/current_status.json")


@dataclass(frozen=True)
class EngineRoomStatus:
    created_at: str
    repo_root: str
    branch: str
    dirty_state: str
    active_mission: str
    active_worker_lane: str
    active_task: str
    current_action: str
    files_in_focus: list[str]
    validator_status: str
    approval_status: str
    resume_status: str
    notification_status: str
    packet_queue_status: str
    cli_bridge_status: str
    next_safe_action: str
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_engine_room_status(
    repo_state: Any,
    active_mission: str,
    active_worker_lane: str,
    active_task: str,
    current_action: str,
    files_in_focus: list[str],
    validator_status: str,
    approval_status: str,
    resume_status: str,
    notification_status: str,
    packet_queue_status: str,
    cli_bridge_status: str,
    next_safe_action: str,
) -> EngineRoomStatus:
    return EngineRoomStatus(
        created_at=datetime.now(timezone.utc).isoformat(),
        repo_root=str(getattr(repo_state, "repo_root", "")),
        branch=str(getattr(repo_state, "branch", "")),
        dirty_state=str(getattr(repo_state, "dirty_state", "")),
        active_mission=active_mission,
        active_worker_lane=active_worker_lane,
        active_task=active_task,
        current_action=current_action,
        files_in_focus=files_in_focus,
        validator_status=validator_status,
        approval_status=approval_status,
        resume_status=resume_status,
        notification_status=notification_status,
        packet_queue_status=packet_queue_status,
        cli_bridge_status=cli_bridge_status,
        next_safe_action=next_safe_action,
        executable=False,
    )


def write_engine_room_status(
    repo_root: Path,
    status: EngineRoomStatus,
    output_path: Path | str = DEFAULT_ENGINE_ROOM_STATUS,
) -> Path:
    path = (repo_root.resolve() / Path(output_path)).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(status.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
