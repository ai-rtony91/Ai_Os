from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_runtime_http_transport_one_order_owner_run_v1 import (  # noqa: E402
    TRANSPORT_ATTEMPTED_OANDA_DEMO_ORDER_ONCE,
    evaluate_oanda_demo_runtime_http_transport_one_order_owner_run_v1,
    post_oanda_demo_order_with_urllib,
)


REQUIRED_EXECUTE_CONFIRMATIONS = {
    "i_confirm_transport_reviewed": "--i-confirm-transport-reviewed",
    "i_confirm_actual_demo_order_intent": (
        "--i-confirm-actual-demo-order-intent"
    ),
    "i_understand_demo_only": "--i-understand-demo-only",
    "i_understand_one_order_only": "--i-understand-one-order-only",
    "i_understand_loss_possible": "--i-understand-loss-possible",
    "i_understand_no_profit_guarantee": "--i-understand-no-profit-guarantee",
    "i_confirm_stop_loss": "--i-confirm-stop-loss",
    "i_confirm_take_profit": "--i-confirm-take-profit",
    "i_confirm_no_second_order": "--i-confirm-no-second-order",
    "i_confirm_post_trade_evidence": "--i-confirm-post-trade-evidence",
    "i_confirm_kill_switch_ready": "--i-confirm-kill-switch-ready",
    "i_confirm_runtime_credentials_external": (
        "--i-confirm-runtime-credentials-external"
    ),
}

