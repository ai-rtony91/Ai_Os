from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.realized_pl_result_bucket_update_gate_v1 import (  # noqa: E402
    BUCKET_UPDATE_BLOCKED_UNSAFE_OR_INVALID,
    PACKET_ID,
    evaluate_realized_pl_result_bucket_update_gate_v1,
    realized_pl_result_bucket_update_gate_samples_v1,
    realized_pl_result_bucket_update_gate_template_v1,
)


SCRIPT_STATUS_PACKAGE = "REALIZED_PL_RESULT_BUCKET_UPDATE_GATE_DRY_RUN_SAMPLES"
SCRIPT_STATUS_TEMPLATE = "REALIZED_PL_RESULT_BUCKET_UPDATE_GATE_TEMPLATE_ONLY"
SCRIPT_STATUS_BLOCKED = "REALIZED_PL_RESULT_BUCKET_UPDATE_GATE_INPUT_BLOCKED"

SAFETY_FLAGS = (
    "network_call_performed",
    "broker_network_call_performed",
    "broker_api_call_performed",
    "broker_call_performed",
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
    "next_allocation_authorized",
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
            "template": realized_pl_result_bucket_update_gate_template_v1(),
            "gate_only_not_bucket_mutator": True,
            "oanda_call_performed_here": False,
            "broker_call_performed_here": False,
            "runtime_state_written_here": False,
            "next_trade_authorized_here": False,
            "live_funding_authorized_here": False,
        }
        payload.update(_safety_flags())
        _print_json(payload)
        return 0

    samples = realized_pl_result_bucket_update_gate_samples_v1()
    selected = samples if args.sample == "all" else {args.sample: samples[args.sample]}
    decisions = {
        name: evaluate_realized_pl_result_bucket_update_gate_v1(
            sample["owner_run_exercise_decision"],
            sample.get("bucket_state"),
        )
        for name, sample in selected.items()
    }
    payload = {
        "script_status": SCRIPT_STATUS_PACKAGE,
        "packet_id": PACKET_ID,
        "dry_run": True,
        "json_only": True,
        "sample": args.sample,
        "gate_only_not_bucket_mutator": True,
        "oanda_call_performed_here": False,
        "broker_call_performed_here": False,
        "runtime_state_written_here": False,
        "next_trade_authorized_here": False,
        "live_funding_authorized_here": False,
        "decisions": decisions,
    }
    payload.update(_safety_flags())
    _print_json(payload)
    return 0


def _parser() -> argparse.ArgumentParser:
    sample_names = sorted(realized_pl_result_bucket_update_gate_samples_v1())
    parser = SanitizedArgumentParser(
        allow_abbrev=False,
        description=(
            "AIOS realized P/L result bucket update gate. Prints JSON only "
            "and performs no bucket mutation, broker/OANDA call, runtime "
            "state write, next-trade authorization, or live funding action."
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
    decision = evaluate_realized_pl_result_bucket_update_gate_v1(
        {
            "exercise_status": "UNSUPPORTED",
            "no_new_order_authorized": True,
            "no_bucket_update_performed": True,
            "no_live_funding_authorized": True,
        }
    )
    payload: dict[str, Any] = {
        "script_status": SCRIPT_STATUS_BLOCKED,
        "packet_id": PACKET_ID,
        "dry_run": True,
        "json_only": True,
        "blockers": list(blockers),
        "decision": decision,
        "gate_status": BUCKET_UPDATE_BLOCKED_UNSAFE_OR_INVALID,
        "oanda_call_performed_here": False,
        "broker_call_performed_here": False,
        "runtime_state_written_here": False,
        "next_trade_authorized_here": False,
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
