from datetime import date
from pathlib import Path

from automation.forex_engine.daily_forex_orchestrator_artifact_v1 import (
    SAFETY_STATEMENT,
    artifact_summary,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_artifact_summary_reports_rolling_continuity_and_maintenance() -> None:
    result = artifact_summary(REPO_ROOT, today=date(2026, 7, 3))

    rolling = result["rolling_continuity"]
    assert rolling["real_demo_day_dates"][-2:] == ["2026-07-02", "2026-07-03"]
    assert rolling["real_demo_day_count"] >= 2
    assert rolling["consecutive_real_demo_day_count"] == 2
    assert rolling["missing_dates"] == []
    assert rolling["next_required_evidence_date"] == "2026-07-04"
    assert rolling["five_day_window_status"] == "IN_PROGRESS"
    assert rolling["thirty_day_window_status"] == "IN_PROGRESS"
    assert rolling["rolling_continuity_status"] == "ROLLING_CONTINUITY_IN_PROGRESS"

    maintenance = result["maintenance_planner"]
    assert maintenance["status"] == "MAINTENANCE_WORKLOAD_PLAN_READY"
    assert maintenance["next_best_packet"] == "AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1"
    assert maintenance["blockers"] == []

    assert result["explicit_safety_statement"] == SAFETY_STATEMENT
    for forbidden_claim in [
        "production/trading/live-broker/profitability readiness claim",
        "no broker calls",
        "no .env reads",
        "no automatic merge",
    ]:
        assert forbidden_claim in result["explicit_safety_statement"]
