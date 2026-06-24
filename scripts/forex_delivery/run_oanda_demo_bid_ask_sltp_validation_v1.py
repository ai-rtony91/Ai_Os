from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_bid_ask_sltp_validation_v1 import (  # noqa: E402
    evaluate_oanda_demo_bid_ask_sltp_validation_v1,
)


REQUIRED_CONFIRMATIONS = {
    "demo_only_confirmed": "--i-confirm-demo-only",
    "no_broker_call_confirmed": "--i-confirm-no-broker-call",
    "no_order_confirmed": "--i-confirm-no-order",
    "no_live_endpoint_confirmed": "--i-confirm-no-live-endpoint",
    "no_profit_claim_confirmed": "--i-confirm-no-profit-claim",
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_template:
        _print_json(_template_payload())
        return 0

    if not args.validate_bid_ask_sltp:
        _print_json(_template_payload())
        return 0

    decision = evaluate_oanda_demo_bid_ask_sltp_validation_v1(
        _validation_context_from_args(args)
    )
    _print_json(_script_payload(decision))
    return 0 if decision["validation_ready"] is True else 1


def _parser() -> argparse.ArgumentParser:
    parser = SanitizedArgumentParser(
        allow_abbrev=False,
        description="AIOS OANDA demo bid/ask SL/TP validation gate.",
    )
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument("--validate-bid-ask-sltp", action="store_true")
    parser.add_argument("--instrument")
    parser.add_argument("--direction", choices=("BUY", "SELL"))
    parser.add_argument("--bid")
    parser.add_argument("--ask")
    parser.add_argument("--stop-loss", dest="stop_loss")
    parser.add_argument("--take-profit", dest="take_profit")
    parser.add_argument("--min-distance-pips", dest="min_distance_pips")
    parser.add_argument("--pip-size", dest="pip_size")
    parser.add_argument("--i-confirm-demo-only", dest="demo_only_confirmed", action="store_true")
    parser.add_argument(
        "--i-confirm-no-broker-call",
        dest="no_broker_call_confirmed",
        action="store_true",
    )
    parser.add_argument(
        "--i-confirm-no-order",
        dest="no_order_confirmed",
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
                "broker_quote_lookup_performed": False,
                "live_market_data_read": False,
            }
        )
        raise SystemExit(2)


def _validation_context_from_args(args: argparse.Namespace) -> dict[str, Any]:
    context = {
        "instrument": args.instrument,
        "direction": args.direction,
        "bid": args.bid,
        "ask": args.ask,
        "stop_loss": args.stop_loss,
        "take_profit": args.take_profit,
        "min_distance_pips": args.min_distance_pips,
        "pip_size": args.pip_size,
    }
    context.update({attr: bool(getattr(args, attr)) for attr in REQUIRED_CONFIRMATIONS})
    return context


def _template_payload() -> dict[str, Any]:
    return {
        "script_status": "BID_ASK_SLTP_VALIDATION_TEMPLATE_ONLY",
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
        "broker_quote_lookup_performed": False,
        "live_market_data_read": False,
        "accepted_value_arguments": [
            "--instrument EUR_USD",
            "--direction BUY or SELL",
            "--bid EXAMPLE_BID",
            "--ask EXAMPLE_ASK",
            "--stop-loss EXAMPLE_STOP_LOSS",
            "--take-profit EXAMPLE_TAKE_PROFIT",
            "--min-distance-pips 2",
            "--pip-size 0.0001",
        ],
        "required_confirmations": list(REQUIRED_CONFIRMATIONS.values()),
        "validation_rules": {
            "buy_executable_entry_side": "ask",
            "buy_stop_loss": "below_current_bid_by_minimum_distance",
            "buy_take_profit": "above_current_ask_by_minimum_distance",
            "sell_executable_entry_side": "bid",
            "sell_stop_loss": "above_current_ask_by_minimum_distance",
            "sell_take_profit": "below_current_bid_by_minimum_distance",
            "quote_source": "owner_or_upstream_supplied_non_secret_input",
            "broker_price_lookup_allowed": False,
            "order_allowed": False,
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
        "broker_quote_lookup_performed": safety.get(
            "broker_quote_lookup_performed",
            False,
        ),
        "live_market_data_read": safety.get("live_market_data_read", False),
        "decision": decision,
    }


def _example_command() -> str:
    return (
        "python scripts/forex_delivery/"
        "run_oanda_demo_bid_ask_sltp_validation_v1.py "
        "--validate-bid-ask-sltp "
        "--instrument EUR_USD "
        "--direction BUY "
        "--bid EXAMPLE_BID "
        "--ask EXAMPLE_ASK "
        "--stop-loss EXAMPLE_STOP_LOSS "
        "--take-profit EXAMPLE_TAKE_PROFIT "
        "--min-distance-pips 2 "
        "--pip-size 0.0001 "
        "--i-confirm-demo-only "
        "--i-confirm-no-broker-call "
        "--i-confirm-no-order "
        "--i-confirm-no-live-endpoint "
        "--i-confirm-no-profit-claim"
    )


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
