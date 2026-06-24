from __future__ import annotations

import json
from pathlib import Path

import pytest

from automation.forex_engine.oanda_demo_one_trade_readiness_v1 import (
    BLOCKED_BY_AUTONOMY_REQUEST,
    BLOCKED_BY_KILL_SWITCH,
    BLOCKED_BY_LIVE_ENDPOINT,
    BLOCKED_BY_ORDER_CAP,
    BLOCKED_BY_PREFLIGHT,
    BLOCKED_BY_PROFIT_CLAIM,
    BLOCKED_BY_RISK_GATE,
    READINESS_FIELDS,
    READY_FOR_OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE,
    evaluate_oanda_demo_one_trade_readiness_v1,
)
from scripts.forex_delivery import run_oanda_demo_one_trade_readiness_v1 as runner


def test_ready_context_classifies_owner_command_package_ready() -> None:
    decision = evaluate_oanda_demo_one_trade_readiness_v1(_ready_context())

    assert decision["classification"] == READY_FOR_OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE
    assert decision["readiness_ready"] is True
    assert decision["safety_proof"]["order_placement_performed"] is False
    assert decision["safety_proof"]["credential_read_performed"] is False
    assert decision["execution_authority"]["demo_order_allowed"] is False


@pytest.mark.parametrize(
    ("field", "classification"),
    [
        ("read_only_preflight_passed", BLOCKED_BY_PREFLIGHT),
        ("max_loss_gate_passed", BLOCKED_BY_RISK_GATE),
        ("kill_switch_state_passed", BLOCKED_BY_KILL_SWITCH),
        ("one_order_only_cap_available", BLOCKED_BY_ORDER_CAP),
        ("no_live_endpoint", BLOCKED_BY_LIVE_ENDPOINT),
        ("no_scheduler_daemon_webhook", BLOCKED_BY_AUTONOMY_REQUEST),
        ("no_profit_claim", BLOCKED_BY_PROFIT_CLAIM),
    ],
)
def test_single_failed_gate_returns_expected_classification(
    field: str,
    classification: str,
) -> None:
    context = _ready_context()
    context[field] = False

    decision = evaluate_oanda_demo_one_trade_readiness_v1(context)

    assert decision["classification"] == classification
    assert decision["readiness_ready"] is False
    assert f"{field}_required" in decision["blockers"]


def test_default_context_blocks_by_preflight() -> None:
    decision = evaluate_oanda_demo_one_trade_readiness_v1()

    assert decision["classification"] == BLOCKED_BY_PREFLIGHT
    assert decision["readiness_ready"] is False
    assert "read_only_preflight_passed_required" in decision["blockers"]


def test_print_template_returns_sanitized_json(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = runner.main(["--print-template"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["script_status"] == "ONE_TRADE_READINESS_TEMPLATE_ONLY"
    assert payload["accepted_value_arguments"] == []
    assert payload["broker_call_performed_by_codex"] is False
    assert payload["credential_read_performed"] is False


def test_script_evaluates_ready_context_from_non_secret_flags(
    capsys: pytest.CaptureFixture[str],
) -> None:
    flags = [
        "--evaluate-readiness",
        "--i-confirm-demo-only",
        "--i-confirm-read-only-preflight-passed",
        "--i-confirm-owner-runtime-command-required",
        "--i-confirm-codex-broker-call-not-performed",
        "--i-confirm-instrument-allowed",
        "--i-confirm-eur-usd-available",
        "--i-confirm-direction-allowed",
        "--i-confirm-micro-units-present",
        "--i-confirm-stop-loss-present",
        "--i-confirm-take-profit-present",
        "--i-confirm-max-loss-gate-passed",
        "--i-confirm-daily-stop-gate-passed",
        "--i-confirm-kill-switch-state-passed",
        "--i-confirm-one-order-only-cap-available",
        "--i-confirm-post-trade-evidence-plan-present",
        "--i-confirm-result-bucket-plan-present",
        "--i-confirm-next-allocation-plan-present",
        "--i-confirm-compound-or-withdraw-conditional",
        "--i-confirm-no-live-endpoint",
        "--i-confirm-no-scheduler-daemon-webhook",
        "--i-confirm-no-profit-claim",
    ]

    exit_code = runner.main(flags)
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["classification"] == READY_FOR_OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE
    assert payload["order_placement_performed"] is False
    assert payload["orders_endpoint_called"] is False


def test_script_rejects_secret_like_cli_arguments_without_echoing_value(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as excinfo:
        runner.main(["--evaluate-readiness", "--token", "SHOULD_NOT_APPEAR"])
    payload_text = capsys.readouterr().out
    payload = json.loads(payload_text)

    assert excinfo.value.code == 2
    assert payload["script_status"] == "BLOCKED_INVALID_ARGUMENTS"
    assert "SHOULD_NOT_APPEAR" not in payload_text
    assert payload["credential_value_printed"] is False


def test_source_contains_no_broker_transport_or_vault_read_paths() -> None:
    module_source = Path(
        "automation/forex_engine/oanda_demo_one_trade_readiness_v1.py"
    ).read_text(encoding="utf-8")
    script_source = Path(
        "scripts/forex_delivery/run_oanda_demo_one_trade_readiness_v1.py"
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
        "/v3/accounts",
        "/orders",
    )
    for term in forbidden_terms:
        assert term not in combined_source


def _ready_context() -> dict[str, bool]:
    return {field: True for field in READINESS_FIELDS}
