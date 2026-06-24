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

from automation.forex_engine.oanda_demo_runtime_http_transport_one_order_owner_run_v1 import (  # noqa: E402
    post_oanda_demo_order_with_urllib,
)
from automation.forex_engine.oanda_demo_vault_backed_one_order_transport_v1 import (  # noqa: E402
    ACCESS_TOKEN_CREDENTIAL_NAME,
    ACCOUNT_ID_CREDENTIAL_NAME,
    APPROVED_VAULT_CREDENTIAL_NAMES,
    BLOCKED_BY_INVALID_TRADE_INTENT,
    VAULT_BACKED_DEMO_ONE_ORDER_ATTEMPTED,
    default_oanda_demo_vault_backed_one_order_transport_context_v1,
    evaluate_oanda_demo_vault_backed_one_order_transport_v1,
)


REQUIRED_EXECUTE_CONFIRMATIONS = {
    "i_confirm_demo_only": "--i-confirm-demo-only",
    "i_confirm_vault_backed_runtime_only": (
        "--i-confirm-vault-backed-runtime-only"
    ),
    "i_confirm_one_order_only": "--i-confirm-one-order-only",
    "i_confirm_owner_manual_runtime_only": (
        "--i-confirm-owner-manual-runtime-only"
    ),
    "i_confirm_stop_loss": "--i-confirm-stop-loss",
    "i_confirm_take_profit": "--i-confirm-take-profit",
    "i_confirm_no_live_endpoint": "--i-confirm-no-live-endpoint",
    "i_confirm_no_autonomous_order": "--i-confirm-no-autonomous-order",
    "i_confirm_no_second_order": "--i-confirm-no-second-order",
    "i_confirm_post_trade_evidence": "--i-confirm-post-trade-evidence",
    "i_confirm_kill_switch_ready": "--i-confirm-kill-switch-ready",
    "i_understand_loss_possible": "--i-understand-loss-possible",
    "i_understand_no_profit_guarantee": "--i-understand-no-profit-guarantee",
}

REQUIRED_EXECUTE_ORDER_ARGS = (
    "instrument",
    "direction",
    "units",
    "stop_loss",
    "take_profit",
    "risk_amount",
    "client_order_id",
    "order_type",
)


def main(
    argv: Sequence[str] | None = None,
    *,
    vault_load_callable: object | None = None,
    http_post_callable: object | None = None,
) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_template:
        _print_json(_template_payload())
        return 0

    if not args.execute_vault_backed_demo_one_order:
        _print_json(_template_payload())
        return 0

    missing_order_args = [
        field for field in REQUIRED_EXECUTE_ORDER_ARGS if getattr(args, field) is None
    ]
    missing_confirmations = _missing_confirmations(args)
    if missing_order_args or missing_confirmations:
        _print_json(
            {
                "script_status": BLOCKED_BY_INVALID_TRADE_INTENT,
                "missing_order_args": missing_order_args,
                "missing_confirmations": missing_confirmations,
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "order_attempt_count": 0,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "credential_value_printed": False,
                "account_id_value_printed": False,
                "dotenv_read": False,
            }
        )
        return 1

    loader = vault_load_callable or load_from_windows_credential_manager_v1
    transport = http_post_callable or post_oanda_demo_order_with_urllib
    decision = evaluate_oanda_demo_vault_backed_one_order_transport_v1(
        _command_context_from_args(args),
        vault_load_callable=loader,
        http_post_callable=transport,
        execute_transport=True,
    )
    _print_json(_script_payload(decision))
    return 0 if decision["status"] == VAULT_BACKED_DEMO_ONE_ORDER_ATTEMPTED else 1


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
        description="AIOS OANDA demo vault-backed one-order owner transport.",
    )
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument("--execute-vault-backed-demo-one-order", action="store_true")
    parser.add_argument("--instrument")
    parser.add_argument("--direction", choices=("BUY", "SELL"))
    parser.add_argument("--units", type=float)
    parser.add_argument("--stop-loss", dest="stop_loss")
    parser.add_argument("--take-profit", dest="take_profit")
    parser.add_argument("--risk-amount", dest="risk_amount", type=float)
    parser.add_argument("--client-order-id", dest="client_order_id")
    parser.add_argument("--order-type", dest="order_type", choices=("MARKET",))
    for attr, flag in REQUIRED_EXECUTE_CONFIRMATIONS.items():
        parser.add_argument(flag, dest=attr, action="store_true")
    return parser


class SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        _print_json(
            {
                "script_status": "BLOCKED_INVALID_ARGUMENTS",
                "argument_error": "unsupported_or_invalid_argument",
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "order_attempt_count": 0,
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


def _command_context_from_args(args: argparse.Namespace) -> dict[str, Any]:
    context = default_oanda_demo_vault_backed_one_order_transport_context_v1()
    context.update(
        {
            "instrument": args.instrument,
            "direction": args.direction,
            "units": args.units,
            "stop_loss": args.stop_loss,
            "take_profit": args.take_profit,
            "risk_amount": args.risk_amount,
            "client_order_id": args.client_order_id,
            "order_type": args.order_type,
            "demo_only_confirmed": args.i_confirm_demo_only,
            "vault_backed_runtime_only_confirmed": (
                args.i_confirm_vault_backed_runtime_only
            ),
            "one_order_only_confirmed": args.i_confirm_one_order_only,
            "owner_manual_runtime_only_confirmed": (
                args.i_confirm_owner_manual_runtime_only
            ),
            "stop_loss_confirmed": args.i_confirm_stop_loss,
            "take_profit_confirmed": args.i_confirm_take_profit,
            "no_live_endpoint_confirmed": args.i_confirm_no_live_endpoint,
            "no_autonomous_order_confirmed": args.i_confirm_no_autonomous_order,
            "no_second_order_confirmed": args.i_confirm_no_second_order,
            "post_trade_evidence_confirmed": args.i_confirm_post_trade_evidence,
            "kill_switch_ready_confirmed": args.i_confirm_kill_switch_ready,
            "loss_possible_understood": args.i_understand_loss_possible,
            "no_profit_guarantee_understood": (
                args.i_understand_no_profit_guarantee
            ),
        }
    )
    return context


def _template_payload() -> dict[str, Any]:
    return {
        "script_status": "VAULT_BACKED_DEMO_ONE_ORDER_TEMPLATE_ONLY",
        "dry_run": True,
        "broker_network_call_performed": False,
        "order_placement_performed": False,
        "order_attempt_count": 0,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "credential_value_printed": False,
        "account_id_value_printed": False,
        "dotenv_read": False,
        "approved_vault_labels": [
            ACCESS_TOKEN_CREDENTIAL_NAME,
            ACCOUNT_ID_CREDENTIAL_NAME,
        ],
        "runtime_input_rule": {
            "command_line_token_argument_supported": False,
            "command_line_account_id_argument_supported": False,
            "env_file_supported": False,
            "repo_secret_supported": False,
            "windows_vault_adapter_required_at_owner_runtime": True,
        },
        "required_confirmations": list(REQUIRED_EXECUTE_CONFIRMATIONS.values()),
        "owner_template_command": _owner_template_command(),
        "forbidden": {
            "live_endpoint": True,
            "second_order": True,
            "autonomous_order": True,
            "scheduler": True,
            "daemon": True,
            "webhook": True,
            "profit_guarantee": True,
        },
    }


def _script_payload(decision: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "script_status": decision.get("status"),
        "classification": decision.get("status"),
        "broker_network_call_performed": decision.get(
            "broker_network_call_performed",
            False,
        ),
        "order_placement_performed": decision.get("order_placement_performed", False),
        "order_attempt_count": decision.get("order_attempt_count", 0),
        "credential_read_performed": decision.get("credential_read_performed", False),
        "account_id_read_performed": decision.get("account_id_read_performed", False),
        "credential_value_printed": False,
        "account_id_value_printed": False,
        "dotenv_read": False,
        "decision": decision,
    }


def _owner_template_command() -> str:
    return (
        "python scripts/forex_delivery/"
        "run_oanda_demo_vault_backed_one_order_transport_v1.py "
        "--execute-vault-backed-demo-one-order "
        "--instrument EUR_USD "
        "--direction BUY "
        "--units 1 "
        "--stop-loss 1.07000 "
        "--take-profit 1.07100 "
        "--risk-amount 1.00 "
        "--client-order-id AIOS-DEMO-ONE-ORDER-OWNER-RUNTIME-001 "
        "--order-type MARKET "
        "--i-confirm-demo-only "
        "--i-confirm-vault-backed-runtime-only "
        "--i-confirm-one-order-only "
        "--i-confirm-owner-manual-runtime-only "
        "--i-confirm-stop-loss "
        "--i-confirm-take-profit "
        "--i-confirm-no-live-endpoint "
        "--i-confirm-no-autonomous-order "
        "--i-confirm-no-second-order "
        "--i-confirm-post-trade-evidence "
        "--i-confirm-kill-switch-ready "
        "--i-understand-loss-possible "
        "--i-understand-no-profit-guarantee"
    )


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
