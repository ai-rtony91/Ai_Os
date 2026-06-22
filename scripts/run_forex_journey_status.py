from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.review_chain_end_to_end_candidate_journey import (
    JOURNEY_BLOCKED,
    JOURNEY_INCOMPLETE,
    JOURNEY_REVIEW_READY,
    JOURNEY_REJECTED,
    run_review_chain_end_to_end_candidate_journey,
)


def format_human_status(payload: dict[str, Any]) -> str:
    selected_candidate_id = str(payload.get("selected_candidate_id", ""))
    selected_strategy = str(payload.get("selected_strategy", ""))
    selected_direction = str(payload.get("selected_direction", ""))
    candidate_verdict = str(payload.get("candidate_demo_review_verdict", ""))
    review_chain_status = str(payload.get("review_chain_status", ""))
    final_verdict = str(payload.get("final_verdict", ""))
    live_trading_authorized = bool(payload.get("live_trading_authorized", False))
    candidate_blockers = payload.get("candidate_demo_review_blockers", [])
    review_chain_blockers = payload.get("review_chain_blockers", [])
    if not isinstance(candidate_blockers, list):
        candidate_blockers = list(candidate_blockers) if candidate_blockers is not None else []
    if not isinstance(review_chain_blockers, list):
        review_chain_blockers = list(review_chain_blockers) if review_chain_blockers is not None else []
    final_next_safe_action = str(payload.get("final_next_safe_action", ""))
    safety = payload.get("safety", {})
    if not isinstance(safety, dict):
        safety = {}

    blocker_lines: list[str] = []
    safety_lines: list[str] = []
    for label, value in (
        ("candidate_demo_review_blockers", candidate_blockers),
        ("review_chain_blockers", review_chain_blockers),
    ):
        blocker_lines.append(f"{label}: {', '.join(value)}")

    for key in ("paper_only", "broker_connected", "credentials_used", "network_used", "order_execution", "demo_trading", "live_trading"):
        safety_lines.append(f"{key}: {bool(safety.get(key, False))}")

    return "\n".join(
        [
            "AIOS Forex Journey Status",
            f"selected_candidate_id: {selected_candidate_id}",
            f"selected_strategy: {selected_strategy}",
            f"selected_direction: {selected_direction}",
            f"candidate_demo_review_verdict: {candidate_verdict}",
            f"review_chain_status: {review_chain_status}",
            f"final_verdict: {final_verdict}",
            f"live_trading_authorized: {live_trading_authorized}",
            "\n".join(blocker_lines),
            f"final_next_safe_action: {final_next_safe_action}",
            "safety:",
            "  " + "\n  ".join(safety_lines),
        ]
    )


def exit_code_for_final_verdict(final_verdict: str) -> int:
    if final_verdict in {JOURNEY_REVIEW_READY, JOURNEY_INCOMPLETE}:
        return 0
    if final_verdict == JOURNEY_REJECTED:
        return 1
    if final_verdict == JOURNEY_BLOCKED:
        return 2
    return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_forex_journey_status",
        description="Run deterministic Forex journey status check.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON payload.",
    )
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Persist journey report artifact.",
    )
    return parser


def _build_required_json_keys(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "selected_candidate_id": payload.get("selected_candidate_id"),
        "selected_strategy": payload.get("selected_strategy"),
        "selected_direction": payload.get("selected_direction"),
        "candidate_demo_review_verdict": payload.get("candidate_demo_review_verdict"),
        "review_chain_status": payload.get("review_chain_status"),
        "final_verdict": payload.get("final_verdict"),
        "live_trading_authorized": payload.get("live_trading_authorized"),
        "candidate_demo_review_blockers": list(payload.get("candidate_demo_review_blockers", [])),
        "review_chain_blockers": list(payload.get("review_chain_blockers", [])),
        "final_next_safe_action": payload.get("final_next_safe_action"),
        "safety": payload.get("safety", {}),
    }


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    payload = run_review_chain_end_to_end_candidate_journey(write_reports=bool(args.write_report))
    if args.json:
        json_payload = _build_required_json_keys(payload)
        sys.stdout.write(json.dumps(json_payload, indent=2, sort_keys=True))
        sys.stdout.write("\n")
        return exit_code_for_final_verdict(str(payload.get("final_verdict", "")))

    sys.stdout.write(format_human_status(payload))
    sys.stdout.write("\n")
    return exit_code_for_final_verdict(str(payload.get("final_verdict", "")))


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "format_human_status",
    "exit_code_for_final_verdict",
    "main",
]

