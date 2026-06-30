"""Supervised demo evidence review contract for AIOS Forex."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


PACKET_ID = "PKT-FOREX-SUPERVISED-DEMO-EVIDENCE-REVIEW-V1"
MODULE_NAME = "forex_supervised_demo_evidence_review_v1"

CURRENT_STAGE = "demo_evidence_review"
RUNTIME_MODE_DRY_RUN = "dry_run"

DEMO_ORDER_EVIDENCE_MISSING = "DEMO_ORDER_EVIDENCE_MISSING"
DEMO_ORDER_NOT_CREATED = "DEMO_ORDER_NOT_CREATED"
REDACTION_REVIEW_REQUIRED = "REDACTION_REVIEW_REQUIRED"
PROTECTED_BOUNDARY_VIOLATION = "PROTECTED_BOUNDARY_VIOLATION"
SUPERVISED_DEMO_EVIDENCE_CLEAN = "SUPERVISED_DEMO_EVIDENCE_CLEAN"

NEXT_STAGE_REVIEW_DEMO_EVIDENCE = "demo_evidence_review"
NEXT_STAGE_OWNER_REVIEW = "stop_and_owner_review"
NEXT_STAGE_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL = "owner_micro_live_exception_approval"


@dataclass(frozen=True)
class SupervisedDemoEvidenceReviewInput:
    supervised_demo_order_attempted: bool
    supervised_demo_order_success: bool
    order_status: str
    order_status_code: int
    demo_order_execution: bool
    live_order_execution: bool
    money_movement: bool
    broker_api_called: bool
    redaction_verified: bool
    max_one_order_verified: bool
    state_report_present: bool
    order_endpoint_redacted: bool
    token_redacted: bool
    account_id_redacted: bool
    scheduler_started: bool
    daemon_started: bool
    webhook_started: bool


@dataclass(frozen=True)
class SupervisedDemoEvidenceReviewResult:
    evidence_status: str
    current_stage: str
    next_stage: str
    blockers: list[str]
    safe_next_action: str
    supervised_demo_order_attempted: bool
    supervised_demo_order_success: bool
    order_status: str
    order_status_code: int
    demo_order_execution: bool
    live_order_execution: bool
    money_movement: bool
    broker_api_called: bool
    redaction_verified: bool
    max_one_order_verified: bool
    state_report_present: bool
    order_endpoint_redacted: bool
    token_redacted: bool
    account_id_redacted: bool
    scheduler_started: bool
    daemon_started: bool
    webhook_started: bool


def build_default_input() -> SupervisedDemoEvidenceReviewInput:
    return SupervisedDemoEvidenceReviewInput(
        supervised_demo_order_attempted=True,
        supervised_demo_order_success=True,
        order_status="created",
        order_status_code=201,
        demo_order_execution=True,
        live_order_execution=False,
        money_movement=False,
        broker_api_called=True,
        redaction_verified=True,
        max_one_order_verified=True,
        state_report_present=True,
        order_endpoint_redacted=True,
        token_redacted=True,
        account_id_redacted=True,
        scheduler_started=False,
        daemon_started=False,
        webhook_started=False,
    )


def evaluate_supervised_demo_evidence_review_v1(
    input_data: SupervisedDemoEvidenceReviewInput,
) -> SupervisedDemoEvidenceReviewResult:
    if _has_protected_boundary_flags(input_data):
        return _result(
            evidence_status=PROTECTED_BOUNDARY_VIOLATION,
            blockers=_protected_boundary_blockers(input_data),
            next_stage=NEXT_STAGE_OWNER_REVIEW,
            safe_next_action=_safe_next_action(PROTECTED_BOUNDARY_VIOLATION),
            input_data=input_data,
        )

    if not input_data.supervised_demo_order_attempted or not input_data.state_report_present:
        return _result(
            evidence_status=DEMO_ORDER_EVIDENCE_MISSING,
            blockers=_missing_order_blockers(input_data),
            next_stage=NEXT_STAGE_REVIEW_DEMO_EVIDENCE,
            safe_next_action=_safe_next_action(DEMO_ORDER_EVIDENCE_MISSING),
            input_data=input_data,
        )

    if (
        not input_data.supervised_demo_order_success
        or _normalize_order_status(input_data.order_status) != "created"
        or input_data.order_status_code != 201
    ):
        return _result(
            evidence_status=DEMO_ORDER_NOT_CREATED,
            blockers=_not_created_order_blockers(input_data),
            next_stage=NEXT_STAGE_REVIEW_DEMO_EVIDENCE,
            safe_next_action=_safe_next_action(DEMO_ORDER_NOT_CREATED),
            input_data=input_data,
        )

    if not _max_one_order_verified(input_data):
        return _result(
            evidence_status=DEMO_ORDER_NOT_CREATED,
            blockers=["max_one_order_verified is False"],
            next_stage=NEXT_STAGE_REVIEW_DEMO_EVIDENCE,
            safe_next_action=_safe_next_action(DEMO_ORDER_NOT_CREATED),
            input_data=input_data,
        )

    if not _redaction_valid(input_data):
        return _result(
            evidence_status=REDACTION_REVIEW_REQUIRED,
            blockers=_redaction_blockers(input_data),
            next_stage=NEXT_STAGE_REVIEW_DEMO_EVIDENCE,
            safe_next_action=_safe_next_action(REDACTION_REVIEW_REQUIRED),
            input_data=input_data,
        )

    return _result(
        evidence_status=SUPERVISED_DEMO_EVIDENCE_CLEAN,
        blockers=[],
        next_stage=NEXT_STAGE_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL,
        safe_next_action=_safe_next_action(SUPERVISED_DEMO_EVIDENCE_CLEAN),
        input_data=input_data,
    )


def input_as_dict(input_data: SupervisedDemoEvidenceReviewInput) -> dict[str, Any]:
    return asdict(input_data)


def result_as_dict(result: SupervisedDemoEvidenceReviewResult) -> dict[str, Any]:
    return asdict(result)


def _normalize_order_status(order_status: str) -> str:
    if not isinstance(order_status, str):
        return ""
    return order_status.strip().lower()


def _has_protected_boundary_flags(
    input_data: SupervisedDemoEvidenceReviewInput,
) -> bool:
    return any(
        (
            input_data.live_order_execution,
            input_data.money_movement,
            input_data.scheduler_started,
            input_data.daemon_started,
            input_data.webhook_started,
        ),
    )


def _protected_boundary_blockers(
    input_data: SupervisedDemoEvidenceReviewInput,
) -> list[str]:
    blockers: list[str] = []
    if input_data.live_order_execution:
        blockers.append("live_order_execution is True")
    if input_data.money_movement:
        blockers.append("money_movement is True")
    if input_data.scheduler_started:
        blockers.append("scheduler_started is True")
    if input_data.daemon_started:
        blockers.append("daemon_started is True")
    if input_data.webhook_started:
        blockers.append("webhook_started is True")
    return blockers


def _missing_order_blockers(input_data: SupervisedDemoEvidenceReviewInput) -> list[str]:
    blockers: list[str] = []
    if not input_data.supervised_demo_order_attempted:
        blockers.append("supervised_demo_order_attempted is False")
    if not input_data.state_report_present:
        blockers.append("state_report_present is False")
    return blockers


def _not_created_order_blockers(
    input_data: SupervisedDemoEvidenceReviewInput,
) -> list[str]:
    blockers: list[str] = []
    if not input_data.supervised_demo_order_success:
        blockers.append("supervised_demo_order_success is False")
    if _normalize_order_status(input_data.order_status) != "created":
        blockers.append("order_status is not created")
    if input_data.order_status_code != 201:
        blockers.append(f"order_status_code is {input_data.order_status_code}")
    return blockers


def _max_one_order_verified(input_data: SupervisedDemoEvidenceReviewInput) -> bool:
    return bool(input_data.max_one_order_verified)


def _redaction_blockers(input_data: SupervisedDemoEvidenceReviewInput) -> list[str]:
    blockers: list[str] = []
    if not input_data.redaction_verified:
        blockers.append("redaction_verified is False")
    if not input_data.order_endpoint_redacted:
        blockers.append("order_endpoint_redacted is False")
    if not input_data.token_redacted:
        blockers.append("token_redacted is False")
    if not input_data.account_id_redacted:
        blockers.append("account_id_redacted is False")
    return blockers


def _redaction_valid(input_data: SupervisedDemoEvidenceReviewInput) -> bool:
    return bool(
        input_data.redaction_verified
        and input_data.order_endpoint_redacted
        and input_data.token_redacted
        and input_data.account_id_redacted,
    )


def _result(
    *,
    evidence_status: str,
    blockers: list[str],
    next_stage: str,
    safe_next_action: str,
    input_data: SupervisedDemoEvidenceReviewInput,
) -> SupervisedDemoEvidenceReviewResult:
    return SupervisedDemoEvidenceReviewResult(
        evidence_status=evidence_status,
        current_stage=CURRENT_STAGE,
        next_stage=next_stage,
        blockers=blockers,
        safe_next_action=safe_next_action,
        supervised_demo_order_attempted=bool(input_data.supervised_demo_order_attempted),
        supervised_demo_order_success=bool(input_data.supervised_demo_order_success),
        order_status=str(input_data.order_status),
        order_status_code=int(input_data.order_status_code),
        demo_order_execution=bool(input_data.demo_order_execution),
        live_order_execution=bool(input_data.live_order_execution),
        money_movement=bool(input_data.money_movement),
        broker_api_called=bool(input_data.broker_api_called),
        redaction_verified=bool(input_data.redaction_verified),
        max_one_order_verified=bool(input_data.max_one_order_verified),
        state_report_present=bool(input_data.state_report_present),
        order_endpoint_redacted=bool(input_data.order_endpoint_redacted),
        token_redacted=bool(input_data.token_redacted),
        account_id_redacted=bool(input_data.account_id_redacted),
        scheduler_started=bool(input_data.scheduler_started),
        daemon_started=bool(input_data.daemon_started),
        webhook_started=bool(input_data.webhook_started),
    )


def _safe_next_action(status: str) -> str:
    return {
        DEMO_ORDER_EVIDENCE_MISSING: (
            "Collect supervised demo order evidence and rerun with state/report evidence "
            "for this review."
        ),
        DEMO_ORDER_NOT_CREATED: (
            "Collect evidence that the demo order was attempted and created once."
        ),
        REDACTION_REVIEW_REQUIRED: (
            "Review redaction fields (endpoint, token, account id) before advancing."
        ),
        PROTECTED_BOUNDARY_VIOLATION: (
            "Stop and clear protected boundary flags before any review decision."
        ),
        SUPERVISED_DEMO_EVIDENCE_CLEAN: (
            "Advance to owner_micro_live_exception_approval."
        ),
    }[status]


__all__ = [
    "PACKET_ID",
    "MODULE_NAME",
    "RUNTIME_MODE_DRY_RUN",
    "CURRENT_STAGE",
    "DEMO_ORDER_EVIDENCE_MISSING",
    "DEMO_ORDER_NOT_CREATED",
    "REDACTION_REVIEW_REQUIRED",
    "PROTECTED_BOUNDARY_VIOLATION",
    "SUPERVISED_DEMO_EVIDENCE_CLEAN",
    "NEXT_STAGE_REVIEW_DEMO_EVIDENCE",
    "NEXT_STAGE_OWNER_REVIEW",
    "NEXT_STAGE_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL",
    "SupervisedDemoEvidenceReviewInput",
    "SupervisedDemoEvidenceReviewResult",
    "build_default_input",
    "evaluate_supervised_demo_evidence_review_v1",
    "input_as_dict",
    "result_as_dict",
]
