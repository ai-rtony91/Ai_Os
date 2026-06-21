from automation.forex_engine.broker_policy_readiness_engine import (
    STATUS_BLOCKED,
    STATUS_MORE_INFO,
    STATUS_READY,
    evaluate_broker_policy_readiness,
)


def _policy():
    return {
        "broker_name": "declared-demo-broker",
        "account_type": "forex",
        "jurisdiction": "US",
        "instrument_type": "forex",
        "symbol": "EUR_USD",
        "long_allowed": True,
        "short_allowed": True,
        "hedging_allowed": False,
        "fifo_required": True,
        "margin_trading_allowed": True,
        "max_leverage": 20,
        "min_trade_size": 1,
        "max_trade_size": 1000,
        "supported_order_types": ["market", "limit"],
        "trading_sessions": ["regular", "london", "new_york"],
        "paper_only_policy_review": True,
    }


def _strategy():
    return {
        "symbol": "EUR_USD",
        "direction": "both",
        "order_type": "market",
        "session": "regular",
        "trade_size": 10,
        "required_leverage": 2,
    }


def test_broker_policy_ready():
    result = evaluate_broker_policy_readiness(_policy(), _strategy())
    assert result["broker_policy_ready"] is True
    assert result["account_policy_status"] == STATUS_READY
    assert "short trading" in result["approved_capabilities"]
    assert result["safety"]["broker_access"] is False


def test_missing_policy_metadata_blocked():
    result = evaluate_broker_policy_readiness({"broker_name": "x"}, _strategy())
    assert result["broker_policy_ready"] is False
    assert result["account_policy_status"] == STATUS_MORE_INFO
    assert any(reason.startswith("missing_policy_metadata:") for reason in result["blocked_reasons"])


def test_short_trading_not_allowed_blocks_bidirectional_strategy():
    policy = _policy()
    policy["short_allowed"] = False
    result = evaluate_broker_policy_readiness(policy, _strategy())
    assert result["broker_policy_ready"] is False
    assert "short_trading_not_allowed" in result["blocked_reasons"]


def test_hedging_fifo_conflict_blocked():
    policy = _policy()
    policy["hedging_allowed"] = True
    policy["fifo_required"] = True
    result = evaluate_broker_policy_readiness(policy, _strategy())
    assert result["account_policy_status"] == STATUS_BLOCKED
    assert "hedging_fifo_conflict_requires_review" in result["blocked_reasons"]


def test_trade_size_outside_limits_blocked():
    strategy = _strategy()
    strategy["trade_size"] = 5000
    result = evaluate_broker_policy_readiness(_policy(), strategy)
    assert "trade_size_outside_broker_limits" in result["blocked_reasons"]


def test_unsupported_order_type_blocked():
    strategy = _strategy()
    strategy["order_type"] = "stop_market"
    result = evaluate_broker_policy_readiness(_policy(), strategy)
    assert "unsupported_order_type" in result["blocked_reasons"]


def test_unsupported_session_blocked():
    strategy = _strategy()
    strategy["session"] = "closed"
    result = evaluate_broker_policy_readiness(_policy(), strategy)
    assert "unsupported_trading_session" in result["blocked_reasons"]


def test_deterministic_output():
    first = evaluate_broker_policy_readiness(_policy(), _strategy())
    second = evaluate_broker_policy_readiness(_policy(), _strategy())
    assert first == second


def test_safety_source_scan():
    source = open("automation/forex_engine/broker_policy_readiness_engine.py", encoding="utf-8").read()
    forbidden = ["requests", "urllib", "socket", "subprocess", "os.environ", "http://", "https://"]
    for token in forbidden:
        assert token not in source


def test_forbidden_execution_state_absent():
    result = evaluate_broker_policy_readiness(_policy(), _strategy())
    safety = result["safety"]
    assert safety["broker_connection_active"] is False
    assert safety["credentials_access"] is False
    assert safety["network_access"] is False
    assert safety["order_execution_enabled"] is False
    assert safety["live_trading_authorized"] is False
    assert safety["capital_allocation_modified"] is False
