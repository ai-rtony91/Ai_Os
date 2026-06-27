"""Display-only dashboard truth summary engine V1 for AIOS Forex."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


DASHBOARD_TRUTH_SUMMARY_VERSION = "dashboard_truth_summary_v1"

DASHBOARD_TRUTH_DISPLAY_READY = "DASHBOARD_TRUTH_DISPLAY_READY"
DASHBOARD_TRUTH_BLOCKED = "DASHBOARD_TRUTH_BLOCKED"
DASHBOARD_TRUTH_INCOMPLETE = "DASHBOARD_TRUTH_INCOMPLETE"

PROTECTED_PERMISSION_FLAGS = {
    "broker_execution_allowed": False,
    "live_trading_allowed": False,
    "order_submission_allowed": False,
    "credential_access_allowed": False,
    "account_access_allowed": False,
    "dashboard_execution_authority": False,
    "owner_approval_created": False,
}

REQUIRED_UPSTREAM_KEYS = (
    "risk",
    "broker",
    "profitability",
    "stop",
    "demo_intent",
)

READY_STATUSES = {
    "risk": "RISK_BUDGET_ACCEPTED",
    "broker": "BROKER_HEALTH_REVIEW_READY",
    "profitability": "PROFITABILITY_EVIDENCE_REVIEW_READY",
    "stop": "REVIEW_ONLY_RESUME",
    "demo_intent": "DEMO_INTENT_OWNER_REVIEW_READY",
}

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


def build_dashboard_truth_summary(
    upstream_results: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build one compact display-only truth summary from upstream results."""

    if upstream_results is None:
        return _result(
            status=DASHBOARD_TRUTH_INCOMPLETE,
            stage_statuses={},
            blockers=["upstream_results are required"],
            freshness={"state": "missing", "stale_sources": []},
            evidence_state="INCOMPLETE",
            next_safe_action="Provide upstream result dictionaries before dashboard display.",
        )

    missing = [
        key
        for key in REQUIRED_UPSTREAM_KEYS
        if key not in upstream_results or not isinstance(upstream_results[key], Mapping)
    ]
    if missing:
        return _result(
            status=DASHBOARD_TRUTH_INCOMPLETE,
            stage_statuses={},
            blockers=[f"missing upstream result: {key}" for key in missing],
            freshness={"state": "missing", "stale_sources": []},
            evidence_state="INCOMPLETE",
            next_safe_action="Provide all required upstream results before dashboard display.",
        )

    stages = {key: dict(upstream_results[key]) for key in REQUIRED_UPSTREAM_KEYS}
    blockers: list[str] = []
    stage_statuses: dict[str, str] = {}
    stale_sources: list[str] = []

    for name, payload in stages.items():
        status = _text(payload.get("status") or payload.get("classification"))
        stage_statuses[name] = status
        if status != READY_STATUSES[name]:
            blockers.append(f"{name} status is not display-ready: {status or 'missing'}")
        blockers.extend(f"{name}: {item}" for item in _blockers(payload))
        blockers.extend(_unsafe_fragments(payload, name))
        if _is_stale(payload):
            stale_sources.append(name)

    if stale_sources:
        blockers.extend(f"{name} evidence is stale" for name in stale_sources)

    status = DASHBOARD_TRUTH_BLOCKED if blockers else DASHBOARD_TRUTH_DISPLAY_READY
    evidence_state = "DISPLAY_READY" if status == DASHBOARD_TRUTH_DISPLAY_READY else "BLOCKED"
    next_safe_action = (
        "Display this summary as read-only truth; do not treat it as execution authority."
        if status == DASHBOARD_TRUTH_DISPLAY_READY
        else "Repair upstream blockers before presenting dashboard truth as current."
    )
    return _result(
        status=status,
        stage_statuses=stage_statuses,
        blockers=_dedupe(blockers),
        freshness={
            "state": "STALE" if stale_sources else "FRESH",
            "stale_sources": list(stale_sources),
        },
        evidence_state=evidence_state,
        next_safe_action=next_safe_action,
    )


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return dict(result)


def result_to_operator_text(result: Mapping[str, Any]) -> str:
    status = str(result.get("status", DASHBOARD_TRUTH_INCOMPLETE))
    if status == DASHBOARD_TRUTH_DISPLAY_READY:
        return "Dashboard truth summary is display-ready only. It creates no readiness or execution authority."
    blockers = result.get("blockers") or ["dashboard truth input incomplete"]
    return "Dashboard truth summary blocked: " + "; ".join(str(item) for item in blockers)


def _result(
    *,
    status: str,
    stage_statuses: Mapping[str, str],
    blockers: list[str],
    freshness: Mapping[str, Any],
    evidence_state: str,
    next_safe_action: str,
) -> dict[str, Any]:
    return {
        "engine_version": DASHBOARD_TRUTH_SUMMARY_VERSION,
        "status": status,
        "display_only": True,
        "truth_summary": {
            "stage_statuses": dict(stage_statuses),
            "blocker_count": len(blockers),
            "freshness": dict(freshness),
            "evidence_state": evidence_state,
        },
        "stage_statuses": dict(stage_statuses),
        "blockers": list(blockers),
        "freshness": dict(freshness),
        "evidence_state": evidence_state,
        "next_safe_action": next_safe_action,
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


def _blockers(payload: Mapping[str, Any]) -> list[str]:
    raw = payload.get("blockers") or []
    if isinstance(raw, str):
        return [raw] if raw else []
    if isinstance(raw, (list, tuple, set)):
        return [_text(item) for item in raw if _text(item)]
    return [_text(raw)] if raw else []


def _is_stale(payload: Mapping[str, Any]) -> bool:
    freshness = payload.get("freshness")
    if isinstance(freshness, Mapping):
        if freshness.get("fresh") is False:
            return True
        if _text(freshness.get("state")).upper() == "STALE":
            return True
    age = _decimal(payload.get("evidence_age_days"))
    max_age = _decimal(payload.get("max_evidence_age_days"))
    if age is not None and max_age is not None:
        return age > max_age
    return False


def _unsafe_fragments(payload: Mapping[str, Any], prefix: str) -> list[str]:
    fragments: list[str] = []
    _scan_payload(payload, prefix, fragments)
    return fragments


def _scan_payload(value: Any, path: str, fragments: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            lowered = key_text.lower()
            if lowered in UNSAFE_TRUE_FIELDS and _truthy(item):
                fragments.append(f"{path}.{key_text} is unsafe true")
            if lowered in UNSAFE_TRUE_FIELDS:
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


def _text(value: Any) -> str:
    if value is None:
        return ""
    return value.strip() if isinstance(value, str) else str(value).strip()


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


__all__ = [
    "DASHBOARD_TRUTH_BLOCKED",
    "DASHBOARD_TRUTH_DISPLAY_READY",
    "DASHBOARD_TRUTH_INCOMPLETE",
    "DASHBOARD_TRUTH_SUMMARY_VERSION",
    "build_dashboard_truth_summary",
    "result_to_jsonable_dict",
    "result_to_operator_text",
]
