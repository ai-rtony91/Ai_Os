from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-BROKER-CALL-IMPLEMENTATION-ONE-ORDER-MANUAL-RUN-V1"
BROKER_CALL_VERSION = "v1"

BROKER_CALL_BLOCKED_MISSING_FINAL_OWNER_RUN = (
    "BROKER_CALL_BLOCKED_MISSING_FINAL_OWNER_RUN"
)
BROKER_CALL_BLOCKED_FINAL_OWNER_RUN_NOT_READY = (
    "BROKER_CALL_BLOCKED_FINAL_OWNER_RUN_NOT_READY"
)
BROKER_CALL_BLOCKED_CONTEXT = "BROKER_CALL_BLOCKED_CONTEXT"
BROKER_CALL_BLOCKED_ORDER_PAYLOAD = "BROKER_CALL_BLOCKED_ORDER_PAYLOAD"
BROKER_CALL_BLOCKED_OWNER_APPROVAL = "BROKER_CALL_BLOCKED_OWNER_APPROVAL"
BROKER_CALL_DRY_RUN_READY = "BROKER_CALL_DRY_RUN_READY"
BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED = "BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED"
BROKER_CALL_ATTEMPTED_DEMO_ORDER_ONCE = "BROKER_CALL_ATTEMPTED_DEMO_ORDER_ONCE"
BROKER_CALL_REJECTED = "BROKER_CALL_REJECTED"

FINAL_OWNER_RUN_READY_STATUS = "OWNER_RUN_READY_FOR_EXPLICIT_MANUAL_COMMAND"
DEMO_API_BASE_URL_PREFIX = "https://api-fxpractice.oanda.com"
RUNTIME_ACCOUNT_ID_REFERENCE = "RUNTIME_ONLY_ACCOUNT_ID"
RUNTIME_TOKEN_REFERENCE = "RUNTIME_ONLY_BEARER_TOKEN"
TRANSPORT_TIMEOUT_SECONDS = 10

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
    "owner_approved_actual_oanda_demo_broker_call",
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

BROKER_CONTEXT_REQUIRED_TRUE_FIELDS = (
    "demo_environment",
    "runtime_access_token_present",
    "runtime_account_id_present",
    "token_runtime_only",
    "account_id_runtime_only",
    "one_order_only",
    "kill_switch_ready",
    "daily_stop_ready",
    "max_loss_gate_ready",
    "pre_trade_evidence_ready",
    "post_trade_evidence_plan_ready",
)

BROKER_CONTEXT_REQUIRED_FALSE_FIELDS = (
    "live_environment",
    "credential_persistence_detected",
    "account_id_persistence_detected",
    "order_already_attempted",
    "broker_network_call_performed",
    "order_placement_performed",
)

FORBIDDEN_ORDER_PAYLOAD_KEY_TERMS = (
    "account_id",
    "token",
    "credential",
    "secret",
    "password",
    "authorization",
)

SENSITIVE_EVIDENCE_KEY_TERMS = (
    "account_id",
    "accountid",
    "access_token",
    "token",
    "credential",
    "secret",
    "password",
    "authorization",
    "auth",
)


