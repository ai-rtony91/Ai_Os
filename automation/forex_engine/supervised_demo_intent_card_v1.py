"""Supervised demo intent card engine V1 for AIOS Forex.

The engine creates an owner-review card from sanitized upstream review states.
It does not create approval, order objects, broker payloads, or execution
authority.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


SUPERVISED_DEMO_INTENT_CARD_VERSION = "supervised_demo_intent_card_v1"

DEMO_INTENT_OWNER_REVIEW_READY = "DEMO_INTENT_OWNER_REVIEW_READY"
DEMO_INTENT_BLOCKED = "DEMO_INTENT_BLOCKED"
DEMO_INTENT_INCOMPLETE = "DEMO_INTENT_INCOMPLETE"

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
    "instrument",
    "direction",
    "evidence_age_days",
    "max_evidence_age_days",
    "sanitized",
)

READY_STATUSES = {
    "RISK_BUDGET_ACCEPTED",
    "BROKER_HEALTH_REVIEW_READY",
    "PROFITABILITY_EVIDENCE_REVIEW_READY",
    "REVIEW_ONLY_RESUME",
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
        "instrument": "EUR_USD_SANITIZED_REVIEW",
        "direction": "long_review",
        "evidence_age_days": 2,
        "max_evidence_age_days": 7,
        "sanitized": True,
    }


def evaluate_supervised_demo_intent_card(
    candidate: Mapping[str, Any] | None = None,
    risk_state: Mapping[str, Any] | None = None,
    broker_state: Mapping[str, Any] | None = None,
    profitability_state: Mapping[str, Any] | None = None,
    stop_state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a review-only supervised demo intent card."""

    inputs = {
        "candidate": candidate,
        "risk_state": risk_state,
        "broker_state": broker_state,
        "profitability_state": profitability_state,
        "stop_state": stop_state,
    }
    missing_inputs = [name for name, value in inputs.items() if value is None]
    if missing_inputs:
        return _result(
            status=DEMO_INTENT_INCOMPLETE,
            candidate={},
            owner_review_card={},
            proof_requirements=[],
            blockers=[f"{name} is required" for name in missing_inputs],
            next_safe_action="Provide complete upstream states before demo intent review.",
        )

    candidate_payload = dict(candidate or {})
    missing_candidate = _missing_fields(candidate_payload, REQUIRED_CANDIDATE_FIELDS)
    if missing_candidate:
        return _result(
            status=DEMO_INTENT_INCOMPLETE,
            candidate=candidate_payload,
            owner_review_card={},
            proof_requirements=[],
            blockers=[f"missing candidate field: {name}" for name in missing_candidate],
            next_safe_action="Provide missing sanitized candidate fields before owner review.",
        )

    states = {
        "risk": dict(risk_state or {}),
        "broker": dict(broker_state or {}),
        "profitability": dict(profitability_state or {}),
        "stop": dict(stop_state or {}),
    }
    blockers: list[str] = []
    blockers.extend(_unsafe_fragments(candidate_payload, "candidate"))
    for name, payload in states.items():
        blockers.extend(_unsafe_fragments(payload, f"{name}_state"))
        status = _text(payload.get("status") or payload.get("classification"))
        if status not in READY_STATUSES:
            blockers.append(f"{name} state is not review-ready: {status or 'missing'}")
        blockers.extend(f"{name}: {item}" for item in _blockers(payload))

    age = _decimal(candidate_payload.get("evidence_age_days"))
    max_age = _decimal(candidate_payload.get("max_evidence_age_days"))
    if age is None or max_age is None:
        return _result(
            status=DEMO_INTENT_INCOMPLETE,
            candidate=candidate_payload,
            owner_review_card={},
            proof_requirements=[],
            blockers=["candidate evidence age fields must be numeric"],
            next_safe_action="Repair candidate freshness fields before owner review.",
        )
    if age > max_age:
        blockers.append("candidate evidence is stale for supervised demo intent review")
    if candidate_payload.get("sanitized") is not True:
        blockers.append("candidate is not marked sanitized")

    proof_requirements = [
        "risk budget accepted for review only",
        "sanitized broker health read-only evidence ready",
        "profitability evidence review-ready",
        "stop/pause/resume state is review-only resume",
        "owner must make any future approval separately",
    ]
    card = {
        "card_type": "SUPERVISED_DEMO_INTENT_REVIEW_ONLY",
        "candidate_id": _text(candidate_payload.get("candidate_id")),
        "strategy_id": _text(candidate_payload.get("strategy_id")),
        "instrument": _text(candidate_payload.get("instrument")),
        "direction": _text(candidate_payload.get("direction")),
        "evidence_age_days": float(age),
        "review_scope": "owner_review_only_no_execution",
        "required_owner_decision": "review evidence; no approval is created by this card",
        "proof_requirements": list(proof_requirements),
    }

    status = DEMO_INTENT_BLOCKED if blockers else DEMO_INTENT_OWNER_REVIEW_READY
    next_safe_action = (
        "Display the intent card for owner review only; do not execute or approve."
        if status == DEMO_INTENT_OWNER_REVIEW_READY
        else "Repair demo intent blockers before owner review."
    )
    return _result(
        status=status,
        candidate=candidate_payload,
        owner_review_card=card,
        proof_requirements=proof_requirements,
        blockers=_dedupe(blockers),
        next_safe_action=next_safe_action,
    )


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return dict(result)


def result_to_operator_text(result: Mapping[str, Any]) -> str:
    status = str(result.get("status", DEMO_INTENT_INCOMPLETE))
    card = result.get("owner_review_card") or {}
    if status == DEMO_INTENT_OWNER_REVIEW_READY:
        return (
            f"Supervised demo intent card ready for owner review only: "
            f"{card.get('strategy_id')} {card.get('direction')} {card.get('instrument')}. "
            "No approval or execution authority was created."
        )
    blockers = result.get("blockers") or ["demo intent input incomplete"]
    return "Supervised demo intent blocked: " + "; ".join(str(item) for item in blockers)


def _result(
    *,
    status: str,
    candidate: Mapping[str, Any],
    owner_review_card: Mapping[str, Any],
    proof_requirements: list[str],
    blockers: list[str],
    next_safe_action: str,
) -> dict[str, Any]:
    return {
        "engine_version": SUPERVISED_DEMO_INTENT_CARD_VERSION,
        "status": status,
        "candidate_id": _text(candidate.get("candidate_id")),
        "owner_review_card": dict(owner_review_card),
        "proof_requirements": list(proof_requirements),
        "blockers": list(blockers),
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


def _blockers(payload: Mapping[str, Any]) -> list[str]:
    raw = payload.get("blockers") or []
    if isinstance(raw, str):
        return [raw] if raw else []
    if isinstance(raw, (list, tuple, set)):
        return [_text(item) for item in raw if _text(item)]
    return [_text(raw)] if raw else []


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
    "DEMO_INTENT_BLOCKED",
    "DEMO_INTENT_INCOMPLETE",
    "DEMO_INTENT_OWNER_REVIEW_READY",
    "SUPERVISED_DEMO_INTENT_CARD_VERSION",
    "build_sample_candidate",
    "evaluate_supervised_demo_intent_card",
    "result_to_jsonable_dict",
    "result_to_operator_text",
]
