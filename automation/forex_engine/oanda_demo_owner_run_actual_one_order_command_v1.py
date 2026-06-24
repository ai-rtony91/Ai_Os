from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-OWNER-RUN-ACTUAL-ONE-ORDER-COMMAND-V1"
COMMAND_VERSION = "v1"

OWNER_COMMAND_BLOCKED_MISSING_BROKER_CALL_RESULT = (
    "OWNER_COMMAND_BLOCKED_MISSING_BROKER_CALL_RESULT"
)
OWNER_COMMAND_BLOCKED_BROKER_CALL_NOT_READY = (
    "OWNER_COMMAND_BLOCKED_BROKER_CALL_NOT_READY"
)
OWNER_COMMAND_BLOCKED_OWNER_APPROVAL = "OWNER_COMMAND_BLOCKED_OWNER_APPROVAL"
OWNER_COMMAND_BLOCKED_CONTEXT = "OWNER_COMMAND_BLOCKED_CONTEXT"
OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND = (
    "OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND"
)
OWNER_COMMAND_REJECTED = "OWNER_COMMAND_REJECTED"

READY_BROKER_CALL_STATUSES = {
    "BROKER_CALL_DRY_RUN_READY",
    "BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED",
}

BROKER_CALL_SCRIPT_PATH = (
    "scripts/forex_delivery/run_oanda_demo_broker_call_one_order_manual_run_v1.py"
)

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
    "owner_approved_actual_one_order_command",
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
    "owner_confirmed_runtime_credentials_external",
)

COMMAND_CONTEXT_REQUIRED_TRUE_FIELDS = (
    "demo_endpoint_only",
    "live_endpoint_absent",
    "runtime_token_external",
    "runtime_account_id_external",
    "one_order_only",
    "kill_switch_ready",
    "daily_stop_ready",
    "max_loss_gate_ready",
    "pre_trade_evidence_ready",
    "post_trade_evidence_plan_ready",
)

COMMAND_CONTEXT_REQUIRED_FALSE_FIELDS = (
    "credential_persistence_detected",
    "account_id_persistence_detected",
    "order_already_attempted",
)

MANUAL_PRE_RUN_CHECKLIST_ITEMS = (
    "review_pr_landed_and_main_synced",
    "confirm_oanda_demo_environment_only",
    "confirm_no_live_endpoint_configured",
    "supply_oanda_demo_access_token_runtime_only",
    "supply_oanda_demo_account_id_runtime_only",
    "confirm_no_credential_or_account_id_persistence",
    "confirm_one_order_only_and_max_one_attempt",
    "confirm_order_not_already_attempted",
    "confirm_stop_loss_and_take_profit_values",
    "confirm_loss_possible_and_no_profit_guarantee",
    "confirm_kill_switch_daily_stop_and_max_loss_gates_ready",
    "capture_pre_trade_evidence_before_manual_command",
)

MANUAL_POST_RUN_EVIDENCE_CHECKLIST_ITEMS = (
    "capture_command_exit_status",
    "capture_sanitized_broker_response_or_transport_blocker",
    "capture_single_order_attempt_reference",
    "capture_stop_loss_attachment_status",
    "capture_take_profit_attachment_status",
    "capture_post_attempt_open_orders_count",
    "capture_post_attempt_pending_orders_count",
    "capture_sanitized_balance_or_nav_snapshot",
    "confirm_no_credentials_or_account_ids_persisted",
    "confirm_no_second_order_attempted",
)


def evaluate_oanda_demo_owner_run_actual_one_order_command_v1(
    broker_call_result: dict | None = None,
    owner_command_approval: dict | None = None,
    command_context: dict | None = None,
) -> dict:
    broker_call = _mapping(broker_call_result)
    owner_approval = _mapping(owner_command_approval)
    context = _mapping(command_context)

    if not broker_call:
        return _result(
            status=OWNER_COMMAND_BLOCKED_MISSING_BROKER_CALL_RESULT,
            blockers=["missing_broker_call_result"],
            warnings=_warnings(OWNER_COMMAND_BLOCKED_MISSING_BROKER_CALL_RESULT),
            broker_call=broker_call,
            owner_approval=owner_approval,
            context=context,
        )

    unsafe_blockers = _unsafe_execution_blockers(
        broker_call,
        owner_approval,
        context,
    )
    broker_call_blockers = _broker_call_blockers(broker_call)
    owner_blockers = _owner_approval_blockers(owner_approval)
    context_blockers = _command_context_blockers(context)

    blockers = _unique(
        unsafe_blockers + broker_call_blockers + owner_blockers + context_blockers
    )
    status = _status(
        unsafe_blockers=unsafe_blockers,
        broker_call_blockers=broker_call_blockers,
        owner_blockers=owner_blockers,
        context_blockers=context_blockers,
    )

    return _result(
        status=status,
        blockers=blockers,
        warnings=_warnings(status),
        broker_call=broker_call,
        owner_approval=owner_approval,
        context=context,
    )