def evaluate_oanda_demo_broker_call_one_order_manual_run_v1(
    final_owner_run_result: dict | None = None,
    broker_call_context: dict | None = None,
    sanitized_order_payload: dict | None = None,
    owner_broker_call_approval: dict | None = None,
    execute_demo_order: bool = False,
    http_transport: object | None = None,
) -> dict:
    final_owner_run = _mapping(final_owner_run_result)
    context = _mapping(broker_call_context)
    order_payload = _mapping(sanitized_order_payload)
    owner_approval = _mapping(owner_broker_call_approval)

    if not final_owner_run:
        return _result(
            status=BROKER_CALL_BLOCKED_MISSING_FINAL_OWNER_RUN,
            blockers=["missing_final_owner_run_result"],
            warnings=_warnings(BROKER_CALL_BLOCKED_MISSING_FINAL_OWNER_RUN),
            final_owner_run=final_owner_run,
            context=context,
            order_payload=order_payload,
            owner_approval=owner_approval,
            execute_demo_order=execute_demo_order,
            transport_request=None,
            transport_result=None,
            network_call_performed=False,
            order_placement_performed=False,
            order_attempt_count=0,
        )

    unsafe_blockers = _unsafe_execution_blockers(
        final_owner_run,
        _mapping(final_owner_run.get("manual_runtime_run_contract")),
        context,
        order_payload,
        owner_approval,
    )
    final_owner_blockers = _final_owner_run_blockers(final_owner_run)
    context_blockers = _broker_context_blockers(context)
    order_blockers = _order_payload_blockers(order_payload)
    owner_blockers = _owner_approval_blockers(owner_approval)

    blockers = _unique(
        unsafe_blockers
        + final_owner_blockers
        + context_blockers
        + order_blockers
        + owner_blockers
    )
    status = _status(
        unsafe_blockers=unsafe_blockers,
        final_owner_blockers=final_owner_blockers,
        context_blockers=context_blockers,
        order_blockers=order_blockers,
        owner_blockers=owner_blockers,
        execute_demo_order=execute_demo_order,
        http_transport=http_transport,
    )

    transport_request = _transport_request(context, order_payload) if not blockers else None
    transport_result: dict[str, Any] | None = None
    network_call_performed = False
    order_placement_performed = False
    order_attempt_count = 0

    if status == BROKER_CALL_ATTEMPTED_DEMO_ORDER_ONCE and transport_request is not None:
        network_call_performed = True
        order_attempt_count = 1
        raw_transport_result = http_transport(transport_request)  # type: ignore[misc]
        transport_result = _sanitize_transport_result(raw_transport_result)
        order_placement_performed = _transport_result_indicates_success(
            raw_transport_result
        )

    return _result(
        status=status,
        blockers=blockers,
        warnings=_warnings(status),
        final_owner_run=final_owner_run,
        context=context,
        order_payload=order_payload,
        owner_approval=owner_approval,
        execute_demo_order=execute_demo_order,
        transport_request=transport_request,
        transport_result=transport_result,
        network_call_performed=network_call_performed,
        order_placement_performed=order_placement_performed,
        order_attempt_count=order_attempt_count,
    )


def _status(
    *,
    unsafe_blockers: list[str],
    final_owner_blockers: list[str],
    context_blockers: list[str],
    order_blockers: list[str],
    owner_blockers: list[str],
    execute_demo_order: bool,
    http_transport: object | None,
) -> str:
    if unsafe_blockers:
        return BROKER_CALL_REJECTED
    if final_owner_blockers:
        return BROKER_CALL_BLOCKED_FINAL_OWNER_RUN_NOT_READY
    if context_blockers:
        return BROKER_CALL_BLOCKED_CONTEXT
    if order_blockers:
        return BROKER_CALL_BLOCKED_ORDER_PAYLOAD
    if owner_blockers:
        return BROKER_CALL_BLOCKED_OWNER_APPROVAL
    if not execute_demo_order:
        return BROKER_CALL_DRY_RUN_READY
    if not callable(http_transport):
        return BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED
    return BROKER_CALL_ATTEMPTED_DEMO_ORDER_ONCE


def _final_owner_run_blockers(final_owner_run: Mapping[str, Any]) -> list[str]:
    contract = _mapping(final_owner_run.get("manual_runtime_run_contract"))
    blockers: list[str] = []
    if final_owner_run.get("status") != FINAL_OWNER_RUN_READY_STATUS:
        blockers.append("final_owner_run_status_not_ready")
    if not _bool(contract.get("ready")):
        blockers.append("manual_runtime_run_contract_ready_required")
    if not _bool(contract.get("one_order_only")):
        blockers.append("manual_runtime_run_contract_one_order_only_required")
    if _number(contract.get("max_order_attempts"), -1) != 1:
        blockers.append("manual_runtime_run_contract_max_order_attempts_must_be_one")
    if not _bool(contract.get("actual_execution_requires_owner_to_run_command")):
        blockers.append("manual_runtime_run_contract_owner_command_required")
    blockers.extend(_authority_blockers(final_owner_run, "final_owner_run_result"))
    return blockers


