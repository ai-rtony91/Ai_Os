from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-FIRST-TRADE-ACTUAL-OWNER-COMMAND-RUN"
COMMAND_RUN_VERSION = "v1"

ACTUAL_RUN_BLOCKED_MISSING_EXECUTION_WINDOW = (
    "ACTUAL_RUN_BLOCKED_MISSING_EXECUTION_WINDOW"
)
ACTUAL_RUN_BLOCKED_EXECUTION_WINDOW_NOT_READY = (
    "ACTUAL_RUN_BLOCKED_EXECUTION_WINDOW_NOT_READY"
)
ACTUAL_RUN_BLOCKED_OWNER_COMMAND = "ACTUAL_RUN_BLOCKED_OWNER_COMMAND"
ACTUAL_RUN_BLOCKED_BROKER_CALL = "ACTUAL_RUN_BLOCKED_BROKER_CALL"
ACTUAL_RUN_BLOCKED_CONTEXT = "ACTUAL_RUN_BLOCKED_CONTEXT"
ACTUAL_RUN_BLOCKED_OWNER_CONFIRMATION = "ACTUAL_RUN_BLOCKED_OWNER_CONFIRMATION"
ACTUAL_RUN_READY_FOR_OWNER_MANUAL_COMMAND = (
    "ACTUAL_RUN_READY_FOR_OWNER_MANUAL_COMMAND"
)
ACTUAL_RUN_NOGO = "ACTUAL_RUN_NOGO"

WINDOW_READY_STATUS = "WINDOW_READY_FOR_OWNER_MANUAL_DEMO_EXECUTION"
OWNER_COMMAND_READY_STATUS = "OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND"
BROKER_CALL_DRY_RUN_STATUS = "BROKER_CALL_DRY_RUN_READY"
BROKER_CALL_READY_TRANSPORT_STATUS = "BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED"
BROKER_CALL_READY_STATUSES = {
    BROKER_CALL_DRY_RUN_STATUS,
    BROKER_CALL_READY_TRANSPORT_STATUS,
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
    "execution_window_open",
    "market_open_or_owner_override",
)

CONTEXT_REQUIRED_FALSE_FIELDS = (
    "credential_persistence_detected",
    "account_id_persistence_detected",
    "order_already_attempted",
)

OWNER_CONFIRMATION_REQUIRED_TRUE_FIELDS = (
    "owner_confirmed_actual_command_reviewed",
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
    "owner_confirmed_ready_to_press_manual_demo_button",
)

REQUIRED_CONFIRMATION_FLAGS = (
    "--execute-demo-order",
    "--i-approve-actual-oanda-demo-broker-call",
    "--i-understand-demo-only",
    "--i-understand-one-order-only",
    "--i-understand-loss-possible",
    "--i-understand-no-profit-guarantee",
    "--i-confirm-stop-loss",
    "--i-confirm-take-profit",
    "--i-confirm-no-second-order",
    "--i-confirm-post-trade-evidence",
)

FINAL_EVIDENCE_ITEMS = (
    "capture_command_exit_status",
    "capture_sanitized_order_reference",
    "capture_fill_or_rejection_status",
    "capture_sl_tp_attachment_status",
    "record_pl_realized_or_unrealized",
    "record_balance_nav_snapshot",
    "record_timestamp_utc",
    "confirm_no_credentials_or_account_ids_persisted",
    "confirm_no_second_order_attempted",
)


