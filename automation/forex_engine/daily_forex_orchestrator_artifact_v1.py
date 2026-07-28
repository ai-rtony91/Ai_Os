"""Report-only helpers for the daily Forex orchestrator artifact."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
import json
from pathlib import Path
from typing import Any

from automation.forex_engine.forex_runtime_maintenance_workload_execution_plan_v1 import (
    evaluate_forex_runtime_maintenance_workload_execution_plan_v1,
)
from scripts.forex_delivery.run_forex_runtime_maintenance_workload_execution_plan_v1 import (
    _payload as maintenance_payload,
)

SAFETY_STATEMENT = (
    "Report-only continuity artifact: no broker calls, no live orders, no credentials, "
    "no .env reads, no money movement, no automatic evidence append, no automatic merge, "
    "and no production/trading/live-broker/profitability readiness claim."
)


def real_demo_day_dates(ledger_path: Path) -> list[str]:
    if not ledger_path.exists():
        return []

    dates: set[str] = set()
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("record_type") == "REAL_DEMO_DAY" and row.get("date"):
            dates.add(str(row["date"]))
    return sorted(dates)


def rolling_continuity_status(ledger_path: Path, *, today: date | None = None) -> dict[str, Any]:
    today = today or datetime.now(UTC).date()
    dates = real_demo_day_dates(ledger_path)
    date_set = set(dates)

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

    next_required = (date.fromisoformat(dates[-1]) + timedelta(days=1)).isoformat() if dates else today.isoformat()
    rolling_status = (
        "NO_REAL_DEMO_DAY_RECORDS"
        if not dates
        else "GAP_DETECTED"
        if missing_dates
        else "ROLLING_CONTINUITY_IN_PROGRESS"
    )

    return {
        "real_demo_day_dates": dates,
        "real_demo_day_count": len(dates),
        "consecutive_real_demo_day_count": consecutive,
        "missing_dates": missing_dates,
        "next_required_evidence_date": next_required,
        "five_day_window_status": "PASS" if consecutive >= 5 else "IN_PROGRESS",
        "thirty_day_window_status": "PASS" if consecutive >= 30 else "IN_PROGRESS",
        "rolling_continuity_status": rolling_status,
    }


def maintenance_planner_snapshot() -> dict[str, Any]:
    result = evaluate_forex_runtime_maintenance_workload_execution_plan_v1(
        maintenance_payload()
    )
    return {
        "status": result["status"],
        "next_best_packet": result["next_best_packet"],
        "blockers": result["blockers"],
    }


def artifact_summary(repo_root: Path, *, today: date | None = None) -> dict[str, Any]:
    return {
        "rolling_continuity": rolling_continuity_status(
            repo_root / "telemetry" / "forex" / "demo_proof_ledger.jsonl",
            today=today,
        ),
        "maintenance_planner": maintenance_planner_snapshot(),
        "explicit_safety_statement": SAFETY_STATEMENT,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build daily Forex orchestrator report-only artifact summary.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--today", default="")
    args = parser.parse_args()

    today = date.fromisoformat(args.today) if args.today else None
    print(json.dumps(artifact_summary(Path(args.repo_root), today=today), sort_keys=True))


if __name__ == "__main__":
    main()
