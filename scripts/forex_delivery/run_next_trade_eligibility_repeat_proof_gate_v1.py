from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.next_trade_eligibility_repeat_proof_gate_v1 import (  # noqa: E402
    NEXT_TRADE_BLOCKED_UNSAFE_OR_INVALID,
    PACKET_ID,
    evaluate_next_trade_eligibility_repeat_proof_gate_v1,
    next_trade_eligibility_repeat_proof_gate_samples_v1,
    next_trade_eligibility_repeat_proof_gate_template_v1,
)


SCRIPT_STATUS_PACKAGE = "NEXT_TRADE_ELIGIBILITY_REPEAT_PROOF_GATE_DRY_RUN_SAMPLES"
SCRIPT_STATUS_TEMPLATE = "NEXT_TRADE_ELIGIBILITY_REPEAT_PROOF_GATE_TEMPLATE_ONLY"
SCRIPT_STATUS_BLOCKED = "NEXT_TRADE_ELIGIBILITY_REPEAT_PROOF_GATE_INPUT_BLOCKED"

SAFETY_FLAGS = (
    "network_call_performed",
    "broker_network_call_performed",
    "broker_api_call_performed",
    "broker_call_performed",
    "oanda_call_performed",
    "oanda_api_call_performed",
    "broker_write_performed",
    "credential_read_performed",
    "account_id_read_performed",
    "vault_read_performed",
    "windows_vault_read_performed",
    "dotenv_read",
    "env_read",
    "order_placement_performed",
    "order_close_performed",
    "order_mutation_performed",
    "trade_mutation_performed",
    "position_mutation_performed",
    "orders_endpoint_called",
    "live_endpoint_used",
    "raw_broker_payload_persisted",
    "file_persistence_performed",
    "write_performed",
    "bucket_update_performed",
    "bucket_mutation_performed",
    "result_bucket_update_performed",
    "result_bucket_mutation_performed",
    "next_order_authorized",
    "next_trade_authorized",
    "next_trade_executed",
    "order_placement_authorized",
    "scheduler_started",
    "daemon_started",
    "webhook_called",
    "live_funding_performed",
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_template:
        payload = {
            "script_status": SCRIPT_STATUS_TEMPLATE,
            "packet_id": PACKET_ID,
            "dry_run": True,
            "json_only": True,
            "template": next_trade_eligibility_repeat_proof_gate_template_v1(),
            "review_eligibility_only": True,
            "next_trade_review_authorized_here": False,
            "next_trade_authorized_here": False,
            "order_placement_authorized_here": False,
            "broker_call_authorized_here": False,
            "live_funding_authorized_here": False,
        }
        payload.update(_safety_flags())
        _print_json(payload)
        return 0

    samples = next_trade_eligibility_repeat_proof_gate_samples_v1()
    selected = samples if args.sample == "all" else {args.sample: samples[args.sample]}
    decisions = {
        name: evaluate_next_trade_eligibility_repeat_proof_gate_v1(
            sample["owner_run_decision"],
            sample["bucket_gate_decision"],
            sample.get("exposure_state"),
            sample.get("owner_approval"),
            sample.get("risk_state"),
        )
        for name, sample in selected.items()
    }
    payload = {
        "script_status": SCRIPT_STATUS_PACKAGE,
        "packet_id": PACKET_ID,
        "dry_run": True,
        "json_only": True,
        "sample": args.sample,
        "review_eligibility_only": True,
        "next_trade_authorized_here": False,
        "order_placement_authorized_here": False,
        "broker_call_authorized_here": False,
        "live_funding_authorized_here": False,
        "decisions": decisions,
    }
    payload.update(_safety_flags())
    _print_json(payload)
    return 0


def _parser() -> argparse.ArgumentParser:
    sample_names = sorted(next_trade_eligibility_repeat_proof_gate_samples_v1())
    parser = SanitizedArgumentParser(
        allow_abbrev=False,
        description=(
            "AIOS next-trade eligibility repeat-proof gate. Prints JSON only "
            "and performs no broker/OANDA call, order placement, bucket "
            "mutation, next-trade execution, or live funding action."
        ),
    )
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument(
        "--sample",
        choices=["all", *sample_names],
        default="all",
        help="Built-in sanitized gate sample to evaluate.",
    )
    return parser


class SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        payload = _blocked_script_payload(["unsupported_or_invalid_argument"])
        payload["argument_error"] = "unsupported_or_invalid_argument"
        _print_json(payload)
        raise SystemExit(2)


def _blocked_script_payload(blockers: Sequence[str]) -> dict[str, Any]:
    decision = evaluate_next_trade_eligibility_repeat_proof_gate_v1(
        {"exercise_status": "UNSUPPORTED"},
        {"gate_status": "UNSUPPORTED"},
        {"open_trade_count": 0, "open_position_count": 0, "pending_order_count": 0},
        {"owner_approved_next_trade_review": False},
        {"review_only": True},
    )
    payload: dict[str, Any] = {
        "script_status": SCRIPT_STATUS_BLOCKED,
        "packet_id": PACKET_ID,
        "dry_run": True,
        "json_only": True,
        "blockers": list(blockers),
        "decision": decision,
        "gate_status": NEXT_TRADE_BLOCKED_UNSAFE_OR_INVALID,
        "review_eligibility_only": True,
        "next_trade_authorized_here": False,
        "order_placement_authorized_here": False,
        "broker_call_authorized_here": False,
        "live_funding_authorized_here": False,
    }
    payload.update(_safety_flags())
    return payload


def _safety_flags() -> dict[str, bool]:
    return {field: False for field in SAFETY_FLAGS}


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
