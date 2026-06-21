"""Tests for deterministic paper-only evidence-depth expansion of c1-eur-buy."""
from __future__ import annotations

import inspect

from automation.forex_engine import evidence_depth_expansion_q_v1 as module
from automation.forex_engine import profit_objective_accelerator_l_v1 as accelerator


def _run():
    return module.run_evidence_depth_expansion(write_reports=False)


def test_anchor_present_with_expanded_depth():
    result = _run()
    rows = result["candidates"]
    anchor = next(row for row in rows if row["candidate_id"] == "c1-eur-buy")
    assert anchor["strategy_id"] == "paper_long_run_supervisor_v2"
    assert anchor["direction"] == "LONG"
    assert anchor["closed_trade_count"] >= 20
    assert anchor["expectancy"] == 200.0
    assert anchor["profit_factor"] == 999.0
    assert anchor["max_drawdown"] == 0.0


def test_long_and_short_evidence_rows_exist():
    result = _run()
    directions = {row["direction"] for row in result["candidates"]}
    assert "LONG" in directions
    assert "SHORT" in directions


def test_accelerator_via_profit_objective_is_used():
    result = _run()
    assert result["accelerator_mode"] == accelerator.MODE
    assert result["mode"] == module.MODE
    for row in result["candidates"]:
        assert "score" in row
        assert "promotion_status" in row


def test_anchor_sample_gate_clear_and_no_other_gates_blocked():
    result = _run()
    assert result["anchor_sample_size_gate_cleared"] is True
    assert result["anchor_closed_trades"] >= 20
    assert result["anchor_any_remaining_blockers"] is False


def test_short_candidates_remain_blocked_for_negative_weak_direction():
    result = _run()
    short_rows = [row for row in result["candidates"] if row["direction"] == "SHORT"]
    assert len(short_rows) >= 1
    assert any(row["blocked"] for row in short_rows)
    assert any(row["blocked_reasons"] for row in short_rows)


def test_best_candidate_deterministic():
    first = _run()["best_candidate"]
    second = _run()["best_candidate"]
    assert first == second
    assert first["candidate_id"] == "c1-eur-buy"
    assert first["direction"] == "LONG"


def test_reports_are_written_and_match_expected_paths():
    result = _run()
    paths = module.write_reports(result)
    assert paths["packet"].name == "AIOS_FOREX_EVIDENCE_DEPTH_EXPANSION_PACKET_Q_V1_REPORT.md"
    assert paths["scoreboard"].name == "AIOS_FOREX_C1_EUR_BUY_EVIDENCE_DEPTH_SCOREBOARD_V1.md"
    assert paths["matrix"].name == "AIOS_FOREX_LONG_SHORT_EVIDENCE_DEPTH_MATRIX_V1.md"


def test_output_structure_and_safety_surface_no_broker_network_surface():
    result = _run()
    safety = result["safety"]
    assert safety["paper_only"] is True
    assert safety["broker_connected"] is False
    assert safety["credentials_used"] is False
    assert safety["account_id_present"] is False
    assert safety["network_used"] is False
    assert safety["order_execution"] is False
    assert safety["demo_trading"] is False
    assert safety["live_trading"] is False


def test_no_forbidden_runtime_apis():
    source = inspect.getsource(module)
    forbidden = (
        "requests",
        "urllib",
        "socket",
        "subprocess",
        "os.environ",
        "getenv(",
        "write_bytes(",
        "oanda",
    )
    for token in forbidden:
        assert token not in source
