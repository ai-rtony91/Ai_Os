from __future__ import annotations

import hashlib
from typing import Any


SUPPORTED_PAIRS = {"EURUSD", "GBPUSD", "USDJPY"}
SUPPORTED_ACTIONS = {"buy", "sell", "hold"}
SAFETY_BLOCK_FLAGS = {
    "live_execution",
    "broker_order",
    "credentials",
    "api_key",
    "real_order",
    "webhook_url",
    "network",
    "network_access",
}


def _base_safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "live_execution": False,
        "broker_order": False,
        "credentials": False,
        "api_key": False,
        "real_order": False,
        "webhook_url": False,
        "network": False,
        "network_access": False,
        "broker": False,
        "live_trading": False,
        "real_orders": False,
        "real_webhooks": False,
    }


def _pip_size(pair: str) -> float:
    return 0.01 if pair.endswith("JPY") else 0.0001


def _price_precision(pair: str) -> int:
    return 3 if pair.endswith("JPY") else 5


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_units(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _market_for_pair(pair: str, market: dict[str, Any]) -> dict[str, Any]:
    nested = market.get(pair)
    if isinstance(nested, dict):
        return nested
    return market


def _paper_order_id(pair: str, action: str, units: int, price: float | None) -> str:
    price_text = "none" if price is None else f"{price:.5f}"
    digest = hashlib.sha256(f"{pair}|{action}|{units}|{price_text}".encode("utf-8")).hexdigest()[:12].upper()
    return f"PAPER-{pair}-{action.upper()}-{digest}"


def _blocked(
    *,
    reason: str,
    pair: str,
    action: str,
    requested_units: int,
    requested_price: float | None,
    fill_price: float | None,
    spread_pips: float,
    slippage_pips: float,
    safety: dict[str, bool],
) -> dict[str, Any]:
    return {
        "allowed": False,
        "executed": False,
        "blocked_reason": reason,
        "pair": pair,
        "action": action,
        "requested_units": requested_units,
        "filled_units": 0,
        "requested_price": requested_price,
        "fill_price": fill_price,
        "slippage_pips": slippage_pips,
        "spread_pips": spread_pips,
        "paper_order_id": _paper_order_id(pair, action, requested_units, fill_price),
        "paper_only": True,
        "execution_quality": {
            "spread_pips": spread_pips,
            "slippage_pips": slippage_pips,
            "accepted": False,
            "rejected_reason": reason,
        },
        "safety": safety,
        "next_safe_action": "Stop paper execution simulation and inspect the blocked reason.",
    }


def simulate_paper_execution(
    signal: dict[str, Any],
    risk_result: dict[str, Any],
    market: dict[str, Any],
    config: dict[str, Any] | None = None,
    **safety_flags: Any,
) -> dict[str, Any]:
    config = config if isinstance(config, dict) else {}
    signal = signal if isinstance(signal, dict) else {}
    risk_result = risk_result if isinstance(risk_result, dict) else {}
    market = market if isinstance(market, dict) else {}

    pair = str(signal.get("pair") or risk_result.get("pair") or "").upper()
    action = str(signal.get("action") or risk_result.get("action") or "").lower()
    requested_units = _as_units(
        signal.get("position_size_units", signal.get("units", risk_result.get("position_size_units", 0)))
    )
    safety = _base_safety()

    for flag in SAFETY_BLOCK_FLAGS:
        if bool(safety_flags.get(flag)):
            safety[flag] = True
            return _blocked(
                reason=f"safety_flag_{flag}",
                pair=pair,
                action=action,
                requested_units=requested_units,
                requested_price=None,
                fill_price=None,
                spread_pips=0.0,
                slippage_pips=0.0,
                safety=safety,
            )

    if risk_result.get("allowed") is False:
        return _blocked(
            reason="risk_controls_blocked",
            pair=pair,
            action=action,
            requested_units=requested_units,
            requested_price=None,
            fill_price=None,
            spread_pips=0.0,
            slippage_pips=0.0,
            safety=safety,
        )
    if pair not in SUPPORTED_PAIRS:
        return _blocked(
            reason="invalid_pair",
            pair=pair,
            action=action,
            requested_units=requested_units,
            requested_price=None,
            fill_price=None,
            spread_pips=0.0,
            slippage_pips=0.0,
            safety=safety,
        )
    if action not in SUPPORTED_ACTIONS:
        return _blocked(
            reason="unsupported_action",
            pair=pair,
            action=action,
            requested_units=requested_units,
            requested_price=None,
            fill_price=None,
            spread_pips=0.0,
            slippage_pips=0.0,
            safety=safety,
        )
    if action in {"buy", "sell"} and requested_units <= 0:
        return _blocked(
            reason="non_positive_units",
            pair=pair,
            action=action,
            requested_units=requested_units,
            requested_price=None,
            fill_price=None,
            spread_pips=0.0,
            slippage_pips=0.0,
            safety=safety,
        )

    pair_market = _market_for_pair(pair, market)
    bid = pair_market.get("bid")
    ask = pair_market.get("ask")
    if bid is None or ask is None:
        return _blocked(
            reason="missing_market_price",
            pair=pair,
            action=action,
            requested_units=requested_units,
            requested_price=None,
            fill_price=None,
            spread_pips=0.0,
            slippage_pips=0.0,
            safety=safety,
        )

    pip_size = _pip_size(pair)
    bid_price = _as_float(bid)
    ask_price = _as_float(ask)
    spread_pips = round((ask_price - bid_price) / pip_size, 4)
    slippage_pips = _as_float(config.get("slippage_pips", signal.get("slippage_pips", 0.0)))
    max_spread_pips = _as_float(config.get("max_spread_pips", 3.0), 3.0)
    max_slippage_pips = _as_float(config.get("max_slippage_pips", 1.0), 1.0)

    requested_price = None
    if action == "buy":
        requested_price = ask_price
    elif action == "sell":
        requested_price = bid_price
    elif action == "hold":
        requested_units = 0

    if spread_pips > max_spread_pips:
        return _blocked(
            reason="spread_limit_exceeded",
            pair=pair,
            action=action,
            requested_units=requested_units,
            requested_price=requested_price,
            fill_price=None,
            spread_pips=spread_pips,
            slippage_pips=slippage_pips,
            safety=safety,
        )
    if slippage_pips > max_slippage_pips:
        return _blocked(
            reason="slippage_limit_exceeded",
            pair=pair,
            action=action,
            requested_units=requested_units,
            requested_price=requested_price,
            fill_price=None,
            spread_pips=spread_pips,
            slippage_pips=slippage_pips,
            safety=safety,
        )

    fill_price = None
    executed = False
    filled_units = 0
    if action == "buy":
        fill_price = round(ask_price + (slippage_pips * pip_size), _price_precision(pair))
        executed = True
        filled_units = requested_units
    elif action == "sell":
        fill_price = round(bid_price - (slippage_pips * pip_size), _price_precision(pair))
        executed = True
        filled_units = requested_units

    return {
        "allowed": True,
        "executed": executed,
        "blocked_reason": "none",
        "pair": pair,
        "action": action,
        "requested_units": requested_units,
        "filled_units": filled_units,
        "requested_price": requested_price,
        "fill_price": fill_price,
        "slippage_pips": slippage_pips,
        "spread_pips": spread_pips,
        "paper_order_id": _paper_order_id(pair, action, requested_units, fill_price),
        "paper_only": True,
        "execution_quality": {
            "spread_pips": spread_pips,
            "slippage_pips": slippage_pips,
            "accepted": True,
            "rejected_reason": "none",
        },
        "safety": safety,
        "next_safe_action": "Record the simulated paper execution only in paper/research state.",
    }
