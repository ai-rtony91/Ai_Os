from __future__ import annotations

from typing import Any

from automation.forex_engine import canonical_demo_review_evidence_bridge
from automation.forex_engine import review_chain_orchestrator
from pytest import MonkeyPatch


def _fake_candidate_payload(verdict: str, blockers: list[str] | None = None) -> dict[str, Any]:
    return {
        "mode": "TEST",
        "packet_id": "TEST",
        "selected_candidate_id": "c1-eur-buy",
        "selected_strategy": "ema_rsi",
        "selected_direction": "LONG",
        "selection_reason": "unit-test",
        "verdict": verdict,
        "blockers": blockers or [],
        "next_safe_action": "continue",
        "safety": {
            "paper_only": True,
            "broker_connected": False,
            "credentials_used": False,
            "account_id_present": False,
            "network_used": False,
            "order_execution": False,
            "demo_trading": False,
            "live_trading": False,
        },
        "demo_review_bundle": {"verdict": verdict, "blockers": blockers or []},
    }


def _fake_orchestrate_status(status: str, blockers: list[str] | None = None, *, safe: bool = False) -> dict[str, Any]:
    safety = {
        "broker_connection_active": safe,
        "network_access": safe,
        "credentials_accessed": safe,
        "account_identifiers_accessed": safe,
        "order_execution_enabled": safe,
        "live_trading_authorized": False,
        "execution_authority_granted": safe,
        "capital_allocated": safe,
    }
    return {
        "review_chain_status": status,
        "blockers": blockers or [],
        "next_safe_action": "next",
        "required_next_packets": ["collect_missing_chain_outputs"],
        "human_live_review_ready": False,
        "live_micro_trade_review_ready": False,
        "live_trading_authorized": False,
        "safety": safety,
    }


def test_stable_top_level_keys() -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey

    result = journey.run_review_chain_end_to_end_candidate_journey()
    for key in (
        "mode",
        "packet_id",
        "safety",
        "selected_candidate_id",
        "selected_strategy",
        "selected_direction",
        "candidate_selection_reason",
        "candidate_demo_review_verdict",
        "candidate_demo_review_blockers",
        "candidate_demo_review_next_safe_action",
        "review_chain_status",
        "review_chain_blockers",
        "review_chain_next_safe_action",
        "review_chain_required_next_packets",
        "human_live_review_ready",
        "live_micro_trade_review_ready",
        "live_trading_authorized",
        "journey_completed",
        "final_verdict",
        "final_next_safe_action",
        "source_modules",
    ):
        assert key in result


def test_safety_is_paper_only_and_no_live_flags() -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey

    result = journey.run_review_chain_end_to_end_candidate_journey()
    safety = result["safety"]
    assert safety["paper_only"] is True
    assert safety["broker_connected"] is False
    assert safety["credentials_used"] is False
    assert safety["network_used"] is False
    assert safety["order_execution"] is False
    assert safety["demo_trading"] is False
    assert safety["live_trading"] is False


def test_selected_candidate_id_non_empty() -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey

    result = journey.run_review_chain_end_to_end_candidate_journey()
    assert isinstance(result["selected_candidate_id"], str)
    assert result["selected_candidate_id"]


def test_candidate_verdict_enum_present() -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey

    result = journey.run_review_chain_end_to_end_candidate_journey()
    assert result["candidate_demo_review_verdict"] in {
        canonical_demo_review_evidence_bridge.DEMO_REVIEW_READY,
        canonical_demo_review_evidence_bridge.PAPER_CONTINUE,
        canonical_demo_review_evidence_bridge.REJECTED,
        canonical_demo_review_evidence_bridge.BLOCKED_INCOMPLETE_EVIDENCE,
    }


