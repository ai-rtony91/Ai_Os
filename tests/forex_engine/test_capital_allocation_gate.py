from automation.forex_engine.capital_allocation_gate import (
    STATUS_BLOCKED,
    STATUS_MORE_INFO,
    STATUS_READY,
    evaluate_capital_allocation_gate,
)


def _metadata():
    return {
        "account_equity_declared": 1000,
        "max_account_risk_percent_declared": 2,
        "max_trade_risk_percent_declared": 0.5,
        "max_daily_loss_percent_declared": 2,
        "max_drawdown_percent_declared": 8,
        "single_micro_trade_only": True,
        "capital_allocation_requires_operator_approval": True,
        "paper_only_allocation_review": True,
    }


def test_capital_allocation_ready():
    result = evaluate_capital_allocation_gate(_metadata())
    assert result["capital_allocation_ready"] is True
    assert result["capital_allocation_status"] == STATUS_READY
    assert result["max_trade_risk_amount"] == 5.0
    assert result["max_daily_loss_amount"] == 20.0
    assert result["safety"]["capital_allocated"] is False


def test_missing_metadata_blocked():
    result = evaluate_capital_allocation_gate({"account_equity_declared": 1000})
    assert result["capital_allocation_ready"] is False
    assert result["capital_allocation_status"] == STATUS_MORE_INFO
    assert any(reason.startswith("missing_capital_allocation_metadata:") for reason in result["blocked_reasons"])


def test_invalid_account_equity_blocked():
    metadata = _metadata()
    metadata["account_equity_declared"] = 0
    result = evaluate_capital_allocation_gate(metadata)
    assert result["capital_allocation_status"] == STATUS_BLOCKED
    assert "capital_allocation_control_failed:account_equity_declared" in result["blocked_reasons"]


def test_trade_risk_too_high_blocked():
    metadata = _metadata()
    metadata["max_trade_risk_percent_declared"] = 2
    result = evaluate_capital_allocation_gate(metadata)
    assert "capital_allocation_control_failed:max_trade_risk_percent_declared" in result["blocked_reasons"]


def test_trade_risk_exceeds_account_risk_blocked():
    metadata = _metadata()
    metadata["max_account_risk_percent_declared"] = 0.25
    metadata["max_trade_risk_percent_declared"] = 0.5
    result = evaluate_capital_allocation_gate(metadata)
    assert "trade_risk_exceeds_account_risk_limit" in result["blocked_reasons"]


def test_daily_loss_below_trade_risk_blocked():
    metadata = _metadata()
    metadata["max_daily_loss_percent_declared"] = 0.25
    result = evaluate_capital_allocation_gate(metadata)
    assert "daily_loss_limit_below_trade_risk" in result["blocked_reasons"]


def test_single_micro_trade_required():
    metadata = _metadata()
    metadata["single_micro_trade_only"] = False
    result = evaluate_capital_allocation_gate(metadata)
    assert "capital_allocation_control_failed:single_micro_trade_only" in result["blocked_reasons"]


def test_operator_approval_required():
    metadata = _metadata()
    metadata["capital_allocation_requires_operator_approval"] = False
    result = evaluate_capital_allocation_gate(metadata)
    assert "capital_allocation_control_failed:capital_allocation_requires_operator_approval" in result["blocked_reasons"]


def test_deterministic_output():
    first = evaluate_capital_allocation_gate(_metadata())
    second = evaluate_capital_allocation_gate(_metadata())
    assert first == second


def test_safety_source_scan():
    source = open("automation/forex_engine/capital_allocation_gate.py", encoding="utf-8").read()
    forbidden = ["requests", "urllib", "socket", "subprocess", "os.environ", ".env", "http://", "https://"]
    for token in forbidden:
        assert token not in source


def test_forbidden_execution_state_absent():
    result = evaluate_capital_allocation_gate(_metadata())
    safety = result["safety"]
    assert safety["capital_allocated"] is False
    assert safety["capital_allocation_modified"] is False
    assert safety["broker_connection_active"] is False
    assert safety["credentials_accessed"] is False
    assert safety["network_access"] is False
    assert safety["order_execution_enabled"] is False
    assert safety["live_trading_authorized"] is False
