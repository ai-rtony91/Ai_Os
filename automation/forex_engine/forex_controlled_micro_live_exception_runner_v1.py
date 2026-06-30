"""Controlled micro-live exception runner contract for AI OS forex."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


PACKET_ID = "AIOS-FOREX-CONTROLLED-MICRO-LIVE-EXCEPTION-RUNNER-V1"
CURRENT_STAGE = "controlled_micro_live_exception_runner"

RUNTIME_MODE_DRY_RUN = "dry_run"
RUNTIME_MODE_OWNER_APPROVED_CONTROLLED_MICRO_LIVE_EXCEPTION = (
    "owner_approved_controlled_micro_live_exception"
)

OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED = (
    "OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED"
)
SUPERVISED_DEMO_EVIDENCE_REQUIRED = "SUPERVISED_DEMO_EVIDENCE_REQUIRED"
OWNER_RUNTIME_LIVE_FLAG_REQUIRED = "OWNER_RUNTIME_LIVE_FLAG_REQUIRED"
PROTECTED_BOUNDARY_VIOLATION = "PROTECTED_BOUNDARY_VIOLATION"
LIVE_RUNTIME_CREDENTIAL_ACCESS_REQUIRED = "LIVE_RUNTIME_CREDENTIAL_ACCESS_REQUIRED"
LIVE_BOUNDARY_REQUIRED = "LIVE_BOUNDARY_REQUIRED"
KILL_SWITCH_BLOCKED = "KILL_SWITCH_BLOCKED"
MICRO_LIVE_CONTROL_BLOCKED = "MICRO_LIVE_CONTROL_BLOCKED"
CONTROLLED_MICRO_LIVE_EXCEPTION_READY = "CONTROLLED_MICRO_LIVE_EXCEPTION_READY"

NEXT_STAGE_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL = "owner_micro_live_exception_approval"
NEXT_STAGE_OWNER_RUN_CONTROLLED_MICRO_LIVE_EXCEPTION = (
    "owner_run_controlled_micro_live_exception"
)
NEXT_STAGE_STOP_AND_OWNER_REVIEW = "stop_and_owner_review"
NEXT_STAGE_OWNER_UNLOCK_BITWARDEN_LIVE_RUNTIME = "owner_unlock_bitwarden_live_runtime"
NEXT_STAGE_REPAIR_LIVE_BOUNDARY = "repair_live_boundary"
NEXT_STAGE_OWNER_REVIEW_REQUIRED = "owner_review_required"
NEXT_STAGE_REPAIR_MICRO_LIVE_CONTROLS = "repair_micro_live_controls"
NEXT_STAGE_OWNER_EXECUTE_ONE_CONTROLLED_MICRO_LIVE_ORDER = (
    "owner_execute_one_controlled_micro_live_order"
)


@dataclass(frozen=True)
class ControlledMicroLiveExceptionInput:
    owner_micro_live_exception_approval_granted: bool
    supervised_demo_evidence_clean: bool
    live_runtime_owner_flag: bool
    bw_session_present: bool
    bitwarden_cli_available: bool
    bitwarden_item_read_success: bool
    live_credential_values_available_to_runtime: bool
    live_endpoint_is_oanda_fxtrade: bool
    environment_is_live: bool
    allowed_mode_is_micro_live_only: bool
    kill_switch_enabled: bool
    kill_switch_triggered: bool
    daily_loss_cap_defined: bool
    daily_loss_within_limit: bool
    trade_risk_cap_defined: bool
    proposed_trade_risk_within_limit: bool
    duplicate_order_guard_enabled: bool
    duplicate_order_detected: bool
    audit_log_enabled: bool
    audit_log_write_success: bool
    max_one_live_order_enforced: bool
    micro_size_only: bool
    instrument: str
    units: int
    side: str
    order_type: str
    stop_loss_defined: bool
    take_profit_defined: bool
    time_in_force: str
    broker_api_called: bool
    bitwarden_cli_called: bool
    credentials_read: bool
    env_file_read: bool
    live_order_execution: bool
    demo_order_execution: bool
    money_movement: bool
    scheduler_started: bool
    daemon_started: bool
    webhook_started: bool


@dataclass(frozen=True)
class ControlledMicroLiveExceptionResult:
    micro_live_status: str
    current_stage: str
    next_stage: str
    blockers: list[str]
    runtime_mode: str
    live_item_ref: str
    order_intent_summary: str
    broker_api_called: bool
    bitwarden_cli_called: bool
    credentials_read: bool
    env_file_read: bool
    live_order_execution: bool
    demo_order_execution: bool
    money_movement: bool
    scheduler_started: bool
    daemon_started: bool
    webhook_started: bool
    safe_next_action: str


def build_default_input() -> ControlledMicroLiveExceptionInput:
    return ControlledMicroLiveExceptionInput(
        owner_micro_live_exception_approval_granted=True,
        supervised_demo_evidence_clean=True,
        live_runtime_owner_flag=False,
        bw_session_present=False,
        bitwarden_cli_available=False,
        bitwarden_item_read_success=False,
        live_credential_values_available_to_runtime=False,
        live_endpoint_is_oanda_fxtrade=True,
        environment_is_live=True,
        allowed_mode_is_micro_live_only=True,
        kill_switch_enabled=True,
        kill_switch_triggered=False,
        daily_loss_cap_defined=True,
        daily_loss_within_limit=True,
        trade_risk_cap_defined=True,
        proposed_trade_risk_within_limit=True,
        duplicate_order_guard_enabled=True,
        duplicate_order_detected=False,
        audit_log_enabled=True,
        audit_log_write_success=True,
        max_one_live_order_enforced=True,
        micro_size_only=True,
        instrument="EUR_USD",
        units=1,
        side="buy",
        order_type="market",
        stop_loss_defined=True,
        take_profit_defined=True,
        time_in_force="FOK",
        broker_api_called=False,
        bitwarden_cli_called=False,
        credentials_read=False,
        env_file_read=False,
        live_order_execution=False,
        demo_order_execution=False,
        money_movement=False,
        scheduler_started=False,
        daemon_started=False,
        webhook_started=False,
    )


def input_as_dict(input_data: ControlledMicroLiveExceptionInput) -> dict[str, Any]:
    return asdict(input_data)


def result_as_dict(
    result: ControlledMicroLiveExceptionResult,
) -> dict[str, Any]:
    return asdict(result)


def evaluate_controlled_micro_live_exception(
    input_data: ControlledMicroLiveExceptionInput,
) -> ControlledMicroLiveExceptionResult:
    blockers: list[str] = []
    runtime_mode = _runtime_mode(input_data.live_runtime_owner_flag)
    current_stage = CURRENT_STAGE
    live_item_ref = "AIOS / OANDA / Live / Broker Runtime"

    if not input_data.owner_micro_live_exception_approval_granted:
        return _result(
            micro_live_status=OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED,
            current_stage=current_stage,
            next_stage=NEXT_STAGE_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL,
            blockers=["owner_micro_live_exception_approval_granted is False"],
            runtime_mode=runtime_mode,
            live_item_ref=live_item_ref,
            order_intent_summary=_order_intent_summary(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(
                OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED,
            ),
        )

    if not input_data.supervised_demo_evidence_clean:
        return _result(
            micro_live_status=SUPERVISED_DEMO_EVIDENCE_REQUIRED,
            current_stage=current_stage,
            next_stage="supervised_demo_evidence_review",
            blockers=["supervised_demo_evidence_clean is False"],
            runtime_mode=runtime_mode,
            live_item_ref=live_item_ref,
            order_intent_summary=_order_intent_summary(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(
                SUPERVISED_DEMO_EVIDENCE_REQUIRED,
            ),
        )

    if runtime_mode == RUNTIME_MODE_DRY_RUN and _protected_boundary_flags(input_data):
        return _result(
            micro_live_status=PROTECTED_BOUNDARY_VIOLATION,
            current_stage=current_stage,
            next_stage=NEXT_STAGE_STOP_AND_OWNER_REVIEW,
            blockers=_protected_boundary_blockers(input_data),
            runtime_mode=runtime_mode,
            live_item_ref=live_item_ref,
            order_intent_summary=_order_intent_summary(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(PROTECTED_BOUNDARY_VIOLATION),
        )

    if not input_data.live_runtime_owner_flag:
        return _result(
            micro_live_status=OWNER_RUNTIME_LIVE_FLAG_REQUIRED,
            current_stage=current_stage,
            next_stage=NEXT_STAGE_OWNER_RUN_CONTROLLED_MICRO_LIVE_EXCEPTION,
            blockers=["live_runtime_owner_flag is False"],
            runtime_mode=runtime_mode,
            live_item_ref=live_item_ref,
            order_intent_summary=_order_intent_summary(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(OWNER_RUNTIME_LIVE_FLAG_REQUIRED),
        )

    if not (
        input_data.bw_session_present
        and input_data.bitwarden_cli_available
        and input_data.bitwarden_item_read_success
        and input_data.live_credential_values_available_to_runtime
    ):
        blockers = []
        if not input_data.bw_session_present:
            blockers.append("bw_session_present is False")
        if not input_data.bitwarden_cli_available:
            blockers.append("bitwarden_cli_available is False")
        if not input_data.bitwarden_item_read_success:
            blockers.append("bitwarden_item_read_success is False")
        if not input_data.live_credential_values_available_to_runtime:
            blockers.append("live_credential_values_available_to_runtime is False")
        return _result(
            micro_live_status=LIVE_RUNTIME_CREDENTIAL_ACCESS_REQUIRED,
            current_stage=current_stage,
            next_stage=NEXT_STAGE_OWNER_UNLOCK_BITWARDEN_LIVE_RUNTIME,
            blockers=blockers,
            runtime_mode=runtime_mode,
            live_item_ref=live_item_ref,
            order_intent_summary=_order_intent_summary(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(LIVE_RUNTIME_CREDENTIAL_ACCESS_REQUIRED),
        )

    if not (
        input_data.live_endpoint_is_oanda_fxtrade
        and input_data.environment_is_live
        and input_data.allowed_mode_is_micro_live_only
    ):
        blockers = []
        if not input_data.live_endpoint_is_oanda_fxtrade:
            blockers.append("live_endpoint_is_oanda_fxtrade is False")
        if not input_data.environment_is_live:
            blockers.append("environment_is_live is False")
        if not input_data.allowed_mode_is_micro_live_only:
            blockers.append("allowed_mode_is_micro_live_only is False")
        return _result(
            micro_live_status=LIVE_BOUNDARY_REQUIRED,
            current_stage=current_stage,
            next_stage=NEXT_STAGE_REPAIR_LIVE_BOUNDARY,
            blockers=blockers,
            runtime_mode=runtime_mode,
            live_item_ref=live_item_ref,
            order_intent_summary=_order_intent_summary(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(LIVE_BOUNDARY_REQUIRED),
        )

    if not input_data.kill_switch_enabled or input_data.kill_switch_triggered:
        blockers = []
        if not input_data.kill_switch_enabled:
            blockers.append("kill_switch_enabled is False")
        if input_data.kill_switch_triggered:
            blockers.append("kill_switch_triggered is True")
        return _result(
            micro_live_status=KILL_SWITCH_BLOCKED,
            current_stage=current_stage,
            next_stage=NEXT_STAGE_OWNER_REVIEW_REQUIRED,
            blockers=blockers,
            runtime_mode=runtime_mode,
            live_item_ref=live_item_ref,
            order_intent_summary=_order_intent_summary(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(KILL_SWITCH_BLOCKED),
        )

    if not _controls_ready(input_data):
        return _result(
            micro_live_status=MICRO_LIVE_CONTROL_BLOCKED,
            current_stage=current_stage,
            next_stage=NEXT_STAGE_REPAIR_MICRO_LIVE_CONTROLS,
            blockers=_control_blockers(input_data),
            runtime_mode=runtime_mode,
            live_item_ref=live_item_ref,
            order_intent_summary=_order_intent_summary(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(MICRO_LIVE_CONTROL_BLOCKED),
        )

    return _result(
        micro_live_status=CONTROLLED_MICRO_LIVE_EXCEPTION_READY,
        current_stage=current_stage,
        next_stage=NEXT_STAGE_OWNER_EXECUTE_ONE_CONTROLLED_MICRO_LIVE_ORDER,
        blockers=[],
        runtime_mode=runtime_mode,
        live_item_ref=live_item_ref,
        order_intent_summary=_order_intent_summary(input_data),
        input_data=input_data,
        safe_next_action=_safe_next_action(CONTROLLED_MICRO_LIVE_EXCEPTION_READY),
    )


def _runtime_mode(is_owner_runtime: bool) -> str:
    return (
        RUNTIME_MODE_OWNER_APPROVED_CONTROLLED_MICRO_LIVE_EXCEPTION
        if is_owner_runtime
        else RUNTIME_MODE_DRY_RUN
    )


def _protected_boundary_flags(input_data: ControlledMicroLiveExceptionInput) -> bool:
    return any(
        (
            input_data.broker_api_called,
            input_data.bitwarden_cli_called,
            input_data.credentials_read,
            input_data.env_file_read,
            input_data.live_order_execution,
            input_data.demo_order_execution,
            input_data.money_movement,
            input_data.scheduler_started,
            input_data.daemon_started,
            input_data.webhook_started,
        ),
    )


def _protected_boundary_blockers(
    input_data: ControlledMicroLiveExceptionInput,
) -> list[str]:
    blockers: list[str] = []
    if input_data.broker_api_called:
        blockers.append("broker_api_called is True")
    if input_data.bitwarden_cli_called:
        blockers.append("bitwarden_cli_called is True")
    if input_data.credentials_read:
        blockers.append("credentials_read is True")
    if input_data.env_file_read:
        blockers.append("env_file_read is True")
    if input_data.live_order_execution:
        blockers.append("live_order_execution is True")
    if input_data.demo_order_execution:
        blockers.append("demo_order_execution is True")
    if input_data.money_movement:
        blockers.append("money_movement is True")
    if input_data.scheduler_started:
        blockers.append("scheduler_started is True")
    if input_data.daemon_started:
        blockers.append("daemon_started is True")
    if input_data.webhook_started:
        blockers.append("webhook_started is True")
    return blockers


def _controls_ready(input_data: ControlledMicroLiveExceptionInput) -> bool:
    return (
        input_data.daily_loss_cap_defined
        and input_data.daily_loss_within_limit
        and input_data.trade_risk_cap_defined
        and input_data.proposed_trade_risk_within_limit
        and input_data.duplicate_order_guard_enabled
        and not input_data.duplicate_order_detected
        and input_data.audit_log_enabled
        and input_data.audit_log_write_success
        and input_data.max_one_live_order_enforced
        and input_data.micro_size_only
        and input_data.stop_loss_defined
        and input_data.take_profit_defined
    )


def _control_blockers(input_data: ControlledMicroLiveExceptionInput) -> list[str]:
    blockers: list[str] = []
    if not input_data.daily_loss_cap_defined:
        blockers.append("daily_loss_cap_defined is False")
    if not input_data.daily_loss_within_limit:
        blockers.append("daily_loss_within_limit is False")
    if not input_data.trade_risk_cap_defined:
        blockers.append("trade_risk_cap_defined is False")
    if not input_data.proposed_trade_risk_within_limit:
        blockers.append("proposed_trade_risk_within_limit is False")
    if not input_data.duplicate_order_guard_enabled:
        blockers.append("duplicate_order_guard_enabled is False")
    if input_data.duplicate_order_detected:
        blockers.append("duplicate_order_detected is True")
    if not input_data.audit_log_enabled:
        blockers.append("audit_log_enabled is False")
    if not input_data.audit_log_write_success:
        blockers.append("audit_log_write_success is False")
    if not input_data.max_one_live_order_enforced:
        blockers.append("max_one_live_order_enforced is False")
    if not input_data.micro_size_only:
        blockers.append("micro_size_only is False")
    if not input_data.stop_loss_defined:
        blockers.append("stop_loss_defined is False")
    if not input_data.take_profit_defined:
        blockers.append("take_profit_defined is False")
    return blockers


def _order_intent_summary(input_data: ControlledMicroLiveExceptionInput) -> str:
    return (
        f"instrument={input_data.instrument}, units={input_data.units}, "
        f"side={input_data.side}, order_type={input_data.order_type}, "
        f"time_in_force={input_data.time_in_force}"
    )


def _result(
    *,
    micro_live_status: str,
    current_stage: str,
    next_stage: str,
    blockers: list[str],
    runtime_mode: str,
    live_item_ref: str,
    order_intent_summary: str,
    input_data: ControlledMicroLiveExceptionInput,
    safe_next_action: str,
) -> ControlledMicroLiveExceptionResult:
    return ControlledMicroLiveExceptionResult(
        micro_live_status=micro_live_status,
        current_stage=current_stage,
        next_stage=next_stage,
        blockers=blockers,
        runtime_mode=runtime_mode,
        live_item_ref=live_item_ref,
        order_intent_summary=order_intent_summary,
        broker_api_called=bool(input_data.broker_api_called),
        bitwarden_cli_called=bool(input_data.bitwarden_cli_called),
        credentials_read=bool(input_data.credentials_read),
        env_file_read=bool(input_data.env_file_read),
        live_order_execution=False,
        demo_order_execution=False,
        money_movement=False,
        scheduler_started=False,
        daemon_started=False,
        webhook_started=False,
        safe_next_action=safe_next_action,
    )


def _safe_next_action(status: str) -> str:
    return {
        OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED: (
            "Collect owner micro-live approval grant from previous lane output."
        ),
        SUPERVISED_DEMO_EVIDENCE_REQUIRED: (
            "Repair supervised demo evidence and rerun this packet."
        ),
        OWNER_RUNTIME_LIVE_FLAG_REQUIRED: (
            "Run this packet with --owner-approved-controlled-micro-live-exception."
        ),
        LIVE_RUNTIME_CREDENTIAL_ACCESS_REQUIRED: (
            "Resolve BW_SESSION, Bitwarden CLI availability, and live runtime credentials."
        ),
        LIVE_BOUNDARY_REQUIRED: (
            "Use OANDA live fxtrade endpoint, live environment, "
            "and controlled_micro_live_exception_only mode."
        ),
        KILL_SWITCH_BLOCKED: (
            "Owner must clear kill-switch or gate review before proceeding."
        ),
        PROTECTED_BOUNDARY_VIOLATION: "Stop and repair protected-boundary flags.",
        MICRO_LIVE_CONTROL_BLOCKED: (
            "Repair daily loss, trade risk, duplicate order guard, audit log, "
            "max-one-order, micro-size, SL/TP control blockers."
        ),
        CONTROLLED_MICRO_LIVE_EXCEPTION_READY: (
            "Execute at most one owner-run controlled micro-live OANDA order."
        ),
    }.get(status, "Review packet state and repair blockers.")


__all__ = [
    "ControlledMicroLiveExceptionInput",
    "ControlledMicroLiveExceptionResult",
    "evaluate_controlled_micro_live_exception",
    "build_default_input",
    "input_as_dict",
    "result_as_dict",
    "PACKET_ID",
    "CURRENT_STAGE",
    "RUNTIME_MODE_DRY_RUN",
    "RUNTIME_MODE_OWNER_APPROVED_CONTROLLED_MICRO_LIVE_EXCEPTION",
    "OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED",
    "SUPERVISED_DEMO_EVIDENCE_REQUIRED",
    "OWNER_RUNTIME_LIVE_FLAG_REQUIRED",
    "PROTECTED_BOUNDARY_VIOLATION",
    "LIVE_RUNTIME_CREDENTIAL_ACCESS_REQUIRED",
    "LIVE_BOUNDARY_REQUIRED",
    "KILL_SWITCH_BLOCKED",
    "MICRO_LIVE_CONTROL_BLOCKED",
    "CONTROLLED_MICRO_LIVE_EXCEPTION_READY",
    "NEXT_STAGE_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL",
    "NEXT_STAGE_OWNER_RUN_CONTROLLED_MICRO_LIVE_EXCEPTION",
    "NEXT_STAGE_STOP_AND_OWNER_REVIEW",
    "NEXT_STAGE_OWNER_UNLOCK_BITWARDEN_LIVE_RUNTIME",
    "NEXT_STAGE_REPAIR_LIVE_BOUNDARY",
    "NEXT_STAGE_OWNER_REVIEW_REQUIRED",
    "NEXT_STAGE_REPAIR_MICRO_LIVE_CONTROLS",
    "NEXT_STAGE_OWNER_EXECUTE_ONE_CONTROLLED_MICRO_LIVE_ORDER",
]
