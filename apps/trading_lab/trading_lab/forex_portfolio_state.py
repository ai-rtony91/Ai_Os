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
        "portfolio_risk_percent": 0.0,
        "trade_count": 0,
        "consecutive_losses": 0,
        "session_count": 0,
        "last_update_timestamp": None,
        "open_positions": {},
        "open_positions_count": 0,
        "exposure_by_symbol": {},
        "next_trade_allowed": False,
        "next_trade_blocked_reason": reason,
        "paper_only": True,
        "safety": _safety_summary(),
        "next_safe_action": "Stop and review the portfolio input.",
        "realized_loss_bucket": 0.0,
        "realized_gain_bucket": 0.0,
        "loss_bucket": 0.0,
        "profit_bucket": 0.0,
        "balance_bucket": 0.0,
        "previous_position_size_units": 0.0,
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


def _coerce_initial_open_positions(open_positions: Any) -> tuple[dict[str, dict[str, float]], str | None]:
    if open_positions is None:
        return {}, None
    if not isinstance(open_positions, dict):
        return {}, "invalid_open_positions"

    normalized: dict[str, dict[str, float]] = {}
    for symbol, raw_state in open_positions.items():
        normalized_pair = str(symbol).upper()
        if normalized_pair not in SUPPORTED_PAIRS:
            return {}, "invalid_open_position_symbol"
        if not isinstance(raw_state, dict):
            return {}, "invalid_open_position_state"

        units = _as_float(raw_state.get("units", raw_state.get("position_size", 0.0)))
        if units == 0.0:
            continue
        entry = _as_float(raw_state.get("average_entry_price", raw_state.get("entry_price", 0.0)))
        if entry <= 0.0:
            return {}, "invalid_open_position_entry_price"
        normalized[normalized_pair] = {
            "units": units,
            "average_entry_price": entry,
        }
    return normalized, None


def _next_trade_gate(
    *,
    trade_count: int,
    daily_loss_used: float,
    exposure_by_symbol: dict[str, float],
    open_trade_count: int,
    consecutive_losses: int,
    drawdown_percent: float,
    portfolio_risk_percent: float,
    limits: dict[str, Any],
) -> tuple[bool, str]:
    max_trades = _as_int(limits.get("max_trades_per_day", limits.get("max_trades")), 0)
    if max_trades > 0 and trade_count >= max_trades:
        return False, "max_trades_limit_hit"

    daily_loss_limit = _as_float(limits.get("daily_loss_limit", limits.get("max_daily_loss")), 0.0)
    if daily_loss_limit > 0 and daily_loss_used >= daily_loss_limit:
        return False, "daily_loss_limit_hit"

    max_drawdown_percent = _as_float(limits.get("max_drawdown_percent", limits.get("max_drawdown")), 0.0)
    if max_drawdown_percent > 0 and drawdown_percent >= max_drawdown_percent:
        return False, "max_drawdown_limit_hit"

    max_portfolio_risk = _as_float(
        limits.get("max_total_portfolio_risk_percent", limits.get("max_portfolio_risk_percent")),
        0.0,
    )
    if max_portfolio_risk > 0 and portfolio_risk_percent >= max_portfolio_risk:
        return False, "max_portfolio_risk_limit_hit"

    max_exposure = _as_float(limits.get("max_exposure_per_symbol"), 0.0)
    if max_exposure > 0:
        for exposure in exposure_by_symbol.values():
            if exposure > max_exposure:
                return False, "exposure_limit_hit"

    max_open_trades = _as_int(limits.get("max_open_trades", limits.get("max_open_positions")), 0)
    if max_open_trades > 0 and open_trade_count >= max_open_trades:
        return False, "max_open_trades_limit_hit"

    max_consecutive_losses = _as_int(limits.get("max_consecutive_losses"), 0)
    if max_consecutive_losses > 0 and consecutive_losses >= max_consecutive_losses:
        return False, "max_consecutive_losses_limit_hit"

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


