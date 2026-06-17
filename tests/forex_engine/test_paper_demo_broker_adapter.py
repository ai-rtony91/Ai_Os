from __future__ import annotations

from pathlib import Path

from automation.forex_engine import paper_demo_broker_adapter


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "paper_demo_broker_adapter.py"
DOC_PATH = (
    REPO_ROOT
    / "docs"
    / "trading_lab"
    / "AIOS_FOREX_BUILDER_BROKER_PAPER_DEMO_ADAPTER.md"
)


def _adapter() -> paper_demo_broker_adapter.PaperDemoBrokerAdapter:
    adapter = paper_demo_broker_adapter.PaperDemoBrokerAdapter()
    adapter.connect()
    adapter.authenticate()
    return adapter


def _order(**overrides):
    payload = {
        "client_order_id": "test-paper-demo-order",
        "instrument": "EUR_USD",
        "side": "BUY",
        "order_type": "MARKET",
        "units": 1,
        "entry_reference_price": 1.08,
        "stop_loss": 1.075,
        "take_profit": 1.09,
        "max_loss_usd": 1.0,
    }
    payload.update(overrides)
    return payload


def test_contract_and_doc_exist_and_block_live_capabilities() -> None:
    contract = paper_demo_broker_adapter.build_paper_demo_broker_adapter_contract()

    assert MODULE_PATH.exists()
    assert DOC_PATH.exists()
    assert contract["mode"] == "PAPER_DEMO"
    assert "connect" in contract["supported_capabilities"]
    assert "evidence_generation" in contract["supported_capabilities"]
    assert contract["unsupported_actions_fail_closed"] is True
    for field in (
        "broker_sdk_allowed",
        "network_api_allowed",
        "credentials_allowed",
        "env_secret_read_allowed",
        "broker_paper_orders_allowed",
        "live_orders_allowed",
        "live_execution_allowed",
        "live_ready",
        "live_trade_ready",
        "real_order_ready",
        "would_place_order",
        "order_placed",
        "broker_request_sent",
        "network_used",
        "credentials_used",
    ):
        assert contract[field] is False


