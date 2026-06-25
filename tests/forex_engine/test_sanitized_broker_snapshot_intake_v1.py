from __future__ import annotations

import json

import pytest

from automation.forex_engine.broker_read_only_snapshot_contract_v1 import BROKER_SNAPSHOT_VALID
from automation.forex_engine.sanitized_broker_snapshot_intake_v1 import (
    REQUIRED_SNAPSHOT_FIELDS,
    SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_CONTRACT_VALIDATION,
    SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_INVALID_TYPES,
    SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_MISSING_REQUIRED_FIELDS,
    SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_REDACTION_GUARD,
    SANITIZED_BROKER_SNAPSHOT_INTAKE_READY,
    build_sample_blocked_snapshot_intake_input,
    build_sample_missing_fields_snapshot_intake_input,
    build_sample_sanitized_snapshot_intake_input,
    intake_sanitized_broker_snapshot,
    sanitized_snapshot_intake_to_jsonable_dict,
    sanitized_snapshot_intake_to_markdown,
    sanitized_snapshot_intake_to_operator_text,
)
from automation.forex_engine.sanitized_broker_snapshot_redaction_guard_v1 import (
    DEMO_ACCOUNT_REFERENCE_PRESENT,
)


def _ready_mapping() -> dict[str, object]:
    return dict(build_sample_sanitized_snapshot_intake_input().snapshot)


def test_intake_ready_sample_passes() -> None:
    result = intake_sanitized_broker_snapshot(build_sample_sanitized_snapshot_intake_input())
    assert result.classification == SANITIZED_BROKER_SNAPSHOT_INTAKE_READY
    assert result.broker_snapshot_status == BROKER_SNAPSHOT_VALID


def test_intake_json_string_passes() -> None:
    result = intake_sanitized_broker_snapshot(json.dumps(_ready_mapping()))
    assert result.classification == SANITIZED_BROKER_SNAPSHOT_INTAKE_READY


def test_intake_mapping_passes() -> None:
    result = intake_sanitized_broker_snapshot(_ready_mapping())
    assert result.classification == SANITIZED_BROKER_SNAPSHOT_INTAKE_READY


def test_missing_required_fields_blocks() -> None:
    result = intake_sanitized_broker_snapshot(build_sample_missing_fields_snapshot_intake_input())
    assert result.classification == SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_MISSING_REQUIRED_FIELDS
    assert any("balance" in blocker for blocker in result.blockers)


def test_invalid_decimal_blocks() -> None:
    raw = _ready_mapping()
    raw["balance"] = "not-a-decimal"
    result = intake_sanitized_broker_snapshot(raw)
    assert result.classification == SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_INVALID_TYPES
    assert "invalid decimal field: balance" in result.blockers


def test_invalid_integer_blocks() -> None:
    raw = _ready_mapping()
    raw["open_trades"] = "1.5"
    result = intake_sanitized_broker_snapshot(raw)
    assert result.classification == SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_INVALID_TYPES
    assert "invalid integer field: open_trades" in result.blockers


def test_redaction_guard_block_blocks_intake() -> None:
    result = intake_sanitized_broker_snapshot(build_sample_blocked_snapshot_intake_input())
    assert result.classification == SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_REDACTION_GUARD
    assert result.normalized_snapshot is None


def test_contract_validation_block_blocks_intake() -> None:
    raw = _ready_mapping()
    raw["market_hours_open"] = False
    result = intake_sanitized_broker_snapshot(raw)
    assert result.classification == SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_CONTRACT_VALIDATION
    assert "MARKET_CLOSED" in result.broker_snapshot_status


def test_normalized_snapshot_contains_all_required_fields() -> None:
    result = intake_sanitized_broker_snapshot()
    data = sanitized_snapshot_intake_to_jsonable_dict(result)
    normalized = data["normalized_snapshot"]
    assert all(field in normalized for field in REQUIRED_SNAPSHOT_FIELDS)


def test_normalized_snapshot_uses_placeholder_account_reference_only() -> None:
    result = intake_sanitized_broker_snapshot()
    assert result.normalized_snapshot is not None
    assert result.normalized_snapshot.account_reference == DEMO_ACCOUNT_REFERENCE_PRESENT


def test_intake_output_has_no_account_id_persistence() -> None:
    result = intake_sanitized_broker_snapshot()
    data = sanitized_snapshot_intake_to_jsonable_dict(result)
    assert data["account_id_persistence_allowed"] is False
    assert "101-001-1234567-001" not in json.dumps(data)


@pytest.mark.parametrize(
    "permission",
    [
        "demo_execution_allowed",
        "broker_action_allowed",
        "real_money_allowed",
        "compounding_allowed",
        "bank_movement_allowed",
        "live_trading_allowed",
        "credential_access_allowed",
        "account_id_persistence_allowed",
    ],
)
def test_intake_permission_flags_remain_false(permission: str) -> None:
    result = intake_sanitized_broker_snapshot()
    assert getattr(result, permission) is False


def test_intake_markdown_has_title() -> None:
    assert sanitized_snapshot_intake_to_markdown().startswith("# Sanitized Broker Snapshot Intake V1")


def test_intake_operator_text_is_plain_english() -> None:
    text = sanitized_snapshot_intake_to_operator_text()
    assert "review-ready" in text
    assert "No trade was placed." in text


def test_intake_output_json_serializable() -> None:
    payload = sanitized_snapshot_intake_to_jsonable_dict(intake_sanitized_broker_snapshot())
    assert json.loads(json.dumps(payload))["classification"] == SANITIZED_BROKER_SNAPSHOT_INTAKE_READY
