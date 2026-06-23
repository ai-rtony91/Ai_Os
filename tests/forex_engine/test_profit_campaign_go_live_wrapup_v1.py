from datetime import datetime, timezone
from pathlib import Path

from automation.forex_engine import broker_proof_ticket_closure_v1 as broker
from automation.forex_engine import forex_uptime_range_planner_v1 as uptime
from automation.forex_engine import micro_batch_campaign_ladder_v1 as ladder
from automation.forex_engine import profit_campaign_go_live_wrapup_v1 as wrapup


def use_tmp_repo(monkeypatch, tmp_path: Path):
    repo = tmp_path / "repo"
    reports = repo / "Reports" / "forex_delivery"
    reports.mkdir(parents=True)

    monkeypatch.setattr(broker, "REPO_ROOT", repo)
    monkeypatch.setattr(broker, "REPORTS_DIR", reports)

    monkeypatch.setattr(ladder, "REPO_ROOT", repo)
    monkeypatch.setattr(ladder, "REPORTS_DIR", reports)
    monkeypatch.setattr(
        ladder,
        "REPORT_PATHS",
        {
            "campaign_ladder": reports / "AIOS_FOREX_MICRO_BATCH_CAMPAIGN_LADDER_V1.md",
            "target_50": reports / "AIOS_FOREX_50_PERCENT_CAMPAIGN_TARGET_V1.md",
            "target_100": reports / "AIOS_FOREX_100_PERCENT_REPEATABILITY_TARGET_V1.md",
        },
    )

    monkeypatch.setattr(uptime, "REPO_ROOT", repo)
    monkeypatch.setattr(uptime, "REPORTS_DIR", reports)
    monkeypatch.setattr(uptime, "REPORT_PATH", reports / "AIOS_FOREX_UPTIME_RANGE_PLANNER_80_22_5_22_6_V1.md")

    monkeypatch.setattr(wrapup, "REPO_ROOT", repo)
    monkeypatch.setattr(wrapup, "REPORTS_DIR", reports)
    monkeypatch.setattr(wrapup, "WRAPUP_REPORT", reports / "AIOS_FOREX_PROFIT_CAMPAIGN_GO_LIVE_WRAPUP_V1.md")
    monkeypatch.setattr(wrapup, "OPTIONAL_READY_REPORT", reports / "AIOS_FOREX_READY_FOR_HUMAN_ARMING_CANDIDATE_V3.md")
    return repo, reports


def current_proof(**overrides):
    payload = {
        "broker_alias": "BROKER_ALIAS_ONLY",
        "environment": "DEMO",
        "proof_timestamp": datetime.now(timezone.utc).isoformat(),
        "instrument_availability": "EUR_USD_AVAILABLE",
        "connection_proof_status": "CURRENT",
        "order_placement_disabled_confirmation": True,
        "account_id_redacted_confirmation": True,
        "credential_not_pasted_confirmation": True,
        "credential_not_persisted_confirmation": True,
        "broker_ui_balance_redacted_confirmation": True,
        "human_operator_confirmation": True,
    }
    payload.update(overrides)
    return payload


def complete_ticket(**overrides):
    payload = {
        "aios_trade_number": "AIOS-TRADE-TEST-001",
        "session_id": "SESSION-TEST-001",
        "candidate_id": "CANDIDATE-TEST-001",
        "setup_id": "SETUP-TEST-001",
        "strategy_id": "STRATEGY-TEST-001",
        "instrument": "EUR_USD",
        "side": "BUY",
        "mode": "DEMO_PROOF_ONLY",
        "micro_size_units": 1,
        "stop_loss": "1.0800",
        "take_profit": "1.0860",
        "max_loss_gate": "CLEAR",
        "daily_stop_gate": "CLEAR",
        "kill_switch_state": "CLEAR",
        "one_order_only_rule": "ENFORCED",
        "broker_proof_reference": "RUNTIME_ONLY_SANITIZED_PROOF",
        "credential_handling_rule": "RUNTIME_ONLY_NO_PERSISTENCE",
        "post_trade_reconciliation_rule": "REQUIRED",
        "incident_stop_rule": "PRESENT",
        "evidence_path": "Reports/forex_delivery/SANITIZED_ALIAS.md",
    }
    payload.update(overrides)
    return payload


def campaign(campaign_id="CAMP-001", **overrides):
    payload = {
        "campaign_id": campaign_id,
        "micro_execution_ids": [f"{campaign_id}-MICRO-{index:03d}" for index in range(1, 13)],
        "strategy_id": "STRATEGY-001",
        "candidate_id": "CANDIDATE-001",
        "instrument": "EUR_USD",
        "side": "BUY",
        "start_time": "2026-06-23T00:00:00Z",
        "end_time": "2026-06-23T01:00:00Z",
        "gross_pl": 75.0,
        "net_pl": 52.0,
        "return_percent": 52.0,
        "max_drawdown": 4.0,
        "win_count": 9,
        "loss_count": 2,
        "breakeven_count": 1,
        "average_r": 1.8,
        "profit_factor": 2.7,
        "fees": 1.0,
        "spread": 0.8,
        "slippage": 0.2,
        "stop_loss_compliance": True,
        "take_profit_compliance": True,
        "risk_governor_state": "PASS",
        "broker_proof_state": "CURRENT",
        "reconciliation_state": "RECONCILED",
        "evidence_path": "Reports/forex_delivery/SANITIZED_CAMPAIGN_EVIDENCE.md",
        "proof_mode": "PAPER",
    }
    payload.update(overrides)
    return payload


