from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

from automation.forex_engine.forex_bitwarden_cloud_credential_reference_handoff_v1 import (
    BitwardenCloudCredentialReferenceInput,
    evaluate_bitwarden_cloud_credential_reference_handoff,
)
from scripts.forex_delivery.run_forex_bitwarden_cloud_credential_reference_handoff_v1 import (
    build_default_handoff_input,
    build_report_markdown,
)


def _base_input() -> BitwardenCloudCredentialReferenceInput:
    return build_default_handoff_input()


def test_default_input_returns_credential_reference_handoff_ready():
    result = evaluate_bitwarden_cloud_credential_reference_handoff(_base_input())
    assert result.handoff_status == "CREDENTIAL_REFERENCE_HANDOFF_READY"
    assert result.current_stage == "bitwarden_cloud_credential_reference_handoff"
    assert result.next_stage == "broker_runtime_read_only_auth_probe"


def test_missing_probe_returns_broker_read_only_probe_required():
    result = evaluate_bitwarden_cloud_credential_reference_handoff(
        replace(_base_input(), broker_read_only_probe_landed=False),
    )
    assert result.handoff_status == "BROKER_READ_ONLY_PROBE_REQUIRED"
    assert result.next_stage == "broker_read_only_state_probe"


def test_non_bitwarden_provider_returns_bitwarden_provider_required():
    result = evaluate_bitwarden_cloud_credential_reference_handoff(
        replace(_base_input(), bitwarden_provider="Vault"),
    )
    assert result.handoff_status == "BITWARDEN_PROVIDER_REQUIRED"
    assert result.next_stage == "select_bitwarden_provider"


def test_missing_owner_reference_map_returns_owner_reference_map_required():
    result = evaluate_bitwarden_cloud_credential_reference_handoff(
        replace(_base_input(), owner_reference_map_created=False),
    )
    assert result.handoff_status == "OWNER_REFERENCE_MAP_REQUIRED"
    assert result.next_stage == "create_bitwarden_reference_map"


def test_missing_item_reference_returns_broker_runtime_item_reference_required():
    result = evaluate_bitwarden_cloud_credential_reference_handoff(
        replace(_base_input(), item_reference_declared=False),
    )
    assert result.handoff_status == "BROKER_RUNTIME_ITEM_REFERENCE_REQUIRED"
    assert result.next_stage == "declare_broker_runtime_item_reference"


def test_missing_field_references_returns_broker_runtime_field_references_required():
    result = evaluate_bitwarden_cloud_credential_reference_handoff(
        replace(_base_input(), field_references_declared=False),
    )
    assert result.handoff_status == "BROKER_RUNTIME_FIELD_REFERENCES_REQUIRED"
    assert result.next_stage == "declare_broker_runtime_field_references"


def test_secret_values_present_returns_secret_value_rejected():
    result = evaluate_bitwarden_cloud_credential_reference_handoff(
        replace(_base_input(), secret_values_present_in_repo=True),
    )
    assert result.handoff_status == "SECRET_VALUE_REJECTED"
    assert result.next_stage == "remove_secret_values_from_repo"


def test_any_protected_flag_true_returns_protected_boundary_violation():
    for protected_field in [
        "bitwarden_cli_called",
        "bitwarden_vault_read",
        "credentials_read",
        "env_read",
        "broker_api_called",
        "order_execution",
        "demo_authorized",
        "live_authorized",
    ]:
        assert (
            evaluate_bitwarden_cloud_credential_reference_handoff(
                replace(_base_input(), **{protected_field: True})
            ).handoff_status
            == "PROTECTED_BOUNDARY_VIOLATION"
        )


def test_all_protected_output_booleans_are_false():
    result = evaluate_bitwarden_cloud_credential_reference_handoff(_base_input())
    assert result.bitwarden_cli_called is False
    assert result.bitwarden_vault_read is False
    assert result.credentials_read is False
    assert result.env_read is False
    assert result.broker_api_called is False
    assert result.order_execution is False
    assert result.demo_authorized is False
    assert result.live_authorized is False


