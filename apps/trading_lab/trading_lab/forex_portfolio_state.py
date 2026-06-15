from __future__ import annotations

from typing import Any, Iterable


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


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "allowed": False,
        "blocked_reason": reason,
        "cash_balance": 0.0,
        "open_positions": {},
        "realized_pnl": 0.0,
        "unrealized_pnl": 0.0,
        "trade_count": 0,
        "daily_loss_used": 0.0,
        "exposure_by_symbol": {},
        "next_trade_allowed": False,
        "next_trade_blocked_reason": reason,
        "paper_only": True,
        "safety": _safety_summary(),
        "next_safe_action": "Stop and review the paper-only portfolio state input.",
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


def _market_price_for(pair: str, units: float, market_prices: dict[str, Any] | None) -> float | None:
    if not market_prices:
        return None
    market = market_prices.get(pair) or market_prices.get(pair.lower())
    if market is None:
        return None
    if isinstance(market, dict):
        if units > 0:
            return _as_float(market.get("bid", market.get("price")), None)  # type: ignore[arg-type]
        return _as_float(market.get("ask", market.get("price")), None)  # type: ignore[arg-type]
    return _as_float(market, None)  # type: ignore[arg-type]


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
    limits = limits or {}
    cash_balance = _as_float(account.get("cash_balance", account.get("balance")), 0.0)
    positions: dict[str, dict[str, float]] = {}
    realized_pnl = 0.0
    realized_losses = 0.0
    trade_count = 0

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
        cash_balance += pnl

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
    next_allowed, next_blocked_reason = _next_trade_gate(
        trade_count=trade_count,
        daily_loss_used=daily_loss_used,
        exposure_by_symbol=exposure_by_symbol,
        limits=limits,
    )

    return {
        "allowed": True,
        "blocked_reason": "none",
        "cash_balance": _round_money(cash_balance),
        "open_positions": open_positions,
        "realized_pnl": _round_money(realized_pnl),
        "unrealized_pnl": _round_money(unrealized_pnl),
        "trade_count": trade_count,
        "daily_loss_used": _round_money(daily_loss_used),
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
