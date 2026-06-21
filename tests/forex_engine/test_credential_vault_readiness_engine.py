from automation.forex_engine.credential_vault_readiness_engine import (
    STATUS_BLOCKED,
    STATUS_MORE_INFO,
    STATUS_READY,
    evaluate_credential_vault_readiness,
)


def _metadata():
    return {
        "vault_provider_declared": True,
        "vault_access_method_declared": True,
        "secret_names_declared_only": True,
        "no_plaintext_secret_storage": True,
        "no_secret_values_present": True,
        "rotation_policy_declared": True,
        "access_audit_required": True,
        "least_privilege_required": True,
        "operator_approval_required": True,
        "emergency_revoke_plan_declared": True,
        "credential_scope_declared": True,
        "paper_only_credential_review": True,
    }


def test_credential_vault_ready():
    result = evaluate_credential_vault_readiness(_metadata())
    assert result["credential_vault_ready"] is True
    assert result["credential_policy_status"] == STATUS_READY
    assert result["safety"]["credential_values_accessed"] is False


def test_missing_metadata_blocked():
    result = evaluate_credential_vault_readiness({"vault_provider_declared": True})
    assert result["credential_vault_ready"] is False
    assert result["credential_policy_status"] == STATUS_MORE_INFO
    assert any(reason.startswith("missing_credential_metadata:") for reason in result["blocked_reasons"])


def test_secret_value_present_blocked():
    metadata = _metadata()
    metadata["no_secret_values_present"] = False
    result = evaluate_credential_vault_readiness(metadata)
    assert result["credential_policy_status"] == STATUS_BLOCKED
    assert "credential_control_failed:no_secret_values_present" in result["blocked_reasons"]


def test_plaintext_storage_allowed_blocked():
    metadata = _metadata()
    metadata["no_plaintext_secret_storage"] = False
    result = evaluate_credential_vault_readiness(metadata)
    assert "credential_control_failed:no_plaintext_secret_storage" in result["blocked_reasons"]


def test_missing_rotation_policy_blocked():
    metadata = _metadata()
    metadata["rotation_policy_declared"] = False
    result = evaluate_credential_vault_readiness(metadata)
    assert "credential_control_failed:rotation_policy_declared" in result["blocked_reasons"]


def test_missing_audit_requirement_blocked():
    metadata = _metadata()
    metadata["access_audit_required"] = False
    result = evaluate_credential_vault_readiness(metadata)
    assert "credential_control_failed:access_audit_required" in result["blocked_reasons"]


def test_missing_least_privilege_blocked():
    metadata = _metadata()
    metadata["least_privilege_required"] = False
    result = evaluate_credential_vault_readiness(metadata)
    assert "credential_control_failed:least_privilege_required" in result["blocked_reasons"]


def test_missing_emergency_revoke_plan_blocked():
    metadata = _metadata()
    metadata["emergency_revoke_plan_declared"] = False
    result = evaluate_credential_vault_readiness(metadata)
    assert "credential_control_failed:emergency_revoke_plan_declared" in result["blocked_reasons"]


def test_deterministic_output():
    first = evaluate_credential_vault_readiness(_metadata())
    second = evaluate_credential_vault_readiness(_metadata())
    assert first == second


def test_safety_source_scan():
    source = open("automation/forex_engine/credential_vault_readiness_engine.py", encoding="utf-8").read()
    forbidden = ["requests", "urllib", "socket", "subprocess", "os.environ", ".env", "http://", "https://"]
    for token in forbidden:
        assert token not in source


def test_forbidden_credential_access_state_absent():
    result = evaluate_credential_vault_readiness(_metadata())
    safety = result["safety"]
    assert safety["credential_values_accessed"] is False
    assert safety["credential_values_stored"] is False
    assert safety["credential_values_printed"] is False
    assert safety["env_files_read"] is False
    assert safety["vault_connection_active"] is False
    assert safety["network_access"] is False
