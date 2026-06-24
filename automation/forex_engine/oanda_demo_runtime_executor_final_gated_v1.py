from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-RUNTIME-EXECUTOR-FINAL-GATED-V1"
EXECUTOR_VERSION = "v1"

FINAL_GATED_BLOCKED_MISSING_DRYRUN = "FINAL_GATED_BLOCKED_MISSING_DRYRUN"
FINAL_GATED_BLOCKED_DRYRUN_NOT_READY = "FINAL_GATED_BLOCKED_DRYRUN_NOT_READY"
FINAL_GATED_BLOCKED_FINAL_CLICK = "FINAL_GATED_BLOCKED_FINAL_CLICK"
FINAL_GATED_BLOCKED_RUNTIME_CONTEXT = "FINAL_GATED_BLOCKED_RUNTIME_CONTEXT"
FINAL_GATED_BLOCKED_CONTROLS = "FINAL_GATED_BLOCKED_CONTROLS"
FINAL_GATED_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTOR_PACKET = (
    "FINAL_GATED_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTOR_PACKET"
)
FINAL_GATED_REJECTED = "FINAL_GATED_REJECTED"

DRYRUN_READY_STATUS = "DRYRUN_READY_FOR_OWNER_REVIEW"
DRYRUN_PAYLOAD_STATUS = "DRYRUN_ONLY_NOT_EXECUTABLE"
FINAL_CLICK_READY_STATUS = "FINAL_CLICK_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTION_REVIEW"
PREPARED_ORDER_REVIEW_STATUS = "READY_FOR_EXTERNAL_RUNTIME_EXECUTOR_REVIEW_ONLY"
RUNTIME_PACKAGE_STATUS = "READY_FOR_SEPARATE_RUNTIME_EXECUTOR_PACKET"

EXECUTION_AUTHORITY_FIELDS = (
    "execution_allowed",
    "demo_order_allowed",
    "live_order_allowed",
    "broker_write_allowed",
    "autonomous_order_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
)


def evaluate_oanda_demo_runtime_executor_final_gated_v1(
    dryrun_result: dict | None = None,
    final_owner_click_result: dict | None = None,
    runtime_context: dict | None = None,
    final_gate_controls: dict | None = None,
) -> dict:
    dryrun = _mapping(dryrun_result)
    if not dryrun:
        return _result(
            status=FINAL_GATED_BLOCKED_MISSING_DRYRUN,
            blockers=["missing_dryrun_result"],
            warnings=_warnings(FINAL_GATED_BLOCKED_MISSING_DRYRUN),
            dryrun=dryrun,
            final_click=_mapping(final_owner_click_result),
            runtime_context=_mapping(runtime_context),
            controls=_mapping(final_gate_controls),
        )

    final_click = _mapping(final_owner_click_result)
    runtime = _mapping(runtime_context)
    controls = _mapping(final_gate_controls)

    unsafe_blockers = _unsafe_execution_blockers(dryrun, final_click, runtime, controls)
    dryrun_blockers = _dryrun_blockers(dryrun)
    final_click_blockers = _final_click_blockers(final_click)
    runtime_blockers = _runtime_context_blockers(runtime)
    control_blockers = _control_blockers(controls)

    blockers = _unique(
        unsafe_blockers
        + dryrun_blockers
        + final_click_blockers
        + runtime_blockers
        + control_blockers
    )
    status = _status(
        unsafe_blockers=unsafe_blockers,
        dryrun_blockers=dryrun_blockers,
        final_click_blockers=final_click_blockers,
        runtime_blockers=runtime_blockers,
        control_blockers=control_blockers,
    )

    return _result(
        status=status,
        blockers=blockers,
        warnings=_warnings(status),
        dryrun=dryrun,
        final_click=final_click,
        runtime_context=runtime,
        controls=controls,
    )


def _status(
    *,
    unsafe_blockers: list[str],
    dryrun_blockers: list[str],
    final_click_blockers: list[str],
    runtime_blockers: list[str],
    control_blockers: list[str],
) -> str:
    if unsafe_blockers:
        return FINAL_GATED_REJECTED
    if dryrun_blockers:
        return FINAL_GATED_BLOCKED_DRYRUN_NOT_READY
    if final_click_blockers:
        return FINAL_GATED_BLOCKED_FINAL_CLICK
    if runtime_blockers:
        return FINAL_GATED_BLOCKED_RUNTIME_CONTEXT
    if control_blockers:
        return FINAL_GATED_BLOCKED_CONTROLS
    return FINAL_GATED_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTOR_PACKET


