from __future__ import annotations

from typing import Any, Mapping

from automation.forex_engine.oanda_demo_read_only_preflight_from_vault_v1 import (
    ACCESS_TOKEN_CREDENTIAL_NAME,
    ACCOUNT_ID_CREDENTIAL_NAME,
)
from automation.forex_engine.oanda_demo_runtime_http_transport_one_order_owner_run_v1 import (
    DEMO_API_BASE_URL_PREFIX,
    TRANSPORT_ATTEMPTED_OANDA_DEMO_ORDER_ONCE,
    TRANSPORT_BLOCKED_RUNTIME_CREDENTIALS_MISSING,
    evaluate_oanda_demo_runtime_http_transport_one_order_owner_run_v1,
)


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-VAULT-BACKED-ONE-ORDER-TRANSPORT-V1"
TRANSPORT_VERSION = "v1"

VAULT_BACKED_DEMO_ONE_ORDER_READY_FOR_OWNER_RUN = (
    "VAULT_BACKED_DEMO_ONE_ORDER_READY_FOR_OWNER_RUN"
)
BLOCKED_BY_MISSING_VAULT_CREDENTIALS = "BLOCKED_BY_MISSING_VAULT_CREDENTIALS"
BLOCKED_BY_INVALID_TRADE_INTENT = "BLOCKED_BY_INVALID_TRADE_INTENT"
BLOCKED_BY_MISSING_STOP_LOSS = "BLOCKED_BY_MISSING_STOP_LOSS"
BLOCKED_BY_MISSING_TAKE_PROFIT = "BLOCKED_BY_MISSING_TAKE_PROFIT"
BLOCKED_BY_LIVE_ENDPOINT = "BLOCKED_BY_LIVE_ENDPOINT"
BLOCKED_BY_AUTONOMY_REQUEST = "BLOCKED_BY_AUTONOMY_REQUEST"
BLOCKED_BY_ORDER_CAP = "BLOCKED_BY_ORDER_CAP"
BLOCKED_BY_PROFIT_CLAIM = "BLOCKED_BY_PROFIT_CLAIM"
VAULT_BACKED_DEMO_ONE_ORDER_ATTEMPTED = "VAULT_BACKED_DEMO_ONE_ORDER_ATTEMPTED"

APPROVED_INSTRUMENT = "EUR_USD"
ALLOWED_DIRECTIONS = ("BUY", "SELL")
ALLOWED_ORDER_TYPES = ("MARKET",)
MICRO_UNITS_MIN = 1
MICRO_UNITS_MAX = 1000
REDACTED_TOKEN_REFERENCE = "REDACTED_RUNTIME_ACCESS_TOKEN"
REDACTED_ACCOUNT_ID_REFERENCE = "REDACTED_RUNTIME_ACCOUNT_ID"
REDACTED_RUNTIME_ONLY_REFERENCE = "REDACTED_RUNTIME_ONLY_REFERENCE"

APPROVED_VAULT_CREDENTIAL_NAMES = (
    ACCESS_TOKEN_CREDENTIAL_NAME,
    ACCOUNT_ID_CREDENTIAL_NAME,
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
    "order_mutation_allowed",
    "position_mutation_allowed",
)

SENSITIVE_KEY_EXACT = {
    "access_token",
    "token",
    "authorization",
    "password",
    "secret",
    "api_key",
    "secret_value",
    "credential_value",
    "runtime_access_token",
    "runtime_account_id",
    "account_id",
    "accountid",
}

SENSITIVE_KEY_TERMS = (
    "access_token",
    "authorization",
    "password",
    "secret",
    "api_key",
    "secret_value",
    "credential_value",
    "runtime_access_token",
    "runtime_account_id",
    "account_id",
    "accountid",
)


