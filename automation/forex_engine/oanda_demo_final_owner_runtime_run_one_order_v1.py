from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-FINAL-OWNER-RUNTIME-RUN-ONE-ORDER-V1"
RUNTIME_RUN_VERSION = "v1"

OWNER_RUN_BLOCKED_MISSING_FINAL_WIRE = "OWNER_RUN_BLOCKED_MISSING_FINAL_WIRE"
OWNER_RUN_BLOCKED_FINAL_WIRE_NOT_READY = "OWNER_RUN_BLOCKED_FINAL_WIRE_NOT_READY"
OWNER_RUN_BLOCKED_OWNER_APPROVAL = "OWNER_RUN_BLOCKED_OWNER_APPROVAL"
OWNER_RUN_BLOCKED_RUNTIME_CONTEXT = "OWNER_RUN_BLOCKED_RUNTIME_CONTEXT"
OWNER_RUN_READY_FOR_EXPLICIT_MANUAL_COMMAND = (
    "OWNER_RUN_READY_FOR_EXPLICIT_MANUAL_COMMAND"
)
OWNER_RUN_REJECTED = "OWNER_RUN_REJECTED"

FINAL_WIRE_READY_STATUS = (
    "FINAL_WIRE_READY_FOR_MANUAL_ONE_ORDER_DEMO_RUNTIME_ATTEMPT"
)
FINAL_WIRE_REQUEST_READY_STATUS = "READY_FOR_MANUAL_RUNTIME_INVOCATION"

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

OWNER_APPROVAL_REQUIRED_TRUE_FIELDS = (
    "owner_approved_final_manual_runtime_run",
    "owner_confirmed_demo_only",
    "owner_confirmed_no_live_money",
    "owner_confirmed_one_order_only",
    "owner_confirmed_max_one_attempt",
    "owner_confirmed_stop_loss",
    "owner_confirmed_take_profit",
    "owner_confirmed_loss_possible",
    "owner_confirmed_no_profit_guarantee",
    "owner_confirmed_no_second_order",
    "owner_confirmed_manual_run_only",
    "owner_confirmed_no_autonomous_execution",
    "owner_confirmed_post_trade_evidence_required",
)

RUNTIME_CONTEXT_REQUIRED_TRUE_FIELDS = (
    "demo_environment",
    "runtime_credentials_external",
    "one_order_only",
    "kill_switch_ready",
    "daily_stop_ready",
    "max_loss_gate_ready",
    "pre_trade_evidence_ready",
    "post_trade_evidence_plan_ready",
)

RUNTIME_CONTEXT_REQUIRED_FALSE_FIELDS = (
    "live_environment",
    "credential_persistence_detected",
    "account_id_persistence_detected",
    "order_already_attempted",
    "broker_network_call_performed",
    "order_placement_performed",
)

PRE_RUN_CHECKLIST_ITEMS = (
    "final_wire_ready_for_manual_runtime_invocation",
    "owner_approved_final_manual_runtime_run",
    "demo_environment_confirmed",
    "no_live_money_confirmed",
    "one_order_only_confirmed",
    "max_one_attempt_confirmed",
    "stop_loss_confirmed",
    "take_profit_confirmed",
    "loss_possible_confirmed",
    "no_profit_guarantee_confirmed",
    "no_second_order_confirmed",
    "manual_run_only_confirmed",
    "runtime_credentials_external",
    "credential_persistence_not_detected",
    "account_id_persistence_not_detected",
    "existing_open_orders_zero",
    "existing_pending_orders_zero",
    "order_not_already_attempted",
    "kill_switch_ready",
    "daily_stop_ready",
    "max_loss_gate_ready",
    "pre_trade_evidence_ready",
    "post_trade_evidence_plan_ready",
)

