"""22H/6D supervised observation evidence adapter for AIOS Forex."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


SUPERVISED_OBSERVATION_22H6D_EVIDENCE_VERSION = "supervised_observation_22h6d_evidence_v1"

SUPERVISED_OBSERVATION_READY = "SUPERVISED_OBSERVATION_READY"
SUPERVISED_OBSERVATION_BLOCKED = "SUPERVISED_OBSERVATION_BLOCKED"
SUPERVISED_OBSERVATION_INCOMPLETE = "SUPERVISED_OBSERVATION_INCOMPLETE"

PROTECTED_PERMISSION_FLAGS = {
    "broker_execution_allowed": False,
    "live_trading_allowed": False,
    "order_submission_allowed": False,
    "credential_access_allowed": False,
    "account_access_allowed": False,
    "dashboard_execution_authority": False,
    "owner_approval_created": False,
}

REQUIRED_OBSERVATION_FIELDS = (
    "observed_hours",
    "required_hours",
    "observed_sessions",
    "required_sessions",
    "observed_days",
    "required_days",
    "interruption_count",
    "max_interruption_count",
    "manual_override_count",
    "max_manual_override_count",
    "sanitized",
    "evidence_age_days",
    "max_evidence_age_days",
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
    "money_movement_allowed",
    "vacation_mode_execution_allowed",
)


def build_sample_observation_summary() -> dict[str, Any]:
    return {
        "observed_hours": 22,
        "required_hours": 22,
        "observed_sessions": 6,
        "required_sessions": 6,
        "observed_days": 6,
        "required_days": 6,
        "interruption_count": 1,
        "max_interruption_count": 2,
        "manual_override_count": 0,
        "max_manual_override_count": 1,
        "sanitized": True,
        "evidence_age_days": 1,
        "max_evidence_age_days": 7,
    }


def evaluate_supervised_observation_22h6d_evidence(
    observation_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate caller-provided supervised observation evidence."""

    if observation_summary is None:
        return _result(
            status=SUPERVISED_OBSERVATION_INCOMPLETE,
            blockers=["22H/6D observation summary is required"],
            missing_fields=list(REQUIRED_OBSERVATION_FIELDS),
            metrics={},
            next_safe_action="Provide sanitized 22H/6D supervised observation evidence.",
        )
    if not isinstance(observation_summary, Mapping):
        return _result(
            status=SUPERVISED_OBSERVATION_INCOMPLETE,
            blockers=["22H/6D observation summary must be a dictionary"],
            missing_fields=list(REQUIRED_OBSERVATION_FIELDS),
            metrics={},
            next_safe_action="Provide observation evidence as a dictionary.",
        )

    summary = dict(observation_summary)
    safety_blockers = _unsafe_fragments(summary, "observation_summary")
    missing_fields = _missing_fields(summary, REQUIRED_OBSERVATION_FIELDS)
    if missing_fields:
        return _result(
            status=SUPERVISED_OBSERVATION_INCOMPLETE,
            blockers=safety_blockers + [f"missing field: {name}" for name in missing_fields],
            missing_fields=missing_fields,
            metrics={},
            next_safe_action="Provide all required 22H/6D fields and rerun locally.",
        )

    numeric_names = (
        "observed_hours",
        "required_hours",
        "observed_sessions",
        "required_sessions",
        "observed_days",
        "required_days",
        "interruption_count",
        "max_interruption_count",
        "manual_override_count",
        "max_manual_override_count",
        "evidence_age_days",
        "max_evidence_age_days",
    )
    numeric = {name: _decimal(summary.get(name)) for name in numeric_names}
    numeric_errors = [name for name, value in numeric.items() if value is None]
    if numeric_errors:
        return _result(
            status=SUPERVISED_OBSERVATION_INCOMPLETE,
            blockers=safety_blockers + [f"field must be numeric: {name}" for name in numeric_errors],
            missing_fields=[],
            metrics={},
            next_safe_action="Repair numeric 22H/6D observation fields and rerun locally.",
        )

    observed_hours = numeric["observed_hours"] or Decimal("0")
    required_hours = numeric["required_hours"] or Decimal("0")
    observed_sessions = numeric["observed_sessions"] or Decimal("0")
    required_sessions = numeric["required_sessions"] or Decimal("0")
    observed_days = numeric["observed_days"] or Decimal("0")
    required_days = numeric["required_days"] or Decimal("0")
    interruptions = numeric["interruption_count"] or Decimal("0")
    max_interruptions = numeric["max_interruption_count"] or Decimal("0")
    overrides = numeric["manual_override_count"] or Decimal("0")
    max_overrides = numeric["max_manual_override_count"] or Decimal("0")
    evidence_age = numeric["evidence_age_days"] or Decimal("0")
    max_age = numeric["max_evidence_age_days"] or Decimal("0")

    blockers = list(safety_blockers)
    if required_hours < 22:
        blockers.append("required_hours must be at least 22")
    if required_sessions < 6:
        blockers.append("required_sessions must be at least 6")
    if required_days < 6:
        blockers.append("required_days must be at least 6")
    if observed_hours < required_hours:
        blockers.append("observed_hours are below required_hours")
    if observed_sessions < required_sessions:
        blockers.append("observed_sessions are below required_sessions")
    if observed_days < required_days:
        blockers.append("observed_days are below required_days")
    if interruptions < 0 or max_interruptions < 0:
        blockers.append("interruption counts cannot be negative")
    if interruptions > max_interruptions:
        blockers.append("too many interruptions for supervised observation")
    if overrides < 0 or max_overrides < 0:
        blockers.append("manual override counts cannot be negative")
    if overrides > max_overrides:
        blockers.append("too many manual overrides for supervised observation")
    if summary.get("sanitized") is not True:
        blockers.append("22H/6D observation summary is not marked sanitized")
    if evidence_age < 0 or max_age < 0:
        blockers.append("evidence age fields cannot be negative")
    if max_age >= 0 and evidence_age > max_age:
        blockers.append("22H/6D observation evidence is stale")

    metrics = {
        "observed_hours": _float(observed_hours),
        "required_hours": _float(required_hours),
        "observed_sessions": int(observed_sessions),
        "required_sessions": int(required_sessions),
        "observed_days": int(observed_days),
        "required_days": int(required_days),
        "interruption_count": int(interruptions),
        "max_interruption_count": int(max_interruptions),
        "manual_override_count": int(overrides),
        "max_manual_override_count": int(max_overrides),
        "freshness": {
            "evidence_age_days": _float(evidence_age),
            "max_evidence_age_days": _float(max_age),
            "fresh": max_age >= 0 and evidence_age <= max_age,
        },
    }
    status = SUPERVISED_OBSERVATION_BLOCKED if blockers else SUPERVISED_OBSERVATION_READY
    next_safe_action = (
        "Continue to final closure evidence; observation evidence creates no trading approval."
        if status == SUPERVISED_OBSERVATION_READY
        else "Repair 22H/6D observation blockers before relying on this evidence."
    )
    return _result(
        status=status,
        blockers=_dedupe(blockers),
        missing_fields=[],
        metrics=metrics,
        next_safe_action=next_safe_action,
    )


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return dict(result)


