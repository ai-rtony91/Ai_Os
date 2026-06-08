"""Local run-planning scaffold for Operator Relief night missions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any


@dataclass(frozen=True)
class MissionSchedulePlan:
    mode: str
    interval_minutes: int
    planned_at: str
    next_run_at: str
    max_cycles: int
    registration_required: bool
    task_scheduler_registered: bool
    background_process_started: bool
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def plan_mission_schedule(
    interval_minutes: int = 60,
    max_cycles: int = 3,
    now: datetime | None = None,
) -> MissionSchedulePlan:
    if interval_minutes <= 0:
        raise ValueError("interval_minutes must be greater than zero.")
    if max_cycles <= 0:
        raise ValueError("max_cycles must be greater than zero.")

    base = now or datetime.now(timezone.utc)
    if base.tzinfo is None:
        base = base.replace(tzinfo=timezone.utc)
    next_run = base + timedelta(minutes=interval_minutes)
    return MissionSchedulePlan(
        mode="SCAFFOLD_ONLY",
        interval_minutes=interval_minutes,
        planned_at=base.isoformat(),
        next_run_at=next_run.isoformat(),
        max_cycles=max_cycles,
        registration_required=False,
        task_scheduler_registered=False,
        background_process_started=False,
        executable=False,
    )
