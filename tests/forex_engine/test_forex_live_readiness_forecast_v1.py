from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "automation/forex_engine/forex_live_readiness_forecast_v1.py"


def module():
    spec = importlib.util.spec_from_file_location("forecast", MODULE_PATH)
    value = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(value)
    return value


def build(evidence: dict | None = None, previous: dict | None = None, as_of: str = "2026-07-27"):
    m = module()
    bundle = {"sanitized_evidence": evidence or {}, "sources": [], "previous_state": previous}
    return m.build_forex_live_readiness_forecast(bundle, as_of_date=as_of)


def pass_evidence(m, *, owner=False, external=False):
    criteria = {}
    for criterion_id, _, _ in m.CRITERIA_SPEC:
        item = {"status": "PASS", "source_type": "sanitized_runtime_evidence", "source_path": "evidence/current.json"}
        if criterion_id in m.OWNER_CRITERIA:
            item["explicit_current_owner_approval"] = owner
        if criterion_id in m.EXTERNAL_CRITERIA:
            item["external_runtime_evidence"] = external
        criteria[criterion_id] = item
    return {"criteria": criteria}


def test_catalog_is_unique_and_missing_evidence_fails_closed() -> None:
    m = module()
    ids = [item[0] for item in m.CRITERIA_SPEC]
    assert len(ids) == len(set(ids)) == 40
    state = build()
    assert state["criteria_summary"]["criteria_not_verified"] > 0
    assert state["live_status"] == "EVIDENCE_COLLECTION_REQUIRED"
    assert state["live_readiness_evidence_percent"] == 0.0


def test_duplicate_criterion_ids_block_forecast() -> None:
    state = build({"criterion_ids": ["A", "A"]})
    assert state["duplicate_criterion_ids"] == ["A"]
    assert state["live_status"] == "NOT_READY"
    assert state["live_readiness_evidence_percent"] == 0.0


def test_only_pass_gets_credit_and_percentages_reconcile() -> None:
    m = module()
    evidence = {"criteria": {m.CRITERIA_SPEC[0][0]: {"status": "PASS", "source_type": "genuine_market_demo", "source_path": "telemetry/current.json"}}}
    state = build(evidence)
    summary = state["criteria_summary"]
    assert summary["criteria_passed"] == 1
    assert summary["criteria_passed"] + summary["criteria_remaining"] == summary["criteria_total"]
    assert 0 <= state["live_readiness_evidence_percent"] <= 100
    for score in state["category_scores"].values():
        assert score["criteria_passed"] <= score["criteria_total"]
        assert 0 <= score["percent"] <= 100


def test_demo_or_owner_review_does_not_authorize_live_execution() -> None:
    m = module()
    evidence = {"criteria": {key: {"status": "PASS", "source_type": "genuine_demo", "source_path": "evidence/demo.json"} for key, category, _ in m.CRITERIA_SPEC if category in {"demo_evidence", "profitability_evidence"}}}
    state = build(evidence)
    assert state["permissions"]["live_execution_authorized"] is False
    assert state["permissions"]["general_live_trading_ready"] is False
    assert state["live_status"] != "PROTECTED_ATTEMPT_WINDOW_ELIGIBLE"


def test_paper_fixture_and_synthetic_evidence_receive_no_credit() -> None:
    m = module()
    criterion_id = m.CRITERIA_SPEC[0][0]
    for source in ("paper_simulation", "fixture", "synthetic", "mock"):
        state = build({"criteria": {criterion_id: {"status": "PASS", "source_type": source}}})
        criterion = next(item for item in state["criteria"] if item["criterion_id"] == criterion_id)
        assert criterion["status"] == "NOT_VERIFIED"
        assert criterion["counted_for_progress"] is False


def test_conflict_fails_closed_and_blocked_work_is_not_executable() -> None:
    criterion_id = module().CRITERIA_SPEC[0][0]
    state = build({"criteria": {criterion_id: {"status": "CONFLICT", "executable_now": True}}})
    item = next(item for item in state["criteria"] if item["criterion_id"] == criterion_id)
    assert state["live_status"] == "NOT_READY"
    assert item["executable_now"] is False
    assert criterion_id in state["source_conflicts"]


