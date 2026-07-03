from __future__ import annotations

from datetime import date
from pathlib import Path

from automation.forex_engine.daily_forex_orchestrator_artifact_v1 import (
    SAFETY_STATEMENT,
    build_artifact_summary,
)


def test_daily_forex_orchestrator_artifact_reports_rolling_continuity() -> None:
    payload = build_artifact_summary(Path("."), today=date(2026, 7, 3))

    assert payload["ledger_path"] == "telemetry/forex/demo_proof_ledger.jsonl"
    assert payload["today_utc"] == "2026-07-03"
    assert payload["real_demo_day_dates"] == ["2026-07-02", "2026-07-03"]
    assert payload["real_demo_day_count"] == 2
    assert payload["consecutive_real_demo_day_count"] == 2
    assert payload["missing_dates"] == []
    assert payload["next_required_evidence_date"] == "2026-07-04"
    assert payload["five_day_window_status"] == "IN_PROGRESS"
    assert payload["thirty_day_window_status"] == "IN_PROGRESS"
    assert payload["rolling_continuity_status"] == "ROLLING_CONTINUITY_IN_PROGRESS"


def test_daily_forex_orchestrator_artifact_reports_maintenance_plan() -> None:
    payload = build_artifact_summary(Path("."), today=date(2026, 7, 3))
    maintenance = payload["maintenance"]

    assert maintenance["status"] == "MAINTENANCE_WORKLOAD_PLAN_READY"
    assert maintenance["ready"] is True
    assert maintenance["maintenance_plan_enabled"] is True
    assert maintenance["current_maintenance_lane"] == "clean_maintenance_plan"
    assert maintenance["maintenance_window_recommended"] is True
    assert maintenance["next_best_packet"] == "AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1"
    assert maintenance["blockers"] == []


def test_daily_forex_orchestrator_artifact_declares_safety_boundaries() -> None:
    payload = build_artifact_summary(Path("."), today=date(2026, 7, 3))

    assert payload["safety_statement"] == SAFETY_STATEMENT
    assert "No broker calls" in payload["safety_statement"]
    assert "no live orders" in payload["safety_statement"]
    assert "no credentials" in payload["safety_statement"]
    assert "no .env reads" in payload["safety_statement"]
    assert "no money movement" in payload["safety_statement"]
    assert "no automatic cleanup" in payload["safety_statement"]
    assert "no automatic evidence append" in payload["safety_statement"]
    assert "no automatic merge" in payload["safety_statement"]
    assert "no profitability claim" in payload["safety_statement"]
