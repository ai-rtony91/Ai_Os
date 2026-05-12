from __future__ import annotations

from typing import Any


def build_traderspost_handoff_payload(signal: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    """Prepare a TradersPost-style payload shape while keeping delivery blocked."""
    direction = signal.get("direction")
    return {
        "destination": "TradersPost_READY_FORMAT_ONLY",
        "action": "buy" if direction == "BUY" else "sell" if direction == "SELL" else "review",
        "ticker": signal.get("pair") or "UNKNOWN",
        "direction": direction or "UNKNOWN",
        "quantity_mode": "paper_placeholder",
        "order_type": "market_placeholder",
        "live_execution_status": "BLOCKED",
        "broker_status": "NOT_CONNECTED",
        "webhook_status": "NOT_SENT",
        "reason": "AI_OS paper validation only",
        "paper_validation_status": validation.get("validation_status", "BLOCKED"),
    }