def test_review_chain_status_enum_present() -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey

    result = journey.run_review_chain_end_to_end_candidate_journey()
    assert result["review_chain_status"] in {
        review_chain_orchestrator.REVIEW_CHAIN_REVIEW_READY,
        review_chain_orchestrator.REVIEW_CHAIN_INCOMPLETE,
        review_chain_orchestrator.REVIEW_CHAIN_REJECTED,
        review_chain_orchestrator.REVIEW_CHAIN_BLOCKED,
    }


def test_final_verdict_enum_present() -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey

    result = journey.run_review_chain_end_to_end_candidate_journey()
    assert result["final_verdict"] in {
        journey.JOURNEY_REVIEW_READY,
        journey.JOURNEY_INCOMPLETE,
        journey.JOURNEY_REJECTED,
        journey.JOURNEY_BLOCKED,
    }


def test_live_trading_authorized_false() -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey

    result = journey.run_review_chain_end_to_end_candidate_journey()
    assert result["live_trading_authorized"] is False


def test_write_reports_false_no_report() -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey

    result = journey.run_review_chain_end_to_end_candidate_journey(write_reports=False)
    assert result.get("report") is None


def test_write_reports_true_reports_path() -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey

    result = journey.run_review_chain_end_to_end_candidate_journey(write_reports=True)
    assert isinstance(result.get("report"), str)
    assert str(result["report"]).replace("\\", "/").startswith("Reports/forex_delivery/")


def test_source_modules_listed() -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey

    result = journey.run_review_chain_end_to_end_candidate_journey()
    assert result["source_modules"] == [
        "automation/forex_engine/candidate_intake_demo_review_bridge.py",
        "automation/forex_engine/canonical_demo_review_evidence_bridge.py",
        "automation/forex_engine/review_chain_orchestrator.py",
    ]


def test_monkeypatch_demo_ready_and_orchestrator_ready_maps_to_journey_review_ready(monkeypatch: Any) -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey

    candidate_payload = _fake_candidate_payload(canonical_demo_review_evidence_bridge.DEMO_REVIEW_READY)
    monkeypatch.setattr(
        journey.candidate_intake_demo_review_bridge,
        "run_candidate_intake_demo_review_bridge",
        lambda write_reports: candidate_payload,
    )
    monkeypatch.setattr(
        journey.review_chain_orchestrator,
        "orchestrate_forex_review_chain",
        lambda state: _fake_orchestrate_status(
            review_chain_orchestrator.REVIEW_CHAIN_REVIEW_READY,
            ["candidate_blocked"],
        ),
    )
    result = journey.run_review_chain_end_to_end_candidate_journey()
    assert result["final_verdict"] == journey.JOURNEY_REVIEW_READY


def test_monkeypatch_candidate_continue_and_orchestrator_incomplete(monkeypatch: Any) -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey

    candidate_payload = _fake_candidate_payload(canonical_demo_review_evidence_bridge.PAPER_CONTINUE)
    monkeypatch.setattr(
        journey.candidate_intake_demo_review_bridge,
        "run_candidate_intake_demo_review_bridge",
        lambda write_reports: candidate_payload,
    )
    monkeypatch.setattr(
        journey.review_chain_orchestrator,
        "orchestrate_forex_review_chain",
        lambda state: _fake_orchestrate_status(
            review_chain_orchestrator.REVIEW_CHAIN_INCOMPLETE,
            ["missing_walk_forward"],
        ),
    )
    result = journey.run_review_chain_end_to_end_candidate_journey()
    assert result["final_verdict"] == journey.JOURNEY_INCOMPLETE


def test_monkeypatch_candidate_rejected_and_orchestrator_rejected(monkeypatch: Any) -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey

    candidate_payload = _fake_candidate_payload(canonical_demo_review_evidence_bridge.REJECTED)
    monkeypatch.setattr(
        journey.candidate_intake_demo_review_bridge,
        "run_candidate_intake_demo_review_bridge",
        lambda write_reports: candidate_payload,
    )
    monkeypatch.setattr(
        journey.review_chain_orchestrator,
        "orchestrate_forex_review_chain",
        lambda state: _fake_orchestrate_status(
            review_chain_orchestrator.REVIEW_CHAIN_REJECTED,
            ["candidate_rejected"],
        ),
    )
    result = journey.run_review_chain_end_to_end_candidate_journey()
    assert result["final_verdict"] == journey.JOURNEY_REJECTED


