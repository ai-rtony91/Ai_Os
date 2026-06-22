from __future__ import annotations

from pathlib import Path
from typing import Any

import automation.forex_engine.proof_gap_closure_plan as module


def _journey_payload(
    candidate_blockers: list[str] | None = None,
    chain_blockers: list[str] | None = None,
    *,
    verdict: str = "PAPER_CONTINUE",
    review_chain_status: str = "REVIEW_CHAIN_INCOMPLETE",
    final_verdict: str = "JOURNEY_INCOMPLETE",
    safety_override: dict[str, bool] | None = None,
) -> dict[str, Any]:
    return {
        "selected_candidate_id": "c1-eur-buy",
        "selected_strategy": "ema_rsi",
        "selected_direction": "LONG",
        "candidate_demo_review_verdict": verdict,
        "candidate_demo_review_blockers": candidate_blockers or [],
        "review_chain_status": review_chain_status,
        "review_chain_blockers": chain_blockers or [],
        "final_verdict": final_verdict,
        "final_next_safe_action": "continue",
        "safety": {
            "paper_only": True,
            "broker_connected": False,
            "credentials_used": False,
            "account_id_present": False,
            "network_used": False,
            "order_execution": False,
            "demo_trading": False,
            "live_trading": False,
            **(safety_override or {}),
        },
    }


def _safe_module(monkeypatch: Any, payload: dict[str, Any]) -> None:
    def fake_run(*, write_reports: bool = True) -> dict[str, Any]:
        return payload

    monkeypatch.setattr(module.review_chain_end_to_end_candidate_journey, "run_review_chain_end_to_end_candidate_journey", fake_run)


def test_stable_top_level_keys(monkeypatch: Any) -> None:
    payload = _journey_payload()
    _safe_module(monkeypatch, payload)
    result = module.run_proof_gap_closure_plan(write_reports=False)
    expected = {
        "mode",
        "packet_id",
        "safety",
        "source_journey_final_verdict",
        "source_candidate_verdict",
        "source_review_chain_status",
        "selected_candidate_id",
        "selected_strategy",
        "selected_direction",
        "normalized_blockers",
        "closure_buckets",
        "recommended_packet_sequence",
        "highest_value_next_packet",
        "blocked_for_demo_review",
        "blocked_for_live_review",
        "next_safe_action",
    }
    assert expected.issubset(set(result.keys()))


def test_evidence_gap_buckets_and_sequence(monkeypatch: Any) -> None:
    payload = _journey_payload(
        candidate_blockers=["missing_replay_proof", "missing_reconciliation_proof"],
    )
    _safe_module(monkeypatch, payload)
    result = module.run_proof_gap_closure_plan(write_reports=False)
    assert result["highest_value_next_packet"] == module.PROOF_PACKET_ID
    assert result["closure_buckets"]["evidence_proof_gaps"]
    assert result["recommended_packet_sequence"][0]["packet_id"] == module.PROOF_PACKET_ID


def test_replay_reconciliation_rollback_demo_validation_gaps_map_to_proof_packet(monkeypatch: Any) -> None:
    payload = _journey_payload(
        chain_blockers=[
            "missing_replay_proof",
            "missing_reconciliation_proof",
            "missing_rollback_proof",
            "missing_demo_validation_proof",
        ],
    )
    _safe_module(monkeypatch, payload)
    result = module.run_proof_gap_closure_plan(write_reports=False)
    assert result["highest_value_next_packet"] == module.PROOF_PACKET_ID


def test_walk_forward_paper_evidence_mitigation_gaps_map_to_evidence_repair(monkeypatch: Any) -> None:
    payload = _journey_payload(
        chain_blockers=["walk_forward_failed", "paper_evidence_not_ready", "mitigation_worsened"],
    )
    _safe_module(monkeypatch, payload)
    result = module.run_proof_gap_closure_plan(write_reports=False)
    assert result["highest_value_next_packet"] == module.EVIDENCE_PACKET_ID


def test_missing_demo_validation_contract_maps_to_demo_contract_packet(monkeypatch: Any) -> None:
    payload = _journey_payload(chain_blockers=["missing_demo_validation_contract"])
    _safe_module(monkeypatch, payload)
    result = module.run_proof_gap_closure_plan(write_reports=False)
    assert result["highest_value_next_packet"] == module.DEMO_CONTRACT_PACKET_ID