def _dryrun_blockers(dryrun: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if dryrun.get("status") != DRYRUN_READY_STATUS:
        blockers.append("dryrun_status_not_ready_for_owner_review")
    payload = _mapping(dryrun.get("dryrun_order_payload"))
    if payload.get("status") != DRYRUN_PAYLOAD_STATUS:
        blockers.append("dryrun_order_payload_status_not_dryrun_only")
    if not _steps_stop_before_broker_call(dryrun.get("simulated_execution_steps")):
        blockers.append("dryrun_steps_must_stop_before_broker_call")
    blockers.extend(_authority_blockers(dryrun, "dryrun"))
    return blockers


def _final_click_blockers(final_click: Mapping[str, Any]) -> list[str]:
    if not final_click:
        return ["missing_final_owner_click_result"]

    blockers: list[str] = []
    if final_click.get("status") != FINAL_CLICK_READY_STATUS:
        blockers.append("final_owner_click_status_not_ready")
    prepared = _mapping(final_click.get("prepared_order_review"))
    if prepared.get("status") != PREPARED_ORDER_REVIEW_STATUS:
        blockers.append("prepared_order_review_status_not_ready")
    blockers.extend(_authority_blockers(final_click, "final_owner_click"))
    return blockers


def _runtime_context_blockers(runtime: Mapping[str, Any]) -> list[str]:
    if not runtime:
        return ["missing_runtime_context"]

    required_true = (
        "demo_environment",
        "runtime_only_credentials_present",
        "kill_switch_ready",
        "daily_stop_ready",
        "max_loss_gate_ready",
    )
    required_false = (
        "live_environment",
        "credential_persistence_detected",
        "account_id_persistence_detected",
        "broker_network_call_performed",
        "order_placement_performed",
    )

    blockers: list[str] = []
    if runtime.get("broker") != "OANDA_DEMO":
        blockers.append("runtime_context_broker_must_be_oanda_demo")
    if runtime.get("environment") != "DEMO":
        blockers.append("runtime_context_environment_must_be_demo")
    for field in required_true:
        if not _bool(runtime.get(field)):
            blockers.append(f"runtime_context_{field}_required")
    for field in required_false:
        if _bool(runtime.get(field)):
            blockers.append(f"runtime_context_{field}_must_be_false")
    blockers.extend(_authority_blockers(runtime, "runtime_context"))
    return blockers


def _control_blockers(controls: Mapping[str, Any]) -> list[str]:
    if not controls:
        return ["missing_final_gate_controls"]

    required_true = (
        "final_runtime_packet_required",
        "owner_runtime_confirmation_required",
        "require_runtime_executor_packet_next",
        "require_pre_trade_evidence",
        "require_post_trade_evidence",
    )
    required_false = (
        "allow_live_trading",
        "allow_autonomous_execution",
        "allow_scheduler",
        "allow_daemon",
        "allow_webhook",
        "allow_order_placement_in_this_module",
    )

    blockers: list[str] = []
    for field in required_true:
        if not _bool(controls.get(field)):
            blockers.append(f"final_gate_controls_{field}_required")
    for field in required_false:
        if _bool(controls.get(field)):
            blockers.append(f"final_gate_controls_{field}_must_be_false")
    blockers.extend(_authority_blockers(controls, "final_gate_controls"))
    return blockers


def _result(
    *,
    status: str,
    blockers: list[str],
    warnings: list[str],
    dryrun: Mapping[str, Any],
    final_click: Mapping[str, Any],
    runtime_context: Mapping[str, Any],
    controls: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "packet_id": PACKET_ID,
        "executor_version": EXECUTOR_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "final_gate_summary": _final_gate_summary(controls),
        "runtime_context_summary": _runtime_context_summary(runtime_context),
        "prepared_runtime_package": _prepared_runtime_package(status, dryrun, final_click),
        "required_runtime_actions": _required_runtime_actions(status),
        "required_owner_actions": _required_owner_actions(status, _prepared_order_review(final_click)),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }


def _prepared_runtime_package(
    status: str,
    dryrun: Mapping[str, Any],
    final_click: Mapping[str, Any],
) -> dict[str, Any]:
    prepared_order = _prepared_order_review(final_click)
    dryrun_payload = _mapping(dryrun.get("dryrun_order_payload"))
    source = prepared_order if prepared_order else dryrun_payload

    package = {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "package_status": "NOT_READY",
        "demo_only": True,
        "live_trading_allowed": False,
        "autonomous_execution_allowed": False,
        "order_placement_allowed_in_this_module": False,
        "runtime_credentials_required": True,
        "credential_persistence_allowed": False,
        "account_id_persistence_allowed": False,
        "hard_stop_loss_required": True,
        "hard_take_profit_required": True,
        "pre_trade_evidence_required": True,
        "post_trade_evidence_required": True,
        "instrument": source.get("instrument"),
        "direction": source.get("direction"),
        "order_type": source.get("order_type"),
        "time_in_force": source.get("time_in_force"),
        "planned_entry": source.get("planned_entry"),
        "stop_loss": source.get("stop_loss"),
        "take_profit": source.get("take_profit"),
        "position_size_units": source.get("position_size_units"),
        "risk_amount": source.get("risk_amount"),
        "reward_risk_ratio": source.get("reward_risk_ratio"),
        "hold_allowed_overnight": _bool(source.get("hold_allowed_overnight")),
    }
    if status == FINAL_GATED_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTOR_PACKET:
        package["package_status"] = RUNTIME_PACKAGE_STATUS
    return package


def _final_gate_summary(controls: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "final_runtime_packet_required": _bool(controls.get("final_runtime_packet_required")),
        "owner_runtime_confirmation_required": _bool(
            controls.get("owner_runtime_confirmation_required")
        ),
        "allow_live_trading": _bool(controls.get("allow_live_trading")),
        "allow_autonomous_execution": _bool(controls.get("allow_autonomous_execution")),
        "allow_scheduler": _bool(controls.get("allow_scheduler")),
        "allow_daemon": _bool(controls.get("allow_daemon")),
        "allow_webhook": _bool(controls.get("allow_webhook")),
        "allow_order_placement_in_this_module": _bool(
            controls.get("allow_order_placement_in_this_module")
        ),
        "require_runtime_executor_packet_next": _bool(
            controls.get("require_runtime_executor_packet_next")
        ),
        "require_pre_trade_evidence": _bool(controls.get("require_pre_trade_evidence")),
        "require_post_trade_evidence": _bool(controls.get("require_post_trade_evidence")),
    }


def _runtime_context_summary(runtime: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker": _text(runtime.get("broker"), "MISSING"),
        "environment": _text(runtime.get("environment"), "MISSING"),
        "demo_environment": _bool(runtime.get("demo_environment")),
        "live_environment": _bool(runtime.get("live_environment")),
        "runtime_only_credentials_present": _bool(
            runtime.get("runtime_only_credentials_present")
        ),
        "credential_persistence_detected": _bool(
            runtime.get("credential_persistence_detected")
        ),
        "account_id_persistence_detected": _bool(
            runtime.get("account_id_persistence_detected")
        ),
        "kill_switch_ready": _bool(runtime.get("kill_switch_ready")),
        "daily_stop_ready": _bool(runtime.get("daily_stop_ready")),
        "max_loss_gate_ready": _bool(runtime.get("max_loss_gate_ready")),
        "broker_network_call_performed": _bool(runtime.get("broker_network_call_performed")),
        "order_placement_performed": _bool(runtime.get("order_placement_performed")),
    }


def _required_runtime_actions(status: str) -> list[str]:
    actions = [
        "run separate one-order-only runtime executor packet",
        "inject OANDA demo credentials runtime-only outside repo",
        "verify OANDA demo account, not live",
        "attach hard stop loss before execution",
        "attach hard take profit before execution",
        "capture sanitized pre-trade evidence",
        "capture sanitized post-trade evidence",
        "stop after one order attempt",
    ]
    if status != FINAL_GATED_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTOR_PACKET:
        return ["repair blocked final-gated runtime package inputs"] + actions
    return actions


def _required_owner_actions(status: str, prepared_order: Mapping[str, Any]) -> list[str]:
    actions = [
        "approve separate runtime executor packet",
        "confirm demo-only environment",
        "confirm no live money",
        "confirm one order only",
        "confirm stop loss and take profit",
        "confirm overnight hold if applicable",
    ]
    if status != FINAL_GATED_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTOR_PACKET:
        return ["repair owner/runtime confirmations before final-gated package review"] + actions
    if not _bool(prepared_order.get("hold_allowed_overnight")):
        return actions
    return actions


def _unsafe_execution_blockers(*payloads: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for index, payload in enumerate(payloads):
        blockers.extend(_authority_blockers(payload, f"payload_{index}"))
    return blockers


def _authority_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []
    authority = _mapping(payload.get("execution_authority"))
    for field in EXECUTION_AUTHORITY_FIELDS:
        if _bool(payload.get(field)) or _bool(authority.get(field)):
            blockers.append(f"unsafe_{label}_{field}_true")
    return blockers


def _steps_stop_before_broker_call(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    return _text(value[-1]).lower() == "stop before broker call"


def _prepared_order_review(final_click: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(final_click.get("prepared_order_review"))


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _warnings(status: str) -> list[str]:
    warnings = [
        "final_gated_package_only",
        "execution_authority_false",
        "no_broker_call_performed",
        "no_credentials_or_account_ids_read_or_persisted",
        "no_order_placement_performed",
    ]
    if status == FINAL_GATED_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTOR_PACKET:
        warnings.append("separate_one_order_only_runtime_executor_packet_required")
    return warnings


def _next_safe_action(status: str) -> str:
    return {
        FINAL_GATED_BLOCKED_MISSING_DRYRUN: "provide_ready_runtime_executor_dryrun_result",
        FINAL_GATED_BLOCKED_DRYRUN_NOT_READY: "repair_runtime_executor_dryrun_before_final_gate",
        FINAL_GATED_BLOCKED_FINAL_CLICK: "provide_ready_final_owner_click_result",
        FINAL_GATED_BLOCKED_RUNTIME_CONTEXT: "provide_demo_only_runtime_context_with_runtime_credentials_present_but_not_persisted",
        FINAL_GATED_BLOCKED_CONTROLS: "provide_final_gate_controls_that_block_live_autonomy_and_order_placement",
        FINAL_GATED_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTOR_PACKET: (
            "owner_review_separate_one_order_only_runtime_executor_packet"
        ),
        FINAL_GATED_REJECTED: "remove_execution_authority_request_before_final_gate_review",
    }.get(status, "stop_and_review_final_gated_executor_state")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
