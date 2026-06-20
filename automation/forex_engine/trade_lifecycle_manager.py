"""Paper-only trade lifecycle close manager."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from automation.forex_engine.paper_trade_lifecycle import paper_trade_to_dict, transition_paper_trade

TRADE_LIFECYCLE_MODE = "PAPER_ONLY"
TRADE_LIFECYCLE_ALLOWED = "allowed"
TRADE_LIFECYCLE_BLOCKED = "blocked"

CLOSE_REASON_STOP_LOSS = "stop_loss"
CLOSE_REASON_TAKE_PROFIT = "take_profit"
CLOSE_REASON_MANUAL_CLOSE = "manual_close"
CLOSE_REASON_EXPIRY = "expiry"
CLOSE_REASON_KILL_SWITCH = "kill_switch"
CLOSE_REASON_ERROR = "error"
CLOSE_REASON_NONE = "none"

REASON_NONE = "none"
REASON_INVALID_TRADE = "invalid_trade"
REASON_INVALID_PRICE_UPDATE = "invalid_price_update"
REASON_NON_PAPER_MODE = "non_paper_mode"
REASON_LIVE_TRADING_BLOCKED = "live_trading_blocked"
REASON_TRADE_NOT_ACTIVE = "trade_not_active"
REASON_MISSING_PAIR = "missing_pair"
REASON_MISSING_DIRECTION = "missing_direction"
REASON_MISSING_UNITS = "missing_units"
REASON_MISSING_ENTRY_PRICE = "missing_entry_price"
REASON_MISSING_STOP_LOSS = "missing_stop_loss"
REASON_MISSING_TAKE_PROFIT = "missing_take_profit"
REASON_MISSING_PRICE = "missing_price"
REASON_INVALID_MANUAL_CLOSE_PRICE = "invalid_manual_close_price"
REASON_INVALID_EXPIRY = "invalid_expiry"
REASON_UNSUPPORTED_CLOSE_REASON = "unsupported_close_reason"
REASON_EVIDENCE_PATH_INVALID = "evidence_path_invalid"


def _coerce_str(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip()
    return None


def _coerce_upper(value: Any) -> str | None:
    value_str = _coerce_str(value)
    return value_str.upper() if value_str else None


def _coerce_lower(value: Any) -> str | None:
    value_str = _coerce_str(value)
    return value_str.lower() if value_str else None


def _coerce_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def _coerce_positive_float(value: Any) -> float | None:
    as_float = _coerce_float(value)
    if as_float is None or as_float <= 0:
        return None
    return as_float


def _coerce_non_negative_float(value: Any) -> float | None:
    as_float = _coerce_float(value)
    if as_float is None or as_float < 0:
        return None
    return as_float


def _safe_safety_dict() -> dict[str, bool]:
    return {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }


def _safe_relative_path(path_value: Any) -> tuple[bool, str | None]:
    if path_value is None:
        return True, None
    if not isinstance(path_value, str):
        return False, None
    path = path_value.strip()
    if path == "":
        return True, path
    if path.startswith(("/", "\\")) or ":" in path or "\\\\" in path:
        return False, path
    return True, path


def _dedupe(values: list[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        if value not in out:
            out.append(value)
    return out


def _get_field(value: Any, key: str) -> Any:
    if isinstance(value, Mapping):
        return value.get(key)
    return getattr(value, key, None)


def _get_trade_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        try:
            return dict(value.to_dict())
        except Exception:
            pass
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    try:
        return paper_trade_to_dict(value)
    except Exception:
        return {}


def _next_safe_action(first_reason: str | None) -> str:
    if not first_reason or first_reason == REASON_NONE:
        return "continue_monitoring"
    actions = {
        REASON_NON_PAPER_MODE: "use_paper_only_inputs",
        REASON_LIVE_TRADING_BLOCKED: "remove_live_mode_inputs",
        REASON_TRADE_NOT_ACTIVE: "provide_active_or_opened_trade",
        REASON_MISSING_PAIR: "provide_pair",
        REASON_MISSING_DIRECTION: "provide_direction",
        REASON_MISSING_UNITS: "provide_units",
        REASON_MISSING_ENTRY_PRICE: "provide_entry_price",
        REASON_MISSING_STOP_LOSS: "provide_stop_loss",
        REASON_MISSING_TAKE_PROFIT: "provide_take_profit",
        REASON_MISSING_PRICE: "provide_price_update",
        REASON_INVALID_PRICE_UPDATE: "provide_valid_price_update",
        REASON_INVALID_MANUAL_CLOSE_PRICE: "provide_valid_manual_close_price",
        REASON_INVALID_EXPIRY: "provide_valid_expiry",
        REASON_UNSUPPORTED_CLOSE_REASON: "fix_existing_close_reason",
        REASON_INVALID_TRADE: "provide_valid_trade_payload",
        REASON_EVIDENCE_PATH_INVALID: "use_relative_evidence_path",
    }
    return actions.get(first_reason, "review_trade_update_inputs")


def _normalize_market_price(price_update: Any, direction: str | None) -> tuple[float | None, dict[str, Any]]:
    if not isinstance(price_update, Mapping):
        return None, {}
    bid = _coerce_positive_float(price_update.get("bid"))
    ask = _coerce_positive_float(price_update.get("ask"))
    price = _coerce_positive_float(price_update.get("price"))
    normalized = {
        "bid": bid,
        "ask": ask,
        "price": price,
    }
    if direction == "buy":
        return bid or price, normalized
    if direction == "sell":
        return ask or price, normalized
    return price, normalized


def _close_reason_for_direction(direction: str | None, selected_price: float | None, stop_loss: float, take_profit: float) -> str | None:
    if selected_price is None:
        return None
    if direction == "buy":
        if selected_price <= stop_loss:
            return CLOSE_REASON_STOP_LOSS
        if selected_price >= take_profit:
            return CLOSE_REASON_TAKE_PROFIT
    elif direction == "sell":
        if selected_price >= stop_loss:
            return CLOSE_REASON_STOP_LOSS
        if selected_price <= take_profit:
            return CLOSE_REASON_TAKE_PROFIT
    return None


def _calc_realized_pnl(direction: str | None, entry_price: float, exit_price: float, units: float) -> float:
    if direction == "buy":
        return round((exit_price - entry_price) * units, 12)
    if direction == "sell":
        return round((entry_price - exit_price) * units, 12)
    return 0.0


def _safe_transition(
    trade: Any,
    next_status: str,
    timestamp: float,
    close_reason: str,
    realized_pnl: float,
) -> tuple[Any, bool]:
    try:
        transitioned = transition_paper_trade(
            trade,
            next_status,
            timestamp=timestamp,
            reason=close_reason,
            realized_pnl=realized_pnl,
        )
        return transitioned, True
    except Exception:
        try:
            setattr(trade, "status", next_status)
            setattr(trade, "close_reason", close_reason)
            setattr(trade, "closed_timestamp", timestamp)
            setattr(trade, "realized_pnl", realized_pnl)
            history = list(getattr(trade, "lifecycle_history", []))
            if next_status not in history:
                history.append(next_status)
            setattr(trade, "lifecycle_history", history)
            return trade, True
        except Exception:
            if isinstance(trade, dict):
                trade["status"] = next_status
                trade["close_reason"] = close_reason
                trade["closed_timestamp"] = timestamp
                trade["realized_pnl"] = realized_pnl
                history = list(trade.get("lifecycle_history", []))
                if next_status not in history:
                    history.append(next_status)
                trade["lifecycle_history"] = history
                return trade, False
    return trade, False


@dataclass(frozen=True)
class TradeLifecycleManagerDecision:
    allowed: bool
    decision: str
    blocked_reason: str
    blocked_reasons: list[str]
    warnings: list[str]
    paper_only: bool
    mode: str
    trade_id: str | None
    pair: str | None
    direction: str | None
    status: str
    previous_status: str | None
    closed: bool
    close_reason: str
    entry_price: float | None
    exit_price: float | None
    units: float
    realized_pnl: float
    opened_timestamp: float | None
    closed_timestamp: float | None
    price_update: dict[str, Any] | None
    trade: dict[str, Any]
    lifecycle_result: dict[str, Any]
    evidence: dict[str, Any]
    evidence_path: str | None
    safety: dict[str, bool]
    next_safe_action: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def process_trade_update(
    trade: Any,
    price_update: Any = None,
    timestamp: Any = None,
    manual_close_price: Any = None,
    expire_at: Any = None,
    kill_switch: bool = False,
    evidence_path: Any = None,
    metadata: Any = None,
) -> dict[str, Any]:
    warnings: list[str] = []
    blocked_reasons: list[str] = []

    if not isinstance(trade, (Mapping, object)):
        return TradeLifecycleManagerDecision(
            allowed=False,
            decision=TRADE_LIFECYCLE_BLOCKED,
            blocked_reason=REASON_INVALID_TRADE,
            blocked_reasons=[REASON_INVALID_TRADE],
            warnings=warnings,
            paper_only=True,
            mode=TRADE_LIFECYCLE_MODE,
            trade_id=None,
            pair=None,
            direction=None,
            status="candidate",
            previous_status=None,
            closed=False,
            close_reason=CLOSE_REASON_NONE,
            entry_price=None,
            exit_price=None,
            units=0.0,
            realized_pnl=0.0,
            opened_timestamp=None,
            closed_timestamp=None,
            price_update=None,
            trade={},
            lifecycle_result={},
            evidence={},
            evidence_path=None,
            safety=_safe_safety_dict(),
            next_safe_action=_next_safe_action(REASON_INVALID_TRADE),
            metadata={
                "reason": "invalid_trade_type",
                "timestamp": timestamp,
            },
        ).to_dict()

    trade_dict = _get_trade_dict(trade)
    trade_id = _coerce_str(_get_field(trade, "trade_id"))
    pair = _coerce_upper(_get_field(trade, "pair"))
    direction = _coerce_lower(_get_field(trade, "direction"))
    status = _coerce_lower(_get_field(trade, "status")) or "candidate"
    paper_only = _get_field(trade, "paper_only")
    mode = _coerce_lower(_get_field(trade, "mode")) or TRADE_LIFECYCLE_MODE
    entry_price = _coerce_positive_float(_get_field(trade, "entry_price"))
    units = _coerce_positive_float(_get_field(trade, "units"))
    stop_loss = _coerce_positive_float(_get_field(trade, "stop_loss"))
    take_profit = _coerce_positive_float(_get_field(trade, "take_profit"))
    opened_timestamp = _coerce_float(_get_field(trade, "opened_timestamp"))
    closed_timestamp = _coerce_float(_get_field(trade, "closed_timestamp"))
    existing_close_reason = _coerce_str(_get_field(trade, "close_reason")) or CLOSE_REASON_NONE
    ts = _coerce_float(timestamp)
    if ts is None:
        ts = 0.0

    valid_path, evidence_path_value = _safe_relative_path(evidence_path)
    if not valid_path:
        blocked_reasons.append(REASON_EVIDENCE_PATH_INVALID)

    if paper_only is False:
        blocked_reasons.append(REASON_NON_PAPER_MODE)
    if mode in {"live", "demo", "broker"}:
        blocked_reasons.append(REASON_LIVE_TRADING_BLOCKED)
    if status not in {"active", "opened"}:
        blocked_reasons.append(REASON_TRADE_NOT_ACTIVE)
    if not pair:
        blocked_reasons.append(REASON_MISSING_PAIR)
    if direction not in {"buy", "sell"}:
        blocked_reasons.append(REASON_MISSING_DIRECTION)
    if units is None:
        blocked_reasons.append(REASON_MISSING_UNITS)
    if entry_price is None:
        blocked_reasons.append(REASON_MISSING_ENTRY_PRICE)
    if stop_loss is None:
        blocked_reasons.append(REASON_MISSING_STOP_LOSS)
    if take_profit is None:
        blocked_reasons.append(REASON_MISSING_TAKE_PROFIT)
    if existing_close_reason not in {
        CLOSE_REASON_NONE,
        CLOSE_REASON_STOP_LOSS,
        CLOSE_REASON_TAKE_PROFIT,
        CLOSE_REASON_MANUAL_CLOSE,
        CLOSE_REASON_EXPIRY,
        CLOSE_REASON_KILL_SWITCH,
        CLOSE_REASON_ERROR,
    }:
        blocked_reasons.append(REASON_UNSUPPORTED_CLOSE_REASON)

    selected_price, normalized_price_update = _normalize_market_price(price_update, direction)
    has_valid_price_update = price_update is not None and bool(normalized_price_update)
    if has_valid_price_update and all(v is None for v in normalized_price_update.values()):
        blocked_reasons.append(REASON_INVALID_PRICE_UPDATE)

    manual_price = _coerce_positive_float(manual_close_price)
    if manual_close_price is not None and manual_price is None:
        blocked_reasons.append(REASON_INVALID_MANUAL_CLOSE_PRICE)

    if expire_at is not None:
        expire_ts = _coerce_float(expire_at)
        if expire_ts is None or expire_ts <= 0:
            blocked_reasons.append(REASON_INVALID_EXPIRY)
    else:
        expire_ts = None

    if blocked_reasons:
        blocked_reasons = _dedupe(blocked_reasons)
        return TradeLifecycleManagerDecision(
            allowed=False,
            decision=TRADE_LIFECYCLE_BLOCKED,
            blocked_reason=blocked_reasons[0],
            blocked_reasons=blocked_reasons,
            warnings=warnings,
            paper_only=True,
            mode=TRADE_LIFECYCLE_MODE,
            trade_id=trade_id,
            pair=pair,
            direction=direction,
            status=status,
            previous_status=None,
            closed=False,
            close_reason=CLOSE_REASON_NONE,
            entry_price=entry_price,
            exit_price=None,
            units=units or 0.0,
            realized_pnl=0.0,
            opened_timestamp=opened_timestamp,
            closed_timestamp=closed_timestamp,
            price_update=normalized_price_update if has_valid_price_update else None,
            trade=trade_dict,
            lifecycle_result={},
            evidence={},
            evidence_path=evidence_path_value,
            safety=_safe_safety_dict(),
            next_safe_action=_next_safe_action(blocked_reasons[0]),
            metadata={
                "timestamp": ts,
                "expire_at": expire_ts,
                **(dict(metadata) if isinstance(metadata, Mapping) else {}),
            },
        ).to_dict()

    close_reason = CLOSE_REASON_NONE
    close_price: float | None = None

    if manual_price is not None:
        close_reason = CLOSE_REASON_MANUAL_CLOSE
        close_price = manual_price
    elif kill_switch:
        if selected_price is None and manual_price is None:
            return TradeLifecycleManagerDecision(
                allowed=False,
                decision=TRADE_LIFECYCLE_BLOCKED,
                blocked_reason=REASON_MISSING_PRICE,
                blocked_reasons=[REASON_MISSING_PRICE],
                warnings=warnings,
                paper_only=True,
                mode=TRADE_LIFECYCLE_MODE,
                trade_id=trade_id,
                pair=pair,
                direction=direction,
                status=status,
                previous_status=None,
                closed=False,
                close_reason=CLOSE_REASON_NONE,
                entry_price=entry_price,
                exit_price=None,
                units=units or 0.0,
                realized_pnl=0.0,
                opened_timestamp=opened_timestamp,
                closed_timestamp=closed_timestamp,
                price_update=normalized_price_update or None,
                trade=trade_dict,
                lifecycle_result={},
                evidence={},
                evidence_path=evidence_path_value,
                safety=_safe_safety_dict(),
                next_safe_action=_next_safe_action(REASON_MISSING_PRICE),
                metadata={
                    "timestamp": ts,
                    "kill_switch": True,
                    **(dict(metadata) if isinstance(metadata, Mapping) else {}),
                },
            ).to_dict()
        close_reason = CLOSE_REASON_KILL_SWITCH
        close_price = selected_price
    elif expire_ts is not None and ts >= expire_ts:
        if selected_price is None:
            return TradeLifecycleManagerDecision(
                allowed=False,
                decision=TRADE_LIFECYCLE_BLOCKED,
                blocked_reason=REASON_MISSING_PRICE,
                blocked_reasons=[REASON_MISSING_PRICE],
                warnings=warnings,
                paper_only=True,
                mode=TRADE_LIFECYCLE_MODE,
                trade_id=trade_id,
                pair=pair,
                direction=direction,
                status=status,
                previous_status=None,
                closed=False,
                close_reason=CLOSE_REASON_NONE,
                entry_price=entry_price,
                exit_price=None,
                units=units or 0.0,
                realized_pnl=0.0,
                opened_timestamp=opened_timestamp,
                closed_timestamp=closed_timestamp,
                price_update=normalized_price_update or None,
                trade=trade_dict,
                lifecycle_result={},
                evidence={},
                evidence_path=evidence_path_value,
                safety=_safe_safety_dict(),
                next_safe_action=_next_safe_action(REASON_MISSING_PRICE),
                metadata={
                    "timestamp": ts,
                    "expire_at": expire_ts,
                    "kill_switch": False,
                    **(dict(metadata) if isinstance(metadata, Mapping) else {}),
                },
            ).to_dict()
        close_reason = CLOSE_REASON_EXPIRY
        close_price = selected_price
    else:
        candidate_close = _close_reason_for_direction(direction, selected_price, stop_loss, take_profit)
        if candidate_close is not None:
            close_reason = candidate_close
            close_price = selected_price

    if close_reason == CLOSE_REASON_NONE:
        return TradeLifecycleManagerDecision(
            allowed=True,
            decision=TRADE_LIFECYCLE_ALLOWED,
            blocked_reason=REASON_NONE,
            blocked_reasons=[],
            warnings=warnings,
            paper_only=True,
            mode=TRADE_LIFECYCLE_MODE,
            trade_id=trade_id,
            pair=pair,
            direction=direction,
            status=status,
            previous_status=status,
            closed=False,
            close_reason=CLOSE_REASON_NONE,
            entry_price=entry_price,
            exit_price=None,
            units=units or 0.0,
            realized_pnl=0.0,
            opened_timestamp=opened_timestamp,
            closed_timestamp=None,
            price_update=normalized_price_update or None,
            trade=trade_dict,
            lifecycle_result={"status": status, "history": trade_dict.get("lifecycle_history", [])},
            evidence={
                "trade_id": trade_id,
                "status": status,
                "event": "monitor",
                "reason": CLOSE_REASON_NONE,
                "timestamp": ts,
                "mode": TRADE_LIFECYCLE_MODE,
            },
            evidence_path=evidence_path_value,
            safety=_safe_safety_dict(),
            next_safe_action="continue_monitoring",
            metadata={
                "timestamp": ts,
                "kill_switch": kill_switch,
                "expire_at": expire_ts,
                **(dict(metadata) if isinstance(metadata, Mapping) else {}),
            },
        ).to_dict()

    realized_pnl = _calc_realized_pnl(direction, entry_price or 0.0, close_price, units or 0.0)
    target_status = {
        CLOSE_REASON_STOP_LOSS: "closed",
        CLOSE_REASON_TAKE_PROFIT: "closed",
        CLOSE_REASON_MANUAL_CLOSE: "closed",
        CLOSE_REASON_EXPIRY: "expired",
        CLOSE_REASON_KILL_SWITCH: "killed",
        CLOSE_REASON_ERROR: "error",
    }[close_reason]

    updated_trade, _ = _safe_transition(trade, target_status, ts, close_reason, realized_pnl)
    updated_dict = _get_trade_dict(updated_trade)
    lifecycle_history = list(updated_dict.get("lifecycle_history", []))

    result_trade = updated_dict
    if not isinstance(result_trade, Mapping):
        result_trade = trade_dict

    return TradeLifecycleManagerDecision(
        allowed=True,
        decision=TRADE_LIFECYCLE_ALLOWED,
        blocked_reason=REASON_NONE,
        blocked_reasons=[],
        warnings=warnings,
        paper_only=True,
        mode=TRADE_LIFECYCLE_MODE,
        trade_id=trade_id,
        pair=pair,
        direction=direction,
        status=target_status,
        previous_status=status,
        closed=target_status in {"closed", "killed", "expired", "error"},
        close_reason=close_reason,
        entry_price=entry_price,
        exit_price=close_price,
        units=units or 0.0,
        realized_pnl=realized_pnl,
        opened_timestamp=opened_timestamp,
        closed_timestamp=ts,
        price_update=normalized_price_update or None,
        trade=result_trade,
        lifecycle_result={"status": target_status, "history": lifecycle_history + [target_status] if target_status not in lifecycle_history else lifecycle_history},
        evidence={
            "trade_id": trade_id,
            "close_reason": close_reason,
            "exit_price": close_price,
            "realized_pnl": realized_pnl,
            "timestamp": ts,
            "mode": TRADE_LIFECYCLE_MODE,
        },
        evidence_path=evidence_path_value,
        safety=_safe_safety_dict(),
        next_safe_action="prepare_accounting_update",
        metadata={
            "timestamp": ts,
            "target_status": target_status,
            "kill_switch": kill_switch,
            "expire_at": expire_ts,
            **(dict(metadata) if isinstance(metadata, Mapping) else {}),
        },
    ).to_dict()
