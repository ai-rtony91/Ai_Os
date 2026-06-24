from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_one_trade_readiness_v1 import (  # noqa: E402
    READINESS_FIELDS,
    default_oanda_demo_one_trade_readiness_context_v1,
    evaluate_oanda_demo_one_trade_readiness_v1,
)


CONFIRMATION_ATTRS = {
    "demo_only_confirmed": "--i-confirm-demo-only",
    "read_only_preflight_passed": "--i-confirm-read-only-preflight-passed",
    "owner_runtime_command_required": "--i-confirm-owner-runtime-command-required",
    "broker_call_not_performed_by_codex": (
        "--i-confirm-codex-broker-call-not-performed"
    ),
    "instrument_allowed": "--i-confirm-instrument-allowed",
    "eur_usd_available": "--i-confirm-eur-usd-available",
    "direction_allowed": "--i-confirm-direction-allowed",
    "micro_units_present": "--i-confirm-micro-units-present",
    "stop_loss_present": "--i-confirm-stop-loss-present",
    "take_profit_present": "--i-confirm-take-profit-present",
    "max_loss_gate_passed": "--i-confirm-max-loss-gate-passed",
    "daily_stop_gate_passed": "--i-confirm-daily-stop-gate-passed",
    "kill_switch_state_passed": "--i-confirm-kill-switch-state-passed",
    "one_order_only_cap_available": "--i-confirm-one-order-only-cap-available",
    "post_trade_evidence_plan_present": (
        "--i-confirm-post-trade-evidence-plan-present"
    ),
    "result_bucket_plan_present": "--i-confirm-result-bucket-plan-present",
    "next_allocation_plan_present": "--i-confirm-next-allocation-plan-present",
    "compound_or_withdraw_decision_is_conditional": (
        "--i-confirm-compound-or-withdraw-conditional"
    ),
    "no_live_endpoint": "--i-confirm-no-live-endpoint",
    "no_scheduler_daemon_webhook": "--i-confirm-no-scheduler-daemon-webhook",
    "no_profit_claim": "--i-confirm-no-profit-claim",
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_template:
        _print_json(_template_payload())
        return 0

    if not args.evaluate_readiness:
        _print_json(_template_payload())
        return 0

    readiness_context = {
        field: bool(getattr(args, field))
        for field in READINESS_FIELDS
    }
    decision = evaluate_oanda_demo_one_trade_readiness_v1(readiness_context)
    _print_json(_script_payload(decision))
    return 0 if decision["readiness_ready"] is True else 1


def _parser() -> argparse.ArgumentParser:
    parser = SanitizedArgumentParser(
        allow_abbrev=False,
        description="AIOS OANDA demo one-trade readiness evaluator.",
    )
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument("--evaluate-readiness", action="store_true")
    for attr, flag in CONFIRMATION_ATTRS.items():
        parser.add_argument(flag, dest=attr, action="store_true")
    return parser


class SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        _print_json(
            {
                "script_status": "BLOCKED_INVALID_ARGUMENTS",
                "argument_error": "unsupported_or_invalid_argument",
                "broker_call_performed_by_codex": False,
                "order_placement_performed": False,
                "orders_endpoint_called": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "credential_value_printed": False,
                "account_id_value_printed": False,
                "dotenv_read": False,
                "live_endpoint_used": False,
            }
        )
        raise SystemExit(2)


def _template_payload() -> dict[str, Any]:
    return {
        "script_status": "ONE_TRADE_READINESS_TEMPLATE_ONLY",
        "broker_call_performed_by_codex": False,
        "order_placement_performed": False,
        "orders_endpoint_called": False,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "credential_value_printed": False,
        "account_id_value_printed": False,
        "dotenv_read": False,
        "live_endpoint_used": False,
        "accepted_value_arguments": [],
        "required_non_secret_flags": [
            CONFIRMATION_ATTRS[field] for field in READINESS_FIELDS
        ],
        "default_context": default_oanda_demo_one_trade_readiness_context_v1(),
    }


def _script_payload(decision: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "script_status": decision.get("classification"),
        "classification": decision.get("classification"),
        "readiness_ready": decision.get("readiness_ready", False),
        "broker_call_performed_by_codex": False,
        "order_placement_performed": False,
        "orders_endpoint_called": False,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "credential_value_printed": False,
        "account_id_value_printed": False,
        "dotenv_read": False,
        "live_endpoint_used": False,
        "decision": decision,
    }


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
