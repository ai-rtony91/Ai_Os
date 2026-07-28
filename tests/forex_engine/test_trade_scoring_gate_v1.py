from automation.forex_engine.trade_scoring_gate_v1 import (
    DECISION_BLOCKED,
    DECISION_MICRO_LIVE_REVIEW_REQUIRED,
    DECISION_PAPER_ELIGIBLE,
    evaluate_trade_scoring_gate_v1,
)


def _candidate(**overrides):
    candidate = {
        "symbol": "EUR_USD",
        "direction": "BUY",
        "entry_type": "LIMIT",
        "proposed_entry": 1.1000,
        "stop_loss": 1.0980,
        "take_profit": 1.1045,
        "risk_amount": 25.0,
        "account_mode": "PAPER",
        "strategy_id": "paper_fixture_expectancy_probe_v1",
        "session": "LONDON",
        "spread": 1.0,
        "slippage_estimate": 0.5,
        "volatility_state": "NORMAL",
        "trend_alignment": "ALIGNED",
        "walk_forward_status": "MORE_PAPER_REQUIRED",
        "recent_strategy_status": "ACCEPTABLE",
        "kill_switch_active": False,
        "broker_ready": False,
        "evidence_depth": 5,
    }
    candidate.update(overrides)
    return candidate


def test_missing_kill_switch_active_blocks_fail_closed():
    candidate = _candidate()
    candidate.pop("kill_switch_active")
    result = evaluate_trade_scoring_gate_v1(candidate)
    assert result["decision"] == DECISION_BLOCKED
    assert "kill_switch_active_missing" in result["blockers"]
    assert "kill_switch_active_missing_or_non_bool" in result["blockers"]


def test_kill_switch_active_true_blocks():
    result = evaluate_trade_scoring_gate_v1(_candidate(kill_switch_active=True))
    assert result["decision"] == DECISION_BLOCKED
    assert "kill_switch_active_true" in result["blockers"]


def test_missing_required_fields_blocks():
    candidate = _candidate()
    candidate.pop("symbol")
    result = evaluate_trade_scoring_gate_v1(candidate)
    assert result["decision"] == DECISION_BLOCKED
    assert "symbol_missing" in result["blockers"]


def test_bad_stop_take_profit_geometry_blocks():
    result = evaluate_trade_scoring_gate_v1(_candidate(stop_loss=1.1010))
    assert result["decision"] == DECISION_BLOCKED
    assert "invalid_stop_take_profit_geometry" in result["blockers"]


def test_bad_risk_reward_blocks():
    result = evaluate_trade_scoring_gate_v1(_candidate(take_profit=1.1010))
    assert result["decision"] == DECISION_BLOCKED
    assert "risk_reward_below_minimum" in result["blockers"]


def test_failed_walk_forward_blocks():
    result = evaluate_trade_scoring_gate_v1(_candidate(walk_forward_status="FAILED"))
    assert result["decision"] == DECISION_BLOCKED
    assert "walk_forward_failed" in result["blockers"]


def test_valid_weak_evidence_candidate_becomes_paper_eligible():
    result = evaluate_trade_scoring_gate_v1(_candidate())
    assert result["decision"] == DECISION_PAPER_ELIGIBLE
    assert result["execution_allowed"] is False


def test_strong_candidate_becomes_micro_live_review_required():
    result = evaluate_trade_scoring_gate_v1(
        _candidate(
            account_mode="MICRO_LIVE_REVIEW",
            walk_forward_status="PASS",
            broker_ready=True,
            evidence_depth=45,
        )
    )
    assert result["decision"] == DECISION_MICRO_LIVE_REVIEW_REQUIRED
    assert result["human_review_required"] is True


def test_micro_live_review_required_still_has_execution_allowed_false():
    result = evaluate_trade_scoring_gate_v1(
        _candidate(
            account_mode="MICRO_LIVE_REVIEW",
            walk_forward_status="PASS",
            broker_ready=True,
            evidence_depth=45,
        )
    )
    assert result["decision"] == DECISION_MICRO_LIVE_REVIEW_REQUIRED
    assert result["execution_allowed"] is False


def test_broker_action_allowed_always_false_in_v1():
    for candidate in [
        _candidate(),
        _candidate(kill_switch_active=True),
        _candidate(account_mode="MICRO_LIVE_REVIEW", walk_forward_status="PASS", broker_ready=True, evidence_depth=45),
    ]:
        assert evaluate_trade_scoring_gate_v1(candidate)["broker_action_allowed"] is False
