"""Sanitize and classify repository-local genuine Forex demo evidence."""

from __future__ import annotations

import argparse
import json
import math
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

SCHEMA = "AIOS_FOREX_GENUINE_DEMO_EVIDENCE_INTAKE.v1"
MODE = "READ_ONLY_SANITIZED_EVIDENCE_INTAKE"
DEMO_CRITERIA = (
    "DEMO_GENUINE_MARKET_EVIDENCE", "DEMO_EVIDENCE_FRESH", "DEMO_METRICS_COMPLETE",
    "DEMO_SYSTEM_MINIMUM", "DEMO_RECEIPT_READY", "POST_TRADE_REVIEW_READY",
)
OWNER_TASK = "CAPTURE_ONE_SANITIZED_OANDA_PRACTICE_TRADE_RECEIPT"
REQUIRED_FIELDS = (
    "evidence schema", "evidence timestamp", "session date", "broker family label",
    "environment DEMO or PRACTICE", "instrument", "side", "sanitized size or units",
    "trade state OPEN or CLOSED", "entry timestamp", "entry price",
    "exit timestamp when closed", "exit price when closed", "realized PnL when closed",
    "sanitized unrealized PnL when open", "stop-loss state", "take-profit state",
    "one-order-only confirmation", "no-retry confirmation", "no-live-money confirmation",
    "broker-origin confirmation", "evidence freshness", "secret_values_recorded false",
    "private_identifiers_recorded false", "raw_broker_payload_recorded false",
    "credential_values_recorded false", "account_identifiers_recorded false",
    "live_trading_allowed false", "money_movement_allowed false",
)
SENSITIVE_KEYS = {"access_token", "api_key", "account_id", "account_identifier", "broker_order_id", "authorization"}


def _iso(value: str | None) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def _walk(value: Any):
    if isinstance(value, Mapping):
        for key, item in value.items():
            yield str(key).lower(), item
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


def _record(path: str, source_type: str = "structured") -> dict[str, Any]:
    return {"source_path": path, "source_type": source_type, "source_schema": None,
            "classification": "UNCLASSIFIED", "evidence_date": None, "freshness_days": None,
            "broker_family": None, "environment": None, "session_mode": None,
            "record_type": None, "trade_state": None, "trade_count": 0,
            "broker_origin_verified": False, "sanitized": False,
            "secret_values_present": False, "account_identifiers_present": False,
            "raw_broker_payload_present": False, "fixture_markers_present": False,
            "paper_markers_present": False, "finite_numeric_fields": True,
            "accepted_for_genuine_demo": False, "accepted_for_metrics": False,
            "rejection_reasons": []}


