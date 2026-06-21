"""Tests for deterministic paper-only walk-forward depth expansion of c1-eur-buy."""
from __future__ import annotations

import inspect

from automation.forex_engine import walk_forward_depth_r_v1 as module
from automation.forex_engine import profit_objective_accelerator_l_v1 as accelerator


def _run():
    return module.run_walk_forward_depth(write_reports=False)


def test_anchor_in_every_walk_forward_window():
    result = _run()
    scored = result["scored_windows"]
    assert len(scored) >= 4
    assert all(row["candidate_id"] == "c1-eur-buy" for row in scored)
    assert all(row["strategy_id"] == "paper_long_run_supervisor_v2" for row in scored)
    assert all(row["direction"] == "LONG" for row in scored)


def test_each_window_has_closed_trade_rows():
    result = _run()
    scored = result["scored_windows"]
    for row in scored:
        assert row["closed_trade_count"] >= 1


def test_accelerator_used_for_scoring():
    result = _run()
    assert result["accelerator_mode"] == accelerator.MODE
    assert result["mode"] == module.MODE
    for row in result["scored_windows"]:
        assert "expectancy" in row
        assert "profit_factor" in row
        assert "max_drawdown" in row


def test_walk_forward_stability_summary_and_gate():
    result = _run()
    summary = result["stability_scoreboard"]
    assert summary["total_windows"] == 4
    assert "passing_windows" in summary
    assert "failing_windows" in summary
    assert "stable_expectancy" in summary
    assert "stable_profit_factor" in summary
    assert "controlled_drawdown" in summary
    assert summary["walk_forward_gate_cleared"] in (True, False)


def test_walk_forward_gate_is_deterministic():
    first = _run()["stability_scoreboard"]["walk_forward_gate_cleared"]
    second = _run()["stability_scoreboard"]["walk_forward_gate_cleared"]
    assert first == second


def test_failing_windows_report_blockers_for_quality():
    result = _run()
    failing = [row for row in result["scored_windows"] if row["blocker_reasons"]]
    assert len(failing) >= 1
    any_negative = any("negative_expectancy" in row["blocker_reasons"] for row in result["scored_windows"])
    any_low_pf = any("low_profit_factor" in row["blocker_reasons"] for row in result["scored_windows"])
    any_drawdown = any("excessive_drawdown" in row["blocker_reasons"] for row in result["scored_windows"])
    assert any_negative or any_low_pf or any_drawdown


def test_best_candidate_selection_is_deterministic():
    first = _run()["best_candidate"]
    second = _run()["best_candidate"]
    assert first == second
    assert first["candidate_id"] == "c1-eur-buy"
    assert first["strategy_id"] == "paper_long_run_supervisor_v2"


def test_no_forbidden_runtime_surfaces():
    source = inspect.getsource(module)
    forbidden = (
        "requests",
        "socket",
        "urllib",
        "subprocess",
        "os.environ",
        "getenv(",
        "oanda",
    )
    for token in forbidden:
        assert token not in source
