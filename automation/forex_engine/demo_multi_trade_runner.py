"""Plan-only demo multi-trade runner for AIOS Forex."""

from __future__ import annotations

import hashlib
from typing import Any, Mapping


RUNNER_MODE = "DEMO_RUN_PLAN_ONLY"
DECISION_ALLOWED = "allowed"
DECISION_BLOCKED = "blocked"

REASON_NONE = "none"
REASON_PROMOTION_NOT_ALLOWED = "promotion_not_allowed"
REASON_READONLY_NOT_ALLOWED = "readonly_not_allowed"
REASON_RECONCILIATION_NOT_READY = "reconciliation_not_ready"
REASON_SUBMIT_ENABLED = "submit_enabled"
REASON_BROKER_WRITE_ENABLED = "broker_write_enabled"
REASON_LIVE_TRADING_ENABLED = "live_trading_enabled"
REASON_CREDENTIALS_PRESENT = "credentials_present"
REASON_ACCOUNT_ID_PRESENT = "account_id_present"
REASON_DUPLICATE_IDEMPOTENCY_KEY = "duplicate_idempotency_key"
REASON_INVALID_UNITS = "invalid_units"
REASON_UNSUPPORTED_PAIR = "unsupported_pair"
REASON_UNSUPPORTED_SIDE = "unsupported_side"
REASON_UNSUPPORTED_ORDER_TYPE = "unsupported_order_type"
REASON_DEMO_ORDER_CAP_EXCEEDED = "max_demo_order_cap_exceeded"
REASON_INVALID_INTENT = "invalid_intent"

SUPPORTED_PAIRS = {"EUR_USD", "GBP_USD", "USD_JPY"}
SUPPORTED_SIDES = {"BUY", "SELL"}
SUPPORTED_ORDER_TYPES = {"MARKET"}


