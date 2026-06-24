from __future__ import annotations

import json
from pathlib import Path

import pytest

from automation.forex_engine.oanda_demo_owner_one_trade_command_package_v1 import (
    BLOCKED_BY_AUTONOMY_REQUEST,
    BLOCKED_BY_INVALID_DIRECTION,
    BLOCKED_BY_INVALID_INSTRUMENT,
    BLOCKED_BY_INVALID_UNITS,
    BLOCKED_BY_LIVE_ENDPOINT,
    BLOCKED_BY_MISSING_STOP_LOSS,
    BLOCKED_BY_MISSING_TAKE_PROFIT,
    BLOCKED_BY_MISSING_TRADE_INTENT,
    BLOCKED_BY_PROFIT_CLAIM,
    OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE_READY,
    build_oanda_demo_owner_one_trade_command_package_v1,
)
from scripts.forex_delivery import (
    run_oanda_demo_owner_one_trade_command_package_v1 as runner,
)


def test_ready_package_returns_owner_manual_template_only() -> None:
    decision = build_oanda_demo_owner_one_trade_command_package_v1(_ready_context())
    package = decision["owner_manual_command_package"]

    assert decision["classification"] == OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE_READY
    assert decision["package_ready"] is True
    assert package["template_only"] is True
    assert package["max_order_attempts"] == 1
    assert "run_oanda_demo_runtime_http_transport_one_order_owner_run_v1.py" in (
        package["owner_manual_command_template"]
    )
    assert "--execute-transport" in package["owner_manual_command_template"]
    assert decision["safety_proof"]["order_placement_performed"] is False
    assert decision["execution_authority"]["demo_order_allowed"] is False


@pytest.mark.parametrize(
    ("field", "value", "classification"),
    [
        ("instrument", "GBP_USD", BLOCKED_BY_INVALID_INSTRUMENT),
        ("direction", "HOLD", BLOCKED_BY_INVALID_DIRECTION),
        ("units", "1001", BLOCKED_BY_INVALID_UNITS),
        ("stop_loss_price", "", BLOCKED_BY_MISSING_STOP_LOSS),
        ("take_profit_price", "", BLOCKED_BY_MISSING_TAKE_PROFIT),
        ("no_live_endpoint_confirmed", False, BLOCKED_BY_LIVE_ENDPOINT),
        ("no_autonomous_order_confirmed", False, BLOCKED_BY_AUTONOMY_REQUEST),
        ("no_profit_claim_confirmed", False, BLOCKED_BY_PROFIT_CLAIM),
    ],
)
def test_blocking_classifications(field: str, value: object, classification: str) -> None:
    context = _ready_context()
    context[field] = value

    decision = build_oanda_demo_owner_one_trade_command_package_v1(context)

    assert decision["classification"] == classification
    assert decision["package_ready"] is False
    assert decision["owner_manual_command_package"]["owner_manual_command_template"] is None


def test_missing_trade_intent_blocks_package() -> None:
    context = _ready_context()
    context["instrument"] = ""

    decision = build_oanda_demo_owner_one_trade_command_package_v1(context)

    assert decision["classification"] == BLOCKED_BY_MISSING_TRADE_INTENT
    assert "instrument_required" in decision["blockers"]


def test_print_template_returns_sanitized_json(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = runner.main(["--print-template"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["script_status"] == "OWNER_ONE_TRADE_COMMAND_PACKAGE_TEMPLATE_ONLY"
    assert "--stop-loss-price EXAMPLE_STOP_LOSS_PRICE" in payload[
        "example_builder_command"
    ]
    assert payload["broker_call_performed_by_codex"] is False
    assert payload["credential_read_performed"] is False


def test_script_builds_ready_package_from_non_secret_flags(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = runner.main(_ready_flags())
    payload = json.loads(capsys.readouterr().out)
    command_template = payload["decision"]["owner_manual_command_package"][
        "owner_manual_command_template"
    ]

    assert exit_code == 0
    assert payload["classification"] == OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE_READY
    assert payload["order_placement_performed"] is False
    assert "--stop-loss EXAMPLE_STOP_LOSS_PRICE" in command_template
    assert "--take-profit EXAMPLE_TAKE_PROFIT_PRICE" in command_template


def test_script_rejects_secret_like_cli_arguments_without_echoing_value(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as excinfo:
        runner.main(["--build-owner-command-package", "--api-key", "VALUE_SHOULD_NOT_APPEAR"])
    payload_text = capsys.readouterr().out
    payload = json.loads(payload_text)

    assert excinfo.value.code == 2
    assert payload["script_status"] == "BLOCKED_INVALID_ARGUMENTS"
    assert "VALUE_SHOULD_NOT_APPEAR" not in payload_text
    assert payload["credential_value_printed"] is False


def test_source_contains_no_broker_transport_or_secret_read_paths() -> None:
    module_source = Path(
        "automation/forex_engine/oanda_demo_owner_one_trade_command_package_v1.py"
    ).read_text(encoding="utf-8")
    script_source = Path(
        "scripts/forex_delivery/run_oanda_demo_owner_one_trade_command_package_v1.py"
    ).read_text(encoding="utf-8")
    combined_source = module_source + script_source

    forbidden_terms = (
        "os.environ",
        "CredRead",
        "urlopen",
        "requests.",
        "subprocess",
        "api-fxpractice.oanda.com",
        "api-fxtrade.oanda.com",
    )
    for term in forbidden_terms:
        assert term not in combined_source


def _ready_context() -> dict[str, object]:
    return {
        "instrument": "EUR_USD",
        "direction": "BUY",
        "units": "1",
        "stop_loss_price": "EXAMPLE_STOP_LOSS_PRICE",
        "take_profit_price": "EXAMPLE_TAKE_PROFIT_PRICE",
        "demo_only_confirmed": True,
        "one_order_only_confirmed": True,
        "owner_manual_runtime_only_confirmed": True,
        "stop_loss_present_confirmed": True,
        "take_profit_present_confirmed": True,
        "no_live_endpoint_confirmed": True,
        "no_autonomous_order_confirmed": True,
        "post_trade_evidence_required_confirmed": True,
        "result_bucket_required_confirmed": True,
        "no_profit_claim_confirmed": True,
    }


def _ready_flags() -> list[str]:
    return [
        "--build-owner-command-package",
        "--instrument",
        "EUR_USD",
        "--direction",
        "BUY",
        "--units",
        "1",
        "--stop-loss-price",
        "EXAMPLE_STOP_LOSS_PRICE",
        "--take-profit-price",
        "EXAMPLE_TAKE_PROFIT_PRICE",
        "--i-confirm-demo-only",
        "--i-confirm-one-order-only",
        "--i-confirm-owner-manual-runtime-only",
        "--i-confirm-stop-loss-present",
        "--i-confirm-take-profit-present",
        "--i-confirm-no-live-endpoint",
        "--i-confirm-no-autonomous-order",
        "--i-confirm-post-trade-evidence-required",
        "--i-confirm-result-bucket-required",
        "--i-confirm-no-profit-claim",
    ]