def classify_genuine_demo_source(source_path: str, payload: Any, *, as_of_date: str | None = None) -> dict[str, Any]:
    """Classify one parsed source without retaining private values."""
    record = _record(source_path)
    if not isinstance(payload, Mapping):
        record["classification"] = "UNCLASSIFIED"
        record["rejection_reasons"] = ["structured mapping required"]
        return record
    flat = list(_walk(payload))
    keys = {key for key, _ in flat}
    text = " ".join(str(value).lower() for _, value in flat if isinstance(value, str))
    get = lambda *names: next((payload[name] for name in names if name in payload), None)
    record.update(source_schema=get("schema", "evidence_schema"), broker_family=get("broker_family", "broker"),
                  environment=get("environment"), session_mode=get("session_mode"),
                  record_type=get("record_type", "evidence_type", "day_type"),
                  trade_state=str(get("trade_state", "state") or "").upper() or None)
    trades = payload.get("trades")
    record["trade_count"] = int(payload.get("trade_count", len(trades) if isinstance(trades, list) else 0) or 0)
    record["broker_origin_verified"] = payload.get("broker_origin_verified", payload.get("broker_origin_confirmation")) is True
    false_flags = ("secret_values_recorded", "credential_values_recorded", "private_identifiers_recorded",
                   "account_identifiers_recorded", "raw_broker_payload_recorded")
    record["sanitized"] = payload.get("sanitized") is True or all(payload.get(key) is False for key in false_flags)
    record["secret_values_present"] = any((key in SENSITIVE_KEYS or "credential" in key) and value not in (False, None, "") for key, value in flat)
    record["account_identifiers_present"] = any(("account_id" in key or "account_identifier" in key) and value not in (False, None, "") for key, value in flat)
    record["raw_broker_payload_present"] = any(("raw_request" in key or "raw_response" in key or "raw_broker_payload" in key) and value not in (False, None, "") for key, value in flat)
    record["fixture_markers_present"] = any(word in text for word in ("fixture", "synthetic", "mock", "initial_stub"))
    record["paper_markers_present"] = "paper_simulation" in text or "paper_signal_execution_loop" in text
    numbers = [value for _, value in flat if isinstance(value, (int, float)) and not isinstance(value, bool)]
    record["finite_numeric_fields"] = all(math.isfinite(float(value)) for value in numbers)
    evidence_value = get("evidence_timestamp", "evidence_date", "session_date", "as_of_utc", "freshness_utc")
    evidence_dt = _iso(str(evidence_value)) if evidence_value else None
    record["evidence_date"] = evidence_dt.isoformat().replace("+00:00", "Z") if evidence_dt else None
    as_of = _iso((as_of_date or date.today().isoformat()) + ("T00:00:00Z" if len(as_of_date or date.today().isoformat()) == 10 else ""))
    if evidence_dt and as_of:
        record["freshness_days"] = max((as_of.date() - evidence_dt.date()).days, 0)
    reasons = record["rejection_reasons"]
    lower_path = source_path.lower()
    if lower_path.endswith(".md"):
        record["source_type"] = "narrative_markdown"
        reasons.append("narrative prose alone is not structured evidence")
    if record["fixture_markers_present"]: reasons.append("fixture, mock, synthetic, or stub marker")
    if record["paper_markers_present"] or str(record["session_mode"]).upper() == "PAPER_SIMULATION": reasons.append("paper simulation marker")
    if any(word in text for word in ("command_package_only", "procedure_only", "telemetry_blocked", "telemetry_rejected", "evidence_not_supplied")):
        reasons.append("non-evidence or blocked evidence marker")
    if record["secret_values_present"]: reasons.append("sensitive value risk")
    if record["account_identifiers_present"]: reasons.append("account identifier risk")
    if record["raw_broker_payload_present"]: reasons.append("raw broker payload risk")
    if any(payload.get(key) is True for key in ("live_trading_allowed", "money_movement_allowed", "live_capital")): reasons.append("protected live flag is true")
    if not record["finite_numeric_fields"]: reasons.append("non-finite numeric value")
    if not evidence_dt: reasons.append("evidence date missing")
    if record["freshness_days"] is not None and record["freshness_days"] > 7: reasons.append("stale evidence")
    broker_ok = "oanda" in str(record["broker_family"]).lower()
    environment_ok = str(record["environment"]).upper() in {"DEMO", "PRACTICE"}
    state_ok = record["trade_state"] in {"OPEN", "CLOSED"}
    if not broker_ok: reasons.append("supported broker-demo family not verified")
    if not environment_ok: reasons.append("DEMO or PRACTICE environment not verified")
    if not record["broker_origin_verified"]: reasons.append("broker origin not verified")
    if not record["sanitized"]: reasons.append("sanitization not verified")
    if record["trade_count"] < 1: reasons.append("trade count is below one")
    if not state_ok: reasons.append("OPEN or CLOSED trade state not verified")
    record["accepted_for_genuine_demo"] = not reasons
    closed_complete = record["trade_state"] == "CLOSED" and all(payload.get(k) is not None for k in ("realized_pnl", "drawdown")) and payload.get("post_trade_review") is True
    rows_complete = isinstance(trades, list) and bool(trades) and all(isinstance(row, Mapping) and row.get("realized_pnl") is not None for row in trades)
    record["accepted_for_metrics"] = record["accepted_for_genuine_demo"] and closed_complete and rows_complete
    if record["accepted_for_genuine_demo"]:
        record["classification"] = "GENUINE_SANITIZED_OPEN_DEMO_TRADE" if record["trade_state"] == "OPEN" else "GENUINE_SANITIZED_CLOSED_DEMO_TRADE"
    elif record["secret_values_present"] or record["account_identifiers_present"] or record["raw_broker_payload_present"]:
        record["classification"] = "SANITIZED_TELEMETRY_REJECTED"
    elif record["paper_markers_present"]: record["classification"] = "PAPER_SIMULATION"
    elif record["fixture_markers_present"]: record["classification"] = "OFFLINE_FIXTURE"
    elif "command" in text or "runbook" in lower_path: record["classification"] = "COMMAND_PACKAGE_ONLY"
    elif "blocked" in text: record["classification"] = "BROKER_TELEMETRY_BLOCKED"
    elif "not_supplied" in text: record["classification"] = "EVIDENCE_NOT_SUPPLIED"
    elif "stale evidence" in reasons: record["classification"] = "STALE"
    return record


