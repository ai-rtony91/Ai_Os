from pathlib import Path

from automation.forex_engine.demo_connector_readonly import evaluate_demo_connector_snapshot


def _snapshot_valid() -> dict:
    return {
        "mode": "DEMO_READONLY",
        "balance_is_present": True,
        "last_read_timestamp": "2026-06-20T00:00:00Z",
        "stale": False,
        "account_summary": {
            "balance_is_present": True,
            "balance": "10000.00",
            "currency": "USD",
            "instruments": ["EUR_USD", "GBP_USD"],
        },
        "prices": [
            {"instrument": "EUR_USD", "bid": "1.0920", "ask": "1.0922"},
            {"instrument": "GBP_USD", "bid": 1.27, "ask": 1.271},
        ],
        "positions_summary": [
            {"instrument": "EUR_USD", "status": "open", "units": 0.25},
            {"instrument": "GBP_USD", "status": "closed", "units": -0.5},
            {"instrument": "GBP_USD", "status": "open", "units": 1.0},
        ],
    }


def test_valid_sanitized_demo_snapshot_passes() -> None:
    snapshot = _snapshot_valid()
    result = evaluate_demo_connector_snapshot(
        snapshot,
        now_timestamp=1_760_000_000.0,
        max_data_age_seconds=3600.0,
    )

    assert result["allowed"] is True
    assert result["decision"] == "allowed"
    assert result["mode"] in ("DEMO_READONLY", "PAPER_ONLY_COMPATIBLE")
    assert result["demo_readonly"] is True
    assert result["paper_only"] is True
    assert result["fresh"] is True
    assert result["data_age_seconds"] is not None
    assert result["account_summary"]["balance_is_present"] is True
    assert result["account_summary"]["currency"] == "USD"
    assert "EUR_USD" in result["price_summary"]["instruments"][0]["instrument"]


def test_exact_account_identifier_blocks() -> None:
    snapshot = _snapshot_valid()
    snapshot["account_summary"] = {
        "account_id": "101-222-333333-001",
        "currency": "USD",
        "balance_is_present": True,
        "balance": 1000,
    }
    result = evaluate_demo_connector_snapshot(snapshot, now_timestamp=1_760_000_000.0)

    assert result["allowed"] is False
    assert result["decision"] == "blocked"
    assert result["blocked_reason"] == "account_identifier_detected"
    assert "account_identifier_detected" in result["blocked_reasons"]


def test_credentials_loaded_blocks() -> None:
    snapshot = _snapshot_valid()
    snapshot["credentials_loaded"] = True
    result = evaluate_demo_connector_snapshot(snapshot)

    assert result["allowed"] is False
    assert "runtime_material_present" in result["blocked_reasons"]


def test_live_trading_enabled_blocks() -> None:
    snapshot = _snapshot_valid()
    snapshot["live_trading_enabled"] = True
    result = evaluate_demo_connector_snapshot(snapshot)

    assert result["allowed"] is False
    assert "live_control_enabled" in result["blocked_reasons"]


def test_order_submit_enabled_blocks() -> None:
    snapshot = _snapshot_valid()
    snapshot["order_submit_enabled"] = True
    result = evaluate_demo_connector_snapshot(snapshot)

    assert result["allowed"] is False
    assert "order_submission_enabled" in result["blocked_reasons"]


def test_stale_snapshot_blocks() -> None:
    snapshot = _snapshot_valid()
    result = evaluate_demo_connector_snapshot(
        snapshot,
        now_timestamp=1_760_000_000.0,
        max_data_age_seconds=1.0,
    )

    assert result["allowed"] is False
    assert "stale_demo_data" in result["blocked_reasons"]
    assert result["fresh"] is False

def test_missing_balance_warning() -> None:
    snapshot = _snapshot_valid()
    snapshot["account_summary"] = {
        "balance_is_present": False,
        "currency": "USD",
        "instruments": ["EUR_USD"],
    }
    result = evaluate_demo_connector_snapshot(snapshot)

    assert result["allowed"] is True
    assert "missing_balance" in result["account_summary"]["warnings"]


def test_prices_normalized() -> None:
    snapshot = _snapshot_valid()
    snapshot["prices"] = [
        {"instrument": "eur_usd", "bid": "1.2", "ask": "1.2005"},
    ]
    result = evaluate_demo_connector_snapshot(snapshot)

    price = result["price_summary"]["instruments"][0]
    assert price["instrument"] == "EUR_USD"
    assert isinstance(price["bid"], float)
    assert isinstance(price["ask"], float)
    assert price["spread"] > 0


def test_positions_summarized() -> None:
    snapshot = _snapshot_valid()
    result = evaluate_demo_connector_snapshot(snapshot)

    assert result["position_summary"]["position_count"] == 3
    assert result["position_summary"]["open_position_count"] == 2
    assert result["position_summary"]["symbols"] == ["EUR_USD", "GBP_USD"]


def test_safety_dict_present_and_strict() -> None:
    result = evaluate_demo_connector_snapshot(_snapshot_valid())

    safety = result["safety"]
    assert safety["paper_only"] is True
    assert safety["demo_readonly"] is True
    assert safety["broker_write"] is False
    assert safety["live_trading"] is False
    assert safety["credentials"] is False
    assert safety["real_orders"] is False
    assert safety["network_submit"] is False


def test_source_scan_blocks_forbidden_runtime_apis() -> None:
    module_path = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "demo_connector_readonly.py"
    source = module_path.read_text(encoding="utf-8").lower()

    for token in (
        "subprocess",
        "requests",
        "socket",
        "urllib",
        "open(",
        "write_text(",
        "pathlib",
        "os.system",
        "getenv",
        "environ",
        "secret",
        "account_id",
        "credential",
    ):
        assert token not in source