POST_RUN_EVIDENCE_ITEMS = (
    "manual_command_invoked_by_owner",
    "broker_environment_demo_only",
    "single_order_attempt_result",
    "sanitized_order_reference",
    "filled_or_rejected_status",
    "stop_loss_attachment_status",
    "take_profit_attachment_status",
    "post_attempt_open_orders",
    "post_attempt_pending_orders",
    "post_trade_balance_or_nav_snapshot",
    "sanitized_timestamp_utc",
    "no_credentials_or_account_ids_persisted",
    "no_second_order_attempted",
)


def evaluate_oanda_demo_final_owner_runtime_run_one_order_v1(
    final_wire_result: dict | None = None,
    owner_runtime_run_approval: dict | None = None,
    runtime_run_context: dict | None = None,
) -> dict:
    final_wire = _mapping(final_wire_result)
    owner_approval = _mapping(owner_runtime_run_approval)
    runtime_context = _mapping(runtime_run_context)

    if not final_wire:
        return _result(
            status=OWNER_RUN_BLOCKED_MISSING_FINAL_WIRE,
            blockers=["missing_final_wire_result"],
            warnings=_warnings(OWNER_RUN_BLOCKED_MISSING_FINAL_WIRE),
            final_wire=final_wire,
            owner_approval=owner_approval,
            runtime_context=runtime_context,
        )

    unsafe_blockers = _unsafe_execution_blockers(
        final_wire,
        _mapping(final_wire.get("final_wire_request")),
        owner_approval,
        runtime_context,
    )
    final_wire_blockers = _final_wire_blockers(final_wire)
    owner_blockers = _owner_approval_blockers(owner_approval)
    runtime_context_blockers = _runtime_context_blockers(runtime_context)

    blockers = _unique(
        unsafe_blockers
        + final_wire_blockers
        + owner_blockers
        + runtime_context_blockers
    )
    status = _status(
        unsafe_blockers=unsafe_blockers,
        final_wire_blockers=final_wire_blockers,
        owner_blockers=owner_blockers,
        runtime_context_blockers=runtime_context_blockers,
    )

    return _result(
        status=status,
        blockers=blockers,
        warnings=_warnings(status),
        final_wire=final_wire,
        owner_approval=owner_approval,
        runtime_context=runtime_context,
    )


def _status(
    *,
    unsafe_blockers: list[str],
    final_wire_blockers: list[str],
    owner_blockers: list[str],
    runtime_context_blockers: list[str],
) -> str:
    if unsafe_blockers:
        return OWNER_RUN_REJECTED
    if final_wire_blockers:
        return OWNER_RUN_BLOCKED_FINAL_WIRE_NOT_READY
    if owner_blockers:
        return OWNER_RUN_BLOCKED_OWNER_APPROVAL
    if runtime_context_blockers:
        return OWNER_RUN_BLOCKED_RUNTIME_CONTEXT
    return OWNER_RUN_READY_FOR_EXPLICIT_MANUAL_COMMAND


def _final_wire_blockers(final_wire: Mapping[str, Any]) -> list[str]:
    request = _mapping(final_wire.get("final_wire_request"))
    blockers: list[str] = []
    if final_wire.get("status") != FINAL_WIRE_READY_STATUS:
        blockers.append("final_wire_status_not_ready")
    if request.get("status") != FINAL_WIRE_REQUEST_READY_STATUS:
        blockers.append("final_wire_request_status_not_ready")
    if not _bool(request.get("one_order_only")):
        blockers.append("final_wire_request_one_order_only_required")
    if _number(request.get("max_order_attempts"), -1) != 1:
        blockers.append("final_wire_request_max_order_attempts_must_be_one")
    if _bool(request.get("live_trading_allowed")):
        blockers.append("final_wire_request_live_trading_allowed_must_be_false")
    if _bool(request.get("autonomous_execution_allowed")):
        blockers.append(
            "final_wire_request_autonomous_execution_allowed_must_be_false"
        )
    blockers.extend(_authority_blockers(final_wire, "final_wire_result"))
    return blockers


