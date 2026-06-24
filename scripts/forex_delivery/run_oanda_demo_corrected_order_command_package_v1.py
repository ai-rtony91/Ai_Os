"""CLI for the corrected OANDA demo order command package builder."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_corrected_order_command_package_v1 import (
    APPROVED_INSTRUMENT,
    APPROVED_ORDER_TYPE,
    CORRECTED_CLIENT_ORDER_ID,
    PACKET_ID,
    build_oanda_demo_corrected_order_command_package_v1,
)


class SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        payload = {
            "packet_id": PACKET_ID,
            "script_status": "BLOCKED_BY_INVALID_TRADE_INTENT",
            "error": "invalid_or_missing_sanitized_argument",
            "broker_network_call_performed": False,
            "order_placement_performed": False,
            "credential_read_performed": False,
            "account_id_read_performed": False,
            "vault_read_performed": False,
            "environment_read_performed": False,
            "dotenv_read_performed": False,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        raise SystemExit(2)


def build_parser() -> argparse.ArgumentParser:
    parser = SanitizedArgumentParser(
        description="Build a sanitized corrected OANDA demo command package."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--print-template", action="store_true")
    mode.add_argument("--build-corrected-command-package", action="store_true")

    parser.add_argument("--instrument", default=APPROVED_INSTRUMENT)
    parser.add_argument("--direction", default="BUY")
    parser.add_argument("--units", default="1")
    parser.add_argument("--reference-price")
    parser.add_argument("--stop-loss")
    parser.add_argument("--take-profit")
    parser.add_argument("--risk-amount", default="1.00")
    parser.add_argument("--client-order-id", default=CORRECTED_CLIENT_ORDER_ID)
    parser.add_argument("--order-type", default=APPROVED_ORDER_TYPE)

    parser.add_argument("--i-confirm-demo-only", action="store_true")
    parser.add_argument("--i-confirm-sltp-validation-passed", action="store_true")
    parser.add_argument("--i-confirm-one-prior-order-cap-consumed", action="store_true")
    parser.add_argument(
        "--i-confirm-new-owner-approval-required-before-any-future-order",
        action="store_true",
    )
    parser.add_argument("--i-confirm-owner-manual-runtime-only", action="store_true")
    parser.add_argument("--i-confirm-no-live-endpoint", action="store_true")
    parser.add_argument("--i-confirm-no-autonomous-order", action="store_true")
    parser.add_argument("--i-confirm-post-trade-evidence-required", action="store_true")
    parser.add_argument("--i-confirm-no-profit-claim", action="store_true")

    parser.add_argument("--profit-claim-made", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "--live-endpoint-requested", action="store_true", help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--autonomous-order-requested", action="store_true", help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--second-order-requested", action="store_true", help=argparse.SUPPRESS
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.print_template:
        _print_template()
        return 0

    result = build_oanda_demo_corrected_order_command_package_v1(
        {
            "instrument": args.instrument,
            "direction": args.direction,
            "units": args.units,
            "reference_price": args.reference_price,
            "stop_loss": args.stop_loss,
            "take_profit": args.take_profit,
            "risk_amount": args.risk_amount,
            "client_order_id": args.client_order_id,
            "order_type": args.order_type,
            "demo_only_confirmed": args.i_confirm_demo_only,
            "sltp_validation_passed_confirmed": args.i_confirm_sltp_validation_passed,
            "one_prior_order_cap_consumed_confirmed": (
                args.i_confirm_one_prior_order_cap_consumed
            ),
            "new_owner_approval_required_before_any_future_order_confirmed": (
                args.i_confirm_new_owner_approval_required_before_any_future_order
            ),
            "owner_manual_runtime_only_confirmed": (
                args.i_confirm_owner_manual_runtime_only
            ),
            "no_live_endpoint_confirmed": args.i_confirm_no_live_endpoint,
            "no_autonomous_order_confirmed": args.i_confirm_no_autonomous_order,
            "post_trade_evidence_required_confirmed": (
                args.i_confirm_post_trade_evidence_required
            ),
            "no_profit_claim_confirmed": args.i_confirm_no_profit_claim,
            "profit_claim_made": args.profit_claim_made,
            "live_endpoint_requested": args.live_endpoint_requested,
            "autonomous_order_requested": args.autonomous_order_requested,
            "second_order_requested": args.second_order_requested,
        }
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("package_ready") else 1


def _print_template() -> None:
    payload: dict[str, Any] = {
        "packet_id": PACKET_ID,
        "script_status": "TEMPLATE_ONLY",
        "broker_network_call_performed": False,
        "order_placement_performed": False,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "vault_read_performed": False,
        "environment_read_performed": False,
        "dotenv_read_performed": False,
        "template_command": (
            "python scripts/forex_delivery/"
            "run_oanda_demo_corrected_order_command_package_v1.py "
            "--build-corrected-command-package --instrument EUR_USD "
            "--direction BUY --units 1 "
            "--reference-price EXAMPLE_REFERENCE_PRICE "
            "--stop-loss EXAMPLE_VALID_STOP_LOSS_PRICE "
            "--take-profit EXAMPLE_VALID_TAKE_PROFIT_PRICE "
            "--risk-amount 1.00 "
            "--client-order-id AIOS-DEMO-CORRECTED-ONE-ORDER-OWNER-RUNTIME-001 "
            "--order-type MARKET --i-confirm-demo-only "
            "--i-confirm-sltp-validation-passed "
            "--i-confirm-one-prior-order-cap-consumed "
            "--i-confirm-new-owner-approval-required-before-any-future-order "
            "--i-confirm-owner-manual-runtime-only --i-confirm-no-live-endpoint "
            "--i-confirm-no-autonomous-order "
            "--i-confirm-post-trade-evidence-required "
            "--i-confirm-no-profit-claim"
        ),
        "template_status": {
            "requires_reference_price": True,
            "requires_stop_loss": True,
            "requires_take_profit": True,
            "requires_sltp_validation_pass": True,
            "prior_order_cap_consumed": True,
            "future_owner_approval_required_before_order": True,
            "order_authorized_by_template": False,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
