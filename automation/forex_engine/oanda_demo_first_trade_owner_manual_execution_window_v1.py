from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = (
    "AIOS-FOREX-OANDA-DEMO-FIRST-TRADE-OWNER-MANUAL-EXECUTION-WINDOW-V1"
)
EXECUTION_WINDOW_VERSION = "v1"

WINDOW_BLOCKED_MISSING_GO_NOGO = "WINDOW_BLOCKED_MISSING_GO_NOGO"
WINDOW_BLOCKED_GO_NOGO_NOT_READY = "WINDOW_BLOCKED_GO_NOGO_NOT_READY"
WINDOW_BLOCKED_OWNER_COMMAND = "WINDOW_BLOCKED_OWNER_COMMAND"
WINDOW_BLOCKED_CONTEXT = "WINDOW_BLOCKED_CONTEXT"
WINDOW_BLOCKED_OWNER_CONFIRMATION = "WINDOW_BLOCKED_OWNER_CONFIRMATION"
WINDOW_READY_FOR_OWNER_MANUAL_DEMO_EXECUTION = (
    "WINDOW_READY_FOR_OWNER_MANUAL_DEMO_EXECUTION"
)
WINDOW_NOGO = "WINDOW_NOGO"

RUNBOOK_GO_READY_STATUS = "RUNBOOK_GO_READY_FOR_OWNER_MANUAL_DEMO_ATTEMPT"
RUNBOOK_NEXT_SAFE_ACTION = "owner_may_run_first_demo_order_command_once"
OWNER_COMMAND_READY_STATUS = "OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND"

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

CONTEXT_REQUIRED_TRUE_FIELDS = (
    "demo_endpoint_only",
    "live_endpoint_absent",
    "runtime_token_external",
    "runtime_account_id_external",
    "runtime_credentials_available_to_owner",
    "one_order_only",
    "owner_present_for_manual_run",
    "kill_switch_ready",
    "daily_stop_ready",
    "max_loss_gate_ready",
    "stop_loss_ready",
    "take_profit_ready",
    "pre_trade_evidence_ready",
    "post_trade_evidence_plan_ready",
    "market_open_or_owner_override",
)

CONTEXT_REQUIRED_FALSE_FIELDS = (
    "credential_persistence_detected",
    "account_id_persistence_detected",
    "order_already_attempted",
)

OWNER_CONFIRMATION_REQUIRED_TRUE_FIELDS = (
    "owner_confirmed_execution_window_reviewed",
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
    "owner_confirmed_runtime_credentials_external",
)

FINAL_PRE_EXECUTION_CHECKLIST_ITEMS = (
    "confirm_go_nogo_still_go",
    "confirm_owner_command_package_ready",
    "confirm_runtime_values_are_owner_supplied_only",
    "confirm_demo_endpoint_only_and_no_live_money",
    "confirm_execution_window_time_limit",
    "confirm_market_open_or_owner_override",
    "confirm_owner_present_for_manual_run",
    "confirm_one_order_only_and_max_one_attempt",
    "confirm_no_second_order",
    "confirm_existing_open_orders_zero",
    "confirm_existing_pending_orders_zero",
    "confirm_stop_loss_ready",
    "confirm_take_profit_ready",
    "confirm_kill_switch_daily_stop_and_max_loss_gates_ready",
    "capture_pre_trade_evidence_before_owner_command",
)

FINAL_POST_EXECUTION_EVIDENCE_ITEMS = (
    "capture_command_exit_status",
    "capture_sanitized_order_reference",
    "capture_fill_or_rejection_status",
    "capture_sl_tp_attachment_status",
    "record_pl_realized_or_unrealized",
    "record_balance_nav_snapshot",
    "record_timestamp_utc",
    "confirm_no_credentials_or_account_ids_persisted",
    "confirm_no_second_order_attempted",
    "feed_post_trade_evidence_capture_layer",
    "feed_result_to_bucket_layer_after_evidence_capture",
)


