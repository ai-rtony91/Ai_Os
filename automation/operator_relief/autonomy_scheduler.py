"""Scheduling metadata scaffold for Operator Relief autonomy spine v1."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any


@dataclass(frozen=True)
class SchedulePlan:
    mode: str
    next_run_after_utc: str
    max_steps: int
    daemon_started: bool
    service_registered: bool
    background_watcher_started: bool
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def plan_next_run(max_steps: int = 3, interval_minutes: int = 60) -> SchedulePlan:
    next_run = datetime.now(timezone.utc) + timedelta(minutes=interval_minutes)
    return SchedulePlan(
        mode="SCAFFOLD_ONLY",
        next_run_after_utc=next_run.isoformat(),
        max_steps=max_steps,
        daemon_started=False,
        service_registered=False,
        background_watcher_started=False,
        executable=False,
    )
