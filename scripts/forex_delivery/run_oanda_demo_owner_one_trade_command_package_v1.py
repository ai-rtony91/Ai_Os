from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_owner_one_trade_command_package_v1 import (  # noqa: E402
    default_oanda_demo_owner_one_trade_command_package_context_v1,
    build_oanda_demo_owner_one_trade_command_package_v1,
)


CONFIRMATION_ATTRS = {
    "demo_only_confirmed": "--i-confirm-demo-only",
    "one_order_only_confirmed": "--i-confirm-one-order-only",
    "owner_manual_runtime_only_confirmed": "--i-confirm-owner-manual-runtime-only",
    "stop_loss_present_confirmed": "--i-confirm-stop-loss-present",
    "take_profit_present_confirmed": "--i-confirm-take-profit-present",
    "no_live_endpoint_confirmed": "--i-confirm-no-live-endpoint",
    "no_autonomous_order_confirmed": "--i-confirm-no-autonomous-order",
    "post_trade_evidence_required_confirmed": (
        "--i-confirm-post-trade-evidence-required"
    ),
    "result_bucket_required_confirmed": "--i-confirm-result-bucket-required",
    "no_profit_claim_confirmed": "--i-confirm-no-profit-claim",
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_template:
        _print_json(_template_payload())
        return 0

    if not args.build_owner_command_package:
        _print_json(_template_payload())
        return 0

    command_context = {
        "instrument": args.instrument,
        "direction": args.direction,
        "units": args.units,
        "stop_loss_price": args.stop_loss_price,
        "take_profit_price": args.take_profit_price,
    }
    command_context.update(
        {field: bool(getattr(args, field)) for field in CONFIRMATION_ATTRS}
    )
    decision = build_oanda_demo_owner_one_trade_command_package_v1(command_context)
    _print_json(_script_payload(decision))
    return 0 if decision["package_ready"] is True else 1


def _parser() -> argparse.ArgumentParser:
    parser = SanitizedArgumentParser(
        allow_abbrev=False,
        description="AIOS OANDA demo owner one-trade command package builder.",
    )
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument("--build-owner-command-package", action="store_true")
    parser.add_argument("--instrument")
    parser.add_argument("--direction")
    parser.add_argument("--units")
    parser.add_argument("--stop-loss-price", dest="stop_loss_price")
    parser.add_argument("--take-profit-price", dest="take_profit_price")
    for attr, flag in CONFIRMATION_ATTRS.items():
        parser.add_argument(flag, dest=attr, action="store_true")
    return parser


class SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        _print_json(
            {
                "script_status": "BLOCKED_INVALID_ARGUMENTS",
                "argument_error": "unsupported_or_invalid_argument",
                "broker_call_performed_by_codex": False,
                "order_placement_performed": False,
                "orders_endpoint_called": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "credential_value_printed": False,
                "account_id_value_printed": False,
                "dotenv_read": False,
                "live_endpoint_used": False,
            }
        )
        raise SystemExit(2)


def _template_payload() -> dict[str, Any]:
    return {
        "script_status": "OWNER_ONE_TRADE_COMMAND_PACKAGE_TEMPLATE_ONLY",
        "broker_call_performed_by_codex": False,
        "order_placement_performed": False,
        "orders_endpoint_called": False,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "credential_value_printed": False,
        "account_id_value_printed": False,
        "dotenv_read": False,
        "live_endpoint_used": False,
        "accepted_value_arguments": [
            "--instrument",
            "--direction",
            "--units",
            "--stop-loss-price",
            "--take-profit-price",
        ],
        "required_non_secret_flags": [
            "--build-owner-command-package",
            "--instrument EUR_USD",
            "--direction BUY",
            "--units 1",
            "--stop-loss-price EXAMPLE_STOP_LOSS_PRICE",
            "--take-profit-price EXAMPLE_TAKE_PROFIT_PRICE",
            *CONFIRMATION_ATTRS.values(),
        ],
        "example_builder_command": _example_builder_command(),
        "default_context": default_oanda_demo_owner_one_trade_command_package_context_v1(),
    }


def _script_payload(decision: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "script_status": decision.get("classification"),
        "classification": decision.get("classification"),
        "package_ready": decision.get("package_ready", False),
        "broker_call_performed_by_codex": False,
        "order_placement_performed": False,
        "orders_endpoint_called": False,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "credential_value_printed": False,
        "account_id_value_printed": False,
        "dotenv_read": False,
        "live_endpoint_used": False,
        "decision": decision,
    }


def _example_builder_command() -> str:
    return (
        "python scripts/forex_delivery/"
        "run_oanda_demo_owner_one_trade_command_package_v1.py "
        "--build-owner-command-package "
        "--instrument EUR_USD "
        "--direction BUY "
        "--units 1 "
        "--stop-loss-price EXAMPLE_STOP_LOSS_PRICE "
        "--take-profit-price EXAMPLE_TAKE_PROFIT_PRICE "
        "--i-confirm-demo-only "
        "--i-confirm-one-order-only "
        "--i-confirm-owner-manual-runtime-only "
        "--i-confirm-stop-loss-present "
        "--i-confirm-take-profit-present "
        "--i-confirm-no-live-endpoint "
        "--i-confirm-no-autonomous-order "
        "--i-confirm-post-trade-evidence-required "
        "--i-confirm-result-bucket-required "
        "--i-confirm-no-profit-claim"
    )


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
