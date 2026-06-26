"""Final readiness checker V1 for AIOS Forex closure review."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


FOREX_FINAL_READINESS_CHECKER_VERSION = "forex_final_readiness_checker_v1"

FOREX_FINAL_READINESS_REVIEW_READY = "FOREX_FINAL_READINESS_REVIEW_READY"
FOREX_FINAL_READINESS_BLOCKED = "FOREX_FINAL_READINESS_BLOCKED"
FOREX_FINAL_READINESS_INCOMPLETE = "FOREX_FINAL_READINESS_INCOMPLETE"

CHAIN_READY_STATUS = "FOREX_CLOSURE_CHAIN_REVIEW_READY"

REQUIRED_EVIDENCE_KEYS = (
    "persistent_profitability_proof",
    "twenty_two_hour_six_day_observation",
    "sanitized_broker_readonly_evidence",
    "replay_proof",
    "walk_forward_proof",
    "owner_review_evidence",
    "validator_evidence",
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


def build_sample_validator_evidence() -> dict[str, Any]:
    return {
        "persistent_profitability_proof": True,
        "twenty_two_hour_six_day_observation": True,
        "sanitized_broker_readonly_evidence": True,
        "replay_proof": True,
        "walk_forward_proof": True,
        "owner_review_evidence": True,
        "validator_evidence": True,
        "validators": [
            {"name": "targeted_pytest", "status": "PASS"},
            {"name": "py_compile", "status": "PASS"},
        ],
        "sanitized": True,
    }


def build_sample_evidence_age_metadata() -> dict[str, Any]:
    return {
        key: {"age_days": 1, "max_age_days": 7}
        for key in REQUIRED_EVIDENCE_KEYS
    }


def evaluate_forex_final_readiness(
    integrated_chain: Mapping[str, Any] | None = None,
    validator_evidence: Mapping[str, Any] | None = None,
    evidence_age_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate final readiness evidence for owner review only."""

    if integrated_chain is None or validator_evidence is None or evidence_age_metadata is None:
        return _result(
            status=FOREX_FINAL_READINESS_INCOMPLETE,
            closure_blockers=[
                "integrated_chain, validator_evidence, and evidence_age_metadata are required"
            ],
            missing_evidence=list(REQUIRED_EVIDENCE_KEYS),
            stale_evidence=[],
            next_safe_action="Provide final chain, validator evidence, and age metadata before readiness review.",
        )

    chain = dict(integrated_chain)
    validators = dict(validator_evidence)
    age_meta = dict(evidence_age_metadata)
    closure_blockers: list[str] = []
    missing_evidence: list[str] = []
    stale_evidence: list[str] = []

    closure_blockers.extend(_unsafe_fragments(chain, "integrated_chain"))
    closure_blockers.extend(_unsafe_fragments(validators, "validator_evidence"))
    closure_blockers.extend(_unsafe_fragments(age_meta, "evidence_age_metadata"))

    if chain.get("status") != CHAIN_READY_STATUS:
        closure_blockers.append(
            f"integrated chain is not review-ready: {chain.get('status', 'missing')}"
        )
    closure_blockers.extend(f"chain: {item}" for item in _blockers(chain))

    for key in REQUIRED_EVIDENCE_KEYS:
        if validators.get(key) is not True:
            missing_evidence.append(key)
        stale_reason = _stale_reason(key, age_meta.get(key))
        if stale_reason:
            stale_evidence.append(stale_reason)

    if not _validators_pass(validators.get("validators")):
        missing_evidence.append("passing_validator_records")

    closure_blockers.extend(f"missing evidence: {key}" for key in missing_evidence)
    closure_blockers.extend(f"stale evidence: {item}" for item in stale_evidence)

    status = (
        FOREX_FINAL_READINESS_BLOCKED
        if closure_blockers
        else FOREX_FINAL_READINESS_REVIEW_READY
    )
    next_safe_action = (
        "Prepare owner decision brief for review only; do not approve execution."
        if status == FOREX_FINAL_READINESS_REVIEW_READY
        else "Close final readiness blockers before owner decision review."
    )
    return _result(
        status=status,
        closure_blockers=_dedupe(closure_blockers),
        missing_evidence=_dedupe(missing_evidence),
        stale_evidence=_dedupe(stale_evidence),
        next_safe_action=next_safe_action,
    )


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return dict(result)


def result_to_operator_text(result: Mapping[str, Any]) -> str:
    status = str(result.get("status", FOREX_FINAL_READINESS_INCOMPLETE))
    if status == FOREX_FINAL_READINESS_REVIEW_READY:
        return "Final readiness is review-ready only. It creates no trading approval."
    blockers = result.get("closure_blockers") or ["final readiness evidence incomplete"]
    return "Final readiness blocked: " + "; ".join(str(item) for item in blockers)


def _result(
    *,
    status: str,
    closure_blockers: list[str],
    missing_evidence: list[str],
    stale_evidence: list[str],
    next_safe_action: str,
) -> dict[str, Any]:
    return {
        "engine_version": FOREX_FINAL_READINESS_CHECKER_VERSION,
        "status": status,
        "final_readiness_status": status,
        "closure_blockers": list(closure_blockers),
        "missing_evidence": list(missing_evidence),
        "stale_evidence": list(stale_evidence),
        "next_safe_action": next_safe_action,
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


def _validators_pass(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for item in value:
        if not isinstance(item, Mapping):
            return False
        status = str(item.get("status", "")).upper()
        if status not in {"PASS", "PASSED", "OK"}:
            return False
    return True


def _stale_reason(key: str, value: Any) -> str:
    if not isinstance(value, Mapping):
        return f"{key} age metadata missing"
    age = _decimal(value.get("age_days"))
    max_age = _decimal(value.get("max_age_days"))
    if age is None or max_age is None:
        return f"{key} age metadata incomplete"
    if age > max_age:
        return f"{key} age {age} exceeds max {max_age}"
    return ""


def _blockers(payload: Mapping[str, Any]) -> list[str]:
    raw = payload.get("blockers") or payload.get("closure_blockers") or []
    if isinstance(raw, str):
        return [raw] if raw else []
    if isinstance(raw, (list, tuple, set)):
        return [str(item) for item in raw if str(item)]
    return [str(raw)] if raw else []


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


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


__all__ = [
    "FOREX_FINAL_READINESS_BLOCKED",
    "FOREX_FINAL_READINESS_CHECKER_VERSION",
    "FOREX_FINAL_READINESS_INCOMPLETE",
    "FOREX_FINAL_READINESS_REVIEW_READY",
    "REQUIRED_EVIDENCE_KEYS",
    "build_sample_evidence_age_metadata",
    "build_sample_validator_evidence",
    "evaluate_forex_final_readiness",
    "result_to_jsonable_dict",
    "result_to_operator_text",
]
