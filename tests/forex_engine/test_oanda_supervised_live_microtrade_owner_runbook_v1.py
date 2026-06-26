from __future__ import annotations

import json

import pytest

from automation.forex_engine import oanda_supervised_live_microtrade_owner_runbook_v1 as runbook
from automation.forex_engine.oanda_supervised_live_microtrade_final_gate_v1 import (
    EXACT_NEXT_CODEX_PACKET,
    PROTECTED_FLAG_NAMES,
)


def _result(builder=runbook.build_sample_ready_input):
    return runbook.build_oanda_supervised_live_microtrade_owner_runbook(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (
            runbook.build_sample_ready_input,
            runbook.OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_READY_FOR_OWNER_REVIEW,
        ),
        (
            runbook.build_sample_missing_input,
            runbook.OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_REQUIRE_REPAIR,
        ),
        (
            runbook.build_sample_unsafe_input,
            runbook.OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_BLOCKED_UNSAFE,
        ),
    ),
)
def test_owner_runbook_sample_classifications(builder, classification: str):
    assert _result(builder).classification == classification


def test_owner_runbook_version_constant():
    assert runbook.VERSION == "oanda_supervised_live_microtrade_owner_runbook_v1"


@pytest.mark.parametrize("item", runbook.OWNER_CHECKLIST)
def test_owner_runbook_ready_has_owner_checklist_item(item: str):
    assert item in _result().owner_checklist


@pytest.mark.parametrize("item", runbook.RUNTIME_PLACEHOLDERS)
def test_owner_runbook_ready_has_runtime_placeholder(item: str):
    assert item in _result().runtime_placeholder_list


@pytest.mark.parametrize("item", runbook.FORBIDDEN_VALUES)
def test_owner_runbook_ready_has_forbidden_value(item: str):
    assert item in _result().forbidden_value_list


@pytest.mark.parametrize("item", runbook.ABORT_CHECKLIST)
def test_owner_runbook_ready_has_abort_item(item: str):
    assert item in _result().abort_checklist


@pytest.mark.parametrize("item", runbook.POST_TRADE_CAPTURE_CHECKLIST)
def test_owner_runbook_ready_has_post_trade_capture_item(item: str):
    assert item in _result().post_trade_capture_checklist


@pytest.mark.parametrize(
    "required_phrase",
    (
        "Anthony performs any real broker action manually outside Codex.",
        "Codex does not execute.",
        "AIOS does not execute autonomously.",
        "Runtime values are not persisted.",
        "Account identifiers are not stored.",
        "One tiny trade only.",
        "No compounding.",
        "No bank movement.",
        "No unattended loop.",
        "No vacation mode approval.",
        "No profit guarantee.",
    ),
)
def test_owner_runbook_required_statements(required_phrase: str):
    text = runbook.to_markdown(_result())
    assert required_phrase in text


def test_owner_runbook_missing_sample_requires_repair():
    result = _result(runbook.build_sample_missing_input)
    assert result.missing_items


def test_owner_runbook_unsafe_sample_blocked():
    result = _result(runbook.build_sample_unsafe_input)
    assert "runtime_value_persistence_attempt" in result.blocked_items


def test_owner_runbook_final_confirmation_placeholder():
    assert _result().final_confirmation_phrase_placeholder == "OWNER_RUNTIME_FINAL_CONFIRMATION_PHRASE"


def test_owner_runbook_next_packet_after_owner_run():
    assert _result().next_packet_after_owner_run == EXACT_NEXT_CODEX_PACKET


@pytest.mark.parametrize("flag_name", PROTECTED_FLAG_NAMES)
def test_owner_runbook_all_protected_flags_false(flag_name: str):
    result = _result()
    assert getattr(result, flag_name) is False
    assert result.protected_flags[flag_name] is False


@pytest.mark.parametrize(
    "forbidden_fragment",
    ("api-fxtrade", "sk-", "broker_order_id", "raw_broker_payload"),
)
def test_owner_runbook_no_real_sensitive_fragments(forbidden_fragment: str):
    payload = json.dumps(runbook.to_jsonable_dict(_result())).lower()
    assert forbidden_fragment not in payload


def test_owner_runbook_json_serializable():
    json.dumps(runbook.to_jsonable_dict(_result()))


def test_owner_runbook_markdown_output():
    assert runbook.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Supervised Live Microtrade Owner Runbook V1"
    )


def test_owner_runbook_operator_text_output():
    assert "Owner runbook status" in runbook.to_operator_text(_result())
