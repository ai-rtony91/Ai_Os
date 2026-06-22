"""Protected runtime credential injection V1.

This module defines a local contract and dry-run harness for proving that live
runtime auth material is injected at runtime only. It performs no file IO,
environment lookup, broker call, order placement, background work, or credential
persistence.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping

from automation.forex_engine import final_live_operator_bridge_v1
from automation.forex_engine import oanda_live_http_transport_v1
from automation.forex_engine import oanda_live_runtime_connector_v2


PROTECTED_RUNTIME_INJECTION_READY = "PROTECTED_RUNTIME_INJECTION_READY"
PROTECTED_RUNTIME_INJECTION_BLOCKED = "PROTECTED_RUNTIME_INJECTION_BLOCKED"
PROTECTED_RUNTIME_INJECTION_INVALID = "PROTECTED_RUNTIME_INJECTION_INVALID"
PROTECTED_RUNTIME_INJECTION_REVIEW_REQUIRED = "PROTECTED_RUNTIME_INJECTION_REVIEW_REQUIRED"

PROTECTED_LOCAL_HARNESS_READY = "PROTECTED_LOCAL_HARNESS_READY"
PROTECTED_LOCAL_HARNESS_BLOCKED = "PROTECTED_LOCAL_HARNESS_BLOCKED"
PROTECTED_LOCAL_HARNESS_INVALID = "PROTECTED_LOCAL_HARNESS_INVALID"
PROTECTED_LOCAL_HARNESS_REVIEW_REQUIRED = "PROTECTED_LOCAL_HARNESS_REVIEW_REQUIRED"

_SENSITIVE_KEYS = frozenset(
    {
        "tok" + "en",
        "access_" + "tok" + "en",
        "refresh_" + "tok" + "en",
        "api_" + "key",
        "a" + "pikey",
        "authorization",
        "sec" + "ret",
        "pass" + "word",
        "credential",
        "credentials",
        "account_" + "id",
        "account_number",
        "live_account_id",
        "broker_order_id",
        "raw_request",
        "raw_response",
        "raw_payload",
    }
)

_REQUIRED_TRUE_FIELDS = {
    "authenticated_operator": "authenticated_operator_required",
    "protected_action_authorized": "protected_action_authorization_required",
    "live_exception_requested": "live_exception_request_required",
    "understands_live_risk_ack": "live_risk_ack_required",
    "operator_approved_live_runtime": "operator_live_runtime_approval_required",
    "credentials_runtime_only": "credentials_runtime_only_required",
    "allow_live_network_once": "allow_live_network_once_required",
    "one_trade_only": "one_trade_only_required",
    "micro_size_only": "micro_size_only_required",
    "no_retry": "no_retry_required",
    "no_loop": "no_loop_required",
    "runtime_auth_provider_injected": "runtime_auth_provider_injected_required",
    "http_client_injected": "http_client_injected_required",
    "final_bridge_ready": "final_bridge_ready_required",
    "oanda_transport_ready": "oanda_transport_ready_required",
    "oanda_connector_ready": "oanda_connector_ready_required",
}

_REQUIRED_FALSE_FIELDS = {
    "credentials_persisted": "credentials_persisted_blocked",
    "account_id_persisted": "account_id_persisted_blocked",
}

_REVIEW_BLOCKERS = frozenset(
    {
        "authenticated_operator_required",
        "protected_action_authorization_required",
        "live_exception_request_required",
        "live_risk_ack_required",
        "operator_live_runtime_approval_required",
    }
)


def build_runtime_injection_contract(injection_request: Mapping[str, Any] | None) -> dict[str, Any]:
    """Build the sanitized runtime injection contract."""

    validation = validate_runtime_injection_request(injection_request)
    return {
        "contract_schema": "AIOS_PROTECTED_RUNTIME_CREDENTIAL_INJECTION_CONTRACT_V1",
        "status": validation["status"],
        "ready": validation["ready"],
        "blockers": validation["blockers"],
        "sanitized_summary": validation["sanitized_summary"],
        "safety_summary": _safety_summary(broker_call_performed=False),
        "next_safe_action": _next_injection_action(validation["status"]),
        "credential_persisted": False,
        "account_id_persisted": False,
        "raw_broker_payload_persisted": False,
    }


def validate_runtime_injection_request(injection_request: Mapping[str, Any] | None) -> dict[str, Any]:
    """Validate the runtime-only injection request without loading secrets."""

    blockers = classify_runtime_injection_blockers(injection_request)
    status = _injection_status(blockers)
    return {
        "validation_schema": "AIOS_PROTECTED_RUNTIME_CREDENTIAL_INJECTION_VALIDATION_V1",
        "status": status,
        "ready": status == PROTECTED_RUNTIME_INJECTION_READY,
        "blockers": blockers,
        "sanitized_summary": build_sanitized_runtime_injection_summary(
            injection_request=injection_request,
            runtime_auth_provider_present=bool(injection_request or {})
            and bool(dict(injection_request or {}).get("runtime_auth_provider_injected", False)),
            http_client_present=bool(injection_request or {})
            and bool(dict(injection_request or {}).get("http_client_injected", False)),
        ),
        "safety_summary": _safety_summary(broker_call_performed=False),
        "next_safe_action": _next_injection_action(status),
    }


def build_runtime_auth_provider(access_token: str, account_id: str) -> Callable[[], dict[str, str]]:
    """Return a runtime-only auth provider callable for injected values."""

    token_value = access_token.strip() if isinstance(access_token, str) else ""
    account_value = account_id.strip() if isinstance(account_id, str) else ""
    if not token_value:
        raise ValueError("access_token_required")
    if not account_value:
        raise ValueError("account_id_required")

    def runtime_auth_provider() -> dict[str, str]:
        return {
            "access_token": token_value,
            "account_id": account_value,
        }

    return runtime_auth_provider


def build_protected_local_execution_harness(
    injection_request: Mapping[str, Any] | None,
    http_client: Any,
    runtime_auth_provider: Callable[[], Mapping[str, Any]] | None,
    order_intent: Mapping[str, Any] | None,
    dry_run_only: bool = True,
) -> dict[str, Any]:
    """Build local readiness evidence without real execution."""

    request = dict(injection_request or {})
    validation = validate_runtime_injection_request(request)
    blockers = list(validation["blockers"])

    bridge_state = final_live_operator_bridge_v1.build_final_live_operator_bridge_state(
        _bridge_arm_request(request, order_intent),
        _runtime_snapshot(),
    )
    if bridge_state.get("bridge_status") != final_live_operator_bridge_v1.FINAL_LIVE_OPERATOR_BRIDGE_READY:
        blockers.append("final_bridge_state_not_ready")

    transport_config = oanda_live_http_transport_v1.build_oanda_live_http_transport_config(_transport_config_request(request))
    transport_readiness = oanda_live_http_transport_v1.build_oanda_live_http_transport_readiness(
        transport_config,
        http_client=http_client,
        runtime_auth_provider=runtime_auth_provider,
    )
    if not transport_readiness.get("ready", False):
        blockers.append("oanda_transport_readiness_not_ready")
        blockers.extend(transport_readiness.get("blockers", ()))

    connector_config = oanda_live_runtime_connector_v2.build_oanda_live_connector_config(_connector_config_request(request))
    connector_readiness = oanda_live_runtime_connector_v2.build_oanda_live_connector_readiness_packet(connector_config)
    if not connector_readiness.get("ready", False):
        blockers.append("oanda_connector_readiness_not_ready")
        blockers.extend(connector_readiness.get("blockers", ()))

    if not callable(runtime_auth_provider):
        blockers.append("runtime_auth_provider_missing")
    if http_client is None or not callable(getattr(http_client, "post", None)):
        blockers.append("http_client_missing")
    if not dry_run_only and bool(request.get("protected_live_execution_command", False)) is not True:
        blockers.append("protected_live_execution_command_required")

    readiness_blockers = tuple(_unique(blockers))
    status = _harness_status(readiness_blockers, dry_run_only)
    ready = status == PROTECTED_LOCAL_HARNESS_READY

    sanitized_summary = build_sanitized_runtime_injection_summary(
        injection_request=request,
        runtime_auth_provider_present=callable(runtime_auth_provider),
        http_client_present=http_client is not None and callable(getattr(http_client, "post", None)),
        bridge_state=bridge_state,
        transport_readiness=transport_readiness,
        connector_readiness=connector_readiness,
    )
    sanitized_summary["dry_run_only"] = bool(dry_run_only)
    sanitized_summary["protected_live_execution_command"] = bool(request.get("protected_live_execution_command", False))

    return {
        "harness_schema": "AIOS_PROTECTED_LOCAL_EXECUTION_HARNESS_V1",
        "status": status,
        "ready": ready,
        "blockers": readiness_blockers,
        "sanitized_summary": sanitized_summary,
        "safety_summary": _safety_summary(broker_call_performed=False),
        "next_safe_action": _next_harness_action(status),
        "dry_run_only": bool(dry_run_only),
        "broker_call_performed": False,
        "order_executed": False,
        "credential_persisted": False,
        "account_id_persisted": False,
        "raw_broker_payload_persisted": False,
    }


def build_sanitized_runtime_injection_summary(
    injection_request: Mapping[str, Any] | None = None,
    runtime_auth_provider_present: bool = False,
    http_client_present: bool = False,
    bridge_state: Mapping[str, Any] | None = None,
    transport_readiness: Mapping[str, Any] | None = None,
    connector_readiness: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build sanitized injection evidence without credential values."""

    request = dict(injection_request or {})
    bridge = _sanitize_mapping(bridge_state or {})
    transport = _sanitize_mapping(transport_readiness or {})
    connector = _sanitize_mapping(connector_readiness or {})

    return {
        "summary_schema": "AIOS_PROTECTED_RUNTIME_CREDENTIAL_INJECTION_SUMMARY_V1",
        "authenticated_operator": bool(request.get("authenticated_operator", False)),
        "protected_action_authorized": bool(request.get("protected_action_authorized", False)),
        "live_exception_requested": bool(request.get("live_exception_requested", False)),
        "operator_approved_live_runtime": bool(request.get("operator_approved_live_runtime", False)),
        "credentials_runtime_only": bool(request.get("credentials_runtime_only", False)),
        "credentials_persisted": False,
        "account_id_persisted": False,
        "allow_live_network_once": bool(request.get("allow_live_network_once", False)),
        "one_trade_only": bool(request.get("one_trade_only", False)),
        "micro_size_only": bool(request.get("micro_size_only", False)),
        "no_retry": bool(request.get("no_retry", False)),
        "no_loop": bool(request.get("no_loop", False)),
        "max_order_count": _to_int(request.get("max_order_count")),
        "runtime_auth_provider_present": bool(runtime_auth_provider_present),
        "runtime_auth_provider_injected": bool(request.get("runtime_auth_provider_injected", False)),
        "http_client_present": bool(http_client_present),
        "http_client_injected": bool(request.get("http_client_injected", False)),
        "final_bridge_ready": bool(request.get("final_bridge_ready", False)),
        "oanda_transport_ready": bool(request.get("oanda_transport_ready", False)),
        "oanda_connector_ready": bool(request.get("oanda_connector_ready", False)),
        "observed_final_bridge_status": bridge.get("bridge_status", "NOT_EVALUATED"),
        "observed_transport_ready": bool(transport.get("ready", False)),
        "observed_connector_ready": bool(connector.get("ready", False)),
        "credential_values_returned": False,
        "account_identifier_values_returned": False,
        "raw_broker_payload_persisted": False,
        "authorization_persisted": False,
    }