def evaluate_oanda_demo_first_trade_actual_owner_command_run(
    execution_window_result: dict | None = None,
    owner_command_result: dict | None = None,
    broker_call_result: dict | None = None,
    actual_run_context: dict | None = None,
    owner_actual_run_confirmation: dict | None = None,
) -> dict:
    execution_window = _mapping(execution_window_result)
    owner_command = _mapping(owner_command_result)
    broker_call = _mapping(broker_call_result)
    context = _mapping(actual_run_context)
    owner_confirmation = _mapping(owner_actual_run_confirmation)

    if not execution_window:
        return _result(
            status=ACTUAL_RUN_BLOCKED_MISSING_EXECUTION_WINDOW,
            blockers=["missing_execution_window_result"],
            execution_window=execution_window,
            owner_command=owner_command,
            broker_call=broker_call,
            context=context,
            owner_confirmation=owner_confirmation,
        )

    execution_window_blockers = _execution_window_blockers(execution_window)
    if execution_window_blockers:
        return _result(
            status=ACTUAL_RUN_BLOCKED_EXECUTION_WINDOW_NOT_READY,
            blockers=execution_window_blockers,
            execution_window=execution_window,
            owner_command=owner_command,
            broker_call=broker_call,
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
            status=ACTUAL_RUN_BLOCKED_OWNER_COMMAND,
            blockers=owner_command_blockers,
            execution_window=execution_window,
            owner_command=owner_command,
            broker_call=broker_call,
            context=context,
            owner_confirmation=owner_confirmation,
        )

    broker_call_blockers = (
        ["missing_broker_call_result"]
        if not broker_call
        else _broker_call_blockers(broker_call)
    )
    if broker_call_blockers:
        return _result(
            status=ACTUAL_RUN_BLOCKED_BROKER_CALL,
            blockers=broker_call_blockers,
            execution_window=execution_window,
            owner_command=owner_command,
            broker_call=broker_call,
            context=context,
            owner_confirmation=owner_confirmation,
        )

    context_blockers = (
        ["missing_actual_run_context"]
        if not context
        else _actual_run_context_blockers(context)
    )
    if context_blockers:
        return _result(
            status=ACTUAL_RUN_BLOCKED_CONTEXT,
            blockers=context_blockers,
            execution_window=execution_window,
            owner_command=owner_command,
            broker_call=broker_call,
            context=context,
            owner_confirmation=owner_confirmation,
        )

    owner_confirmation_blockers = _owner_confirmation_blockers(owner_confirmation)
    if owner_confirmation_blockers:
        return _result(
            status=ACTUAL_RUN_BLOCKED_OWNER_CONFIRMATION,
            blockers=owner_confirmation_blockers,
            execution_window=execution_window,
            owner_command=owner_command,
            broker_call=broker_call,
            context=context,
            owner_confirmation=owner_confirmation,
        )

    return _result(
        status=ACTUAL_RUN_READY_FOR_OWNER_MANUAL_COMMAND,
        blockers=[],
        execution_window=execution_window,
        owner_command=owner_command,
        broker_call=broker_call,
        context=context,
        owner_confirmation=owner_confirmation,
    )


def _execution_window_blockers(execution_window: Mapping[str, Any]) -> list[str]:
    package = _mapping(execution_window.get("execution_window_package"))
    blockers: list[str] = []
    if execution_window.get("status") != WINDOW_READY_STATUS:
        blockers.append("execution_window_status_not_ready")
    if not _bool(package.get("ready")):
        blockers.append("execution_window_package_ready_required")
    if not _bool(package.get("one_order_only")):
        blockers.append("execution_window_package_one_order_only_required")
    if _number(package.get("max_order_attempts"), -1) != 1:
        blockers.append("execution_window_package_max_order_attempts_must_be_one")
    if not _bool(package.get("actual_order_requires_owner_manual_command")):
        blockers.append("execution_window_owner_manual_command_required")
    blockers.extend(_authority_blockers(execution_window, "execution_window_result"))
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


