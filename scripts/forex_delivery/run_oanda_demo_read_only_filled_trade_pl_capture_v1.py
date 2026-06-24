from __future__ import annotations

import argparse
import ctypes
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_read_only_filled_trade_pl_capture_v1 import (  # noqa: E402
    ACCESS_TOKEN_CREDENTIAL_NAME,
    ACCOUNT_ID_CREDENTIAL_NAME,
    APPROVED_VAULT_CREDENTIAL_NAMES,
    BLOCKED_BY_READ_ONLY_PL_CAPTURE_FAILURE,
    DEFAULT_CLIENT_ORDER_ID,
    DEFAULT_INSTRUMENT,
    DEFAULT_ORDER_CREATE_TRANSACTION_ID,
    DEFAULT_ORDER_FILL_TRANSACTION_ID,
    DEFAULT_RELATED_TRANSACTION_IDS,
    FILLED_TRADE_PL_NEGATIVE,
    FILLED_TRADE_PL_NOT_FOUND,
    FILLED_TRADE_PL_OPEN_UNREALIZED,
    FILLED_TRADE_PL_POSITIVE,
    FILLED_TRADE_PL_ZERO,
    PRACTICE_API_BASE_URL,
    READ_ONLY_FILLED_TRADE_PL_CAPTURE_READY,
    default_oanda_demo_read_only_filled_trade_pl_capture_context_v1,
    evaluate_oanda_demo_read_only_filled_trade_pl_capture_v1,
    validate_oanda_demo_read_only_filled_trade_pl_capture_endpoint_url_v1,
)


REQUIRED_EXECUTE_CONFIRMATIONS = {
    "i_confirm_demo_only": "--i-confirm-demo-only",
    "i_confirm_read_only_pl_capture": "--i-confirm-read-only-pl-capture",
    "i_confirm_windows_vault_only": "--i-confirm-windows-vault-only",
    "i_confirm_no_env_file": "--i-confirm-no-env-file",
    "i_confirm_no_repo_persistence": "--i-confirm-no-repo-persistence",
    "i_confirm_no_live_endpoint": "--i-confirm-no-live-endpoint",
    "i_confirm_no_order": "--i-confirm-no-order",
    "i_confirm_no_close_trade": "--i-confirm-no-close-trade",
    "i_confirm_no_mutation": "--i-confirm-no-mutation",
    "i_confirm_no_second_order": "--i-confirm-no-second-order",
    "i_confirm_no_profit_claim": "--i-confirm-no-profit-claim",
}