def build_demo_run_plan(
    promotion_decision: Any,
    mapped_demo_order_intents: Any,
    readonly_snapshot: Any,
    reconciliation_result: Any,
    limits: Any = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a non-submitting demo run plan from approved demo workflow outputs."""

    promotion = _as_mapping(promotion_decision)
    readonly = _as_mapping(readonly_snapshot)
    reconciliation = _as_mapping(reconciliation_result)
    limit_cfg = _limits(limits)
    raw_intents = _intent_list(mapped_demo_order_intents)

    blocked_reasons: list[str] = []
    warnings: list[str] = []
    rejected_intents: list[dict[str, Any]] = []
    selected_intents: list[dict[str, Any]] = []

    if promotion.get("allowed") is not True:
        blocked_reasons.append(REASON_PROMOTION_NOT_ALLOWED)
    if readonly.get("allowed") is not True:
        blocked_reasons.append(REASON_READONLY_NOT_ALLOWED)
    if reconciliation.get("allowed") is not True or (
        reconciliation.get("matched") is not True and reconciliation.get("match_score") != 1.0
    ):
        blocked_reasons.append(REASON_RECONCILIATION_NOT_READY)

    blocked_reasons.extend(_runtime_blockers(promotion))
    blocked_reasons.extend(_runtime_blockers(readonly))
    blocked_reasons.extend(_runtime_blockers(reconciliation))

    seen_keys: set[str] = set()
    duplicate_seen = False
    for index, raw in enumerate(raw_intents):
        intent = _unwrap_intent(raw)
        intent_blockers = _intent_blockers(intent)
        key = str(intent.get("idempotency_key") or "")
        if not key:
            intent_blockers.append(REASON_INVALID_INTENT)
        elif key in seen_keys:
            intent_blockers.append(REASON_DUPLICATE_IDEMPOTENCY_KEY)
            duplicate_seen = True
        else:
            seen_keys.add(key)

        record = {
            "index": index,
            "idempotency_key": key,
            "pair": _normalize_pair(intent.get("pair")),
            "side": _normalize_side(intent.get("side")),
            "units": _positive_float(intent.get("units")),
            "order_type": _normalize_order_type(intent.get("order_type")),
        }
        if intent_blockers:
            rejected_intents.append({**record, "blocked_reasons": _dedupe(intent_blockers)})
            blocked_reasons.extend(intent_blockers)
        else:
            selected_intents.append(_safe_intent_record(intent))

    if duplicate_seen:
        blocked_reasons.append(REASON_DUPLICATE_IDEMPOTENCY_KEY)
    if len(raw_intents) > limit_cfg["max_demo_orders"]:
        blocked_reasons.append(REASON_DEMO_ORDER_CAP_EXCEEDED)
    if not raw_intents:
        blocked_reasons.append(REASON_INVALID_INTENT)

    blocked_reasons = _dedupe(blocked_reasons)
    allowed = not blocked_reasons
    if not allowed:
        selected_intents = []

    idempotency_keys = [intent["idempotency_key"] for intent in selected_intents]
    run_id = _run_id(idempotency_keys, limit_cfg["max_demo_orders"])

    return {
        "allowed": allowed,
        "decision": DECISION_ALLOWED if allowed else DECISION_BLOCKED,
        "blocked_reason": REASON_NONE if allowed else blocked_reasons[0],
        "blocked_reasons": [] if allowed else blocked_reasons,
        "warnings": warnings,
        "mode": RUNNER_MODE,
        "paper_only": True,
        "demo_readonly": True,
        "submit_enabled": False,
        "broker_write_enabled": False,
        "live_trading": False,
        "demo_run_plan": {
            "mode": RUNNER_MODE,
            "run_id": run_id,
            "selected_intents": selected_intents,
            "rejected_intents": rejected_intents,
            "idempotency_keys": idempotency_keys,
            "max_demo_orders": limit_cfg["max_demo_orders"],
            "submit_enabled": False,
            "broker_write_enabled": False,
            "live_trading": False,
            "safety": _safety_dict(),
        },
        "selected_intents": selected_intents,
        "rejected_intents": rejected_intents,
        "run_id": run_id,
        "idempotency_keys": idempotency_keys,
        "max_demo_orders": limit_cfg["max_demo_orders"],
        "safety": _safety_dict(),
        "next_safe_action": "review_demo_run_plan" if allowed else "fix_demo_run_plan_inputs",
        "metadata": {
            "requested_intent_count": len(raw_intents),
            "selected_intent_count": len(selected_intents),
            "rejected_intent_count": len(rejected_intents),
            "limits": dict(limit_cfg),
            **dict(metadata or {}),
        },
    }


def _intent_blockers(intent: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not intent:
        return [REASON_INVALID_INTENT]
    blockers.extend(_runtime_blockers(intent))
    pair = _normalize_pair(intent.get("pair"))
    side = _normalize_side(intent.get("side"))
    order_type = _normalize_order_type(intent.get("order_type"))
    units = _positive_float(intent.get("units"))
    if pair not in SUPPORTED_PAIRS:
        blockers.append(REASON_UNSUPPORTED_PAIR)
    if side not in SUPPORTED_SIDES:
        blockers.append(REASON_UNSUPPORTED_SIDE)
    if order_type not in SUPPORTED_ORDER_TYPES:
        blockers.append(REASON_UNSUPPORTED_ORDER_TYPE)
    if units is None:
        blockers.append(REASON_INVALID_UNITS)
    return blockers


def _runtime_blockers(value: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for key, nested in _walk(value):
        normalized = _normalize_key(key)
        if normalized == "submit_enabled" and _truthy(nested):
            blockers.append(REASON_SUBMIT_ENABLED)
        if "broker" in normalized and "write" in normalized and _truthy(nested):
            blockers.append(REASON_BROKER_WRITE_ENABLED)
        if "live" in normalized and "trading" in normalized and _truthy(nested):
            blockers.append(REASON_LIVE_TRADING_ENABLED)
        if "credential" in normalized and _present(nested):
            blockers.append(REASON_CREDENTIALS_PRESENT)
        if "account" in normalized and "id" in normalized and _present(nested):
            blockers.append(REASON_ACCOUNT_ID_PRESENT)
        if isinstance(nested, str) and _looks_like_account_identifier(nested):
            blockers.append(REASON_ACCOUNT_ID_PRESENT)
    return blockers


def _intent_list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, Mapping):
        if isinstance(value.get("demo_order_intent"), Mapping):
            return [dict(value)]
        if isinstance(value.get("intents"), list):
            return [dict(item) for item in value["intents"] if isinstance(item, Mapping)]
        if isinstance(value.get("demo_order_intents"), list):
            return [dict(item) for item in value["demo_order_intents"] if isinstance(item, Mapping)]
        return [dict(value)]
    if isinstance(value, list):
        return [dict(item) for item in value if isinstance(item, Mapping)]
    return []


def _unwrap_intent(value: Mapping[str, Any]) -> dict[str, Any]:
    nested = value.get("demo_order_intent")
    if isinstance(nested, Mapping):
        return dict(nested)
    return dict(value)


def _safe_intent_record(intent: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "pair": _normalize_pair(intent.get("pair")),
        "side": _normalize_side(intent.get("side")),
        "units": _positive_float(intent.get("units")),
        "order_type": _normalize_order_type(intent.get("order_type")),
        "entry_price": _positive_float(intent.get("entry_price")),
        "stop_loss": _positive_float(intent.get("stop_loss")),
        "take_profit": _positive_float(intent.get("take_profit")),
        "client_order_id": str(intent.get("client_order_id") or ""),
        "idempotency_key": str(intent.get("idempotency_key") or ""),
        "mode": RUNNER_MODE,
        "submit_enabled": False,
        "broker_write_enabled": False,
        "live_trading": False,
    }


def _limits(value: Any) -> dict[str, int]:
    raw = _as_mapping(value)
    max_orders = _positive_int(raw.get("max_demo_orders"), 3)
    return {"max_demo_orders": max_orders}


def _run_id(keys: list[str], cap: int) -> str:
    raw = "|".join(sorted(keys) + [str(cap)])
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"demo-run-{digest[:20]}"


def _as_mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


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


def _positive_int(value: Any, default: int) -> int:
    if isinstance(value, bool):
        return default
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return number if number > 0 else default


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
        "submit_enabled": False,
        "broker_write_enabled": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_submit": False,
    }
