from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_readonly_closed_result_tpsl_classifier_adapter_v1 import (  # noqa: E402
    evaluate_oanda_readonly_closed_result_tpsl_classifier_adapter_v1,
    oanda_readonly_closed_result_tpsl_classifier_adapter_default_samples_v1,
    oanda_readonly_closed_result_tpsl_classifier_adapter_template_v1,
)


SCRIPT_STATUS_PACKAGE = (
    "OANDA_READONLY_CLOSED_RESULT_TPSL_CLASSIFIER_ADAPTER_DRY_RUN_SAMPLES"
)
SCRIPT_STATUS_TEMPLATE = (
    "OANDA_READONLY_CLOSED_RESULT_TPSL_CLASSIFIER_ADAPTER_TEMPLATE_ONLY"
)

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
            "dry_run": True,
            "sanitized_input_only": True,
            "adapter_only_not_broker_caller": True,
            "adapter_only_not_order_closer": True,
            "adapter_only_not_bucket_updater": True,
            "adapter_only_not_scheduler_or_daemon": True,
            "template": oanda_readonly_closed_result_tpsl_classifier_adapter_template_v1(),
        }
        payload.update(_safety_flags())
        _print_json(payload)
        return 0

    samples = oanda_readonly_closed_result_tpsl_classifier_adapter_default_samples_v1()
    selected = samples if args.sample == "all" else {args.sample: samples[args.sample]}
    decisions = {
        name: evaluate_oanda_readonly_closed_result_tpsl_classifier_adapter_v1(sample)
        for name, sample in selected.items()
    }
    payload = {
        "script_status": SCRIPT_STATUS_PACKAGE,
        "dry_run": True,
        "sample": args.sample,
        "sanitized_input_only": True,
        "adapter_only_not_broker_caller": True,
        "adapter_only_not_order_closer": True,
        "adapter_only_not_bucket_updater": True,
        "adapter_only_not_scheduler_or_daemon": True,
        "oanda_capture_run_here": False,
        "vault_read_performed_here": False,
        "dotenv_or_env_read_here": False,
        "decisions": decisions,
    }
    payload.update(_safety_flags())
    _print_json(payload)
    return 0


def _parser() -> argparse.ArgumentParser:
    sample_names = sorted(
        oanda_readonly_closed_result_tpsl_classifier_adapter_default_samples_v1()
    )
    parser = SanitizedArgumentParser(
        allow_abbrev=False,
        description=(
            "AIOS OANDA sanitized read-only closed-result TP/SL classifier "
            "adapter. Prints dry-run JSON only and performs no broker, vault, "
            "env, order, bucket, scheduler, or daemon action."
        ),
    )
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument(
        "--sample",
        choices=["all", *sample_names],
        default="all",
        help="Sanitized built-in capture sample to adapt and classify.",
    )
    return parser


class SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        payload = {
            "script_status": "BLOCKED_INVALID_ARGUMENTS",
            "argument_error": "unsupported_or_invalid_argument",
        }
        payload.update(_safety_flags())
        _print_json(payload)
        raise SystemExit(2)


def _safety_flags() -> dict[str, bool]:
    return {field: False for field in SAFETY_FLAGS}


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
