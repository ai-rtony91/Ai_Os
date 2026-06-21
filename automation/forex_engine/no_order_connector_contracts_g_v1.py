"""AIOS Forex Packet G: no-order connector contracts.

This module is local-only contract logic. It creates no broker connectivity,
no credentials, no account access, no network calls, and no order execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Tuple


class EndpointMode(str, Enum):
    DEMO = "DEMO"
    LIVE = "LIVE"


class KillSwitchState(str, Enum):
    CLEAR = "CLEAR"
    ACTIVE = "ACTIVE"


class GovernanceStatus(str, Enum):
    APPROVED = "APPROVED"
    NOT_APPROVED = "NOT_APPROVED"


PROHIBITED_CAPABILITIES = frozenset(
    {
        "network_transport",
        "broker_sdk",
        "credential_access",
        "account_identifier_access",
        "order_place",
        "order_modify",
        "order_cancel",
        "position_mutate",
        "live_trading",
        "demo_trading_execution",
    }
)

ALLOWED_CAPABILITIES = frozenset(
    {
        "read_only_planning",
        "no_order_planning",
        "blocked_attempt_recording",
    }
)


@dataclass(frozen=True)
class NoOrderConnectorContract:
    connector_id: str
    connector_mode: str
    endpoint_mode: str
    capabilities: Tuple[str, ...] = field(default_factory=tuple)
    kill_switch_state: str = KillSwitchState.CLEAR.value
    credential_boundary_clear: bool = True
    account_boundary_clear: bool = True
    governance_status: str = GovernanceStatus.APPROVED.value
    blocked_reasons: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ConnectorReadinessResult:
    ready: bool
    blocked_reasons: Tuple[str, ...]


def normalize_capabilities(capabilities: Iterable[str]) -> Tuple[str, ...]:
    return tuple(sorted({str(capability).strip() for capability in capabilities if str(capability).strip()}))


def evaluate_no_order_connector(contract: NoOrderConnectorContract) -> ConnectorReadinessResult:
    reasons = list(contract.blocked_reasons)

    if not contract.connector_id.strip():
        reasons.append("connector_id_missing")

    if not contract.endpoint_mode:
        reasons.append("endpoint_mode_missing")
    elif contract.endpoint_mode != EndpointMode.DEMO.value:
        reasons.append("endpoint_mode_not_demo")

    normalized_capabilities = normalize_capabilities(contract.capabilities)
    prohibited_found = sorted(set(normalized_capabilities).intersection(PROHIBITED_CAPABILITIES))
    for capability in prohibited_found:
        reasons.append(f"prohibited_capability:{capability}")

    if "read_only_planning" not in normalized_capabilities:
        reasons.append("read_only_planning_missing")

    if "no_order_planning" not in normalized_capabilities:
        reasons.append("no_order_planning_missing")

    if contract.kill_switch_state != KillSwitchState.CLEAR.value:
        reasons.append("kill_switch_active")

    if not contract.credential_boundary_clear:
        reasons.append("credential_boundary_not_clear")

    if not contract.account_boundary_clear:
        reasons.append("account_boundary_not_clear")

    if contract.governance_status != GovernanceStatus.APPROVED.value:
        reasons.append("governance_not_approved")

    deduped_reasons = tuple(dict.fromkeys(reasons))
    return ConnectorReadinessResult(ready=not deduped_reasons, blocked_reasons=deduped_reasons)


def build_demo_no_order_contract(
    connector_id: str,
    *,
    capabilities: Iterable[str] | None = None,
    kill_switch_state: str = KillSwitchState.CLEAR.value,
    credential_boundary_clear: bool = True,
    account_boundary_clear: bool = True,
    governance_status: str = GovernanceStatus.APPROVED.value,
) -> NoOrderConnectorContract:
    base_capabilities = {
        "read_only_planning",
        "no_order_planning",
        "blocked_attempt_recording",
    }
    if capabilities:
        base_capabilities.update(capabilities)

    return NoOrderConnectorContract(
        connector_id=connector_id,
        connector_mode="NO_ORDER_CONNECTOR_CONTRACT",
        endpoint_mode=EndpointMode.DEMO.value,
        capabilities=normalize_capabilities(base_capabilities),
        kill_switch_state=kill_switch_state,
        credential_boundary_clear=credential_boundary_clear,
        account_boundary_clear=account_boundary_clear,
        governance_status=governance_status,
    )


def assert_no_order_connector_ready(contract: NoOrderConnectorContract) -> NoOrderConnectorContract:
    result = evaluate_no_order_connector(contract)
    if not result.ready:
        raise ValueError(";".join(result.blocked_reasons))
    return contract