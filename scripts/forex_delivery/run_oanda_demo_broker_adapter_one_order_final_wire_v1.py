from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_broker_adapter_one_order_final_wire_v1 import (  # noqa: E402
    evaluate_oanda_demo_broker_adapter_one_order_final_wire_v1,
)


REQUIRED_EXECUTE_CONFIRMATIONS = {
    "i_understand_demo_only": "--i-understand-demo-only",
    "i_understand_one_order_only": "--i-understand-one-order-only",
    "i_understand_loss_possible": "--i-understand-loss-possible",
    "i_understand_no_profit_guarantee": "--i-understand-no-profit-guarantee",
    "i_confirm_stop_loss": "--i-confirm-stop-loss",
    "i_confirm_take_profit": "--i-confirm-take-profit",
    "i_confirm_no_second_order": "--i-confirm-no-second-order",
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    decision = evaluate_oanda_demo_broker_adapter_one_order_final_wire_v1()

    if args.print_template:
        _print_json(
            {
                "script_status": "TEMPLATE_ONLY",
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "template": _input_template(),
            }
        )
        return 0

    if not args.execute_demo_order:
        _print_json(
            {
                "script_status": "DRY_RUN_DECISION_ONLY",
                "dry_run": True,
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "decision": decision,
            }
        )
        return 0

    missing_confirmations = [
        flag for attr, flag in REQUIRED_EXECUTE_CONFIRMATIONS.items() if not getattr(args, attr)
    ]
    if missing_confirmations:
        _print_json(
            {
                "script_status": "BLOCKED_MISSING_REQUIRED_CONFIRMATIONS",
                "missing_confirmations": missing_confirmations,
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "decision": decision,
            }
        )
        return 1

    _print_json(
        {
            "script_status": "BLOCKED_PENDING_FINAL_OWNER_RUNTIME_RUN",
            "broker_network_call_performed": False,
            "order_placement_performed": False,
            "credential_read_performed": False,
            "account_id_read_performed": False,
            "decision": decision,
        }
    )
    return 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AIOS OANDA demo broker adapter one-order final wire safety shell."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Print JSON decision output only. This is the default behavior.",
    )
    parser.add_argument(
        "--print-template",
        action="store_true",
        help="Print a JSON input template without reading credentials or placing orders.",
    )
    parser.add_argument(
        "--execute-demo-order",
        action="store_true",
        help="Remain blocked unless all explicit confirmations are present.",
    )
    parser.add_argument("--i-understand-demo-only", action="store_true")
    parser.add_argument("--i-understand-one-order-only", action="store_true")
    parser.add_argument("--i-understand-loss-possible", action="store_true")
    parser.add_argument("--i-understand-no-profit-guarantee", action="store_true")
    parser.add_argument("--i-confirm-stop-loss", action="store_true")
    parser.add_argument("--i-confirm-take-profit", action="store_true")
    parser.add_argument("--i-confirm-no-second-order", action="store_true")
    return parser


def _input_template() -> dict:
    return {
        "runtime_exception_result": {
            "status": "EXCEPTION_READY_FOR_MANUAL_RUNTIME_DEMO_ORDER_ATTEMPT",
            "allowed_manual_runtime_invocation": True,
            "one_order_runtime_contract": {
                "one_order_only": True,
                "max_order_attempts": 1,
            },
            "execution_authority": {
                "execution_allowed": False,
                "demo_order_allowed": False,
                "live_order_allowed": False,
                "broker_write_allowed": False,
                "autonomous_order_allowed": False,
                "scheduler_allowed": False,
                "daemon_allowed": False,
                "webhook_allowed": False,
            },
        },
        "adapter_runtime_context": {
            "broker": "OANDA_DEMO",
            "environment": "DEMO",
            "demo_environment": True,
            "live_environment": False,
            "runtime_only_credentials_present": True,
            "credential_persistence_detected": False,
            "account_id_persistence_detected": False,
            "account_id_runtime_only": True,
            "token_runtime_only": True,
            "one_order_only": True,
            "max_order_attempts": 1,
            "existing_open_orders": 0,
            "existing_pending_orders": 0,
            "order_already_attempted": False,
            "kill_switch_ready": True,
            "daily_stop_ready": True,
            "max_loss_gate_ready": True,
            "broker_network_call_performed": False,
            "order_placement_performed": False,
            "manual_runtime_invocation_required": True,
        },
        "sanitized_order_payload": {
            "instrument": "EUR_USD",
            "direction": "BUY",
            "order_type": "MARKET",
            "units": 1,
            "stop_loss": 1.0,
            "take_profit": 1.1,
            "risk_amount": 1.0,
            "reward_risk_ratio": 1.0,
            "client_order_id": "AIOS-DEMO-ONE-ORDER-001",
        },
        "owner_final_wire_approval": {
            "owner_approved_final_manual_demo_order_attempt": True,
            "owner_confirmed_demo_only": True,
            "owner_confirmed_no_live_money": True,
            "owner_confirmed_one_order_only": True,
            "owner_confirmed_max_one_attempt": True,
            "owner_confirmed_stop_loss": True,
            "owner_confirmed_take_profit": True,
            "owner_confirmed_loss_possible": True,
            "owner_confirmed_no_profit_guarantee": True,
            "owner_confirmed_runtime_credentials_outside_repo": True,
            "owner_confirmed_manual_invocation_required": True,
            "owner_confirmed_no_autonomous_execution": True,
            "owner_confirmed_no_second_order": True,
        },
    }


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
