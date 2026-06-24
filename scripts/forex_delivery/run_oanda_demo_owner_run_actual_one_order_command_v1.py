from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_owner_run_actual_one_order_command_v1 import (  # noqa: E402
    evaluate_oanda_demo_owner_run_actual_one_order_command_v1,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    decision = evaluate_oanda_demo_owner_run_actual_one_order_command_v1(
        broker_call_result=_ready_broker_call_result(),
        owner_command_approval=_ready_owner_command_approval(),
        command_context=_ready_command_context(),
    )

    if args.print_command:
        _print_json(
            {
                "script_status": "OWNER_COMMAND_TEMPLATE_ONLY",
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "final_owner_command": decision["final_owner_command"],
            }
        )
        return 0

    if args.print_checklist:
        _print_json(
            {
                "script_status": "OWNER_COMMAND_CHECKLIST_ONLY",
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "manual_pre_run_checklist": decision["manual_pre_run_checklist"],
                "manual_post_run_evidence_checklist": decision[
                    "manual_post_run_evidence_checklist"
                ],
            }
        )
        return 0

    _print_json(
        {
            "script_status": "OWNER_COMMAND_DRY_RUN_PACKAGE",
            "dry_run": True,
            "broker_network_call_performed": False,
            "order_placement_performed": False,
            "credential_read_performed": False,
            "account_id_read_performed": False,
            "decision": decision,
        }
    )
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AIOS OANDA demo owner-run one-order command generator."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Print JSON command package only. This is the default behavior.",
    )
    parser.add_argument(
        "--print-command",
        action="store_true",
        help="Print the final owner command template only.",
    )
    parser.add_argument(
        "--print-checklist",
        action="store_true",
        help="Print the pre-run and post-run checklist only.",
    )
    return parser


def _ready_broker_call_result() -> dict:
    return {
        "status": "BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED",
        "network_call_performed": False,
        "order_placement_performed": False,
        "execution_attempt": {
            "network_call_performed": False,
            "order_placement_performed": False,
        },
        "execution_authority": _execution_authority_false(),
    }


def _ready_owner_command_approval() -> dict:
    return {
        "owner_approved_actual_one_order_command": True,
        "owner_confirmed_demo_only": True,
        "owner_confirmed_no_live_money": True,
        "owner_confirmed_one_order_only": True,
        "owner_confirmed_max_one_attempt": True,
        "owner_confirmed_stop_loss": True,
        "owner_confirmed_take_profit": True,
        "owner_confirmed_loss_possible": True,
        "owner_confirmed_no_profit_guarantee": True,
        "owner_confirmed_no_second_order": True,
        "owner_confirmed_manual_run_only": True,
        "owner_confirmed_no_autonomous_execution": True,
        "owner_confirmed_post_trade_evidence_required": True,
        "owner_confirmed_runtime_credentials_external": True,
    }


def _ready_command_context() -> dict:
    return {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "demo_endpoint_only": True,
        "live_endpoint_absent": True,
        "runtime_token_external": True,
        "runtime_account_id_external": True,
        "credential_persistence_detected": False,
        "account_id_persistence_detected": False,
        "one_order_only": True,
        "max_order_attempts": 1,
        "order_already_attempted": False,
        "kill_switch_ready": True,
        "daily_stop_ready": True,
        "max_loss_gate_ready": True,
        "pre_trade_evidence_ready": True,
        "post_trade_evidence_plan_ready": True,
    }


def _execution_authority_false() -> dict:
    return {
        "execution_allowed": False,
        "demo_order_allowed": False,
        "live_order_allowed": False,
        "broker_write_allowed": False,
        "autonomous_order_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
    }


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
