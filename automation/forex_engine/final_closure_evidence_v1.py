"""Final closure evidence adapter for AIOS Forex."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re
from typing import Any, Mapping


FINAL_CLOSURE_EVIDENCE_VERSION = "final_closure_evidence_v1"

FINAL_CLOSURE_REVIEW_READY = "FINAL_CLOSURE_REVIEW_READY"
FINAL_CLOSURE_BLOCKED = "FINAL_CLOSURE_BLOCKED"
FINAL_CLOSURE_INCOMPLETE = "FINAL_CLOSURE_INCOMPLETE"

PROTECTED_PERMISSION_FLAGS = {
    "broker_execution_allowed": False,
    "broker_connection_allowed": False,
    "broker_api_call_allowed": False,
    "live_trading_allowed": False,
    "order_submission_allowed": False,
    "credential_access_allowed": False,
    "account_access_allowed": False,
    "money_movement_allowed": False,
    "all_money_control_allowed": False,
    "bank_movement_allowed": False,
    "withdrawal_allowed": False,
    "deposit_allowed": False,
    "compounding_allowed": False,
    "compounding_execution_allowed": False,
    "autonomous_compounding_allowed": False,
    "scheduler_allowed": False,
    "daemon_allowed": False,
    "webhook_allowed": False,
    "dashboard_execution_authority": False,
    "owner_approval_created": False,
}

REQUIRED_CLOSURE_INPUTS = (
    "replay_evidence",
    "walk_forward_oos_evidence",
    "persistent_profitability_evidence",
    "supervised_observation_22h6d_evidence",
    "final_readiness_evidence",
    "owner_brief_evidence",
)

READY_STATUS_BY_INPUT = {
    "replay_evidence": "REPLAY_PROOF_READY",
    "walk_forward_oos_evidence": "WALK_FORWARD_OOS_READY",
    "persistent_profitability_evidence": "PERSISTENT_PROFITABILITY_READY",
    "supervised_observation_22h6d_evidence": "SUPERVISED_OBSERVATION_READY",
    "final_readiness_evidence": "FOREX_FINAL_READINESS_REVIEW_READY",
    "owner_brief_evidence": "OWNER_DECISION_BRIEF_REVIEW_READY",
}

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
    "broker_connection_allowed",
    "broker_api_call_allowed",
    "live_trading_allowed",
    "order_submission_allowed",
    "credential_access_allowed",
    "account_access_allowed",
    "money_movement_allowed",
    "all_money_control_allowed",
    "bank_movement_allowed",
    "withdrawal_allowed",
    "deposit_allowed",
    "compounding_allowed",
    "compounding_execution_allowed",
    "autonomous_compounding_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
    "dashboard_execution_authority",
    "owner_approval_created",
    "execution_allowed",
    "trade_allowed",
    "broker_access_allowed",
    "real_money_allowed",
    "vacation_mode_execution_allowed",
)


def build_sample_final_closure_inputs() -> dict[str, dict[str, Any]]:
    return {
        "replay_evidence": {
            "status": "REPLAY_PROOF_READY",
            "replay_proof_status": "REPLAY_PROOF_READY",
            "blockers": [],
            "sanitized": True,
            "evidence_age_days": 1,
            "max_evidence_age_days": 7,
            **PROTECTED_PERMISSION_FLAGS,
        },
        "walk_forward_oos_evidence": {
            "status": "WALK_FORWARD_OOS_READY",
            "walk_forward_oos_status": "WALK_FORWARD_OOS_READY",
            "blockers": [],
            "sanitized": True,
            "evidence_age_days": 1,
            "max_evidence_age_days": 7,
            **PROTECTED_PERMISSION_FLAGS,
        },
        "persistent_profitability_evidence": {
            "status": "PERSISTENT_PROFITABILITY_READY",
            "persistent_profitability_status": "PERSISTENT_PROFITABILITY_READY",
            "blockers": [],
            "sanitized": True,
            "evidence_age_days": 1,
            "max_evidence_age_days": 7,
            **PROTECTED_PERMISSION_FLAGS,
        },
        "supervised_observation_22h6d_evidence": {
            "status": "SUPERVISED_OBSERVATION_READY",
            "observation_status": "SUPERVISED_OBSERVATION_READY",
            "blockers": [],
            "sanitized": True,
            "evidence_age_days": 1,
            "max_evidence_age_days": 7,
            **PROTECTED_PERMISSION_FLAGS,
        },
        "final_readiness_evidence": {
            "status": "FOREX_FINAL_READINESS_REVIEW_READY",
            "final_readiness_status": "FOREX_FINAL_READINESS_REVIEW_READY",
            "closure_blockers": [],
            "sanitized": True,
            "evidence_age_days": 1,
            "max_evidence_age_days": 7,
            **PROTECTED_PERMISSION_FLAGS,
        },
        "owner_brief_evidence": {
            "status": "OWNER_DECISION_BRIEF_REVIEW_READY",
            "owner_decision_brief_status": "OWNER_DECISION_BRIEF_REVIEW_READY",
            "blockers": [],
            "owner_review_required": True,
            "sanitized": True,
            "evidence_age_days": 1,
            "max_evidence_age_days": 7,
            **PROTECTED_PERMISSION_FLAGS,
        },
    }


def evaluate_final_closure_evidence(
    closure_inputs: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Evaluate final closure inputs for owner review only."""

    if closure_inputs is None:
        return _result(
            status=FINAL_CLOSURE_INCOMPLETE,
            blockers=["final closure evidence inputs are required"],
            missing_evidence=list(REQUIRED_CLOSURE_INPUTS),
            stale_evidence=[],
            next_safe_action="Provide all final closure evidence inputs.",
        )
    if not isinstance(closure_inputs, Mapping):
        return _result(
            status=FINAL_CLOSURE_INCOMPLETE,
            blockers=["final closure evidence inputs must be a dictionary"],
            missing_evidence=list(REQUIRED_CLOSURE_INPUTS),
            stale_evidence=[],
            next_safe_action="Provide final closure evidence as a dictionary.",
        )

    inputs = {str(key): value for key, value in closure_inputs.items()}
    missing = [name for name in REQUIRED_CLOSURE_INPUTS if name not in inputs]
    blockers: list[str] = []
    stale: list[str] = []
    blockers.extend(_unsafe_fragments(inputs, "closure_inputs"))
    if missing:
        return _result(
            status=FINAL_CLOSURE_INCOMPLETE,
            blockers=blockers + [f"missing evidence: {name}" for name in missing],
            missing_evidence=missing,
            stale_evidence=[],
            next_safe_action="Provide all required final closure evidence inputs.",
        )

    for key in REQUIRED_CLOSURE_INPUTS:
        value = inputs[key]
        if not isinstance(value, Mapping):
            blockers.append(f"{key} must be a dictionary")
            continue
        evidence = dict(value)
        if evidence.get("sanitized") is not True:
            blockers.append(f"{key} is not marked sanitized")
        ready_status = READY_STATUS_BY_INPUT[key]
        observed_status = _status(evidence)
        if observed_status != ready_status:
            blockers.append(f"{key} is not ready: {observed_status or 'missing'}")
        blockers.extend(f"{key}: {item}" for item in _blockers(evidence))
        stale_reason = _stale_reason(key, evidence)
        if stale_reason:
            stale.append(stale_reason)

    blockers.extend(f"stale evidence: {item}" for item in stale)
    status = FINAL_CLOSURE_BLOCKED if blockers else FINAL_CLOSURE_REVIEW_READY
    next_safe_action = (
        "Owner review is required. This evidence creates no trading approval."
        if status == FINAL_CLOSURE_REVIEW_READY
        else "Close final closure evidence blockers before owner review."
    )
    return _result(
        status=status,
        blockers=_dedupe(blockers),
        missing_evidence=[],
        stale_evidence=_dedupe(stale),
        next_safe_action=next_safe_action,
    )


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return dict(result)


