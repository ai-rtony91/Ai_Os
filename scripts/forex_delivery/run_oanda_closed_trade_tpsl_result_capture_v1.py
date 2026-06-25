from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_closed_trade_tpsl_result_capture_v1 import (  # noqa: E402
    BLOCKED_INVALID_EVIDENCE,
    evaluate_oanda_closed_trade_tpsl_result_capture_v1,
    oanda_closed_trade_tpsl_result_capture_default_samples_v1,
    oanda_closed_trade_tpsl_result_capture_template_v1,
)


SAMPLE_ALIASES = {
    "still-open": "still_open_trade_328",
    "closed-by-tp": "closed_by_tp_trade_328",
    "closed-by-sl": "closed_by_sl_trade_328",
    "closed-other-profit": "closed_other_profit_trade_328",
    "closed-other-loss": "closed_other_loss_trade_328",
    "breakeven": "breakeven_trade_328",
    "trade-not-found": "trade_not_found",
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_template:
        payload = {
            "script_status": "OANDA_CLOSED_TRADE_TPSL_RESULT_CAPTURE_TEMPLATE_ONLY",
            "broker_network_call_performed": False,
            "credential_read_performed": False,
            "order_placement_performed": False,
            "order_close_performed": False,
            "bucket_update_performed": False,
            "template": oanda_closed_trade_tpsl_result_capture_template_v1(),
        }
        _print_json(payload)
        return 0

    samples = oanda_closed_trade_tpsl_result_capture_default_samples_v1()
    if args.sample == "all":
        selected = {
            alias: samples[sample_name]
            for alias, sample_name in SAMPLE_ALIASES.items()
        }
    else:
        sample_name = SAMPLE_ALIASES.get(args.sample, args.sample)
        selected = {args.sample: samples[sample_name]}
    decisions = {
        name: evaluate_oanda_closed_trade_tpsl_result_capture_v1(evidence)
        for name, evidence in selected.items()
    }
    payload = {
        "script_status": "OANDA_CLOSED_TRADE_TPSL_RESULT_CAPTURE_DRY_RUN_SAMPLES",
        "sample": args.sample,
        "broker_network_call_performed": False,
        "broker_api_call_performed": False,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "vault_read_performed": False,
        "dotenv_read": False,
        "env_read": False,
        "order_placement_performed": False,
        "order_close_performed": False,
        "order_mutation_performed": False,
        "trade_mutation_performed": False,
        "position_mutation_performed": False,
        "live_endpoint_used": False,
        "bucket_update_performed": False,
        "scheduler_started": False,
        "daemon_started": False,
        "decisions": decisions,
    }
    _print_json(payload)
    return 1 if _has_invalid_decision(decisions) else 0


def _parser() -> argparse.ArgumentParser:
    sample_names = sorted(
        oanda_closed_trade_tpsl_result_capture_default_samples_v1().keys()
    )
    sample_aliases = sorted(SAMPLE_ALIASES.keys())
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description=(
            "AIOS OANDA sanitized closed-trade TP/SL result classifier. "
            "Prints dry-run JSON only and performs no broker, vault, env, "
            "order, bucket, scheduler, or daemon action."
        ),
    )
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument(
        "--sample",
        choices=["all", *sample_aliases, *sample_names],
        default="all",
        help="Sanitized built-in sample to classify.",
    )
    return parser


def _has_invalid_decision(decisions: Mapping[str, Mapping[str, Any]]) -> bool:
    return any(
        decision.get("status") == BLOCKED_INVALID_EVIDENCE
        for decision in decisions.values()
    )


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
