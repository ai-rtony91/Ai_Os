from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_first_trade_actual_owner_command_run import (  # noqa: E402
    evaluate_oanda_demo_first_trade_actual_owner_command_run,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    decision = evaluate_oanda_demo_first_trade_actual_owner_command_run(
        execution_window_result=_ready_execution_window_result(),
        owner_command_result=_ready_owner_command_result(),
        broker_call_result=_ready_broker_call_result(),
        actual_run_context=_ready_actual_run_context(),
        owner_actual_run_confirmation=_ready_owner_confirmation(),
    )

    if args.print_command:
        print(decision["final_manual_command_package"]["command_text"])
        return 0

    if args.print_final_warning:
        _print_final_warning(decision)
        return 0

    _print_json(
        {
            "script_status": "ACTUAL_OWNER_COMMAND_DRY_RUN_PACKAGE",
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
        description="AIOS OANDA demo final actual owner command package printer."
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
        help="Print the exact owner command template with placeholders.",
    )
    parser.add_argument(
        "--print-final-warning",
        action="store_true",
        help="Print final one-order risk warning and evidence checklist.",
    )
    return parser


def _ready_execution_window_result() -> dict:
    return {
        "status": "WINDOW_READY_FOR_OWNER_MANUAL_DEMO_EXECUTION",
        "execution_window_package": {
            "ready": True,
            "one_order_only": True,
            "max_order_attempts": 1,
            "actual_order_requires_owner_manual_command": True,
        },
        "execution_authority": _execution_authority_false(),
    }


def _ready_owner_command_result() -> dict:
    return {
        "status": "OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND",
        "final_owner_command": {
            "ready": True,
            "command_type": "powershell",
            "script_path": (
                "scripts/forex_delivery/"
                "run_oanda_demo_broker_call_one_order_manual_run_v1.py"
            ),
            "command_text": "OWNER_RUNTIME_COMMAND_AVAILABLE_OUTSIDE_CODEX",
        },
        "execution_authority": _execution_authority_false(),
    }


def _ready_broker_call_result() -> dict:
    return {
        "status": "BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED",
        "network_call_performed": False,
        "order_placement_performed": False,
        "execution_authority": _execution_authority_false(),
    }


def _ready_actual_run_context() -> dict:
    return {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "demo_endpoint_only": True,
        "live_endpoint_absent": True,
        "runtime_token_external": True,
        "runtime_account_id_external": True,
        "runtime_credentials_available_to_owner": True,
        "credential_persistence_detected": False,
        "account_id_persistence_detected": False,
        "one_order_only": True,
        "max_order_attempts": 1,
        "order_already_attempted": False,
        "existing_open_orders": 0,
        "existing_pending_orders": 0,
        "owner_present_for_manual_run": True,
        "kill_switch_ready": True,
        "daily_stop_ready": True,
        "max_loss_gate_ready": True,
        "stop_loss_ready": True,
        "take_profit_ready": True,
        "pre_trade_evidence_ready": True,
        "post_trade_evidence_plan_ready": True,
        "execution_window_open": True,
        "market_open_or_owner_override": True,
    }


def _ready_owner_confirmation() -> dict:
    return {
        "owner_confirmed_actual_command_reviewed": True,
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
        "owner_confirmed_post_trade_evidence_required": True,
        "owner_confirmed_kill_switch_ready": True,
        "owner_confirmed_runtime_credentials_external": True,
        "owner_confirmed_ready_to_press_manual_demo_button": True,
    }


def _print_final_warning(decision: dict) -> None:
    print("FINAL ONE-ORDER RISK WARNING")
    print("Run exactly one OANDA DEMO order attempt only if every gate remains ready.")
    print("Do not use live money. Loss is possible. Profit is not guaranteed.")
    print("Do not rerun the command after one attempt.")
    print("Codex must not execute the command or call OANDA.")
    print("EVIDENCE CHECKLIST:")
    for item in decision["final_evidence_requirements"]["items"]:
        print(f"- {item}")


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