def default_oanda_demo_vault_backed_one_order_transport_context_v1() -> dict[str, Any]:
    return {
        "instrument": APPROVED_INSTRUMENT,
        "direction": "BUY",
        "units": 1,
        "stop_loss": "",
        "take_profit": "",
        "risk_amount": None,
        "client_order_id": "AIOS-DEMO-ONE-ORDER-OWNER-RUNTIME-001",
        "order_type": "MARKET",
        "reward_risk_ratio": 1.0,
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "demo_api_base_url": DEMO_API_BASE_URL_PREFIX,
        "live_api_base_url": "",
        "demo_only_confirmed": False,
        "vault_backed_runtime_only_confirmed": False,
        "one_order_only_confirmed": False,
        "owner_manual_runtime_only_confirmed": False,
        "stop_loss_confirmed": False,
        "take_profit_confirmed": False,
        "no_live_endpoint_confirmed": False,
        "no_autonomous_order_confirmed": False,
        "no_second_order_confirmed": False,
        "post_trade_evidence_confirmed": False,
        "kill_switch_ready_confirmed": False,
        "loss_possible_understood": False,
        "no_profit_guarantee_understood": False,
        "max_order_attempts": 1,
        "order_already_attempted": False,
        "scheduler_requested": False,
        "daemon_requested": False,
        "webhook_requested": False,
        "profit_claim_made": False,
    }


def evaluate_oanda_demo_vault_backed_one_order_transport_v1(
    command_context: Mapping[str, Any] | None = None,
    *,
    vault_load_callable: object | None = None,
    http_post_callable: object | None = None,
    execute_transport: bool = False,
) -> dict[str, Any]:
    normalized = _normalize_context(command_context)
    classification = _classification(normalized)
    blockers = _blockers(normalized)
    vault_records: list[dict[str, Any]] = []
    runtime_access_token = ""
    runtime_account_id = ""
    transport_decision: Mapping[str, Any] | None = None

    if classification != VAULT_BACKED_DEMO_ONE_ORDER_READY_FOR_OWNER_RUN:
        return _result(
            status=classification,
            blockers=blockers,
            normalized=normalized,
            vault_records=vault_records,
            transport_decision=transport_decision,
            runtime_access_token=runtime_access_token,
            runtime_account_id=runtime_account_id,
        )

    if execute_transport is not True:
        return _result(
            status=VAULT_BACKED_DEMO_ONE_ORDER_READY_FOR_OWNER_RUN,
            blockers=[],
            normalized=normalized,
            vault_records=vault_records,
            transport_decision=transport_decision,
            runtime_access_token=runtime_access_token,
            runtime_account_id=runtime_account_id,
        )

    if not callable(vault_load_callable):
        return _result(
            status=BLOCKED_BY_MISSING_VAULT_CREDENTIALS,
            blockers=["windows_vault_load_adapter_required"],
            normalized=normalized,
            vault_records=vault_records,
            transport_decision=transport_decision,
            runtime_access_token=runtime_access_token,
            runtime_account_id=runtime_account_id,
        )

    vault_records = [
        _load_vault_record(vault_load_callable, ACCESS_TOKEN_CREDENTIAL_NAME),
        _load_vault_record(vault_load_callable, ACCOUNT_ID_CREDENTIAL_NAME),
    ]
    runtime_access_token = _extract_loaded_secret(vault_records[0])
    runtime_account_id = _extract_loaded_secret(vault_records[1])

    if not _present(runtime_access_token) or not _present(runtime_account_id):
        missing = []
        if not _present(runtime_access_token):
            missing.append("approved_demo_access_token_missing_from_vault")
        if not _present(runtime_account_id):
            missing.append("approved_demo_account_id_missing_from_vault")
        return _result(
            status=BLOCKED_BY_MISSING_VAULT_CREDENTIALS,
            blockers=missing,
            normalized=normalized,
            vault_records=vault_records,
            transport_decision=transport_decision,
            runtime_access_token=runtime_access_token,
            runtime_account_id=runtime_account_id,
        )

    if not callable(http_post_callable):
        return _result(
            status=BLOCKED_BY_INVALID_TRADE_INTENT,
            blockers=["http_post_callable_required_for_owner_runtime_transport"],
            normalized=normalized,
            vault_records=vault_records,
            transport_decision=transport_decision,
            runtime_access_token=runtime_access_token,
            runtime_account_id=runtime_account_id,
        )

    transport_decision = evaluate_oanda_demo_runtime_http_transport_one_order_owner_run_v1(
        actual_owner_command_result=_ready_actual_owner_command_result(),
        broker_call_result=_ready_broker_call_result(),
        transport_context=_ready_transport_context(normalized),
        sanitized_order_payload=_order_payload(normalized),
        owner_transport_confirmation=_owner_transport_confirmation(),
        execute_transport=True,
        runtime_access_token=runtime_access_token,
        runtime_account_id=runtime_account_id,
        http_post_callable=http_post_callable,
    )
    if transport_decision.get("status") == TRANSPORT_ATTEMPTED_OANDA_DEMO_ORDER_ONCE:
        status = VAULT_BACKED_DEMO_ONE_ORDER_ATTEMPTED
    elif transport_decision.get("status") == TRANSPORT_BLOCKED_RUNTIME_CREDENTIALS_MISSING:
        status = BLOCKED_BY_MISSING_VAULT_CREDENTIALS
    else:
        status = _map_transport_status(transport_decision.get("status"))

    return _result(
        status=status,
        blockers=list(transport_decision.get("blockers", [])),
        normalized=normalized,
        vault_records=vault_records,
        transport_decision=transport_decision,
        runtime_access_token=runtime_access_token,
        runtime_account_id=runtime_account_id,
    )


