from __future__ import annotations

import json

import pytest

from automation.forex_engine.sanitized_broker_snapshot_redaction_guard_v1 import (
    DEMO_ACCOUNT_REFERENCE_PRESENT,
    SANITIZED_TRANSACTION_REFERENCE_PRESENT,
    SNAPSHOT_REDACTION_GUARD_BLOCKED_ACCOUNT_ID,
    SNAPSHOT_REDACTION_GUARD_BLOCKED_EMPTY_INPUT,
    SNAPSHOT_REDACTION_GUARD_BLOCKED_LIVE_ENDPOINT,
    SNAPSHOT_REDACTION_GUARD_BLOCKED_RAW_BROKER_PAYLOAD,
    SNAPSHOT_REDACTION_GUARD_BLOCKED_SECRET,
    SNAPSHOT_REDACTION_GUARD_BLOCKED_UNSAFE_PERSISTENCE,
    SNAPSHOT_REDACTION_GUARD_CLEAR,
    SnapshotRedactionGuardInput,
    build_sample_blocked_account_id_input,
    build_sample_blocked_raw_broker_payload_input,
    build_sample_blocked_secret_input,
    build_sample_safe_redaction_guard_input,
    evaluate_snapshot_redaction_guard,
    redaction_guard_to_jsonable_dict,
    redaction_guard_to_operator_text,
)


def test_safe_redaction_guard_passes() -> None:
    result = evaluate_snapshot_redaction_guard(build_sample_safe_redaction_guard_input())
    assert result.classification == SNAPSHOT_REDACTION_GUARD_CLEAR
    assert result.safe_to_process is True


def test_empty_input_blocks() -> None:
    result = evaluate_snapshot_redaction_guard(SnapshotRedactionGuardInput(snapshot={}))
    assert result.classification == SNAPSHOT_REDACTION_GUARD_BLOCKED_EMPTY_INPUT
    assert result.safe_to_process is False


def test_account_id_looking_value_blocks() -> None:
    result = evaluate_snapshot_redaction_guard(build_sample_blocked_account_id_input())
    assert result.classification == SNAPSHOT_REDACTION_GUARD_BLOCKED_ACCOUNT_ID
    assert result.safe_to_process is False


def test_secret_wording_blocks() -> None:
    result = evaluate_snapshot_redaction_guard({"secret_value": "deterministic sample"})
    assert result.classification == SNAPSHOT_REDACTION_GUARD_BLOCKED_SECRET


def test_token_wording_blocks() -> None:
    result = evaluate_snapshot_redaction_guard(build_sample_blocked_secret_input())
    assert result.classification == SNAPSHOT_REDACTION_GUARD_BLOCKED_SECRET


def test_bearer_auth_blocks() -> None:
    result = evaluate_snapshot_redaction_guard({"note": "Authorization: Bearer deterministic-sample"})
    assert result.classification == SNAPSHOT_REDACTION_GUARD_BLOCKED_SECRET


def test_env_fragment_blocks() -> None:
    result = evaluate_snapshot_redaction_guard({"note": ".env OPENAI_API_KEY=deterministic-sample"})
    assert result.classification == SNAPSHOT_REDACTION_GUARD_BLOCKED_SECRET


def test_password_field_blocks() -> None:
    result = evaluate_snapshot_redaction_guard({"password": "deterministic sample"})
    assert result.classification == SNAPSHOT_REDACTION_GUARD_BLOCKED_SECRET


def test_raw_broker_payload_blocks() -> None:
    result = evaluate_snapshot_redaction_guard(build_sample_blocked_raw_broker_payload_input())
    assert result.classification == SNAPSHOT_REDACTION_GUARD_BLOCKED_RAW_BROKER_PAYLOAD


def test_live_endpoint_blocks() -> None:
    result = evaluate_snapshot_redaction_guard({"endpoint": "https://live-api.example.invalid/v3/accounts"})
    assert result.classification == SNAPSHOT_REDACTION_GUARD_BLOCKED_LIVE_ENDPOINT


def test_unsafe_persistence_blocks() -> None:
    result = evaluate_snapshot_redaction_guard({"store_account_identifier_for_later": True})
    assert result.classification == SNAPSHOT_REDACTION_GUARD_BLOCKED_UNSAFE_PERSISTENCE


def test_allowed_placeholder_account_reference_passes() -> None:
    result = evaluate_snapshot_redaction_guard({"account_reference": DEMO_ACCOUNT_REFERENCE_PRESENT})
    assert result.classification == SNAPSHOT_REDACTION_GUARD_CLEAR


def test_allowed_transaction_placeholder_passes() -> None:
    result = evaluate_snapshot_redaction_guard({"last_transaction_id": SANITIZED_TRANSACTION_REFERENCE_PRESENT})
    assert result.classification == SNAPSHOT_REDACTION_GUARD_CLEAR


def test_redacted_preview_does_not_leak_blocked_value() -> None:
    blocked_value = "101-001-1234567-001"
    result = evaluate_snapshot_redaction_guard({"account_reference": blocked_value})
    assert blocked_value not in result.redacted_preview
    assert "private values are shown" in result.redacted_preview


def test_redaction_output_json_serializable() -> None:
    result = evaluate_snapshot_redaction_guard(build_sample_safe_redaction_guard_input())
    payload = redaction_guard_to_jsonable_dict(result)
    assert json.loads(json.dumps(payload))["classification"] == SNAPSHOT_REDACTION_GUARD_CLEAR


def test_operator_text_is_plain_english() -> None:
    text = redaction_guard_to_operator_text(evaluate_snapshot_redaction_guard())
    assert "No trade was placed." in text
    assert "SNAPSHOT_" not in text


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
def test_redaction_permission_flags_remain_false(permission: str) -> None:
    result = evaluate_snapshot_redaction_guard()
    assert getattr(result, permission) is False