def _broker_context_blockers(context: Mapping[str, Any]) -> list[str]:
    if not context:
        return ["missing_broker_call_context"]

    blockers: list[str] = []
    if context.get("broker") != "OANDA_DEMO":
        blockers.append("broker_call_context_broker_must_be_oanda_demo")
    if context.get("environment") != "DEMO":
        blockers.append("broker_call_context_environment_must_be_demo")

    demo_base_url = _text(context.get("demo_api_base_url"))
    live_base_url = _text(context.get("live_api_base_url"))
    if not demo_base_url.startswith(DEMO_API_BASE_URL_PREFIX):
        blockers.append("broker_call_context_demo_api_base_url_must_be_practice")
    if live_base_url:
        blockers.append("broker_call_context_live_api_base_url_must_be_absent")

    for field in BROKER_CONTEXT_REQUIRED_TRUE_FIELDS:
        if not _bool(context.get(field)):
            blockers.append(f"broker_call_context_{field}_required")
    for field in BROKER_CONTEXT_REQUIRED_FALSE_FIELDS:
        if _bool(context.get(field)):
            blockers.append(f"broker_call_context_{field}_must_be_false")

    if _number(context.get("max_order_attempts"), -1) != 1:
        blockers.append("broker_call_context_max_order_attempts_must_be_one")
    if _number(context.get("existing_open_orders"), -1) != 0:
        blockers.append("broker_call_context_existing_open_orders_must_be_zero")
    if _number(context.get("existing_pending_orders"), -1) != 0:
        blockers.append("broker_call_context_existing_pending_orders_must_be_zero")

    blockers.extend(_authority_blockers(context, "broker_call_context"))
    return blockers


def _order_payload_blockers(order_payload: Mapping[str, Any]) -> list[str]:
    if not order_payload:
        return ["missing_sanitized_order_payload"]

    blockers: list[str] = []
    if not _text(order_payload.get("instrument")):
        blockers.append("order_payload_instrument_required")
    if order_payload.get("direction") not in {"BUY", "SELL"}:
        blockers.append("order_payload_direction_must_be_buy_or_sell")
    if order_payload.get("order_type") not in {"MARKET", "LIMIT", "STOP"}:
        blockers.append("order_payload_order_type_must_be_market_limit_or_stop")
    if not _positive_number(order_payload.get("units")):
        blockers.append("order_payload_units_must_be_positive")
    if "stop_loss" not in order_payload or order_payload.get("stop_loss") is None:
        blockers.append("order_payload_stop_loss_required")
    if "take_profit" not in order_payload or order_payload.get("take_profit") is None:
        blockers.append("order_payload_take_profit_required")
    if not _positive_number(order_payload.get("risk_amount")):
        blockers.append("order_payload_risk_amount_must_be_positive")
    if _number(order_payload.get("reward_risk_ratio"), 0) < 1.0:
        blockers.append("order_payload_reward_risk_ratio_must_be_at_least_one")
    if not _sanitized_client_order_id(order_payload.get("client_order_id")):
        blockers.append("order_payload_client_order_id_must_be_sanitized")

    for term in _forbidden_order_payload_key_terms(order_payload):
        blockers.append(f"order_payload_forbidden_{term}_field")
    blockers.extend(_authority_blockers(order_payload, "order_payload"))
    return blockers


