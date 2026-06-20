from __future__ import annotations

from typing import Any, Iterable
import datetime as _dt


SUPPORTED_PAIRS = {"EURUSD", "GBPUSD", "USDJPY"}
SUPPORTED_ACTIONS = {"buy", "sell", "hold"}
UNSAFE_FLAG_NAMES = {
    "live_execution",
    "broker_order",
    "credentials",
    "api_key",
    "real_order",
    "webhook_url",
    "network",
    "network_access",
}


def _safety_summary() -> dict[str, bool]:
    return {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "real_webhooks": False,
        "network_access": False,
    }


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "allowed": False,
        "blocked_reason": reason,
        "starting_balance": 0.0,
        "current_balance": 0.0,
        "cash_balance": 0.0,
        "equity": 0.0,
        "realized_pnl": 0.0,
        "unrealized_pnl": 0.0,
        "open_risk": 0.0,
        "available_risk": 0.0,
        "max_daily_loss": 0.0,
        "daily_loss_used": 0.0,
        "drawdown": 0.0,
        "drawdown_percent": 0.0,
        "trade_count": 0,
        "session_count": 0,
        "last_update_timestamp": None,
        "open_positions": {},
        "exposure_by_symbol": {},
        "next_trade_allowed": False,
        "next_trade_blocked_reason": reason,
        "paper_only": True,
        "safety": _safety_summary(),
        "next_safe_action": "Stop and review the paper-only portfolio state input.",
    }


def _unsafe_reason(flags: dict[str, Any]) -> str | None:
    for name in sorted(UNSAFE_FLAG_NAMES):
        if flags.get(name):
            return f"unsafe_flag_{name}"
    return None


def _as_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _round_money(value: float) -> float:
    return round(value, 6)


def _is_valid_timestamp(value: Any) -> bool:
    if value is None:
        return True
    return isinstance(value, (int, float, str, _dt.datetime, _dt.date))


def _market_price_for(pair: str, units: float, market_prices: dict[str, Any] | None) -> float | None:
    if not market_prices:
        return None
    market = market_prices.get(pair) or market_prices.get(pair.lower())
    if market is None:
        return None
    if isinstance(market, dict):
        if units > 0:
            return _as_float(market.get("bid", market.get("price")), None)
        return _as_float(market.get("ask", market.get("price")), None)
    return _as_float(market, None)


def _next_trade_gate(
    *,
    trade_count: int,
    daily_loss_used: float,
    exposure_by_symbol: dict[str, float],
    limits: dict[str, Any],
) -> tuple[bool, str]:
    max_trades = _as_int(limits.get("max_trades_per_day", limits.get("max_trades")), 0)
    if max_trades > 0 and trade_count >= max_trades:
        return False, "max_trades_limit_hit"

    daily_loss_limit = _as_float(limits.get("daily_loss_limit", limits.get("max_daily_loss")), 0.0)
    if daily_loss_limit > 0 and daily_loss_used >= daily_loss_limit:
        return False, "daily_loss_limit_hit"

    max_exposure = _as_float(limits.get("max_exposure_per_symbol"), 0.0)
    if max_exposure > 0:
        for exposure in exposure_by_symbol.values():
            if exposure > max_exposure:
                return False, "exposure_limit_hit"

    return True, "none"


def _as_strict_non_negative_float(value: Any) -> float | None:
    if value is None:
        return 0.0
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if parsed < 0:
        return None
    return parsed


def _validate_account_state(
    *,
    starting_balance: float,
    max_daily_loss: float,
    daily_loss_used: float,
    open_risk: float,
    session_count: int,
    last_update_timestamp: Any | None,
) -> str | None:
    if starting_balance < 0:
        return "negative_starting_balance"
    if max_daily_loss < 0:
        return "negative_max_daily_loss"
    if daily_loss_used < 0:
        return "negative_daily_loss_used"
    if open_risk < 0:
        return "negative_open_risk"
    if session_count < 0:
        return "invalid_session_count"
    if last_update_timestamp is not None and not _is_valid_timestamp(last_update_timestamp):
        return "invalid_timestamp_type"
    return None


