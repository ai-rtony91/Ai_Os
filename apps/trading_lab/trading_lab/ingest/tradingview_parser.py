from __future__ import annotations

from datetime import datetime
from typing import Any


def parse_tradingview_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": "tradingview",
        "signal_id": str(payload.get("signal_id") or payload.get("id") or ""),
        "strategy_id": payload.get("strategy_id") or payload.get("strategy"),
        "symbol": payload.get("symbol") or payload.get("ticker") or payload.get("pair"),
        "timeframe": payload.get("timeframe") or payload.get("interval"),
        "side": payload.get("side") or payload.get("action") or payload.get("direction"),
        "payload": payload,
        "paper_status": "paper_received",
        "execution_allowed": False,
        "received_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
