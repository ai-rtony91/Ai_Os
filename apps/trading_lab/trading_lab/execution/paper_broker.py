from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import Candle, PaperFill, PaperOrder, Signal
from .risk_gate import check_paper_risk


def normalize_side(side: str | None) -> str | None:
    if not side:
        return None
    side = side.lower()
    if side == "buy":
        return "long"
    if side == "sell":
        return "short"
    return side


def create_paper_order_from_signal(session: Session, signal: Signal, quantity: float = 1.0) -> dict:
    side = normalize_side(signal.side)
    regime_status = signal.regime_status or "UNKNOWN"
    evidence_score = float(signal.evidence_score or 0.0)
    risk = check_paper_risk(signal.symbol, side, quantity, regime_status, evidence_score)
    if not risk["approved"]:
        order = PaperOrder(
            signal_id=signal.id,
            symbol=signal.symbol or "",
            timeframe=signal.timeframe or "",
            side=side or "",
            quantity=quantity,
            status="paper_blocked",
            risk_status=risk["status"],
            decision_status="blocked_missing_evidence",
            evidence_score=evidence_score,
            regime_status=regime_status,
            blocked_reason=risk["reason"],
        )
        signal.risk_gate_status = risk["status"]
        signal.paper_decision = "blocked_missing_evidence"
        signal.blocked_reason = risk["reason"]
        session.add(order)
        session.flush()
        return {
            "status": "paper_order_blocked",
            "order_id": order.id,
            "reason": risk["reason"],
            "live_execution": "BLOCKED",
        }

    candle = (
        session.query(Candle)
        .filter(Candle.symbol == signal.symbol, Candle.timeframe == signal.timeframe)
        .order_by(Candle.timestamp.desc())
        .first()
    )
    if not candle:
        reason = "No candle price available."
        order = PaperOrder(
            signal_id=signal.id,
            symbol=signal.symbol or "",
            timeframe=signal.timeframe or "",
            side=side or "",
            quantity=quantity,
            status="paper_blocked",
            risk_status=risk["status"],
            decision_status="blocked_no_price",
            evidence_score=evidence_score,
            regime_status=regime_status,
            blocked_reason=reason,
        )
        signal.risk_gate_status = risk["status"]
        signal.paper_decision = "blocked_no_price"
        signal.blocked_reason = reason
        session.add(order)
        session.flush()
        return {"status": "paper_order_blocked", "order_id": order.id, "reason": reason, "live_execution": "BLOCKED"}

    order = PaperOrder(
        signal_id=signal.id,
        symbol=signal.symbol or "",
        timeframe=signal.timeframe or "",
        side=side or "",
        quantity=quantity,
        status="paper_filled",
        risk_status=risk["status"],
        decision_status="paper_fill_allowed",
        evidence_score=evidence_score,
        regime_status=regime_status,
        blocked_reason=None,
    )
    signal.risk_gate_status = risk["status"]
    signal.paper_decision = "paper_fill_allowed"
    signal.blocked_reason = None
    session.add(order)
    session.flush()
    fill = PaperFill(order_id=order.id, fill_price=float(candle.close), quantity=quantity)
    session.add(fill)
    return {
        "status": "paper_filled",
        "order_id": order.id,
        "fill_price": float(candle.close),
        "live_execution": "BLOCKED",
    }
