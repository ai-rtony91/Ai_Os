from __future__ import annotations

from pathlib import Path

from automation.forex_engine import demo_validation_contract as contract


def _candidate(state: str = contract.DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION, approved: bool = True) -> dict:
    return {
        "candidate_id": "cand-001",
        "candidate_state": state,
        "candidate_approved": approved,
    }


def _result(
    sessions: int = 3,
    trade_count: int = 20,
    win_count: int = 12,
    loss_count: int = 8,
    realized_pl: float = 3.5,
    expectancy: float = 0.08,
    profit_factor: float = 1.25,
    drawdown: float = 2.0,
    evidence_score: float = 0.8,
    risk_failed: bool = False,
) -> dict:
    return {
        "trade_count": trade_count,
        "session_count": sessions,
        "win_count": win_count,
        "loss_count": loss_count,
        "realized_pl": realized_pl,
        "expectancy": expectancy,
        "profit_factor": profit_factor,
        "max_drawdown": drawdown,
        "evidence_score": evidence_score,
        "risk_failed": risk_failed,
    }


def _evaluate(
    state: dict | None = None,
    *,
    candidate: dict | None = None,
    results: list[dict] | None = None,
) -> dict:
    payload = {} if state is None else dict(state)
    if candidate is not None:
        payload["demo_candidate_record"] = candidate
    if results is not None:
        payload["demo_validation_results"] = results
    return contract.evaluate_demo_validation_contract(payload)


def test_empty_state_blocks() -> None:
    result = contract.evaluate_demo_validation_contract({})
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_BLOCKED
    assert result["live_readiness_candidate"] is False
    assert result["demo_validation_contract_completed"] is True
    assert "missing_candidate_record" in result["blockers"]


def test_missing_validation_results_requests_more_evidence() -> None:
    result = _evaluate(candidate=_candidate(), results=[])
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_MORE_EVIDENCE_REQUIRED
    assert result["next_safe_action"] == "collect_more_validation_results"
    assert "missing_validation_results" in result["blockers"]


def test_insufficient_sessions_continues() -> None:
    result = _evaluate(candidate=_candidate(), results=[_result(sessions=2)])
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_CONTINUE
    assert result["live_readiness_candidate"] is False


def test_insufficient_trades_continues() -> None:
    result = _evaluate(candidate=_candidate(), results=[_result(trade_count=10)])
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_CONTINUE
    assert "minimum_validation_trades_not_met" in result["blockers"]


def test_negative_expectancy_rejected() -> None:
    result = _evaluate(candidate=_candidate(), results=[_result(expectancy=-0.2)])
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_REJECTED
    assert "negative_expectancy" in result["blockers"]


def test_expectancy_below_threshold_continues() -> None:
    result = _evaluate(candidate=_candidate(), results=[_result(expectancy=0.001)])
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_CONTINUE
    assert "expectancy_below_threshold" in result["blockers"]


def test_low_profit_factor_rejected() -> None:
    result = _evaluate(candidate=_candidate(), results=[_result(profit_factor=0.7)])
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_REJECTED
    assert "profit_factor_below_threshold" in result["blockers"]


def test_drawdown_above_threshold_rejected() -> None:
    result = _evaluate(candidate=_candidate(), results=[_result(drawdown=20.0)])
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_REJECTED
    assert "drawdown_above_threshold" in result["blockers"]


def test_low_evidence_score_rejected() -> None:
    result = _evaluate(candidate=_candidate(), results=[_result(evidence_score=0.1)])
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_REJECTED
    assert "evidence_score_below_threshold" in result["blockers"]


def test_approved_passing_candidate_completes() -> None:
    result = _evaluate(candidate=_candidate(), results=[_result()])
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_COMPLETE
    assert result["live_readiness_candidate"] is True
    assert result["demo_validation_contract_completed"] is True
    assert result["safety"]["operator_review_required"] is True


def test_unapproved_candidate_blocks() -> None:
    result = _evaluate(candidate=_candidate(approved=False), results=[_result()])
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_BLOCKED
    assert "candidate_not_approved_for_demo_validation" in result["blockers"]


