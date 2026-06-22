"""CLI for deterministic replay/reconciliation proof bundling."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.replay_reconciliation_proof_bundle import (
    PROOF_BUNDLE_BLOCKED,
    PROOF_BUNDLE_COMPLETE,
    PROOF_BUNDLE_INCOMPLETE,
    run_replay_reconciliation_proof_bundle,
)

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_forex_replay_reconciliation_proof_bundle",
        description="Run deterministic replay/reconciliation proof bundle build.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print payload as JSON",
    )
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Persist proof-bundle report artifact",
    )
    return parser


def format_human_status(payload: dict[str, Any]) -> str:
    blockers = payload.get("unresolved_blockers", {})
    return "\n".join(
        [
            "AIOS Forex Replay Reconciliation Proof Bundle",
            f"selected_candidate_id: {payload.get('selected_candidate_id', '')}",
            f"selected_strategy: {payload.get('selected_strategy', '')}",
            f"selected_direction: {payload.get('selected_direction', '')}",
            f"source_candidate_verdict: {payload.get('source_candidate_verdict', '')}",
            f"source_review_chain_status: {payload.get('source_review_chain_status', '')}",
            f"source_journey_final_verdict: {payload.get('source_journey_final_verdict', '')}",
            f"proof_bundle_status: {payload.get('proof_bundle_status', '')}",
            f"proof_bundle_ready_for_candidate_bridge: {payload.get('proof_bundle_ready_for_candidate_bridge', False)}",
            f"replay_proof_status: {payload.get('replay_proof_status', False)}",
            f"reconciliation_proof_status: {payload.get('reconciliation_proof_status', False)}",
            f"rollback_proof_status: {payload.get('rollback_proof_status', False)}",
            f"demo_validation_proof_status: {payload.get('demo_validation_proof_status', False)}",
            f"next_safe_action: {payload.get('next_safe_action', '')}",
            f"safety: {payload.get('safety', {})}",
            f"unresolved_blockers: {blockers}",
        ]
    )


def _json_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "selected_candidate_id": payload.get("selected_candidate_id"),
        "selected_strategy": payload.get("selected_strategy"),
        "selected_direction": payload.get("selected_direction"),
        "source_candidate_verdict": payload.get("source_candidate_verdict"),
        "source_review_chain_status": payload.get("source_review_chain_status"),
        "source_journey_final_verdict": payload.get("source_journey_final_verdict"),
        "proof_bundle_status": payload.get("proof_bundle_status"),
        "proof_bundle_ready_for_candidate_bridge": payload.get("proof_bundle_ready_for_candidate_bridge"),
        "replay_proof_status": payload.get("replay_proof_status"),
        "reconciliation_proof_status": payload.get("reconciliation_proof_status"),
        "rollback_proof_status": payload.get("rollback_proof_status"),
        "demo_validation_proof_status": payload.get("demo_validation_proof_status"),
        "replay_trace_id": payload.get("replay_trace_id"),
        "reconciliation_trace_id": payload.get("reconciliation_trace_id"),
        "rollback_plan_id": payload.get("rollback_plan_id"),
        "demo_validation_trace_id": payload.get("demo_validation_trace_id"),
        "unresolved_blockers": payload.get("unresolved_blockers", {}),
        "next_safe_action": payload.get("next_safe_action"),
        "safety": payload.get("safety", {}),
    }


def exit_code_for_status(status: str) -> int:
    if status == PROOF_BUNDLE_COMPLETE:
        return 0
    if status == PROOF_BUNDLE_INCOMPLETE:
        return 1
    if status == PROOF_BUNDLE_BLOCKED:
        return 2
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    payload = run_replay_reconciliation_proof_bundle(write_reports=bool(args.write_report))
    if args.json:
        sys.stdout.write(json.dumps(_json_payload(payload), sort_keys=True, indent=2))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(format_human_status(payload))
        sys.stdout.write("\n")
    return exit_code_for_status(payload.get("proof_bundle_status", ""))


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "format_human_status",
    "exit_code_for_status",
    "main",
]
