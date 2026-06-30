"""Bitwarden cloud credential reference handoff contract for Forex execution bridge.

This packet is repository-safe and stores only item/field references for owner-held
Bitwarden credentials.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass(frozen=True)
class BitwardenCloudCredentialReferenceInput:
    broker_read_only_probe_landed: bool
    bitwarden_provider: str
    broker_runtime_item_ref: str
    credential_reference_map_item_ref: str
    broker_api_token_field_ref: str
    broker_account_id_field_ref: str
    endpoint_field_ref: str
    environment_field_ref: str
    allowed_mode_field_ref: str
    expected_broker: str
    expected_environment: str
    expected_endpoint: str
    expected_allowed_mode: str
    owner_reference_map_created: bool
    item_reference_declared: bool
    field_references_declared: bool
    secret_values_present_in_repo: bool
    bitwarden_cli_called: bool
    bitwarden_vault_read: bool
    credentials_read: bool
    env_read: bool
    broker_api_called: bool
    order_execution: bool
    demo_authorized: bool
    live_authorized: bool
    session_window_hours: int
    session_window_days_per_week: int


@dataclass(frozen=True)
class BitwardenCloudCredentialReferenceResult:
    handoff_status: str
    current_stage: str
    next_stage: str
    blockers: List[str]
    broker_runtime_item_ref: str
    credential_reference_map_item_ref: str
    field_refs: Dict[str, str]
    bitwarden_cli_called: bool
    bitwarden_vault_read: bool
    credentials_read: bool
    env_read: bool
    broker_api_called: bool
    order_execution: bool
    demo_authorized: bool
    live_authorized: bool
    safe_next_action: str


_CURRENT_STAGE = "bitwarden_cloud_credential_reference_handoff"


def _safe_next_action_for_status(status: str) -> str:
    actions = {
        "BROKER_READ_ONLY_PROBE_REQUIRED": (
            "Land the broker read-only state probe result before handoff."
        ),
        "BITWARDEN_PROVIDER_REQUIRED": "Use Bitwarden as the credential provider and rerun.",
        "OWNER_REFERENCE_MAP_REQUIRED": "Create the owner reference map item and rerun.",
        "BROKER_RUNTIME_ITEM_REFERENCE_REQUIRED": (
            "Declare the owner-created broker runtime item reference."
        ),
        "BROKER_RUNTIME_FIELD_REFERENCES_REQUIRED": (
            "Declare every required broker runtime field reference name."
        ),
        "SECRET_VALUE_REJECTED": (
            "Remove secret values from the repo and keep reference placeholders only."
        ),
        "PROTECTED_BOUNDARY_VIOLATION": (
            "Stop and complete owner review before any further execution."
        ),
        "CREDENTIAL_REFERENCE_HANDOFF_READY": (
            "Proceed to broker runtime read-only auth probe."
        ),
    }
    return actions.get(status, "Review required fields and rerun.")


def _reference_field_map(input_data: BitwardenCloudCredentialReferenceInput) -> Dict[str, str]:
    return {
        "broker_api_token": input_data.broker_api_token_field_ref,
        "broker_account_id": input_data.broker_account_id_field_ref,
        "endpoint": input_data.endpoint_field_ref,
        "environment": input_data.environment_field_ref,
        "allowed_mode": input_data.allowed_mode_field_ref,
    }


def _protected_action_triggered(input_data: BitwardenCloudCredentialReferenceInput) -> bool:
    return (
        input_data.bitwarden_cli_called
        or input_data.bitwarden_vault_read
        or input_data.credentials_read
        or input_data.env_read
        or input_data.broker_api_called
        or input_data.order_execution
        or input_data.demo_authorized
        or input_data.live_authorized
    )


def evaluate_bitwarden_cloud_credential_reference_handoff(
    input_data: BitwardenCloudCredentialReferenceInput,
) -> BitwardenCloudCredentialReferenceResult:
    field_refs = _reference_field_map(input_data)

    if not input_data.broker_read_only_probe_landed:
        status = "BROKER_READ_ONLY_PROBE_REQUIRED"
        next_stage = "broker_read_only_state_probe"
        blockers = ["broker_read_only_probe_landed is False"]
    elif input_data.bitwarden_provider.lower() != "bitwarden":
        status = "BITWARDEN_PROVIDER_REQUIRED"
        next_stage = "select_bitwarden_provider"
        blockers = ["bitwarden_provider is not Bitwarden"]
    elif not input_data.owner_reference_map_created:
        status = "OWNER_REFERENCE_MAP_REQUIRED"
        next_stage = "create_bitwarden_reference_map"
        blockers = ["owner_reference_map_created is False"]
    elif not input_data.item_reference_declared:
        status = "BROKER_RUNTIME_ITEM_REFERENCE_REQUIRED"
        next_stage = "declare_broker_runtime_item_reference"
        blockers = ["item_reference_declared is False"]
    elif not input_data.field_references_declared:
        status = "BROKER_RUNTIME_FIELD_REFERENCES_REQUIRED"
        next_stage = "declare_broker_runtime_field_references"
        blockers = ["field_references_declared is False"]
    elif input_data.secret_values_present_in_repo:
        status = "SECRET_VALUE_REJECTED"
        next_stage = "remove_secret_values_from_repo"
        blockers = ["secret_values_present_in_repo is True"]
    elif _protected_action_triggered(input_data):
        status = "PROTECTED_BOUNDARY_VIOLATION"
        next_stage = "stop_and_owner_review"
        blockers = ["protected action flag is True"]
    else:
        status = "CREDENTIAL_REFERENCE_HANDOFF_READY"
        next_stage = "broker_runtime_read_only_auth_probe"
        blockers = []

    return BitwardenCloudCredentialReferenceResult(
        handoff_status=status,
        current_stage=_CURRENT_STAGE,
        next_stage=next_stage,
        blockers=blockers,
        broker_runtime_item_ref=input_data.broker_runtime_item_ref,
        credential_reference_map_item_ref=input_data.credential_reference_map_item_ref,
        field_refs=field_refs,
        bitwarden_cli_called=False,
        bitwarden_vault_read=False,
        credentials_read=False,
        env_read=False,
        broker_api_called=False,
        order_execution=False,
        demo_authorized=False,
        live_authorized=False,
        safe_next_action=_safe_next_action_for_status(status),
    )


def input_as_dict(input_data: BitwardenCloudCredentialReferenceInput) -> dict[str, object]:
    return asdict(input_data)


def result_as_dict(result: BitwardenCloudCredentialReferenceResult) -> dict[str, object]:
    return asdict(result)


__all__ = [
    "BitwardenCloudCredentialReferenceInput",
    "BitwardenCloudCredentialReferenceResult",
    "evaluate_bitwarden_cloud_credential_reference_handoff",
    "input_as_dict",
    "result_as_dict",
]
