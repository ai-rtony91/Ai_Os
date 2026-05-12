from __future__ import annotations


def check_paper_risk(
    symbol: str | None,
    side: str | None,
    quantity: float,
    regime_status: str | None = "UNKNOWN",
    evidence_score: float | int | None = 0.0,
) -> dict:
    if not symbol:
        return {"approved": False, "status": "blocked", "reason": "Missing symbol."}
    if side not in {"long", "short", "buy", "sell"}:
        return {"approved": False, "status": "blocked", "reason": "Missing or invalid side."}
    if quantity <= 0:
        return {"approved": False, "status": "blocked", "reason": "Quantity must be positive."}
    normalized_regime = (regime_status or "UNKNOWN").strip().upper()
    if normalized_regime == "UNKNOWN":
        return {"approved": False, "status": "blocked", "reason": "Regime status is UNKNOWN."}
    score = float(evidence_score or 0.0)
    if score < 70:
        return {"approved": False, "status": "blocked", "reason": "Evidence score is below 70."}
    return {"approved": True, "status": "paper_approved", "reason": "Paper risk gate passed."}
