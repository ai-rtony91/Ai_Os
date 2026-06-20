"""Tests for paper evidence ledger."""
from __future__ import annotations

from automation.forex_engine.paper_evidence_ledger import append_event, create_ledger, reconstruct_session_from_events


def test_evidence_ledger_reconstructs_session():
    ledger = create_ledger("session-test")
    ledger = append_event(ledger, "candidate_created", {"candidate_id": "c1"})
    ledger = append_event(ledger, "risk_approved", {"candidate_id": "c1"})
    ledger = append_event(ledger, "paper_trade_closed", {"trade_id": "t1", "realized_pl": 50.0})
    replay = reconstruct_session_from_events(ledger)
    assert ledger["valid"] is True
    assert replay["event_count"] == 3
    assert replay["candidate_count"] == 1
    assert replay["approved_trade_count"] == 1
    assert replay["win_count"] == 1
    assert replay["realized_pl"] == 50.0