def load_genuine_demo_source_inventory(repo_root: str | Path, *, as_of_date: str | None = None) -> list[dict[str, Any]]:
    root = Path(repo_root).resolve()
    delivery = root / "Reports/forex_delivery"
    paths = [root / "telemetry/forex/demo_proof_ledger.jsonl"]
    generated = {"AIOS_FOREX_GENUINE_DEMO_EVIDENCE_INTAKE_V1_STATE.json", "AIOS_FOREX_GENUINE_DEMO_EVIDENCE_INTAKE_V1_REPORT.md", "AIOS_FOREX_LIVE_READINESS_FORECAST_V1_STATE.json", "AIOS_FOREX_LIVE_READINESS_FORECAST_V1_REPORT.md"}
    paths += sorted(p for p in delivery.glob("*") if p.name not in generated and p.suffix.lower() in {".json", ".jsonl", ".md"} and ("DEMO" in p.name.upper() or "OANDA" in p.name.upper()))
    inventory = []
    for path in paths:
        rel = path.relative_to(root).as_posix()
        if path.suffix.lower() == ".md":
            inventory.append(classify_genuine_demo_source(rel, {"record_type": "NARRATIVE", "text": path.read_text(encoding="utf-8", errors="replace")[:20000]}, as_of_date=as_of_date))
            continue
        try:
            text = path.read_text(encoding="utf-8")
            values = [json.loads(line) for line in text.splitlines() if line.strip()] if path.suffix.lower() == ".jsonl" else [json.loads(text)]
            for index, value in enumerate(values):
                label = f"{rel}#{index + 1}" if len(values) > 1 else rel
                inventory.append(classify_genuine_demo_source(label, value, as_of_date=as_of_date))
        except (OSError, UnicodeError, json.JSONDecodeError):
            item = _record(rel); item["classification"] = "PARSE_FAILURE"; item["rejection_reasons"] = ["source parse failed"]
            inventory.append(item)
    return inventory


def _criterion(cid: str, passed: bool, source: str | None, summary: str, blocker: str | None) -> dict[str, Any]:
    return {"criterion_id": cid, "status": "PASS" if passed else "NOT_VERIFIED", "source_path": source,
            "evidence_summary": summary, "blocker": blocker, "closure_condition": None if passed else OWNER_TASK,
            "evidence_freshness": "CURRENT" if passed else "NOT_VERIFIED", "counted_for_progress": passed}


def build_genuine_demo_evidence_bundle(inventory: Sequence[Mapping[str, Any]], *, as_of_date: str | None = None) -> dict[str, Any]:
    qualifying = [dict(item) for item in inventory if item.get("accepted_for_genuine_demo")]
    excluded = [dict(item) for item in inventory if not item.get("accepted_for_genuine_demo") and item.get("classification") != "PARSE_FAILURE"]
    failures = [dict(item) for item in inventory if item.get("classification") == "PARSE_FAILURE"]
    sensitive = any(item.get("secret_values_present") or item.get("account_identifiers_present") or item.get("raw_broker_payload_present") for item in inventory)
    source = qualifying[0]["source_path"] if qualifying else None
    closed = any(item.get("accepted_for_metrics") for item in qualifying)
    fresh = any(item.get("freshness_days") is not None and item["freshness_days"] <= 7 for item in qualifying)
    receipt = bool(qualifying)
    criteria = [
        _criterion("DEMO_GENUINE_MARKET_EVIDENCE", bool(qualifying), source, "Sanitized broker-origin demo trade verified." if qualifying else "No qualifying structured broker-origin demo trade found.", None if qualifying else OWNER_TASK),
        _criterion("DEMO_EVIDENCE_FRESH", fresh, source if fresh else None, "Evidence is within seven days." if fresh else "Current genuine demo evidence not verified.", None if fresh else OWNER_TASK),
        _criterion("DEMO_METRICS_COMPLETE", closed, source if closed else None, "Closed-trade metrics are complete." if closed else "Terminal metrics not verified.", None if closed else "Capture complete closed-trade metrics."),
        _criterion("DEMO_SYSTEM_MINIMUM", closed, source if closed else None, "Minimum complete demo result verified." if closed else "System minimum not verified.", None if closed else "Complete the canonical demo minimum."),
        _criterion("DEMO_RECEIPT_READY", receipt, source, "Sanitized trade receipt verified." if receipt else "Sanitized trade receipt absent.", None if receipt else OWNER_TASK),
        _criterion("POST_TRADE_REVIEW_READY", closed, source if closed else None, "Post-trade review verified." if closed else "Post-trade review requires terminal evidence.", None if closed else "Capture terminal evidence and post-trade review."),
    ]
    if sensitive: status = "BLOCKED_SENSITIVE_DATA_RISK"
    elif failures: status = "BLOCKED_INVALID_SOURCE_EVIDENCE"
    elif closed: status = "QUALIFYING_CLOSED_DEMO_EVIDENCE_FOUND"
    elif qualifying: status = "QUALIFYING_OPEN_DEMO_EVIDENCE_FOUND"
    else: status = "BLOCKED_GENUINE_DEMO_EVIDENCE_NOT_FOUND"
    forecast_input = {"schema": SCHEMA, "criterion_ids": list(DEMO_CRITERIA), "criteria": {item["criterion_id"]: {**item, "source_type": "genuine_demo_intake", "source_schema": SCHEMA} for item in criteria}}
    return {"schema": SCHEMA, "mode": MODE, "as_of_utc": (as_of_date or date.today().isoformat()) + "T00:00:00Z", "status": status,
            "source_inventory": list(inventory), "qualifying_records": qualifying, "excluded_records": excluded,
            "conflicting_records": [], "parse_failures": failures,
            "ledger_summary": {"source_path": "telemetry/forex/demo_proof_ledger.jsonl", "modified": False},
            "criteria_evidence": criteria, "forecast_input": forecast_input,
            "owner_evidence_requirement": {"owner_evidence_status": None if qualifying else "OWNER_SANITIZED_DEMO_EVIDENCE_REQUIRED", "required_sanitized_fields": list(REQUIRED_FIELDS), "prohibited_fields": sorted(SENSITIVE_KEYS)},
            "next_verified_task": OWNER_TASK if not qualifying else ("CAPTURE_TERMINAL_DEMO_TRADE_EVIDENCE" if not closed else "REVIEW_NEXT_LIVE_READINESS_BLOCKER"),
            "evidence_limitations": ["Repository-local structured evidence only.", "No external evidence capture was performed."],
            "permissions": {key: False for key in ("live_execution_authorized", "broker_connection_authorized", "credential_access_authorized", "account_identifier_access_authorized", "order_placement_authorized", "money_movement_authorized")},
            "protected_actions": {key: False for key in ("network_request", "broker_call", "credential_access", "account_id_access", "order_placement", "money_movement", "worker_creation", "scheduler_creation", "daemon_creation", "webhook_creation")}}


