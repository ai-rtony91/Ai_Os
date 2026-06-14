from __future__ import annotations

from typing import Any


SUPPORTED_PAIRS = {"EURUSD", "GBPUSD", "USDJPY"}
REQUIRED_FIELDS = ("timestamp", "pair", "open", "high", "low", "close")
OPTIONAL_NUMERIC_FIELDS = ("volume", "fast_ma", "slow_ma", "momentum")
NUMERIC_FIELDS = ("open", "high", "low", "close", *OPTIONAL_NUMERIC_FIELDS)

PAPER_DATA_IMPORT_SAFETY = {
    "paper_only": True,
    "research_only": True,
    "network_access": False,
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


def blocked_row(reason: str) -> dict[str, Any]:
    return {
        "allowed": False,
        "status": "blocked",
        "blocked_reason": reason,
        **PAPER_DATA_IMPORT_SAFETY,
    }


def _blocked_scope_reason(row: dict[str, Any]) -> str | None:
    for field in sorted(BLOCKED_SCOPE_FIELDS):
        if row.get(field):
            return f"{field}_blocked"
    return None


def _parse_number(value: Any, field: str) -> tuple[float | None, str | None]:
    try:
        return float(value), None
    except (TypeError, ValueError):
        return None, f"invalid_numeric_{field}"


def normalize_csv_row(row: dict[str, Any]) -> dict[str, Any]:
    blocked_reason = _blocked_scope_reason(row)
    if blocked_reason:
        return blocked_row(blocked_reason)

    for field in REQUIRED_FIELDS:
        if row.get(field) in (None, ""):
            return blocked_row(f"missing_{field}")

    pair = str(row["pair"]).upper()
    if pair not in SUPPORTED_PAIRS:
        return blocked_row("unsupported_pair")

    candle: dict[str, Any] = {
        "allowed": True,
        "status": "normalized",
        "timestamp": str(row["timestamp"]),
        "pair": pair,
        **PAPER_DATA_IMPORT_SAFETY,
    }

    for field in NUMERIC_FIELDS:
        if field not in row or row.get(field) in (None, ""):
            continue
        parsed, reason = _parse_number(row.get(field), field)
        if reason:
            return blocked_row(reason)
        candle[field] = parsed

    if candle["high"] < candle["low"]:
        return blocked_row("invalid_ohlc_high_below_low")
    if candle["high"] < max(candle["open"], candle["close"]):
        return blocked_row("invalid_ohlc_high_below_open_or_close")
    if candle["low"] > min(candle["open"], candle["close"]):
        return blocked_row("invalid_ohlc_low_above_open_or_close")

    return candle


def normalize_csv_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    records = [normalize_csv_row(row) for row in rows]
    candles = [record for record in records if record.get("allowed")]
    blocked = [record for record in records if not record.get("allowed")]
    return {
        "rows_received": len(rows),
        "candles_normalized": len(candles),
        "rows_blocked": len(blocked),
        "candles": candles,
        "blocked_rows": blocked,
        **PAPER_DATA_IMPORT_SAFETY,
    }
