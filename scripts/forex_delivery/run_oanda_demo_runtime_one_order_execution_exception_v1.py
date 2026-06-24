from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_runtime_one_order_execution_exception_v1 import (  # noqa: E402
    evaluate_oanda_demo_runtime_one_order_execution_exception_v1,
)


REQUIRED_EXECUTE_CONFIRMATIONS = {
    "i_understand_demo_only": "--i-understand-demo-only",
    "i_understand_one_order_only": "--i-understand-one-order-only",
    "i_understand_loss_possible": "--i-understand-loss-possible",
    "i_understand_no_profit_guarantee": "--i-understand-no-profit-guarantee",
    "i_confirm_stop_loss": "--i-confirm-stop-loss",
    "i_confirm_take_profit": "--i-confirm-take-profit",
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    decision = evaluate_oanda_demo_runtime_one_order_execution_exception_v1()

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
            "script_status": "BLOCKED_PENDING_BROKER_ADAPTER_IMPLEMENTATION",
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
        description="AIOS OANDA demo one-order runtime exception safety shell."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Print JSON decision output only. This is the default behavior.",
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
    return parser


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
