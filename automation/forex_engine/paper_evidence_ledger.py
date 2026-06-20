"""Deterministic replayable paper evidence ledger."""
from __future__ import annotations

from typing import Any

DEFAULT_TIMESTAMP = "2026-01-01T00:00:00Z"
VALID_EVENT_TYPES = {
    "candidate_created",
    "candidate_rejected",
    "risk_approved",
    "risk_rejected",
    "sizing_created",
    "paper_trade_opened",
    "paper_trade_closed",
    "balance_updated",
    "watchlist_row_created",
    "session_replay_created",
}


def create_ledger(session_id: str = "paper-session-v2") -> dict[str, Any]:
    """Create an empty deterministic paper ledger."""
    return {
        "session_id": session_id,
        "events": [],
        "valid": True,
        "rejection_reasons": [],
        "paper_only": True,
    }


def append_event(
    ledger: dict[str, Any],
    event_type: str,
    payload: dict[str, Any] | None = None,
    timestamp: str = DEFAULT_TIMESTAMP,
) -> dict[str, Any]:
    """Append a replayable event and return a new ledger dictionary."""
    events = [dict(event) for event in ledger.get("events", [])]
    reasons = list(ledger.get("rejection_reasons", []))
    if event_type not in VALID_EVENT_TYPES:
        reasons.append("invalid_event_type")
    event = {
        "event_id": f"evt-{len(events) + 1:04d}",
        "event_type": event_type,
        "timestamp": timestamp,
        "payload": dict(payload or {}),
        "paper_only": True,
    }
    events.append(event)
    return {
        "session_id": ledger.get("session_id", "paper-session-v2"),
        "events": events,
        "valid": not reasons,
        "rejection_reasons": reasons,
        "paper_only": True,
    }


def reconstruct_session_from_events(ledger: dict[str, Any] | list[dict[str, Any]]) -> dict[str, Any]:
    """Reconstruct basic session facts from ledger events."""
    events = ledger if isinstance(ledger, list) else ledger.get("events", [])
    counts: dict[str, int] = {}
    realized_pl = 0.0
    win_count = 0
    loss_count = 0
    for event in events:
        event_type = str(event.get("event_type"))
        counts[event_type] = counts.get(event_type, 0) + 1
        if event_type == "paper_trade_closed":
            pl = float(event.get("payload", {}).get("realized_pl", 0.0))
            realized_pl = round(realized_pl + pl, 8)
            if pl > 0:
                win_count += 1
            if pl < 0:
                loss_count += 1
    return {
        "valid": True,
        "event_count": len(events),
        "counts_by_event_type": counts,
        "candidate_count": counts.get("candidate_created", 0),
        "approved_trade_count": counts.get("risk_approved", 0),
        "rejected_trade_count": counts.get("candidate_rejected", 0) + counts.get("risk_rejected", 0),
        "closed_trade_count": counts.get("paper_trade_closed", 0),
        "win_count": win_count,
        "loss_count": loss_count,
        "realized_pl": realized_pl,
        "paper_only": True,
    }
