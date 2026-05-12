from pathlib import Path

import pytest

from aios.modules.trader.payloads.alert_payload import build_mock_alert_payload


def test_payload_defaults_to_paper_only_true():
    payload = build_mock_alert_payload("EURUSD", "1h", "bullish", "BUY", 0.8)

    assert payload["paper_only"] is True


def test_payload_defaults_live_execution_status_blocked():
    payload = build_mock_alert_payload("EURUSD", "1h", "bullish", "BUY", 0.8)

    assert payload["live_execution_status"] == "BLOCKED"


def test_payload_defaults_execution_allowed_false():
    payload = build_mock_alert_payload("EURUSD", "1h", "bullish", "BUY", 0.8)

    assert payload["execution_allowed"] is False


def test_payload_route_status_is_mock_only():
    payload = build_mock_alert_payload("EURUSD", "1h", "bullish", "BUY", 0.8)

    assert payload["route_status"] == "MOCK_ONLY"


def test_invalid_permission_fails():
    with pytest.raises(ValueError):
        build_mock_alert_payload("EURUSD", "1h", "invalid", "BUY", 0.8)


def test_invalid_signal_fails():
    with pytest.raises(ValueError):
        build_mock_alert_payload("EURUSD", "1h", "bullish", "WAIT", 0.8)


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_confidence_outside_zero_to_one_fails(confidence):
    with pytest.raises(ValueError):
        build_mock_alert_payload("EURUSD", "1h", "bullish", "BUY", confidence)


def test_payload_does_not_contain_blocked_routing_fields():
    payload = build_mock_alert_payload("EURUSD", "1h", "bullish", "BUY", 0.8)
    blocked = [
        "webhook" + "_url",
        "broker",
        "api" + "_key",
        "secret" + "_key",
        "live" + "_order",
        "real" + "_order",
    ]

    for key in blocked:
        assert key not in payload


def test_metadata_with_blocked_routing_field_fails():
    with pytest.raises(ValueError):
        build_mock_alert_payload(
            "EURUSD",
            "1h",
            "bullish",
            "BUY",
            0.8,
            {"api" + "_key": "not-allowed"},
        )


def test_payload_source_file_avoids_literal_sensitive_tokens():
    source = Path("aios/modules/trader/payloads/alert_payload.py").read_text()
    blocked = [
        "webhook" + "_url",
        "api" + "_key",
        "secret" + "_key",
        "live" + "_order",
        "real" + "_order",
    ]

    for token in blocked:
        assert token not in source.lower()