def evaluate_oanda_demo_first_trade_owner_manual_execution_window_v1(
    go_nogo_result: dict | None = None,
    owner_command_result: dict | None = None,
    execution_window_context: dict | None = None,
    owner_execution_window_confirmation: dict | None = None,
) -> dict:
    go_nogo = _mapping(go_nogo_result)
    owner_command = _mapping(owner_command_result)
    context = _mapping(execution_window_context)
    owner_confirmation = _mapping(owner_execution_window_confirmation)

    if not go_nogo:
        return _result(
            status=WINDOW_BLOCKED_MISSING_GO_NOGO,
            blockers=["missing_go_nogo_result"],
            go_nogo=go_nogo,
            owner_command=owner_command,
            context=context,
            owner_confirmation=owner_confirmation,
        )

    go_nogo_blockers = _go_nogo_blockers(go_nogo)
    if go_nogo_blockers:
        return _result(
            status=WINDOW_BLOCKED_GO_NOGO_NOT_READY,
            blockers=go_nogo_blockers,
            go_nogo=go_nogo,
            owner_command=owner_command,
            context=context,
            owner_confirmation=owner_confirmation,
        )

    owner_command_blockers = (
        ["missing_owner_command_result"]
        if not owner_command
        else _owner_command_blockers(owner_command)
    )
    if owner_command_blockers:
        return _result(
            status=WINDOW_BLOCKED_OWNER_COMMAND,
            blockers=owner_command_blockers,
            go_nogo=go_nogo,
            owner_command=owner_command,
            context=context,
            owner_confirmation=owner_confirmation,
        )

    context_blockers = (
        ["missing_execution_window_context"]
        if not context
        else _execution_window_context_blockers(context)
    )
    if context_blockers:
        return _result(
            status=WINDOW_BLOCKED_CONTEXT,
            blockers=context_blockers,
            go_nogo=go_nogo,
            owner_command=owner_command,
            context=context,
            owner_confirmation=owner_confirmation,
        )

    owner_confirmation_blockers = _owner_confirmation_blockers(owner_confirmation)
    if owner_confirmation_blockers:
        return _result(
            status=WINDOW_BLOCKED_OWNER_CONFIRMATION,
            blockers=owner_confirmation_blockers,
            go_nogo=go_nogo,
            owner_command=owner_command,
            context=context,
            owner_confirmation=owner_confirmation,
        )

    return _result(
        status=WINDOW_READY_FOR_OWNER_MANUAL_DEMO_EXECUTION,
        blockers=[],
        go_nogo=go_nogo,
        owner_command=owner_command,
        context=context,
        owner_confirmation=owner_confirmation,
    )


