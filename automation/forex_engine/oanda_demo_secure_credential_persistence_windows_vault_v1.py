from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-SECURE-CREDENTIAL-PERSISTENCE-WINDOWS-VAULT-V1"
PERSISTENCE_VERSION = "v1"

VAULT_TEMPLATE_ONLY = "VAULT_TEMPLATE_ONLY"
VAULT_DRY_RUN_READY = "VAULT_DRY_RUN_READY"
VAULT_BLOCKED_CONTEXT = "VAULT_BLOCKED_CONTEXT"
VAULT_BLOCKED_DEMO_ONLY_REQUIRED = "VAULT_BLOCKED_DEMO_ONLY_REQUIRED"
VAULT_BLOCKED_SECRET_MISSING = "VAULT_BLOCKED_SECRET_MISSING"
VAULT_BLOCKED_ACCOUNT_MISMATCH = "VAULT_BLOCKED_ACCOUNT_MISMATCH"
VAULT_BLOCKED_CALLABLE_REQUIRED = "VAULT_BLOCKED_CALLABLE_REQUIRED"
VAULT_SAVE_READY = "VAULT_SAVE_READY"
VAULT_SAVED = "VAULT_SAVED"
VAULT_LOAD_READY = "VAULT_LOAD_READY"
VAULT_LOADED_REDACTED = "VAULT_LOADED_REDACTED"
VAULT_STATUS_READY = "VAULT_STATUS_READY"
VAULT_STATUS_REDACTED = "VAULT_STATUS_REDACTED"
VAULT_DELETE_READY = "VAULT_DELETE_READY"
VAULT_DELETED = "VAULT_DELETED"
VAULT_REJECTED = "VAULT_REJECTED"

ACCESS_TOKEN_CREDENTIAL_NAME = "AIOS_OANDA_DEMO_ACCESS_TOKEN"
ACCOUNT_ID_CREDENTIAL_NAME = "AIOS_OANDA_DEMO_ACCOUNT_ID"
TOKEN_VISIBLE_DEMO_ACCOUNT_REFERENCE = "REDACTED_TOKEN_VISIBLE_DEMO_ACCOUNT_ID"
MISMATCHED_DEMO_ACCOUNT_REFERENCE = "REDACTED_MISMATCHED_ACCOUNT_ID"
REDACTED_DEMO_TOKEN_REFERENCE = "REDACTED_OANDA_DEMO_ACCESS_TOKEN"
REDACTED_RUNTIME_ONLY_REFERENCE = "REDACTED_RUNTIME_ONLY_VALUE"

SUPPORTED_ACTIONS = ("template", "dry_run", "save", "load", "status", "delete")

EXECUTION_AUTHORITY_FIELDS = (
    "execution_allowed",
    "demo_order_allowed",
    "live_order_allowed",
    "broker_write_allowed",
    "broker_call_allowed",
    "autonomous_order_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
    "order_mutation_allowed",
    "position_mutation_allowed",
)

CONTEXT_REQUIRED_TRUE_FIELDS = (
    "demo_only",
    "windows_vault_only",
    "read_only_preflight_passed_or_diagnostic_available",
    "credential_persistence_for_demo_only",
    "owner_present_for_manual_save",
)

CONTEXT_REQUIRED_FALSE_FIELDS = (
    "live_credentials_allowed",
    "plaintext_persistence_allowed",
    "env_file_persistence_allowed",
    "repo_persistence_allowed",
    "account_id_repo_persistence_allowed",
    "token_repo_persistence_allowed",
    "credential_printing_allowed",
    "account_id_printing_allowed",
    "order_execution_allowed",
    "broker_call_allowed",
    "orders_endpoint_allowed",
)

DEMO_ONLY_BLOCKER_PREFIXES = (
    "persistence_context_broker_must_be_oanda_demo",
    "persistence_context_environment_must_be_demo",
    "persistence_context_demo_only_required",
    "persistence_context_live_credentials_allowed_must_be_false",
)

SENSITIVE_KEY_TERMS = (
    "account_id",
    "accountid",
    "access_token",
    "authorization",
    "password",
    "secret",
    "api_key",
    "credential",
    "runtime_demo_access_token",
    "runtime_demo_account_id",
)


def evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
    persistence_context: dict | None = None,
    requested_action: str = "dry_run",
    runtime_demo_access_token: str | None = None,
    runtime_demo_account_id: str | None = None,
    vault_save_callable: object | None = None,
    vault_load_callable: object | None = None,
    vault_delete_callable: object | None = None,
    vault_status_callable: object | None = None,
) -> dict:
    action = _normalize_action(requested_action)
    context = _context_or_default(persistence_context)
    context_blockers = _context_blockers(context)
    account_check = _account_check(
        context=context,
        runtime_demo_account_id=runtime_demo_account_id,
    )

    blockers = _unique(context_blockers + account_check["blockers"])
    status = _status(
        action=action,
        context_blockers=context_blockers,
        runtime_demo_access_token=runtime_demo_access_token,
        runtime_demo_account_id=runtime_demo_account_id,
        account_check=account_check,
        vault_save_callable=vault_save_callable,
        vault_load_callable=vault_load_callable,
        vault_delete_callable=vault_delete_callable,
        vault_status_callable=vault_status_callable,
    )

    raw_vault_results: list[dict[str, Any]] = []
    vault_attempt = _vault_attempt_base(action)

    if status == VAULT_SAVED:
        save_payloads = _save_payloads(
            runtime_demo_access_token=runtime_demo_access_token,
            runtime_demo_account_id=runtime_demo_account_id,
        )
        vault_attempt["vault_mutation_requested"] = True
        vault_attempt["vault_save_payload_count"] = len(save_payloads)
        for payload in save_payloads:
            raw_vault_results.append(
                {
                    "operation": "save",
                    "credential_name": payload["credential_name"],
                    "result": vault_save_callable(payload),  # type: ignore[misc]
                }
            )
    elif status == VAULT_LOADED_REDACTED:
        for payload in _credential_reference_payloads():
            raw_vault_results.append(
                {
                    "operation": "load",
                    "credential_name": payload["credential_name"],
                    "result": vault_load_callable(payload),  # type: ignore[misc]
                }
            )
    elif status == VAULT_STATUS_REDACTED:
        for payload in _credential_reference_payloads():
            raw_vault_results.append(
                {
                    "operation": "status",
                    "credential_name": payload["credential_name"],
                    "result": vault_status_callable(payload),  # type: ignore[misc]
                }
            )
    elif status == VAULT_DELETED:
        vault_attempt["vault_mutation_requested"] = True
        for payload in _credential_reference_payloads():
            raw_vault_results.append(
                {
                    "operation": "delete",
                    "credential_name": payload["credential_name"],
                    "result": vault_delete_callable(payload),  # type: ignore[misc]
                }
            )

    return {
        "packet_id": PACKET_ID,
        "persistence_version": PERSISTENCE_VERSION,
        "status": status,
        "blockers": _status_blockers(status, blockers),
        "warnings": _warnings(status),
        "persistence_context_summary": _persistence_context_summary(context),
        "vault_target_summary": _vault_target_summary(),
        "requested_action_summary": _requested_action_summary(action, status),
        "vault_attempt": vault_attempt,
        "sanitized_vault_result": _sanitize_value(
            raw_vault_results,
            runtime_demo_access_token=runtime_demo_access_token,
            runtime_demo_account_id=runtime_demo_account_id,
        )
        if raw_vault_results
        else None,
        "credential_policy": _credential_policy(account_check),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }


def default_oanda_demo_secure_credential_persistence_context_v1() -> dict[str, Any]:
    return {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "demo_only": True,
        "live_credentials_allowed": False,
        "windows_vault_only": True,
        "plaintext_persistence_allowed": False,
        "env_file_persistence_allowed": False,
        "repo_persistence_allowed": False,
        "account_id_repo_persistence_allowed": False,
        "token_repo_persistence_allowed": False,
        "credential_printing_allowed": False,
        "account_id_printing_allowed": False,
        "order_execution_allowed": False,
        "broker_call_allowed": False,
        "orders_endpoint_allowed": False,
        "read_only_preflight_passed_or_diagnostic_available": True,
        "token_visible_account_id": TOKEN_VISIBLE_DEMO_ACCOUNT_REFERENCE,
        "rejected_mismatched_account_id": MISMATCHED_DEMO_ACCOUNT_REFERENCE,
        "credential_persistence_for_demo_only": True,
        "owner_present_for_manual_save": True,
        "execution_authority": _execution_authority(),
    }


