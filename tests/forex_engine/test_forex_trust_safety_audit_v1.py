from __future__ import annotations

import json

from automation.forex_engine.forex_trust_safety_audit_v1 import (
    TRUST_SAFETY_AUDIT_BLOCKED,
    TRUST_SAFETY_AUDIT_READY,
    audit_sanitized_payload,
    contains_sensitive_material,
    redact_sensitive_material,
)


def test_clean_allowed_payload_passes():
    result = audit_sanitized_payload(
        {"broker_name": "OANDA", "mode": "demo"},
        allowed_keys={"broker_name", "mode"},
        required_keys={"broker_name"},
    )
    assert result["status"] == TRUST_SAFETY_AUDIT_READY
    assert result["execution_allowed"] is False


def test_missing_required_key_blocks():
    result = audit_sanitized_payload({"broker_name": "OANDA"}, required_keys={"broker_name", "mode"})
    assert result["status"] == TRUST_SAFETY_AUDIT_BLOCKED
    assert "missing_required_keys" in result["blockers"]


def test_unknown_key_blocks_when_allowed_keys_supplied():
    result = audit_sanitized_payload({"broker_name": "OANDA", "extra": True}, allowed_keys={"broker_name"})
    assert result["status"] == TRUST_SAFETY_AUDIT_BLOCKED
    assert "unknown_keys_present" in result["blockers"]
    assert result["unknown_keys"] == ["extra"]


def test_api_key_key_blocks():
    result = audit_sanitized_payload({"api_key": "redacted"})
    assert result["status"] == TRUST_SAFETY_AUDIT_BLOCKED
    assert "api_key" in result["rejected_keys"]


def test_token_key_blocks():
    result = audit_sanitized_payload({"token": "redacted"})
    assert result["status"] == TRUST_SAFETY_AUDIT_BLOCKED
    assert "token" in result["rejected_keys"]


def test_password_key_blocks():
    result = audit_sanitized_payload({"password": "redacted"})
    assert result["status"] == TRUST_SAFETY_AUDIT_BLOCKED
    assert "password" in result["rejected_keys"]


def test_bearer_value_blocks():
    result = audit_sanitized_payload({"proof_source": "Bearer abc"})
    assert result["status"] == TRUST_SAFETY_AUDIT_BLOCKED
    assert "proof_source" in result["sensitive_value_locations"]


def test_account_id_key_blocks():
    result = audit_sanitized_payload({"account_id": "redacted"})
    assert result["status"] == TRUST_SAFETY_AUDIT_BLOCKED
    assert "account_id" in result["rejected_keys"]


def test_env_value_blocks():
    result = audit_sanitized_payload({"proof_source": "C:/tmp/.env"})
    assert result["status"] == TRUST_SAFETY_AUDIT_BLOCKED
    assert "proof_source" in result["sensitive_value_locations"]


def test_nested_sensitive_value_blocks():
    result = audit_sanitized_payload({"outer": {"proof": "authorization: secret"}})
    assert result["status"] == TRUST_SAFETY_AUDIT_BLOCKED
    assert "outer.proof" in result["sensitive_value_locations"]


def test_list_nested_sensitive_value_blocks():
    result = audit_sanitized_payload({"proofs": ["safe", "sk-test-redacted"]})
    assert result["status"] == TRUST_SAFETY_AUDIT_BLOCKED
    assert "proofs[1]" in result["sensitive_value_locations"]


def test_redaction_never_exposes_original_sensitive_value():
    payload = {"proof": "Bearer very-secret-value", "safe": "ok"}
    redacted = redact_sensitive_material(payload)
    encoded = json.dumps(redacted)
    assert "very-secret-value" not in encoded
    assert "Bearer" not in encoded
    assert "REDACTED_SENSITIVE_VALUE" in encoded


def test_audit_result_is_json_serializable():
    result = audit_sanitized_payload({"items": {"a", "b"}})
    json.dumps(result, sort_keys=True)


def test_contains_sensitive_material_detects_sensitive_payload():
    assert contains_sensitive_material({"nested": {"account_number": "redacted"}}) is True


def test_audit_never_sets_execution_allowed_true():
    result = audit_sanitized_payload({"broker_name": "OANDA"})
    assert result["execution_allowed"] is False
    assert result["ready_to_execute"] is False
    assert result["live_autonomy_allowed"] is False
