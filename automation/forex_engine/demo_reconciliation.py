"""Demo-only reconciliation for sanitized forex snapshots and mapped intents."""

from __future__ import annotations

from typing import Any, Mapping


RECONCILIATION_MODE = "DEMO_RECONCILIATION_ONLY"
DECISION_ALLOWED = "allowed"
DECISION_BLOCKED = "blocked"

REASON_NONE = "none"
REASON_ACCOUNT_ID_PRESENT = "account_id_present"
REASON_CREDENTIALS_LOADED = "credentials_loaded"
REASON_BROKER_WRITE_ENABLED = "broker_write_enabled"
REASON_ORDER_SUBMIT_ENABLED = "order_submit_enabled"
REASON_NETWORK_SUBMIT_ENABLED = "network_submit_enabled"
REASON_LIVE_TRADING_ENABLED = "live_trading_enabled"
REASON_UNSUPPORTED_MODE = "unsupported_mode"
REASON_STALE_DATA = "stale_data"
REASON_INVALID_INTENT = "invalid_intent"
REASON_MISSING_PAIR = "missing_pair"
REASON_MISSING_SIDE = "missing_side"
REASON_MISSING_UNITS = "missing_units"

ALLOWED_SNAPSHOT_MODES = {"DEMO_READONLY", "PAPER_ONLY_COMPATIBLE"}
ALLOWED_INTENT_MODE = "DEMO_MAPPING_ONLY"