SUCCESS_CLASSIFICATIONS = {
    FILLED_TRADE_PL_POSITIVE,
    FILLED_TRADE_PL_NEGATIVE,
    FILLED_TRADE_PL_ZERO,
    FILLED_TRADE_PL_OPEN_UNREALIZED,
    FILLED_TRADE_PL_NOT_FOUND,
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

    transaction_ids = [str(value) for value in args.related_transaction_ids]
    if not args.execute_read_only_filled_trade_pl_capture_from_vault:
        decision = evaluate_oanda_demo_read_only_filled_trade_pl_capture_v1(
            default_oanda_demo_read_only_filled_trade_pl_capture_context_v1(),
            related_transaction_ids=transaction_ids,
            order_create_transaction_id=args.order_create_transaction_id,
            order_fill_transaction_id=args.order_fill_transaction_id,
            instrument=args.instrument,
            client_order_id=args.client_order_id,
        )
        _print_json(_script_payload(decision, dry_run=True))
        return 0

    missing = _missing_confirmations(args)
    if missing:
        decision = evaluate_oanda_demo_read_only_filled_trade_pl_capture_v1(
            default_oanda_demo_read_only_filled_trade_pl_capture_context_v1(),
            related_transaction_ids=transaction_ids,
            order_create_transaction_id=args.order_create_transaction_id,
            order_fill_transaction_id=args.order_fill_transaction_id,
            instrument=args.instrument,
            client_order_id=args.client_order_id,
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
    transport = http_get_callable or get_oanda_demo_read_only_with_urllib_v1
    decision = evaluate_oanda_demo_read_only_filled_trade_pl_capture_v1(
        default_oanda_demo_read_only_filled_trade_pl_capture_context_v1(),
        vault_load_callable=loader,
        http_get_callable=transport,
        execute_capture=True,
        related_transaction_ids=transaction_ids,
        order_create_transaction_id=args.order_create_transaction_id,
        order_fill_transaction_id=args.order_fill_transaction_id,
        instrument=args.instrument,
        client_order_id=args.client_order_id,
    )
    _print_json(_script_payload(decision, dry_run=False))
    classification = decision.get("pl_capture_classification")
    return 0 if classification in SUCCESS_CLASSIFICATIONS else 1


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


def get_oanda_demo_read_only_with_urllib_v1(
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    method = str(payload.get("method", "GET")).upper()
    url = str(payload.get("url", ""))
    token = str(payload.get("runtime_access_token", ""))
    endpoint_blockers = validate_oanda_demo_read_only_filled_trade_pl_capture_endpoint_url_v1(
        url,
        method=method,
    )
    if endpoint_blockers:
        return {
            "status_code": None,
            "blocked": True,
            "blockers": endpoint_blockers,
        }
    request = Request(
        url,
        method="GET",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=20) as response:  # noqa: S310
            body = response.read().decode("utf-8", errors="replace")
            return {
                "status_code": int(response.status),
                "body": body,
                "json": _json_or_empty(body),
            }
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {
            "status_code": int(exc.code),
            "body": body,
            "json": _json_or_empty(body),
        }
    except URLError as exc:
        return {
            "status_code": None,
            "error_type": type(exc.reason).__name__,
            "error": "read_only_oanda_get_failed",
        }


def _parser() -> argparse.ArgumentParser:
    parser = SanitizedArgumentParser(
        allow_abbrev=False,
        description=(
            "AIOS OANDA demo read-only filled-trade P/L capture from Windows vault."
        ),
    )
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument(
        "--execute-read-only-filled-trade-pl-capture-from-vault",
        action="store_true",
    )
    parser.add_argument("--instrument", default=DEFAULT_INSTRUMENT)
    parser.add_argument(
        "--order-create-transaction-id",
        default=DEFAULT_ORDER_CREATE_TRANSACTION_ID,
    )
    parser.add_argument(
        "--order-fill-transaction-id",
        default=DEFAULT_ORDER_FILL_TRANSACTION_ID,
    )
    parser.add_argument(
        "--related-transaction-ids",
        nargs="+",
        default=list(DEFAULT_RELATED_TRANSACTION_IDS),
    )
    parser.add_argument("--client-order-id", default=DEFAULT_CLIENT_ORDER_ID)
    parser.add_argument("--i-confirm-demo-only", action="store_true")
    parser.add_argument("--i-confirm-read-only-pl-capture", action="store_true")
    parser.add_argument("--i-confirm-windows-vault-only", action="store_true")
    parser.add_argument("--i-confirm-no-env-file", action="store_true")
    parser.add_argument("--i-confirm-no-repo-persistence", action="store_true")
    parser.add_argument("--i-confirm-no-live-endpoint", action="store_true")
    parser.add_argument("--i-confirm-no-order", action="store_true")
    parser.add_argument("--i-confirm-no-close-trade", action="store_true")
    parser.add_argument("--i-confirm-no-mutation", action="store_true")
    parser.add_argument("--i-confirm-no-second-order", action="store_true")
    parser.add_argument("--i-confirm-no-profit-claim", action="store_true")
    return parser


class SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        _print_json(
            {
                "script_status": "BLOCKED_INVALID_ARGUMENTS",
                "argument_error": "unsupported_or_invalid_argument",
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "order_close_performed": False,
                "order_mutation_performed": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "credential_value_printed": False,
                "account_id_value_printed": False,
                "dotenv_read": False,
                "live_endpoint_used": False,
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
    command_template = [
        "python",
        "scripts/forex_delivery/run_oanda_demo_read_only_filled_trade_pl_capture_v1.py",
        "--execute-read-only-filled-trade-pl-capture-from-vault",
        "--instrument",
        DEFAULT_INSTRUMENT,
        "--order-create-transaction-id",
        DEFAULT_ORDER_CREATE_TRANSACTION_ID,
        "--order-fill-transaction-id",
        DEFAULT_ORDER_FILL_TRANSACTION_ID,
        "--related-transaction-ids",
        *DEFAULT_RELATED_TRANSACTION_IDS,
        "--client-order-id",
        DEFAULT_CLIENT_ORDER_ID,
        *REQUIRED_EXECUTE_CONFIRMATIONS.values(),
    ]
    return {
        "script_status": "READ_ONLY_FILLED_TRADE_PL_CAPTURE_TEMPLATE_ONLY",
        "dry_run": True,
        "broker_network_call_performed": False,
        "order_placement_performed": False,
        "order_close_performed": False,
        "order_mutation_performed": False,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "credential_value_printed": False,
        "account_id_value_printed": False,
        "dotenv_read": False,
        "env_read": False,
        "live_endpoint_used": False,
        "windows_vault_only": True,
        "credential_names": [
            ACCESS_TOKEN_CREDENTIAL_NAME,
            ACCOUNT_ID_CREDENTIAL_NAME,
        ],
        "allowed_endpoints": [
            f"GET {PRACTICE_API_BASE_URL}/v3/accounts",
            f"GET {PRACTICE_API_BASE_URL}/v3/accounts/<runtime_account_id>",
            f"GET {PRACTICE_API_BASE_URL}/v3/accounts/<runtime_account_id>/summary",
            f"GET {PRACTICE_API_BASE_URL}/v3/accounts/<runtime_account_id>/openTrades",
            (
                f"GET {PRACTICE_API_BASE_URL}/v3/accounts/"
                "<runtime_account_id>/openPositions"
            ),
            (
                f"GET {PRACTICE_API_BASE_URL}/v3/accounts/"
                "<runtime_account_id>/transactions"
            ),
        ],
        "pl_classifications": [
            FILLED_TRADE_PL_POSITIVE,
            FILLED_TRADE_PL_NEGATIVE,
            FILLED_TRADE_PL_ZERO,
            FILLED_TRADE_PL_OPEN_UNREALIZED,
            FILLED_TRADE_PL_NOT_FOUND,
            BLOCKED_BY_READ_ONLY_PL_CAPTURE_FAILURE,
        ],
        "runtime_input_rule": {
            "command_line_token_argument_supported": False,
            "command_line_account_id_argument_supported": False,
            "env_file_supported": False,
            "repo_secret_supported": False,
            "windows_vault_adapter_required": True,
        },
        "required_confirmations": list(REQUIRED_EXECUTE_CONFIRMATIONS.values()),
        "owner_command_template": " ".join(command_template),
    }


def _script_payload(decision: Mapping[str, Any], *, dry_run: bool) -> dict[str, Any]:
    return {
        "script_status": decision.get(
            "status",
            READ_ONLY_FILLED_TRADE_PL_CAPTURE_READY,
        ),
        "dry_run": dry_run,
        "pl_capture_classification": decision.get("pl_capture_classification"),
        "broker_network_call_performed": decision.get(
            "broker_network_call_performed",
            False,
        ),
        "order_placement_performed": False,
        "order_close_performed": False,
        "order_mutation_performed": False,
        "credential_read_performed": decision.get("credential_read_performed", False),
        "account_id_read_performed": decision.get("account_id_read_performed", False),
        "credential_value_printed": False,
        "account_id_value_printed": False,
        "dotenv_read": False,
        "env_read": False,
        "live_endpoint_used": False,
        "profit_claimed": False,
        "decision": decision,
    }


def _json_or_empty(body: str) -> Any:
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {}


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
