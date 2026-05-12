from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from fastapi import FastAPI
except ImportError:  # pragma: no cover - keeps local parsing usable without server startup.
    FastAPI = None  # type: ignore[assignment]


REPO_ROOT = Path(__file__).resolve().parents[4]
RESULT_ROOT = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "results" / "paper_signal_api"

REQUIRED_FIELDS = ("symbol", "timeframe", "direction", "strategy_id", "confidence", "alert_time", "source")
MAX_SIGNAL_AGE_SECONDS = 900
MAX_CLOCK_SKEW_SECONDS = 120

SAFETY_STATUS = {
    "route_mode": "PAPER_PREVIEW_ONLY",
    "live_execution_status": "BLOCKED",
    "broker_status": "BLOCKED",
    "oanda_status": "BLOCKED",
    "api_key_status": "BLOCKED",
    "secrets_status": "BLOCKED",
    "real_webhook_status": "BLOCKED",
    "real_order_status": "BLOCKED",
}

DIRECTION_MAP = {
    "long": "LONG_REVIEW",
    "buy": "LONG_REVIEW",
    "long_review": "LONG_REVIEW",
    "short": "SHORT_REVIEW",
    "sell": "SHORT_REVIEW",
    "short_review": "SHORT_REVIEW",
}

app = FastAPI(title="AI_OS Paper Signal Intake") if FastAPI else None


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def now_utc() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def now_utc_iso() -> str:
    return now_utc().isoformat().replace("+00:00", "Z")


def normalize_direction(value: Any) -> str | None:
    return DIRECTION_MAP.get(str(value or "").strip().lower())


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def build_rejection(reason: str, payload: dict[str, Any], validation_time: datetime) -> dict[str, Any]:
    validation_time_text = validation_time.isoformat().replace("+00:00", "Z")
    validation_result = {
        "validation_result_id": "PAPER_SIGNAL_VALIDATION_RESULT_001",
        "mode": "paper_only",
        "validation_status": "REJECTED",
        "blocked_reason": reason,
        "validated_at": validation_time_text,
        "missing_fields": [field for field in REQUIRED_FIELDS if field not in payload or payload.get(field) in (None, "")],
        "clock_skew_status": "NOT_EVALUATED",
        "stale_signal_status": "NOT_EVALUATED",
        **SAFETY_STATUS,
    }
    route_preview = {
        "paper_route_preview_id": "PAPER_ROUTE_PREVIEW_001",
        "mode": "paper_only",
        "paper_route_status": "BLOCKED",
        "blocked_reason": reason,
        "target_platform": "TRADERSPOST_REFERENCE",
        "next_safe_action": "Fix the local paper signal payload and rerun the dry-run validator.",
        **SAFETY_STATUS,
    }
    ledger = {
        "paper_signal_intake_ledger_id": "PAPER_SIGNAL_INTAKE_LEDGER_001",
        "mode": "paper_only",
        "intake_status": "REJECTED",
        "source": payload.get("source", "UNKNOWN"),
        "received_at": validation_time_text,
        "blocked_reason": reason,
        **SAFETY_STATUS,
    }
    return {
        "ledger": ledger,
        "validation_result": validation_result,
        "paper_route_preview": route_preview,
    }


