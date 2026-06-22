import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey


def test_review_chain_end_to_end_candidate_journey_uses_module_bridge_wrapper(monkeypatch):
    calls = {}

    def fake_bridge(*, write_reports: bool = False, proof_bundle_payload=None):
        calls["write_reports"] = write_reports
        return {
            "mode": "LOCAL_APPLY",
            "packet_id": "AIOS_TEST",
            "safety": {"is_safe": True, "safety_gaps": []},
            "selected_candidate_id": "c1-eur-buy",
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
                "walk_forward_status": "passed",
                "paper_evidence_status": "ready",
                "mitigation_status": "mitigated",
                "expectancy": 0.8,
                "profit_factor": 2.1,
                "max_drawdown": 0.08,
                "win_rate": 0.64,
                "sample_size": 220,
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
                    "walk_forward_status": "passed",
                    "paper_evidence_status": "ready",
                    "mitigation_status": "mitigated",
                    "expectancy": 0.8,
                    "profit_factor": 2.1,
                    "max_drawdown": 0.08,
                    "win_rate": 0.64,
                    "sample_size": 220,
                },
                "verdict": "PAPER_CONTINUE",
                "blockers": [
                    "walk_forward_failed",
                    "paper_evidence_not_ready",
                    "mitigation_worsened",
                ],
                "next_safe_action": "collect_demo_validation_contract",
            },
            "next_safe_action": "collect_demo_validation_contract",
        }

    monkeypatch.setattr(journey, "run_proof_bundle_to_candidate_bridge", fake_bridge)

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

    def fake_orchestrator(state):
        return {
            "verdict": journey.JOURNEY_READY,
            "final_state": journey.JOURNEY_READY,
            "blockers": [],
            "next_safe_action": "review_chain_complete",
        }

    if hasattr(journey.review_chain_orchestrator, "orchestrate_forex_review_chain"):
        monkeypatch.setattr(journey.review_chain_orchestrator, "orchestrate_forex_review_chain", fake_orchestrator)
    else:
        monkeypatch.setattr(journey.review_chain_orchestrator, "run_review_chain_orchestrator", fake_orchestrator)

    result = journey.run_review_chain_end_to_end_candidate_journey("c1-eur-buy", write_reports=False)

    assert result["final_state"] == journey.JOURNEY_READY
    assert result["candidate_journey_state"] == journey.JOURNEY_READY
    assert result["demo_validation_contract"]["blockers"] == []
    assert result["one_shot_exception_package"]["blockers"] == []
    assert result["live_review_readiness_certificate"]["blockers"] == []
    assert calls["write_reports"] is False
    assert result["live_trading_authorized"] is False


def test_bridge_api_exports():
    assert journey.JOURNEY_INCOMPLETE == "REVIEW_CHAIN_INCOMPLETE"
    assert journey.JOURNEY_REVIEW_READY == journey.JOURNEY_READY
    assert hasattr(journey, "candidate_intake_demo_review_bridge")
    assert hasattr(journey, "review_chain_orchestrator")
    assert callable(journey.build_review_chain_state)
    assert callable(journey.run_proof_bundle_to_candidate_bridge)
