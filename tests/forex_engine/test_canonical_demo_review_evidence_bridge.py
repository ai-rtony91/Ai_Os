from __future__ import annotations

from datetime import datetime, timedelta, timezone

from automation.forex_engine.canonical_demo_review_evidence_bridge import (
    BLOCKED_INCOMPLETE_EVIDENCE,
    DEMO_REVIEW_READY,
    PAPER_CONTINUE,
    REJECTED,
    BridgeThresholds,
    build_review_bundle,
)


BASE_THRESHOLD = BridgeThresholds()
NOW = datetime(2026, 6, 21, 12, 0, 0, tzinfo=timezone.utc)


def _fixture_for_c1_eur_buy() -> dict:
    return {
        "candidate_id": "c1-eur-buy",
        "strategy": "mean_reversion_gap",
        "pair": "EURUSD",
        "direction": "buy",
        "expectancy": 0.18,
        "profit_factor": 1.36,
        "max_drawdown": 0.08,
        "win_rate": 0.47,
        "sample_size": 58,
        "walk_forward_status": "pass",
        "paper_evidence_status": "passed",
        "mitigation_status": "not_worse",
        "replay_proof": True,
        "reconciliation_proof": True,
        "kill_switch_proof": True,
        "rollback_proof": True,
        "risk_proof": True,
        "demo_validation_proof": True,
        "freshness_proof": {
            "timestamp": NOW.isoformat(),
        },
    }


def test_complete_strong_candidate_returns_demo_review_ready():
    bundle = build_review_bundle(_fixture_for_c1_eur_buy())
    assert bundle["verdict"] == DEMO_REVIEW_READY
    assert not bundle["blockers"]
    assert bundle["next_safe_action"] == "Prepare demo-review packet with consolidated proof bundle."


def test_positive_expectancy_small_sample_returns_paper_continue():
    candidate = _fixture_for_c1_eur_buy()
    candidate["sample_size"] = 8
    bundle = build_review_bundle(candidate)
    assert bundle["verdict"] == PAPER_CONTINUE
    assert "minimum" in bundle["next_safe_action"]
    assert bundle["metrics"]["sample_size"] == 8


def test_negative_expectancy_returns_rejected():
    candidate = _fixture_for_c1_eur_buy()
    candidate["expectancy"] = -0.02
    bundle = build_review_bundle(candidate)
    assert bundle["verdict"] == REJECTED
    assert any("expectancy" in item for item in bundle["blockers"])
    assert "Re-run with re-optimized signals" not in bundle["next_safe_action"]


def test_low_profit_factor_returns_rejected():
    candidate = _fixture_for_c1_eur_buy()
    candidate["profit_factor"] = 0.98
    bundle = build_review_bundle(candidate)
    assert bundle["verdict"] == REJECTED
    assert any("profit_factor_below_minimum" in item for item in bundle["blockers"])


def test_excessive_drawdown_returns_rejected():
    candidate = _fixture_for_c1_eur_buy()
    candidate["max_drawdown"] = 0.22
    bundle = build_review_bundle(candidate)
    assert bundle["verdict"] == REJECTED
    assert any("excessive_drawdown" in item for item in bundle["blockers"])


def test_missing_replay_proof_blocks():
    candidate = _fixture_for_c1_eur_buy()
    candidate["replay_proof"] = None
    bundle = build_review_bundle(candidate)
    assert bundle["verdict"] == BLOCKED_INCOMPLETE_EVIDENCE
    assert "missing_replay_proof" in bundle["blockers"]


def test_missing_reconciliation_proof_blocks():
    candidate = _fixture_for_c1_eur_buy()
    candidate["reconciliation_proof"] = None
    bundle = build_review_bundle(candidate)
    assert bundle["verdict"] == BLOCKED_INCOMPLETE_EVIDENCE
    assert "missing_reconciliation_proof" in bundle["blockers"]


def test_missing_kill_switch_proof_blocks():
    candidate = _fixture_for_c1_eur_buy()
    candidate["kill_switch_proof"] = None
    bundle = build_review_bundle(candidate)
    assert bundle["verdict"] == BLOCKED_INCOMPLETE_EVIDENCE
    assert "missing_kill_switch_proof" in bundle["blockers"]


def test_missing_rollback_proof_blocks():
    candidate = _fixture_for_c1_eur_buy()
    candidate["rollback_proof"] = None
    bundle = build_review_bundle(candidate)
    assert bundle["verdict"] == BLOCKED_INCOMPLETE_EVIDENCE
    assert "missing_rollback_proof" in bundle["blockers"]


def test_stale_freshness_proof_blocks():
    candidate = _fixture_for_c1_eur_buy()
    candidate["freshness_proof"] = {
        "timestamp": (NOW - timedelta(hours=33)).isoformat(),
    }
    bundle = build_review_bundle(candidate)
    assert bundle["verdict"] == BLOCKED_INCOMPLETE_EVIDENCE
    assert "stale_freshness_or_missing" in bundle["blockers"]


def test_failed_walk_forward_returns_rejected_or_continue_based_on_severity():
    candidate = _fixture_for_c1_eur_buy()
    candidate["walk_forward_status"] = "failed"
    bundle = build_review_bundle(candidate)
    assert bundle["verdict"] == REJECTED
    assert "walk_forward_failed" in bundle["blockers"]

    candidate["walk_forward_status"] = "weak"
    bundle = build_review_bundle(candidate)
    assert bundle["verdict"] == PAPER_CONTINUE
    assert "walk-forward" in bundle["walk_forward_detail"] or "walk_forward" in bundle["walk_forward_detail"] or "walk_forward" in bundle["next_safe_action"]


def test_alias_metric_names_normalize_correctly():
    candidate = {
        "candidate_id": "alias-case",
        "expected_value": 0.32,
        "pf": 1.5,
        "drawdown": 0.03,
        "winrate": 0.52,
        "total_trades": 40,
        "walkforward_status": "pass",
        "replay": True,
        "reconciliation": True,
        "kill_switch": True,
        "rollback": True,
        "risk": True,
        "demo_validation": True,
        "freshness": {
            "timestamp": NOW.isoformat(),
        },
        "paper_evidence_status": "passed",
        "mitigation_status": "not_worse",
    }
    bundle = build_review_bundle(candidate)
    assert bundle["metrics"]["expectancy"] == 0.32
    assert bundle["metrics"]["profit_factor"] == 1.5
    assert bundle["metrics"]["max_drawdown"] == 0.03
    assert bundle["metrics"]["win_rate"] == 0.52
    assert bundle["metrics"]["sample_size"] == 40
    assert bundle["metrics"]["walk_forward_status"] == "pass"


def test_c1_eur_buy_fixture_expected_verdict_deterministic():
    bundle = build_review_bundle(_fixture_for_c1_eur_buy(), BASE_THRESHOLD)
    assert bundle["candidate_id"] == "c1-eur-buy"
    assert bundle["verdict"] == DEMO_REVIEW_READY
    assert bundle["metrics"]["expectancy"] == 0.18


def test_bundle_includes_stable_keys():
    bundle = build_review_bundle(_fixture_for_c1_eur_buy())
    expected_keys = {
        "candidate_id",
        "strategy",
        "pair",
        "direction",
        "verdict",
        "blockers",
        "next_safe_action",
        "metrics",
        "proofs",
        "thresholds",
    }
    assert expected_keys.issubset(set(bundle.keys()))