def _normalize_context(command_context: Mapping[str, Any] | None) -> dict[str, Any]:
    defaults = default_oanda_demo_vault_backed_one_order_transport_context_v1()
    context = command_context if isinstance(command_context, Mapping) else {}
    merged = {**defaults, **dict(context)}
    return {
        "instrument": _text(merged.get("instrument")).upper(),
        "direction": _text(merged.get("direction")).upper(),
        "units": _number_or_none(merged.get("units")),
        "units_supplied": merged.get("units") is not None,
        "stop_loss": _text(merged.get("stop_loss")),
        "take_profit": _text(merged.get("take_profit")),
        "risk_amount": _number_or_none(merged.get("risk_amount")),
        "risk_amount_supplied": merged.get("risk_amount") is not None,
        "client_order_id": _text(merged.get("client_order_id")),
        "order_type": _text(merged.get("order_type")).upper(),
        "reward_risk_ratio": _number_or_none(merged.get("reward_risk_ratio")) or 1.0,
        "broker": _text(merged.get("broker")),
        "environment": _text(merged.get("environment")),
        "demo_api_base_url": _text(merged.get("demo_api_base_url")),
        "live_api_base_url": _text(merged.get("live_api_base_url")),
        "demo_only_confirmed": _bool(merged.get("demo_only_confirmed")),
        "vault_backed_runtime_only_confirmed": _bool(
            merged.get("vault_backed_runtime_only_confirmed")
        ),
        "one_order_only_confirmed": _bool(merged.get("one_order_only_confirmed")),
        "owner_manual_runtime_only_confirmed": _bool(
            merged.get("owner_manual_runtime_only_confirmed")
        ),
        "stop_loss_confirmed": _bool(merged.get("stop_loss_confirmed")),
        "take_profit_confirmed": _bool(merged.get("take_profit_confirmed")),
        "no_live_endpoint_confirmed": _bool(merged.get("no_live_endpoint_confirmed")),
        "no_autonomous_order_confirmed": _bool(
            merged.get("no_autonomous_order_confirmed")
        ),
        "no_second_order_confirmed": _bool(merged.get("no_second_order_confirmed")),
        "post_trade_evidence_confirmed": _bool(
            merged.get("post_trade_evidence_confirmed")
        ),
        "kill_switch_ready_confirmed": _bool(
            merged.get("kill_switch_ready_confirmed")
        ),
        "loss_possible_understood": _bool(merged.get("loss_possible_understood")),
        "no_profit_guarantee_understood": _bool(
            merged.get("no_profit_guarantee_understood")
        ),
        "max_order_attempts": _number_or_none(merged.get("max_order_attempts")),
        "order_already_attempted": _bool(merged.get("order_already_attempted")),
        "scheduler_requested": _bool(merged.get("scheduler_requested")),
        "daemon_requested": _bool(merged.get("daemon_requested")),
        "webhook_requested": _bool(merged.get("webhook_requested")),
        "profit_claim_made": _bool(merged.get("profit_claim_made")),
    }


