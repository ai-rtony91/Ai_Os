from __future__ import annotations

from pathlib import Path

from automation.forex_engine.consolidated_readiness_blocker_closure_v1 import (
    CANONICAL_BLOCKERS,
    run_consolidated_readiness_blocker_closure_v1,
)


def _base_payload():
    return {
        "candidate": {
            "candidate_id": "c1-eur-buy",
            "strategy_name": "ema_mean_reversion",
            "pair": "EURUSD",
            "direction": "buy",
            "walk_forward_status": "passed",
            "mitigation_status": "improved",
        },
        "paper_metrics": {
            "total_trades": 120,
            "closed_trades": 120,
            "win_rate": 0.61,
            "expectancy": 0.12,
            "profit_factor": 1.8,
            "max_drawdown": 0.05,
            "risk_of_ruin": 0.01,
            "risk_adjusted_return": 0.20,
            "sample_size": 120,
        },
        "walk_forward_status": "passed",
        "validation_results": [{"id": "v1"}],
        "validation_payload": {"status": "PASS"},
        "candidate_approved_for_demo_validation": True,
        "demo_validation_contract": {"demo_validation_contract_completed": True, "status": "COMPLETE"},
        "live_readiness_candidate": {"candidate_id": "c1-eur-buy", "live_ready": True},
        "approval_trace": {"signed": True, "reviewed_by": "review_lead"},
        "risk_limits": {"max_drawdown_limit": 0.10},
        "kill_switch_proof": {"status": "PASS", "timestamp": "2026-06-22T00:00:00+00:00"},
        "rollback_proof": {"status": "PASS"},
        "reconciliation_proof": {"status": "PASS"},
        "evidence_timestamp": "2026-06-22T01:00:00+00:00",
        "replayability_proof": {"status": "PASS"},
        "final_disarm_proof": {"status": "PASS"},
        "post_trade_journal_path": "/tmp/post_trade_journal.csv",
        "one_shot_exception_package": {"exception_package_completed": True},
        "live_review_certificate": {"certificate_completed": True},
        "human_review_ready": True,
    }


def _full_demo_ready_payload():
    payload = _base_payload()
    payload["validation_results"] = [{"status": "PASS"}]
    return payload


def _full_live_ready_payload():
    payload = _full_demo_ready_payload()
    payload["live_readiness_candidate"] = {"live_ready": True}
    return payload


def test_empty_evidence_blocked():
    payload = run_consolidated_readiness_blocker_closure_v1(evidence_payload={}, write_reports=False)
    assert payload["status"] == "BLOCKED"
    assert payload["decision"] == "blocked"
    assert payload["blockers"]


def test_walk_forward_failed_blocker():
    payload = _base_payload()
    payload["walk_forward_status"] = "failed"
    payload["candidate"]["walk_forward_status"] = "failed"
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "walk_forward_failed" in result["unresolved_blockers"]


def test_missing_paper_metrics_blocker():
    payload = _base_payload()
    payload["paper_metrics"] = {"sample_size": 12}
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "paper_evidence_not_ready" in result["unresolved_blockers"]


def test_negative_expectancy_blocker():
    payload = _base_payload()
    payload["paper_metrics"]["expectancy"] = -0.01
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "paper_evidence_not_ready" in result["unresolved_blockers"]


def test_low_profit_factor_blocker():
    payload = _base_payload()
    payload["paper_metrics"]["profit_factor"] = 1.0
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "paper_evidence_not_ready" in result["unresolved_blockers"]


def test_missing_validation_results_blocker():
    payload = _base_payload()
    payload["validation_results"] = []
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "missing_validation_results" in result["unresolved_blockers"]


def test_candidate_not_approved_blocker():
    payload = _base_payload()
    payload["candidate_approved_for_demo_validation"] = False
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "candidate_not_approved_for_demo_validation" in result["unresolved_blockers"]


def test_demo_contract_not_complete_blocker():
    payload = _base_payload()
    payload["demo_validation_contract"] = {"status": "PENDING"}
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "demo_contract_not_complete" in result["unresolved_blockers"]
    assert "demo_validation_contract_not_complete" in result["unresolved_blockers"]


def test_missing_live_readiness_candidate_blocker():
    payload = _base_payload()
    payload["live_readiness_candidate"] = {}
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "missing_live_readiness_candidate" in result["unresolved_blockers"]


def test_missing_approval_trace_blocker():
    payload = _base_payload()
    payload.pop("approval_trace")
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "missing_approval_trace" in result["unresolved_blockers"]