def _owner_approval_blockers(owner_approval: Mapping[str, Any]) -> list[str]:
    if not owner_approval:
        return ["missing_owner_broker_call_approval"]

    blockers: list[str] = []
    for field in OWNER_APPROVAL_REQUIRED_TRUE_FIELDS:
        if not _bool(owner_approval.get(field)):
            blockers.append(f"{field}_required")
    blockers.extend(_authority_blockers(owner_approval, "owner_approval"))
    return blockers


def _result(
    *,
    status: str,
    blockers: list[str],
    warnings: list[str],
    final_owner_run: Mapping[str, Any],
    context: Mapping[str, Any],
    order_payload: Mapping[str, Any],
    owner_approval: Mapping[str, Any],
    execute_demo_order: bool,
    transport_request: Mapping[str, Any] | None,
    transport_result: Mapping[str, Any] | None,
    network_call_performed: bool,
    order_placement_performed: bool,
    order_attempt_count: int,
) -> dict[str, Any]:
    return {
        "packet_id": PACKET_ID,
        "broker_call_version": BROKER_CALL_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "final_owner_run_summary": _final_owner_run_summary(final_owner_run),
        "broker_call_context_summary": _broker_context_summary(context),
        "sanitized_order_summary": _sanitized_order_summary(order_payload),
        "owner_approval_summary": _owner_approval_summary(owner_approval),
        "oanda_order_payload": _oanda_order_payload(order_payload)
        if transport_request
        else None,
        "transport_request_preview": dict(transport_request)
        if transport_request
        else None,
        "transport_result": dict(transport_result) if transport_result else None,
        "execution_attempt": {
            "execute_demo_order_requested": execute_demo_order is True,
            "network_call_performed": network_call_performed,
            "order_placement_performed": order_placement_performed,
            "order_attempt_count": order_attempt_count,
            "account_id_reference": RUNTIME_ACCOUNT_ID_REFERENCE,
            "authorization_reference": RUNTIME_TOKEN_REFERENCE,
        },
        "manual_runtime_contract": {
            "broker": "OANDA_DEMO",
            "environment": "DEMO",
            "demo_endpoint_only": True,
            "one_order_only": True,
            "max_order_attempts": 1,
            "transport_injection_required_for_network_call": True,
            "autonomous_retry_allowed": False,
            "second_order_allowed": False,
        },
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }


def _transport_request(
    context: Mapping[str, Any], order_payload: Mapping[str, Any]
) -> dict[str, Any]:
    base_url = _trim_trailing_slash(_text(context.get("demo_api_base_url")))
    return {
        "method": "POST",
        "url": f"{base_url}/v3/accounts/{RUNTIME_ACCOUNT_ID_REFERENCE}/orders",
        "headers": {
            "Authorization": f"Bearer {RUNTIME_TOKEN_REFERENCE}",
            "Content-Type": "application/json",
        },
        "json": _oanda_order_payload(order_payload),
        "timeout_seconds": TRANSPORT_TIMEOUT_SECONDS,
    }


def _oanda_order_payload(order_payload: Mapping[str, Any]) -> dict[str, Any]:
    direction = order_payload.get("direction")
    return {
        "order": {
            "type": order_payload.get("order_type"),
            "instrument": order_payload.get("instrument"),
            "units": _signed_units(order_payload.get("units"), direction),
            "positionFill": "DEFAULT",
            "clientExtensions": {
                "id": order_payload.get("client_order_id"),
            },
            "stopLossOnFill": {
                "price": str(order_payload.get("stop_loss")),
            },
            "takeProfitOnFill": {
                "price": str(order_payload.get("take_profit")),
            },
        }
    }


def _final_owner_run_summary(final_owner_run: Mapping[str, Any]) -> dict[str, Any]:
    contract = _mapping(final_owner_run.get("manual_runtime_run_contract"))
    return {
        "status": _text(final_owner_run.get("status"), "MISSING"),
        "contract_ready": _bool(contract.get("ready")),
        "one_order_only": _bool(contract.get("one_order_only")),
        "max_order_attempts": _number(contract.get("max_order_attempts"), 0),
        "actual_execution_requires_owner_to_run_command": _bool(
            contract.get("actual_execution_requires_owner_to_run_command")
        ),
        "execution_authority_false": not _authority_blockers(
            final_owner_run, "final_owner_run_result"
        ),
    }


