from __future__ import annotations

import inspect

from automation.forex_engine.self_improvement_review import (
    SELF_IMPROVEMENT_ALLOWED,
    SELF_IMPROVEMENT_REQUIRES_APPROVAL,
    SELF_IMPROVEMENT_BLOCKED,
    RejectionReason,
    review_self_improvement,
)


def test_module_imports():
    assert SELF_IMPROVEMENT_ALLOWED == "allowed"
    assert hasattr(review_self_improvement, "__call__")


def test_insufficient_evidence_collect_more():
    result = review_self_improvement(session_replay={"mode": "PAPER_ONLY", "trades_closed": 2, "wins": 1}, evidence_summary={}, supervisor_summary={})
    assert result["allowed"] is False
    assert result["decision"] == SELF_IMPROVEMENT_BLOCKED
    assert result["recommended_improvement"] == "collect_more_paper_evidence"
    assert result["blocked_reason"] in {RejectionReason.INSUFFICIENT_EVIDENCE, RejectionReason.MISSING_SESSION_METRICS}
    assert result["proposed_regression_tests"]
    assert result["safety"]["paper_only"] is True


def test_winning_session_recommends_bounded_improvement():
    session_replay = {
        "mode": "PAPER_ONLY",
        "trades_closed": 20,
        "wins": 12,
        "losses": 6,
        "breakeven": 2,
        "net_pnl": 180.0,
        "win_rate_pct": 60.0,
        "max_drawdown": 12.0,
        "counts_by_event_type": {},
        "blocked_reasons": [],
    }
    evidence_summary = {"rejection_summary": {}}
    supervisor_summary = {"candidate_count": 40, "selected_count": 10}
    result = review_self_improvement(session_replay=session_replay, evidence_summary=evidence_summary, supervisor_summary=supervisor_summary)
    assert result["allowed"] is True
    assert result["decision"] == SELF_IMPROVEMENT_ALLOWED
    assert result["recommended_improvement"] in {
        "tighten_spread_cap",
        "add_missing_rejection_regression_test",
        "reduce_risk_multiplier_on_drawdown",
        "improve_stale_data_rejection",
        "improve_no_trade_filter",
        "add_duplicate_setup_block_regression",
    }
    assert isinstance(result["proposed_regression_tests"], list)
    assert len(result["proposed_regression_tests"]) >= 1
    assert result["total_trades"] == 20
    assert result["wins"] == 12
    assert result["losses"] == 6
    assert result["breakeven"] == 2
    assert result["next_safe_action"]


def test_losing_session_and_risk_failures():
    session_replay = {
        "mode": "PAPER_ONLY",
        "trades_closed": 16,
        "wins": 2,
        "losses": 13,
        "breakeven": 1,
        "net_pnl": -130.0,
        "win_rate_pct": 12.5,
        "max_drawdown": 80.0,
        "blocked_reasons": ["risk_exceeded", "risk_exceeded", "risk_exceeded"],
    }
    result = review_self_improvement(session_replay=session_replay, evidence_summary={"rejection_summary": {}}, supervisor_summary={})
    assert result["allowed"] is True
    assert result["risk_failures"] >= 3
    assert result["recommended_improvement"] == "reduce_risk_multiplier_on_drawdown"
    assert result["recommended_improvement_scope"] == "trade_risk_governance"
    assert result["proposed_regression_tests"]
    assert result["next_safe_action"]


def test_rejection_reason_aggregation():
    session_replay = {
        "mode": "PAPER_ONLY",
        "trades_closed": 12,
        "wins": 4,
        "losses": 6,
        "breakeven": 2,
        "net_pnl": -20.0,
        "win_rate_pct": 33.3,
        "max_drawdown": 22.0,
        "blocked_reasons": ["spread_too_high", "stale_data_rejected", "spread_too_high", "duplicate_setup"],
    }
    result = review_self_improvement(
        session_replay=session_replay,
        evidence_summary={"rejected_reasons": ["risk_blocked", "spread_too_high"]},
        supervisor_summary={"rejected_candidates": [{"reason": "duplicate_setup"}, "candidate_rejected"]},
    )
    assert result["allowed"] is True
    assert result["rejection_summary"]["spread_too_high"] == 2
    assert result["rejected_setup_summary"]["duplicate_setups"] >= 1


def test_protected_action_requires_approval():
    result_live = review_self_improvement(
        session_replay={"mode": "PAPER_ONLY", "trades_closed": 11, "wins": 1, "losses": 0, "breakeven": 0, "net_pnl": 5.0},
        requested_change="Enable live trading and increase leverage",
        evidence_summary={"net_pnl": 5.0},
        supervisor_summary={},
    )
    assert result_live["decision"] == SELF_IMPROVEMENT_REQUIRES_APPROVAL
    assert result_live["approval_required"] is True
    assert result_live["protected_action_detected"] is True
    assert result_live["no_live_setting_change"] is True
    assert result_live["allowed"] is False

    result_broker = review_self_improvement(
        session_replay={"mode": "PAPER_ONLY", "trades_closed": 11, "wins": 2, "losses": 1, "breakeven": 0, "net_pnl": 7.0},
        requested_change="Use broker SDK credentials to submit orders",
        evidence_summary={"net_pnl": 7.0},
    )
    assert result_broker["decision"] == SELF_IMPROVEMENT_REQUIRES_APPROVAL
    assert result_broker["approval_required"] is True


def test_one_improvement_only():
    session_replay = {
        "mode": "PAPER_ONLY",
        "trades_closed": 15,
        "wins": 7,
        "losses": 4,
        "breakeven": 4,
        "net_pnl": 15.0,
        "win_rate_pct": 46.0,
        "max_drawdown": 5.0,
        "blocked_reasons": ["spread_too_high", "stale_data_rejected", "duplicate_setup", "risk_blocked"],
    }
    result = review_self_improvement(session_replay=session_replay, evidence_summary={"rejected_reasons": ["spread_too_high"]}, supervisor_summary={})
    assert isinstance(result["recommended_improvement"], str)
    assert result["recommended_improvement"] in {
        "tighten_spread_cap",
        "improve_stale_data_rejection",
        "improve_no_trade_filter",
        "add_duplicate_setup_block_regression",
        "add_missing_rejection_regression_test",
        "reduce_risk_multiplier_on_drawdown",
    }
    assert not isinstance(result["proposed_regression_tests"], str)
    assert len(result["proposed_regression_tests"]) == 2


def test_evidence_path_absolute_block():
    result = review_self_improvement(
        session_replay={"mode": "PAPER_ONLY", "trades_closed": 15, "wins": 1, "losses": 2, "breakeven": 0, "net_pnl": 1.0},
        evidence_path="/tmp/abs/path",
        evidence_summary={},
    )
    assert result["decision"] != SELF_IMPROVEMENT_ALLOWED
    assert result["blocked_reason"] == "evidence_path_invalid"


def test_module_source_safety_scan():
    source = inspect.getsource(__import__("automation.forex_engine.self_improvement_review", fromlist=["*"]))
    forbidden = [
        "subprocess",
        "requests.",
        "socket",
        "urllib",
        "open(",
        ".write_text",
        ".write_bytes",
        "pathlib",
        "os.system",
        "broker_sdk",
        "secret",
        "getenv",
        "environ",
    ]
    for token in forbidden:
        assert token not in source