REQUIRED_EXECUTE_ORDER_ARGS = (
    "instrument",
    "direction",
    "units",
    "stop_loss",
    "take_profit",
    "risk_amount",
    "client_order_id",
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_template:
        _print_json(
            {
                "script_status": "RUNTIME_HTTP_TRANSPORT_TEMPLATE_ONLY",
                "dry_run": True,
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "template": _runtime_input_template(),
            }
        )
        return 0

    if not args.execute_transport:
        decision = evaluate_oanda_demo_runtime_http_transport_one_order_owner_run_v1(
            actual_owner_command_result=_ready_actual_owner_command_result(),
            broker_call_result=_ready_broker_call_result(),
            transport_context=_ready_transport_context(),
            sanitized_order_payload=_order_payload_from_args(args),
            owner_transport_confirmation=_owner_confirmation_ready(),
        )
        _print_json(
            {
                "script_status": "RUNTIME_HTTP_TRANSPORT_DRY_RUN_PREVIEW",
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
        flag
        for attr, flag in REQUIRED_EXECUTE_CONFIRMATIONS.items()
        if not getattr(args, attr)
    ]
    if missing_confirmations:
        decision = evaluate_oanda_demo_runtime_http_transport_one_order_owner_run_v1()
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

    access_token = os.environ.get("OANDA_DEMO_ACCESS_TOKEN")
    account_id = os.environ.get("OANDA_DEMO_ACCOUNT_ID")
    credential_read_performed = bool(access_token)
    account_id_read_performed = bool(account_id)

    if not access_token or not account_id:
        decision = evaluate_oanda_demo_runtime_http_transport_one_order_owner_run_v1(
            actual_owner_command_result=_ready_actual_owner_command_result(),
            broker_call_result=_ready_broker_call_result(),
            transport_context=_ready_transport_context(),
            sanitized_order_payload=_order_payload_from_args(args),
            owner_transport_confirmation=_owner_confirmation_from_confirmations(),
            execute_transport=True,
            runtime_access_token=access_token,
            runtime_account_id=account_id,
            http_post_callable=post_oanda_demo_order_with_urllib,
        )
        _print_json(
            {
                "script_status": "TRANSPORT_BLOCKED_RUNTIME_CREDENTIALS_MISSING",
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "credential_read_performed": credential_read_performed,
                "account_id_read_performed": account_id_read_performed,
                "decision": decision,
            }
        )
        return 1

    missing_order_args = [
        field for field in REQUIRED_EXECUTE_ORDER_ARGS if getattr(args, field) is None
    ]
    if missing_order_args:
        decision = evaluate_oanda_demo_runtime_http_transport_one_order_owner_run_v1(
            actual_owner_command_result=_ready_actual_owner_command_result(),
            broker_call_result=_ready_broker_call_result(),
            transport_context=_ready_transport_context(),
            sanitized_order_payload={},
            owner_transport_confirmation=_owner_confirmation_from_confirmations(),
        )
        _print_json(
            {
                "script_status": "BLOCKED_MISSING_REQUIRED_ORDER_ARGS",
                "missing_order_args": missing_order_args,
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "credential_read_performed": credential_read_performed,
                "account_id_read_performed": account_id_read_performed,
                "decision": decision,
            }
        )
        return 1

    decision = evaluate_oanda_demo_runtime_http_transport_one_order_owner_run_v1(
        actual_owner_command_result=_ready_actual_owner_command_result(),
        broker_call_result=_ready_broker_call_result(),
        transport_context=_ready_transport_context(),
        sanitized_order_payload=_order_payload_from_args(args),
        owner_transport_confirmation=_owner_confirmation_from_confirmations(),
        execute_transport=True,
        runtime_access_token=access_token,
        runtime_account_id=account_id,
        http_post_callable=post_oanda_demo_order_with_urllib,
    )
    _print_json(
        {
            "script_status": decision["status"],
            "broker_network_call_performed": decision["transport_attempt"][
                "network_call_performed"
            ],
            "order_placement_performed": decision["transport_attempt"][
                "order_placement_performed"
            ],
            "credential_read_performed": credential_read_performed,
            "account_id_read_performed": account_id_read_performed,
            "decision": decision,
        }
    )
    return 0 if decision["status"] == TRANSPORT_ATTEMPTED_OANDA_DEMO_ORDER_ONCE else 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AIOS OANDA demo runtime HTTP transport owner-run shell."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Print a sanitized JSON preview only. This is the default behavior.",
    )
    parser.add_argument(
        "--print-template",
        action="store_true",
        help="Print required external runtime inputs without reading secrets.",
    )
    parser.add_argument(
        "--execute-transport",
        action="store_true",
        help="Attempt one OANDA demo HTTP transport call only with all confirmations.",
    )
    parser.add_argument("--instrument")
    parser.add_argument("--direction", choices=("BUY", "SELL"))
    parser.add_argument("--units", type=float)
    parser.add_argument("--stop-loss", dest="stop_loss")
    parser.add_argument("--take-profit", dest="take_profit")
    parser.add_argument("--risk-amount", dest="risk_amount", type=float)
    parser.add_argument("--client-order-id", dest="client_order_id")
    parser.add_argument("--reward-risk-ratio", dest="reward_risk_ratio", type=float, default=1.0)
    parser.add_argument("--order-type", dest="order_type", choices=("MARKET", "LIMIT", "STOP"), default="MARKET")
    parser.add_argument("--i-confirm-transport-reviewed", action="store_true")
    parser.add_argument("--i-confirm-actual-demo-order-intent", action="store_true")
    parser.add_argument("--i-understand-demo-only", action="store_true")
    parser.add_argument("--i-understand-one-order-only", action="store_true")
    parser.add_argument("--i-understand-loss-possible", action="store_true")
    parser.add_argument("--i-understand-no-profit-guarantee", action="store_true")
    parser.add_argument("--i-confirm-stop-loss", action="store_true")
    parser.add_argument("--i-confirm-take-profit", action="store_true")
    parser.add_argument("--i-confirm-no-second-order", action="store_true")
    parser.add_argument("--i-confirm-post-trade-evidence", action="store_true")
    parser.add_argument("--i-confirm-kill-switch-ready", action="store_true")
    parser.add_argument("--i-confirm-runtime-credentials-external", action="store_true")
    return parser


def _runtime_input_template() -> dict:
    return {
        "runtime_environment_variables": {
            "OANDA_DEMO_ACCESS_TOKEN": "externally supplied at owner runtime",
            "OANDA_DEMO_ACCOUNT_ID": "externally supplied at owner runtime",
            "credential_persistence_allowed": False,
            "account_id_persistence_allowed": False,
            "script_reads_dotenv": False,
        },
        "order_args": {
            "--instrument": "EUR_USD",
            "--direction": "BUY or SELL",
            "--units": "positive_number",
            "--stop-loss": "required_price",
            "--take-profit": "required_price",
            "--risk-amount": "positive_number",
            "--client-order-id": "AIOS-DEMO-ONE-ORDER-001",
            "--reward-risk-ratio": "default_1.0",
            "--order-type": "default_MARKET",
        },
        "required_confirmations": list(REQUIRED_EXECUTE_CONFIRMATIONS.values()),
        "transport": {
            "demo_api_base_url": "https://api-fxpractice.oanda.com",
            "live_api_base_url_allowed": False,
            "one_order_only": True,
            "max_order_attempts": 1,
        },
    }


def _ready_actual_owner_command_result() -> dict:
    return {
        "status": "ACTUAL_RUN_READY_FOR_OWNER_MANUAL_COMMAND",
        "final_manual_command_package": {
            "ready": True,
            "one_order_only": True,
            "max_order_attempts": 1,
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


def _ready_transport_context() -> dict:
    return {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "demo_endpoint_only": True,
        "live_endpoint_absent": True,
        "demo_api_base_url": "https://api-fxpractice.oanda.com",
        "live_api_base_url": "",
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


def _order_payload_from_args(args: argparse.Namespace) -> dict:
    return {
        "instrument": args.instrument or "EUR_USD",
        "direction": args.direction or "BUY",
        "order_type": args.order_type or "MARKET",
        "units": args.units if args.units is not None else 1,
        "stop_loss": args.stop_loss if args.stop_loss is not None else "1.0",
        "take_profit": args.take_profit if args.take_profit is not None else "1.1",
        "risk_amount": args.risk_amount if args.risk_amount is not None else 1.0,
        "reward_risk_ratio": args.reward_risk_ratio,
        "client_order_id": args.client_order_id or "AIOS-DEMO-ONE-ORDER-001",
    }


def _owner_confirmation_ready() -> dict:
    return {
        "owner_confirmed_transport_reviewed": True,
        "owner_confirmed_actual_demo_order_intent": True,
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


def _owner_confirmation_from_confirmations() -> dict:
    return _owner_confirmation_ready()


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
