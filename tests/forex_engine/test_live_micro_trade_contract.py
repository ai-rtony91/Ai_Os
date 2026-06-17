from pathlib import Path

import pytest

from automation.forex_engine import live_micro_trade_contract as contract


ACTIVE_WINDOW = {
    "starts_at_utc": "2026-01-01T00:00:00Z",
    "expires_at_utc": "2099-01-01T00:00:00Z",
}


def valid_request(**overrides):
    payload = {
        "packet_id": "AIOS-LIVE-COUNTDOWN-03B-LIVE-MICRO-TRADE-CONTRACT-APPLY-001",
        "approval_window": dict(ACTIVE_WINDOW),
        "broker_path": "approved-human-owner-vault-handle",
        "instrument": "EUR_USD",
        "side": "buy",
        "units": 1,
        "max_loss": 1.0,
        "daily_loss_cap": 2.0,
        "stop_loss": 1.0,
        "order_type": "market",
        "evidence_bundle_id": "evidence-03b",
        "kill_switch_required": True,
        "approval_nonce_hash": "sha256:approval-nonce-redacted",
        "arming_step": "manual-human-owner-arm",
        "stop_point": "hard-stop-after-terminal-result",
    }
    payload.update(overrides)
    return payload


def valid_approval(**overrides):
    payload = {
        "packet_id": "AIOS-LIVE-COUNTDOWN-03B-LIVE-MICRO-TRADE-CONTRACT-APPLY-001",
        "human_owner": "Anthony",
        "approval_type": contract.ACTIVE_APPROVAL_TYPE,
        "approval_window": dict(ACTIVE_WINDOW),
        "broker_path": "approved-human-owner-vault-handle",
        "instrument": "EUR_USD",
        "side": "buy",
        "units": 1,
        "max_loss": 1.0,
        "daily_loss_cap": 2.0,
        "stop_loss": 1.0,
        "order_type": "market",
        "evidence_bundle_id": "evidence-03b",
        "approval_nonce_hash": "sha256:approval-nonce-redacted",
        "arming_step": "manual-human-owner-arm",
        "stop_point": "hard-stop-after-terminal-result",
        "non_transferable": True,
        "expires_after_use": True,
    }
    payload.update(overrides)
    return payload


def valid_evidence(**overrides):
    payload = {
        "evidence_bundle_id": "evidence-03b",
        "packet_id": "AIOS-LIVE-COUNTDOWN-03B-LIVE-MICRO-TRADE-CONTRACT-APPLY-001",
        "broker_sandbox_or_demo_proof": True,
        "risk_gate_passed": True,
        "kill_switch_active": True,
        "daily_loss_cap_active": True,
        "approval_hash_verified": True,
        "sanitized": True,
    }
    payload.update(overrides)
    return payload


def valid_audit(**overrides):
    payload = {
        "event_type": "approval",
        "packet_id": "AIOS-LIVE-COUNTDOWN-03B-LIVE-MICRO-TRADE-CONTRACT-APPLY-001",
        "sanitized": True,
        "redacted_identifiers_only": True,
    }
    payload.update(overrides)
    return payload


def valid_arming(**overrides):
    payload = {
        "packet_id": "AIOS-LIVE-COUNTDOWN-03B-LIVE-MICRO-TRADE-CONTRACT-APPLY-001",
        "approval_nonce_hash": "sha256:approval-nonce-redacted",
        "evidence_bundle_id": "evidence-03b",
        "kill_switch_active": True,
        "daily_loss_cap_active": True,
        "evidence_bundle_present": True,
        "approval_hash_verified": True,
        "approval_window_active": True,
        "one_order_remaining": True,
        "armed": True,
        "orders_remaining": 1,
    }
    payload.update(overrides)
    return payload


def valid_disarm(**overrides):
    payload = {
        "packet_id": "AIOS-LIVE-COUNTDOWN-03B-LIVE-MICRO-TRADE-CONTRACT-APPLY-001",
        "terminal_state": "fill",
        "disarmed": True,
        "final": True,
    }
    payload.update(overrides)
    return payload


def assert_rejected(code, func, payload):
    with pytest.raises(contract.ContractValidationError) as exc_info:
        func(payload)
    assert exc_info.value.code == code


def test_valid_request_passes_only_with_every_required_field():
    result = contract.validate_micro_trade_request(valid_request())

    assert result["contract"] == "SingleLiveMicroTradeRequest"
    assert result["request_contract_valid"] is True
    assert result["live_mode"] is False
    assert result["one_order_only"] is True
    assert result["retry_allowed"] is False
    assert result["autonomous_reentry_allowed"] is False
    assert result["human_owner_approval_required"] is True


def test_missing_or_ambiguous_required_field_blocks():
    missing = valid_request()
    missing.pop("packet_id")
    assert_rejected("missing_required_fields", contract.validate_micro_trade_request, missing)

    ambiguous = valid_request(notional_limit=10.0)
    assert_rejected("ambiguous_trade_size", contract.validate_micro_trade_request, ambiguous)

    no_size = valid_request()
    no_size.pop("units")
    assert_rejected("missing_trade_size", contract.validate_micro_trade_request, no_size)