def _status(
    *,
    unsafe_blockers: list[str],
    broker_call_blockers: list[str],
    owner_blockers: list[str],
    context_blockers: list[str],
) -> str:
    if unsafe_blockers:
        return OWNER_COMMAND_REJECTED
    if broker_call_blockers:
        return OWNER_COMMAND_BLOCKED_BROKER_CALL_NOT_READY
    if owner_blockers:
        return OWNER_COMMAND_BLOCKED_OWNER_APPROVAL
    if context_blockers:
        return OWNER_COMMAND_BLOCKED_CONTEXT
    return OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND


def _broker_call_blockers(broker_call: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if broker_call.get("status") not in READY_BROKER_CALL_STATUSES:
        blockers.append("broker_call_status_not_ready_for_owner_command")
    if _network_call_performed(broker_call):
        blockers.append("broker_call_network_call_performed_must_be_false")
    if _order_placement_performed(broker_call):
        blockers.append("broker_call_order_placement_performed_must_be_false")
    blockers.extend(_authority_blockers(broker_call, "broker_call_result"))
    return blockers


def _owner_approval_blockers(owner_approval: Mapping[str, Any]) -> list[str]:
    if not owner_approval:
        return ["missing_owner_command_approval"]

    blockers: list[str] = []
    for field in OWNER_APPROVAL_REQUIRED_TRUE_FIELDS:
        if not _bool(owner_approval.get(field)):
            blockers.append(f"{field}_required")
    blockers.extend(_authority_blockers(owner_approval, "owner_approval"))
    return blockers


def _command_context_blockers(context: Mapping[str, Any]) -> list[str]:
    if not context:
        return ["missing_command_context"]

    blockers: list[str] = []
    if context.get("broker") != "OANDA_DEMO":
        blockers.append("command_context_broker_must_be_oanda_demo")
    if context.get("environment") != "DEMO":
        blockers.append("command_context_environment_must_be_demo")
    for field in COMMAND_CONTEXT_REQUIRED_TRUE_FIELDS:
        if not _bool(context.get(field)):
            blockers.append(f"command_context_{field}_required")
    for field in COMMAND_CONTEXT_REQUIRED_FALSE_FIELDS:
        if _bool(context.get(field)):
            blockers.append(f"command_context_{field}_must_be_false")
    if _number(context.get("max_order_attempts"), -1) != 1:
        blockers.append("command_context_max_order_attempts_must_be_one")
    blockers.extend(_authority_blockers(context, "command_context"))
    return blockers


def _result(
    *,
    status: str,
    blockers: list[str],
    warnings: list[str],
    broker_call: Mapping[str, Any],
    owner_approval: Mapping[str, Any],
    context: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "packet_id": PACKET_ID,
        "command_version": COMMAND_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "broker_call_summary": _broker_call_summary(broker_call),
        "owner_approval_summary": _owner_approval_summary(owner_approval),
        "command_context_summary": _command_context_summary(context),
        "final_owner_command": _final_owner_command(status),
        "manual_pre_run_checklist": _manual_pre_run_checklist(status),
        "manual_post_run_evidence_checklist": _manual_post_run_evidence_checklist(
            status
        ),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }


def _broker_call_summary(broker_call: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": _text(broker_call.get("status"), "MISSING"),
        "accepted_ready_status": broker_call.get("status")
        in READY_BROKER_CALL_STATUSES,
        "network_call_performed": _network_call_performed(broker_call),
        "order_placement_performed": _order_placement_performed(broker_call),
        "execution_authority_false": not _authority_blockers(
            broker_call, "broker_call_result"
        ),
    }


def _owner_approval_summary(owner_approval: Mapping[str, Any]) -> dict[str, bool]:
    return {
        field: _bool(owner_approval.get(field))
        for field in OWNER_APPROVAL_REQUIRED_TRUE_FIELDS
    }


def _command_context_summary(context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker": _text(context.get("broker"), "MISSING"),
        "environment": _text(context.get("environment"), "MISSING"),
        "demo_endpoint_only": _bool(context.get("demo_endpoint_only")),
        "live_endpoint_absent": _bool(context.get("live_endpoint_absent")),
        "runtime_token_external": _bool(context.get("runtime_token_external")),
        "runtime_account_id_external": _bool(
            context.get("runtime_account_id_external")
        ),
        "credential_persistence_detected": _bool(
            context.get("credential_persistence_detected")
        ),
        "account_id_persistence_detected": _bool(
            context.get("account_id_persistence_detected")
        ),
        "one_order_only": _bool(context.get("one_order_only")),
        "max_order_attempts": _number(context.get("max_order_attempts"), 0),
        "order_already_attempted": _bool(context.get("order_already_attempted")),
        "kill_switch_ready": _bool(context.get("kill_switch_ready")),
        "daily_stop_ready": _bool(context.get("daily_stop_ready")),
        "max_loss_gate_ready": _bool(context.get("max_loss_gate_ready")),
        "pre_trade_evidence_ready": _bool(context.get("pre_trade_evidence_ready")),
        "post_trade_evidence_plan_ready": _bool(
            context.get("post_trade_evidence_plan_ready")
        ),
    }


def _final_owner_command(status: str) -> dict[str, Any]:
    ready = status == OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND
    return {
        "ready": ready,
        "command_type": "powershell",
        "script_path": BROKER_CALL_SCRIPT_PATH,
        "credential_placeholders": {
            "access_token": "OANDA_DEMO_ACCESS_TOKEN",
            "account_id": "OANDA_DEMO_ACCOUNT_ID",
            "runtime_only": True,
            "persistence_allowed": False,
        },
        "order_placeholders": {
            "instrument": "<instrument>",
            "direction": "<BUY_OR_SELL>",
            "units": "<units>",
            "stop_loss": "<stop_loss>",
            "take_profit": "<take_profit>",
            "risk_amount": "<risk_amount>",
            "client_order_id": "<client_order_id>",
        },
        "one_order_warning": (
            "ONE ORDER ONLY: run this command at most once, then stop."
        ),
        "evidence_reminder": (
            "Capture sanitized pre-run and post-run evidence; do not store "
            "credentials or account identifiers."
        ),
        "command_text": _command_text() if ready else None,
    }


def _command_text() -> str:
    return "\n".join(
        (
            "$env:OANDA_DEMO_ACCESS_TOKEN = '<OANDA_DEMO_ACCESS_TOKEN_RUNTIME_ONLY>'",
            "$env:OANDA_DEMO_ACCOUNT_ID = '<OANDA_DEMO_ACCOUNT_ID_RUNTIME_ONLY>'",
            "$Instrument = '<instrument>'",
            "$Direction = '<BUY_OR_SELL>'",
            "$Units = '<units>'",
            "$StopLoss = '<stop_loss>'",
            "$TakeProfit = '<take_profit>'",
            "$RiskAmount = '<risk_amount>'",
            "$ClientOrderId = '<client_order_id>'",
            "python scripts/forex_delivery/run_oanda_demo_broker_call_one_order_manual_run_v1.py `",
            "  --execute-demo-order `",
            "  --i-approve-actual-oanda-demo-broker-call `",
            "  --i-understand-demo-only `",
            "  --i-understand-one-order-only `",
            "  --i-understand-loss-possible `",
            "  --i-understand-no-profit-guarantee `",
            "  --i-confirm-stop-loss `",
            "  --i-confirm-take-profit `",
            "  --i-confirm-no-second-order `",
            "  --i-confirm-post-trade-evidence",
            "# ONE ORDER ONLY: do not rerun this command after one attempt.",
            "# Evidence required: capture sanitized pre-run and post-run evidence.",
        )
    )


def _manual_pre_run_checklist(status: str) -> dict[str, Any]:
    ready = status == OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND
    return {
        "ready": ready,
        "items": list(MANUAL_PRE_RUN_CHECKLIST_ITEMS),
        "must_complete_before_manual_command": True,
    }


def _manual_post_run_evidence_checklist(status: str) -> dict[str, Any]:
    ready = status == OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND
    return {
        "ready": ready,
        "items": list(MANUAL_POST_RUN_EVIDENCE_CHECKLIST_ITEMS),
        "sanitize_before_repo_storage": True,
        "credential_or_account_identifier_storage_allowed": False,
    }


def _network_call_performed(broker_call: Mapping[str, Any]) -> bool:
    execution_attempt = _mapping(broker_call.get("execution_attempt"))
    return _bool(broker_call.get("network_call_performed")) or _bool(
        execution_attempt.get("network_call_performed")
    )


def _order_placement_performed(broker_call: Mapping[str, Any]) -> bool:
    execution_attempt = _mapping(broker_call.get("execution_attempt"))
    return _bool(broker_call.get("order_placement_performed")) or _bool(
        execution_attempt.get("order_placement_performed")
    )


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
        "owner_command_generator_only",
        "execution_authority_false",
        "no_oanda_call_performed",
        "no_broker_call_performed",
        "no_credentials_or_account_ids_read_or_persisted",
        "no_order_placement_performed",
        "manual_owner_command_required",
    ]
    if status == OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND:
        warnings.append("owner_may_copy_command_after_pr_lands")
    return warnings


def _next_safe_action(status: str) -> str:
    return {
        OWNER_COMMAND_BLOCKED_MISSING_BROKER_CALL_RESULT: (
            "provide_broker_call_readiness_result"
        ),
        OWNER_COMMAND_BLOCKED_BROKER_CALL_NOT_READY: (
            "repair_broker_call_readiness_before_owner_command"
        ),
        OWNER_COMMAND_BLOCKED_OWNER_APPROVAL: (
            "complete_owner_command_approval_before_manual_command"
        ),
        OWNER_COMMAND_BLOCKED_CONTEXT: (
            "provide_demo_only_command_context_before_manual_command"
        ),
        OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND: (
            "owner_may_copy_final_manual_demo_order_command_once"
        ),
        OWNER_COMMAND_REJECTED: (
            "remove_execution_authority_or_unsafe_command_request"
        ),
    }.get(status, "stop_and_review_owner_command_state")


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
