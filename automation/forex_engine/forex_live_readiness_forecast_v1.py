"""Read-only evidence forecast for a governed single live Forex micro-trade review."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

SCHEMA = "AIOS_FOREX_LIVE_READINESS_FORECAST.v1"
MODE = "READ_ONLY_EVIDENCE_FORECAST"
MILESTONE = "FIRST_SINGLE_LIVE_MICRO_TRADE_REVIEW_AND_ATTEMPT_ELIGIBILITY"
STATUSES = {"PASS", "BLOCKED", "NOT_VERIFIED", "STALE", "CONFLICT", "WAITING_OWNER", "WAITING_EXTERNAL"}
GENUINE_DEMO_SCHEMA = "AIOS_FOREX_GENUINE_DEMO_EVIDENCE_INTAKE.v1"
GENUINE_DEMO_CRITERIA = {"DEMO_GENUINE_MARKET_EVIDENCE", "DEMO_EVIDENCE_FRESH", "DEMO_METRICS_COMPLETE", "DEMO_SYSTEM_MINIMUM", "DEMO_RECEIPT_READY", "POST_TRADE_REVIEW_READY"}

# Each criterion occurs once. Categories are the numerical denominator; stages are
# the critical-path ordering. File presence never passes a criterion by itself.
CRITERIA_SPEC: tuple[tuple[str, str, str], ...] = (
    ("DEMO_GENUINE_MARKET_EVIDENCE", "demo_evidence", "DEMO_EVIDENCE"),
    ("DEMO_EVIDENCE_FRESH", "demo_evidence", "DEMO_EVIDENCE"),
    ("DEMO_METRICS_COMPLETE", "demo_evidence", "DEMO_EVIDENCE"),
    ("DEMO_SYSTEM_MINIMUM", "demo_evidence", "DEMO_EVIDENCE"),
    ("PROFIT_EXPECTANCY_POSITIVE", "profitability_evidence", "PROFITABILITY_EVIDENCE"),
    ("PROFIT_FACTOR_THRESHOLD", "profitability_evidence", "PROFITABILITY_EVIDENCE"),
    ("DRAWDOWN_THRESHOLD", "profitability_evidence", "PROFITABILITY_EVIDENCE"),
    ("RISK_CONTROLS_PRESENT", "risk_controls", "RISK_AND_TERMINAL_SAFETY"),
    ("RISK_CONTROLS_PASSED", "risk_controls", "RISK_AND_TERMINAL_SAFETY"),
    ("DEMO_RECEIPT_READY", "demo_evidence", "LIVE_MICRO_REVIEW_EVIDENCE"),
    ("POST_TRADE_REVIEW_READY", "demo_evidence", "LIVE_MICRO_REVIEW_EVIDENCE"),
    ("REPEATABILITY_THRESHOLD", "profitability_evidence", "LIVE_MICRO_REVIEW_EVIDENCE"),
    ("RISK_PER_TRADE_CAP", "risk_controls", "RISK_AND_TERMINAL_SAFETY"),
    ("DAILY_LOSS_CAP", "risk_controls", "RISK_AND_TERMINAL_SAFETY"),
    ("KILL_SWITCH_READY", "terminal_safety", "RISK_AND_TERMINAL_SAFETY"),
    ("DAILY_LOSS_STOP_READY", "terminal_safety", "RISK_AND_TERMINAL_SAFETY"),
    ("NO_SECRET_SCAN_CURRENT", "sensitive_data_boundary", "SENSITIVE_DATA_BOUNDARY"),
    ("NO_ACCOUNT_ID_SCAN_CURRENT", "sensitive_data_boundary", "SENSITIVE_DATA_BOUNDARY"),
    ("EXTERNAL_CREDENTIAL_BOUNDARY", "sensitive_data_boundary", "SENSITIVE_DATA_BOUNDARY"),
    ("EXTERNAL_ACCOUNT_REFERENCE_BOUNDARY", "sensitive_data_boundary", "SENSITIVE_DATA_BOUNDARY"),
    ("PRACTICE_ENDPOINT_PROOF", "protected_runtime", "PROTECTED_RUNTIME"),
    ("LIVE_ENDPOINT_DENIAL", "protected_runtime", "PROTECTED_RUNTIME"),
    ("PROTECTED_RUNTIME_CONNECTOR", "protected_runtime", "PROTECTED_RUNTIME"),
    ("ONE_ORDER_ONLY", "protected_runtime", "PROTECTED_RUNTIME"),
    ("NO_RETRY_LOOP", "protected_runtime", "PROTECTED_RUNTIME"),
    ("NO_AUTONOMOUS_REENTRY", "protected_runtime", "PROTECTED_RUNTIME"),
    ("EXPLICIT_ARMING_STEP", "protected_runtime", "PROTECTED_RUNTIME"),
    ("TIMEOUT_CONTROL", "protected_runtime", "PROTECTED_RUNTIME"),
    ("FINAL_DISARM", "terminal_safety", "RISK_AND_TERMINAL_SAFETY"),
    ("ROLLBACK_PROOF", "terminal_safety", "RISK_AND_TERMINAL_SAFETY"),
    ("PRE_TRADE_EVIDENCE_BUNDLE", "exception_package", "EXCEPTION_PACKAGE"),
    ("POST_TRADE_EVIDENCE_BUNDLE", "exception_package", "EXCEPTION_PACKAGE"),
    ("POST_TRADE_JOURNAL", "exception_package", "EXCEPTION_PACKAGE"),
    ("RECONCILIATION_PROOF", "exception_package", "EXCEPTION_PACKAGE"),
    ("OWNER_EXCEPTION_FIELDS_COMPLETE", "owner_approval", "HUMAN_OWNER_APPROVAL"),
    ("OWNER_APPROVAL_VERIFIED", "owner_approval", "HUMAN_OWNER_APPROVAL"),
    ("APPROVAL_WINDOW_CURRENT", "owner_approval", "HUMAN_OWNER_APPROVAL"),
    ("FINAL_VALIDATOR_EVIDENCE", "final_validation", "FINAL_VALIDATION"),
    ("FINAL_EVIDENCE_FRESHNESS", "final_validation", "FINAL_VALIDATION"),
    ("TERMINAL_HARD_STOP_PROOF", "terminal_safety", "RISK_AND_TERMINAL_SAFETY"),
)
STAGES = (
    "DEMO_EVIDENCE", "PROFITABILITY_EVIDENCE", "LIVE_MICRO_REVIEW_EVIDENCE",
    "RISK_AND_TERMINAL_SAFETY", "SENSITIVE_DATA_BOUNDARY", "PROTECTED_RUNTIME",
    "EXCEPTION_PACKAGE", "FINAL_VALIDATION", "HUMAN_OWNER_APPROVAL",
    "PROTECTED_ATTEMPT_WINDOW",
)
OWNER_CRITERIA = {"OWNER_EXCEPTION_FIELDS_COMPLETE", "OWNER_APPROVAL_VERIFIED", "APPROVAL_WINDOW_CURRENT"}
EXTERNAL_CRITERIA = {"EXTERNAL_CREDENTIAL_BOUNDARY", "EXTERNAL_ACCOUNT_REFERENCE_BOUNDARY", "PROTECTED_RUNTIME_CONNECTOR"}
DISALLOWED_LIVE_SOURCES = {"paper_simulation", "fixture", "example", "synthetic", "mock"}
CANONICAL_PATHS = (
    "RISK_POLICY.md",
    "automation/forex_engine/forex_extended_evidence_campaign_v1.py",
    "automation/forex_engine/forex_profit_production_next_gate_v1.py",
    "automation/forex_engine/forex_proof_to_live_micro_gate_v1.py",
    "automation/forex_engine/forex_final_readiness_checker_v1.py",
    "automation/forex_engine/review_chain_end_to_end_candidate_journey.py",
    "automation/forex_engine/first_live_micro_trade_proof.py",
    "automation/forex_engine/oanda_demo_to_live_profit_readiness_truth_v1.py",
    "automation/forex_engine/live_preflight_evidence_bundle_v1.py",
    "src/forex_delivery/governed_readiness.py",
    "src/forex_delivery/live_arming_evidence_gap.py",
    "telemetry/forex/demo_proof_ledger.jsonl",
)


def _permissions() -> dict[str, bool]:
    return {key: False for key in (
        "live_execution_authorized", "order_submission_authorized", "broker_connection_authorized",
        "credential_access_authorized", "money_movement_authorized", "general_live_trading_ready",
    )}


def _protected_actions() -> dict[str, bool]:
    return {key: False for key in (
        "network_request", "broker_call", "credential_access", "account_id_access", "order_placement",
        "money_movement", "worker_dispatch", "scheduler_creation", "daemon_creation", "approval_creation",
    )}


def _as_of(value: str | None) -> str:
    if not value:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    text = value.strip()
    if len(text) == 10:
        date.fromisoformat(text)
        return text + "T00:00:00Z"
    return text


def _load_genuine_demo_evidence(root: Path, source: str | Path | None) -> dict[str, Any]:
    if source is None:
        return {}
    candidate = Path(source)
    path = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    if path != root and root not in path.parents:
        raise ValueError("genuine demo evidence path must remain inside repository")
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != GENUINE_DEMO_SCHEMA:
        raise ValueError("unsupported genuine demo evidence schema")
    forecast_input = value.get("forecast_input")
    if not isinstance(forecast_input, Mapping) or forecast_input.get("schema") != GENUINE_DEMO_SCHEMA:
        raise ValueError("invalid genuine demo forecast input")
    ids = forecast_input.get("criterion_ids")
    if not isinstance(ids, list) or len(ids) != len(set(ids)):
        raise ValueError("duplicate genuine demo criterion IDs")
    if set(ids) - GENUINE_DEMO_CRITERIA:
        raise ValueError("unsupported genuine demo criterion ID")
    criteria = forecast_input.get("criteria")
    if not isinstance(criteria, Mapping) or set(criteria) - GENUINE_DEMO_CRITERIA:
        raise ValueError("unsupported genuine demo criterion mapping")
    return {"criterion_ids": ids, "criteria": dict(criteria)}


def load_forex_live_readiness_evidence(repo_root: str | Path, explicit_evidence: Mapping[str, Any] | None = None, genuine_demo_evidence: str | Path | None = None) -> dict[str, Any]:
    """Inventory local sources and sanitized caller evidence; perform no external access."""
    root = Path(repo_root).resolve()
    sources = [{"path": path, "present": (root / path).is_file()} for path in CANONICAL_PATHS]
    previous_path = root / "Reports/forex_delivery/AIOS_FOREX_LIVE_READINESS_FORECAST_V1_STATE.json"
    previous = None
    if previous_path.is_file():
        try:
            candidate = json.loads(previous_path.read_text(encoding="utf-8"))
            previous = candidate if candidate.get("schema") == SCHEMA else None
        except (OSError, UnicodeError, json.JSONDecodeError):
            previous = None
    sanitized = dict(explicit_evidence or {})
    direct = _load_genuine_demo_evidence(root, genuine_demo_evidence)
    if direct:
        existing = sanitized.get("criteria") if isinstance(sanitized.get("criteria"), Mapping) else {}
        sanitized["criteria"] = {**existing, **direct["criteria"]}
        sanitized["criterion_ids"] = direct["criterion_ids"]
    return {
        "schema": "AIOS_FOREX_LIVE_READINESS_EVIDENCE.v1",
        "repo_root": root.as_posix(),
        "sources": sources,
        "sanitized_evidence": sanitized,
        "previous_state": previous,
        "network_accessed": False,
        "broker_accessed": False,
        "credentials_accessed": False,
    }


def _criterion(spec: tuple[str, str, str], evidence: Mapping[str, Any]) -> dict[str, Any]:
    criterion_id, category, stage = spec
    supplied = evidence.get(criterion_id)
    supplied = supplied if isinstance(supplied, Mapping) else {}
    status = str(supplied.get("status") or "NOT_VERIFIED").upper()
    if status not in STATUSES:
        status = "CONFLICT"
    source_type = str(supplied.get("source_type") or "unavailable").lower()
    if status == "PASS" and source_type in DISALLOWED_LIVE_SOURCES:
        status = "NOT_VERIFIED"
    if criterion_id in OWNER_CRITERIA and status == "PASS" and supplied.get("explicit_current_owner_approval") is not True:
        status = "WAITING_OWNER"
    if criterion_id in EXTERNAL_CRITERIA and status == "PASS" and supplied.get("external_runtime_evidence") is not True:
        status = "WAITING_EXTERNAL"
    source_path = supplied.get("source_path")
    if source_path and (Path(str(source_path)).is_absolute() or ".." in Path(str(source_path)).parts):
        status, source_path = "CONFLICT", None
    return {
        "criterion_id": criterion_id, "category": category, "stage": stage,
        "description": str(supplied.get("description") or criterion_id.replace("_", " ").title()),
        "source_type": source_type, "source_path": source_path,
        "source_schema": supplied.get("source_schema"), "status": status,
        "blocker": supplied.get("blocker") or (None if status == "PASS" else f"{criterion_id} is {status}"),
        "closure_condition": supplied.get("closure_condition") or f"Supply current sanitized PASS evidence for {criterion_id}.",
        "executable_now": bool(supplied.get("executable_now")) and status not in {"BLOCKED", "CONFLICT", "STALE", "WAITING_OWNER", "WAITING_EXTERNAL"},
        "external_dependency": criterion_id in EXTERNAL_CRITERIA or status == "WAITING_EXTERNAL",
        "owner_action_required": criterion_id in OWNER_CRITERIA or status == "WAITING_OWNER",
        "evidence_freshness": supplied.get("evidence_freshness") or "NOT_VERIFIED",
        "counted_for_progress": status == "PASS",
    }


def _hours(evidence: Mapping[str, Any]) -> tuple[float | None, str]:
    remaining = evidence.get("remaining_work_packets")
    if isinstance(remaining, list) and remaining and all(isinstance(item, Mapping) and isinstance(item.get("estimated_hours"), (int, float)) and item["estimated_hours"] >= 0 for item in remaining):
        return round(sum(float(item["estimated_hours"]) for item in remaining), 2), "VERIFIED_PACKET_METADATA"
    completed = evidence.get("comparable_completed_packets")
    units = evidence.get("remaining_comparable_work_units")
    if isinstance(completed, list) and len(completed) >= 3 and isinstance(units, int) and units >= 0:
        durations: list[float] = []
        for item in completed:
            if not isinstance(item, Mapping):
                return None, "NOT_VERIFIED"
            try:
                start = datetime.fromisoformat(str(item["started_at_utc"]).replace("Z", "+00:00"))
                end = datetime.fromisoformat(str(item["completed_at_utc"]).replace("Z", "+00:00"))
            except (KeyError, TypeError, ValueError):
                return None, "NOT_VERIFIED"
            hours = (end - start).total_seconds() / 3600
            if hours < 0:
                return None, "NOT_VERIFIED"
            durations.append(hours)
        return round(sum(durations) / len(durations) * units, 2), "COMPARABLE_DURATION_EVIDENCE"
    return None, "NOT_VERIFIED"


def _daily_delta(previous: Mapping[str, Any] | None, current: Sequence[Mapping[str, Any]], as_of_utc: str, percent: float, current_stage: str | None) -> dict[str, Any]:
    if not previous:
        return {"daily_delta_status": "BASELINE_CREATED", "previous_as_of_utc": None, "current_as_of_utc": as_of_utc, "criteria_closed_today": [], "criteria_reopened_today": [], "new_blockers_today": [], "cleared_blockers_today": [], "readiness_percent_change": None, "critical_path_change": None, "forecast_change": None}
    old = {item["criterion_id"]: item for item in previous.get("criteria", []) if isinstance(item, Mapping) and item.get("criterion_id")}
    new = {item["criterion_id"]: item for item in current}
    closed = sorted(key for key in new if new[key]["status"] == "PASS" and old.get(key, {}).get("status") != "PASS")
    reopened = sorted(key for key in new if old.get(key, {}).get("status") == "PASS" and new[key]["status"] != "PASS")
    new_blockers = sorted(key for key in new if new[key]["status"] in {"BLOCKED", "CONFLICT"} and old.get(key, {}).get("status") not in {"BLOCKED", "CONFLICT"})
    cleared = sorted(key for key in old if old[key].get("status") in {"BLOCKED", "CONFLICT"} and new.get(key, {}).get("status") not in {"BLOCKED", "CONFLICT"})
    old_percent = previous.get("live_readiness_evidence_percent")
    change = round(percent - float(old_percent), 2) if isinstance(old_percent, (int, float)) else None
    old_stage = (previous.get("critical_path") or {}).get("current_stage")
    return {"daily_delta_status": "COMPARED", "previous_as_of_utc": previous.get("as_of_utc"), "current_as_of_utc": as_of_utc, "criteria_closed_today": closed, "criteria_reopened_today": reopened, "new_blockers_today": new_blockers, "cleared_blockers_today": cleared, "readiness_percent_change": change, "critical_path_change": None if old_stage == current_stage else {"from": old_stage, "to": current_stage}, "forecast_change": None}


def build_forex_live_readiness_forecast(evidence_bundle: Mapping[str, Any], *, as_of_date: str | None = None) -> dict[str, Any]:
    sanitized = evidence_bundle.get("sanitized_evidence")
    sanitized = sanitized if isinstance(sanitized, Mapping) else {}
    criterion_evidence = sanitized.get("criteria")
    criterion_evidence = criterion_evidence if isinstance(criterion_evidence, Mapping) else {}
    supplied_ids = sanitized.get("criterion_ids")
    ids = list(supplied_ids) if isinstance(supplied_ids, list) else [item[0] for item in CRITERIA_SPEC]
    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    criteria = [_criterion(spec, criterion_evidence) for spec in CRITERIA_SPEC]
    conflicts = [item["criterion_id"] for item in criteria if item["status"] == "CONFLICT"]
    counts = {status.lower(): sum(item["status"] == status for item in criteria) for status in STATUSES}
    total = len(criteria)
    passed = counts["pass"]
    percent = round(passed / total * 100, 2) if total and not duplicates else 0.0
    percent = min(max(percent, 0.0), 100.0)
    remaining_percent = round(100.0 - percent, 2)
    categories: dict[str, dict[str, Any]] = {}
    for category in sorted({item["category"] for item in criteria}):
        selected = [item for item in criteria if item["category"] == category]
        category_passed = sum(item["status"] == "PASS" for item in selected)
        categories[category] = {"criteria_total": len(selected), "criteria_passed": category_passed, "percent": round(category_passed / len(selected) * 100, 2)}
    stage_state: dict[str, str] = {}
    for stage in STAGES[:-1]:
        values = [item for item in criteria if item["stage"] == stage]
        stage_state[stage] = "PASS" if values and all(item["status"] == "PASS" for item in values) else "BLOCKED"
    attempt_ready = all(item["status"] == "PASS" for item in criteria)
    stage_state["PROTECTED_ATTEMPT_WINDOW"] = "PASS" if attempt_ready else "BLOCKED"
    current_stage = next((stage for stage in STAGES if stage_state[stage] != "PASS"), None)
    current_criteria = [item for item in criteria if item["stage"] == current_stage and item["status"] != "PASS"]
    highest = current_criteria[0] if current_criteria else None
    completed_stages = [stage for stage in STAGES if stage_state[stage] == "PASS"]
    blocked_stages = [stage for stage in STAGES if stage_state[stage] != "PASS"]
    next_stage = STAGES[STAGES.index(current_stage) + 1] if current_stage and STAGES.index(current_stage) + 1 < len(STAGES) else None
    executable = [item["criterion_id"] for item in criteria if item["executable_now"]]
    waiting_owner = counts["waiting_owner"] > 0 or any(item["criterion_id"] in OWNER_CRITERIA and item["status"] != "PASS" for item in criteria)
    waiting_external = [item["criterion_id"] for item in criteria if item["external_dependency"] and item["status"] != "PASS"]
    live_status = "PROTECTED_ATTEMPT_WINDOW_ELIGIBLE" if attempt_ready else ("OWNER_APPROVAL_REQUIRED" if all(item["status"] == "PASS" for item in criteria if item["criterion_id"] not in OWNER_CRITERIA) else ("EVIDENCE_COLLECTION_REQUIRED" if any(item["status"] in {"NOT_VERIFIED", "STALE"} for item in criteria) else "NOT_READY"))
    hours, hours_status = _hours(sanitized)
    genuine_days = int(sanitized.get("genuine_market_demo_days", 0)) if isinstance(sanitized.get("genuine_market_demo_days", 0), int) else 0
    minimum_days = sanitized.get("canonical_minimum_demo_days")
    calendar_remaining = max(int(minimum_days) - genuine_days, 0) if isinstance(minimum_days, int) and minimum_days >= 0 else None
    as_of_utc = _as_of(as_of_date)
    review_date = (date.fromisoformat(as_of_utc[:10]) + timedelta(days=calendar_remaining)).isoformat() if calendar_remaining is not None else None
    approval_current = all(next(item for item in criteria if item["criterion_id"] == cid)["status"] == "PASS" for cid in OWNER_CRITERIA)
    protected_window = sanitized.get("protected_live_attempt_window") if attempt_ready and approval_current else None
    forecast = {"earliest_evidence_review_date": review_date, "minimum_evidence_calendar_days_remaining": calendar_remaining, "estimated_engineering_hours_remaining": hours, "engineering_hours_estimate_status": hours_status, "protected_live_attempt_window": protected_window, "protected_live_attempt_window_status": "VERIFIED" if protected_window else "NOT_VERIFIED", "actual_live_trade_date": None, "actual_live_trade_date_status": "NOT_AUTHORIZED", "owner_approval_wait_estimated": False, "external_wait_separate_from_engineering_time": True}
    critical_path = {"completed_stages": completed_stages, "current_stage": current_stage, "next_stage": next_stage, "blocked_stages": blocked_stages, "critical_path": list(STAGES), "parallel_safe_work": sorted(executable), "sequential_only_work": list(STAGES), "highest_blocker": highest["blocker"] if highest else None, "highest_blocker_source": highest["source_path"] if highest else None, "highest_blocker_closure_condition": highest["closure_condition"] if highest else None, "next_verified_task": executable[0] if executable else (highest["criterion_id"] if highest else None)}
    summary = {"criteria_total": total, "criteria_passed": passed, "criteria_remaining": total - passed, "criteria_blocked": counts["blocked"], "criteria_not_verified": counts["not_verified"], "criteria_stale": counts["stale"], "criteria_waiting_owner": counts["waiting_owner"], "criteria_waiting_external": counts["waiting_external"]}
    daily = _daily_delta(evidence_bundle.get("previous_state") if isinstance(evidence_bundle.get("previous_state"), Mapping) else None, criteria, as_of_utc, percent, current_stage)
    return {"schema": SCHEMA, "mode": MODE, "as_of_utc": as_of_utc, "milestone_scope": MILESTONE, "live_status": "NOT_READY" if duplicates or conflicts else live_status, "live_readiness_evidence_percent": percent, "remaining_to_first_trade_percent": remaining_percent, "criteria_summary": summary, "category_scores": categories, "criteria": criteria, "duplicate_criterion_ids": duplicates, "critical_path": critical_path, "highest_blocker": critical_path["highest_blocker"], "next_verified_task": critical_path["next_verified_task"], "forecast": forecast, "daily_delta": daily, "source_inventory": evidence_bundle.get("sources", []), "source_conflicts": conflicts, "evidence_limitations": ["Local procedure or implementation presence does not prove live runtime readiness.", "PAPER_SIMULATION, fixtures, examples, synthetic data, and mocks receive no live-readiness credit."], "owner_action_required": waiting_owner, "external_dependencies": sorted(waiting_external), "permissions": _permissions(), "protected_actions": _protected_actions()}


def render_forex_live_readiness_report(state: Mapping[str, Any]) -> str:
    summary = state["criteria_summary"]
    critical = state["critical_path"]
    forecast = state["forecast"]
    criteria = state["criteria"]
    remaining = [item for item in criteria if item["status"] != "PASS"]
    passed = [item for item in criteria if item["status"] == "PASS"]
    marker = {"PASS": "✅", "BLOCKED": "❌", "STALE": "⚠️", "CONFLICT": "⚠️", "WAITING_OWNER": "🔐", "WAITING_EXTERNAL": "🌐", "NOT_VERIFIED": "⏳"}
    def lines(items: Sequence[Mapping[str, Any]]) -> str:
        return "\n".join(f"- {marker[item['status']]} `{item['criterion_id']}` — {item['status']}: {item['closure_condition']}" for item in items) or "- None."
    return f"""# 🚦 AIOS FOREX — WHEN CAN WE GO LIVE?