def sanitize_oanda_demo_vault_value_v1(
    value: Any,
    *,
    runtime_demo_access_token: str | None = None,
    runtime_demo_account_id: str | None = None,
) -> Any:
    return _sanitize_value(
        value,
        runtime_demo_access_token=runtime_demo_access_token,
        runtime_demo_account_id=runtime_demo_account_id,
    )


def _status(
    *,
    action: str,
    context_blockers: list[str],
    runtime_demo_access_token: str | None,
    runtime_demo_account_id: str | None,
    account_check: Mapping[str, Any],
    vault_save_callable: object | None,
    vault_load_callable: object | None,
    vault_delete_callable: object | None,
    vault_status_callable: object | None,
) -> str:
    if action not in SUPPORTED_ACTIONS:
        return VAULT_REJECTED
    if action == "template":
        return VAULT_TEMPLATE_ONLY
    if _demo_only_blocked(context_blockers):
        return VAULT_BLOCKED_DEMO_ONLY_REQUIRED
    if _context_blocked(context_blockers):
        return VAULT_BLOCKED_CONTEXT
    if action == "dry_run":
        return VAULT_DRY_RUN_READY
    if action == "save":
        if not _present(runtime_demo_access_token) or not _present(
            runtime_demo_account_id
        ):
            return VAULT_BLOCKED_SECRET_MISSING
        if account_check.get("account_mismatch") is True:
            return VAULT_BLOCKED_ACCOUNT_MISMATCH
        if not callable(vault_save_callable):
            return VAULT_BLOCKED_CALLABLE_REQUIRED
        return VAULT_SAVED
    if action == "load":
        if not callable(vault_load_callable):
            return VAULT_BLOCKED_CALLABLE_REQUIRED
        return VAULT_LOADED_REDACTED
    if action == "status":
        if not callable(vault_status_callable):
            return VAULT_BLOCKED_CALLABLE_REQUIRED
        return VAULT_STATUS_REDACTED
    if action == "delete":
        if not callable(vault_delete_callable):
            return VAULT_BLOCKED_CALLABLE_REQUIRED
        return VAULT_DELETED
    return VAULT_REJECTED


def _context_or_default(context: dict | None) -> Mapping[str, Any]:
    if context is None:
        return default_oanda_demo_secure_credential_persistence_context_v1()
    return context if isinstance(context, Mapping) else {}


def _context_blockers(context: Mapping[str, Any]) -> list[str]:
    if not context:
        return ["missing_persistence_context"]

    blockers: list[str] = []
    if context.get("broker") != "OANDA_DEMO":
        blockers.append("persistence_context_broker_must_be_oanda_demo")
    if context.get("environment") != "DEMO":
        blockers.append("persistence_context_environment_must_be_demo")

    for field in CONTEXT_REQUIRED_TRUE_FIELDS:
        if context.get(field) is not True:
            blockers.append(f"persistence_context_{field}_required")
    for field in CONTEXT_REQUIRED_FALSE_FIELDS:
        if context.get(field) is True:
            blockers.append(f"persistence_context_{field}_must_be_false")

    if not _present(context.get("token_visible_account_id")):
        blockers.append("persistence_context_token_visible_account_reference_required")
    if not _present(context.get("rejected_mismatched_account_id")):
        blockers.append("persistence_context_rejected_account_reference_required")

    blockers.extend(_authority_blockers(context, "persistence_context"))
    return _unique(blockers)


