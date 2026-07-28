from __future__ import annotations

from datetime import date
import json
from pathlib import Path

from automation.forex_engine.daily_forex_continuation_router_v1 import (
    FALSE_AUTHORITY_FLAGS,
    route_daily_forex_continuation,
    write_outputs,
)


def _repo(tmp_path: Path, rows: list[dict] | None = None) -> Path:
    repo = tmp_path / "repo"
    ledger_dir = repo / "telemetry" / "forex"
    reports_dir = repo / "Reports" / "forex_delivery"
    ledger_dir.mkdir(parents=True)
    reports_dir.mkdir(parents=True)
    (reports_dir / "AIOS_DAILY_FOREX_ORCHESTRATOR_V1_REPORT.md").write_text("# report\n", encoding="utf-8")
    if rows is not None:
        (ledger_dir / "demo_proof_ledger.jsonl").write_text(
            "\n".join(json.dumps(row) for row in rows) + "\n",
            encoding="utf-8",
        )
    return repo


def _real_day(day: str) -> dict:
    return {"schema": "aios.forex.demo_proof_ledger.v1", "record_type": "REAL_DEMO_DAY", "date": day}


def _artifact(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "artifact.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_missing_today_evidence_routes_to_owner_evidence_append(tmp_path: Path) -> None:
    result = route_daily_forex_continuation(_repo(tmp_path, [_real_day("2026-07-03")]), today=date(2026, 7, 4))
    assert result["decision"]["next_packet_id"] == "AIOS_FOREX_OWNER_EVIDENCE_APPEND_NEXT_VALID_DAY_V1"
    assert result["decision"]["owner_action_required"] is True


def test_duplicate_evidence_routes_to_duplicate_review(tmp_path: Path) -> None:
    artifact = _artifact(tmp_path, {"evidence_status": "DUPLICATE_EVIDENCE_BLOCKED"})
    result = route_daily_forex_continuation(_repo(tmp_path, [_real_day("2026-07-04")]), artifact_json=artifact, today=date(2026, 7, 4))
    assert result["decision"]["next_packet_id"] == "AIOS_FOREX_DUPLICATE_DEMO_DAY_REVIEW_V1"


def test_missing_ledger_routes_to_ledger_integrity_review(tmp_path: Path) -> None:
    result = route_daily_forex_continuation(_repo(tmp_path, None), today=date(2026, 7, 4))
    assert result["state"]["evidence_status"] == "LEDGER_MISSING"
    assert result["decision"]["next_packet_id"] == "AIOS_FOREX_LEDGER_INTEGRITY_REVIEW_V1"


def test_blocked_continuity_routes_to_continuity_blocker_review(tmp_path: Path) -> None:
    artifact = _artifact(tmp_path, {"evidence_status": "TODAY_EVIDENCE_PRESENT", "rolling_continuity": {"rolling_continuity_status": "ROLLING_CONTINUITY_BLOCKED"}})
    result = route_daily_forex_continuation(_repo(tmp_path, [_real_day("2026-07-04")]), artifact_json=artifact, today=date(2026, 7, 4))
    assert result["decision"]["next_packet_id"] == "AIOS_FOREX_ROLLING_CONTINUITY_BLOCKER_REVIEW_V1"


def test_maintenance_recommendation_is_included_but_not_executed(tmp_path: Path) -> None:
    artifact = _artifact(tmp_path, {"evidence_status": "TODAY_EVIDENCE_PRESENT", "maintenance_planner": {"status": "MAINTENANCE_WORKLOAD_PLAN_READY", "next_best_packet": "AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1", "blockers": []}})
    result = route_daily_forex_continuation(_repo(tmp_path, [_real_day("2026-07-04")]), artifact_json=artifact, today=date(2026, 7, 4))
    assert result["state"]["maintenance_next_best_packet"] == "AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1"
    assert result["decision"]["next_packet_id"] == "AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1"
    assert result["execution_allowed"] is False


def test_today_evidence_present_routes_to_next_safe_build_packet(tmp_path: Path) -> None:
    result = route_daily_forex_continuation(_repo(tmp_path, [_real_day("2026-07-03"), _real_day("2026-07-04")]), today=date(2026, 7, 4))
    assert result["state"]["evidence_status"] == "TODAY_EVIDENCE_PRESENT"
    assert result["decision"]["next_packet_id"] == "AIOS_FOREX_NEXT_SAFE_BUILD_PACKET_SELECTION_V1"


def test_malformed_explicit_artifact_blocks_safely(tmp_path: Path) -> None:
    artifact = tmp_path / "bad.json"
    artifact.write_text("{not-json", encoding="utf-8")
    result = route_daily_forex_continuation(_repo(tmp_path, [_real_day("2026-07-04")]), artifact_json=artifact, today=date(2026, 7, 4))
    assert result["status"] == "BLOCKED"
    assert result["decision"]["next_packet_id"] == "AIOS_FOREX_MANUAL_REVIEW_REQUIRED_V1"
    assert "malformed_explicit_artifact" in result["state"]["blockers"]


def test_all_authority_flags_remain_false(tmp_path: Path) -> None:
    result = route_daily_forex_continuation(_repo(tmp_path, [_real_day("2026-07-04")]), today=date(2026, 7, 4))
    for flag in FALSE_AUTHORITY_FLAGS:
        assert result[flag] is False


def test_output_ticket_schema_is_stable(tmp_path: Path) -> None:
    result = route_daily_forex_continuation(_repo(tmp_path, [_real_day("2026-07-04")]), today=date(2026, 7, 4))
    paths = write_outputs(result, tmp_path / "out")
    ticket = json.loads(paths["ticket_json"].read_text(encoding="utf-8"))
    assert ticket["schema"] == "aios.daily_forex_next_packet_ticket.v1"
    assert set(ticket) == {"schema", "authority", "decision", "state"}


def test_no_broker_secrets_env_live_fields_can_become_true(tmp_path: Path) -> None:
    artifact = _artifact(tmp_path, {"broker_calls_allowed": True, "credential_access_allowed": True, "env_file_reads_allowed": True, "execution_allowed": True})
    result = route_daily_forex_continuation(_repo(tmp_path, [_real_day("2026-07-04")]), artifact_json=artifact, today=date(2026, 7, 4))
    for field in ["broker_calls_allowed", "credential_access_allowed", "env_file_reads_allowed", "execution_allowed", "money_movement_allowed"]:
        assert result[field] is False
