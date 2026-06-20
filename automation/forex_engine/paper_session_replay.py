"""Build replay summaries from paper evidence ledgers."""
from __future__ import annotations

from typing import Any


def build_paper_session_replay(
    ledger_or_events: dict[str, Any] | list[dict[str, Any]],
    starting_balance: float | None = None,
    ending_balance: float | None = None,
) -> dict[str, Any]:
    """Summarize paper session events into deterministic replay metrics."""
    events = ledger_or_events if isinstance(ledger_or_events, list) else ledger_or_events.get("events", [])
    counts: dict[str, int] = {}
    realized_pl = 0.0
    win_count = 0
    loss_count = 0
    risk_rejections: list[str] = []
    warnings: list[str] = []

    for event in events:
        event_type = str(event.get("event_type"))
        payload = dict(event.get("payload", {}))
        counts[event_type] = counts.get(event_type, 0) + 1
        if event_type == "paper_trade_closed":
            pl = float(payload.get("realized_pl", 0.0))
            realized_pl = round(realized_pl + pl, 8)
            if pl > 0:
                win_count += 1
            if pl < 0:
                loss_count += 1
        if event_type == "risk_rejected":
            reason = payload.get("reason") or payload.get("rejection_reason")
            if reason:
                risk_rejections.append(str(reason))

    start = float(starting_balance if starting_balance is not None else 0.0)
    end = float(ending_balance if ending_balance is not None else round(start + realized_pl, 8))
    if counts.get("candidate_created", 0) == 0:
        warnings.append("missing_candidate_evidence")
    if counts.get("balance_updated", 0) < counts.get("paper_trade_closed", 0):
        warnings.append("missing_balance_update_evidence")

    return {
        "candidate_count": counts.get("candidate_created", 0),
        "approved_trade_count": counts.get("risk_approved", 0),
        "rejected_trade_count": counts.get("candidate_rejected", 0) + counts.get("risk_rejected", 0),
        "closed_trade_count": counts.get("paper_trade_closed", 0),
        "win_count": win_count,
        "loss_count": loss_count,
        "starting_balance": round(start, 8),
        "ending_balance": round(end, 8),
        "realized_pl": round(realized_pl, 8),
        "drawdown": round(max(0.0, start - end), 8),
        "risk_rejections": risk_rejections,
        "missing_evidence_warnings": warnings,
        "event_count": len(events),
        "counts_by_event_type": counts,
        "paper_only": True,
    }
