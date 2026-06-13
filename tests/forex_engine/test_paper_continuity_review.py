import json
import socket

from automation.forex_engine.paper_continuity_review import (
    PAPER_REVIEW_BLOCKED,
    PAPER_REVIEW_READY,
    PAPER_CONTINUITY_REVIEW_SCHEMA,
    evaluate_decision_for_continuity_review,
)
from automation.forex_engine.paper_risk_decision import evaluate_ledger_for_paper_risk_decision
from automation.forex_engine.paper_signal_intake import build_demo_local_signal, evaluate_local_signal_for_ledger


def _safe_decision() -> dict:
    ledger = evaluate_local_signal_for_ledger(
        build_demo_local_signal("continuity_signal_001"),
        signal_id="continuity_signal_001",
        generated_at_utc="2026-06-12T00:00:00Z",
    )
    decision = evaluate_ledger_for_paper_risk_decision(
        ledger,
        generated_at_utc="2026-06-12T00:00:00Z",
        decision_id="continuity_decision_001",
    )
    decision["source_decision_id"] = "continuity_decision_001"
    return decision


def test_valid_paper_risk_decision_produces_review_ready():
    result = evaluate_decision_for_continuity_review(
        _safe_decision(),
        generated_at_utc="2026-06-12T00:00:00Z",
    )

    assert result["schema"] == PAPER_CONTINUITY_REVIEW_SCHEMA
    assert result["mode"] == "PAPER_ONLY"
    assert result["review_status"] == PAPER_REVIEW_READY
    assert result["accepted_for_paper"] is True
    assert result["execution_allowed"] is False
    assert result["decision"] == "PAPER_ACCEPT"


def test_rejected_paper_risk_decision_produces_review_blocked():
    decision = _safe_decision()
    decision["decision"] = "PAPER_REJECT"

    result = evaluate_decision_for_continuity_review(decision)

    assert result["review_status"] == PAPER_REVIEW_BLOCKED
    assert result["accepted_for_paper"] is False
    assert any("decision is not PAPER_ACCEPT" in reason for reason in result["reasons"])


def test_missing_source_ids_produce_review_blocked():
    decision = _safe_decision()
    decision["source_decision_id"] = ""
    decision["source_ledger_record_id"] = ""
    decision["signal_id"] = ""

    result = evaluate_decision_for_continuity_review(decision)

    assert result["review_status"] == PAPER_REVIEW_BLOCKED
    assert result["accepted_for_paper"] is False
    assert any("Missing source_decision_id." in reason for reason in result["reasons"])


def test_execution_allowed_true_is_review_blocked():
    decision = _safe_decision()
    decision["execution_allowed"] = True

    result = evaluate_decision_for_continuity_review(decision)

    assert result["review_status"] == PAPER_REVIEW_BLOCKED
    assert any("execution_allowed must be false." in reason for reason in result["reasons"])


def test_risk_flags_present_produce_review_blocked():
    decision = _safe_decision()
    decision["risk_flags"] = ["risk_block"]

    result = evaluate_decision_for_continuity_review(decision)

    assert result["review_status"] == PAPER_REVIEW_BLOCKED
    assert any("risk_flags are present" in reason for reason in result["reasons"])


def test_required_blocked_actions_are_present_for_external_paths():
    result = evaluate_decision_for_continuity_review(_safe_decision())

    blocked = set(result["blocked_actions"])
    assert "broker_api_call" in blocked
    assert "oanda_api_call" in blocked
    assert "real_order_submission" in blocked
    assert "webhook_execution" in blocked
    assert "secret_or_api_key_load" in blocked


def test_review_id_is_deterministic_with_supplied_inputs():
    decision = _safe_decision()
    first = evaluate_decision_for_continuity_review(
        decision,
        generated_at_utc="2026-06-12T00:00:00Z",
        review_id=None,
    )
    second = evaluate_decision_for_continuity_review(
        decision,
        generated_at_utc="2026-06-12T00:00:00Z",
        review_id=None,
    )

    assert first["review_id"] == second["review_id"]


def test_demo_outputs_review_schema_and_ready_status(capsys):
    from automation.forex_engine.run_paper_continuity_review_demo import main

    exit_code = main()
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["schema"] == PAPER_CONTINUITY_REVIEW_SCHEMA
    assert output["review_status"] == PAPER_REVIEW_READY


def test_no_network_or_external_paths_are_used(monkeypatch):
    created = []

    def blocked_socket(*args, **kwargs):
        created.append((args, kwargs))
        raise AssertionError("No external network calls are allowed.")

    monkeypatch.setattr(socket, "socket", blocked_socket)

    result = evaluate_decision_for_continuity_review(_safe_decision())

    assert created == []
    assert result["schema"] == PAPER_CONTINUITY_REVIEW_SCHEMA
    assert result["review_status"] in (PAPER_REVIEW_READY, PAPER_REVIEW_BLOCKED)
