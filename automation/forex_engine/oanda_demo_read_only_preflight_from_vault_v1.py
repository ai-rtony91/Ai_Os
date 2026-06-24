from __future__ import annotations

from typing import Any, Mapping, Sequence
from urllib.parse import urlparse

from automation.forex_engine.oanda_demo_credential_account_permission_preflight_no_order_v1 import (
    DEMO_API_BASE_URL_PREFIX,
    PREFLIGHT_READ_ONLY_ATTEMPTED,
    evaluate_oanda_demo_credential_account_permission_preflight_no_order_v1,
)
from automation.forex_engine.oanda_demo_secure_credential_persistence_windows_vault_v1 import (
    ACCESS_TOKEN_CREDENTIAL_NAME,
    ACCOUNT_ID_CREDENTIAL_NAME,
)


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-READ-ONLY-PREFLIGHT-FROM-VAULT-V1"
PREFLIGHT_FROM_VAULT_VERSION = "v1"

VAULT_PREFLIGHT_DRY_RUN_READY = "VAULT_PREFLIGHT_DRY_RUN_READY"
VAULT_PREFLIGHT_BLOCKED_MISSING_VAULT_ADAPTER = (
    "VAULT_PREFLIGHT_BLOCKED_MISSING_VAULT_ADAPTER"
)
VAULT_PREFLIGHT_BLOCKED_MISSING_TOKEN = "VAULT_PREFLIGHT_BLOCKED_MISSING_TOKEN"
VAULT_PREFLIGHT_BLOCKED_MISSING_ACCOUNT_ID = (
    "VAULT_PREFLIGHT_BLOCKED_MISSING_ACCOUNT_ID"
)
VAULT_PREFLIGHT_BLOCKED_LIVE_MODE = "VAULT_PREFLIGHT_BLOCKED_LIVE_MODE"
VAULT_PREFLIGHT_BLOCKED_UNSAFE_ENDPOINT = "VAULT_PREFLIGHT_BLOCKED_UNSAFE_ENDPOINT"
VAULT_PREFLIGHT_READ_ONLY_ATTEMPTED = "VAULT_PREFLIGHT_READ_ONLY_ATTEMPTED"

REDACTED_TOKEN_REFERENCE = "REDACTED_RUNTIME_ACCESS_TOKEN"
REDACTED_ACCOUNT_ID_REFERENCE = "REDACTED_RUNTIME_ACCOUNT_ID"
REDACTED_RUNTIME_ONLY_REFERENCE = "REDACTED_RUNTIME_ONLY_REFERENCE"

FORBIDDEN_ENDPOINT_TERMS = (
    "/orders",
    "/trades",
    "/positions",
    "/transactions",
    "api-fxtrade.oanda.com",
)

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

