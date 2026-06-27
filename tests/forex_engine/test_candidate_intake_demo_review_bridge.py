from __future__ import annotations

from pathlib import Path

from automation.forex_engine import candidate_intake_demo_review_bridge as module
from automation.forex_engine import canonical_demo_review_evidence_bridge as canonical_bridge


def _assert_valid_verdict(verdict: str) -> None:
    assert verdict in {
        canonical_bridge.DEMO_REVIEW_READY,
        canonical_bridge.PAPER_CONTINUE,
        canonical_bridge.REJECTED,
        canonical_bridge.BLOCKED_INCOMPLETE_EVIDENCE,
    }



def _valid_canonical_candidate() -> dict:
    return {
        "candidate_id": "test-candidate",
        "strategy": "paper_test_strategy",
        "pair": "EURUSD",
        "direction": "LONG",
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
        "freshness_proof": {"age_hours": 1},
    }


def _valid_proofs_only() -> dict:
    candidate = _valid_canonical_candidate()
    return {
        key: candidate[key]
        for key in (
            "replay_proof",
            "reconciliation_proof",
            "kill_switch_proof",
            "rollback_proof",
            "risk_proof",
            "demo_validation_proof",
            "freshness_proof",
        )
    }

def test_safety_flags():
    safety = module._safety()
    assert safety["paper_only"] is True
    assert safety["broker_connected"] is False
    assert safety["credentials_used"] is False
    assert safety["network_used"] is False
    assert safety["order_execution"] is False
    assert safety["demo_trading"] is False
    assert safety["live_trading"] is False


def test_intake_returns_expected_top_level_keys():
    payload = module.build_candidate_intake_payload()
    required = {
        "mode",
        "packet_id",
        "safety",
        "selected_candidate_id",
        "selected_strategy",
        "selected_direction",
        "selection_reason",
        "discovery_summary",
        "mitigation_summary",
        "normalized_candidate",
        "demo_review_bundle",
        "verdict",
        "blockers",
        "next_safe_action",
    }
    assert required.issubset(payload.keys())


def test_selected_candidate_id_stable_non_empty():
    payload = module.build_candidate_intake_payload()
    assert isinstance(payload["selected_candidate_id"], str)
    assert payload["selected_candidate_id"]


def test_normalized_candidate_has_canonical_metric_keys():
    payload = module.build_candidate_intake_payload()
    candidate = payload["normalized_candidate"]
    assert candidate["candidate_id"] == payload["selected_candidate_id"]
    assert candidate["strategy"]
    assert candidate["pair"]
    assert candidate["direction"]
    assert "expectancy" in candidate
    assert "profit_factor" in candidate
    assert "max_drawdown" in candidate
    assert "win_rate" in candidate
    assert "sample_size" in candidate
    assert "walk_forward_status" in candidate
    assert "paper_evidence_status" in candidate
    assert "mitigation_status" in candidate


def test_normalized_candidate_includes_proof_keys():
    payload = module.build_candidate_intake_payload()
    candidate = payload["normalized_candidate"]
    for key in [
        "replay_proof",
        "reconciliation_proof",
        "kill_switch_proof",
        "rollback_proof",
        "risk_proof",
        "demo_validation_proof",
        "freshness_proof",
    ]:
        assert key in candidate


def test_demo_review_bundle_exists_and_has_verdict():
    payload = module.build_candidate_intake_payload()
    bundle = payload["demo_review_bundle"]
    assert bundle["candidate_id"] == payload["selected_candidate_id"]
    assert bundle["verdict"] in {
        canonical_bridge.DEMO_REVIEW_READY,
        canonical_bridge.PAPER_CONTINUE,
        canonical_bridge.REJECTED,
        canonical_bridge.BLOCKED_INCOMPLETE_EVIDENCE,
    }
    assert "blockers" in bundle
    assert "next_safe_action" in bundle


def test_verdict_is_valid_enum():
    payload = module.build_candidate_intake_payload()
    _assert_valid_verdict(payload["verdict"])


def test_no_broker_network_live_order_flags_true():
    payload = module.build_candidate_intake_payload()
    safety = payload["safety"]
    assert safety["broker_connected"] is False
    assert safety["network_used"] is False
    assert safety["order_execution"] is False
    assert safety["demo_trading"] is False
    assert safety["live_trading"] is False
    assert safety["paper_only"] is True


def test_write_reports_disabled_returns_no_report_field():
    payload = module.run_candidate_intake_demo_review_bridge(write_reports=False)
    assert payload["report"] is None
    assert Path("Reports/forex_delivery").exists()


def test_write_reports_enabled_writes_report_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    payload = module.run_candidate_intake_demo_review_bridge(write_reports=True)
    report = payload["report"]
    assert isinstance(report, str)
    assert report.endswith("AIOS_FOREX_CANDIDATE_INTAKE_DEMO_REVIEW_BRIDGE_V1_REPORT.md")
    assert Path(report).exists()


def test_anchor_candidate_is_traceable_in_summaries():
    payload = module.build_candidate_intake_payload()
    summary = payload["discovery_summary"]
    assert summary["anchor_candidate_id"] == "c1-eur-buy"


def test_missing_required_proof_blocks_verdict(monkeypatch):
    def _missing_replay(*_: object, **kwargs: object) -> dict[str, bool | dict[str, object]]:
        return {
            "replay_proof": False,
            "reconciliation_proof": True,
            "kill_switch_proof": True,
            "rollback_proof": True,
            "risk_proof": True,
            "demo_validation_proof": True,
            "freshness_proof": {"timestamp": "2026-06-21T12:00:00Z"},
        }

    monkeypatch.setattr(module, "build_internal_proofs", _missing_replay)
    rebuilt = module.build_candidate_intake_payload()
    assert rebuilt["verdict"] == canonical_bridge.BLOCKED_INCOMPLETE_EVIDENCE


def test_negative_expectancy_rejects(monkeypatch):
    def _force_negative_expectancy(selected, discovery_payload, mitigation_payload):
        candidate = _valid_canonical_candidate()
        candidate["expectancy"] = -0.45
        return candidate

    def _valid_proofs(selected, discovery_payload, mitigation_payload):
        return _valid_proofs_only()

    monkeypatch.setattr(module, "normalize_selected_candidate", _force_negative_expectancy)
    monkeypatch.setattr(module, "build_internal_proofs", _valid_proofs)

    payload = module.build_candidate_intake_payload()

    assert payload["verdict"] == canonical_bridge.REJECTED


def test_small_sample_positive_expectancy_continues(monkeypatch):
    def _force_small_sample(selected, discovery_payload, mitigation_payload):
        candidate = _valid_canonical_candidate()
        candidate["expectancy"] = 0.22
        candidate["profit_factor"] = 1.36
        candidate["max_drawdown"] = 0.08
        candidate["win_rate"] = 0.47
        candidate["sample_size"] = 10
        candidate["walk_forward_status"] = "pass"
        candidate["paper_evidence_status"] = "passed"
        candidate["mitigation_status"] = "not_worse"
        return candidate

    def _valid_proofs(selected, discovery_payload, mitigation_payload):
        return _valid_proofs_only()

    monkeypatch.setattr(module, "normalize_selected_candidate", _force_small_sample)
    monkeypatch.setattr(module, "build_internal_proofs", _valid_proofs)

    payload = module.build_candidate_intake_payload()

    assert payload["verdict"] == canonical_bridge.PAPER_CONTINUE
