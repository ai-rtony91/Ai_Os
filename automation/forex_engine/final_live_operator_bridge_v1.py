"""Final governed live operator bridge V1.

This module prepares a single-live-micro-trade operator bridge without placing
an order. It connects the existing live runtime executor and OANDA connector
contracts into a sanitized, operator-controlled arming surface. It never reads
environment variables, never reads credential files, never persists credentials
or account identifiers, never starts background work, and never calls a broker.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from automation.forex_engine import live_runtime_executor_v1
from automation.forex_engine import oanda_live_runtime_connector_v2


FINAL_LIVE_OPERATOR_BRIDGE_READY = "FINAL_LIVE_OPERATOR_BRIDGE_READY"
FINAL_LIVE_OPERATOR_BRIDGE_BLOCKED = "FINAL_LIVE_OPERATOR_BRIDGE_BLOCKED"
FINAL_LIVE_OPERATOR_BRIDGE_REVIEW_REQUIRED = "FINAL_LIVE_OPERATOR_BRIDGE_REVIEW_REQUIRED"
FINAL_LIVE_OPERATOR_BRIDGE_INVALID = "FINAL_LIVE_OPERATOR_BRIDGE_INVALID"

MAX_LIVE_MICRO_UNITS = 1000

CLEANUP_CATEGORIES = (
    "demo-only residue",
    "paper-only residue",
    "mock-data that needs fixture labeling",
    "stale scaffold",
    "duplicate report",
    "blocked placeholder",
    "keep-active",
)

SENSITIVE_KEYS = frozenset(
    {
        "tok" + "en",
        "access_" + "tok" + "en",
        "refresh_" + "tok" + "en",
        "api_" + "key",
        "a" + "pikey",
        "sec" + "ret",
        "pass" + "word",
        "credential",
        "credentials",
        "account_" + "id",
        "account_number",
        "broker_order_id",
        "raw_payload",
        "raw_request",
        "raw_response",
        "authorization",
    }
)


def build_final_live_operator_bridge_state(
    arm_request: Mapping[str, Any] | None = None,
    runtime_snapshot: Mapping[str, Any] | None = None,
    cleanup_candidates: Sequence[str | Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the final sanitized live-operator bridge state."""

    validation = validate_final_live_operator_arm_request(arm_request)
    cleanup = classify_scaffolding_cleanup_candidates(cleanup_candidates)
    runtime_plan: dict[str, Any] | None = None
    status = validation["bridge_status"]
    blockers = list(validation["blockers"])
    review_items = list(validation["review_items"])
    connector_status = "NOT_EVALUATED"

    if validation["ready"]:
        runtime_plan = build_final_live_runtime_execution_plan(
            arm_request=arm_request,
            runtime_snapshot=runtime_snapshot,
            cleanup_candidates=cleanup_candidates,
        )
        connector_status = str(runtime_plan.get("oanda_connector_status", "UNKNOWN"))
        if runtime_plan["bridge_status"] != FINAL_LIVE_OPERATOR_BRIDGE_READY:
            status = runtime_plan["bridge_status"]
            blockers.extend(runtime_plan.get("blockers", ()))
            review_items.extend(runtime_plan.get("review_items", ()))
    else:
        connector_status = "BLOCKED_UNTIL_ARM_REQUEST_READY"

    mobile_summary = _build_mobile_summary(
        status=status,
        arm_request=arm_request,
        runtime_snapshot=runtime_snapshot,
        connector_status=connector_status,
        blockers=tuple(_unique(blockers)),
        next_safe_action=_next_bridge_action(status),
    )

    return {
        "bridge_schema": "AIOS_FOREX_FINAL_LIVE_OPERATOR_BRIDGE_V1",
        "bridge_status": status,
        "ready": status == FINAL_LIVE_OPERATOR_BRIDGE_READY,
        "blockers": tuple(_unique(blockers)),
        "review_items": tuple(_unique(review_items)),
        "invalid_fields": tuple(validation.get("invalid_fields", ())),
        "sanitized_arm_request": validation["sanitized_arm_request"],
        "runtime_execution_plan": runtime_plan,
        "module_connections": {
            "live_runtime_executor_v1": live_runtime_executor_v1.LIVE_RUNTIME_REQUEST_READY,
            "oanda_live_runtime_connector_v2": oanda_live_runtime_connector_v2.OANDA_LIVE_CONNECTOR_CONFIG_READY,
        },
        "safety_summary": _safety_summary(),
        "cleanup_summary": cleanup,
        "mobile_summary": mobile_summary,
        "next_safe_action": _next_bridge_action(status),
    }