def reconcile_demo_snapshot(
    readonly_snapshot: Any,
    demo_order_intent: Any,
    *,
    paper_fill_result: Any = None,
    lifecycle_result: Any = None,
    price_tolerance: float = 0.0005,
    units_tolerance: float = 0.000001,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compare sanitized readonly state with a demo order intent without mutating anything."""

    snapshot = dict(readonly_snapshot) if isinstance(readonly_snapshot, Mapping) else {}
    intent = dict(demo_order_intent) if isinstance(demo_order_intent, Mapping) else {}
    fill = dict(paper_fill_result) if isinstance(paper_fill_result, Mapping) else {}
    lifecycle = dict(lifecycle_result) if isinstance(lifecycle_result, Mapping) else {}

    blocked_reasons: list[str] = []
    warnings: list[str] = []
    blocked_reasons.extend(_runtime_blockers(snapshot))
    blocked_reasons.extend(_runtime_blockers(intent))
    blocked_reasons.extend(_runtime_blockers(fill))
    blocked_reasons.extend(_runtime_blockers(lifecycle))

    snapshot_mode = _upper(snapshot.get("mode"))
    if snapshot_mode and snapshot_mode not in ALLOWED_SNAPSHOT_MODES:
        blocked_reasons.append(REASON_UNSUPPORTED_MODE)
    if snapshot.get("allowed") is not True:
        blocked_reasons.append(REASON_UNSUPPORTED_MODE)
    stale_data = snapshot.get("fresh") is False or snapshot.get("stale") is True or _contains_reason(snapshot, "stale")
    if stale_data:
        blocked_reasons.append(REASON_STALE_DATA)

    if not intent or _upper(intent.get("mode")) != ALLOWED_INTENT_MODE:
        blocked_reasons.append(REASON_INVALID_INTENT)

    pair = _normalize_pair(intent.get("pair"))
    side = _normalize_side(intent.get("side"))
    units = _positive_float(intent.get("units"))
    entry_price = _positive_float(intent.get("entry_price"))
    stop_loss = _positive_float(intent.get("stop_loss"))
    take_profit = _positive_float(intent.get("take_profit"))

    if not pair:
        blocked_reasons.append(REASON_MISSING_PAIR)
    if side not in {"BUY", "SELL"}:
        blocked_reasons.append(REASON_MISSING_SIDE)
    if units is None:
        blocked_reasons.append(REASON_MISSING_UNITS)

    position_record = _find_position(snapshot, pair)
    order_record = _find_order(snapshot, pair)
    observed_price = _observed_price(snapshot, position_record, order_record, fill)
    observed_units = _observed_units(position_record, order_record, fill)
    observed_side = _observed_side(position_record, order_record, fill)
    observed_stop_loss = _first_positive(position_record, order_record, fill, "stop_loss")
    observed_take_profit = _first_positive(position_record, order_record, fill, "take_profit")

    position_seen = bool(position_record)
    order_seen = bool(order_record)
    pair_match = bool(pair and (position_seen or order_seen or _price_seen(snapshot, pair)))
    side_match = bool(side and observed_side == side)
    units_match = _within_tolerance(units, observed_units, units_tolerance)
    price_within_tolerance = _within_tolerance(entry_price, observed_price, price_tolerance)
    stop_loss_match = _within_tolerance(stop_loss, observed_stop_loss, price_tolerance)
    take_profit_match = _within_tolerance(take_profit, observed_take_profit, price_tolerance)

    mismatches = _mismatches(
        pair_match=pair_match,
        side_match=side_match,
        units_match=units_match,
        price_within_tolerance=price_within_tolerance,
        stop_loss_match=stop_loss_match,
        take_profit_match=take_profit_match,
        position_seen=position_seen,
        order_seen=order_seen,
    )
    match_score = _match_score(
        pair_match,
        side_match,
        units_match,
        price_within_tolerance,
        stop_loss_match,
        take_profit_match,
        position_seen or order_seen,
    )

    blocked_reasons = _dedupe(blocked_reasons)
    allowed = not blocked_reasons
    matched = allowed and not mismatches and match_score == 1.0

    return {
        "allowed": allowed,
        "decision": DECISION_ALLOWED if allowed else DECISION_BLOCKED,
        "blocked_reason": REASON_NONE if allowed else blocked_reasons[0],
        "blocked_reasons": [] if allowed else blocked_reasons,
        "warnings": warnings,
        "mode": RECONCILIATION_MODE,
        "paper_only": True,
        "demo_readonly": True,
        "matched": matched,
        "match_score": match_score,
        "pair_match": pair_match,
        "side_match": side_match,
        "units_match": units_match,
        "price_within_tolerance": price_within_tolerance,
        "stop_loss_match": stop_loss_match,
        "take_profit_match": take_profit_match,
        "position_seen": position_seen,
        "order_seen": order_seen,
        "stale_data": stale_data,
        "mismatches": mismatches,
        "evidence": {
            "intent_pair": pair,
            "intent_side": side,
            "intent_units": units,
            "intent_entry_price": entry_price,
            "observed_price": observed_price,
            "observed_units": observed_units,
            "observed_side": observed_side,
            "observed_stop_loss": observed_stop_loss,
            "observed_take_profit": observed_take_profit,
            "snapshot_mode": snapshot_mode,
            "paper_fill_present": bool(fill),
            "lifecycle_present": bool(lifecycle),
        },
        "safety": _safety_dict(),
        "next_safe_action": "record_reconciliation_evidence" if allowed else "fix_demo_reconciliation_inputs",
        "metadata": dict(metadata or {}),
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


def _find_position(snapshot: Mapping[str, Any], pair: str) -> dict[str, Any]:
    positions = snapshot.get("positions_summary", snapshot.get("positions", []))
    if isinstance(positions, Mapping):
        positions = positions.get("positions", [])
    if not isinstance(positions, list):
        return {}
    for item in positions:
        if isinstance(item, Mapping) and _normalize_pair(item.get("pair", item.get("instrument"))) == pair:
            return dict(item)
    return {}


def _find_order(snapshot: Mapping[str, Any], pair: str) -> dict[str, Any]:
    orders = snapshot.get("orders", snapshot.get("order_summary", []))
    if isinstance(orders, Mapping):
        orders = orders.get("orders", [])
    if not isinstance(orders, list):
        return {}
    for item in orders:
        if isinstance(item, Mapping) and _normalize_pair(item.get("pair", item.get("instrument"))) == pair:
            return dict(item)
    return {}


def _observed_price(
    snapshot: Mapping[str, Any],
    position: Mapping[str, Any],
    order: Mapping[str, Any],
    fill: Mapping[str, Any],
) -> float | None:
    for payload in (position, order, fill):
        value = _positive_float(payload.get("entry_price", payload.get("fill_price", payload.get("requested_price"))))
        if value is not None:
            return value
    for price in _price_rows(snapshot):
        bid = _positive_float(price.get("bid"))
        ask = _positive_float(price.get("ask"))
        mid = _positive_float(price.get("mid"))
        if mid is not None:
            return mid
        if bid is not None and ask is not None:
            return (bid + ask) / 2
    return None


def _observed_units(
    position: Mapping[str, Any],
    order: Mapping[str, Any],
    fill: Mapping[str, Any],
) -> float | None:
    for payload in (position, order, fill):
        value = _positive_float(payload.get("units", payload.get("filled_units", payload.get("requested_units"))))
        if value is not None:
            return value
    return None


def _observed_side(
    position: Mapping[str, Any],
    order: Mapping[str, Any],
    fill: Mapping[str, Any],
) -> str:
    for payload in (position, order, fill):
        side = _normalize_side(payload.get("side", payload.get("direction")))
        if side in {"BUY", "SELL"}:
            return side
    for payload in (position, order, fill):
        raw_units = _number(payload.get("units", payload.get("filled_units", payload.get("requested_units"))))
        if raw_units is not None:
            if raw_units > 0:
                return "BUY"
            if raw_units < 0:
                return "SELL"
    return ""


def _first_positive(*payloads_and_key: Any) -> float | None:
    key = payloads_and_key[-1]
    for payload in payloads_and_key[:-1]:
        if isinstance(payload, Mapping):
            value = _positive_float(payload.get(key))
            if value is not None:
                return value
    return None


def _price_seen(snapshot: Mapping[str, Any], pair: str) -> bool:
    for price in _price_rows(snapshot):
        if _normalize_pair(price.get("pair", price.get("instrument", price.get("symbol")))) == pair:
            return True
    return False


def _price_rows(snapshot: Mapping[str, Any]) -> list[dict[str, Any]]:
    prices = snapshot.get("prices", [])
    if isinstance(prices, Mapping):
        prices = prices.get("instruments", prices.get("prices", []))
    if not isinstance(prices, list):
        return []
    return [dict(item) for item in prices if isinstance(item, Mapping)]


def _mismatches(**checks: bool) -> list[str]:
    return [name for name, passed in checks.items() if not passed]


def _match_score(*checks: bool) -> float:
    if not checks:
        return 0.0
    return round(sum(1 for check in checks if check) / len(checks), 6)


def _within_tolerance(expected: float | None, observed: float | None, tolerance: float) -> bool:
    if expected is None or observed is None:
        return False
    return abs(float(expected) - float(observed)) <= float(tolerance)


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


def _positive_float(value: Any) -> float | None:
    number = _number(value)
    if number is None or number <= 0:
        return None
    return number


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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


def _upper(value: Any) -> str:
    return str(value or "").strip().upper()


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _dedupe(items: list[str]) -> list[str]:
    ordered: list[str] = []
    for item in items:
        if item and item not in ordered:
            ordered.append(item)
    return ordered


def _safety_dict() -> dict[str, bool]:
    return {
        "paper_only": True,
        "demo_readonly": True,
        "broker_write": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_submit": False,
    }
