"""Evidence milestone selector for AIOS Forex closure evidence."""

from __future__ import annotations

from typing import Any, Mapping


EVIDENCE_MILESTONE_SELECTOR_VERSION = "evidence_milestone_selector_v1"

EVIDENCE_MILESTONE_CONTINUE = "EVIDENCE_MILESTONE_CONTINUE"
EVIDENCE_MILESTONE_BLOCKED = "EVIDENCE_MILESTONE_BLOCKED"
EVIDENCE_MILESTONE_COMPLETE = "EVIDENCE_MILESTONE_COMPLETE"

PROTECTED_PERMISSION_FLAGS = {
    "broker_execution_allowed": False,
    "live_trading_allowed": False,
    "order_submission_allowed": False,
    "credential_access_allowed": False,
    "account_access_allowed": False,
    "dashboard_execution_authority": False,
    "owner_approval_created": False,
}

MILESTONE_ORDER = (
    "replay_proof_evidence",
    "walk_forward_oos_evidence",
    "persistent_profitability_evidence",
    "supervised_observation_22h6d_evidence",
    "final_closure_evidence",
)

READY_STATUS_BY_MILESTONE = {
    "replay_proof_evidence": "REPLAY_PROOF_READY",
    "walk_forward_oos_evidence": "WALK_FORWARD_OOS_READY",
    "persistent_profitability_evidence": "PERSISTENT_PROFITABILITY_READY",
    "supervised_observation_22h6d_evidence": "SUPERVISED_OBSERVATION_READY",
    "final_closure_evidence": "FINAL_CLOSURE_REVIEW_READY",
}

NEXT_PACKET_BY_MILESTONE = {
    "replay_proof_evidence": "AIOS-FOREX-REPLAY-PROOF-EVIDENCE-V1",
    "walk_forward_oos_evidence": "AIOS-FOREX-WALK-FORWARD-OOS-EVIDENCE-V1",
    "persistent_profitability_evidence": "AIOS-FOREX-PERSISTENT-PROFITABILITY-EVIDENCE-V1",
    "supervised_observation_22h6d_evidence": "AIOS-FOREX-22H6D-SUPERVISED-OBSERVATION-EVIDENCE-V1",
    "final_closure_evidence": "AIOS-FOREX-FINAL-CLOSURE-EVIDENCE-V1",
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
    "money_movement_allowed",
    "vacation_mode_execution_allowed",
)


def build_sample_evidence_results() -> dict[str, dict[str, Any]]:
    return {
        "replay_proof_evidence": {
            "status": "REPLAY_PROOF_READY",
            "replay_proof_status": "REPLAY_PROOF_READY",
            "blockers": [],
            "sanitized": True,
            **PROTECTED_PERMISSION_FLAGS,
        },
        "walk_forward_oos_evidence": {
            "status": "WALK_FORWARD_OOS_READY",
            "walk_forward_oos_status": "WALK_FORWARD_OOS_READY",
            "blockers": [],
            "sanitized": True,
            **PROTECTED_PERMISSION_FLAGS,
        },
        "persistent_profitability_evidence": {
            "status": "PERSISTENT_PROFITABILITY_READY",
            "persistent_profitability_status": "PERSISTENT_PROFITABILITY_READY",
            "blockers": [],
            "sanitized": True,
            **PROTECTED_PERMISSION_FLAGS,
        },
        "supervised_observation_22h6d_evidence": {
            "status": "SUPERVISED_OBSERVATION_READY",
            "observation_status": "SUPERVISED_OBSERVATION_READY",
            "blockers": [],
            "sanitized": True,
            **PROTECTED_PERMISSION_FLAGS,
        },
        "final_closure_evidence": {
            "status": "FINAL_CLOSURE_REVIEW_READY",
            "final_closure_status": "FINAL_CLOSURE_REVIEW_READY",
            "blockers": [],
            "sanitized": True,
            **PROTECTED_PERMISSION_FLAGS,
        },
    }


