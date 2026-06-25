from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_owner_run_closed_result_adapter_exercise_v1 import (  # noqa: E402
    ADAPTED_BLOCKED_INVALID_EVIDENCE,
    PACKET_ID,
    blocked_oanda_owner_run_closed_result_adapter_exercise_v1,
    evaluate_oanda_owner_run_closed_result_adapter_exercise_v1,
    oanda_owner_run_closed_result_adapter_exercise_default_samples_v1,
    oanda_owner_run_closed_result_adapter_exercise_template_v1,
)


SCRIPT_STATUS_PACKAGE = (
    "OANDA_OWNER_RUN_CLOSED_RESULT_ADAPTER_EXERCISE_DRY_RUN_SAMPLES"
)
SCRIPT_STATUS_TEMPLATE = (
    "OANDA_OWNER_RUN_CLOSED_RESULT_ADAPTER_EXERCISE_TEMPLATE_ONLY"
)
SCRIPT_STATUS_INPUT_EVALUATED = (
    "OANDA_OWNER_RUN_CLOSED_RESULT_ADAPTER_EXERCISE_INPUT_JSON_EVALUATED"
)
SCRIPT_STATUS_INPUT_BLOCKED = (
    "OANDA_OWNER_RUN_CLOSED_RESULT_ADAPTER_EXERCISE_INPUT_JSON_BLOCKED"
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
            "packet_id": PACKET_ID,
            "dry_run": True,
            "sanitized_json_only": True,
            "template": oanda_owner_run_closed_result_adapter_exercise_template_v1(),
            "oanda_capture_run_here": False,
            "vault_read_performed_here": False,
            "dotenv_or_env_read_here": False,
            "raw_input_persisted_here": False,
        }
        payload.update(_safety_flags())
        _print_json(payload)
        return 0

    if args.input_json:
        loaded, blockers = _load_owner_input_json(args.input_json)
        if blockers:
            payload = _blocked_script_payload(blockers)
            _print_json(payload)
            return 1

        decision = evaluate_oanda_owner_run_closed_result_adapter_exercise_v1(loaded)
        blocked = decision["exercise_status"] == "OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID"
        payload = {
            "script_status": SCRIPT_STATUS_INPUT_BLOCKED
            if blocked
            else SCRIPT_STATUS_INPUT_EVALUATED,
            "packet_id": PACKET_ID,
            "dry_run": True,
            "sanitized_json_only": True,
            "input_json_source": "owner_supplied_local_json",
            "raw_input_persisted_here": False,
            "decision": decision,
            "oanda_capture_run_here": False,
            "vault_read_performed_here": False,
            "dotenv_or_env_read_here": False,
        }
        payload.update(_safety_flags())
        _print_json(payload)
        return 1 if blocked else 0

    samples = oanda_owner_run_closed_result_adapter_exercise_default_samples_v1()
    selected = samples if args.sample == "all" else {args.sample: samples[args.sample]}
    decisions = {
        name: evaluate_oanda_owner_run_closed_result_adapter_exercise_v1(sample)
        for name, sample in selected.items()
    }
    payload = {
        "script_status": SCRIPT_STATUS_PACKAGE,
        "packet_id": PACKET_ID,
        "dry_run": True,
        "sample": args.sample,
        "sanitized_json_only": True,
        "exercise_only_not_broker_caller": True,
        "exercise_only_not_oanda_caller": True,
        "exercise_only_not_order_closer": True,
        "exercise_only_not_bucket_updater": True,
        "exercise_only_not_next_trade_authorizer": True,
        "exercise_only_not_scheduler_or_daemon": True,
        "oanda_capture_run_here": False,
        "vault_read_performed_here": False,
        "dotenv_or_env_read_here": False,
        "raw_input_persisted_here": False,
        "decisions": decisions,
    }
    payload.update(_safety_flags())
    _print_json(payload)
    return 0


def _parser() -> argparse.ArgumentParser:
    sample_names = sorted(
        oanda_owner_run_closed_result_adapter_exercise_default_samples_v1()
    )
    parser = SanitizedArgumentParser(
        allow_abbrev=False,
        description=(
            "AIOS OANDA owner-run sanitized closed-result adapter exercise. "
            "Prints JSON only and performs no OANDA capture, broker, vault, "
            "env, order, bucket, scheduler, daemon, or live funding action."
        ),
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--print-template", action="store_true")
    mode.add_argument(
        "--input-json",
        metavar="PATH",
        help="Owner-supplied sanitized local JSON object to evaluate.",
    )
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument(
        "--sample",
        choices=["all", *sample_names],
        default="all",
        help="Sanitized built-in owner-run sample to exercise.",
    )
    return parser


class SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        payload = _blocked_script_payload(["unsupported_or_invalid_argument"])
        payload["argument_error"] = "unsupported_or_invalid_argument"
        _print_json(payload)
        raise SystemExit(2)


def _load_owner_input_json(path_text: str) -> tuple[dict[str, Any] | None, list[str]]:
    path = Path(path_text)
    if _blocked_input_path(path):
        return None, ["input_json_path_blocked_before_read"]
    if not path.is_file():
        return None, ["input_json_missing_file"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None, ["input_json_read_failed"]
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None, ["input_json_invalid_json"]
    if not isinstance(payload, dict):
        return None, ["input_json_must_be_json_object"]
    return payload, []


def _blocked_input_path(path: Path) -> bool:
    parts = [part.lower() for part in path.parts]
    name = path.name.lower()
    return (
        name == ".env"
        or name.startswith(".env.")
        or "credentials" in parts
        or "credential" in name
    )


def _blocked_script_payload(blockers: Sequence[str]) -> dict[str, Any]:
    decision = blocked_oanda_owner_run_closed_result_adapter_exercise_v1(
        blockers=blockers,
        warnings=["cli_rejected_input_before_owner_run_adapter_exercise"],
        adapter_status=ADAPTED_BLOCKED_INVALID_EVIDENCE,
    )
    payload: dict[str, Any] = {
        "script_status": SCRIPT_STATUS_INPUT_BLOCKED,
        "packet_id": PACKET_ID,
        "dry_run": True,
        "sanitized_json_only": True,
        "blockers": list(blockers),
        "decision": decision,
        "oanda_capture_run_here": False,
        "vault_read_performed_here": False,
        "dotenv_or_env_read_here": False,
        "raw_input_persisted_here": False,
    }
    payload.update(_safety_flags())
    return payload


def _safety_flags() -> dict[str, bool]:
    return {field: False for field in SAFETY_FLAGS}


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
