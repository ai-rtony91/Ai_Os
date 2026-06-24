from __future__ import annotations

import argparse
import ctypes
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_credential_account_permission_preflight_no_order_v1 import (  # noqa: E402
    get_oanda_demo_read_only_with_urllib,
)
from automation.forex_engine.oanda_demo_read_only_preflight_from_vault_v1 import (  # noqa: E402
    ACCESS_TOKEN_CREDENTIAL_NAME,
    ACCOUNT_ID_CREDENTIAL_NAME,
    APPROVED_VAULT_CREDENTIAL_NAMES,
    VAULT_PREFLIGHT_DRY_RUN_READY,
    VAULT_PREFLIGHT_READ_ONLY_ATTEMPTED,
    default_oanda_demo_read_only_preflight_from_vault_context_v1,
    evaluate_oanda_demo_read_only_preflight_from_vault_v1,
)


REQUIRED_EXECUTE_CONFIRMATIONS = {
    "i_confirm_demo_only": "--i-confirm-demo-only",
    "i_confirm_read_only_preflight": "--i-confirm-read-only-preflight",
    "i_confirm_windows_vault_only": "--i-confirm-windows-vault-only",
    "i_confirm_no_env_file": "--i-confirm-no-env-file",
    "i_confirm_no_repo_persistence": "--i-confirm-no-repo-persistence",
    "i_confirm_no_live_credentials": "--i-confirm-no-live-credentials",
    "i_confirm_token_visible_account": "--i-confirm-token-visible-account",
    "i_confirm_no_order_endpoint": "--i-confirm-no-order-endpoint",
    "i_confirm_no_trade_mutation": "--i-confirm-no-trade-mutation",
    "i_confirm_no_second_order_attempt": "--i-confirm-no-second-order-attempt",
}


def main(
    argv: Sequence[str] | None = None,
    *,
    vault_load_callable: object | None = None,
    http_get_callable: object | None = None,
) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_template:
        _print_json(_template_payload())
        return 0

    if not args.execute_read_only_preflight_from_vault:
        decision = evaluate_oanda_demo_read_only_preflight_from_vault_v1(
            preflight_context=default_oanda_demo_read_only_preflight_from_vault_context_v1(),
        )
        _print_json(_script_payload(decision, dry_run=True))
        return 0

    missing = _missing_confirmations(args)
    if missing:
        decision = evaluate_oanda_demo_read_only_preflight_from_vault_v1(
            preflight_context=default_oanda_demo_read_only_preflight_from_vault_context_v1(),
        )
        payload = _script_payload(decision, dry_run=False)
        payload.update(
            {
                "script_status": "BLOCKED_MISSING_REQUIRED_CONFIRMATIONS",
                "missing_confirmations": missing,
            }
        )
        _print_json(payload)
        return 1

    loader = vault_load_callable or load_from_windows_credential_manager_v1
    transport = http_get_callable or get_oanda_demo_read_only_with_urllib
    decision = evaluate_oanda_demo_read_only_preflight_from_vault_v1(
        preflight_context=default_oanda_demo_read_only_preflight_from_vault_context_v1(),
        vault_load_callable=loader,
        http_get_callable=transport,
        execute_preflight=True,
    )
    _print_json(_script_payload(decision, dry_run=False))
    return 0 if decision["status"] == VAULT_PREFLIGHT_READ_ONLY_ATTEMPTED else 1


