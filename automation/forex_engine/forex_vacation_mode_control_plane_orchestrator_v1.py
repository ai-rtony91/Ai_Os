"""Top-level metadata-only Vacation Mode control-plane orchestrator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.forex_vacation_mode_entry_authority_gate_v1 import (
    ENTRY_AUTHORITY_READY_FOR_OWNER_REVIEW,
    ENTRY_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY,
    ENTRY_BLOCKED_BY_PRODUCT_POLICY,
    base_hard_false_fields,
    evaluate_forex_vacation_mode_entry_authority_gate_v1,
)
from automation.forex_engine.forex_vacation_mode_exit_authority_gate_v1 import (
    EXIT_AUTHORITY_HOLD_ALLOWED,
    evaluate_forex_vacation_mode_exit_authority_gate_v1,
)
from automation.forex_engine.forex_vacation_mode_owner_handoff_v1 import (
    OWNER_HANDOFF_READY,
    evaluate_forex_vacation_mode_owner_handoff_v1,
)
from automation.forex_engine.forex_vacation_mode_position_supervisor_v1 import (
    POSITION_SUPERVISION_HOLD,
    evaluate_forex_vacation_mode_position_supervisor_v1,
)
from automation.forex_engine.forex_vacation_mode_release_candidate_scorecard_v1 import (
    SCORECARD_BLOCKED_BY_EXTERNAL_EVIDENCE,
    SCORECARD_BLOCKED_BY_LEGAL_COMPLIANCE,
    SCORECARD_READY_FOR_CONTROL_PLANE_REVIEW,
    evaluate_forex_vacation_mode_release_candidate_scorecard_v1,
)

SCHEMA = "AIOS_FOREX_VACATION_MODE_CONTROL_PLANE_ORCHESTRATOR_V1"
MODE = "READ_ONLY_METADATA_ONLY_VACATION_MODE_CONTROL_PLANE_ORCHESTRATOR"

VACATION_MODE_CONTROL_PLANE_READY_FOR_OWNER_REVIEW = (
    "VACATION_MODE_CONTROL_PLANE_READY_FOR_OWNER_REVIEW"
)
VACATION_MODE_BLOCKED_BY_PRODUCT_POLICY = "VACATION_MODE_BLOCKED_BY_PRODUCT_POLICY"
VACATION_MODE_BLOCKED_BY_ENTRY_AUTHORITY = "VACATION_MODE_BLOCKED_BY_ENTRY_AUTHORITY"
VACATION_MODE_BLOCKED_BY_POSITION_SUPERVISION = "VACATION_MODE_BLOCKED_BY_POSITION_SUPERVISION"
VACATION_MODE_BLOCKED_BY_EXIT_AUTHORITY = "VACATION_MODE_BLOCKED_BY_EXIT_AUTHORITY"
VACATION_MODE_BLOCKED_BY_OWNER_HANDOFF = "VACATION_MODE_BLOCKED_BY_OWNER_HANDOFF"
VACATION_MODE_BLOCKED_BY_RELEASE_SCORECARD = "VACATION_MODE_BLOCKED_BY_RELEASE_SCORECARD"
VACATION_MODE_BLOCKED_BY_EXTERNAL_BROKER_EVIDENCE = (
    "VACATION_MODE_BLOCKED_BY_EXTERNAL_BROKER_EVIDENCE"
)
VACATION_MODE_BLOCKED_BY_LEGAL_COMPLIANCE = "VACATION_MODE_BLOCKED_BY_LEGAL_COMPLIANCE"
VACATION_MODE_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY = (
    "VACATION_MODE_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY"
)
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

REQUIRED_SECTIONS = (
    "entry_payload",
    "supervisor_payload",
    "exit_payload",
    "scorecard_payload",
    "owner_alert_state",
    "handoff_safety_policy",
)


def evaluate_forex_vacation_mode_control_plane_orchestrator_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate all metadata-only Vacation Mode control-plane gates."""

    source = _mapping(payload)
    if not source:
        return _result(INCOMPLETE_INPUTS, False, ("payload_missing",), {})
    missing = _missing_sections(source, REQUIRED_SECTIONS)
    if missing:
        return _result(INCOMPLETE_INPUTS, False, missing, {})

    entry = evaluate_forex_vacation_mode_entry_authority_gate_v1(
        dict(_mapping(source.get("entry_payload")))
    )
    supervisor = evaluate_forex_vacation_mode_position_supervisor_v1(
        dict(_mapping(source.get("supervisor_payload")))
    )
    exit_result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        dict(_mapping(source.get("exit_payload")))
    )
    scorecard = evaluate_forex_vacation_mode_release_candidate_scorecard_v1(
        dict(_mapping(source.get("scorecard_payload")))
    )
    handoff = evaluate_forex_vacation_mode_owner_handoff_v1(
        {
            "entry_result": entry,
            "supervisor_result": supervisor,
            "exit_result": exit_result,
            "scorecard_result": scorecard,
            "owner_alert_state": _mapping(source.get("owner_alert_state")),
            "safety_policy": _mapping(source.get("handoff_safety_policy")),
        }
    )

    results = {
        "entry_result": entry,
        "supervisor_result": supervisor,
        "exit_result": exit_result,
        "scorecard_result": scorecard,
        "handoff_result": handoff,
    }

    status, blockers = _final_status(results)
    return _result(
        status,
        status == VACATION_MODE_CONTROL_PLANE_READY_FOR_OWNER_REVIEW,
        blockers,
        results,
    )


