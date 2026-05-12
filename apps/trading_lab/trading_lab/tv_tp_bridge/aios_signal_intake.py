from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def normalize_tradingview_payload(payload: dict[str, Any], *, received_time: str | None = None) -> dict[str, Any]:
    """Normalize a TradingView-style payload into the AI_OS paper signal shape."""
    pair = payload.get("pair") or payload.get("symbol")
    alert_time = payload.get("alert_time")
    received_at = received_time or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    signal_id = f"AIOS_TV_{str(pair or 'UNKNOWN').replace('/', '_')}_{str(alert_time or received_at).replace(':', '').replace('-', '').replace('Z', '')}"

    return {
        "signal_id": signal_id,
        "received_by": "AI_OS",
        "source": payload.get("source", "TradingView"),
        "pair": pair,
        "timeframe": payload.get("timeframe"),
        "direction": str(payload.get("direction", "")).upper(),
        "signal_type": payload.get("signal_type"),
        "source_alert_time": alert_time,
        "aios_received_time": received_at,
        "paper_only": payload.get("risk_mode") == "paper_only",
        "live_execution_allowed": False,
    }
