import pytest

from automation.forex_engine.config import ForexEngineConfig, validate_config


def test_default_config_values_are_paper_only():
    config = ForexEngineConfig()
    assert config.mode == "PAPER_ONLY"
    assert config.starting_balance_usd == 500.0
    assert {"EURUSD", "GBPUSD", "USDJPY", "XAUUSD"}.issubset(config.symbols)
    assert config.paper_risk_per_trade_pct == 0.5
    assert config.first_live_risk_target_pct == 0.25
    assert config.max_daily_drawdown_pct == 2.0
    assert config.max_open_trades_paper == 2


def test_config_validation_passes():
    validate_config(ForexEngineConfig())


def test_invalid_mode_fails_validation():
    with pytest.raises(ValueError, match="PAPER_ONLY"):
        validate_config(ForexEngineConfig(mode="LIVE"))
