from __future__ import annotations

from pathlib import Path

from automation.forex_engine import oanda_live_http_transport_v1 as transport_mod
from automation.forex_engine import oanda_live_runtime_connector_v2 as connector_mod


class FakeResponse:
    status_code = 201

    def json(self) -> dict:
        return {
            "status": "ACCEPTED",
            "token": "SHOULD_NOT_LEAK",
            "authorization": "Bearer SHOULD_NOT_LEAK",
            "account_id": "ACCOUNT_SHOULD_NOT_LEAK",
            "broker_order_id": "ORDER_SHOULD_NOT_LEAK",
            "raw_response": {"value": "SHOULD_NOT_LEAK"},
            "orderCreateTransaction": {
                "id": "OANDA_ID_SHOULD_NOT_LEAK",
                "instrument": "EUR_USD",
            },
        }


class FakeHttpClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def post(self, url: str, json: dict, headers: dict) -> FakeResponse:
        self.calls.append({"url": url, "json": dict(json), "headers": dict(headers)})
        return FakeResponse()


def _ready_config() -> dict:
    return {
        "operator_approved_live_runtime": True,
        "live_endpoint_confirmed": True,
        "allow_live_network_once": True,
        "credentials_runtime_only": True,
        "credentials_persisted": False,
        "account_id_persisted": False,
        "single_order_only": True,
        "micro_size_only": True,
        "no_retry": True,
        "no_loop": True,
        "max_order_count": 1,
        "http_client_injected": True,
        "runtime_auth_provider_injected": True,
    }


def _ready_transport_config() -> dict:
    return transport_mod.build_oanda_live_http_transport_config(_ready_config())


def _connector_config() -> dict:
    return connector_mod.build_oanda_live_connector_config(
        {
            "operator_approved_live_runtime": True,
            "live_endpoint_confirmed": True,
            "credentials_runtime_only": True,
            "credentials_persisted": False,
            "account_id_persisted": False,
            "single_order_only": True,
            "micro_size_only": True,
            "no_retry": True,
            "no_loop": True,
            "max_order_count": 1,
            "transport_injected": True,
        }
    )


def _auth_provider() -> dict:
    return {
        "access_token": "TOKEN_SHOULD_NOT_LEAK",
        "account_id": "ACCOUNT_SHOULD_NOT_LEAK",
    }


def _intent(**overrides: object) -> dict:
    intent = {
        "instrument": "EUR_USD",
        "side": "BUY",
        "units": 10,
        "stop_loss": "1.0800",
        "take_profit": "1.0860",
    }
    intent.update(overrides)
    return intent


def test_missing_config_blocks() -> None:
    result = transport_mod.build_oanda_live_http_transport_config(None)

    assert result["config_status"] == transport_mod.OANDA_LIVE_HTTP_TRANSPORT_INVALID
    assert "transport_config_missing" in result["blockers"]


def test_missing_operator_approval_blocks() -> None:
    config = _ready_config()
    config["operator_approved_live_runtime"] = False

    result = transport_mod.build_oanda_live_http_transport_config(config)

    assert result["config_status"] == transport_mod.OANDA_LIVE_HTTP_TRANSPORT_REVIEW_REQUIRED
    assert "operator_approval_missing" in result["blockers"]


def test_ready_config_creates_ready_transport() -> None:
    http_client = FakeHttpClient()
    config = _ready_transport_config()

    readiness = transport_mod.build_oanda_live_http_transport_readiness(config, http_client, _auth_provider)
    transport = transport_mod.OandaLiveHttpTransportV1(config, http_client, _auth_provider)

    assert readiness["ready"] is True
    assert transport.supports_live_orders is True
    assert transport.supports_single_order_only is True
    assert transport.supports_micro_size_only is True
    assert transport.stores_credentials is False
    assert transport.stores_account_id is False


def test_buy_payload_uses_positive_units() -> None:
    result = transport_mod.build_oanda_market_order_payload(_intent(side="BUY", units=7))

    assert result["ready"] is True
    assert result["payload"]["order"]["units"] == "7"


def test_sell_payload_uses_negative_units() -> None:
    result = transport_mod.build_oanda_market_order_payload(_intent(side="SELL", units=7))

    assert result["ready"] is True
    assert result["payload"]["order"]["units"] == "-7"


def test_missing_stop_loss_blocks() -> None:
    result = transport_mod.build_oanda_market_order_payload(_intent(stop_loss=None))

    assert result["ready"] is False
    assert "stop_loss_missing" in result["blockers"]


