"""Mapping-only demo order intent builder for AIOS Forex."""

from __future__ import annotations

import hashlib
from typing import Any, Mapping


DEMO_MAPPING_MODE = "DEMO_MAPPING_ONLY"
DECISION_ALLOWED = "allowed"
DECISION_BLOCKED = "blocked"

REASON_NONE = "none"
REASON_INVALID_SOURCE = "invalid_order_source"
REASON_PREVIEW_NOT_ALLOWED = "preview_not_allowed"
REASON_APPROVAL_NOT_READY = "approval_state_not_paper_preview_ready"
REASON_CONNECTOR_NOT_ALLOWED = "readonly_connector_not_allowed"
REASON_ACCOUNT_ID_PRESENT = "account_id_present"
REASON_CREDENTIALS_LOADED = "credentials_loaded"
REASON_BROKER_WRITE_ENABLED = "broker_write_enabled"
REASON_ORDER_SUBMIT_ENABLED = "order_submit_enabled"
REASON_NETWORK_SUBMIT_ENABLED = "network_submit_enabled"
REASON_LIVE_TRADING_ENABLED = "live_trading_enabled"
REASON_INVALID_UNITS = "invalid_units"
REASON_MISSING_ENTRY_PRICE = "missing_entry_price"
REASON_MISSING_STOP_LOSS = "missing_stop_loss"
REASON_MISSING_TAKE_PROFIT = "missing_take_profit"
REASON_UNSUPPORTED_PAIR = "unsupported_pair"
REASON_UNSUPPORTED_SIDE = "unsupported_side"
REASON_UNSUPPORTED_ORDER_TYPE = "unsupported_order_type"
REASON_STALE_READONLY_DATA = "stale_readonly_data"

SUPPORTED_PAIRS = {"EUR_USD", "GBP_USD", "USD_JPY"}
SUPPORTED_SIDES = {"BUY", "SELL"}
SUPPORTED_ORDER_TYPES = {"MARKET"}


