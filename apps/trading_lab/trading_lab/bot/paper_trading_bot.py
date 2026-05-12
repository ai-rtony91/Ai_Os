from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from trading_lab.ingest.paper_signal_api import (
    REPO_ROOT,
    SAFETY_STATUS,
    parse_utc,
    process_paper_signal,
)


BOT_RESULT_ROOT = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "results" / "bot"
DEFAULT_SIGNAL_FIXTURE = (
    REPO_ROOT
    / "apps"
    / "trading_lab"
    / "trading_lab"
    / "fixtures"
    / "paper_signal_api"
    / "PAPER_SIGNAL_API_VALID_001.json"
)
DASHBOARD_STATUS_FIXTURE = REPO_ROOT / "apps" / "dashboard" / "mock-data" / "paper-trading-bot-status.example.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def bot_decision_from_intake(intake_result: dict[str, Any]) -> str:
    validation = intake_result["validation_result"]
    route = intake_result["paper_route_preview"]
    if validation.get("validation_status") == "PASS" and route.get("paper_route_status") == "PAPER_PREVIEW_ONLY":
        return "ACCEPT"
    if validation.get("validation_status") == "REJECTED":
        return "REJECT"
    return "REVIEW"


def build_paper_result(decision: str, intake_result: dict[str, Any]) -> dict[str, Any]:
    validation = intake_result["validation_result"]
    route = intake_result["paper_route_preview"]
    if decision == "ACCEPT":
        return {
            "paper_result_id": "PAPER_TRADING_BOT_RESULT_001",
            "mode": "paper_only",
            "paper_result_status": "PAPER_RESULT_PREVIEW",
            "result_summary": "Paper route preview accepted for local review only. No order was placed.",
            "route_preview_id": route.get("paper_route_preview_id"),
            "validation_status": validation.get("validation_status"),
            **SAFETY_STATUS,
        }
    return {
        "paper_result_id": "PAPER_TRADING_BOT_RESULT_001",
        "mode": "paper_only",
        "paper_result_status": "BLOCKED",
        "result_summary": validation.get("blocked_reason", "Paper bot result remains under review."),
        "route_preview_id": route.get("paper_route_preview_id"),
        "validation_status": validation.get("validation_status"),
        **SAFETY_STATUS,
    }


def build_bot_outputs(signal_payload: dict[str, Any], intake_result: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    decision = bot_decision_from_intake(intake_result)
    ledger = intake_result["ledger"]
    validation = intake_result["validation_result"]
    route = intake_result["paper_route_preview"]
    paper_result = build_paper_result(decision, intake_result)
    normalized_signal = ledger.get("normalized_signal", {})
    status = {
        "bot_status_id": "PAPER_TRADING_BOT_STATUS_001",
        "mode": "paper_only",
        "bot_name": "AI_OS Paper Trading Bot Prototype",
        "bot_status": "PAPER_BOT_READY" if decision == "ACCEPT" else "PAPER_BOT_BLOCKED",
        "decision": decision,
        "signal_source": signal_payload.get("source", "LOCAL_SAMPLE"),
        "symbol": normalized_signal.get("symbol", signal_payload.get("symbol")),
        "timeframe": normalized_signal.get("timeframe", signal_payload.get("timeframe")),
        "direction": normalized_signal.get("direction", signal_payload.get("direction")),
        "strategy_id": normalized_signal.get("strategy_id", signal_payload.get("strategy_id")),
        "validation_status": validation.get("validation_status"),
        "paper_route_status": route.get("paper_route_status"),
        "paper_result_status": paper_result["paper_result_status"],
        "visible_status_output": f"{decision}: {paper_result['result_summary']}",
        "next_safe_action": "Review the paper bot status and keep all execution paths blocked.",
        **SAFETY_STATUS,
    }
    result_ledger = {
        "bot_ledger_id": "PAPER_TRADING_BOT_LEDGER_001",
        "mode": "paper_only",
        "decision": decision,
        "signal_payload": signal_payload,
        "paper_signal_intake": ledger,
        "validation_decision": validation,
        "paper_route_preview": route,
        "paper_result": paper_result,
        "live_execution": "BLOCKED",
        "broker": "BLOCKED",
        "oanda": "BLOCKED",
        "webull": "BLOCKED",
        "api_keys": "BLOCKED",
        "secrets": "BLOCKED",
        "real_webhooks": "BLOCKED",
        "real_orders": "BLOCKED",
        **SAFETY_STATUS,
    }
    return status, result_ledger


def run_bot(signal_fixture: Path = DEFAULT_SIGNAL_FIXTURE, validation_time: datetime | None = None) -> dict[str, Any]:
    signal_payload = read_json(signal_fixture)
    intake_result = process_paper_signal(signal_payload, validation_time=validation_time, write_outputs=True)
    status, ledger = build_bot_outputs(signal_payload, intake_result)
    write_json(BOT_RESULT_ROOT / "PAPER_TRADING_BOT_STATUS_001.json", status)
    write_json(BOT_RESULT_ROOT / "PAPER_TRADING_BOT_LEDGER_001.json", ledger)
    write_json(DASHBOARD_STATUS_FIXTURE, status)
    return {"status": status, "ledger": ledger}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the AI_OS paper-only trading bot prototype.")
    parser.add_argument("--fixture", default=str(DEFAULT_SIGNAL_FIXTURE), help="Local paper signal fixture.")
    parser.add_argument("--validation-time", default=None, help="Optional ISO validation time for deterministic dry runs.")
    args = parser.parse_args()
    validation_time = parse_utc(args.validation_time) if args.validation_time else None
    result = run_bot(Path(args.fixture), validation_time=validation_time)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
