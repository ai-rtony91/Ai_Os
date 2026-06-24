from __future__ import annotations

import json
from typing import Any, Mapping
from urllib import error, request


PACKET_ID = (
    "AIOS-FOREX-OANDA-DEMO-RUNTIME-HTTP-TRANSPORT-ONE-ORDER-OWNER-RUN-V1"
)
TRANSPORT_VERSION = "v1"

TRANSPORT_BLOCKED_MISSING_OWNER_COMMAND = (
    "TRANSPORT_BLOCKED_MISSING_OWNER_COMMAND"
)
TRANSPORT_BLOCKED_OWNER_COMMAND_NOT_READY = (
    "TRANSPORT_BLOCKED_OWNER_COMMAND_NOT_READY"
)
TRANSPORT_BLOCKED_BROKER_CALL_NOT_READY = (
    "TRANSPORT_BLOCKED_BROKER_CALL_NOT_READY"
)
TRANSPORT_BLOCKED_CONTEXT = "TRANSPORT_BLOCKED_CONTEXT"
TRANSPORT_BLOCKED_ORDER_PAYLOAD = "TRANSPORT_BLOCKED_ORDER_PAYLOAD"
TRANSPORT_BLOCKED_OWNER_CONFIRMATION = "TRANSPORT_BLOCKED_OWNER_CONFIRMATION"
TRANSPORT_DRY_RUN_READY = "TRANSPORT_DRY_RUN_READY"
TRANSPORT_BLOCKED_RUNTIME_CREDENTIALS_MISSING = (
    "TRANSPORT_BLOCKED_RUNTIME_CREDENTIALS_MISSING"
)
TRANSPORT_BLOCKED_HTTP_POST_CALLABLE_REQUIRED = (
    "TRANSPORT_BLOCKED_HTTP_POST_CALLABLE_REQUIRED"
)
TRANSPORT_ATTEMPTED_OANDA_DEMO_ORDER_ONCE = (
    "TRANSPORT_ATTEMPTED_OANDA_DEMO_ORDER_ONCE"
)
TRANSPORT_REJECTED = "TRANSPORT_REJECTED"

ACTUAL_OWNER_COMMAND_READY_STATUS = "ACTUAL_RUN_READY_FOR_OWNER_MANUAL_COMMAND"
BROKER_CALL_READY_STATUSES = {
    "BROKER_CALL_DRY_RUN_READY",
    "BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED",
}
DEMO_API_BASE_URL_PREFIX = "https://api-fxpractice.oanda.com"
REDACTED_ACCOUNT_ID_REFERENCE = "REDACTED_RUNTIME_ACCOUNT_ID"
REDACTED_TOKEN_REFERENCE = "REDACTED_RUNTIME_ACCESS_TOKEN"
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

SENSITIVE_KEY_TERMS = (
    "account_id",
    "accountid",
    "accountID",
    "access_token",
    "token",
    "credential",
    "secret",
    "password",
    "authorization",
    "auth",
)

