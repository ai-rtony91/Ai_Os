"""AIOS Forex Packet I: runtime orchestration binding.

Aggregates local-only broker bridge readiness signals. No broker SDK,
network transport, endpoint calls, credentials, account IDs, or orders.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Tuple

from automation.forex_engine.broker_bridge_runtime_validator_h_v1 import validate_broker_bridge_runtime
from automation.forex_engine.no_order_connector_contracts_g_v1 import NoOrderConnectorContract
from automation.forex_engine.read_only_probe_skeleton_i_v1 import (
    ReadOnlyProbeSkeleton,
    evaluate_read_only_probe,
)


@dataclass(frozen=True)
class RuntimeOrchestrationBinding:
    ready: bool
    blocked_reasons: Tuple[str, ...]
    replay_references: Tuple[str, ...]
    evidence_references: Tuple[str, ...]


def bind_runtime_orchestration(
    *,
    endpoint_mode: str | None,
    credential_metadata: Mapping[str, object] | None,
    account_metadata: Mapping[str, object] | None,
    governance_approved: bool,
    kill_switch_active: bool,
    no_order_connector: NoOrderConnectorContract,
    read_only_probe: ReadOnlyProbeSkeleton,
) -> RuntimeOrchestrationBinding:
    reasons = []

    bridge_result = validate_broker_bridge_runtime(
        endpoint_mode=endpoint_mode,
        credential_metadata=credential_metadata,
        account_metadata=account_metadata,
        governance_approved=governance_approved,
        kill_switch_active=kill_switch_active,
        no_order_connector=no_order_connector,
    )
    reasons.extend(bridge_result.blocked_reasons)

    probe_result = evaluate_read_only_probe(read_only_probe)
    reasons.extend(probe_result.blocked_reasons)

    blocked_reasons = tuple(dict.fromkeys(reasons))
    return RuntimeOrchestrationBinding(
        ready=not blocked_reasons,
        blocked_reasons=blocked_reasons,
        replay_references=probe_result.replay_references,
        evidence_references=probe_result.evidence_references,
    )