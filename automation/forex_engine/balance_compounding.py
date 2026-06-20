"""Paper-only balance updates and compounding helper for closed Forex trades."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

BALANCE_COMPOUNDING_MODE = "PAPER_ONLY"
BALANCE_COMPOUNDING_ALLOWED = "allowed"
BALANCE_COMPOUNDING_BLOCKED = "blocked"

REJECTION_REASON_NONE = "none"
REJECTION_REASON_INVALID_ACCOUNT_STATE = "invalid_account_state"
REJECTION_REASON_INVALID_CLOSED_TRADE = "invalid_closed_trade"
REJECTION_REASON_NON_PAPER_MODE = "non_paper_mode"
REJECTION_REASON_LIVE_TRADING_BLOCKED = "live_trading_blocked"
REJECTION_REASON_MISSING_BALANCE = "missing_balance"
REJECTION_REASON_INVALID_BALANCE = "invalid_balance"
REJECTION_REASON_MISSING_REALIZED_PNL = "missing_realized_pnl"
REJECTION_REASON_INVALID_REALIZED_PNL = "invalid_realized_pnl"
REJECTION_REASON_INVALID_COMPOUNDING_CAP = "invalid_compounding_cap"
REJECTION_REASON_INVALID_PROFIT_LOCK = "invalid_profit_lock"
REJECTION_REASON_MARTINGALE_BLOCKED = "martingale_blocked"
REJECTION_REASON_RECOVERY_SIZING_BLOCKED = "recovery_sizing_blocked"
REJECTION_REASON_DRAWDOWN_LIMIT_HIT = "drawdown_limit_hit"
REJECTION_REASON_EVIDENCE_PATH_INVALID = "evidence_path_invalid"


@dataclass(frozen=True)
class BalanceCompoundingLimits:
    compounding_enabled: bool = True
    compounding_cap_percent: float = 10.0
    profit_lock_percent: float = 20.0
    drawdown_reduce_threshold_percent: float = 20.0
    recovery_risk_multiplier: float = 1.0
    max_recovery_multiplier_after_loss: float = 1.0
    max_drawdown_percent: float = 100.0
    evidence_path: Optional[str] = None


def _to_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return {}


def _safe_number(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if value != value or value == float("inf") or value == float("-inf"):
            return None
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _mode(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _safe_safety() -> Dict[str, bool]:
    return {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }


def _base_payload() -> Dict[str, Any]:
    return {
        "allowed": True,
        "decision": BALANCE_COMPOUNDING_ALLOWED,
        "blocked_reason": REJECTION_REASON_NONE,
        "blocked_reasons": [],
        "warnings": [],
        "paper_only": True,
        "mode": BALANCE_COMPOUNDING_MODE,
        "account_state_before": {},
        "account_state_after": {},
        "current_balance_before": 0.0,
        "current_balance_after": 0.0,
        "starting_balance": 0.0,
        "realized_pnl_delta": 0.0,
        "realized_pnl_total": 0.0,
        "daily_loss_used": 0.0,
        "peak_balance": 0.0,
        "drawdown": 0.0,
        "drawdown_percent": 0.0,
        "compounding_enabled": False,
        "compounding_cap_percent": 0.0,
        "profit_lock_percent": 0.0,
        "protected_profit": 0.0,
        "available_compound_profit": 0.0,
        "risk_base": 0.0,
        "recommended_risk_multiplier": 1.0,
        "trade_count": 0,
        "session_count": 0,
        "evidence": {},
        "evidence_path": None,
        "safety": _safe_safety(),
        "next_safe_action": "retry_with_valid_inputs",
        "metadata": {},
    }


def _is_relative_path(path: Any) -> bool:
    if not isinstance(path, str) or not path:
        return False
    if path.startswith("/") or path.startswith("\\"):
        return False
    if ":" in path:
        return False
    parts = path.replace("\\", "/").split("/")
    if ".." in parts:
        return False
    return True


def _block(
    payload: Dict[str, Any],
    reason: str,
    next_action: str,
    blocked_reasons: Optional[list] = None,
) -> Dict[str, Any]:
    payload["allowed"] = False
    payload["decision"] = BALANCE_COMPOUNDING_BLOCKED
    payload["blocked_reason"] = reason
    payload["blocked_reasons"] = list(blocked_reasons) if blocked_reasons else [reason]
    payload["next_safe_action"] = next_action
    return payload


def _coerce_limits(raw_limits: Any) -> Dict[str, Any]:
    def _defaulted(value: Any, fallback: float) -> float:
        number = _safe_number(value)
        return number if number is not None else fallback

    if not isinstance(raw_limits, dict):
        return {
            "compounding_enabled": BalanceCompoundingLimits.compounding_enabled,
            "compounding_cap_percent": _defaulted(
                BalanceCompoundingLimits.compounding_cap_percent, 10.0
            ),
            "profit_lock_percent": _defaulted(
                BalanceCompoundingLimits.profit_lock_percent, 20.0
            ),
            "drawdown_reduce_threshold_percent": _defaulted(
                BalanceCompoundingLimits.drawdown_reduce_threshold_percent, 20.0
            ),
            "recovery_risk_multiplier": _defaulted(
                BalanceCompoundingLimits.recovery_risk_multiplier, 1.0
            ),
            "max_recovery_multiplier_after_loss": _defaulted(
                BalanceCompoundingLimits.max_recovery_multiplier_after_loss, 1.0
            ),
            "max_drawdown_percent": _defaulted(
                BalanceCompoundingLimits.max_drawdown_percent, 100.0
            ),
            "evidence_path": BalanceCompoundingLimits.evidence_path,
        }
    return {
        "compounding_enabled": bool(raw_limits.get("compounding_enabled", BalanceCompoundingLimits.compounding_enabled)),
        "compounding_cap_percent": _defaulted(
            raw_limits.get("compounding_cap_percent", BalanceCompoundingLimits.compounding_cap_percent),
            10.0,
        ),
        "profit_lock_percent": _defaulted(
            raw_limits.get("profit_lock_percent", BalanceCompoundingLimits.profit_lock_percent),
            20.0,
        ),
        "drawdown_reduce_threshold_percent": _safe_number(
            raw_limits.get("drawdown_reduce_threshold_percent", BalanceCompoundingLimits.drawdown_reduce_threshold_percent)
            ) or 20.0,
        "recovery_risk_multiplier": _defaulted(
            raw_limits.get("recovery_risk_multiplier", BalanceCompoundingLimits.recovery_risk_multiplier),
            1.0,
        ),
        "max_recovery_multiplier_after_loss": _defaulted(
            raw_limits.get("max_recovery_multiplier_after_loss", BalanceCompoundingLimits.max_recovery_multiplier_after_loss),
            1.0,
        ),
        "max_drawdown_percent": _defaulted(
            raw_limits.get("max_drawdown_percent", BalanceCompoundingLimits.max_drawdown_percent),
            100.0,
        ),
        "evidence_path": raw_limits.get("evidence_path"),
    }


def _extract_balance(account_state: Dict[str, Any], payload: Dict[str, Any]) -> Optional[float]:
    for key in ("current_balance", "cash_balance", "equity"):
        if key in account_state:
            candidate = _safe_number(account_state.get(key))
            if candidate is None:
                return _block(payload, REJECTION_REASON_INVALID_BALANCE, f"provide_numeric_{key}")["current_balance_after"]
            if candidate < 0:
                return _block(payload, REJECTION_REASON_INVALID_BALANCE, "provide_non_negative_balance")["current_balance_after"]
            return candidate
    return _block(payload, REJECTION_REASON_MISSING_BALANCE, "provide_current_cash_or_equity")["current_balance_after"]


def _recommended_multiplier(account_state: Dict[str, Any], drawdown_percent: float, limits: Dict[str, Any]) -> float:
    threshold = limits["drawdown_reduce_threshold_percent"]
    if threshold <= 0:
        return 1.0
    if drawdown_percent <= threshold:
        return 1.0
    ratio = drawdown_percent / threshold
    reduction = min(0.5, 0.1 * max(0.0, ratio - 1.0))
    return round(max(0.2, 1.0 - reduction), 8)


def _compute_risk_base(
    account_state: Dict[str, Any],
    current_balance_after: float,
    limits: Dict[str, Any],
    payload: Dict[str, Any],
    block_compounding_cap: bool = True,
) -> None:
    compounding_enabled = bool(limits["compounding_enabled"])
    payload["compounding_enabled"] = compounding_enabled
    starting_balance = _safe_number(account_state.get("starting_balance"))
    if starting_balance is None:
        starting_balance = current_balance_after
    payload["starting_balance"] = starting_balance
    payload["compounding_cap_percent"] = limits["compounding_cap_percent"]
    payload["profit_lock_percent"] = limits["profit_lock_percent"]

    if limits["compounding_cap_percent"] < 0:
        _block(payload, REJECTION_REASON_INVALID_COMPOUNDING_CAP, "set_non_negative_compounding_cap")
        return
    if limits["profit_lock_percent"] < 0 or limits["profit_lock_percent"] > 100:
        _block(payload, REJECTION_REASON_INVALID_PROFIT_LOCK, "set_profit_lock_between_0_and_100")
        return

    if compounding_enabled:
        max_risk_base = starting_balance * (1.0 + limits["compounding_cap_percent"] / 100.0)
        if current_balance_after > max_risk_base:
            if block_compounding_cap:
                _block(payload, REJECTION_REASON_INVALID_COMPOUNDING_CAP, "reduce_compounding_cap_or_starting_balance")
                return
            payload["risk_base"] = max_risk_base
        else:
            payload["risk_base"] = current_balance_after
    else:
        payload["risk_base"] = min(current_balance_after, starting_balance)

    profit_above_start = max(0.0, current_balance_after - starting_balance)
    payload["protected_profit"] = profit_above_start
    payload["available_compound_profit"] = profit_above_start

    payload["recommended_risk_multiplier"] = _recommended_multiplier(
        account_state,
        payload["drawdown_percent"],
        limits,
    )


def calculate_risk_base(account_state: Any, limits: Any = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = _base_payload()
    payload["account_state_before"] = _to_dict(account_state)
    payload["metadata"] = dict(metadata or {})
    payload["account_state_after"] = _to_dict(account_state)
    lim = _coerce_limits(limits)

    if not _is_relative_path(lim["evidence_path"]) and lim["evidence_path"] is not None:
        return _block(payload, REJECTION_REASON_EVIDENCE_PATH_INVALID, "supply_relative_evidence_path")

    current_balance = _extract_balance(payload["account_state_before"], payload)
    if payload["blocked_reason"] != REJECTION_REASON_NONE:
        return payload

    payload["current_balance_before"] = current_balance
    payload["current_balance_after"] = current_balance

    realized_total = _safe_number(payload["account_state_before"].get("realized_pnl"))
    if realized_total is None:
        realized_total = 0.0
    payload["realized_pnl_total"] = realized_total

    daily_loss = _safe_number(payload["account_state_before"].get("daily_loss_used"))
    if daily_loss is None:
        daily_loss = 0.0
    if daily_loss < 0:
        return _block(payload, REJECTION_REASON_INVALID_ACCOUNT_STATE, "set_non_negative_daily_loss_used")
    payload["daily_loss_used"] = daily_loss

    peak = _safe_number(payload["account_state_before"].get("peak_balance"))
    if peak is None:
        peak = current_balance
    payload["peak_balance"] = max(peak, current_balance)
    payload["drawdown"] = max(0.0, payload["peak_balance"] - current_balance)
    if payload["peak_balance"] > 0:
        payload["drawdown_percent"] = round(
            payload["drawdown"] / payload["peak_balance"] * 100.0,
            8,
        )

    payload["trade_count"] = int(_safe_number(payload["account_state_before"].get("trade_count")) or 0)
    payload["session_count"] = int(_safe_number(payload["account_state_before"].get("session_count")) or 0)

    if payload["account_state_before"].get("last_trade_realized_pnl", 0.0) < 0 and lim["recovery_risk_multiplier"] > lim["max_recovery_multiplier_after_loss"]:
        return _block(payload, REJECTION_REASON_RECOVERY_SIZING_BLOCKED, "do_not_increase_after_loss")

    _compute_risk_base(payload["account_state_before"], current_balance, lim, payload)
    return payload


def apply_closed_trade_to_balance(
    account_state: Any,
    closed_trade_result: Any,
    limits: Any = None,
    evidence_path: Any = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload = _base_payload()
    payload["metadata"] = dict(metadata or {})
    payload["evidence_path"] = evidence_path
    lim = _coerce_limits(limits)
    payload["compounding_enabled"] = lim["compounding_enabled"]
    payload["compounding_cap_percent"] = lim["compounding_cap_percent"]
    payload["profit_lock_percent"] = lim["profit_lock_percent"]
    payload["account_state_before"] = _to_dict(account_state)
    payload["account_state_after"] = _to_dict(account_state)

    if not _is_relative_path(evidence_path) and evidence_path is not None:
        return _block(payload, REJECTION_REASON_EVIDENCE_PATH_INVALID, "supply_relative_evidence_path")

    closed = _to_dict(closed_trade_result)
    if not closed:
        return _block(payload, REJECTION_REASON_INVALID_CLOSED_TRADE, "supply_closed_trade_dict")

    if not closed.get("closed", False):
        return _block(payload, REJECTION_REASON_INVALID_CLOSED_TRADE, "supply_closed_trade_flag")

    if closed.get("paper_only") is False:
        return _block(payload, REJECTION_REASON_NON_PAPER_MODE, "provide_paper_only_trade")
    if _mode(closed.get("mode")) in {"live", "demo", "broker"}:
        reason = REJECTION_REASON_LIVE_TRADING_BLOCKED if _mode(closed.get("mode")) == "live" else REJECTION_REASON_NON_PAPER_MODE
        return _block(payload, reason, "provide_paper_only_trade_mode")

    if "realized_pnl" not in closed:
        return _block(payload, REJECTION_REASON_MISSING_REALIZED_PNL, "supply_realized_pnl")
    realized_pnl = _safe_number(closed.get("realized_pnl"))
    if realized_pnl is None:
        return _block(payload, REJECTION_REASON_INVALID_REALIZED_PNL, "supply_numeric_realized_pnl")
    payload["realized_pnl_delta"] = realized_pnl

    current_balance = _extract_balance(payload["account_state_before"], payload)
    if payload["blocked_reason"] != REJECTION_REASON_NONE:
        return payload
    payload["current_balance_before"] = current_balance
    payload["current_balance_after"] = current_balance + realized_pnl

    prior_realized_total = _safe_number(payload["account_state_before"].get("realized_pnl"))
    if prior_realized_total is None:
        prior_realized_total = 0.0
    payload["realized_pnl_total"] = prior_realized_total + realized_pnl

    daily_loss = _safe_number(payload["account_state_before"].get("daily_loss_used"))
    if daily_loss is None:
        daily_loss = 0.0
    if daily_loss < 0:
        return _block(payload, REJECTION_REASON_INVALID_ACCOUNT_STATE, "set_non_negative_daily_loss_used")
    if realized_pnl < 0:
        daily_loss += abs(realized_pnl)
    payload["daily_loss_used"] = daily_loss

    trade_count = int(_safe_number(payload["account_state_before"].get("trade_count")) or 0)
    session_count = int(_safe_number(payload["account_state_before"].get("session_count")) or 0)
    payload["trade_count"] = trade_count + 1
    payload["session_count"] = session_count + 1

    prior_peak = _safe_number(payload["account_state_before"].get("peak_balance"))
    if prior_peak is None:
        prior_peak = current_balance
    payload["peak_balance"] = max(prior_peak, payload["current_balance_after"])
    payload["drawdown"] = max(0.0, current_balance - payload["current_balance_after"])
    if payload["peak_balance"] > 0:
        payload["drawdown_percent"] = round(payload["drawdown"] / payload["peak_balance"] * 100.0, 8)
    if payload["drawdown_percent"] > lim["max_drawdown_percent"]:
        return _block(payload, REJECTION_REASON_DRAWDOWN_LIMIT_HIT, "reduce_risk_or_stop_trading")

    if payload["current_balance_after"] < 0:
        return _block(payload, REJECTION_REASON_INVALID_BALANCE, "set_non_negative_balance_after_trade")

    if payload["account_state_before"].get("last_trade_realized_pnl", 0.0) < 0 and lim["recovery_risk_multiplier"] > lim["max_recovery_multiplier_after_loss"]:
        return _block(payload, REJECTION_REASON_MARTINGALE_BLOCKED, "avoid_martingale_after_loss")

    _compute_risk_base(payload["account_state_before"], payload["current_balance_after"], lim, payload, block_compounding_cap=False)
    if payload["blocked_reason"] != REJECTION_REASON_NONE:
        return payload

    account_after = dict(payload["account_state_before"])
    account_after["current_balance"] = payload["current_balance_after"]
    account_after["realized_pnl"] = payload["realized_pnl_total"]
    account_after["daily_loss_used"] = payload["daily_loss_used"]
    account_after["trade_count"] = payload["trade_count"]
    account_after["session_count"] = payload["session_count"]
    account_after["peak_balance"] = payload["peak_balance"]
    account_after["drawdown_percent"] = payload["drawdown_percent"]
    account_after["compounding_enabled"] = payload["compounding_enabled"]
    account_after["starting_balance"] = payload["starting_balance"]
    account_after["last_trade_realized_pnl"] = realized_pnl
    payload["account_state_after"] = account_after

    payload["evidence"] = {
        "trade_id": closed.get("trade_id"),
        "pair": closed.get("pair"),
        "direction": closed.get("direction"),
        "close_reason": closed.get("close_reason", "none"),
        "realized_pnl": payload["realized_pnl_delta"],
        "current_balance_after": payload["current_balance_after"],
        "risk_base": payload["risk_base"],
        "recommended_risk_multiplier": payload["recommended_risk_multiplier"],
    }

    if payload["drawdown_percent"] >= lim["drawdown_reduce_threshold_percent"]:
        payload["warnings"].append("drawdown_threshold_hit")
        payload["recommended_risk_multiplier"] = _recommended_multiplier(
            payload["account_state_after"],
            payload["drawdown_percent"],
            lim,
        )
    payload["next_safe_action"] = "update_forex_portfolio_projection"
    return payload
