from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_readonly_account_snapshot_balance_separation_adapter_v1 import (  # noqa: E402
    evaluate_oanda_readonly_account_snapshot_balance_separation_adapter_v1,
)


SCRIPT_STATUS_PACKAGE = (
    "OANDA_READONLY_ACCOUNT_SNAPSHOT_BALANCE_SEPARATION_ADAPTER_PACKAGE"
)
SCRIPT_STATUS_TEMPLATE = (
    "OANDA_READONLY_ACCOUNT_SNAPSHOT_BALANCE_SEPARATION_ADAPTER_TEMPLATE_ONLY"
)

SAFETY_FLAGS = (
    "network_call_performed",
    "broker_network_call_performed",
    "broker_api_call_performed",
    "credential_read_performed",
    "account_id_read_performed",
    "dotenv_read",
    "env_read",
    "order_placement_performed",
    "order_close_performed",
    "order_mutation_performed",
    "trade_mutation_performed",
    "position_mutation_performed",
    "live_endpoint_used",
    "raw_broker_payload_persisted",
    "file_persistence_performed",
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_template:
        _print_json(_template_payload())
        return 0

    capture_result = (
        _flat_capture_sample() if args.sample_flat_account else _trade_328_capture_sample()
    )
    decision = evaluate_oanda_readonly_account_snapshot_balance_separation_adapter_v1(
        read_only_capture_result=capture_result,
        bucket_risk_policy=_bucket_risk_policy(),
    )
    payload = {
        "script_status": SCRIPT_STATUS_PACKAGE,
        "dry_run": True,
        "sanitized_input_only": True,
        "adapter_only_not_bucket_updater": True,
        "decision": decision,
    }
    payload.update(_safety_flags())
    _print_json(payload)
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = SanitizedArgumentParser(
        allow_abbrev=False,
        description=(
            "AIOS OANDA sanitized read-only account snapshot to balance "
            "separation adapter."
        ),
    )
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument(
        "--sample-flat-account",
        action="store_true",
        help="Use a sanitized no-open-exposure example.",
    )
    return parser


class SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        payload = {
            "script_status": "BLOCKED_INVALID_ARGUMENTS",
            "argument_error": "unsupported_or_invalid_argument",
        }
        payload.update(_safety_flags())
        _print_json(payload)
        raise SystemExit(2)


def _template_payload() -> dict:
    payload = {
        "script_status": SCRIPT_STATUS_TEMPLATE,
        "dry_run": True,
        "sanitized_input_only": True,
        "adapter_only_not_bucket_updater": True,
        "read_only_capture_result": {
            "decision": {
                "status": "READ_ONLY_FILLED_TRADE_PL_CAPTURE_ATTEMPTED",
                "pl_capture_classification": "FILLED_TRADE_PL_OPEN_UNREALIZED",
                "pl_evidence": {
                    "account_summary_snapshot": {
                        "balance": "number_gte_zero",
                        "NAV": "number_gte_zero_when_present",
                        "unrealizedPL": "number",
                        "pl": "number",
                        "marginUsed": "number_gte_zero",
                        "marginAvailable": "number_gte_zero",
                    },
                    "open_trade_evidence": [],
                    "open_position_evidence": [],
                },
            },
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
        "runtime_input_rule": {
            "command_line_secret_argument_supported": False,
            "command_line_account_identifier_supported": False,
            "env_file_supported": False,
            "repo_secret_supported": False,
            "owner_run_required": False,
        },
    }
    payload.update(_safety_flags())
    return payload


def _trade_328_capture_sample() -> dict:
    payload = {
        "script_status": "SANITIZED_READ_ONLY_CAPTURE_RESULT_SAMPLE",
        "decision": {
            "status": "READ_ONLY_FILLED_TRADE_PL_CAPTURE_ATTEMPTED",
            "pl_capture_classification": "FILLED_TRADE_PL_OPEN_UNREALIZED",
            "pl_evidence": {
                "transaction_match": {
                    "orderCreateTransaction_id": "327",
                    "orderFillTransaction_id": "328",
                    "relatedTransactionIDs": ["327", "328", "329", "330"],
                    "matched_transaction_count": 0,
                },
                "realized_pl_values": [],
                "realized_pl_total": "0",
                "open_trade_evidence": [
                    {
                        "trade_id": "328",
                        "instrument": "EUR_USD",
                        "currentUnits": "1",
                        "unrealizedPL": "-0.0001",
                    },
                ],
                "open_position_evidence": [
                    {
                        "instrument": "EUR_USD",
                        "long_units": "1",
                        "short_units": "0",
                        "unrealizedPL": "-0.0001",
                    },
                ],
                "account_summary_snapshot": {
                    "balance": "10000.00",
                    "NAV": "9999.9999",
                    "unrealizedPL": "-0.0001",
                    "pl": "0.00",
                    "marginUsed": "0.01",
                    "marginAvailable": "9999.98",
                },
                "evidence_found": True,
            },
        },
    }
    payload.update(_safety_flags())
    payload["execution_authority"] = _execution_authority()
    return payload


def _flat_capture_sample() -> dict:
    payload = {
        "script_status": "SANITIZED_READ_ONLY_CAPTURE_RESULT_SAMPLE",
        "account_snapshot": {
            "balance": "10000.00",
            "NAV": "10000.00",
            "unrealizedPL": "0.00",
            "pl": "0.00",
            "marginUsed": "0.00",
            "marginAvailable": "10000.00",
            "openTradeCount": 0,
            "openPositionCount": 0,
            "pendingOrderCount": 0,
        },
    }
    payload.update(_safety_flags())
    payload["execution_authority"] = _execution_authority()
    return payload


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


def _execution_authority() -> dict[str, bool]:
    return {
        "network_allowed": False,
        "broker_call_allowed": False,
        "credential_access_allowed": False,
        "order_placement_allowed": False,
        "order_close_allowed": False,
        "order_mutation_allowed": False,
        "trade_mutation_allowed": False,
        "position_mutation_allowed": False,
        "live_endpoint_allowed": False,
        "live_trading_allowed": False,
        "raw_broker_payload_persistence_allowed": False,
    }


def _safety_flags() -> dict[str, bool]:
    return {field: False for field in SAFETY_FLAGS}


def _print_json(payload: Mapping[str, object]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