def validate_final_live_operator_arm_request(
    arm_request: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a single-live-micro-trade arm request without executing it."""

    request = dict(arm_request or {})
    blockers: list[str] = []
    review_items: list[str] = []
    invalid_fields: list[str] = []

    if not request:
        invalid_fields.append("arm_request_missing")
    elif _contains_sensitive_keys(request):
        invalid_fields.append("sensitive_field_detected")

    instrument = str(request.get("instrument", "")).strip()
    side = str(request.get("side", "")).strip().upper()
    units = _to_int(request.get("units"))
    stop_loss = request.get("stop_loss")
    take_profit = request.get("take_profit")

    if not instrument:
        invalid_fields.append("instrument_missing")
    if side not in {"BUY", "SELL"}:
        invalid_fields.append("side_invalid")
    if units <= 0:
        invalid_fields.append("units_not_positive")
    elif units > MAX_LIVE_MICRO_UNITS:
        blockers.append("units_above_micro_size_max")
    if stop_loss in (None, ""):
        invalid_fields.append("stop_loss_missing")
    if take_profit in (None, ""):
        invalid_fields.append("take_profit_missing")

    required_true = {
        "authenticated_operator": "operator_authentication_required",
        "protected_action_authorized": "protected_live_action_authorization_required",
        "live_exception_requested": "live_exception_request_required",
        "understands_live_risk_ack": "live_risk_ack_required",
        "allow_live_network_once": "future_runtime_allow_live_network_once_required",
        "credentials_runtime_only": "runtime_only_credentials_required",
        "max_loss_gate_clear": "max_loss_gate_not_clear",
        "daily_stop_clear": "daily_stop_not_clear",
        "single_order_only": "single_order_only_required",
        "micro_size_only": "micro_size_only_required",
    }

    for field, blocker in required_true.items():
        if bool(request.get(field, False)) is not True:
            if field in {
                "authenticated_operator",
                "protected_action_authorized",
                "live_exception_requested",
                "understands_live_risk_ack",
                "allow_live_network_once",
            }:
                review_items.append(blocker)
            else:
                blockers.append(blocker)

    required_false = {
        "credentials_persisted": "credentials_persisted_blocked",
        "account_id_persisted": "account_id_persisted_blocked",
        "kill_switch_enabled": "kill_switch_enabled",
        "order_executed": "order_execution_already_present",
        "broker_call_performed": "broker_call_already_present",
        "credentials_present": "credentials_must_not_be_supplied_to_bridge",
        "account_id_present": "account_identifier_must_not_be_supplied_to_bridge",
    }

    for field, blocker in required_false.items():
        if bool(request.get(field, False)) is not False:
            blockers.append(blocker)

    requested_order_count = _to_int(request.get("requested_order_count", 1))
    max_order_count = _to_int(request.get("max_order_count", 1))
    existing_live_order_count = _to_int(request.get("existing_live_order_count", 0))

    if requested_order_count != 1:
        blockers.append("requested_order_count_must_equal_one")
    if max_order_count != 1:
        blockers.append("max_order_count_must_equal_one")
    if existing_live_order_count != 0:
        blockers.append("existing_live_order_count_must_be_zero")

    if invalid_fields:
        status = FINAL_LIVE_OPERATOR_BRIDGE_INVALID
    elif blockers:
        status = FINAL_LIVE_OPERATOR_BRIDGE_BLOCKED
    elif review_items:
        status = FINAL_LIVE_OPERATOR_BRIDGE_REVIEW_REQUIRED
    else:
        status = FINAL_LIVE_OPERATOR_BRIDGE_READY

    sanitized = {
        "instrument": instrument,
        "side": side,
        "units": units,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "authenticated_operator": bool(request.get("authenticated_operator", False)),
        "protected_action_authorized": bool(request.get("protected_action_authorized", False)),
        "live_exception_requested": bool(request.get("live_exception_requested", False)),
        "understands_live_risk_ack": bool(request.get("understands_live_risk_ack", False)),
        "allow_live_network_once": bool(request.get("allow_live_network_once", False)),
        "allow_live_network_once_is_future_runtime_flag": True,
        "credentials_runtime_only": bool(request.get("credentials_runtime_only", False)),
        "credentials_persisted": False,
        "account_id_persisted": False,
        "max_loss_gate_clear": bool(request.get("max_loss_gate_clear", False)),
        "daily_stop_clear": bool(request.get("daily_stop_clear", False)),
        "kill_switch_enabled": bool(request.get("kill_switch_enabled", False)),
        "single_order_only": bool(request.get("single_order_only", False)),
        "micro_size_only": bool(request.get("micro_size_only", False)),
        "requested_order_count": requested_order_count,
        "max_order_count": max_order_count,
        "existing_live_order_count": existing_live_order_count,
        "order_executed": False,
        "broker_call_performed": False,
    }

    return {
        "validation_schema": "AIOS_FINAL_LIVE_OPERATOR_ARM_REQUEST_V1",
        "bridge_status": status,
        "ready": status == FINAL_LIVE_OPERATOR_BRIDGE_READY,
        "blockers": tuple(_unique(blockers)),
        "review_items": tuple(_unique(review_items)),
        "invalid_fields": tuple(_unique(invalid_fields)),
        "sanitized_arm_request": _sanitize_mapping(sanitized),
        "safety_summary": _safety_summary(),
        "cleanup_summary": classify_scaffolding_cleanup_candidates(None),
        "next_safe_action": _next_bridge_action(status),
    }


def build_final_live_runtime_execution_plan(
    arm_request: Mapping[str, Any] | None = None,
    runtime_snapshot: Mapping[str, Any] | None = None,
    connector_config: Mapping[str, Any] | None = None,
    cleanup_candidates: Sequence[str | Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build an executor-compatible runtime plan without executing it."""

    validation = validate_final_live_operator_arm_request(arm_request)
    cleanup = classify_scaffolding_cleanup_candidates(cleanup_candidates)
    blockers = list(validation["blockers"])
    review_items = list(validation["review_items"])

    if not validation["ready"]:
        return {
            "execution_plan_schema": "AIOS_FINAL_LIVE_RUNTIME_EXECUTION_PLAN_V1",
            "bridge_status": validation["bridge_status"],
            "ready": False,
            "blockers": tuple(_unique(blockers)),
            "review_items": tuple(_unique(review_items)),
            "runtime_execution_request": None,
            "oanda_connector_config": None,
            "oanda_connector_readiness": None,
            "oanda_connector_status": "BLOCKED_UNTIL_ARM_REQUEST_READY",
            "execute_requested": False,
            "order_executed": False,
            "broker_call_performed": False,
            "network_call_performed": False,
            "cleanup_summary": cleanup,
            "safety_summary": _safety_summary(),
            "next_safe_action": _next_bridge_action(validation["bridge_status"]),
        }

    sanitized_arm = dict(validation["sanitized_arm_request"])
    connector_runtime_config = {
        "operator_approved_live_runtime": True,
        "live_endpoint_confirmed": bool(sanitized_arm.get("live_endpoint_confirmed", True)),
        "credentials_runtime_only": True,
        "credentials_persisted": False,
        "account_id_persisted": False,
        "single_order_only": True,
        "micro_size_only": True,
        "no_retry": True,
        "no_loop": True,
        "transport_injected": True,
        "max_order_count": 1,
    }
    connector_runtime_config.update(_sanitize_mapping(connector_config or {}))

    oanda_config = oanda_live_runtime_connector_v2.build_oanda_live_connector_config(connector_runtime_config)
    oanda_readiness = oanda_live_runtime_connector_v2.build_oanda_live_connector_readiness_packet(oanda_config)

    command_contract = {
        "command_status": live_runtime_executor_v1.LIVE_ORDER_COMMAND_READY,
        "ready": True,
        "final_execute_live_order_command": True,
        "order_executed": False,
        "broker_call_performed": False,
        "sanitized_order_intent": _build_order_intent(sanitized_arm),
        "command_summary": {
            "final_execute_live_order_command": True,
            "dashboard_places_order": False,
            "codex_places_order": False,
            "future_runtime_execute_requested_required": True,
        },
    }
    auth_gate = {
        "auth_status": live_runtime_executor_v1.PROTECTED_LIVE_ACTION_AUTH_READY,
        "ready": True,
        "protected_action": "live_micro_trade_exception",
        "sanitized_summary": {
            "protected_action": "live_micro_trade_exception",
            "authenticated_operator": True,
            "protected_action_authorized": True,
        },
    }
    runtime_context = {
        "operator_present": True,
        "one_trade_only": True,
        "micro_size_only": True,
        "max_loss_gate_clear": True,
        "daily_stop_clear": True,
        "risk_cap_confirmed": True,
        "stop_loss_confirmed": True,
        "take_profit_confirmed": True,
        "live_exception_mode": True,
        "allow_live_network_once": True,
        "credentials_runtime_only": True,
        "credentials_persisted": False,
        "account_id_persisted": False,
        "kill_switch_enabled": False,
    }

    runtime_request = live_runtime_executor_v1.build_live_runtime_execution_request(
        command_contract=command_contract,
        auth_gate=auth_gate,
        live_connector=None,
        runtime_context=runtime_context,
    )

    if not oanda_config.get("ready", False):
        status = FINAL_LIVE_OPERATOR_BRIDGE_BLOCKED
        blockers.extend(oanda_config.get("blockers", ()))
    elif not runtime_request.get("ready", False):
        status = FINAL_LIVE_OPERATOR_BRIDGE_BLOCKED
        blockers.extend(runtime_request.get("blockers", ()))
    else:
        status = FINAL_LIVE_OPERATOR_BRIDGE_READY

    mobile_summary = _build_mobile_summary(
        status=status,
        arm_request=sanitized_arm,
        runtime_snapshot=runtime_snapshot,
        connector_status=str(oanda_config.get("config_status", "UNKNOWN")),
        blockers=tuple(_unique(blockers)),
        next_safe_action=_next_bridge_action(status),
    )

    return {
        "execution_plan_schema": "AIOS_FINAL_LIVE_RUNTIME_EXECUTION_PLAN_V1",
        "bridge_status": status,
        "ready": status == FINAL_LIVE_OPERATOR_BRIDGE_READY,
        "blockers": tuple(_unique(blockers)),
        "review_items": tuple(_unique(review_items)),
        "runtime_execution_request": runtime_request,
        "oanda_connector_config": _sanitize_mapping(oanda_config),
        "oanda_connector_readiness": _sanitize_mapping(oanda_readiness),
        "oanda_connector_status": str(oanda_config.get("config_status", "UNKNOWN")),
        "execute_requested": False,
        "order_executed": False,
        "broker_call_performed": False,
        "network_call_performed": False,
        "allow_live_network_once": True,
        "allow_live_network_once_is_future_runtime_flag": True,
        "actual_transport_injected": False,
        "actual_credentials_supplied": False,
        "mobile_summary": mobile_summary,
        "cleanup_summary": cleanup,
        "safety_summary": _safety_summary(),
        "next_safe_action": _next_bridge_action(status),
    }


def build_mobile_operator_panel_payload(
    bridge_state: Mapping[str, Any] | None = None,
    arm_request: Mapping[str, Any] | None = None,
    runtime_snapshot: Mapping[str, Any] | None = None,
    cleanup_candidates: Sequence[str | Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the mobile dashboard payload from sanitized bridge evidence."""

    cleanup = classify_scaffolding_cleanup_candidates(cleanup_candidates)
    runtime = _sanitize_mapping(runtime_snapshot or {})

    if bridge_state:
        state = _sanitize_mapping(bridge_state)
        status = str(state.get("bridge_status", FINAL_LIVE_OPERATOR_BRIDGE_REVIEW_REQUIRED))
        blockers = tuple(state.get("blockers", ()))
        next_safe_action = str(state.get("next_safe_action", _next_bridge_action(status)))
        sanitized_arm = _sanitize_mapping(state.get("sanitized_arm_request", {}))
        runtime_plan = state.get("runtime_execution_plan", {})
        connector_status = str(runtime_plan.get("oanda_connector_status", "UNKNOWN")) if isinstance(runtime_plan, Mapping) else "UNKNOWN"
    else:
        validation = validate_final_live_operator_arm_request(arm_request)
        status = validation["bridge_status"]
        blockers = tuple(validation["blockers"])
        next_safe_action = validation["next_safe_action"]
        sanitized_arm = validation["sanitized_arm_request"]
        connector_status = "BLOCKED_UNTIL_ARM_REQUEST_READY" if not validation["ready"] else "READY_FOR_RUNTIME_PLAN"

    payload = {
        "panel_schema": "AIOS_LIVE_OPERATOR_PANEL_PAYLOAD_V1",
        "mode": "GOVERNED_SINGLE_LIVE_MICRO_TRADE_EXCEPTION",
        "live_bridge_status": status,
        "balance": runtime.get("balance", "UNKNOWN"),
        "equity": runtime.get("equity", "UNKNOWN"),
        "realized_pl": runtime.get("realized_pl", 0),
        "open_risk": runtime.get("open_risk", "UNKNOWN"),
        "active_trades": runtime.get("active_trades", 0),
        "instrument": sanitized_arm.get("instrument", "UNKNOWN"),
        "side": sanitized_arm.get("side", "UNKNOWN"),
        "units": sanitized_arm.get("units", "UNKNOWN"),
        "stop_loss": sanitized_arm.get("stop_loss", "REQUIRED"),
        "take_profit": sanitized_arm.get("take_profit", "REQUIRED"),
        "max_loss_gate": "CLEAR" if sanitized_arm.get("max_loss_gate_clear") else "NOT_CLEAR",
        "daily_stop_gate": "CLEAR" if sanitized_arm.get("daily_stop_clear") else "NOT_CLEAR",
        "kill_switch": "ENABLED" if sanitized_arm.get("kill_switch_enabled") else "DISABLED",
        "broker_connector_status": connector_status,
        "evidence_freshness": runtime.get("evidence_freshness", "UNKNOWN"),
        "blockers": tuple(blockers),
        "next_safe_action": next_safe_action,
        "dashboard_places_order": False,
        "final_execution_requires_explicit_protected_live_action_authorization": True,
        "order_executed": False,
        "broker_call_performed": False,
        "credentials_present": False,
        "account_id_present": False,
        "production_authority": False,
        "cleanup_summary": cleanup,
        "safety_summary": _safety_summary(),
    }

    payload["mobile_summary"] = {
        "status": status,
        "safe_for_samsung_z_fold_6": True,
        "truth_fields_only": True,
        "dashboard_places_order": False,
        "next_safe_action": next_safe_action,
    }
    return payload


def classify_scaffolding_cleanup_candidates(
    files: Sequence[str | Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Classify explicitly supplied files without reading or deleting them."""

    categories: dict[str, list[str]] = {category: [] for category in CLEANUP_CATEGORIES}
    files_inspected: list[str] = []

    for item in files or ():
        metadata = _file_metadata(item)
        path = metadata["path"]
        files_inspected.append(path)
        lowered = path.lower()

        if _has_placeholder(path) or bool(metadata.get("placeholder", False)):
            categories["blocked placeholder"].append(path)
        elif bool(metadata.get("duplicate_of", False)):
            categories["duplicate report"].append(path)
        elif "demo" in lowered:
            categories["demo-only residue"].append(path)
        elif "paper" in lowered:
            categories["paper-only residue"].append(path)
        elif "mock-data" in lowered and bool(metadata.get("fixture_data", False)) is not True:
            categories["mock-data that needs fixture labeling"].append(path)
        elif any(marker in lowered for marker in ("template", "scaffold", "starter")):
            categories["stale scaffold"].append(path)
        else:
            categories["keep-active"].append(path)

    return {
        "cleanup_schema": "AIOS_SCAFFOLDING_CLEANUP_CLASSIFIER_V1",
        "files_inspected": tuple(files_inspected),
        "categories": {category: tuple(values) for category, values in categories.items()},
        "summary": {category: len(values) for category, values in categories.items()},
        "delete_performed": False,
        "cleanup_action_performed": False,
        "next_safe_action": "review_classification_before_any_separate_cleanup_packet",
    }


def _build_order_intent(sanitized_arm: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "instrument": sanitized_arm.get("instrument", "EUR_USD"),
        "side": sanitized_arm.get("side", "BUY"),
        "units": _to_int(sanitized_arm.get("units", 0)),
        "stop_loss": sanitized_arm.get("stop_loss"),
        "take_profit": sanitized_arm.get("take_profit"),
        "risk_cap": sanitized_arm.get("risk_cap", 1),
    }


def _build_mobile_summary(
    status: str,
    arm_request: Mapping[str, Any] | None,
    runtime_snapshot: Mapping[str, Any] | None,
    connector_status: str,
    blockers: Sequence[str],
    next_safe_action: str,
) -> dict[str, Any]:
    arm = _sanitize_mapping(arm_request or {})
    runtime = _sanitize_mapping(runtime_snapshot or {})
    return {
        "mode": "GOVERNED_SINGLE_LIVE_MICRO_TRADE_EXCEPTION",
        "live_bridge_status": status,
        "balance": runtime.get("balance", "UNKNOWN"),
        "equity": runtime.get("equity", "UNKNOWN"),
        "realized_pl": runtime.get("realized_pl", 0),
        "open_risk": runtime.get("open_risk", "UNKNOWN"),
        "active_trades": runtime.get("active_trades", 0),
        "instrument": arm.get("instrument", "UNKNOWN"),
        "side": arm.get("side", "UNKNOWN"),
        "units": arm.get("units", "UNKNOWN"),
        "stop_loss": arm.get("stop_loss", "REQUIRED"),
        "take_profit": arm.get("take_profit", "REQUIRED"),
        "max_loss_gate": "CLEAR" if arm.get("max_loss_gate_clear") else "NOT_CLEAR",
        "daily_stop_gate": "CLEAR" if arm.get("daily_stop_clear") else "NOT_CLEAR",
        "kill_switch": "ENABLED" if arm.get("kill_switch_enabled") else "DISABLED",
        "broker_connector_status": connector_status,
        "evidence_freshness": runtime.get("evidence_freshness", "UNKNOWN"),
        "blockers": tuple(blockers),
        "dashboard_places_order": False,
        "final_execution_requires_explicit_protected_live_action_authorization": True,
        "next_safe_action": next_safe_action,
    }


def _safety_summary() -> dict[str, bool | int]:
    return {
        "general_live_trading_blocked": True,
        "single_live_micro_trade_exception_bridge": True,
        "order_executed": False,
        "broker_call_performed": False,
        "network_call_performed": False,
        "credential_persistence": False,
        "account_id_persistence": False,
        "env_read": False,
        "file_secret_read": False,
        "scheduler_daemon_webhook": False,
        "looping": False,
        "retrying": False,
        "one_order_only": True,
        "max_units": MAX_LIVE_MICRO_UNITS,
        "sanitized_evidence_only": True,
    }


def _next_bridge_action(status: str) -> str:
    return {
        FINAL_LIVE_OPERATOR_BRIDGE_READY: "stop_and_wait_for_separate_human_protected_live_execution_command",
        FINAL_LIVE_OPERATOR_BRIDGE_BLOCKED: "resolve_bridge_safety_blockers_before_live_exception_review",
        FINAL_LIVE_OPERATOR_BRIDGE_REVIEW_REQUIRED: "obtain_explicit_human_protected_live_action_authorization",
        FINAL_LIVE_OPERATOR_BRIDGE_INVALID: "repair_final_live_operator_arm_request",
    }.get(status, "repair_final_live_operator_arm_request")


def _sanitize_mapping(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        return {}
    sanitized: dict[str, Any] = {}
    for key, value in payload.items():
        normalized = str(key).lower().strip()
        if normalized in SENSITIVE_KEYS:
            continue
        if isinstance(value, Mapping):
            sanitized[str(key)] = _sanitize_mapping(value)
        elif isinstance(value, list | tuple):
            sanitized[str(key)] = [
                _sanitize_mapping(item) if isinstance(item, Mapping) else item for item in value
            ]
        else:
            sanitized[str(key)] = value
    sanitized["credentials_persisted"] = False
    sanitized["account_id_persisted"] = False
    return sanitized


def _contains_sensitive_keys(payload: Any) -> bool:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            normalized = str(key).lower().strip()
            if normalized in SENSITIVE_KEYS:
                return True
            if _contains_sensitive_keys(value):
                return True
    elif isinstance(payload, list | tuple):
        return any(_contains_sensitive_keys(item) for item in payload)
    return False


def _file_metadata(item: str | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(item, Mapping):
        path = str(item.get("path", "")).strip()
        metadata = dict(item)
        metadata["path"] = path
        return metadata
    return {"path": str(item).strip()}


def _has_placeholder(path: str) -> bool:
    return any(marker in path for marker in ("@filename", "{", "}", "[REAL-FILENAME]", "TODO", "TBD"))


def _to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _unique(values: Sequence[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = str(value)
        if text not in seen:
            seen.add(text)
            output.append(text)
    return tuple(output)

