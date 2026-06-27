"""Sanitized broker health read-only engine V1 for AIOS Forex.

This module evaluates local sanitized snapshot dictionaries only. It does not
import broker SDKs, call brokers, read credentials, read environment variables,
handle account identifiers, accept raw broker payloads, or authorize orders.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


BROKER_HEALTH_READONLY_VERSION = "broker_health_readonly_v1"

BROKER_HEALTH_REVIEW_READY = "BROKER_HEALTH_REVIEW_READY"
BROKER_HEALTH_BLOCKED = "BROKER_HEALTH_BLOCKED"
BROKER_HEALTH_INCOMPLETE = "BROKER_HEALTH_INCOMPLETE"

PROTECTED_PERMISSION_FLAGS = {
    "broker_execution_allowed": False,
    "live_trading_allowed": False,
    "order_submission_allowed": False,
    "credential_access_allowed": False,
    "account_access_allowed": False,
    "dashboard_execution_authority": False,
    "owner_approval_created": False,
}

REQUIRED_SNAPSHOT_FIELDS = (
    "snapshot_id",
    "sanitized",
    "read_only",
    "snapshot_age_minutes",
    "max_snapshot_age_minutes",
    "market_open",
    "instrument_tradeable",
    "spread_pips",
    "max_spread_pips",
    "exposure_reconciled",
    "positions_flat",
    "recovery_plan_present",
    "recovery_drill_age_days",
    "max_recovery_drill_age_days",
)

SECRET_OR_ACCOUNT_FIELD_FRAGMENTS = (
    "api_key",
    "access_token",
    "refresh_token",
    "authorization",
    "bearer",
    "password",
    "secret",
    "credential",
    "account_id",
    "accountid",
    "account_number",
    "account_reference",
    "broker_account",
    "broker_order_id",
    "raw_order_id",
    "raw_transaction_id",
    "raw_payload",
    "order_payload",
)

UNSAFE_TRUE_FIELDS = (
    "broker_execution_allowed",
    "live_trading_allowed",
    "order_submission_allowed",
    "credential_access_allowed",
    "account_access_allowed",
    "dashboard_execution_authority",
    "owner_approval_created",
    "execution_allowed",
    "trade_allowed",
    "broker_access_allowed",
    "raw_payload_present",
)


def build_sample_snapshot() -> dict[str, Any]:
    return {
        "snapshot_id": "sanitized-broker-health-review-sample",
        "sanitized": True,
        "read_only": True,
        "snapshot_age_minutes": 3,
        "max_snapshot_age_minutes": 15,
        "market_open": True,
        "instrument_tradeable": True,
        "spread_pips": 0.8,
        "max_spread_pips": 1.5,
        "exposure_reconciled": True,
        "positions_flat": True,
        "recovery_plan_present": True,
        "recovery_drill_age_days": 2,
        "max_recovery_drill_age_days": 14,
        "source": "sanitized_manual_read_only_snapshot",
    }


def evaluate_broker_health_readonly(
    snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate sanitized read-only broker health evidence."""

    if snapshot is None:
        return _result(
            status=BROKER_HEALTH_INCOMPLETE,
            snapshot={},
            stale_data_blockers=["snapshot is required"],
            market_blockers=[],
            spread_blockers=[],
            recovery_blockers=[],
            safety_blockers=[],
            next_safe_action="Provide a sanitized read-only snapshot and rerun this local engine.",
        )

    payload = dict(snapshot)
    missing = _missing_fields(payload, REQUIRED_SNAPSHOT_FIELDS)
    if missing:
        return _result(
            status=BROKER_HEALTH_INCOMPLETE,
            snapshot=payload,
            stale_data_blockers=[f"missing required field: {name}" for name in missing],
            market_blockers=[],
            spread_blockers=[],
            recovery_blockers=[],
            safety_blockers=[],
            next_safe_action="Provide missing sanitized broker health fields; do not call a broker.",
        )

    safety_blockers = _unsafe_fragments(payload, "snapshot")
    stale_data_blockers: list[str] = []
    market_blockers: list[str] = []
    spread_blockers: list[str] = []
    recovery_blockers: list[str] = []

    snapshot_age = _decimal(payload["snapshot_age_minutes"])
    max_snapshot_age = _decimal(payload["max_snapshot_age_minutes"])
    spread = _decimal(payload["spread_pips"])
    max_spread = _decimal(payload["max_spread_pips"])
    recovery_age = _decimal(payload["recovery_drill_age_days"])
    max_recovery_age = _decimal(payload["max_recovery_drill_age_days"])

    numeric_errors = [
        name
        for name, value in (
            ("snapshot.snapshot_age_minutes", snapshot_age),
            ("snapshot.max_snapshot_age_minutes", max_snapshot_age),
            ("snapshot.spread_pips", spread),
            ("snapshot.max_spread_pips", max_spread),
            ("snapshot.recovery_drill_age_days", recovery_age),
            ("snapshot.max_recovery_drill_age_days", max_recovery_age),
        )
        if value is None
    ]
    if numeric_errors:
        return _result(
            status=BROKER_HEALTH_INCOMPLETE,
            snapshot=payload,
            stale_data_blockers=[f"field must be numeric: {name}" for name in numeric_errors],
            market_blockers=[],
            spread_blockers=[],
            recovery_blockers=[],
            safety_blockers=safety_blockers,
            next_safe_action="Repair numeric snapshot fields before broker health review.",
        )

    assert snapshot_age is not None
    assert max_snapshot_age is not None
    assert spread is not None
    assert max_spread is not None
    assert recovery_age is not None
    assert max_recovery_age is not None

    if payload.get("sanitized") is not True:
        safety_blockers.append("snapshot is not marked sanitized")
    if payload.get("read_only") is not True:
        safety_blockers.append("snapshot is not marked read-only")
    if snapshot_age > max_snapshot_age:
        stale_data_blockers.append("snapshot evidence is stale")
    if payload.get("exposure_reconciled") is not True:
        stale_data_blockers.append("broker exposure is not reconciled")
    if payload.get("market_open") is not True:
        market_blockers.append("market is closed")
    if payload.get("instrument_tradeable") is not True:
        market_blockers.append("instrument is not tradeable")
    if spread > max_spread:
        spread_blockers.append("spread exceeds review cap")
    if payload.get("positions_flat") is not True:
        market_blockers.append("positions are not flat or cannot be safely reviewed")
    if payload.get("recovery_plan_present") is not True:
        recovery_blockers.append("broker recovery plan is missing")
    if recovery_age > max_recovery_age:
        recovery_blockers.append("broker recovery drill evidence is stale")

    blockers = (
        stale_data_blockers
        + market_blockers
        + spread_blockers
        + recovery_blockers
        + safety_blockers
    )
    status = BROKER_HEALTH_BLOCKED if blockers else BROKER_HEALTH_REVIEW_READY
    next_safe_action = (
        "Continue to profitability evidence review; keep broker execution locked."
        if status == BROKER_HEALTH_REVIEW_READY
        else "Repair broker health blockers with sanitized read-only evidence; do not call a broker."
    )

    return _result(
        status=status,
        snapshot=payload,
        stale_data_blockers=stale_data_blockers,
        market_blockers=market_blockers,
        spread_blockers=spread_blockers,
        recovery_blockers=recovery_blockers,
        safety_blockers=safety_blockers,
        next_safe_action=next_safe_action,
    )


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return _jsonable(dict(result))


