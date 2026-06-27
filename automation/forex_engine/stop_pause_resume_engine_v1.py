"""Stop, pause, and review-only resume engine V1 for AIOS Forex."""

from __future__ import annotations

from typing import Any, Mapping


STOP_PAUSE_RESUME_ENGINE_VERSION = "stop_pause_resume_engine_v1"

STOP_REQUIRED = "STOP_REQUIRED"
PAUSE_REQUIRED = "PAUSE_REQUIRED"
REVIEW_ONLY_RESUME = "REVIEW_ONLY_RESUME"
STOP_PAUSE_RESUME_INCOMPLETE = "STOP_PAUSE_RESUME_INCOMPLETE"

PROTECTED_PERMISSION_FLAGS = {
    "broker_execution_allowed": False,
    "live_trading_allowed": False,
    "order_submission_allowed": False,
    "credential_access_allowed": False,
    "account_access_allowed": False,
    "dashboard_execution_authority": False,
    "owner_approval_created": False,
}

READY_STATUSES = {
    "RISK_BUDGET_ACCEPTED",
    "BROKER_HEALTH_REVIEW_READY",
    "PROFITABILITY_EVIDENCE_REVIEW_READY",
    "DASHBOARD_TRUTH_DISPLAY_READY",
}

INCOMPLETE_STATUS_FRAGMENTS = ("INCOMPLETE", "MISSING", "UNKNOWN")
BLOCKED_STATUS_FRAGMENTS = ("BLOCKED", "STOP", "FAILED", "UNSAFE", "REJECT")

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


def build_sample_dashboard_state() -> dict[str, Any]:
    return {
        "display_state": "DISPLAY_ONLY_READY",
        "evidence_fresh": True,
        "blockers": [],
        "dashboard_execution_authority": False,
        "dashboard_mutation_requested": False,
    }


def build_sample_operator_halt_state() -> dict[str, Any]:
    return {
        "halt_requested": False,
        "operator_reason": "",
        "resume_requested": False,
    }


