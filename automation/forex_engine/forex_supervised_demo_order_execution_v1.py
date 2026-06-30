"""Supervised demo order execution contract and evaluator for AI OS forex."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


PACKET_ID = "AIOS-FOREX-SUPERVISED-DEMO-ORDER-EXECUTION-V1"
CURRENT_STAGE = "supervised_demo_order_execution"
RUNTIME_MODE_DRY_RUN = "dry_run"

PREREQUISITES_REQUIRED = "PREREQUISITES_REQUIRED"
OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED = "OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED"
OWNER_RUNTIME_ORDER_FLAG_REQUIRED = "OWNER_RUNTIME_ORDER_FLAG_REQUIRED"
PROTECTED_BOUNDARY_VIOLATION = "PROTECTED_BOUNDARY_VIOLATION"
RUNTIME_CREDENTIAL_ACCESS_REQUIRED = "RUNTIME_CREDENTIAL_ACCESS_REQUIRED"
PRACTICE_DEMO_BOUNDARY_REQUIRED = "PRACTICE_DEMO_BOUNDARY_REQUIRED"
KILL_SWITCH_BLOCKED = "KILL_SWITCH_BLOCKED"
EXECUTION_CONTROL_BLOCKED = "EXECUTION_CONTROL_BLOCKED"
SUPERVISED_DEMO_ORDER_READY = "SUPERVISED_DEMO_ORDER_READY"

NEXT_STAGE_COMPLETE_PRIOR_LANES = "complete_prior_execution_lanes"
NEXT_STAGE_OWNER_SUPERVISED_DEMO_APPROVAL = "owner_supervised_demo_approval"
NEXT_STAGE_OWNER_RUN_SUPERVISED_DEMO_ORDER = "owner_run_supervised_demo_order"
NEXT_STAGE_OWNER_REVIEW = "stop_and_owner_review"
NEXT_STAGE_OWNER_UNLOCK_BITWARDEN = "owner_unlock_bitwarden_cli"
NEXT_STAGE_REPAIR_DEMO_BOUNDARY = "repair_demo_boundary"
NEXT_STAGE_OWNER_REVIEW_REQUIRED = "owner_review_required"
NEXT_STAGE_REPAIR_EXECUTION_CONTROLS = "repair_execution_controls"
NEXT_STAGE_OWNER_EXECUTE_ONE_ORDER = "owner_execute_one_supervised_demo_order"

DEFAULT_RUNTIME_ALLOWED_MODES = (
    "read_only_until_owner_demo_approval",
    "supervised_demo_only",
)


@dataclass(frozen=True)
class SupervisedDemoOrderInput:
    broker_runtime_read_only_auth_proven: bool
    execution_control_stack_landed: bool
    live_execution_program_landed: bool
    owner_supervised_demo_approval: bool
    owner_runtime_order_flag: bool
    bw_session_present: bool
    bitwarden_cli_available: bool
    bitwarden_item_read_success: bool
    credential_values_available_to_runtime: bool
    endpoint_is_oanda_practice: bool
    environment_is_practice_demo: bool
    allowed_mode_is_demo_only: bool
    kill_switch_enabled: bool
    kill_switch_triggered: bool
    max_daily_loss_defined: bool
    daily_loss_within_limit: bool
    max_trade_risk_defined: bool
    proposed_trade_risk_within_limit: bool
    duplicate_order_guard_enabled: bool
    duplicate_order_detected: bool
    audit_log_enabled: bool
    audit_log_write_success: bool
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
    demo_order_execution: bool
    live_order_execution: bool
    money_movement: bool
    scheduler_started: bool
    daemon_started: bool
    webhook_started: bool


@dataclass(frozen=True)
class SupervisedDemoOrderResult:
    demo_order_status: str
    current_stage: str
    next_stage: str
    blockers: list[str]
    runtime_mode: str
    order_intent_summary: str
    broker_api_called: bool
    bitwarden_cli_called: bool
    credentials_read: bool
    env_file_read: bool
    demo_order_execution: bool
    live_order_execution: bool
    money_movement: bool
    scheduler_started: bool
    daemon_started: bool
    webhook_started: bool
    safe_next_action: str


def build_default_input(
    *,
    owner_supervised_demo_approval: bool = False,
    owner_runtime_order_flag: bool = False,
) -> SupervisedDemoOrderInput:
    return SupervisedDemoOrderInput(
        broker_runtime_read_only_auth_proven=True,
        execution_control_stack_landed=True,
        live_execution_program_landed=True,
        owner_supervised_demo_approval=owner_supervised_demo_approval,
        owner_runtime_order_flag=owner_runtime_order_flag,
        bw_session_present=False,
        bitwarden_cli_available=False,
        bitwarden_item_read_success=False,
        credential_values_available_to_runtime=False,
        endpoint_is_oanda_practice=True,
        environment_is_practice_demo=True,
        allowed_mode_is_demo_only=True,
        kill_switch_enabled=True,
        kill_switch_triggered=False,
        max_daily_loss_defined=True,
        daily_loss_within_limit=True,
        max_trade_risk_defined=True,
        proposed_trade_risk_within_limit=True,
        duplicate_order_guard_enabled=True,
        duplicate_order_detected=False,
        audit_log_enabled=True,
        audit_log_write_success=True,
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
        demo_order_execution=False,
        live_order_execution=False,
        money_movement=False,
        scheduler_started=False,
        daemon_started=False,
        webhook_started=False,
    )


def evaluate_supervised_demo_order_execution(
    input_data: SupervisedDemoOrderInput,
) -> SupervisedDemoOrderResult:
    blockers: list[str] = []
    current_stage = CURRENT_STAGE

    if not _prerequisites_ready(input_data):
        blockers.extend(_prerequisite_blockers(input_data))
        return _result(
            demo_order_status=PREREQUISITES_REQUIRED,
            current_stage=current_stage,
            next_stage=NEXT_STAGE_COMPLETE_PRIOR_LANES,
            blockers=blockers,
            runtime_mode=RUNTIME_MODE_DRY_RUN,
            order_intent_summary=_order_intent_summary(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(PREREQUISITES_REQUIRED),
        )

    if not input_data.owner_supervised_demo_approval:
        return _result(
            demo_order_status=OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED,
            current_stage=current_stage,
            next_stage=NEXT_STAGE_OWNER_SUPERVISED_DEMO_APPROVAL,
            blockers=["owner_supervised_demo_approval is False"],
            runtime_mode=RUNTIME_MODE_DRY_RUN,
            order_intent_summary=_order_intent_summary(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(
                OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED,
            ),
        )

    if not input_data.owner_runtime_order_flag:
        return _result(
            demo_order_status=OWNER_RUNTIME_ORDER_FLAG_REQUIRED,
            current_stage=current_stage,
            next_stage=NEXT_STAGE_OWNER_RUN_SUPERVISED_DEMO_ORDER,
            blockers=["owner_runtime_order_flag is False"],
            runtime_mode=RUNTIME_MODE_DRY_RUN,
            order_intent_summary=_order_intent_summary(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(OWNER_RUNTIME_ORDER_FLAG_REQUIRED),
        )

    if _protected_boundary_flags(input_data):
        return _result(
            demo_order_status=PROTECTED_BOUNDARY_VIOLATION,
            current_stage=current_stage,
            next_stage=NEXT_STAGE_OWNER_REVIEW,
            blockers=_protected_boundary_blockers(input_data),
            runtime_mode=RUNTIME_MODE_DRY_RUN,
            order_intent_summary=_order_intent_summary(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(PROTECTED_BOUNDARY_VIOLATION),
        )

    if not (
        input_data.bw_session_present
        and input_data.bitwarden_cli_available
        and input_data.bitwarden_item_read_success
        and input_data.credential_values_available_to_runtime
    ):
        blockers = []
        if not input_data.bw_session_present:
            blockers.append("bw_session_present is False")
        if not input_data.bitwarden_cli_available:
            blockers.append("bitwarden_cli_available is False")
        if not input_data.bitwarden_item_read_success:
            blockers.append("bitwarden_item_read_success is False")
        if not input_data.credential_values_available_to_runtime:
            blockers.append("credential_values_available_to_runtime is False")
        return _result(
            demo_order_status=RUNTIME_CREDENTIAL_ACCESS_REQUIRED,
            current_stage=current_stage,
            next_stage=NEXT_STAGE_OWNER_UNLOCK_BITWARDEN,
            blockers=blockers,
            runtime_mode=RUNTIME_MODE_DRY_RUN,
            order_intent_summary=_order_intent_summary(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(RUNTIME_CREDENTIAL_ACCESS_REQUIRED),
        )

    if not (
        input_data.endpoint_is_oanda_practice
        and input_data.environment_is_practice_demo
        and input_data.allowed_mode_is_demo_only
    ):
        blockers = []
        if not input_data.endpoint_is_oanda_practice:
            blockers.append("endpoint_is_oanda_practice is False")
        if not input_data.environment_is_practice_demo:
            blockers.append("environment_is_practice_demo is False")
        if not input_data.allowed_mode_is_demo_only:
            blockers.append("allowed_mode_is_demo_only is False")
        return _result(
            demo_order_status=PRACTICE_DEMO_BOUNDARY_REQUIRED,
            current_stage=current_stage,
            next_stage=NEXT_STAGE_REPAIR_DEMO_BOUNDARY,
            blockers=blockers,
            runtime_mode=RUNTIME_MODE_DRY_RUN,
            order_intent_summary=_order_intent_summary(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(PRACTICE_DEMO_BOUNDARY_REQUIRED),
        )

    if (not input_data.kill_switch_enabled) or input_data.kill_switch_triggered:
        blockers = []
        if not input_data.kill_switch_enabled:
            blockers.append("kill_switch_enabled is False")
        if input_data.kill_switch_triggered:
            blockers.append("kill_switch_triggered is True")
        return _result(
            demo_order_status=KILL_SWITCH_BLOCKED,
            current_stage=current_stage,
            next_stage=NEXT_STAGE_OWNER_REVIEW_REQUIRED,
            blockers=blockers,
            runtime_mode=RUNTIME_MODE_DRY_RUN,
            order_intent_summary=_order_intent_summary(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(KILL_SWITCH_BLOCKED),
        )

    if not _execution_controls_ready(input_data):
        return _result(
            demo_order_status=EXECUTION_CONTROL_BLOCKED,
            current_stage=current_stage,
            next_stage=NEXT_STAGE_REPAIR_EXECUTION_CONTROLS,
            blockers=_execution_control_blockers(input_data),
            runtime_mode=RUNTIME_MODE_DRY_RUN,
            order_intent_summary=_order_intent_summary(input_data),
            input_data=input_data,
            safe_next_action=_safe_next_action(EXECUTION_CONTROL_BLOCKED),
        )

    return _result(
        demo_order_status=SUPERVISED_DEMO_ORDER_READY,
        current_stage=current_stage,
        next_stage=NEXT_STAGE_OWNER_EXECUTE_ONE_ORDER,
        blockers=[],
        runtime_mode=RUNTIME_MODE_DRY_RUN,
        order_intent_summary=_order_intent_summary(input_data),
        input_data=input_data,
        safe_next_action=_safe_next_action(SUPERVISED_DEMO_ORDER_READY),
    )


def input_as_dict(input_data: SupervisedDemoOrderInput) -> dict[str, Any]:
    return asdict(input_data)


def result_as_dict(result: SupervisedDemoOrderResult) -> dict[str, Any]:
    return asdict(result)


def _prerequisites_ready(input_data: SupervisedDemoOrderInput) -> bool:
    return (
        input_data.broker_runtime_read_only_auth_proven
        and input_data.execution_control_stack_landed
        and input_data.live_execution_program_landed
    )


def _prerequisite_blockers(input_data: SupervisedDemoOrderInput) -> list[str]:
    blockers: list[str] = []
    if not input_data.broker_runtime_read_only_auth_proven:
        blockers.append("broker_runtime_read_only_auth_proven is False")
    if not input_data.execution_control_stack_landed:
        blockers.append("execution_control_stack_landed is False")
    if not input_data.live_execution_program_landed:
        blockers.append("live_execution_program_landed is False")
    return blockers


def _protected_boundary_flags(input_data: SupervisedDemoOrderInput) -> bool:
    return any(
        (
            input_data.broker_api_called,
            input_data.bitwarden_cli_called,
            input_data.credentials_read,
            input_data.env_file_read,
            input_data.demo_order_execution,
            input_data.live_order_execution,
            input_data.money_movement,
            input_data.scheduler_started,
            input_data.daemon_started,
            input_data.webhook_started,
        ),
    )


def _protected_boundary_blockers(input_data: SupervisedDemoOrderInput) -> list[str]:
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


def _execution_controls_ready(input_data: SupervisedDemoOrderInput) -> bool:
    return (
        input_data.max_daily_loss_defined
        and input_data.daily_loss_within_limit
        and input_data.max_trade_risk_defined
        and input_data.proposed_trade_risk_within_limit
        and input_data.duplicate_order_guard_enabled
        and not input_data.duplicate_order_detected
        and input_data.audit_log_enabled
        and input_data.audit_log_write_success
        and input_data.stop_loss_defined
        and input_data.take_profit_defined
    )


def _execution_control_blockers(input_data: SupervisedDemoOrderInput) -> list[str]:
    blockers: list[str] = []
    if not input_data.max_daily_loss_defined:
        blockers.append("max_daily_loss_defined is False")
    if not input_data.daily_loss_within_limit:
        blockers.append("daily_loss_within_limit is False")
    if not input_data.max_trade_risk_defined:
        blockers.append("max_trade_risk_defined is False")
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
    if not input_data.stop_loss_defined:
        blockers.append("stop_loss_defined is False")
    if not input_data.take_profit_defined:
        blockers.append("take_profit_defined is False")
    return blockers


def _order_intent_summary(input_data: SupervisedDemoOrderInput) -> str:
    return (
        f"instrument={input_data.instrument}, units={input_data.units}, "
        f"side={input_data.side}, order_type={input_data.order_type}, "
        f"time_in_force={input_data.time_in_force}"
    )


def _result(
    *,
    demo_order_status: str,
    current_stage: str,
    next_stage: str,
    blockers: list[str],
    runtime_mode: str,
    order_intent_summary: str,
    input_data: SupervisedDemoOrderInput,
    safe_next_action: str,
) -> SupervisedDemoOrderResult:
    return SupervisedDemoOrderResult(
        demo_order_status=demo_order_status,
        current_stage=current_stage,
        next_stage=next_stage,
        blockers=blockers,
        runtime_mode=runtime_mode,
        order_intent_summary=order_intent_summary,
        broker_api_called=bool(input_data.broker_api_called),
        bitwarden_cli_called=bool(input_data.bitwarden_cli_called),
        credentials_read=bool(input_data.credentials_read),
        env_file_read=bool(input_data.env_file_read),
        demo_order_execution=bool(input_data.demo_order_execution),
        live_order_execution=False,
        money_movement=False,
        scheduler_started=False,
        daemon_started=False,
        webhook_started=False,
        safe_next_action=safe_next_action,
    )


def _safe_next_action(status: str) -> str:
    return {
        PREREQUISITES_REQUIRED: (
            "Complete broker runtime auth, execution control stack, and live execution "
            "program lanes before this packet."
        ),
        OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED: (
            "Collect owner supervised demo approval and rerun with approval context."
        ),
        OWNER_RUNTIME_ORDER_FLAG_REQUIRED: (
            "Run this packet with --owner-approved-supervised-demo-order."
        ),
        PROTECTED_BOUNDARY_VIOLATION: (
            "Stop and repair protected-boundary flags before any runtime action."
        ),
        RUNTIME_CREDENTIAL_ACCESS_REQUIRED: (
            "Resolve BW_SESSION, Bitwarden CLI, Bitwarden item, and runtime credentials."
        ),
        PRACTICE_DEMO_BOUNDARY_REQUIRED: (
            "Use OANDA practice endpoint, practice_demo environment, and demo-only mode."
        ),
        KILL_SWITCH_BLOCKED: "Run owner review to clear kill-switch or stop trading gates.",
        EXECUTION_CONTROL_BLOCKED: (
            "Repair daily loss, trade risk, duplicate order guard, audit, and SL/TP controls."
        ),
        SUPERVISED_DEMO_ORDER_READY: "Execute owner-approved supervised demo order runtime path.",
    }.get(status, "Review packet state and repair blockers.")


__all__ = [
    "SupervisedDemoOrderInput",
    "SupervisedDemoOrderResult",
    "evaluate_supervised_demo_order_execution",
    "build_default_input",
    "input_as_dict",
    "result_as_dict",
    "PACKET_ID",
    "CURRENT_STAGE",
    "PREREQUISITES_REQUIRED",
    "OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED",
    "OWNER_RUNTIME_ORDER_FLAG_REQUIRED",
    "PROTECTED_BOUNDARY_VIOLATION",
    "RUNTIME_CREDENTIAL_ACCESS_REQUIRED",
    "PRACTICE_DEMO_BOUNDARY_REQUIRED",
    "KILL_SWITCH_BLOCKED",
    "EXECUTION_CONTROL_BLOCKED",
    "SUPERVISED_DEMO_ORDER_READY",
    "DEFAULT_RUNTIME_ALLOWED_MODES",
    "RUNTIME_MODE_DRY_RUN",
]
