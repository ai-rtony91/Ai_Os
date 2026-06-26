from __future__ import annotations

import json

import pytest

from automation.forex_engine import oanda_supervised_live_microtrade_disarm_recovery_v1 as disarm
from automation.forex_engine.oanda_supervised_live_microtrade_final_gate_v1 import (
    PROTECTED_FLAG_NAMES,
)


def _result(builder=disarm.build_sample_ready_input):
    return disarm.build_oanda_supervised_live_microtrade_disarm_recovery(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (
            disarm.build_sample_ready_input,
            disarm.OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_READY_FOR_OWNER_REVIEW,
        ),
        (
            disarm.build_sample_missing_input,
            disarm.OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_REQUIRE_REPAIR,
        ),
        (
            disarm.build_sample_unsafe_input,
            disarm.OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_BLOCKED_UNSAFE,
        ),
    ),
)
def test_disarm_recovery_sample_classifications(builder, classification: str):
    assert _result(builder).classification == classification


def test_disarm_recovery_version_constant():
    assert disarm.VERSION == "oanda_supervised_live_microtrade_disarm_recovery_v1"


@pytest.mark.parametrize("item", disarm.REQUIRED_CHECKLIST_ITEMS)
def test_disarm_recovery_ready_has_required_item(item: str):
    assert _result().checklist[item] is True


@pytest.mark.parametrize("item", disarm.REQUIRED_CHECKLIST_ITEMS)
def test_disarm_recovery_missing_item_requires_repair(item: str):
    sample = disarm.build_sample_ready_input()
    checklist = dict(sample.checklist)
    checklist[item] = False
    result = disarm.build_oanda_supervised_live_microtrade_disarm_recovery({"checklist": checklist})
    assert result.classification == disarm.OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_REQUIRE_REPAIR
    assert item in result.missing_items


def test_disarm_recovery_unsafe_blocks_repeat_execution_risk():
    result = _result(disarm.build_sample_unsafe_input)
    assert "repeat_execution_risk" in result.blocked_items


@pytest.mark.parametrize("flag_name", PROTECTED_FLAG_NAMES)
def test_disarm_recovery_all_protected_flags_false(flag_name: str):
    result = _result()
    assert getattr(result, flag_name) is False
    assert result.protected_flags[flag_name] is False


def test_disarm_recovery_json_serializable():
    json.dumps(disarm.to_jsonable_dict(_result()))


def test_disarm_recovery_markdown_output():
    assert disarm.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Supervised Live Microtrade Disarm Recovery V1"
    )


def test_disarm_recovery_operator_text_output():
    assert "Disarm recovery status" in disarm.to_operator_text(_result())


@pytest.mark.parametrize(
    "expected_item",
    (
        "kill_switch",
        "abort_on_timeout",
        "rollback_plan",
        "final_disarm",
        "duplicate_guard",
        "abort_if_account_boundary_unclear",
        "abort_if_credential_boundary_unclear",
        "no_repeat_execution",
    ),
)
def test_disarm_recovery_named_required_coverage(expected_item: str):
    assert expected_item in disarm.REQUIRED_CHECKLIST_ITEMS