def build_demo_order_intent(
    order_source: Any,
    readonly_state: Any,
    *,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Convert approved paper preview/fill data into a non-submitting demo intent."""

    source = dict(order_source) if isinstance(order_source, Mapping) else {}
    connector = dict(readonly_state) if isinstance(readonly_state, Mapping) else {}
    blocked_reasons: list[str] = []
    warnings: list[str] = []

    if not source:
        blocked_reasons.append(REASON_INVALID_SOURCE)
    if source.get("allowed") is not True:
        blocked_reasons.append(REASON_PREVIEW_NOT_ALLOWED)

    source_kind = _source_kind(source)
    approval_state = _lower(source.get("approval_state"))
    if source_kind == "preview" and approval_state != "paper_preview_ready":
        blocked_reasons.append(REASON_APPROVAL_NOT_READY)
    if source_kind == "unknown":
        blocked_reasons.append(REASON_APPROVAL_NOT_READY)

    if connector.get("allowed") is not True:
        blocked_reasons.append(REASON_CONNECTOR_NOT_ALLOWED)
    if connector.get("fresh") is False or _contains_reason(connector, "stale"):
        blocked_reasons.append(REASON_STALE_READONLY_DATA)

    blocked_reasons.extend(_runtime_blockers(source))
    blocked_reasons.extend(_runtime_blockers(connector))

    pair = _normalize_pair(_first(source, "pair", "instrument", "symbol"))
    side = _normalize_side(_first(source, "side", "direction"))
    order_type = _normalize_order_type(_first(source, "order_type", "entry_type", default="market"))
    units = _positive_float(_first(source, "units", "filled_units", "requested_units"))
    entry_price = _positive_float(_first(source, "entry_price", "requested_price", "fill_price"))
    stop_loss = _positive_float(_first_nested(source, "stop_loss", ("trade", "stop_loss")))
    take_profit = _positive_float(_first_nested(source, "take_profit", ("trade", "take_profit")))

    if pair not in SUPPORTED_PAIRS:
        blocked_reasons.append(REASON_UNSUPPORTED_PAIR)
    if side not in SUPPORTED_SIDES:
        blocked_reasons.append(REASON_UNSUPPORTED_SIDE)
    if order_type not in SUPPORTED_ORDER_TYPES:
        blocked_reasons.append(REASON_UNSUPPORTED_ORDER_TYPE)
    if units is None:
        blocked_reasons.append(REASON_INVALID_UNITS)
    if entry_price is None:
        blocked_reasons.append(REASON_MISSING_ENTRY_PRICE)
    if stop_loss is None:
        blocked_reasons.append(REASON_MISSING_STOP_LOSS)
    if take_profit is None:
        blocked_reasons.append(REASON_MISSING_TAKE_PROFIT)

    blocked_reasons = _dedupe(blocked_reasons)
    allowed = not blocked_reasons
    intent = _intent_payload(
        pair=pair,
        side=side,
        units=units,
        order_type=order_type,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        client_order_id=_client_order_id(source, pair, side),
    )

    return {
        "allowed": allowed,
        "decision": DECISION_ALLOWED if allowed else DECISION_BLOCKED,
        "blocked_reason": REASON_NONE if allowed else blocked_reasons[0],
        "blocked_reasons": [],
        "warnings": warnings,
        "mode": DEMO_MAPPING_MODE,
        "demo_order_intent": intent if allowed else {},
        "submit_enabled": False,
        "broker_write_enabled": False,
        "live_trading": False,
        "safety": _safety_dict(),
        "next_safe_action": "handoff_demo_order_intent_for_review" if allowed else "fix_demo_order_mapping_inputs",
        "metadata": {
            "source_kind": source_kind,
            "source_id": _source_id(source),
            "readonly_mode": connector.get("mode"),
            "blocked_reasons": blocked_reasons,
            **dict(metadata or {}),
        },
    } if allowed else {
        "allowed": False,
        "decision": DECISION_BLOCKED,
        "blocked_reason": blocked_reasons[0],
        "blocked_reasons": blocked_reasons,
        "warnings": warnings,
        "mode": DEMO_MAPPING_MODE,
        "demo_order_intent": {},
        "submit_enabled": False,
        "broker_write_enabled": False,
        "live_trading": False,
        "safety": _safety_dict(),
        "next_safe_action": "fix_demo_order_mapping_inputs",
        "metadata": {
            "source_kind": source_kind,
            "source_id": _source_id(source),
            "readonly_mode": connector.get("mode"),
            **dict(metadata or {}),
        },
    }


def _intent_payload(
    *,
    pair: str,
    side: str,
    units: float | None,
    order_type: str,
    entry_price: float | None,
    stop_loss: float | None,
    take_profit: float | None,
    client_order_id: str,
) -> dict[str, Any]:
    key = _idempotency_key(pair, side, units, order_type, entry_price, stop_loss, take_profit, client_order_id)
    return {
        "pair": pair,
        "side": side,
        "units": units,
        "order_type": order_type,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "client_order_id": client_order_id,
        "idempotency_key": key,
        "mode": DEMO_MAPPING_MODE,
        "submit_enabled": False,
        "broker_write_enabled": False,
        "live_trading": False,
        "safety": _safety_dict(),
    }


def _runtime_blockers(value: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for key, nested in _walk(value):
        normalized = _normalize_key(key)
        if "account" in normalized and "id" in normalized and _present(nested):
            blockers.append(REASON_ACCOUNT_ID_PRESENT)
        if "credential" in normalized and "load" in normalized and _truthy(nested):
            blockers.append(REASON_CREDENTIALS_LOADED)
        if "broker" in normalized and "write" in normalized and _truthy(nested):
            blockers.append(REASON_BROKER_WRITE_ENABLED)
        if "order" in normalized and "submit" in normalized and _truthy(nested):
            blockers.append(REASON_ORDER_SUBMIT_ENABLED)
        if "network" in normalized and "submit" in normalized and _truthy(nested):
            blockers.append(REASON_NETWORK_SUBMIT_ENABLED)
        if "live" in normalized and "trading" in normalized and _truthy(nested):
            blockers.append(REASON_LIVE_TRADING_ENABLED)
        if isinstance(nested, str) and _looks_like_account_identifier(nested):
            blockers.append(REASON_ACCOUNT_ID_PRESENT)
    return blockers


def _source_kind(source: Mapping[str, Any]) -> str:
    if "fill_id" in source or "filled_units" in source or "fill_price" in source:
        return "paper_fill"
    if "approval_state" in source or "preview_id" in source:
        return "preview"
    return "unknown"


def _source_id(source: Mapping[str, Any]) -> str:
    for key in ("preview_id", "fill_id", "trade_id", "client_order_id"):
        value = source.get(key)
        if value not in (None, ""):
            return str(value)
    return "unknown"


def _client_order_id(source: Mapping[str, Any], pair: str, side: str) -> str:
    for key in ("client_order_id", "preview_id", "fill_id"):
        value = source.get(key)
        if value not in (None, ""):
            return str(value)
    return f"AIOS-DEMO-MAP-{pair}-{side}"


def _idempotency_key(*parts: Any) -> str:
    raw = "|".join(str(part) for part in parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"demo-map-{digest[:20]}"


def _first(source: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        value = source.get(key)
        if value not in (None, ""):
            return value
    return default


def _first_nested(source: Mapping[str, Any], direct_key: str, nested_path: tuple[str, str]) -> Any:
    direct = source.get(direct_key)
    if direct not in (None, ""):
        return direct
    nested = source.get(nested_path[0])
    if isinstance(nested, Mapping):
        return nested.get(nested_path[1])
    return None


def _normalize_pair(value: Any) -> str:
    text = str(value or "").strip().upper().replace("/", "_").replace("-", "_")
    text = text.replace(" ", "")
    if len(text) == 6 and "_" not in text:
        return f"{text[:3]}_{text[3:]}"
    return text


def _normalize_side(value: Any) -> str:
    text = str(value or "").strip().upper()
    if text in {"BUY", "LONG"}:
        return "BUY"
    if text in {"SELL", "SHORT"}:
        return "SELL"
    return text


def _normalize_order_type(value: Any) -> str:
    return str(value or "").strip().upper().replace(" ", "_")


def _positive_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _contains_reason(value: Mapping[str, Any], marker: str) -> bool:
    reasons = value.get("blocked_reasons", [])
    if not isinstance(reasons, list):
        return False
    return any(marker in str(reason).lower() for reason in reasons)


def _walk(value: Any) -> list[tuple[str, Any]]:
    out: list[tuple[str, Any]] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            out.append((str(key), nested))
            out.extend(_walk(nested))
    elif isinstance(value, list):
        for nested in value:
            out.extend(_walk(nested))
    return out


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "on"}
    return False


def _present(value: Any) -> bool:
    return value not in (None, "", [], {})


def _looks_like_account_identifier(value: str) -> bool:
    parts = value.strip().split("-")
    return len(parts) >= 3 and all(part.isdigit() for part in parts)


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _lower(value: Any) -> str:
    return str(value or "").strip().lower()


def _dedupe(items: list[str]) -> list[str]:
    ordered: list[str] = []
    for item in items:
        if item and item not in ordered:
            ordered.append(item)
    return ordered


def _safety_dict() -> dict[str, bool]:
    return {
        "paper_only": True,
        "demo_mapping_only": True,
        "submit_enabled": False,
        "broker_write_enabled": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_submit": False,
    }
