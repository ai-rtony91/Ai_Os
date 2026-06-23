import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from automation.forex_engine import broker_proof_ticket_closure_v1 as closer


def use_tmp_repo(monkeypatch, tmp_path: Path):
    repo = tmp_path / "repo"
    reports = repo / "Reports" / "forex_delivery"
    reports.mkdir(parents=True)
    monkeypatch.setattr(closer, "REPO_ROOT", repo)
    monkeypatch.setattr(closer, "REPORTS_DIR", reports)
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


def test_missing_broker_proof_returns_runtime_only_human_intake(monkeypatch, tmp_path):
    use_tmp_repo(monkeypatch, tmp_path)

    result = closer.run_broker_proof_ticket_closure()

    assert result["classifications"]["BROKER_PROOF_STATUS"] == closer.BROKER_PROOF_REQUIRES_RUNTIME_ONLY_HUMAN_INTAKE
    assert result["safety_summary"]["broker_call_performed"] is False


def test_stale_broker_proof_returns_stale(monkeypatch, tmp_path):
    use_tmp_repo(monkeypatch, tmp_path)
    old_timestamp = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()

    result = closer.run_broker_proof_ticket_closure(
        {"broker_proof": current_proof(proof_timestamp=old_timestamp)}
    )

    assert result["classifications"]["BROKER_PROOF_STATUS"] == closer.BROKER_PROOF_STALE


def test_sanitized_current_broker_proof_can_return_current(monkeypatch, tmp_path):
    use_tmp_repo(monkeypatch, tmp_path)

    result = closer.run_broker_proof_ticket_closure({"broker_proof": current_proof()})

    assert result["classifications"]["BROKER_PROOF_STATUS"] == closer.BROKER_PROOF_CURRENT


def test_missing_take_profit_returns_take_profit_missing(monkeypatch, tmp_path):
    use_tmp_repo(monkeypatch, tmp_path)
    ticket = complete_ticket(take_profit=None)

    result = closer.run_broker_proof_ticket_closure({"ticket": ticket})

    assert result["classifications"]["TAKE_PROFIT_STATUS"] == closer.TAKE_PROFIT_EVIDENCE_MISSING
    assert "deterministic_take_profit_evidence" in result["missing_evidence"]


def test_complete_synthetic_local_ticket_can_return_ticket_ready(monkeypatch, tmp_path):
    use_tmp_repo(monkeypatch, tmp_path)

    result = closer.run_broker_proof_ticket_closure(
        {
            "expectancy_status": closer.EXPECTANCY_PROVEN,
            "broker_proof": current_proof(),
            "ticket": complete_ticket(),
            "incident_stop_procedure_present": True,
        }
    )

    assert result["classifications"]["TRADE_TICKET_STATUS"] == closer.TRADE_TICKET_READY_FROM_EVIDENCE
    assert result["classifications"]["TAKE_PROFIT_STATUS"] == closer.TAKE_PROFIT_PROVEN
    assert result["classifications"]["RISK_GATE_STATUS"] == closer.RISK_GATES_PASS


def test_missing_risk_gates_blocks_human_arming_candidate(monkeypatch, tmp_path):
    use_tmp_repo(monkeypatch, tmp_path)
    ticket = complete_ticket(kill_switch_state="FAILED")

    result = closer.run_broker_proof_ticket_closure(
        {
            "expectancy_status": closer.EXPECTANCY_PROVEN,
            "broker_proof": current_proof(),
            "ticket": ticket,
            "incident_stop_procedure_present": True,
        }
    )

    assert result["classifications"]["RISK_GATE_STATUS"] == closer.RISK_GATES_FAIL
    assert result["classifications"]["HUMAN_ARMING_CANDIDATE_STATUS"] == closer.BLOCKED_BY_RISK_GATE


def test_dashboard_fixture_data_does_not_count_as_broker_proof(monkeypatch, tmp_path):
    use_tmp_repo(monkeypatch, tmp_path)

    result = closer.run_broker_proof_ticket_closure(
        {"broker_proof": current_proof(source_label="dashboard_fixture")}
    )

    assert result["classifications"]["BROKER_PROOF_STATUS"] != closer.BROKER_PROOF_CURRENT
    assert result["found_evidence"]["dashboard_fixture_broker_proof"] is True


def test_credentials_and_account_ids_are_redacted(monkeypatch, tmp_path):
    use_tmp_repo(monkeypatch, tmp_path)
    proof = current_proof(account_id="123456789", api_key="secret-key")

    result = closer.run_broker_proof_ticket_closure({"broker_proof": proof})
    serialized = json.dumps(result, sort_keys=True)

    assert "123456789" not in serialized
    assert "secret-key" not in serialized
    assert result["sanitization"]["sensitive_input_rejected_or_redacted"] is True
    assert any("account_id" in field for field in result["sanitization"]["redacted_fields"])


def test_function_never_requires_env_network_broker_credentials_or_account_ids(monkeypatch, tmp_path):
    use_tmp_repo(monkeypatch, tmp_path)

    result = closer.run_broker_proof_ticket_closure()

    assert ".env" in result["files_skipped_for_safety"]
    assert "credentials/" in result["files_skipped_for_safety"]
    assert result["safety_summary"]["network_call_performed"] is False
    assert result["safety_summary"]["credentials_read"] is False
    assert result["safety_summary"]["account_identifiers_read"] is False
    assert result["safety_summary"]["broker_call_performed"] is False


def test_report_writing_only_writes_allowed_report_paths(monkeypatch, tmp_path):
    _, reports = use_tmp_repo(monkeypatch, tmp_path)

    result = closer.run_broker_proof_ticket_closure(write_reports=True)
    written_names = {Path(path).name for path in result["reports"]["written"]}

    assert written_names == set(closer.REPORT_FILENAMES.values())
    assert not (reports / closer.OPTIONAL_READY_REPORT).exists()
