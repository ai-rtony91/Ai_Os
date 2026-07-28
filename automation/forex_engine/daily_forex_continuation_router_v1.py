"""Read-only Layer 2 router for the daily Forex orchestrator artifact."""

from __future__ import annotations

import argparse
from datetime import UTC, date, datetime, timedelta
import json
from pathlib import Path
from typing import Any

SCHEMA = "aios.daily_forex_continuation_router.v1"
AUTHORITY = "READ_ONLY_REPORTING"
REPORT_NAME = "AIOS_DAILY_FOREX_CONTINUATION_ROUTER_V1_REPORT.md"
TICKET_NAME = "AIOS_DAILY_FOREX_NEXT_PACKET_TICKET_V1.json"
DEFAULT_REPORT_PATH = Path("Reports/forex_delivery/AIOS_DAILY_FOREX_ORCHESTRATOR_V1_REPORT.md")
DEFAULT_LEDGER_PATH = Path("telemetry/forex/demo_proof_ledger.jsonl")

FALSE_AUTHORITY_FLAGS = {
    "execution_allowed": False,
    "broker_calls_allowed": False,
    "credential_access_allowed": False,
    "env_file_reads_allowed": False,
    "money_movement_allowed": False,
    "automatic_evidence_append_allowed": False,
    "automatic_commit_allowed": False,
    "automatic_pr_allowed": False,
    "automatic_merge_allowed": False,
}

