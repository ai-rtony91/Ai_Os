from __future__ import annotations

import ctypes
import sys
from typing import Any, Mapping

from automation.forex_engine.oanda_demo_secure_credential_persistence_windows_vault_v1 import (
    ACCESS_TOKEN_CREDENTIAL_NAME,
    ACCOUNT_ID_CREDENTIAL_NAME,
)


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-OWNER-VAULT-SAVE-HELPER-V1"
HELPER_VERSION = "v1"

OWNER_VAULT_SAVE_TEMPLATE_ONLY = "OWNER_VAULT_SAVE_TEMPLATE_ONLY"
OWNER_VAULT_SAVE_BLOCKED_MISSING_CONFIRMATIONS = (
    "OWNER_VAULT_SAVE_BLOCKED_MISSING_CONFIRMATIONS"
)
OWNER_VAULT_SAVE_BLOCKED_VALUES_MISSING = "OWNER_VAULT_SAVE_BLOCKED_VALUES_MISSING"
OWNER_VAULT_SAVE_BLOCKED_NON_WINDOWS = "OWNER_VAULT_SAVE_BLOCKED_NON_WINDOWS"
OWNER_VAULT_SAVE_BLOCKED_UNAPPROVED_LABEL = (
    "OWNER_VAULT_SAVE_BLOCKED_UNAPPROVED_LABEL"
)
OWNER_VAULT_SAVE_BLOCKED_ADAPTER_ERROR = "OWNER_VAULT_SAVE_BLOCKED_ADAPTER_ERROR"
OWNER_VAULT_SAVE_SAVED = "OWNER_VAULT_SAVE_SAVED"

APPROVED_LABELS = (
    ACCESS_TOKEN_CREDENTIAL_NAME,
    ACCOUNT_ID_CREDENTIAL_NAME,
)

REQUIRED_CONFIRMATION_FLAGS = (
    "--i-confirm-demo-only",
    "--i-confirm-windows-vault-only",
    "--i-confirm-no-env-file",
    "--i-confirm-no-repo-persistence",
    "--i-confirm-no-value-printing",
)

READ_ONLY_PREFLIGHT_RERUN_COMMAND = (
    "python scripts/forex_delivery/"
    "run_oanda_demo_read_only_preflight_from_vault_v1.py "
    "--execute-read-only-preflight-from-vault "
    "--i-confirm-demo-only "
    "--i-confirm-read-only-preflight "
    "--i-confirm-windows-vault-only "
    "--i-confirm-no-env-file "
    "--i-confirm-no-repo-persistence "
    "--i-confirm-no-live-credentials "
    "--i-confirm-token-visible-account "
    "--i-confirm-no-order-endpoint "
    "--i-confirm-no-trade-mutation "
    "--i-confirm-no-second-order-attempt"
)

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


def owner_vault_save_template_v1() -> dict[str, Any]:
    return _payload(
        status=OWNER_VAULT_SAVE_TEMPLATE_ONLY,
        labels_saved=False,
        warnings=["template_only_no_prompt_no_vault_write"],
    )


def blocked_missing_confirmations_v1(missing_confirmations: list[str]) -> dict[str, Any]:
    payload = _payload(
        status=OWNER_VAULT_SAVE_BLOCKED_MISSING_CONFIRMATIONS,
        labels_saved=False,
        warnings=["missing_owner_confirmations_no_prompt_no_vault_write"],
    )
    payload["missing_confirmations"] = list(missing_confirmations)
    return payload


def save_owner_oanda_demo_values_to_windows_vault_v1(
    *,
    runtime_demo_access_token: str,
    runtime_demo_account_id: str,
    vault_save_callable: object | None = None,
    platform_name: str | None = None,
) -> dict[str, Any]:
    if not _present(runtime_demo_access_token) or not _present(runtime_demo_account_id):
        return _payload(
            status=OWNER_VAULT_SAVE_BLOCKED_VALUES_MISSING,
            labels_saved=False,
            warnings=["runtime_values_required_no_vault_write"],
        )

    save_callable = vault_save_callable or save_to_windows_credential_manager_v1
    label_results: list[dict[str, Any]] = []
    for label, value in (
        (ACCESS_TOKEN_CREDENTIAL_NAME, runtime_demo_access_token),
        (ACCOUNT_ID_CREDENTIAL_NAME, runtime_demo_account_id),
    ):
        result = save_callable(
            {
                "credential_name": label,
                "secret_value": value,
                "platform_name": platform_name or sys.platform,
            }
        )
        result_map = result if isinstance(result, Mapping) else {}
        label_results.append(
            {
                "credential_name": label,
                "value_saved": result_map.get("value_saved") is True,
                "status": _safe_status_text(result_map.get("status")),
            }
        )

    labels_saved = all(item["value_saved"] is True for item in label_results)
    if labels_saved:
        return _payload(
            status=OWNER_VAULT_SAVE_SAVED,
            labels_saved=True,
            warnings=["owner_runtime_values_saved_no_values_returned"],
        )

    statuses = {_safe_status_text(item["status"]) for item in label_results}
    if "blocked_non_windows_platform" in statuses:
        status = OWNER_VAULT_SAVE_BLOCKED_NON_WINDOWS
    elif "blocked_unapproved_credential_name" in statuses:
        status = OWNER_VAULT_SAVE_BLOCKED_UNAPPROVED_LABEL
    else:
        status = OWNER_VAULT_SAVE_BLOCKED_ADAPTER_ERROR
    return _payload(
        status=status,
        labels_saved=False,
        warnings=["vault_save_failed_no_values_returned"],
    )


