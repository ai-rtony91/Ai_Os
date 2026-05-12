from __future__ import annotations

from datetime import datetime
from typing import Any


def parse_traderspost_payload(payload: dict[str, Any]) -> dict[str, Any]:
    order = payload.get("order") if isinstance(payload.get("order"), dict) else {}
    return {
        "source": "traderspost",
        "signal_id": str(payload.get("signal_id") or payload.get("id") or order.get("id") or ""),
        "strategy_id": payload.get("strategy_id") or payload.get("strategy"),
        "symbol": payload.get("symbol") or order.get("symbol"),
        "timeframe": payload.get("timeframe"),
        "side": payload.get("side") or payload.get("action") or order.get("side"),
        "payload": payload,
        "paper_status": "paper_received",
        "execution_allowed": False,
        "received_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
