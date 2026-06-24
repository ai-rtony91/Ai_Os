from __future__ import annotations

import argparse
import getpass
import json
from pathlib import Path
import sys
from typing import Callable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_owner_vault_save_helper_v1 import (  # noqa: E402
    OWNER_VAULT_SAVE_BLOCKED_MISSING_CONFIRMATIONS,
    REQUIRED_CONFIRMATION_FLAGS,
    blocked_missing_confirmations_v1,
    owner_vault_save_template_v1,
    save_owner_oanda_demo_values_to_windows_vault_v1,
)


CONFIRMATION_ATTRS = {
    "i_confirm_demo_only": "--i-confirm-demo-only",
    "i_confirm_windows_vault_only": "--i-confirm-windows-vault-only",
    "i_confirm_no_env_file": "--i-confirm-no-env-file",
    "i_confirm_no_repo_persistence": "--i-confirm-no-repo-persistence",
    "i_confirm_no_value_printing": "--i-confirm-no-value-printing",
}


def main(
    argv: Sequence[str] | None = None,
    *,
    vault_save_callable: object | None = None,
    token_prompt_callable: Callable[[str], str] | None = None,
    account_prompt_callable: Callable[[str], str] | None = None,
    platform_name: str | None = None,
) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_template:
        _print_json(owner_vault_save_template_v1())
        return 0

    if not args.owner_save_to_windows_vault:
        _print_json(owner_vault_save_template_v1())
        return 0

    missing = _missing_confirmations(args)
    if missing:
        payload = blocked_missing_confirmations_v1(missing)
        _print_json(payload)
        return 1

    runtime_demo_access_token = _hidden_prompt(
        "OANDA demo access token (input hidden): ",
        token_prompt_callable,
    )
    runtime_demo_account_id = _hidden_prompt(
        "OANDA demo account ID (input hidden): ",
        account_prompt_callable,
    )
    payload = save_owner_oanda_demo_values_to_windows_vault_v1(
        runtime_demo_access_token=runtime_demo_access_token,
        runtime_demo_account_id=runtime_demo_account_id,
        vault_save_callable=vault_save_callable,
        platform_name=platform_name,
    )
    _print_json(payload)
    return 0 if payload["labels_saved"] is True else 1


def _parser() -> argparse.ArgumentParser:
    parser = SanitizedArgumentParser(
        allow_abbrev=False,
        description="Owner-run OANDA demo Windows Vault save helper.",
    )
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument("--owner-save-to-windows-vault", action="store_true")
    parser.add_argument("--i-confirm-demo-only", action="store_true")
    parser.add_argument("--i-confirm-windows-vault-only", action="store_true")
    parser.add_argument("--i-confirm-no-env-file", action="store_true")
    parser.add_argument("--i-confirm-no-repo-persistence", action="store_true")
    parser.add_argument("--i-confirm-no-value-printing", action="store_true")
    return parser


class SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        _print_json(
            {
                "script_status": "BLOCKED_INVALID_ARGUMENTS",
                "argument_error": "unsupported_or_invalid_argument",
                "labels_saved": False,
                "broker_call_performed": False,
                "order_placement_performed": False,
                "orders_endpoint_called": False,
                "credential_value_printed": False,
                "account_id_value_printed": False,
                "dotenv_read": False,
                "windows_vault_read_performed": False,
            }
        )
        raise SystemExit(2)


def _missing_confirmations(args: argparse.Namespace) -> list[str]:
    return [
        flag
        for attr, flag in CONFIRMATION_ATTRS.items()
        if not getattr(args, attr)
    ]


def _hidden_prompt(
    prompt: str,
    prompt_callable: Callable[[str], str] | None,
) -> str:
    if prompt_callable is not None:
        return prompt_callable(prompt)
    return getpass.getpass(prompt)


def _print_json(payload: Mapping[str, object]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
