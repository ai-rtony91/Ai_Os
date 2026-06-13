import json

from automation.forex_engine.models import Direction, ForexSignal
from automation.forex_engine.readiness import (
    BLOCKED_ACTIONS,
    PAPER_READY,
    PAPER_REJECTED,
    build_unsafe_mock_signal,
    build_valid_mock_signal,
    evaluate_paper_readiness,
)
from automation.forex_engine.run_readiness_demo import main as readiness_demo_main


def test_valid_mock_signal_is_paper_ready():
    result = evaluate_paper_readiness(build_valid_mock_signal())

    assert result["status"] == PAPER_READY
    assert result["accepted_for_paper"] is True
    assert result["execution_allowed"] is False
    assert result["paper_only"] is True
    assert result["risk_flags"] == []
    assert result["confidence"]["allowed"] is True
    assert result["risk"]["allowed"] is True
    assert result["next_safe_action"]


def test_unsafe_mock_signal_is_rejected():
    result = evaluate_paper_readiness(build_unsafe_mock_signal())

    assert result["status"] == PAPER_REJECTED
    assert result["accepted_for_paper"] is False
    assert result["execution_allowed"] is False
    assert "unsafe_external_metadata" in result["risk_flags"]
    assert "api_key" in result["reason"]
    assert "webhook_url" in result["reason"]
    assert result["next_safe_action"]


def test_invalid_signal_is_rejected_with_reason_and_blocked_actions():
    invalid_signal = ForexSignal(
        symbol="EURUSD",
        timeframe="5m",
        direction=Direction.BUY,
        entry_price=1.0800,
        stop_loss=1.0810,
        take_profit=1.0790,
        timestamp="2026-06-12T00:00:00Z",
        strategy_name="invalid_price_fixture",
        metadata={"source": "local_fixture"},
    )

    result = evaluate_paper_readiness(invalid_signal)

    assert result["status"] == PAPER_REJECTED
    assert result["accepted_for_paper"] is False
    assert "input_validation_failed" in result["risk_flags"]
    assert "BUY signal requires stop below entry" in result["reason"]
    assert result["blocked_actions"] == list(BLOCKED_ACTIONS)
    assert result["next_safe_action"]


def test_external_execution_paths_remain_disabled():
    result = evaluate_paper_readiness(build_valid_mock_signal())

    assert result["blocked_actions"] == list(BLOCKED_ACTIONS)
    assert result["execution_allowed"] is False
    assert all(value is True for value in result["safety"].values())
    assert result["safety"]["no_live_trading"] is True
    assert result["safety"]["no_broker_apis"] is True
    assert result["safety"]["no_oanda"] is True
    assert result["safety"]["no_webhooks"] is True
    assert result["safety"]["no_real_market_data"] is True
    assert result["safety"]["no_real_orders"] is True
    assert result["safety"]["no_api_keys_or_secrets"] is True
    assert "broker_api_call" in result["blocked_actions"]
    assert "webhook_execution" in result["blocked_actions"]
    assert "secret_or_api_key_load" in result["blocked_actions"]


def test_readiness_output_contains_required_evidence_fields():
    result = evaluate_paper_readiness(build_valid_mock_signal())

    for key in ("reason", "risk_flags", "blocked_actions", "next_safe_action"):
        assert key in result
    assert result["reason"]
    assert isinstance(result["risk_flags"], list)
    assert isinstance(result["blocked_actions"], list)
    assert result["next_safe_action"]


def test_readiness_demo_outputs_deterministic_json(capsys):
    exit_code = readiness_demo_main()
    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 0
    assert result["status"] == PAPER_READY
    assert result["signal"]["timestamp"] == "2026-06-12T00:00:00Z"
    assert result["execution_allowed"] is False
