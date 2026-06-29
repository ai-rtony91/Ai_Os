"""Repo-safe Forex execution-readiness lane contract."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


LANE_STATUS_PROOF_PREREQUISITES_INCOMPLETE = "PROOF_PREREQUISITES_INCOMPLETE"
LANE_STATUS_BROKER_READ_ONLY_PREP_REQUIRED = "BROKER_READ_ONLY_PREP_REQUIRED"
LANE_STATUS_CREDENTIAL_PERSISTENCE_REQUIRED = "CREDENTIAL_PERSISTENCE_REQUIRED"
LANE_STATUS_EXECUTION_CONTROLS_REQUIRED = "EXECUTION_CONTROLS_REQUIRED"
LANE_STATUS_SUPERVISED_DEMO_APPROVAL_REQUIRED = "SUPERVISED_DEMO_APPROVAL_REQUIRED"
LANE_STATUS_CONTROLLED_DEMO_EXECUTION_READY = "CONTROLLED_DEMO_EXECUTION_READY"
LANE_STATUS_CONTROLLED_MICRO_LIVE_EXCEPTION_READY = "CONTROLLED_MICRO_LIVE_EXCEPTION_READY"

STAGE_REPO_SAFE_PROOF = "repo_safe_proof"
STAGE_EXECUTION_READINESS = "execution_readiness"
STAGE_SUPERVISED_DEMO_READINESS = "supervised_demo_readiness"
STAGE_SUPERVISED_DEMO_EXECUTION = "supervised_demo_execution"
STAGE_MICRO_LIVE_EXCEPTION_READINESS = "micro_live_exception_readiness"

NEXT_PROOF_PREREQUISITES = "complete_proof_prerequisites"
NEXT_BROKER_READ_ONLY_STATE_PROBE = "broker_read_only_state_probe"
NEXT_CREDENTIAL_PERSISTENCE_OWNER_HANDOFF = "credential_persistence_owner_handoff"
NEXT_EXECUTION_CONTROL_STACK = "execution_control_stack"
NEXT_OWNER_SUPERVISED_DEMO_APPROVAL = "owner_supervised_demo_approval"
NEXT_CONTROLLED_DEMO_EXECUTION_EVIDENCE = "controlled_demo_execution_evidence"
NEXT_SINGLE_MICRO_LIVE_EXCEPTION_PACKET = "single_micro_live_exception_packet"

STATE_NAME = "AIOS_FOREX_LIVE_EXECUTION_READINESS_LANE_V1_STATE.json"
REPORT_NAME = "AIOS_FOREX_LIVE_EXECUTION_READINESS_LANE_V1_REPORT.md"

DEFAULT_SESSION_WINDOW_HOURS = 22
DEFAULT_SESSION_WINDOW_DAYS_PER_WEEK = 6

PACKET_ID = "PKT-FOREX-LIVE-EXECUTION-READINESS-LANE-V1"
MODULE_NAME = "forex_live_execution_readiness_lane_v1"


@dataclass(frozen=True)
class ExecutionReadinessInput:
    forex_110_closed: bool
    persistent_profitability_ready: bool
    walkforward_oos_proven: bool
    broker_read_only_config_present: bool
    broker_credentials_available_to_runtime: bool
    owner_demo_approval: bool
    owner_micro_live_exception_approval: bool
    kill_switch_defined: bool
    max_daily_loss_defined: bool
    max_trade_risk_defined: bool
    duplicate_order_guard_defined: bool
    audit_log_defined: bool
    session_window_hours: int
    session_window_days_per_week: int


@dataclass(frozen=True)
class ExecutionReadinessResult:
    lane_status: str
    current_stage: str
    next_stage: str
    blockers: tuple[str, ...]
    broker_api_used: bool
    credentials_read: bool
    env_read: bool
    order_execution: bool
    demo_authorized: bool
    live_authorized: bool
    autonomous_22h_6d_authorized: bool
    safe_next_action: str


def build_default_execution_readiness_input() -> ExecutionReadinessInput:
    """Return the default current-state input required by this lane."""

    return ExecutionReadinessInput(
        forex_110_closed=True,
        persistent_profitability_ready=True,
        walkforward_oos_proven=True,
        broker_read_only_config_present=False,
        broker_credentials_available_to_runtime=False,
        owner_demo_approval=False,
        owner_micro_live_exception_approval=False,
        kill_switch_defined=False,
        max_daily_loss_defined=False,
        max_trade_risk_defined=False,
        duplicate_order_guard_defined=False,
        audit_log_defined=False,
        session_window_hours=DEFAULT_SESSION_WINDOW_HOURS,
        session_window_days_per_week=DEFAULT_SESSION_WINDOW_DAYS_PER_WEEK,
    )


def evaluate_live_execution_readiness(
    input_state: ExecutionReadinessInput,
) -> ExecutionReadinessResult:
    """Evaluate repo-safe readiness state transitions for the lane."""

    if not _proof_prerequisites_complete(input_state):
        return _build_result(
            LANE_STATUS_PROOF_PREREQUISITES_INCOMPLETE,
            STAGE_REPO_SAFE_PROOF,
            NEXT_PROOF_PREREQUISITES,
            tuple(_proof_missing_blockers(input_state)),
            "Resolve Forex 110 proof prerequisites before execution lane progression.",
        )

    if not input_state.broker_read_only_config_present:
        return _build_result(
            LANE_STATUS_BROKER_READ_ONLY_PREP_REQUIRED,
            STAGE_EXECUTION_READINESS,
            NEXT_BROKER_READ_ONLY_STATE_PROBE,
            ("broker_read_only_config_present is False",),
            "Prepare the broker read-only state probe path and retry.",
        )

    if not input_state.broker_credentials_available_to_runtime:
        return _build_result(
            LANE_STATUS_CREDENTIAL_PERSISTENCE_REQUIRED,
            STAGE_EXECUTION_READINESS,
            NEXT_CREDENTIAL_PERSISTENCE_OWNER_HANDOFF,
            ("broker_credentials_available_to_runtime is False",),
            "Perform owner handoff for credential persistence approval.",
        )

    if not _execution_controls_complete(input_state):
        return _build_result(
            LANE_STATUS_EXECUTION_CONTROLS_REQUIRED,
            STAGE_EXECUTION_READINESS,
            NEXT_EXECUTION_CONTROL_STACK,
            _execution_control_blockers(input_state),
            "Build the execution control stack, including kill switch and audit controls.",
        )

    if not input_state.owner_demo_approval:
        return _build_result(
            LANE_STATUS_SUPERVISED_DEMO_APPROVAL_REQUIRED,
            STAGE_SUPERVISED_DEMO_READINESS,
            NEXT_OWNER_SUPERVISED_DEMO_APPROVAL,
            ("owner_demo_approval is False",),
            "Obtain owner supervised-demo approval before any demo-run evidence.",
        )

    if not input_state.owner_micro_live_exception_approval:
        return _build_result(
            LANE_STATUS_CONTROLLED_DEMO_EXECUTION_READY,
            STAGE_SUPERVISED_DEMO_EXECUTION,
            NEXT_CONTROLLED_DEMO_EXECUTION_EVIDENCE,
            ("owner_micro_live_exception_approval is False",),
            "Complete controlled demo execution evidence and collect micro-live exception evidence.",
        )

    return _build_result(
        LANE_STATUS_CONTROLLED_MICRO_LIVE_EXCEPTION_READY,
        STAGE_MICRO_LIVE_EXCEPTION_READINESS,
        NEXT_SINGLE_MICRO_LIVE_EXCEPTION_PACKET,
        tuple(),
        "Prepare the controlled micro-live exception packet with explicit owner handoff.",
    )


def run_forex_live_execution_readiness_lane_v1(
    input_state: ExecutionReadinessInput | None = None,
) -> dict[str, Any]:
    """Return payload for runner output and artifacts."""

    active_state = input_state or build_default_execution_readiness_input()
    result = evaluate_live_execution_readiness(active_state)
    return {
        "packet_id": PACKET_ID,
        "module": MODULE_NAME,
        "input": asdict(active_state),
        "result": result_to_jsonable_dict(result),
        "report": build_report(active_state, result),
    }


def result_to_jsonable_dict(result: ExecutionReadinessResult) -> dict[str, Any]:
    """Convert execution-readiness result to JSON-safe output."""

    return {
        "lane_status": result.lane_status,
        "current_stage": result.current_stage,
        "next_stage": result.next_stage,
        "blockers": list(result.blockers),
        "broker_api_used": result.broker_api_used,
        "credentials_read": result.credentials_read,
        "env_read": result.env_read,
        "order_execution": result.order_execution,
        "demo_authorized": result.demo_authorized,
        "live_authorized": result.live_authorized,
        "autonomous_22h_6d_authorized": result.autonomous_22h_6d_authorized,
        "safe_next_action": result.safe_next_action,
    }


def build_report(input_state: ExecutionReadinessInput, result: ExecutionReadinessResult) -> str:
    """Build the lane report body used by the runner."""
    if result.blockers:
        blocker_lines = [f"- {blocker}" for blocker in result.blockers]
    else:
        blocker_lines = ["- none"]
    lines = [
        "# AIOS Forex Live Execution Readiness Lane V1",
        "",
        "## Current lane evaluation",
        f"- packet_id: {PACKET_ID}",
        f"- lane_status: {result.lane_status}",
        f"- current_stage: {result.current_stage}",
        f"- next_stage: {result.next_stage}",
        f"- session_window_hours: {input_state.session_window_hours}",
        f"- session_window_days_per_week: {input_state.session_window_days_per_week}",
        f"- demo_authorized: {result.demo_authorized}",
        f"- live_authorized: {result.live_authorized}",
        f"- autonomous_22h_6d_authorized: {result.autonomous_22h_6d_authorized}",
        f"- safe_next_action: {result.safe_next_action}",
        "",
        "## Blockers",
        *blocker_lines,
        "",
        "## Repo-safe guarantees applied in this module",
        "- broker_api_used: false",
        "- credentials_read: false",
        "- env_read: false",
        "- order_execution: false",
        "- demo_authorized: false",
        "- live_authorized: false",
        "- autonomous_22h_6d_authorized: false",
        "",
        "## Target path",
        "- supervised demo -> controlled micro-live exception -> 22hr/day, 6day/week autonomous execution.",
    ]

    return "\n".join(lines) + "\n"


def _proof_prerequisites_complete(input_state: ExecutionReadinessInput) -> bool:
    return bool(
        input_state.forex_110_closed
        and input_state.persistent_profitability_ready
        and input_state.walkforward_oos_proven
    )


def _proof_missing_blockers(input_state: ExecutionReadinessInput) -> list[str]:
    blockers: list[str] = []
    if not input_state.forex_110_closed:
        blockers.append("forex_110_closed is False")
    if not input_state.persistent_profitability_ready:
        blockers.append("persistent_profitability_ready is False")
    if not input_state.walkforward_oos_proven:
        blockers.append("walkforward_oos_proven is False")
    return blockers


def _execution_controls_complete(input_state: ExecutionReadinessInput) -> bool:
    return (
        input_state.kill_switch_defined
        and input_state.max_daily_loss_defined
        and input_state.max_trade_risk_defined
        and input_state.duplicate_order_guard_defined
        and input_state.audit_log_defined
        and input_state.session_window_hours == DEFAULT_SESSION_WINDOW_HOURS
        and input_state.session_window_days_per_week == DEFAULT_SESSION_WINDOW_DAYS_PER_WEEK
    )


def _execution_control_blockers(input_state: ExecutionReadinessInput) -> tuple[str, ...]:
    blockers: list[str] = []
    if not input_state.kill_switch_defined:
        blockers.append("kill_switch_defined is False")
    if not input_state.max_daily_loss_defined:
        blockers.append("max_daily_loss_defined is False")
    if not input_state.max_trade_risk_defined:
        blockers.append("max_trade_risk_defined is False")
    if not input_state.duplicate_order_guard_defined:
        blockers.append("duplicate_order_guard_defined is False")
    if not input_state.audit_log_defined:
        blockers.append("audit_log_defined is False")
    if input_state.session_window_hours != DEFAULT_SESSION_WINDOW_HOURS:
        blockers.append("session_window_hours must be 22")
    if input_state.session_window_days_per_week != DEFAULT_SESSION_WINDOW_DAYS_PER_WEEK:
        blockers.append("session_window_days_per_week must be 6")
    return tuple(_dedupe(blockers))


def _build_result(
    lane_status: str,
    current_stage: str,
    next_stage: str,
    blockers: tuple[str, ...],
    safe_next_action: str,
) -> ExecutionReadinessResult:
    return ExecutionReadinessResult(
        lane_status=lane_status,
        current_stage=current_stage,
        next_stage=next_stage,
        blockers=_dedupe(blockers),
        broker_api_used=False,
        credentials_read=False,
        env_read=False,
        order_execution=False,
        demo_authorized=False,
        live_authorized=False,
        autonomous_22h_6d_authorized=False,
        safe_next_action=safe_next_action,
    )


def _dedupe(items: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(items))