def _broker_call_blockers(broker_call: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if broker_call.get("status") not in BROKER_CALL_READY_STATUSES:
        blockers.append("broker_call_status_not_ready")
    if _network_call_performed(broker_call):
        blockers.append("broker_call_network_call_performed_must_be_false")
    if _order_placement_performed(broker_call):
        blockers.append("broker_call_order_placement_performed_must_be_false")
    blockers.extend(_authority_blockers(broker_call, "broker_call_result"))
    for term in _forbidden_key_terms(broker_call):
        blockers.append(f"broker_call_forbidden_{term}_field")
    return blockers


def _actual_run_context_blockers(context: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if context.get("broker") != "OANDA_DEMO":
        blockers.append("actual_run_context_broker_must_be_oanda_demo")
    if context.get("environment") != "DEMO":
        blockers.append("actual_run_context_environment_must_be_demo")
    for field in CONTEXT_REQUIRED_TRUE_FIELDS:
        if not _bool(context.get(field)):
            blockers.append(f"actual_run_context_{field}_required")
    for field in CONTEXT_REQUIRED_FALSE_FIELDS:
        if _bool(context.get(field)):
            blockers.append(f"actual_run_context_{field}_must_be_false")
    if _number(context.get("max_order_attempts"), -1) != 1:
        blockers.append("actual_run_context_max_order_attempts_must_be_one")
    if _number(context.get("existing_open_orders"), -1) != 0:
        blockers.append("actual_run_context_existing_open_orders_must_be_zero")
    if _number(context.get("existing_pending_orders"), -1) != 0:
        blockers.append("actual_run_context_existing_pending_orders_must_be_zero")
    blockers.extend(_authority_blockers(context, "actual_run_context"))
    return blockers


def _owner_confirmation_blockers(owner_confirmation: Mapping[str, Any]) -> list[str]:
    if not owner_confirmation:
        return ["missing_owner_actual_run_confirmation"]

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
    execution_window: Mapping[str, Any],
    owner_command: Mapping[str, Any],
    broker_call: Mapping[str, Any],
    context: Mapping[str, Any],
    owner_confirmation: Mapping[str, Any],
) -> dict[str, Any]:
    ready = status == ACTUAL_RUN_READY_FOR_OWNER_MANUAL_COMMAND
    return {
        "packet_id": PACKET_ID,
        "command_run_version": COMMAND_RUN_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": _warnings(status),
        "execution_window_summary": _execution_window_summary(execution_window),
        "owner_command_summary": _owner_command_summary(owner_command),
        "broker_call_summary": _broker_call_summary(broker_call),
        "actual_run_context_summary": _actual_run_context_summary(context),
        "owner_confirmation_summary": _owner_confirmation_summary(owner_confirmation),
        "final_manual_command_package": _final_manual_command_package(ready),
        "final_safety_interlocks": _final_safety_interlocks(context, ready),
        "final_evidence_requirements": _final_evidence_requirements(ready),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }


def _execution_window_summary(execution_window: Mapping[str, Any]) -> dict[str, Any]:
    package = _mapping(execution_window.get("execution_window_package"))
    return {
        "status": _text(execution_window.get("status"), "MISSING"),
        "package_ready": _bool(package.get("ready")),
        "one_order_only": _bool(package.get("one_order_only")),
        "max_order_attempts": _number(package.get("max_order_attempts"), 0),
        "actual_order_requires_owner_manual_command": _bool(
            package.get("actual_order_requires_owner_manual_command")
        ),
        "execution_authority_false": not _authority_blockers(
            execution_window, "execution_window_result"
        ),
    }


def _owner_command_summary(owner_command: Mapping[str, Any]) -> dict[str, Any]:
    command = _mapping(owner_command.get("final_owner_command"))
    return {
        "status": _text(owner_command.get("status"), "MISSING"),
        "ready": owner_command.get("status") == OWNER_COMMAND_READY_STATUS,
        "final_owner_command_present": _present(owner_command.get("final_owner_command")),
        "command_type": _text(command.get("command_type"), "MISSING"),
        "script_path": _text(command.get("script_path"), "MISSING"),
        "command_text_present": bool(_text(command.get("command_text"))),
        "sensitive_key_terms_detected": _forbidden_key_terms(owner_command),
        "execution_authority_false": not _authority_blockers(
            owner_command, "owner_command_result"
        ),
    }


def _broker_call_summary(broker_call: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": _text(broker_call.get("status"), "MISSING"),
        "ready_status": broker_call.get("status") in BROKER_CALL_READY_STATUSES,
        "network_call_performed": _network_call_performed(broker_call),
        "order_placement_performed": _order_placement_performed(broker_call),
        "sensitive_key_terms_detected": _forbidden_key_terms(broker_call),
        "execution_authority_false": not _authority_blockers(
            broker_call, "broker_call_result"
        ),
    }


def _actual_run_context_summary(context: Mapping[str, Any]) -> dict[str, Any]:
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
        "execution_window_open": _bool(context.get("execution_window_open")),
        "market_open_or_owner_override": _bool(
            context.get("market_open_or_owner_override")
        ),
    }


def _owner_confirmation_summary(owner_confirmation: Mapping[str, Any]) -> dict[str, bool]:
    return {
        field: _bool(owner_confirmation.get(field))
        for field in OWNER_CONFIRMATION_REQUIRED_TRUE_FIELDS
    }


