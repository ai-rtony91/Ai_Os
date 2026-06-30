"""Integrated Forex live execution program contract for governance-only lane progression."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

PACKET_ID = "PKT-FOREX-LIVE-EXECUTION-PROGRAM-V1"
MODULE_NAME = "forex_live_execution_program_v1"
RUNTIME_MODE_DRY_RUN = "dry_run"

BROKER_RUNTIME_READ_ONLY_AUTH_REQUIRED = "BROKER_RUNTIME_READ_ONLY_AUTH_REQUIRED"
EXECUTION_CONTROL_STACK_REQUIRED = "EXECUTION_CONTROL_STACK_REQUIRED"
EXECUTION_CONTROL_STACK_NOT_READY = "EXECUTION_CONTROL_STACK_NOT_READY"
PROTECTED_BOUNDARY_VIOLATION = "PROTECTED_BOUNDARY_VIOLATION"
EXECUTION_CONTROLS_INCOMPLETE = "EXECUTION_CONTROLS_INCOMPLETE"
KILL_SWITCH_BLOCKED = "KILL_SWITCH_BLOCKED"
OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED = "OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED"
SUPERVISED_DEMO_ORDER_RUNTIME_REQUIRED = "SUPERVISED_DEMO_ORDER_RUNTIME_REQUIRED"
SUPERVISED_DEMO_ORDER_EXECUTION_READY = "SUPERVISED_DEMO_ORDER_EXECUTION_READY"
SUPERVISED_DEMO_EVIDENCE_REVIEW_REQUIRED = "SUPERVISED_DEMO_EVIDENCE_REVIEW_REQUIRED"
MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED = "MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED"
MICRO_LIVE_ORDER_RUNTIME_REQUIRED = "MICRO_LIVE_ORDER_RUNTIME_REQUIRED"
MICRO_LIVE_ORDER_EXECUTION_READY = "MICRO_LIVE_ORDER_EXECUTION_READY"
MICRO_LIVE_EVIDENCE_REVIEW_REQUIRED = "MICRO_LIVE_EVIDENCE_REVIEW_REQUIRED"
LIVE_TRADING_APPROVAL_REQUIRED = "LIVE_TRADING_APPROVAL_REQUIRED"
LIVE_ORDER_LANE_REQUIRED = "LIVE_ORDER_LANE_REQUIRED"
LIVE_ORDER_EXECUTION_RUNTIME_REQUIRED = "LIVE_ORDER_EXECUTION_RUNTIME_REQUIRED"
AUTONOMOUS_22H_6D_RUNTIME_REQUIRED = "AUTONOMOUS_22H_6D_RUNTIME_REQUIRED"
LIVE_22H_6D_EXECUTION_PROGRAM_READY = "LIVE_22H_6D_EXECUTION_PROGRAM_READY"

CURRENT_SESSION_WINDOW_HOURS = 22
CURRENT_SESSION_WINDOW_DAYS_PER_WEEK = 6

STAGE_BROKER_RUNTIME = "broker_runtime_read_only_auth_probe"
STAGE_EXECUTION_CONTROL_STACK = "execution_control_stack"
STAGE_SUPERVISED_DEMO_APPROVAL = "owner_supervised_demo_approval"
STAGE_SUPERVISED_DEMO_ORDER_EXECUTION = "supervised_demo_order_execution"
STAGE_SUPERVISED_DEMO_OWNER_RUN = "owner_run_supervised_demo_order"
STAGE_DEMO_EVIDENCE_REVIEW = "demo_evidence_review"
STAGE_MICRO_LIVE_APPROVAL = "owner_micro_live_exception_approval"
STAGE_MICRO_LIVE_RUNTIME = "controlled_micro_live_exception"
STAGE_MICRO_LIVE_OWNER_RUN = "owner_run_micro_live_exception"
STAGE_MICRO_LIVE_EVIDENCE_REVIEW = "micro_live_evidence_review"
STAGE_LIVE_TRADING_APPROVAL = "owner_live_trading_approval"
STAGE_LIVE_ORDER_LANE = "live_order_lane"
STAGE_LIVE_ORDER_RUNTIME = "owner_run_live_order_execution"
STAGE_AUTONOMOUS_RUNTIME = "autonomous_22h_6d_runtime"
STAGE_AUTONOMOUS_READY = "owner_run_22h_6d_live_execution"

EXECUTION_PATH = [
    STAGE_BROKER_RUNTIME,
    STAGE_EXECUTION_CONTROL_STACK,
    STAGE_SUPERVISED_DEMO_APPROVAL,
    STAGE_SUPERVISED_DEMO_ORDER_EXECUTION,
    STAGE_SUPERVISED_DEMO_OWNER_RUN,
    STAGE_DEMO_EVIDENCE_REVIEW,
    STAGE_MICRO_LIVE_APPROVAL,
    STAGE_MICRO_LIVE_RUNTIME,
    STAGE_MICRO_LIVE_OWNER_RUN,
    STAGE_MICRO_LIVE_EVIDENCE_REVIEW,
    STAGE_LIVE_TRADING_APPROVAL,
    STAGE_LIVE_ORDER_LANE,
    STAGE_LIVE_ORDER_RUNTIME,
    STAGE_AUTONOMOUS_RUNTIME,
    STAGE_AUTONOMOUS_READY,
]


@dataclass(frozen=True)
class LiveExecutionProgramInput:
    broker_runtime_read_only_auth_proven: bool
    execution_control_stack_landed: bool
    execution_control_stack_ready: bool
    owner_supervised_demo_approval: bool
    supervised_demo_order_runtime_enabled: bool
    supervised_demo_order_executed: bool
    supervised_demo_evidence_clean: bool
    owner_micro_live_exception_approval: bool
    micro_live_order_runtime_enabled: bool
    micro_live_order_executed: bool
    micro_live_evidence_clean: bool
    owner_live_trading_approval: bool
    live_order_lane_enabled: bool
    live_order_execution_enabled: bool
    autonomous_22h_6d_enabled: bool
    kill_switch_enabled: bool
    kill_switch_triggered: bool
    max_daily_loss_defined: bool
    max_trade_risk_defined: bool
    duplicate_order_guard_enabled: bool
    audit_log_enabled: bool
    stop_loss_required: bool
    take_profit_required: bool
    broker_api_called: bool
    bitwarden_cli_called: bool
    credentials_read: bool
    env_file_read: bool
    demo_order_execution: bool
    micro_live_order_execution: bool
    live_order_execution: bool
    money_movement: bool
    scheduler_started: bool
    daemon_started: bool
    webhook_started: bool
    session_window_hours: int
    session_window_days_per_week: int


@dataclass(frozen=True)
class LiveExecutionProgramResult:
    program_status: str
    current_stage: str
    next_stage: str
    blockers: list[str]
    execution_path: list[str]
    runtime_mode: str
    demo_order_execution: bool
    micro_live_order_execution: bool
    live_order_execution: bool
    money_movement: bool
    autonomous_22h_6d_authorized: bool
    broker_api_called: bool
    bitwarden_cli_called: bool
    credentials_read: bool
    env_file_read: bool
    scheduler_started: bool
    daemon_started: bool
    webhook_started: bool
    safe_next_action: str


def build_default_live_execution_program_input() -> LiveExecutionProgramInput:
    return LiveExecutionProgramInput(
        broker_runtime_read_only_auth_proven=True,
        execution_control_stack_landed=True,
        execution_control_stack_ready=False,
        owner_supervised_demo_approval=False,
        supervised_demo_order_runtime_enabled=False,
        supervised_demo_order_executed=False,
        supervised_demo_evidence_clean=False,
        owner_micro_live_exception_approval=False,
        micro_live_order_runtime_enabled=False,
        micro_live_order_executed=False,
        micro_live_evidence_clean=False,
        owner_live_trading_approval=False,
        live_order_lane_enabled=False,
        live_order_execution_enabled=False,
        autonomous_22h_6d_enabled=False,
        kill_switch_enabled=True,
        kill_switch_triggered=False,
        max_daily_loss_defined=True,
        max_trade_risk_defined=True,
        duplicate_order_guard_enabled=True,
        audit_log_enabled=True,
        stop_loss_required=True,
        take_profit_required=True,
        broker_api_called=False,
        bitwarden_cli_called=False,
        credentials_read=False,
        env_file_read=False,
        demo_order_execution=False,
        micro_live_order_execution=False,
        live_order_execution=False,
        money_movement=False,
        scheduler_started=False,
        daemon_started=False,
        webhook_started=False,
        session_window_hours=CURRENT_SESSION_WINDOW_HOURS,
        session_window_days_per_week=CURRENT_SESSION_WINDOW_DAYS_PER_WEEK,
    )


def evaluate_live_execution_program(
    input_data: LiveExecutionProgramInput,
) -> LiveExecutionProgramResult:
    if not input_data.broker_runtime_read_only_auth_proven:
        return _result(
            BROKER_RUNTIME_READ_ONLY_AUTH_REQUIRED,
            STAGE_BROKER_RUNTIME,
            "broker_runtime_read_only_auth_probe",
            ("broker_runtime_read_only_auth_proven is False",),
        )

    if not input_data.execution_control_stack_landed:
        return _result(
            EXECUTION_CONTROL_STACK_REQUIRED,
            STAGE_EXECUTION_CONTROL_STACK,
            "execution_control_stack",
            ("execution_control_stack_landed is False",),
        )

    if not input_data.execution_control_stack_ready:
        status = EXECUTION_CONTROL_STACK_NOT_READY
        next_stage = "owner_supervised_demo_approval"
        blockers = ("execution_control_stack_ready is False",)
        if not input_data.owner_supervised_demo_approval:
            status = OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED
        return _result(status, STAGE_EXECUTION_CONTROL_STACK, next_stage, blockers)

    if _has_protected_boundary_flags(input_data):
        return _result(
            PROTECTED_BOUNDARY_VIOLATION,
            STAGE_EXECUTION_CONTROL_STACK,
            "stop_and_owner_review",
            _protected_boundary_blockers(input_data),
        )

    if (
        not input_data.kill_switch_enabled
        or not input_data.max_daily_loss_defined
        or not input_data.max_trade_risk_defined
        or not input_data.duplicate_order_guard_enabled
        or not input_data.audit_log_enabled
        or not input_data.stop_loss_required
        or not input_data.take_profit_required
    ):
        return _result(
            EXECUTION_CONTROLS_INCOMPLETE,
            STAGE_EXECUTION_CONTROL_STACK,
            "repair_execution_control_stack",
            _execution_controls_blockers(input_data),
        )

    if input_data.kill_switch_triggered:
        return _result(
            KILL_SWITCH_BLOCKED,
            STAGE_EXECUTION_CONTROL_STACK,
            "owner_review_required",
            ("kill_switch_triggered is True",),
        )

    if not input_data.owner_supervised_demo_approval:
        return _result(
            OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED,
            STAGE_SUPERVISED_DEMO_APPROVAL,
            "owner_supervised_demo_approval",
            ("owner_supervised_demo_approval is False",),
        )

    if not input_data.supervised_demo_order_runtime_enabled:
        return _result(
            SUPERVISED_DEMO_ORDER_RUNTIME_REQUIRED,
            STAGE_SUPERVISED_DEMO_ORDER_EXECUTION,
            "supervised_demo_order_execution",
            ("supervised_demo_order_runtime_enabled is False",),
        )

    if not input_data.supervised_demo_order_executed:
        return _result(
            SUPERVISED_DEMO_ORDER_EXECUTION_READY,
            STAGE_SUPERVISED_DEMO_OWNER_RUN,
            "owner_run_supervised_demo_order",
            ("supervised_demo_order_executed is False",),
        )

    if not input_data.supervised_demo_evidence_clean:
        return _result(
            SUPERVISED_DEMO_EVIDENCE_REVIEW_REQUIRED,
            STAGE_DEMO_EVIDENCE_REVIEW,
            "demo_evidence_review",
            ("supervised_demo_evidence_clean is False",),
        )

    if not input_data.owner_micro_live_exception_approval:
        return _result(
            MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED,
            STAGE_MICRO_LIVE_APPROVAL,
            "owner_micro_live_exception_approval",
            ("owner_micro_live_exception_approval is False",),
        )

    if not input_data.micro_live_order_runtime_enabled:
        return _result(
            MICRO_LIVE_ORDER_RUNTIME_REQUIRED,
            STAGE_MICRO_LIVE_RUNTIME,
            "controlled_micro_live_exception",
            ("micro_live_order_runtime_enabled is False",),
        )

    if not input_data.micro_live_order_executed:
        return _result(
            MICRO_LIVE_ORDER_EXECUTION_READY,
            STAGE_MICRO_LIVE_OWNER_RUN,
            "owner_run_micro_live_exception",
            ("micro_live_order_executed is False",),
        )

    if not input_data.micro_live_evidence_clean:
        return _result(
            MICRO_LIVE_EVIDENCE_REVIEW_REQUIRED,
            STAGE_MICRO_LIVE_EVIDENCE_REVIEW,
            "micro_live_evidence_review",
            ("micro_live_evidence_clean is False",),
        )

    if not input_data.owner_live_trading_approval:
        return _result(
            LIVE_TRADING_APPROVAL_REQUIRED,
            STAGE_LIVE_TRADING_APPROVAL,
            "owner_live_trading_approval",
            ("owner_live_trading_approval is False",),
        )

    if not input_data.live_order_lane_enabled:
        return _result(
            LIVE_ORDER_LANE_REQUIRED,
            STAGE_LIVE_ORDER_LANE,
            "live_order_lane",
            ("live_order_lane_enabled is False",),
        )

    if not input_data.live_order_execution_enabled:
        return _result(
            LIVE_ORDER_EXECUTION_RUNTIME_REQUIRED,
            STAGE_LIVE_ORDER_RUNTIME,
            "owner_run_live_order_execution",
            ("live_order_execution_enabled is False",),
        )

    if not input_data.autonomous_22h_6d_enabled:
        return _result(
            AUTONOMOUS_22H_6D_RUNTIME_REQUIRED,
            STAGE_AUTONOMOUS_RUNTIME,
            "autonomous_22h_6d_runtime",
            ("autonomous_22h_6d_enabled is False",),
        )

    return _result(
        LIVE_22H_6D_EXECUTION_PROGRAM_READY,
        STAGE_AUTONOMOUS_READY,
        "owner_run_22h_6d_live_execution",
        tuple(),
    )


def input_as_dict(input_data: LiveExecutionProgramInput) -> dict[str, Any]:
    return asdict(input_data)


def result_as_dict(result: LiveExecutionProgramResult) -> dict[str, Any]:
    return asdict(result)


def _result(
    status: str,
    current_stage: str,
    next_stage: str,
    blockers: tuple[str, ...],
) -> LiveExecutionProgramResult:
    return LiveExecutionProgramResult(
        program_status=status,
        current_stage=current_stage,
        next_stage=next_stage,
        blockers=list(blockers),
        execution_path=_execution_path_for_stage(current_stage),
        runtime_mode=RUNTIME_MODE_DRY_RUN,
        demo_order_execution=False,
        micro_live_order_execution=False,
        live_order_execution=False,
        money_movement=False,
        autonomous_22h_6d_authorized=False,
        broker_api_called=False,
        bitwarden_cli_called=False,
        credentials_read=False,
        env_file_read=False,
        scheduler_started=False,
        daemon_started=False,
        webhook_started=False,
        safe_next_action=_safe_next_action(status),
    )


def _execution_controls_blockers(input_data: LiveExecutionProgramInput) -> tuple[str, ...]:
    blockers: list[str] = []
    if not input_data.kill_switch_enabled:
        blockers.append("kill_switch_enabled is False")
    if not input_data.max_daily_loss_defined:
        blockers.append("max_daily_loss_defined is False")
    if not input_data.max_trade_risk_defined:
        blockers.append("max_trade_risk_defined is False")
    if not input_data.duplicate_order_guard_enabled:
        blockers.append("duplicate_order_guard_enabled is False")
    if not input_data.audit_log_enabled:
        blockers.append("audit_log_enabled is False")
    if not input_data.stop_loss_required:
        blockers.append("stop_loss_required is False")
    if not input_data.take_profit_required:
        blockers.append("take_profit_required is False")
    return tuple(blockers)


def _has_protected_boundary_flags(input_data: LiveExecutionProgramInput) -> bool:
    return any(
        (
            input_data.broker_api_called,
            input_data.bitwarden_cli_called,
            input_data.credentials_read,
            input_data.env_file_read,
            input_data.demo_order_execution,
            input_data.micro_live_order_execution,
            input_data.live_order_execution,
            input_data.money_movement,
            input_data.scheduler_started,
            input_data.daemon_started,
            input_data.webhook_started,
        ),
    )


def _protected_boundary_blockers(input_data: LiveExecutionProgramInput) -> tuple[str, ...]:
    blockers: list[str] = []
    if input_data.broker_api_called:
        blockers.append("broker_api_called is True")
    if input_data.bitwarden_cli_called:
        blockers.append("bitwarden_cli_called is True")
    if input_data.credentials_read:
        blockers.append("credentials_read is True")
    if input_data.env_file_read:
        blockers.append("env_file_read is True")
    if input_data.demo_order_execution:
        blockers.append("demo_order_execution is True")
    if input_data.micro_live_order_execution:
        blockers.append("micro_live_order_execution is True")
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
    return tuple(blockers)


def _execution_path_for_stage(stage: str) -> list[str]:
    if stage in EXECUTION_PATH:
        index = EXECUTION_PATH.index(stage)
        return EXECUTION_PATH[: index + 1]
    return EXECUTION_PATH[:]


def _safe_next_action(status: str) -> str:
    return {
        BROKER_RUNTIME_READ_ONLY_AUTH_REQUIRED: "Run the broker runtime read-only auth probe and return this packet to execution control.",
        EXECUTION_CONTROL_STACK_REQUIRED: "Land the execution control stack stage and rerun this packet.",
        EXECUTION_CONTROL_STACK_NOT_READY: "Repair execution control stack readiness before supervised demo approval.",
        PROTECTED_BOUNDARY_VIOLATION: "Stop immediately, clear protected-boundary flags, then rerun for validation-only review.",
        EXECUTION_CONTROLS_INCOMPLETE: "Complete kill switch, risk caps, duplicate guard, audit, and SL/TP controls before continuing.",
        KILL_SWITCH_BLOCKED: "Owner review required before any runtime movement.",
        OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED: "Collect owner supervised demo approval and run owner-approved demo order runtime separately.",
        SUPERVISED_DEMO_ORDER_RUNTIME_REQUIRED: "Enable supervised demo order runtime mode with explicit owner guard before execution.",
        SUPERVISED_DEMO_ORDER_EXECUTION_READY: "Run owner-run supervised demo order command in dry-run mode only.",
        SUPERVISED_DEMO_EVIDENCE_REVIEW_REQUIRED: "Review and clear supervised demo evidence before micro-live exception.",
        MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED: "Obtain owner micro-live exception approval and rerun in owner-controlled mode.",
        MICRO_LIVE_ORDER_RUNTIME_REQUIRED: "Enable micro-live order runtime mode with owner approval before micro-live order execution.",
        MICRO_LIVE_ORDER_EXECUTION_READY: "Run owner micro-live exception command with explicit owner action and no live side effects.",
        MICRO_LIVE_EVIDENCE_REVIEW_REQUIRED: "Review and clear micro-live evidence before enabling the live order lane.",
        LIVE_TRADING_APPROVAL_REQUIRED: "Collect owner live trading approval before any live lane readiness.",
        LIVE_ORDER_LANE_REQUIRED: "Enable the live order lane with explicit owner runtime flag.",
        LIVE_ORDER_EXECUTION_RUNTIME_REQUIRED: "Run owner live-order execution runtime gate and stage explicitly.",
        AUTONOMOUS_22H_6D_RUNTIME_REQUIRED: "Collect separate owner approval for 22hr/day 6day/week autonomous runtime.",
        LIVE_22H_6D_EXECUTION_PROGRAM_READY: "Autonomous runtime is ready from control perspective; execute only through owner run command.",
    }[status]


__all__ = [
    "LiveExecutionProgramInput",
    "LiveExecutionProgramResult",
    "evaluate_live_execution_program",
    "build_default_live_execution_program_input",
    "input_as_dict",
    "result_as_dict",
    "RUNTIME_MODE_DRY_RUN",
    "PACKET_ID",
    "MODULE_NAME",
    "BROKER_RUNTIME_READ_ONLY_AUTH_REQUIRED",
    "EXECUTION_CONTROL_STACK_REQUIRED",
    "EXECUTION_CONTROL_STACK_NOT_READY",
    "PROTECTED_BOUNDARY_VIOLATION",
    "EXECUTION_CONTROLS_INCOMPLETE",
    "KILL_SWITCH_BLOCKED",
    "OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED",
    "SUPERVISED_DEMO_ORDER_RUNTIME_REQUIRED",
    "SUPERVISED_DEMO_ORDER_EXECUTION_READY",
    "SUPERVISED_DEMO_EVIDENCE_REVIEW_REQUIRED",
    "MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED",
    "MICRO_LIVE_ORDER_RUNTIME_REQUIRED",
    "MICRO_LIVE_ORDER_EXECUTION_READY",
    "MICRO_LIVE_EVIDENCE_REVIEW_REQUIRED",
    "LIVE_TRADING_APPROVAL_REQUIRED",
    "LIVE_ORDER_LANE_REQUIRED",
    "LIVE_ORDER_EXECUTION_RUNTIME_REQUIRED",
    "AUTONOMOUS_22H_6D_RUNTIME_REQUIRED",
    "LIVE_22H_6D_EXECUTION_PROGRAM_READY",
    "STAGE_BROKER_RUNTIME",
    "STAGE_EXECUTION_CONTROL_STACK",
    "STAGE_SUPERVISED_DEMO_APPROVAL",
    "STAGE_SUPERVISED_DEMO_ORDER_EXECUTION",
    "STAGE_SUPERVISED_DEMO_OWNER_RUN",
    "STAGE_DEMO_EVIDENCE_REVIEW",
    "STAGE_MICRO_LIVE_APPROVAL",
    "STAGE_MICRO_LIVE_RUNTIME",
    "STAGE_MICRO_LIVE_OWNER_RUN",
    "STAGE_MICRO_LIVE_EVIDENCE_REVIEW",
    "STAGE_LIVE_TRADING_APPROVAL",
    "STAGE_LIVE_ORDER_LANE",
    "STAGE_LIVE_ORDER_RUNTIME",
    "STAGE_AUTONOMOUS_RUNTIME",
    "STAGE_AUTONOMOUS_READY",
    "CURRENT_SESSION_WINDOW_HOURS",
    "CURRENT_SESSION_WINDOW_DAYS_PER_WEEK",
]
