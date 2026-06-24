from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_first_trade_runbook_go_nogo_v1 import (  # noqa: E402
    evaluate_oanda_demo_first_trade_runbook_go_nogo_v1,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_go_nogo_template:
        _print_json(
            {
                "script_status": "FIRST_TRADE_GO_NOGO_TEMPLATE_ONLY",
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "template": _sanitized_template(),
            }
        )
        return 0

    decision = evaluate_oanda_demo_first_trade_runbook_go_nogo_v1(
        owner_command_result=_ready_owner_command_result(),
        broker_call_readiness_result=_ready_broker_call_result(),
        result_bucket_readiness_result=_ready_bucket_result(),
        runtime_readiness_context=_ready_runtime_context(),
        owner_go_nogo_confirmation=_ready_owner_confirmation(),
    )

    payload = {
        "script_status": "FIRST_TRADE_GO_NOGO_DRY_RUN_PACKAGE",
        "dry_run": True,
        "broker_network_call_performed": False,
        "order_placement_performed": False,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "decision": decision,
    }

    if args.print_runbook:
        _print_runbook_text(decision)
        print("JSON:")
        print(json.dumps(payload, sort_keys=True))
        return 0

    _print_json(payload)
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AIOS OANDA demo first-trade GO/NOGO runbook printer."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Print JSON runbook package only. This is the default behavior.",
    )
    parser.add_argument(
        "--print-runbook",
        action="store_true",
        help="Print concise human-readable checklist text plus JSON.",
    )
    parser.add_argument(
        "--print-go-nogo-template",
        action="store_true",
        help="Print a sanitized GO/NOGO input template.",
    )
    return parser


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
        "live_order_allowed": False,
        "autonomous_order_allowed": False,
        "execution_authority": _execution_authority_false(),
    }


def _ready_bucket_result() -> dict:
    return {
        "status": "BUCKET_UPDATE_READY",
        "recommendation": {
            "next_trade_requires_owner_approval": True,
            "live_allocation_allowed": False,
            "autonomous_compounding_allowed": False,
        },
        "execution_authority": _execution_authority_false(),
    }


def _ready_runtime_context() -> dict:
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
        "existing_open_orders": 0,
        "existing_pending_orders": 0,
        "kill_switch_ready": True,
        "daily_stop_ready": True,
        "max_loss_gate_ready": True,
        "stop_loss_ready": True,
        "take_profit_ready": True,
        "pre_trade_evidence_ready": True,
        "post_trade_evidence_plan_ready": True,
        "owner_present_for_manual_run": True,
    }


def _ready_owner_confirmation() -> dict:
    return {
        "owner_confirmed_go_nogo_reviewed": True,
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
    }


def _sanitized_template() -> dict:
    return {
        "owner_command_result": {
            "status": "OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND",
            "final_owner_command": "owner_command_package_from_prior_layer",
            "execution_authority": _execution_authority_false(),
        },
        "broker_call_readiness_result": {
            "status": (
                "BROKER_CALL_DRY_RUN_READY | "
                "BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED"
            ),
            "live_order_allowed": False,
            "autonomous_order_allowed": False,
            "execution_authority": _execution_authority_false(),
        },
        "result_bucket_readiness_result": {
            "status": "BUCKET_UPDATE_READY",
            "recommendation": {
                "next_trade_requires_owner_approval": True,
                "live_allocation_allowed": False,
                "autonomous_compounding_allowed": False,
            },
            "execution_authority": _execution_authority_false(),
        },
        "runtime_readiness_context": _ready_runtime_context(),
        "owner_go_nogo_confirmation": _ready_owner_confirmation(),
    }


def _print_runbook_text(decision: dict) -> None:
    print("AIOS OANDA DEMO FIRST TRADE GO/NOGO RUNBOOK")
    print(f"GO/NOGO: {decision['go_nogo']}")
    print("PRE-RUN CHECKLIST:")
    for item in decision["pre_run_checklist"]["items"]:
        print(f"- {item}")
    print("POST-RUN EVIDENCE CHECKLIST:")
    for item in decision["post_run_evidence_checklist"]["items"]:
        print(f"- {item}")
    print("KILL SWITCH:")
    print(f"- ready: {decision['kill_switch_plan']['ready']}")
    print("RISK CONTROLS:")
    print(f"- one_order_only: {decision['risk_controls']['one_order_only']}")
    print("- Codex must not run the owner command.")


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
