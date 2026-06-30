"""Owner micro-live exception approval grant packet for AIOS Forex."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


PACKET_ID = "PKT-FOREX-OWNER-MICRO-LIVE-EXCEPTION-APPROVAL-GRANT-V1"
MODULE_NAME = "forex_owner_micro_live_exception_approval_grant_v1"

CURRENT_STAGE = "owner_micro_live_exception_approval_grant"
RUNTIME_MODE_DRY_RUN = "dry_run"

PRIOR_GATE_REQUIRED = "PRIOR_GATE_REQUIRED"
SUPERVISED_DEMO_EVIDENCE_REQUIRED = "SUPERVISED_DEMO_EVIDENCE_REQUIRED"
OWNER_MICRO_LIVE_APPROVAL_CONFIRMATION_REQUIRED = (
    "OWNER_MICRO_LIVE_APPROVAL_CONFIRMATION_REQUIRED"
)
OWNER_LIVE_RISK_CONFIRMATION_REQUIRED = "OWNER_LIVE_RISK_CONFIRMATION_REQUIRED"
MICRO_LIVE_CONTROL_CONFIRMATION_REQUIRED = "MICRO_LIVE_CONTROL_CONFIRMATION_REQUIRED"
PROTECTED_BOUNDARY_VIOLATION = "PROTECTED_BOUNDARY_VIOLATION"
OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED = (
    "OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED"
)

NEXT_STAGE_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL = "owner_micro_live_exception_approval"
NEXT_STAGE_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER = (
    "controlled_micro_live_exception_runner"
)
NEXT_STAGE_OWNER_REVIEW = "stop_and_owner_review"


@dataclass(frozen=True)
class OwnerMicroLiveExceptionApprovalGrantInput:
    prior_approval_gate_landed: bool
    supervised_demo_evidence_clean: bool
    supervised_demo_order_created: bool
    demo_order_status_code: int
    owner_micro_live_exception_approval: bool
    owner_understands_live_money_risk: bool
    owner_confirms_micro_size_only: bool
    owner_confirms_max_one_live_order: bool
    owner_confirms_no_autonomous_runtime: bool
    owner_confirms_kill_switch_ready: bool
    owner_confirms_daily_loss_cap_ready: bool
    owner_confirms_trade_risk_cap_ready: bool
    owner_confirms_audit_log_ready: bool
    owner_confirms_future_runner_only: bool
    live_order_execution: bool
    money_movement: bool
    broker_api_called: bool
    bitwarden_cli_called: bool
    credentials_read: bool
    env_file_read: bool
    scheduler_started: bool
    daemon_started: bool
    webhook_started: bool


@dataclass(frozen=True)
class OwnerMicroLiveExceptionApprovalGrantResult:
    owner_approval_status: str
    current_stage: str
    next_stage: str
    blockers: list[str]
    prior_approval_gate_landed: bool
    supervised_demo_evidence_clean: bool
    supervised_demo_order_created: bool
    demo_order_status_code: int
    owner_micro_live_exception_approval: bool
    owner_understands_live_money_risk: bool
    owner_confirms_micro_size_only: bool
    owner_confirms_max_one_live_order: bool
    owner_confirms_no_autonomous_runtime: bool
    owner_confirms_kill_switch_ready: bool
    owner_confirms_daily_loss_cap_ready: bool
    owner_confirms_trade_risk_cap_ready: bool
    owner_confirms_audit_log_ready: bool
    owner_confirms_future_runner_only: bool
    live_order_execution: bool
    money_movement: bool
    broker_api_called: bool
    bitwarden_cli_called: bool
    credentials_read: bool
    env_file_read: bool
    scheduler_started: bool
    daemon_started: bool
    webhook_started: bool
    safe_next_action: str


def build_default_input() -> OwnerMicroLiveExceptionApprovalGrantInput:
    return OwnerMicroLiveExceptionApprovalGrantInput(
        prior_approval_gate_landed=True,
        supervised_demo_evidence_clean=True,
        supervised_demo_order_created=True,
        demo_order_status_code=201,
        owner_micro_live_exception_approval=True,
        owner_understands_live_money_risk=True,
        owner_confirms_micro_size_only=True,
        owner_confirms_max_one_live_order=True,
        owner_confirms_no_autonomous_runtime=True,
        owner_confirms_kill_switch_ready=True,
        owner_confirms_daily_loss_cap_ready=True,
        owner_confirms_trade_risk_cap_ready=True,
        owner_confirms_audit_log_ready=True,
        owner_confirms_future_runner_only=True,
        live_order_execution=False,
        money_movement=False,
        broker_api_called=False,
        bitwarden_cli_called=False,
        credentials_read=False,
        env_file_read=False,
        scheduler_started=False,
        daemon_started=False,
        webhook_started=False,
    )


def evaluate_owner_micro_live_exception_approval_grant_v1(
    input_data: OwnerMicroLiveExceptionApprovalGrantInput,
) -> OwnerMicroLiveExceptionApprovalGrantResult:
    if _has_protected_boundary_flags(input_data):
        return _result(
            owner_approval_status=PROTECTED_BOUNDARY_VIOLATION,
            current_stage=CURRENT_STAGE,
            next_stage=NEXT_STAGE_OWNER_REVIEW,
            blockers=_protected_boundary_blockers(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(PROTECTED_BOUNDARY_VIOLATION),
        )

    if not input_data.prior_approval_gate_landed:
        return _result(
            owner_approval_status=PRIOR_GATE_REQUIRED,
            current_stage=CURRENT_STAGE,
            next_stage=NEXT_STAGE_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL,
            blockers=("prior_approval_gate_landed is False",),
            input_data=input_data,
            safe_next_action=_safe_next_action(PRIOR_GATE_REQUIRED),
        )

    if not _supervised_demo_evidence_ready(input_data):
        return _result(
            owner_approval_status=SUPERVISED_DEMO_EVIDENCE_REQUIRED,
            current_stage=CURRENT_STAGE,
            next_stage=NEXT_STAGE_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL,
            blockers=_supervised_demo_evidence_blockers(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(SUPERVISED_DEMO_EVIDENCE_REQUIRED),
        )

    if not input_data.owner_micro_live_exception_approval:
        return _result(
            owner_approval_status=OWNER_MICRO_LIVE_APPROVAL_CONFIRMATION_REQUIRED,
            current_stage=CURRENT_STAGE,
            next_stage=CURRENT_STAGE,
            blockers=("owner_micro_live_exception_approval is False",),
            input_data=input_data,
            safe_next_action=_safe_next_action(
                OWNER_MICRO_LIVE_APPROVAL_CONFIRMATION_REQUIRED,
            ),
        )

    if not _owner_live_risk_acknowledgments(input_data):
        return _result(
            owner_approval_status=OWNER_LIVE_RISK_CONFIRMATION_REQUIRED,
            current_stage=CURRENT_STAGE,
            next_stage=CURRENT_STAGE,
            blockers=_owner_live_risk_ack_blockers(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(OWNER_LIVE_RISK_CONFIRMATION_REQUIRED),
        )

    if not _micro_live_control_confirmations(input_data):
        return _result(
            owner_approval_status=MICRO_LIVE_CONTROL_CONFIRMATION_REQUIRED,
            current_stage=CURRENT_STAGE,
            next_stage=CURRENT_STAGE,
            blockers=_micro_live_control_blockers(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(
                MICRO_LIVE_CONTROL_CONFIRMATION_REQUIRED,
            ),
        )

    return _result(
        owner_approval_status=OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED,
        current_stage=CURRENT_STAGE,
        next_stage=NEXT_STAGE_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER,
        blockers=tuple(),
        input_data=input_data,
        safe_next_action=_safe_next_action(
            OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED,
        ),
    )


def input_as_dict(input_data: OwnerMicroLiveExceptionApprovalGrantInput) -> dict[str, Any]:
    return asdict(input_data)


def result_as_dict(
    result: OwnerMicroLiveExceptionApprovalGrantResult,
) -> dict[str, Any]:
    return asdict(result)


def _has_protected_boundary_flags(
    input_data: OwnerMicroLiveExceptionApprovalGrantInput,
) -> bool:
    return any(
        (
            input_data.live_order_execution,
            input_data.money_movement,
            input_data.broker_api_called,
            input_data.bitwarden_cli_called,
            input_data.credentials_read,
            input_data.env_file_read,
            input_data.scheduler_started,
            input_data.daemon_started,
            input_data.webhook_started,
        ),
    )


def _protected_boundary_blockers(
    input_data: OwnerMicroLiveExceptionApprovalGrantInput,
) -> tuple[str, ...]:
    blockers: list[str] = []
    if input_data.live_order_execution:
        blockers.append("live_order_execution is True")
    if input_data.money_movement:
        blockers.append("money_movement is True")
    if input_data.broker_api_called:
        blockers.append("broker_api_called is True")
    if input_data.bitwarden_cli_called:
        blockers.append("bitwarden_cli_called is True")
    if input_data.credentials_read:
        blockers.append("credentials_read is True")
    if input_data.env_file_read:
        blockers.append("env_file_read is True")
    if input_data.scheduler_started:
        blockers.append("scheduler_started is True")
    if input_data.daemon_started:
        blockers.append("daemon_started is True")
    if input_data.webhook_started:
        blockers.append("webhook_started is True")
    return tuple(blockers)


def _supervised_demo_evidence_ready(
    input_data: OwnerMicroLiveExceptionApprovalGrantInput,
) -> bool:
    return (
        input_data.supervised_demo_evidence_clean
        and input_data.supervised_demo_order_created
        and input_data.demo_order_status_code == 201
    )


def _supervised_demo_evidence_blockers(
    input_data: OwnerMicroLiveExceptionApprovalGrantInput,
) -> tuple[str, ...]:
    blockers: list[str] = []
    if not input_data.supervised_demo_evidence_clean:
        blockers.append("supervised_demo_evidence_clean is False")
    if not input_data.supervised_demo_order_created:
        blockers.append("supervised_demo_order_created is False")
    if input_data.demo_order_status_code != 201:
        blockers.append(f"demo_order_status_code is {input_data.demo_order_status_code}")
    return tuple(blockers)


def _owner_live_risk_acknowledgments(
    input_data: OwnerMicroLiveExceptionApprovalGrantInput,
) -> bool:
    return (
        input_data.owner_understands_live_money_risk
        and input_data.owner_confirms_kill_switch_ready
        and input_data.owner_confirms_daily_loss_cap_ready
        and input_data.owner_confirms_trade_risk_cap_ready
        and input_data.owner_confirms_audit_log_ready
    )


def _owner_live_risk_ack_blockers(
    input_data: OwnerMicroLiveExceptionApprovalGrantInput,
) -> tuple[str, ...]:
    blockers: list[str] = []
    if not input_data.owner_understands_live_money_risk:
        blockers.append("owner_understands_live_money_risk is False")
    if not input_data.owner_confirms_kill_switch_ready:
        blockers.append("owner_confirms_kill_switch_ready is False")
    if not input_data.owner_confirms_daily_loss_cap_ready:
        blockers.append("owner_confirms_daily_loss_cap_ready is False")
    if not input_data.owner_confirms_trade_risk_cap_ready:
        blockers.append("owner_confirms_trade_risk_cap_ready is False")
    if not input_data.owner_confirms_audit_log_ready:
        blockers.append("owner_confirms_audit_log_ready is False")
    return tuple(blockers)


def _micro_live_control_confirmations(
    input_data: OwnerMicroLiveExceptionApprovalGrantInput,
) -> bool:
    return (
        input_data.owner_confirms_micro_size_only
        and input_data.owner_confirms_max_one_live_order
        and input_data.owner_confirms_no_autonomous_runtime
        and input_data.owner_confirms_future_runner_only
    )


def _micro_live_control_blockers(
    input_data: OwnerMicroLiveExceptionApprovalGrantInput,
) -> tuple[str, ...]:
    blockers: list[str] = []
    if not input_data.owner_confirms_micro_size_only:
        blockers.append("owner_confirms_micro_size_only is False")
    if not input_data.owner_confirms_max_one_live_order:
        blockers.append("owner_confirms_max_one_live_order is False")
    if not input_data.owner_confirms_no_autonomous_runtime:
        blockers.append("owner_confirms_no_autonomous_runtime is False")
    if not input_data.owner_confirms_future_runner_only:
        blockers.append("owner_confirms_future_runner_only is False")
    return tuple(blockers)


def _result(
    *,
    owner_approval_status: str,
    current_stage: str,
    next_stage: str,
    blockers: tuple[str, ...],
    input_data: OwnerMicroLiveExceptionApprovalGrantInput,
    safe_next_action: str,
) -> OwnerMicroLiveExceptionApprovalGrantResult:
    return OwnerMicroLiveExceptionApprovalGrantResult(
        owner_approval_status=owner_approval_status,
        current_stage=current_stage,
        next_stage=next_stage,
        blockers=list(blockers),
        prior_approval_gate_landed=bool(input_data.prior_approval_gate_landed),
        supervised_demo_evidence_clean=bool(input_data.supervised_demo_evidence_clean),
        supervised_demo_order_created=bool(input_data.supervised_demo_order_created),
        demo_order_status_code=int(input_data.demo_order_status_code),
        owner_micro_live_exception_approval=bool(
            input_data.owner_micro_live_exception_approval,
        ),
        owner_understands_live_money_risk=bool(
            input_data.owner_understands_live_money_risk,
        ),
        owner_confirms_micro_size_only=bool(input_data.owner_confirms_micro_size_only),
        owner_confirms_max_one_live_order=bool(
            input_data.owner_confirms_max_one_live_order,
        ),
        owner_confirms_no_autonomous_runtime=bool(
            input_data.owner_confirms_no_autonomous_runtime,
        ),
        owner_confirms_kill_switch_ready=bool(input_data.owner_confirms_kill_switch_ready),
        owner_confirms_daily_loss_cap_ready=bool(
            input_data.owner_confirms_daily_loss_cap_ready,
        ),
        owner_confirms_trade_risk_cap_ready=bool(
            input_data.owner_confirms_trade_risk_cap_ready,
        ),
        owner_confirms_audit_log_ready=bool(input_data.owner_confirms_audit_log_ready),
        owner_confirms_future_runner_only=bool(
            input_data.owner_confirms_future_runner_only,
        ),
        live_order_execution=False,
        money_movement=False,
        broker_api_called=False,
        bitwarden_cli_called=False,
        credentials_read=False,
        env_file_read=False,
        scheduler_started=False,
        daemon_started=False,
        webhook_started=False,
        safe_next_action=safe_next_action,
    )


def _safe_next_action(status: str) -> str:
    return {
        PRIOR_GATE_REQUIRED: (
            "Collect proof that PR #1254 landing is recorded, then rerun "
            "this grant packet."
        ),
        SUPERVISED_DEMO_EVIDENCE_REQUIRED: (
            "Return to supervised demo evidence and resolve missing evidence flags."
        ),
        OWNER_MICRO_LIVE_APPROVAL_CONFIRMATION_REQUIRED: (
            "Collect owner micro-live exception approval and rerun this grant."
        ),
        OWNER_LIVE_RISK_CONFIRMATION_REQUIRED: (
            "Collect owner micro-live real-money risk acknowledgments."
        ),
        MICRO_LIVE_CONTROL_CONFIRMATION_REQUIRED: (
            "Collect micro-live control confirmations for size, one-order, and runtime."
        ),
        PROTECTED_BOUNDARY_VIOLATION: (
            "Stop and clear protected boundary flags before this grant can proceed."
        ),
        OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED: (
            "Advance to controlled_micro_live_exception_runner."
        ),
    }[status]


__all__ = [
    "OwnerMicroLiveExceptionApprovalGrantInput",
    "OwnerMicroLiveExceptionApprovalGrantResult",
    "PACKET_ID",
    "MODULE_NAME",
    "CURRENT_STAGE",
    "RUNTIME_MODE_DRY_RUN",
    "PRIOR_GATE_REQUIRED",
    "SUPERVISED_DEMO_EVIDENCE_REQUIRED",
    "OWNER_MICRO_LIVE_APPROVAL_CONFIRMATION_REQUIRED",
    "OWNER_LIVE_RISK_CONFIRMATION_REQUIRED",
    "MICRO_LIVE_CONTROL_CONFIRMATION_REQUIRED",
    "PROTECTED_BOUNDARY_VIOLATION",
    "OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED",
    "NEXT_STAGE_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL",
    "NEXT_STAGE_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER",
    "NEXT_STAGE_OWNER_REVIEW",
    "build_default_input",
    "evaluate_owner_micro_live_exception_approval_grant_v1",
    "input_as_dict",
    "result_as_dict",
]