PROOF_FIELDS = (
    "broker_network_call_performed",
    "order_placement_performed",
    "orders_endpoint_called",
    "credential_value_printed",
    "account_id_value_printed",
    "vault_value_persisted_to_repo",
    "dotenv_read",
    "live_endpoint_used",
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


def evaluate_oanda_demo_read_only_preflight_from_vault_v1(
    preflight_context: dict | None = None,
    *,
    vault_load_callable: object | None = None,
    http_get_callable: object | None = None,
    execute_preflight: bool = False,
    endpoint_plan_override: Sequence[Mapping[str, Any] | str] | None = None,
) -> dict[str, Any]:
    context = _context_or_default(preflight_context)
    endpoint_plan = _endpoint_plan_from_context(
        context,
        endpoint_plan_override=endpoint_plan_override,
    )
    context_blockers = _context_blockers(context)
    endpoint_blockers = _endpoint_plan_blockers(endpoint_plan)
    blockers = _unique(context_blockers + endpoint_blockers)

    token: str | None = None
    account_id: str | None = None
    vault_records: list[dict[str, Any]] = []
    preflight_decision: dict[str, Any] | None = None

    if context_blockers:
        status = VAULT_PREFLIGHT_BLOCKED_LIVE_MODE
    elif endpoint_blockers:
        status = VAULT_PREFLIGHT_BLOCKED_UNSAFE_ENDPOINT
    elif execute_preflight is not True:
        status = VAULT_PREFLIGHT_DRY_RUN_READY
    elif not callable(vault_load_callable):
        status = VAULT_PREFLIGHT_BLOCKED_MISSING_VAULT_ADAPTER
        blockers = _unique(blockers + ["windows_vault_load_adapter_required"])
    else:
        vault_records = [
            _load_vault_record(vault_load_callable, ACCESS_TOKEN_CREDENTIAL_NAME),
            _load_vault_record(vault_load_callable, ACCOUNT_ID_CREDENTIAL_NAME),
        ]
        token = _extract_loaded_secret(vault_records[0])
        account_id = _extract_loaded_secret(vault_records[1])

        if not _present(token):
            status = VAULT_PREFLIGHT_BLOCKED_MISSING_TOKEN
            blockers = _unique(blockers + ["vault_demo_access_token_missing"])
        elif not _present(account_id):
            status = VAULT_PREFLIGHT_BLOCKED_MISSING_ACCOUNT_ID
            blockers = _unique(blockers + ["vault_demo_account_id_missing"])
        elif not callable(http_get_callable):
            status = VAULT_PREFLIGHT_BLOCKED_UNSAFE_ENDPOINT
            blockers = _unique(
                blockers + ["http_get_callable_required_for_read_only_preflight"]
            )
        else:
            preflight_decision = (
                evaluate_oanda_demo_credential_account_permission_preflight_no_order_v1(
                    preflight_context=_account_permission_preflight_context(),
                    runtime_access_token=token,
                    runtime_account_id=account_id,
                    http_get_callable=http_get_callable,
                    execute_preflight=True,
                )
            )
            if preflight_decision.get("status") == PREFLIGHT_READ_ONLY_ATTEMPTED:
                status = VAULT_PREFLIGHT_READ_ONLY_ATTEMPTED
            else:
                status = VAULT_PREFLIGHT_BLOCKED_UNSAFE_ENDPOINT
                blockers = _unique(
                    blockers
                    + [
                        "read_only_preflight_dependency_blocked",
                        _text(preflight_decision.get("status"), "unknown_status"),
                    ]
                )

    proof = _proof_fields(preflight_decision)
    result: dict[str, Any] = {
        "packet_id": PACKET_ID,
        "preflight_from_vault_version": PREFLIGHT_FROM_VAULT_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": _warnings(status),
        "preflight_context_summary": _preflight_context_summary(context),
        "vault_load_boundary": {
            "adapter_required_for_execute": True,
            "adapter_supplied": callable(vault_load_callable),
            "vault_load_attempted": bool(vault_records),
            "credential_names": list(APPROVED_VAULT_CREDENTIAL_NAMES),
            "credential_values_runtime_only": True,
            "credential_values_printed": False,
            "credential_values_persisted_to_repo": False,
            "approved_credential_names_only": True,
        },
        "sanitized_vault_load_result": _sanitize_value(
            vault_records,
            runtime_access_token=token,
            runtime_account_id=account_id,
        )
        if vault_records
        else None,
        "read_only_endpoint_policy": {
            "allowed_endpoints": _allowed_endpoint_templates(),
            "forbidden_endpoint_terms": list(FORBIDDEN_ENDPOINT_TERMS),
            "method_allowed": "GET",
            "practice_base_url_only": True,
            "live_base_url_allowed": False,
            "mutation_endpoints_allowed": False,
        },
        "read_only_endpoint_plan": _sanitize_value(
            endpoint_plan,
            runtime_access_token=token,
            runtime_account_id=account_id,
        ),
        "sanitized_read_only_preflight_decision": _sanitize_value(
            preflight_decision,
            runtime_access_token=token,
            runtime_account_id=account_id,
        )
        if preflight_decision
        else None,
        "execution_authority": _execution_authority(),
        "safety_proof": proof,
        "next_safe_action": _next_safe_action(status),
    }
    result.update(_execution_authority())
    result.update(proof)
    return _sanitize_value(
        result,
        runtime_access_token=token,
        runtime_account_id=account_id,
    )


def default_oanda_demo_read_only_preflight_from_vault_context_v1() -> dict[str, Any]:
    return {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "demo_only": True,
        "windows_vault_only": True,
        "demo_api_base_url": DEMO_API_BASE_URL_PREFIX,
        "live_api_base_url": "",
        "live_credentials_allowed": False,
        "live_mode": False,
        "read_only_preflight_only": True,
        "no_env_file": True,
        "no_repo_persistence": True,
        "no_live_credentials": True,
        "token_visible_account_required": True,
        "no_order_endpoint": True,
        "no_trade_mutation": True,
        "no_second_order_attempt": True,
        "execution_authority": _execution_authority(),
    }


def validate_oanda_demo_vault_preflight_endpoint_url_v1(
    url: str,
    *,
    method: str = "GET",
) -> list[str]:
    blockers: list[str] = []
    parsed = urlparse(url)
    normalized_method = _text(method).upper()

    if normalized_method != "GET":
        blockers.append("method_must_be_get")
    for term in FORBIDDEN_ENDPOINT_TERMS:
        if term in url:
            blockers.append(f"forbidden_endpoint_term_{_blocker_label(term)}")
    if parsed.scheme != "https" or parsed.netloc != "api-fxpractice.oanda.com":
        blockers.append("url_must_use_oanda_practice_base")

    path_parts = [part for part in parsed.path.split("/") if part]
    allowed_shape = (
        path_parts == ["v3", "accounts"]
        or (
            len(path_parts) == 3
            and path_parts[0:2] == ["v3", "accounts"]
            and _present(path_parts[2])
        )
        or (
            len(path_parts) == 4
            and path_parts[0:2] == ["v3", "accounts"]
            and _present(path_parts[2])
            and path_parts[3] in {"summary", "instruments"}
        )
    )
    if not allowed_shape:
        blockers.append("url_must_be_allowed_account_metadata_endpoint")
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


def _context_or_default(context: dict | None) -> Mapping[str, Any]:
    if context is None:
        return default_oanda_demo_read_only_preflight_from_vault_context_v1()
    return context if isinstance(context, Mapping) else {}


def _context_blockers(context: Mapping[str, Any]) -> list[str]:
    if not context:
        return ["missing_preflight_from_vault_context"]

    blockers: list[str] = []
    if context.get("broker") != "OANDA_DEMO":
        blockers.append("context_broker_must_be_oanda_demo")
    if context.get("environment") != "DEMO":
        blockers.append("context_environment_must_be_demo")
    if context.get("demo_only") is not True:
        blockers.append("context_demo_only_required")
    if context.get("windows_vault_only") is not True:
        blockers.append("context_windows_vault_only_required")
    if context.get("live_mode") is True:
        blockers.append("context_live_mode_must_be_false")
    if context.get("live_credentials_allowed") is True:
        blockers.append("context_live_credentials_allowed_must_be_false")
    if _text(context.get("live_api_base_url")):
        blockers.append("context_live_api_base_url_must_be_absent")
    if not _text(context.get("demo_api_base_url")).startswith(DEMO_API_BASE_URL_PREFIX):
        blockers.append("context_demo_api_base_url_must_be_practice")

    required_true = (
        "read_only_preflight_only",
        "no_env_file",
        "no_repo_persistence",
        "no_live_credentials",
        "token_visible_account_required",
        "no_order_endpoint",
        "no_trade_mutation",
        "no_second_order_attempt",
    )
    for field in required_true:
        if context.get(field) is not True:
            blockers.append(f"context_{field}_required")
    blockers.extend(_authority_blockers(context, "preflight_from_vault_context"))
    return _unique(blockers)


def _endpoint_plan_from_context(
    context: Mapping[str, Any],
    *,
    endpoint_plan_override: Sequence[Mapping[str, Any] | str] | None,
) -> dict[str, Any]:
    if endpoint_plan_override is not None:
        endpoints = [_normalize_endpoint(endpoint) for endpoint in endpoint_plan_override]
    else:
        base_url = _text(context.get("demo_api_base_url"), DEMO_API_BASE_URL_PREFIX)
        endpoints = [
            {"name": "accounts", "method": "GET", "url": f"{base_url}/v3/accounts"},
            {
                "name": "account_details",
                "method": "GET",
                "url": f"{base_url}/v3/accounts/{REDACTED_ACCOUNT_ID_REFERENCE}",
            },
            {
                "name": "account_summary",
                "method": "GET",
                "url": (
                    f"{base_url}/v3/accounts/"
                    f"{REDACTED_ACCOUNT_ID_REFERENCE}/summary"
                ),
            },
            {
                "name": "account_instruments",
                "method": "GET",
                "url": (
                    f"{base_url}/v3/accounts/"
                    f"{REDACTED_ACCOUNT_ID_REFERENCE}/instruments"
                ),
            },
        ]
    return {
        "endpoints": endpoints,
        "allowed_endpoint_templates": _allowed_endpoint_templates(),
        "forbidden_endpoint_terms": list(FORBIDDEN_ENDPOINT_TERMS),
        "read_only_only": True,
        "mutation_endpoints_allowed": False,
    }


def _normalize_endpoint(endpoint: Mapping[str, Any] | str) -> dict[str, Any]:
    if isinstance(endpoint, str):
        return {"name": "override_endpoint", "method": "GET", "url": endpoint}
    mapping = endpoint if isinstance(endpoint, Mapping) else {}
    return {
        "name": _text(mapping.get("name"), "override_endpoint"),
        "method": _text(mapping.get("method"), "GET"),
        "url": _text(mapping.get("url")),
    }


def _endpoint_plan_blockers(endpoint_plan: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for endpoint in endpoint_plan.get("endpoints", []):
        endpoint_mapping = endpoint if isinstance(endpoint, Mapping) else {}
        method = _text(endpoint_mapping.get("method"), "GET")
        url = _text(endpoint_mapping.get("url"))
        for blocker in validate_oanda_demo_vault_preflight_endpoint_url_v1(
            url,
            method=method,
        ):
            blockers.append(f"unsafe_endpoint_{blocker}")
    return _unique(blockers)


def _account_permission_preflight_context() -> dict[str, Any]:
    return {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "demo_endpoint_only": True,
        "live_endpoint_absent": True,
        "demo_api_base_url": DEMO_API_BASE_URL_PREFIX,
        "live_api_base_url": "",
        "live_api_base_url_allowed": False,
        "runtime_token_external": True,
        "runtime_account_id_external": True,
        "credential_persistence_detected": False,
        "account_id_persistence_detected": False,
        "no_order_endpoint_allowed": True,
        "order_mutation_forbidden": True,
        "read_only_only": True,
        "owner_present_for_manual_run": True,
        "prior_403_evidence_captured": True,
        "prior_order_placement_performed": False,
        "prior_order_attempt_count": 1,
        "no_second_order_attempt_allowed": True,
        "execution_authority": _execution_authority(),
    }


def _preflight_context_summary(context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker": _text(context.get("broker"), "MISSING"),
        "environment": _text(context.get("environment"), "MISSING"),
        "demo_only": context.get("demo_only") is True,
        "windows_vault_only": context.get("windows_vault_only") is True,
        "demo_api_base_url_is_practice": _text(
            context.get("demo_api_base_url")
        ).startswith(DEMO_API_BASE_URL_PREFIX),
        "live_api_base_url_present": bool(_text(context.get("live_api_base_url"))),
        "live_credentials_allowed": context.get("live_credentials_allowed") is True,
        "read_only_preflight_only": context.get("read_only_preflight_only") is True,
        "no_env_file": context.get("no_env_file") is True,
        "no_repo_persistence": context.get("no_repo_persistence") is True,
        "no_order_endpoint": context.get("no_order_endpoint") is True,
        "no_trade_mutation": context.get("no_trade_mutation") is True,
        "no_second_order_attempt": context.get("no_second_order_attempt") is True,
    }


def _allowed_endpoint_templates() -> list[str]:
    return [
        "GET https://api-fxpractice.oanda.com/v3/accounts",
        "GET https://api-fxpractice.oanda.com/v3/accounts/<runtime_account_id>",
        (
            "GET https://api-fxpractice.oanda.com/v3/accounts/"
            "<runtime_account_id>/summary"
        ),
        (
            "GET https://api-fxpractice.oanda.com/v3/accounts/"
            "<runtime_account_id>/instruments"
        ),
    ]


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _proof_fields(preflight_decision: Mapping[str, Any] | None) -> dict[str, bool]:
    attempted = False
    if preflight_decision:
        attempt = preflight_decision.get("preflight_attempt")
        if isinstance(attempt, Mapping):
            attempted = attempt.get("network_call_performed") is True
    proof = {field: False for field in PROOF_FIELDS}
    proof["broker_network_call_performed"] = attempted
    return proof


def _warnings(status: str) -> list[str]:
    warnings = [
        "demo_only",
        "windows_vault_adapter_boundary_only",
        "read_only_oanda_practice_metadata_get_only",
        "no_orders_endpoint",
        "no_trades_positions_or_transactions_endpoint",
        "no_live_endpoint",
        "no_credential_or_account_id_printing",
        "no_credential_or_account_id_repo_persistence",
        "no_dotenv_read",
        "execution_authority_false",
    ]
    if status == VAULT_PREFLIGHT_DRY_RUN_READY:
        warnings.append("dry_run_default_no_vault_or_broker_call")
    if status == VAULT_PREFLIGHT_READ_ONLY_ATTEMPTED:
        warnings.append("owner_confirmed_read_only_get_attempted")
    return warnings


def _next_safe_action(status: str) -> str:
    if status == VAULT_PREFLIGHT_DRY_RUN_READY:
        return "owner_may_review_template_before_manual_vault_backed_preflight"
    if status == VAULT_PREFLIGHT_BLOCKED_MISSING_VAULT_ADAPTER:
        return "provide_windows_vault_load_adapter_callable"
    if status == VAULT_PREFLIGHT_BLOCKED_MISSING_TOKEN:
        return "owner_save_demo_access_token_to_approved_windows_vault_label"
    if status == VAULT_PREFLIGHT_BLOCKED_MISSING_ACCOUNT_ID:
        return "owner_save_token_visible_demo_account_id_to_approved_windows_vault_label"
    if status == VAULT_PREFLIGHT_BLOCKED_LIVE_MODE:
        return "repair_context_to_demo_practice_only_before_any_broker_preflight"
    if status == VAULT_PREFLIGHT_BLOCKED_UNSAFE_ENDPOINT:
        return "remove_live_or_mutation_endpoint_before_read_only_preflight"
    if status == VAULT_PREFLIGHT_READ_ONLY_ATTEMPTED:
        return "owner_review_redacted_preflight_result_before_any_next_trade_packet"
    return "stop_and_review_preflight_from_vault_status"


def _authority_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            authority = node.get("execution_authority")
            authority_mapping = authority if isinstance(authority, Mapping) else {}
            for field in EXECUTION_AUTHORITY_FIELDS:
                if node.get(field) is True or authority_mapping.get(field) is True:
                    blockers.append(f"unsafe_{label}_{field}_true")
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(payload)
    return _unique(blockers)


def _sanitize_value(
    value: Any,
    *,
    runtime_access_token: str | None,
    runtime_account_id: str | None,
) -> Any:
    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        for key, child in value.items():
            key_text = str(key)
            if key_text in {"credential_name", "credential_names"}:
                sanitized[key_text] = child
            elif _sensitive_key(key_text) and isinstance(child, str):
                sanitized[key_text] = REDACTED_RUNTIME_ONLY_REFERENCE
            elif key_text == "id" and child == runtime_account_id:
                sanitized[key_text] = REDACTED_ACCOUNT_ID_REFERENCE
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
    if key_text in {"credential_name", "credential_names"}:
        return False
    return key_text in SENSITIVE_KEY_EXACT or any(
        term in key_text for term in SENSITIVE_KEY_TERMS
    )


def _blocker_label(value: str) -> str:
    return (
        value.replace("https://", "")
        .strip("/")
        .replace("/", "_")
        .replace(".", "_")
        .replace("-", "_")
    )


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _present(value: Any) -> bool:
    return bool(value.strip()) if isinstance(value, str) else value is not None


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