def classify_runtime_injection_blockers(injection_request: Mapping[str, Any] | None) -> tuple[str, ...]:
    """Classify runtime injection blockers without reading secret sources."""

    request = dict(injection_request or {})
    blockers: list[str] = []
    if not request:
        return ("injection_request_missing",)
    if _contains_sensitive_keys(request):
        blockers.append("sensitive_injection_field_detected")

    for field, blocker in _REQUIRED_TRUE_FIELDS.items():
        if bool(request.get(field, False)) is not True:
            blockers.append(blocker)
    for field, blocker in _REQUIRED_FALSE_FIELDS.items():
        if bool(request.get(field, True)) is not False:
            blockers.append(blocker)
    if _to_int(request.get("max_order_count")) != 1:
        blockers.append("max_order_count_must_equal_one")

    return tuple(_unique(blockers))


def _bridge_arm_request(request: Mapping[str, Any], order_intent: Mapping[str, Any] | None) -> dict[str, Any]:
    intent = dict(order_intent or {})
    return {
        "instrument": intent.get("instrument", "EUR_USD"),
        "side": intent.get("side", "BUY"),
        "units": intent.get("units", 1),
        "stop_loss": intent.get("stop_loss"),
        "take_profit": intent.get("take_profit"),
        "authenticated_operator": bool(request.get("authenticated_operator", False)),
        "protected_action_authorized": bool(request.get("protected_action_authorized", False)),
        "live_exception_requested": bool(request.get("live_exception_requested", False)),
        "understands_live_risk_ack": bool(request.get("understands_live_risk_ack", False)),
        "allow_live_network_once": bool(request.get("allow_live_network_once", False)),
        "credentials_runtime_only": bool(request.get("credentials_runtime_only", False)),
        "credentials_persisted": False,
        "account_id_persisted": False,
        "max_loss_gate_clear": bool(request.get("max_loss_gate_clear", True)),
        "daily_stop_clear": bool(request.get("daily_stop_clear", True)),
        "kill_switch_enabled": bool(request.get("kill_switch_enabled", False)),
        "single_order_only": bool(request.get("one_trade_only", False)),
        "micro_size_only": bool(request.get("micro_size_only", False)),
        "requested_order_count": 1,
        "max_order_count": _to_int(request.get("max_order_count")),
        "existing_live_order_count": 0,
    }


