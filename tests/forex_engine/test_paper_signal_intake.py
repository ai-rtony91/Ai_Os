import socket

from automation.forex_engine.models import Direction, EngineMode
from automation.forex_engine.paper_signal_intake import (
    PAPER_SIGNAL_INTAKE_SCHEMA,
    build_demo_local_signal,
    build_unsafe_demo_local_signal,
    evaluate_local_signal_for_ledger,
)
from automation.forex_engine.models import ForexSignal
from automation.forex_engine.readiness import PAPER_READY, PAPER_REJECTED


def test_valid_mock_signal_creates_accepted_paper_ledger_record():
    record = evaluate_local_signal_for_ledger(
        {
            "symbol": "EURUSD",
            "timeframe": "5m",
            "direction": Direction.BUY,
            "entry_price": 1.0800,
            "stop_loss": 1.0790,
            "take_profit": 1.0820,
            "timestamp": "2026-06-12T00:00:00Z",
            "strategy_name": "paper_fixture_accept",
            "metadata": {"source": "local_fixture"},
        },
        signal_id="signal_accept_001",
        generated_at_utc="2026-06-12T00:00:00Z",
    )

    assert record["schema"] == PAPER_SIGNAL_INTAKE_SCHEMA
    assert record["mode"] == EngineMode.PAPER_ONLY
    assert record["readiness_status"] == PAPER_READY
    assert record["accepted_for_paper"] is True
    assert record["execution_allowed"] is False
    assert record["signal_summary"]["symbol"] == "EURUSD"
    assert record["signal_summary"]["direction"] == Direction.BUY
    assert record["signal_id"] == "signal_accept_001"


def test_object_input_signal_is_accepted_by_ledger():
    record = evaluate_local_signal_for_ledger(
        ForexSignal(
            symbol="EURUSD",
            timeframe="5m",
            direction=Direction.BUY,
            entry_price=1.0800,
            stop_loss=1.0790,
            take_profit=1.0820,
            timestamp="2026-06-12T00:00:00Z",
            strategy_name="paper_fixture_object_input",
            metadata={"source": "local_fixture"},
        ),
        signal_id="object_input_001",
        generated_at_utc="2026-06-12T00:00:00Z",
    )

    assert record["readiness_status"] == PAPER_READY
    assert record["accepted_for_paper"] is True
    assert record["signal_id"] == "object_input_001"


def test_invalid_mock_signal_creates_rejected_paper_ledger_record():
    # Create a structurally invalid signal
    invalid = build_demo_local_signal(signal_id="invalid_prices")
    invalid["direction"] = Direction.SELL
    invalid["entry_price"] = 1.0800
    invalid["stop_loss"] = 1.0790
    invalid["take_profit"] = 1.0795

    record = evaluate_local_signal_for_ledger(
        invalid,
        signal_id="signal_reject_001",
        generated_at_utc="2026-06-12T00:00:00Z",
    )

    assert record["readiness_status"] == PAPER_REJECTED
    assert record["accepted_for_paper"] is False
    assert record["execution_allowed"] is False
    assert record["readiness_status"] == PAPER_REJECTED
    assert record["blocked_actions"], "blocked actions must be present"


def test_unsafe_metadata_fields_are_flagged_or_rejected():
    record = evaluate_local_signal_for_ledger(
        build_unsafe_demo_local_signal(),
        signal_id="signal_unsafe_001",
        generated_at_utc="2026-06-12T00:00:00Z",
    )
    assert record["accepted_for_paper"] is False
    assert record["readiness_status"] == PAPER_REJECTED
    assert record["signal_summary"]["metadata"]["api_key"] == "blocked-key"
    assert "unsafe_external_metadata" in record["risk_flags"]
    assert any("api_key" in reason for reason in record["reasons"])
    assert any("webhook_url" in reason for reason in record["reasons"])


def test_execution_allowed_is_always_false_and_blocked_actions_are_present():
    record = evaluate_local_signal_for_ledger(
        build_demo_local_signal("demo_safe_blocked_001"),
        generated_at_utc="2026-06-12T00:00:00Z",
    )

    assert record["execution_allowed"] is False
    assert set(["broker_api_call", "oanda_api_call", "real_order_submission"]).issubset(
        set(record["blocked_actions"])
    )
    assert "webhook_execution" in record["blocked_actions"]
    assert "secret_or_api_key_load" in record["blocked_actions"]


def test_output_is_deterministic_when_timestamp_and_signal_id_are_supplied():
    signal = build_demo_local_signal("deterministic_001")
    first = evaluate_local_signal_for_ledger(
        signal,
        signal_id="deterministic_record_001",
        generated_at_utc="2026-06-12T00:00:00Z",
    )
    second = evaluate_local_signal_for_ledger(
        signal,
        signal_id="deterministic_record_001",
        generated_at_utc="2026-06-12T00:00:00Z",
    )
    assert first == second


def test_evaluate_local_signal_for_ledger_rejects_network_interaction_attempts(monkeypatch):
    created = []

    def blocked_socket(*args, **kwargs):
        created.append((args, kwargs))
        raise AssertionError("No external network calls are allowed.")

    monkeypatch.setattr(socket, "socket", blocked_socket)

    record = evaluate_local_signal_for_ledger(
        build_demo_local_signal("network_guard_001"),
        generated_at_utc="2026-06-12T00:00:00Z",
    )

    assert created == []
    assert record["schema"] == PAPER_SIGNAL_INTAKE_SCHEMA
