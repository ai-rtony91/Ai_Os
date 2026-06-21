"""AIOS Forex Packet I: read-only probe skeleton.

Local-only skeleton. No broker SDK, network transport, endpoint calls,
credentials, account access, order execution, demo trading, or live trading.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Tuple


PROHIBITED_PROBE_CAPABILITIES = frozenset(
    {
        "network_transport",
        "endpoint_access",
        "credential_access",
        "account_access",
        "order_execution",
        "order_place",
        "order_modify",
        "order_cancel",
        "position_mutate",
        "demo_trading_execution",
        "live_trading",
    }
)


@dataclass(frozen=True)
class ReadOnlyProbeSkeleton:
    probe_id: str
    probe_mode: str = "READ_ONLY_PROBE_SKELETON"
    capabilities: Tuple[str, ...] = field(default_factory=lambda: ("read_only_probe_planning",))
    replay_references: Tuple[str, ...] = field(default_factory=tuple)
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    blocked_reasons: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ReadOnlyProbeReadiness:
    ready: bool
    blocked_reasons: Tuple[str, ...]
    replay_references: Tuple[str, ...]
    evidence_references: Tuple[str, ...]


def normalize_items(items: Iterable[str]) -> Tuple[str, ...]:
    return tuple(sorted({str(item).strip() for item in items if str(item).strip()}))


def evaluate_read_only_probe(probe: ReadOnlyProbeSkeleton) -> ReadOnlyProbeReadiness:
    reasons = list(probe.blocked_reasons)

    if not probe.probe_id.strip():
        reasons.append("probe_id_missing")

    capabilities = normalize_items(probe.capabilities)
    if "read_only_probe_planning" not in capabilities:
        reasons.append("read_only_probe_planning_missing")

    for capability in sorted(set(capabilities).intersection(PROHIBITED_PROBE_CAPABILITIES)):
        reasons.append(f"prohibited_probe_capability:{capability}")

    blocked_reasons = tuple(dict.fromkeys(reasons))
    return ReadOnlyProbeReadiness(
        ready=not blocked_reasons,
        blocked_reasons=blocked_reasons,
        replay_references=normalize_items(probe.replay_references),
        evidence_references=normalize_items(probe.evidence_references),
    )