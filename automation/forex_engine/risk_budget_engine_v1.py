"""Pure-local AIOS Forex risk budget engine V1.

The engine evaluates sanitized candidate and risk-cap dictionaries for owner
review only. It performs no broker calls, credential reads, account lookups,
order creation, file writes, scheduling, or runtime mutation.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


RISK_BUDGET_ENGINE_VERSION = "risk_budget_engine_v1"

RISK_BUDGET_ACCEPTED = "RISK_BUDGET_ACCEPTED"
RISK_BUDGET_BLOCKED = "RISK_BUDGET_BLOCKED"
RISK_BUDGET_INCOMPLETE = "RISK_BUDGET_INCOMPLETE"

REVIEW_ONLY_NEXT_ACTION = (
    "Continue to broker health read-only review; do not approve, route, or "
    "submit any order."
)
BLOCKED_NEXT_ACTION = (
    "Repair risk budget blockers before any supervised demo review."
)
INCOMPLETE_NEXT_ACTION = (
    "Provide the missing sanitized candidate and risk-cap fields, then rerun "
    "the local risk budget engine."
)

PROTECTED_PERMISSION_FLAGS = {
    "broker_execution_allowed": False,
    "live_trading_allowed": False,
    "order_submission_allowed": False,
    "credential_access_allowed": False,
    "account_access_allowed": False,
    "dashboard_execution_authority": False,
    "owner_approval_created": False,
}

REQUIRED_CANDIDATE_FIELDS = (
    "candidate_id",
    "strategy_id",
    "risk_per_trade_pct",
    "daily_loss_pct",
    "current_drawdown_pct",
    "expectancy",
    "profit_factor",
    "sample_size",
    "evidence_age_days",
)

REQUIRED_RISK_CAP_FIELDS = (
    "max_risk_per_trade_pct",
    "max_daily_loss_pct",
    "max_total_drawdown_pct",
    "min_expectancy",
    "min_profit_factor",
    "min_sample_size",
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
)


def build_sample_candidate() -> dict[str, Any]:
    return {
        "candidate_id": "supertrend-review-candidate",
        "strategy_id": "supertrend_m15_v1",
        "risk_per_trade_pct": 0.25,
        "daily_loss_pct": 0.0,
        "current_drawdown_pct": 2.0,
        "expectancy": 0.18,
        "profit_factor": 1.75,
        "sample_size": 64,
        "evidence_age_days": 2,
        "risk_controls_present": True,
        "sanitized": True,
    }


def build_sample_risk_caps() -> dict[str, Any]:
    return {
        "max_risk_per_trade_pct": 0.5,
        "max_daily_loss_pct": 2.0,
        "max_total_drawdown_pct": 8.0,
        "min_expectancy": 0.05,
        "min_profit_factor": 1.25,
        "min_sample_size": 30,
        "max_evidence_age_days": 7,
    }


def evaluate_risk_budget(
    candidate: Mapping[str, Any] | None = None,
    risk_caps: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate a sanitized candidate against risk caps for review only."""

    if candidate is None or risk_caps is None:
        return _result(
            status=RISK_BUDGET_INCOMPLETE,
            candidate=candidate,
            risk_caps=risk_caps,
            blockers=["candidate and risk_caps are required"],
            risk_budget={},
            next_safe_action=INCOMPLETE_NEXT_ACTION,
        )

    candidate_payload = dict(candidate)
    cap_payload = dict(risk_caps)
    blockers: list[str] = []
    warnings: list[str] = []

    missing = _missing_fields(candidate_payload, REQUIRED_CANDIDATE_FIELDS)
    missing.extend(
        f"risk_caps.{name}" for name in _missing_fields(cap_payload, REQUIRED_RISK_CAP_FIELDS)
    )
    if missing:
        return _result(
            status=RISK_BUDGET_INCOMPLETE,
            candidate=candidate_payload,
            risk_caps=cap_payload,
            blockers=[f"missing required field: {name}" for name in missing],
            risk_budget={},
            next_safe_action=INCOMPLETE_NEXT_ACTION,
        )

    unsafe_fragments = _unsafe_fragments(candidate_payload, "candidate")
    unsafe_fragments.extend(_unsafe_fragments(cap_payload, "risk_caps"))
    if unsafe_fragments:
        blockers.extend(unsafe_fragments)

    risk_per_trade = _decimal(candidate_payload["risk_per_trade_pct"])
    daily_loss = _decimal(candidate_payload["daily_loss_pct"])
    drawdown = _decimal(candidate_payload["current_drawdown_pct"])
    expectancy = _decimal(candidate_payload["expectancy"])
    profit_factor = _decimal(candidate_payload["profit_factor"])
    sample_size = _decimal(candidate_payload["sample_size"])
    evidence_age = _decimal(candidate_payload["evidence_age_days"])

    max_risk = _decimal(cap_payload["max_risk_per_trade_pct"])
    max_daily_loss = _decimal(cap_payload["max_daily_loss_pct"])
    max_drawdown = _decimal(cap_payload["max_total_drawdown_pct"])
    min_expectancy = _decimal(cap_payload["min_expectancy"])
    min_profit_factor = _decimal(cap_payload["min_profit_factor"])
    min_sample = _decimal(cap_payload["min_sample_size"])
    max_age = _decimal(cap_payload["max_evidence_age_days"])

    decimal_errors = [
        name
        for name, value in (
            ("candidate.risk_per_trade_pct", risk_per_trade),
            ("candidate.daily_loss_pct", daily_loss),
            ("candidate.current_drawdown_pct", drawdown),
            ("candidate.expectancy", expectancy),
            ("candidate.profit_factor", profit_factor),
            ("candidate.sample_size", sample_size),
            ("candidate.evidence_age_days", evidence_age),
            ("risk_caps.max_risk_per_trade_pct", max_risk),
            ("risk_caps.max_daily_loss_pct", max_daily_loss),
            ("risk_caps.max_total_drawdown_pct", max_drawdown),
            ("risk_caps.min_expectancy", min_expectancy),
            ("risk_caps.min_profit_factor", min_profit_factor),
            ("risk_caps.min_sample_size", min_sample),
            ("risk_caps.max_evidence_age_days", max_age),
        )
        if value is None
    ]
    if decimal_errors:
        return _result(
            status=RISK_BUDGET_INCOMPLETE,
            candidate=candidate_payload,
            risk_caps=cap_payload,
            blockers=[f"field must be numeric: {name}" for name in decimal_errors],
            risk_budget={},
            next_safe_action=INCOMPLETE_NEXT_ACTION,
        )

    assert risk_per_trade is not None
    assert daily_loss is not None
    assert drawdown is not None
    assert expectancy is not None
    assert profit_factor is not None
    assert sample_size is not None
    assert evidence_age is not None
    assert max_risk is not None
    assert max_daily_loss is not None
    assert max_drawdown is not None
    assert min_expectancy is not None
    assert min_profit_factor is not None
    assert min_sample is not None
    assert max_age is not None

    if min_expectancy < 0:
        blockers.append("risk_caps.min_expectancy conflicts with fail-closed policy")
    if max_risk <= 0 or max_daily_loss <= 0 or max_drawdown <= 0:
        blockers.append("risk cap limits must be positive")
    if risk_per_trade > max_risk:
        blockers.append("candidate risk_per_trade_pct exceeds risk cap")
    if daily_loss > max_daily_loss:
        blockers.append("candidate daily_loss_pct exceeds daily loss cap")
    if drawdown > max_drawdown:
        blockers.append("candidate current_drawdown_pct exceeds drawdown cap")
    if expectancy < min_expectancy:
        blockers.append("candidate expectancy is below risk budget minimum")
    if profit_factor < min_profit_factor:
        blockers.append("candidate profit_factor is below risk budget minimum")
    if sample_size < min_sample:
        blockers.append("candidate sample_size is below risk budget minimum")
    if evidence_age > max_age:
        blockers.append("candidate evidence is stale for risk review")
    if candidate_payload.get("risk_controls_present") is False:
        blockers.append("candidate risk controls are marked absent")
    if candidate_payload.get("sanitized") is False:
        blockers.append("candidate is not marked sanitized")

    remaining_daily_loss = max(max_daily_loss - daily_loss, Decimal("0"))
    remaining_drawdown = max(max_drawdown - drawdown, Decimal("0"))
    risk_budget = {
        "risk_per_trade_pct": _float(risk_per_trade),
        "max_risk_per_trade_pct": _float(max_risk),
        "daily_loss_pct": _float(daily_loss),
        "remaining_daily_loss_pct": _float(remaining_daily_loss),
        "current_drawdown_pct": _float(drawdown),
        "remaining_drawdown_pct": _float(remaining_drawdown),
        "sample_size": int(sample_size),
        "evidence_age_days": _float(evidence_age),
        "review_only": True,
    }

    if blockers:
        status = RISK_BUDGET_BLOCKED
        next_action = BLOCKED_NEXT_ACTION
    else:
        status = RISK_BUDGET_ACCEPTED
        next_action = REVIEW_ONLY_NEXT_ACTION
        warnings.append("risk budget is review-only and authorizes no trading")

    result = _result(
        status=status,
        candidate=candidate_payload,
        risk_caps=cap_payload,
        blockers=blockers,
        risk_budget=risk_budget,
        next_safe_action=next_action,
    )
    result["warnings"] = warnings
    return result


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return _jsonable(dict(result))


