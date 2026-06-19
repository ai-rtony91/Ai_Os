"""Sanitizers for read-only forex broker data.

This module converts broker-shaped payloads into dashboard-safe read models.
It must never preserve secrets, account identifiers, order identifiers,
transaction identifiers, raw broker payloads, or credential material.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


SANITIZED_EVIDENCE_PATH = (
    "Reports/forex_delivery/AIOS_FOREX_READ_ONLY_LIVE_DATA_BRIDGE_DRY_RUN_V1.md"
)

ACCOUNT_ID_KEYS = {
    "accountid",
    "account_id",
    "accountidentifier",
    "account_identifier",
}

STRIP_IDENTIFIER_KEYS = {
    "id",
    "orderid",
    "order_id",
    "tradeid",
    "trade_id",
    "transactionid",
    "transaction_id",
    "clientorderid",
    "client_order_id",
    "clienttradeid",
    "client_trade_id",
    "relatedtransactionids",
    "related_transaction_ids",
}

SECRET_KEY_MARKERS = (
    "authorization",
    "bearer",
    "credential",
    "password",
    "private_key",
    "secret",
    "token",
)

SECRET_VALUE_MARKERS = (
    "authorization:",
    "bearer ",
    "client_secret",
    "password=",
    "private_key",
    "refresh_token",
    "secret=",
    "token=",
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def source_fields(
    *,
    source_type: str,
    source_label: str,
    freshness_utc: str,
    stale_status: str,
    block_reason: str,
) -> dict[str, Any]:
    return {
        "source_type": source_type,
        "source_label": source_label,
        "freshness_utc": freshness_utc,
        "stale_status": stale_status,
        "live_trading_allowed_from_this_data": False,
        "read_only": True,
        "block_reason": block_reason,
        "sanitized_evidence_path": SANITIZED_EVIDENCE_PATH,
    }


def sanitize_tree(value: Any) -> Any:
    """Recursively remove or mask sensitive broker-derived fields."""

    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, nested in value.items():
            normalized = _normalize_key(key)
            if _is_secret_key(normalized):
                continue
            if normalized in ACCOUNT_ID_KEYS:
                sanitized[str(key)] = "MASKED_ACCOUNT_ID"
                continue
            if normalized in STRIP_IDENTIFIER_KEYS or normalized.endswith("transactionids"):
                continue
            sanitized[str(key)] = sanitize_tree(nested)
        return sanitized
    if isinstance(value, list):
        return [sanitize_tree(item) for item in value]
    if isinstance(value, str):
        if _looks_like_secret(value):
            return "REDACTED_SECRET_LIKE_VALUE"
        if _looks_like_account_identifier(value):
            return "MASKED_IDENTIFIER"
    return value


def sanitize_account_summary(
    payload: dict[str, Any] | None,
    *,
    broker_mode: str,
    freshness_utc: str,
    source_context: dict[str, Any],
) -> dict[str, Any]:
    account = _payload_body(payload, "account")
    reachable = bool(account)
    open_position_count = _int_or_none(
        _first_present(account, "openPositionCount", "positionCount", "open_position_count")
    )
    pending_order_count = _int_or_none(
        _first_present(account, "pendingOrderCount", "orderCount", "pending_order_count")
    )
    realized_pl = _safe_text(_first_present(account, "pl", "realizedPL", "realizedPl"))
    unrealized_pl = _safe_text(_first_present(account, "unrealizedPL", "unrealizedPl"))
    margin_available = _safe_text(
        _first_present(account, "marginAvailable", "margin_available", "marginAvailableHomeCurrency")
    )
    block_reason = (
        ""
        if reachable
        else "Broker/account summary is unavailable from the read-only source."
    )

    return {
        **source_context,
        "broker_mode": broker_mode,
        "account_reachable": reachable,
        "open_position_count": open_position_count,
        "pending_order_count": pending_order_count,
        "open_positions_reconciled": open_position_count is not None,
        "pending_orders_reconciled": pending_order_count is not None,
        "daily_pl_available": realized_pl != "UNAVAILABLE",
        "margin_risk_available": margin_available != "UNAVAILABLE",
        "realized_pl": realized_pl,
        "unrealized_pl": unrealized_pl,
        "margin_available": margin_available,
        "block_reason": block_reason or source_context["block_reason"],
    }


def sanitize_positions(
    positions_payload: dict[str, Any] | None,
    trades_payload: dict[str, Any] | None,
    *,
    source_context: dict[str, Any],
) -> dict[str, Any]:
    raw_positions = list(_payload_body(positions_payload, "positions") or [])
    raw_trades = list(_payload_body(trades_payload, "trades") or [])
    positions = [
        _safe_position(position)
        for position in raw_positions
        if isinstance(position, dict)
    ]
    open_trades = [
        _safe_trade(trade)
        for trade in raw_trades
        if isinstance(trade, dict)
    ]
    open_position_count = len(positions)
    open_trade_count = len(open_trades)

    return {
        **source_context,
        "positions_reconciled": positions_payload is not None,
        "open_position_count": open_position_count,
        "open_trade_count": open_trade_count,
        "positions": positions,
        "open_trades": open_trades,
        "block_reason": (
            source_context["block_reason"]
            if positions_payload is None
            else ""
        ),
    }


def sanitize_pending_orders(
    pending_orders_payload: dict[str, Any] | None,
    *,
    source_context: dict[str, Any],
) -> dict[str, Any]:
    orders = list(_payload_body(pending_orders_payload, "orders") or [])
    return {
        **source_context,
        "pending_orders_reconciled": pending_orders_payload is not None,
        "pending_order_count": len(orders),
        "pending_orders": [
            {
                "instrument": _safe_text(order.get("instrument")),
                "type": _safe_text(order.get("type")),
                "units": _safe_text(order.get("units")),
                "price": _safe_text(_first_present(order, "price", "priceBound")),
                "sanitized": True,
            }
            for order in orders
            if isinstance(order, dict)
        ],
        "block_reason": (
            source_context["block_reason"]
            if pending_orders_payload is None
            else ""
        ),
    }


def sanitize_pricing(
    pricing_payload: dict[str, Any] | None,
    *,
    selected_pair: str,
    source_context: dict[str, Any],
) -> dict[str, Any]:
    prices = list(_payload_body(pricing_payload, "prices") or [])
    selected = None
    for price in prices:
        if not isinstance(price, dict):
            continue
        if _safe_text(price.get("instrument")) == selected_pair:
            selected = price
            break
    if selected is None and prices and isinstance(prices[0], dict):
        selected = prices[0]

    bid = _price_from_bucket(selected, "bids") if selected else "UNAVAILABLE"
    ask = _price_from_bucket(selected, "asks") if selected else "UNAVAILABLE"
    mid = _mid_price(bid, ask)

    return {
        **source_context,
        "selected_pair": selected_pair,
        "price_snapshot_available": selected is not None,
        "instrument": _safe_text(selected.get("instrument")) if selected else selected_pair,
        "bid": bid,
        "ask": ask,
        "mid": mid,
        "price_time": _safe_text(selected.get("time")) if selected else "UNAVAILABLE",
        "block_reason": (
            ""
            if selected is not None
            else "Read-only pricing snapshot is unavailable."
        ),
    }


def sanitize_trading_history(
    transactions_payload: dict[str, Any] | None,
    *,
    source_context: dict[str, Any],
) -> dict[str, Any]:
    transactions = list(_payload_body(transactions_payload, "transactions") or [])
    rows: list[dict[str, Any]] = []
    for item in transactions:
        if not isinstance(item, dict):
            continue
        tx_type = _safe_text(item.get("type"))
        if tx_type == "UNAVAILABLE":
            continue
        rows.append(
            {
                "pair": _safe_text(item.get("instrument")),
                "side": _side_from_units(item.get("units")),
                "units": _abs_units(item.get("units")),
                "entry_time": "UNAVAILABLE",
                "exit_time": _safe_text(item.get("time")),
                "duration": "UNAVAILABLE",
                "realized_pl": _safe_text(_first_present(item, "pl", "realizedPL", "realizedPl")),
                "exit_reason": tx_type,
                "slippage": "UNAVAILABLE",
                "source": source_context["source_label"],
                "freshness": source_context["freshness_utc"],
                "evidence_status": "BROKER_READ_ONLY_SANITIZED",
            }
        )

    return {
        **source_context,
        "trading_history_available": bool(rows),
        "closed_trade_count": len(rows),
        "rows": rows,
        "block_reason": (
            ""
            if rows
            else "No sanitized closed-trade history is available from the read-only source."
        ),
    }


def assert_no_forbidden_output(
    payload: Any,
    *,
    forbidden_values: tuple[str | None, ...] = (),
) -> bool:
    text = str(payload)
    lowered = text.lower()
    for marker in SECRET_VALUE_MARKERS:
        if marker in lowered:
            raise ValueError("Sanitized read model contains secret-like material")
    for value in forbidden_values:
        if value and str(value) in text:
            raise ValueError("Sanitized read model contains a forbidden runtime value")
    return True


def _safe_position(position: dict[str, Any]) -> dict[str, Any]:
    long_units = _safe_text((position.get("long") or {}).get("units"))
    short_units = _safe_text((position.get("short") or {}).get("units"))
    return {
        "instrument": _safe_text(position.get("instrument")),
        "long_units": long_units,
        "short_units": short_units,
        "unrealized_pl": _safe_text(_first_present(position, "unrealizedPL", "unrealizedPl")),
        "sanitized": True,
    }


def _safe_trade(trade: dict[str, Any]) -> dict[str, Any]:
    return {
        "instrument": _safe_text(trade.get("instrument")),
        "side": _side_from_units(trade.get("currentUnits")),
        "units": _abs_units(trade.get("currentUnits")),
        "price": _safe_text(trade.get("price")),
        "unrealized_pl": _safe_text(_first_present(trade, "unrealizedPL", "unrealizedPl")),
        "open_time": _safe_text(trade.get("openTime")),
        "sanitized": True,
    }


def _payload_body(payload: dict[str, Any] | None, key: str) -> Any:
    if not isinstance(payload, dict):
        return None
    sanitized = sanitize_tree(payload)
    if isinstance(sanitized, dict) and key in sanitized:
        return sanitized[key]
    return sanitized


def _first_present(payload: dict[str, Any], *keys: str) -> Any:
    if not isinstance(payload, dict):
        return None
    for key in keys:
        if key in payload and payload[key] not in (None, "", [], {}):
            return payload[key]
    return None


def _safe_text(value: Any) -> str:
    if value in (None, "", [], {}):
        return "UNAVAILABLE"
    sanitized = sanitize_tree(value)
    return str(sanitized)


def _int_or_none(value: Any) -> int | None:
    try:
        if value in (None, ""):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _price_from_bucket(price: dict[str, Any] | None, key: str) -> str:
    if not isinstance(price, dict):
        return "UNAVAILABLE"
    bucket = price.get(key)
    if not isinstance(bucket, list) or not bucket:
        return "UNAVAILABLE"
    first = bucket[0]
    if not isinstance(first, dict):
        return "UNAVAILABLE"
    return _safe_text(first.get("price"))


def _mid_price(bid: str, ask: str) -> str:
    try:
        return f"{(float(bid) + float(ask)) / 2:.5f}"
    except (TypeError, ValueError):
        return "UNAVAILABLE"


def _side_from_units(value: Any) -> str:
    try:
        units = float(value)
    except (TypeError, ValueError):
        return "NONE"
    if units > 0:
        return "BUY"
    if units < 0:
        return "SELL"
    return "NONE"


def _abs_units(value: Any) -> str:
    try:
        return str(abs(float(value)))
    except (TypeError, ValueError):
        return "UNAVAILABLE"


def _normalize_key(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def _is_secret_key(normalized_key: str) -> bool:
    return any(marker in normalized_key for marker in SECRET_KEY_MARKERS)


def _looks_like_secret(value: str) -> bool:
    lowered = value.strip().lower()
    return any(marker in lowered for marker in SECRET_VALUE_MARKERS)


def _looks_like_account_identifier(value: str) -> bool:
    parts = value.strip().split("-")
    return len(parts) >= 3 and all(part.isdigit() for part in parts[:3])
