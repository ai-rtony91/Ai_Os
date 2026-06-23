"""Tests for deterministic paper-only mitigation optimization (Packet T)."""
from __future__ import annotations

import inspect

from automation.forex_engine import mitigation_optimization_t_v1 as module


def _run():
    return module.run_mitigation_optimization(write_reports=False)


def test_baseline_results_exist():
    payload = _run()
    baseline = payload["baseline_results"]
    assert baseline["candidate_id"] == "c1-eur-buy"
    assert baseline["strategy_id"] == "paper_long_run_supervisor_v2"
    assert baseline["direction"] == "LONG"
    assert baseline["metrics"]["closed_trade_count"] >= 0
    assert isinstance(baseline["window_results"], list)


def test_optimized_results_exist():
    payload = _run()
    optimized = payload["optimized_results"]
    assert optimized["candidate_id"] == "c1-eur-buy"
    assert optimized["strategy_id"] == "paper_long_run_supervisor_v2"
    assert isinstance(optimized["window_results"], list)
    assert optimized["metrics"]["closed_trade_count"] >= 0


def test_mitigation_controls_execute():
    controls = module.apply_mitigation_controls([200.0, -7000.0, 40.0, -600.0, 15.0, -20.0, -25.0])
    changed = controls["trade_pnl_list"]
    assert controls["controls_executed"]
    assert any(control in controls["controls_executed"] for control in (
        "drawdown_containment",
        "consecutive_loss_throttle",
        "trade_concentration_limiter",
        "weak_expectancy_suppression",
    ))
    assert len(changed) <= 7
    # consecutive losses should not exceed the configured throttle target after mitigation
    losses = module.accelerator._consecutive_counts(changed)[1]
    assert losses <= module.MITIGATION_PARAMS["consecutive_loss_throttle"]


def test_weak_expectancy_suppression_removes_losses_not_small_winners():
    controls = module.apply_mitigation_controls([30.0, -40.0, 12.0, -14.0, 8.0])
    changed = controls["trade_pnl_list"]
    assert "weak_expectancy_suppression" in controls["controls_executed"]
    assert len(changed) == 5
    assert 8.0 in changed
    assert -14.0 not in changed
    assert 0.0 in changed
    assert sum(changed) / len(changed) > 0.0


def test_before_after_comparison_exists():
    payload = _run()
    summary = payload["optimization_summary"]
    for key in (
        "baseline",
        "optimized",
        "expectancy_delta",
        "profit_factor_delta",
        "win_rate_delta",
        "drawdown_delta",
        "verdict_change",
    ):
        assert key in summary
    assert isinstance(summary["verdict_change"], str)
    assert payload["candidate_status"] in {
        "CONTINUE",
        "REQUIRE_MORE_EVIDENCE",
        "REQUIRE_OPTIMIZATION",
        "REJECT",
    }


def test_candidate_status_and_gate_flags():
    payload = _run()
    assert isinstance(payload["walk_forward_improved"], bool)
    assert isinstance(payload["optimization_improved_candidate"], bool)
    assert payload["candidate_status"] in {
        "CONTINUE",
        "REQUIRE_MORE_EVIDENCE",
        "REQUIRE_OPTIMIZATION",
        "REJECT",
    }


def test_insufficient_sample_collapses_through_evidence_preservation():
    payload = _run()
    assert payload["candidate_status"] == "CONTINUE"
    assert payload["optimized_results"]["walk_forward_gate_cleared"] is True
    assert payload["optimized_results"]["mitigation_remaining_blockers"] == []
    assert [row["closed_trade_count"] for row in payload["optimized_results"]["window_results"]] == [5, 5, 5, 5]
    assert all(
        row["closed_trade_count"] >= module.MITIGATION_THRESHOLDS["minimum_sample_size"]
        for row in payload["optimized_results"]["window_results"]
    )


def test_retest_only_blockers_require_more_evidence_without_clearing_gate():
    comparison = {
        "expectancy_delta": 1.0,
        "profit_factor_delta": -1.0,
        "win_rate_delta": 0.0,
        "drawdown_delta": -1.0,
        "consecutive_losses_delta": 0,
    }
    optimized = {
        "metrics": {"closed_trade_count": module.MITIGATION_THRESHOLDS["minimum_sample_size"]},
        "mitigation_remaining_blockers": ["insufficient_sample"],
        "walk_forward_gate_cleared": False,
    }
    baseline = {"walk_forward_gate_cleared": False}
    assert module.determine_candidate_status(comparison, optimized, baseline) == "REQUIRE_MORE_EVIDENCE"
    assert optimized["walk_forward_gate_cleared"] is False


def test_deterministic_behavior():
    first = _run()
    second = _run()
    assert first["candidate_status"] == second["candidate_status"]
    assert first["optimization_summary"]["expectancy_delta"] == second["optimization_summary"]["expectancy_delta"]
    assert first["optimization_summary"]["profit_factor_delta"] == second["optimization_summary"]["profit_factor_delta"]
    assert first["baseline_results"]["window_results"] == second["baseline_results"]["window_results"]


def test_no_broker_network_demo_or_live_surface():
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

