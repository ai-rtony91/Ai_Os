from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_first_trade_owner_manual_execution_window_v1 import (  # noqa: E402
    evaluate_oanda_demo_first_trade_owner_manual_execution_window_v1,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    decision = evaluate_oanda_demo_first_trade_owner_manual_execution_window_v1(
        go_nogo_result=_ready_go_nogo_result(),
        owner_command_result=_ready_owner_command_result(),
        execution_window_context=_ready_execution_window_context(),
        owner_execution_window_confirmation=_ready_owner_confirmation(),
    )

    if args.print_final_checklist:
        _print_final_checklist(decision)
        return 0

    if args.print_owner_command_reminder:
        _print_owner_command_reminder()
        return 0

    payload = {
        "script_status": "FIRST_TRADE_EXECUTION_WINDOW_DRY_RUN_PACKAGE",
        "dry_run": True,
        "broker_network_call_performed": False,
        "order_placement_performed": False,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "decision": decision,
    }

    if args.print_window:
        _print_window_text(decision)
        print("JSON:")
        print(json.dumps(payload, sort_keys=True))
        return 0

    _print_json(payload)
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AIOS OANDA demo owner manual execution-window printer."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Print JSON execution-window package only. This is the default.",
    )
    parser.add_argument(
        "--print-window",
        action="store_true",
        help="Print concise human-readable execution window plus JSON.",
    )
    parser.add_argument(
        "--print-final-checklist",
        action="store_true",
        help="Print final pre-execution and post-execution checklist text.",
    )
    parser.add_argument(
        "--print-owner-command-reminder",
        action="store_true",
        help="Print sanitized owner command reminder with placeholders only.",
    )
    return parser


def _ready_go_nogo_result() -> dict:
    return {
        "status": "RUNBOOK_GO_READY_FOR_OWNER_MANUAL_DEMO_ATTEMPT",
        "go_nogo": "GO",
        "next_safe_action": "owner_may_run_first_demo_order_command_once",
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


def _ready_execution_window_context() -> dict:
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
        "execution_window_minutes": 30,
        "market_open_or_owner_override": True,
    }


def _ready_owner_confirmation() -> dict:
    return {
        "owner_confirmed_execution_window_reviewed": True,
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
    }


def _print_window_text(decision: dict) -> None:
    package = decision["execution_window_package"]
    print("AIOS OANDA DEMO OWNER MANUAL EXECUTION WINDOW")
    print(f"STATUS: {decision['status']}")
    print(f"READY: {package['ready']}")
    print(f"WINDOW MINUTES: {package['execution_window_minutes']}")
    print("ONE ORDER ONLY: true")
    print("CODEX MUST NOT RUN THE OWNER COMMAND")


def _print_final_checklist(decision: dict) -> None:
    print("FINAL PRE-EXECUTION CHECKLIST:")
    for item in decision["final_pre_execution_checklist"]["items"]:
        print(f"- {item}")
    print("FINAL POST-EXECUTION EVIDENCE PATH:")
    for item in decision["final_post_execution_evidence_path"]["items"]:
        print(f"- {item}")


def _print_owner_command_reminder() -> None:
    print("OWNER COMMAND REMINDER")
    print("Use the prior owner command package only after WINDOW READY.")
    print("Runtime access value placeholder: <OANDA_DEMO_ACCESS_VALUE_RUNTIME_ONLY>")
    print("Runtime demo account placeholder: <OANDA_DEMO_ACCOUNT_RUNTIME_ONLY>")
    print("Order placeholders: <instrument> <BUY_OR_SELL> <units>")
    print("Protection placeholders: <stop_loss> <take_profit> <risk_amount>")
    print("Run once only, then stop for sanitized evidence capture.")
    print("Codex must not execute this command.")


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
