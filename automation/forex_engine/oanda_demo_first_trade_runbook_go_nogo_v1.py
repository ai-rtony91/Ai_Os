from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-FIRST-TRADE-RUNBOOK-AND-OWNER-GO-NOGO-V1"
RUNBOOK_VERSION = "v1"

RUNBOOK_BLOCKED_MISSING_OWNER_COMMAND = "RUNBOOK_BLOCKED_MISSING_OWNER_COMMAND"
RUNBOOK_BLOCKED_OWNER_COMMAND_NOT_READY = (
    "RUNBOOK_BLOCKED_OWNER_COMMAND_NOT_READY"
)
RUNBOOK_BLOCKED_BROKER_CALL_READINESS = (
    "RUNBOOK_BLOCKED_BROKER_CALL_READINESS"
)
RUNBOOK_BLOCKED_BUCKET_READINESS = "RUNBOOK_BLOCKED_BUCKET_READINESS"
RUNBOOK_BLOCKED_RUNTIME_CONTEXT = "RUNBOOK_BLOCKED_RUNTIME_CONTEXT"
RUNBOOK_BLOCKED_OWNER_CONFIRMATION = "RUNBOOK_BLOCKED_OWNER_CONFIRMATION"
RUNBOOK_GO_READY_FOR_OWNER_MANUAL_DEMO_ATTEMPT = (
    "RUNBOOK_GO_READY_FOR_OWNER_MANUAL_DEMO_ATTEMPT"
)
RUNBOOK_NOGO = "RUNBOOK_NOGO"

OWNER_COMMAND_READY_STATUS = "OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND"
BUCKET_UPDATE_READY_STATUS = "BUCKET_UPDATE_READY"
BROKER_CALL_DRY_RUN_STATUS = "BROKER_CALL_DRY_RUN_READY"
BROKER_CALL_READY_TRANSPORT_STATUS = "BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED"
BROKER_CALL_ATTEMPTED_STATUS = "BROKER_CALL_ATTEMPTED_DEMO_ORDER_ONCE"

BROKER_CALL_READY_STATUSES = {
    BROKER_CALL_DRY_RUN_STATUS,
    BROKER_CALL_READY_TRANSPORT_STATUS,
    BROKER_CALL_ATTEMPTED_STATUS,
}

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

SENSITIVE_KEY_TERMS = (
    "account_id",
    "token",
    "credential",
    "secret",
    "password",
    "authorization",
)

RUNTIME_REQUIRED_TRUE_FIELDS = (
    "demo_endpoint_only",
    "live_endpoint_absent",
    "runtime_token_external",
    "runtime_account_id_external",
    "one_order_only",
    "kill_switch_ready",
    "daily_stop_ready",
    "max_loss_gate_ready",
    "stop_loss_ready",
    "take_profit_ready",
    "pre_trade_evidence_ready",
    "post_trade_evidence_plan_ready",
    "owner_present_for_manual_run",
)

RUNTIME_REQUIRED_FALSE_FIELDS = (
    "credential_persistence_detected",
    "account_id_persistence_detected",
    "order_already_attempted",
)

OWNER_CONFIRMATION_REQUIRED_TRUE_FIELDS = (
    "owner_confirmed_go_nogo_reviewed",
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
    "owner_confirmed_post_trade_evidence_required",
    "owner_confirmed_kill_switch_ready",
)

PRE_RUN_CHECKLIST_ITEMS = (
    "review_pr_landed_and_main_synced",
    "confirm_oanda_demo_environment_only_and_no_live_money",
    "confirm_demo_endpoint_only_and_live_endpoint_absent",
    "confirm_runtime_token_external_and_not_persisted",
    "confirm_runtime_account_id_external_and_not_persisted",
    "confirm_one_order_only_max_one_attempt_and_no_second_order",
    "confirm_order_not_already_attempted",
    "confirm_existing_open_orders_zero",
    "confirm_existing_pending_orders_zero",
    "confirm_stop_loss_ready_and_order_value_known",
    "confirm_take_profit_ready_and_order_value_known",
    "confirm_kill_switch_daily_stop_and_max_loss_gates_ready",
    "capture_pre_trade_evidence_before_manual_command",
    "open_owner_command_template_only_after_go",
    "do_not_rerun_after_one_attempt",
)

