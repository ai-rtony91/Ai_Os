from __future__ import annotations

from typing import Any


SUPPORTED_PAIRS = {"EURUSD", "GBPUSD", "USDJPY"}
SUPPORTED_ACTIONS = {"buy", "sell", "hold"}
FORBIDDEN_SIZING_SIGNALS = ("martingale", "revenge", "averaging", "grid", "anti-martingale")

PAPER_RISK_SAFETY = {
    "paper_only": True,
    "execution_allowed": False,
    "broker_execution": False,
    "credential_use": False,
    "live_trading": False,
    "real_orders": False,
    "real_webhooks": False,
    "network_access": False,
}


def _number(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"1", "true", "yes", "on", "y"}:
            return True
        if text in {"0", "false", "no", "off", "n", "none", "null", ""}:
            return False
    return bool(value)


def _to_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _contains_forbidden_sizing(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip().lower()
    return any(token in text for token in FORBIDDEN_SIZING_SIGNALS)


def _blocked(
    reason: str,
    *,
    pair: str,
    action: str | None,
    position_size_units: float,
    max_position_size_units: float,
    risk_percent: float,
    max_risk_percent: float,
    max_pair_risk_percent: float = 0.0,
    max_portfolio_risk_percent: float = 0.0,
    portfolio_risk_percent: float = 0.0,
    max_open_trades: int = 0,
    open_trade_count: int = 0,
    max_consecutive_losses: int = 0,
    consecutive_losses: int = 0,
    kill_switch_active: bool = False,
    margin_guard_ok: bool = True,
    max_portfolio_risk_hit: bool = False,
    owner_approval_required_for_live_capital_increase: bool = False,
    daily_loss_limit_hit: bool = False,
    max_trades_limit_hit: bool = False,
) -> dict[str, Any]:
    return {
        "allowed": False,
        "blocked_reason": reason,
        "pair": pair,
        "action": action,
        "position_size_units": position_size_units,
        "max_position_size_units": max_position_size_units,
        "risk_percent": risk_percent,
        "max_risk_percent": max_risk_percent,
        "max_pair_risk_percent": max_pair_risk_percent,
        "max_portfolio_risk_percent": max_portfolio_risk_percent,
        "portfolio_risk_percent": portfolio_risk_percent,
        "max_open_trades": max_open_trades,
        "open_trade_count": open_trade_count,
        "max_consecutive_losses": max_consecutive_losses,
        "consecutive_losses": consecutive_losses,
        "kill_switch_active": kill_switch_active,
        "margin_guard_ok": margin_guard_ok,
        "max_portfolio_risk_hit": max_portfolio_risk_hit,
        "owner_approval_required_for_live_capital_increase": owner_approval_required_for_live_capital_increase,
        "daily_loss_limit_hit": daily_loss_limit_hit,
        "max_trades_limit_hit": max_trades_limit_hit,
        "paper_only": True,
        "safety": PAPER_RISK_SAFETY.copy(),
        "next_safe_action": "Stop and review the blocked paper risk-control decision.",
    }


def _safety_block_reason(flags: dict[str, Any]) -> str | None:
    blocked_fields = [
        ("live_execution", "live_execution_blocked"),
        ("broker_order", "broker_order_blocked"),
        ("credentials", "credentials_blocked"),
        ("api_key", "api_key_blocked"),
        ("real_order", "real_order_blocked"),
        ("webhook_url", "real_webhook_blocked"),
        ("real_webhook", "real_webhook_blocked"),
        ("network", "network_blocked"),
        ("network_access", "network_blocked"),
    ]
    for field, reason in blocked_fields:
        if flags.get(field):
            return reason
    return None


def _daily_loss_limit_hit(account: dict[str, Any], limits: dict[str, Any]) -> bool:
    daily_loss_limit = _number(limits.get("daily_loss_limit"), 0.0)
    if daily_loss_limit <= 0:
        return False
    explicit_daily_loss = _number(account.get("daily_loss"), 0.0)
    daily_pnl = _number(account.get("daily_pnl"), 0.0)
    observed_loss = max(explicit_daily_loss, abs(min(daily_pnl, 0.0)))
    return observed_loss >= daily_loss_limit


def _max_trades_limit_hit(account: dict[str, Any], limits: dict[str, Any]) -> bool:
    max_trades = int(_number(limits.get("max_trades_per_day"), 0.0))
    if max_trades <= 0:
        return False
    trades_today = int(_number(account.get("trades_today"), 0.0))
    return trades_today >= max_trades


def _max_consecutive_losses_hit(account: dict[str, Any], limits: dict[str, Any]) -> bool:
    max_consecutive_losses = int(_number(limits.get("max_consecutive_losses"), 0.0))
    if max_consecutive_losses <= 0:
        return False
    consecutive_losses = int(_number(account.get("consecutive_losses", account.get("consecutive_loss_count")), 0.0))
    return consecutive_losses >= max_consecutive_losses


def _open_trades_limit_hit(account: dict[str, Any], limits: dict[str, Any]) -> bool:
    max_open_trades = _to_int(limits.get("max_open_trades", limits.get("max_open_positions")), 0)
    if max_open_trades <= 0:
        return False
    open_trade_count = _to_int(
        account.get("open_positions_count", account.get("open_trade_count", account.get("open_positions", 0))),
        0,
    )
    return open_trade_count >= max_open_trades


def _portfolio_risk_hit(account: dict[str, Any], limits: dict[str, Any], risk_percent: float) -> bool:
    max_portfolio_risk_percent = _number(
        limits.get("max_total_portfolio_risk_percent"),
        0.0,
    )
    if max_portfolio_risk_percent <= 0:
        max_portfolio_risk_percent = _number(limits.get("max_portfolio_risk_percent"), 0.0)
    if max_portfolio_risk_percent <= 0:
        return False
    current_portfolio_risk = _number(
        account.get("portfolio_risk_percent"),
        _number(account.get("risk_utilization_percent"), 0.0),
    )
    return (current_portfolio_risk + risk_percent) > max_portfolio_risk_percent


def _kill_switch_hit(safety_flags: dict[str, Any], limits: dict[str, Any]) -> bool:
    return _to_bool(safety_flags.get("kill_switch_active")) or _to_bool(limits.get("kill_switch_active"), False)


def _margin_guard_hit(safety_flags: dict[str, Any], limits: dict[str, Any]) -> bool:
    margin_guard_ok = _to_bool(safety_flags.get("margin_guard_ok"), _to_bool(limits.get("margin_guard_ok"), True))
    if not margin_guard_ok:
        return True
    return not _to_bool(limits.get("margin_guard_active"), True)


def _live_capital_increase_without_owner_approval(signal: dict[str, Any], limits: dict[str, Any]) -> bool:
    requested = _to_bool(signal.get("owner_request_live_capital_increase"))
    requested = requested or _to_bool(signal.get("request_live_capital_increase"))
    requested = requested or _to_bool(signal.get("request_auto_risk_scaling"))
    if not requested:
        return False
    return not _to_bool(
        signal.get("owner_approved_live_capital_increase"),
        _to_bool(limits.get("owner_approved_live_capital_increase"), False),
    )


def _compounding_or_forbidden_growth(account: dict[str, Any], signal: dict[str, Any], limits: dict[str, Any]) -> bool:
    previous_position_size = account.get("previous_position_size_units")
    if previous_position_size is None:
        previous_position_size = account.get("last_position_size_units")
    if previous_position_size is None:
        return False
    previous_size = _number(previous_position_size, 0.0)
    if previous_size <= 0:
        return False
    requested_size = _number(signal.get("position_size_units"), 0.0)
    if requested_size <= previous_size:
        return False
    if _to_bool(signal.get("compounding_approved"), _to_bool(limits.get("compounding_approved"), False)):
        return False
    if _to_bool(signal.get("owner_approved_compounding"), _to_bool(limits.get("owner_approved_compounding"), False)):
        return False
    return True


def _position_size_forbidden_model(signal: dict[str, Any]) -> bool:
    if _to_bool(signal.get("is_revenge"), False):
        return True
    if _to_bool(signal.get("is_martingale"), False):
        return True
    if _contains_forbidden_sizing(signal.get("sizing_model")):
        return True
    return False


def _spread_slippage_guard_hit(signal: dict[str, Any], limits: dict[str, Any]) -> str | None:
    spread_pips = _number(signal.get("spread_pips"), _number(signal.get("estimated_spread_pips"), 0.0))
    slippage_pips = _number(signal.get("slippage_pips"), _number(signal.get("estimated_slippage_pips"), 0.0))
    max_spread_pips = _number(limits.get("max_spread_pips", limits.get("max_spread_bps")), 0.0)
    max_slippage_pips = _number(limits.get("max_slippage_pips", limits.get("max_slippage_bps")), 0.0)

    if max_spread_pips > 0 and spread_pips > max_spread_pips:
        return "spread_limit_exceeded"
    if max_slippage_pips > 0 and slippage_pips > max_slippage_pips:
        return "slippage_limit_exceeded"
    return None


def evaluate_risk_controls(
    signal: dict[str, Any],
    account: dict[str, Any],
    limits: dict[str, Any],
    **safety_flags: Any,
) -> dict[str, Any]:
    if not isinstance(signal, dict):
        signal = {}
    if not isinstance(account, dict):
        account = {}
    if not isinstance(limits, dict):
        limits = {}

    pair = str(signal.get("pair", "")).upper()
    action_value = signal.get("action")
    action = str(action_value).lower() if action_value is not None else None
    max_position_size_units = _number(limits.get("max_position_size_units"), 0.0)
    max_risk_percent = _number(limits.get("max_risk_percent"), 0.0)
    max_pair_risk_percent = _number(limits.get("max_pair_risk_percent"), max_risk_percent)
    max_portfolio_risk_percent = _number(
        limits.get("max_total_portfolio_risk_percent"),
        _number(limits.get("max_portfolio_risk_percent"), 0.0),
    )
    if max_pair_risk_percent > max_portfolio_risk_percent > 0:
        max_pair_risk_percent = max_portfolio_risk_percent
    max_open_trades = _to_int(limits.get("max_open_trades", limits.get("max_open_positions")), 0)
    max_consecutive_losses = _to_int(limits.get("max_consecutive_losses"), 0)
    open_trade_count = _to_int(
        account.get("open_positions_count", account.get("open_trade_count", account.get("open_positions", 0))),
        0,
    )
    position_size_units = _number(signal.get("position_size_units"), 0.0)
    risk_percent = _number(signal.get("risk_percent"), 0.0)
    portfolio_risk_percent = _number(account.get("portfolio_risk_percent"), 0.0)

    if action == "hold":
        position_size_units = 0.0
        risk_percent = 0.0

    daily_limit_hit = _daily_loss_limit_hit(account, limits)
    trades_limit_hit = _max_trades_limit_hit(account, limits)
    consecutive_losses = _to_int(account.get("consecutive_losses", account.get("consecutive_loss_count")), 0)
    consecutive_losses_hit = _max_consecutive_losses_hit(account, limits)
    open_trades_limit_hit = _open_trades_limit_hit(account, limits)
    portfolio_risk_hit = _portfolio_risk_hit(account, limits, risk_percent)
    kill_switch_active = _kill_switch_hit(safety_flags, limits)
    margin_guard_hit = _margin_guard_hit(safety_flags, limits)
    live_increase_blocked = _live_capital_increase_without_owner_approval(signal, limits)
    spread_slippage_hit = _spread_slippage_guard_hit(signal, limits)
    compounding_growth_blocked = _compounding_or_forbidden_growth(account, signal, limits)
    forbidden_sizing = _position_size_forbidden_model(signal)

    safety_reason = _safety_block_reason(safety_flags)
    if safety_reason:
        return _blocked(
            safety_reason,
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=kill_switch_active,
            margin_guard_ok=not margin_guard_hit,
            max_portfolio_risk_hit=portfolio_risk_hit,
            owner_approval_required_for_live_capital_increase=live_increase_blocked,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if pair not in SUPPORTED_PAIRS:
        return _blocked(
            "invalid_pair",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=kill_switch_active,
            margin_guard_ok=not margin_guard_hit,
            max_portfolio_risk_hit=portfolio_risk_hit,
            owner_approval_required_for_live_capital_increase=live_increase_blocked,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if action is None:
        return _blocked(
            "missing_action",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=kill_switch_active,
            margin_guard_ok=not margin_guard_hit,
            max_portfolio_risk_hit=portfolio_risk_hit,
            owner_approval_required_for_live_capital_increase=live_increase_blocked,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if action not in SUPPORTED_ACTIONS:
        return _blocked(
            "unsupported_action",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=kill_switch_active,
            margin_guard_ok=not margin_guard_hit,
            max_portfolio_risk_hit=portfolio_risk_hit,
            owner_approval_required_for_live_capital_increase=live_increase_blocked,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if kill_switch_active:
        return _blocked(
            "kill_switch_active",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=True,
            margin_guard_ok=not margin_guard_hit,
            max_portfolio_risk_hit=portfolio_risk_hit,
            owner_approval_required_for_live_capital_increase=live_increase_blocked,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if margin_guard_hit:
        return _blocked(
            "margin_guard_blocked",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=False,
            margin_guard_ok=False,
            max_portfolio_risk_hit=portfolio_risk_hit,
            owner_approval_required_for_live_capital_increase=live_increase_blocked,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if max_position_size_units > 0 and position_size_units > max_position_size_units:
        return _blocked(
            "position_size_above_max",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=kill_switch_active,
            margin_guard_ok=not margin_guard_hit,
            max_portfolio_risk_hit=portfolio_risk_hit,
            owner_approval_required_for_live_capital_increase=live_increase_blocked,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if max_risk_percent > 0 and risk_percent > max_risk_percent:
        return _blocked(
            "risk_percent_above_max",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=kill_switch_active,
            margin_guard_ok=not margin_guard_hit,
            max_portfolio_risk_hit=portfolio_risk_hit,
            owner_approval_required_for_live_capital_increase=live_increase_blocked,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if max_pair_risk_percent > 0 and risk_percent > max_pair_risk_percent:
        return _blocked(
            "risk_percent_above_pair_cap",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=kill_switch_active,
            margin_guard_ok=not margin_guard_hit,
            max_portfolio_risk_hit=portfolio_risk_hit,
            owner_approval_required_for_live_capital_increase=live_increase_blocked,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if action in {"buy", "sell"} and position_size_units <= 0:
        return _blocked(
            "non_positive_position_size",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=kill_switch_active,
            margin_guard_ok=not margin_guard_hit,
            max_portfolio_risk_hit=portfolio_risk_hit,
            owner_approval_required_for_live_capital_increase=live_increase_blocked,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if spread_slippage_hit is not None:
        return _blocked(
            spread_slippage_hit,
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=kill_switch_active,
            margin_guard_ok=not margin_guard_hit,
            max_portfolio_risk_hit=portfolio_risk_hit,
            owner_approval_required_for_live_capital_increase=live_increase_blocked,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if _position_size_forbidden_model(signal):
        return _blocked(
            "forbidden_sizing_model",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=kill_switch_active,
            margin_guard_ok=not margin_guard_hit,
            max_portfolio_risk_hit=portfolio_risk_hit,
            owner_approval_required_for_live_capital_increase=live_increase_blocked,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if compounding_growth_blocked:
        return _blocked(
            "forbidden_compounding_growth",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=kill_switch_active,
            margin_guard_ok=not margin_guard_hit,
            max_portfolio_risk_hit=portfolio_risk_hit,
            owner_approval_required_for_live_capital_increase=live_increase_blocked,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if open_trades_limit_hit:
        return _blocked(
            "max_open_trades_limit_hit",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=kill_switch_active,
            margin_guard_ok=not margin_guard_hit,
            max_portfolio_risk_hit=portfolio_risk_hit,
            owner_approval_required_for_live_capital_increase=live_increase_blocked,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if consecutive_losses_hit:
        return _blocked(
            "max_consecutive_losses_limit_hit",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=kill_switch_active,
            margin_guard_ok=not margin_guard_hit,
            max_portfolio_risk_hit=portfolio_risk_hit,
            owner_approval_required_for_live_capital_increase=live_increase_blocked,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if live_increase_blocked:
        return _blocked(
            "owner_approval_required_for_live_capital_increase",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=kill_switch_active,
            margin_guard_ok=not margin_guard_hit,
            max_portfolio_risk_hit=portfolio_risk_hit,
            owner_approval_required_for_live_capital_increase=True,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if portfolio_risk_hit:
        return _blocked(
            "portfolio_risk_cap_hit",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=kill_switch_active,
            margin_guard_ok=not margin_guard_hit,
            max_portfolio_risk_hit=True,
            owner_approval_required_for_live_capital_increase=live_increase_blocked,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if daily_limit_hit:
        return _blocked(
            "daily_loss_limit_hit",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=kill_switch_active,
            margin_guard_ok=not margin_guard_hit,
            max_portfolio_risk_hit=portfolio_risk_hit,
            owner_approval_required_for_live_capital_increase=live_increase_blocked,
            daily_loss_limit_hit=True,
            max_trades_limit_hit=trades_limit_hit,
        )
    if trades_limit_hit:
        return _blocked(
            "max_trades_limit_hit",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            max_pair_risk_percent=max_pair_risk_percent,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            portfolio_risk_percent=portfolio_risk_percent,
            max_open_trades=max_open_trades,
            open_trade_count=open_trade_count,
            max_consecutive_losses=max_consecutive_losses,
            consecutive_losses=consecutive_losses,
            kill_switch_active=kill_switch_active,
            margin_guard_ok=not margin_guard_hit,
            max_portfolio_risk_hit=portfolio_risk_hit,
            owner_approval_required_for_live_capital_increase=live_increase_blocked,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=True,
        )

    return {
        "allowed": True,
        "blocked_reason": "none",
        "pair": pair,
        "action": action,
        "position_size_units": position_size_units,
        "max_position_size_units": max_position_size_units,
        "risk_percent": risk_percent,
        "max_risk_percent": max_risk_percent,
        "max_pair_risk_percent": max_pair_risk_percent,
        "max_portfolio_risk_percent": max_portfolio_risk_percent,
        "portfolio_risk_percent": portfolio_risk_percent,
        "max_open_trades": max_open_trades,
        "open_trade_count": open_trade_count,
        "max_consecutive_losses": max_consecutive_losses,
        "consecutive_losses": consecutive_losses,
        "kill_switch_active": False,
        "margin_guard_ok": True,
        "max_portfolio_risk_hit": False,
        "owner_approval_required_for_live_capital_increase": live_increase_blocked,
        "daily_loss_limit_hit": False,
        "max_trades_limit_hit": False,
        "paper_only": True,
        "safety": PAPER_RISK_SAFETY.copy(),
        "next_safe_action": "Use this paper-only risk decision for local review only.",
    }
