"""AIOS Forex Packet I: final demo-readiness validator.

Local-only readiness composition. No broker SDK, network, endpoint calls,
credentials, account IDs, orders, demo trading, or live trading.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping, Tuple

from automation.forex_engine.no_order_connector_contracts_g_v1 import NoOrderConnectorContract
from automation.forex_engine.read_only_probe_skeleton_i_v1 import ReadOnlyProbeSkeleton
from automation.forex_engine.runtime_orchestration_binding_i_v1 import bind_runtime_orchestration


ReadinessStatus = Literal["READY", "NOT_READY"]


@dataclass(frozen=True)
class FinalDemoReadiness:
    status: ReadinessStatus
    blocked_reasons: Tuple[str, ...]
    replay_references: Tuple[str, ...]
    evidence_references: Tuple[str, ...]


def validate_final_demo_readiness(
    *,
    endpoint_mode: str | None,
    credential_metadata: Mapping[str, object] | None,
    account_metadata: Mapping[str, object] | None,
    governance_approved: bool,
    kill_switch_active: bool,
    no_order_connector: NoOrderConnectorContract,
    read_only_probe: ReadOnlyProbeSkeleton,
) -> FinalDemoReadiness:
    binding = bind_runtime_orchestration(
        endpoint_mode=endpoint_mode,
        credential_metadata=credential_metadata,
        account_metadata=account_metadata,
        governance_approved=governance_approved,
        kill_switch_active=kill_switch_active,
        no_order_connector=no_order_connector,
        read_only_probe=read_only_probe,
    )

    return FinalDemoReadiness(
        status="READY" if binding.ready else "NOT_READY",
        blocked_reasons=binding.blocked_reasons,
        replay_references=binding.replay_references,
        evidence_references=binding.evidence_references,
    )