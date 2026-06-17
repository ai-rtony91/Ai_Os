from __future__ import annotations

from pathlib import Path

from automation.forex_engine import broker_specific_paper_demo
from automation.forex_engine import paper_demo_broker_adapter


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "broker_specific_paper_demo.py"
DOC_PATH = (
    REPO_ROOT
    / "docs"
    / "trading_lab"
    / "AIOS_FOREX_BUILDER_OANDA_PAPER_DEMO_MAPPING.md"
)


def _adapter_outputs() -> dict[str, dict[str, object]]:
    adapter = paper_demo_broker_adapter.PaperDemoBrokerAdapter()
    adapter.connect()
    adapter.authenticate()
    market = adapter.get_market_data("EUR_USD")
    account = adapter.get_account_state()
    order = adapter.create_order(
        {
            "client_order_id": "test-broker-specific-order",
            "instrument": "EUR_USD",
            "side": "BUY",
            "order_type": "MARKET",
            "units": 1,
            "entry_reference_price": 1.08,
            "stop_loss": 1.075,
            "take_profit": 1.09,
            "max_loss_usd": 1.0,
        }
    )
    return {
        "market": market,
        "account": account,
        "order": order,
        "fill": order["fill"],
        "evidence": adapter.build_evidence_bundle(),
    }


def test_broker_target_is_oanda_and_doc_exists() -> None:
    requirements = broker_specific_paper_demo.build_broker_specific_paper_demo_interface_requirements()

    assert MODULE_PATH.exists()
    assert DOC_PATH.exists()
    assert requirements["broker_id"] == "OANDA"
    assert requirements["broker_reference"] == "OANDA_PAPER_DEMO_REFERENCE_ONLY"
    assert requirements["external_auth_reference_required"] is True
    assert requirements["repo_stored_auth_material_allowed"] is False
    assert requirements["network_api_allowed"] is False
    assert requirements["live_execution_allowed"] is False


def test_broker_config_validation_accepts_paper_demo_reference_only() -> None:
    result = broker_specific_paper_demo.validate_broker_specific_paper_demo_config()

    assert result["status"] == "BROKER_SPECIFIC_PAPER_DEMO_CONFIG_READY"
    assert result["config_valid"] is True
    assert result["broker_id"] == "OANDA"
    assert result["account_mode"] == "PRACTICE_DEMO"
    assert result["external_auth_reference_present"] is True
    assert result["credential_material_present"] is False
    assert result["repo_stored_auth_material_allowed"] is False
    assert result["network_api_allowed"] is False
    assert result["live_execution_allowed"] is False


