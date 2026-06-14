from __future__ import annotations

from typing import Any


SUPPORTED_PAIRS = {"EURUSD", "GBPUSD", "USDJPY"}
SUPPORTED_DIRECTIONS = {"buy", "sell"}

PAPER_LEDGER_SAFETY = {
    "paper_only": True,
    "execution_allowed": False,
    "broker_execution": False,
    "credential_use": False,
    "live_trading": False,
    "real_orders": False,
    "real_webhooks": False,
}

BLOCKED_SCOPE_FIELDS = {
    "api_key",
    "broker_order",
    "credentials",
    "live_execution",
    "real_order",
    "webhook_url",
}


def blocked_record(reason: str) -> dict[str, Any]:
    return {
        "allowed": False,
        "record_type": "blocked",
        "blocked_reason": reason,
        **PAPER_LEDGER_SAFETY,
    }


def _pip_size(pair: str) -> float:
    return 0.01 if pair.endswith("JPY") else 0.0001


def _blocked_scope_reason(payload: dict[str, Any]) -> str | None:
    for field in sorted(BLOCKED_SCOPE_FIELDS):
        if payload.get(field):
            return f"{field}_blocked"
    return None


def _result_pips(pair: str, direction: str, entry: float, target: float) -> float:
    pip_size = _pip_size(pair)
    if direction == "buy":
        return round((target - entry) / pip_size, 1)
    return round((entry - target) / pip_size, 1)


def record_paper_trade(
    *,
    pair: str,
    direction: str,
    entry: float,
    stop: float,
    target: float,
    position_size: float,
    timestamp: str,
    live_execution: bool = False,
    broker_order: bool = False,
    credentials: Any = None,
    api_key: Any = None,
    real_order: bool = False,
    webhook_url: str | None = None,
) -> dict[str, Any]:
    payload = {
        "live_execution": live_execution,
        "broker_order": broker_order,
        "credentials": credentials,
        "api_key": api_key,
        "real_order": real_order,
        "webhook_url": webhook_url,
    }
    blocked_reason = _blocked_scope_reason(payload)
    if blocked_reason:
        return blocked_record(blocked_reason)

    normalized_pair = str(pair).upper()
    normalized_direction = str(direction).lower()
    if normalized_pair not in SUPPORTED_PAIRS:
        return blocked_record("unsupported_pair")
    if normalized_direction not in SUPPORTED_DIRECTIONS:
        return blocked_record("unsupported_direction")
    if position_size <= 0:
        return blocked_record("position_size_must_be_positive")

    entry_value = float(entry)
    stop_value = float(stop)
    target_value = float(target)
    size_value = float(position_size)
    result_pips = _result_pips(normalized_pair, normalized_direction, entry_value, target_value)
    if normalized_direction == "buy":
        pnl = (target_value - entry_value) * size_value
    else:
        pnl = (entry_value - target_value) * size_value

    return {
        "allowed": True,
        "record_type": "paper_trade",
        "pair": normalized_pair,
        "direction": normalized_direction,
        "entry": entry_value,
        "stop": stop_value,
        "target": target_value,
        "position_size": size_value,
        "result_pips": result_pips,
        "pnl": round(pnl, 2),
        "timestamp": timestamp,
        **PAPER_LEDGER_SAFETY,
    }


def summarize_paper_ledger(trades: list[dict[str, Any]]) -> dict[str, Any]:
    records = [record_paper_trade(**trade) for trade in trades]
    allowed_records = [record for record in records if record.get("allowed")]
    winning_trades = [record for record in allowed_records if record["pnl"] > 0]
    losing_trades = [record for record in allowed_records if record["pnl"] < 0]
    total_pnl = round(sum(record["pnl"] for record in allowed_records), 2)
    return {
        "trade_count": len(allowed_records),
        "winning_trades": len(winning_trades),
        "losing_trades": len(losing_trades),
        "blocked_trades": len(records) - len(allowed_records),
        "total_pnl": total_pnl,
        "records": records,
        **PAPER_LEDGER_SAFETY,
    }
