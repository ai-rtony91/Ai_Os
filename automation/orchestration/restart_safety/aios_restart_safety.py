"""Crash-safe restart marker classification.

This module is pure stdlib and side-effect free except for the explicit atomic
write helper. It exists so restart rules can be tested without starting the
night cycle, scheduler, live SOS, or any worker loop.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_PHASES = [
    "hygiene",
    "clear-stale-approvals",
    "pull-backlog",
    "relay-runner",
    "approval-resume",
    "relay-runner-resume-drain",
    "self-continuation",
    "night-supervisor",
    "autonomy-bridge",
    "morning-brief",
    "sos-file-notifier",
    "pr-watch",
]

APPLY_PHASES = {
    "clear-stale-approvals",
    "pull-backlog",
    "relay-runner",
    "approval-resume",
    "relay-runner-resume-drain",
    "self-continuation",
}


@dataclass(frozen=True)
class RestartDecision:
    status: str
    resume_from: str | None
    cycle_id: str | None
    completed_phases: list[str]
    completed_apply_phases: list[str]
    scheduler_allowed: bool
    live_sos_allowed: bool
    safe_to_start_new_dry_run: bool
    reasons: list[str]
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "resume_from": self.resume_from,
            "cycle_id": self.cycle_id,
            "completed_phases": self.completed_phases,
            "completed_apply_phases": self.completed_apply_phases,
            "scheduler_allowed": self.scheduler_allowed,
            "live_sos_allowed": self.live_sos_allowed,
            "safe_to_start_new_dry_run": self.safe_to_start_new_dry_run,
            "reasons": self.reasons,
            "executable": self.executable,
        }


def _phase_names(marker: dict[str, Any]) -> list[str]:
    phases = marker.get("phases")
    if not isinstance(phases, list):
        return list(DEFAULT_PHASES)
    names: list[str] = []
    for phase in phases:
        if isinstance(phase, dict) and phase.get("name"):
            names.append(str(phase["name"]))
        elif isinstance(phase, str):
            names.append(phase)
    return names or list(DEFAULT_PHASES)


def _completed(marker: dict[str, Any]) -> list[str]:
    completed = marker.get("completed_phases")
    if not isinstance(completed, list):
        return []
    return [str(item) for item in completed if str(item).strip()]


def classify_marker(
    marker: dict[str, Any] | None,
    *,
    marker_exists: bool,
    marker_corrupt: bool = False,
    stale: bool = False,
) -> RestartDecision:
    if marker_corrupt:
        return RestartDecision(
            status="BLOCKED_RESTART_MARKER_CORRUPT",
            resume_from=None,
            cycle_id=None,
            completed_phases=[],
            completed_apply_phases=[],
            scheduler_allowed=False,
            live_sos_allowed=False,
            safe_to_start_new_dry_run=False,
            reasons=["Restart marker is unreadable JSON; fail closed before any APPLY phase can run."],
        )
    if not marker_exists:
        return RestartDecision(
            status="NO_PRIOR_MARKER_SAFE_DRY_RUN_ONLY",
            resume_from=None,
            cycle_id=None,
            completed_phases=[],
            completed_apply_phases=[],
            scheduler_allowed=False,
            live_sos_allowed=False,
            safe_to_start_new_dry_run=True,
            reasons=["No prior marker exists; only default DRY_RUN behavior is safe."],
        )
    if not isinstance(marker, dict):
        return RestartDecision(
            status="BLOCKED_RESTART_MARKER_INVALID",
            resume_from=None,
            cycle_id=None,
            completed_phases=[],
            completed_apply_phases=[],
            scheduler_allowed=False,
            live_sos_allowed=False,
            safe_to_start_new_dry_run=False,
            reasons=["Restart marker parsed but is not an object."],
        )

    cycle_id = str(marker.get("cycle_id") or "UNKNOWN")
    completed = _completed(marker)
    completed_apply = [phase for phase in completed if phase in APPLY_PHASES]
    phase_state = str(marker.get("phase_state") or "")

    if phase_state == "WAITING_FOR_APPROVAL":
        return RestartDecision(
            status="WAITING_FOR_OPERATOR_APPROVAL",
            resume_from=None,
            cycle_id=cycle_id,
            completed_phases=completed,
            completed_apply_phases=completed_apply,
            scheduler_allowed=False,
            live_sos_allowed=False,
            safe_to_start_new_dry_run=False,
            reasons=["Prior cycle is waiting for approval; do not proceed automatically."],
        )

    if bool(marker.get("cycle_in_progress")) is False:
        return RestartDecision(
            status="LAST_CYCLE_COMPLETE_NOTHING_TO_RESUME",
            resume_from=None,
            cycle_id=cycle_id,
            completed_phases=completed,
            completed_apply_phases=completed_apply,
            scheduler_allowed=False,
            live_sos_allowed=False,
            safe_to_start_new_dry_run=True,
            reasons=["Prior cycle is complete; no phase replay is needed."],
        )

    if stale:
        return RestartDecision(
            status="STALE_RUNNING_MARKER_REQUIRES_OPERATOR",
            resume_from=None,
            cycle_id=cycle_id,
            completed_phases=completed,
            completed_apply_phases=completed_apply,
            scheduler_allowed=False,
            live_sos_allowed=False,
            safe_to_start_new_dry_run=False,
            reasons=["Prior cycle is still marked running and stale; require operator/queue decision."],
        )

    phases = _phase_names(marker)
    resume_from = next((phase for phase in phases if phase not in completed), None)
    if resume_from is None:
        return RestartDecision(
            status="IN_PROGRESS_MARKER_ALL_PHASES_COMPLETE",
            resume_from=None,
            cycle_id=cycle_id,
            completed_phases=completed,
            completed_apply_phases=completed_apply,
            scheduler_allowed=False,
            live_sos_allowed=False,
            safe_to_start_new_dry_run=False,
            reasons=["Marker says running but all phases are complete; require review before rewriting state."],
        )

    reasons = [f"Resume from first incomplete phase: {resume_from}."]
    if completed_apply:
        reasons.append("Completed APPLY phases must not be replayed by default: " + ", ".join(completed_apply))
    return RestartDecision(
        status="RESUME_FROM_FIRST_INCOMPLETE_PHASE",
        resume_from=resume_from,
        cycle_id=cycle_id,
        completed_phases=completed,
        completed_apply_phases=completed_apply,
        scheduler_allowed=False,
        live_sos_allowed=False,
        safe_to_start_new_dry_run=False,
        reasons=reasons,
    )


def classify_marker_file(path: Path) -> RestartDecision:
    if not path.exists():
        return classify_marker(None, marker_exists=False)
    try:
        marker = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return classify_marker(None, marker_exists=True, marker_corrupt=True)
    return classify_marker(marker, marker_exists=True)


def atomic_write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    tmp_path = path.with_name(f"{path.name}.{stamp}.tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp_path, path)
    return path