def test_unsafe_safety_flag_blocks_journey(monkeypatch: Any) -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey

    candidate_payload = _fake_candidate_payload(canonical_demo_review_evidence_bridge.DEMO_REVIEW_READY)
    candidate_payload["safety"]["broker_connected"] = True
    monkeypatch.setattr(
        journey.candidate_intake_demo_review_bridge,
        "run_candidate_intake_demo_review_bridge",
        lambda write_reports: candidate_payload,
    )
    result = journey.run_review_chain_end_to_end_candidate_journey()
    assert result["final_verdict"] == journey.JOURNEY_BLOCKED


def test_review_chain_blockers_preserved_in_journey_payload(monkeypatch: MonkeyPatch) -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey

    candidate_payload = _fake_candidate_payload(canonical_demo_review_evidence_bridge.DEMO_REVIEW_READY)
    monkeypatch.setattr(
        journey.candidate_intake_demo_review_bridge,
        "run_candidate_intake_demo_review_bridge",
        lambda write_reports: candidate_payload,
    )
    monkeypatch.setattr(
        journey.review_chain_orchestrator,
        "orchestrate_forex_review_chain",
        lambda state: _fake_orchestrate_status(
            review_chain_orchestrator.REVIEW_CHAIN_INCOMPLETE,
            ["demo_chain_blocker", "candidate_chain_wait"],
        ),
    )
    result = journey.run_review_chain_end_to_end_candidate_journey()
    assert result["review_chain_blockers"] == ["demo_chain_blocker", "candidate_chain_wait"]


def test_candidate_blockers_preserved_in_journey_payload(monkeypatch: MonkeyPatch) -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey

    candidate_payload = _fake_candidate_payload(
        canonical_demo_review_evidence_bridge.PAPER_CONTINUE,
        ["proof_missing", "walk_forward_warning"],
    )
    monkeypatch.setattr(
        journey.candidate_intake_demo_review_bridge,
        "run_candidate_intake_demo_review_bridge",
        lambda write_reports: candidate_payload,
    )
    monkeypatch.setattr(
        journey.review_chain_orchestrator,
        "orchestrate_forex_review_chain",
        lambda state: _fake_orchestrate_status(
            review_chain_orchestrator.REVIEW_CHAIN_INCOMPLETE,
            ["candidate_chain_blocker"],
        ),
    )
    result = journey.run_review_chain_end_to_end_candidate_journey()
    assert set(candidate_payload["blockers"]).issubset(set(result["candidate_demo_review_blockers"]))


def test_build_review_chain_state_passes_candidate_and_safety() -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey

    payload = _fake_candidate_payload(canonical_demo_review_evidence_bridge.DEMO_REVIEW_READY)
    state = journey.build_review_chain_state(payload)
    assert state["candidate_intake_demo_review"] == payload
    assert state["live_readiness_candidate"] is True
    assert state["human_live_review_ready"] is True


def test_build_review_chain_state_flags_unsafe_aliases() -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey

    payload = _fake_candidate_payload(canonical_demo_review_evidence_bridge.DEMO_REVIEW_READY)
    payload["safety"]["account_id_present"] = True
    state = journey.build_review_chain_state(payload)
    assert state.get("unsafe_account_identifier_access_detected") is True


def test_review_chain_payload_written_when_requested_and_under_reports_dir() -> None:
    import automation.forex_engine.review_chain_end_to_end_candidate_journey as journey
    from pathlib import Path

    result = journey.run_review_chain_end_to_end_candidate_journey(write_reports=True)
    report_path = Path(result["report"])
    assert report_path.exists()
    assert report_path.is_file()
    assert str(report_path).replace("\\", "/").startswith("Reports/forex_delivery/")
