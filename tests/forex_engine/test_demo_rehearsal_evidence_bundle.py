"""Tests for deterministic demo rehearsal evidence bundles."""
from __future__ import annotations

import inspect

from automation.forex_engine import demo_rehearsal_evidence_bundle as bundle


def test_default_rehearsal_returns_review_bundle():
    result = bundle.run_demo_rehearsal_evidence_bundle()
    assert result["allowed"] is True
    assert result["decision"] == "REHEARSAL_EVIDENCE_READY"
    assert result["mode"] == bundle.DEMO_REHEARSAL_MODE
    assert result["pass_fail"]["passed"] is True


def test_output_contains_required_top_level_sections():
    result = bundle.run_demo_rehearsal_evidence_bundle()
    required = {
        "bundle_id",
        "bundle_version",
        "generated_at",
        "mode",
        "input_summary",
        "normalized_market_state",
        "strategy_candidates",
        "rejected_candidates",
        "selected_candidate_ids",
        "risk_sizing",
        "order_preview",
        "paper_fill",
        "lifecycle_summary",
        "balance_summary",
        "evidence_ledger_summary",
        "session_replay_summary",
        "safety_boundary",
        "approval_gates",
        "pass_fail",
        "blockers",
        "next_action",
    }
    assert required.issubset(set(result))


def test_safety_boundary_blocks_live_and_broker_submit():
    result = bundle.run_demo_rehearsal_evidence_bundle()
    safety = result["safety_boundary"]
    assert safety["live_trading_allowed"] is False
    assert safety["broker_submit_allowed"] is False
    assert result["live_trading_allowed"] is False
    assert result["broker_submit_allowed"] is False


def test_no_credentials_account_ids_network_live_order_or_runtime_write_used():
    result = bundle.run_demo_rehearsal_evidence_bundle()
    assert result["credentials_used"] is False
    assert result["account_id_used"] is False
    assert result["network_calls"] is False
    assert result["live_order_submitted"] is False
    assert result["runtime_file_written"] is False


def test_bundle_is_deterministic_for_same_input_and_timestamp():
    timestamp = 1_700_001_000.0
    first = bundle.run_demo_rehearsal_evidence_bundle(timestamp=timestamp)
    second = bundle.run_demo_rehearsal_evidence_bundle(timestamp=timestamp)
    assert first["bundle_id"] == second["bundle_id"]
    assert first["selected_candidate_ids"] == second["selected_candidate_ids"]
    assert first["decision"] == second["decision"]
    assert first["blockers"] == second["blockers"]


def test_bad_market_input_returns_blockers_without_crashing():
    result = bundle.run_demo_rehearsal_evidence_bundle(market_snapshot={"pair": "", "bid": None})
    assert result["allowed"] is False
    assert result["decision"] == "REHEARSAL_EVIDENCE_BLOCKED"
    assert result["blockers"]
    assert result["next_action"] == "resolve_demo_rehearsal_blockers_before_review"


def test_source_scan_no_dangerous_runtime_behavior():
    source = inspect.getsource(bundle)
    banned = (
        "requests",
        "socket",
        "urllib",
        "subprocess",
        "open(",
        "write_text",
        "write_bytes",
        "os.environ",
        "getenv(",
        "broker_sdk",
    )
    for token in banned:
        assert token not in source

