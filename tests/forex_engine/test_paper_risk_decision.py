import socket

from automation.forex_engine.paper_risk_decision import (
    PAPER_ACCEPT,
    PAPER_REJECT,
    PAPER_DECISION_SCHEMA,
    evaluate_ledger_for_paper_risk_decision,
)
from automation.forex_engine.paper_signal_intake import (
    build_demo_local_signal,
    build_unsafe_demo_local_signal,
    evaluate_local_signal_for_ledger,
)


def _safe_record() -> dict:
    return evaluate_local_signal_for_ledger(
        build_demo_local_signal(signal_id="safe_demo_signal_001"),
        signal_id="safe_demo_signal_001",
        generated_at_utc="2026-06-12T00:00:00Z",
    )


def test_valid_paper_intake_ledger_produces_paper_accept():
    result = evaluate_ledger_for_paper_risk_decision(
        _safe_record(),
        generated_at_utc="2026-06-12T00:00:00Z",
        decision_id="static_decision_id",
    )

    assert result["schema"] == PAPER_DECISION_SCHEMA
    assert result["mode"] == "PAPER_ONLY"
    assert result["decision"] == PAPER_ACCEPT
    assert result["execution_allowed"] is False
    assert result["accepted_for_paper"] is True
    assert result["readiness_status"] == "PAPER_READY"
    assert result["source_ledger_record_id"] == _safe_record()["ledger_record_id"]
    assert result["risk_flags"] == []


def test_rejected_paper_intake_ledger_produces_paper_reject():
    record = _safe_record()
    record["readiness_status"] = "PAPER_REJECTED"

    result = evaluate_ledger_for_paper_risk_decision(record)

    assert result["decision"] == PAPER_REJECT
    assert result["accepted_for_paper"] is False
    assert result["execution_allowed"] is False


def test_missing_safety_fields_produce_reject():
    record = _safe_record()
    record.pop("safety")

    result = evaluate_ledger_for_paper_risk_decision(record)

    assert result["decision"] == PAPER_REJECT
    assert result["accepted_for_paper"] is False
    assert any("Safety blocks not fully satisfied" in reason for reason in result["reasons"])


def test_execution_allowed_true_produces_reject():
    record = _safe_record()
    record["execution_allowed"] = True

    result = evaluate_ledger_for_paper_risk_decision(record)

    assert result["decision"] == PAPER_REJECT
    assert result["accepted_for_paper"] is False
    assert any("execution_allowed must be false" in reason for reason in result["reasons"])


def test_risk_flags_present_produce_reject():
    record = _safe_record()
    record["risk_flags"] = ["risk_alert"]

    result = evaluate_ledger_for_paper_risk_decision(record)

    assert result["decision"] == PAPER_REJECT
    assert result["accepted_for_paper"] is False
    assert any("Risk flags are present" in reason for reason in result["reasons"])


def test_required_blocked_actions_are_present_for_broker_oanda_webhook_orders_and_secrets():
    result = evaluate_ledger_for_paper_risk_decision(_safe_record())

    blocked = set(result["blocked_actions"])
    assert "broker_api_call" in blocked
    assert "oanda_api_call" in blocked
    assert "real_order_submission" in blocked
    assert "webhook_execution" in blocked
    assert "secret_or_api_key_load" in blocked


def test_decision_id_is_deterministic_with_supplied_timestamp_and_source_keys():
    record = evaluate_local_signal_for_ledger(
        build_unsafe_demo_local_signal(),
        signal_id="deterministic_signal",
        generated_at_utc="2026-06-12T00:00:00Z",
    )

    first = evaluate_ledger_for_paper_risk_decision(
        record,
        generated_at_utc="2026-06-12T00:00:00Z",
        decision_id=None,
    )
    second = evaluate_ledger_for_paper_risk_decision(
        record,
        generated_at_utc="2026-06-12T00:00:00Z",
        decision_id=None,
    )

    assert first["decision_id"] == second["decision_id"]
    assert first["source_ledger_record_id"] == second["source_ledger_record_id"]


def test_demo_safe_fixture_is_deterministic_and_accepts_when_safe(capsys):
    from automation.forex_engine.run_paper_risk_decision_demo import main

    result_code = main()
    output = capsys.readouterr().out
    decision = __import__("json").loads(output)

    assert result_code == 0
    assert decision["schema"] == PAPER_DECISION_SCHEMA
    assert decision["decision"] == PAPER_ACCEPT
    assert decision["mode"] == "PAPER_ONLY"
    assert decision["execution_allowed"] is False


def test_no_network_or_runtime_paths_are_used(monkeypatch):
    created = []

    def blocked_socket(*args, **kwargs):
        created.append((args, kwargs))
        raise AssertionError("No external network calls are allowed.")

    monkeypatch.setattr(socket, "socket", blocked_socket)

    result = evaluate_ledger_for_paper_risk_decision(
        _safe_record(),
        generated_at_utc="2026-06-12T00:00:00Z",
    )

    assert created == []
    assert result["schema"] == PAPER_DECISION_SCHEMA
    assert result["decision"] in (PAPER_ACCEPT, PAPER_REJECT)
