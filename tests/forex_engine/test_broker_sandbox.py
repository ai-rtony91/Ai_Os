from pathlib import Path

from automation.forex_engine.broker_sandbox import BrokerSandbox, PLACEHOLDER_PRICES
from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.models import (
    BrokerReadinessStatus,
    BrokerSandboxMode,
    SandboxOrderRequest,
    SandboxOrderSide,
    SandboxOrderStatus,
    SandboxOrderType,
    SandboxRejectReason,
)


def _request(**overrides):
    data = {
        "mode": BrokerSandboxMode.SANDBOX_MODEL_ONLY,
        "symbol": "EURUSD",
        "side": SandboxOrderSide.BUY,
        "order_type": SandboxOrderType.MARKET,
        "units": 1000,
        "requested_price": 1.08,
        "client_order_id": "test-order",
        "metadata": {},
    }
    data.update(overrides)
    return SandboxOrderRequest(**data)


def test_sandbox_accepts_valid_market_order():
    response = BrokerSandbox(ForexEngineConfig()).submit_order(_request())
    assert response.status == SandboxOrderStatus.FILLED
    assert response.reject_reason == SandboxRejectReason.NONE


def test_sandbox_rejects_invalid_symbol():
    response = BrokerSandbox(ForexEngineConfig()).submit_order(_request(symbol="AUDCAD"))
    assert response.reject_reason == SandboxRejectReason.INVALID_SYMBOL


def test_sandbox_rejects_invalid_units():
    response = BrokerSandbox(ForexEngineConfig()).submit_order(_request(units=0))
    assert response.reject_reason == SandboxRejectReason.INVALID_UNITS


def test_sandbox_rejects_invalid_side():
    response = BrokerSandbox(ForexEngineConfig()).submit_order(_request(side="LONG"))
    assert response.reject_reason == SandboxRejectReason.INVALID_SIDE


def test_sandbox_rejects_invalid_order_type():
    response = BrokerSandbox(ForexEngineConfig()).submit_order(_request(order_type="IOC"))
    assert response.reject_reason == SandboxRejectReason.INVALID_ORDER_TYPE


def test_sandbox_blocks_live_mode():
    response = BrokerSandbox(ForexEngineConfig()).submit_order(_request(mode="LIVE"))
    assert response.status == SandboxOrderStatus.LIVE_BLOCKED
    assert response.reject_reason == SandboxRejectReason.LIVE_TRADING_BLOCKED


def test_sandbox_rejects_credential_metadata():
    response = BrokerSandbox(ForexEngineConfig()).submit_order(_request(metadata={"api_key": "blocked"}))
    assert response.reject_reason == SandboxRejectReason.CREDENTIALS_NOT_ALLOWED


def test_sandbox_network_disabled():
    assert BrokerSandbox(ForexEngineConfig()).account_state.network_enabled is False


def test_sandbox_credentials_not_loaded():
    assert BrokerSandbox(ForexEngineConfig()).account_state.credentials_loaded is False


def test_market_order_uses_placeholder_price_when_no_price():
    response = BrokerSandbox(ForexEngineConfig()).submit_order(_request(requested_price=None))
    assert response.fill_price == PLACEHOLDER_PRICES["EURUSD"]


def test_limit_order_model_only_pending_or_clear_response():
    response = BrokerSandbox(ForexEngineConfig()).submit_order(
        _request(order_type=SandboxOrderType.LIMIT, requested_price=1.075)
    )
    assert response.status == SandboxOrderStatus.PENDING
    assert "model-only" in response.message


def test_rejected_order_count_increments():
    sandbox = BrokerSandbox(ForexEngineConfig())
    sandbox.submit_order(_request(symbol="AUDCAD"))
    assert sandbox.account_state.rejected_order_count == 1


def test_filled_order_count_increments():
    sandbox = BrokerSandbox(ForexEngineConfig())
    sandbox.submit_order(_request())
    assert sandbox.account_state.filled_order_count == 1


def test_readiness_check_not_live_ready():
    check = BrokerSandbox(ForexEngineConfig()).build_readiness_check()
    assert check.status in (
        BrokerReadinessStatus.NOT_LIVE_READY,
        BrokerReadinessStatus.REQUIRES_SEPARATE_AUTHORIZATION,
    )


def test_readiness_check_lists_blocked_reasons():
    check = BrokerSandbox(ForexEngineConfig()).build_readiness_check()
    reasons = " ".join(check.blocked_reasons)
    assert "credentials" in reasons
    assert "live authorization" in reasons


def test_broker_sandbox_demo_imports_without_network():
    import automation.forex_engine.run_broker_sandbox_demo as demo

    assert demo.main


def test_existing_demos_still_import():
    import automation.forex_engine.run_backtest_demo as backtest_demo
    import automation.forex_engine.run_confidence_demo as confidence_demo
    import automation.forex_engine.run_market_data_demo as market_data_demo
    import automation.forex_engine.run_paper_demo as paper_demo
    import automation.forex_engine.run_paper_operator_demo as paper_operator_demo
    import automation.forex_engine.run_signal_rules_demo as signal_rules_demo
    import automation.forex_engine.run_strategy_comparison_demo as strategy_comparison_demo
    import automation.forex_engine.run_walk_forward_demo as walk_forward_demo

    assert backtest_demo.main
    assert confidence_demo.main
    assert market_data_demo.main
    assert paper_demo.main
    assert paper_operator_demo.main
    assert signal_rules_demo.main
    assert strategy_comparison_demo.main
    assert walk_forward_demo.main


def test_no_live_trading_demo_created():
    assert not Path("automation/forex_engine/run_live_trading_demo.py").exists()
