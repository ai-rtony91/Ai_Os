"""CLI entrypoint for deterministic Forex proof gap closure planning."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.proof_gap_closure_plan import run_proof_gap_closure_plan


def format_human_plan(payload: dict[str, Any]) -> str:
    bucket_lines = [
        "closure_buckets:",
    ]
    for key in (
        "evidence_proof_gaps",
        "strategy_quality_gaps",
        "demo_contract_gaps",
        "review_package_gaps",
        "safety_gaps",
        "human_review_gaps",
    ):
        bucket_lines.append(
            f"  {key}: {', '.join(payload.get('closure_buckets', {}).get(key, []))}"
        )

    safety_lines = ["safety:"]
    for key in (
        "paper_only",
        "broker_connected",
        "credentials_used",
        "network_used",
        "order_execution",
        "demo_trading",
        "live_trading",
    ):
        safety_lines.append(f"  {key}: {bool(payload.get('safety', {}).get(key, False))}")

    sequence = ", ".join(item.get("packet_id", "") for item in payload.get("recommended_packet_sequence", []))
    lines = [
        "AIOS Forex Proof Gap Closure Plan",
        f"selected_candidate_id: {payload.get('selected_candidate_id', '')}",
        f"source_candidate_verdict: {payload.get('source_candidate_verdict', '')}",
        f"source_review_chain_status: {payload.get('source_review_chain_status', '')}",
        f"source_journey_final_verdict: {payload.get('source_journey_final_verdict', '')}",
        f"highest_value_next_packet: {payload.get('highest_value_next_packet', '')}",
        f"recommended_packet_sequence: {sequence}",
        f"next_safe_action: {payload.get('next_safe_action', '')}",
        *bucket_lines,
        *safety_lines,
    ]
    return "\n".join(lines)


def exit_code_for_final_verdict(payload: dict[str, Any]) -> int:
    if payload.get("closure_buckets", {}).get("safety_gaps"):
        return 2
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_forex_proof_gap_closure_plan",
        description="Plan deterministic review-chain closure packets from journey output.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON output.",
    )
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Persist proof-gap closure report artifact.",
    )
    return parser


def _json_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "selected_candidate_id": payload.get("selected_candidate_id"),
        "source_candidate_verdict": payload.get("source_candidate_verdict"),
        "source_review_chain_status": payload.get("source_review_chain_status"),
        "source_journey_final_verdict": payload.get("source_journey_final_verdict"),
        "highest_value_next_packet": payload.get("highest_value_next_packet"),
        "recommended_packet_sequence": payload.get("recommended_packet_sequence", []),
        "closure_buckets": payload.get("closure_buckets", {}),
        "next_safe_action": payload.get("next_safe_action"),
        "safety": payload.get("safety", {}),
    }


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    payload = run_proof_gap_closure_plan(write_reports=bool(args.write_report))
    if args.json:
        data = _json_payload(payload)
        sys.stdout.write(json.dumps(data, sort_keys=True, indent=2))
        sys.stdout.write("\n")
        return exit_code_for_final_verdict(payload)

    sys.stdout.write(format_human_plan(payload))
    sys.stdout.write("\n")
    return exit_code_for_final_verdict(payload)


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "format_human_plan",
    "exit_code_for_final_verdict",
    "main",
]
