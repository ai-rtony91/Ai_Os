"""Utilities for counting supervised demo evidence in Flow 2.

This module is intentionally self-contained and standard-library only. It does not
perform I/O, networking, broker interactions, or order/credential handling.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


EVIDENCE_NOT_STARTED = "EVIDENCE_NOT_STARTED"
EVIDENCE_IN_PROGRESS = "EVIDENCE_IN_PROGRESS"
EVIDENCE_READY_FOR_REVIEW = "EVIDENCE_READY_FOR_REVIEW"
EVIDENCE_BLOCKED = "EVIDENCE_BLOCKED"

FLOW2_READY_FOR_REVIEW_ACTION = "OPEN_OWNER_SUPERVISED_DEMO_REVIEW"
FLOW2_CONTINUE_CAPTURE_ACTION = "CONTINUE_SUPERVISED_DEMO_EVIDENCE_CAPTURE"
FLOW2_FIRST_CAPTURE_ACTION = "CAPTURE_FIRST_SUPERVISED_DEMO_EVIDENCE_ITEM"
FLOW2_RESOLVE_BLOCKERS_ACTION = "RESOLVE_EVIDENCE_BLOCKERS"


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    label: str
    captured: bool
    blocker: str = ""
    sanitized_reference: str = ""


@dataclass(frozen=True)
class EvidenceCountdownResult:
    flow_id: str
    status: str
    required_evidence_count: int
    captured_evidence_count: int
    remaining_evidence_count: int
    captured_evidence_ids: tuple[str, ...]
    missing_evidence_ids: tuple[str, ...]
    blockers: tuple[str, ...]
    next_action: str

    def to_dict(self) -> dict[str, object]:
        return {
            "flow_id": self.flow_id,
            "status": self.status,
            "required_evidence_count": self.required_evidence_count,
            "captured_evidence_count": self.captured_evidence_count,
            "remaining_evidence_count": self.remaining_evidence_count,
            "captured_evidence_ids": list(self.captured_evidence_ids),
            "missing_evidence_ids": list(self.missing_evidence_ids),
            "blockers": list(self.blockers),
            "next_action": self.next_action,
        }


def build_default_flow2_required_evidence() -> tuple[EvidenceItem, ...]:
    return (
        EvidenceItem(
            evidence_id="broker_connection_readiness_sanitized",
            label="Broker connection readiness (sanitized)",
            captured=False,
            sanitized_reference="",
        ),
        EvidenceItem(
            evidence_id="supervised_demo_trade_plan",
            label="Supervised demo trade plan",
            captured=False,
            sanitized_reference="",
        ),
        EvidenceItem(
            evidence_id="risk_controls_snapshot",
            label="Risk controls snapshot",
            captured=False,
            sanitized_reference="",
        ),
        EvidenceItem(
            evidence_id="kill_switch_state",
            label="Kill-switch state",
            captured=False,
            sanitized_reference="",
        ),
        EvidenceItem(
            evidence_id="demo_execution_transcript_sanitized",
            label="Demo execution transcript (sanitized)",
            captured=False,
            sanitized_reference="",
        ),
        EvidenceItem(
            evidence_id="post_trade_pl_capture_sanitized",
            label="Post-trade P&L capture (sanitized)",
            captured=False,
            sanitized_reference="",
        ),
        EvidenceItem(
            evidence_id="evidence_quality_review",
            label="Evidence quality review",
            captured=False,
            sanitized_reference="",
        ),
        EvidenceItem(
            evidence_id="owner_review_handoff",
            label="Owner review handoff",
            captured=False,
            sanitized_reference="",
        ),
    )


def capture_flow2_supervised_demo_evidence_countdown(
    evidence_items: Iterable[EvidenceItem] | None = None,
    *,
    flow_id: str = "flow2_supervised_demo",
) -> EvidenceCountdownResult:
    items = tuple(evidence_items) if evidence_items is not None else build_default_flow2_required_evidence()

    captured_ids = tuple(item.evidence_id for item in items if item.captured)
    missing_evidence_ids = tuple(item.evidence_id for item in items if not item.captured)
    blockers = tuple(item.blocker for item in items if item.blocker)

    required_evidence_count = len(items)
    captured_evidence_count = len(captured_ids)
    remaining_evidence_count = required_evidence_count - captured_evidence_count

    status = _derive_evidence_status(
        required_evidence_count=required_evidence_count,
        captured_evidence_count=captured_evidence_count,
        blockers=blockers,
    )
    next_action = _derive_next_action(status)

    return EvidenceCountdownResult(
        flow_id=flow_id,
        status=status,
        required_evidence_count=required_evidence_count,
        captured_evidence_count=captured_evidence_count,
        remaining_evidence_count=remaining_evidence_count,
        captured_evidence_ids=captured_ids,
        missing_evidence_ids=missing_evidence_ids,
        blockers=blockers,
        next_action=next_action,
    )


def _derive_evidence_status(
    *,
    required_evidence_count: int,
    captured_evidence_count: int,
    blockers: tuple[str, ...],
) -> str:
    if blockers:
        return EVIDENCE_BLOCKED
    if captured_evidence_count == 0:
        return EVIDENCE_NOT_STARTED
    if captured_evidence_count < required_evidence_count:
        return EVIDENCE_IN_PROGRESS
    return EVIDENCE_READY_FOR_REVIEW


def _derive_next_action(status: str) -> str:
    if status == EVIDENCE_NOT_STARTED:
        return FLOW2_FIRST_CAPTURE_ACTION
    if status == EVIDENCE_IN_PROGRESS:
        return FLOW2_CONTINUE_CAPTURE_ACTION
    if status == EVIDENCE_READY_FOR_REVIEW:
        return FLOW2_READY_FOR_REVIEW_ACTION
    return FLOW2_RESOLVE_BLOCKERS_ACTION