def test_owner_approval_and_external_runtime_are_never_synthesized() -> None:
    m = module()
    evidence = pass_evidence(m)
    state = build(evidence)
    for item in state["criteria"]:
        if item["criterion_id"] in m.OWNER_CRITERIA:
            assert item["status"] == "WAITING_OWNER"
        if item["criterion_id"] in m.EXTERNAL_CRITERIA:
            assert item["status"] == "WAITING_EXTERNAL"
    assert state["forecast"]["actual_live_trade_date"] is None
    assert state["forecast"]["actual_live_trade_date_status"] == "NOT_AUTHORIZED"


def test_hours_are_null_without_evidence_and_comparable_records_are_deterministic() -> None:
    state = build()
    assert state["forecast"]["estimated_engineering_hours_remaining"] is None
    assert state["forecast"]["engineering_hours_estimate_status"] == "NOT_VERIFIED"
    comparable = [
        {"started_at_utc": "2026-07-01T00:00:00Z", "completed_at_utc": "2026-07-01T02:00:00Z"},
        {"started_at_utc": "2026-07-02T00:00:00Z", "completed_at_utc": "2026-07-02T03:00:00Z"},
        {"started_at_utc": "2026-07-03T00:00:00Z", "completed_at_utc": "2026-07-03T04:00:00Z"},
    ]
    state = build({"comparable_completed_packets": comparable, "remaining_comparable_work_units": 2})
    assert state["forecast"]["estimated_engineering_hours_remaining"] == 6.0
    assert state["forecast"]["engineering_hours_estimate_status"] == "COMPARABLE_DURATION_EVIDENCE"


def test_calendar_wait_is_separate_from_hours() -> None:
    state = build({"canonical_minimum_demo_days": 10, "genuine_market_demo_days": 3})
    assert state["forecast"]["minimum_evidence_calendar_days_remaining"] == 7
    assert state["forecast"]["earliest_evidence_review_date"] == "2026-08-03"
    assert state["forecast"]["estimated_engineering_hours_remaining"] is None
    assert state["forecast"]["external_wait_separate_from_engineering_time"] is True


def test_critical_path_is_deterministic() -> None:
    first = build()
    second = build()
    assert first["critical_path"] == second["critical_path"]
    assert first["critical_path"]["current_stage"] == "DEMO_EVIDENCE"
    assert first["next_verified_task"] == "DEMO_GENUINE_MARKET_EVIDENCE"


def test_daily_baseline_and_delta_are_deterministic() -> None:
    m = module()
    baseline = build()
    assert baseline["daily_delta"]["daily_delta_status"] == "BASELINE_CREATED"
    criterion_id = m.CRITERIA_SPEC[0][0]
    current = build({"criteria": {criterion_id: {"status": "PASS", "source_type": "genuine_market_demo"}}}, previous=baseline, as_of="2026-07-28")
    assert current["daily_delta"]["criteria_closed_today"] == [criterion_id]
    assert current["daily_delta"] == build({"criteria": {criterion_id: {"status": "PASS", "source_type": "genuine_market_demo"}}}, previous=baseline, as_of="2026-07-28")["daily_delta"]


def test_repository_paths_and_source_inventory_are_read_only(tmp_path: Path) -> None:
    m = module()
    path = tmp_path / "RISK_POLICY.md"
    path.write_text("policy", encoding="utf-8")
    before = path.read_bytes()
    bundle = m.load_forex_live_readiness_evidence(tmp_path)
    assert before == path.read_bytes()
    assert all(not Path(item["path"]).is_absolute() for item in bundle["sources"])
    assert bundle["network_accessed"] is False
    assert bundle["broker_accessed"] is False
    assert bundle["credentials_accessed"] is False


def test_json_and_markdown_are_stable_and_remaining_precedes_completed() -> None:
    m = module()
    state = build()
    assert m.stable_json(state) == m.stable_json(state)
    report = m.render_forex_live_readiness_report(state)
    headings = [line for line in report.splitlines() if line.startswith("#")]
    assert report.startswith("# 🚦 AIOS FOREX — WHEN CAN WE GO LIVE?")
    assert all(len(line.split(maxsplit=2)) > 1 and not line.split(maxsplit=2)[1][0].isalnum() for line in headings)
    assert report.index("## 📉 WHAT REMAINS") < report.index("## ✅ MATERIAL WORK CLOSED TODAY")


def test_all_permissions_and_protected_actions_remain_false() -> None:
    state = build()
    assert state["permissions"] and not any(state["permissions"].values())
    assert state["protected_actions"] and not any(state["protected_actions"].values())
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ("requests", "urllib", "socket", "subprocess", "os.environ"):
        assert forbidden not in source