TRANSPORT_CONTEXT_REQUIRED_TRUE_FIELDS = (
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

TRANSPORT_CONTEXT_REQUIRED_FALSE_FIELDS = (
    "credential_persistence_detected",
    "account_id_persistence_detected",
    "order_already_attempted",
)

OWNER_CONFIRMATION_REQUIRED_TRUE_FIELDS = (
    "owner_confirmed_transport_reviewed",
    "owner_confirmed_actual_demo_order_intent",
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

POST_TRADE_EVIDENCE_REQUIREMENTS = (
    "capture_http_status_code",
    "capture_sanitized_order_transaction_reference",
    "capture_fill_or_rejection_status",
    "capture_stop_loss_take_profit_attachment_status",
    "record_balance_nav_snapshot",
    "record_timestamp_utc",
    "confirm_no_credentials_or_account_ids_persisted",
    "confirm_no_second_order_attempted",
)


def evaluate_oanda_demo_runtime_http_transport_one_order_owner_run_v1(
    actual_owner_command_result: dict | None = None,
    broker_call_result: dict | None = None,
    transport_context: dict | None = None,
    sanitized_order_payload: dict | None = None,
    owner_transport_confirmation: dict | None = None,
    execute_transport: bool = False,
    runtime_access_token: str | None = None,
    runtime_account_id: str | None = None,
    http_post_callable: object | None = None,
) -> dict:
    owner_command = _mapping(actual_owner_command_result)
    broker_call = _mapping(broker_call_result)
    context = _mapping(transport_context)
    order_payload = _mapping(sanitized_order_payload)
    owner_confirmation = _mapping(owner_transport_confirmation)

    if not owner_command:
        return _result(
            status=TRANSPORT_BLOCKED_MISSING_OWNER_COMMAND,
            blockers=["missing_actual_owner_command_result"],
            warnings=_warnings(TRANSPORT_BLOCKED_MISSING_OWNER_COMMAND),
            owner_command=owner_command,
            broker_call=broker_call,
            context=context,
            order_payload=order_payload,
            owner_confirmation=owner_confirmation,
            execute_transport=execute_transport,
            transport_request=None,
            raw_transport_result=None,
            runtime_access_token=runtime_access_token,
            runtime_account_id=runtime_account_id,
            network_call_performed=False,
            order_placement_performed=False,
            order_attempt_count=0,
        )

    unsafe_blockers = _unsafe_input_blockers(
        broker_call=broker_call,
        order_payload=order_payload,
    )
    owner_command_blockers = _actual_owner_command_blockers(owner_command)
    broker_call_blockers = _broker_call_blockers(broker_call)
    context_blockers = _transport_context_blockers(context)
    order_payload_blockers = _order_payload_blockers(order_payload)
    owner_confirmation_blockers = _owner_confirmation_blockers(owner_confirmation)

    status = _status(
        unsafe_blockers=unsafe_blockers,
        owner_command_blockers=owner_command_blockers,
        broker_call_blockers=broker_call_blockers,
        context_blockers=context_blockers,
        order_payload_blockers=order_payload_blockers,
        owner_confirmation_blockers=owner_confirmation_blockers,
        execute_transport=execute_transport,
        runtime_access_token=runtime_access_token,
        runtime_account_id=runtime_account_id,
        http_post_callable=http_post_callable,
    )
    blockers = _unique(
        unsafe_blockers
        + owner_command_blockers
        + broker_call_blockers
        + context_blockers
        + order_payload_blockers
        + owner_confirmation_blockers
    )

    transport_request = (
        _transport_request(
            context=context,
            order_payload=order_payload,
            runtime_access_token=runtime_access_token,
            runtime_account_id=runtime_account_id,
        )
        if status
        in {
            TRANSPORT_DRY_RUN_READY,
            TRANSPORT_BLOCKED_RUNTIME_CREDENTIALS_MISSING,
            TRANSPORT_BLOCKED_HTTP_POST_CALLABLE_REQUIRED,
            TRANSPORT_ATTEMPTED_OANDA_DEMO_ORDER_ONCE,
        }
        else None
    )

    raw_transport_result: Any = None
    network_call_performed = False
    order_placement_performed = False
    order_attempt_count = 0

    if (
        status == TRANSPORT_ATTEMPTED_OANDA_DEMO_ORDER_ONCE
        and transport_request is not None
    ):
        network_call_performed = True
        order_attempt_count = 1
        raw_transport_result = http_post_callable(transport_request)  # type: ignore[misc]
        order_placement_performed = _transport_result_indicates_success(
            raw_transport_result
        )

    return _result(
        status=status,
        blockers=blockers,
        warnings=_warnings(status),
        owner_command=owner_command,
        broker_call=broker_call,
        context=context,
        order_payload=order_payload,
        owner_confirmation=owner_confirmation,
        execute_transport=execute_transport,
        transport_request=transport_request,
        raw_transport_result=raw_transport_result,
        runtime_access_token=runtime_access_token,
        runtime_account_id=runtime_account_id,
        network_call_performed=network_call_performed,
        order_placement_performed=order_placement_performed,
        order_attempt_count=order_attempt_count,
    )


def post_oanda_demo_order_with_urllib(post_request: Mapping[str, Any]) -> dict[str, Any]:
    payload = json.dumps(post_request.get("json", {})).encode("utf-8")
    headers = {
        str(key): str(value)
        for key, value in _mapping(post_request.get("headers")).items()
    }
    req = request.Request(
        url=_text(post_request.get("url")),
        data=payload,
        headers=headers,
        method=_text(post_request.get("method"), "POST"),
    )
    timeout = _number(
        post_request.get("timeout_seconds"),
        TRANSPORT_TIMEOUT_SECONDS,
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:  # nosec B310
            body = response.read().decode("utf-8")
            return {
                "status_code": response.getcode(),
                "status": "created" if response.getcode() in {200, 201} else "response",
                "body": _parse_json_body(body),
            }
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {
            "status_code": exc.code,
            "status": "http_error",
            "body": _parse_json_body(body),
        }
    except error.URLError as exc:
        return {
            "status_code": 0,
            "status": "url_error",
            "reason": str(exc.reason),
        }


def _status(
    *,
    unsafe_blockers: list[str],
    owner_command_blockers: list[str],
    broker_call_blockers: list[str],
    context_blockers: list[str],
    order_payload_blockers: list[str],
    owner_confirmation_blockers: list[str],
    execute_transport: bool,
    runtime_access_token: str | None,
    runtime_account_id: str | None,
    http_post_callable: object | None,
) -> str:
    if unsafe_blockers:
        return TRANSPORT_REJECTED
    if owner_command_blockers:
        return TRANSPORT_BLOCKED_OWNER_COMMAND_NOT_READY
    if broker_call_blockers:
        return TRANSPORT_BLOCKED_BROKER_CALL_NOT_READY
    if context_blockers:
        return TRANSPORT_BLOCKED_CONTEXT
    if order_payload_blockers:
        return TRANSPORT_BLOCKED_ORDER_PAYLOAD
    if owner_confirmation_blockers:
        return TRANSPORT_BLOCKED_OWNER_CONFIRMATION
    if not execute_transport:
        return TRANSPORT_DRY_RUN_READY
    if not _present(runtime_access_token) or not _present(runtime_account_id):
        return TRANSPORT_BLOCKED_RUNTIME_CREDENTIALS_MISSING
    if not callable(http_post_callable):
        return TRANSPORT_BLOCKED_HTTP_POST_CALLABLE_REQUIRED
    return TRANSPORT_ATTEMPTED_OANDA_DEMO_ORDER_ONCE


def _actual_owner_command_blockers(owner_command: Mapping[str, Any]) -> list[str]:
    package = _mapping(owner_command.get("final_manual_command_package"))
    blockers: list[str] = []
    if owner_command.get("status") != ACTUAL_OWNER_COMMAND_READY_STATUS:
        blockers.append("actual_owner_command_status_not_ready")
    if not _bool(package.get("ready")):
        blockers.append("actual_owner_command_package_ready_required")
    if not _bool(package.get("one_order_only")):
        blockers.append("actual_owner_command_package_one_order_only_required")
    if _number(package.get("max_order_attempts"), -1) != 1:
        blockers.append("actual_owner_command_package_max_order_attempts_must_be_one")
    blockers.extend(_authority_blockers(owner_command, "actual_owner_command_result"))
    return blockers


def _broker_call_blockers(broker_call: Mapping[str, Any]) -> list[str]:
    if not broker_call:
        return ["missing_broker_call_result"]

    blockers: list[str] = []
    if broker_call.get("status") not in BROKER_CALL_READY_STATUSES:
        blockers.append("broker_call_status_not_ready")
    if _network_call_performed(broker_call):
        blockers.append("broker_call_network_call_performed_must_be_false")
    if _order_placement_performed(broker_call):
        blockers.append("broker_call_order_placement_performed_must_be_false")
    blockers.extend(_authority_blockers(broker_call, "broker_call_result"))
    return blockers


def _transport_context_blockers(context: Mapping[str, Any]) -> list[str]:
    if not context:
        return ["missing_transport_context"]

    blockers: list[str] = []
    if context.get("broker") != "OANDA_DEMO":
        blockers.append("transport_context_broker_must_be_oanda_demo")
    if context.get("environment") != "DEMO":
        blockers.append("transport_context_environment_must_be_demo")

    demo_base_url = _text(context.get("demo_api_base_url"))
    live_base_url = _text(context.get("live_api_base_url"))
    if not demo_base_url.startswith(DEMO_API_BASE_URL_PREFIX):
        blockers.append("transport_context_demo_api_base_url_must_be_practice")
    if live_base_url:
        blockers.append("transport_context_live_api_base_url_must_be_absent")

    for field in TRANSPORT_CONTEXT_REQUIRED_TRUE_FIELDS:
        if not _bool(context.get(field)):
            blockers.append(f"transport_context_{field}_required")
    for field in TRANSPORT_CONTEXT_REQUIRED_FALSE_FIELDS:
        if _bool(context.get(field)):
            blockers.append(f"transport_context_{field}_must_be_false")

    if _number(context.get("max_order_attempts"), -1) != 1:
        blockers.append("transport_context_max_order_attempts_must_be_one")
    if _number(context.get("existing_open_orders"), -1) != 0:
        blockers.append("transport_context_existing_open_orders_must_be_zero")
    if _number(context.get("existing_pending_orders"), -1) != 0:
        blockers.append("transport_context_existing_pending_orders_must_be_zero")
    blockers.extend(_authority_blockers(context, "transport_context"))
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
    blockers.extend(_authority_blockers(order_payload, "order_payload"))
    return blockers


def _owner_confirmation_blockers(owner_confirmation: Mapping[str, Any]) -> list[str]:
    if not owner_confirmation:
        return ["missing_owner_transport_confirmation"]

    blockers: list[str] = []
    for field in OWNER_CONFIRMATION_REQUIRED_TRUE_FIELDS:
        if not _bool(owner_confirmation.get(field)):
            blockers.append(f"{field}_required")
    blockers.extend(_authority_blockers(owner_confirmation, "owner_confirmation"))
    return blockers


def _unsafe_input_blockers(
    *,
    broker_call: Mapping[str, Any],
    order_payload: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    for term in _forbidden_key_terms(broker_call):
        blockers.append(f"broker_call_forbidden_{term}_field")
    for term in _forbidden_key_terms(order_payload):
        blockers.append(f"order_payload_forbidden_{term}_field")
    return blockers


def _result(
    *,
    status: str,
    blockers: list[str],
    warnings: list[str],
    owner_command: Mapping[str, Any],
    broker_call: Mapping[str, Any],
    context: Mapping[str, Any],
    order_payload: Mapping[str, Any],
    owner_confirmation: Mapping[str, Any],
    execute_transport: bool,
    transport_request: Mapping[str, Any] | None,
    raw_transport_result: Any,
    runtime_access_token: str | None,
    runtime_account_id: str | None,
    network_call_performed: bool,
    order_placement_performed: bool,
    order_attempt_count: int,
) -> dict[str, Any]:
    return {
        "packet_id": PACKET_ID,
        "transport_version": TRANSPORT_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "actual_owner_command_summary": _actual_owner_command_summary(owner_command),
        "broker_call_summary": _broker_call_summary(broker_call),
        "transport_context_summary": _transport_context_summary(context),
        "sanitized_order_summary": _sanitized_order_summary(order_payload),
        "owner_confirmation_summary": _owner_confirmation_summary(owner_confirmation),
        "transport_request_preview": _sanitize_transport_request(
            transport_request,
            runtime_access_token=runtime_access_token,
            runtime_account_id=runtime_account_id,
        )
        if transport_request
        else None,
        "transport_attempt": {
            "execute_transport_requested": execute_transport is True,
            "network_call_performed": network_call_performed,
            "order_placement_performed": order_placement_performed,
            "order_attempt_count": order_attempt_count,
            "demo_endpoint_only": True,
            "one_order_only": True,
            "max_order_attempts": 1,
            "second_order_allowed": False,
            "autonomous_retry_allowed": False,
            "post_trade_evidence_required": True,
            "post_trade_evidence_requirements": list(POST_TRADE_EVIDENCE_REQUIREMENTS),
        },
        "sanitized_transport_result": _sanitize_evidence_value(
            raw_transport_result,
            runtime_access_token=runtime_access_token,
            runtime_account_id=runtime_account_id,
        )
        if raw_transport_result is not None
        else None,
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }


def _transport_request(
    *,
    context: Mapping[str, Any],
    order_payload: Mapping[str, Any],
    runtime_access_token: str | None,
    runtime_account_id: str | None,
) -> dict[str, Any]:
    base_url = _trim_trailing_slash(_text(context.get("demo_api_base_url")))
    account_id = runtime_account_id if _present(runtime_account_id) else REDACTED_ACCOUNT_ID_REFERENCE
    token = runtime_access_token if _present(runtime_access_token) else REDACTED_TOKEN_REFERENCE
    return {
        "method": "POST",
        "url": f"{base_url}/v3/accounts/{account_id}/orders",
        "headers": {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        "json": _oanda_order_payload(order_payload),
        "timeout_seconds": TRANSPORT_TIMEOUT_SECONDS,
    }


def _oanda_order_payload(order_payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "order": {
            "type": order_payload.get("order_type"),
            "instrument": order_payload.get("instrument"),
            "units": _signed_units(order_payload.get("units"), order_payload.get("direction")),
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


def _actual_owner_command_summary(owner_command: Mapping[str, Any]) -> dict[str, Any]:
    package = _mapping(owner_command.get("final_manual_command_package"))
    return {
        "status": _text(owner_command.get("status"), "MISSING"),
        "ready": owner_command.get("status") == ACTUAL_OWNER_COMMAND_READY_STATUS,
        "package_ready": _bool(package.get("ready")),
        "one_order_only": _bool(package.get("one_order_only")),
        "max_order_attempts": _number(package.get("max_order_attempts"), 0),
        "execution_authority_false": not _authority_blockers(
            owner_command, "actual_owner_command_result"
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


def _transport_context_summary(context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker": _text(context.get("broker"), "MISSING"),
        "environment": _text(context.get("environment"), "MISSING"),
        "demo_endpoint_only": _bool(context.get("demo_endpoint_only")),
        "live_endpoint_absent": _bool(context.get("live_endpoint_absent")),
        "demo_api_base_url_is_practice": _text(
            context.get("demo_api_base_url")
        ).startswith(DEMO_API_BASE_URL_PREFIX),
        "live_api_base_url_present": bool(_text(context.get("live_api_base_url"))),
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


def _sanitized_order_summary(order_payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "instrument": _text(order_payload.get("instrument"), "MISSING"),
        "direction": _text(order_payload.get("direction"), "MISSING"),
        "order_type": _text(order_payload.get("order_type"), "MISSING"),
        "units": _number(order_payload.get("units"), 0),
        "signed_units_preview": _signed_units(
            order_payload.get("units"),
            order_payload.get("direction"),
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
        "forbidden_payload_keys_detected": _forbidden_key_terms(order_payload),
    }


def _owner_confirmation_summary(owner_confirmation: Mapping[str, Any]) -> dict[str, bool]:
    return {
        field: _bool(owner_confirmation.get(field))
        for field in OWNER_CONFIRMATION_REQUIRED_TRUE_FIELDS
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


def _authority_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            authority = _mapping(node.get("execution_authority"))
            for field in EXECUTION_AUTHORITY_FIELDS:
                if _bool(node.get(field)) or _bool(authority.get(field)):
                    blockers.append(f"unsafe_{label}_{field}_true")
            for child in node.values():
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
                    if key_text == "execution_authority" or term.lower() == "auth":
                        continue
                    if term.lower() in key_text and term not in found:
                        found.append(term)
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)
    return found


def _sanitize_transport_request(
    transport_request: Mapping[str, Any] | None,
    *,
    runtime_access_token: str | None,
    runtime_account_id: str | None,
) -> dict[str, Any] | None:
    if transport_request is None:
        return None
    redacted = _sanitize_evidence_value(
        transport_request,
        runtime_access_token=runtime_access_token,
        runtime_account_id=runtime_account_id,
    )
    if not isinstance(redacted, dict):
        return None
    headers = _mapping(redacted.get("headers"))
    if "Authorization" in headers:
        redacted["headers"] = {
            **dict(headers),
            "Authorization": f"Bearer {REDACTED_TOKEN_REFERENCE}",
        }
    return redacted


def _sanitize_evidence_value(
    value: Any,
    *,
    runtime_access_token: str | None,
    runtime_account_id: str | None,
) -> Any:
    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        for key, child in value.items():
            key_text = str(key)
            if _sensitive_key(key_text):
                sanitized[key_text] = "REDACTED_RUNTIME_ONLY_REFERENCE"
            else:
                sanitized[key_text] = _sanitize_evidence_value(
                    child,
                    runtime_access_token=runtime_access_token,
                    runtime_account_id=runtime_account_id,
                )
        return sanitized
    if isinstance(value, list):
        return [
            _sanitize_evidence_value(
                child,
                runtime_access_token=runtime_access_token,
                runtime_account_id=runtime_account_id,
            )
            for child in value
        ]
    return _safe_scalar(
        value,
        runtime_access_token=runtime_access_token,
        runtime_account_id=runtime_account_id,
    )


def _safe_scalar(
    value: Any,
    *,
    runtime_access_token: str | None,
    runtime_account_id: str | None,
) -> Any:
    if isinstance(value, str):
        text = value
        if runtime_access_token:
            text = text.replace(runtime_access_token, REDACTED_TOKEN_REFERENCE)
        if runtime_account_id:
            text = text.replace(runtime_account_id, REDACTED_ACCOUNT_ID_REFERENCE)
        return text
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return repr(value)


def _sensitive_key(key: str) -> bool:
    key_text = key.lower()
    return any(term.lower() in key_text for term in SENSITIVE_KEY_TERMS)


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
        or "orderCreateTransaction" in result
        or "orderFillTransaction" in result
    )


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _warnings(status: str) -> list[str]:
    warnings = [
        "owner_run_only",
        "runtime_credentials_external_only",
        "execution_authority_false",
        "demo_endpoint_only",
        "one_order_cap_in_force",
        "no_live_trading",
        "no_autonomous_execution",
        "no_scheduler_daemon_or_webhook",
        "no_credentials_or_account_ids_persisted",
        "post_trade_evidence_required",
    ]
    if status == TRANSPORT_DRY_RUN_READY:
        warnings.append("dry_run_preview_only_no_network_call")
    if status == TRANSPORT_ATTEMPTED_OANDA_DEMO_ORDER_ONCE:
        warnings.append("runtime_http_transport_called_once")
    return warnings


def _next_safe_action(status: str) -> str:
    return {
        TRANSPORT_BLOCKED_MISSING_OWNER_COMMAND: (
            "provide_actual_owner_command_ready_result"
        ),
        TRANSPORT_BLOCKED_OWNER_COMMAND_NOT_READY: (
            "repair_actual_owner_command_before_runtime_transport"
        ),
        TRANSPORT_BLOCKED_BROKER_CALL_NOT_READY: (
            "repair_broker_call_readiness_before_runtime_transport"
        ),
        TRANSPORT_BLOCKED_CONTEXT: "repair_oanda_demo_transport_context",
        TRANSPORT_BLOCKED_ORDER_PAYLOAD: "provide_sanitized_oanda_order_payload",
        TRANSPORT_BLOCKED_OWNER_CONFIRMATION: (
            "complete_owner_transport_confirmations"
        ),
        TRANSPORT_DRY_RUN_READY: "owner_may_review_sanitized_runtime_http_preview",
        TRANSPORT_BLOCKED_RUNTIME_CREDENTIALS_MISSING: (
            "owner_must_supply_runtime_env_credentials_outside_repo"
        ),
        TRANSPORT_BLOCKED_HTTP_POST_CALLABLE_REQUIRED: (
            "owner_runtime_script_must_supply_http_post_callable"
        ),
        TRANSPORT_ATTEMPTED_OANDA_DEMO_ORDER_ONCE: (
            "capture_sanitized_post_trade_evidence_and_do_not_rerun"
        ),
        TRANSPORT_REJECTED: "remove_sensitive_or_unsafe_input_before_transport",
    }.get(status, "stop_and_review_transport_state")


def _parse_json_body(body: str) -> Any:
    if not body:
        return None
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body


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


def _present(value: Any) -> bool:
    return bool(value.strip()) if isinstance(value, str) else value is not None


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