def _account_check(
    *,
    context: Mapping[str, Any],
    runtime_demo_account_id: str | None,
) -> dict[str, Any]:
    expected = _text(context.get("token_visible_account_id"))
    rejected = _text(context.get("rejected_mismatched_account_id"))
    supplied = _text(runtime_demo_account_id)

    if not supplied:
        return {
            "account_reference": None,
            "account_mismatch": False,
            "classification": "account_not_supplied",
            "blockers": [],
        }
    if supplied in {MISMATCHED_DEMO_ACCOUNT_REFERENCE, rejected}:
        return {
            "account_reference": MISMATCHED_DEMO_ACCOUNT_REFERENCE,
            "account_mismatch": True,
            "classification": "prior_mismatched_account_rejected",
            "blockers": ["runtime_demo_account_id_rejected_mismatched_account"],
        }
    if expected and expected != TOKEN_VISIBLE_DEMO_ACCOUNT_REFERENCE:
        if supplied != expected:
            return {
                "account_reference": "REDACTED_UNKNOWN_DEMO_ACCOUNT_ID",
                "account_mismatch": True,
                "classification": "runtime_account_does_not_match_context",
                "blockers": ["runtime_demo_account_id_does_not_match_context"],
            }
    elif supplied == TOKEN_VISIBLE_DEMO_ACCOUNT_REFERENCE or _looks_like_demo_account(
        supplied
    ):
        return {
            "account_reference": TOKEN_VISIBLE_DEMO_ACCOUNT_REFERENCE,
            "account_mismatch": False,
            "classification": "token_visible_demo_account_confirmed",
            "blockers": [],
        }
    else:
        return {
            "account_reference": "REDACTED_UNKNOWN_DEMO_ACCOUNT_ID",
            "account_mismatch": True,
            "classification": "runtime_account_not_token_visible_reference",
            "blockers": ["runtime_demo_account_id_not_token_visible_reference"],
        }

    return {
        "account_reference": TOKEN_VISIBLE_DEMO_ACCOUNT_REFERENCE,
        "account_mismatch": False,
        "classification": "token_visible_demo_account_confirmed",
        "blockers": [],
    }


def _looks_like_demo_account(value: str) -> bool:
    parts = value.split("-")
    return (
        len(parts) == 4
        and parts[0] == "101"
        and all(part.isdigit() for part in parts)
        and all(part for part in parts)
    )


def _save_payloads(
    *,
    runtime_demo_access_token: str | None,
    runtime_demo_account_id: str | None,
) -> list[dict[str, str]]:
    return [
        {
            "credential_name": ACCESS_TOKEN_CREDENTIAL_NAME,
            "secret_value": _text(runtime_demo_access_token),
        },
        {
            "credential_name": ACCOUNT_ID_CREDENTIAL_NAME,
            "secret_value": _text(runtime_demo_account_id),
        },
    ]


def _credential_reference_payloads() -> list[dict[str, str]]:
    return [
        {"credential_name": ACCESS_TOKEN_CREDENTIAL_NAME},
        {"credential_name": ACCOUNT_ID_CREDENTIAL_NAME},
    ]


def _persistence_context_summary(context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker": _text(context.get("broker"), "MISSING"),
        "environment": _text(context.get("environment"), "MISSING"),
        "demo_only": context.get("demo_only") is True,
        "live_credentials_allowed": context.get("live_credentials_allowed") is True,
        "windows_vault_only": context.get("windows_vault_only") is True,
        "plaintext_persistence_allowed": context.get(
            "plaintext_persistence_allowed"
        )
        is True,
        "env_file_persistence_allowed": context.get("env_file_persistence_allowed")
        is True,
        "repo_persistence_allowed": context.get("repo_persistence_allowed") is True,
        "credential_printing_allowed": context.get("credential_printing_allowed")
        is True,
        "account_id_printing_allowed": context.get("account_id_printing_allowed")
        is True,
        "order_execution_allowed": context.get("order_execution_allowed") is True,
        "broker_call_allowed": context.get("broker_call_allowed") is True,
        "orders_endpoint_allowed": context.get("orders_endpoint_allowed") is True,
        "read_only_preflight_passed_or_diagnostic_available": context.get(
            "read_only_preflight_passed_or_diagnostic_available"
        )
        is True,
        "token_visible_account_reference": TOKEN_VISIBLE_DEMO_ACCOUNT_REFERENCE
        if _present(context.get("token_visible_account_id"))
        else "MISSING",
        "rejected_mismatched_account_reference": MISMATCHED_DEMO_ACCOUNT_REFERENCE
        if _present(context.get("rejected_mismatched_account_id"))
        else "MISSING",
        "owner_present_for_manual_save": context.get("owner_present_for_manual_save")
        is True,
    }


