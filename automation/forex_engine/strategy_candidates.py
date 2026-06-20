"""Rule-based strategy candidate generator for paper-only Forex trades."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

STRATEGY_CANDIDATE_MODE = "PAPER_ONLY"
STRATEGY_CANDIDATE_ALLOWED = "allowed"
STRATEGY_CANDIDATE_BLOCKED = "blocked"

REJECTION_REASON_NONE = "none"
REJECTION_REASON_INVALID_MARKET_DATA = "invalid_market_data"
REJECTION_REASON_NON_PAPER_MODE = "non_paper_mode"
REJECTION_REASON_LIVE_TRADING_BLOCKED = "live_trading_blocked"
REJECTION_REASON_MISSING_PAIR = "missing_pair"
REJECTION_REASON_UNSUPPORTED_PAIR = "unsupported_pair"
REJECTION_REASON_MISSING_CANDLES = "missing_candles"
REJECTION_REASON_INSUFFICIENT_CANDLES = "insufficient_candles"
REJECTION_REASON_INVALID_CANDLE_DATA = "invalid_candle_data"
REJECTION_REASON_NO_TRADE_SIGNAL = "no_trade_signal"
REJECTION_REASON_UNSUPPORTED_STRATEGY = "unsupported_strategy"
REJECTION_REASON_SCORE_BELOW_THRESHOLD = "score_below_threshold"
REJECTION_REASON_STALE_MARKET_DATA = "stale_market_data"
REJECTION_REASON_SPREAD_TOO_HIGH = "spread_too_high"
REJECTION_REASON_EVIDENCE_PATH_INVALID = "evidence_path_invalid"


@dataclass(frozen=True)
class StrategyLimits:
    supported_pairs: tuple = ("EURUSD", "GBPUSD", "USDJPY")
    default_short_window: int = 3
    default_long_window: int = 5
    default_stop_distance: float = 0.0020
    default_take_distance: float = 0.0040
    default_risk_percent: float = 1.0
    min_score: float = 50.0
    max_spread_pips: float = 3.0
    max_data_age_seconds: float = 300.0
    require_timestamp: bool = True
    stale_blocked: bool = True


def _safe_number(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if numeric != numeric or numeric == float("inf") or numeric == float("-inf"):
        return None
    return numeric


def _is_relative_path(path: Any) -> bool:
    if not isinstance(path, str) or not path:
        return False
    if path.startswith("/") or path.startswith("\\"):
        return False
    if ":" in path:
        return False
    if ".." in path.split("/"):
        return False
    return True


def _safe_snapshot(payload: Any) -> Dict[str, Any]:
    if isinstance(payload, dict):
        return dict(payload)
    if hasattr(payload, "__dict__"):
        return dict(payload.__dict__)
    return {}

def _normalize_limits(raw: Any) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        return {
            "supported_pairs": tuple(StrategyLimits.supported_pairs),
            "default_short_window": StrategyLimits.default_short_window,
            "default_long_window": StrategyLimits.default_long_window,
            "default_stop_distance": _safe_number(StrategyLimits.default_stop_distance) or 0.0020,
            "default_take_distance": _safe_number(StrategyLimits.default_take_distance) or 0.0040,
            "default_risk_percent": _safe_number(StrategyLimits.default_risk_percent) or 1.0,
            "min_score": _safe_number(StrategyLimits.min_score) or 50.0,
            "max_spread_pips": _safe_number(StrategyLimits.max_spread_pips) or 3.0,
            "max_data_age_seconds": _safe_number(StrategyLimits.max_data_age_seconds) or 300.0,
            "require_timestamp": StrategyLimits.require_timestamp,
            "stale_blocked": StrategyLimits.stale_blocked,
            "strategies": ["moving_average_trend", "breakout"],
        }

    pairs = raw.get("supported_pairs", StrategyLimits.supported_pairs)
    if not isinstance(pairs, (tuple, list)) or not pairs:
        pairs = StrategyLimits.supported_pairs

    strategy_names = raw.get("strategies", ["moving_average_trend", "breakout"])
    if not isinstance(strategy_names, (tuple, list)):
        strategy_names = ["moving_average_trend", "breakout"]

    return {
        "supported_pairs": tuple(str(p).upper() for p in pairs if isinstance(p, str)),
        "default_short_window": int(raw.get("default_short_window", StrategyLimits.default_short_window) or StrategyLimits.default_short_window),
        "default_long_window": int(raw.get("default_long_window", StrategyLimits.default_long_window) or StrategyLimits.default_long_window),
        "default_stop_distance": _safe_number(raw.get("default_stop_distance", StrategyLimits.default_stop_distance)) or 0.0020,
        "default_take_distance": _safe_number(raw.get("default_take_distance", StrategyLimits.default_take_distance)) or 0.0040,
        "default_risk_percent": _safe_number(raw.get("default_risk_percent", StrategyLimits.default_risk_percent)) or 1.0,
        "min_score": _safe_number(raw.get("min_score", StrategyLimits.min_score)) or 50.0,
        "max_spread_pips": _safe_number(raw.get("max_spread_pips", StrategyLimits.max_spread_pips)) or 3.0,
        "max_data_age_seconds": _safe_number(raw.get("max_data_age_seconds", StrategyLimits.max_data_age_seconds)) or 300.0,
        "require_timestamp": bool(raw.get("require_timestamp", StrategyLimits.require_timestamp)),
        "stale_blocked": bool(raw.get("stale_blocked", StrategyLimits.stale_blocked)),
        "strategies": list(strategy_names),
    }


def _safety() -> Dict[str, bool]:
    return {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }


def _base_response() -> Dict[str, Any]:
    return {
        "allowed": True,
        "decision": STRATEGY_CANDIDATE_ALLOWED,
        "blocked_reason": REJECTION_REASON_NONE,
        "blocked_reasons": [],
        "warnings": [],
        "paper_only": True,
        "mode": STRATEGY_CANDIDATE_MODE,
        "pair": None,
        "strategy_count": 0,
        "candidates": [],
        "rejected_candidates": [],
        "selected_count": 0,
        "rejected_count": 0,
        "no_trade_count": 0,
        "safety": _safety(),
        "evidence": {},
        "evidence_path": None,
        "next_safe_action": "supply_valid_normalized_market_data",
        "metadata": {},
    }


def _block(payload: Dict[str, Any], reason: str, next_action: str) -> Dict[str, Any]:
    payload["allowed"] = False
    payload["decision"] = STRATEGY_CANDIDATE_BLOCKED
    payload["blocked_reason"] = reason
    payload["blocked_reasons"] = [reason]
    payload["next_safe_action"] = next_action
    return payload


def _normalize_mode(source_mode: Any) -> str:
    if source_mode is None:
        return ""
    return str(source_mode).strip().lower()


def _extract_candles(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    if isinstance(data.get("candle"), dict):
        return [dict(data["candle"])]
    if isinstance(data.get("candles"), list):
        out: List[Dict[str, Any]] = []
        for item in data["candles"]:
            if isinstance(item, dict):
                out.append(dict(item))
        return out
    return []


def _validate_pair(pair: Any, limits: Dict[str, Any], output: Dict[str, Any]) -> Optional[str]:
    if not pair:
        _block(output, REJECTION_REASON_MISSING_PAIR, "supply_pair")
        return None
    pair_up = str(pair).upper().replace("-", "").replace("_", "")
    if limits["supported_pairs"] and pair_up not in limits["supported_pairs"]:
        _block(output, REJECTION_REASON_UNSUPPORTED_PAIR, "use_supported_pair")
        return None
    return pair_up


def _validate_source_mode(data: Dict[str, Any], out: Dict[str, Any]) -> bool:
    mode = _normalize_mode(data.get("source_mode"))
    if mode in {"live", "live_trading"}:
        _block(out, REJECTION_REASON_LIVE_TRADING_BLOCKED, "supply_paper_or_sample_mode")
        return False
    if mode in {"broker"}:
        _block(out, REJECTION_REASON_NON_PAPER_MODE, "supply_paper_only_data")
        return False
    if mode in {"", None}:
        return True
    if mode in {"paper", "sample", "demo_readonly", "live_blocked"}:
        return True
    _block(out, REJECTION_REASON_INVALID_MARKET_DATA, "use_supported_source_mode")
    return False


def _validate_timestamp_and_freshness(data: Dict[str, Any], now_timestamp: Optional[float], limits: Dict[str, Any], out: Dict[str, Any]) -> bool:
    ts = data.get("timestamp")
    if ts is None:
        ts = data.get("data_timestamp")
    if ts is None:
        if limits["require_timestamp"]:
            _block(out, REJECTION_REASON_INVALID_MARKET_DATA, "supply_data_timestamp")
            return False
        return True
    ts_num = _safe_number(ts)
    if ts_num is None:
        _block(out, REJECTION_REASON_INVALID_MARKET_DATA, "supply_numeric_timestamp")
        return False
    if now_timestamp is not None:
        now_val = _safe_number(now_timestamp)
        if now_val is None:
            _block(out, REJECTION_REASON_INVALID_MARKET_DATA, "supply_numeric_now_timestamp")
            return False
        age = now_val - ts_num
        if age > limits["max_data_age_seconds"] and limits["stale_blocked"]:
            _block(out, REJECTION_REASON_STALE_MARKET_DATA, "supply_fresh_market_data")
            return False
    return True


def _validate_spread(data: Dict[str, Any], limits: Dict[str, Any], out: Dict[str, Any]) -> bool:
    spread_pips = data.get("spread_pips", 0.0)
    sp = _safe_number(spread_pips)
    if sp is None:
        _block(out, REJECTION_REASON_INVALID_MARKET_DATA, "supply_valid_spread_pips")
        return False
    if limits["max_spread_pips"] > 0 and sp > limits["max_spread_pips"]:
        out["warnings"].append("spread_too_wide")
        out["blocked_reason"] = REJECTION_REASON_SPREAD_TOO_HIGH
        out["blocked_reasons"] = [REJECTION_REASON_SPREAD_TOO_HIGH]
        out["allowed"] = False
        out["decision"] = STRATEGY_CANDIDATE_BLOCKED
        out["next_safe_action"] = "use_tighter_spread_source"
        return False
    return True


def _extract_candle_series(candles: List[Dict[str, Any]]) -> List[float]:
    closes: List[float] = []
    for item in candles:
        close = _safe_number(item.get("close"))
        if close is None:
            return []
        closes.append(close)
    return closes


def _extract_high_low_series(candles: List[Dict[str, Any]]) -> (List[float], List[float]):
    highs: List[float] = []
    lows: List[float] = []
    for item in candles:
        h = _safe_number(item.get("high"))
        l = _safe_number(item.get("low"))
        if h is None or l is None:
            return [], []
        highs.append(h)
        lows.append(l)
    return highs, lows


def _sma(values: List[float], window: int) -> Optional[float]:
    if window <= 0:
        return None
    if len(values) < window:
        return None
    return sum(values[-window:]) / float(window)


def _candidate_id(pair: str, strategy_name: str, direction: str, entry_price: float, index: int, timestamp: float) -> str:
    return f"{pair}:{strategy_name}:{direction}:{int(index)}:{round(entry_price, 8)}:{int(timestamp)}"


def _make_candidate(
    pair: str,
    strategy_name: str,
    direction: str,
    timestamp: float,
    data: Dict[str, Any],
    entry_price: float,
    stop_distance: float,
    take_distance: float,
    risk_percent: float,
    score: float,
) -> Dict[str, Any]:
    if direction == "buy":
        stop_loss = entry_price - stop_distance
        take_profit = entry_price + take_distance
    else:
        stop_loss = entry_price + stop_distance
        take_profit = entry_price - take_distance
    candidate_id = _candidate_id(pair, strategy_name, direction, entry_price, 0, timestamp)
    return {
        "candidate_id": candidate_id,
        "strategy_name": strategy_name,
        "pair": pair,
        "direction": direction,
        "entry_type": "market",
        "entry_price": round(entry_price, 8),
        "stop_loss": round(stop_loss, 8),
        "take_profit": round(take_profit, 8),
        "risk_percent": risk_percent,
        "score": round(score, 2),
        "reasons": [strategy_name],
        "rejection_reasons": [],
        "source_mode": data.get("source_mode", "sample"),
        "timestamp": int(timestamp),
        "spread_pips": _safe_number(data.get("spread_pips")),
        "data_timestamp": data.get("timestamp") if data.get("timestamp") is not None else data.get("data_timestamp"),
        "normalized_snapshot": data,
        "paper_only": True,
    }


def _mark_rejected_candidate(
    strategy_name: str,
    pair: str,
    reason: str,
    reasons: Optional[List[str]] = None,
) -> Dict[str, Any]:
    return {
        "candidate_id": f"{pair}:{strategy_name}:{reason}",
        "strategy_name": strategy_name,
        "pair": pair,
        "direction": None,
        "entry_type": None,
        "entry_price": None,
        "stop_loss": None,
        "take_profit": None,
        "risk_percent": None,
        "score": 0.0,
        "reasons": [],
        "rejection_reasons": [reason] + (reasons or []),
        "paper_only": True,
    }


def generate_strategy_candidates(
    normalized_market_data: Any,
    strategies: Optional[List[str]] = None,
    limits: Optional[Dict[str, Any]] = None,
    now_timestamp: Optional[float] = None,
    evidence_path: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    output = _base_response()
    output["metadata"] = dict(metadata or {})

    if not _is_relative_path(evidence_path) and evidence_path is not None:
        output["evidence_path"] = evidence_path
        return _block(output, REJECTION_REASON_EVIDENCE_PATH_INVALID, "supply_relative_evidence_path")
    output["evidence_path"] = evidence_path

    limit_cfg = _normalize_limits(limits)
    output["strategy_count"] = len(limit_cfg["strategies"])
    strategy_set = set(limit_cfg["strategies"])

    if strategies is None:
        strategy_names = limit_cfg["strategies"]
    else:
        if not isinstance(strategies, (list, tuple)) or not strategies:
            strategy_names = []
        else:
            strategy_names = [str(s) for s in strategies]
    selected = set(strategy_names)

    for name in selected:
        if name not in {"moving_average_trend", "breakout"}:
            output["rejected_candidates"].append(_mark_rejected_candidate(name, "", REJECTION_REASON_UNSUPPORTED_STRATEGY))

    data = _safe_snapshot(normalized_market_data)
    if not data:
        # canonical fallback for nested normalized shapes
        data = _safe_snapshot(getattr(normalized_market_data, "normalized_for_strategy", {}))

    if not data:
        return _block(output, REJECTION_REASON_INVALID_MARKET_DATA, "supply_normalized_market_data")

    if "normalized_for_strategy" in data:
        nested = data.get("normalized_for_strategy")
        if isinstance(nested, dict):
            data = dict(nested)

    if not _validate_source_mode(data, output):
        return output
    if data.get("paper_only") is False:
        return _block(output, REJECTION_REASON_NON_PAPER_MODE, "supply_paper_only_market_data")

    pair = _validate_pair(data.get("pair"), limit_cfg, output)
    if output["allowed"] is False:
        return output
    output["pair"] = pair

    if not _validate_spread(data, limit_cfg, output):
        return output
    if not _validate_timestamp_and_freshness(data, now_timestamp, limit_cfg, output):
        return output

    candles = _extract_candles(data)
    if not candles:
        return _block(output, REJECTION_REASON_MISSING_CANDLES, "supply_candles")

    closes = _extract_candle_series(candles)
    if not closes:
        return _block(output, REJECTION_REASON_INVALID_CANDLE_DATA, "supply_numeric_candle_data")

    timestamp = _safe_number(data.get("timestamp", data.get("data_timestamp")) ) or 0.0
    min_score = limit_cfg["min_score"]
    stop_dist = limit_cfg["default_stop_distance"]
    take_dist = limit_cfg["default_take_distance"]
    risk_pct = limit_cfg["default_risk_percent"]
    short_window = max(1, limit_cfg["default_short_window"])
    long_window = max(2, limit_cfg["default_long_window"])

    active_strategies = [s for s in strategy_names if s in selected and s in {"moving_average_trend", "breakout"}]
    if not active_strategies:
        output["warnings"].append("no_active_strategies")
        output["next_safe_action"] = "enable_strategies"

    for strategy_name in active_strategies:
        if strategy_name == "moving_average_trend":
            if len(closes) < long_window:
                output["rejected_candidates"].append(_mark_rejected_candidate(strategy_name, pair, REJECTION_REASON_INSUFFICIENT_CANDLES))
                output["rejected_count"] += 1
                continue
            short_ma = _sma(closes, short_window)
            long_ma = _sma(closes, long_window)
            if short_ma is None or long_ma is None:
                output["rejected_candidates"].append(_mark_rejected_candidate(strategy_name, pair, REJECTION_REASON_INSUFFICIENT_CANDLES))
                output["rejected_count"] += 1
                continue

            latest = closes[-1]
            prior = closes[-2] if len(closes) >= 2 else latest
            direction = None
            if short_ma > long_ma and latest > prior:
                direction = "buy"
            elif short_ma < long_ma and latest < prior:
                direction = "sell"

            if direction is None:
                output["rejected_candidates"].append(_mark_rejected_candidate(strategy_name, pair, REJECTION_REASON_NO_TRADE_SIGNAL))
                output["rejected_count"] += 1
                output["no_trade_count"] += 1
                continue

            score = 70.0 if direction else 0.0
            if score < min_score:
                output["rejected_candidates"].append(_mark_rejected_candidate(strategy_name, pair, REJECTION_REASON_SCORE_BELOW_THRESHOLD))
                output["rejected_count"] += 1
                continue

            cand = _make_candidate(pair, strategy_name, direction, timestamp, data, latest, stop_dist, take_dist, risk_pct, score)
            cand["candidate_id"] = _candidate_id(pair, strategy_name, direction, latest, 0, timestamp)
            cand["reasons"] = [strategy_name, "ma_trend"]
            output["candidates"].append(cand)
            output["selected_count"] += 1

        if strategy_name == "breakout":
            if len(candles) < 2:
                output["rejected_candidates"].append(_mark_rejected_candidate(strategy_name, pair, REJECTION_REASON_INSUFFICIENT_CANDLES))
                output["rejected_count"] += 1
                continue

            highs, lows = _extract_high_low_series(candles[:-1])
            if not highs or not lows:
                output["rejected_candidates"].append(_mark_rejected_candidate(strategy_name, pair, REJECTION_REASON_INVALID_CANDLE_DATA))
                output["rejected_count"] += 1
                continue

            latest_close = closes[-1]
            prior_high = max(highs)
            prior_low = min(lows)
            direction = None
            if latest_close > prior_high:
                direction = "buy"
            elif latest_close < prior_low:
                direction = "sell"

            if direction is None:
                output["rejected_candidates"].append(_mark_rejected_candidate(strategy_name, pair, REJECTION_REASON_NO_TRADE_SIGNAL))
                output["rejected_count"] += 1
                output["no_trade_count"] += 1
                continue

            score = 65.0
            if score < min_score:
                output["rejected_candidates"].append(_mark_rejected_candidate(strategy_name, pair, REJECTION_REASON_SCORE_BELOW_THRESHOLD))
                output["rejected_count"] += 1
                continue

            # breakout uses candle range when available as a fallback distance anchor
            prior = closes[-2]
            candle_range = abs(candle_range) if False else (abs(highs[-1] - lows[-1]) if highs and lows else stop_dist)
            effective_stop = max(stop_dist, candle_range * 0.25)
            effective_take = max(take_dist, candle_range * 0.5)
            cand = _make_candidate(pair, strategy_name, direction, timestamp, data, latest_close, effective_stop, effective_take, risk_pct, score)
            cand["candidate_id"] = _candidate_id(pair, strategy_name, direction, latest_close, 1, timestamp)
            cand["reasons"] = [strategy_name, "breakout"]
            output["candidates"].append(cand)
            output["selected_count"] += 1

    output["rejected_count"] = len(output["rejected_candidates"])
    if output["selected_count"] == 0 and output["allowed"]:
        output["next_safe_action"] = "monitor_for_signal"
        if output["rejected_count"] == 0:
            output["no_trade_count"] = 0

    if output["selected_count"] == 0 and output["rejected_count"] > 0:
        # keep allowed and provide deterministic no-trade response
        output["next_safe_action"] = "wait_for_valid_signal"

    output["evidence"] = {
        "pair": output["pair"],
        "strategy_count": output["strategy_count"],
        "selected_count": output["selected_count"],
        "rejected_count": output["rejected_count"],
        "no_trade_count": output["no_trade_count"],
    }

    output["evidence_path"] = evidence_path
    return output