def _final_status(results: Mapping[str, Mapping[str, Any]]) -> tuple[str, tuple[str, ...]]:
    entry = results["entry_result"]
    supervisor = results["supervisor_result"]
    exit_result = results["exit_result"]
    scorecard = results["scorecard_result"]
    handoff = results["handoff_result"]

    if entry.get("status") == ENTRY_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY:
        return VACATION_MODE_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY, ("entry_live_boundary",)
    if entry.get("status") == ENTRY_BLOCKED_BY_PRODUCT_POLICY:
        return VACATION_MODE_BLOCKED_BY_PRODUCT_POLICY, ("entry_product_policy",)
    if entry.get("status") != ENTRY_AUTHORITY_READY_FOR_OWNER_REVIEW:
        return VACATION_MODE_BLOCKED_BY_ENTRY_AUTHORITY, ("entry_not_ready",)
    if supervisor.get("status") != POSITION_SUPERVISION_HOLD:
        return VACATION_MODE_BLOCKED_BY_POSITION_SUPERVISION, ("supervision_not_hold",)
    if exit_result.get("status") != EXIT_AUTHORITY_HOLD_ALLOWED:
        return VACATION_MODE_BLOCKED_BY_EXIT_AUTHORITY, ("exit_not_hold",)
    if scorecard.get("status") == SCORECARD_BLOCKED_BY_EXTERNAL_EVIDENCE:
        return VACATION_MODE_BLOCKED_BY_EXTERNAL_BROKER_EVIDENCE, ("scorecard_external_evidence",)
    if scorecard.get("status") == SCORECARD_BLOCKED_BY_LEGAL_COMPLIANCE:
        return VACATION_MODE_BLOCKED_BY_LEGAL_COMPLIANCE, ("scorecard_legal_compliance",)
    if scorecard.get("status") != SCORECARD_READY_FOR_CONTROL_PLANE_REVIEW:
        return VACATION_MODE_BLOCKED_BY_RELEASE_SCORECARD, ("scorecard_not_ready",)
    if handoff.get("status") != OWNER_HANDOFF_READY:
        return VACATION_MODE_BLOCKED_BY_OWNER_HANDOFF, ("handoff_not_ready",)
    return VACATION_MODE_CONTROL_PLANE_READY_FOR_OWNER_REVIEW, ()


def _result(
    status: str,
    ready: bool,
    blockers: Sequence[str],
    results: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "ready": ready,
        "metadata_only": True,
        "read_only": True,
        "final_status": status,
        "exact_blockers": _unique(blockers),
        "owner_next_action": _next_action(status),
        "release_candidate_blockers": _release_blockers(results),
        "module_results": dict(results),
        "control_plane_ready_claimed": ready,
        **base_hard_false_fields(),
    }


def _release_blockers(results: Mapping[str, Any]) -> list[str]:
    if not results:
        return ["inputs_incomplete"]
    blockers: list[str] = []
    for key, result in results.items():
        if isinstance(result, Mapping) and result.get("ready") is not True:
            blockers.append(f"{key}_not_ready")
    blockers.extend(
        [
            "final_release_review_required",
            "owner_legal_compliance_review_required",
            "mobile_packaging_review_required",
        ]
    )
    return _unique(blockers)


def _missing_sections(source: Mapping[str, Any], sections: Sequence[str]) -> tuple[str, ...]:
    return tuple(f"{section}_missing" for section in sections if not _mapping(source.get(section)))


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _next_action(status: str) -> str:
    if status == VACATION_MODE_CONTROL_PLANE_READY_FOR_OWNER_REVIEW:
        return "Owner may review the metadata-only Vacation Mode control plane."
    return "Repair listed Vacation Mode control-plane blockers before owner review."


__all__ = [
    "VACATION_MODE_CONTROL_PLANE_READY_FOR_OWNER_REVIEW",
    "VACATION_MODE_BLOCKED_BY_PRODUCT_POLICY",
    "VACATION_MODE_BLOCKED_BY_ENTRY_AUTHORITY",
    "VACATION_MODE_BLOCKED_BY_POSITION_SUPERVISION",
    "VACATION_MODE_BLOCKED_BY_EXIT_AUTHORITY",
    "VACATION_MODE_BLOCKED_BY_OWNER_HANDOFF",
    "VACATION_MODE_BLOCKED_BY_RELEASE_SCORECARD",
    "VACATION_MODE_BLOCKED_BY_EXTERNAL_BROKER_EVIDENCE",
    "VACATION_MODE_BLOCKED_BY_LEGAL_COMPLIANCE",
    "VACATION_MODE_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY",
    "INCOMPLETE_INPUTS",
    "evaluate_forex_vacation_mode_control_plane_orchestrator_v1",
]
