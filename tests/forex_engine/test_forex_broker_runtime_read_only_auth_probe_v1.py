from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from automation.forex_engine.forex_broker_runtime_read_only_auth_probe_v1 import (
    BROKER_RUNTIME_READ_ONLY_AUTH_PROBE_READY,
    BROKER_RUNTIME_READ_ONLY_AUTH_PROVEN,
    CREDENTIAL_REFERENCE_HANDOFF_REQUIRED,
    LIVE_ENDPOINT_REJECTED,
    OANDA_PRACTICE_READ_ONLY_ACCOUNT_PROBE_REQUIRED,
    ORDER_PATH_REJECTED,
    OWNER_READ_ONLY_APPROVAL_REQUIRED,
    REFERENCE_CONTRACT_MISMATCH,
    SECRET_LOGGING_REJECTED,
    ENV_FILE_READ_REJECTED,
    BW_SESSION_REQUIRED,
    BITWARDEN_CLI_REQUIRED,
    BITWARDEN_ITEM_READ_REQUIRED,
    build_default_input,
    evaluate_broker_runtime_read_only_auth_probe,
    redact_sensitive_values,
)
from scripts.forex_delivery.run_forex_broker_runtime_read_only_auth_probe_v1 import (
    run_probe,
)


def _input(
    runtime_probe_requested: bool = False,
    owner_approved_read_only_probe: bool = False,
):
    return build_default_input(
        runtime_probe_requested=runtime_probe_requested,
        owner_approved_read_only_probe=owner_approved_read_only_probe,
    )


def test_default_input_returns_owner_runtime_read_only_probe_ready():
    result = evaluate_broker_runtime_read_only_auth_probe(_input())
    assert result.probe_status == BROKER_RUNTIME_READ_ONLY_AUTH_PROBE_READY
    assert result.current_stage == "broker_runtime_read_only_auth_probe"
    assert result.next_stage == "owner_run_read_only_auth_probe"


def test_missing_credential_reference_handoff_returns_required_status():
    result = evaluate_broker_runtime_read_only_auth_probe(
        replace(_input(), credential_reference_handoff_landed=False),
    )
    assert result.probe_status == CREDENTIAL_REFERENCE_HANDOFF_REQUIRED
    assert result.next_stage == "bitwarden_cloud_credential_reference_handoff"


def test_wrong_reference_contract_returns_contract_mismatch():
    for field_name, bad_value in [
        ("broker_runtime_item_ref", "INVALID / ITEM / REF"),
        ("broker_api_token_field_ref", "bad_token_ref"),
        ("endpoint_field_ref", "bad_endpoint_ref"),
        ("environment_field_ref", "wrong_environment_ref"),
        ("allowed_mode_field_ref", "wrong_allowed_mode_ref"),
        ("expected_endpoint", "https://example.com/not-allowed"),
        ("expected_environment", "live"),
        ("expected_allowed_mode", "not_read_only"),
    ]:
        result = evaluate_broker_runtime_read_only_auth_probe(
            replace(_input(), **{field_name: bad_value}),
        )
        assert result.probe_status == REFERENCE_CONTRACT_MISMATCH
        assert result.next_stage == "fix_bitwarden_reference_contract"


def test_secret_values_logged_rejected():
    result = evaluate_broker_runtime_read_only_auth_probe(
        replace(_input(), secret_values_logged=True),
    )
    assert result.probe_status == SECRET_LOGGING_REJECTED
    assert result.next_stage == "remove_secret_logging"


def test_env_file_read_rejected():
    result = evaluate_broker_runtime_read_only_auth_probe(
        replace(_input(), env_file_read=True),
    )
    assert result.probe_status == ENV_FILE_READ_REJECTED
    assert result.next_stage == "remove_env_file_read"


def test_live_endpoint_used_rejected():
    result = evaluate_broker_runtime_read_only_auth_probe(
        replace(_input(), live_endpoint_used=True),
    )
    assert result.probe_status == LIVE_ENDPOINT_REJECTED
    assert result.next_stage == "use_oanda_practice_endpoint_only"


def test_order_endpoint_or_execution_rejected():
    result = evaluate_broker_runtime_read_only_auth_probe(
        replace(_input(), order_endpoint_used=True),
    )
    assert result.probe_status == ORDER_PATH_REJECTED
    assert result.next_stage == "remove_order_path"


def test_runtime_requested_without_owner_approval_rejected():
    result = evaluate_broker_runtime_read_only_auth_probe(
        replace(_input(runtime_probe_requested=True), owner_approved_read_only_probe=False),
    )
    assert result.probe_status == OWNER_READ_ONLY_APPROVAL_REQUIRED
    assert result.next_stage == "owner_approve_read_only_probe"


def test_runtime_requested_without_bw_session_rejected():
    result = evaluate_broker_runtime_read_only_auth_probe(
        replace(
            _input(runtime_probe_requested=True, owner_approved_read_only_probe=True),
            bw_session_present=False,
        ),
    )
    assert result.probe_status == BW_SESSION_REQUIRED
    assert result.next_stage == "owner_unlock_bitwarden_cli"


def test_runtime_requested_without_bitwarden_cli_rejected():
    result = evaluate_broker_runtime_read_only_auth_probe(
        replace(
            _input(runtime_probe_requested=True, owner_approved_read_only_probe=True),
            bw_session_present=True,
            bitwarden_cli_available=False,
        ),
    )
    assert result.probe_status == BITWARDEN_CLI_REQUIRED
    assert result.next_stage == "install_or_authenticate_bitwarden_cli"


