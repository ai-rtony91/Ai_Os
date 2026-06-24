import json

import pytest

from automation.forex_engine.oanda_demo_live_quote_derived_sltp_runtime_v1 import (
    APPROVED_ACCOUNT_ID_LABEL,
    APPROVED_ACCESS_TOKEN_LABEL,
    BLOCKED_BY_INVALID_TRADE_INTENT,
    BLOCKED_BY_MISSING_VAULT_CREDENTIALS,
    BLOCKED_BY_PROFIT_CLAIM,
    LIVE_QUOTE_DERIVED_DEMO_ORDER_ATTEMPTED,
    LIVE_QUOTE_DERIVED_RUNTIME_PACKET_READY,
    build_live_quote_derived_sltp_runtime_v1,
)
from scripts.forex_delivery.run_oanda_demo_live_quote_derived_sltp_runtime_v1 import (
    main,
)


def valid_context(**overrides):
    context = {
        "instrument": "EUR_USD",
        "direction": "BUY",
        "units": "1",
        "stop_loss_pips": "2",
        "take_profit_pips": "3",
        "min_distance_pips": "2",
        "pip_size": "0.0001",
        "risk_amount": "1.00",
        "client_order_id": "AIOS-DEMO-LIVEQUOTE-DERIVED-OWNER-RUNTIME-001",
        "order_type": "MARKET",
        "demo_only_confirmed": True,
        "vault_backed_runtime_only_confirmed": True,
        "one_order_only_confirmed": True,
        "owner_manual_runtime_only_confirmed": True,
        "no_live_endpoint_confirmed": True,
        "no_autonomous_order_confirmed": True,
        "no_second_order_confirmed": True,
        "post_trade_evidence_required_confirmed": True,
        "no_profit_claim_confirmed": True,
        "loss_possible_understood": True,
        "no_profit_guarantee_understood": True,
    }
    context.update(overrides)
    return context


def fake_vault_loader(payload):
    credential_name = payload["credential_name"]
    if credential_name == APPROVED_ACCESS_TOKEN_LABEL:
        return {"credential_name": credential_name, "secret_value": "TOKEN_SECRET"}
    if credential_name == APPROVED_ACCOUNT_ID_LABEL:
        return {"credential_name": credential_name, "secret_value": "ACCOUNT_SECRET"}
    return {"credential_name": credential_name, "secret_value": ""}


def fake_pricing_get(payload):
    assert payload["method"] == "GET"
    assert payload["instrument"] == "EUR_USD"
    return {
        "network_call_performed": True,
        "status_code": 200,
        "response_json": {
            "prices": [
                {
                    "instrument": "EUR_USD",
                    "time": "2026-06-24T12:00:00.000000000Z",
                    "bids": [{"price": "1.07040"}],
                    "asks": [{"price": "1.07050"}],
                }
            ]
        },
    }


def fake_order_post(payload):
    assert payload["method"] == "POST"
    assert payload["one_order_only"] is True
    order = payload["order_payload"]["order"]
    assert order["stopLossOnFill"]["price"] == "1.07020"
    assert order["takeProfitOnFill"]["price"] == "1.07080"
    return {
        "network_call_performed": True,
        "order_placement_performed": True,
        "order_attempt_count": 1,
        "status_code": 201,
        "response_json": {
            "orderCreateTransaction": {"id": "319"},
            "orderFillTransaction": {"id": "320"},
            "relatedTransactionIDs": ["319", "320"],
        },
    }


def test_owner_build_fetches_quote_and_derives_buy_sltp():
    result = build_live_quote_derived_sltp_runtime_v1(
        valid_context(),
        vault_load_callable=fake_vault_loader,
        http_get_pricing_callable=fake_pricing_get,
        execute_order=False,
    )

    assert result["classification"] == LIVE_QUOTE_DERIVED_RUNTIME_PACKET_READY
    assert result["pricing_snapshot"]["bid"] == "1.07040"
    assert result["pricing_snapshot"]["ask"] == "1.07050"
    assert result["derived_order"]["stop_loss"] == "1.07020"
    assert result["derived_order"]["take_profit"] == "1.07080"
    assert result["bid_ask_validation"]["classification"] == "BID_ASK_SLTP_VALIDATION_READY"
    assert result["safety_boundaries"]["order_placement_performed"] is False
    assert "TOKEN_SECRET" not in json.dumps(result)
    assert "ACCOUNT_SECRET" not in json.dumps(result)


