"""Execution control stack contract and evaluator for AI_OS Forex packet flow."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


PACKET_ID = "AIOS-FOREX-EXECUTION-CONTROL-STACK-V1"
CURRENT_STAGE = "execution_control_stack"
NEXT_STAGE_AFTER_READY = "supervised_demo_order_execution"
SAFE_MODE = "dry_run"

BROKER_RUNTIME_READ_ONLY_AUTH_REQUIRED = "BROKER_RUNTIME_READ_ONLY_AUTH_REQUIRED"
PROTECTED_BOUNDARY_VIOLATION = "PROTECTED_BOUNDARY_VIOLATION"
KILL_SWITCH_REQUIRED = "KILL_SWITCH_REQUIRED"
KILL_SWITCH_BLOCKED = "KILL_SWITCH_BLOCKED"
MAX_DAILY_LOSS_REQUIRED = "MAX_DAILY_LOSS_REQUIRED"
MAX_DAILY_LOSS_BLOCKED = "MAX_DAILY_LOSS_BLOCKED"
MAX_TRADE_RISK_REQUIRED = "MAX_TRADE_RISK_REQUIRED"
MAX_TRADE_RISK_BLOCKED = "MAX_TRADE_RISK_BLOCKED"
DUPLICATE_ORDER_GUARD_REQUIRED = "DUPLICATE_ORDER_GUARD_REQUIRED"
DUPLICATE_ORDER_BLOCKED = "DUPLICATE_ORDER_BLOCKED"
AUDIT_LOG_REQUIRED = "AUDIT_LOG_REQUIRED"
AUDIT_LOG_WRITE_REQUIRED = "AUDIT_LOG_WRITE_REQUIRED"
STOP_LOSS_REQUIRED = "STOP_LOSS_REQUIRED"
TAKE_PROFIT_REQUIRED = "TAKE_PROFIT_REQUIRED"
SUPERVISED_DEMO_APPROVAL_REQUIRED = "SUPERVISED_DEMO_APPROVAL_REQUIRED"
EXECUTION_CONTROL_STACK_READY = "EXECUTION_CONTROL_STACK_READY"

CURRENT_SESSION_WINDOW_HOURS = 22
CURRENT_SESSION_WINDOW_DAYS_PER_WEEK = 6


@dataclass(frozen=True)
class ExecutionControlInput:
    broker_runtime_read_only_auth_proven: bool
    owner_demo_approval: bool
    owner_live_approval: bool
    kill_switch_enabled: bool
    kill_switch_triggered: bool
    max_daily_loss_defined: bool
    max_daily_loss_amount: float
    current_daily_loss_amount: float
    max_trade_risk_defined: bool
    max_trade_risk_amount: float
    proposed_trade_risk_amount: float
    duplicate_order_guard_enabled: bool
    duplicate_order_detected: bool
    audit_log_enabled: bool
    audit_log_write_success: bool
    order_intent_id: str
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
    order_execution: bool
    demo_authorized: bool
    live_authorized: bool
    session_window_hours: int
    session_window_days_per_week: int


@dataclass(frozen=True)
class ExecutionControlResult:
    control_status: str
    current_stage: str
    next_stage: str
    blockers: list[str]
    order_intent_id: str
    pre_order_decision: str
    kill_switch_state: str
    risk_state: str
    duplicate_guard_state: str
    audit_state: str
    broker_api_called: bool
    bitwarden_cli_called: bool
    credentials_read: bool
    env_file_read: bool
    order_execution: bool
    demo_authorized: bool
    live_authorized: bool
    safe_next_action: str


def build_default_input(
    *,
    owner_demo_approval: bool = False,
    owner_live_approval: bool = False,
) -> ExecutionControlInput:
    return ExecutionControlInput(
        broker_runtime_read_only_auth_proven=True,
        owner_demo_approval=owner_demo_approval,
        owner_live_approval=owner_live_approval,
        kill_switch_enabled=True,
        kill_switch_triggered=False,
        max_daily_loss_defined=True,
        max_daily_loss_amount=25.00,
        current_daily_loss_amount=0.00,
        max_trade_risk_defined=True,
        max_trade_risk_amount=2.00,
        proposed_trade_risk_amount=1.00,
        duplicate_order_guard_enabled=True,
        duplicate_order_detected=False,
        audit_log_enabled=True,
        audit_log_write_success=True,
        order_intent_id="DRY_RUN_ORDER_INTENT_001",
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
        order_execution=False,
        demo_authorized=False,
        live_authorized=False,
        session_window_hours=CURRENT_SESSION_WINDOW_HOURS,
        session_window_days_per_week=CURRENT_SESSION_WINDOW_DAYS_PER_WEEK,
    )


def evaluate_execution_control_stack(
    input_data: ExecutionControlInput,
) -> ExecutionControlResult:
    blockers: list[str] = []
    control_status = EXECUTION_CONTROL_STACK_READY
    next_stage = NEXT_STAGE_AFTER_READY

    if not input_data.broker_runtime_read_only_auth_proven:
        control_status = BROKER_RUNTIME_READ_ONLY_AUTH_REQUIRED
        next_stage = "broker_runtime_read_only_auth_probe"
        blockers.append("broker_runtime_read_only_auth_proven is False")

    elif _has_protected_boundary_flags(input_data):
        control_status = PROTECTED_BOUNDARY_VIOLATION
        next_stage = "stop_and_owner_review"
        blockers.extend(_protected_flag_blockers(input_data))

    elif not input_data.kill_switch_enabled:
        control_status = KILL_SWITCH_REQUIRED
        next_stage = "define_kill_switch"
        blockers.append("kill_switch_enabled is False")

    elif input_data.kill_switch_triggered:
        control_status = KILL_SWITCH_BLOCKED
        next_stage = "owner_review_required"
        blockers.append("kill_switch_triggered is True")

    elif not input_data.max_daily_loss_defined:
        control_status = MAX_DAILY_LOSS_REQUIRED
        next_stage = "define_max_daily_loss"
        blockers.append("max_daily_loss_defined is False")

    elif input_data.current_daily_loss_amount >= input_data.max_daily_loss_amount:
        control_status = MAX_DAILY_LOSS_BLOCKED
        next_stage = "daily_loss_owner_review"
        blockers.append(
            "current_daily_loss_amount is greater than or equal to "
            "max_daily_loss_amount",
        )

    elif not input_data.max_trade_risk_defined:
        control_status = MAX_TRADE_RISK_REQUIRED
        next_stage = "define_max_trade_risk"
        blockers.append("max_trade_risk_defined is False")

    elif input_data.proposed_trade_risk_amount > input_data.max_trade_risk_amount:
        control_status = MAX_TRADE_RISK_BLOCKED
        next_stage = "reduce_trade_risk"
        blockers.append("proposed_trade_risk_amount exceeds max_trade_risk_amount")

    elif not input_data.duplicate_order_guard_enabled:
        control_status = DUPLICATE_ORDER_GUARD_REQUIRED
        next_stage = "define_duplicate_order_guard"
        blockers.append("duplicate_order_guard_enabled is False")

    elif input_data.duplicate_order_detected:
        control_status = DUPLICATE_ORDER_BLOCKED
        next_stage = "duplicate_order_owner_review"
        blockers.append("duplicate_order_detected is True")

    elif not input_data.audit_log_enabled:
        control_status = AUDIT_LOG_REQUIRED
        next_stage = "define_order_intent_audit_log"
        blockers.append("audit_log_enabled is False")

    elif not input_data.audit_log_write_success:
        control_status = AUDIT_LOG_WRITE_REQUIRED
        next_stage = "repair_order_intent_audit_log"
        blockers.append("audit_log_write_success is False")

    elif not input_data.stop_loss_defined:
        control_status = STOP_LOSS_REQUIRED
        next_stage = "define_stop_loss"
        blockers.append("stop_loss_defined is False")

    elif not input_data.take_profit_defined:
        control_status = TAKE_PROFIT_REQUIRED
        next_stage = "define_take_profit"
        blockers.append("take_profit_defined is False")

    elif not input_data.owner_demo_approval:
        control_status = SUPERVISED_DEMO_APPROVAL_REQUIRED
        next_stage = "owner_supervised_demo_approval"
        blockers.append("owner_demo_approval is False")

    return ExecutionControlResult(
        control_status=control_status,
        current_stage=CURRENT_STAGE,
        next_stage=next_stage,
        blockers=blockers,
        order_intent_id=input_data.order_intent_id,
        pre_order_decision=_pre_order_decision(control_status),
        kill_switch_state=_kill_switch_state(input_data),
        risk_state=_risk_state(input_data),
        duplicate_guard_state=_duplicate_guard_state(input_data),
        audit_state=_audit_state(input_data),
        broker_api_called=bool(input_data.broker_api_called),
        bitwarden_cli_called=bool(input_data.bitwarden_cli_called),
        credentials_read=bool(input_data.credentials_read),
        env_file_read=bool(input_data.env_file_read),
        order_execution=False,
        demo_authorized=False,
        live_authorized=False,
        safe_next_action=_safe_next_action(control_status),
    )


def _pre_order_decision(control_status: str) -> str:
    if control_status == EXECUTION_CONTROL_STACK_READY:
        return "READY_TO_SEND_ORDER_INTENT"
    return "BLOCK_ORDER_INTENT"


def _kill_switch_state(input_data: ExecutionControlInput) -> str:
    if not input_data.kill_switch_enabled:
        return "required"
    if input_data.kill_switch_triggered:
        return "triggered"
    return "enabled"


def _risk_state(input_data: ExecutionControlInput) -> str:
    if not input_data.max_daily_loss_defined:
        return "max_daily_loss_required"
    if input_data.current_daily_loss_amount >= input_data.max_daily_loss_amount:
        return "max_daily_loss_exceeded"
    if not input_data.max_trade_risk_defined:
        return "max_trade_risk_required"
    if input_data.proposed_trade_risk_amount > input_data.max_trade_risk_amount:
        return "max_trade_risk_exceeded"
    return "within_limits"


def _duplicate_guard_state(input_data: ExecutionControlInput) -> str:
    if not input_data.duplicate_order_guard_enabled:
        return "guard_required"
    if input_data.duplicate_order_detected:
        return "duplicate_detected"
    return "guard_enabled"


def _audit_state(input_data: ExecutionControlInput) -> str:
    if not input_data.audit_log_enabled:
        return "audit_log_required"
    if not input_data.audit_log_write_success:
        return "audit_write_failed"
    return "audit_log_ok"


def _safe_next_action(control_status: str) -> str:
    actions = {
        BROKER_RUNTIME_READ_ONLY_AUTH_REQUIRED: (
            "Run broker-runtime read-only auth proof and re-run this packet."
        ),
        PROTECTED_BOUNDARY_VIOLATION: (
            "Stop and request owner review. Remove all protected-boundary flags."
        ),
        KILL_SWITCH_REQUIRED: "Define and enable kill switch controls.",
        KILL_SWITCH_BLOCKED: "Clear kill switch trigger and review controls.",
        MAX_DAILY_LOSS_REQUIRED: "Define daily loss cap before continuing.",
        MAX_DAILY_LOSS_BLOCKED: "Review and reset daily losses before proceeding.",
        MAX_TRADE_RISK_REQUIRED: "Define maximum trade risk before continuing.",
        MAX_TRADE_RISK_BLOCKED: (
            "Reduce proposed trade risk to be within max_trade_risk_amount."
        ),
        DUPLICATE_ORDER_GUARD_REQUIRED: "Enable duplicate-order guard before continuing.",
        DUPLICATE_ORDER_BLOCKED: (
            "Review duplicate-order detection and remove or intentionally clear duplicate flag."
        ),
        AUDIT_LOG_REQUIRED: (
            "Enable order-intent audit log before continuing this packet."
        ),
        AUDIT_LOG_WRITE_REQUIRED: (
            "Repair order-intent audit log write path before continuing."
        ),
        STOP_LOSS_REQUIRED: "Define stop-loss control for the order intent.",
        TAKE_PROFIT_REQUIRED: "Define take-profit control for the order intent.",
        SUPERVISED_DEMO_APPROVAL_REQUIRED: (
            "Request owner supervised demo approval before order execution."
        ),
        EXECUTION_CONTROL_STACK_READY: (
            "Proceed to supervised demo order execution lane."
        ),
    }
    return actions.get(control_status, "Review execution control stack requirements.")


def _has_protected_boundary_flags(input_data: ExecutionControlInput) -> bool:
    return any(
        [
            bool(input_data.broker_api_called),
            bool(input_data.bitwarden_cli_called),
            bool(input_data.credentials_read),
            bool(input_data.env_file_read),
            bool(input_data.order_execution),
            bool(input_data.demo_authorized),
            bool(input_data.live_authorized),
        ],
    )


def _protected_flag_blockers(input_data: ExecutionControlInput) -> list[str]:
    blocked: list[str] = []
    if input_data.broker_api_called:
        blocked.append("broker_api_called is True")
    if input_data.bitwarden_cli_called:
        blocked.append("bitwarden_cli_called is True")
    if input_data.credentials_read:
        blocked.append("credentials_read is True")
    if input_data.env_file_read:
        blocked.append("env_file_read is True")
    if input_data.order_execution:
        blocked.append("order_execution is True")
    if input_data.demo_authorized:
        blocked.append("demo_authorized is True")
    if input_data.live_authorized:
        blocked.append("live_authorized is True")
    return blocked


def input_as_dict(input_data: ExecutionControlInput) -> dict[str, Any]:
    return asdict(input_data)


def result_as_dict(result: ExecutionControlResult) -> dict[str, Any]:
    return asdict(result)


__all__ = [
    "ExecutionControlInput",
    "ExecutionControlResult",
    "evaluate_execution_control_stack",
    "build_default_input",
    "input_as_dict",
    "result_as_dict",
    "BROKER_RUNTIME_READ_ONLY_AUTH_REQUIRED",
    "PROTECTED_BOUNDARY_VIOLATION",
    "KILL_SWITCH_REQUIRED",
    "KILL_SWITCH_BLOCKED",
    "MAX_DAILY_LOSS_REQUIRED",
    "MAX_DAILY_LOSS_BLOCKED",
    "MAX_TRADE_RISK_REQUIRED",
    "MAX_TRADE_RISK_BLOCKED",
    "DUPLICATE_ORDER_GUARD_REQUIRED",
    "DUPLICATE_ORDER_BLOCKED",
    "AUDIT_LOG_REQUIRED",
    "AUDIT_LOG_WRITE_REQUIRED",
    "STOP_LOSS_REQUIRED",
    "TAKE_PROFIT_REQUIRED",
    "SUPERVISED_DEMO_APPROVAL_REQUIRED",
    "EXECUTION_CONTROL_STACK_READY",
    "PACKET_ID",
    "CURRENT_STAGE",
    "NEXT_STAGE_AFTER_READY",
    "SAFE_MODE",
    "CURRENT_SESSION_WINDOW_HOURS",
    "CURRENT_SESSION_WINDOW_DAYS_PER_WEEK",
]