def test_runtime_requested_without_bitwarden_item_read_rejected():
    result = evaluate_broker_runtime_read_only_auth_probe(
        replace(
            _input(runtime_probe_requested=True, owner_approved_read_only_probe=True),
            bw_session_present=True,
            bitwarden_cli_available=True,
            bitwarden_item_read_success=False,
        ),
    )
    assert result.probe_status == BITWARDEN_ITEM_READ_REQUIRED
    assert result.next_stage == "read_owner_approved_bitwarden_item"


def test_runtime_requested_without_account_summary_rejected():
    result = evaluate_broker_runtime_read_only_auth_probe(
        replace(
            _input(runtime_probe_requested=True, owner_approved_read_only_probe=True),
            bw_session_present=True,
            bitwarden_cli_available=True,
            bitwarden_item_read_success=True,
            broker_account_summary_read_success=False,
        ),
    )
    assert result.probe_status == OANDA_PRACTICE_READ_ONLY_ACCOUNT_PROBE_REQUIRED
    assert result.next_stage == "oanda_practice_account_summary_read"


def test_runtime_success_returns_proven_and_advances():
    result = evaluate_broker_runtime_read_only_auth_probe(
        replace(
            _input(runtime_probe_requested=True, owner_approved_read_only_probe=True),
            bw_session_present=True,
            bitwarden_cli_available=True,
            bitwarden_item_read_success=True,
            broker_account_summary_read_success=True,
        ),
    )
    assert result.probe_status == BROKER_RUNTIME_READ_ONLY_AUTH_PROVEN
    assert result.next_stage == "execution_control_stack"
    assert result.order_execution is False
    assert result.demo_authorized is False
    assert result.live_authorized is False


def test_all_outputs_redact_token_and_account():
    payload = {
        "level1": "EXAMPLE_REDACTION_MARKER_A",
        "level2": {
            "account": "EXAMPLE_REDACTION_MARKER_B",
            "list": ["keep", "EXAMPLE_REDACTION_MARKER_A", {"nested_account": "EXAMPLE_REDACTION_MARKER_B"}],
        },
    }
    redacted = redact_sensitive_values(
        payload,
        token = "EXAMPLE_REDACTION_MARKER_A",
        account_id = "EXAMPLE_REDACTION_MARKER_B",
    )
    payload_text = json.dumps(redacted)
    assert "EXAMPLE_REDACTION_MARKER_A" not in payload_text
    assert "EXAMPLE_REDACTION_MARKER_B" not in payload_text
    assert "REDACTED_TOKEN" in payload_text
    assert "REDACTED_ACCOUNT_ID" in payload_text


def test_runner_dry_run_writes_state_and_report(tmp_path: Path):
    state_path = tmp_path / "AIOS_FOREX_FOREX_BROKER_RUNTIME_READ_ONLY_AUTH_PROBE_V1_STATE.json"
    report_path = tmp_path / "AIOS_FOREX_FOREX_BROKER_RUNTIME_READ_ONLY_AUTH_PROBE_V1_REPORT.md"
    payload = run_probe(
        owner_approved_mode=False,
        state_output=state_path,
        report_output=report_path,
        write_report=True,
    )
    assert state_path.exists()
    assert report_path.exists()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    result = state["result"]
    assert result["probe_status"] == BROKER_RUNTIME_READ_ONLY_AUTH_PROBE_READY
    assert result["current_stage"] == "broker_runtime_read_only_auth_probe"
    assert result["next_stage"] == "owner_run_read_only_auth_probe"
    assert result["bitwarden_cli_called"] is False
    assert result["bitwarden_vault_read"] is False
    assert result["credentials_read"] is False
    assert result["env_file_read"] is False
    assert result["broker_api_called"] is False
    assert result["order_execution"] is False
    assert result["demo_authorized"] is False
    assert result["live_authorized"] is False
    assert "OWNER_RUNTIME_READ_ONLY_PROBE_READY" in report_path.read_text(encoding="utf-8")
    assert payload["result"]["probe_status"] == BROKER_RUNTIME_READ_ONLY_AUTH_PROBE_READY


def test_template_is_nosecret_and_has_required_fields():
    data = json.loads(
        Path(
            "configs/forex/AIOS_FOREX_BROKER_RUNTIME_READ_ONLY_AUTH_PROBE_V1.example.json",
        ).read_text(encoding="utf-8"),
    )
    assert data["default_mode"] == "dry_run"
    assert data["owner_runtime_flag"] == "--owner-approved-read-only-probe"
    assert data["requires_bw_session_env"] is True
    assert data["raw_secret_values_allowed"] is False
    assert data["env_file_read_allowed"] is False
    assert data["order_execution_allowed"] is False
    assert data["demo_authorized_by_this_packet"] is False
    assert data["live_authorized_by_this_packet"] is False
    assert "broker_api_token" in data["field_refs"]
    assert "broker_account_id" in data["field_refs"]
    assert "endpoint" in data["field_refs"]
    assert "environment" in data["field_refs"]
    assert "allowed_mode" in data["field_refs"]
    raw_dump = json.dumps(data)
    assert "token_value" not in raw_dump


def test_doc_mentions_runtime_owner_boundary_contract():
    text = Path(
        "docs/trading_lab/forex/FOREX_BROKER_RUNTIME_READ_ONLY_AUTH_PROBE_V1.md",
    ).read_text(encoding="utf-8")
    for phrase in [
        "first owner-run broker runtime auth bridge",
        "Bitwarden cloud references",
        "does not store raw secrets",
        "does not read `.env`",
        "--owner-approved-read-only-probe",
        "BW_SESSION",
        "account summary",
        "cannot place orders",
        "cannot authorize demo trading",
        "cannot authorize live trading",
    ]:
        assert phrase in text