def _owner_approval_blockers(owner_approval: Mapping[str, Any]) -> list[str]:
    if not owner_approval:
        return ["missing_owner_runtime_run_approval"]

    blockers: list[str] = []
    for field in OWNER_APPROVAL_REQUIRED_TRUE_FIELDS:
        if not _bool(owner_approval.get(field)):
            blockers.append(f"{field}_required")
    blockers.extend(_authority_blockers(owner_approval, "owner_approval"))
    return blockers


def _runtime_context_blockers(runtime_context: Mapping[str, Any]) -> list[str]:
    if not runtime_context:
        return ["missing_runtime_run_context"]

    blockers: list[str] = []
    if runtime_context.get("broker") != "OANDA_DEMO":
        blockers.append("runtime_context_broker_must_be_oanda_demo")
    if runtime_context.get("environment") != "DEMO":
        blockers.append("runtime_context_environment_must_be_demo")
    for field in RUNTIME_CONTEXT_REQUIRED_TRUE_FIELDS:
        if not _bool(runtime_context.get(field)):
            blockers.append(f"runtime_context_{field}_required")
    for field in RUNTIME_CONTEXT_REQUIRED_FALSE_FIELDS:
        if _bool(runtime_context.get(field)):
            blockers.append(f"runtime_context_{field}_must_be_false")
    if _number(runtime_context.get("max_order_attempts"), -1) != 1:
        blockers.append("runtime_context_max_order_attempts_must_be_one")
    if _number(runtime_context.get("existing_open_orders"), -1) != 0:
        blockers.append("runtime_context_existing_open_orders_must_be_zero")
    if _number(runtime_context.get("existing_pending_orders"), -1) != 0:
        blockers.append("runtime_context_existing_pending_orders_must_be_zero")
    blockers.extend(_authority_blockers(runtime_context, "runtime_context"))
    return blockers


def _result(
    *,
    status: str,
    blockers: list[str],
    warnings: list[str],
    final_wire: Mapping[str, Any],
    owner_approval: Mapping[str, Any],
    runtime_context: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "packet_id": PACKET_ID,
        "runtime_run_version": RUNTIME_RUN_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "final_wire_summary": _final_wire_summary(final_wire),
        "owner_approval_summary": _owner_approval_summary(owner_approval),
        "runtime_run_context_summary": _runtime_context_summary(runtime_context),
        "manual_runtime_run_contract": _manual_runtime_run_contract(status),
        "pre_run_checklist": _pre_run_checklist(status),
        "post_run_evidence_plan": _post_run_evidence_plan(status),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }


def _final_wire_summary(final_wire: Mapping[str, Any]) -> dict[str, Any]:
    request = _mapping(final_wire.get("final_wire_request"))
    return {
        "status": _text(final_wire.get("status"), "MISSING"),
        "final_wire_request_status": _text(request.get("status"), "MISSING"),
        "one_order_only": _bool(request.get("one_order_only")),
        "max_order_attempts": _number(request.get("max_order_attempts"), 0),
        "live_trading_allowed": _bool(request.get("live_trading_allowed")),
        "autonomous_execution_allowed": _bool(
            request.get("autonomous_execution_allowed")
        ),
        "execution_authority_false": not _authority_blockers(
            final_wire, "final_wire_result"
        ),
    }


def _owner_approval_summary(owner_approval: Mapping[str, Any]) -> dict[str, bool]:
    return {
        field: _bool(owner_approval.get(field))
        for field in OWNER_APPROVAL_REQUIRED_TRUE_FIELDS
    }