def test_missing_one_shot_package_maps_to_one_shot_packet(monkeypatch: Any) -> None:
    payload = _journey_payload(chain_blockers=["missing_one_shot_exception_package"])
    _safe_module(monkeypatch, payload)
    result = module.run_proof_gap_closure_plan(write_reports=False)
    assert result["highest_value_next_packet"] == module.ONE_SHOT_PACKET_ID


def test_missing_certificate_maps_to_certificate_packet(monkeypatch: Any) -> None:
    payload = _journey_payload(chain_blockers=["missing_live_review_readiness_certificate"])
    _safe_module(monkeypatch, payload)
    result = module.run_proof_gap_closure_plan(write_reports=False)
    assert result["highest_value_next_packet"] == module.CERTIFICATE_PACKET_ID


def test_missing_human_review_ready_maps_to_human_handoff_packet(monkeypatch: Any) -> None:
    payload = _journey_payload(chain_blockers=["missing_human_review_ready"])
    _safe_module(monkeypatch, payload)
    result = module.run_proof_gap_closure_plan(write_reports=False)
    assert result["highest_value_next_packet"] == module.HUMAN_PACKET_ID


def test_safety_gap_overrides_all_priorities(monkeypatch: Any) -> None:
    payload = _journey_payload(
        candidate_blockers=["missing_replay_proof"],
        safety_override={"broker_connected": True},
    )
    _safe_module(monkeypatch, payload)
    result = module.run_proof_gap_closure_plan(write_reports=False)
    assert result["highest_value_next_packet"] == module.SAFETY_PACKET_ID
    assert result["blocked_for_demo_review"] is True
    assert result["blocked_for_live_review"] is True


def test_no_blockers_returns_no_gap_detected(monkeypatch: Any) -> None:
    payload = _journey_payload(chain_blockers=[], candidate_blockers=[])
    _safe_module(monkeypatch, payload)
    result = module.run_proof_gap_closure_plan(write_reports=False)
    assert result["highest_value_next_packet"] == module.NO_GAP_DETECTED
    assert result["recommended_packet_sequence"] == []


def test_recommended_packet_sequence_is_priority_ordered(monkeypatch: Any) -> None:
    payload = _journey_payload(
        chain_blockers=[
            "walk_forward_failed",
            "missing_demo_validation_contract",
            "missing_one_shot_exception_package",
            "missing_live_review_readiness_certificate",
            "missing_human_review_ready",
        ],
    )
    _safe_module(monkeypatch, payload)
    result = module.run_proof_gap_closure_plan(write_reports=False)
    priorities = [entry["priority"] for entry in result["recommended_packet_sequence"]]
    assert priorities == sorted(priorities)


def test_highest_value_packet_respects_priority(monkeypatch: Any) -> None:
    payload = _journey_payload(
        chain_blockers=[
            "missing_human_review_ready",
            "missing_demo_validation_contract",
            "missing_one_shot_exception_package",
            "walk_forward_failed",
        ],
    )
    _safe_module(monkeypatch, payload)
    result = module.run_proof_gap_closure_plan(write_reports=False)
    assert result["highest_value_next_packet"] == module.EVIDENCE_PACKET_ID


def test_write_reports_false_has_no_report_path() -> None:
    payload = _journey_payload()
    assert module.run_proof_gap_closure_plan(journey_payload=payload, write_reports=False).get("report_path") is None


def test_write_reports_true_returns_report_path(monkeypatch: Any) -> None:
    payload = _journey_payload()
    _safe_module(monkeypatch, payload)
    result = module.run_proof_gap_closure_plan(write_reports=True)
    report = result.get("report_path")
    assert isinstance(report, str)
    path = Path(str(report))
    assert path.exists()
    assert path.is_file()
    assert str(path).replace("\\", "/").startswith("Reports/forex_delivery/")


def test_safety_flags_remain_paper_only_when_no_unsafe_flags(monkeypatch: Any) -> None:
    payload = _journey_payload()
    _safe_module(monkeypatch, payload)
    result = module.run_proof_gap_closure_plan(write_reports=False)
    safety = result["safety"]
    assert safety["paper_only"] is True
    assert safety["broker_connected"] is False
    assert safety["credentials_used"] is False
    assert safety["network_used"] is False
    assert safety["order_execution"] is False
    assert safety["demo_trading"] is False
    assert safety["live_trading"] is False
