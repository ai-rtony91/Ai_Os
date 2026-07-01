from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.oanda_demo_owner_approved_one_order_protected_runtime_execution_v1 import (  # noqa: E402
    HARD_FALSE_FIELDS,
)
from automation.forex_engine.owner_runtime_credential_session_bridge_v1 import (  # noqa: E402
    BLOCKED_BY_CREDENTIAL_BOUNDARY,
    BLOCKED_BY_SENSITIVE_DATA,
    BLOCKED_BY_SESSION_EXPIRY,
    INCOMPLETE_INPUTS,
    RUNTIME_CREDENTIAL_SESSION_BRIDGE_READY,
    evaluate_owner_runtime_credential_session_bridge_v1,
)


def _payload() -> dict:
    return {
        "owner_enters_credentials_outside_repo_chat": True,
        "runtime_only_credential_handoff": True,
        "no_stored_api_key": True,
        "no_stored_account_id": True,
        "no_master_password": True,
        "no_vault_password": True,
        "no_raw_token": True,
        "secret_scan_required": True,
        "redaction_required": True,
        "session_expiry_required": True,
        "session_unexpired": True,
        "one_order_session_scope": True,
        "credential_values_provided": False,
        "credential_values_persisted": False,
        "credential_values_logged": False,
        "credential_values_requested_by_aios": False,
        "repo_secret_storage_allowed": False,
        "chat_secret_sharing_allowed": False,
        "env_var_read_allowed": False,
        "account_id_provided": False,
    }


def _run(payload: dict | None = None) -> dict:
    return evaluate_owner_runtime_credential_session_bridge_v1(payload)


def test_empty_payload_incomplete() -> None:
    assert _run({})["credential_session_bridge_status"] == INCOMPLETE_INPUTS


def test_safe_owner_runtime_credential_metadata_passes() -> None:
    result = _run(_payload())
    assert result["credential_session_bridge_status"] == RUNTIME_CREDENTIAL_SESSION_BRIDGE_READY
    assert result["credential_session_bridge_ready"] is True


def test_expired_session_blocks() -> None:
    payload = _payload()
    payload["session_unexpired"] = False
    assert _run(payload)["credential_session_bridge_status"] == BLOCKED_BY_SESSION_EXPIRY


def test_credential_value_provided_blocks() -> None:
    payload = _payload()
    payload["credential_values_provided"] = True
    assert _run(payload)["credential_session_bridge_status"] == BLOCKED_BY_CREDENTIAL_BOUNDARY


def test_stored_api_key_metadata_false_passes() -> None:
    payload = _payload()
    payload["api_key_stored"] = False
    assert _run(payload)["credential_session_bridge_status"] == RUNTIME_CREDENTIAL_SESSION_BRIDGE_READY


def test_raw_api_key_blocks() -> None:
    payload = _payload()
    payload["api_key"] = "hidden-key"
    result = _run(payload)
    assert result["credential_session_bridge_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "hidden-key" not in repr(result)


def test_master_password_blocks() -> None:
    payload = _payload()
    payload["master_password"] = "hidden-master"
    result = _run(payload)
    assert result["credential_session_bridge_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "hidden-master" not in repr(result)


def test_hard_false_fields_remain_false() -> None:
    result = _run(_payload())
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