def test_paused_candidate_blocks() -> None:
    result = _evaluate(candidate=_candidate(state=contract.DEMO_CANDIDATE_PAUSED), results=[_result()])
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_BLOCKED
    assert "candidate_state_blocked" in result["blockers"]


def test_revoked_candidate_blocks() -> None:
    result = _evaluate(candidate=_candidate(state=contract.DEMO_CANDIDATE_REVOKED), results=[_result()])
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_BLOCKED
    assert "candidate_state_blocked" in result["blockers"]


def test_risk_failure_rejected() -> None:
    result = _evaluate(candidate=_candidate(), results=[_result(risk_failed=True)])
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_REJECTED
    assert "risk_failures_present" in result["blockers"]


def test_alias_aware_metrics_work() -> None:
    result = _evaluate(
        candidate=_candidate(),
        results=[
            {
                "validation_trade_count": 20,
                "validation_session_count": 3,
                "validation_win_count": 12,
                "validation_loss_count": 8,
                "validation_realized_pl": 3.5,
                "validation_expectancy": 0.08,
                "validation_profit_factor": 1.25,
                "validation_max_drawdown": 2.0,
                "validation_evidence_score": 0.8,
            }
        ],
    )
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_COMPLETE
    assert result["metric_summary"]["validation_trade_count"] == 20
    assert result["metric_summary"]["validation_session_count"] == 3


def test_unsafe_broker_connection_blocks() -> None:
    result = _evaluate(
        state={"broker_connection_active": True},
        candidate=_candidate(),
        results=[_result()],
    )
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_BLOCKED
    assert "unsafe_broker_connection_detected" in result["blockers"]


def test_unsafe_credential_access_blocks() -> None:
    result = _evaluate(
        state={"credentials_accessed": True},
        candidate=_candidate(),
        results=[_result()],
    )
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_BLOCKED
    assert "unsafe_credential_access_detected" in result["blockers"]


def test_unsafe_account_identifier_blocks() -> None:
    result = _evaluate(
        state={"account_identifiers_accessed": True},
        candidate=_candidate(),
        results=[_result()],
    )
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_BLOCKED
    assert "unsafe_account_identifier_detected" in result["blockers"]


def test_unsafe_order_execution_blocks() -> None:
    result = _evaluate(
        state={"order_execution_enabled": True},
        candidate=_candidate(),
        results=[_result()],
    )
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_BLOCKED
    assert "unsafe_order_execution_detected" in result["blockers"]


def test_unsafe_live_trading_blocks() -> None:
    result = _evaluate(
        state={"live_trading_authorized": True},
        candidate=_candidate(),
        results=[_result()],
    )
    assert result["demo_validation_contract_status"] == contract.DEMO_CONTRACT_BLOCKED
    assert "unsafe_live_trading_detected" in result["blockers"]


def test_next_safe_action_deterministic() -> None:
    first = _evaluate(candidate=_candidate(), results=[_result()])
    second = _evaluate(candidate=_candidate(), results=[_result()])
    assert first["next_safe_action"] == second["next_safe_action"]


def test_required_next_packets_ranked() -> None:
    result = _evaluate(candidate=_candidate(), results=[])
    assert result["required_next_packets"] == [
        "collect_more_validation_results",
        "run_validation_session_batch",
        "refresh_live_readiness_packet",
    ]


def test_safety_never_authorizes_live_trading() -> None:
    result = _evaluate(candidate=_candidate(), results=[_result()])
    assert result["safety"]["live_trading_authorized"] is False


def test_safety_never_enables_order_execution() -> None:
    result = _evaluate(candidate=_candidate(), results=[_result()])
    assert result["safety"]["order_execution_enabled"] is False


def test_source_scan_no_banned_tokens() -> None:
    source = Path("automation/forex_engine/demo_validation_contract.py").read_text(encoding="utf-8").lower()
    banned = ("requests", "urllib", "socket", "subprocess", "os.environ", ".env", "http://", "https://")
    for token in banned:
        assert token not in source