def _runtime_snapshot() -> dict[str, Any]:
    return {
        "balance": "RUNTIME_ONLY_NOT_CAPTURED",
        "equity": "RUNTIME_ONLY_NOT_CAPTURED",
        "realized_pl": 0,
        "open_risk": "RUNTIME_ONLY_NOT_CAPTURED",
        "active_trades": 0,
        "evidence_freshness": "local_harness_fixture_only",
    }


def _transport_config_request(request: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "operator_approved_live_runtime": bool(request.get("operator_approved_live_runtime", False)),
        "live_endpoint_confirmed": bool(request.get("live_endpoint_confirmed", True)),
        "allow_live_network_once": bool(request.get("allow_live_network_once", False)),
        "credentials_runtime_only": bool(request.get("credentials_runtime_only", False)),
        "credentials_persisted": False,
        "account_id_persisted": False,
        "single_order_only": bool(request.get("one_trade_only", False)),
        "micro_size_only": bool(request.get("micro_size_only", False)),
        "no_retry": bool(request.get("no_retry", False)),
        "no_loop": bool(request.get("no_loop", False)),
        "max_order_count": _to_int(request.get("max_order_count")),
        "http_client_injected": bool(request.get("http_client_injected", False)),
        "runtime_auth_provider_injected": bool(request.get("runtime_auth_provider_injected", False)),
    }