def _final_manual_command_package(ready: bool) -> dict[str, Any]:
    return {
        "ready": ready,
        "command_type": "powershell",
        "script_path": BROKER_CALL_SCRIPT_PATH,
        "one_order_only": True,
        "max_order_attempts": 1,
        "owner_must_run_manually": True,
        "codex_must_not_run_command": True,
        "runtime_values_are_placeholders": True,
        "command_text": _manual_command_text(),
    }


def _manual_command_text() -> str:
    return "\n".join(
        (
            "$env:OANDA_DEMO_ACCESS_TOKEN = '<OANDA_DEMO_ACCESS_TOKEN_RUNTIME_ONLY>'",
            "$env:OANDA_DEMO_ACCOUNT_ID = '<OANDA_DEMO_ACCOUNT_ID_RUNTIME_ONLY>'",
            "$Instrument = '<INSTRUMENT>'",
            "$Direction = '<DIRECTION>'",
            "$Units = '<UNITS>'",
            "$StopLoss = '<STOP_LOSS>'",
            "$TakeProfit = '<TAKE_PROFIT>'",
            "$RiskAmount = '<RISK_AMOUNT>'",
            "$ClientOrderId = '<CLIENT_ORDER_ID>'",
            f"python {BROKER_CALL_SCRIPT_PATH} `",
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
            "# ONE ORDER ONLY: do not rerun after one attempt.",
            "# Codex must not execute this command.",
        )
    )


def _final_safety_interlocks(
    context: Mapping[str, Any],
    ready: bool,
) -> dict[str, Any]:
    return {
        "ready": ready,
        "demo_only": context.get("environment") == "DEMO",
        "live_endpoint_absent": _bool(context.get("live_endpoint_absent")),
        "one_order_only": _bool(context.get("one_order_only")),
        "max_order_attempts": _number(context.get("max_order_attempts"), 0),
        "order_already_attempted": _bool(context.get("order_already_attempted")),
        "kill_switch_ready": _bool(context.get("kill_switch_ready")),
        "daily_stop_ready": _bool(context.get("daily_stop_ready")),
        "max_loss_gate_ready": _bool(context.get("max_loss_gate_ready")),
        "stop_loss_ready": _bool(context.get("stop_loss_ready")),
        "take_profit_ready": _bool(context.get("take_profit_ready")),
        "second_order_allowed": False,
        "autonomous_retry_allowed": False,
        "live_order_allowed": False,
    }


def _final_evidence_requirements(ready: bool) -> dict[str, Any]:
    return {
        "ready": ready,
        "items": list(FINAL_EVIDENCE_ITEMS),
        "post_trade_evidence_required": True,
        "sanitize_before_repo_storage": True,
        "credential_or_account_identifier_storage_allowed": False,
    }


def _network_call_performed(payload: Mapping[str, Any]) -> bool:
    attempt = _mapping(payload.get("execution_attempt"))
    return _bool(payload.get("network_call_performed")) or _bool(
        attempt.get("network_call_performed")
    )


def _order_placement_performed(payload: Mapping[str, Any]) -> bool:
    attempt = _mapping(payload.get("execution_attempt"))
    return _bool(payload.get("order_placement_performed")) or _bool(
        attempt.get("order_placement_performed")
    )


def _warnings(status: str) -> list[str]:
    warnings = [
        "owner_command_package_only",
        "execution_authority_false",
        "no_oanda_call_performed_by_codex",
        "no_broker_call_performed_by_codex",
        "no_order_placement_performed_by_codex",
        "no_credentials_or_account_ids_read_or_persisted",
        "owner_manual_run_only",
        "one_order_cap_remains_in_force",
    ]
    if status == ACTUAL_RUN_READY_FOR_OWNER_MANUAL_COMMAND:
        warnings.append("owner_can_run_exact_manual_demo_order_command_once")
    return warnings


def _next_safe_action(status: str) -> str:
    if status == ACTUAL_RUN_READY_FOR_OWNER_MANUAL_COMMAND:
        return "owner_can_run_exact_manual_demo_order_command_once"
    return "repair_blocker_before_actual_owner_command"


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
