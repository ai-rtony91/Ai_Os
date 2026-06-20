"""Paper-only market data normalization utilities for Forex strategy/risk inputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

MARKET_DATA_MODE = "PAPER_ONLY"
MARKET_DATA_ALLOWED = "allowed"
MARKET_DATA_BLOCKED = "blocked"

REJECTION_NONE = "none"
REJECTION_INVALID_MARKET_DATA = "invalid_market_data"
REJECTION_NON_PAPER_MODE = "non_paper_mode"
REJECTION_LIVE_TRADING_BLOCKED = "live_trading_blocked"
REJECTION_MISSING_PAIR = "missing_pair"
REJECTION_UNSUPPORTED_PAIR = "unsupported_pair"
REJECTION_MISSING_BID = "missing_bid"
REJECTION_MISSING_ASK = "missing_ask"
REJECTION_INVALID_BID = "invalid_bid"
REJECTION_INVALID_ASK = "invalid_ask"
REJECTION_INVALID_SPREAD = "invalid_spread"
REJECTION_SPREAD_TOO_HIGH = "spread_too_high"
REJECTION_MISSING_TIMESTAMP = "missing_timestamp"
REJECTION_INVALID_TIMESTAMP = "invalid_timestamp"
REJECTION_STALE_DATA = "stale_market_data"
REJECTION_MISSING_CANDLE = "missing_candle"
REJECTION_INVALID_CANDLE = "invalid_candle"
REJECTION_INVALID_OHLCV = "invalid_ohlcv"
REJECTION_INVALID_SOURCE_MODE = "invalid_source_mode"
REJECTION_EVIDENCE_PATH_INVALID = "evidence_path_invalid"


@dataclass(frozen=True)
class MarketDataLimits:
    supported_pairs: tuple = ("EURUSD", "GBPUSD", "USDJPY")
    max_spread_pips: float = 3.0
    max_data_age_seconds: float = 300.0
    require_timestamp: bool = True
    require_candle: bool = False
    source_mode: str = "sample"


def _safe_number(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    if value is None:
        return None
    try:
        value_float = float(value)
    except (TypeError, ValueError):
        return None
    if value_float != value_float or value_float == float("inf") or value_float == float("-inf"):
        return None
    return value_float


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


def _normalize_pair(raw_pair: Any) -> str:
    if not isinstance(raw_pair, str):
        return ""
    normalized = "".join(raw_pair.strip().upper().replace("/", "").replace("-", "").replace("_", "").split())
    return normalized


def _pip_size(pair: str) -> float:
    if pair.endswith("JPY"):
        return 0.01
    return 0.0001


def _to_list(value: Any) -> List[Dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, dict):
        return [dict(value)]
    if isinstance(value, list):
        out: List[Dict[str, Any]] = []
        for item in value:
            if isinstance(item, dict):
                out.append(dict(item))
            else:
                return []
        return out
    return []


def _base_response() -> Dict[str, Any]:
    return {
        "allowed": True,
        "decision": MARKET_DATA_ALLOWED,
        "blocked_reason": REJECTION_NONE,
        "blocked_reasons": [],
        "warnings": [],
        "paper_only": True,
        "mode": MARKET_DATA_MODE,
        "pair": None,
        "bid": None,
        "ask": None,
        "mid": None,
        "spread": None,
        "spread_pips": None,
        "pip_size": None,
        "timestamp": None,
        "data_age_seconds": None,
        "fresh": True,
        "source_mode": "sample",
        "session_label": None,
        "candle": None,
        "candles": [],
        "normalized_for_preview": {},
        "normalized_for_strategy": {},
        "evidence": {},
        "evidence_path": None,
        "safety": {
            "paper_only": True,
            "broker": False,
            "live_trading": False,
            "credentials": False,
            "real_orders": False,
            "network_access": False,
        },
        "next_safe_action": "collect_valid_market_data",
        "metadata": {},
    }


def _block(payload: Dict[str, Any], reason: str, next_action: str) -> Dict[str, Any]:
    payload["allowed"] = False
    payload["decision"] = MARKET_DATA_BLOCKED
    payload["blocked_reason"] = reason
    payload["blocked_reasons"] = [reason]
    payload["next_safe_action"] = next_action
    return payload


def _coerce_limits(raw_limits: Any) -> Dict[str, Any]:
    if not isinstance(raw_limits, dict):
        return {
            "supported_pairs": tuple(MarketDataLimits.supported_pairs),
            "max_spread_pips": _safe_number(MarketDataLimits.max_spread_pips) or 3.0,
            "max_data_age_seconds": _safe_number(MarketDataLimits.max_data_age_seconds) or 300.0,
            "require_timestamp": MarketDataLimits.require_timestamp,
            "require_candle": MarketDataLimits.require_candle,
            "source_mode": MarketDataLimits.source_mode,
        }
    raw_pairs = raw_limits.get("supported_pairs", MarketDataLimits.supported_pairs)
    if not isinstance(raw_pairs, (list, tuple)):
        raw_pairs = MarketDataLimits.supported_pairs
    return {
        "supported_pairs": tuple(str(p).strip().upper() for p in raw_pairs if isinstance(p, str)),
        "max_spread_pips": _safe_number(raw_limits.get("max_spread_pips", MarketDataLimits.max_spread_pips)) or 3.0,
        "max_data_age_seconds": _safe_number(raw_limits.get("max_data_age_seconds", MarketDataLimits.max_data_age_seconds)) or 300.0,
        "require_timestamp": bool(raw_limits.get("require_timestamp", MarketDataLimits.require_timestamp)),
        "require_candle": bool(raw_limits.get("require_candle", MarketDataLimits.require_candle)),
        "source_mode": str(raw_limits.get("source_mode", MarketDataLimits.source_mode)),
    }


def _validate_ohlcv(payload: Dict[str, Any], candle: Dict[str, Any], index: str) -> bool:
    required_fields = ("open", "high", "low", "close", "volume", "timestamp")
    for field in required_fields:
        if field not in candle:
            payload["warnings"].append(f"candle_{index}_missing_{field}")
            return False
    o = _safe_number(candle.get("open"))
    h = _safe_number(candle.get("high"))
    l = _safe_number(candle.get("low"))
    c = _safe_number(candle.get("close"))
    v = _safe_number(candle.get("volume"))
    t = _safe_number(candle.get("timestamp"))
    if None in (o, h, l, c, v, t):
        payload["warnings"].append(f"candle_{index}_non_numeric_field")
        return False
    if o <= 0 or h <= 0 or l <= 0 or c <= 0 or v < 0 or t <= 0:
        payload["warnings"].append(f"candle_{index}_invalid_values")
        return False
    if h < max(o, c) or h < l:
        payload["warnings"].append(f"candle_{index}_invalid_high")
        return False
    if l > min(o, c) or l > h:
        payload["warnings"].append(f"candle_{index}_invalid_low")
        return False
    return True


def _normalize_candles(payload: Dict[str, Any], raw: Any) -> Iterable[Dict[str, Any]]:
    candles = _to_list(raw)
    if not candles:
        payload["warnings"].append("raw_candles_invalid")
        return []

    normalized: List[Dict[str, Any]] = []
    for idx, candle in enumerate(candles):
        if not isinstance(candle, dict):
            payload["warnings"].append(f"candle_{idx}_invalid_type")
            return []
        if not _validate_ohlcv(payload, candle, str(idx)):
            return []
        normalized.append(
            {
                "open": _safe_number(candle["open"]),
                "high": _safe_number(candle["high"]),
                "low": _safe_number(candle["low"]),
                "close": _safe_number(candle["close"]),
                "volume": _safe_number(candle["volume"]),
                "timestamp": _safe_number(candle["timestamp"]),
            }
        )
    return normalized


def normalize_market_snapshot(
    raw_market_data: Any,
    limits: Any = None,
    now_timestamp: Optional[float] = None,
    evidence_path: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload = _base_response()
    payload["metadata"] = dict(metadata or {})
    lim = _coerce_limits(limits)
    payload["supported_pairs"] = list(lim["supported_pairs"])  # internal traceability field only

    if not _is_relative_path(evidence_path) and evidence_path is not None:
        payload["evidence_path"] = evidence_path
        return _block(payload, REJECTION_EVIDENCE_PATH_INVALID, "supply_relative_evidence_path")
    payload["evidence_path"] = evidence_path

    data = _to_dict(raw_market_data)
    if not data:
        return _block(payload, REJECTION_INVALID_MARKET_DATA, "supply_valid_market_data_dict")

    payload["source_mode"] = str(data.get("source_mode", "sample")).strip().lower()
    payload["session_label"] = data.get("session_label")
    pair = _normalize_pair(data.get("pair", data.get("symbol")))
    if not pair:
        return _block(payload, REJECTION_MISSING_PAIR, "supply_pair_or_symbol")
    payload["pair"] = pair

    if lim["supported_pairs"] and pair not in lim["supported_pairs"]:
        return _block(payload, REJECTION_UNSUPPORTED_PAIR, "use_supported_pair")

    mode = payload["source_mode"]
    if mode == "live":
        return _block(payload, REJECTION_LIVE_TRADING_BLOCKED, "use_paper_or_sample_data_mode")
    if mode == "broker":
        return _block(payload, REJECTION_NON_PAPER_MODE, "use_paper_or_sample_data_mode")
    if mode not in {"sample", "paper", "demo_readonly", "live_blocked", "live", "broker"}:
        if mode not in {"", None}:
            return _block(payload, REJECTION_INVALID_SOURCE_MODE, "use_supported_source_mode")

    bid = _safe_number(data.get("bid"))
    if bid is None:
        reason = REJECTION_MISSING_BID if "bid" not in data else REJECTION_INVALID_BID
        return _block(payload, reason, "supply_positive_bid")
    ask = _safe_number(data.get("ask"))
    if ask is None:
        reason = REJECTION_MISSING_ASK if "ask" not in data else REJECTION_INVALID_ASK
        return _block(payload, reason, "supply_positive_ask")
    if bid <= 0:
        return _block(payload, REJECTION_INVALID_BID, "supply_positive_bid")
    if ask <= 0:
        return _block(payload, REJECTION_INVALID_ASK, "supply_positive_ask")
    if ask < bid:
        return _block(payload, REJECTION_INVALID_SPREAD, "fix_ask_not_below_bid")

    spread = ask - bid
    pip = _pip_size(pair)
    spread_pips = spread / pip
    if lim["max_spread_pips"] > 0 and spread_pips > lim["max_spread_pips"]:
        return _block(payload, REJECTION_SPREAD_TOO_HIGH, "reduce_spread_or_use_other_source")

    timestamp_field = data.get("timestamp")
    if timestamp_field is None:
        timestamp_field = data.get("data_timestamp")
    timestamp = _safe_number(timestamp_field)
    if timestamp is None:
        if lim["require_timestamp"]:
            reason = REJECTION_MISSING_TIMESTAMP if timestamp_field is None else REJECTION_INVALID_TIMESTAMP
            return _block(payload, reason, "supply_market_timestamp")
        timestamp = 0.0

    payload["bid"] = bid
    payload["ask"] = ask
    payload["mid"] = (bid + ask) / 2.0
    payload["spread"] = spread
    payload["spread_pips"] = spread_pips
    payload["pip_size"] = pip
    payload["timestamp"] = timestamp

    if now_timestamp is not None and timestamp is not None:
        age = float(now_timestamp) - float(timestamp)
        if age < 0:
            age = 0.0
        payload["data_age_seconds"] = age
        if lim["max_data_age_seconds"] >= 0 and age > lim["max_data_age_seconds"]:
            return _block(payload, REJECTION_STALE_DATA, "collect_fresher_market_data")
        payload["fresh"] = age <= lim["max_data_age_seconds"]
    else:
        payload["data_age_seconds"] = None
        payload["fresh"] = True

    single_candle = data.get("candle")
    candles = data.get("candles")
    normalized_single = None
    normalized_many: List[Dict[str, Any]] = []

    if single_candle is not None:
        normalized = list(_normalize_candles(payload, single_candle))
        if normalized:
            normalized_single = normalized[0]
        else:
            return _block(payload, REJECTION_INVALID_CANDLE, "supply_valid_candle")
    if candles is not None:
        normalized_many = list(_normalize_candles(payload, candles))
        if not normalized_many:
            return _block(payload, REJECTION_INVALID_CANDLE, "supply_valid_candles")

    if lim["require_candle"] and normalized_single is None and not normalized_many:
        return _block(payload, REJECTION_MISSING_CANDLE, "supply_recent_candle_data")

    if normalized_single is not None:
        payload["candle"] = normalized_single
    if normalized_many:
        payload["candles"] = normalized_many

    payload["normalized_for_preview"] = {
        "pair": pair,
        "entry_price": payload["mid"],
        "bid": bid,
        "ask": ask,
        "spread": spread,
        "spread_pips": spread_pips,
        "data_timestamp": timestamp,
        "paper_only": True,
    }
    payload["normalized_for_strategy"] = {
        "pair": pair,
        "bid": bid,
        "ask": ask,
        "mid": payload["mid"],
        "spread_pips": spread_pips,
        "candle": normalized_single,
        "candles": normalized_many,
        "timestamp": timestamp,
        "source_mode": payload["source_mode"],
        "session_label": payload["session_label"],
        "paper_only": True,
    }

    payload["evidence"] = {
        "pair": pair,
        "mid": payload["mid"],
        "spread_pips": spread_pips,
        "fresh": payload["fresh"],
        "candle_count": len(normalized_many),
        "source_mode": payload["source_mode"],
    }

    payload["next_safe_action"] = "pass_to_order_preview_and_governor"
    return payload


def _to_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return {}

