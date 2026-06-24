"""CLI for the corrected future OANDA demo runtime packet builder."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_corrected_future_runtime_packet_v1 import (
    APPROVED_INSTRUMENT,
    APPROVED_ORDER_TYPE,
    FUTURE_CLIENT_ORDER_ID,
    PACKET_ID,
    build_oanda_demo_corrected_future_runtime_packet_v1,
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
        description="Build a sanitized corrected future OANDA demo runtime packet."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--print-template", action="store_true")
    mode.add_argument("--build-corrected-future-runtime-packet", action="store_true")

    parser.add_argument("--instrument", default=APPROVED_INSTRUMENT)
    parser.add_argument("--direction", default="BUY")
    parser.add_argument("--units", default="1")
    parser.add_argument("--reference-price")
    parser.add_argument("--stop-loss")
    parser.add_argument("--take-profit")
    parser.add_argument("--risk-amount", default="1.00")
    parser.add_argument("--client-order-id", default=FUTURE_CLIENT_ORDER_ID)
    parser.add_argument("--order-type", default=APPROVED_ORDER_TYPE)

    parser.add_argument("--i-confirm-corrected-package-ready", action="store_true")
    parser.add_argument("--i-confirm-future-approval-gate-ready", action="store_true")
    parser.add_argument("--i-confirm-sltp-validation-ready", action="store_true")
    parser.add_argument("--i-confirm-demo-only", action="store_true")
    parser.add_argument("--i-confirm-owner-manual-runtime-only", action="store_true")
    parser.add_argument("--i-confirm-no-live-endpoint", action="store_true")
    parser.add_argument("--i-confirm-no-autonomous-order", action="store_true")
    parser.add_argument("--i-confirm-post-trade-evidence-required", action="store_true")
    parser.add_argument("--i-confirm-no-profit-claim", action="store_true")

    parser.add_argument(
        "--live-endpoint-requested", action="store_true", help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--autonomous-order-requested", action="store_true", help=argparse.SUPPRESS
    )
    parser.add_argument("--profit-claim-made", action="store_true", help=argparse.SUPPRESS)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.print_template:
        _print_template()
        return 0

    result = build_oanda_demo_corrected_future_runtime_packet_v1(
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
            "corrected_package_ready_confirmed": (
                args.i_confirm_corrected_package_ready
            ),
            "future_approval_gate_ready_confirmed": (
                args.i_confirm_future_approval_gate_ready
            ),
            "sltp_validation_ready_confirmed": (
                args.i_confirm_sltp_validation_ready
            ),
            "demo_only_confirmed": args.i_confirm_demo_only,
            "owner_manual_runtime_only_confirmed": (
                args.i_confirm_owner_manual_runtime_only
            ),
            "no_live_endpoint_confirmed": args.i_confirm_no_live_endpoint,
            "no_autonomous_order_confirmed": args.i_confirm_no_autonomous_order,
            "post_trade_evidence_required_confirmed": (
                args.i_confirm_post_trade_evidence_required
            ),
            "no_profit_claim_confirmed": args.i_confirm_no_profit_claim,
            "live_endpoint_requested": args.live_endpoint_requested,
            "autonomous_order_requested": args.autonomous_order_requested,
            "profit_claim_made": args.profit_claim_made,
        }
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("runtime_packet_ready") else 1


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
            "run_oanda_demo_corrected_future_runtime_packet_v1.py "
            "--build-corrected-future-runtime-packet --instrument EUR_USD "
            "--direction BUY --units 1 --reference-price 1.07050 "
            "--stop-loss 1.06950 --take-profit 1.07150 --risk-amount 1.00 "
            "--client-order-id AIOS-DEMO-CORRECTED-FUTURE-OWNER-RUNTIME-001 "
            "--order-type MARKET --i-confirm-corrected-package-ready "
            "--i-confirm-future-approval-gate-ready "
            "--i-confirm-sltp-validation-ready --i-confirm-demo-only "
            "--i-confirm-owner-manual-runtime-only --i-confirm-no-live-endpoint "
            "--i-confirm-no-autonomous-order "
            "--i-confirm-post-trade-evidence-required "
            "--i-confirm-no-profit-claim"
        ),
        "template_status": {
            "owner_only": True,
            "codex_execution_authorized": False,
            "broker_network_call_performed": False,
            "vault_read_performed": False,
            "post_trade_evidence_required_after_owner_run": True,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
