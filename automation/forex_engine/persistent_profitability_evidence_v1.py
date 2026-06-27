"""Persistent profitability evidence adapter for AIOS Forex."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


PERSISTENT_PROFITABILITY_EVIDENCE_VERSION = "persistent_profitability_evidence_v1"

PERSISTENT_PROFITABILITY_READY = "PERSISTENT_PROFITABILITY_READY"
PERSISTENT_PROFITABILITY_BLOCKED = "PERSISTENT_PROFITABILITY_BLOCKED"
PERSISTENT_PROFITABILITY_INCOMPLETE = "PERSISTENT_PROFITABILITY_INCOMPLETE"

PROTECTED_PERMISSION_FLAGS = {
    "broker_execution_allowed": False,
    "live_trading_allowed": False,
    "order_submission_allowed": False,
    "credential_access_allowed": False,
    "account_access_allowed": False,
    "dashboard_execution_authority": False,
    "owner_approval_created": False,
}

REQUIRED_PROFITABILITY_FIELDS = (
    "closed_trade_count",
    "min_closed_trade_count",
    "expectancy",
    "min_expectancy",
    "profit_factor",
    "min_profit_factor",
    "max_drawdown",
    "max_allowed_drawdown",
    "consecutive_profitable_periods",
    "min_profitable_periods",
    "after_costs",
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


def build_sample_persistent_profitability_summary() -> dict[str, Any]:
    return {
        "closed_trade_count": 42,
        "min_closed_trade_count": 30,
        "expectancy": 0.42,
        "min_expectancy": 0.05,
        "profit_factor": 1.82,
        "min_profit_factor": 1.25,
        "max_drawdown": 4.0,
        "max_allowed_drawdown": 10.0,
        "consecutive_profitable_periods": 6,
        "min_profitable_periods": 4,
        "after_costs": True,
        "sanitized": True,
        "evidence_age_days": 1,
        "max_evidence_age_days": 7,
    }


def evaluate_persistent_profitability_evidence(
    profitability_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate persistent profitability summary evidence for review only."""

    if profitability_summary is None:
        return _result(
            status=PERSISTENT_PROFITABILITY_INCOMPLETE,
            blockers=["persistent profitability summary is required"],
            missing_fields=list(REQUIRED_PROFITABILITY_FIELDS),
            metrics={},
            next_safe_action="Provide sanitized persistent profitability evidence.",
        )
    if not isinstance(profitability_summary, Mapping):
        return _result(
            status=PERSISTENT_PROFITABILITY_INCOMPLETE,
            blockers=["persistent profitability summary must be a dictionary"],
            missing_fields=list(REQUIRED_PROFITABILITY_FIELDS),
            metrics={},
            next_safe_action="Provide persistent profitability evidence as a dictionary.",
        )

    summary = dict(profitability_summary)
    safety_blockers = _unsafe_fragments(summary, "profitability_summary")
    missing_fields = _missing_fields(summary, REQUIRED_PROFITABILITY_FIELDS)
    if missing_fields:
        return _result(
            status=PERSISTENT_PROFITABILITY_INCOMPLETE,
            blockers=safety_blockers + [f"missing field: {name}" for name in missing_fields],
            missing_fields=missing_fields,
            metrics={},
            next_safe_action="Provide all required persistent profitability fields and rerun locally.",
        )

    numeric_names = (
        "closed_trade_count",
        "min_closed_trade_count",
        "expectancy",
        "min_expectancy",
        "profit_factor",
        "min_profit_factor",
        "max_drawdown",
        "max_allowed_drawdown",
        "consecutive_profitable_periods",
        "min_profitable_periods",
        "evidence_age_days",
        "max_evidence_age_days",
    )
    numeric = {name: _decimal(summary.get(name)) for name in numeric_names}
    numeric_errors = [name for name, value in numeric.items() if value is None]
    if numeric_errors:
        return _result(
            status=PERSISTENT_PROFITABILITY_INCOMPLETE,
            blockers=safety_blockers + [f"field must be numeric: {name}" for name in numeric_errors],
            missing_fields=[],
            metrics={},
            next_safe_action="Repair numeric persistent profitability fields and rerun locally.",
        )

    closed_trade_count = numeric["closed_trade_count"] or Decimal("0")
    min_closed_trade_count = numeric["min_closed_trade_count"] or Decimal("0")
    expectancy = numeric["expectancy"] or Decimal("0")
    min_expectancy = numeric["min_expectancy"] or Decimal("0")
    profit_factor = numeric["profit_factor"] or Decimal("0")
    min_profit_factor = numeric["min_profit_factor"] or Decimal("0")
    max_drawdown = numeric["max_drawdown"] or Decimal("0")
    max_allowed_drawdown = numeric["max_allowed_drawdown"] or Decimal("0")
    periods = numeric["consecutive_profitable_periods"] or Decimal("0")
    min_periods = numeric["min_profitable_periods"] or Decimal("0")
    evidence_age = numeric["evidence_age_days"] or Decimal("0")
    max_age = numeric["max_evidence_age_days"] or Decimal("0")

    blockers = list(safety_blockers)
    if min_closed_trade_count <= 0:
        blockers.append("min_closed_trade_count must be positive")
    if closed_trade_count < min_closed_trade_count:
        blockers.append("closed trade count is below threshold")
    if min_expectancy < 0:
        blockers.append("min_expectancy cannot be negative")
    if expectancy < min_expectancy:
        blockers.append("expectancy is below threshold")
    if expectancy <= 0:
        blockers.append("expectancy is not positive")
    if min_profit_factor < 1:
        blockers.append("min_profit_factor conflicts with profitability proof")
    if profit_factor < min_profit_factor:
        blockers.append("profit factor is below threshold")
    if max_drawdown < 0:
        blockers.append("max_drawdown cannot be negative")
    if max_allowed_drawdown <= 0:
        blockers.append("max_allowed_drawdown must be positive")
    if max_drawdown > max_allowed_drawdown:
        blockers.append("drawdown exceeds allowed threshold")
    if min_periods <= 0:
        blockers.append("min_profitable_periods must be positive")
    if periods < min_periods:
        blockers.append("profitable periods are below threshold")
    if summary.get("after_costs") is not True:
        blockers.append("after-cost profitability evidence is missing")
    if summary.get("sanitized") is not True:
        blockers.append("profitability summary is not marked sanitized")
    if evidence_age < 0 or max_age < 0:
        blockers.append("evidence age fields cannot be negative")
    if max_age >= 0 and evidence_age > max_age:
        blockers.append("persistent profitability evidence is stale")

    metrics = {
        "closed_trade_count": int(closed_trade_count),
        "min_closed_trade_count": int(min_closed_trade_count),
        "expectancy": _float(expectancy),
        "min_expectancy": _float(min_expectancy),
        "profit_factor": _float(profit_factor),
        "min_profit_factor": _float(min_profit_factor),
        "max_drawdown": _float(max_drawdown),
        "max_allowed_drawdown": _float(max_allowed_drawdown),
        "consecutive_profitable_periods": int(periods),
        "min_profitable_periods": int(min_periods),
        "after_costs": summary.get("after_costs") is True,
        "freshness": {
            "evidence_age_days": _float(evidence_age),
            "max_evidence_age_days": _float(max_age),
            "fresh": max_age >= 0 and evidence_age <= max_age,
        },
    }
    status = PERSISTENT_PROFITABILITY_BLOCKED if blockers else PERSISTENT_PROFITABILITY_READY
    next_safe_action = (
        "Continue to 22H/6D supervised observation evidence; profitability evidence creates no trading approval."
        if status == PERSISTENT_PROFITABILITY_READY
        else "Repair persistent profitability blockers before relying on this evidence."
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
    status = str(result.get("persistent_profitability_status", result.get("status", PERSISTENT_PROFITABILITY_INCOMPLETE)))
    if status == PERSISTENT_PROFITABILITY_READY:
        metrics = result.get("metrics") or {}
        return (
            "Persistent profitability evidence is ready for review only. "
            f"Expectancy {metrics.get('expectancy')}, profit factor {metrics.get('profit_factor')}. "
            "No trading approval was created."
        )
    blockers = result.get("blockers") or ["persistent profitability evidence incomplete"]
    return "Persistent profitability evidence blocked: " + "; ".join(str(item) for item in blockers)


def _result(
    *,
    status: str,
    blockers: list[str],
    missing_fields: list[str],
    metrics: Mapping[str, Any],
    next_safe_action: str,
) -> dict[str, Any]:
    return {
        "engine_version": PERSISTENT_PROFITABILITY_EVIDENCE_VERSION,
        "status": status,
        "persistent_profitability_status": status,
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
    "PERSISTENT_PROFITABILITY_BLOCKED",
    "PERSISTENT_PROFITABILITY_EVIDENCE_VERSION",
    "PERSISTENT_PROFITABILITY_INCOMPLETE",
    "PERSISTENT_PROFITABILITY_READY",
    "build_sample_persistent_profitability_summary",
    "evaluate_persistent_profitability_evidence",
    "result_to_jsonable_dict",
    "result_to_operator_text",
]
