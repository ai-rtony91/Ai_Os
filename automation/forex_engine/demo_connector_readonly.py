"""Read-only demo connector validator for AIOS Forex snapshots."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


DEMO_CONNECTOR_SCHEMA = "AIOS_FOREX_DEMO_CONNECTOR_READONLY.v1"
ALLOWED_MODES = ("PAPER_ONLY_COMPATIBLE", "DEMO_READONLY")

REJECTION_NONE = "none"
REJECTION_ACCOUNT_ID = "account_identifier_detected"
REJECTION_CREDS = "runtime_material_present"
REJECTION_LIVE = "live_control_enabled"
REJECTION_BROKER_WRITE = "broker_write_enabled"
REJECTION_ORDER_SUBMIT = "order_submission_enabled"
REJECTION_NETWORK_SUBMIT = "network_submission_enabled"
REJECTION_STALE_DATA = "stale_demo_data"
REJECTION_INVALID_INPUT = "invalid_demo_snapshot"
REJECTION_MODE = "unsupported_demo_mode"


def evaluate_demo_connector_snapshot(
    snapshot: Any,
    *,
    now_timestamp: float | None = None,
    max_data_age_seconds: float = 300.0,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Validate and normalize a read-only demo snapshot.

    The output is a strict allow/deny envelope that preserves a paper/demo-only
    posture while surfacing blocked reasons and readability signals.
    """

    out = _base_payload(snapshot)
    out["metadata"] = dict(metadata or {})
    if metadata is None:
        out["metadata"]["validator"] = DEMO_CONNECTOR_SCHEMA

    if not isinstance(snapshot, dict):
        return _deny(out, REJECTION_INVALID_INPUT, "supply_dict_snapshot")

    _append_external_blockers(out, snapshot)
    account_summary = _build_account_summary(snapshot.get("account_summary", {}))
    price_summary = _build_price_summary(snapshot.get("prices", []))
    position_summary = _build_position_summary(
        snapshot.get("positions_summary", snapshot.get("positions", []))
    )

    out["account_summary"] = account_summary
    out["price_summary"] = price_summary
    out["position_summary"] = position_summary
    out["warnings"] = list(dict.fromkeys(_merge_warnings([], account_summary["warnings"], price_summary["warnings"], position_summary["warnings"])))

    mode, demo_only = _resolve_mode(snapshot.get("mode"), snapshot.get("account_summary"))
    out["mode"] = mode
    out["demo_readonly"] = demo_only
    out["paper_only"] = True

    stale_input = snapshot.get("stale", False)
    read_timestamp = snapshot.get("last_read_timestamp")
    if read_timestamp is None:
        read_timestamp = snapshot.get("data_timestamp", snapshot.get("timestamp"))
    stale_from_timestamp, age_seconds = _evaluate_data_age(
        read_timestamp, now_timestamp, max_data_age_seconds
    )
    out["data_age_seconds"] = age_seconds
    out["fresh"] = not stale_from_timestamp if age_seconds is not None else (not bool(stale_input))

    if stale_input:
        out["blocked_reasons"].append(REJECTION_STALE_DATA)
        out["fresh"] = False

    if age_seconds is not None and age_seconds > max_data_age_seconds:
        out["blocked_reasons"].append(REJECTION_STALE_DATA)
        out["fresh"] = False

    if mode not in ALLOWED_MODES:
        out["blocked_reasons"].append(REJECTION_MODE)

    out["blocked_reasons"] = _dedupe(out["blocked_reasons"] + list(snapshot.get("blocked_reasons", [])))

    out["blocked_reasons"] = [str(item) for item in out["blocked_reasons"] if str(item)]
    if out["blocked_reasons"]:
        out["allowed"] = False
        out["decision"] = "blocked"
        out["blocked_reason"] = out["blocked_reasons"][0]
        out["next_safe_action"] = "supply_fresh_demo_readonly_snapshot"
    out["warnings"] = _dedupe(out["warnings"])
    if not out["warnings"]:
        out["warnings"] = []

    if out["allowed"]:
        out["next_safe_action"] = "consume_demo_readonly_snapshot"

    out["safety"] = {
        "paper_only": True,
        "demo_readonly": True,
        "broker_write": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_submit": False,
    }
    return out