def uptime_state(**overrides):
    payload = {
        "uptime_80_requested": True,
        "requested_range": "22/5",
        "trading_hours_per_day": 22,
        "trading_days_per_week": 5,
        "maintenance_hours_per_day": 2,
        "broker_session_proof": {"status": "SUPPORTED", "instrument": "EUR_USD", "supported_hours_per_week": 110, "supported_days_per_week": 5},
        "market_session_proof": {"status": "SUPPORTED", "instrument": "EUR_USD"},
        "incident_stop_proof": {"status": "PROVEN"},
        "monitoring_proof": {"status": "PROVEN"},
        "reconciliation_proof": {"status": "PROVEN"},
    }
    payload.update(overrides)
    return payload


def complete_state(**overrides):
    payload = {
        "expectancy_status": wrapup.EXPECTANCY_PROVEN,
        "broker_proof": current_proof(),
        "ticket": complete_ticket(),
        "incident_stop_procedure_present": True,
        "campaigns": [campaign("CAMP-001"), campaign("CAMP-002")],
        "uptime_range": uptime_state(),
    }
    payload.update(overrides)
    return payload


def test_missing_evidence_blocks_wrapup_and_requires_human_intake(monkeypatch, tmp_path):
    use_tmp_repo(monkeypatch, tmp_path)

    result = wrapup.run_profit_campaign_go_live_wrapup()

    assert result["classifications"]["GO_LIVE_WRAPUP_STATUS"] == wrapup.WRAPUP_BLOCKED_BY_EVIDENCE
    assert result["classifications"]["BROKER_PROOF_STATUS"] == broker.BROKER_PROOF_REQUIRES_RUNTIME_ONLY_HUMAN_INTAKE
    assert result["classifications"]["TARGET_50_STATUS"] == wrapup.TARGET_50_EVIDENCE_MISSING
    assert result["optional_ready_report"]["created"] is False
    assert result["safety_summary"]["network_call_performed"] is False


def test_single_50_percent_campaign_does_not_satisfy_100_percent_repeatability(monkeypatch, tmp_path):
    use_tmp_repo(monkeypatch, tmp_path)

    state = complete_state(campaigns=[campaign("CAMP-001")])
    result = wrapup.run_profit_campaign_go_live_wrapup(state)

    assert result["classifications"]["TARGET_50_STATUS"] == wrapup.TARGET_50_REPEATABILITY_REQUIRED
    assert result["classifications"]["TARGET_100_STATUS"] == wrapup.TARGET_100_PLANNING_ONLY
    assert result["classifications"]["HUMAN_ARMING_CANDIDATE_STATUS"] == broker.BLOCKED_BY_EXPECTANCY_EVIDENCE
    assert result["optional_ready_report"]["created"] is False


def test_two_50_percent_campaign_profiles_can_reach_human_arming_candidate(monkeypatch, tmp_path):
    use_tmp_repo(monkeypatch, tmp_path)

    result = wrapup.run_profit_campaign_go_live_wrapup(complete_state())

    assert result["classifications"]["GO_LIVE_WRAPUP_STATUS"] == wrapup.WRAPUP_READY_FOR_HUMAN_ARMING_CANDIDATE
    assert result["classifications"]["TARGET_50_STATUS"] == wrapup.TARGET_50_PAPER_CANDIDATE
    assert result["classifications"]["TARGET_100_STATUS"] == wrapup.TARGET_100_REPEATABILITY_REQUIRED
    assert result["visible_money_facts"]["campaign_count"] == 2
    assert result["visible_money_facts"]["micro_execution_count"] == 24


def test_22_6_requested_range_stays_planning_without_broker_session_support(monkeypatch, tmp_path):
    use_tmp_repo(monkeypatch, tmp_path)
    state = complete_state(
        uptime_range={
            "requested_range": "22/6",
            "trading_hours_per_day": 22,
            "trading_days_per_week": 6,
            "maintenance_hours_per_day": 2,
        }
    )

    result = wrapup.run_profit_campaign_go_live_wrapup(state)

    assert result["classifications"]["UPTIME_RANGE_STATUS"] == uptime.UPTIME_RANGE_PLANNING_ONLY
    assert result["uptime_range_planner"]["activation_status"]["range_22_6_activated"] is False


def test_credentials_account_ids_and_broker_order_ids_are_redacted(monkeypatch, tmp_path):
    use_tmp_repo(monkeypatch, tmp_path)
    state = complete_state(account_id="123456", api_key="LEAKME-API-KEY", broker_order_id="ORDER-1")

    result = wrapup.run_profit_campaign_go_live_wrapup(state)
    serialized = str(result)

    assert "123456" not in serialized
    assert "LEAKME-API-KEY" not in serialized
    assert "ORDER-1" not in serialized
    assert result["sanitization"]["sensitive_input_rejected_or_redacted"] is True


def test_write_reports_creates_required_reports_and_optional_v3_only_when_all_gates_pass(monkeypatch, tmp_path):
    _, reports = use_tmp_repo(monkeypatch, tmp_path)

    result = wrapup.run_profit_campaign_go_live_wrapup(complete_state(), write_reports=True)
    written_names = {Path(path).name for path in result["reports"]["written"]}

    assert "AIOS_FOREX_PROFIT_CAMPAIGN_GO_LIVE_WRAPUP_V1.md" in written_names
    assert "AIOS_FOREX_MICRO_BATCH_CAMPAIGN_LADDER_V1.md" in written_names
    assert "AIOS_FOREX_UPTIME_RANGE_PLANNER_80_22_5_22_6_V1.md" in written_names
    assert result["optional_ready_report"]["created"] is True
    assert (reports / "AIOS_FOREX_READY_FOR_HUMAN_ARMING_CANDIDATE_V3.md").exists()
