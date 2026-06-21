from __future__ import annotations

from pathlib import Path

from automation.forex_engine import campaign_evidence_accumulator as accumulator


def _paper_session(**overrides) -> dict:
    payload = {
        "trade_count": 12,
        "session_count": 2,
        "win_count": 6,
        "loss_count": 6,
        "realized_pl": 4.0,
        "expectancy": 0.15,
        "profit_factor": 1.8,
        "max_drawdown": 6.0,
        "evidence_score": 0.82,
    }
    payload.update(overrides)
    return payload


def _profitability(**overrides) -> dict:
    payload = {
        "status": "passed",
        "score": 0.9,
        "expectancy": 0.2,
        "trade_count": 8,
        "session_count": 1,
        "win_count": 4,
        "loss_count": 4,
        "realized_pl": 3.2,
    }
    payload.update(overrides)
    return payload


def _walk_forward(**overrides) -> dict:
    payload = {
        "status": "pass",
        "score": 0.85,
        "trade_count": 5,
        "session_count": 1,
        "expectancy": 0.2,
        "profit_factor": 1.3,
    }
    payload.update(overrides)
    return payload


def _promotion(**overrides) -> dict:
    payload = {"status": "success", "score": 1.0, "trade_count": 0, "session_count": 0}
    payload.update(overrides)
    return payload


def _capital_allocation(**overrides) -> dict:
    payload = {"status": "true", "score": 0.95, "trade_count": 0, "session_count": 0}
    payload.update(overrides)
    return payload


def _evaluate(**overrides) -> dict:
    args = {
        "paper_session_results": [_paper_session()],
        "profitability_results": [_profitability()],
        "walk_forward_results": [_walk_forward()],
        "promotion_results": [_promotion()],
        "capital_allocation_results": [_capital_allocation()],
    }
    args.update(overrides)
    return accumulator.evaluate_campaign_evidence(**args)


def test_positive_ready_path() -> None:
    result = _evaluate(
        paper_session_results=[
            _paper_session(trade_count=20, session_count=3, expectancy=0.12, profit_factor=1.2, max_drawdown=4.0),
            _paper_session(trade_count=10, session_count=1, expectancy=0.1, profit_factor=1.5, max_drawdown=2.0),
        ]
    )
    assert result["campaign_evidence_status"] == accumulator.CAMPAIGN_EVIDENCE_READY
    assert result["campaign_demo_candidate"] is True
    assert result["campaign_trade_count"] == 43
    assert result["campaign_session_count"] == 6
    assert result["operator_review_required"] is True


def test_empty_evidence_path() -> None:
    result = accumulator.evaluate_campaign_evidence(
        paper_session_results=[],
        profitability_results=[],
        walk_forward_results=[],
        promotion_results=[],
        capital_allocation_results=[],
    )
    assert result["campaign_evidence_status"] == accumulator.CAMPAIGN_MORE_EVIDENCE_REQUIRED
    assert result["campaign_demo_candidate"] is False
    assert "no_evidence_results" in result["campaign_blockers"]


def test_missing_input_path() -> None:
    result = accumulator.evaluate_campaign_evidence(
        paper_session_results=None,
        profitability_results=None,
        walk_forward_results=None,
        promotion_results=None,
        capital_allocation_results=None,
    )
    assert result["campaign_evidence_status"] == accumulator.CAMPAIGN_MORE_EVIDENCE_REQUIRED
    assert result["campaign_blockers"] == ["no_evidence_results"]


def test_insufficient_trade_count_path() -> None:
    result = _evaluate(
        paper_session_results=[_paper_session(trade_count=5, session_count=1, expectancy=0.2, profit_factor=1.3, max_drawdown=1.0)],
        profitability_results=[_profitability()],
        walk_forward_results=[_walk_forward()],
        promotion_results=[_promotion()],
        capital_allocation_results=[_capital_allocation()],
    )
    assert result["campaign_evidence_status"] == accumulator.CAMPAIGN_MORE_EVIDENCE_REQUIRED
    assert result["campaign_trade_count"] < 20


def test_insufficient_session_count_path() -> None:
    result = _evaluate(
        paper_session_results=[_paper_session(trade_count=20, session_count=1, expectancy=0.2, profit_factor=1.3, max_drawdown=1.0)],
        profitability_results=[_profitability(session_count=0, trade_count=0)],
        walk_forward_results=[_walk_forward(session_count=0, trade_count=0)],
        promotion_results=[_promotion()],
        capital_allocation_results=[_capital_allocation()],
    )
    assert result["campaign_evidence_status"] == accumulator.CAMPAIGN_MORE_EVIDENCE_REQUIRED
    assert result["campaign_session_count"] < 3