def test_owner_build_derives_sell_sltp():
    result = build_live_quote_derived_sltp_runtime_v1(
        valid_context(direction="SELL"),
        vault_load_callable=fake_vault_loader,
        http_get_pricing_callable=fake_pricing_get,
        execute_order=False,
    )

    assert result["classification"] == LIVE_QUOTE_DERIVED_RUNTIME_PACKET_READY
    assert result["derived_order"]["stop_loss"] == "1.07070"
    assert result["derived_order"]["take_profit"] == "1.07010"


def test_owner_execute_submits_exactly_one_demo_order_with_fakes():
    result = build_live_quote_derived_sltp_runtime_v1(
        valid_context(),
        vault_load_callable=fake_vault_loader,
        http_get_pricing_callable=fake_pricing_get,
        http_post_order_callable=fake_order_post,
        execute_order=True,
    )

    assert result["classification"] == LIVE_QUOTE_DERIVED_DEMO_ORDER_ATTEMPTED
    assert result["order_submission"]["status_code"] == 201
    assert result["order_submission"]["order_create_transaction_id"] == "319"
    assert result["order_submission"]["order_fill_transaction_id"] == "320"
    assert result["safety_boundaries"]["order_attempt_count"] == 1


def test_missing_vault_loader_blocks_before_pricing():
    result = build_live_quote_derived_sltp_runtime_v1(valid_context())

    assert result["classification"] == BLOCKED_BY_MISSING_VAULT_CREDENTIALS
    assert result["pricing_fetch"]["performed"] is False


def test_profit_claim_blocks_before_vault():
    result = build_live_quote_derived_sltp_runtime_v1(
        valid_context(profit_claim_made=True),
        vault_load_callable=fake_vault_loader,
        http_get_pricing_callable=fake_pricing_get,
    )

    assert result["classification"] == BLOCKED_BY_PROFIT_CLAIM
    assert result["vault_load_boundary"]["vault_load_attempted"] is False


def test_distance_below_minimum_blocks_trade_intent():
    result = build_live_quote_derived_sltp_runtime_v1(
        valid_context(stop_loss_pips="1"),
        vault_load_callable=fake_vault_loader,
        http_get_pricing_callable=fake_pricing_get,
    )

    assert result["classification"] == BLOCKED_BY_INVALID_TRADE_INTENT


def test_cli_print_template_is_sanitized(capsys):
    exit_code = main(["--print-template"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["script_status"] == "LIVE_QUOTE_DERIVED_SLTP_RUNTIME_TEMPLATE_ONLY"
    assert payload["broker_network_call_performed"] is False
    assert payload["token_argument_supported"] is False


def test_cli_owner_build_with_fakes(capsys):
    exit_code = main(
        _owner_args("--owner-build-live-quote-derived-demo-order"),
        vault_load_callable=fake_vault_loader,
        http_get_pricing_callable=fake_pricing_get,
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["classification"] == LIVE_QUOTE_DERIVED_RUNTIME_PACKET_READY
    assert payload["pricing_network_call_performed"] is True
    assert payload["order_placement_performed"] is False


def test_cli_rejects_token_argument(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--token", "SECRET"])
    payload = json.loads(capsys.readouterr().out)

    assert exc_info.value.code == 2
    assert payload["script_status"] == "BLOCKED_INVALID_ARGUMENTS"
    assert payload["token_argument_supported"] is False


def _owner_args(mode):
    return [
        mode,
        "--instrument",
        "EUR_USD",
        "--direction",
        "BUY",
        "--units",
        "1",
        "--stop-loss-pips",
        "2",
        "--take-profit-pips",
        "3",
        "--min-distance-pips",
        "2",
        "--pip-size",
        "0.0001",
        "--risk-amount",
        "1.00",
        "--client-order-id",
        "AIOS-DEMO-LIVEQUOTE-DERIVED-OWNER-RUNTIME-001",
        "--order-type",
        "MARKET",
        "--i-confirm-demo-only",
        "--i-confirm-vault-backed-runtime-only",
        "--i-confirm-one-order-only",
        "--i-confirm-owner-manual-runtime-only",
        "--i-confirm-no-live-endpoint",
        "--i-confirm-no-autonomous-order",
        "--i-confirm-no-second-order",
        "--i-confirm-post-trade-evidence-required",
        "--i-confirm-no-profit-claim",
        "--i-understand-loss-possible",
        "--i-understand-no-profit-guarantee",
    ]
