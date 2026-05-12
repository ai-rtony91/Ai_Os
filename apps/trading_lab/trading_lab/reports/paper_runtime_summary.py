from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[4]
BOT_RESULTS_ROOT = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "results" / "bot"
STATUS_PATH = BOT_RESULTS_ROOT / "PAPER_TRADING_BOT_STATUS_001.json"
LEDGER_PATH = BOT_RESULTS_ROOT / "PAPER_TRADING_BOT_LEDGER_001.json"


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


def nested(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def build_summary() -> str:
    status = load_json(STATUS_PATH)
    ledger = load_json(LEDGER_PATH)

    latency = first_value(status.get("latest_latency"), ledger.get("latency"), default={})
    if not isinstance(latency, dict):
        latency = {}

    validation = nested(ledger, "validation_decision")
    if not isinstance(validation, dict):
        validation = {}

    signal_payload = ledger.get("signal_payload")
    if not isinstance(signal_payload, dict):
        signal_payload = {}

    paper_decision = first_value(status.get("decision"), ledger.get("decision"))
    live_status = first_value(
        status.get("live_execution_status"),
        ledger.get("live_execution_status"),
        ledger.get("live_execution"),
    )
    symbol = first_value(status.get("symbol"), signal_payload.get("symbol"))
    latency_seconds = first_value(
        latency.get("total_delay_seconds"),
        validation.get("signal_age_seconds"),
    )
    stale_status = first_value(latency.get("stale_status"), validation.get("stale_signal_status"))
    clock_skew_status = first_value(latency.get("clock_skew_status"), validation.get("clock_skew_status"))
    ledger_display = LEDGER_PATH.relative_to(REPO_ROOT).as_posix()

    status_load = status.get("_load_status", "UNKNOWN")
    ledger_load = ledger.get("_load_status", "UNKNOWN")
    safety_note = "Live trading remains BLOCKED. Broker, API keys, secrets, real webhooks, and real orders remain BLOCKED."
    if live_status != "BLOCKED":
        safety_note = "INVALID DATA: live trading status is not verified as BLOCKED in the local JSON evidence."

    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return "\n".join(
        [
            "# AI_OS Paper Runtime Operator Summary",
            "",
            f"Generated at: {generated_at}",
            "",
            "Local paper runtime visibility:",
            f"- Latest paper decision: {paper_decision}",
            f"- Live trading status: {live_status}",
            f"- Latest symbol: {symbol}",
            f"- Latency seconds: {latency_seconds}",
            f"- Stale status: {stale_status}",
            f"- Clock skew status: {clock_skew_status}",
            f"- Ledger path: {ledger_display}",
            "",
            "Local evidence files:",
            f"- Status JSON: {STATUS_PATH.relative_to(REPO_ROOT).as_posix()} ({status_load})",
            f"- Ledger JSON: {ledger_display} ({ledger_load})",
            "",
            f"Safety: {safety_note}",
            "",
            "Next safe action: Review this summary and keep all runtime work paper-only and local-only.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the AI_OS paper runtime operator summary.")
    parser.add_argument("--output", type=Path, help="Optional markdown file path for the generated summary.")
    args = parser.parse_args()

    summary = build_summary()
    print(summary, end="")

    if args.output:
        output_path = args.output if args.output.is_absolute() else REPO_ROOT / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(summary, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
