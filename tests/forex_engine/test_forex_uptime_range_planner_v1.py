from pathlib import Path

from automation.forex_engine import forex_uptime_range_planner_v1 as planner


def readiness_state(**overrides):
    state = {
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
    state.update(overrides)
    return state


def test_default_uptime_range_is_planning_only_and_safe():
    result = planner.run_forex_uptime_range_planner()

    assert result["classifications"]["UPTIME_RANGE_STATUS"] == planner.UPTIME_RANGE_PLANNING_ONLY
    assert planner.UPTIME_80_PLANNING in result["planning_modes"]
    assert result["safety_summary"]["network_call_performed"] is False
    assert result["activation_status"]["uptime_80_activated"] is False


def test_22_6_requested_remains_planning_without_session_proof():
    result = planner.run_forex_uptime_range_planner(
        {
            "requested_range": "22/6",
            "trading_hours_per_day": 22,
            "trading_days_per_week": 6,
            "maintenance_hours_per_day": 2,
        }
    )

    assert planner.RANGE_22_6_REQUESTED_PLANNING in result["planning_modes"]
    assert result["classifications"]["UPTIME_RANGE_STATUS"] == planner.UPTIME_RANGE_PLANNING_ONLY
    assert "22_6_requires_broker_and_market_session_support" in result["blocked_reasons"]
    assert result["activation_status"]["range_22_6_activated"] is False


def test_22_5_remains_planning_until_readiness_gates_pass():
    result = planner.run_forex_uptime_range_planner(
        {
            "requested_range": "22/5",
            "trading_hours_per_day": 22,
            "trading_days_per_week": 5,
            "maintenance_hours_per_day": 2,
        }
    )

    assert planner.RANGE_22_5_PLANNING in result["planning_modes"]
    assert result["classifications"]["UPTIME_RANGE_STATUS"] == planner.UPTIME_RANGE_PLANNING_ONLY
    assert result["activation_status"]["range_22_5_activated"] is False


def test_80_percent_uptime_remains_planning_until_readiness_gates_pass():
    result = planner.run_forex_uptime_range_planner(
        {
            "uptime_80_requested": True,
            "trading_hours_per_day": 19.2,
            "trading_days_per_week": 7,
            "maintenance_hours_per_day": 4.8,
        }
    )

    assert planner.UPTIME_80_PLANNING in result["planning_modes"]
    assert result["classifications"]["UPTIME_RANGE_STATUS"] == planner.UPTIME_RANGE_PLANNING_ONLY
    assert result["activation_status"]["uptime_80_activated"] is False


def test_readiness_gates_can_reach_paper_simulation_without_activation():
    result = planner.run_forex_uptime_range_planner(readiness_state())

    assert result["classifications"]["UPTIME_RANGE_STATUS"] == planner.UPTIME_RANGE_READY_FOR_PAPER_SIMULATION
    assert result["calculations"]["trading_hours_per_week"] == 110
    assert result["activation_status"]["range_22_5_activated"] is False


def test_22_6_with_session_support_still_blocks_on_live_evidence_for_future_approval():
    result = planner.run_forex_uptime_range_planner(
        readiness_state(
            requested_range="22/6",
            trading_days_per_week=6,
            broker_session_proof={
                "status": "SUPPORTED",
                "instrument": "EUR_USD",
                "supported_hours_per_week": 132,
                "supported_days_per_week": 6,
            },
        )
    )

    assert planner.RANGE_DETECTED_FROM_BROKER_SESSION in result["planning_modes"]
    assert result["classifications"]["UPTIME_RANGE_STATUS"] == planner.UPTIME_RANGE_BLOCKED_BY_LIVE_EVIDENCE
    assert result["activation_status"]["range_22_6_activated"] is False


def test_credentials_and_account_ids_are_redacted():
    result = planner.run_forex_uptime_range_planner(
        {
            "requested_range": "22/6",
            "account_id": "123456",
            "api_key": "secret",
        }
    )

    assert result["sanitization"]["sensitive_input_rejected_or_redacted"] is True
    assert "account_id" in result["sanitization"]["redacted_fields"]


def test_write_report_only_writes_allowed_path(monkeypatch, tmp_path):
    reports = tmp_path / "Reports" / "forex_delivery"
    monkeypatch.setattr(planner, "REPORTS_DIR", reports)
    monkeypatch.setattr(planner, "REPORT_PATH", reports / "AIOS_FOREX_UPTIME_RANGE_PLANNER_80_22_5_22_6_V1.md")

    result = planner.run_forex_uptime_range_planner(readiness_state(), write_reports=True)

    assert {Path(path).name for path in result["reports"]["written"]} == {
        "AIOS_FOREX_UPTIME_RANGE_PLANNER_80_22_5_22_6_V1.md"
    }
    assert (reports / "AIOS_FOREX_UPTIME_RANGE_PLANNER_80_22_5_22_6_V1.md").exists()