def test_generic_approved_by_human_true_fails():
    assert_rejected(
        "specific_human_owner_approval_required",
        contract.validate_micro_trade_approval,
        {"approved_by_human": True},
    )


def test_validator_dashboard_router_approval_fails():
    for key in ["validator_approval", "dashboard_approval", "router_approval"]:
        assert_rejected(
            "non_authoritative_approval_source",
            contract.validate_micro_trade_approval,
            valid_approval(**{key: True}),
        )


def test_credential_like_fields_fail_anywhere():
    for key in ["credentials", "token", "tokens", "api_key", "password", "secret"]:
        payload = valid_request()
        payload["nested"] = {key: "redacted"}
        assert_rejected("forbidden_field", contract.validate_micro_trade_request, payload)


def test_broker_order_account_and_raw_payload_fields_fail():
    for key in ["broker_order_id", "account_id", "account_identifier", "raw_live_payload", "live_payload"]:
        payload = valid_audit()
        payload[key] = "redacted"
        assert_rejected("forbidden_field", contract.validate_audit_event, payload)

    evidence = valid_evidence(private_account_data="redacted")
    assert_rejected("forbidden_field", contract.validate_evidence_bundle, evidence)


def test_live_mode_defaults_false_and_true_is_rejected():
    result = contract.validate_micro_trade_request(valid_request())
    assert result["live_mode"] is False

    assert_rejected(
        "live_mode_must_default_false",
        contract.validate_micro_trade_request,
        valid_request(live_mode=True),
    )


def test_arming_fails_without_kill_switch_daily_cap_or_evidence():
    for key in ["kill_switch_active", "daily_loss_cap_active", "evidence_bundle_present"]:
        assert_rejected(
            "invalid_boolean_gate",
            contract.validate_arming_state,
            valid_arming(**{key: False}),
        )


def test_one_order_limit_enforced():
    assert_rejected(
        "one_order_limit_required",
        contract.validate_micro_trade_request,
        valid_request(one_order_only=False),
    )
    assert_rejected(
        "invalid_boolean_gate",
        contract.validate_arming_state,
        valid_arming(one_order_remaining=False),
    )
    assert_rejected(
        "one_order_limit_required",
        contract.validate_arming_state,
        valid_arming(orders_remaining=2),
    )


def test_retry_and_reentry_rejected():
    assert_rejected(
        "retry_forbidden",
        contract.validate_micro_trade_request,
        valid_request(retry_allowed=True),
    )
    assert_rejected(
        "autonomous_reentry_forbidden",
        contract.validate_arming_state,
        valid_arming(autonomous_reentry_allowed=True),
    )


def test_terminal_disarm_states_pass_and_nonterminal_state_fails():
    for terminal_state in contract.TERMINAL_DISARM_STATES:
        result = contract.validate_disarm_state(valid_disarm(terminal_state=terminal_state))
        assert result["disarm_contract_valid"] is True
        assert result["terminal"] is True
        assert result["execution_allowed"] is False

    assert_rejected(
        "terminal_disarm_state_required",
        contract.validate_disarm_state,
        valid_disarm(terminal_state="pending"),
    )


def test_evidence_and_audit_contracts_require_sanitized_facts():
    evidence = contract.validate_evidence_bundle(valid_evidence())
    audit = contract.validate_audit_event(valid_audit())

    assert evidence["evidence_bundle_contract_valid"] is True
    assert audit["audit_event_contract_valid"] is True
    assert_rejected(
        "invalid_boolean_gate",
        contract.validate_evidence_bundle,
        valid_evidence(sanitized=False),
    )
    assert_rejected(
        "invalid_boolean_gate",
        contract.validate_audit_event,
        valid_audit(contains_private_data=True),
    )


def test_source_scan_proves_no_execution_capabilities():
    source = Path(contract.__file__).read_text(encoding="utf-8").lower()

    forbidden_snippets = [
        "import requests",
        "import socket",
        "import urllib",
        "import subprocess",
        "import os",
        "from os",
        "from subprocess",
        "oanda",
        "ibkr",
        "mt5",
        "os.environ",
        "getenv(",
        "requests.",
        "socket.",
        "urllib.",
        "subprocess.",
        "start-process",
        "write_text(",
        "write_bytes(",
        "open(",
        "input(",
        "schedule.",
        "daemon.",
    ]
    for snippet in forbidden_snippets:
        assert snippet not in source

    summary = contract.assert_contract_module_has_no_execution_capabilities()
    assert summary["broker_sdk_allowed"] is False
    assert summary["network_allowed"] is False
    assert summary["credential_access_allowed"] is False
    assert summary["file_write_allowed"] is False
    assert summary["subprocess_allowed"] is False
    assert summary["scheduler_allowed"] is False
    assert summary["daemon_allowed"] is False
    assert summary["live_trading_enabled"] is False
    assert summary["orders_allowed"] is False
