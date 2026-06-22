"""Offline broker-demo decision bridge.

This module combines evidence from V1/V2/V3-style checks into a single
deterministic decision for protected demo-readiness review.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Iterable, Mapping, Tuple


BROKER_DEMO_DECISION_READY = "BROKER_DEMO_DECISION_READY"
BROKER_DEMO_DECISION_BLOCKED = "BROKER_DEMO_DECISION_BLOCKED"
BROKER_DEMO_DECISION_INVALID = "BROKER_DEMO_DECISION_INVALID"
BROKER_DEMO_DECISION_REVIEW_REQUIRED = "BROKER_DEMO_DECISION_REVIEW_REQUIRED"

UNSAFE_FLAGS = (
    "live_trading",
    "order_execution",
    "credentials_read",
    "env_read",
    "network_calls",
    "scheduler_daemon_webhook",
    "raw_broker_payload_persisted",
    "account_id_present",
)

NEXT_SAFE_ACTION_BY_DECISION = {
    BROKER_DEMO_DECISION_READY: "prepare_protected_demo_review_packet",
    BROKER_DEMO_DECISION_BLOCKED: "resolve_blockers_before_demo_review",
    BROKER_DEMO_DECISION_INVALID: "repair_missing_or_invalid_evidence",
    BROKER_DEMO_DECISION_REVIEW_REQUIRED: "human_review_required",
}


def _now_ms(start: float, end: float) -> float:
    return (end - start) * 1000.0


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _is_truthy_ready(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return bool(value)


def _normalize_ready_state(raw: Any) -> Tuple[bool, Any]:
    if raw is None:
        return False, None
    if isinstance(raw, Mapping):
        if "ready" in raw:
            return _is_truthy_ready(raw["ready"]), raw.get("ready")
        if "verdict" in raw:
            verdict = str(raw["verdict"]).upper()
            if verdict.endswith("_READY"):
                return True, verdict
            if verdict.endswith("_BLOCKED") or verdict.endswith("_INVALID"):
                return False, verdict
        if "decision" in raw:
            decision = str(raw["decision"]).upper()
            return decision == BROKER_DEMO_DECISION_READY, decision
    return bool(raw), raw


def _collect_blockers(values: Iterable[str]) -> Tuple[str, ...]:
    return tuple(sorted(set(filter(None, values))))


def _extract_gates(gates: Any) -> Tuple[bool, bool, bool]:
    normalized = _as_mapping(gates)
    kill_switch_enabled = _is_truthy_ready(normalized.get("kill_switch_enabled", False))
    max_loss_gate_clear = _is_truthy_ready(normalized.get("max_loss_gate_clear", True))
    daily_stop_clear = _is_truthy_ready(normalized.get("daily_stop_clear", True))
    return kill_switch_enabled, max_loss_gate_clear, daily_stop_clear


def _extract_unsafe_flags(*payloads: Any) -> Dict[str, bool]:
    flags: Dict[str, bool] = {key: False for key in UNSAFE_FLAGS}
    for payload in payloads:
        mapping = _as_mapping(payload)
        for key in UNSAFE_FLAGS:
            if key in mapping:
                flags[key] = bool(mapping[key]) or flags[key]
    return flags


def _is_integration_ready(evidence: Any) -> bool:
    prepared = _as_mapping(evidence)
    if not prepared:
        return False
    # V1/V2 styles usually export ready-like keys.
    if "integration_ready" in prepared:
        return _is_truthy_ready(prepared.get("integration_ready"))
    if "connector_ready" in prepared:
        return _is_truthy_ready(prepared.get("connector_ready"))
    ready, _ = _normalize_ready_state(prepared)
    return ready


def _is_connector_ready(evidence: Any) -> bool:
    prepared = _as_mapping(evidence)
    if not prepared:
        return False
    if "connector_ready" in prepared:
        return _is_truthy_ready(prepared.get("connector_ready"))
    if "connector_probe_ready" in prepared:
        return _is_truthy_ready(prepared.get("connector_probe_ready"))
    return _is_truthy_ready(prepared.get("ready", False))


def _is_demo_data_ready(evidence: Any) -> bool:
    prepared = _as_mapping(evidence)
    if not prepared:
        return False
    if "demo_data_ready" in prepared:
        return _is_truthy_ready(prepared.get("demo_data_ready"))
    if "decision" in prepared:
        return _is_truthy_ready(prepared["decision"] == "BROKER_DEMO_DATA_READY")
    if "verdict" in prepared:
        return _is_truthy_ready(prepared["verdict"] == "BROKER_DEMO_DATA_READY")
    if "ready" in prepared:
        return _is_truthy_ready(prepared.get("ready"))
    return False


def evaluate_broker_demo_decision(
    integration: Any,
    connector_probe: Any,
    demo_data: Any,
    gates: Any = None,
) -> Dict[str, Any]:
    start = time.perf_counter()
    integration_read_start = time.perf_counter()
    integration_ready = bool(integration)
    integration_verdict = BROKER_DEMO_DECISION_INVALID
    if integration_ready:
        integration_ready = _is_integration_ready(integration)
        integration_verdict = (
            BROKER_DEMO_DECISION_READY if integration_ready else BROKER_DEMO_DECISION_INVALID
        )
    integration_read_ms = _now_ms(integration_read_start, time.perf_counter())

    connector_read_start = time.perf_counter()
    connector_ready = bool(connector_probe)
    connector_verdict = BROKER_DEMO_DECISION_INVALID
    if connector_ready:
        connector_ready = _is_connector_ready(connector_probe)
        connector_verdict = (
            BROKER_DEMO_DECISION_READY if connector_ready else BROKER_DEMO_DECISION_BLOCKED
        )
    connector_read_ms = _now_ms(connector_read_start, time.perf_counter())

    demo_data_read_start = time.perf_counter()
    demo_data_ready = bool(demo_data)
    demo_data_verdict = BROKER_DEMO_DECISION_INVALID
    if demo_data_ready:
        demo_data_ready = _is_demo_data_ready(demo_data)
        demo_data_verdict = (
            BROKER_DEMO_DECISION_READY if demo_data_ready else BROKER_DEMO_DECISION_BLOCKED
        )
    demo_data_read_ms = _now_ms(demo_data_read_start, time.perf_counter())

    safety_gate_start = time.perf_counter()
    kill_switch_enabled, max_loss_gate_clear, daily_stop_clear = _extract_gates(gates)
    unsafe_flags = _extract_unsafe_flags(integration, connector_probe, demo_data, gates)
    blockers = []
    if integration is None:
        blockers.append("integration_evidence_missing")
    if connector_probe is None:
        blockers.append("connector_probe_missing")
    if demo_data is None:
        blockers.append("demo_data_missing")

    if not integration_ready:
        blockers.append("integration_not_ready")
    if not connector_ready:
        blockers.append("connector_not_ready")
    if not demo_data_ready:
        blockers.append("demo_data_not_ready")

    if kill_switch_enabled:
        blockers.append("kill_switch_enabled")
    if not max_loss_gate_clear:
        blockers.append("max_loss_gate_blocked")
    if not daily_stop_clear:
        blockers.append("daily_stop_blocked")

    for key, value in unsafe_flags.items():
        if value:
            blockers.append(f"unsafe_flag_{key}")

    blockers = _collect_blockers(blockers)
    safety_gate_ms = _now_ms(safety_gate_start, time.perf_counter())

    decision_mapping_start = time.perf_counter()
    if integration is None or connector_probe is None or demo_data is None:
        decision = BROKER_DEMO_DECISION_INVALID
    elif not blockers:
        decision = BROKER_DEMO_DECISION_READY
    elif (
        integration_verdict == BROKER_DEMO_DECISION_INVALID
        or connector_verdict == BROKER_DEMO_DECISION_INVALID
        or demo_data_verdict == BROKER_DEMO_DECISION_INVALID
    ):
        decision = BROKER_DEMO_DECISION_INVALID
    elif any(
        b.startswith("unsafe_flag_")
        or b in ("kill_switch_enabled", "max_loss_gate_blocked", "daily_stop_blocked")
        for b in blockers
    ):
        decision = BROKER_DEMO_DECISION_BLOCKED
    elif blockers:
        decision = BROKER_DEMO_DECISION_BLOCKED
    else:
        decision = BROKER_DEMO_DECISION_REVIEW_REQUIRED

    # explicit review-required condition for sanitized data
    demo_verdict = (
        str(_as_mapping(demo_data).get("verdict", "")).upper()
        if _as_mapping(demo_data)
        else ""
    )
    if decision == BROKER_DEMO_DECISION_READY and demo_verdict == "BROKER_DEMO_DATA_SANITIZED":
        decision = BROKER_DEMO_DECISION_REVIEW_REQUIRED

    if decision in (
        BROKER_DEMO_DECISION_INVALID,
        BROKER_DEMO_DECISION_BLOCKED,
        BROKER_DEMO_DECISION_REVIEW_REQUIRED,
    ):
        if not blockers:
            blockers = _collect_blockers(("requires_review",))

    decision_mapping_ms = _now_ms(decision_mapping_start, time.perf_counter())

    return {
        "decision": decision,
        "ready": decision == BROKER_DEMO_DECISION_READY,
        "blockers": blockers,
        "evidence_summary": {
            "integration": {
                "ready": integration_ready,
                "verdict": integration_verdict,
            },
            "connector": {
                "ready": connector_ready,
                "verdict": connector_verdict,
            },
            "demo_data": {
                "ready": demo_data_ready,
                "verdict": demo_data_verdict,
            },
            "gates": {
                "kill_switch_enabled": kill_switch_enabled,
                "max_loss_gate_clear": max_loss_gate_clear,
                "daily_stop_clear": daily_stop_clear,
            },
        },
        "safety_summary": {
            "unsafe_flags": unsafe_flags,
            "unsafe_count": len([value for value in unsafe_flags.values() if value]),
        },
        "next_safe_action": NEXT_SAFE_ACTION_BY_DECISION[decision],
        "latency_budget": {
            "integration_evidence_read_ms": integration_read_ms,
            "connector_probe_read_ms": connector_read_ms,
            "demo_data_read_ms": demo_data_read_ms,
            "safety_gate_eval_ms": safety_gate_ms,
            "decision_mapping_ms": decision_mapping_ms,
            "network_latency_ms": "excluded_offline_default",
            "total_ms": _now_ms(start, time.perf_counter()),
        },
    }
