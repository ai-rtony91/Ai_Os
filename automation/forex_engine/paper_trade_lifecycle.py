"""Canonical paper trade model and lifecycle helpers for AI_OS Trading Lab.

This module is model-only and keeps paper-only boundaries explicit in every
trade dictionary returned by this API.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field, replace
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class PaperTradeStatus:
    CANDIDATE = "candidate"
    PREVIEWED = "previewed"
    REJECTED = "rejected"
    QUEUED = "queued"
    OPENED = "opened"
    ACTIVE = "active"
    CLOSED = "closed"
    KILLED = "killed"
    EXPIRED = "expired"
    ERROR = "error"


class TradeDirection:
    BUY = "buy"
    SELL = "sell"


class TradeEntryType:
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"


class TradeCloseReason:
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    MANUAL_CLOSE = "manual_close"
    EXPIRY = "expiry"
    KILL_SWITCH = "kill_switch"
    RISK_BLOCK = "risk_block"
    ERROR = "error"
    NONE = "none"


PAPER_TRADE_STATUSES = {
    PaperTradeStatus.CANDIDATE,
    PaperTradeStatus.PREVIEWED,
    PaperTradeStatus.REJECTED,
    PaperTradeStatus.QUEUED,
    PaperTradeStatus.OPENED,
    PaperTradeStatus.ACTIVE,
    PaperTradeStatus.CLOSED,
    PaperTradeStatus.KILLED,
    PaperTradeStatus.EXPIRED,
    PaperTradeStatus.ERROR,
}


TERMINAL_PAPER_TRADE_STATUSES = {
    PaperTradeStatus.REJECTED,
    PaperTradeStatus.CLOSED,
    PaperTradeStatus.KILLED,
    PaperTradeStatus.EXPIRED,
    PaperTradeStatus.ERROR,
}


PAPER_TRADE_ALLOWED_TRANSITIONS: Dict[str, set[str]] = {
    PaperTradeStatus.CANDIDATE: {
        PaperTradeStatus.PREVIEWED,
        PaperTradeStatus.REJECTED,
    },
    PaperTradeStatus.PREVIEWED: {
        PaperTradeStatus.QUEUED,
        PaperTradeStatus.REJECTED,
    },
    PaperTradeStatus.QUEUED: {
        PaperTradeStatus.OPENED,
        PaperTradeStatus.EXPIRED,
        PaperTradeStatus.KILLED,
        PaperTradeStatus.REJECTED,
    },
    PaperTradeStatus.OPENED: {
        PaperTradeStatus.ACTIVE,
        PaperTradeStatus.CLOSED,
        PaperTradeStatus.KILLED,
        PaperTradeStatus.ERROR,
    },
    PaperTradeStatus.ACTIVE: {
        PaperTradeStatus.CLOSED,
        PaperTradeStatus.KILLED,
        PaperTradeStatus.EXPIRED,
        PaperTradeStatus.ERROR,
    },
}


def _paper_safety() -> Dict[str, bool]:
    return {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }


def _normalize_pair(pair: str) -> str:
    return str(pair).strip().upper()


def _normalize_direction(direction: str) -> str:
    return str(direction).strip().lower()


def _normalize_entry_type(entry_type: str) -> str:
    return str(entry_type).strip().lower()


def _as_float(value: Any) -> float:
    return float(value)


def _as_timestamp(value: Any) -> str:
    if value is None:
        return utc_now_iso()
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
    return str(value)


def _validate_status(value: str) -> str:
    if value not in PAPER_TRADE_STATUSES:
        raise ValueError(f"Invalid paper trade status: {value}")
    return value


@dataclass
class PaperTradeLifecycle:
    trade_id: str
    pair: str
    direction: str
    entry_type: str
    entry_price: float
    stop_loss: float
    take_profit: float
    units: float
    dollar_risk: float
    percent_risk: float
    status: str
    created_timestamp: str
    opened_timestamp: Optional[str] = None
    closed_timestamp: Optional[str] = None
    close_reason: str = TradeCloseReason.NONE
    realized_pnl: float = 0.0
    evidence_path: str = ""
    paper_only: bool = True
    safety: Dict[str, bool] = field(default_factory=_paper_safety)
    blocked_reason: str = "none"
    lifecycle_history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


def _default_validation_payload() -> Dict[str, Any]:
    return {
        "valid": True,
        "blocked_reason": "none",
        "errors": [],
        "warnings": [],
        "paper_only": True,
        "next_safe_action": "Await policy gate and lifecycle-safe paper transitions.",
    }


def _is_valid_paper_only_safety(payload: Dict[str, Any]) -> bool:
    safety = payload.get("safety", payload)
    return (
        isinstance(safety, dict)
        and safety.get("paper_only") is True
        and safety.get("broker", False) is False
        and safety.get("live_trading") is False
        and safety.get("credentials") is False
        and safety.get("real_orders") is False
        and safety.get("network_access") is False
    )


def build_paper_trade(
    *,
    trade_id: str,
    pair: str,
    direction: str,
    entry_type: str,
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    units: float,
    dollar_risk: float,
    percent_risk: float,
    status: str = PaperTradeStatus.CANDIDATE,
    created_timestamp: Optional[str] = None,
    opened_timestamp: Optional[str] = None,
    closed_timestamp: Optional[str] = None,
    close_reason: str = TradeCloseReason.NONE,
    realized_pnl: float = 0.0,
    evidence_path: str = "",
    blocked_reason: str = "none",
    lifecycle_history: Optional[List[Dict[str, Any]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> PaperTradeLifecycle:
    return PaperTradeLifecycle(
        trade_id=trade_id,
        pair=_normalize_pair(pair),
        direction=_normalize_direction(direction),
        entry_type=_normalize_entry_type(entry_type),
        entry_price=_as_float(entry_price),
        stop_loss=_as_float(stop_loss),
        take_profit=_as_float(take_profit),
        units=_as_float(units),
        dollar_risk=_as_float(dollar_risk),
        percent_risk=_as_float(percent_risk),
        status=_validate_status(status),
        created_timestamp=created_timestamp or utc_now_iso(),
        opened_timestamp=opened_timestamp,
        closed_timestamp=closed_timestamp,
        close_reason=close_reason,
        realized_pnl=_as_float(realized_pnl),
        evidence_path=str(evidence_path),
        paper_only=True,
        safety=_paper_safety(),
        blocked_reason=blocked_reason,
        lifecycle_history=list(lifecycle_history or []),
        metadata=dict(metadata or {}),
    )


def validate_paper_trade(trade: Any) -> Dict[str, Any]:
    result = _default_validation_payload()
    if not isinstance(trade, PaperTradeLifecycle):
        result["valid"] = False
        result["errors"].append("trade must be PaperTradeLifecycle")
        result["blocked_reason"] = "invalid_type"
        result["next_safe_action"] = "Construct a valid PaperTradeLifecycle and retry validation."
        return result

    if not trade.trade_id or not str(trade.trade_id).strip():
        result["valid"] = False
        result["errors"].append("trade_id is required and must be non-empty")
        result["blocked_reason"] = "missing_trade_id"

    normalized_pair = _normalize_pair(trade.pair)
    if not normalized_pair or not normalized_pair.replace("-", "").isalpha():
        result["valid"] = False
        result["errors"].append("pair must be a normalized symbol string")
        result["blocked_reason"] = "invalid_pair"
    elif trade.pair != normalized_pair:
        result["warnings"].append("pair is not uppercase-normalized")
        trade.pair = normalized_pair

    if trade.direction not in (TradeDirection.BUY, TradeDirection.SELL):
        result["valid"] = False
        result["errors"].append("direction must be buy or sell")
        result["blocked_reason"] = "invalid_direction"

    if trade.entry_type not in (
        TradeEntryType.MARKET,
        TradeEntryType.LIMIT,
        TradeEntryType.STOP,
    ):
        result["valid"] = False
        result["errors"].append("entry_type must be market, limit, or stop")
        result["blocked_reason"] = "invalid_entry_type"

    for field_name in ("entry_price", "stop_loss", "take_profit", "units"):
        value = getattr(trade, field_name, None)
        try:
            if float(value) <= 0:
                result["valid"] = False
                result["errors"].append(f"{field_name} must be positive")
                result["blocked_reason"] = f"invalid_{field_name}"
        except (TypeError, ValueError):
            result["valid"] = False
            result["errors"].append(f"{field_name} must be numeric")
            result["blocked_reason"] = f"invalid_{field_name}"

    for field_name in ("dollar_risk", "percent_risk"):
        value = getattr(trade, field_name, None)
        try:
            if float(value) < 0:
                result["valid"] = False
                result["errors"].append(f"{field_name} must be non-negative")
                result["blocked_reason"] = f"invalid_{field_name}"
        except (TypeError, ValueError):
            result["valid"] = False
            result["errors"].append(f"{field_name} must be numeric")
            result["blocked_reason"] = f"invalid_{field_name}"

    if not trade.created_timestamp:
        result["valid"] = False
        result["errors"].append("created_timestamp is required")
        result["blocked_reason"] = "missing_created_timestamp"

    if trade.status in TERMINAL_PAPER_TRADE_STATUSES and trade.status != PaperTradeStatus.REJECTED:
        if not trade.closed_timestamp:
            result["valid"] = False
            result["errors"].append("closed_timestamp is required for terminal paper status")
            result["blocked_reason"] = "missing_closed_timestamp"

    if trade.close_reason not in (
        TradeCloseReason.STOP_LOSS,
        TradeCloseReason.TAKE_PROFIT,
        TradeCloseReason.MANUAL_CLOSE,
        TradeCloseReason.EXPIRY,
        TradeCloseReason.KILL_SWITCH,
        TradeCloseReason.RISK_BLOCK,
        TradeCloseReason.ERROR,
        TradeCloseReason.NONE,
    ):
        result["valid"] = False
        result["errors"].append("close_reason invalid")
        result["blocked_reason"] = "invalid_close_reason"

    if not isinstance(_paper_safety(), dict) or not _is_valid_paper_only_safety(trade.safety):
        result["valid"] = False
        result["errors"].append("safety boundary must deny broker, live, credentials, real orders, and network access")
        result["blocked_reason"] = "invalid_safety"

    if not trade.paper_only:
        result["valid"] = False
        result["errors"].append("paper_only must be True")
        result["blocked_reason"] = "paper_only_false"

    if not _is_valid_paper_only_safety(trade.safety):
        result["valid"] = False
        result["errors"].append("safety boundary is unsafe")
        result["blocked_reason"] = "unsafe_safety"

    try:
        if trade.status not in PAPER_TRADE_STATUSES:
            result["valid"] = False
            result["errors"].append(f"invalid status: {trade.status}")
            result["blocked_reason"] = "invalid_status"
    except AttributeError:
        result["valid"] = False
        result["errors"].append("status is required")
        result["blocked_reason"] = "missing_status"

    if trade.status in ("candidate", "previewed", "queued") and trade.blocked_reason not in ("", "none", None):
        result["warnings"].append("blocked_reason set while trade is not terminal")

    if not result["valid"]:
        if not result["errors"]:
            result["errors"].append("invalid trade state")
        if result["blocked_reason"] == "none":
            result["blocked_reason"] = "validation_failure"
        result["paper_only"] = False
        result["next_safe_action"] = "Fix the listed validation errors and retry."

    return result


def _append_lifecycle_event(
    trade: PaperTradeLifecycle,
    event: Dict[str, Any],
) -> List[Dict[str, Any]]:
    next_history = list(trade.lifecycle_history or [])
    next_history.append(event)
    return next_history


def _next_safe_action_for_status(status: str) -> str:
    if status in (PaperTradeStatus.CLOSED, PaperTradeStatus.KILLED, PaperTradeStatus.EXPIRED, PaperTradeStatus.ERROR, PaperTradeStatus.REJECTED):
        return "No further transition is allowed from terminal statuses."
    return f"Advance lifecycle via allowed transitions toward {PaperTradeStatus.ACTIVE} then terminal close."


def transition_paper_trade(
    trade: PaperTradeLifecycle,
    new_status: str,
    *,
    timestamp: Optional[str] = None,
    reason: Optional[str] = None,
    realized_pnl: Optional[float] = None,
    evidence_path: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> PaperTradeLifecycle:
    validation = validate_paper_trade(trade)
    if not validation["valid"]:
        raise ValueError(f"Invalid current trade: {'; '.join(validation['errors'])}")

    if new_status not in PAPER_TRADE_STATUSES:
        raise ValueError(f"Invalid target status: {new_status}")

    allowed_next = PAPER_TRADE_ALLOWED_TRANSITIONS.get(trade.status, set())
    if new_status not in allowed_next:
        raise ValueError(f"Blocked transition from {trade.status} to {new_status}")

    event_ts = _as_timestamp(timestamp or utc_now_iso())
    lifecycle_history = trade.lifecycle_history
    if not (trade.status == PaperTradeStatus.OPENED and new_status == PaperTradeStatus.ACTIVE):
        lifecycle_history = _append_lifecycle_event(
            trade,
            {
                "event": "status_transition",
                "from_status": trade.status,
                "to_status": new_status,
                "timestamp": event_ts,
                "reason": reason or "none",
                "evidence_path": str(evidence_path or trade.evidence_path),
                "metadata": dict(metadata or {}),
            },
        )
    updates: Dict[str, Any] = {
        "status": new_status,
        "lifecycle_history": lifecycle_history,
    }

    if new_status in (PaperTradeStatus.OPENED, PaperTradeStatus.ACTIVE) and trade.opened_timestamp is None:
        updates["opened_timestamp"] = event_ts

    if new_status in (PaperTradeStatus.CLOSED, PaperTradeStatus.KILLED, PaperTradeStatus.EXPIRED, PaperTradeStatus.ERROR):
        if trade.closed_timestamp is None:
            updates["closed_timestamp"] = event_ts
        if reason is not None:
            updates["close_reason"] = reason

    if realized_pnl is not None:
        updates["realized_pnl"] = _as_float(realized_pnl)

    if evidence_path is not None:
        updates["evidence_path"] = str(evidence_path)

    if metadata:
        updates["metadata"] = {**trade.metadata, **metadata}

    if reason is not None and reason in (TradeCloseReason.STOP_LOSS, TradeCloseReason.TAKE_PROFIT):
        updates["close_reason"] = reason

    updated_trade = replace(
        trade,
        paper_only=True,
        safety=_paper_safety(),
        **updates,
    )
    updated_trade.blocked_reason = "none"
    updated_trade.blocked_reason = (
        "none" if validation["blocked_reason"] == "none" else validation["blocked_reason"]
    )

    return updated_trade


def paper_trade_to_dict(trade: PaperTradeLifecycle) -> Dict[str, Any]:
    payload = asdict(trade)
    payload["safety"] = _paper_safety()
    payload["paper_only"] = True
    payload["paper_trade_model_version"] = "forex-paper-trade-model-v1"
    payload["lifecycle_events_count"] = len(trade.lifecycle_history)
    payload["next_safe_action"] = _next_safe_action_for_status(trade.status)
    return payload


def paper_trade_from_dict(payload: Dict[str, Any]) -> PaperTradeLifecycle:
    trade_payload = dict(payload or {})
    return build_paper_trade(
        trade_id=trade_payload.get("trade_id", ""),
        pair=trade_payload.get("pair", ""),
        direction=trade_payload.get("direction", ""),
        entry_type=trade_payload.get("entry_type", ""),
        entry_price=_as_float(trade_payload.get("entry_price", 0.0)),
        stop_loss=_as_float(trade_payload.get("stop_loss", 0.0)),
        take_profit=_as_float(trade_payload.get("take_profit", 0.0)),
        units=_as_float(trade_payload.get("units", 0.0)),
        dollar_risk=_as_float(trade_payload.get("dollar_risk", 0.0)),
        percent_risk=_as_float(trade_payload.get("percent_risk", 0.0)),
        status=_validate_status(trade_payload.get("status", PaperTradeStatus.CANDIDATE)),
        created_timestamp=trade_payload.get("created_timestamp"),
        opened_timestamp=trade_payload.get("opened_timestamp"),
        closed_timestamp=trade_payload.get("closed_timestamp"),
        close_reason=trade_payload.get("close_reason", TradeCloseReason.NONE),
        realized_pnl=_as_float(trade_payload.get("realized_pnl", 0.0)),
        evidence_path=trade_payload.get("evidence_path", ""),
        blocked_reason=trade_payload.get("blocked_reason", "none"),
        lifecycle_history=list(trade_payload.get("lifecycle_history", [])),
        metadata=dict(trade_payload.get("metadata", {})),
    )


def _paper_trade_realized_pl(trade: Mapping[str, Any], exit_price: float) -> float:
    entry = float(trade.get("entry", 0.0))
    units = float(trade.get("units", 0.0))
    if trade.get("direction") == "sell":
        return round((entry - float(exit_price)) * units, 8)
    return round((float(exit_price) - entry) * units, 8)


def create_paper_trade(
    trade_id: str,
    symbol: str,
    direction: str,
    entry: float,
    stop: float,
    target: float,
    units: float,
    risk_dollars: float,
    risk_percent: float,
    timestamp: str = "2026-01-01T00:00:00Z",
    status: str = "candidate",
) -> Dict[str, Any]:
    """Create a simple serializable paper trade for engine-spine workflows."""
    reasons: list[str] = []
    if status not in PAPER_TRADE_STATUSES:
        reasons.append("invalid_status")
    if direction not in {"buy", "sell"}:
        reasons.append("invalid_direction")
    if float(units) <= 0:
        reasons.append("invalid_units")
    if stop == entry:
        reasons.append("invalid_stop")
    return {
        "trade_id": trade_id,
        "symbol": symbol,
        "direction": direction,
        "entry": round(float(entry), 8),
        "stop": round(float(stop), 8),
        "target": round(float(target), 8),
        "units": round(float(units), 8),
        "risk_dollars": round(float(risk_dollars), 8),
        "risk_percent": round(float(risk_percent), 8),
        "status": status,
        "created_at": timestamp,
        "opened_at": None,
        "closed_at": None,
        "close_reason": None,
        "realized_pl": 0.0,
        "valid": not reasons,
        "rejection_reasons": reasons,
        "paper_only": True,
    }


def open_paper_trade(
    trade: Mapping[str, Any],
    timestamp: str = "2026-01-01T00:00:00Z",
) -> Dict[str, Any]:
    """Open a candidate, previewed, or queued paper trade."""
    result = dict(trade)
    if result.get("status") not in {"candidate", "previewed", "queued", "opened"}:
        result["valid"] = False
        result["rejection_reasons"] = list(result.get("rejection_reasons", [])) + ["invalid_open_transition"]
        return result
    result["status"] = "active"
    result["opened_at"] = timestamp
    result["valid"] = True
    result["rejection_reasons"] = []
    return result


def close_paper_trade(
    trade: Mapping[str, Any],
    exit_price: float,
    close_reason: str,
    timestamp: str = "2026-01-01T00:00:00Z",
) -> Dict[str, Any]:
    """Close an active paper trade and calculate realized P/L."""
    result = dict(trade)
    if result.get("status") not in {"active", "opened"}:
        result["valid"] = False
        result["rejection_reasons"] = list(result.get("rejection_reasons", [])) + ["invalid_close_transition"]
        return result
    result["status"] = "closed"
    result["exit"] = round(float(exit_price), 8)
    result["closed_at"] = timestamp
    result["close_reason"] = close_reason
    result["realized_pl"] = _paper_trade_realized_pl(result, float(exit_price))
    result["valid"] = True
    result["rejection_reasons"] = []
    return result


def process_price_update(
    trade: Mapping[str, Any],
    price: float,
    timestamp: str = "2026-01-01T00:00:00Z",
    manual_close: bool = False,
    expired: bool = False,
) -> Dict[str, Any]:
    """Process a deterministic price update for stop, target, expiry, or manual close."""
    result = dict(trade)
    if result.get("status") not in {"active", "opened"}:
        result["valid"] = False
        result["rejection_reasons"] = list(result.get("rejection_reasons", [])) + ["trade_not_active"]
        return result
    direction = result.get("direction")
    close_reason_value: str | None = None
    price_value = float(price)
    if manual_close:
        close_reason_value = "manual_close"
    elif expired:
        close_reason_value = "expiry"
    elif direction == "buy" and price_value <= float(result["stop"]):
        close_reason_value = "stop_loss"
        price_value = float(result["stop"])
    elif direction == "buy" and price_value >= float(result["target"]):
        close_reason_value = "take_profit"
        price_value = float(result["target"])
    elif direction == "sell" and price_value >= float(result["stop"]):
        close_reason_value = "stop_loss"
        price_value = float(result["stop"])
    elif direction == "sell" and price_value <= float(result["target"]):
        close_reason_value = "take_profit"
        price_value = float(result["target"])
    if close_reason_value:
        return close_paper_trade(result, price_value, close_reason_value, timestamp)
    result["last_price"] = round(price_value, 8)
    result["valid"] = True
    result["rejection_reasons"] = []
    return result