def select_evidence_milestone(
    evidence_results: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Select the next unfinished evidence milestone from result dictionaries."""

    if evidence_results is None:
        return _result(
            status=EVIDENCE_MILESTONE_CONTINUE,
            completed=[],
            blocked=[],
            incomplete=list(MILESTONE_ORDER),
            next_milestone=MILESTONE_ORDER[0],
            blockers=["evidence results are required"],
        )
    if not isinstance(evidence_results, Mapping):
        return _result(
            status=EVIDENCE_MILESTONE_BLOCKED,
            completed=[],
            blocked=[],
            incomplete=list(MILESTONE_ORDER),
            next_milestone=MILESTONE_ORDER[0],
            blockers=["evidence results must be a dictionary"],
        )

    results = {str(key): value for key, value in evidence_results.items()}
    safety_blockers = _unsafe_fragments(results, "evidence_results")
    completed: list[str] = []
    blocked: list[str] = []
    incomplete: list[str] = []
    blockers: list[str] = list(safety_blockers)

    for milestone in MILESTONE_ORDER:
        value = results.get(milestone)
        if not isinstance(value, Mapping):
            incomplete.append(milestone)
            continue
        evidence = dict(value)
        if evidence.get("sanitized") is False:
            blocked.append(milestone)
            blockers.append(f"{milestone} is not marked sanitized")
            continue
        observed_status = _status(evidence)
        expected_status = READY_STATUS_BY_MILESTONE[milestone]
        if observed_status == expected_status:
            completed.append(milestone)
            continue
        if "BLOCKED" in observed_status:
            blocked.append(milestone)
            blockers.extend(f"{milestone}: {item}" for item in _blockers(evidence))
            continue
        incomplete.append(milestone)

    next_milestone = ""
    for milestone in MILESTONE_ORDER:
        if milestone not in completed:
            next_milestone = milestone
            break

    if safety_blockers or blocked:
        status = EVIDENCE_MILESTONE_BLOCKED
    elif not next_milestone:
        status = EVIDENCE_MILESTONE_COMPLETE
    else:
        status = EVIDENCE_MILESTONE_CONTINUE

    return _result(
        status=status,
        completed=completed,
        blocked=blocked,
        incomplete=incomplete,
        next_milestone=next_milestone,
        blockers=_dedupe(blockers),
    )


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return dict(result)


def result_to_operator_text(result: Mapping[str, Any]) -> str:
    status = str(result.get("status", EVIDENCE_MILESTONE_CONTINUE))
    if status == EVIDENCE_MILESTONE_COMPLETE:
        return "All Forex evidence milestones are complete for review. No trading approval was created."
    next_milestone = str(result.get("next_evidence_milestone") or "unknown")
    if status == EVIDENCE_MILESTONE_BLOCKED:
        blockers = result.get("blockers") or ["evidence milestone blocked"]
        return f"Evidence milestone blocked at {next_milestone}: " + "; ".join(str(item) for item in blockers)
    return f"Next Forex evidence milestone: {next_milestone}. No trading approval was created."


def _result(
    *,
    status: str,
    completed: list[str],
    blocked: list[str],
    incomplete: list[str],
    next_milestone: str,
    blockers: list[str],
) -> dict[str, Any]:
    remaining = [milestone for milestone in MILESTONE_ORDER if milestone not in completed]
    next_packet = NEXT_PACKET_BY_MILESTONE.get(next_milestone, "AIOS-FOREX-OWNER-COMMIT-REVIEW-V1")
    return {
        "engine_version": EVIDENCE_MILESTONE_SELECTOR_VERSION,
        "status": status,
        "completed_evidence_milestones": list(completed),
        "blocked_evidence_milestones": list(blocked),
        "incomplete_evidence_milestones": list(incomplete),
        "next_evidence_milestone": next_milestone,
        "next_safe_packet": next_packet,
        "remaining_evidence_milestones": remaining,
        "blockers": list(blockers),
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
        "final_closure_status",
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
    "EVIDENCE_MILESTONE_BLOCKED",
    "EVIDENCE_MILESTONE_COMPLETE",
    "EVIDENCE_MILESTONE_CONTINUE",
    "EVIDENCE_MILESTONE_SELECTOR_VERSION",
    "MILESTONE_ORDER",
    "build_sample_evidence_results",
    "result_to_jsonable_dict",
    "result_to_operator_text",
    "select_evidence_milestone",
]