def result_to_operator_text(result: Mapping[str, Any]) -> str:
    status = str(result.get("observation_status", result.get("status", SUPERVISED_OBSERVATION_INCOMPLETE)))
    if status == SUPERVISED_OBSERVATION_READY:
        metrics = result.get("metrics") or {}
        return (
            "22H/6D supervised observation evidence is ready for review only. "
            f"Observed {metrics.get('observed_hours')} hours over {metrics.get('observed_days')} days. "
            "No trading approval was created."
        )
    blockers = result.get("blockers") or ["22H/6D observation evidence incomplete"]
    return "22H/6D observation evidence blocked: " + "; ".join(str(item) for item in blockers)


def _result(
    *,
    status: str,
    blockers: list[str],
    missing_fields: list[str],
    metrics: Mapping[str, Any],
    next_safe_action: str,
) -> dict[str, Any]:
    return {
        "engine_version": SUPERVISED_OBSERVATION_22H6D_EVIDENCE_VERSION,
        "status": status,
        "observation_status": status,
        "metrics": dict(metrics),
        "blockers": list(blockers),
        "missing_fields": list(missing_fields),
        "next_safe_action": next_safe_action,
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


def _missing_fields(payload: Mapping[str, Any], required: tuple[str, ...]) -> list[str]:
    return [name for name in required if name not in payload]


def _unsafe_fragments(value: Any, prefix: str) -> list[str]:
    fragments: list[str] = []
    _scan_payload(value, prefix, fragments)
    return fragments


def _scan_payload(value: Any, path: str, fragments: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            lowered = key_text.lower()
            if lowered in UNSAFE_TRUE_FIELDS:
                if _truthy(item):
                    fragments.append(f"{path}.{key_text} is unsafe true")
                continue
            if any(fragment in lowered for fragment in SECRET_OR_ACCOUNT_FIELD_FRAGMENTS):
                fragments.append(f"{path}.{key_text} contains secret-like or account-like data")
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


def _float(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.000001")))


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


__all__ = [
    "SUPERVISED_OBSERVATION_BLOCKED",
    "SUPERVISED_OBSERVATION_22H6D_EVIDENCE_VERSION",
    "SUPERVISED_OBSERVATION_INCOMPLETE",
    "SUPERVISED_OBSERVATION_READY",
    "build_sample_observation_summary",
    "evaluate_supervised_observation_22h6d_evidence",
    "result_to_jsonable_dict",
    "result_to_operator_text",
]