def _broker_context_summary(context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker": _text(context.get("broker"), "MISSING"),
        "environment": _text(context.get("environment"), "MISSING"),
        "demo_environment": _bool(context.get("demo_environment")),
        "live_environment": _bool(context.get("live_environment")),
        "demo_api_base_url_is_practice": _text(
            context.get("demo_api_base_url")
        ).startswith(DEMO_API_BASE_URL_PREFIX),
        "live_api_base_url_present": bool(_text(context.get("live_api_base_url"))),
        "runtime_access_token_present": _bool(
            context.get("runtime_access_token_present")
        ),
        "runtime_account_id_present": _bool(
            context.get("runtime_account_id_present")
        ),
        "token_runtime_only": _bool(context.get("token_runtime_only")),
        "account_id_runtime_only": _bool(context.get("account_id_runtime_only")),
        "credential_persistence_detected": _bool(
            context.get("credential_persistence_detected")
        ),
        "account_id_persistence_detected": _bool(
            context.get("account_id_persistence_detected")
        ),
        "one_order_only": _bool(context.get("one_order_only")),
        "max_order_attempts": _number(context.get("max_order_attempts"), 0),
        "order_already_attempted": _bool(context.get("order_already_attempted")),
        "existing_open_orders": _number(context.get("existing_open_orders"), 0),
        "existing_pending_orders": _number(context.get("existing_pending_orders"), 0),
        "kill_switch_ready": _bool(context.get("kill_switch_ready")),
        "daily_stop_ready": _bool(context.get("daily_stop_ready")),
        "max_loss_gate_ready": _bool(context.get("max_loss_gate_ready")),
        "pre_trade_evidence_ready": _bool(context.get("pre_trade_evidence_ready")),
        "post_trade_evidence_plan_ready": _bool(
            context.get("post_trade_evidence_plan_ready")
        ),
        "broker_network_call_performed": _bool(
            context.get("broker_network_call_performed")
        ),
        "order_placement_performed": _bool(context.get("order_placement_performed")),
    }


def _sanitized_order_summary(order_payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "instrument": _text(order_payload.get("instrument"), "MISSING"),
        "direction": _text(order_payload.get("direction"), "MISSING"),
        "order_type": _text(order_payload.get("order_type"), "MISSING"),
        "units": _number(order_payload.get("units"), 0),
        "signed_units_preview": _signed_units(
            order_payload.get("units"), order_payload.get("direction")
        )
        if _positive_number(order_payload.get("units"))
        else "MISSING",
        "stop_loss_present": "stop_loss" in order_payload
        and order_payload.get("stop_loss") is not None,
        "take_profit_present": "take_profit" in order_payload
        and order_payload.get("take_profit") is not None,
        "risk_amount": _number(order_payload.get("risk_amount"), 0),
        "reward_risk_ratio": _number(order_payload.get("reward_risk_ratio"), 0),
        "client_order_id_present": bool(_text(order_payload.get("client_order_id"))),
        "forbidden_payload_keys_detected": _forbidden_order_payload_key_terms(
            order_payload
        ),
    }


def _owner_approval_summary(owner_approval: Mapping[str, Any]) -> dict[str, bool]:
    return {
        field: _bool(owner_approval.get(field))
        for field in OWNER_APPROVAL_REQUIRED_TRUE_FIELDS
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


def _forbidden_order_payload_key_terms(value: Any) -> list[str]:
    found: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            for key, child in node.items():
                key_text = str(key).lower()
                for term in FORBIDDEN_ORDER_PAYLOAD_KEY_TERMS:
                    if term in key_text and term not in found:
                        found.append(term)
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)
    return found


