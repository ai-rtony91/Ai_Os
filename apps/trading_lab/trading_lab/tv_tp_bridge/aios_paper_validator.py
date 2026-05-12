from __future__ import annotations

from typing import Any


def validate_aios_paper_signal(signal: dict[str, Any]) -> dict[str, Any]:
    """Validate the normalized AI_OS signal for a blocked paper-route handoff."""
    blocked_reasons: list[str] = []

    if signal.get("paper_only") is not True:
        blocked_reasons.append("paper_only must be true")
    if signal.get("live_execution_allowed") is True:
        blocked_reasons.append("live execution must remain disabled")
    if not signal.get("pair"):
        blocked_reasons.append("pair is required")
    if signal.get("direction") not in {"BUY", "SELL"}:
        blocked_reasons.append("direction must be BUY or SELL")
    if not signal.get("timeframe"):
        blocked_reasons.append("timeframe is required")

    approved = not blocked_reasons
    return {
        "validation_status": "PAPER_ROUTE_READY" if approved else "BLOCKED",
        "approved_for_paper": approved,
        "approved_for_live": False,
        "blocked_reason": "" if approved else "; ".join(blocked_reasons),
        "safety_status": {
            "paper_only": signal.get("paper_only") is True,
            "live_execution": "BLOCKED",
            "broker": "NOT_CONNECTED",
            "webhook": "NOT_SENT",
            "real_orders": "BLOCKED",
        },
    }
