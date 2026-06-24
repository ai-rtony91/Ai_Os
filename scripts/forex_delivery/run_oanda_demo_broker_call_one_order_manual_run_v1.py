from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_broker_call_one_order_manual_run_v1 import (  # noqa: E402
    evaluate_oanda_demo_broker_call_one_order_manual_run_v1,
)


REQUIRED_EXECUTE_CONFIRMATIONS = {
    "i_approve_actual_oanda_demo_broker_call": (
        "--i-approve-actual-oanda-demo-broker-call"
    ),
    "i_understand_demo_only": "--i-understand-demo-only",
    "i_understand_one_order_only": "--i-understand-one-order-only",
    "i_understand_loss_possible": "--i-understand-loss-possible",
    "i_understand_no_profit_guarantee": "--i-understand-no-profit-guarantee",
    "i_confirm_stop_loss": "--i-confirm-stop-loss",
    "i_confirm_take_profit": "--i-confirm-take-profit",
    "i_confirm_no_second_order": "--i-confirm-no-second-order",
    "i_confirm_post_trade_evidence": "--i-confirm-post-trade-evidence",
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_template:
        _print_json(
            {
                "script_status": "BROKER_CALL_TEMPLATE_ONLY",
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "template": _runtime_input_template(),
            }
        )
        return 0

    if not args.execute_demo_order:
        decision = evaluate_oanda_demo_broker_call_one_order_manual_run_v1()
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
        decision = evaluate_oanda_demo_broker_call_one_order_manual_run_v1()
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

    decision = evaluate_oanda_demo_broker_call_one_order_manual_run_v1(
        final_owner_run_result=_ready_final_owner_run_result(),
        broker_call_context=_ready_broker_call_context(),
        sanitized_order_payload=_ready_order_payload(),
        owner_broker_call_approval=_owner_approval_from_confirmations(),
        execute_demo_order=True,
        http_transport=None,
    )
    _print_json(
        {
            "script_status": "BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED",
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
        description="AIOS OANDA demo one-order broker call manual-run safety shell."
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
        help="Print required external runtime inputs without reading secrets.",
    )
    parser.add_argument(
        "--execute-demo-order",
        action="store_true",
        help="Remain transport-blocked unless all confirmations are present.",
    )
    parser.add_argument("--i-approve-actual-oanda-demo-broker-call", action="store_true")
    parser.add_argument("--i-understand-demo-only", action="store_true")
    parser.add_argument("--i-understand-one-order-only", action="store_true")
    parser.add_argument("--i-understand-loss-possible", action="store_true")
    parser.add_argument("--i-understand-no-profit-guarantee", action="store_true")
    parser.add_argument("--i-confirm-stop-loss", action="store_true")
    parser.add_argument("--i-confirm-take-profit", action="store_true")
    parser.add_argument("--i-confirm-no-second-order", action="store_true")
    parser.add_argument("--i-confirm-post-trade-evidence", action="store_true")
    return parser


def _runtime_input_template() -> dict:
    return {
        "runtime_credentials": {
            "OANDA_DEMO_ACCESS_TOKEN": "externally supplied at runtime",
            "OANDA_DEMO_ACCOUNT_ID": "externally supplied at runtime",
            "credential_persistence_allowed": False,
            "account_id_persistence_allowed": False,
        },
        "order": {
            "instrument": "EUR_USD",
            "direction": "BUY",
            "units": 1,
            "stop_loss": "required",
            "take_profit": "required",
            "risk_amount": "required_positive_number",
            "client_order_id": "AIOS-DEMO-ONE-ORDER-001",
        },
        "transport": {
            "demo_api_base_url": "https://api-fxpractice.oanda.com",
            "transport_injection_required": True,
            "network_transport_enabled_in_this_script": False,
        },
        "safety": {
            "demo_only": True,
            "one_order_only": True,
            "max_order_attempts": 1,
            "live_trading_allowed": False,
            "autonomous_execution_allowed": False,
        },
    }


def _ready_final_owner_run_result() -> dict:
    return {
        "status": "OWNER_RUN_READY_FOR_EXPLICIT_MANUAL_COMMAND",
        "manual_runtime_run_contract": {
            "ready": True,
            "one_order_only": True,
            "max_order_attempts": 1,
            "actual_execution_requires_owner_to_run_command": True,
        },
        "execution_authority": _execution_authority_false(),
    }


def _ready_broker_call_context() -> dict:
    return {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "demo_environment": True,
        "live_environment": False,
        "demo_api_base_url": "https://api-fxpractice.oanda.com",
        "live_api_base_url": "",
        "runtime_access_token_present": True,
        "runtime_account_id_present": True,
        "token_runtime_only": True,
        "account_id_runtime_only": True,
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
        "pre_trade_evidence_ready": True,
        "post_trade_evidence_plan_ready": True,
        "broker_network_call_performed": False,
        "order_placement_performed": False,
    }


def _ready_order_payload() -> dict:
    return {
        "instrument": "EUR_USD",
        "direction": "BUY",
        "order_type": "MARKET",
        "units": 1,
        "stop_loss": 1.0,
        "take_profit": 1.1,
        "risk_amount": 1.0,
        "reward_risk_ratio": 1.0,
        "client_order_id": "AIOS-DEMO-ONE-ORDER-001",
    }


def _owner_approval_from_confirmations() -> dict:
    return {
        "owner_approved_actual_oanda_demo_broker_call": True,
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
