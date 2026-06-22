"""CLI for deterministic proof-bundle-to-candidate bridge execution."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.proof_bundle_to_candidate_bridge import run_proof_bundle_to_candidate_bridge


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_forex_proof_bundle_to_candidate_bridge",
        description="Run deterministic proof-bundle to candidate bridge path.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON output.",
    )
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Persist bridge report artifact.",
    )
    return parser


def format_human_status(payload: dict[str, Any]) -> str:
    blockers = ", ".join(payload.get("closed_blockers", []))
    remaining = ", ".join(payload.get("remaining_blockers", []))
    return "\n".join(
        [
            "AIOS Forex Proof Bundle To Candidate Bridge",
            f"selected_candidate_id: {payload.get('selected_candidate_id', '')}",
            f"source_proof_bundle_status: {payload.get('source_proof_bundle_status', '')}",
            f"source_candidate_verdict: {payload.get('source_candidate_verdict', '')}",
            f"candidate_bridge_verdict: {payload.get('candidate_bridge_verdict', '')}",
            f"closed_blockers: {blockers}",
            f"remaining_blockers: {remaining}",
            f"next_safe_action: {payload.get('next_safe_action', '')}",
            f"safety: {payload.get('safety', {})}",
        ]
    )


def _json_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "selected_candidate_id": payload.get("selected_candidate_id"),
        "source_proof_bundle_status": payload.get("source_proof_bundle_status"),
        "source_candidate_verdict": payload.get("source_candidate_verdict"),
        "candidate_bridge_verdict": payload.get("candidate_bridge_verdict"),
        "closed_blockers": payload.get("closed_blockers", []),
        "remaining_blockers": payload.get("remaining_blockers", []),
        "safety": payload.get("safety", {}),
        "next_safe_action": payload.get("next_safe_action"),
        "enriched_candidate": payload.get("enriched_candidate", {}),
        "canonical_review_bundle": payload.get("canonical_review_bundle", {}),
        "strategy_quality_gaps": payload.get("strategy_quality_gaps", []),
        "demo_contract_gaps": payload.get("demo_contract_gaps", []),
        "review_package_gaps": payload.get("review_package_gaps", []),
        "human_review_gaps": payload.get("human_review_gaps", []),
        "safety_gaps": payload.get("safety_gaps", []),
        "report_path": payload.get("report_path"),
        "live_trading_authorized": payload.get("safety", {}).get("live_trading_authorized", False),
    }


def _safety_gap_exists(safety: Any) -> bool:
    if not isinstance(safety, dict):
        return False
    return any(
        bool(safety.get(flag, False))
        for flag in (
            "broker_connected",
            "credentials_used",
            "account_id_present",
            "network_used",
            "order_execution",
            "demo_trading",
            "live_trading",
            "live_trading_authorized",
        )
    )


def _proof_blockers_closed(payload: dict[str, Any]) -> bool:
    return bool(payload.get("closed_blockers", []))


def exit_code_for_payload(payload: dict[str, Any]) -> int:
    if _safety_gap_exists(payload.get("safety", {})):
        return 2
    if _proof_blockers_closed(payload):
        return 0
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    payload = run_proof_bundle_to_candidate_bridge(write_reports=bool(args.write_report))
    if args.json:
        sys.stdout.write(json.dumps(_json_payload(payload), indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(format_human_status(payload))
        sys.stdout.write("\n")
    return exit_code_for_payload(payload)


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "format_human_status",
    "exit_code_for_payload",
    "main",
]
