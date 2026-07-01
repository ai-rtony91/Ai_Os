from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.oanda_demo_owner_approved_one_order_protected_runtime_execution_v1 import (  # noqa: E402
    BLOCKED_BY_CREDENTIAL_SESSION_BOUNDARY,
    BLOCKED_BY_DAILY_LOSS_STOP,
    BLOCKED_BY_KILL_SWITCH,
    BLOCKED_BY_OWNER_APPROVAL_TOKEN,
    BLOCKED_BY_RISK_GATES,
    BLOCKED_BY_SENSITIVE_DATA,
    HARD_FALSE_FIELDS,
    INCOMPLETE_INPUTS,
    PROTECTED_ONE_ORDER_GATE_CLEARED,
    evaluate_oanda_demo_owner_approved_one_order_protected_runtime_execution_v1,
)


def _approval() -> dict:
    return {
        "approval_token_required": True,
        "approval_token_metadata_present": True,
        "approval_token_id_present": True,
        "approval_token_unexpired": True,
        "approval_token_unused": True,
        "approval_challenge_hash_present": True,
        "approval_timestamp_present": True,
        "approval_phrase_matches": True,
        "approval_action_matches": True,
        "approval_mode_matches": True,
        "approval_instrument_matches": True,
        "approval_units_matches": True,
        "approval_risk_matches": True,
        "generic_yes_detected": False,
    }


def _credential() -> dict:
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


def _payload() -> dict:
    return {
        "owner_approval_metadata": _approval(),
        "credential_session_boundary": _credential(),
        "oanda_mode_declaration": {
            "mode": "OANDA_DEMO",
            "account_id_provided": False,
        },
        "one_order_policy": {
            "one_order_only": True,
            "max_order_count_this_packet": 1,
            "duplicate_order_detected": False,
            "existing_open_order_for_candidate": False,
            "existing_open_position_for_candidate": False,
        },
        "risk_limits": {
            "stop_loss_present": True,
            "take_profit_present": True,
            "max_risk_per_trade_pct": "0.01",
            "max_daily_loss_pct": "0.03",
            "max_spread_pips": "2.5",
            "max_slippage_pips": "0.5",
        },
        "execution_controls": {
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
        },
        "post_execution_review_metadata": {
            "post_execution_review_required": True,
            "next_order_blocked_until_review": True,
        },
    }


def _run(payload: dict | None = None) -> dict:
    return evaluate_oanda_demo_owner_approved_one_order_protected_runtime_execution_v1(
        payload
    )


def test_empty_payload_incomplete() -> None:
    assert _run({})["protected_runtime_status"] == INCOMPLETE_INPUTS


def test_sensitive_data_blocked_and_value_not_echoed() -> None:
    payload = _payload()
    payload["nested"] = {"password": "DO-NOT-ECHO"}
    result = _run(payload)
    assert result["protected_runtime_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "DO-NOT-ECHO" not in repr(result)


def test_secret_like_notes_value_blocked_and_value_not_echoed() -> None:
    payload = _payload()
    payload["notes"] = "bearer SECRET"
    result = _run(payload)
    assert result["protected_runtime_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "SECRET" not in repr(result)


def test_secret_like_oanda_mode_value_blocked_and_value_not_echoed() -> None:
    payload = _payload()
    payload["oanda_mode_declaration"]["mode"] = "sk-secret"
    result = _run(payload)
    assert result["protected_runtime_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "sk-secret" not in repr(result)


def test_nested_secret_like_list_value_blocked_and_value_not_echoed() -> None:
    payload = _payload()
    payload["review_notes"] = ["safe metadata", "access token SECRET"]
    result = _run(payload)
    assert result["protected_runtime_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "access token SECRET" not in repr(result)


def test_account_id_blocked() -> None:
    payload = _payload()
    payload["account_id"] = "hidden-account"
    result = _run(payload)
    assert result["protected_runtime_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "hidden-account" not in repr(result)


def test_api_key_blocked() -> None:
    payload = _payload()
    payload["api_key"] = "hidden-key"
    assert _run(payload)["protected_runtime_status"] == BLOCKED_BY_SENSITIVE_DATA


def test_master_password_blocked() -> None:
    payload = _payload()
    payload["master_password"] = "hidden-master"
    assert _run(payload)["protected_runtime_status"] == BLOCKED_BY_SENSITIVE_DATA


def test_exact_approval_token_passes() -> None:
    result = _run(_payload())
    assert result["owner_approval_summary"]["ready"] is True


def test_generic_yes_blocks() -> None:
    payload = _payload()
    payload["owner_approval_metadata"]["generic_yes_detected"] = True
    assert _run(payload)["protected_runtime_status"] == BLOCKED_BY_OWNER_APPROVAL_TOKEN


def test_missing_credential_boundary_blocks() -> None:
    payload = _payload()
    payload["credential_session_boundary"]["credential_values_provided"] = True
    assert _run(payload)["protected_runtime_status"] == BLOCKED_BY_CREDENTIAL_SESSION_BOUNDARY


def test_expired_credential_session_blocks() -> None:
    payload = _payload()
    payload["credential_session_boundary"]["session_unexpired"] = False
    assert _run(payload)["protected_runtime_status"] == BLOCKED_BY_CREDENTIAL_SESSION_BOUNDARY


def test_risk_over_limit_blocks() -> None:
    payload = _payload()
    payload["risk_limits"]["max_risk_per_trade_pct"] = "0.02"
    assert _run(payload)["protected_runtime_status"] == BLOCKED_BY_RISK_GATES


def test_missing_stop_loss_blocks() -> None:
    payload = _payload()
    payload["risk_limits"]["stop_loss_present"] = False
    assert _run(payload)["protected_runtime_status"] == BLOCKED_BY_RISK_GATES


def test_missing_take_profit_blocks() -> None:
    payload = _payload()
    payload["risk_limits"]["take_profit_present"] = False
    assert _run(payload)["protected_runtime_status"] == BLOCKED_BY_RISK_GATES


def test_kill_switch_blocks() -> None:
    payload = _payload()
    payload["execution_controls"]["kill_switch_active"] = True
    assert _run(payload)["protected_runtime_status"] == BLOCKED_BY_KILL_SWITCH


def test_daily_loss_stop_blocks() -> None:
    payload = _payload()
    payload["execution_controls"]["daily_loss_stop_active"] = True
    assert _run(payload)["protected_runtime_status"] == BLOCKED_BY_DAILY_LOSS_STOP


def test_duplicate_order_blocks() -> None:
    payload = _payload()
    payload["one_order_policy"]["duplicate_order_detected"] = True
    assert _run(payload)["protected_runtime_status"] == "BLOCKED_BY_DUPLICATE_ORDER"


def test_strong_metadata_reaches_protected_one_order_gate_cleared() -> None:
    result = _run(_payload())
    assert result["protected_runtime_status"] == PROTECTED_ONE_ORDER_GATE_CLEARED
    assert result["protected_runtime_ready"] is True


def test_hard_false_fields_remain_false() -> None:
    result = _run(_payload())
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
