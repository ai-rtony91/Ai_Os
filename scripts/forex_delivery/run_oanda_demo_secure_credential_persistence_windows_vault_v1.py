from __future__ import annotations

import argparse
import getpass
import json
from pathlib import Path
import sys
from typing import Callable, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_secure_credential_persistence_windows_vault_v1 import (  # noqa: E402
    ACCOUNT_ID_CREDENTIAL_NAME,
    ACCESS_TOKEN_CREDENTIAL_NAME,
    MISMATCHED_DEMO_ACCOUNT_REFERENCE,
    TOKEN_VISIBLE_DEMO_ACCOUNT_REFERENCE,
    VAULT_BLOCKED_CALLABLE_REQUIRED,
    VAULT_BLOCKED_SECRET_MISSING,
    VAULT_DELETED,
    VAULT_DRY_RUN_READY,
    VAULT_LOADED_REDACTED,
    VAULT_SAVED,
    VAULT_STATUS_REDACTED,
    VAULT_TEMPLATE_ONLY,
    default_oanda_demo_secure_credential_persistence_context_v1,
    evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1,
)


SAVE_CONFIRMATIONS = {
    "i_confirm_demo_only": "--i-confirm-demo-only",
    "i_confirm_windows_vault_only": "--i-confirm-windows-vault-only",
    "i_confirm_no_env_file": "--i-confirm-no-env-file",
    "i_confirm_no_repo_persistence": "--i-confirm-no-repo-persistence",
    "i_confirm_no_live_credentials": "--i-confirm-no-live-credentials",
    "i_confirm_token_visible_account": "--i-confirm-token-visible-account",
    "i_confirm_no_order_execution": "--i-confirm-no-order-execution",
}

DELETE_CONFIRMATIONS = {
    "i_confirm_delete_demo_vault_credentials": (
        "--i-confirm-delete-demo-vault-credentials"
    ),
    "i_confirm_no_order_execution": "--i-confirm-no-order-execution",
}

SUCCESS_STATUSES = {
    VAULT_TEMPLATE_ONLY,
    VAULT_DRY_RUN_READY,
    VAULT_SAVED,
    VAULT_LOADED_REDACTED,
    VAULT_STATUS_REDACTED,
    VAULT_DELETED,
}


def main(
    argv: Sequence[str] | None = None,
    *,
    vault_save_callable: object | None = None,
    vault_load_callable: object | None = None,
    vault_delete_callable: object | None = None,
    vault_status_callable: object | None = None,
    token_prompt_callable: Callable[[str], str] | None = None,
    account_prompt_callable: Callable[[str], str] | None = None,
) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_template:
        _print_json(_template_payload())
        return 0

    action = _selected_action(args)
    context = _ready_persistence_context(live_mode=args.live)

    if action == "save":
        missing = _missing_confirmations(args, SAVE_CONFIRMATIONS)
        if missing:
            return _print_blocked_confirmations(missing, action)
        token = _read_token(token_prompt_callable)
        account_id = args.demo_account_id or _read_account_id(account_prompt_callable)
        decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
            persistence_context=context,
            requested_action="save",
            runtime_demo_access_token=token,
            runtime_demo_account_id=account_id,
            vault_save_callable=vault_save_callable,
        )
        return _emit_decision(decision)

    if action == "delete":
        missing = _missing_confirmations(args, DELETE_CONFIRMATIONS)
        if missing:
            return _print_blocked_confirmations(missing, action)
        decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
            persistence_context=context,
            requested_action="delete",
            vault_delete_callable=vault_delete_callable,
        )
        return _emit_decision(decision)

    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        persistence_context=context,
        requested_action=action,
        vault_load_callable=vault_load_callable,
        vault_status_callable=vault_status_callable,
    )
    return _emit_decision(decision)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "AIOS OANDA demo secure credential persistence Windows vault boundary."
        )
    )
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--load", action="store_true")
    parser.add_argument("--delete", action="store_true")
    parser.add_argument("--live", action="store_true", help="Rejected safety test flag.")
    parser.add_argument(
        "--demo-account-id",
        help="Optional owner-supplied demo account ID for save; output is redacted.",
    )
    parser.add_argument("--i-confirm-demo-only", action="store_true")
    parser.add_argument("--i-confirm-windows-vault-only", action="store_true")
    parser.add_argument("--i-confirm-no-env-file", action="store_true")
    parser.add_argument("--i-confirm-no-repo-persistence", action="store_true")
    parser.add_argument("--i-confirm-no-live-credentials", action="store_true")
    parser.add_argument("--i-confirm-token-visible-account", action="store_true")
    parser.add_argument("--i-confirm-no-order-execution", action="store_true")
    parser.add_argument(
        "--i-confirm-delete-demo-vault-credentials",
        action="store_true",
    )
    return parser