## 👤 OWNER VIEW
- 🎯 Target: first evidence-backed governed live Forex micro-trade review
- 📉 Remaining-to-First-Trade: {state['remaining_to_first_trade_percent']}%
- 📈 Live-Readiness evidence: {state['live_readiness_evidence_percent']}%
- 🧩 Criteria passed: {summary['criteria_passed']}
- 🧱 Criteria remaining: {summary['criteria_remaining']}
- ⛔ Highest blocker: {state['highest_blocker'] or 'None verified.'}
- ▶️ Next verified task: `{state['next_verified_task'] or 'NOT_VERIFIED'}`
- 🔐 Owner approval status: {'REQUIRED' if state['owner_action_required'] else 'NOT_CURRENTLY_REQUIRED'}
- 🌐 External dependencies: {state['external_dependencies']}
- ⚠️ Confidence: evidence-backed repository state only
- 🛑 live_execution_authorized false

## 🔴 CURRENT ANSWER
`{state['live_status']}`. General live trading remains out of scope and unauthorized.

## 📉 WHAT REMAINS
{summary['criteria_remaining']} of {summary['criteria_total']} unique criteria remain.

{lines(remaining)}

## 📊 LIVE-READINESS EVIDENCE
- Evidence-backed readiness: {state['live_readiness_evidence_percent']}%
- Passed: {summary['criteria_passed']}
- Remaining: {summary['criteria_remaining']}

