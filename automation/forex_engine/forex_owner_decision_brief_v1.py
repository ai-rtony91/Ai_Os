"""Owner decision brief generator V1 for AIOS Forex."""

from __future__ import annotations

from typing import Any, Mapping


FOREX_OWNER_DECISION_BRIEF_VERSION = "forex_owner_decision_brief_v1"

OWNER_DECISION_BRIEF_REVIEW_READY = "OWNER_DECISION_BRIEF_REVIEW_READY"
OWNER_DECISION_BRIEF_BLOCKED = "OWNER_DECISION_BRIEF_BLOCKED"
OWNER_DECISION_BRIEF_INCOMPLETE = "OWNER_DECISION_BRIEF_INCOMPLETE"

CHAIN_READY_STATUS = "FOREX_CLOSURE_CHAIN_REVIEW_READY"
READINESS_READY_STATUS = "FOREX_FINAL_READINESS_REVIEW_READY"

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
)


def build_forex_owner_decision_brief(
    integrated_chain: Mapping[str, Any] | None = None,
    final_readiness: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an owner-readable decision brief from final chain evidence."""

    if integrated_chain is None or final_readiness is None:
        return _result(
            status=OWNER_DECISION_BRIEF_INCOMPLETE,
            brief={},
            blockers=["integrated_chain and final_readiness are required"],
            evidence_gaps=["decision brief inputs missing"],
            next_safe_action="Provide chain and final readiness outputs before owner brief review.",
        )

    chain = dict(integrated_chain)
    readiness = dict(final_readiness)
    blockers: list[str] = []
    evidence_gaps: list[str] = []
    blockers.extend(_unsafe_fragments(chain, "integrated_chain"))
    blockers.extend(_unsafe_fragments(readiness, "final_readiness"))

    if chain.get("status") != CHAIN_READY_STATUS:
        blockers.append(f"integrated chain is not review-ready: {chain.get('status', 'missing')}")
    if readiness.get("status") != READINESS_READY_STATUS:
        blockers.append(f"final readiness is not review-ready: {readiness.get('status', 'missing')}")

    blockers.extend(f"chain: {item}" for item in _blockers(chain))
    blockers.extend(f"readiness: {item}" for item in _blockers(readiness))
    evidence_gaps.extend(str(item) for item in readiness.get("missing_evidence", []) if str(item))
    evidence_gaps.extend(str(item) for item in readiness.get("stale_evidence", []) if str(item))

    status = OWNER_DECISION_BRIEF_BLOCKED if blockers or evidence_gaps else OWNER_DECISION_BRIEF_REVIEW_READY
    next_safe_action = (
        "Anthony may review the brief; this output creates no approval or execution authority."
        if status == OWNER_DECISION_BRIEF_REVIEW_READY
        else "Close blockers and evidence gaps before owner decision review."
    )
    brief = {
        "brief_type": "AIOS_FOREX_OWNER_DECISION_REVIEW_ONLY",
        "current_status": status,
        "chain_status": chain.get("status"),
        "final_readiness_status": readiness.get("status"),
        "stage_statuses": dict(chain.get("stage_statuses", {})),
        "blockers": _dedupe(blockers),
        "evidence_gaps": _dedupe(evidence_gaps),
        "owner_decision_required": status == OWNER_DECISION_BRIEF_REVIEW_READY,
        "approval_created": False,
        "execution_authority": "none",
        "next_safe_action": next_safe_action,
    }
    return _result(
        status=status,
        brief=brief,
        blockers=_dedupe(blockers),
        evidence_gaps=_dedupe(evidence_gaps),
        next_safe_action=next_safe_action,
    )


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return dict(result)


def result_to_operator_text(result: Mapping[str, Any]) -> str:
    brief = result.get("decision_brief") or {}
    status = str(result.get("status", OWNER_DECISION_BRIEF_INCOMPLETE))
    if status == OWNER_DECISION_BRIEF_REVIEW_READY:
        return (
            "Owner decision brief is review-ready. Anthony may review the "
            "evidence, but no approval or execution authority was created."
        )
    blockers = brief.get("blockers") or result.get("blockers") or ["owner brief input incomplete"]
    return "Owner decision brief blocked: " + "; ".join(str(item) for item in blockers)


def _result(
    *,
    status: str,
    brief: Mapping[str, Any],
    blockers: list[str],
    evidence_gaps: list[str],
    next_safe_action: str,
) -> dict[str, Any]:
    return {
        "engine_version": FOREX_OWNER_DECISION_BRIEF_VERSION,
        "status": status,
        "decision_brief": dict(brief),
        "blockers": list(blockers),
        "evidence_gaps": list(evidence_gaps),
        "next_safe_action": next_safe_action,
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


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
    "FOREX_OWNER_DECISION_BRIEF_VERSION",
    "OWNER_DECISION_BRIEF_BLOCKED",
    "OWNER_DECISION_BRIEF_INCOMPLETE",
    "OWNER_DECISION_BRIEF_REVIEW_READY",
    "build_forex_owner_decision_brief",
    "result_to_jsonable_dict",
    "result_to_operator_text",
]
