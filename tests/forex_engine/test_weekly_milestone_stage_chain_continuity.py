import types

import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey
from automation.forex_engine.review_chain_end_to_end_candidate_journey import (
    JOURNEY_ERROR,
    JOURNEY_FAILED,
    JOURNEY_INCOMPLETE,
    JOURNEY_READY,
    JOURNEY_REJECTED,
    JOURNEY_REVIEW_READY,
    run_review_chain_end_to_end_candidate_journey,
)


def test_weekly_milestone_continuity_produces_readiness_artifacts(monkeypatch):
    monkeypatch.setattr(
        journey,
        "run_proof_bundle_to_candidate_bridge",
        lambda *_, **__: {
            "mode": "LOCAL_APPLY",
            "packet_id": "AIOS_TEST",
            "safety": {"is_safe": True, "safety_gaps": []},
            "selected_candidate_id": "c1-eur-buy",
            "selected_strategy": "ema_mean_reversion",
            "selected_direction": "buy",
            "source_proof_bundle_status": "PROOF_BUNDLE_COMPLETE",
            "source_candidate_verdict": "PAPER_CONTINUE",
            "candidate_bridge_verdict": "PAPER_CONTINUE",
            "proof_bundle_ready_for_candidate_bridge": True,
            "closed_blockers": [
                "missing_replay_proof",
                "missing_reconciliation_proof",
                "missing_rollback_proof",
                "missing_demo_validation_proof",
            ],
            "enriched_candidate": {
                "candidate_id": "c1-eur-buy",
                "strategy": "ema_mean_reversion",
                "pair": "EURUSD",
                "direction": "buy",
                "expectancy": 0.65,
                "profit_factor": 2.1,
                "max_drawdown": 0.05,
                "win_rate": 0.58,
                "sample_size": 320,
                "walk_forward_status": "passed",
                "paper_evidence_status": "ready",
                "mitigation_status": "mitigated",
                "replay_proof": True,
                "reconciliation_proof": True,
                "rollback_proof": True,
                "demo_validation_proof": True,
                "kill_switch_proof": True,
                "risk_proof": True,
                "freshness_proof": {"age_hours": 1},
            },
            "canonical_review_bundle": {
                "candidate": {
                    "candidate_id": "c1-eur-buy",
                    "strategy": "ema_mean_reversion",
                    "pair": "EURUSD",
                    "direction": "buy",
                    "expectancy": 0.65,
                    "profit_factor": 2.1,
                    "max_drawdown": 0.05,
                    "win_rate": 0.58,
                    "sample_size": 320,
                    "walk_forward_status": "passed",
                    "paper_evidence_status": "ready",
                    "mitigation_status": "mitigated",
                },
                "verdict": "PAPER_CONTINUE",
                "blockers": [
                    "walk_forward_failed",
                    "paper_evidence_not_ready",
                ],
                "safety_gaps": [],
                "next_safe_action": "collect_demo_validation_contract",
            },
            "canonical_review_bundle_ready": True,
            "next_safe_action": "collect_demo_validation_contract",
        },
    )

    monkeypatch.setattr(
        journey,
        "evaluate_demo_validation_contract",
        lambda state: {
            "demo_validation_contract_status": "COMPLETE",
            "demo_validation_contract_completed": True,
            "blockers": [],
            "next_safe_action": "assemble_one_shot_exception_package",
            "safety_gaps": [],
        },
    )
    monkeypatch.setattr(
        journey,
        "assemble_one_shot_exception_package",
        lambda state: {
            "exception_package_status": "READY",
            "exception_package_completed": True,
            "blockers": [],
            "live_micro_trade_review_ready": True,
            "next_safe_action": "generate_live_review_readiness_certificate",
            "safety_gaps": [],
        },
    )
    monkeypatch.setattr(
        journey,
        "generate_live_review_readiness_certificate",
        lambda state: {
            "certificate_status": "READY",
            "certificate_completed": True,
            "blockers": [],
            "safety_gaps": [],
            "human_live_review_ready": False,
            "next_safe_action": "run_review_chain",
        },
    )
    monkeypatch.setattr(
        journey.review_chain_orchestrator,
        "orchestrate_forex_review_chain",
        lambda state: {
            "verdict": JOURNEY_READY,
            "final_state": JOURNEY_READY,
            "blockers": ["walk_forward_failed", "paper_evidence_not_ready"],
            "next_safe_action": "review_chain_continuity_complete",
        },
    )

    result = run_review_chain_end_to_end_candidate_journey(candidate_id="c1-eur-buy", write_reports=False)

    assert result["selected_candidate_id"] == "c1-eur-buy"
    assert result["enriched_candidate"]["candidate_id"] == "c1-eur-buy"
    assert result["final_state"] == JOURNEY_READY
    assert result["candidate_journey_state"] == JOURNEY_READY
    assert result["demo_validation_contract"]["blockers"] == []
    assert result["one_shot_exception_package"]["blockers"] == []
    assert result["live_review_readiness_certificate"]["blockers"] == []
    assert "missing_demo_validation_contract" not in result["remaining_blockers"]
    assert "missing_one_shot_exception_package" not in result["remaining_blockers"]
    assert "missing_live_review_readiness_certificate" not in result["remaining_blockers"]
    assert result["live_trading_authorized"] is False


def test_stage_chain_compatibility_constants():
    assert JOURNEY_REVIEW_READY == JOURNEY_READY
    assert JOURNEY_INCOMPLETE == "REVIEW_CHAIN_INCOMPLETE"
    assert JOURNEY_ERROR == "REVIEW_ERROR"
    assert JOURNEY_REJECTED == "REVIEW_REJECTED"
    assert JOURNEY_FAILED == "REVIEW_FAILED"
    assert isinstance(run_review_chain_end_to_end_candidate_journey, types.FunctionType)