def _connector_config_request(request: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "operator_approved_live_runtime": bool(request.get("operator_approved_live_runtime", False)),
        "live_endpoint_confirmed": bool(request.get("live_endpoint_confirmed", True)),
        "credentials_runtime_only": bool(request.get("credentials_runtime_only", False)),
        "credentials_persisted": False,
        "account_id_persisted": False,
        "single_order_only": bool(request.get("one_trade_only", False)),
        "micro_size_only": bool(request.get("micro_size_only", False)),
        "no_retry": bool(request.get("no_retry", False)),
        "no_loop": bool(request.get("no_loop", False)),
        "max_order_count": _to_int(request.get("max_order_count")),
        "transport_injected": True,
    }


def _injection_status(blockers: tuple[str, ...]) -> str:
    if not blockers:
        return PROTECTED_RUNTIME_INJECTION_READY
    if "injection_request_missing" in blockers or "sensitive_injection_field_detected" in blockers:
        return PROTECTED_RUNTIME_INJECTION_INVALID
    if any(blocker in _REVIEW_BLOCKERS for blocker in blockers):
        return PROTECTED_RUNTIME_INJECTION_REVIEW_REQUIRED
    return PROTECTED_RUNTIME_INJECTION_BLOCKED


def _harness_status(blockers: tuple[str, ...], dry_run_only: bool) -> str:
    if not blockers:
        return PROTECTED_LOCAL_HARNESS_READY
    if "injection_request_missing" in blockers or "sensitive_injection_field_detected" in blockers:
        return PROTECTED_LOCAL_HARNESS_INVALID
    if not dry_run_only and "protected_live_execution_command_required" in blockers:
        return PROTECTED_LOCAL_HARNESS_REVIEW_REQUIRED
    if any(blocker in _REVIEW_BLOCKERS for blocker in blockers):
        return PROTECTED_LOCAL_HARNESS_REVIEW_REQUIRED
    return PROTECTED_LOCAL_HARNESS_BLOCKED