POST_RUN_EVIDENCE_CHECKLIST_ITEMS = (
    "capture_command_exit_status",
    "capture_sanitized_order_reference",
    "capture_fill_or_rejection_status",
    "capture_stop_loss_take_profit_attachment_status",
    "record_realized_or_unrealized_pl",
    "record_balance_nav_snapshot",
    "record_timestamp_utc",
    "confirm_no_credentials_or_account_ids_persisted",
    "confirm_no_second_order_attempted",
    "prepare_post_trade_evidence_capture_package",
    "prepare_result_to_bucket_update_after_evidence_capture",
)


def evaluate_oanda_demo_first_trade_runbook_go_nogo_v1(
    owner_command_result: dict | None = None,
    broker_call_readiness_result: dict | None = None,
    result_bucket_readiness_result: dict | None = None,
    runtime_readiness_context: dict | None = None,
    owner_go_nogo_confirmation: dict | None = None,
) -> dict:
    owner_command = _mapping(owner_command_result)
    broker_call = _mapping(broker_call_readiness_result)
    bucket_result = _mapping(result_bucket_readiness_result)
    runtime_context = _mapping(runtime_readiness_context)
    owner_confirmation = _mapping(owner_go_nogo_confirmation)

    if not owner_command:
        return _result(
            status=RUNBOOK_BLOCKED_MISSING_OWNER_COMMAND,
            blockers=["missing_owner_command_result"],
            owner_command=owner_command,
            broker_call=broker_call,
            bucket_result=bucket_result,
            runtime_context=runtime_context,
            owner_confirmation=owner_confirmation,
        )

    owner_blockers = _owner_command_blockers(owner_command)
    if owner_blockers:
        return _result(
            status=RUNBOOK_BLOCKED_OWNER_COMMAND_NOT_READY,
            blockers=owner_blockers,
            owner_command=owner_command,
            broker_call=broker_call,
            bucket_result=bucket_result,
            runtime_context=runtime_context,
            owner_confirmation=owner_confirmation,
        )

    broker_blockers = (
        ["missing_broker_call_readiness_result"]
        if not broker_call
        else _broker_call_blockers(broker_call)
    )
    if broker_blockers:
        return _result(
            status=RUNBOOK_BLOCKED_BROKER_CALL_READINESS,
            blockers=broker_blockers,
            owner_command=owner_command,
            broker_call=broker_call,
            bucket_result=bucket_result,
            runtime_context=runtime_context,
            owner_confirmation=owner_confirmation,
        )

    bucket_blockers = (
        ["missing_result_bucket_readiness_result"]
        if not bucket_result
        else _result_bucket_blockers(bucket_result)
    )
    if bucket_blockers:
        return _result(
            status=RUNBOOK_BLOCKED_BUCKET_READINESS,
            blockers=bucket_blockers,
            owner_command=owner_command,
            broker_call=broker_call,
            bucket_result=bucket_result,
            runtime_context=runtime_context,
            owner_confirmation=owner_confirmation,
        )

    runtime_blockers = (
        ["missing_runtime_readiness_context"]
        if not runtime_context
        else _runtime_context_blockers(runtime_context)
    )
    if runtime_blockers:
        return _result(
            status=RUNBOOK_BLOCKED_RUNTIME_CONTEXT,
            blockers=runtime_blockers,
            owner_command=owner_command,
            broker_call=broker_call,
            bucket_result=bucket_result,
            runtime_context=runtime_context,
            owner_confirmation=owner_confirmation,
        )

    owner_confirmation_blockers = _owner_confirmation_blockers(owner_confirmation)
    if owner_confirmation_blockers:
        return _result(
            status=RUNBOOK_BLOCKED_OWNER_CONFIRMATION,
            blockers=owner_confirmation_blockers,
            owner_command=owner_command,
            broker_call=broker_call,
            bucket_result=bucket_result,
            runtime_context=runtime_context,
            owner_confirmation=owner_confirmation,
        )

    return _result(
        status=RUNBOOK_GO_READY_FOR_OWNER_MANUAL_DEMO_ATTEMPT,
        blockers=[],
        owner_command=owner_command,
        broker_call=broker_call,
        bucket_result=bucket_result,
        runtime_context=runtime_context,
        owner_confirmation=owner_confirmation,
    )