def load_from_windows_credential_manager_v1(
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    credential_name = str(payload.get("credential_name", ""))
    if credential_name not in APPROVED_VAULT_CREDENTIAL_NAMES:
        return {
            "credential_name": credential_name,
            "load_status": "blocked_unapproved_credential_name",
            "secret_value": "",
        }
    if sys.platform != "win32":
        return {
            "credential_name": credential_name,
            "load_status": "windows_credential_manager_unavailable",
            "secret_value": "",
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

    credential_pointer = ctypes.POINTER(Credential)()
    advapi32 = ctypes.windll.advapi32  # type: ignore[attr-defined]
    cred_type_generic = 1

    loaded = advapi32.CredReadW(
        credential_name,
        cred_type_generic,
        0,
        ctypes.byref(credential_pointer),
    )
    if not loaded:
        return {
            "credential_name": credential_name,
            "load_status": "credential_not_found",
            "secret_value": "",
        }

    try:
        credential = credential_pointer.contents
        raw_secret = ctypes.string_at(
            credential.CredentialBlob,
            credential.CredentialBlobSize,
        )
        try:
            secret_value = raw_secret.decode("utf-16-le").rstrip("\x00")
        except UnicodeDecodeError:
            secret_value = raw_secret.decode("utf-8", errors="replace")
        return {
            "credential_name": credential_name,
            "load_status": "loaded_from_windows_credential_manager",
            "secret_value": secret_value,
        }
    finally:
        advapi32.CredFree(credential_pointer)


def _parser() -> argparse.ArgumentParser:
    parser = SanitizedArgumentParser(
        allow_abbrev=False,
        description=(
            "AIOS OANDA demo read-only preflight from Windows vault boundary."
        ),
    )
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument(
        "--execute-read-only-preflight-from-vault",
        action="store_true",
    )
    parser.add_argument("--i-confirm-demo-only", action="store_true")
    parser.add_argument("--i-confirm-read-only-preflight", action="store_true")
    parser.add_argument("--i-confirm-windows-vault-only", action="store_true")
    parser.add_argument("--i-confirm-no-env-file", action="store_true")
    parser.add_argument("--i-confirm-no-repo-persistence", action="store_true")
    parser.add_argument("--i-confirm-no-live-credentials", action="store_true")
    parser.add_argument("--i-confirm-token-visible-account", action="store_true")
    parser.add_argument("--i-confirm-no-order-endpoint", action="store_true")
    parser.add_argument("--i-confirm-no-trade-mutation", action="store_true")
    parser.add_argument("--i-confirm-no-second-order-attempt", action="store_true")
    return parser


class SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        _print_json(
            {
                "script_status": "BLOCKED_INVALID_ARGUMENTS",
                "argument_error": "unsupported_or_invalid_argument",
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "orders_endpoint_called": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "credential_value_printed": False,
                "account_id_value_printed": False,
                "dotenv_read": False,
            }
        )
        raise SystemExit(2)


def _missing_confirmations(args: argparse.Namespace) -> list[str]:
    return [
        flag
        for attr, flag in REQUIRED_EXECUTE_CONFIRMATIONS.items()
        if not getattr(args, attr)
    ]


def _template_payload() -> dict[str, Any]:
    return {
        "script_status": "VAULT_PREFLIGHT_TEMPLATE_ONLY",
        "dry_run": True,
        "broker_network_call_performed": False,
        "order_placement_performed": False,
        "orders_endpoint_called": False,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "credential_value_printed": False,
        "account_id_value_printed": False,
        "dotenv_read": False,
        "windows_vault_only": True,
        "credential_names": [
            ACCESS_TOKEN_CREDENTIAL_NAME,
            ACCOUNT_ID_CREDENTIAL_NAME,
        ],
        "runtime_input_rule": {
            "command_line_token_argument_supported": False,
            "command_line_account_id_argument_supported": False,
            "env_file_supported": False,
            "repo_secret_supported": False,
            "windows_vault_adapter_required": True,
        },
        "required_confirmations": list(REQUIRED_EXECUTE_CONFIRMATIONS.values()),
        "allowed_endpoints": [
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
        ],
        "forbidden": {
            "orders_endpoint": True,
            "trades_endpoint": True,
            "positions_endpoint": True,
            "transactions_endpoint": True,
            "live_endpoint": True,
            "broker_write": True,
            "order_placement": True,
        },
    }


def _script_payload(decision: Mapping[str, Any], *, dry_run: bool) -> dict[str, Any]:
    vault_boundary = decision.get("vault_load_boundary")
    vault_boundary = vault_boundary if isinstance(vault_boundary, Mapping) else {}
    return {
        "script_status": decision.get("status", VAULT_PREFLIGHT_DRY_RUN_READY),
        "dry_run": dry_run,
        "broker_network_call_performed": decision.get(
            "broker_network_call_performed",
            False,
        ),
        "order_placement_performed": False,
        "orders_endpoint_called": False,
        "credential_read_performed": vault_boundary.get(
            "vault_load_attempted",
            False,
        ),
        "account_id_read_performed": vault_boundary.get("vault_load_attempted", False),
        "credential_value_printed": False,
        "account_id_value_printed": False,
        "dotenv_read": False,
        "decision": decision,
    }


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