def test_runner_writes_state_json_and_report():
    command = [
        sys.executable,
        "scripts/forex_delivery/run_forex_bitwarden_cloud_credential_reference_handoff_v1.py",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=True)
    assert completed.returncode == 0
    assert completed.stdout.startswith("{")

    state_path = Path(
        "Reports/forex_delivery/AIOS_FOREX_BITWARDEN_CLOUD_CREDENTIAL_REFERENCE_HANDOFF_V1_STATE.json",
    )
    report_path = Path(
        "Reports/forex_delivery/AIOS_FOREX_BITWARDEN_CLOUD_CREDENTIAL_REFERENCE_HANDOFF_V1_REPORT.md",
    )

    state_json = json.loads(state_path.read_text(encoding="utf-8"))
    assert state_json["result"]["handoff_status"] == "CREDENTIAL_REFERENCE_HANDOFF_READY"
    assert report_path.exists()
    report_text = report_path.read_text(encoding="utf-8")
    assert "CREDENTIAL_REFERENCE_HANDOFF_READY" in report_text
    assert "broker_runtime_read_only_auth_probe" in report_text


def test_config_template_exists_and_contains_no_secret_values():
    template_path = Path(
        "configs/forex/AIOS_FOREX_BITWARDEN_CLOUD_CREDENTIAL_REFERENCE_HANDOFF_V1.example.json",
    )
    data = json.loads(template_path.read_text(encoding="utf-8"))
    assert data["bitwarden_provider"] == "Bitwarden"
    assert data["broker_runtime_item_ref"] == (
        "AIOS / OANDA / Practice Demo / Broker Runtime"
    )
    assert data["credential_reference_map_item_ref"] == (
        "AIOS / Bitwarden / Credential Reference Map"
    )
    assert data["field_refs"] == {
        "broker_api_token": "broker_api_token",
        "broker_account_id": "broker_account_id",
        "endpoint": "endpoint",
        "environment": "environment",
        "allowed_mode": "allowed_mode",
    }
    assert data["expected_endpoint"] == "https://api-fxpractice.oanda.com"
    assert data["expected_environment"] == "practice_demo"
    assert data["expected_allowed_mode"] == "read_only_until_owner_demo_approval"
    assert data["raw_secret_values_allowed"] is False
    assert data["bitwarden_cli_called_by_this_packet"] is False
    assert data["bitwarden_vault_read_by_this_packet"] is False
    assert data["credentials_read_by_this_packet"] is False
    assert data["env_read_by_this_packet"] is False
    assert data["broker_api_called_by_this_packet"] is False
    assert data["order_execution_by_this_packet"] is False
    assert data["demo_authorized_by_this_packet"] is False
    assert data["live_authorized_by_this_packet"] is False
    assert data["next_stage"] == "broker_runtime_read_only_auth_probe"


def test_docs_include_reference_only_handoff_and_next_probe():
    doc_path = Path(
        "docs/trading_lab/forex/FOREX_BITWARDEN_CLOUD_CREDENTIAL_REFERENCE_HANDOFF_V1.md",
    )
    text = doc_path.read_text(encoding="utf-8").lower()
    assert "owner-created bitwarden cloud item" in text
    assert "reference map" in text
    assert "stores item names and field names only" in text
    assert "does not call bitwarden cli" in text
    assert "does not read bitwarden vault contents" in text
    assert "next real packet is broker runtime read-only auth probe" in text


def test_report_includes_next_stage_for_ready_input_when_evaluated():
    result = evaluate_bitwarden_cloud_credential_reference_handoff(_base_input())
    assert result.handoff_status == "CREDENTIAL_REFERENCE_HANDOFF_READY"
    assert result.next_stage == "broker_runtime_read_only_auth_probe"
    report = build_report_markdown(result.__dict__)
    assert "next_stage: broker_runtime_read_only_auth_probe" in report
