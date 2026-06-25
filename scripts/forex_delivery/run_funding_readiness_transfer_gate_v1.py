from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.funding_readiness_transfer_gate_v1 import (  # noqa: E402
    FUNDING_REVIEW_BLOCKED_UNSAFE_INPUT,
    PACKET_ID,
    evaluate_funding_readiness_transfer_gate_v1,
    funding_readiness_transfer_gate_samples_v1,
    funding_readiness_transfer_gate_template_v1,
)


SCRIPT_STATUS_PACKAGE = "FUNDING_READINESS_TRANSFER_GATE_DRY_RUN_SAMPLES"
SCRIPT_STATUS_TEMPLATE = "FUNDING_READINESS_TRANSFER_GATE_TEMPLATE_ONLY"
SCRIPT_STATUS_INPUT = "FUNDING_READINESS_TRANSFER_GATE_INPUT_EVALUATED"
SCRIPT_STATUS_BLOCKED = "FUNDING_READINESS_TRANSFER_GATE_INPUT_BLOCKED"

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

SAFETY_FLAGS = (
    "funding_transfer_authorized",
    "deposit_authorized",
    "withdrawal_authorized",
    "broker_call_authorized",
    "oanda_call_authorized",
    "order_placement_authorized",
    "live_trading_authorized",
    "runtime_mutation_authorized",
    "funding_transfer_performed",
    "money_transfer_performed",
    "deposit_performed",
    "withdrawal_performed",
    "bank_call_performed",
    "broker_call_performed",
    "oanda_call_performed",
    "order_placement_performed",
    "order_execution_performed",
    "live_trading_performed",
    "runtime_mutation_performed",
    "credential_read_performed",
    "network_call_performed",
    "scheduler_started",
    "daemon_started",
    "webhook_called",
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
            "template": funding_readiness_transfer_gate_template_v1(),
            "owner_review_only": True,
        }
        payload.update(_safety_flags())
        _print_json(payload)
        return 0

    if args.input_json:
        return _run_input_json(args.input_json)

    sample_name = args.sample or "all"
    samples = funding_readiness_transfer_gate_samples_v1()
    selected = samples if sample_name == "all" else {sample_name: samples[sample_name]}
    decisions = {
        name: _evaluate_payload(sample)
        for name, sample in selected.items()
    }
    payload = {
        "script_status": SCRIPT_STATUS_PACKAGE,
        "packet_id": PACKET_ID,
        "dry_run": True,
        "json_only": True,
        "sample": sample_name,
        "owner_review_only": True,
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

    result = _evaluate_payload(payload)
    output = {
        "script_status": SCRIPT_STATUS_INPUT,
        "packet_id": PACKET_ID,
        "dry_run": True,
        "json_only": True,
        "owner_review_only": True,
        "decision": result,
    }
    output.update(_safety_flags())
    _print_json(output)
    return 0


def _evaluate_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return evaluate_funding_readiness_transfer_gate_v1(
        funding_intent=payload.get("funding_intent"),
        account_separation=payload.get("account_separation"),
        bucket_gate_decision=payload.get("bucket_gate_decision"),
        next_trade_eligibility=payload.get("next_trade_eligibility"),
        risk_state=payload.get("risk_state"),
        owner_approval=payload.get("owner_approval"),
    )


def _parser() -> argparse.ArgumentParser:
    sample_names = sorted(funding_readiness_transfer_gate_samples_v1())
    parser = SanitizedArgumentParser(
        allow_abbrev=False,
        description=(
            "AIOS funding-readiness transfer gate. Prints JSON only and "
            "performs no broker/OANDA call, order placement, funding transfer, "
            "deposit, withdrawal, runtime mutation, scheduler, daemon, or webhook."
        ),
    )
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument(
        "--sample",
        choices=["all", *sample_names],
        default=None,
        help="Built-in sanitized gate sample to evaluate.",
    )
    parser.add_argument(
        "--input-json",
        metavar="PATH",
        help="Sanitized JSON input object with funding gate fields.",
    )
    return parser


class SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        payload = _blocked_script_payload(["unsupported_or_invalid_argument"])
        payload["argument_error"] = "unsupported_or_invalid_argument"
        _print_json(payload)
        raise SystemExit(2)


def _blocked_script_payload(blockers: Sequence[str]) -> dict[str, Any]:
    decision = evaluate_funding_readiness_transfer_gate_v1(
        funding_intent={
            "funding_intent_present": True,
            "funding_mode": "review_only",
            "proposed_amount": "1",
            "proposed_currency": "USD",
            "api_key": "sk-sample-unsafe-not-a-real-key",
        },
        account_separation=None,
        bucket_gate_decision=None,
        next_trade_eligibility=None,
        risk_state=None,
        owner_approval={"owner_approved_funding_review": False},
    )
    payload: dict[str, Any] = {
        "script_status": SCRIPT_STATUS_BLOCKED,
        "packet_id": PACKET_ID,
        "dry_run": True,
        "json_only": True,
        "blockers": list(blockers),
        "gate_status": FUNDING_REVIEW_BLOCKED_UNSAFE_INPUT,
        "decision": decision,
        "owner_review_only": True,
    }
    payload.update(_safety_flags())
    return payload


def _unsafe_path(path_text: str) -> bool:
    lowered = path_text.lower()
    return any(term in lowered for term in UNSAFE_PATH_TERMS)


def _safety_flags() -> dict[str, bool]:
    return {field: False for field in SAFETY_FLAGS}


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