def result_to_operator_text(result: Mapping[str, Any]) -> str:
    status = str(result.get("status", RISK_BUDGET_INCOMPLETE))
    blockers = result.get("blockers") or []
    if status == RISK_BUDGET_ACCEPTED:
        return (
            "Risk budget accepted for review only. No broker execution, live "
            "trading, order submission, credential access, account access, "
            "dashboard authority, or owner approval was created."
        )
    blocker_text = "; ".join(str(item) for item in blockers) or "input incomplete"
    return f"Risk budget blocked: {blocker_text}. No execution authority was created."


def _result(
    *,
    status: str,
    candidate: Mapping[str, Any] | None,
    risk_caps: Mapping[str, Any] | None,
    blockers: list[str],
    risk_budget: Mapping[str, Any],
    next_safe_action: str,
) -> dict[str, Any]:
    return {
        "engine_version": RISK_BUDGET_ENGINE_VERSION,
        "status": status,
        "candidate_id": _text((candidate or {}).get("candidate_id")),
        "strategy_id": _text((candidate or {}).get("strategy_id")),
        "blockers": list(blockers),
        "risk_budget": dict(risk_budget),
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


def _float(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.000001")))


def _jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return _float(value)
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


__all__ = [
    "RISK_BUDGET_ACCEPTED",
    "RISK_BUDGET_BLOCKED",
    "RISK_BUDGET_ENGINE_VERSION",
    "RISK_BUDGET_INCOMPLETE",
    "build_sample_candidate",
    "build_sample_risk_caps",
    "evaluate_risk_budget",
    "result_to_jsonable_dict",
    "result_to_operator_text",
]
