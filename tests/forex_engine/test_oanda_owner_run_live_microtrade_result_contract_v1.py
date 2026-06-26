from __future__ import annotations

import json
from pathlib import Path

import pytest

from automation.forex_engine import oanda_owner_run_live_microtrade_result_contract_v1 as contract


REPO_ROOT = Path(__file__).resolve().parents[2]


def _result(builder=contract.build_sample_profit_result_input):
    return contract.evaluate_oanda_owner_run_live_microtrade_result_contract(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (
            contract.build_sample_profit_result_input,
            contract.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_READY,
        ),
        (
            contract.build_sample_loss_result_input,
            contract.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_READY,
        ),
        (
            contract.build_sample_breakeven_result_input,
            contract.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_READY,
        ),
        (
            contract.build_sample_missing_owner_result_input,
            contract.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_BLOCKED_UNSAFE,
        ),
        (
            contract.build_sample_unsafe_result_input,
            contract.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_BLOCKED_UNSAFE,
        ),
    ),
)
def test_contract_sample_classifications(builder, classification: str):
    assert _result(builder).classification == classification


def test_contract_version_constant():
    assert contract.VERSION == "oanda_owner_run_live_microtrade_result_contract_v1"


@pytest.mark.parametrize("field_name", contract.REQUIRED_SANITIZED_RESULT_FIELDS)
def test_contract_has_required_sanitized_fields(field_name: str):
    assert field_name in _result().required_sanitized_fields


@pytest.mark.parametrize("field_name", contract.REQUIRED_SANITIZED_RESULT_FIELDS)
def test_contract_preserves_required_sanitized_fields(field_name: str):
    assert field_name in _result().sanitized_result_fields


@pytest.mark.parametrize("field_name", contract.OPTIONAL_SANITIZED_RESULT_FIELDS)
def test_contract_preserves_optional_sanitized_fields(field_name: str):
    assert field_name in _result().sanitized_result_fields


@pytest.mark.parametrize(
    "field_name",
    (
        "no_credentials_in_payload",
        "no_account_id_in_payload",
        "no_broker_order_id_in_payload",
        "no_raw_broker_payload",
    ),
)
def test_contract_blocks_required_no_private_marker_false(field_name: str):
    sample = contract.build_sample_profit_result_input()
    payload = dict(sample.owner_result or {})
    payload[field_name] = False
    result = contract.evaluate_oanda_owner_run_live_microtrade_result_contract(
        {"owner_result": payload}
    )
    assert result.classification == contract.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_BLOCKED_UNSAFE
    assert result.blocked_items


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("runtime_account", "SANITIZED-BOUNDARY"),
        ("account_identifier", "SANITIZED-BOUNDARY"),
        ("access_token", "SANITIZED-BOUNDARY"),
        ("authorization", "SANITIZED-BOUNDARY"),
        ("broker_order_id", "SANITIZED-BOUNDARY"),
        ("raw_payload", {"sanitized": True}),
    ),
)
def test_contract_blocks_private_or_raw_marker_keys(field_name: str, value):
    sample = contract.build_sample_profit_result_input()
    payload = dict(sample.owner_result or {})
    payload[field_name] = value
    result = contract.evaluate_oanda_owner_run_live_microtrade_result_contract(
        {"owner_result": payload}
    )
    assert result.classification == contract.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_BLOCKED_UNSAFE


@pytest.mark.parametrize("flag_name", contract.PROTECTED_FLAG_NAMES)
def test_contract_output_protected_flags_false(flag_name: str):
    result = _result()
    assert result.protected_flags[flag_name] is False
    assert getattr(result, flag_name) is False


@pytest.mark.parametrize("flag_name", contract.PROTECTED_FLAG_NAMES)
def test_contract_blocks_protected_flag_true_in_payload(flag_name: str):
    sample = contract.build_sample_profit_result_input()
    payload = dict(sample.owner_result or {})
    payload[flag_name] = True
    result = contract.evaluate_oanda_owner_run_live_microtrade_result_contract(
        {"owner_result": payload}
    )
    assert result.classification == contract.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_BLOCKED_UNSAFE


@pytest.mark.parametrize(
    "builder",
    (
        contract.build_sample_profit_result_input,
        contract.build_sample_loss_result_input,
        contract.build_sample_breakeven_result_input,
        contract.build_sample_missing_owner_result_input,
        contract.build_sample_unsafe_result_input,
    ),
)
def test_contract_outputs_are_json_serializable(builder):
    json.dumps(contract.to_jsonable_dict(_result(builder)))


@pytest.mark.parametrize(
    "builder",
    (
        contract.build_sample_profit_result_input,
        contract.build_sample_loss_result_input,
        contract.build_sample_breakeven_result_input,
        contract.build_sample_missing_owner_result_input,
        contract.build_sample_unsafe_result_input,
    ),
)
def test_contract_outputs_are_deterministic(builder):
    assert contract.to_jsonable_dict(_result(builder)) == contract.to_jsonable_dict(_result(builder))


def test_contract_operator_text_output():
    assert "Result contract status" in contract.to_operator_text(_result())


def test_contract_markdown_output():
    assert contract.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Owner-Run Live Microtrade Result Contract V1"
    )


def test_contract_exact_owner_warning():
    assert _result().owner_warning == contract.EXACT_OWNER_WARNING


def test_contract_exact_result_warning():
    assert _result().result_warning == contract.EXACT_RESULT_WARNING


def test_contract_result_capture_only_true():
    assert _result().result_capture_only is True


def test_contract_missing_owner_result_reports_missing_fields():
    result = _result(contract.build_sample_missing_owner_result_input)
    assert set(result.missing_fields) == set(contract.REQUIRED_SANITIZED_RESULT_FIELDS)


def test_contract_no_extra_private_fields_preserved():
    sample = contract.build_sample_profit_result_input()
    payload = dict(sample.owner_result or {})
    payload["not_allowed_private_runtime_material"] = "SANITIZED-BOUNDARY"
    result = contract.evaluate_oanda_owner_run_live_microtrade_result_contract(
        {"owner_result": payload}
    )
    assert "not_allowed_private_runtime_material" not in result.sanitized_result_fields


def test_contract_report_path_expected():
    assert (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_V1.md"
    ).exists()
