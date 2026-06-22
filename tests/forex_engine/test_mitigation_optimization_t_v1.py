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