def _vault_target_summary() -> dict[str, Any]:
    return {
        "vault_class": "windows_os_backed_credential_storage",
        "adapter_boundary": True,
        "credential_names": [
            ACCESS_TOKEN_CREDENTIAL_NAME,
            ACCOUNT_ID_CREDENTIAL_NAME,
        ],
        "accepted_demo_account_reference": TOKEN_VISIBLE_DEMO_ACCOUNT_REFERENCE,
        "rejected_demo_account_reference": MISMATCHED_DEMO_ACCOUNT_REFERENCE,
        "plaintext_file_target": False,
        "repo_target": False,
        "env_file_target": False,
    }


def _requested_action_summary(action: str, status: str) -> dict[str, Any]:
    return {
        "requested_action": action,
        "supported_action": action in SUPPORTED_ACTIONS,
        "status": status,
        "vault_mutation_action": action in {"save", "delete"},
        "broker_call_requested": False,
        "order_execution_requested": False,
        "orders_endpoint_requested": False,
    }


def _vault_attempt_base(action: str) -> dict[str, Any]:
    return {
        "requested_action": action,
        "vault_callable_used": action in {"save", "load", "status", "delete"},
        "vault_mutation_requested": False,
        "broker_network_call_performed": False,
        "broker_call_performed": False,
        "order_placement_performed": False,
        "order_execution_performed": False,
        "orders_endpoint_called": False,
        "trade_mutation_performed": False,
        "position_mutation_performed": False,
        "plaintext_persistence_performed": False,
        "env_file_read_performed": False,
        "env_file_write_performed": False,
        "repo_secret_write_performed": False,
    }


def _credential_policy(account_check: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "demo_credentials_only": True,
        "live_credentials_allowed": False,
        "windows_vault_only": True,
        "plaintext_persistence_allowed": False,
        "env_file_persistence_allowed": False,
        "repo_persistence_allowed": False,
        "credential_printing_allowed": False,
        "account_id_printing_allowed": False,
        "accepted_account_reference": TOKEN_VISIBLE_DEMO_ACCOUNT_REFERENCE,
        "rejected_account_reference": MISMATCHED_DEMO_ACCOUNT_REFERENCE,
        "runtime_account_classification": account_check.get("classification"),
        "runtime_account_reference": account_check.get("account_reference"),
        "order_execution_allowed": False,
        "broker_call_allowed": False,
        "orders_endpoint_allowed": False,
    }


def _status_blockers(status: str, blockers: list[str]) -> list[str]:
    if status in {
        VAULT_TEMPLATE_ONLY,
        VAULT_DRY_RUN_READY,
        VAULT_SAVED,
        VAULT_LOADED_REDACTED,
        VAULT_STATUS_REDACTED,
        VAULT_DELETED,
    }:
        return blockers
    if status == VAULT_BLOCKED_SECRET_MISSING:
        return _unique(blockers + ["runtime_demo_token_and_account_required"])
    if status == VAULT_BLOCKED_CALLABLE_REQUIRED:
        return _unique(blockers + ["windows_vault_callable_required"])
    if status == VAULT_REJECTED:
        return _unique(blockers + ["unsupported_vault_action"])
    return blockers


def _warnings(status: str) -> list[str]:
    warnings = [
        "demo_credentials_only",
        "windows_vault_or_os_backed_adapter_only",
        "adapter_boundary_ready_not_plaintext_storage",
        "no_env_file_secret_source",
        "no_repo_secret_persistence",
        "no_broker_call",
        "orders_endpoint_forbidden",
        "no_order_execution",
        "execution_authority_false",
    ]
    if status == VAULT_DRY_RUN_READY:
        warnings.append("dry_run_only_no_vault_mutation")
    if status == VAULT_SAVED:
        warnings.append("vault_save_callable_invoked_with_runtime_values")
    return warnings