def _sanitize_transport_result(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return _sanitize_mapping(value)
    return {"type": type(value).__name__, "value": _safe_scalar(value)}


def _sanitize_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, child in value.items():
        key_text = str(key)
        if _sensitive_key(key_text):
            sanitized[key_text] = "REDACTED_RUNTIME_ONLY_REFERENCE"
        else:
            sanitized[key_text] = _sanitize_evidence_value(child)
    return sanitized


def _sanitize_evidence_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return _sanitize_mapping(value)
    if isinstance(value, list):
        return [_sanitize_evidence_value(child) for child in value]
    return _safe_scalar(value)


def _safe_scalar(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _sensitive_key(key: str) -> bool:
    key_text = key.lower()
    return any(term in key_text for term in SENSITIVE_EVIDENCE_KEY_TERMS)


def _transport_result_indicates_success(raw_transport_result: Any) -> bool:
    result = _mapping(raw_transport_result)
    status_code = _number(result.get("status_code"), 0)
    status_text = _text(result.get("status")).lower()
    return (
        status_code in {200, 201}
        or status_text in {"success", "accepted", "created"}
        or _bool(result.get("success"))
        or _bool(result.get("accepted"))
        or _bool(result.get("created"))
    )


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _warnings(status: str) -> list[str]:
    warnings = [
        "manual_owner_runtime_only",
        "execution_authority_false",
        "demo_endpoint_only",
        "no_live_trading",
        "no_autonomous_execution",
        "no_scheduler_daemon_or_webhook",
        "no_credentials_or_account_ids_persisted",
    ]
    if status == BROKER_CALL_DRY_RUN_READY:
        warnings.append("dry_run_preview_only_no_network_call")
    if status == BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED:
        warnings.append("transport_must_be_injected_by_owner_runtime")
    if status == BROKER_CALL_ATTEMPTED_DEMO_ORDER_ONCE:
        warnings.append("manual_injected_transport_called_once")
    return warnings


def _next_safe_action(status: str) -> str:
    return {
        BROKER_CALL_BLOCKED_MISSING_FINAL_OWNER_RUN: "provide_final_owner_run_result",
        BROKER_CALL_BLOCKED_FINAL_OWNER_RUN_NOT_READY: (
            "repair_final_owner_runtime_run_before_broker_call"
        ),
        BROKER_CALL_BLOCKED_CONTEXT: "provide_oanda_demo_broker_call_context",
        BROKER_CALL_BLOCKED_ORDER_PAYLOAD: "provide_sanitized_one_order_payload",
        BROKER_CALL_BLOCKED_OWNER_APPROVAL: (
            "complete_owner_broker_call_approval_before_manual_run"
        ),
        BROKER_CALL_DRY_RUN_READY: "review_dry_run_transport_request_preview",
        BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED: (
            "owner_must_inject_runtime_http_transport_for_manual_demo_call"
        ),
        BROKER_CALL_ATTEMPTED_DEMO_ORDER_ONCE: "capture_sanitized_post_trade_evidence",
        BROKER_CALL_REJECTED: "remove_unsafe_execution_authority_request",
    }.get(status, "stop_and_review_broker_call_state")


def _trim_trailing_slash(value: str) -> str:
    return value.rstrip("/")


def _signed_units(units: Any, direction: Any) -> str:
    numeric_units = _number(units, 0)
    if direction == "SELL":
        numeric_units = -abs(numeric_units)
    else:
        numeric_units = abs(numeric_units)
    if isinstance(numeric_units, float) and numeric_units.is_integer():
        return str(int(numeric_units))
    return str(numeric_units)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _number(value: Any, default: float) -> float:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else default


def _positive_number(value: Any) -> bool:
    return _number(value, 0) > 0


def _sanitized_client_order_id(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    client_order_id = value.strip()
    if not client_order_id or client_order_id != value:
        return False
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.:")
    return all(character in allowed for character in client_order_id)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
