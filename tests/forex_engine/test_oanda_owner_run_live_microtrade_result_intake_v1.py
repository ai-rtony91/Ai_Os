from __future__ import annotations

import json
from pathlib import Path

import pytest

from automation.forex_engine import oanda_owner_run_live_microtrade_result_contract_v1 as contract
from automation.forex_engine import oanda_owner_run_live_microtrade_result_intake_v1 as intake


REPO_ROOT = Path(__file__).resolve().parents[2]


def _result(builder=intake.build_sample_profit_result_input):
    return intake.intake_oanda_owner_run_live_microtrade_result(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (
            intake.build_sample_profit_result_input,
            intake.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_ACCEPTED,
        ),
        (
            intake.build_sample_loss_result_input,
            intake.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_ACCEPTED,
        ),
        (
            intake.build_sample_breakeven_result_input,
            intake.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_ACCEPTED,
        ),
        (
            intake.build_sample_missing_owner_result_input,
            intake.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_NO_OWNER_RESULT,
        ),
        (
            intake.build_sample_unsafe_result_input,
            intake.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_UNSAFE,
        ),
    ),
)
def test_intake_sample_classifications(builder, classification: str):
    assert _result(builder).classification == classification


def test_intake_version_constant():
    assert intake.VERSION == "oanda_owner_run_live_microtrade_result_intake_v1"


def test_intake_blocks_incomplete_result():
    sample = intake.build_sample_profit_result_input()
    payload = dict(sample.owner_result or {})
    payload.pop("realized_pl")
    result = intake.intake_oanda_owner_run_live_microtrade_result(
        {"owner_result": payload}
    )
    assert result.classification == intake.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_INCOMPLETE
    assert "realized_pl" in result.missing_fields


@pytest.mark.parametrize("field_name", contract.REQUIRED_SANITIZED_RESULT_FIELDS)
def test_intake_preserves_required_sanitized_fields_only(field_name: str):
    result = _result()
    assert field_name in result.sanitized_result_fields


@pytest.mark.parametrize("field_name", contract.OPTIONAL_SANITIZED_RESULT_FIELDS)
def test_intake_preserves_optional_sanitized_fields(field_name: str):
    result = _result()
    assert field_name in result.sanitized_result_fields


@pytest.mark.parametrize(
    "extra_field",
    (
        "runtime_account",
        "authorization",
        "broker_order_id",
        "raw_payload",
        "not_allowed_runtime_material",
    ),
)
def test_intake_does_not_preserve_extra_fields(extra_field: str):
    sample = intake.build_sample_profit_result_input()
    payload = dict(sample.owner_result or {})
    payload[extra_field] = "SANITIZED-BOUNDARY"
    result = intake.intake_oanda_owner_run_live_microtrade_result(
        {"owner_result": payload}
    )
    assert extra_field not in result.sanitized_result_fields


@pytest.mark.parametrize(
    "field_name",
    (
        "no_credentials_in_payload",
        "no_account_id_in_payload",
        "no_broker_order_id_in_payload",
        "no_raw_broker_payload",
        "no_repeat_execution_confirmed",
        "no_compounding_confirmed",
        "no_bank_movement_confirmed",
        "no_autonomous_loop_confirmed",
    ),
)
def test_intake_blocks_missing_safety_confirmation(field_name: str):
    sample = intake.build_sample_profit_result_input()
    payload = dict(sample.owner_result or {})
    payload[field_name] = False
    result = intake.intake_oanda_owner_run_live_microtrade_result(
        {"owner_result": payload}
    )
    assert result.classification == intake.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_UNSAFE


@pytest.mark.parametrize("flag_name", contract.PROTECTED_FLAG_NAMES)
def test_intake_output_protected_flags_false(flag_name: str):
    result = _result()
    assert result.protected_flags[flag_name] is False
    assert getattr(result, flag_name) is False


@pytest.mark.parametrize("flag_name", contract.PROTECTED_FLAG_NAMES)
def test_intake_blocks_protected_flag_true(flag_name: str):
    sample = intake.build_sample_profit_result_input()
    payload = dict(sample.owner_result or {})
    payload[flag_name] = True
    result = intake.intake_oanda_owner_run_live_microtrade_result(
        {"owner_result": payload}
    )
    assert result.classification == intake.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_UNSAFE


@pytest.mark.parametrize(
    "builder",
    (
        intake.build_sample_profit_result_input,
        intake.build_sample_loss_result_input,
        intake.build_sample_breakeven_result_input,
        intake.build_sample_missing_owner_result_input,
        intake.build_sample_unsafe_result_input,
    ),
)
def test_intake_json_serializable_outputs(builder):
    json.dumps(intake.to_jsonable_dict(_result(builder)))


@pytest.mark.parametrize(
    "builder",
    (
        intake.build_sample_profit_result_input,
        intake.build_sample_loss_result_input,
        intake.build_sample_breakeven_result_input,
        intake.build_sample_missing_owner_result_input,
        intake.build_sample_unsafe_result_input,
    ),
)
def test_intake_deterministic_outputs(builder):
    assert intake.to_jsonable_dict(_result(builder)) == intake.to_jsonable_dict(_result(builder))


def test_intake_operator_text_output():
    assert "Result intake status" in intake.to_operator_text(_result())


def test_intake_markdown_output():
    assert intake.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Owner-Run Live Microtrade Result Intake V1"
    )


def test_intake_missing_owner_result_not_accepted():
    result = _result(intake.build_sample_missing_owner_result_input)
    assert result.intake_accepted is False
    assert result.result_reference == ""


def test_intake_profit_result_accepted():
    result = _result(intake.build_sample_profit_result_input)
    assert result.intake_accepted is True
    assert result.result_reference == "SANITIZED-OWNER-RUN-RESULT-PROFIT-001"


def test_intake_result_capture_only_true():
    assert _result().result_capture_only is True


def test_intake_report_exists():
    assert (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_V1.md"
    ).exists()