def _runtime_context_summary(runtime_context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker": _text(runtime_context.get("broker"), "MISSING"),
        "environment": _text(runtime_context.get("environment"), "MISSING"),
        "live_environment": _bool(runtime_context.get("live_environment")),
        "demo_environment": _bool(runtime_context.get("demo_environment")),
        "runtime_credentials_external": _bool(
            runtime_context.get("runtime_credentials_external")
        ),
        "credential_persistence_detected": _bool(
            runtime_context.get("credential_persistence_detected")
        ),
        "account_id_persistence_detected": _bool(
            runtime_context.get("account_id_persistence_detected")
        ),
        "one_order_only": _bool(runtime_context.get("one_order_only")),
        "max_order_attempts": _number(runtime_context.get("max_order_attempts"), 0),
        "order_already_attempted": _bool(
            runtime_context.get("order_already_attempted")
        ),
        "existing_open_orders": _number(runtime_context.get("existing_open_orders"), 0),
        "existing_pending_orders": _number(
            runtime_context.get("existing_pending_orders"), 0
        ),
        "kill_switch_ready": _bool(runtime_context.get("kill_switch_ready")),
        "daily_stop_ready": _bool(runtime_context.get("daily_stop_ready")),
        "max_loss_gate_ready": _bool(runtime_context.get("max_loss_gate_ready")),
        "pre_trade_evidence_ready": _bool(
            runtime_context.get("pre_trade_evidence_ready")
        ),
        "post_trade_evidence_plan_ready": _bool(
            runtime_context.get("post_trade_evidence_plan_ready")
        ),
        "broker_network_call_performed": _bool(
            runtime_context.get("broker_network_call_performed")
        ),
        "order_placement_performed": _bool(
            runtime_context.get("order_placement_performed")
        ),
    }


def _manual_runtime_run_contract(status: str) -> dict[str, Any]:
    ready = status == OWNER_RUN_READY_FOR_EXPLICIT_MANUAL_COMMAND
    return {
        "ready": ready,
        "status": "READY_FOR_EXPLICIT_OWNER_COMMAND" if ready else "NOT_READY",
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "one_order_only": True,
        "max_order_attempts": 1,
        "actual_execution_requires_owner_to_run_command": True,
        "broker_call_implemented_in_this_pr": False,
        "pr_places_order": False,
        "stop_after_one_order_attempt": True,
        "no_second_order": True,
    }


def _pre_run_checklist(status: str) -> dict[str, Any]:
    ready = status == OWNER_RUN_READY_FOR_EXPLICIT_MANUAL_COMMAND
    return {
        "ready": ready,
        "items": list(PRE_RUN_CHECKLIST_ITEMS),
        "must_complete_before_manual_command": True,
    }


def _post_run_evidence_plan(status: str) -> dict[str, Any]:
    ready = status == OWNER_RUN_READY_FOR_EXPLICIT_MANUAL_COMMAND
    return {
        "ready": ready,
        "items": list(POST_RUN_EVIDENCE_ITEMS),
        "sanitize_before_repo_storage": True,
        "credential_or_account_identifier_storage_allowed": False,
    }


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


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _warnings(status: str) -> list[str]:
    warnings = [
        "final_owner_runtime_run_model_only",
        "execution_authority_false",
        "no_oanda_call_performed",
        "no_broker_call_performed",
        "no_credentials_or_account_ids_read_or_persisted",
        "no_order_placement_performed",
        "manual_owner_command_required",
    ]
    if status == OWNER_RUN_READY_FOR_EXPLICIT_MANUAL_COMMAND:
        warnings.append("owner_must_run_manual_demo_order_command_once")
    return warnings


def _next_safe_action(status: str) -> str:
    return {
        OWNER_RUN_BLOCKED_MISSING_FINAL_WIRE: "provide_final_wire_result",
        OWNER_RUN_BLOCKED_FINAL_WIRE_NOT_READY: "repair_final_wire_before_owner_run",
        OWNER_RUN_BLOCKED_OWNER_APPROVAL: (
            "complete_owner_runtime_run_approval_before_manual_command"
        ),
        OWNER_RUN_BLOCKED_RUNTIME_CONTEXT: (
            "provide_oanda_demo_runtime_context_before_manual_command"
        ),
        OWNER_RUN_READY_FOR_EXPLICIT_MANUAL_COMMAND: (
            "owner_may_run_manual_demo_order_command_once"
        ),
        OWNER_RUN_REJECTED: (
            "remove_execution_authority_or_broker_call_request_before_owner_run"
        ),
    }.get(status, "stop_and_review_owner_runtime_run_state")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _number(value: Any, default: float) -> float:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else default


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