def _classification(normalized: Mapping[str, Any]) -> str:
    blockers = _blockers(normalized)
    for status in (
        BLOCKED_BY_LIVE_ENDPOINT,
        BLOCKED_BY_AUTONOMY_REQUEST,
        BLOCKED_BY_ORDER_CAP,
        BLOCKED_BY_PROFIT_CLAIM,
        BLOCKED_BY_MISSING_STOP_LOSS,
        BLOCKED_BY_MISSING_TAKE_PROFIT,
        BLOCKED_BY_INVALID_TRADE_INTENT,
    ):
        if any(blocker.startswith(f"{status}:") for blocker in blockers):
            return status
    return VAULT_BACKED_DEMO_ONE_ORDER_READY_FOR_OWNER_RUN


def _blockers(normalized: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []

    def add(status: str, message: str) -> None:
        blockers.append(f"{status}:{message}")

    if normalized["live_api_base_url"] or not normalized["no_live_endpoint_confirmed"]:
        add(BLOCKED_BY_LIVE_ENDPOINT, "live_endpoint_must_be_absent_and_confirmed")
    if normalized["environment"] != "DEMO" or normalized["broker"] != "OANDA_DEMO":
        add(BLOCKED_BY_LIVE_ENDPOINT, "transport_context_must_be_oanda_demo")
    if not normalized["demo_api_base_url"].startswith(DEMO_API_BASE_URL_PREFIX):
        add(BLOCKED_BY_LIVE_ENDPOINT, "demo_api_base_url_must_be_practice")

    if (
        not normalized["owner_manual_runtime_only_confirmed"]
        or not normalized["vault_backed_runtime_only_confirmed"]
        or not normalized["no_autonomous_order_confirmed"]
        or normalized["scheduler_requested"]
        or normalized["daemon_requested"]
        or normalized["webhook_requested"]
    ):
        add(
            BLOCKED_BY_AUTONOMY_REQUEST,
            "owner_manual_vault_runtime_only_and_no_autonomy_required",
        )

    if (
        not normalized["one_order_only_confirmed"]
        or not normalized["no_second_order_confirmed"]
        or normalized["max_order_attempts"] != 1
        or normalized["order_already_attempted"]
    ):
        add(BLOCKED_BY_ORDER_CAP, "one_order_only_cap_required")

    if (
        not normalized["no_profit_guarantee_understood"]
        or normalized["profit_claim_made"]
    ):
        add(BLOCKED_BY_PROFIT_CLAIM, "no_profit_guarantee_required")

    if not _present(normalized["stop_loss"]) or not normalized["stop_loss_confirmed"]:
        add(BLOCKED_BY_MISSING_STOP_LOSS, "stop_loss_required_and_confirmed")
    if not _present(normalized["take_profit"]) or not normalized["take_profit_confirmed"]:
        add(BLOCKED_BY_MISSING_TAKE_PROFIT, "take_profit_required_and_confirmed")

    if normalized["instrument"] != APPROVED_INSTRUMENT:
        add(BLOCKED_BY_INVALID_TRADE_INTENT, "instrument_must_be_eur_usd")
    if normalized["direction"] not in ALLOWED_DIRECTIONS:
        add(BLOCKED_BY_INVALID_TRADE_INTENT, "direction_must_be_buy_or_sell")
    if not _micro_units_valid(normalized["units"]):
        add(BLOCKED_BY_INVALID_TRADE_INTENT, "units_must_be_integer_micro_size")
    if (
        not normalized["risk_amount_supplied"]
        or not _positive_number(normalized["risk_amount"])
    ):
        add(BLOCKED_BY_INVALID_TRADE_INTENT, "risk_amount_must_be_positive")
    if normalized["order_type"] not in ALLOWED_ORDER_TYPES:
        add(BLOCKED_BY_INVALID_TRADE_INTENT, "order_type_must_be_market")
    if not _sanitized_client_order_id(normalized["client_order_id"]):
        add(BLOCKED_BY_INVALID_TRADE_INTENT, "client_order_id_required_and_sanitized")
    for field in (
        "demo_only_confirmed",
        "post_trade_evidence_confirmed",
        "kill_switch_ready_confirmed",
        "loss_possible_understood",
    ):
        if not normalized[field]:
            add(BLOCKED_BY_INVALID_TRADE_INTENT, f"{field}_required")
    return _unique(blockers)


def _load_vault_record(
    vault_load_callable: object,
    credential_name: str,
) -> dict[str, Any]:
    payload = {"credential_name": credential_name}
    try:
        result = vault_load_callable(payload)  # type: ignore[misc]
    except Exception as exc:  # pragma: no cover - defensive adapter boundary
        result = {
            "credential_name": credential_name,
            "load_status": "vault_adapter_exception",
            "error_type": type(exc).__name__,
            "secret_value": "",
        }
    return {
        "operation": "load",
        "credential_name": credential_name,
        "result": result,
    }


def _extract_loaded_secret(vault_record: Mapping[str, Any]) -> str:
    result = vault_record.get("result")
    if isinstance(result, str):
        return result
    if isinstance(result, Mapping):
        for key in (
            "secret_value",
            "value",
            "secret",
            "credential_value",
            "password",
        ):
            value = result.get(key)
            if isinstance(value, str):
                return value
    return ""


def _ready_actual_owner_command_result() -> dict[str, Any]:
    return {
        "status": "ACTUAL_RUN_READY_FOR_OWNER_MANUAL_COMMAND",
        "final_manual_command_package": {
            "ready": True,
            "one_order_only": True,
            "max_order_attempts": 1,
        },
        "execution_authority": _execution_authority(),
    }


def _ready_broker_call_result() -> dict[str, Any]:
    return {
        "status": "BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED",
        "network_call_performed": False,
        "order_placement_performed": False,
        "execution_authority": _execution_authority(),
    }


def _ready_transport_context(normalized: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "demo_endpoint_only": True,
        "live_endpoint_absent": True,
        "demo_api_base_url": normalized["demo_api_base_url"],
        "live_api_base_url": "",
        "runtime_token_external": True,
        "runtime_account_id_external": True,
        "runtime_credentials_available_to_owner": True,
        "credential_persistence_detected": False,
        "account_id_persistence_detected": False,
        "one_order_only": True,
        "max_order_attempts": 1,
        "order_already_attempted": False,
        "existing_open_orders": 0,
        "existing_pending_orders": 0,
        "owner_present_for_manual_run": True,
        "kill_switch_ready": True,
        "daily_stop_ready": True,
        "max_loss_gate_ready": True,
        "stop_loss_ready": True,
        "take_profit_ready": True,
        "pre_trade_evidence_ready": True,
        "post_trade_evidence_plan_ready": True,
        "execution_window_open": True,
        "market_open_or_owner_override": True,
        "execution_authority": _execution_authority(),
    }


def _order_payload(normalized: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "instrument": normalized["instrument"],
        "direction": normalized["direction"],
        "order_type": normalized["order_type"],
        "units": normalized["units"],
        "stop_loss": normalized["stop_loss"],
        "take_profit": normalized["take_profit"],
        "risk_amount": normalized["risk_amount"],
        "reward_risk_ratio": normalized["reward_risk_ratio"],
        "client_order_id": normalized["client_order_id"],
        "execution_authority": _execution_authority(),
    }


def _owner_transport_confirmation() -> dict[str, bool]:
    return {
        "owner_confirmed_transport_reviewed": True,
        "owner_confirmed_actual_demo_order_intent": True,
        "owner_confirmed_demo_only": True,
        "owner_confirmed_no_live_money": True,
        "owner_confirmed_one_order_only": True,
        "owner_confirmed_max_one_attempt": True,
        "owner_confirmed_stop_loss": True,
        "owner_confirmed_take_profit": True,
        "owner_confirmed_loss_possible": True,
        "owner_confirmed_no_profit_guarantee": True,
        "owner_confirmed_no_second_order": True,
        "owner_confirmed_manual_run_only": True,
        "owner_confirmed_post_trade_evidence_required": True,
        "owner_confirmed_kill_switch_ready": True,
        "owner_confirmed_runtime_credentials_external": True,
    }


def _result(
    *,
    status: str,
    blockers: list[str],
    normalized: Mapping[str, Any],
    vault_records: list[dict[str, Any]],
    transport_decision: Mapping[str, Any] | None,
    runtime_access_token: str,
    runtime_account_id: str,
) -> dict[str, Any]:
    transport_attempt = _mapping(transport_decision.get("transport_attempt")) if transport_decision else {}
    result = {
        "packet_id": PACKET_ID,
        "transport_version": TRANSPORT_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": _warnings(status),
        "approved_vault_labels": list(APPROVED_VAULT_CREDENTIAL_NAMES),
        "vault_load_boundary": {
            "vault_load_attempted": bool(vault_records),
            "approved_vault_labels_only": True,
            "credential_values_runtime_only": True,
            "credential_values_printed": False,
            "credential_values_persisted_to_repo": False,
            "command_line_token_argument_supported": False,
            "command_line_account_id_argument_supported": False,
        },
        "sanitized_vault_load_result": vault_records if vault_records else None,
        "trade_intent_summary": _trade_intent_summary(normalized),
        "transport_decision": transport_decision,
        "broker_network_call_performed": _bool(
            transport_attempt.get("network_call_performed")
        ),
        "order_placement_performed": _bool(
            transport_attempt.get("order_placement_performed")
        ),
        "order_attempt_count": _integer(transport_attempt.get("order_attempt_count"), 0),
        "credential_read_performed": bool(vault_records),
        "account_id_read_performed": bool(vault_records),
        "credential_value_printed": False,
        "account_id_value_printed": False,
        "dotenv_read": False,
        "live_endpoint_used": False,
        "one_order_only": True,
        "second_order_allowed": False,
        "autonomous_retry_allowed": False,
        "post_trade_evidence_required": True,
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }
    result.update(_execution_authority())
    return _sanitize_value(
        result,
        runtime_access_token=runtime_access_token,
        runtime_account_id=runtime_account_id,
    )


def _trade_intent_summary(normalized: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "instrument": normalized["instrument"],
        "direction": normalized["direction"],
        "units": normalized["units"],
        "order_type": normalized["order_type"],
        "stop_loss_present": _present(normalized["stop_loss"]),
        "take_profit_present": _present(normalized["take_profit"]),
        "risk_amount_present": _positive_number(normalized["risk_amount"]),
        "client_order_id_present": _present(normalized["client_order_id"]),
        "demo_endpoint_only": True,
        "one_order_only": True,
        "owner_manual_runtime_only": True,
    }


def _warnings(status: str) -> list[str]:
    warnings = [
        "owner_run_only",
        "windows_vault_runtime_only",
        "approved_vault_labels_only",
        "demo_endpoint_only",
        "one_order_cap_in_force",
        "no_live_trading",
        "no_autonomous_execution",
        "no_scheduler_daemon_or_webhook",
        "no_credentials_or_account_ids_persisted",
        "post_trade_evidence_required",
        "no_profit_guarantee",
    ]
    if status == VAULT_BACKED_DEMO_ONE_ORDER_READY_FOR_OWNER_RUN:
        warnings.append("ready_state_does_not_read_vault_or_call_broker")
    if status == VAULT_BACKED_DEMO_ONE_ORDER_ATTEMPTED:
        warnings.append("owner_runtime_http_transport_called_once")
    return warnings


def _next_safe_action(status: str) -> str:
    return {
        VAULT_BACKED_DEMO_ONE_ORDER_READY_FOR_OWNER_RUN: (
            "owner_may_run_vault_backed_demo_one_order_wrapper_if_intended"
        ),
        BLOCKED_BY_MISSING_VAULT_CREDENTIALS: (
            "owner_confirm_approved_windows_vault_labels_exist"
        ),
        BLOCKED_BY_INVALID_TRADE_INTENT: (
            "repair_trade_intent_and_required_confirmations"
        ),
        BLOCKED_BY_MISSING_STOP_LOSS: "provide_owner_reviewed_stop_loss",
        BLOCKED_BY_MISSING_TAKE_PROFIT: "provide_owner_reviewed_take_profit",
        BLOCKED_BY_LIVE_ENDPOINT: "remove_live_endpoint_or_live_trading_request",
        BLOCKED_BY_AUTONOMY_REQUEST: (
            "remove_scheduler_daemon_webhook_or_non_manual_path"
        ),
        BLOCKED_BY_ORDER_CAP: "preserve_one_order_only_and_no_second_order",
        BLOCKED_BY_PROFIT_CLAIM: "remove_profit_or_campaign_guarantee_claim",
        VAULT_BACKED_DEMO_ONE_ORDER_ATTEMPTED: (
            "capture_sanitized_post_trade_evidence_and_do_not_rerun"
        ),
    }.get(status, "stop_and_review_vault_backed_transport_status")


def _map_transport_status(status: Any) -> str:
    status_text = _text(status)
    if "LIVE" in status_text:
        return BLOCKED_BY_LIVE_ENDPOINT
    if "CONFIRMATION" in status_text:
        return BLOCKED_BY_INVALID_TRADE_INTENT
    if "ORDER_PAYLOAD" in status_text:
        return BLOCKED_BY_INVALID_TRADE_INTENT
    if "CONTEXT" in status_text:
        return BLOCKED_BY_INVALID_TRADE_INTENT
    return BLOCKED_BY_INVALID_TRADE_INTENT


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _sanitize_value(
    value: Any,
    *,
    runtime_access_token: str,
    runtime_account_id: str,
) -> Any:
    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        for key, child in value.items():
            key_text = str(key)
            if key_text in {"credential_name", "approved_vault_labels"}:
                sanitized[key_text] = child
            elif _sensitive_key(key_text) and isinstance(child, str):
                sanitized[key_text] = REDACTED_RUNTIME_ONLY_REFERENCE
            else:
                sanitized[key_text] = _sanitize_value(
                    child,
                    runtime_access_token=runtime_access_token,
                    runtime_account_id=runtime_account_id,
                )
        return sanitized
    if isinstance(value, list):
        return [
            _sanitize_value(
                child,
                runtime_access_token=runtime_access_token,
                runtime_account_id=runtime_account_id,
            )
            for child in value
        ]
    if isinstance(value, str):
        redacted = value
        if runtime_access_token:
            redacted = redacted.replace(runtime_access_token, REDACTED_TOKEN_REFERENCE)
        if runtime_account_id:
            redacted = redacted.replace(runtime_account_id, REDACTED_ACCOUNT_ID_REFERENCE)
        return redacted
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return repr(value)


def _sensitive_key(key: str) -> bool:
    key_text = key.lower()
    if key_text in {"credential_name", "approved_vault_labels"}:
        return False
    return key_text in SENSITIVE_KEY_EXACT or any(
        term in key_text for term in SENSITIVE_KEY_TERMS
    )


def _micro_units_valid(value: Any) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    return float(value).is_integer() and MICRO_UNITS_MIN <= value <= MICRO_UNITS_MAX


def _positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def _number_or_none(value: Any) -> int | float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            numeric = float(stripped)
        except ValueError:
            return None
        return int(numeric) if numeric.is_integer() else numeric
    return None


def _integer(value: Any, default: int) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return default


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _present(value: Any) -> bool:
    return bool(value.strip()) if isinstance(value, str) else value is not None


def _bool(value: Any) -> bool:
    return value is True


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


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
