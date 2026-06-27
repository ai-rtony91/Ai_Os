"""Walk-forward and out-of-sample evidence adapter for AIOS Forex."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


WALK_FORWARD_OOS_EVIDENCE_VERSION = "walk_forward_oos_evidence_v1"

WALK_FORWARD_OOS_READY = "WALK_FORWARD_OOS_READY"
WALK_FORWARD_OOS_BLOCKED = "WALK_FORWARD_OOS_BLOCKED"
WALK_FORWARD_OOS_INCOMPLETE = "WALK_FORWARD_OOS_INCOMPLETE"

PROTECTED_PERMISSION_FLAGS = {
    "broker_execution_allowed": False,
    "live_trading_allowed": False,
    "order_submission_allowed": False,
    "credential_access_allowed": False,
    "account_access_allowed": False,
    "dashboard_execution_authority": False,
    "owner_approval_created": False,
}

REQUIRED_WALK_FORWARD_FIELDS = (
    "windows_total",
    "windows_passed",
    "oos_segments_total",
    "oos_segments_passed",
    "min_pass_rate",
    "max_drawdown",
    "max_allowed_drawdown",
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


def build_sample_walk_forward_oos_summary() -> dict[str, Any]:
    return {
        "windows_total": 6,
        "windows_passed": 6,
        "oos_segments_total": 4,
        "oos_segments_passed": 4,
        "min_pass_rate": 0.75,
        "max_drawdown": 2.5,
        "max_allowed_drawdown": 8.0,
        "sanitized": True,
        "evidence_age_days": 1,
        "max_evidence_age_days": 7,
    }


def evaluate_walk_forward_oos_evidence(
    walk_forward_oos_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate caller-provided walk-forward/OOS evidence for review only."""

    if walk_forward_oos_summary is None:
        return _result(
            status=WALK_FORWARD_OOS_INCOMPLETE,
            blockers=["walk-forward/OOS summary is required"],
            missing_fields=list(REQUIRED_WALK_FORWARD_FIELDS),
            metrics={},
            next_safe_action="Provide sanitized walk-forward/OOS summary evidence.",
        )
    if not isinstance(walk_forward_oos_summary, Mapping):
        return _result(
            status=WALK_FORWARD_OOS_INCOMPLETE,
            blockers=["walk-forward/OOS summary must be a dictionary"],
            missing_fields=list(REQUIRED_WALK_FORWARD_FIELDS),
            metrics={},
            next_safe_action="Provide walk-forward/OOS evidence as a dictionary.",
        )

    summary = dict(walk_forward_oos_summary)
    safety_blockers = _unsafe_fragments(summary, "walk_forward_oos_summary")
    missing_fields = _missing_fields(summary, REQUIRED_WALK_FORWARD_FIELDS)
    if missing_fields:
        return _result(
            status=WALK_FORWARD_OOS_INCOMPLETE,
            blockers=safety_blockers + [f"missing field: {name}" for name in missing_fields],
            missing_fields=missing_fields,
            metrics={},
            next_safe_action="Provide all required walk-forward/OOS fields and rerun locally.",
        )

    numeric = {
        name: _decimal(summary.get(name))
        for name in (
            "windows_total",
            "windows_passed",
            "oos_segments_total",
            "oos_segments_passed",
            "min_pass_rate",
            "max_drawdown",
            "max_allowed_drawdown",
            "evidence_age_days",
            "max_evidence_age_days",
        )
    }
    numeric_errors = [name for name, value in numeric.items() if value is None]
    if numeric_errors:
        return _result(
            status=WALK_FORWARD_OOS_INCOMPLETE,
            blockers=safety_blockers + [f"field must be numeric: {name}" for name in numeric_errors],
            missing_fields=[],
            metrics={},
            next_safe_action="Repair numeric walk-forward/OOS fields and rerun locally.",
        )

    windows_total = numeric["windows_total"] or Decimal("0")
    windows_passed = numeric["windows_passed"] or Decimal("0")
    oos_total = numeric["oos_segments_total"] or Decimal("0")
    oos_passed = numeric["oos_segments_passed"] or Decimal("0")
    min_pass_rate = numeric["min_pass_rate"] or Decimal("0")
    max_drawdown = numeric["max_drawdown"] or Decimal("0")
    max_allowed_drawdown = numeric["max_allowed_drawdown"] or Decimal("0")
    evidence_age = numeric["evidence_age_days"] or Decimal("0")
    max_age = numeric["max_evidence_age_days"] or Decimal("0")

    blockers = list(safety_blockers)
    if windows_total <= 0:
        blockers.append("windows_total must be positive")
    if oos_total <= 0:
        blockers.append("oos_segments_total must be positive")
    if windows_passed < 0 or oos_passed < 0:
        blockers.append("passed counts cannot be negative")
    if windows_passed > windows_total:
        blockers.append("windows_passed cannot exceed windows_total")
    if oos_passed > oos_total:
        blockers.append("oos_segments_passed cannot exceed oos_segments_total")
    if min_pass_rate <= 0 or min_pass_rate > 1:
        blockers.append("min_pass_rate must be greater than 0 and no more than 1")
    if max_drawdown < 0:
        blockers.append("max_drawdown cannot be negative")
    if max_allowed_drawdown <= 0:
        blockers.append("max_allowed_drawdown must be positive")
    if summary.get("sanitized") is not True:
        blockers.append("walk-forward/OOS summary is not marked sanitized")
    if max_drawdown > max_allowed_drawdown:
        blockers.append("drawdown exceeds allowed threshold")
    if evidence_age < 0 or max_age < 0:
        blockers.append("evidence age fields cannot be negative")
    if max_age >= 0 and evidence_age > max_age:
        blockers.append("walk-forward/OOS evidence is stale")

    window_pass_rate = windows_passed / windows_total if windows_total > 0 else Decimal("0")
    oos_pass_rate = oos_passed / oos_total if oos_total > 0 else Decimal("0")
    if windows_total > 0 and window_pass_rate < min_pass_rate:
        blockers.append("walk-forward pass rate is below threshold")
    if oos_total > 0 and oos_pass_rate < min_pass_rate:
        blockers.append("OOS pass rate is below threshold")

    metrics = {
        "windows_total": int(windows_total),
        "windows_passed": int(windows_passed),
        "oos_segments_total": int(oos_total),
        "oos_segments_passed": int(oos_passed),
        "walk_forward_pass_rate": _float(window_pass_rate),
        "oos_pass_rate": _float(oos_pass_rate),
        "min_pass_rate": _float(min_pass_rate),
        "max_drawdown": _float(max_drawdown),
        "max_allowed_drawdown": _float(max_allowed_drawdown),
        "freshness": {
            "evidence_age_days": _float(evidence_age),
            "max_evidence_age_days": _float(max_age),
            "fresh": max_age >= 0 and evidence_age <= max_age,
        },
    }
    status = WALK_FORWARD_OOS_BLOCKED if blockers else WALK_FORWARD_OOS_READY
    next_safe_action = (
        "Continue to persistent profitability evidence; OOS evidence creates no trading approval."
        if status == WALK_FORWARD_OOS_READY
        else "Repair walk-forward/OOS blockers before relying on this evidence."
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
    status = str(result.get("walk_forward_oos_status", result.get("status", WALK_FORWARD_OOS_INCOMPLETE)))
    if status == WALK_FORWARD_OOS_READY:
        metrics = result.get("metrics") or {}
        return (
            "Walk-forward/OOS evidence is ready for review only. "
            f"Pass rates: WF {metrics.get('walk_forward_pass_rate')}, "
            f"OOS {metrics.get('oos_pass_rate')}. No trading approval was created."
        )
    blockers = result.get("blockers") or ["walk-forward/OOS evidence incomplete"]
    return "Walk-forward/OOS evidence blocked: " + "; ".join(str(item) for item in blockers)


def _result(
    *,
    status: str,
    blockers: list[str],
    missing_fields: list[str],
    metrics: Mapping[str, Any],
    next_safe_action: str,
) -> dict[str, Any]:
    return {
        "engine_version": WALK_FORWARD_OOS_EVIDENCE_VERSION,
        "status": status,
        "walk_forward_oos_status": status,
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
    "WALK_FORWARD_OOS_BLOCKED",
    "WALK_FORWARD_OOS_EVIDENCE_VERSION",
    "WALK_FORWARD_OOS_INCOMPLETE",
    "WALK_FORWARD_OOS_READY",
    "build_sample_walk_forward_oos_summary",
    "evaluate_walk_forward_oos_evidence",
    "result_to_jsonable_dict",
    "result_to_operator_text",
]
