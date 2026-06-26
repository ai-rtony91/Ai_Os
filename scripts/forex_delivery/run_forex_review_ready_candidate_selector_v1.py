"""CLI runner for the pure local AIOS Forex review-ready candidate selector."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_review_ready_candidate_selector_v1 import (  # noqa: E402
    select_review_ready_candidate,
)


FORBIDDEN_PATH_FRAGMENTS = (
    ".env",
    "secret",
    "secrets",
    "credential",
    "credentials",
    "broker",
    "oanda",
    "account",
    "runtime",
    "dashboard",
    "scheduler",
    "daemon",
    "webhook",
    "production",
)


def sample_candidates() -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": "blocked-old-candidate",
            "strategy": "range_breakout_v1",
            "symbol": "EUR_USD",
            "direction": "LONG",
            "review_ready": True,
            "blocked_reasons": ["superseded_by_newer_evidence"],
            "evidence_depth_score": 0.80,
            "statistical_profit_score": 0.70,
            "profit_factor": 1.35,
            "expectancy": 0.12,
            "max_drawdown": 0.04,
            "sample_size": 40,
            "risk_score": 0.60,
            "recency_score": 0.40,
        },
        {
            "candidate_id": "review-ready-balanced",
            "strategy": "london_open_v2",
            "symbol": "EUR_USD",
            "direction": "LONG",
            "status": "REVIEW_READY",
            "gate_status": "PASSED",
            "evidence_depth_score": 0.72,
            "statistical_profit_score": 0.76,
            "profit_factor": 1.55,
            "expectancy": 0.18,
            "max_drawdown": 0.025,
            "sample_size": 55,
            "risk_score": 0.71,
            "recency_score": 0.65,
            "proof_flags": {},
        },
        {
            "candidate_id": "review-ready-strong",
            "strategy": "ny_continuation_v1",
            "instrument": "EUR_USD",
            "direction": "LONG",
            "review_ready": True,
            "readiness_status": "PASSED",
            "evidence_depth_score": 0.91,
            "statistical_profit_score": 0.88,
            "profit_factor": 1.92,
            "expectancy": 0.31,
            "max_drawdown": 0.018,
            "drawdown_score": 0.78,
            "sample_size": 84,
            "risk_score": 0.82,
            "recency_score": 0.74,
            "metadata": {"source": "deterministic_sample"},
        },
    ]


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the local AIOS Forex Review-Ready Candidate Selector V1."
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Local JSON file containing a candidate list or an object with a candidates key.",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.0,
        help="Minimum deterministic total score required for selection.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional exact local JSON output path. No file is written without this.",
    )
    args = parser.parse_args(argv)

    out = stdout if stdout is not None else sys.stdout
    candidates = _load_candidates(args.input) if args.input else sample_candidates()
    result = select_review_ready_candidate(candidates, min_score=args.min_score)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"

    out.write(payload)
    if args.output is not None:
        _write_output(args.output, payload)
    return 0


def _load_candidates(path: Path) -> list[dict[str, Any]]:
    _reject_forbidden_path(path)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        candidates = payload.get("candidates")
        return candidates if isinstance(candidates, list) else []
    return []


def _write_output(path: Path, payload: str) -> None:
    _reject_forbidden_path(path)
    path.write_text(payload, encoding="utf-8")


def _reject_forbidden_path(path: Path) -> None:
    normalized = str(path).replace("\\", "/").lower()
    if any(fragment in normalized for fragment in FORBIDDEN_PATH_FRAGMENTS):
        raise ValueError(f"refusing forbidden local path: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