## ⏳ EARLIEST DEFENSIBLE WINDOW
- Earliest evidence-review date: {forecast['earliest_evidence_review_date'] or 'NOT_VERIFIED'}
- Evidence days remaining: {forecast['minimum_evidence_calendar_days_remaining'] if forecast['minimum_evidence_calendar_days_remaining'] is not None else 'NOT_VERIFIED'}
- Engineering hours remaining: {forecast['estimated_engineering_hours_remaining'] if forecast['estimated_engineering_hours_remaining'] is not None else 'NOT_VERIFIED'}
- Protected attempt window: {forecast['protected_live_attempt_window'] or 'NOT_VERIFIED'}
- Actual live trade date: NOT_AUTHORIZED

## ⛔ HIGHEST BLOCKER
{state['highest_blocker'] or 'None verified.'}

## ▶️ NEXT VERIFIED TASK
`{state['next_verified_task'] or 'NOT_VERIFIED'}`

## 🧱 CRITICAL PATH
- Current stage: `{critical['current_stage'] or 'COMPLETE'}`
- Next stage: `{critical['next_stage'] or 'NONE'}`
- Ordered stages: {' -> '.join(critical['critical_path'])}

## 🟢 EXECUTABLE NOW
{chr(10).join('- ' + item for item in critical['parallel_safe_work']) or '- None verified.'}