def build_portfolio_state(
    ledger_records: Iterable[dict[str, Any]],
    account_snapshot: dict[str, Any] | None = None,
    market_prices: dict[str, Any] | None = None,
    limits: dict[str, Any] | None = None,
    **safety_flags: Any,
) -> dict[str, Any]:
    """Build deterministic paper portfolio state from execution-ledger events."""
    unsafe = _unsafe_reason(safety_flags)
    if unsafe:
        return _blocked(unsafe)

    account = account_snapshot or {}
    if account_snapshot is not None and not isinstance(account_snapshot, dict):
        return _blocked("invalid_account_snapshot")

    limits = limits or {}
    if not isinstance(limits, dict):
        return _blocked("invalid_limits")

    has_cash_balance = "cash_balance" in account or "balance" in account
    has_current_balance = "current_balance" in account
    has_open_risk = "open_risk" in account

    cash_balance = _as_float(account.get("cash_balance", account.get("balance")), 0.0)
    current_balance = _as_float(account.get("current_balance", cash_balance), cash_balance)
    if has_cash_balance and cash_balance < 0:
        return _blocked("negative_cash_balance")
    if has_current_balance and current_balance < 0:
        return _blocked("negative_current_balance")

    starting_balance = _as_float(
        account.get("starting_balance", cash_balance),
        cash_balance,
    )

    open_risk_input = _as_strict_non_negative_float(account.get("open_risk")) if has_open_risk else None
    if has_open_risk and open_risk_input is None:
        return _blocked("negative_open_risk")

    realized_pnl = 0.0
    realized_losses = 0.0
    trade_count = 0
    session_count = _as_int(account.get("session_count", 0), 0)
    last_update_timestamp = account.get("last_update_timestamp")
    positions: dict[str, dict[str, float]] = {}

    for record in ledger_records:
        if not isinstance(record, dict):
            return _blocked("invalid_ledger_record")
        if record.get("paper_only") is False:
            return _blocked("non_paper_record")
        if record.get("allowed") is False:
            continue

        pair = str(record.get("pair", "")).upper()
        if pair not in SUPPORTED_PAIRS:
            return _blocked("invalid_pair")

        action = str(record.get("action", "")).lower()
        if action not in SUPPORTED_ACTIONS:
            return _blocked("unsupported_action")
        if action == "hold":
            continue

        filled_units = _as_float(record.get("filled_units"), 0.0)
        fill_price = _as_float(record.get("fill_price"), 0.0)
        if filled_units <= 0:
            return _blocked("invalid_filled_units")
        if fill_price <= 0:
            return _blocked("missing_fill_price")

        pnl = _as_float(record.get("realized_pnl"), 0.0)
        realized_pnl += pnl
        if pnl < 0:
            realized_losses += abs(pnl)
        trade_count += 1

        position = positions.setdefault(pair, {"units": 0.0, "average_entry_price": 0.0})
        old_units = position["units"]
        old_average = position["average_entry_price"]
        signed_units = filled_units if action == "buy" else -filled_units
        new_units = old_units + signed_units

        if old_units == 0 or (old_units > 0 and signed_units > 0) or (old_units < 0 and signed_units < 0):
            total_exposure = abs(old_units) * old_average + abs(signed_units) * fill_price
            new_average = total_exposure / abs(new_units) if new_units else 0.0
        elif new_units == 0:
            new_average = 0.0
        elif (old_units > 0 > new_units) or (old_units < 0 < new_units):
            new_average = fill_price
        else:
            new_average = old_average

        position["units"] = new_units
        position["average_entry_price"] = new_average
        current_balance += pnl

    open_positions: dict[str, dict[str, Any]] = {}
    exposure_by_symbol: dict[str, float] = {}
    unrealized_pnl = 0.0

    for pair, position in sorted(positions.items()):
        units = position["units"]
        if units == 0:
            continue
        average = position["average_entry_price"]
        side = "long" if units > 0 else "short"
        open_positions[pair] = {
            "side": side,
            "units": _round_money(units),
            "average_entry_price": _round_money(average),
        }
        exposure_by_symbol[pair] = _round_money(abs(units) * average)
        market_price = _market_price_for(pair, units, market_prices)
        if market_price is not None:
            if units > 0:
                unrealized_pnl += (market_price - average) * units
            else:
                unrealized_pnl += (average - market_price) * abs(units)

    daily_loss_used = _as_float(account.get("daily_loss_used"), 0.0) + realized_losses
    max_daily_loss = _as_float(
        account.get("max_daily_loss", limits.get("max_daily_loss", limits.get("daily_loss_limit"))),
        0.0,
    )

    open_risk = _round_money(sum(exposure_by_symbol.values()))
    if has_open_risk:
        open_risk = _round_money(open_risk_input or 0.0)

    validation_reason = _validate_account_state(
        starting_balance=starting_balance,
        max_daily_loss=max_daily_loss,
        daily_loss_used=daily_loss_used,
        open_risk=open_risk,
        session_count=session_count,
        last_update_timestamp=last_update_timestamp,
    )
    if validation_reason:
        return _blocked(validation_reason)
    if not _is_valid_timestamp(last_update_timestamp):
        return _blocked("invalid_timestamp_type")

    equity = _round_money(current_balance + unrealized_pnl)
    if starting_balance > 0:
        drawdown = _round_money(max(0.0, starting_balance - equity))
        drawdown_percent = _round_money((drawdown / starting_balance) * 100.0)
    else:
        drawdown = 0.0
        drawdown_percent = 0.0

    available_risk = _round_money(max(0.0, max_daily_loss - daily_loss_used))
    if has_open_risk:
        # Preserve explicit account-snapshot risk overrides when explicitly provided.
        available_risk = _round_money(max(0.0, max_daily_loss - daily_loss_used - open_risk))

    limits_with_alias = dict(limits)
    limits_with_alias["daily_loss_limit"] = max_daily_loss
    next_allowed, next_blocked_reason = _next_trade_gate(
        trade_count=trade_count,
        daily_loss_used=daily_loss_used,
        exposure_by_symbol=exposure_by_symbol,
        limits=limits_with_alias,
    )

    return {
        "allowed": True,
        "blocked_reason": "none",
        "starting_balance": _round_money(starting_balance),
        "current_balance": _round_money(current_balance),
        "cash_balance": _round_money(current_balance),
        "equity": equity,
        "realized_pnl": _round_money(realized_pnl),
        "unrealized_pnl": _round_money(unrealized_pnl),
        "open_risk": open_risk,
        "available_risk": available_risk,
        "max_daily_loss": _round_money(max_daily_loss),
        "daily_loss_used": _round_money(daily_loss_used),
        "drawdown": drawdown,
        "drawdown_percent": drawdown_percent,
        "trade_count": trade_count,
        "session_count": session_count,
        "last_update_timestamp": last_update_timestamp,
        "open_positions": open_positions,
        "exposure_by_symbol": exposure_by_symbol,
        "next_trade_allowed": next_allowed,
        "next_trade_blocked_reason": next_blocked_reason,
        "paper_only": True,
        "safety": _safety_summary(),
        "next_safe_action": (
            "Continue paper-only signal, risk, execution, ledger, and portfolio validation."
            if next_allowed
            else "Stop new paper trades until the portfolio state block is reviewed."
        ),
    }
