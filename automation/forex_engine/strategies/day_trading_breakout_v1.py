"""Deterministic paper-only day-trading breakout strategy."""
from __future__ import annotations

import math
from typing import Any

STRATEGY_NAME = "DAY_TRADING_BREAKOUT_V1"
STRATEGY_VERSION = "v1"
MODE = "DAY_TRADING_BREAKOUT_STRATEGY_ONLY"


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "strategy_generation_only": True,
        "broker_access": False,
        "credentials_access": False,
        "network_access": False,
        "live_trading_active": False,
        "demo_execution_active": False,
        "capital_allocation_modified": False,
    }


def _finite_float(value: Any) -> tuple[float, bool]:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return 0.0, False
    if not math.isfinite(result):
        return 0.0, False
    return round(result, 8), True


def _base_result(
    symbol: str,
    session_name: str,
    timeframe: str,
    blocked_reasons: list[str],
) -> dict[str, Any]:
    return {
        "strategy_name": STRATEGY_NAME,
        "strategy_version": STRATEGY_VERSION,
        "symbol": str(symbol or "").upper(),
        "session_name": str(session_name or ""),
        "timeframe": str(timeframe or ""),
        "candidates": [],
        "candidate_count": 0,
        "evidence": {},
        "blocked_reasons": list(dict.fromkeys(blocked_reasons)),
        "next_safe_action": "send_candidates_to_strategy_evaluation" if not blocked_reasons else "wait_for_valid_breakout_input",
        "safety": _safety(),
        "mode": MODE,
    }


def _candidate(
    *,
    symbol: str,
    session_name: str,
    timeframe: str,
    direction: str,
    entry: float,
    stop: float,
    target: float,
    risk_percent: float,
    breakout_range: float,
) -> dict[str, Any]:
    reward_multiple = round(abs(target - entry) / abs(entry - stop), 8)
    # Evaluation harnesses consume realized_pl as deterministic paper outcome evidence.
    realized_pl = round(100.0 * risk_percent * reward_multiple, 8)
    return {
        "trade_id": f"{STRATEGY_NAME.lower()}-{direction}-{symbol.lower()}-{timeframe.lower()}",
        "strategy_name": STRATEGY_NAME,
        "strategy_version": STRATEGY_VERSION,
        "symbol": symbol,
        "session_name": session_name,
        "timeframe": timeframe,
        "direction": direction,
        "entry": round(entry, 8),
        "stop": round(stop, 8),
        "target": round(target, 8),
        "risk_percent": round(risk_percent, 8),
        "spread": 0.0001,
        "realized_pl": realized_pl,
        "breakout_range": round(breakout_range, 8),
        "paper_only": True,
    }


def generate_day_trading_breakout_candidates(
    *,
    symbol: str,
    session_name: str,
    timeframe: str,
    high_price: Any,
    low_price: Any,
    current_price: Any,
    risk_percent: Any,
) -> dict[str, Any]:
    """Generate deterministic breakout candidates for paper evaluation."""
    high, high_valid = _finite_float(high_price)
    low, low_valid = _finite_float(low_price)
    current, current_valid = _finite_float(current_price)
    risk, risk_valid = _finite_float(risk_percent)
    normalized_symbol = str(symbol or "").upper()
    normalized_session = str(session_name or "")
    normalized_timeframe = str(timeframe or "")

    blocked_reasons: list[str] = []
    if not normalized_symbol:
        blocked_reasons.append("missing_symbol")
    if not normalized_session:
        blocked_reasons.append("missing_session_name")
    if not normalized_timeframe:
        blocked_reasons.append("missing_timeframe")
    if not high_valid or not low_valid or not current_valid:
        blocked_reasons.append("invalid_price_input")
    if high <= low:
        blocked_reasons.append("invalid_range")
    if not risk_valid or risk <= 0:
        blocked_reasons.append("invalid_risk_percent")
    if blocked_reasons:
        return _base_result(normalized_symbol, normalized_session, normalized_timeframe, blocked_reasons)

    breakout_range = round(high - low, 8)
    candidates: list[dict[str, Any]] = []
    signal = "NO_BREAKOUT"
    if current > high:
        signal = "BULLISH_BREAKOUT"
        candidates.append(
            _candidate(
                symbol=normalized_symbol,
                session_name=normalized_session,
                timeframe=normalized_timeframe,
                direction="buy",
                entry=current,
                stop=low,
                target=round(current + breakout_range, 8),
                risk_percent=risk,
                breakout_range=breakout_range,
            )
        )
    elif current < low:
        signal = "BEARISH_BREAKDOWN"
        candidates.append(
            _candidate(
                symbol=normalized_symbol,
                session_name=normalized_session,
                timeframe=normalized_timeframe,
                direction="sell",
                entry=current,
                stop=high,
                target=round(current - breakout_range, 8),
                risk_percent=risk,
                breakout_range=breakout_range,
            )
        )

    reasons = [] if candidates else ["no_breakout"]
    return {
        "strategy_name": STRATEGY_NAME,
        "strategy_version": STRATEGY_VERSION,
        "symbol": normalized_symbol,
        "session_name": normalized_session,
        "timeframe": normalized_timeframe,
        "candidates": candidates,
        "candidate_count": len(candidates),
        "evidence": {
            "signal": signal,
            "high_price": high,
            "low_price": low,
            "current_price": current,
            "breakout_range": breakout_range,
            "risk_percent": risk,
        },
        "blocked_reasons": reasons,
        "next_safe_action": "send_candidates_to_strategy_evaluation" if candidates else "continue_waiting_for_breakout",
        "safety": _safety(),
        "mode": MODE,
    }
