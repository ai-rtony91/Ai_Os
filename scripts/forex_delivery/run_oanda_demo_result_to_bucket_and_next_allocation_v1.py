from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_result_to_bucket_and_next_allocation_v1 import (  # noqa: E402
    evaluate_oanda_demo_result_to_bucket_and_next_allocation_v1,
)


REQUIRED_BUCKET_CONFIRMATIONS = {
    "i_confirm_result_reviewed": "--i-confirm-result-reviewed",
    "i_confirm_demo_only_bucket_update": "--i-confirm-demo-only-bucket-update",
    "i_confirm_no_live_allocation": "--i-confirm-no-live-allocation",
    "i_confirm_next_trade_requires_approval": (
        "--i-confirm-next-trade-requires-approval"
    ),
    "i_confirm_no_autonomous_compounding": "--i-confirm-no-autonomous-compounding",
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_template:
        _print_json(
            {
                "script_status": "RESULT_TO_BUCKET_TEMPLATE_ONLY",
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "template": _sanitized_template(),
            }
        )
        return 0

    if args.evaluate_demo_result:
        missing_confirmations = [
            flag
            for attr, flag in REQUIRED_BUCKET_CONFIRMATIONS.items()
            if not getattr(args, attr)
        ]
        if missing_confirmations:
            _print_json(
                {
                    "script_status": "BLOCKED_MISSING_BUCKET_CONFIRMATIONS",
                    "missing_confirmations": missing_confirmations,
                    "broker_network_call_performed": False,
                    "order_placement_performed": False,
                    "credential_read_performed": False,
                    "account_id_read_performed": False,
                }
            )
            return 1

    decision = evaluate_oanda_demo_result_to_bucket_and_next_allocation_v1(
        post_trade_capture_result=_dry_run_capture_result(),
        bucket_state=_demo_bucket_state(),
        allocation_policy=_allocation_policy(),
        owner_bucket_confirmation=_owner_bucket_confirmation(),
    )
    _print_json(
        {
            "script_status": decision["status"]
            if args.evaluate_demo_result
            else "RESULT_TO_BUCKET_DRY_RUN_PACKAGE",
            "dry_run": args.evaluate_demo_result is False,
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
        description="AIOS OANDA demo result-to-bucket allocation safety shell."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Print JSON result-to-bucket package only. This is the default.",
    )
    parser.add_argument(
        "--print-template",
        action="store_true",
        help="Print sanitized result, bucket, and allocation template.",
    )
    parser.add_argument(
        "--evaluate-demo-result",
        action="store_true",
        help="Evaluate example dry-run evidence after owner confirmations.",
    )
    parser.add_argument("--i-confirm-result-reviewed", action="store_true")
    parser.add_argument("--i-confirm-demo-only-bucket-update", action="store_true")
    parser.add_argument("--i-confirm-no-live-allocation", action="store_true")
    parser.add_argument("--i-confirm-next-trade-requires-approval", action="store_true")
    parser.add_argument("--i-confirm-no-autonomous-compounding", action="store_true")
    return parser


def _sanitized_template() -> dict:
    return {
        "post_trade_capture_result": {
            "status": "EVIDENCE_CAPTURE_READY",
            "post_trade_classification": "DRY_RUN_ONLY | NO_FILL_REJECTED | OPEN_OR_PENDING | OPEN_POSITION | PROFIT | LOSS | BREAKEVEN",
            "normalized_evidence_package": {
                "realized_pl_when_closed": "number_or_null",
                "post_trade_classification": "sanitized_outcome",
            },
        },
        "bucket_state": {
            "bucket_currency": "USD",
            "starting_bucket_balance": "number_gte_zero",
            "current_bucket_balance": "number_gte_zero",
            "total_realized_pl": "number",
            "current_cycle_start_balance": "number_gt_zero",
            "current_cycle_realized_pl": "number",
            "cycle_profit_target_min_pct": "number_gt_zero",
            "cycle_profit_target_max_pct": "number_gte_min",
            "max_single_trade_risk_pct": "number_gt_zero_lte_five",
            "one_order_only": True,
            "demo_only": True,
            "live_trading": False,
        },
        "allocation_policy": {
            "allocation_mode": "PAUSE | CONTINUE_DEMO | REDUCE_RISK | INCREASE_EVIDENCE",
            "compounding_enabled": "boolean",
            "collect_profit_at_target": "boolean",
            "require_more_evidence_after_loss": "boolean",
            "require_owner_approval_for_next_trade": True,
            "max_next_trade_risk_pct": "number_gt_zero_lte_bucket_limit",
            "no_live_allocation": True,
        },
    }


def _dry_run_capture_result() -> dict:
    return {
        "status": "EVIDENCE_CAPTURE_READY",
        "post_trade_classification": "DRY_RUN_ONLY",
        "normalized_evidence_package": {
            "realized_pl_when_closed": None,
            "post_trade_classification": "DRY_RUN_ONLY",
        },
        "execution_authority": _execution_authority_false(),
    }


def _demo_bucket_state() -> dict:
    return {
        "bucket_currency": "USD",
        "starting_bucket_balance": 1000.0,
        "current_bucket_balance": 1000.0,
        "total_realized_pl": 0.0,
        "current_cycle_start_balance": 1000.0,
        "current_cycle_realized_pl": 0.0,
        "cycle_profit_target_min_pct": 2.0,
        "cycle_profit_target_max_pct": 5.0,
        "max_single_trade_risk_pct": 1.0,
        "one_order_only": True,
        "demo_only": True,
        "live_trading": False,
    }


def _allocation_policy() -> dict:
    return {
        "allocation_mode": "CONTINUE_DEMO",
        "compounding_enabled": False,
        "collect_profit_at_target": True,
        "require_more_evidence_after_loss": True,
        "require_owner_approval_for_next_trade": True,
        "max_next_trade_risk_pct": 1.0,
        "no_live_allocation": True,
    }


def _owner_bucket_confirmation() -> dict:
    return {
        "owner_confirmed_result_reviewed": True,
        "owner_confirmed_bucket_update_demo_only": True,
        "owner_confirmed_no_live_allocation": True,
        "owner_confirmed_next_trade_requires_approval": True,
        "owner_confirmed_no_autonomous_compounding": True,
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
