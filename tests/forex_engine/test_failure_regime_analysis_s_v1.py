"""Tests for deterministic failure regime analysis of walk-forward windows."""
from __future__ import annotations

import inspect

from automation.forex_engine import failure_regime_analysis_s_v1 as module
from automation.forex_engine import walk_forward_depth_r_v1


def _run():
    return module.run_failure_regime_analysis(write_reports=False)


def test_walk_forward_data_consumed():
    result = _run()
    assert result["walk_forward_packet_id"] == walk_forward_depth_r_v1.PACKET_ID
    assert len(result["analyzed_windows"]) >= 4
    assert result["analyzed_windows"][0]["candidate_id"] == "c1-eur-buy"


def test_failures_detected_and_root_causes_present():
    result = _run()
    summary = result["failure_summary"]
    assert len(summary["failing_windows"]) >= 1
    assert "wf-02" in summary["failing_windows"] or "wf-03" in summary["failing_windows"] or "wf-04" in summary["failing_windows"]
    assert "systemic_failures" in summary
    assert isinstance(summary["root_causes"], dict)
    assert any(summary["root_causes"].values())


def test_systemic_vs_isolated_classification():
    result = _run()
    summary = result["failure_summary"]
    assert isinstance(summary["systemic_failures"], list)
    assert isinstance(summary["isolated_failures"], list)
    assert set(summary["systemic_failures"]).isdisjoint(set(summary["isolated_failures"]))


def test_verdict_and_confidence_generated():
    result = _run()
    assert result["verdict"] in {"CONTINUE", "REQUIRE_OPTIMIZATION", "REQUIRE_MORE_EVIDENCE", "REJECT"}
    assert isinstance(result["confidence_score"], int)
    assert 0 <= result["confidence_score"] <= 100
    assert result["failure_scoreboard"]["candidate_id"] == "c1-eur-buy"


def test_candidate_best_status_and_viability():
    result = _run()
    status = result["failure_scoreboard"]
    assert status["candidate_id"] == "c1-eur-buy"
    assert isinstance(status["best_candidate_still_viable"], bool)


def test_deterministic_behavior():
    first = _run()
    second = _run()
    assert first["verdict"] == second["verdict"]
    assert first["confidence_score"] == second["confidence_score"]
    assert first["failure_summary"]["failing_windows"] == second["failure_summary"]["failing_windows"]


def test_no_broker_or_network_or_demo_or_live_surface():
    source = inspect.getsource(module)
    forbidden = (
        "requests",
        "socket",
        "urllib",
        "subprocess",
        "oanda",
    )
    for token in forbidden:
        assert token not in source
