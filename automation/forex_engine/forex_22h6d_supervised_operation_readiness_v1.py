"""Metadata-only 22h/6d supervised operation readiness evaluator."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from automation.forex_engine.oanda_demo_owner_approved_one_order_protected_runtime_execution_v1 import (
    _bool,
    find_sensitive_data_blockers,
    hard_false_result,
    safety_false_result,
    safety_summary,
    unique,
)


SCHEMA = "AIOS_FOREX_22H6D_SUPERVISED_OPERATION_READINESS_V1"
MODE = "READ_ONLY_METADATA_ONLY_22H6D_SUPERVISED_OPERATION_READINESS"

TWENTY_TWO_HOUR_SIX_DAY_READINESS_PASSED = (
    "TWENTY_TWO_HOUR_SIX_DAY_READINESS_PASSED"
)
TWENTY_TWO_HOUR_SIX_DAY_READINESS_INCOMPLETE = (
    "TWENTY_TWO_HOUR_SIX_DAY_READINESS_INCOMPLETE"
)
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_PACKET_READY = "AIOS_FOREX_COMPLETION_CAMPAIGN_PART2_V1"

READINESS_COMPONENTS = (
    "broker_session_readiness",
    "monitoring_readiness",
    "kill_switch_readiness",
    "post_trade_review_readiness",
    "audit_readiness",
    "capital_planner_readiness",
    "sos_readiness",
    "owner_approval_readiness",
    "credential_boundary_readiness",
    "recovery_readiness",
)


def evaluate_forex_22h6d_supervised_operation_readiness_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Score supervised readiness from sanitized boolean metadata."""

    source = payload if isinstance(payload, Mapping) else {}
    sensitive_data_blockers = find_sensitive_data_blockers(source)
    sensitive_data_detected = bool(sensitive_data_blockers)
    component_scores = _component_scores(source)
    total_score = sum(component_scores.values())
    component_blockers = _component_blockers(component_scores)

    if sensitive_data_detected:
        status = BLOCKED_BY_SENSITIVE_DATA
        blockers = list(sensitive_data_blockers)
    elif not source:
        status = INCOMPLETE_INPUTS
        blockers = ["payload_missing"]
    elif total_score == 100:
        status = TWENTY_TWO_HOUR_SIX_DAY_READINESS_PASSED
        blockers = []
    else:
        status = TWENTY_TWO_HOUR_SIX_DAY_READINESS_INCOMPLETE
        blockers = component_blockers

    readiness_passed = status == TWENTY_TWO_HOUR_SIX_DAY_READINESS_PASSED
    next_best_packet = NEXT_PACKET_READY if readiness_passed else SCHEMA

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "readiness_status": status,
        "readiness_passed": readiness_passed,
        "total_score": total_score,
        "component_scores": component_scores,
        "component_blockers": component_blockers,
        "owner_action_queue": _owner_action_queue(blockers, next_best_packet),
        "next_best_packet": next_best_packet,
        "owner_decision_required": True,
        "approval_token_required": True,
        "read_only": True,
        "metadata_only": True,
        "sensitive_data_detected": sensitive_data_detected,
        "sensitive_data_blockers": list(sensitive_data_blockers),
        "readiness_blockers": unique(blockers),
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "readiness_status": status,
            "readiness_passed": readiness_passed,
            "total_score": total_score,
            "input_redacted": sensitive_data_detected,
            "read_only": True,
            "metadata_only": True,
            **hard_false_result(),
            **safety_false_result(),
        },
        "safety": safety_summary(),
        **hard_false_result(),
        **safety_false_result(),
    }


def _component_scores(source: Mapping[str, Any]) -> dict[str, int]:
    return {
        component: 10 if _bool(source.get(component)) is True else 0
        for component in READINESS_COMPONENTS
    }


def _component_blockers(component_scores: Mapping[str, int]) -> list[str]:
    return [
        f"{component}_missing_or_false"
        for component, score in component_scores.items()
        if score == 0
    ]


def _owner_action_queue(
    blockers: list[str],
    next_best_packet: str,
) -> list[dict[str, Any]]:
    queue = [
        {
            "action_id": f"REVIEW_{component.upper()}",
            "owner_decision_required": True,
            "blocked_by": [f"{component}_missing_or_false"]
            if f"{component}_missing_or_false" in blockers
            else [],
            "next_best_packet": None,
            **hard_false_result(),
            **safety_false_result(),
        }
        for component in READINESS_COMPONENTS
    ]
    queue.append(
        {
            "action_id": "REVIEW_NEXT_PACKET",
            "owner_decision_required": True,
            "blocked_by": list(blockers),
            "next_best_packet": next_best_packet,
            **hard_false_result(),
            **safety_false_result(),
        }
    )
    return queue
