"""Owner-facing Vacation Mode handoff for AIOS Forex."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.forex_vacation_mode_entry_authority_gate_v1 import (
    ENTRY_AUTHORITY_READY_FOR_OWNER_REVIEW,
    base_hard_false_fields,
)
from automation.forex_engine.forex_vacation_mode_exit_authority_gate_v1 import (
    EXIT_AUTHORITY_HOLD_ALLOWED,
)
from automation.forex_engine.forex_vacation_mode_position_supervisor_v1 import (
    POSITION_SUPERVISION_HOLD,
)
from automation.forex_engine.forex_vacation_mode_release_candidate_scorecard_v1 import (
    SCORECARD_READY_FOR_CONTROL_PLANE_REVIEW,
)

SCHEMA = "AIOS_FOREX_VACATION_MODE_OWNER_HANDOFF_V1"
MODE = "READ_ONLY_METADATA_ONLY_VACATION_MODE_OWNER_HANDOFF"

OWNER_HANDOFF_READY = "OWNER_HANDOFF_READY"
OWNER_HANDOFF_BLOCKED_BY_ENTRY = "OWNER_HANDOFF_BLOCKED_BY_ENTRY"
OWNER_HANDOFF_BLOCKED_BY_SUPERVISION = "OWNER_HANDOFF_BLOCKED_BY_SUPERVISION"
OWNER_HANDOFF_BLOCKED_BY_EXIT = "OWNER_HANDOFF_BLOCKED_BY_EXIT"
OWNER_HANDOFF_BLOCKED_BY_SCORECARD = "OWNER_HANDOFF_BLOCKED_BY_SCORECARD"
OWNER_HANDOFF_BLOCKED_BY_ALERTING = "OWNER_HANDOFF_BLOCKED_BY_ALERTING"
OWNER_HANDOFF_BLOCKED_BY_SAFETY = "OWNER_HANDOFF_BLOCKED_BY_SAFETY"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

REQUIRED_SECTIONS = (
    "entry_result",
    "supervisor_result",
    "exit_result",
    "scorecard_result",
    "owner_alert_state",
    "safety_policy",
)


def evaluate_forex_vacation_mode_owner_handoff_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an owner-facing status summary without granting authority."""

    source = _mapping(payload)
    if not source:
        return _result(INCOMPLETE_INPUTS, False, ("payload_missing",), source)
    missing = _missing_sections(source, REQUIRED_SECTIONS)
    if missing:
        return _result(INCOMPLETE_INPUTS, False, missing, source)

    entry = _mapping(source.get("entry_result"))
    supervisor = _mapping(source.get("supervisor_result"))
    exit_result = _mapping(source.get("exit_result"))
    scorecard = _mapping(source.get("scorecard_result"))
    alert = _mapping(source.get("owner_alert_state"))
    safety = _mapping(source.get("safety_policy"))

    safety_blockers = _safety_blockers(safety)
    if safety_blockers:
        return _result(OWNER_HANDOFF_BLOCKED_BY_SAFETY, False, safety_blockers, source)
    if alert.get("alerting_safe") is not True or alert.get("owner_visible") is not True:
        return _result(
            OWNER_HANDOFF_BLOCKED_BY_ALERTING,
            False,
            ("owner_alert_state_not_safe",),
            source,
        )
    if entry.get("status") != ENTRY_AUTHORITY_READY_FOR_OWNER_REVIEW:
        return _result(OWNER_HANDOFF_BLOCKED_BY_ENTRY, False, ("entry_not_ready",), source)
    if supervisor.get("status") != POSITION_SUPERVISION_HOLD:
        return _result(
            OWNER_HANDOFF_BLOCKED_BY_SUPERVISION,
            False,
            ("supervision_not_hold",),
            source,
        )
    if exit_result.get("status") != EXIT_AUTHORITY_HOLD_ALLOWED:
        return _result(OWNER_HANDOFF_BLOCKED_BY_EXIT, False, ("exit_not_hold",), source)
    if scorecard.get("status") != SCORECARD_READY_FOR_CONTROL_PLANE_REVIEW:
        return _result(
            OWNER_HANDOFF_BLOCKED_BY_SCORECARD,
            False,
            ("scorecard_not_ready_for_control_plane_review",),
            source,
        )
    return _result(OWNER_HANDOFF_READY, True, (), source)


def _result(
    status: str,
    ready: bool,
    blockers: Sequence[str],
    source: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "ready": ready,
        "metadata_only": True,
        "read_only": True,
        "current_phase": "owner_handoff",
        "owner_next_action": _next_action(status),
        "owner_visible_blockers": _unique(blockers),
        "evidence_required": (
            "sanitized_policy_evidence",
            "sanitized_control_plane_evidence",
            "owner_review_record",
        ),
        "no_live_execution_statement": "No live execution occurred in this module.",
        "no_profit_guarantee_statement": "No profit is guaranteed.",
        "legal_compliance_statement": "Legal/compliance review is not complete.",
        "play_store_statement": "AIOS Forex is not Play Store ready.",
        "sell_ready_statement": "AIOS Forex is not sale-cleared.",
        "source_sections_seen": sorted(str(key) for key in source.keys()),
        **base_hard_false_fields(),
    }


def _safety_blockers(safety: Mapping[str, Any]) -> tuple[str, ...]:
    required = (
        "metadata_only",
        "no_live_execution",
        "no_profit_guarantee",
        "legal_compliance_not_complete",
        "not_play_store_ready",
        "not_sell_ready",
    )
    return tuple(f"{field}_required_true" for field in required if safety.get(field) is not True)


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
    if status == OWNER_HANDOFF_READY:
        return "Owner may review the Vacation Mode metadata handoff; no execution occurred."
    return "Repair handoff blockers before owner review."


__all__ = [
    "OWNER_HANDOFF_READY",
    "OWNER_HANDOFF_BLOCKED_BY_ENTRY",
    "OWNER_HANDOFF_BLOCKED_BY_SUPERVISION",
    "OWNER_HANDOFF_BLOCKED_BY_EXIT",
    "OWNER_HANDOFF_BLOCKED_BY_SCORECARD",
    "OWNER_HANDOFF_BLOCKED_BY_ALERTING",
    "OWNER_HANDOFF_BLOCKED_BY_SAFETY",
    "INCOMPLETE_INPUTS",
    "evaluate_forex_vacation_mode_owner_handoff_v1",
]