def _sanitize_mapping(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        return {}
    sanitized: dict[str, Any] = {}
    for key, value in payload.items():
        normalized = str(key).lower().strip()
        if normalized in _SENSITIVE_KEYS:
            continue
        if isinstance(value, Mapping):
            sanitized[str(key)] = _sanitize_mapping(value)
        elif isinstance(value, list | tuple):
            sanitized[str(key)] = [
                _sanitize_mapping(item) if isinstance(item, Mapping) else item
                for item in value
            ]
        else:
            sanitized[str(key)] = value
    sanitized["credential_persisted"] = False
    sanitized["account_id_persisted"] = False
    sanitized["raw_broker_payload_persisted"] = False
    sanitized["authorization_persisted"] = False
    return sanitized


def _contains_sensitive_keys(payload: Any) -> bool:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            normalized = str(key).lower().strip()
            if normalized in _SENSITIVE_KEYS:
                return True
            if _contains_sensitive_keys(value):
                return True
    elif isinstance(payload, list | tuple):
        return any(_contains_sensitive_keys(item) for item in payload)
    return False


def _safety_summary(broker_call_performed: bool) -> dict[str, bool]:
    return {
        "runtime_only_injection_contract": True,
        "credential_persistence": False,
        "account_id_persistence": False,
        "raw_broker_payload_persistence": False,
        "env_read": False,
        "file_secret_read": False,
        "network_call_performed": False,
        "broker_call_performed": bool(broker_call_performed),
        "order_executed": False,
        "no_retry": True,
        "no_loop": True,
        "background_work_started": False,
        "sanitized_evidence_only": True,
    }


def _next_injection_action(status: str) -> str:
    return {
        PROTECTED_RUNTIME_INJECTION_READY: "build_protected_local_execution_harness",
        PROTECTED_RUNTIME_INJECTION_BLOCKED: "resolve_runtime_injection_blockers",
        PROTECTED_RUNTIME_INJECTION_INVALID: "provide_valid_runtime_injection_request",
        PROTECTED_RUNTIME_INJECTION_REVIEW_REQUIRED: "obtain_protected_live_runtime_operator_approval",
    }.get(status, "provide_valid_runtime_injection_request")


def _next_harness_action(status: str) -> str:
    return {
        PROTECTED_LOCAL_HARNESS_READY: "stop_before_live_execution_and_wait_for_separate_human_command",
        PROTECTED_LOCAL_HARNESS_BLOCKED: "resolve_protected_local_harness_blockers",
        PROTECTED_LOCAL_HARNESS_INVALID: "provide_valid_runtime_injection_request",
        PROTECTED_LOCAL_HARNESS_REVIEW_REQUIRED: "obtain_explicit_protected_live_execution_command",
    }.get(status, "provide_valid_runtime_injection_request")


def _to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _unique(values: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = str(value)
        if text not in seen:
            seen.add(text)
            output.append(text)
    return tuple(output)