def test_connect_returns_paper_demo_connection_only() -> None:
    adapter = paper_demo_broker_adapter.PaperDemoBrokerAdapter()
    result = adapter.connect()

    assert result["status"] == "PAPER_DEMO_CONNECTED"
    assert result["connected"] is True
    assert result["broker_connection_allowed"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["live_execution_allowed"] is False


def test_authenticate_returns_local_paper_demo_session_without_credentials() -> None:
    adapter = paper_demo_broker_adapter.PaperDemoBrokerAdapter()
    adapter.connect()

    result = adapter.authenticate()

    assert result["status"] == "PAPER_DEMO_AUTHENTICATED"
    assert result["authenticated"] is True
    assert result["credential_material_required"] is False
    assert result["credential_material_present"] is False
    assert result["credentials_used"] is False
    assert result["network_used"] is False


def test_authenticate_requires_connect_first() -> None:
    result = paper_demo_broker_adapter.PaperDemoBrokerAdapter().authenticate()

    assert result["blocked"] is True
    assert "connect_required_before_authenticate" in result["blockers"]
    assert result["live_execution_allowed"] is False


def test_market_data_contract_uses_local_fixture_only() -> None:
    result = _adapter().get_market_data("EUR_USD")

    assert result["status"] == "LOCAL_MARKET_DATA_READY"
    assert result["instrument"] == "EUR_USD"
    assert result["source"] == "LOCAL_DETERMINISTIC_FIXTURE"
    assert result["price"] > 0
    assert result["spread_pips"] <= 1.5
    assert result["live_market_data"] is False
    assert result["network_used"] is False


def test_account_state_contract_is_sanitized_paper_state() -> None:
    result = _adapter().get_account_state()

    assert result["status"] == "SANITIZED_PAPER_ACCOUNT_STATE"
    assert result["account_mode"] == "PAPER_DEMO"
    assert result["available_margin_usd"] > 0
    assert result["live_account_data"] is False
    assert result["credentials_used"] is False
    assert result["live_ready"] is False


def test_order_create_generates_simulated_fill_and_open_position() -> None:
    result = _adapter().create_order(_order())

    assert result["status"] == "PAPER_ORDER_ACCEPTED"
    assert result["order_status"] == "PAPER_FILL_SIMULATED"
    assert result["order_accepted"] is True
    assert result["paper_order_id"].startswith("AIOS-PAPER-ORDER-")
    assert result["fill"]["status"] == "PAPER_FILL_SIMULATED"
    assert result["fill"]["fill_verified"] is True
    assert result["position"]["status"] == "PAPER_POSITION_OPEN"
    assert result["would_place_order"] is False
    assert result["order_placed"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["live_order"] is False


def test_order_rejects_invalid_instrument_without_side_effects() -> None:
    result = _adapter().create_order(_order(instrument="AUD_USD"))

    assert result["status"] == "PAPER_ORDER_REJECTED"
    assert result["order_accepted"] is False
    assert "instrument_not_allowlisted" in result["blockers"]
    assert result["fill"] is None
    assert result["position"] is None
    assert result["order_placed"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False


def test_order_rejects_missing_stop_loss() -> None:
    result = _adapter().create_order(_order(stop_loss=None))

    assert result["status"] == "PAPER_ORDER_REJECTED"
    assert "stop_loss_required" in result["blockers"]
    assert result["live_orders_allowed"] is False


def test_order_rejects_oversized_units() -> None:
    result = _adapter().create_order(_order(units=2))

    assert result["status"] == "PAPER_ORDER_REJECTED"
    assert "units_exceed_paper_demo_limit" in result["blockers"]
    assert result["broker_paper_orders_allowed"] is False


def test_fill_generation_contract_is_sanitized() -> None:
    result = _adapter().create_order(_order())
    fill = result["fill"]

    assert fill["schema"] == "AIOS_PAPER_DEMO_FILL.v1"
    assert fill["fill_id"].startswith("AIOS-PAPER-FILL-")
    assert fill["paper_order_id"] == result["paper_order_id"]
    assert fill["filled_units"] == 1
    assert fill["fill_price"] > 0
    assert fill["broker_request_sent"] is False
    assert fill["network_used"] is False
    assert fill["live_order"] is False


def test_position_state_and_close_capture_pl() -> None:
    adapter = _adapter()
    order = adapter.create_order(_order())
    position_state = adapter.get_position_state()

    assert position_state["open_position_count"] == 1
    assert position_state["positions"][0]["status"] == "PAPER_POSITION_OPEN"

    position_id = order["position"]["position_id"]
    close = adapter.close_position(position_id, close_price=order["fill_price"])

    assert close["status"] == "PAPER_POSITION_CLOSED"
    assert close["position_closed"] is True
    assert close["realized_pl_usd"] == 0.0
    assert close["pl_capture_status"] == "RECORDED"
    assert adapter.get_position_state()["open_position_count"] == 0


def test_evidence_creation_records_sanitized_events() -> None:
    adapter = _adapter()
    order = adapter.create_order(_order())
    adapter.close_position(order["position"]["position_id"], close_price=order["fill_price"])

    evidence = adapter.build_evidence_bundle()

    assert evidence["status"] == "PAPER_DEMO_EVIDENCE_READY"
    assert evidence["archive_status"] == "IN_MEMORY_ONLY"
    assert evidence["sanitized"] is True
    assert evidence["contains_private_data"] is False
    assert evidence["contains_real_credentials"] is False
    assert evidence["event_count"] >= 6
    assert {event["event"] for event in evidence["events"]} >= {
        "connect",
        "authenticate",
        "order_create",
        "fill",
        "position_open",
        "position_close",
    }


def test_unsupported_broker_actions_fail_closed() -> None:
    result = _adapter().perform_unsupported_action("replace_order")

    assert result["status"] == "UNSUPPORTED_ACTION_BLOCKED"
    assert "unsupported_broker_action" in result["blockers"]
    assert result["order_placed"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["live_orders_allowed"] is False


def test_live_execution_rejection() -> None:
    result = _adapter().submit_live_order({"mode": "LIVE"})

    assert result["status"] == "LIVE_EXECUTION_BLOCKED"
    assert "live_execution_blocked" in result["blockers"]
    assert "live_mode_blocked" in result["blockers"]
    assert result["live_execution_allowed"] is False
    assert result["live_orders_allowed"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False


def test_payload_with_secret_like_fields_fails_closed() -> None:
    result = _adapter().create_order(_order(api_key="EXAMPLE_NOT_A_REAL_VALUE"))

    assert result["status"] == "PAPER_ORDER_REJECTED"
    assert "forbidden_field:api_key" in result["blockers"]
    assert result["order_placed"] is False
    assert result["broker_request_sent"] is False
    assert result["credentials_used"] is False


def test_modules_have_no_forbidden_imports_or_execution_calls() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    import_lines = "\n".join(
        line.strip()
        for line in source.splitlines()
        if line.startswith("import ") or line.startswith("from ")
    )

    for forbidden_import in ("requests", "socket", "urllib", "subprocess", "dotenv", "mt5", "ibkr"):
        assert forbidden_import not in import_lines
    for line in import_lines.splitlines():
        assert not line.startswith("import broker")
        assert not line.startswith("from broker")
        assert not line.startswith("import oanda")
        assert not line.startswith("from oanda")
    for forbidden_call in (
        "os.environ",
        "getenv",
        "open(",
        "write_text(",
        "write_bytes(",
        "start-process",
        "schedule.every",
        "daemon.daemoncontext",
    ):
        assert forbidden_call not in source