def _go_nogo_blockers(go_nogo: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if go_nogo.get("status") != RUNBOOK_GO_READY_STATUS:
        blockers.append("go_nogo_status_not_ready")
    if go_nogo.get("go_nogo") != "GO":
        blockers.append("go_nogo_decision_must_be_go")
    if go_nogo.get("next_safe_action") != RUNBOOK_NEXT_SAFE_ACTION:
        blockers.append("go_nogo_next_safe_action_not_owner_manual_once")
    blockers.extend(_authority_blockers(go_nogo, "go_nogo_result"))
    return blockers


def _owner_command_blockers(owner_command: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if owner_command.get("status") != OWNER_COMMAND_READY_STATUS:
        blockers.append("owner_command_status_not_ready")
    if not _present(owner_command.get("final_owner_command")):
        blockers.append("owner_command_final_owner_command_required")
    blockers.extend(_authority_blockers(owner_command, "owner_command_result"))
    for term in _forbidden_key_terms(owner_command):
        blockers.append(f"owner_command_forbidden_{term}_field")
    return blockers


def _execution_window_context_blockers(context: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if context.get("broker") != "OANDA_DEMO":
        blockers.append("execution_window_context_broker_must_be_oanda_demo")
    if context.get("environment") != "DEMO":
        blockers.append("execution_window_context_environment_must_be_demo")
    for field in CONTEXT_REQUIRED_TRUE_FIELDS:
        if not _bool(context.get(field)):
            blockers.append(f"execution_window_context_{field}_required")
    for field in CONTEXT_REQUIRED_FALSE_FIELDS:
        if _bool(context.get(field)):
            blockers.append(f"execution_window_context_{field}_must_be_false")
    if _number(context.get("max_order_attempts"), -1) != 1:
        blockers.append("execution_window_context_max_order_attempts_must_be_one")
    if _number(context.get("existing_open_orders"), -1) != 0:
        blockers.append("execution_window_context_existing_open_orders_must_be_zero")
    if _number(context.get("existing_pending_orders"), -1) != 0:
        blockers.append(
            "execution_window_context_existing_pending_orders_must_be_zero"
        )
    minutes = context.get("execution_window_minutes")
    if not _is_number(minutes) or not 0 < minutes <= 60:
        blockers.append("execution_window_minutes_must_be_numeric_gt_zero_lte_sixty")
    blockers.extend(_authority_blockers(context, "execution_window_context"))
    return blockers


def _owner_confirmation_blockers(owner_confirmation: Mapping[str, Any]) -> list[str]:
    if not owner_confirmation:
        return ["missing_owner_execution_window_confirmation"]

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
    go_nogo: Mapping[str, Any],
    owner_command: Mapping[str, Any],
    context: Mapping[str, Any],
    owner_confirmation: Mapping[str, Any],
) -> dict[str, Any]:
    ready = status == WINDOW_READY_FOR_OWNER_MANUAL_DEMO_EXECUTION
    return {
        "packet_id": PACKET_ID,
        "execution_window_version": EXECUTION_WINDOW_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": _warnings(status),
        "go_nogo_summary": _go_nogo_summary(go_nogo),
        "owner_command_summary": _owner_command_summary(owner_command),
        "execution_window_context_summary": _execution_window_context_summary(context),
        "owner_confirmation_summary": _owner_confirmation_summary(
            owner_confirmation
        ),
        "execution_window_package": _execution_window_package(context, ready),
        "final_pre_execution_checklist": _final_pre_execution_checklist(ready),
        "final_post_execution_evidence_path": _final_post_execution_evidence_path(
            ready
        ),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }


def _go_nogo_summary(go_nogo: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": _text(go_nogo.get("status"), "MISSING"),
        "go_nogo": _text(go_nogo.get("go_nogo"), "MISSING"),
        "ready": go_nogo.get("status") == RUNBOOK_GO_READY_STATUS
        and go_nogo.get("go_nogo") == "GO",
        "next_safe_action": _text(go_nogo.get("next_safe_action"), "MISSING"),
        "execution_authority_false": not _authority_blockers(
            go_nogo,
            "go_nogo_result",
        ),
    }


def _owner_command_summary(owner_command: Mapping[str, Any]) -> dict[str, Any]:
    command = _mapping(owner_command.get("final_owner_command"))
    return {
        "status": _text(owner_command.get("status"), "MISSING"),
        "ready": owner_command.get("status") == OWNER_COMMAND_READY_STATUS,
        "final_owner_command_present": _present(
            owner_command.get("final_owner_command")
        ),
        "command_type": _text(command.get("command_type"), "MISSING"),
        "script_path": _text(command.get("script_path"), "MISSING"),
        "command_text_present": bool(_text(command.get("command_text"))),
        "sensitive_key_terms_detected": _forbidden_key_terms(owner_command),
        "execution_authority_false": not _authority_blockers(
            owner_command,
            "owner_command_result",
        ),
    }


def _execution_window_context_summary(context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker": _text(context.get("broker"), "MISSING"),
        "environment": _text(context.get("environment"), "MISSING"),
        "demo_endpoint_only": _bool(context.get("demo_endpoint_only")),
        "live_endpoint_absent": _bool(context.get("live_endpoint_absent")),
        "runtime_token_external": _bool(context.get("runtime_token_external")),
        "runtime_account_id_external": _bool(
            context.get("runtime_account_id_external")
        ),
        "runtime_credentials_available_to_owner": _bool(
            context.get("runtime_credentials_available_to_owner")
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
        "owner_present_for_manual_run": _bool(
            context.get("owner_present_for_manual_run")
        ),
        "kill_switch_ready": _bool(context.get("kill_switch_ready")),
        "daily_stop_ready": _bool(context.get("daily_stop_ready")),
        "max_loss_gate_ready": _bool(context.get("max_loss_gate_ready")),
        "stop_loss_ready": _bool(context.get("stop_loss_ready")),
        "take_profit_ready": _bool(context.get("take_profit_ready")),
        "pre_trade_evidence_ready": _bool(context.get("pre_trade_evidence_ready")),
        "post_trade_evidence_plan_ready": _bool(
            context.get("post_trade_evidence_plan_ready")
        ),
        "execution_window_minutes": _number(
            context.get("execution_window_minutes"),
            0,
        ),
        "market_open_or_owner_override": _bool(
            context.get("market_open_or_owner_override")
        ),
    }


def _owner_confirmation_summary(owner_confirmation: Mapping[str, Any]) -> dict[str, bool]:
    return {
        field: _bool(owner_confirmation.get(field))
        for field in OWNER_CONFIRMATION_REQUIRED_TRUE_FIELDS
    }


def _execution_window_package(
    context: Mapping[str, Any],
    ready: bool,
) -> dict[str, Any]:
    return {
        "ready": ready,
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "execution_window_minutes": _number(
            context.get("execution_window_minutes"),
            0,
        ),
        "one_order_only": True,
        "max_order_attempts": 1,
        "actual_order_requires_owner_manual_command": True,
        "codex_must_not_execute_command": True,
        "runtime_credentials_must_be_owner_supplied": True,
        "credential_or_account_identifier_persistence_allowed": False,
        "post_trade_evidence_required": True,
        "next_step_after_attempt": "capture_sanitized_post_trade_evidence",
    }


def _final_pre_execution_checklist(ready: bool) -> dict[str, Any]:
    return {
        "ready": ready,
        "items": list(FINAL_PRE_EXECUTION_CHECKLIST_ITEMS),
        "must_complete_before_owner_manual_command": True,
        "codex_must_not_run_command": True,
    }


def _final_post_execution_evidence_path(ready: bool) -> dict[str, Any]:
    return {
        "ready": ready,
        "items": list(FINAL_POST_EXECUTION_EVIDENCE_ITEMS),
        "sanitize_before_repo_storage": True,
        "credential_or_account_identifier_storage_allowed": False,
        "next_layers": [
            "AIOS_FOREX_OANDA_DEMO_POST_TRADE_EVIDENCE_CAPTURE_V1",
            "AIOS_FOREX_OANDA_DEMO_RESULT_TO_BUCKET_AND_NEXT_ALLOCATION_V1",
        ],
    }


def _warnings(status: str) -> list[str]:
    warnings = [
        "execution_window_package_only",
        "execution_authority_false",
        "no_oanda_call_performed",
        "no_broker_call_performed",
        "no_order_placement_performed",
        "no_credentials_or_account_ids_read_or_persisted",
        "owner_manual_run_only",
        "one_order_cap_remains_in_force",
    ]
    if status == WINDOW_READY_FOR_OWNER_MANUAL_DEMO_EXECUTION:
        warnings.append("owner_may_execute_one_demo_order_inside_window")
    return warnings


def _next_safe_action(status: str) -> str:
    if status == WINDOW_READY_FOR_OWNER_MANUAL_DEMO_EXECUTION:
        return "owner_may_execute_one_demo_order_inside_window"
    return "repair_blocker_before_execution_window"


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


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _number(value: Any, default: float) -> float:
    return value if _is_number(value) else default


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
