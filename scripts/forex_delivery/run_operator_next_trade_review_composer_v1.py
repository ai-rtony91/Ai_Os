"""Run the local AI_OS operator next-trade review composer.

This runner is local-only. It reads optional local JSON evidence, prints a
plain operator answer by default, and never calls brokers, credentials,
network endpoints, schedulers, or repo mutation commands.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.operator_next_trade_review_composer_v1 import (  # noqa: E402
    compose_operator_next_trade_review,
)


PACKET_ID = "AIOS-FOREX-OPERATOR-NEXT-TRADE-REVIEW-RUNNER-LOCAL-APPLY-V1"
MODE = "LOCAL_ONLY_OPERATOR_NEXT_TRADE_REVIEW_RUNNER"

RUNNER_SAFETY = {
    "local_only": True,
    "broker_calls_allowed": False,
    "credential_access_allowed": False,
    "order_placement_allowed": False,
    "order_close_allowed": False,
    "live_endpoint_allowed": False,
    "repo_mutation_performed": False,
    "uses_network": False,
}


def sample_blocked_trade_334_evidence() -> dict:
    """Return local sample evidence that intentionally blocks review."""

    conservative_safety = {
        "local_only": True,
        "broker_calls_allowed": False,
        "credential_access_allowed": False,
        "order_placement_allowed": False,
        "order_close_allowed": False,
        "live_endpoint_allowed": False,
        "repo_mutation_outside_allowed_files": False,
        "uses_network": False,
    }
    return {
        "operator_context": {
            "operator_name": "Anthony",
            "instrument": "EUR_USD",
            "direction": "LONG",
            "strategy_name": "paper_edge_candidate",
            "candidate_id": "trade-334-review",
            "last_trade_id": 334,
            "last_trade_result": (
                "STOP_LOSS_ORDER / FILLED_TRADE_PL_NEGATIVE / -0.0010"
            ),
            "wants_next_demo_review": True,
        },
        "loss_review_metrics_gate": {
            "allowed": False,
            "decision": "BLOCK_NEXT_DEMO_ORDER_MISSING_METRICS",
            "blocked_reasons": [
                "trade 334 proof is incomplete: entry, signal, regime, spread, "
                "risk geometry, and paper-to-demo lineage evidence are missing"
            ],
            "missing_metrics": {
                "entry_metrics": ["bid", "ask", "quote_age_ms"],
                "signal_metrics": ["signal_confidence", "signal_threshold"],
                "market_regime_metrics": ["regime_label", "atr"],
                "spread_slippage_metrics": ["spread_at_fill", "slippage"],
                "risk_geometry_metrics": ["stop_distance", "r_multiple"],
                "paper_to_demo_lineage_metrics": [
                    "paper_sample_size",
                    "walk_forward_passed",
                    "proof_bundle_passed",
                ],
            },
            "safety": conservative_safety,
        },
        "trade_latency_baseline": {
            "allowed": False,
            "decision": "BLOCK_LATENCY_MISSING_TIMESTAMPS",
            "blocked_reasons": [
                "trade 334 timing proof is incomplete: quote, signal, submit, "
                "fill, monitor, P/L classification, and audit timestamps are missing"
            ],
            "missing_timestamps": [
                "quote_received_utc",
                "signal_generated_utc",
                "order_submit_started_utc",
                "order_filled_utc",
                "monitor_started_utc",
                "pl_classified_utc",
                "audit_written_utc",
            ],
            "safety": conservative_safety,
        },
    }


def main(
    argv: list[str] | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    out = stdout or sys.stdout
    err = stderr or sys.stderr
    parser = _build_parser()

    try:
        args = parser.parse_args(argv)
        result, exit_code = _result_from_args(args)
        if args.json:
            json.dump(result, out, indent=2, sort_keys=True)
            out.write("\n")
        else:
            _print_plain(result, out)
        return exit_code
    except SystemExit:
        raise
    except Exception as exc:
        result = _file_or_internal_error_result(
            f"unexpected internal runner error: {exc}"
        )
        _print_plain(result, out)
        err.write("AIOS runner stopped safely before any broker or repo action.\n")
        return 3


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the local AI_OS operator next-trade review composer."
    )
    evidence_group = parser.add_mutually_exclusive_group()
    evidence_group.add_argument(
        "--evidence-json",
        help="Local JSON evidence file to pass to the review composer.",
    )
    evidence_group.add_argument(
        "--sample-blocked-trade-334",
        action="store_true",
        help="Use built-in local sample evidence that intentionally blocks review.",
    )
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="Print JSON output.")
    output_group.add_argument(
        "--plain",
        action="store_true",
        help="Print compact operator output. This is the default.",
    )
    return parser


def _result_from_args(args: argparse.Namespace) -> tuple[dict, int]:
    if args.evidence_json:
        evidence, error = _load_local_json_mapping(Path(args.evidence_json))
        if error:
            return _file_or_internal_error_result(error), 2
        return _with_runner_safety(compose_operator_next_trade_review(evidence)), 0

    if args.sample_blocked_trade_334:
        return (
            _with_runner_safety(
                compose_operator_next_trade_review(
                    sample_blocked_trade_334_evidence()
                )
            ),
            0,
        )

    return _with_runner_safety(compose_operator_next_trade_review(None)), 0


def _load_local_json_mapping(path: Path) -> tuple[dict | None, str | None]:
    if path.name.lower() == ".env" or path.suffix.lower() != ".json":
        return None, "local evidence path must be a JSON file and must not be .env"
    if not path.exists() or not path.is_file():
        return None, f"local evidence JSON file was not found: {path}"
    try:
        with path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
    except json.JSONDecodeError as exc:
        return None, f"local evidence JSON could not be parsed: {exc}"
    except OSError as exc:
        return None, f"local evidence JSON could not be read: {exc}"
    if not isinstance(loaded, dict):
        return None, "local evidence JSON must contain an object at the top level"
    return loaded, None


def _file_or_internal_error_result(message: str) -> dict:
    return {
        "packet_id": PACKET_ID,
        "mode": MODE,
        "allowed": False,
        "decision": "BLOCK_REVIEW_INVALID_EVIDENCE",
        "operator_answer": (
            "Blocked: AIOS does not have enough proof for you to review this trade."
        ),
        "operator_benefit": (
            "One command gives Anthony a review-ready or blocked answer, with no "
            "digging through multiple reports and no broker action."
        ),
        "next_safe_action": "Fix the local evidence file before next-trade review.",
        "blocks": [message],
        "missing_for_review": ["valid_local_evidence_json"],
        "review_summary": "Runner blocked review before any broker or repo action.",
        "loss_gate_decision": None,
        "latency_decision": None,
        "risk_or_safety_clear": True,
        "timing_clear": False,
        "trade_evidence_clear": False,
        "owner_approval_still_required": True,
        "broker_action_allowed": False,
        "safety": dict(RUNNER_SAFETY),
    }


def _with_runner_safety(result: dict) -> dict:
    merged = dict(result)
    safety = dict(result.get("safety") or {})
    safety.update(RUNNER_SAFETY)
    merged["safety"] = safety
    merged["runner_packet_id"] = PACKET_ID
    merged["runner_mode"] = MODE
    return merged


def _print_plain(result: dict, out: TextIO) -> None:
    out.write("AIOS Operator Next Trade Review\n")
    out.write(f"decision: {result.get('decision')}\n")
    out.write(f"allowed: {str(result.get('allowed')).lower()}\n")
    out.write(f"operator_answer: {result.get('operator_answer')}\n")
    out.write(f"next_safe_action: {result.get('next_safe_action')}\n")
    out.write(
        f"broker_action_allowed: {str(result.get('broker_action_allowed')).lower()}\n"
    )
    out.write(
        "owner_approval_still_required: "
        f"{str(result.get('owner_approval_still_required')).lower()}\n"
    )
    _print_list("blocks", result.get("blocks"), out)
    _print_list("missing_for_review", result.get("missing_for_review"), out)


def _print_list(label: str, values: Any, out: TextIO) -> None:
    out.write(f"{label}:\n")
    if isinstance(values, list) and values:
        for value in values:
            out.write(f"  - {value}\n")
    else:
        out.write("  - none\n")


if __name__ == "__main__":
    raise SystemExit(main())
