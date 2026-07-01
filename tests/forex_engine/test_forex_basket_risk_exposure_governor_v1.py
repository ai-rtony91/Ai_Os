from automation.forex_engine.forex_basket_risk_exposure_governor_v1 import (
    BASKET_RISK_EXPOSURE_READY,
    BLOCKED_BY_CORRELATION,
    BLOCKED_BY_CURRENCY_EXPOSURE,
    BLOCKED_BY_DAILY_LOSS_STOP,
    BLOCKED_BY_EMPTY_BASKET,
    BLOCKED_BY_KILL_SWITCH,
    BLOCKED_BY_PER_TRADE_RISK,
    BLOCKED_BY_TOTAL_BASKET_RISK,
    evaluate_forex_basket_risk_exposure_governor_v1,
)
from automation.forex_engine.forex_multi_pair_opportunity_batch_v1 import (
    MULTI_PAIR_OPPORTUNITY_BATCH_READY,
)


def _candidate(pair="EUR_USD", risk_pct=0.005):
    return {
        "pair": pair,
        "side": "BUY",
        "order_type": "MARKET",
        "units": 1000,
        "setup_id": f"SETUP-{pair}",
        "evidence_id": f"EVIDENCE-{pair}",
        "candidate_score": 90,
        "expected_r_multiple": 1.8,
        "minimum_reward_risk_ratio": 1.2,
        "risk_pct": risk_pct,
        "stop_loss_present": True,
        "take_profit_present": True,
    }


def _payload(selected=None, **policy_overrides):
    risk_policy = {
        "max_risk_per_trade_pct": 0.01,
        "max_total_burst_risk_pct": 0.03,
        "max_daily_loss_pct": 0.03,
        "max_concurrent_open_trades": 4,
        "max_candidates_per_burst": 4,
        "max_same_currency_exposure_count": 3,
        "correlation_gate_required": True,
        "correlation_within_limit": True,
        "currency_exposure_within_limit": True,
        "kill_switch_active": False,
        "daily_loss_stop_active": False,
        "one_burst_at_a_time": True,
        "next_burst_blocked_until_review": True,
    }
    risk_policy.update(policy_overrides)
    return {
        "governed_burst_requested": True,
        "opportunity_batch_result": {
            "status": MULTI_PAIR_OPPORTUNITY_BATCH_READY,
            "ready": True,
            "selected_candidates": selected if selected is not None else [_candidate()],
        },
        "risk_policy": risk_policy,
    }


def test_empty_basket_blocks():
    result = evaluate_forex_basket_risk_exposure_governor_v1(_payload([]))
    assert result["status"] == BLOCKED_BY_EMPTY_BASKET


def test_per_trade_risk_over_limit_blocks():
    result = evaluate_forex_basket_risk_exposure_governor_v1(
        _payload([_candidate(risk_pct=0.02)])
    )
    assert result["status"] == BLOCKED_BY_PER_TRADE_RISK


def test_total_basket_risk_over_limit_blocks():
    result = evaluate_forex_basket_risk_exposure_governor_v1(
        _payload(
            [
                _candidate("EUR_USD", 0.008),
                _candidate("GBP_USD", 0.008),
                _candidate("USD_JPY", 0.008),
                _candidate("AUD_USD", 0.008),
            ]
        )
    )
    assert result["status"] == BLOCKED_BY_TOTAL_BASKET_RISK


def test_correlation_breach_blocks():
    result = evaluate_forex_basket_risk_exposure_governor_v1(
        _payload(correlation_within_limit=False)
    )
    assert result["status"] == BLOCKED_BY_CORRELATION


def test_currency_exposure_breach_blocks():
    result = evaluate_forex_basket_risk_exposure_governor_v1(
        _payload(currency_exposure_within_limit=False)
    )
    assert result["status"] == BLOCKED_BY_CURRENCY_EXPOSURE


def test_kill_switch_blocks():
    result = evaluate_forex_basket_risk_exposure_governor_v1(
        _payload(kill_switch_active=True)
    )
    assert result["status"] == BLOCKED_BY_KILL_SWITCH


def test_daily_loss_stop_blocks():
    result = evaluate_forex_basket_risk_exposure_governor_v1(
        _payload(daily_loss_stop_active=True)
    )
    assert result["status"] == BLOCKED_BY_DAILY_LOSS_STOP


def test_valid_basket_ready():
    result = evaluate_forex_basket_risk_exposure_governor_v1(
        _payload([_candidate("EUR_USD"), _candidate("GBP_USD")])
    )
    assert result["status"] == BASKET_RISK_EXPOSURE_READY
    assert result["ready_for_burst_permission"] is True
    assert result["total_burst_risk_pct"] == 0.01