def _base_payload(snapshot: dict[str, Any] | None) -> dict[str, Any]:
    _ = snapshot
    return {
        "allowed": True,
        "decision": "allowed",
        "blocked_reason": REJECTION_NONE,
        "blocked_reasons": [],
        "warnings": [],
        "paper_only": False,
        "mode": "DEMO_READONLY",
        "demo_readonly": True,
        "account_summary": {},
        "price_summary": {},
        "position_summary": {},
        "data_age_seconds": None,
        "fresh": True,
        "safety": {},
        "next_safe_action": "ingest_demo_snapshot",
        "metadata": {},
    }


def _deny(payload: dict[str, Any], reason: str, next_action: str) -> dict[str, Any]:
    payload["allowed"] = False
    payload["decision"] = "blocked"
    payload["blocked_reason"] = reason
    payload["blocked_reasons"] = [reason]
    payload["next_safe_action"] = next_action
    payload["safety"] = {
        "paper_only": True,
        "demo_readonly": False,
        "broker_write": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_submit": False,
    }
    return payload


def _append_external_blockers(payload: dict[str, Any], snapshot: dict[str, Any]) -> None:
    checks = [
        ("account", "id", REJECTION_ACCOUNT_ID),
        ("cred", "load", REJECTION_CREDS),
        ("live", "trading", REJECTION_LIVE),
        ("broker", "write", REJECTION_BROKER_WRITE),
        ("order", "submit", REJECTION_ORDER_SUBMIT),
        ("network", "submit", REJECTION_NETWORK_SUBMIT),
    ]

    for k, v in _walk_mapping(snapshot):
        normalized = _normalize_field_key(k)
        if not normalized:
            continue
        if "account" in normalized and "id" in normalized and _as_str(v):
            payload["blocked_reasons"].append(REJECTION_ACCOUNT_ID)
        if "cred" in normalized and "load" in normalized and _as_bool(v):
            payload["blocked_reasons"].append(REJECTION_CREDS)
        if "live" in normalized and "trading" in normalized and _as_bool(v):
            payload["blocked_reasons"].append(REJECTION_LIVE)
        if "broker" in normalized and "write" in normalized and _as_bool(v):
            payload["blocked_reasons"].append(REJECTION_BROKER_WRITE)
        if "order" in normalized and "submit" in normalized and _as_bool(v):
            payload["blocked_reasons"].append(REJECTION_ORDER_SUBMIT)
        if "network" in normalized and "submit" in normalized and _as_bool(v):
            payload["blocked_reasons"].append(REJECTION_NETWORK_SUBMIT)
        if isinstance(v, str) and _looks_like_account(v):
            payload["blocked_reasons"].append(REJECTION_ACCOUNT_ID)


def _build_account_summary(account_snapshot: Any) -> dict[str, Any]:
    account = account_snapshot if isinstance(account_snapshot, dict) else {}
    balance = account.get("balance")
    balance_present = _as_bool(account.get("balance_is_present"), default=balance is not None)
    currency = _string_or_empty(account.get("currency"))
    instruments = _normalize_instruments(account.get("instruments", []))
    warnings: list[str] = []
    if not balance_present:
        warnings.append("missing_balance")

    return {
        "balance_is_present": bool(balance_present),
        "currency": currency,
        "instruments": instruments,
        "balance": _to_float(balance),
        "warnings": warnings,
    }


