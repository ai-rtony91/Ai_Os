from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from ..database import session_scope
from ..execution.paper_broker import create_paper_order_from_signal
from ..models import Signal
from .traderspost_parser import parse_traderspost_payload
from .tradingview_parser import parse_tradingview_payload


app = FastAPI(title="AI_OS Trading Lab Paper Webhooks")


def extract_regime_status(payload: dict[str, Any]) -> str:
    value = payload.get("regime_status") or payload.get("regime") or "UNKNOWN"
    return str(value or "UNKNOWN")


def extract_evidence_score(payload: dict[str, Any]) -> float:
    value = payload.get("evidence_score", 0)
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def store_signal(parsed: dict[str, Any]) -> dict[str, Any]:
    payload = parsed["payload"]
    regime_status = extract_regime_status(payload)
    evidence_score = extract_evidence_score(payload)
    with session_scope() as session:
        signal = Signal(
            source=parsed["source"],
            signal_id=parsed.get("signal_id") or None,
            strategy_id=parsed.get("strategy_id"),
            symbol=parsed.get("symbol"),
            timeframe=parsed.get("timeframe"),
            side=parsed.get("side"),
            payload=payload,
            paper_status="paper_received",
            execution_allowed=False,
            regime_status=regime_status,
            evidence_score=evidence_score,
            risk_gate_status="blocked",
            paper_decision="blocked_missing_evidence",
        )
        session.add(signal)
        session.flush()
        paper_result = create_paper_order_from_signal(session, signal)
        return {
            "status": "stored_paper_signal",
            "signal_db_id": signal.id,
            "paper_result": paper_result,
            "live_execution": "BLOCKED",
        }


@app.post("/webhook/tradingview")
def tradingview_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    return store_signal(parse_tradingview_payload(payload))


@app.post("/webhook/traderspost")
def traderspost_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    return store_signal(parse_traderspost_payload(payload))


@app.post("/webhook/generic")
def generic_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    parsed = {
        "source": "generic",
        "signal_id": str(payload.get("signal_id") or payload.get("id") or ""),
        "strategy_id": payload.get("strategy_id"),
        "symbol": payload.get("symbol"),
        "timeframe": payload.get("timeframe"),
        "side": payload.get("side") or payload.get("direction"),
        "payload": payload,
        "paper_status": "paper_received",
        "execution_allowed": False,
    }
    return store_signal(parsed)