def _selected_action(args: argparse.Namespace) -> str:
    selected = [
        action
        for action in ("save", "load", "status", "delete")
        if getattr(args, action)
    ]
    if len(selected) > 1:
        return "unsupported_multiple_actions"
    if selected:
        return selected[0]
    return "dry_run"


def _ready_persistence_context(*, live_mode: bool) -> dict:
    context = default_oanda_demo_secure_credential_persistence_context_v1()
    if live_mode:
        context.update(
            {
                "broker": "OANDA_LIVE",
                "environment": "LIVE",
                "demo_only": False,
                "live_credentials_allowed": True,
            }
        )
    return context


def _read_token(token_prompt_callable: Callable[[str], str] | None) -> str:
    prompt = "OANDA demo access token (input hidden): "
    if token_prompt_callable is not None:
        return token_prompt_callable(prompt)
    return getpass.getpass(prompt)


def _read_account_id(account_prompt_callable: Callable[[str], str] | None) -> str:
    prompt = "OANDA demo token-visible account ID: "
    if account_prompt_callable is not None:
        return account_prompt_callable(prompt)
    return input(prompt)


def _missing_confirmations(
    args: argparse.Namespace,
    confirmations: dict[str, str],
) -> list[str]:
    return [flag for attr, flag in confirmations.items() if not getattr(args, attr)]


def _print_blocked_confirmations(missing: list[str], action: str) -> int:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        requested_action="dry_run"
    )
    _print_json(
        {
            "script_status": "BLOCKED_MISSING_REQUIRED_CONFIRMATIONS",
            "requested_action": action,
            "missing_confirmations": missing,
            "vault_mutation_performed": False,
            "broker_call_performed": False,
            "order_execution_performed": False,
            "decision": decision,
        }
    )
    return 1


def _emit_decision(decision: dict) -> int:
    _print_json(
        {
            "script_status": decision["status"],
            "vault_mutation_performed": decision["vault_attempt"][
                "vault_mutation_requested"
            ]
            and decision["status"] in {VAULT_SAVED, VAULT_DELETED},
            "broker_call_performed": False,
            "order_execution_performed": False,
            "orders_endpoint_called": False,
            "decision": decision,
        }
    )
    return 0 if decision["status"] in SUCCESS_STATUSES else 1


def _template_payload() -> dict:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        requested_action="template"
    )
    return {
        "script_status": VAULT_TEMPLATE_ONLY,
        "windows_vault_adapter_status": "ADAPTER_BOUNDARY_READY",
        "credential_names": [
            ACCESS_TOKEN_CREDENTIAL_NAME,
            ACCOUNT_ID_CREDENTIAL_NAME,
        ],
        "accepted_demo_account_reference": TOKEN_VISIBLE_DEMO_ACCOUNT_REFERENCE,
        "rejected_demo_account_reference": MISMATCHED_DEMO_ACCOUNT_REFERENCE,
        "runtime_input_rule": {
            "token": "secure_prompt_only",
            "account_id": "prompt_or_validated_owner_arg_redacted_in_output",
            "command_line_token_arg_supported": False,
            "env_file_supported": False,
            "repo_secret_supported": False,
        },
        "operation_support": {
            "dry_run": True,
            "status": "requires_windows_vault_callable_or_next_secretmanagement_packet",
            "save": "requires_owner_confirmations_and_windows_vault_callable",
            "load": "requires_windows_vault_callable_returns_redacted_output",
            "delete": "requires_owner_confirmations_and_windows_vault_callable",
        },
        "safety": {
            "demo_only": True,
            "live_credentials_allowed": False,
            "broker_call_allowed": False,
            "orders_endpoint_allowed": False,
            "order_execution_allowed": False,
        },
        "decision": decision,
    }


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
