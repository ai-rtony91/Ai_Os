from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_credential_account_permission_preflight_no_order_v1 import (  # noqa: E402
    evaluate_oanda_demo_credential_account_permission_preflight_no_order_v1,
    get_oanda_demo_read_only_with_urllib,
)


REQUIRED_EXECUTE_CONFIRMATIONS = {
    "i_confirm_read_only_preflight": "--i-confirm-read-only-preflight",
    "i_confirm_no_order_endpoint": "--i-confirm-no-order-endpoint",
    "i_confirm_no_trade_mutation": "--i-confirm-no-trade-mutation",
    "i_confirm_demo_only": "--i-confirm-demo-only",
    "i_confirm_runtime_credentials_external": (
        "--i-confirm-runtime-credentials-external"
    ),
    "i_confirm_prior_403_captured": "--i-confirm-prior-403-captured",
    "i_confirm_no_second_order_attempt": "--i-confirm-no-second-order-attempt",
}


def main(
    argv: Sequence[str] | None = None,
    http_get_callable: object | None = None,
) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    transport = http_get_callable or get_oanda_demo_read_only_with_urllib

    if args.print_template:
        _print_json(
            {
                "script_status": "READ_ONLY_PREFLIGHT_TEMPLATE_ONLY",
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "template": _runtime_input_template(),
            }
        )
        return 0

    if not args.execute_read_only_preflight:
        decision = evaluate_oanda_demo_credential_account_permission_preflight_no_order_v1(
            preflight_context=_ready_preflight_context(),
        )
        _print_json(
            {
                "script_status": "READ_ONLY_PREFLIGHT_DRY_RUN_PREVIEW",
                "dry_run": True,
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "decision": decision,
            }
        )
        return 0

    missing_confirmations = [
        flag
        for attr, flag in REQUIRED_EXECUTE_CONFIRMATIONS.items()
        if not getattr(args, attr)
    ]
    if missing_confirmations:
        decision = evaluate_oanda_demo_credential_account_permission_preflight_no_order_v1()
        _print_json(
            {
                "script_status": "BLOCKED_MISSING_REQUIRED_CONFIRMATIONS",
                "missing_confirmations": missing_confirmations,
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "decision": decision,
            }
        )
        return 1

    access_token = os.environ.get("OANDA_DEMO_ACCESS_TOKEN")
    account_id = os.environ.get("OANDA_DEMO_ACCOUNT_ID")
    credential_read_performed = bool(access_token)
    account_id_read_performed = bool(account_id)

    decision = evaluate_oanda_demo_credential_account_permission_preflight_no_order_v1(
        preflight_context=_ready_preflight_context(),
        runtime_access_token=access_token,
        runtime_account_id=account_id,
        http_get_callable=transport,
        execute_preflight=True,
    )
    _print_json(
        {
            "script_status": decision["status"],
            "broker_network_call_performed": decision["preflight_attempt"][
                "network_call_performed"
            ],
            "order_placement_performed": False,
            "credential_read_performed": credential_read_performed,
            "account_id_read_performed": account_id_read_performed,
            "decision": decision,
        }
    )
    return 0 if decision["status"] == "PREFLIGHT_READ_ONLY_ATTEMPTED" else 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AIOS OANDA demo credential/account permission preflight, no order."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Print sanitized read-only endpoint preview only. This is the default.",
    )
    parser.add_argument(
        "--print-template",
        action="store_true",
        help="Print required runtime inputs and confirmations without reading secrets.",
    )
    parser.add_argument(
        "--execute-read-only-preflight",
        action="store_true",
        help="Run read-only GET account preflight only with all confirmations.",
    )
    parser.add_argument("--i-confirm-read-only-preflight", action="store_true")
    parser.add_argument("--i-confirm-no-order-endpoint", action="store_true")
    parser.add_argument("--i-confirm-no-trade-mutation", action="store_true")
    parser.add_argument("--i-confirm-demo-only", action="store_true")
    parser.add_argument("--i-confirm-runtime-credentials-external", action="store_true")
    parser.add_argument("--i-confirm-prior-403-captured", action="store_true")
    parser.add_argument("--i-confirm-no-second-order-attempt", action="store_true")
    return parser


def _runtime_input_template() -> dict:
    return {
        "runtime_environment_variables": {
            "OANDA_DEMO_ACCESS_TOKEN": "externally supplied at owner runtime",
            "OANDA_DEMO_ACCOUNT_ID": "externally supplied at owner runtime",
            "credential_persistence_allowed": False,
            "account_id_persistence_allowed": False,
            "script_reads_dotenv": False,
        },
        "required_confirmations": list(REQUIRED_EXECUTE_CONFIRMATIONS.values()),
        "allowed_endpoints": [
            "GET https://api-fxpractice.oanda.com/v3/accounts",
            "GET https://api-fxpractice.oanda.com/v3/accounts/REDACTED_RUNTIME_ACCOUNT_ID",
            "GET https://api-fxpractice.oanda.com/v3/accounts/REDACTED_RUNTIME_ACCOUNT_ID/summary",
            "GET https://api-fxpractice.oanda.com/v3/accounts/REDACTED_RUNTIME_ACCOUNT_ID/instruments",
        ],
        "forbidden": {
            "orders_endpoint": True,
            "trade_mutation": True,
            "position_mutation": True,
            "live_endpoint": True,
        },
    }


def _ready_preflight_context() -> dict:
    return {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "demo_endpoint_only": True,
        "live_endpoint_absent": True,
        "demo_api_base_url": "https://api-fxpractice.oanda.com",
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
        "execution_authority": _execution_authority_false(),
    }


def _execution_authority_false() -> dict:
    return {
        "execution_allowed": False,
        "demo_order_allowed": False,
        "live_order_allowed": False,
        "broker_write_allowed": False,
        "autonomous_order_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
        "order_mutation_allowed": False,
        "position_mutation_allowed": False,
    }


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
