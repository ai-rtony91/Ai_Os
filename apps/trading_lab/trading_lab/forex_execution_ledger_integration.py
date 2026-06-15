from __future__ import annotations

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


def _blocked(reason: str, *, safety: dict[str, bool], execution_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "allowed": False,
        "blocked_reason": reason,
        "paper_only": True,
        "paper_order_id": execution_result.get("paper_order_id"),
        "pair": str(execution_result.get("pair", "")).upper(),
        "action": str(execution_result.get("action", "")).lower(),
        "filled_units": int(execution_result.get("filled_units", 0) or 0),
        "fill_price": execution_result.get("fill_price"),
        "slippage_pips": float(execution_result.get("slippage_pips", 0.0) or 0.0),
        "spread_pips": float(execution_result.get("spread_pips", 0.0) or 0.0),
        "realized_pnl": 0.0,
        "status": "blocked",
        "ledger_event_type": "blocked_paper_execution",
        "source": "forex_paper_execution_simulator",
        "safety": safety,
        "next_safe_action": "Stop ledger integration and inspect the blocked reason.",
    }


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _realized_pnl(action: str, filled_units: int, fill_price: float, metadata: dict[str, Any]) -> float:
    exit_price = metadata.get("exit_price")
    if exit_price is None:
        return 0.0
    exit_value = _safe_float(exit_price)
    if action == "buy":
        return round((exit_value - fill_price) * filled_units, 2)
    if action == "sell":
        return round((fill_price - exit_value) * filled_units, 2)
    return 0.0


def build_execution_ledger_record(
    execution_result: dict[str, Any],
    signal: dict[str, Any],
    account_snapshot: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    **safety_flags: Any,
) -> dict[str, Any]:
    execution = execution_result if isinstance(execution_result, dict) else {}
    signal = signal if isinstance(signal, dict) else {}
    metadata = metadata if isinstance(metadata, dict) else {}
    safety = _base_safety()

    for flag in SAFETY_BLOCK_FLAGS:
        if bool(safety_flags.get(flag)):
            safety[flag] = True
            return _blocked(f"safety_flag_{flag}", safety=safety, execution_result=execution)

    pair = str(execution.get("pair") or signal.get("pair") or "").upper()
    action = str(execution.get("action") or signal.get("action") or "").lower()
    paper_order_id = execution.get("paper_order_id")
    filled_units = int(execution.get("filled_units", 0) or 0)
    fill_price = execution.get("fill_price")

    if execution.get("allowed") is False:
        return _blocked("execution_not_allowed", safety=safety, execution_result=execution)
    if pair not in SUPPORTED_PAIRS:
        return _blocked("invalid_pair", safety=safety, execution_result={**execution, "pair": pair, "action": action})
    if action not in SUPPORTED_ACTIONS:
        return _blocked(
            "unsupported_action",
            safety=safety,
            execution_result={**execution, "pair": pair, "action": action},
        )
    if not paper_order_id:
        return _blocked(
            "missing_paper_order_id",
            safety=safety,
            execution_result={**execution, "pair": pair, "action": action},
        )
    if action in {"buy", "sell"} and execution.get("executed") is not True:
        return _blocked(
            "execution_required_for_trade_action",
            safety=safety,
            execution_result={**execution, "pair": pair, "action": action},
        )
    if action in {"buy", "sell"} and fill_price is None:
        return _blocked(
            "missing_fill_price",
            safety=safety,
            execution_result={**execution, "pair": pair, "action": action},
        )

    if action == "hold" and execution.get("executed") is False:
        return {
            "allowed": True,
            "blocked_reason": "none",
            "paper_only": True,
            "paper_order_id": paper_order_id,
            "pair": pair,
            "action": action,
            "filled_units": 0,
            "fill_price": None,
            "slippage_pips": _safe_float(execution.get("slippage_pips", 0.0)),
            "spread_pips": _safe_float(execution.get("spread_pips", 0.0)),
            "realized_pnl": 0.0,
            "status": "no_fill_hold",
            "ledger_event_type": "paper_hold",
            "source": "forex_paper_execution_simulator",
            "safety": safety,
            "next_safe_action": "Record hold event in paper ledger only.",
        }

    fill_price_value = _safe_float(fill_price)
    return {
        "allowed": True,
        "blocked_reason": "none",
        "paper_only": True,
        "paper_order_id": paper_order_id,
        "pair": pair,
        "action": action,
        "filled_units": filled_units,
        "fill_price": fill_price_value,
        "slippage_pips": _safe_float(execution.get("slippage_pips", 0.0)),
        "spread_pips": _safe_float(execution.get("spread_pips", 0.0)),
        "realized_pnl": _realized_pnl(action, filled_units, fill_price_value, metadata),
        "status": "filled",
        "ledger_event_type": "paper_execution_fill",
        "source": "forex_paper_execution_simulator",
        "safety": safety,
        "next_safe_action": "Append this deterministic paper event to the paper ledger/report chain.",
    }
