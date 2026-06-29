"""Broker read-only state probe contract for Forex execution readiness lane."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List


@dataclass(frozen=True)
class BrokerReadOnlyProbeInput:
    broker_name: str
    broker_environment: str
    config_template_present: bool
    owner_runtime_config_present: bool
    credential_reference_declared: bool
    credential_material_present: bool
    account_reference_declared: bool
    read_only_capabilities_declared: bool
    mutating_capabilities_blocked: bool
    network_disabled_for_packet: bool
    broker_api_called: bool
    credentials_read: bool
    env_read: bool
    order_execution: bool
    demo_authorized: bool
    live_authorized: bool
    session_window_hours: int
    session_window_days_per_week: int


@dataclass(frozen=True)
class BrokerReadOnlyProbeResult:
    probe_status: str
    current_stage: str
    next_stage: str
    blockers: List[str]
    broker_name: str
    broker_environment: str
    broker_api_called: bool
    credentials_read: bool
    env_read: bool
    order_execution: bool
    demo_authorized: bool
    live_authorized: bool
    safe_next_action: str


def _safe_next_action_for_status(status: str) -> str:
    safe_actions = {
        "BROKER_READ_ONLY_TEMPLATE_REQUIRED": "Create a nonsecret broker read-only template before any probe execution.",
        "OWNER_RUNTIME_CONFIG_REQUIRED": "Hand off owner runtime config reference and path to runner scope.",
        "CREDENTIAL_REFERENCE_REQUIRED": "Add a nonsecret credential reference in runtime config and retry.",
        "SECRET_MATERIAL_REJECTED": "Remove secret material from config and replace with reference placeholders.",
        "ACCOUNT_REFERENCE_REQUIRED": "Add a nonsecret account reference and retry.",
        "READ_ONLY_CAPABILITY_DECLARATION_REQUIRED": "Declare read-only broker capabilities required for packet probe.",
        "MUTATING_CAPABILITY_BLOCK_REQUIRED": "Block mutating broker capabilities in runtime config.",
        "NETWORK_MUST_REMAIN_DISABLED_FOR_THIS_PACKET": "Keep this packet network-disabled and verify probe environment flags.",
        "PROTECTED_BOUNDARY_VIOLATION": "Stop and complete owner review before any packet execution.",
        "BROKER_READ_ONLY_PROBE_CONTRACT_READY": "Proceed to credential persistence owner handoff.",
    }
    return safe_actions.get(status, "Review required fields and retry.")


def evaluate_broker_read_only_state_probe(
    input_data: BrokerReadOnlyProbeInput,
) -> BrokerReadOnlyProbeResult:
    current_stage = "broker_read_only_state_probe"

    if not input_data.config_template_present:
        status = "BROKER_READ_ONLY_TEMPLATE_REQUIRED"
        next_stage = "create_nonsecret_broker_read_only_template"
        blockers = ["config_template_present is False"]
    elif not input_data.owner_runtime_config_present:
        status = "OWNER_RUNTIME_CONFIG_REQUIRED"
        next_stage = "owner_runtime_config_handoff"
        blockers = ["owner_runtime_config_present is False"]
    elif not input_data.credential_reference_declared:
        status = "CREDENTIAL_REFERENCE_REQUIRED"
        next_stage = "credential_persistence_owner_handoff"
        blockers = ["credential_reference_declared is False"]
    elif input_data.credential_material_present:
        status = "SECRET_MATERIAL_REJECTED"
        next_stage = "remove_secret_material_and_use_reference"
        blockers = ["credential_material_present is True"]
    elif not input_data.account_reference_declared:
        status = "ACCOUNT_REFERENCE_REQUIRED"
        next_stage = "owner_account_reference_handoff"
        blockers = ["account_reference_declared is False"]
    elif not input_data.read_only_capabilities_declared:
        status = "READ_ONLY_CAPABILITY_DECLARATION_REQUIRED"
        next_stage = "declare_read_only_capabilities"
        blockers = ["read_only_capabilities_declared is False"]
    elif not input_data.mutating_capabilities_blocked:
        status = "MUTATING_CAPABILITY_BLOCK_REQUIRED"
        next_stage = "block_mutating_capabilities"
        blockers = ["mutating_capabilities_blocked is False"]
    elif not input_data.network_disabled_for_packet:
        status = "NETWORK_MUST_REMAIN_DISABLED_FOR_THIS_PACKET"
        next_stage = "repo_safe_probe_only"
        blockers = ["network_disabled_for_packet is False"]
    elif (
        input_data.broker_api_called
        or input_data.credentials_read
        or input_data.env_read
        or input_data.order_execution
        or input_data.demo_authorized
        or input_data.live_authorized
    ):
        status = "PROTECTED_BOUNDARY_VIOLATION"
        next_stage = "stop_and_owner_review"
        blockers = [
            "protected flags indicate boundary violation",
        ]
    else:
        status = "BROKER_READ_ONLY_PROBE_CONTRACT_READY"
        next_stage = "credential_persistence_owner_handoff"
        blockers = []

    return BrokerReadOnlyProbeResult(
        probe_status=status,
        current_stage=current_stage,
        next_stage=next_stage,
        blockers=blockers,
        broker_name=input_data.broker_name,
        broker_environment=input_data.broker_environment,
        broker_api_called=False,
        credentials_read=False,
        env_read=False,
        order_execution=False,
        demo_authorized=False,
        live_authorized=False,
        safe_next_action=_safe_next_action_for_status(status),
    )


def input_as_dict(input_data: BrokerReadOnlyProbeInput) -> dict:
    return asdict(input_data)


def result_as_dict(result: BrokerReadOnlyProbeResult) -> dict:
    return asdict(result)

