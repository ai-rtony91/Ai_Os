"""Readiness checkpoint ledger for the Forex owner evidence return lane."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


LEDGER_VERSION = "1.0"


@dataclass(frozen=True)
class ReadinessCheckpointEvent:
    stage: str
    status: str
    route: str | None
    blockers: list[str]
    notes: list[str]
    metadata: dict[str, Any]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_notes(notes: list[str]) -> list[str]:
    return [note for note in notes if str(note).strip()]


def build_readiness_checkpoint_ledger(
    packet_id: str,
    *,
    branch: str,
    worktree: str,
    lane: str = "forex_owner_evidence_return_orchestration_v1",
) -> dict[str, Any]:
    return {
        "ledger_version": LEDGER_VERSION,
        "generated_at": _now_iso(),
        "packet_id": packet_id,
        "lane": lane,
        "branch": branch,
        "worktree": worktree,
        "events": [
            {
                "stage": "initialized",
                "status": "STARTED",
                "route": None,
                "blockers": [],
                "notes": ["lane orchestration started"],
                "metadata": {"lane": lane},
                "timestamp": _now_iso(),
            }
        ],
        "event_count": 1,
    }


def append_checkpoint_event(
    ledger: Mapping[str, Any],
    stage: str,
    status: str,
    *,
    route: str | None = None,
    blockers: list[str] | None = None,
    notes: list[str] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "stage": str(stage),
        "status": str(status),
        "route": route,
        "blockers": list(blockers or []),
        "notes": _clean_notes(list(notes or [])),
        "metadata": dict(metadata or {}),
        "timestamp": _now_iso(),
    }
    result = deepcopy(dict(ledger))
    events = list(result.get("events", []))
    events.append(event)
    result["events"] = events
    result["event_count"] = len(events)
    result["generated_at"] = _now_iso()
    return result


def latest_checkpoint_event(ledger: Mapping[str, Any]) -> ReadinessCheckpointEvent | None:
    events = list(ledger.get("events", []))
    if not events:
        return None
    latest = events[-1]
    if not isinstance(latest, Mapping):
        return None
    return ReadinessCheckpointEvent(
        stage=str(latest.get("stage", "unknown")),
        status=str(latest.get("status", "unknown")),
        route=latest.get("route"),
        blockers=list(latest.get("blockers", [])),
        notes=list(latest.get("notes", [])),
        metadata=dict(latest.get("metadata", {})),
    )


def ledger_to_markdown(ledger: Mapping[str, Any]) -> str:
    lines = [
        "# Forex Owner Evidence Return Readiness Ledger V1",
        f"Generated: {ledger.get('generated_at')}",
        f"Packet: {ledger.get('packet_id')}",
        f"Lane: {ledger.get('lane')}",
        f"Branch: {ledger.get('branch')}",
        f"Worktree: {ledger.get('worktree')}",
        f"Event count: {ledger.get('event_count', 0)}",
        "",
        "## Events",
    ]
    for event in ledger.get("events", []):
        if not isinstance(event, Mapping):
            continue
        lines.append(f"- {event.get('timestamp')} | {event.get('stage')} | {event.get('status')}")
        if event.get("route"):
            lines.append(f"  - route: {event.get('route')}")
        if event.get("blockers"):
            lines.append("  - blockers:")
            for blocker in event.get("blockers", []):
                lines.append(f"    - {blocker}")
        if event.get("notes"):
            lines.append("  - notes:")
            for note in event.get("notes", []):
                lines.append(f"    - {note}")
    return "\n".join(lines)


def ledger_to_jsonable_dict(ledger: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ledger_version": ledger.get("ledger_version", LEDGER_VERSION),
        "generated_at": ledger.get("generated_at"),
        "packet_id": ledger.get("packet_id"),
        "lane": ledger.get("lane"),
        "branch": ledger.get("branch"),
        "worktree": ledger.get("worktree"),
        "event_count": int(ledger.get("event_count", 0)),
        "events": list(ledger.get("events", [])),
    }


__all__ = [
    "LEDGER_VERSION",
    "ReadinessCheckpointEvent",
    "append_checkpoint_event",
    "build_readiness_checkpoint_ledger",
    "ledger_to_jsonable_dict",
    "ledger_to_markdown",
    "latest_checkpoint_event",
]