def result_to_operator_text(result: Mapping[str, Any]) -> str:
    status = str(result.get("final_closure_status", result.get("status", FINAL_CLOSURE_INCOMPLETE)))
    if status == FINAL_CLOSURE_REVIEW_READY:
        return "Final closure evidence is review-ready only. Owner review is required and no trading approval was created."
    blockers = result.get("blockers") or ["final closure evidence incomplete"]
    return "Final closure evidence blocked: " + "; ".join(str(item) for item in blockers)


def _result(
    *,
    status: str,
    blockers: list[str],
    missing_evidence: list[str],
    stale_evidence: list[str],
    next_safe_action: str,
) -> dict[str, Any]:
    return {
        "engine_version": FINAL_CLOSURE_EVIDENCE_VERSION,
        "status": status,
        "final_closure_status": status,
        "blockers": list(blockers),
        "missing_evidence": list(missing_evidence),
        "stale_evidence": list(stale_evidence),
        "owner_review_required": True,
        "trading_approval_created": False,
        "next_safe_action": next_safe_action,
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


def _status(payload: Mapping[str, Any]) -> str:
    for key in (
        "status",
        "replay_proof_status",
        "walk_forward_oos_status",
        "persistent_profitability_status",
        "observation_status",
        "final_readiness_status",
        "owner_decision_brief_status",
    ):
        value = payload.get(key)
        if value:
            return str(value)
    return ""


def _blockers(payload: Mapping[str, Any]) -> list[str]:
    raw = payload.get("blockers") or payload.get("closure_blockers") or []
    if isinstance(raw, str):
        return [raw] if raw else []
    if isinstance(raw, (list, tuple, set)):
        return [str(item) for item in raw if str(item)]
    return [str(raw)] if raw else []


def _stale_reason(key: str, payload: Mapping[str, Any]) -> str:
    if payload.get("stale") is True:
        return f"{key} is marked stale"
    age = _decimal(payload.get("evidence_age_days"))
    max_age = _decimal(payload.get("max_evidence_age_days"))
    if age is None and max_age is None:
        return ""
    if age is None or max_age is None:
        return f"{key} age metadata incomplete"
    if age > max_age:
        return f"{key} age {age} exceeds max {max_age}"
    return ""


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
        if _string_contains_secret_like_data(value):
            fragments.append(f"{path} contains secret-like or account-like text")


def _string_contains_secret_like_data(value: str) -> bool:
    """Detect labeled private fields in free text without flagging report filenames."""

    joined_fragments = "|".join(re.escape(fragment) for fragment in SECRET_OR_ACCOUNT_FIELD_FRAGMENTS)
    return bool(
        re.search(
            rf"(?i)(?:^|[\s{{\[,'\"])(?:{joined_fragments})(?:[\s'\"])*[:=]",
            value,
        )
    )


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


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


__all__ = [
    "FINAL_CLOSURE_BLOCKED",
    "FINAL_CLOSURE_EVIDENCE_VERSION",
    "FINAL_CLOSURE_INCOMPLETE",
    "FINAL_CLOSURE_REVIEW_READY",
    "build_sample_final_closure_inputs",
    "evaluate_final_closure_evidence",
    "result_to_jsonable_dict",
    "result_to_operator_text",
]
