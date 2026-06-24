from __future__ import annotations

import argparse
import ctypes
import json
from pathlib import Path
from urllib import parse, request
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_live_quote_derived_sltp_runtime_v1 import (  # noqa: E402
    APPROVED_ACCOUNT_ID_LABEL,
    APPROVED_ACCESS_TOKEN_LABEL,
    APPROVED_VAULT_LABELS,
    DEFAULT_CLIENT_ORDER_ID,
    DEMO_API_BASE_URL_PREFIX,
    LIVE_QUOTE_DERIVED_DEMO_ORDER_ATTEMPTED,
    LIVE_QUOTE_DERIVED_RUNTIME_PACKET_READY,
    build_live_quote_derived_sltp_runtime_v1,
)


REQUIRED_CONFIRMATIONS = {
    "demo_only_confirmed": "--i-confirm-demo-only",
    "vault_backed_runtime_only_confirmed": (
        "--i-confirm-vault-backed-runtime-only"
    ),
    "one_order_only_confirmed": "--i-confirm-one-order-only",
    "owner_manual_runtime_only_confirmed": (
        "--i-confirm-owner-manual-runtime-only"
    ),
    "no_live_endpoint_confirmed": "--i-confirm-no-live-endpoint",
    "no_autonomous_order_confirmed": "--i-confirm-no-autonomous-order",
    "no_second_order_confirmed": "--i-confirm-no-second-order",
    "post_trade_evidence_required_confirmed": (
        "--i-confirm-post-trade-evidence-required"
    ),
    "no_profit_claim_confirmed": "--i-confirm-no-profit-claim",
    "loss_possible_understood": "--i-understand-loss-possible",
    "no_profit_guarantee_understood": "--i-understand-no-profit-guarantee",
}


def main(
    argv: Sequence[str] | None = None,
    *,
    vault_load_callable: object | None = None,
    http_get_pricing_callable: object | None = None,
    http_post_order_callable: object | None = None,
) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_template:
        _print_json(_template_payload())
        return 0

    if not (
        args.owner_build_live_quote_derived_demo_order
        or args.owner_execute_live_quote_derived_demo_order
    ):
        _print_json(_template_payload())
        return 0

    loader = vault_load_callable or load_from_windows_credential_manager_v1
    get_pricing = http_get_pricing_callable or get_oanda_demo_pricing_with_urllib
    post_order = http_post_order_callable or post_oanda_demo_order_with_urllib
    decision = build_live_quote_derived_sltp_runtime_v1(
        _runtime_context_from_args(args),
        vault_load_callable=loader,
        http_get_pricing_callable=get_pricing,
        http_post_order_callable=post_order,
        execute_order=args.owner_execute_live_quote_derived_demo_order,
    )
    _print_json(_script_payload(decision))
    return (
        0
        if decision.get("classification")
        in (
            LIVE_QUOTE_DERIVED_RUNTIME_PACKET_READY,
            LIVE_QUOTE_DERIVED_DEMO_ORDER_ATTEMPTED,
        )
        else 1
    )


def _parser() -> argparse.ArgumentParser:
    parser = SanitizedArgumentParser(
        allow_abbrev=False,
        description="AIOS OANDA demo live-quote-derived SL/TP owner runtime.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--print-template", action="store_true")
    mode.add_argument("--owner-build-live-quote-derived-demo-order", action="store_true")
    mode.add_argument("--owner-execute-live-quote-derived-demo-order", action="store_true")
    parser.add_argument("--instrument")
    parser.add_argument("--direction", choices=("BUY", "SELL"))
    parser.add_argument("--units")
    parser.add_argument("--stop-loss-pips", dest="stop_loss_pips")
    parser.add_argument("--take-profit-pips", dest="take_profit_pips")
    parser.add_argument("--min-distance-pips", dest="min_distance_pips")
    parser.add_argument("--pip-size", dest="pip_size")
    parser.add_argument("--risk-amount", dest="risk_amount")
    parser.add_argument("--client-order-id", dest="client_order_id")
    parser.add_argument("--order-type", dest="order_type", choices=("MARKET",))
    for attr, flag in REQUIRED_CONFIRMATIONS.items():
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
                "environment_variable_read_performed": False,
                "token_argument_supported": False,
                "account_id_argument_supported": False,
            }
        )
        raise SystemExit(2)


def _runtime_context_from_args(args: argparse.Namespace) -> dict[str, Any]:
    context = {
        "instrument": args.instrument,
        "direction": args.direction,
        "units": args.units,
        "stop_loss_pips": args.stop_loss_pips,
        "take_profit_pips": args.take_profit_pips,
        "min_distance_pips": args.min_distance_pips,
        "pip_size": args.pip_size,
        "risk_amount": args.risk_amount,
        "client_order_id": args.client_order_id,
        "order_type": args.order_type,
    }
    context.update({attr: bool(getattr(args, attr)) for attr in REQUIRED_CONFIRMATIONS})
    return context


def load_from_windows_credential_manager_v1(
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    credential_name = str(payload.get("credential_name", ""))
    if credential_name not in APPROVED_VAULT_LABELS:
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
    loaded = advapi32.CredReadW(
        credential_name,
        1,
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


def get_oanda_demo_pricing_with_urllib(payload: Mapping[str, Any]) -> dict[str, Any]:
    access_token = str(payload.get("runtime_access_token", ""))
    account_id = str(payload.get("runtime_account_id", ""))
    instrument = str(payload.get("instrument", "EUR_USD"))
    query = parse.urlencode({"instruments": instrument})
    url = (
        f"{DEMO_API_BASE_URL_PREFIX}/accounts/"
        f"{parse.quote(account_id, safe='')}/pricing?{query}"
    )
    request_payload = request.Request(
        url,
        method="GET",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    with request.urlopen(request_payload, timeout=20) as response:  # nosec B310
        body = response.read().decode("utf-8")
        status_code = getattr(response, "status", None)
    return {
        "network_call_performed": True,
        "endpoint_type": "OANDA practice/demo pricing endpoint only",
        "method": "GET",
        "status_code": status_code,
        "response_json": json.loads(body),
    }


def post_oanda_demo_order_with_urllib(payload: Mapping[str, Any]) -> dict[str, Any]:
    access_token = str(payload.get("runtime_access_token", ""))
    account_id = str(payload.get("runtime_account_id", ""))
    order_payload = payload.get("order_payload")
    body = json.dumps(order_payload).encode("utf-8")
    url = (
        f"{DEMO_API_BASE_URL_PREFIX}/accounts/"
        f"{parse.quote(account_id, safe='')}/orders"
    )
    request_payload = request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )
    with request.urlopen(request_payload, timeout=20) as response:  # nosec B310
        response_body = response.read().decode("utf-8")
        status_code = getattr(response, "status", None)
    return {
        "network_call_performed": True,
        "order_placement_performed": True,
        "order_attempt_count": 1,
        "endpoint_type": "OANDA practice/demo orders endpoint only",
        "method": "POST",
        "status_code": status_code,
        "response_json": json.loads(response_body),
    }


def _template_payload() -> dict[str, Any]:
    return {
        "script_status": "LIVE_QUOTE_DERIVED_SLTP_RUNTIME_TEMPLATE_ONLY",
        "dry_run": True,
        "broker_network_call_performed": False,
        "order_placement_performed": False,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "credential_value_printed": False,
        "account_id_value_printed": False,
        "dotenv_read": False,
        "environment_variable_read_performed": False,
        "token_argument_supported": False,
        "account_id_argument_supported": False,
        "approved_vault_labels": [
            APPROVED_ACCESS_TOKEN_LABEL,
            APPROVED_ACCOUNT_ID_LABEL,
        ],
        "supported_modes": [
            "--owner-build-live-quote-derived-demo-order",
            "--owner-execute-live-quote-derived-demo-order",
        ],
        "accepted_value_arguments": [
            "--instrument EUR_USD",
            "--direction BUY or SELL",
            "--units 1",
            "--stop-loss-pips 2",
            "--take-profit-pips 3",
            "--min-distance-pips 2",
            "--pip-size 0.0001",
            "--risk-amount 1.00",
            f"--client-order-id {DEFAULT_CLIENT_ORDER_ID}",
            "--order-type MARKET",
        ],
        "required_confirmations": list(REQUIRED_CONFIRMATIONS.values()),
        "example_build_command": _example_command(
            "--owner-build-live-quote-derived-demo-order"
        ),
        "example_execute_command": _example_command(
            "--owner-execute-live-quote-derived-demo-order"
        ),
    }


def _script_payload(decision: Mapping[str, Any]) -> dict[str, Any]:
    safety = decision.get("safety_boundaries")
    safety = safety if isinstance(safety, Mapping) else {}
    return {
        "script_status": decision.get("classification"),
        "classification": decision.get("classification"),
        "runtime_ready": decision.get("runtime_ready", False),
        "pricing_network_call_performed": safety.get(
            "pricing_network_call_performed",
            False,
        ),
        "broker_network_call_performed": safety.get(
            "broker_network_call_performed",
            False,
        ),
        "order_placement_performed": safety.get("order_placement_performed", False),
        "order_attempt_count": safety.get("order_attempt_count", 0),
        "credential_read_performed": safety.get("credential_read_performed", False),
        "account_id_read_performed": safety.get("account_id_read_performed", False),
        "credential_value_printed": False,
        "account_id_value_printed": False,
        "dotenv_read": False,
        "decision": decision,
    }


def _example_command(mode_flag: str) -> str:
    return (
        "python scripts/forex_delivery/"
        "run_oanda_demo_live_quote_derived_sltp_runtime_v1.py "
        f"{mode_flag} "
        "--instrument EUR_USD "
        "--direction BUY "
        "--units 1 "
        "--stop-loss-pips 2 "
        "--take-profit-pips 3 "
        "--min-distance-pips 2 "
        "--pip-size 0.0001 "
        "--risk-amount 1.00 "
        "--client-order-id AIOS-DEMO-LIVEQUOTE-DERIVED-OWNER-RUNTIME-001 "
        "--order-type MARKET "
        "--i-confirm-demo-only "
        "--i-confirm-vault-backed-runtime-only "
        "--i-confirm-one-order-only "
        "--i-confirm-owner-manual-runtime-only "
        "--i-confirm-no-live-endpoint "
        "--i-confirm-no-autonomous-order "
        "--i-confirm-no-second-order "
        "--i-confirm-post-trade-evidence-required "
        "--i-confirm-no-profit-claim "
        "--i-understand-loss-possible "
        "--i-understand-no-profit-guarantee"
    )


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