PACKET_TITLES = {
    "AIOS_FOREX_OWNER_EVIDENCE_APPEND_NEXT_VALID_DAY_V1": "Owner Evidence Append For Next Valid Day",
    "AIOS_FOREX_DUPLICATE_DEMO_DAY_REVIEW_V1": "Duplicate Demo Day Review",
    "AIOS_FOREX_LEDGER_INTEGRITY_REVIEW_V1": "Ledger Integrity Review",
    "AIOS_FOREX_ROLLING_CONTINUITY_BLOCKER_REVIEW_V1": "Rolling Continuity Blocker Review",
    "AIOS_FOREX_NEXT_SAFE_BUILD_PACKET_SELECTION_V1": "Next Safe Build Packet Selection",
    "AIOS_FOREX_MANUAL_REVIEW_REQUIRED_V1": "Manual Review Required",
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _real_demo_day_dates(ledger_path: Path) -> list[str]:
    dates: set[str] = set()
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("record_type") == "REAL_DEMO_DAY" and row.get("date"):
            dates.add(str(row["date"]))
    return sorted(dates)


def _ledger_state(repo_root: Path, today: date) -> dict[str, Any]:
    ledger_path = repo_root / DEFAULT_LEDGER_PATH
    if not ledger_path.exists():
        return {
            "evidence_status": "LEDGER_MISSING",
            "real_demo_day_count": 0,
            "consecutive_real_demo_day_count": 0,
            "missing_dates": [],
            "next_required_evidence_date": today.isoformat(),
            "five_day_window_status": "IN_PROGRESS",
            "thirty_day_window_status": "IN_PROGRESS",
            "rolling_continuity_status": "NO_REAL_DEMO_DAY_RECORDS",
            "maintenance_status": "UNKNOWN",
            "maintenance_next_best_packet": "",
            "blockers": ["ledger_missing"],
        }

    dates = _real_demo_day_dates(ledger_path)
    date_set = set(dates)
    today_key = today.isoformat()
    today_count = dates.count(today_key)
    if today_count == 0:
        evidence_status = "MISSING_TODAY_EVIDENCE"
    elif today_count == 1:
        evidence_status = "TODAY_EVIDENCE_PRESENT"
    else:
        evidence_status = "DUPLICATE_EVIDENCE_BLOCKED"

    consecutive = 0
    cursor = today
    while cursor.isoformat() in date_set:
        consecutive += 1
        cursor -= timedelta(days=1)

    missing_dates: list[str] = []
    if dates:
        cursor = date.fromisoformat(dates[0])
        end = date.fromisoformat(dates[-1])
        while cursor <= end:
            key = cursor.isoformat()
            if key not in date_set:
                missing_dates.append(key)
            cursor += timedelta(days=1)

    rolling_status = "ROLLING_CONTINUITY_IN_PROGRESS" if dates and not missing_dates else "GAP_DETECTED" if missing_dates else "NO_REAL_DEMO_DAY_RECORDS"
    next_required = (date.fromisoformat(dates[-1]) + timedelta(days=1)).isoformat() if dates else today_key
    blockers = [] if evidence_status == "TODAY_EVIDENCE_PRESENT" and not missing_dates else [evidence_status.lower()]

    return {
        "evidence_status": evidence_status,
        "real_demo_day_count": len(dates),
        "consecutive_real_demo_day_count": consecutive,
        "missing_dates": missing_dates,
        "next_required_evidence_date": next_required,
        "five_day_window_status": "PASS" if consecutive >= 5 else "IN_PROGRESS",
        "thirty_day_window_status": "PASS" if consecutive >= 30 else "IN_PROGRESS",
        "rolling_continuity_status": rolling_status,
        "maintenance_status": "UNKNOWN",
        "maintenance_next_best_packet": "",
        "blockers": blockers,
    }


def _state_from_artifact(artifact: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    rolling = artifact.get("rolling_continuity") if isinstance(artifact.get("rolling_continuity"), dict) else {}
    maintenance = artifact.get("maintenance_planner") if isinstance(artifact.get("maintenance_planner"), dict) else {}
    merged = dict(fallback)
    merged.update(
        {
            "evidence_status": artifact.get("evidence_status", fallback["evidence_status"]),
            "real_demo_day_count": rolling.get("real_demo_day_count", fallback["real_demo_day_count"]),
            "consecutive_real_demo_day_count": rolling.get("consecutive_real_demo_day_count", fallback["consecutive_real_demo_day_count"]),
            "missing_dates": rolling.get("missing_dates", fallback["missing_dates"]),
            "next_required_evidence_date": rolling.get("next_required_evidence_date", fallback["next_required_evidence_date"]),
            "five_day_window_status": rolling.get("five_day_window_status", fallback["five_day_window_status"]),
            "thirty_day_window_status": rolling.get("thirty_day_window_status", fallback["thirty_day_window_status"]),
            "rolling_continuity_status": rolling.get("rolling_continuity_status", fallback["rolling_continuity_status"]),
            "maintenance_status": maintenance.get("status", fallback["maintenance_status"]),
            "maintenance_next_best_packet": maintenance.get("next_best_packet", fallback["maintenance_next_best_packet"]),
            "blockers": maintenance.get("blockers", fallback["blockers"]),
        }
    )
    return merged


def _decision(state: dict[str, Any]) -> dict[str, Any]:
    evidence_status = state["evidence_status"]
    continuity = state["rolling_continuity_status"]
    maintenance_packet = state.get("maintenance_next_best_packet") or ""

    if evidence_status == "MISSING_TODAY_EVIDENCE":
        return _packet("AIOS_FOREX_OWNER_EVIDENCE_APPEND_NEXT_VALID_DAY_V1", True, "Today UTC evidence is missing.", "Stop. Owner must append valid evidence manually.")
    if evidence_status == "DUPLICATE_EVIDENCE_BLOCKED":
        return _packet("AIOS_FOREX_DUPLICATE_DEMO_DAY_REVIEW_V1", True, "Duplicate evidence detected.", "Stop. Review ledger before further action.")
    if evidence_status == "LEDGER_MISSING":
        return _packet("AIOS_FOREX_LEDGER_INTEGRITY_REVIEW_V1", True, "Demo proof ledger missing.", "Stop. Restore or initialize ledger under governance.")
    if continuity == "ROLLING_CONTINUITY_BLOCKED":
        return _packet("AIOS_FOREX_ROLLING_CONTINUITY_BLOCKER_REVIEW_V1", True, "Rolling continuity is blocked.", "Stop. Resolve continuity blocker first.")
    if maintenance_packet:
        return _packet(maintenance_packet, False, "Maintenance planner recommended next packet.", "Report only. Do not execute.")
    if evidence_status == "TODAY_EVIDENCE_PRESENT" and continuity == "ROLLING_CONTINUITY_IN_PROGRESS":
        return _packet("AIOS_FOREX_NEXT_SAFE_BUILD_PACKET_SELECTION_V1", False, "Evidence is present and continuity is clean.", "Report only. Codex packet must be separately approved.")
    return _packet("AIOS_FOREX_MANUAL_REVIEW_REQUIRED_V1", True, "Router could not safely classify state.", "Stop. Manual review required.")


def _packet(packet_id: str, owner_required: bool, reason: str, stop_rule: str) -> dict[str, Any]:
    return {
        "next_packet_id": packet_id,
        "next_packet_title": PACKET_TITLES.get(packet_id, packet_id.replace("_", " ").title()),
        "next_packet_authority": AUTHORITY,
        "owner_action_required": owner_required,
        "reason": reason,
        "stop_rule": stop_rule,
    }


def route_daily_forex_continuation(repo_root: Path, *, artifact_json: Path | None = None, today: date | None = None) -> dict[str, Any]:
    today = today or datetime.now(UTC).date()
    consumed = [str(DEFAULT_LEDGER_PATH), str(DEFAULT_REPORT_PATH)]
    fallback = _ledger_state(repo_root, today)
    state = fallback
    status = "PASS"

    if artifact_json and artifact_json.exists():
        consumed.append(str(artifact_json))
        try:
            artifact = _read_json(artifact_json)
            if not isinstance(artifact, dict):
                raise ValueError("artifact root must be an object")
            state = _state_from_artifact(artifact, fallback)
        except Exception as exc:  # fail closed for explicit malformed artifact input
            status = "BLOCKED"
            state = dict(fallback)
            state["blockers"] = ["malformed_explicit_artifact", str(exc)]
    decision = _decision(state)
    if status == "BLOCKED":
        decision = _packet("AIOS_FOREX_MANUAL_REVIEW_REQUIRED_V1", True, "Router could not safely classify state.", "Stop. Manual review required.")

    return {
        "schema": SCHEMA,
        "status": status,
        "authority": AUTHORITY,
        **FALSE_AUTHORITY_FLAGS,
        "state": state,
        "decision": decision,
        "consumed_inputs": consumed,
        "produced_outputs": [],
    }


def write_outputs(result: dict[str, Any], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_json = output_dir / "AIOS_DAILY_FOREX_CONTINUATION_ROUTER_V1.json"
    report_md = output_dir / REPORT_NAME
    ticket_json = output_dir / TICKET_NAME
    produced = [str(report_json), str(report_md), str(ticket_json)]
    result = {**result, "produced_outputs": produced}
    report_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ticket = {"schema": "aios.daily_forex_next_packet_ticket.v1", "authority": AUTHORITY, "decision": result["decision"], "state": result["state"]}
    ticket_json.write_text(json.dumps(ticket, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_md.write_text(_markdown(result), encoding="utf-8")
    return {"report_json": report_json, "report_md": report_md, "ticket_json": ticket_json}


def _markdown(result: dict[str, Any]) -> str:
    state = result["state"]
    decision = result["decision"]
    return "\n".join(
        [
            "# AIOS Daily Forex Continuation Router V1",
            "",
            "Layer 2 consumes Layer 1 daily Forex artifact/report state.",
            "It produces a next packet ticket.",
            "It is scheduled at 01:37 UTC.",
            "It is read-only/report-only.",
            "It does not execute packets.",
            "It does not append evidence.",
            "It does not trade.",
            "It does not touch broker/API/secrets.",
            "It does not mutate repo state.",
            "",
            "## Current State",
            f"- evidence_status: {state['evidence_status']}",
            f"- real_demo_day_count: {state['real_demo_day_count']}",
            f"- consecutive_real_demo_day_count: {state['consecutive_real_demo_day_count']}",
            f"- missing_dates: {state['missing_dates']}",
            f"- next_required_evidence_date: {state['next_required_evidence_date']}",
            f"- five_day_window_status: {state['five_day_window_status']}",
            f"- thirty_day_window_status: {state['thirty_day_window_status']}",
            f"- rolling_continuity_status: {state['rolling_continuity_status']}",
            f"- maintenance_status: {state['maintenance_status']}",
            f"- maintenance_next_best_packet: {state['maintenance_next_best_packet']}",
            f"- blockers: {state['blockers']}",
            "",
            "## Selected Next Packet",
            f"- next_packet_id: {decision['next_packet_id']}",
            f"- next_packet_title: {decision['next_packet_title']}",
            f"- reason: {decision['reason']}",
            f"- owner_action_required: {decision['owner_action_required']}",
            f"- stop_rule: {decision['stop_rule']}",
            "",
            "## Safety Boundaries",
            "No broker calls, no OANDA calls, no credentials, no .env reads, no live orders, no money movement, no evidence auto-append, no commits by automation, no PR auto-open, no auto-merge, no trading authority expansion, and no daemon/service/webhook.",
            "",
            "## Consumed Inputs",
            *[f"- {item}" for item in result["consumed_inputs"]],
            "",
            "## Produced Outputs",
            *[f"- {item}" for item in result["produced_outputs"]],
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Route the next safe daily Forex continuation packet.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--artifact-json", default="")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--today", default="")
    args = parser.parse_args(argv)

    today = date.fromisoformat(args.today) if args.today else None
    artifact_json = Path(args.artifact_json) if args.artifact_json else None
    result = route_daily_forex_continuation(Path(args.repo_root), artifact_json=artifact_json, today=today)
    if args.output_dir:
        paths = write_outputs(result, Path(args.output_dir))
        print(json.dumps({key: str(value) for key, value in paths.items()}, sort_keys=True))
    else:
        print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