def evaluate_stop_pause_resume(
    risk_state: Mapping[str, Any] | None = None,
    broker_state: Mapping[str, Any] | None = None,
    profitability_state: Mapping[str, Any] | None = None,
    dashboard_state: Mapping[str, Any] | None = None,
    operator_halt_state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate stop, pause, or review-only resume state."""

    inputs = {
        "risk_state": risk_state,
        "broker_state": broker_state,
        "profitability_state": profitability_state,
        "dashboard_state": dashboard_state,
        "operator_halt_state": operator_halt_state,
    }
    missing_inputs = [name for name, value in inputs.items() if value is None]
    if missing_inputs:
        return _result(
            status=STOP_PAUSE_RESUME_INCOMPLETE,
            control_state="PAUSE",
            blockers=[f"{name} is required" for name in missing_inputs],
            escalation_path="operator_review",
            next_safe_action="Provide complete upstream states before resume review.",
        )

    risk = dict(risk_state or {})
    broker = dict(broker_state or {})
    profitability = dict(profitability_state or {})
    dashboard = dict(dashboard_state or {})
    operator_halt = dict(operator_halt_state or {})

    blockers: list[str] = []
    pause_reasons: list[str] = []
    unsafe = []
    unsafe.extend(_unsafe_fragments(risk, "risk_state"))
    unsafe.extend(_unsafe_fragments(broker, "broker_state"))
    unsafe.extend(_unsafe_fragments(profitability, "profitability_state"))
    unsafe.extend(_unsafe_fragments(dashboard, "dashboard_state"))
    unsafe.extend(_unsafe_fragments(operator_halt, "operator_halt_state"))
    blockers.extend(unsafe)

    if _truthy(operator_halt.get("halt_requested")):
        blockers.append("operator halt is active")
    if _truthy(dashboard.get("dashboard_mutation_requested")):
        blockers.append("dashboard mutation requested")
    if dashboard.get("evidence_fresh") is False:
        pause_reasons.append("dashboard evidence is stale")
    if dashboard.get("display_state") in (None, ""):
        pause_reasons.append("dashboard display state is missing")

    for name, payload in (
        ("risk", risk),
        ("broker", broker),
        ("profitability", profitability),
    ):
        status = _status(payload)
        payload_blockers = _blockers(payload)
        if status in READY_STATUSES:
            continue
        if _contains_fragment(status, BLOCKED_STATUS_FRAGMENTS) or payload_blockers:
            blockers.append(f"{name} state blocks resume: {status}")
            blockers.extend(f"{name}: {item}" for item in payload_blockers)
        elif _contains_fragment(status, INCOMPLETE_STATUS_FRAGMENTS) or not status:
            pause_reasons.append(f"{name} state is incomplete: {status or 'missing'}")
        else:
            blockers.append(f"{name} state is unknown: {status}")

    dashboard_blockers = _blockers(dashboard)
    if dashboard_blockers:
        pause_reasons.extend(f"dashboard: {item}" for item in dashboard_blockers)

    if blockers:
        return _result(
            status=STOP_REQUIRED,
            control_state="STOP",
            blockers=_dedupe(blockers),
            escalation_path="human_owner_review_required",
            next_safe_action="Stop the chain and resolve blockers before any resume review.",
        )
    if pause_reasons:
        return _result(
            status=PAUSE_REQUIRED,
            control_state="PAUSE",
            blockers=_dedupe(pause_reasons),
            escalation_path="evidence_repair_review",
            next_safe_action="Pause and refresh evidence before owner resume review.",
        )
    return _result(
        status=REVIEW_ONLY_RESUME,
        control_state="REVIEW_ONLY_RESUME",
        blockers=[],
        escalation_path="owner_review_only",
        next_safe_action="Prepare review-only demo intent; execution remains locked.",
    )


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return dict(result)


def result_to_operator_text(result: Mapping[str, Any]) -> str:
    status = str(result.get("status", STOP_PAUSE_RESUME_INCOMPLETE))
    state = str(result.get("control_state", "PAUSE"))
    if status == REVIEW_ONLY_RESUME:
        return "Stop/pause/resume state is review-only resume. No execution authority was created."
    blockers = result.get("blockers") or ["resume state incomplete"]
    return f"Stop/pause/resume state is {state}: " + "; ".join(str(item) for item in blockers)


def _result(
    *,
    status: str,
    control_state: str,
    blockers: list[str],
    escalation_path: str,
    next_safe_action: str,
) -> dict[str, Any]:
    return {
        "engine_version": STOP_PAUSE_RESUME_ENGINE_VERSION,
        "status": status,
        "control_state": control_state,
        "blockers": list(blockers),
        "escalation_path": escalation_path,
        "next_safe_action": next_safe_action,
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


def _status(payload: Mapping[str, Any]) -> str:
    return _text(payload.get("status") or payload.get("classification"))


def _blockers(payload: Mapping[str, Any]) -> list[str]:
    raw = payload.get("blockers") or []
    if isinstance(raw, str):
        return [raw] if raw else []
    if isinstance(raw, (list, tuple, set)):
        return [_text(item) for item in raw if _text(item)]
    return [_text(raw)] if raw else []


def _contains_fragment(value: str, fragments: tuple[str, ...]) -> bool:
    canonical = value.upper()
    return any(fragment in canonical for fragment in fragments)


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
    "PAUSE_REQUIRED",
    "REVIEW_ONLY_RESUME",
    "STOP_PAUSE_RESUME_ENGINE_VERSION",
    "STOP_PAUSE_RESUME_INCOMPLETE",
    "STOP_REQUIRED",
    "build_sample_dashboard_state",
    "build_sample_operator_halt_state",
    "evaluate_stop_pause_resume",
    "result_to_jsonable_dict",
    "result_to_operator_text",
]