def _owner_command_blockers(owner_command: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if owner_command.get("status") != OWNER_COMMAND_READY_STATUS:
        blockers.append("owner_command_status_not_ready")
    if not _present(owner_command.get("final_owner_command")):
        blockers.append("owner_command_final_owner_command_required")
    blockers.extend(_authority_blockers(owner_command, "owner_command_result"))
    return blockers


def _broker_call_blockers(broker_call: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    status = broker_call.get("status")
    if status not in BROKER_CALL_READY_STATUSES:
        blockers.append("broker_call_status_not_ready")
    if status == BROKER_CALL_ATTEMPTED_STATUS:
        blockers.append(
            "broker_call_attempted_demo_order_once_is_evidence_mode_not_first_trade_go"
        )
    if _bool(broker_call.get("live_order_allowed")):
        blockers.append("broker_call_live_order_allowed_must_not_be_true")
    if _bool(broker_call.get("autonomous_order_allowed")):
        blockers.append("broker_call_autonomous_order_allowed_must_not_be_true")
    blockers.extend(_authority_blockers(broker_call, "broker_call_readiness_result"))
    for term in _forbidden_key_terms(broker_call):
        blockers.append(f"broker_call_forbidden_{term}_field")
    return blockers


def _result_bucket_blockers(bucket_result: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    recommendation = _mapping(bucket_result.get("recommendation"))
    if bucket_result.get("status") != BUCKET_UPDATE_READY_STATUS:
        blockers.append("result_bucket_status_not_ready")
    if not _bool(recommendation.get("next_trade_requires_owner_approval")):
        blockers.append("result_bucket_next_trade_owner_approval_required")
    if _bool(recommendation.get("live_allocation_allowed")):
        blockers.append("result_bucket_live_allocation_must_be_false")
    if _bool(recommendation.get("autonomous_compounding_allowed")):
        blockers.append("result_bucket_autonomous_compounding_must_be_false")
    blockers.extend(_authority_blockers(bucket_result, "result_bucket_readiness"))
    return blockers


def _runtime_context_blockers(context: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if context.get("broker") != "OANDA_DEMO":
        blockers.append("runtime_context_broker_must_be_oanda_demo")
    if context.get("environment") != "DEMO":
        blockers.append("runtime_context_environment_must_be_demo")
    for field in RUNTIME_REQUIRED_TRUE_FIELDS:
        if not _bool(context.get(field)):
            blockers.append(f"runtime_context_{field}_required")
    for field in RUNTIME_REQUIRED_FALSE_FIELDS:
        if _bool(context.get(field)):
            blockers.append(f"runtime_context_{field}_must_be_false")
    if _number(context.get("max_order_attempts"), -1) != 1:
        blockers.append("runtime_context_max_order_attempts_must_be_one")
    if _number(context.get("existing_open_orders"), -1) != 0:
        blockers.append("runtime_context_existing_open_orders_must_be_zero")
    if _number(context.get("existing_pending_orders"), -1) != 0:
        blockers.append("runtime_context_existing_pending_orders_must_be_zero")
    blockers.extend(_authority_blockers(context, "runtime_context"))
    return blockers


def _owner_confirmation_blockers(owner_confirmation: Mapping[str, Any]) -> list[str]:
    if not owner_confirmation:
        return ["missing_owner_go_nogo_confirmation"]

    blockers: list[str] = []
    for field in OWNER_CONFIRMATION_REQUIRED_TRUE_FIELDS:
        if not _bool(owner_confirmation.get(field)):
            blockers.append(f"{field}_required")
    blockers.extend(_authority_blockers(owner_confirmation, "owner_confirmation"))
    return blockers


def _result(
    *,
    status: str,
    blockers: list[str],
    owner_command: Mapping[str, Any],
    broker_call: Mapping[str, Any],
    bucket_result: Mapping[str, Any],
    runtime_context: Mapping[str, Any],
    owner_confirmation: Mapping[str, Any],
) -> dict[str, Any]:
    go_ready = status == RUNBOOK_GO_READY_FOR_OWNER_MANUAL_DEMO_ATTEMPT
    return {
        "packet_id": PACKET_ID,
        "runbook_version": RUNBOOK_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": _warnings(status),
        "go_nogo": "GO" if go_ready else "NOGO",
        "owner_command_summary": _owner_command_summary(owner_command),
        "broker_call_summary": _broker_call_summary(broker_call),
        "result_bucket_summary": _result_bucket_summary(bucket_result),
        "runtime_readiness_summary": _runtime_readiness_summary(runtime_context),
        "pre_run_checklist": _pre_run_checklist(go_ready),
        "execution_command_summary": _execution_command_summary(
            owner_command,
            go_ready,
        ),
        "post_run_evidence_checklist": _post_run_evidence_checklist(go_ready),
        "kill_switch_plan": _kill_switch_plan(runtime_context, go_ready),
        "risk_controls": _risk_controls(runtime_context, owner_confirmation, go_ready),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }


def _owner_command_summary(owner_command: Mapping[str, Any]) -> dict[str, Any]:
    final_owner_command = owner_command.get("final_owner_command")
    command = _mapping(final_owner_command)
    return {
        "status": _text(owner_command.get("status"), "MISSING"),
        "ready": owner_command.get("status") == OWNER_COMMAND_READY_STATUS,
        "final_owner_command_present": _present(final_owner_command),
        "command_type": _text(command.get("command_type"), "MISSING"),
        "script_path": _text(command.get("script_path"), "MISSING"),
        "command_text_present": bool(_text(command.get("command_text"))),
        "execution_authority_false": not _authority_blockers(
            owner_command,
            "owner_command_result",
        ),
    }


def _broker_call_summary(broker_call: Mapping[str, Any]) -> dict[str, Any]:
    status = _text(broker_call.get("status"), "MISSING")
    return {
        "status": status,
        "ready_status": status in BROKER_CALL_READY_STATUSES,
        "attempted_once_status": status == BROKER_CALL_ATTEMPTED_STATUS,
        "live_order_allowed": _bool(broker_call.get("live_order_allowed")),
        "autonomous_order_allowed": _bool(
            broker_call.get("autonomous_order_allowed")
        ),
        "sensitive_key_terms_detected": _forbidden_key_terms(broker_call),
        "execution_authority_false": not _authority_blockers(
            broker_call,
            "broker_call_readiness_result",
        ),
    }


def _result_bucket_summary(bucket_result: Mapping[str, Any]) -> dict[str, Any]:
    recommendation = _mapping(bucket_result.get("recommendation"))
    return {
        "status": _text(bucket_result.get("status"), "MISSING"),
        "ready": bucket_result.get("status") == BUCKET_UPDATE_READY_STATUS,
        "next_trade_requires_owner_approval": _bool(
            recommendation.get("next_trade_requires_owner_approval")
        ),
        "live_allocation_allowed": _bool(
            recommendation.get("live_allocation_allowed")
        ),
        "autonomous_compounding_allowed": _bool(
            recommendation.get("autonomous_compounding_allowed")
        ),
        "execution_authority_false": not _authority_blockers(
            bucket_result,
            "result_bucket_readiness",
        ),
    }


def _runtime_readiness_summary(context: Mapping[str, Any]) -> dict[str, Any]:
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
        "existing_open_orders": _number(context.get("existing_open_orders"), -1),
        "existing_pending_orders": _number(context.get("existing_pending_orders"), -1),
        "kill_switch_ready": _bool(context.get("kill_switch_ready")),
        "daily_stop_ready": _bool(context.get("daily_stop_ready")),
        "max_loss_gate_ready": _bool(context.get("max_loss_gate_ready")),
        "stop_loss_ready": _bool(context.get("stop_loss_ready")),
        "take_profit_ready": _bool(context.get("take_profit_ready")),
        "pre_trade_evidence_ready": _bool(context.get("pre_trade_evidence_ready")),
        "post_trade_evidence_plan_ready": _bool(
            context.get("post_trade_evidence_plan_ready")
        ),
        "owner_present_for_manual_run": _bool(
            context.get("owner_present_for_manual_run")
        ),
    }


def _pre_run_checklist(go_ready: bool) -> dict[str, Any]:
    return {
        "ready": go_ready,
        "items": list(PRE_RUN_CHECKLIST_ITEMS),
        "must_complete_before_owner_manual_command": True,
        "codex_must_not_run_command": True,
    }


def _execution_command_summary(
    owner_command: Mapping[str, Any],
    go_ready: bool,
) -> dict[str, Any]:
    command = _mapping(owner_command.get("final_owner_command"))
    return {
        "ready": go_ready,
        "owner_manual_command_required": True,
        "codex_must_not_run_command": True,
        "script_path": _text(command.get("script_path"), "MISSING"),
        "command_text_available_to_owner": bool(_text(command.get("command_text"))),
        "credential_values_must_be_runtime_only": True,
        "credential_or_account_identifier_persistence_allowed": False,
        "run_limit": "one_manual_demo_order_attempt_only",
        "reminder": (
            "Anthony may run the owner command once only after GO and must stop "
            "for post-trade evidence capture."
        ),
    }


def _post_run_evidence_checklist(go_ready: bool) -> dict[str, Any]:
    return {
        "ready": go_ready,
        "items": list(POST_RUN_EVIDENCE_CHECKLIST_ITEMS),
        "sanitize_before_repo_storage": True,
        "credential_or_account_identifier_storage_allowed": False,
    }


def _kill_switch_plan(
    context: Mapping[str, Any],
    go_ready: bool,
) -> dict[str, Any]:
    return {
        "ready": go_ready and _bool(context.get("kill_switch_ready")),
        "kill_switch_ready": _bool(context.get("kill_switch_ready")),
        "daily_stop_ready": _bool(context.get("daily_stop_ready")),
        "max_loss_gate_ready": _bool(context.get("max_loss_gate_ready")),
        "before_run": "confirm_manual_stop_path_and_no_second_order_before_command",
        "during_run": "if_unexpected_state_appears_stop_and_do_not_retry",
        "after_run": "capture_evidence_then_stop_before_any_next_trade",
    }


def _risk_controls(
    context: Mapping[str, Any],
    owner_confirmation: Mapping[str, Any],
    go_ready: bool,
) -> dict[str, Any]:
    return {
        "ready": go_ready,
        "demo_only": context.get("environment") == "DEMO",
        "no_live_money_confirmed": _bool(
            owner_confirmation.get("owner_confirmed_no_live_money")
        ),
        "one_order_only": _bool(context.get("one_order_only")),
        "max_order_attempts": _number(context.get("max_order_attempts"), 0),
        "no_second_order_confirmed": _bool(
            owner_confirmation.get("owner_confirmed_no_second_order")
        ),
        "stop_loss_ready": _bool(context.get("stop_loss_ready")),
        "take_profit_ready": _bool(context.get("take_profit_ready")),
        "loss_possible_confirmed": _bool(
            owner_confirmation.get("owner_confirmed_loss_possible")
        ),
        "no_profit_guarantee_confirmed": _bool(
            owner_confirmation.get("owner_confirmed_no_profit_guarantee")
        ),
        "existing_open_orders": _number(context.get("existing_open_orders"), -1),
        "existing_pending_orders": _number(context.get("existing_pending_orders"), -1),
        "live_order_allowed": False,
        "autonomous_order_allowed": False,
    }


def _warnings(status: str) -> list[str]:
    warnings = [
        "first_trade_runbook_only",
        "execution_authority_false",
        "no_oanda_call_performed",
        "no_broker_call_performed",
        "no_order_placement_performed",
        "no_credentials_or_account_ids_read_or_persisted",
        "owner_manual_run_only",
        "one_order_cap_remains_in_force",
    ]
    if status == RUNBOOK_GO_READY_FOR_OWNER_MANUAL_DEMO_ATTEMPT:
        warnings.append("owner_may_run_first_demo_order_command_once_after_review")
    return warnings


def _next_safe_action(status: str) -> str:
    if status == RUNBOOK_GO_READY_FOR_OWNER_MANUAL_DEMO_ATTEMPT:
        return "owner_may_run_first_demo_order_command_once"
    return "repair_blocker_before_owner_manual_demo_attempt"


def _authority_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            for key, child in node.items():
                key_text = str(key)
                if key_text in EXECUTION_AUTHORITY_FIELDS and child is True:
                    blockers.append(f"unsafe_{label}_{key_text}_true")
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(payload)
    return _unique(blockers)


def _forbidden_key_terms(value: Any) -> list[str]:
    found: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            for key, child in node.items():
                key_text = str(key).lower()
                for term in SENSITIVE_KEY_TERMS:
                    if term in key_text and term not in found:
                        found.append(term)
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)
    return found


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _number(value: Any, default: float) -> float:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else default


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, list):
        return bool(value)
    return True


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
