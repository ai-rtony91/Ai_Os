import json
import socket

from automation.forex_engine.paper_continuity_review import (
    PAPER_REVIEW_READY,
    PAPER_REVIEW_BLOCKED,
    evaluate_decision_for_continuity_review,
)
from automation.forex_engine.paper_risk_decision import evaluate_ledger_for_paper_risk_decision
from automation.forex_engine.paper_signal_intake import (
    build_demo_local_signal,
    evaluate_local_signal_for_ledger,
)
from automation.forex_engine.paper_study_journal import (
    PAPER_STUDY_JOURNAL_BLOCKED,
    PAPER_STUDY_JOURNAL_READY,
    PAPER_STUDY_JOURNAL_SCHEMA,
    build_paper_study_journal,
)
from automation.forex_engine.readiness import build_valid_mock_signal, evaluate_paper_readiness


def _safe_review() -> dict:
    readiness = evaluate_paper_readiness(build_valid_mock_signal())
    if not readiness["accepted_for_paper"]:
        raise RuntimeError("README fixture must be accepted for paper study.")

    ledger = evaluate_local_signal_for_ledger(
        build_demo_local_signal("study_signal_001"),
        signal_id="study_signal_001",
        generated_at_utc="2026-06-12T00:00:00Z",
    )
    decision = evaluate_ledger_for_paper_risk_decision(
        ledger,
        generated_at_utc="2026-06-12T00:00:00Z",
        decision_id="study_decision_001",
    )
    return evaluate_decision_for_continuity_review(
        decision,
        generated_at_utc="2026-06-12T00:00:00Z",
        review_id="study_review_001",
    )


def test_valid_continuity_review_produces_ready_journal():
    review = _safe_review()
    result = build_paper_study_journal(
        review,
        generated_at_utc="2026-06-12T00:00:00Z",
        journal_id="study_journal_001",
    )

    assert result["schema"] == PAPER_STUDY_JOURNAL_SCHEMA
    assert result["mode"] == "PAPER_ONLY"
    assert result["journal_status"] == PAPER_STUDY_JOURNAL_READY
    assert result["accepted_for_study"] is True
    assert result["execution_allowed"] is False
    assert result["source_review_status"] == PAPER_REVIEW_READY


def test_non_ready_continuity_review_produces_blocked_journal():
    review = _safe_review()
    review["review_status"] = PAPER_REVIEW_BLOCKED

    result = build_paper_study_journal(review)

    assert result["journal_status"] == PAPER_STUDY_JOURNAL_BLOCKED
    assert result["accepted_for_study"] is False
    assert any("review_status is not PAPER_REVIEW_READY" in reason for reason in result["reasons"])


def test_missing_source_ids_produce_blocked_journal():
    review = _safe_review()
    review["source_decision_id"] = ""
    review["source_ledger_record_id"] = ""
    review["signal_id"] = ""

    result = build_paper_study_journal(review)

    assert result["journal_status"] == PAPER_STUDY_JOURNAL_BLOCKED
    assert any("Missing source_decision_id." in reason for reason in result["reasons"])
    assert any("Missing source_ledger_record_id." in reason for reason in result["reasons"])
    assert any("Missing signal_id." in reason for reason in result["reasons"])


def test_required_blocked_actions_are_present():
    review = _safe_review()
    result = build_paper_study_journal(review)

    blocked = set(result["blocked_actions"])
    assert "broker_api_call" in blocked
    assert "oanda_api_call" in blocked
    assert "real_order_submission" in blocked
    assert "webhook_execution" in blocked
    assert "secret_or_api_key_load" in blocked


def test_journal_id_is_deterministic_with_supplied_inputs():
    review = _safe_review()
    first = build_paper_study_journal(review, generated_at_utc="2026-06-12T00:00:00Z", journal_id=None)
    second = build_paper_study_journal(review, generated_at_utc="2026-06-12T00:00:00Z", journal_id=None)

    assert first["journal_id"] == second["journal_id"]


def test_demo_script_outputs_ready_payload(capsys):
    from automation.forex_engine.run_paper_study_journal_demo import main

    exit_code = main()
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["schema"] == PAPER_STUDY_JOURNAL_SCHEMA
    assert output["journal_status"] == PAPER_STUDY_JOURNAL_READY


def test_no_network_or_external_paths_are_used(monkeypatch):
    review = _safe_review()

    created = []

    def blocked_socket(*args, **kwargs):
        created.append((args, kwargs))
        raise AssertionError("No external network calls are allowed.")

    monkeypatch.setattr(socket, "socket", blocked_socket)

    result = build_paper_study_journal(review)

    assert created == []
    assert result["schema"] == PAPER_STUDY_JOURNAL_SCHEMA
    assert result["journal_status"] in (PAPER_STUDY_JOURNAL_READY, PAPER_STUDY_JOURNAL_BLOCKED)