## 🟡 WAITING ON EVIDENCE
{lines([item for item in remaining if item['status'] in {'NOT_VERIFIED', 'STALE', 'CONFLICT', 'BLOCKED'}])}

## 🔐 WAITING ON HUMAN OWNER
{lines([item for item in remaining if item['owner_action_required']])}

## 🌐 WAITING ON EXTERNAL RUNTIME
{lines([item for item in remaining if item['external_dependency']])}

## 🧪 VALIDATION STILL REQUIRED
{lines([item for item in remaining if item['category'] == 'final_validation'])}

## 📅 CHANGE SINCE LAST REPORT
- Status: `{state['daily_delta']['daily_delta_status']}`
- Criteria closed: {state['daily_delta']['criteria_closed_today']}
- Criteria reopened: {state['daily_delta']['criteria_reopened_today']}

## ⚠️ CONFIDENCE AND LIMITATIONS
{chr(10).join('- ' + item for item in state['evidence_limitations'])}

## ✅ MATERIAL WORK CLOSED TODAY
{lines([item for item in passed if item['criterion_id'] in state['daily_delta']['criteria_closed_today']])}

## 🛑 NO-LIVE-AUTHORITY CONFIRMATION
- Live execution authorized: false
- Order submission authorized: false
- Broker connection authorized: false
- Credential access authorized: false
- Money movement authorized: false
- General live trading ready: false
"""


def stable_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--as-of-date")
    parser.add_argument("--state-output")
    parser.add_argument("--report-output")
    parser.add_argument("--evidence", default="{}", help="Sanitized JSON evidence")
    parser.add_argument("--genuine-demo-evidence")
    args = parser.parse_args(argv)
    bundle = load_forex_live_readiness_evidence(args.repo_root, json.loads(args.evidence), args.genuine_demo_evidence)
    state = build_forex_live_readiness_forecast(bundle, as_of_date=args.as_of_date)
    rendered = stable_json(state)
    if args.state_output:
        Path(args.state_output).write_text(rendered, encoding="utf-8")
    if args.report_output:
        Path(args.report_output).write_text(render_forex_live_readiness_report(state), encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
