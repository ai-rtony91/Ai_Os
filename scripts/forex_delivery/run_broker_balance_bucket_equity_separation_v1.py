from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.broker_balance_bucket_equity_separation_v1 import (  # noqa: E402
    evaluate_broker_balance_bucket_equity_separation_v1,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_template:
        _print_json(_template_payload())
        return 0

    account_snapshot = (
        _flat_account_snapshot()
        if args.sample_flat_account
        else _open_trade_account_snapshot()
    )
    policy = _bucket_risk_policy()
    decision = evaluate_broker_balance_bucket_equity_separation_v1(
        account_snapshot=account_snapshot,
        bucket_risk_policy=policy,
    )
    _print_json(
        {
            "script_status": "BROKER_BALANCE_BUCKET_EQUITY_SEPARATION_PACKAGE",
            "dry_run": True,
            "sanitized_input_only": True,
            "broker_network_call_performed": False,
            "broker_api_call_performed": False,
            "credential_read_performed": False,
            "account_id_read_performed": False,
            "order_placement_performed": False,
            "order_close_performed": False,
            "order_mutation_performed": False,
            "trade_mutation_performed": False,
            "position_mutation_performed": False,
            "live_endpoint_used": False,
            "raw_broker_payload_persisted": False,
            "decision": decision,
        }
    )
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = SanitizedArgumentParser(
        allow_abbrev=False,
        description="AIOS broker balance, bucket, NAV/equity separation evaluator.",
    )
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument(
        "--sample-flat-account",
        action="store_true",
        help="Use a sanitized no-open-exposure example instead of the open-trade sample.",
    )
    return parser


class SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        _print_json(
            {
                "script_status": "BLOCKED_INVALID_ARGUMENTS",
                "argument_error": "unsupported_or_invalid_argument",
                "broker_network_call_performed": False,
                "broker_api_call_performed": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "order_placement_performed": False,
                "order_close_performed": False,
                "order_mutation_performed": False,
                "trade_mutation_performed": False,
                "position_mutation_performed": False,
                "live_endpoint_used": False,
                "raw_broker_payload_persisted": False,
            }
        )
        raise SystemExit(2)


def _template_payload() -> dict:
    return {
        "script_status": "BROKER_BALANCE_BUCKET_EQUITY_SEPARATION_TEMPLATE_ONLY",
        "dry_run": True,
        "sanitized_input_only": True,
        "broker_network_call_performed": False,
        "broker_api_call_performed": False,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "order_placement_performed": False,
        "order_close_performed": False,
        "order_mutation_performed": False,
        "trade_mutation_performed": False,
        "position_mutation_performed": False,
        "live_endpoint_used": False,
        "raw_broker_payload_persisted": False,
        "account_snapshot": {
            "balance": "number_gte_zero",
            "NAV": "number_gte_zero_when_present",
            "unrealizedPL": "number",
            "pl": "number",
            "marginUsed": "number_gte_zero",
            "marginAvailable": "number_gte_zero",
            "openTradeCount": "integer_gte_zero",
            "openPositionCount": "integer_gte_zero",
            "pendingOrderCount": "integer_gte_zero",
        },
        "bucket_risk_policy": {
            "bucket_currency": "USD",
            "configured_trade_bucket_balance": "explicit_number_gte_zero",
            "allow_bucket_to_equal_broker_balance": False,
            "max_single_trade_risk_pct": "number_gt_zero",
            "max_next_trade_risk_pct": "number_gt_zero_lte_single_trade_limit",
            "demo_only": True,
            "live_trading": False,
            "one_order_only": True,
            "require_owner_approval_for_next_trade": True,
            "allow_next_trade_while_open_position": False,
            "compounding_enabled": False,
            "no_live_allocation": True,
        },
    }


def _open_trade_account_snapshot() -> dict:
    return {
        "balance": "10000.00",
        "NAV": "9999.99",
        "unrealizedPL": "-0.01",
        "pl": "0.00",
        "marginUsed": "0.01",
        "marginAvailable": "9999.98",
        "openTradeCount": 1,
        "openPositionCount": 1,
        "pendingOrderCount": 0,
    }


def _flat_account_snapshot() -> dict:
    return {
        "balance": "10000.00",
        "NAV": "10000.00",
        "unrealizedPL": "0.00",
        "pl": "0.00",
        "marginUsed": "0.00",
        "marginAvailable": "10000.00",
        "openTradeCount": 0,
        "openPositionCount": 0,
        "pendingOrderCount": 0,
    }


def _bucket_risk_policy() -> dict:
    return {
        "bucket_currency": "USD",
        "configured_trade_bucket_balance": 1000.0,
        "allow_bucket_to_equal_broker_balance": False,
        "max_single_trade_risk_pct": 1.0,
        "max_next_trade_risk_pct": 0.5,
        "demo_only": True,
        "live_trading": False,
        "one_order_only": True,
        "require_owner_approval_for_next_trade": True,
        "allow_next_trade_while_open_position": False,
        "compounding_enabled": False,
        "no_live_allocation": True,
    }


def _print_json(payload: Mapping[str, object]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