def save_to_windows_credential_manager_v1(payload: Mapping[str, Any]) -> dict[str, Any]:
    credential_name = _text(payload.get("credential_name"))
    if credential_name not in APPROVED_LABELS:
        return {
            "credential_name": credential_name,
            "value_saved": False,
            "status": "blocked_unapproved_credential_name",
        }
    if _text(payload.get("platform_name"), sys.platform) != "win32":
        return {
            "credential_name": credential_name,
            "value_saved": False,
            "status": "blocked_non_windows_platform",
        }

    secret_value = _text(payload.get("secret_value"))
    if not secret_value:
        return {
            "credential_name": credential_name,
            "value_saved": False,
            "status": "blocked_missing_runtime_value",
        }

    class Credential(ctypes.Structure):
        _fields_ = [
            ("Flags", ctypes.c_uint32),
            ("Type", ctypes.c_uint32),
            ("TargetName", ctypes.c_wchar_p),
            ("Comment", ctypes.c_wchar_p),
            ("LastWritten", ctypes.c_uint64),
            ("CredentialBlobSize", ctypes.c_uint32),
            ("CredentialBlob", ctypes.c_void_p),
            ("Persist", ctypes.c_uint32),
            ("AttributeCount", ctypes.c_uint32),
            ("Attributes", ctypes.c_void_p),
            ("TargetAlias", ctypes.c_wchar_p),
            ("UserName", ctypes.c_wchar_p),
        ]

    secret_bytes = secret_value.encode("utf-16-le")
    secret_buffer = ctypes.create_string_buffer(secret_bytes)
    credential = Credential()
    credential.Flags = 0
    credential.Type = 1
    credential.TargetName = credential_name
    credential.Comment = "AIOS owner runtime-only OANDA demo credential"
    credential.LastWritten = 0
    credential.CredentialBlobSize = len(secret_bytes)
    credential.CredentialBlob = ctypes.cast(secret_buffer, ctypes.c_void_p)
    credential.Persist = 2
    credential.AttributeCount = 0
    credential.Attributes = None
    credential.TargetAlias = None
    credential.UserName = "AIOS_OWNER_RUNTIME_ONLY"

    advapi32 = ctypes.windll.advapi32  # type: ignore[attr-defined]
    advapi32.CredWriteW.argtypes = [ctypes.POINTER(Credential), ctypes.c_uint32]
    advapi32.CredWriteW.restype = ctypes.c_bool
    saved = bool(advapi32.CredWriteW(ctypes.byref(credential), 0))
    return {
        "credential_name": credential_name,
        "value_saved": saved,
        "status": "saved_to_windows_credential_manager"
        if saved
        else "windows_credential_write_failed",
    }


def _payload(
    *,
    status: str,
    labels_saved: bool,
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "packet_id": PACKET_ID,
        "helper_version": HELPER_VERSION,
        "script_status": status,
        "labels_saved": labels_saved,
        "approved_labels": list(APPROVED_LABELS),
        "required_confirmations": list(REQUIRED_CONFIRMATION_FLAGS),
        "runtime_input_rule": {
            "interactive_hidden_prompt_required": True,
            "command_line_value_arguments_supported": False,
            "env_file_supported": False,
            "environment_variable_supported": False,
            "repo_secret_supported": False,
        },
        "safety": {
            "demo_only": True,
            "windows_vault_only": True,
            "broker_call_performed": False,
            "order_placement_performed": False,
            "orders_endpoint_called": False,
            "dotenv_read": False,
            "environment_variable_read": False,
            "windows_vault_read_performed": False,
            "credential_value_printed": False,
            "account_id_value_printed": False,
            "repo_persistence_performed": False,
            "scheduler_created": False,
            "daemon_created": False,
            "webhook_created": False,
        },
        "execution_authority": _execution_authority(),
        "warnings": warnings,
        "read_only_preflight_rerun_command": READ_ONLY_PREFLIGHT_RERUN_COMMAND,
        "next_safe_action": _next_safe_action(status),
    }


def _next_safe_action(status: str) -> str:
    if status == OWNER_VAULT_SAVE_TEMPLATE_ONLY:
        return "owner_review_template_before_hidden_prompt_save"
    if status == OWNER_VAULT_SAVE_SAVED:
        return "owner_run_existing_read_only_preflight_command"
    if status == OWNER_VAULT_SAVE_BLOCKED_MISSING_CONFIRMATIONS:
        return "rerun_with_all_owner_confirmations"
    if status == OWNER_VAULT_SAVE_BLOCKED_VALUES_MISSING:
        return "rerun_and_enter_both_runtime_values_at_hidden_prompts"
    if status == OWNER_VAULT_SAVE_BLOCKED_NON_WINDOWS:
        return "run_owner_save_helper_on_windows_only"
    return "stop_and_review_sanitized_vault_save_status"


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _safe_status_text(value: Any) -> str:
    text = _text(value)
    allowed = {
        "saved_to_windows_credential_manager",
        "blocked_unapproved_credential_name",
        "blocked_non_windows_platform",
        "blocked_missing_runtime_value",
        "windows_credential_write_failed",
        "fake_saved",
        "",
    }
    return text if text in allowed else "adapter_status_redacted"


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _present(value: Any) -> bool:
    return bool(value.strip()) if isinstance(value, str) else value is not None
