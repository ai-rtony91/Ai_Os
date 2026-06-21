from automation.forex_engine.credential_boundary_runtime_contract_h_v1 import (
    validate_credential_boundary,
)


def test_empty_credential_metadata_is_clear():
    result = validate_credential_boundary({})

    assert result.clear is True
    assert result.blocked_reasons == ()


def test_inline_api_key_is_rejected():
    result = validate_credential_boundary({"api_key": "example"})

    assert result.clear is False
    assert "credential_key_prohibited:api_key" in result.blocked_reasons


def test_secret_key_is_rejected():
    result = validate_credential_boundary({"secret": "value"})

    assert result.clear is False
    assert "credential_key_prohibited:secret" in result.blocked_reasons


def test_openai_style_secret_value_is_rejected():
    result = validate_credential_boundary({"reference": "sk-example"})

    assert result.clear is False
    assert "credential_value_leak:reference" in result.blocked_reasons


def test_bearer_value_is_rejected():
    result = validate_credential_boundary({"auth": "Bearer example"})

    assert result.clear is False
    assert "credential_value_leak:auth" in result.blocked_reasons


def test_env_file_reference_is_rejected():
    result = validate_credential_boundary({"source": ".env"})

    assert result.clear is False
    assert "repo_env_reference_prohibited:source" in result.blocked_reasons