def test_negative_expectancy_path() -> None:
    result = _evaluate(
        paper_session_results=[_paper_session(expectancy=-0.05)],
        profitability_results=[],
        walk_forward_results=[],
        promotion_results=[],
        capital_allocation_results=[],
    )
    assert result["campaign_evidence_status"] == accumulator.CAMPAIGN_EVIDENCE_REJECTED
    assert result["campaign_expectancy"] < 0


def test_low_profit_factor_path() -> None:
    result = _evaluate(
        paper_session_results=[_paper_session(profit_factor=1.0)],
        profitability_results=[],
        walk_forward_results=[],
        promotion_results=[],
        capital_allocation_results=[],
    )
    assert result["campaign_evidence_status"] == accumulator.CAMPAIGN_EVIDENCE_REJECTED
    assert result["campaign_profit_factor"] < 1.10


def test_excessive_drawdown_path() -> None:
    result = _evaluate(
        paper_session_results=[_paper_session(max_drawdown=11.0)],
        profitability_results=[],
        walk_forward_results=[],
        promotion_results=[],
        capital_allocation_results=[],
    )
    assert result["campaign_evidence_status"] == accumulator.CAMPAIGN_EVIDENCE_REJECTED
    assert result["campaign_max_drawdown"] > 10.0


def test_failed_profitability_component_path() -> None:
    result = _evaluate(
        profitability_results=[_profitability(status="failed")],
    )
    assert result["campaign_evidence_status"] in {
        accumulator.CAMPAIGN_EVIDENCE_REJECTED,
        accumulator.CAMPAIGN_EVIDENCE_BLOCKED,
    }
    assert "profitability_failure" in result["campaign_blockers"]


def test_failed_walk_forward_component_path() -> None:
    result = _evaluate(
        walk_forward_results=[_walk_forward(status="failed")],
    )
    assert result["campaign_evidence_status"] in {
        accumulator.CAMPAIGN_EVIDENCE_REJECTED,
        accumulator.CAMPAIGN_EVIDENCE_BLOCKED,
    }
    assert "walk_forward_failure" in result["campaign_blockers"]


def test_failed_promotion_component_path() -> None:
    result = _evaluate(
        promotion_results=[_promotion(status="failed")],
    )
    assert result["campaign_evidence_status"] in {
        accumulator.CAMPAIGN_EVIDENCE_REJECTED,
        accumulator.CAMPAIGN_EVIDENCE_BLOCKED,
    }
    assert "promotion_failure" in result["campaign_blockers"]


def test_failed_capital_allocation_component_path() -> None:
    result = _evaluate(
        capital_allocation_results=[_capital_allocation(status="failed")],
    )
    assert result["campaign_evidence_status"] in {
        accumulator.CAMPAIGN_EVIDENCE_REJECTED,
        accumulator.CAMPAIGN_EVIDENCE_BLOCKED,
    }
    assert "capital_allocation_failure" in result["campaign_blockers"]


def test_deterministic_output_path() -> None:
    args = {
        "paper_session_results": [_paper_session()],
        "profitability_results": [_profitability()],
        "walk_forward_results": [_walk_forward()],
        "promotion_results": [_promotion()],
        "capital_allocation_results": [_capital_allocation()],
    }
    first = accumulator.evaluate_campaign_evidence(**args)
    second = accumulator.evaluate_campaign_evidence(**args)
    assert first == second


def test_safety_object_path() -> None:
    result = _evaluate()
    safety = result["safety"]
    assert safety == {
        "paper_only": True,
        "broker_connection_active": False,
        "network_access": False,
        "credentials_accessed": False,
        "order_execution_enabled": False,
        "demo_execution_active": False,
        "live_trading_authorized": False,
        "capital_allocated": False,
        "capital_allocation_modified": False,
        "operator_review_required": True,
    }


def test_source_scan_prohibits_network_or_io_sensitive_patterns() -> None:
    source = Path("automation/forex_engine/campaign_evidence_accumulator.py").read_text(encoding="utf-8").lower()
    banned_tokens = (
        "requests",
        "urllib",
        "socket",
        "subprocess",
        "os.environ",
        "http://",
        "https://",
    )
    for token in banned_tokens:
        assert token not in source
