import json
import socket

from automation.forex_engine.paper_continuity_review import evaluate_decision_for_continuity_review
from automation.forex_engine.paper_learning_action_router import (
    PAPER_LEARNING_ACTION_BLOCKED,
    PAPER_LEARNING_ACTION_READY,
    PAPER_LEARNING_ACTION_REVIEW_REQUIRED,
    PAPER_LEARNING_ACTION_ROUTER_SCHEMA,
    route_paper_study_journal_to_learning_action,
)
from automation.forex_engine.paper_risk_decision import evaluate_ledger_for_paper_risk_decision
from automation.forex_engine.paper_signal_intake import build_demo_local_signal, evaluate_local_signal_for_ledger
from automation.forex_engine.paper_study_journal import (
    PAPER_STUDY_JOURNAL_BLOCKED,
    build_paper_study_journal,
)
from automation.forex_engine.readiness import evaluate_paper_readiness, build_valid_mock_signal


def _safe_review() -> dict:
    readiness = evaluate_paper_readiness(build_valid_mock_signal())
    if not readiness["accepted_for_paper"]:
        raise RuntimeError("Fixture readiness must be accepted for paper study.")

    ledger = evaluate_local_signal_for_ledger(
        build_demo_local_signal("router_signal_001"),
        signal_id="router_signal_001",
        generated_at_utc="2026-06-12T00:00:00Z",
    )
    decision = evaluate_ledger_for_paper_risk_decision(
        ledger,
        generated_at_utc="2026-06-12T00:00:00Z",
        decision_id="router_decision_001",
    )
    review = evaluate_decision_for_continuity_review(
        decision,
        generated_at_utc="2026-06-12T00:00:00Z",
        review_id="router_review_001",
    )
    return build_paper_study_journal(
        review,
        generated_at_utc="2026-06-12T00:00:00Z",
        journal_id="router_journal_001",
    )


def test_safe_sprint_18_journal_routes_to_learning_ready():
    journal = _safe_review()
    result = route_paper_study_journal_to_learning_action(journal)

    assert result["route_status"] == PAPER_LEARNING_ACTION_READY
    assert result["accepted_for_learning"] is True


def test_router_schema_is_forex_paper_learning_action_router_v1():
    result = route_paper_study_journal_to_learning_action(_safe_review())
    assert result["schema"] == PAPER_LEARNING_ACTION_ROUTER_SCHEMA


def test_execution_allowed_is_never_true():
    journal = _safe_review()
    ready = route_paper_study_journal_to_learning_action(journal)
    blocked = route_paper_study_journal_to_learning_action(
        {
            **journal,
            "journal_status": PAPER_STUDY_JOURNAL_BLOCKED,
            "accepted_for_study": False,
        }
    )

    assert ready["execution_allowed"] is False
    assert blocked["execution_allowed"] is False


def test_live_execution_remains_blocked():
    result = route_paper_study_journal_to_learning_action(_safe_review())
    assert result["live_execution_status"] == "BLOCKED"


def test_selected_learning_action_is_populated_for_ready_route():
    result = route_paper_study_journal_to_learning_action(_safe_review())
    assert result["selected_learning_action"] != ""
    assert result["route_status"] == PAPER_LEARNING_ACTION_READY


def test_required_evidence_is_populated():
    result = route_paper_study_journal_to_learning_action(_safe_review())
    assert isinstance(result["required_evidence"], list)
    assert result["required_evidence"]


def test_blocked_actions_are_present_and_ordered_deterministically():
    result = route_paper_study_journal_to_learning_action(_safe_review())
    blocked_actions = set(result["blocked_actions"])
    assert "broker_api_call" in blocked_actions
    assert "oanda_api_call" in blocked_actions
    assert "real_order_submission" in blocked_actions
    assert "webhook_execution" in blocked_actions
    assert "secret_or_api_key_load" in blocked_actions
    assert "live_market_data_fetch" in blocked_actions
    assert "scheduler_or_daemon_start" in blocked_actions
    assert "worker_launch" in blocked_actions


def test_rejected_or_blocked_journal_cannot_be_executable():
    rejected = {
        **_safe_review(),
        "journal_status": PAPER_STUDY_JOURNAL_BLOCKED,
        "accepted_for_study": False,
    }
    result = route_paper_study_journal_to_learning_action(rejected)

    assert result["route_status"] == PAPER_LEARNING_ACTION_BLOCKED
    assert result["accepted_for_learning"] is False
    assert result["execution_allowed"] is False


def test_missing_required_fields_produces_review_or_blocked():
    bad = dict(_safe_review())
    bad.pop("journal_id", None)
    bad.pop("source_review_status", None)
    result = route_paper_study_journal_to_learning_action(bad)

    assert result["route_status"] in (PAPER_LEARNING_ACTION_REVIEW_REQUIRED, PAPER_LEARNING_ACTION_BLOCKED)
    assert result["accepted_for_learning"] is False


def test_demo_outputs_valid_json_and_expected_fields(capsys):
    from automation.forex_engine.run_paper_learning_action_router_demo import main

    exit_code = main()
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["schema"] == PAPER_LEARNING_ACTION_ROUTER_SCHEMA
    assert output["route_status"] == PAPER_LEARNING_ACTION_READY
    assert output["execution_allowed"] is False
    assert output["mode"] == "PAPER_ONLY"


def test_no_network_broker_order_behavior(monkeypatch):
    created: list[str] = []

    def blocked_socket(*args, **kwargs):
        created.append("socket")
        raise AssertionError("No network calls allowed in router path.")

    monkeypatch.setattr(socket, "socket", blocked_socket)
    result = route_paper_study_journal_to_learning_action(_safe_review())
    assert created == []
    assert result["route_status"] == PAPER_LEARNING_ACTION_READY