def render_genuine_demo_evidence_report(state: Mapping[str, Any]) -> str:
    return f"""# 🧪 AIOS FOREX — GENUINE DEMO EVIDENCE

## 🔴 CURRENT ANSWER
`{state['status']}`

## ✅ QUALIFYING EVIDENCE
{len(state['qualifying_records'])} qualifying record(s).

## 🚫 EXCLUDED EVIDENCE
{len(state['excluded_records'])} excluded record(s).

## ⚠️ CONFLICTS AND DATA QUALITY
{len(state['conflicting_records'])} conflict(s); {len(state['parse_failures'])} parse failure(s).

## 📦 CANONICAL LEDGER FINDING
The canonical ledger was read only and was not modified.

## 📉 EFFECT ON FIRST-TRADE COUNTDOWN
Only PASS criteria in `forecast_input` receive progress credit.

## ⛔ HIGHEST BLOCKER
`{next((item['criterion_id'] for item in state['criteria_evidence'] if item['status'] != 'PASS'), 'NONE')}`

## ▶️ NEXT VERIFIED TASK
`{state['next_verified_task']}`

## 🔐 SANITIZED OWNER EVIDENCE REQUIRED
`{state['owner_evidence_requirement']['owner_evidence_status'] or 'NOT_REQUIRED'}`. Never provide credentials, account IDs, broker order IDs, raw payloads, balances, or private screenshots.

## 🌐 EXTERNAL EVIDENCE BOUNDARY
No network or broker access occurred. External capture is a separate owner-reviewed task.

## 🧪 VALIDATION
Structured sources are fail-closed against sanitization, origin, freshness, and completeness rules.

## 🛑 NO-BROKER-ACTION CONFIRMATION
Broker calls, credential access, account access, orders, and money movement are false.
"""


def stable_json(value: Mapping[str, Any], pretty: bool = True) -> str:
    return json.dumps(value, indent=2 if pretty else None, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default="."); parser.add_argument("--as-of-date")
    parser.add_argument("--state-output"); parser.add_argument("--report-output"); parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)
    state = build_genuine_demo_evidence_bundle(load_genuine_demo_source_inventory(args.repo_root, as_of_date=args.as_of_date), as_of_date=args.as_of_date)
    rendered = stable_json(state, args.pretty)
    if args.state_output: Path(args.state_output).write_text(rendered, encoding="utf-8")
    if args.report_output: Path(args.report_output).write_text(render_genuine_demo_evidence_report(state), encoding="utf-8")
    print(rendered, end=""); return 0


if __name__ == "__main__":
    raise SystemExit(main())