def test_missing_credential_readiness_rejects_fail_closed() -> None:
    config = broker_specific_paper_demo.BrokerSpecificPaperDemoConfig(
        external_auth_reference_present=False
    )

    result = broker_specific_paper_demo.validate_broker_specific_paper_demo_config(config)

    assert result["status"] == "BROKER_SPECIFIC_PAPER_DEMO_CONFIG_BLOCKED"
    assert result["config_valid"] is False
    assert "missing_external_auth_reference" in result["blockers"]
    assert result["credentials_allowed"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False


def test_unsupported_account_mode_rejects_fail_closed() -> None:
    result = broker_specific_paper_demo.validate_broker_specific_paper_demo_config(
        {"broker_id": "OANDA", "account_mode": "LIVE", "external_auth_reference_present": True}
    )

    assert result["config_valid"] is False
    assert "unsupported_account_mode" in result["blockers"]
    assert "live_account_mode_blocked" in result["blockers"]
    assert result["live_execution_allowed"] is False
    assert result["live_orders_allowed"] is False


def test_sensitive_config_fields_reject_fail_closed() -> None:
    result = broker_specific_paper_demo.validate_broker_specific_paper_demo_config(
        {
            "broker_id": "OANDA",
            "account_mode": "PRACTICE_DEMO",
            "external_auth_reference_present": True,
            "api_key": "NOT_A_REAL_VALUE",
        }
    )

    assert result["config_valid"] is False
    assert "forbidden_field:api_key" in result["blockers"]
    assert result["credentials_used"] is False
    assert result["broker_request_sent"] is False


def test_account_state_mapping_is_sanitized_oanda_shape() -> None:
    outputs = _adapter_outputs()
    result = broker_specific_paper_demo.map_broker_specific_account_state(outputs["account"])

    assert result["schema"] == "AIOS_OANDA_PAPER_DEMO_ACCOUNT_STATE_MAPPING.v1"
    assert result["broker_id"] == "OANDA"
    assert result["status"] == "BROKER_SPECIFIC_PAPER_DEMO_MAPPING_READY"
    assert result["account_mode"] == "PRACTICE_DEMO"
    assert result["account_identifier_present"] is False
    assert result["live_account_data"] is False
    assert result["sanitized"] is True
    assert result["network_used"] is False


def test_market_data_mapping_is_oanda_instrument_shape_without_network() -> None:
    outputs = _adapter_outputs()
    result = broker_specific_paper_demo.map_broker_specific_market_data(outputs["market"])

    assert result["schema"] == "AIOS_OANDA_PAPER_DEMO_MARKET_DATA_MAPPING.v1"
    assert result["oanda_instrument"] == "EUR_USD"
    assert result["quote_type"] == "PRICE_REFERENCE_ONLY"
    assert result["mid_price"] > 0
    assert result["live_market_data"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False


def test_order_state_mapping_is_oanda_preview_only() -> None:
    outputs = _adapter_outputs()
    result = broker_specific_paper_demo.map_broker_specific_order_state(outputs["order"])

    assert result["schema"] == "AIOS_OANDA_PAPER_DEMO_ORDER_STATE_MAPPING.v1"
    assert result["oanda_instrument"] == "EUR_USD"
    assert result["oanda_order_type"] == "MARKET"
    assert result["oanda_units_preview"] == 1
    assert result["time_in_force_preview"] == "FOK"
    assert result["route_allowed"] is False
    assert result["would_place_order"] is False
    assert result["order_placed"] is False
    assert result["broker_request_sent"] is False


def test_sell_order_state_mapping_uses_negative_oanda_units_preview() -> None:
    adapter = paper_demo_broker_adapter.PaperDemoBrokerAdapter()
    adapter.connect()
    adapter.authenticate()
    order = adapter.create_order(
        {
            "client_order_id": "test-sell-order",
            "instrument": "EUR_USD",
            "side": "SELL",
            "order_type": "MARKET",
            "units": 1,
            "entry_reference_price": 1.08,
            "stop_loss": 1.085,
            "take_profit": 1.07,
            "max_loss_usd": 1.0,
        }
    )

    result = broker_specific_paper_demo.map_broker_specific_order_state(order)

    assert result["oanda_units_preview"] == -1
    assert result["broker_request_sent"] is False


def test_fill_state_mapping_is_reference_only() -> None:
    outputs = _adapter_outputs()
    result = broker_specific_paper_demo.map_broker_specific_fill_state(outputs["fill"])

    assert result["schema"] == "AIOS_OANDA_PAPER_DEMO_FILL_STATE_MAPPING.v1"
    assert result["oanda_transaction_type_preview"] == "ORDER_FILL_REFERENCE_ONLY"
    assert result["oanda_transaction_identifier_present"] is False
    assert result["fill_verified"] is True
    assert result["live_order"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False


def test_evidence_mapping_is_sanitized_and_ready() -> None:
    outputs = _adapter_outputs()
    account_mapping = broker_specific_paper_demo.map_broker_specific_account_state(outputs["account"])
    market_mapping = broker_specific_paper_demo.map_broker_specific_market_data(outputs["market"])
    order_mapping = broker_specific_paper_demo.map_broker_specific_order_state(outputs["order"])
    fill_mapping = broker_specific_paper_demo.map_broker_specific_fill_state(outputs["fill"])

    result = broker_specific_paper_demo.build_broker_specific_evidence_mapping(
        account_mapping=account_mapping,
        market_mapping=market_mapping,
        order_mapping=order_mapping,
        fill_mapping=fill_mapping,
        source_evidence=outputs["evidence"],
    )

    assert result["schema"] == "AIOS_OANDA_PAPER_DEMO_EVIDENCE_MAPPING.v1"
    assert result["status"] == "BROKER_SPECIFIC_PAPER_DEMO_MAPPING_READY"
    assert result["evidence_ready"] is True
    assert result["sanitized"] is True
    assert result["contains_private_data"] is False
    assert result["contains_real_credentials"] is False
    assert result["network_used"] is False


def test_mapping_set_wires_all_broker_specific_mappings() -> None:
    outputs = _adapter_outputs()
    result = broker_specific_paper_demo.build_broker_specific_paper_demo_mapping_set(
        account_state=outputs["account"],
        market_data=outputs["market"],
        order_state=outputs["order"],
        fill_state=outputs["fill"],
        source_evidence=outputs["evidence"],
    )

    assert result["status"] == "BROKER_SPECIFIC_PAPER_DEMO_MAPPING_READY"
    assert result["config_validation"]["config_valid"] is True
    assert result["account_mapping"]["broker_id"] == "OANDA"
    assert result["market_data_mapping"]["oanda_instrument"] == "EUR_USD"
    assert result["order_state_mapping"]["oanda_order_type"] == "MARKET"
    assert result["fill_state_mapping"]["fill_verified"] is True
    assert result["evidence_mapping"]["evidence_ready"] is True
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False


def test_mapping_set_blocks_when_config_is_missing_external_auth_reference() -> None:
    outputs = _adapter_outputs()
    config = broker_specific_paper_demo.BrokerSpecificPaperDemoConfig(
        external_auth_reference_present=False
    )

    result = broker_specific_paper_demo.build_broker_specific_paper_demo_mapping_set(
        config=config,
        account_state=outputs["account"],
        market_data=outputs["market"],
        order_state=outputs["order"],
        fill_state=outputs["fill"],
        source_evidence=outputs["evidence"],
    )

    assert result["status"] == "BROKER_SPECIFIC_PAPER_DEMO_MAPPING_BLOCKED"
    assert result["config_validation"]["config_valid"] is False
    assert "missing_external_auth_reference" in result["evidence_mapping"]["blockers"]
    assert result["broker_request_sent"] is False
    assert result["live_execution_allowed"] is False


def test_live_execution_rejection_remains_fail_closed() -> None:
    result = broker_specific_paper_demo.reject_broker_specific_live_execution_attempt(
        {"mode": "LIVE"}
    )

    assert result["status"] == "BROKER_SPECIFIC_LIVE_EXECUTION_BLOCKED"
    assert result["blocked"] is True
    assert "live_execution_blocked" in result["blockers"]
    assert "live_account_mode_blocked" in result["blockers"]
    assert result["live_execution_allowed"] is False
    assert result["live_orders_allowed"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False


def test_unsupported_action_fails_closed() -> None:
    result = broker_specific_paper_demo.fail_closed_broker_specific_action("stream_prices")

    assert result["status"] == "BROKER_SPECIFIC_PAPER_DEMO_MAPPING_BLOCKED"
    assert result["blocked"] is True
    assert "unsupported_broker_specific_action" in result["blockers"]
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["live_orders_allowed"] is False


def test_module_has_no_oanda_sdk_network_env_or_file_write_behavior() -> None:
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