def _validate_account_state(
    *,
    starting_balance: float,
    max_daily_loss: float,
    daily_loss_used: float,
    open_risk: float,
    session_count: int,
    consecutive_losses: int,
    open_trade_count: int,
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
    if consecutive_losses < 0:
        return "negative_consecutive_losses"
    if open_trade_count < 0:
        return "negative_open_trade_count"
    if session_count < 0:
        return "invalid_session_count"
    if last_update_timestamp is not None and not _is_valid_timestamp(last_update_timestamp):
        return "invalid_timestamp_type"
    return None


def _to_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


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

    account = _to_dict(account_snapshot)
    if account_snapshot is not None and not isinstance(account_snapshot, dict):
        return _blocked("invalid_account_snapshot")

    limits = limits or {}
    if not isinstance(limits, dict):
        return _blocked("invalid_limits")

    has_cash_balance = "cash_balance" in account or "balance" in account
    has_current_balance = "current_balance" in account
    has_open_risk = "open_risk" in account
    previous_position_size_units = _as_float(account.get("previous_position_size_units"), 0.0)

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

    initial_open_positions, open_position_error = _coerce_initial_open_positions(account.get("open_positions"))
    if open_position_error:
        return _blocked(open_position_error)

    open_risk_input = _as_strict_non_negative_float(account.get("open_risk")) if has_open_risk else None
    if has_open_risk and open_risk_input is None:
        return _blocked("negative_open_risk")

    consecutive_losses = _as_int(account.get("consecutive_losses", 0), 0)
    open_positions = dict(initial_open_positions)
    realized_pnl = 0.0
    realized_losses = 0.0
    realized_gains = 0.0
    trade_count = 0
    session_count = _as_int(account.get("session_count", 0), 0)
    last_update_timestamp = account.get("last_update_timestamp")

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
        if action in {"buy", "sell"}:
            previous_position_size_units = _round_money(abs(filled_units))
        if pnl < 0:
            realized_losses += abs(pnl)
            consecutive_losses += 1
        else:
            realized_gains += pnl
            consecutive_losses = 0
        trade_count += 1

        position = open_positions.setdefault(pair, {"units": 0.0, "average_entry_price": 0.0})
        old_units = position["units"]
        old_average = position["average_entry_price"]
        signed_units = filled_units if action == "buy" else -filled_units
        new_units = old_units + signed_units

        if old_units == 0 or (old_units > 0 > new_units) or (old_units < 0 < new_units):
            new_average = fill_price
        elif old_units == 0:
            new_average = fill_price
        elif new_units == 0:
            new_average = 0.0
        elif (old_units > 0 and signed_units > 0) or (old_units < 0 and signed_units < 0):
            total_exposure = abs(old_units) * old_average + abs(signed_units) * fill_price
            new_average = total_exposure / abs(new_units)
        else:
            new_average = old_average

        position["units"] = new_units
        position["average_entry_price"] = new_average
        if new_units == 0:
            position["units"] = 0.0
            position["average_entry_price"] = 0.0
        current_balance += pnl

    open_positions = {
        pair: {
            "side": "long" if values["units"] > 0 else "short",
            "units": _round_money(values["units"]),
            "average_entry_price": _round_money(values["average_entry_price"]),
        }
        for pair, values in open_positions.items()
        if values["units"] != 0
    }
    exposure_by_symbol: dict[str, float] = {}
    unrealized_pnl = 0.0
    for pair, values in open_positions.items():
        units = values["units"]
        average = values["average_entry_price"]
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
        consecutive_losses=consecutive_losses,
        open_trade_count=len(open_positions),
        last_update_timestamp=last_update_timestamp,
    )
    if validation_reason:
        return _blocked(validation_reason)

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

    if starting_balance > 0:
        portfolio_risk_percent = _round_money((open_risk / starting_balance) * 100.0)
    else:
        portfolio_risk_percent = 0.0

    open_trade_count = len(open_positions)
    next_allowed, next_blocked_reason = _next_trade_gate(
        trade_count=trade_count,
        daily_loss_used=daily_loss_used,
        exposure_by_symbol=exposure_by_symbol,
        open_trade_count=open_trade_count,
        consecutive_losses=consecutive_losses,
        drawdown_percent=drawdown_percent,
        portfolio_risk_percent=portfolio_risk_percent,
        limits=dict(limits),
    )

    max_drawdown_percent = _as_float(
        limits.get("max_drawdown_percent", limits.get("max_drawdown")),
        0.0,
    )
    max_portfolio_risk_percent = _as_float(
        limits.get("max_total_portfolio_risk_percent", limits.get("max_portfolio_risk_percent")),
        0.0,
    )
    max_open_trades = _as_int(limits.get("max_open_trades", limits.get("max_open_positions")), 0)
    max_consecutive_losses = _as_int(limits.get("max_consecutive_losses"), 0)
    max_pair_risk_percent = _as_float(limits.get("max_pair_risk_percent"), _as_float(limits.get("max_risk_percent"), 0.0))

    next_safe_action = "Continue paper-only signal, risk, execution, and portfolio validation."
    if not next_allowed:
        next_safe_action = "Stop new paper trades until the portfolio state block is reviewed."

    return {
        "allowed": True,
        "blocked_reason": "none",
        "starting_balance": _round_money(starting_balance),
        "current_balance": _round_money(current_balance),
        "cash_balance": _round_money(current_balance),
        "balance_bucket": _round_money(current_balance),
        "equity": equity,
        "realized_pnl": _round_money(realized_pnl),
        "unrealized_pnl": _round_money(unrealized_pnl),
        "open_risk": open_risk,
        "available_risk": available_risk,
        "max_daily_loss": _round_money(max_daily_loss),
        "daily_loss_used": _round_money(daily_loss_used),
        "drawdown": drawdown,
        "drawdown_percent": drawdown_percent,
        "portfolio_risk_percent": portfolio_risk_percent,
        "trade_count": trade_count,
        "consecutive_losses": consecutive_losses,
        "session_count": session_count,
        "last_update_timestamp": last_update_timestamp,
        "open_positions": open_positions,
        "open_positions_count": open_trade_count,
        "exposure_by_symbol": exposure_by_symbol,
        "next_trade_allowed": next_allowed,
        "next_trade_blocked_reason": next_blocked_reason,
        "paper_only": True,
        "safety": _safety_summary(),
        "next_safe_action": next_safe_action,
        "realized_loss_bucket": _round_money(realized_losses),
        "realized_gain_bucket": _round_money(realized_gains),
        "loss_bucket": _round_money(realized_losses),
        "profit_bucket": _round_money(realized_gains),
        "max_drawdown_percent": max_drawdown_percent,
        "previous_position_size_units": previous_position_size_units,
        "max_portfolio_risk_percent": max_portfolio_risk_percent,
        "max_open_trades_limit": max_open_trades,
        "max_consecutive_losses_limit": max_consecutive_losses,
        "max_pair_risk_percent": max_pair_risk_percent,
        "account_state_summary": {
            "max_open_trades_limit": max_open_trades,
            "max_consecutive_losses": max_consecutive_losses,
            "max_trades_limit": _as_int(limits.get("max_trades_per_day", limits.get("max_trades")), 0),
            "max_exposure_per_symbol": _as_float(limits.get("max_exposure_per_symbol"), 0.0),
            "max_drawdown_percent": max_drawdown_percent,
            "max_portfolio_risk_percent": max_portfolio_risk_percent,
        },
    }
