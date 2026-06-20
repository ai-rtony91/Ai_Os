"""Paper-only risk governor for forex trade previews."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional, Sequence


RISK_GOVERNOR_MODE = "PAPER_ONLY"
RISK_DECISION_ALLOWED = "allowed"
RISK_DECISION_BLOCKED = "blocked"

INVALID_PREVIEW_REASON = "invalid_preview"
INVALID_ACCOUNT_STATE_REASON = "invalid_account_state"
NON_PAPER_MODE_REASON = "non_paper_mode"
LIVE_TRADING_BLOCKED_REASON = "live_trading_blocked"
MISSING_STOP_LOSS_REASON = "missing_stop_loss"
MISSING_TAKE_PROFIT_REASON = "missing_take_profit"
INVALID_STOP_DISTANCE_REASON = "invalid_stop_distance"
INVALID_UNITS_REASON = "invalid_units"
INVALID_RISK_AMOUNT_REASON = "invalid_risk_amount"
EXCESSIVE_RISK_PER_TRADE_REASON = "excessive_risk_per_trade"
MAX_DAILY_LOSS_HIT_REASON = "max_daily_loss_hit"
MAX_OPEN_RISK_HIT_REASON = "max_open_risk_hit"
MAX_OPEN_TRADES_HIT_REASON = "max_open_trades_hit"
MAX_PAIR_EXPOSURE_HIT_REASON = "max_pair_exposure_hit"
SPREAD_TOO_HIGH_REASON = "spread_too_high"
STALE_MARKET_DATA_REASON = "stale_market_data"
COOLDOWN_AFTER_LOSS_REASON = "cooldown_after_loss"
DUPLICATE_SETUP_REASON = "duplicate_setup"
KILL_SWITCH_ACTIVE_REASON = "kill_switch_active"

TERMINAL_STATUSES = {"closed", "killed", "expired", "error", "rejected"}


def _paper_safety() -> Dict[str, bool]:
    return {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }


def _to_float(value: Any, *, default: Optional[float] = None) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: Any, *, default: Optional[int] = None) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _round_money(value: float) -> float:
    return round(float(value), 6)


def _to_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
        except ValueError:
            return None
    return None


def _utc_now(now_timestamp: Any = None) -> datetime:
    if now_timestamp is None:
        return datetime.now(timezone.utc)
    parsed = _to_datetime(now_timestamp)
    return parsed if parsed is not None else datetime.now(timezone.utc)


def _safe_get(payload: Any, key: str, default: Any = None) -> Any:
    if isinstance(payload, Mapping):
        return payload.get(key, default)
    return getattr(payload, key, default)


def _normalize_pair(pair: Any) -> str:
    return str(pair).strip().upper()


def _normalize_direction(direction: Any) -> str:
    return str(direction).strip().lower()


def _extract_dollar_risk(preview: Any, default: float = 0.0) -> float:
    keys = ("dollar_risk", "risk_dollars", "risk_amount", "risk_amount_usd")
    if isinstance(preview, Mapping):
        for key in keys:
            value = _to_float(preview.get(key), default=None)
            if value is not None:
                return value
        nested = preview.get("risk")
        if isinstance(nested, Mapping):
            for key in keys:
                value = _to_float(nested.get(key), default=None)
                if value is not None:
                    return value
    for key in keys:
        value = _to_float(_safe_get(preview, key, None), default=None)
        if value is not None:
            return value
    return default


def _extract_status(value: Any) -> str:
    return _normalize_direction(value)


def _pair_exposure_and_open_count(open_trades: Sequence[Any], pair: str) -> tuple[float, float, int]:
    open_exposure = 0.0
    pair_exposure = 0.0
    open_count = 0
    for trade in open_trades:
        if not isinstance(trade, Mapping):
            continue
        status = _extract_status(_safe_get(trade, "status", ""))
        if status in TERMINAL_STATUSES:
            continue
        open_count += 1
        trade_pair = _normalize_pair(_safe_get(trade, "pair", ""))
        units = _to_float(_safe_get(trade, "units", 0.0), default=0.0) or 0.0
        entry_price = _to_float(_safe_get(trade, "entry_price", 0.0), default=0.0) or 0.0
        exposure = abs(units * entry_price)
        open_exposure += exposure
        if trade_pair == pair:
            pair_exposure += exposure
    return _round_money(open_exposure), _round_money(pair_exposure), open_count


def _has_recent_loss(closed_trades: Sequence[Any], cooldown_seconds: float, now: datetime) -> bool:
    if cooldown_seconds <= 0:
        return False
    newest_loss = None
    for trade in closed_trades:
        if not isinstance(trade, Mapping):
            continue
        outcome = _normalize_direction(_safe_get(trade, "outcome", ""))
        close_reason = _normalize_direction(_safe_get(trade, "close_reason", ""))
        is_loss = outcome == "loss" or close_reason in {"stop_loss", "risk_block", "loss"}
        if not is_loss:
            continue
        closed_at = _to_datetime(_safe_get(trade, "closed_timestamp", None))
        if closed_at is None:
            continue
        if newest_loss is None or closed_at > newest_loss:
            newest_loss = closed_at
    if newest_loss is None:
        return False
    return (now - newest_loss).total_seconds() < cooldown_seconds


def _is_duplicate_setup(open_trades: Sequence[Any], pair: str, direction: str) -> bool:
    for trade in open_trades:
        if not isinstance(trade, Mapping):
            continue
        trade_status = _extract_status(_safe_get(trade, "status", ""))
        if trade_status not in {"previewed", "queued", "opened", "active"}:
            continue
        if _normalize_pair(_safe_get(trade, "pair", "")) != pair:
            continue
        if _normalize_direction(_safe_get(trade, "direction", "")) != direction:
            continue
        return True
    return False


@dataclass(frozen=True)
class RiskGovernorLimits:
    max_risk_per_trade_pct: float = 1.0
    max_daily_loss: float = 0.0
    max_open_risk: float = 0.0
    max_open_trades: int = 1
    max_pair_exposure: float = 0.0
    max_spread: float = 0.0
    max_data_age_seconds: float = 300.0
    cooldown_after_loss_seconds: float = 0.0
    duplicate_setup_block: bool = True

    @classmethod
    def from_payload(
        cls, payload: Optional[Mapping[str, Any]], account_state: Dict[str, Any]
    ) -> "RiskGovernorLimits":
        if payload is None:
            payload = {}
        max_daily_loss = _to_float(payload.get("max_daily_loss"), default=None)
        if max_daily_loss is None:
            max_daily_loss = _to_float(account_state.get("max_daily_loss"), default=0.0) or 0.0
        return cls(
            max_risk_per_trade_pct=_to_float(payload.get("max_risk_per_trade_pct"), default=cls.max_risk_per_trade_pct)
            or cls.max_risk_per_trade_pct,
            max_daily_loss=max_daily_loss,
            max_open_risk=_to_float(payload.get("max_open_risk"), default=cls.max_open_risk) or cls.max_open_risk,
            max_open_trades=_to_int(payload.get("max_open_trades"), default=cls.max_open_trades) or 0,
            max_pair_exposure=_to_float(payload.get("max_pair_exposure"), default=cls.max_pair_exposure) or cls.max_pair_exposure,
            max_spread=_to_float(payload.get("max_spread"), default=cls.max_spread) or cls.max_spread,
            max_data_age_seconds=_to_float(payload.get("max_data_age_seconds"), default=cls.max_data_age_seconds)
            or cls.max_data_age_seconds,
            cooldown_after_loss_seconds=_to_float(payload.get("cooldown_after_loss_seconds"), default=cls.cooldown_after_loss_seconds)
            or cls.cooldown_after_loss_seconds,
            duplicate_setup_block=bool(payload.get("duplicate_setup_block", cls.duplicate_setup_block)),
        )


@dataclass(frozen=True)
class RiskGovernorDecision:
    allowed: bool
    decision: str
    blocked_reason: str
    blocked_reasons: list[str]
    warnings: list[str]
    paper_only: bool
    mode: str
    pair: str
    dollar_risk: float
    percent_risk: float
    open_risk_after: float
    daily_loss_after: float
    open_trade_count_after: int
    pair_exposure_after: float
    max_risk_per_trade: float
    max_daily_loss: float
    max_open_risk: float
    max_open_trades: int
    max_pair_exposure: float
    max_spread: float
    data_age_seconds: Optional[float]
    safety: Dict[str, bool]
    next_safe_action: str
    metadata: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["safety"] = _paper_safety()
        payload["paper_only"] = True
        return payload


def evaluate_risk_preview(
    preview: Any,
    *,
    account_state: Optional[Dict[str, Any]] = None,
    open_trades: Optional[Sequence[Any]] = None,
    closed_trades: Optional[Sequence[Any]] = None,
    limits: Optional[Dict[str, Any]] = None,
    market_state: Optional[Dict[str, Any]] = None,
    now_timestamp: Optional[Any] = None,
) -> Dict[str, Any]:
    if not isinstance(preview, Mapping):
        return {
            "allowed": False,
            "decision": RISK_DECISION_BLOCKED,
            "blocked_reason": INVALID_PREVIEW_REASON,
            "blocked_reasons": [INVALID_PREVIEW_REASON],
            "warnings": [],
            "paper_only": True,
            "mode": RISK_GOVERNOR_MODE,
            "pair": "",
            "dollar_risk": 0.0,
            "percent_risk": 0.0,
            "open_risk_after": 0.0,
            "daily_loss_after": 0.0,
            "open_trade_count_after": 0,
            "pair_exposure_after": 0.0,
            "max_risk_per_trade": 0.0,
            "max_daily_loss": 0.0,
            "max_open_risk": 0.0,
            "max_open_trades": 0,
            "max_pair_exposure": 0.0,
            "max_spread": 0.0,
            "data_age_seconds": None,
            "safety": _paper_safety(),
            "next_safe_action": "Provide a valid preview dict to evaluate risk.",
            "metadata": {"source": "paper_trade_preview"},
        }

    account_state = account_state or {}
    open_trades = list(open_trades or [])
    closed_trades = list(closed_trades or [])
    market_state = market_state or {}
    now = _utc_now(now_timestamp)
    limits = RiskGovernorLimits.from_payload(limits, account_state)

    pair = _normalize_pair(_safe_get(preview, "pair", ""))
    direction = _normalize_direction(_safe_get(preview, "direction", ""))
    mode = _safe_get(preview, "mode", RISK_GOVERNOR_MODE)
    entry_price = _to_float(_safe_get(preview, "entry_price"), default=None)
    stop_loss = _to_float(_safe_get(preview, "stop_loss"), default=None)
    take_profit = _to_float(_safe_get(preview, "take_profit"), default=None)
    units = _to_float(_safe_get(preview, "units"), default=None)
    spread = _to_float(_safe_get(preview, "spread", 0.0), default=0.0) or 0.0
    percent_risk = _to_float(_safe_get(preview, "percent_risk"), default=0.0) or 0.0
    dollar_risk = _extract_dollar_risk(preview, default=0.0)
    preview_status = _extract_status(_safe_get(preview, "status", "candidate"))
    paper_only = bool(_safe_get(preview, "paper_only", True))
    data_timestamp = _safe_get(preview, "data_timestamp", None)
    if data_timestamp is None and hasattr(preview, "data_timestamp"):
        data_timestamp = _safe_get(preview, "data_timestamp", None)
    data_age_seconds = None
    parsed_data_time = _to_datetime(data_timestamp)
    if parsed_data_time is not None:
        data_age_seconds = (now - parsed_data_time).total_seconds()

    current_balance = _to_float(account_state.get("current_balance"), default=None)
    cash_balance = _to_float(account_state.get("cash_balance"), default=None)
    equity = _to_float(account_state.get("equity"), default=None)
    risk_base = None
    for candidate in (equity, current_balance, cash_balance):
        if candidate is not None:
            risk_base = candidate
            break
    if risk_base is None:
        risk_base = _to_float(account_state.get("starting_balance"), default=0.0) or 0.0
    else:
        risk_base = candidate

    open_risk = _to_float(account_state.get("open_risk"), default=0.0) or 0.0
    daily_loss_used = _to_float(account_state.get("daily_loss_used"), default=0.0) or 0.0
    max_daily_loss = _to_float(account_state.get("max_daily_loss"), default=limits.max_daily_loss) or limits.max_daily_loss
    kill_switch = bool(account_state.get("kill_switch_active", False))

    open_risk_after_base, pair_exposure_after, open_trade_count = _pair_exposure_and_open_count(open_trades, pair)
    open_risk_after = _round_money((open_risk or 0.0) + (dollar_risk or 0.0))
    pair_exposure_after = _round_money(pair_exposure_after + abs((units or 0.0) * (entry_price or 0.0)))
    daily_loss_after = _round_money((daily_loss_used or 0.0) + max(0.0, dollar_risk or 0.0))
    max_risk_per_trade = _round_money(risk_base * (limits.max_risk_per_trade_pct / 100.0))

    blocked_reasons: list[str] = []
    warnings: list[str] = []

    if not pair:
        blocked_reasons.append(INVALID_PREVIEW_REASON)
    elif pair.replace("-", "").isalpha() is False:
        blocked_reasons.append(INVALID_PREVIEW_REASON)

    if mode != RISK_GOVERNOR_MODE:
        if mode in {"live", "demo", "broker"}:
            blocked_reasons.append(LIVE_TRADING_BLOCKED_REASON)
        else:
            blocked_reasons.append(NON_PAPER_MODE_REASON)

    if paper_only is False:
        blocked_reasons.append(NON_PAPER_MODE_REASON)

    if direction not in {"buy", "sell"}:
        blocked_reasons.append(INVALID_PREVIEW_REASON)

    if entry_price is None or entry_price <= 0:
        blocked_reasons.append(INVALID_PREVIEW_REASON)
    if stop_loss is None:
        blocked_reasons.append(MISSING_STOP_LOSS_REASON)
    if take_profit is None:
        blocked_reasons.append(MISSING_TAKE_PROFIT_REASON)
    if units is None or units <= 0:
        blocked_reasons.append(INVALID_UNITS_REASON)

    if dollar_risk < 0 or percent_risk < 0:
        blocked_reasons.append(INVALID_RISK_AMOUNT_REASON)

    if stop_loss is not None and entry_price is not None and entry_price > 0 and take_profit is not None:
        if direction == "buy":
            if stop_loss >= entry_price or take_profit <= entry_price:
                blocked_reasons.append(INVALID_STOP_DISTANCE_REASON)
        elif direction == "sell":
            if stop_loss <= entry_price or take_profit >= entry_price:
                blocked_reasons.append(INVALID_STOP_DISTANCE_REASON)

    if limits.max_spread > 0 and spread > limits.max_spread:
        blocked_reasons.append(SPREAD_TOO_HIGH_REASON)

    for key in (
        _to_float(account_state.get("equity"), default=None),
        _to_float(account_state.get("cash_balance"), default=None),
        _to_float(account_state.get("current_balance"), default=None),
        _to_float(account_state.get("open_risk"), default=None),
        _to_float(account_state.get("daily_loss_used"), default=None),
        max_daily_loss,
    ):
        if key is not None and key < 0:
            blocked_reasons.append(INVALID_ACCOUNT_STATE_REASON)
            break

    if percent_risk > limits.max_risk_per_trade_pct:
        blocked_reasons.append(EXCESSIVE_RISK_PER_TRADE_REASON)
    if risk_base is not None and risk_base > 0:
        if limits.max_risk_per_trade_pct > 0 and (dollar_risk or 0.0) > max_risk_per_trade:
            blocked_reasons.append(EXCESSIVE_RISK_PER_TRADE_REASON)
    if limits.max_daily_loss > 0 and daily_loss_after >= limits.max_daily_loss:
        blocked_reasons.append(MAX_DAILY_LOSS_HIT_REASON)
    if limits.max_open_risk > 0 and open_risk_after > limits.max_open_risk:
        blocked_reasons.append(MAX_OPEN_RISK_HIT_REASON)
    if limits.max_open_trades > 0 and open_trade_count + 1 > limits.max_open_trades:
        blocked_reasons.append(MAX_OPEN_TRADES_HIT_REASON)
    if limits.max_pair_exposure > 0 and pair_exposure_after > limits.max_pair_exposure:
        blocked_reasons.append(MAX_PAIR_EXPOSURE_HIT_REASON)
    if data_age_seconds is not None and limits.max_data_age_seconds > 0 and data_age_seconds > limits.max_data_age_seconds:
        blocked_reasons.append(STALE_MARKET_DATA_REASON)
    if _has_recent_loss(closed_trades, limits.cooldown_after_loss_seconds, now):
        blocked_reasons.append(COOLDOWN_AFTER_LOSS_REASON)
    if limits.duplicate_setup_block and _is_duplicate_setup(open_trades, pair, direction):
        blocked_reasons.append(DUPLICATE_SETUP_REASON)
    if kill_switch:
        blocked_reasons.append(KILL_SWITCH_ACTIVE_REASON)

    blocked_reasons = list(dict.fromkeys(blocked_reasons))
    allowed = not blocked_reasons
    blocked_reason = blocked_reasons[0] if blocked_reasons else "none"
    decision = RISK_DECISION_ALLOWED if allowed else RISK_DECISION_BLOCKED
    next_safe_action = (
        "Fix risk/review constraints before paper execution."
        if not allowed
        else "Proceed to paper fill after required validations."
    )

    if blocked_reasons:
        for must in (INVALID_PREVIEW_REASON, INVALID_ACCOUNT_STATE_REASON, KILL_SWITCH_ACTIVE_REASON):
            if must in blocked_reasons:
                blocked_reason = must
                break

    return {
        "allowed": allowed,
        "decision": decision,
        "blocked_reason": blocked_reason,
        "blocked_reasons": blocked_reasons,
        "warnings": warnings,
        "paper_only": True,
        "mode": RISK_GOVERNOR_MODE,
        "pair": pair,
        "dollar_risk": _round_money(dollar_risk or 0.0),
        "percent_risk": _round_money(percent_risk),
        "open_risk_after": open_risk_after,
        "daily_loss_after": daily_loss_after,
        "open_trade_count_after": int(open_trade_count + 1),
        "pair_exposure_after": pair_exposure_after,
        "max_risk_per_trade": max_risk_per_trade,
        "max_daily_loss": _round_money(max_daily_loss),
        "max_open_risk": _round_money(limits.max_open_risk),
        "max_open_trades": int(limits.max_open_trades),
        "max_pair_exposure": _round_money(limits.max_pair_exposure),
        "max_spread": _round_money(limits.max_spread),
        "data_age_seconds": None if data_age_seconds is None else _round_money(max(0.0, data_age_seconds)),
        "safety": _paper_safety(),
        "next_safe_action": next_safe_action,
        "metadata": {
            "source": "paper_trade_preview",
            "risk_base": _round_money(risk_base),
            "open_risk": _round_money(open_risk),
            "pair_exposure_base": _round_money(pair_exposure_after - abs((units or 0.0) * (entry_price or 0.0))),
            "market_data": {k: market_state.get(k) for k in ("source", "provider") if k in market_state},
        },
    }