def result_to_operator_text(result: Mapping[str, Any]) -> str:
    status = str(result.get("status", BROKER_HEALTH_INCOMPLETE))
    if status == BROKER_HEALTH_REVIEW_READY:
        return (
            "Broker health is review-ready from sanitized read-only evidence. "
            "No broker call, credential access, account access, or order action occurred."
        )
    blockers = result.get("blockers") or ["broker health input incomplete"]
    return "Broker health blocked: " + "; ".join(str(item) for item in blockers)


def _result(
    *,
    status: str,
    snapshot: Mapping[str, Any],
    stale_data_blockers: list[str],
    market_blockers: list[str],
    spread_blockers: list[str],
    recovery_blockers: list[str],
    safety_blockers: list[str],
    next_safe_action: str,
) -> dict[str, Any]:
    blockers = (
        list(stale_data_blockers)
        + list(market_blockers)
        + list(spread_blockers)
        + list(recovery_blockers)
        + list(safety_blockers)
    )
    return {
        "engine_version": BROKER_HEALTH_READONLY_VERSION,
        "status": status,
        "broker_health": "HEALTHY" if status == BROKER_HEALTH_REVIEW_READY else "BLOCKED",
        "snapshot_id": _text(snapshot.get("snapshot_id")),
        "stale_data_blockers": list(stale_data_blockers),
        "market_blockers": list(market_blockers),
        "spread_blockers": list(spread_blockers),
        "recovery_blockers": list(recovery_blockers),
        "safety_blockers": list(safety_blockers),
        "blockers": blockers,
        "freshness": {
            "snapshot_age_minutes": _jsonable(snapshot.get("snapshot_age_minutes")),
            "max_snapshot_age_minutes": _jsonable(snapshot.get("max_snapshot_age_minutes")),
            "recovery_drill_age_days": _jsonable(snapshot.get("recovery_drill_age_days")),
        },
        "next_safe_action": next_safe_action,
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


def _missing_fields(payload: Mapping[str, Any], required: tuple[str, ...]) -> list[str]:
    return [
        name
        for name in required
        if name not in payload or payload[name] in (None, "")
    ]


def _unsafe_fragments(payload: Mapping[str, Any], prefix: str) -> list[str]:
    fragments: list[str] = []
    _scan_payload(payload, prefix, fragments)
    return fragments


def _scan_payload(value: Any, path: str, fragments: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            lowered = key_text.lower()
            if any(fragment in lowered for fragment in SECRET_OR_ACCOUNT_FIELD_FRAGMENTS):
                fragments.append(f"{path}.{key_text} contains secret-like or account-like data")
            if lowered in UNSAFE_TRUE_FIELDS and _truthy(item):
                fragments.append(f"{path}.{key_text} is unsafe true")
            _scan_payload(item, f"{path}.{key_text}", fragments)
    elif isinstance(value, (list, tuple, set)):
        for index, item in enumerate(value):
            _scan_payload(item, f"{path}[{index}]", fragments)
    elif isinstance(value, str):
        lowered = value.lower()
        if any(fragment in lowered for fragment in SECRET_OR_ACCOUNT_FIELD_FRAGMENTS):
            fragments.append(f"{path} contains secret-like or account-like text")


def _decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError):
        return None


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return False


def _text(value: Any) -> str:
    if value is None:
        return ""
    return value.strip() if isinstance(value, str) else str(value).strip()


def _jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value.quantize(Decimal("0.000001")))
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


__all__ = [
    "BROKER_HEALTH_BLOCKED",
    "BROKER_HEALTH_INCOMPLETE",
    "BROKER_HEALTH_READONLY_VERSION",
    "BROKER_HEALTH_REVIEW_READY",
    "build_sample_snapshot",
    "evaluate_broker_health_readonly",
    "result_to_jsonable_dict",
    "result_to_operator_text",
]
