import json
from pathlib import Path

from automation.forex_engine import expectancy_ticket_gate_closure_v1 as closer


def use_tmp_repo(monkeypatch, tmp_path: Path):
    repo = tmp_path / "repo"
    reports = repo / "Reports" / "forex_delivery"
    reports.mkdir(parents=True)
    monkeypatch.setattr(closer, "REPO_ROOT", repo)
    monkeypatch.setattr(closer, "REPORTS_DIR", reports)
    return repo, reports


def write_json(path: Path, payload: dict):
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_missing_evidence_returns_expectancy_insufficient(monkeypatch, tmp_path):
    use_tmp_repo(monkeypatch, tmp_path)

    result = closer.run_expectancy_ticket_gate_closure()

    assert result["classifications"]["EXPECTANCY_STATUS"] == closer.EXPECTANCY_EVIDENCE_INSUFFICIENT
    assert result["safety_summary"]["broker_call_performed"] is False


def test_one_closed_trade_does_not_become_expectancy_proven(monkeypatch, tmp_path):
    _, reports = use_tmp_repo(monkeypatch, tmp_path)
    write_json(
        reports / "readiness_state_recalculation_v1_report.json",
        {
            "selected_candidate_id": "c1-eur-buy",
            "selected_strategy": "paper_long_run_supervisor_v2",
            "instrument": "EUR_USD",
            "side": "BUY",
            "sample_size": 1,
            "closed_trades": 1,
            "gross_profit": 10,
            "gross_loss": 0,
            "profit_factor": 999,
            "max_drawdown": 0,
        },
    )

    result = closer.run_expectancy_ticket_gate_closure()

    assert result["classifications"]["EXPECTANCY_STATUS"] == closer.EXPECTANCY_DIRECTIONAL_BUT_SAMPLE_WEAK


def test_missing_take_profit_yields_take_profit_missing(monkeypatch, tmp_path):
    _, reports = use_tmp_repo(monkeypatch, tmp_path)
    write_json(
        reports / "readiness_state_recalculation_v1_report.json",
        {
            "candidate_id": "c1-eur-buy",
            "instrument": "EUR_USD",
            "side": "BUY",
            "sample_size": 35,
            "gross_profit": 70,
            "gross_loss": 10,
            "closed_trades": 35,
            "profit_factor": 7,
            "max_drawdown": 3,
            "stop_loss": "1.0800",
            "units": 1,
            "max_loss": 1,
            "daily_loss_cap": 2,
            "kill_switch_required": True,
            "one_order_only": True,
        },
    )

    result = closer.run_expectancy_ticket_gate_closure()

    assert result["classifications"]["TAKE_PROFIT_STATUS"] == closer.TAKE_PROFIT_EVIDENCE_MISSING
    assert result["classifications"]["TRADE_TICKET_STATUS"] == closer.TRADE_TICKET_MISSING_FIELDS


def test_missing_broker_proof_yields_missing_or_runtime_intake(monkeypatch, tmp_path):
    use_tmp_repo(monkeypatch, tmp_path)

    result = closer.run_expectancy_ticket_gate_closure()

    assert result["classifications"]["BROKER_PROOF_STATUS"] in {
        closer.BROKER_PROOF_MISSING,
        closer.BROKER_PROOF_REQUIRES_RUNTIME_ONLY_HUMAN_INTAKE,
    }


def test_complete_synthetic_evidence_can_classify_ticket_ready_without_broker_calls(monkeypatch, tmp_path):
    _, reports = use_tmp_repo(monkeypatch, tmp_path)
    write_json(
        reports / "readiness_state_recalculation_v1_report.json",
        {
            "candidate_id": "c1-eur-buy",
            "strategy_name": "paper_long_run_supervisor_v2",
            "setup_id": "setup-001",
            "signal_id": "signal-001",
            "instrument": "EUR_USD",
            "side": "BUY",
            "timeframe": "M5",
            "sample_size": 40,
            "closed_trades": 40,
            "wins": 28,
            "losses": 10,
            "breakeven_count": 2,
            "gross_profit": 120,
            "gross_loss": 40,
            "net_pl": 80,
            "profit_factor": 3,
            "max_drawdown": 4,
            "stop_loss": "1.0800",
            "take_profit": "1.0860",
            "units": 1,
            "max_loss": 1,
            "daily_loss_cap": 2,
            "kill_switch_required": True,
            "one_order_only": True,
            "broker_proof_current": True,
        },
    )
    (reports / "AIOS_FOREX_INCIDENT_STOP_PROCEDURE_V1.md").write_text(
        "# AIOS Forex Incident Stop Procedure V1\n", encoding="utf-8"
    )

    result = closer.run_expectancy_ticket_gate_closure()

    assert result["classifications"]["EXPECTANCY_STATUS"] == closer.EXPECTANCY_PROVEN
    assert result["classifications"]["TRADE_TICKET_STATUS"] == closer.TRADE_TICKET_READY_FROM_EVIDENCE
    assert result["classifications"]["TAKE_PROFIT_STATUS"] == closer.TAKE_PROFIT_PROVEN
    assert result["classifications"]["BROKER_PROOF_STATUS"] == closer.BROKER_PROOF_CURRENT
    assert result["classifications"]["NEXT_ARMING_STATUS"] == closer.READY_FOR_HUMAN_ARMING_CANDIDATE
    assert result["safety_summary"]["broker_call_performed"] is False
    assert result["safety_summary"]["network_call_performed"] is False


def test_function_never_requires_credentials_env_network_or_account_ids(monkeypatch, tmp_path):
    use_tmp_repo(monkeypatch, tmp_path)

    result = closer.run_expectancy_ticket_gate_closure()

    assert ".env" in result["files_skipped_for_safety"]
    assert "credentials/" in result["files_skipped_for_safety"]
    assert result["safety_summary"]["credentials_read"] is False
    assert result["safety_summary"]["account_identifiers_read"] is False
    assert result["safety_summary"]["env_read"] is False
    assert result["safety_summary"]["network_call_performed"] is False


def test_report_writing_only_writes_allowed_report_paths(monkeypatch, tmp_path):
    _, reports = use_tmp_repo(monkeypatch, tmp_path)

    result = closer.run_expectancy_ticket_gate_closure(write_reports=True)
    written_names = {Path(path).name for path in result["reports"]["written"]}

    assert written_names == set(closer.REPORT_FILENAMES.values())
    assert not (reports / closer.OPTIONAL_READY_REPORT).exists()


def test_incident_stop_procedure_report_can_be_created_locally(monkeypatch, tmp_path):
    _, reports = use_tmp_repo(monkeypatch, tmp_path)

    result = closer.run_expectancy_ticket_gate_closure(write_reports=True)

    assert result["classifications"]["INCIDENT_STOP_STATUS"] == closer.INCIDENT_STOP_PROCEDURE_CREATED
    assert (reports / "AIOS_FOREX_INCIDENT_STOP_PROCEDURE_V1.md").exists()
