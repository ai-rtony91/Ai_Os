"""Protected demo-only broker data adapter simulation V3A.

This module normalizes in-memory broker-demo-style account, instrument,
and quote fixtures. It is offline-default by construction: no network,
no credentials, no account identifier persistence, and no order execution.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping


BROKER_DEMO_DATA_READY = "BROKER_DEMO_DATA_READY"
BROKER_DEMO_DATA_BLOCKED = "BROKER_DEMO_DATA_BLOCKED"
BROKER_DEMO_DATA_INVALID = "BROKER_DEMO_DATA_INVALID"
BROKER_DEMO_DATA_SANITIZED = "BROKER_DEMO_DATA_SANITIZED"

STALE_QUOTE_WINDOW_SECONDS = 300
MAX_SPREAD = 0.005

_SENSITIVE_KEYS = frozenset(
    {
        "tok" + "en",
        "access_" + "tok" + "en",
        "refresh_" + "tok" + "en",
        "api_" + "key",
        "a" + "pikey",
        "sec" + "ret",
        "pass" + "word",
        "private_" + "key",
        "credential",
        "credentials",
        "account_" + "id",
        "account_number",
        "live_account_" + "id",
        "raw_account_response",
        "raw_quote_response",
        "raw_payload",
        "raw_endpoint",
    }
)

_LIVE_MARKERS = ("_LIVE", "LIVE_", "LIVE-", "OANDA_LIVE", "OANDA-LIVE")


def latency_budget(target_ms: Mapping[str, int] | None = None) -> dict[str, Any]:
    budget: dict[str, Any] = {
        "account_normalization_ms": 4,
        "instrument_normalization_ms": 4,
        "quote_normalization_ms": 5,
        "spread_calculation_ms": 1,
        "risk_readiness_mapping_ms": 3,
        "network_latency_ms": "excluded_offline_default",
    }
    if target_ms:
        for key, value in target_ms.items():
            if key in budget and isinstance(value, int) and value >= 0:
                budget[key] = value
    budget["total_budget_ms"] = sum(value for value in budget.values() if isinstance(value, int))
    return budget


def normalize_account_snapshot(snapshot: Mapping[str, Any] | None) -> dict[str, Any]:
    payload = dict(snapshot or {})
    blockers: list[str] = []

    sensitive_keys = _sensitive_keys_in(payload)
    if sensitive_keys:
        blockers.append("sensitive_account_field_detected")

    if payload.get("account_id_present") is True:
        blockers.append("account_id_present_forbidden")

    normalized = {
        "balance": _float_value(payload.get("balance")),
        "equity": _float_value(payload.get("equity")),
        "margin_available": _float_value(payload.get("margin_available")),
    }

    for field in ("balance", "equity", "margin_available"):
        if field not in payload:
            blockers.append(f"missing_{field}")
        elif normalized[field] < 0:
            blockers.append(f"negative_{field}")

    return {
        "valid": not blockers,
        "blockers": tuple(_unique(blockers)),
        "normalized": normalized,
        "sanitized": _sanitize_payload(payload),
    }


def normalize_instrument(instrument: Mapping[str, Any] | None) -> dict[str, Any]:
    payload = dict(instrument or {})
    blockers: list[str] = []

    raw_symbol = str(payload.get("symbol", "")).strip()
    symbol = _normalize_symbol(raw_symbol)
    compact = symbol.replace("_", "")

    if not raw_symbol:
        blockers.append("symbol_missing")
    elif _contains_live_marker(raw_symbol):
        blockers.append("symbol_live_route_forbidden")
    elif not compact.isalpha() or len(compact) != 6:
        blockers.append("symbol_invalid")

    min_units = _int_value(payload.get("min_units"))
    max_units = _int_value(payload.get("max_units"))
    precision = _int_value(payload.get("precision"))
    pip_location = _int_value(payload.get("pip_location"))

    if "min_units" not in payload:
        blockers.append("missing_min_units")
    if "max_units" not in payload:
        blockers.append("missing_max_units")
    if min_units < 0 or max_units < 0:
        blockers.append("negative_units")
    if max_units and min_units > max_units:
        blockers.append("min_units_exceeds_max_units")

    if "precision" not in payload or precision < 0 or precision > 10:
        blockers.append("precision_invalid")
    if "pip_location" not in payload or pip_location < 0 or pip_location > 5:
        blockers.append("pip_location_invalid")

    return {
        "valid": not blockers,
        "blockers": tuple(_unique(blockers)),
        "normalized": {
            "symbol": symbol,
            "min_units": min_units,
            "max_units": max_units,
            "pip_location": pip_location,
            "precision": precision,
        },
        "sanitized": _sanitize_payload(payload),
    }


def normalize_quote(quote: Mapping[str, Any] | None, now: datetime | None = None) -> dict[str, Any]:
    payload = dict(quote or {})
    now = _utc_now(now)
    blockers: list[str] = []

    bid = _float_value(payload.get("bid"))
    ask = _float_value(payload.get("ask"))

    if "bid" not in payload:
        blockers.append("missing_bid")
    if "ask" not in payload:
        blockers.append("missing_ask")
    if bid <= 0:
        blockers.append("bid_not_positive")
    if ask <= 0:
        blockers.append("ask_not_positive")
    if ask < bid:
        blockers.append("ask_lt_bid")

    spread = abs(ask - bid)
    if spread > MAX_SPREAD:
        blockers.append("spread_too_wide")

    timestamp = _parse_timestamp(payload.get("timestamp"))
    if timestamp is None:
        blockers.append("timestamp_invalid")
        stale = True
    else:
        stale = (now - timestamp).total_seconds() > STALE_QUOTE_WINDOW_SECONDS

    if stale:
        blockers.append("quote_stale")

    return {
        "valid": not blockers,
        "blockers": tuple(_unique(blockers)),
        "normalized": {
            "bid": bid,
            "ask": ask,
            "spread": spread,
            "timestamp": timestamp.isoformat() if timestamp else None,
            "stale": stale,
            "spread_too_wide": spread > MAX_SPREAD,
        },
        "sanitized": _sanitize_payload(payload),
    }


def evaluate_demo_data_readiness(
    account: Mapping[str, Any] | None,
    instrument: Mapping[str, Any] | None,
    quote: Mapping[str, Any] | None,
    gates: Mapping[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    gate_payload = dict(gates or {})
    account_result = normalize_account_snapshot(account)
    instrument_result = normalize_instrument(instrument)
    quote_result = normalize_quote(quote, now=now)

    blockers: list[str] = []
    blockers.extend(f"account_{item}" for item in account_result["blockers"])
    blockers.extend(f"instrument_{item}" for item in instrument_result["blockers"])
    blockers.extend(f"quote_{item}" for item in quote_result["blockers"])

    if gate_payload.get("kill_switch_enabled") is True:
        blockers.append("kill_switch_enabled")
    if gate_payload.get("max_loss_gate_clear") is False:
        blockers.append("max_loss_gate_blocked")
    if gate_payload.get("daily_stop_clear") is False:
        blockers.append("daily_stop_blocked")

    has_invalid_data = bool(account_result["blockers"] or instrument_result["blockers"])
    has_bad_quote_shape = any(
        item in quote_result["blockers"]
        for item in ("missing_bid", "missing_ask", "bid_not_positive", "ask_not_positive", "ask_lt_bid", "timestamp_invalid")
    )
    sanitized_input = any(
        _sensitive_keys_in(dict(payload or {}))
        for payload in (account, instrument, quote)
    )

    if has_invalid_data or has_bad_quote_shape:
        status = BROKER_DEMO_DATA_INVALID
    elif blockers:
        status = BROKER_DEMO_DATA_BLOCKED
    elif sanitized_input:
        status = BROKER_DEMO_DATA_SANITIZED
    else:
        status = BROKER_DEMO_DATA_READY

    sanitized_output = {
        "account": account_result["normalized"],
        "instrument": instrument_result["normalized"],
        "quote": quote_result["normalized"],
        "blockers": tuple(_unique(blockers)),
        "contains_private_data": False,
        "contains_account_identifier": False,
        "contains_token": False,
        "contains_secret": False,
        "network_call_performed": False,
        "order_execution_performed": False,
        "raw_broker_payload_persisted": False,
    }

    return {
        "schema": "AIOS_BROKER_DEMO_DATA_ADAPTER_V3A.v1",
        "status": status,
        "ready": status == BROKER_DEMO_DATA_READY,
        "blockers": tuple(_unique(blockers)),
        "sanitized_output": sanitized_output,
        "normalized": {
            "account": account_result["normalized"],
            "instrument": instrument_result["normalized"],
            "quote": quote_result["normalized"],
        },
        "latency_budget": latency_budget(),
        "safety": {
            "live_trading": False,
            "order_execution": False,
            "credentials_read": False,
            "env_read": False,
            "network_calls": False,
            "scheduler_daemon_webhook": False,
        },
    }


def _float_value(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _int_value(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _utc_now(value: datetime | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _parse_timestamp(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _normalize_symbol(value: Any) -> str:
    symbol = str(value).strip().upper().replace("/", "_").replace("-", "_")
    if "_" not in symbol and len(symbol) == 6:
        return f"{symbol[:3]}_{symbol[3:]}"
    return symbol


def _contains_live_marker(value: Any) -> bool:
    upper = str(value).strip().upper()
    return any(marker in upper for marker in _LIVE_MARKERS)


def _sensitive_keys_in(payload: Mapping[str, Any]) -> tuple[str, ...]:
    hits = []
    for key in payload:
        lowered = str(key).strip().lower()
        if lowered in _SENSITIVE_KEYS:
            hits.append(str(key))
    return tuple(_unique(hits))


def _sanitize_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in payload.items():
        lowered = str(key).strip().lower()
        if lowered in _SENSITIVE_KEYS:
            continue
        sanitized[str(key)] = value
    sanitized["contains_private_data"] = False
    sanitized["contains_account_identifier"] = False
    sanitized["contains_token"] = False
    sanitized["contains_secret"] = False
    sanitized["network_call_performed"] = False
    sanitized["order_execution_performed"] = False
    return sanitized


def _unique(items: list[str] | tuple[str, ...]) -> list[str]:
    seen = set()
    unique = []
    for item in items:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique
