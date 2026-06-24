from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_sltp_validation_correction_v1 import (  # noqa: E402
    evaluate_oanda_demo_sltp_validation_correction_v1,
)


REQUIRED_CONFIRMATIONS = {
    "demo_only_confirmed": "--i-confirm-demo-only",
    "no_broker_call_confirmed": "--i-confirm-no-broker-call",
    "no_second_order_confirmed": "--i-confirm-no-second-order",
    "no_live_endpoint_confirmed": "--i-confirm-no-live-endpoint",
    "no_profit_claim_confirmed": "--i-confirm-no-profit-claim",
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_template:
        _print_json(_template_payload())
        return 0

    if not args.validate_sltp:
        _print_json(_template_payload())
        return 0

    decision = evaluate_oanda_demo_sltp_validation_correction_v1(
        _validation_context_from_args(args)
    )
    _print_json(_script_payload(decision))
    return 0 if decision["validation_ready"] is True else 1


def _parser() -> argparse.ArgumentParser:
    parser = SanitizedArgumentParser(
        allow_abbrev=False,
        description="AIOS OANDA demo SL/TP side validation correction gate.",
    )
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument("--validate-sltp", action="store_true")
    parser.add_argument("--instrument")
    parser.add_argument("--direction", choices=("BUY", "SELL"))
    parser.add_argument("--reference-price", dest="reference_price")
    parser.add_argument("--stop-loss", dest="stop_loss")
    parser.add_argument("--take-profit", dest="take_profit")
    parser.add_argument("--i-confirm-demo-only", dest="demo_only_confirmed", action="store_true")
    parser.add_argument(
        "--i-confirm-no-broker-call",
        dest="no_broker_call_confirmed",
        action="store_true",
    )
    parser.add_argument(
        "--i-confirm-no-second-order",
        dest="no_second_order_confirmed",
        action="store_true",
    )
    parser.add_argument(
        "--i-confirm-no-live-endpoint",
        dest="no_live_endpoint_confirmed",
        action="store_true",
    )
    parser.add_argument(
        "--i-confirm-no-profit-claim",
        dest="no_profit_claim_confirmed",
        action="store_true",
    )
    return parser


class SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        _print_json(
            {
                "script_status": "BLOCKED_INVALID_ARGUMENTS",
                "argument_error": "unsupported_or_invalid_argument",
                "broker_call_performed": False,
                "order_placement_performed": False,
                "second_order_allowed": False,
                "live_endpoint_used": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "windows_vault_read_performed": False,
                "environment_variable_read_performed": False,
                "dotenv_read": False,
            }
        )
        raise SystemExit(2)


def _validation_context_from_args(args: argparse.Namespace) -> dict[str, Any]:
    context = {
        "instrument": args.instrument,
        "direction": args.direction,
        "reference_price": args.reference_price,
        "stop_loss": args.stop_loss,
        "take_profit": args.take_profit,
    }
    context.update(
        {
            attr: bool(getattr(args, attr))
            for attr in REQUIRED_CONFIRMATIONS
        }
    )
    return context


def _template_payload() -> dict[str, Any]:
    return {
        "script_status": "SLTP_VALIDATION_TEMPLATE_ONLY",
        "dry_run": True,
        "broker_call_performed": False,
        "order_placement_performed": False,
        "second_order_allowed": False,
        "live_endpoint_used": False,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "windows_vault_read_performed": False,
        "environment_variable_read_performed": False,
        "dotenv_read": False,
        "accepted_value_arguments": [
            "--instrument EUR_USD",
            "--direction BUY or SELL",
            "--reference-price EXAMPLE_REFERENCE_PRICE",
            "--stop-loss EXAMPLE_STOP_LOSS_PRICE",
            "--take-profit EXAMPLE_TAKE_PROFIT_PRICE",
        ],
        "required_confirmations": list(REQUIRED_CONFIRMATIONS.values()),
        "validation_rules": {
            "buy_stop_loss": "below_reference_price",
            "buy_take_profit": "above_reference_price",
            "sell_stop_loss": "above_reference_price",
            "sell_take_profit": "below_reference_price",
            "reference_price_source": "owner_supplied_non_secret_input",
            "broker_price_lookup_allowed": False,
        },
        "example_command": _example_command(),
    }


def _script_payload(decision: Mapping[str, Any]) -> dict[str, Any]:
    safety = decision.get("safety_proof")
    safety = safety if isinstance(safety, Mapping) else {}
    return {
        "script_status": decision.get("classification"),
        "classification": decision.get("classification"),
        "validation_ready": decision.get("validation_ready", False),
        "broker_call_performed": safety.get("broker_call_performed", False),
        "order_placement_performed": safety.get("order_placement_performed", False),
        "second_order_allowed": safety.get("second_order_allowed", False),
        "live_endpoint_used": safety.get("live_endpoint_used", False),
        "credential_read_performed": safety.get("credential_read_performed", False),
        "account_id_read_performed": safety.get("account_id_read_performed", False),
        "windows_vault_read_performed": safety.get(
            "windows_vault_read_performed",
            False,
        ),
        "environment_variable_read_performed": safety.get(
            "environment_variable_read_performed",
            False,
        ),
        "dotenv_read": safety.get("dotenv_read", False),
        "decision": decision,
    }


def _example_command() -> str:
    return (
        "python scripts/forex_delivery/"
        "run_oanda_demo_sltp_validation_correction_v1.py "
        "--validate-sltp "
        "--instrument EUR_USD "
        "--direction BUY "
        "--reference-price EXAMPLE_REFERENCE_PRICE "
        "--stop-loss EXAMPLE_STOP_LOSS_PRICE "
        "--take-profit EXAMPLE_TAKE_PROFIT_PRICE "
        "--i-confirm-demo-only "
        "--i-confirm-no-broker-call "
        "--i-confirm-no-second-order "
        "--i-confirm-no-live-endpoint "
        "--i-confirm-no-profit-claim"
    )


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