def test_missing_take_profit_blocks() -> None:
    result = transport_mod.build_oanda_market_order_payload(_intent(take_profit=""))

    assert result["ready"] is False
    assert "take_profit_missing" in result["blockers"]


def test_units_above_1000_block() -> None:
    result = transport_mod.build_oanda_market_order_payload(_intent(units=1001))

    assert result["ready"] is False
    assert "units_above_micro_size_max" in result["blockers"]


def test_missing_http_client_blocks() -> None:
    readiness = transport_mod.build_oanda_live_http_transport_readiness(
        _ready_transport_config(),
        None,
        _auth_provider,
    )

    assert readiness["ready"] is False
    assert "http_client_invalid" in readiness["blockers"]


def test_missing_runtime_auth_provider_blocks() -> None:
    readiness = transport_mod.build_oanda_live_http_transport_readiness(
        _ready_transport_config(),
        FakeHttpClient(),
        None,
    )

    assert readiness["ready"] is False
    assert "runtime_auth_invalid" in readiness["blockers"]


def test_fake_injected_http_client_receives_exactly_one_post_on_valid_order() -> None:
    http_client = FakeHttpClient()
    transport = transport_mod.OandaLiveHttpTransportV1(_ready_transport_config(), http_client, _auth_provider)

    result = transport.place_live_micro_order(_intent())

    assert result["submitted"] is True
    assert result["accepted"] is True
    assert result["status_code"] == 201
    assert result["order_count"] == 1
    assert len(http_client.calls) == 1
    assert http_client.calls[0]["json"]["order"]["type"] == "MARKET"
    assert "Authorization" in http_client.calls[0]["headers"]


def test_second_order_is_blocked() -> None:
    http_client = FakeHttpClient()
    transport = transport_mod.OandaLiveHttpTransportV1(_ready_transport_config(), http_client, _auth_provider)

    first = transport.place_live_micro_order(_intent())
    second = transport.place_live_micro_order(_intent())

    assert first["submitted"] is True
    assert second["submitted"] is False
    assert "second_order_blocked" in second["blockers"]
    assert len(http_client.calls) == 1


def test_sanitized_result_removes_sensitive_runtime_and_broker_fields() -> None:
    raw_result = {
        "token": "TOKEN_SHOULD_NOT_LEAK",
        "authorization": "AUTH_SHOULD_NOT_LEAK",
        "account_id": "ACCOUNT_SHOULD_NOT_LEAK",
        "broker_order_id": "ORDER_SHOULD_NOT_LEAK",
        "raw_response": {"value": "RAW_SHOULD_NOT_LEAK"},
        "nested": {"access_token": "NESTED_TOKEN_SHOULD_NOT_LEAK", "safe": "ok"},
    }

    sanitized = transport_mod.sanitize_oanda_transport_result(raw_result)

    assert "token" not in sanitized
    assert "authorization" not in sanitized
    assert "account_id" not in sanitized
    assert "broker_order_id" not in sanitized
    assert "raw_response" not in sanitized
    assert "access_token" not in sanitized["nested"]
    assert sanitized["nested"]["safe"] == "ok"
    assert sanitized["credential_persisted"] is False
    assert sanitized["account_id_persisted"] is False
    assert sanitized["raw_broker_payload_persisted"] is False
    assert sanitized["authorization_persisted"] is False


def test_integration_shape_works_with_oanda_live_runtime_connector_v2() -> None:
    http_client = FakeHttpClient()
    transport = transport_mod.OandaLiveHttpTransportV1(_ready_transport_config(), http_client, _auth_provider)
    connector = connector_mod.OandaLiveRuntimeConnectorV2(_connector_config(), transport)

    result = connector.place_live_micro_order(_intent())

    assert result["submitted"] is True
    assert result["accepted"] is True
    assert result["order_count"] == 1
    assert len(http_client.calls) == 1
    assert "account_id" not in result["sanitized_response"]


def test_transport_source_has_no_forbidden_network_or_secret_loading_triggers() -> None:
    source = Path("automation/forex_engine/oanda_live_http_transport_v1.py").read_text(encoding="utf-8").lower()
    forbidden_snippets = (
        "os.environ",
        "getenv(",
        "dotenv",
        "import requests",
        "from requests",
        "scheduler",
        "daemon",
        "webhook",
        "retry loop",
        "urlopen(",
        "urllib.request",
    )

    for snippet in forbidden_snippets:
        assert snippet not in source
