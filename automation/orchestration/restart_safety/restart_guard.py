from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from automation.orchestration.runtime.atomic_state import (
    CORRUPT_JSON,
    MISSING_JSON,
    read_json_tolerant,
)


BLOCKED_RESTART_MARKER_CORRUPT = "BLOCKED_RESTART_MARKER_CORRUPT"
STALE_RESTART_MARKER = "STALE_RESTART_MARKER"
WAITING_FOR_OPERATOR = "WAITING_FOR_OPERATOR"
APPLY_REPLAY_BLOCKED = "APPLY_REPLAY_BLOCKED"
WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
SAFE_DRY_RUN_ONLY = "SAFE_DRY_RUN_ONLY"
UNKNOWN_RESTART_STATUS_BLOCKED = "UNKNOWN_RESTART_STATUS_BLOCKED"
MISSING_RESTART_MARKER_SAFE = "MISSING_RESTART_MARKER_SAFE"

TERMINAL_DRY_RUN_STATUSES = {"completed_dry_run", "dry_run_complete"}
TERMINAL_APPLY_STATUSES = {"completed_apply", "apply_complete"}
WAITING_STATUSES = {"waiting_for_operator", "blocked", "failed"}
APPROVAL_STATUSES = {"waiting_for_approval", "approval_required"}


@dataclass(frozen=True)
class RestartDecision:
    status: str
    can_resume: bool
    can_apply: bool
    reason: str


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def classify_restart_marker(
    marker_path: Path | str,
    *,
    now: datetime | None = None,
    stale_after_minutes: int = 60,
) -> RestartDecision:
    loaded = read_json_tolerant(marker_path)
    if loaded.status == MISSING_JSON:
        return RestartDecision(MISSING_RESTART_MARKER_SAFE, False, False, "No restart marker exists.")
    if loaded.status == CORRUPT_JSON:
        return RestartDecision(BLOCKED_RESTART_MARKER_CORRUPT, False, False, loaded.error or "Marker JSON is corrupt.")

    marker = loaded.data
    if not isinstance(marker, dict):
        return RestartDecision(BLOCKED_RESTART_MARKER_CORRUPT, False, False, "Marker JSON must be an object.")

    status = str(marker.get("status", "")).lower()
    mode = str(marker.get("mode", "")).upper()
    current = now or datetime.now(timezone.utc)
    updated_at = _parse_timestamp(marker.get("updated_at") or marker.get("created_at"))
    if updated_at and current - updated_at > timedelta(minutes=stale_after_minutes):
        return RestartDecision(STALE_RESTART_MARKER, False, False, "Restart marker is stale.")

    if status in APPROVAL_STATUSES:
        return RestartDecision(WAITING_FOR_APPROVAL, False, False, "Restart is blocked until approval is refreshed.")
    if status in WAITING_STATUSES:
        return RestartDecision(WAITING_FOR_OPERATOR, False, False, "Restart is waiting for operator review.")
    if status in TERMINAL_APPLY_STATUSES or mode == "APPLY":
        return RestartDecision(APPLY_REPLAY_BLOCKED, False, False, "Completed or pending APPLY must not replay by default.")
    if status in TERMINAL_DRY_RUN_STATUSES or mode == "DRY_RUN":
        return RestartDecision(SAFE_DRY_RUN_ONLY, True, False, "Only DRY_RUN resume is allowed.")
    return RestartDecision(UNKNOWN_RESTART_STATUS_BLOCKED, False, False, f"Unknown restart status: {status or '<missing>'}.")