def validate_payload(payload: dict[str, Any], validation_time: datetime) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if field not in payload or payload.get(field) in (None, "")]
    if missing:
        return build_rejection(f"Missing required fields: {', '.join(missing)}.", payload, validation_time)

    direction = normalize_direction(payload.get("direction"))
    if not direction:
        return build_rejection("Direction is not a paper review value.", payload, validation_time)

    try:
        alert_time = parse_utc(str(payload["alert_time"]))
    except ValueError:
        return build_rejection("Alert time is not valid ISO time.", payload, validation_time)

    age_seconds = int((validation_time - alert_time).total_seconds())
    if age_seconds < -MAX_CLOCK_SKEW_SECONDS:
        result = build_rejection("Clock skew detected: alert time is too far ahead.", payload, validation_time)
        result["validation_result"]["clock_skew_status"] = "CLOCK_SKEW_DETECTED"
        result["validation_result"]["signal_age_seconds"] = age_seconds
        return result

    if age_seconds > MAX_SIGNAL_AGE_SECONDS:
        result = build_rejection("Signal is stale.", payload, validation_time)
        result["validation_result"]["stale_signal_status"] = "STALE_SIGNAL_REJECTED"
        result["validation_result"]["signal_age_seconds"] = age_seconds
        return result

    validation_time_text = validation_time.isoformat().replace("+00:00", "Z")
    normalized = {
        "symbol": str(payload["symbol"]).strip().upper(),
        "timeframe": str(payload["timeframe"]).strip().upper(),
        "direction": direction,
        "strategy_id": str(payload["strategy_id"]).strip(),
        "confidence": float(payload["confidence"]),
        "alert_time": alert_time.isoformat().replace("+00:00", "Z"),
        "source": str(payload["source"]).strip() or "TRADINGVIEW_REFERENCE",
    }
    ledger = {
        "paper_signal_intake_ledger_id": "PAPER_SIGNAL_INTAKE_LEDGER_001",
        "mode": "paper_only",
        "intake_status": "ACCEPTED_FOR_PAPER_PREVIEW",
        "received_at": validation_time_text,
        "normalized_signal": normalized,
        **SAFETY_STATUS,
    }
    validation_result = {
        "validation_result_id": "PAPER_SIGNAL_VALIDATION_RESULT_001",
        "mode": "paper_only",
        "validation_status": "PASS",
        "missing_fields": [],
        "clock_skew_status": "PASS",
        "stale_signal_status": "PASS",
        "signal_age_seconds": age_seconds,
        "validated_at": validation_time_text,
        **SAFETY_STATUS,
    }
    paper_route_preview = {
        "paper_route_preview_id": "PAPER_ROUTE_PREVIEW_001",
        "mode": "paper_only",
        "paper_route_status": "PAPER_PREVIEW_ONLY",
        "target_platform": "TRADERSPOST_REFERENCE",
        "symbol": normalized["symbol"],
        "timeframe": normalized["timeframe"],
        "direction": normalized["direction"],
        "strategy_id": normalized["strategy_id"],
        "validation_status": validation_result["validation_status"],
        "next_safe_action": "Review the paper route preview and keep all execution paths blocked.",
        **SAFETY_STATUS,
    }
    return {
        "ledger": ledger,
        "validation_result": validation_result,
        "paper_route_preview": paper_route_preview,
    }


def process_paper_signal(payload: dict[str, Any], validation_time: datetime | None = None, write_outputs: bool = True) -> dict[str, Any]:
    result = validate_payload(payload, validation_time or now_utc())
    if write_outputs:
        write_json(RESULT_ROOT / "PAPER_SIGNAL_INTAKE_LEDGER_001.json", result["ledger"])
        write_json(RESULT_ROOT / "PAPER_SIGNAL_VALIDATION_RESULT_001.json", result["validation_result"])
        write_json(RESULT_ROOT / "PAPER_ROUTE_PREVIEW_001.json", result["paper_route_preview"])
    return result


def paper_signal(payload: dict[str, Any]) -> dict[str, Any]:
    result = process_paper_signal(payload, write_outputs=True)
    from trading_lab.bot.paper_trading_bot import run_bot_for_payload

    result["paper_bot"] = run_bot_for_payload(payload, intake_result=result)["status"]
    return result


if app:
    app.post("/paper-signal")(paper_signal)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local AI_OS paper signal intake.")
    parser.add_argument("--fixture", required=True, help="Local JSON fixture path.")
    parser.add_argument("--validation-time", default=None, help="Optional ISO validation time.")
    args = parser.parse_args()
    payload = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    validation_time = parse_utc(args.validation_time) if args.validation_time else None
    result = process_paper_signal(payload, validation_time=validation_time, write_outputs=True)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