def _next_safe_action(status: str) -> str:
    if status == VAULT_TEMPLATE_ONLY:
        return "owner_review_windows_vault_adapter_template"
    if status == VAULT_DRY_RUN_READY:
        return "owner_may_prepare_manual_demo_vault_save_after_review"
    if status == VAULT_SAVED:
        return "owner_run_read_only_preflight_from_vault_after_verifying_redacted_status"
    if status == VAULT_LOADED_REDACTED:
        return "owner_may_use_loaded_runtime_values_only_for_read_only_preflight"
    if status == VAULT_STATUS_REDACTED:
        return "owner_review_redacted_vault_presence_status"
    if status == VAULT_DELETED:
        return "owner_confirm_demo_vault_credentials_removed"
    if status == VAULT_BLOCKED_ACCOUNT_MISMATCH:
        return "owner_replace_mismatched_account_with_token_visible_demo_account"
    if status == VAULT_BLOCKED_SECRET_MISSING:
        return "owner_supply_demo_token_and_token_visible_demo_account_at_runtime"
    if status == VAULT_BLOCKED_CALLABLE_REQUIRED:
        return "provide_windows_vault_adapter_callable_or_secretmanagement_integration"
    if status == VAULT_BLOCKED_DEMO_ONLY_REQUIRED:
        return "repair_context_to_demo_only_before_any_vault_action"
    return "repair_secure_credential_persistence_context"


def _sanitize_value(
    value: Any,
    *,
    runtime_demo_access_token: str | None,
    runtime_demo_account_id: str | None,
) -> Any:
    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        for key, child in value.items():
            key_text = str(key)
            if key_text == "credential_name":
                sanitized[key_text] = _sanitize_string(
                    _text(child),
                    runtime_demo_access_token=runtime_demo_access_token,
                    runtime_demo_account_id=runtime_demo_account_id,
                )
            elif _sensitive_key(key_text):
                sanitized[key_text] = REDACTED_RUNTIME_ONLY_REFERENCE
            else:
                sanitized[key_text] = _sanitize_value(
                    child,
                    runtime_demo_access_token=runtime_demo_access_token,
                    runtime_demo_account_id=runtime_demo_account_id,
                )
        return sanitized
    if isinstance(value, list):
        return [
            _sanitize_value(
                child,
                runtime_demo_access_token=runtime_demo_access_token,
                runtime_demo_account_id=runtime_demo_account_id,
            )
            for child in value
        ]
    if isinstance(value, str):
        return _sanitize_string(
            value,
            runtime_demo_access_token=runtime_demo_access_token,
            runtime_demo_account_id=runtime_demo_account_id,
        )
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return repr(value)


def _sanitize_string(
    value: str,
    *,
    runtime_demo_access_token: str | None,
    runtime_demo_account_id: str | None,
) -> str:
    redacted = value
    if runtime_demo_access_token:
        redacted = redacted.replace(runtime_demo_access_token, REDACTED_DEMO_TOKEN_REFERENCE)
    if runtime_demo_account_id:
        redacted = redacted.replace(
            runtime_demo_account_id,
            TOKEN_VISIBLE_DEMO_ACCOUNT_REFERENCE,
        )
    redacted = redacted.replace(
        MISMATCHED_DEMO_ACCOUNT_REFERENCE,
        MISMATCHED_DEMO_ACCOUNT_REFERENCE,
    )
    return redacted


def _sensitive_key(key: str) -> bool:
    key_text = key.lower()
    if key_text in {"credential_name", "credential_names"}:
        return False
    return any(term in key_text for term in SENSITIVE_KEY_TERMS)


def _authority_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            authority = _mapping(node.get("execution_authority"))
            for field in EXECUTION_AUTHORITY_FIELDS:
                if node.get(field) is True or authority.get(field) is True:
                    blockers.append(f"unsafe_{label}_{field}_true")
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(payload)
    return _unique(blockers)


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _normalize_action(action: str) -> str:
    return action.strip().lower() if isinstance(action, str) else ""


def _demo_only_blocked(blockers: list[str]) -> bool:
    return any(blocker in DEMO_ONLY_BLOCKER_PREFIXES for blocker in blockers)


def _context_blocked(blockers: list[str]) -> bool:
    return bool(blockers)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


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