def _build_price_summary(raw_prices: Any) -> dict[str, Any]:
    rows = raw_prices if isinstance(raw_prices, list) else ([raw_prices] if isinstance(raw_prices, dict) else [])
    normalized: list[dict[str, Any]] = []
    warnings: list[str] = []

    for row in rows:
        if not isinstance(row, dict):
            warnings.append("price_row_not_mapping")
            continue
        instrument = _string_or_empty(row.get("instrument") or row.get("symbol") or row.get("pair")).upper()
        bid = _to_float(row.get("bid"))
        ask = _to_float(row.get("ask"))
        if bid is None or ask is None:
            warnings.append(f"missing_price_value:{instrument}")
            continue
        if bid <= 0 or ask <= 0 or ask < bid:
            warnings.append(f"invalid_price_values:{instrument}")
            continue
        spread = ask - bid
        summary = {
            "instrument": instrument or "UNKNOWN",
            "bid": bid,
            "ask": ask,
            "mid": (bid + ask) / 2,
            "spread": spread,
        }
        normalized.append(summary)

    return {
        "instruments": normalized,
        "instrument_count": len(normalized),
        "warnings": warnings,
    }


def _build_position_summary(raw_positions: Any) -> dict[str, Any]:
    position_payload = raw_positions
    if isinstance(position_payload, dict):
        nested = position_payload.get("positions")
        position_payload = nested if isinstance(nested, list) else []
    if not isinstance(position_payload, list):
        return {
            "position_count": 0,
            "open_position_count": 0,
            "symbols": [],
            "warnings": ["positions_payload_not_list"],
        }

    symbols = []
    open_count = 0
    for entry in position_payload:
        if not isinstance(entry, dict):
            continue
        instrument = _string_or_empty(entry.get("instrument") or entry.get("symbol")).upper()
        if instrument:
            symbols.append(instrument)
        status = _string_or_empty(entry.get("status") or entry.get("state")).lower()
        if status == "" or status == "open":
            open_count += 1

    return {
        "position_count": len(position_payload),
        "open_position_count": open_count,
        "symbols": sorted(set(symbols)),
        "warnings": [],
    }


def _resolve_mode(*raw_modes: Any) -> tuple[str, bool]:
    for raw in raw_modes:
        if isinstance(raw, dict):
            value = raw.get("mode")
        else:
            value = raw
        candidate = _string_or_empty(value).strip().upper().replace(" ", "_")
        if candidate in ALLOWED_MODES:
            return candidate, True
    return "DEMO_READONLY", True


def _evaluate_data_age(
    raw_timestamp: Any,
    now_timestamp: float | None,
    max_age_seconds: float,
) -> tuple[bool, float | None]:
    parsed_timestamp = _parse_timestamp(raw_timestamp)
    if parsed_timestamp is None:
        return False, None
    if now_timestamp is None:
        return False, None
    age = max(0.0, now_timestamp - float(parsed_timestamp))
    return age > float(max_age_seconds), age


def _parse_timestamp(raw: Any) -> float | None:
    if isinstance(raw, (int, float)):
        return float(raw)
    if not isinstance(raw, str):
        return None
    text = raw.strip()
    if not text:
        return None
    normalized = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized).astimezone(timezone.utc)
    except ValueError:
        return None
    return parsed.timestamp()


def _walk_mapping(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    out: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if isinstance(key, str):
                out.append((key, nested))
            if isinstance(nested, dict):
                out.extend(_walk_mapping(nested, key))
    return out


def _as_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return default


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_float(value: Any) -> float | None:
    return _as_float(value)


def _as_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_or_empty(value: Any) -> str:
    return str(value) if value is not None else ""


def _normalize_instruments(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        value = [value]
    instruments: list[str] = []
    for item in value:
        normalized = _string_or_empty(item).strip().upper()
        if normalized and normalized not in instruments:
            instruments.append(normalized)
    return instruments


def _looks_like_account(value: str) -> bool:
    if not value:
        return False
    parts = value.strip().split("-")
    if len(parts) < 3:
        return False
    return all(part.isdigit() for part in parts)


def _normalize_field_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _dedupe(items: list[str]) -> list[str]:
    out: list[str] = []
    for item in items:
        if item not in out:
            out.append(item)
    return out


def _merge_warnings(*parts: list[str]) -> list[str]:
    merged: list[str] = []
    for part in parts:
        merged.extend(part)
    return merged
