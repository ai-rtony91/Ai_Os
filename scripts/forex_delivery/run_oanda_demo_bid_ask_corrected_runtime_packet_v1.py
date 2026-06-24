from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_bid_ask_corrected_runtime_packet_v1 import (  # noqa: E402
    BID_ASK_CORRECTED_RUNTIME_PACKET_READY,
    DEFAULT_CLIENT_ORDER_ID,
    build_oanda_demo_bid_ask_corrected_runtime_packet_v1,
)


REQUIRED_CONFIRMATIONS = {
    "bid_ask_sltp_validation_ready_confirmed": (
        "--i-confirm-bid-ask-sltp-validation-ready"
    ),
    "demo_only_confirmed": "--i-confirm-demo-only",
    "owner_manual_runtime_only_confirmed": (
        "--i-confirm-owner-manual-runtime-only"
    ),
    "no_live_endpoint_confirmed": "--i-confirm-no-live-endpoint",
    "no_autonomous_order_confirmed": "--i-confirm-no-autonomous-order",
    "post_trade_evidence_required_confirmed": (
        "--i-confirm-post-trade-evidence-required"
    ),
    "no_profit_claim_confirmed": "--i-confirm-no-profit-claim",
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_template:
        _print_json(_template_payload())
        return 0

    if not args.build_bid_ask_corrected_runtime_packet:
        _print_json(_template_payload())
        return 0

    decision = build_oanda_demo_bid_ask_corrected_runtime_packet_v1(
        _runtime_context_from_args(args)
    )
    _print_json(_script_payload(decision))
    return 0 if decision["classification"] == BID_ASK_CORRECTED_RUNTIME_PACKET_READY else 1


def _parser() -> argparse.ArgumentParser:
    parser = SanitizedArgumentParser(
        allow_abbrev=False,
        description="AIOS OANDA demo bid/ask corrected runtime packet builder.",
    )
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument(
        "--build-bid-ask-corrected-runtime-packet",
        action="store_true",
    )
    parser.add_argument("--instrument")
    parser.add_argument("--direction", choices=("BUY", "SELL"))
    parser.add_argument("--units")
    parser.add_argument("--bid")
    parser.add_argument("--ask")
    parser.add_argument("--stop-loss", dest="stop_loss")
    parser.add_argument("--take-profit", dest="take_profit")
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
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "vault_read_performed": False,
                "environment_read_performed": False,
                "dotenv_read_performed": False,
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
        "bid": args.bid,
        "ask": args.ask,
        "stop_loss": args.stop_loss,
        "take_profit": args.take_profit,
        "min_distance_pips": args.min_distance_pips,
        "pip_size": args.pip_size,
        "risk_amount": args.risk_amount,
        "client_order_id": args.client_order_id,
        "order_type": args.order_type,
    }
    context.update({attr: bool(getattr(args, attr)) for attr in REQUIRED_CONFIRMATIONS})
    return context


def _template_payload() -> dict[str, Any]:
    return {
        "script_status": "BID_ASK_CORRECTED_RUNTIME_PACKET_TEMPLATE_ONLY",
        "dry_run": True,
        "broker_network_call_performed": False,
        "order_placement_performed": False,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "vault_read_performed": False,
        "environment_read_performed": False,
        "dotenv_read_performed": False,
        "token_argument_supported": False,
        "account_id_argument_supported": False,
        "accepted_value_arguments": [
            "--instrument EUR_USD",
            "--direction BUY or SELL",
            "--units 1",
            "--bid EXAMPLE_BID",
            "--ask EXAMPLE_ASK",
            "--stop-loss EXAMPLE_STOP_LOSS",
            "--take-profit EXAMPLE_TAKE_PROFIT",
            "--min-distance-pips 2",
            "--pip-size 0.0001",
            "--risk-amount 1.00",
            f"--client-order-id {DEFAULT_CLIENT_ORDER_ID}",
            "--order-type MARKET",
        ],
        "required_confirmations": list(REQUIRED_CONFIRMATIONS.values()),
        "validation_dependency": "BID_ASK_SLTP_VALIDATION_READY",
        "output_rule": {
            "owner_command_template_only": True,
            "target_transport_wrapper": (
                "scripts/forex_delivery/"
                "run_oanda_demo_vault_backed_one_order_transport_v1.py"
            ),
            "codex_execution_authorized": False,
            "broker_call_allowed": False,
            "vault_read_allowed": False,
        },
        "example_command": _example_command(),
    }


def _script_payload(decision: Mapping[str, Any]) -> dict[str, Any]:
    safety = decision.get("safety_boundaries")
    safety = safety if isinstance(safety, Mapping) else {}
    return {
        "script_status": decision.get("classification"),
        "classification": decision.get("classification"),
        "runtime_packet_ready": decision.get("runtime_packet_ready", False),
        "broker_network_call_performed": safety.get(
            "broker_network_call_performed",
            False,
        ),
        "order_placement_performed": safety.get("order_placement_performed", False),
        "credential_read_performed": safety.get("credential_read_performed", False),
        "account_id_read_performed": safety.get("account_id_read_performed", False),
        "vault_read_performed": safety.get("vault_read_performed", False),
        "environment_read_performed": safety.get("environment_read_performed", False),
        "dotenv_read_performed": safety.get("dotenv_read_performed", False),
        "decision": decision,
    }


def _example_command() -> str:
    return (
        "python scripts/forex_delivery/"
        "run_oanda_demo_bid_ask_corrected_runtime_packet_v1.py "
        "--build-bid-ask-corrected-runtime-packet "
        "--instrument EUR_USD "
        "--direction BUY "
        "--units 1 "
        "--bid 1.07040 "
        "--ask 1.07050 "
        "--stop-loss 1.07010 "
        "--take-profit 1.07080 "
        "--min-distance-pips 2 "
        "--pip-size 0.0001 "
        "--risk-amount 1.00 "
        "--client-order-id AIOS-DEMO-BIDASK-CORRECTED-OWNER-RUNTIME-001 "
        "--order-type MARKET "
        "--i-confirm-bid-ask-sltp-validation-ready "
        "--i-confirm-demo-only "
        "--i-confirm-owner-manual-runtime-only "
        "--i-confirm-no-live-endpoint "
        "--i-confirm-no-autonomous-order "
        "--i-confirm-post-trade-evidence-required "
        "--i-confirm-no-profit-claim"
    )


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
