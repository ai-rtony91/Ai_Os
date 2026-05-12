from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[4]
RESULT_ROOT = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "results"
BOT_STATUS_PATH = RESULT_ROOT / "bot" / "PAPER_TRADING_BOT_STATUS_001.json"
BOT_LEDGER_PATH = RESULT_ROOT / "bot" / "PAPER_TRADING_BOT_LEDGER_001.json"
TEST_PACK_LEDGER_PATH = RESULT_ROOT / "paper_signal_test_pack" / "PAPER_SIGNAL_TEST_PACK_LEDGER_001.json"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"_load_status": "MISSING", "_path": str(path)}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"_load_status": "INVALID DATA", "_path": str(path), "_error": str(exc)}
    if not isinstance(data, dict):
        return {"_load_status": "INVALID DATA", "_path": str(path), "_error": "JSON root is not an object."}
    data["_load_status"] = "PASS"
    return data


def first_value(*values: Any, default: str = "UNKNOWN") -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return default


def count_reason(signals: list[dict[str, Any]], text: str) -> int:
    target = text.lower()
    return sum(1 for signal in signals if target in str(signal.get("blocked_reason", "")).lower())


def numeric_values(*values: Any) -> list[float]:
    numbers: list[float] = []
    for value in values:
        if isinstance(value, (int, float)):
            numbers.append(float(value))
    return numbers


def build_scorecard() -> str:
    status = load_json(BOT_STATUS_PATH)
    ledger = load_json(BOT_LEDGER_PATH)
    test_pack = load_json(TEST_PACK_LEDGER_PATH)

    signals = test_pack.get("signals", [])
    if not isinstance(signals, list):
        signals = []
    signal_rows = [signal for signal in signals if isinstance(signal, dict)]

    accept_count = sum(1 for signal in signal_rows if signal.get("batch_status") in {"ACCEPT", "ACCEPTED"})
    reject_count = sum(1 for signal in signal_rows if signal.get("batch_status") in {"REJECT", "REJECTED"})
    review_count = sum(1 for signal in signal_rows if signal.get("batch_status") in {"REVIEW", "REVIEW_REQUIRED"})

    latest_signal = ledger.get("signal_payload")
    if not isinstance(latest_signal, dict):
        latest_signal = {}

    latest_latency = status.get("latest_latency")
    if not isinstance(latest_latency, dict):
        latest_latency = {}
    ledger_latency = ledger.get("latency")
    if not isinstance(ledger_latency, dict):
        ledger_latency = {}
    validation = ledger.get("validation_decision")
    if not isinstance(validation, dict):
        validation = {}

    latency_samples = numeric_values(
        latest_latency.get("total_delay_seconds"),
        ledger_latency.get("total_delay_seconds"),
    )
    average_latency = round(mean(latency_samples), 2) if latency_samples else "UNKNOWN"

    latest_decision = first_value(status.get("decision"), ledger.get("decision"))
    latest_symbol = first_value(status.get("symbol"), latest_signal.get("symbol"))
    latest_confidence = first_value(latest_signal.get("confidence"))
    stale_reject_count = count_reason(signal_rows, "stale")
    clock_skew_reject_count = count_reason(signal_rows, "clock skew")
    live_status = first_value(
        status.get("live_execution_status"),
        ledger.get("live_execution_status"),
        ledger.get("live_execution"),
    )
    stale_status = first_value(latest_latency.get("stale_status"), validation.get("stale_signal_status"))
    clock_skew_status = first_value(latest_latency.get("clock_skew_status"), validation.get("clock_skew_status"))

    safety = "PAPER LOCAL; live/broker/API/secrets/orders BLOCKED."
    if live_status != "BLOCKED":
        safety = "INVALID DATA: live execution is not verified as BLOCKED."

    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return "\n".join(
        [
            "# Paper Signal Scorecard",
            "",
            f"Generated at: {generated_at}",
            "",
            f"Signals: ACCEPT {accept_count} | REJECT {reject_count} | REVIEW {review_count}",
            f"Latest: {latest_decision} {latest_symbol} confidence {latest_confidence}",
            f"Latency: average {average_latency}s | latest stale {stale_status} | latest clock skew {clock_skew_status}",
            f"Rejected by stale signal: {stale_reject_count}",
            f"Rejected by clock skew: {clock_skew_reject_count}",
            f"Live trading: {live_status}",
            f"Safety: {safety}",
            "",
            "Next safe action: Review rejected paper signals; keep runtime paper-only and local-only.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Print a compact AI_OS paper signal scorecard.")
    parser.add_argument("--output", type=Path, help="Optional markdown output path.")
    args = parser.parse_args()

    report = build_scorecard()
    print(report, end="")

    if args.output:
        output_path = args.output if args.output.is_absolute() else REPO_ROOT / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
