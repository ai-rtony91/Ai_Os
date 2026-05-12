from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_lab.ingest.paper_signal_api import SAFETY_STATUS, parse_utc, process_paper_signal


REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_ROOT = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "fixtures" / "paper_signal_test_pack"
RESULT_ROOT = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "results" / "paper_signal_test_pack"

SUPPORTED_SYMBOLS = {"EUR_USD", "GBP_USD"}
SUPPORTED_TIMEFRAMES = {"M5", "M15", "H1"}
MIN_CONFIDENCE = 0.70
VALIDATION_TIME = "2026-05-12T00:05:00Z"

FIXTURE_ORDER = [
    "PAPER_SIGNAL_VALID_LONG_001.json",
    "PAPER_SIGNAL_VALID_SHORT_001.json",
    "PAPER_SIGNAL_MISSING_FIELD_001.json",
    "PAPER_SIGNAL_STALE_001.json",
    "PAPER_SIGNAL_FUTURE_CLOCK_SKEW_001.json",
    "PAPER_SIGNAL_BAD_DIRECTION_001.json",
    "PAPER_SIGNAL_LOW_CONFIDENCE_001.json",
    "PAPER_SIGNAL_UNSUPPORTED_SYMBOL_001.json",
    "PAPER_SIGNAL_UNSUPPORTED_TIMEFRAME_001.json",
    "PAPER_SIGNAL_DUPLICATE_001.json",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def batch_gate(payload: dict[str, Any], seen_signal_ids: set[str]) -> str:
    signal_id = str(payload.get("signal_id", "")).strip()
    if signal_id and signal_id in seen_signal_ids:
        return "Duplicate signal id."
    try:
        confidence = float(payload.get("confidence", 0))
    except (TypeError, ValueError):
        confidence = 0.0
    if confidence < MIN_CONFIDENCE:
        return "Confidence is below paper review threshold."
    symbol = str(payload.get("symbol", "")).strip().upper()
    if symbol not in SUPPORTED_SYMBOLS:
        return "Symbol is not in the paper test allowlist."
    timeframe = str(payload.get("timeframe", "")).strip().upper()
    if timeframe not in SUPPORTED_TIMEFRAMES:
        return "Timeframe is not in the paper test allowlist."
    return ""


def run_test_pack() -> dict[str, Any]:
    validation_time = parse_utc(VALIDATION_TIME)
    seen_signal_ids: set[str] = set()
    results: list[dict[str, Any]] = []

    for fixture_name in FIXTURE_ORDER:
        payload = load_json(FIXTURE_ROOT / fixture_name)
        intake_result = process_paper_signal(payload, validation_time=validation_time, write_outputs=False)
        validation = intake_result["validation_result"]
        route_preview = intake_result["paper_route_preview"]
        blocked_reason = validation.get("blocked_reason", "")
        batch_reason = ""
        status = "ACCEPTED"

        if validation.get("validation_status") != "PASS":
            status = "REJECTED"
            blocked_reason = blocked_reason or "Phase 21 intake rejected the signal."
        else:
            batch_reason = batch_gate(payload, seen_signal_ids)
            if batch_reason:
                status = "REJECTED"
                blocked_reason = batch_reason

        signal_id = str(payload.get("signal_id", "")).strip()
        if signal_id and status == "ACCEPTED":
            seen_signal_ids.add(signal_id)

        results.append(
            {
                "test_case_id": payload.get("test_case_id", fixture_name.replace(".json", "")),
                "fixture": fixture_name,
                "signal_id": signal_id,
                "symbol": payload.get("symbol", "UNKNOWN"),
                "timeframe": payload.get("timeframe", "UNKNOWN"),
                "direction": payload.get("direction", "UNKNOWN"),
                "confidence": payload.get("confidence", "UNKNOWN"),
                "batch_status": status,
                "validation_status": validation.get("validation_status"),
                "paper_route_status": route_preview.get("paper_route_status"),
                "blocked_reason": blocked_reason,
                "batch_gate_reason": batch_reason,
            }
        )

    counts = Counter(result["batch_status"] for result in results)
    blocked_reasons = [result["blocked_reason"] for result in results if result["blocked_reason"]]
    ledger = {
        "ledger_id": "PAPER_SIGNAL_TEST_PACK_LEDGER_001",
        "phase": "22",
        "mode": "paper_only",
        "validation_time": VALIDATION_TIME,
        "supported_symbols": sorted(SUPPORTED_SYMBOLS),
        "supported_timeframes": sorted(SUPPORTED_TIMEFRAMES),
        "minimum_confidence": MIN_CONFIDENCE,
        "signals": results,
        **SAFETY_STATUS,
    }
    scorecard = {
        "scorecard_id": "PAPER_SIGNAL_TEST_PACK_SCORECARD_001",
        "phase": "22",
        "mode": "paper_only",
        "total_signals": len(results),
        "accepted": counts.get("ACCEPTED", 0),
        "rejected": counts.get("REJECTED", 0),
        "review_required": counts.get("REVIEW_REQUIRED", 0),
        "blocked_reasons": blocked_reasons,
        "next_safe_action": "Review rejected paper signals, then decide whether to expand Phase 21 gates.",
        **SAFETY_STATUS,
    }
    validation_report = {
        "validation_report_id": "PAPER_SIGNAL_TEST_PACK_VALIDATION_REPORT_001",
        "phase": "22",
        "mode": "paper_only",
        "result": "PASS" if len(results) == 10 and counts.get("ACCEPTED", 0) == 2 and counts.get("REJECTED", 0) == 8 else "REVIEW",
        "expected_total_signals": 10,
        "actual_total_signals": len(results),
        "expected_accepted": 2,
        "actual_accepted": counts.get("ACCEPTED", 0),
        "expected_rejected": 8,
        "actual_rejected": counts.get("REJECTED", 0),
        "gates": [
            "phase_21_required_fields",
            "phase_21_stale_signal",
            "phase_21_clock_skew",
            "phase_21_direction",
            "phase_22_confidence",
            "phase_22_supported_symbol",
            "phase_22_supported_timeframe",
            "phase_22_duplicate_signal",
        ],
        **SAFETY_STATUS,
    }

    write_json(RESULT_ROOT / "PAPER_SIGNAL_TEST_PACK_LEDGER_001.json", ledger)
    write_json(RESULT_ROOT / "PAPER_SIGNAL_TEST_PACK_SCORECARD_001.json", scorecard)
    write_json(RESULT_ROOT / "PAPER_SIGNAL_TEST_PACK_VALIDATION_REPORT_001.json", validation_report)
    return {"ledger": ledger, "scorecard": scorecard, "validation_report": validation_report}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the AI_OS Phase 22 paper signal test pack.")
    parser.add_argument("--json", action="store_true", help="Print the full result as JSON.")
    args = parser.parse_args()
    result = run_test_pack()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        scorecard = result["scorecard"]
        print("AI_OS Phase 22 Paper Signal Test Pack")
        print(f"Total signals: {scorecard['total_signals']}")
        print(f"Accepted: {scorecard['accepted']}")
        print(f"Rejected: {scorecard['rejected']}")
        print("Safety: paper-only local fixtures; execution remains blocked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
