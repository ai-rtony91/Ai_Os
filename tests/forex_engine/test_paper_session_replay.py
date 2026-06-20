"""Tests for paper session replay summaries."""
from __future__ import annotations

from automation.forex_engine.paper_evidence_ledger import append_event, create_ledger
from automation.forex_engine.paper_session_replay import build_paper_session_replay


def test_replay_matches_ledger_event_totals():
    ledger = create_ledger("replay-test")
    ledger = append_event(ledger, "candidate_created", {"candidate_id": "c1"})
    ledger = append_event(ledger, "risk_rejected", {"candidate_id": "c2", "reason": "spread_too_high"})
    ledger = append_event(ledger, "risk_approved", {"candidate_id": "c1"})
    ledger = append_event(ledger, "paper_trade_closed", {"trade_id": "t1", "realized_pl": -25.0})
    ledger = append_event(ledger, "balance_updated", {"trade_id": "t1", "current_balance": 9975.0})
    replay = build_paper_session_replay(ledger, 10000.0, 9975.0)
    assert replay["event_count"] == 5
    assert replay["candidate_count"] == 1
    assert replay["approved_trade_count"] == 1
    assert replay["rejected_trade_count"] == 1
    assert replay["loss_count"] == 1
    assert replay["drawdown"] == 25.0
