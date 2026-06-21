"""Deterministic paper-only mean reversion strategy."""
from __future__ import annotations

import math
from typing import Any

STRATEGY_NAME = "MEAN_REVERSION_V1"
STRATEGY_VERSION = "v1"
MODE = "MEAN_REVERSION_STRATEGY_ONLY"


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
        "broker_execution_allowed": False,
        "short_selling_requires_broker_policy_review": True,
        "hedging_fifo_policy_review_required": True,
        "margin_policy_review_required": True,
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
        "next_safe_action": "wait_for_valid_mean_reversion_input",
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
    deviation_from_average_percent: float,
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
        "deviation_from_average_percent": round(deviation_from_average_percent, 8),
        "paper_only": True,
    }


def generate_mean_reversion_candidates(
    *,
    symbol: str,
    session_name: str,
    timeframe: str,
    moving_average: Any,
    current_price: Any,
    deviation_percent: Any,
    risk_percent: Any,
) -> dict[str, Any]:
    """Generate deterministic mean-reversion candidates for paper evaluation."""
    average, average_valid = _finite_float(moving_average)
    current, current_valid = _finite_float(current_price)
    deviation, deviation_valid = _finite_float(deviation_percent)
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
    if not average_valid or not current_valid or average <= 0 or current <= 0:
        blocked_reasons.append("invalid_price_input")
    if not deviation_valid or deviation <= 0:
        blocked_reasons.append("invalid_deviation_percent")
    if not risk_valid or risk <= 0:
        blocked_reasons.append("invalid_risk_percent")
    if blocked_reasons:
        return _base_result(normalized_symbol, normalized_session, normalized_timeframe, blocked_reasons)

    deviation_from_average_percent = round(((current - average) / average) * 100.0, 8)
    threshold = round(abs(deviation), 8)
    lower_trigger = round(average * (1.0 - threshold / 100.0), 8)
    upper_trigger = round(average * (1.0 + threshold / 100.0), 8)
    distance_to_average = round(abs(average - current), 8)
    candidates: list[dict[str, Any]] = []
    signal = "NO_TRADE"

    if current < lower_trigger:
        signal = "BULLISH_MEAN_REVERSION"
        candidates.append(
            _candidate(
                symbol=normalized_symbol,
                session_name=normalized_session,
                timeframe=normalized_timeframe,
                direction="buy",
                entry=current,
                stop=round(current - distance_to_average, 8),
                target=average,
                risk_percent=risk,
                deviation_from_average_percent=deviation_from_average_percent,
            )
        )
    elif current > upper_trigger:
        signal = "BEARISH_MEAN_REVERSION"
        candidates.append(
            _candidate(
                symbol=normalized_symbol,
                session_name=normalized_session,
                timeframe=normalized_timeframe,
                direction="sell",
                entry=current,
                stop=round(current + distance_to_average, 8),
                target=average,
                risk_percent=risk,
                deviation_from_average_percent=deviation_from_average_percent,
            )
        )

    reasons = [] if candidates else ["within_acceptable_deviation"]
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
            "moving_average": average,
            "current_price": current,
            "deviation_percent": threshold,
            "deviation_from_average_percent": deviation_from_average_percent,
            "lower_trigger": lower_trigger,
            "upper_trigger": upper_trigger,
            "risk_percent": risk,
        },
        "blocked_reasons": reasons,
        "next_safe_action": "send_candidates_to_strategy_evaluation" if candidates else "continue_waiting_for_mean_reversion_setup",
        "safety": _safety(),
        "mode": MODE,
    }