def test_missing_risk_limits_blocker():
    payload = _base_payload()
    payload["risk_limits"] = {}
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "missing_risk_limits" in result["unresolved_blockers"]


def test_missing_kill_switch_proof_blocker():
    payload = _base_payload()
    payload["kill_switch_proof"] = None
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "missing_kill_switch_proof" in result["unresolved_blockers"]


def test_missing_rollback_proof_blocker():
    payload = _base_payload()
    payload["rollback_proof"] = None
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "missing_rollback_proof" in result["unresolved_blockers"]


def test_missing_reconciliation_proof_blocker():
    payload = _base_payload()
    payload["reconciliation_proof"] = None
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "missing_reconciliation_proof" in result["unresolved_blockers"]


def test_missing_freshness_blocker():
    payload = _base_payload()
    payload["evidence_timestamp"] = "2025-01-01T00:00:00+00:00"
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "missing_evidence_freshness" in result["unresolved_blockers"]


def test_missing_replayability_blocker():
    payload = _base_payload()
    payload["replayability_proof"] = None
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "missing_replayability_proof" in result["unresolved_blockers"]


def test_missing_final_disarm_proof_blocker():
    payload = _base_payload()
    payload["final_disarm_proof"] = None
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "missing_final_disarm_proof" in result["unresolved_blockers"]


def test_missing_post_trade_journal_path_blocker():
    payload = _base_payload()
    payload["post_trade_journal_path"] = ""
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "missing_post_trade_journal_path" in result["unresolved_blockers"]


def test_missing_one_shot_package_blocker():
    payload = _base_payload()
    payload["one_shot_exception_package"] = {"exception_package_completed": False}
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "one_shot_exception_package_not_review_ready" in result["unresolved_blockers"]


def test_missing_live_review_certificate_blocker():
    payload = _base_payload()
    payload["live_review_certificate"] = {"certificate_completed": False}
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "live_review_certificate_not_review_ready" in result["unresolved_blockers"]


def test_missing_human_review_ready_blocker():
    payload = _base_payload()
    payload["human_review_ready"] = False
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "missing_human_review_ready" in result["unresolved_blockers"]


def test_mitigation_worsened_blocker():
    payload = _base_payload()
    payload["candidate"]["mitigation_status"] = "worsened"
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert "mitigation_worsened" in result["unresolved_blockers"]


def test_demo_evidence_clears_demo_only():
    payload = _full_demo_ready_payload()
    payload["live_readiness_candidate"] = {}
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert result["ready_for_demo_validation"] is True
    assert result["ready_for_live_review"] is False


def test_full_live_readiness_evidence_clears_live_blockers():
    payload = _full_live_ready_payload()
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy", evidence_payload=payload, write_reports=False
    )
    assert result["ready_for_demo_validation"] is True
    assert result["ready_for_live_review"] is True
    assert result["status"] == "READY"
    assert result["unresolved_blockers"] == []


def test_blocker_constants_are_stable():
    required = {
        "walk_forward_failed",
        "paper_evidence_not_ready",
        "mitigation_worsened",
        "missing_validation_results",
        "candidate_not_approved_for_demo_validation",
        "demo_contract_not_complete",
        "missing_live_readiness_candidate",
        "missing_approval_trace",
        "missing_risk_limits",
        "missing_kill_switch_proof",
        "missing_rollback_proof",
        "missing_reconciliation_proof",
        "missing_evidence_freshness",
        "missing_replayability_proof",
        "missing_final_disarm_proof",
        "missing_post_trade_journal_path",
        "demo_validation_contract_not_complete",
        "one_shot_exception_package_not_review_ready",
        "live_review_certificate_not_review_ready",
        "missing_human_review_ready",
    }
    assert set(CANONICAL_BLOCKERS) >= required


def test_payload_stable_blocker_keys_and_ready_live_auth_false():
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy",
        evidence_payload=_full_live_ready_payload(),
        write_reports=False,
    )
    assert result["safety"]["paper_only"] is True
    assert result["safety"]["live_trading_authorized"] is False
    assert "unresolved_blockers" in result
    assert "resolved_blockers" in result
    assert "blocker_details" in result


def test_report_path_under_reports():
    payload = _base_payload()
    result = run_consolidated_readiness_blocker_closure_v1(
        candidate_id="c1-eur-buy",
        evidence_payload=payload,
        write_reports=True,
    )
    report_path = Path(result["report_path"])
    assert "Reports/forex_delivery" in report_path.as_posix()
    assert report_path.name.endswith(".md") or report_path.name.endswith(".json")
