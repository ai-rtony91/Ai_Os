"""AIOS Forex Packet H: broker bridge runtime validator.

Composes local-only runtime foundation checks. No broker SDK, no network,
no credentials, no account identifiers, no endpoint calls, no orders.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Tuple

from automation.forex_engine.account_metadata_sanitizer_h_v1 import sanitize_account_metadata
from automation.forex_engine.credential_boundary_runtime_contract_h_v1 import validate_credential_boundary
from automation.forex_engine.endpoint_mode_verifier_h_v1 import verify_endpoint_mode
from automation.forex_engine.no_order_connector_contracts_g_v1 import (
    NoOrderConnectorContract,
    evaluate_no_order_connector,
)


@dataclass(frozen=True)
class BrokerBridgeRuntimeValidation:
    ready: bool
    blocked_reasons: Tuple[str, ...]
    sanitized_account_metadata: Mapping[str, object]


def validate_broker_bridge_runtime(
    *,
    endpoint_mode: str | None,
    credential_metadata: Mapping[str, object] | None,
    account_metadata: Mapping[str, object] | None,
    governance_approved: bool,
    kill_switch_active: bool,
    no_order_connector: NoOrderConnectorContract,
) -> BrokerBridgeRuntimeValidation:
    reasons = []

    endpoint_result = verify_endpoint_mode(endpoint_mode)
    reasons.extend(endpoint_result.blocked_reasons)

    credential_result = validate_credential_boundary(credential_metadata)
    reasons.extend(credential_result.blocked_reasons)

    sanitized_account_metadata = sanitize_account_metadata(account_metadata)
    if account_metadata and sanitized_account_metadata != dict(account_metadata):
        reasons.append("account_metadata_sanitized")

    if not governance_approved:
        reasons.append("governance_not_approved")

    if kill_switch_active:
        reasons.append("kill_switch_active")

    connector_result = evaluate_no_order_connector(no_order_connector)
    reasons.extend(connector_result.blocked_reasons)

    blocked_reasons = tuple(dict.fromkeys(reasons))
    return BrokerBridgeRuntimeValidation(
        ready=not blocked_reasons,
        blocked_reasons=blocked_reasons,
        sanitized_account_metadata=sanitized_account_metadata,
    )