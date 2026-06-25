from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.owner_gonogo_command_center_report_v1 import (  # noqa: E402
    OWNER_GONOGO_BLOCKED_UNSAFE_INPUT,
    PACKET_ID,
    SAFETY_AUTHORITY_FIELDS,
    build_owner_gonogo_command_center_report_v1,
    owner_gonogo_command_center_report_samples_v1,
    owner_gonogo_command_center_report_template_v1,
)


SCRIPT_STATUS_PACKAGE = "OWNER_GONOGO_COMMAND_CENTER_REPORT_DRY_RUN_SAMPLES"
SCRIPT_STATUS_TEMPLATE = "OWNER_GONOGO_COMMAND_CENTER_REPORT_TEMPLATE_ONLY"
SCRIPT_STATUS_INPUT = "OWNER_GONOGO_COMMAND_CENTER_REPORT_INPUT_EVALUATED"
SCRIPT_STATUS_BLOCKED = "OWNER_GONOGO_COMMAND_CENTER_REPORT_INPUT_BLOCKED"

UNSAFE_PATH_TERMS = (
    ".env",
    "credential",
    "credentials",
    "secret",
    "token",
    "vault",
    "bitwarden",
    "yubikey",
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    selected_modes = sum(
        bool(value)
        for value in (args.print_template, args.sample is not None, args.input_json)
    )
    if selected_modes > 1:
        _print_json(_blocked_script_payload(["choose_one_cli_mode_only"]))
        return 2

    if args.print_template:
        payload = {
            "script_status": SCRIPT_STATUS_TEMPLATE,
            "packet_id": PACKET_ID,
            "dry_run": True,
            "json_only": True,
            "template": owner_gonogo_command_center_report_template_v1(),
            "report_only": True,
        }
        payload.update(_safety_flags())
        _print_json(payload)
        return 0

    if args.input_json:
        return _run_input_json(args.input_json)

    sample_name = args.sample or "all"
    samples = owner_gonogo_command_center_report_samples_v1()
    selected = samples if sample_name == "all" else {sample_name: samples[sample_name]}
    decisions = {name: _evaluate_payload(sample) for name, sample in selected.items()}
    payload = {
        "script_status": SCRIPT_STATUS_PACKAGE,
        "packet_id": PACKET_ID,
        "dry_run": True,
        "json_only": True,
        "sample": sample_name,
        "report_only": True,
        "decisions": decisions,
    }
    payload.update(_safety_flags())
    _print_json(payload)
    return 0


def _run_input_json(input_json: str) -> int:
    if _unsafe_path(input_json):
        _print_json(_blocked_script_payload(["unsafe_input_json_path_rejected"]))
        return 2

    path = Path(input_json)
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        _print_json(_blocked_script_payload(["input_json_read_or_parse_failed"]))
        return 2

    if not isinstance(payload, Mapping):
        _print_json(_blocked_script_payload(["input_json_root_must_be_object"]))
        return 2

    output = {
        "script_status": SCRIPT_STATUS_INPUT,
        "packet_id": PACKET_ID,
        "dry_run": True,
        "json_only": True,
        "report_only": True,
        "decision": _evaluate_payload(payload),
    }
    output.update(_safety_flags())
    _print_json(output)
    return 0


def _evaluate_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return build_owner_gonogo_command_center_report_v1(
        closed_result=payload.get("closed_result"),
        bucket_gate_decision=payload.get("bucket_gate_decision"),
        next_trade_eligibility=payload.get("next_trade_eligibility"),
        funding_readiness=payload.get("funding_readiness"),
        account_separation=payload.get("account_separation"),
        risk_state=payload.get("risk_state"),
        owner_context=payload.get("owner_context"),
    )


def _parser() -> argparse.ArgumentParser:
    sample_names = sorted(owner_gonogo_command_center_report_samples_v1())
    parser = SanitizedArgumentParser(
        allow_abbrev=False,
        description=(
            "AIOS owner go/no-go command center report. Prints JSON only and "
            "performs no broker/OANDA call, order placement, trade execution, "
            "funding transfer, bucket mutation, runtime mutation, scheduler, "
            "daemon, or webhook."
        ),
    )
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument(
        "--sample",
        choices=["all", *sample_names],
        default=None,
        help="Built-in sanitized command-center sample to evaluate.",
    )
    parser.add_argument(
        "--input-json",
        metavar="PATH",
        help="Sanitized JSON input object with owner go/no-go report fields.",
    )
    return parser


class SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        payload = _blocked_script_payload(["unsupported_or_invalid_argument"])
        payload["argument_error"] = "unsupported_or_invalid_argument"
        _print_json(payload)
        raise SystemExit(2)


def _blocked_script_payload(blockers: Sequence[str]) -> dict[str, Any]:
    decision = build_owner_gonogo_command_center_report_v1(
        closed_result={
            "exercise_status": "OWNER_RUN_CLOSED_BY_TAKE_PROFIT",
            "api_key": "sk-sample-unsafe-not-a-real-key",
        },
        bucket_gate_decision=None,
        next_trade_eligibility=None,
        funding_readiness=None,
        account_separation=None,
        risk_state=None,
        owner_context=None,
    )
    payload: dict[str, Any] = {
        "script_status": SCRIPT_STATUS_BLOCKED,
        "packet_id": PACKET_ID,
        "dry_run": True,
        "json_only": True,
        "blockers": list(blockers),
        "command_status": OWNER_GONOGO_BLOCKED_UNSAFE_INPUT,
        "decision": decision,
        "report_only": True,
    }
    payload.update(_safety_flags())
    return payload


def _unsafe_path(path_text: str) -> bool:
    lowered = path_text.lower()
    return any(term in lowered for term in UNSAFE_PATH_TERMS)


def _safety_flags() -> dict[str, bool]:
    return {field: False for field in SAFETY_AUTHORITY_FIELDS}


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
