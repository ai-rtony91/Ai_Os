"""CLI for the future OANDA demo order approval gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_future_order_approval_gate_v1 import (
    PACKET_ID,
    evaluate_oanda_demo_future_order_approval_gate_v1,
)


class SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        payload = {
            "packet_id": PACKET_ID,
            "script_status": "BLOCKED_BY_INVALID_APPROVAL_GATE_ARGUMENT",
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
        description="Evaluate a sanitized future OANDA demo order approval gate."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--print-template", action="store_true")
    mode.add_argument("--evaluate-future-order-approval", action="store_true")

    parser.add_argument("--corrected-order-package-ready", action="store_true")
    parser.add_argument("--sltp-validation-ready", action="store_true")
    parser.add_argument("--prior-cancel-evidence-captured", action="store_true")
    parser.add_argument(
        "--prior-order-cap-consumed-acknowledged", action="store_true"
    )
    parser.add_argument("--explicit-new-owner-approval", action="store_true")
    parser.add_argument("--demo-only", action="store_true")
    parser.add_argument("--one-order-only", action="store_true")
    parser.add_argument("--no-live-endpoint", action="store_true")
    parser.add_argument("--no-autonomous-order", action="store_true")
    parser.add_argument("--post-trade-evidence-required", action="store_true")
    parser.add_argument("--no-profit-claim", action="store_true")

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

    result = evaluate_oanda_demo_future_order_approval_gate_v1(
        {
            "corrected_order_package_ready": args.corrected_order_package_ready,
            "sltp_validation_ready": args.sltp_validation_ready,
            "prior_cancel_evidence_captured": args.prior_cancel_evidence_captured,
            "prior_order_cap_consumed_acknowledged": (
                args.prior_order_cap_consumed_acknowledged
            ),
            "explicit_new_owner_approval": args.explicit_new_owner_approval,
            "demo_only": args.demo_only,
            "one_order_only": args.one_order_only,
            "no_live_endpoint": args.no_live_endpoint,
            "no_autonomous_order": args.no_autonomous_order,
            "post_trade_evidence_required": args.post_trade_evidence_required,
            "no_profit_claim": args.no_profit_claim,
            "live_endpoint_requested": args.live_endpoint_requested,
            "autonomous_order_requested": args.autonomous_order_requested,
            "profit_claim_made": args.profit_claim_made,
        }
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ready_for_manual_decision") else 1


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
            "run_oanda_demo_future_order_approval_gate_v1.py "
            "--evaluate-future-order-approval "
            "--corrected-order-package-ready --sltp-validation-ready "
            "--prior-cancel-evidence-captured "
            "--prior-order-cap-consumed-acknowledged "
            "--explicit-new-owner-approval --demo-only --one-order-only "
            "--no-live-endpoint --no-autonomous-order "
            "--post-trade-evidence-required --no-profit-claim"
        ),
        "template_status": {
            "manual_decision_only": True,
            "order_execution_authorized": False,
            "automatic_order_authorized": False,
            "broker_command_authorized_for_codex": False,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
