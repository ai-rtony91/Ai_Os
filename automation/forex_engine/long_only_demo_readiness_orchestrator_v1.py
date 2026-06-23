"""Integrated long-only Forex demo readiness orchestrator.

This orchestrator combines sanitized broker proof, profitability evidence depth,
risk policy, supervisor state, and a non-executable order intent preview. It is
preparation-only and always preserves execution_allowed=false.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from automation.forex_engine.forex_trust_safety_audit_v1 import contains_sensitive_material
from automation.forex_engine.long_only_profitability_evidence_depth_gate_v1 import (
    PROFITABILITY_EVIDENCE_DEPTH_READY,
    evaluate_long_only_profitability_evidence_depth,
)
from automation.forex_engine.long_only_risk_policy_contract_v1 import (
    RISK_POLICY_CONTRACT_READY,
    evaluate_long_only_risk_policy_contract,
)
from automation.forex_engine.oanda_long_only_broker_proof_intake_v1 import (
    OANDA_LONG_ONLY_BROKER_PROOF_READY,
    evaluate_oanda_long_only_broker_proof,
)
from automation.forex_engine.oanda_long_only_order_intent_preview_v1 import (
    ORDER_INTENT_PREVIEW_READY,
    build_oanda_long_only_order_intent_preview,
)

AUTONOMOUS_BLOCKED_BY_BROKER_GATE = "AUTONOMOUS_BLOCKED_BY_BROKER_GATE"
AUTONOMOUS_BLOCKED_BY_EVIDENCE_DEPTH = "AUTONOMOUS_BLOCKED_BY_EVIDENCE_DEPTH"
AUTONOMOUS_BLOCKED_BY_RISK = "AUTONOMOUS_BLOCKED_BY_RISK"
AUTONOMOUS_BLOCKED_BY_POLICY = "AUTONOMOUS_BLOCKED_BY_POLICY"
AUTONOMOUS_BLOCKED_BY_EXECUTION_ARMING = "AUTONOMOUS_BLOCKED_BY_EXECUTION_ARMING"
AUTONOMOUS_DEMO_PREPARATION_READY = "AUTONOMOUS_DEMO_PREPARATION_READY"
AUTONOMOUS_DEMO_READY_PREVIEW_ONLY = "AUTONOMOUS_DEMO_READY_PREVIEW_ONLY"


def _is_result(payload: Any, ready_status: str) -> bool:
    return isinstance(payload, Mapping) and payload.get("status") in {ready_status} and "blockers" in payload


def _blocked_result(status: str, *, blockers: list[str], warnings: list[str] | None = None) -> dict[str, Any]:
    return {
        "status": status,
        "ready": False,
        "demo_preparation_ready": False,
        "demo_preview_ready": False,
        "broker_gate_status": None,
        "evidence_depth_status": None,
        "risk_policy_status": None,
        "order_intent_preview_status": None,
        "supervisor_status": None,
        "candidate_id": None,
        "strategy_id": None,
        "instrument": None,
        "direction": None,
        "blockers": list(dict.fromkeys(blockers)),
        "warnings": list(warnings or []),
        "next_safe_action": "provide_sanitized_demo_sandbox_broker_and_account_permission_proof",
        "execution_allowed": False,
        "ready_to_execute": False,
        "demo_order_allowed": False,
        "live_autonomy_allowed": False,
        "short_side_enabled": False,
        "broker_mutation_allowed": False,
        "order_execution_allowed": False,
        "safety_summary": _safety_summary(),
    }


def _safety_summary() -> dict[str, bool]:
    return {
        "credentials_read": False,
        "env_read": False,
        "account_id_read": False,
        "network_call": False,
        "broker_mutation": False,
        "demo_order_placed": False,
        "live_order_placed": False,
        "scheduler_created": False,
        "daemon_created": False,
        "webhook_created": False,
        "background_execution_created": False,
        "execution_allowed": False,
        "ready_to_execute": False,
        "demo_order_allowed": False,
        "live_autonomy_allowed": False,
    }


def _next_safe_action(status: str) -> str:
    if status == AUTONOMOUS_BLOCKED_BY_BROKER_GATE:
        return "provide_complete_sanitized_oanda_demo_practice_broker_proof"
    if status == AUTONOMOUS_BLOCKED_BY_EVIDENCE_DEPTH:
        return "provide_sufficient_long_only_profitability_evidence_depth"
    if status == AUTONOMOUS_BLOCKED_BY_RISK:
        return "repair_long_only_risk_policy_contract"
    if status == AUTONOMOUS_BLOCKED_BY_EXECUTION_ARMING:
        return "repair_non_executable_demo_order_intent_preview"
    if status == AUTONOMOUS_DEMO_PREPARATION_READY:
        return "build_non_executable_order_intent_preview_no_order_authorization"
    if status == AUTONOMOUS_DEMO_READY_PREVIEW_ONLY:
        return "owner_review_preview_and_provide_separate_demo_order_arming_packet_if_approved"
    if status == AUTONOMOUS_BLOCKED_BY_POLICY:
        return "provide_owner_policy_contract_before_any_live_autonomy"
    return "stop_before_any_order_action"


def _normalize_broker_result(broker_proof: Any) -> dict[str, Any]:
    if isinstance(broker_proof, Mapping) and broker_proof.get("status") in {
        OANDA_LONG_ONLY_BROKER_PROOF_READY,
        "OANDA_BROKER_PROOF_BLOCKED",
    }:
        return dict(broker_proof)
    return evaluate_oanda_long_only_broker_proof(broker_proof)


def _normalize_evidence_result(candidate_evidence: Any, thresholds: Mapping[str, Any] | None) -> dict[str, Any]:
    if _is_result(candidate_evidence, PROFITABILITY_EVIDENCE_DEPTH_READY) or (
        isinstance(candidate_evidence, Mapping)
        and candidate_evidence.get("status") == "PROFITABILITY_EVIDENCE_DEPTH_BLOCKED"
        and "blockers" in candidate_evidence
    ):
        return dict(candidate_evidence)
    return evaluate_long_only_profitability_evidence_depth(candidate_evidence, thresholds=thresholds)


def _normalize_risk_result(risk_policy: Any) -> dict[str, Any]:
    if _is_result(risk_policy, RISK_POLICY_CONTRACT_READY) or (
        isinstance(risk_policy, Mapping)
        and risk_policy.get("status") == "RISK_POLICY_CONTRACT_BLOCKED"
        and "blockers" in risk_policy
    ):
        return dict(risk_policy)
    return evaluate_long_only_risk_policy_contract(risk_policy)


def _normalize_preview_result(order_intent: Any) -> dict[str, Any] | None:
    if order_intent is None:
        return None
    if _is_result(order_intent, ORDER_INTENT_PREVIEW_READY) or (
        isinstance(order_intent, Mapping)
        and order_intent.get("status") == "ORDER_INTENT_PREVIEW_BLOCKED"
        and "blockers" in order_intent
    ):
        return dict(order_intent)
    return build_oanda_long_only_order_intent_preview(order_intent)


def evaluate_long_only_demo_readiness(
    *,
    broker_proof: Mapping[str, Any] | None = None,
    candidate_evidence: Mapping[str, Any] | None = None,
    risk_policy: Mapping[str, Any] | None = None,
    order_intent: Mapping[str, Any] | None = None,
    supervisor_state: Mapping[str, Any] | None = None,
    thresholds: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate integrated long-only OANDA demo readiness without execution."""
    for payload in (broker_proof, candidate_evidence, risk_policy, order_intent, supervisor_state):
        if payload is not None and contains_sensitive_material(payload):
            return _blocked_result(
                AUTONOMOUS_BLOCKED_BY_BROKER_GATE,
                blockers=["sensitive_material_detected"],
                warnings=["sensitive_payload_rejected_before_readiness_evaluation"],
            )

    broker_result = _normalize_broker_result(broker_proof)
    evidence_result = _normalize_evidence_result(candidate_evidence, thresholds)
    risk_result = _normalize_risk_result(risk_policy)
    preview_result = _normalize_preview_result(order_intent)
    supervisor_status = (
        supervisor_state.get("status") if isinstance(supervisor_state, Mapping) else None
    )

    candidate_id = evidence_result.get("candidate_id") or (preview_result or {}).get("candidate_id")
    strategy_id = evidence_result.get("strategy_id") or (preview_result or {}).get("strategy_id")
    instrument = evidence_result.get("instrument") or broker_result.get("instrument") or (preview_result or {}).get("instrument")
    direction = evidence_result.get("direction") or (preview_result or {}).get("direction")

    blockers: list[str] = []
    warnings: list[str] = []

    if broker_result.get("status") != OANDA_LONG_ONLY_BROKER_PROOF_READY:
        status = AUTONOMOUS_BLOCKED_BY_BROKER_GATE
        blockers.extend(broker_result.get("blockers", []))
    elif evidence_result.get("status") != PROFITABILITY_EVIDENCE_DEPTH_READY:
        status = AUTONOMOUS_BLOCKED_BY_EVIDENCE_DEPTH
        blockers.extend(evidence_result.get("blockers", []))
    elif risk_result.get("status") != RISK_POLICY_CONTRACT_READY:
        status = AUTONOMOUS_BLOCKED_BY_RISK
        blockers.extend(risk_result.get("blockers", []))
    elif preview_result is None:
        status = AUTONOMOUS_DEMO_PREPARATION_READY
        warnings.append("order_intent_preview_not_built")
    elif preview_result.get("status") != ORDER_INTENT_PREVIEW_READY:
        status = AUTONOMOUS_BLOCKED_BY_EXECUTION_ARMING
        blockers.extend(preview_result.get("blockers", []))
    else:
        status = AUTONOMOUS_DEMO_READY_PREVIEW_ONLY
        warnings.append("preview_only_no_demo_order_authorization")

    demo_preparation_ready = status in {
        AUTONOMOUS_DEMO_PREPARATION_READY,
        AUTONOMOUS_DEMO_READY_PREVIEW_ONLY,
    }
    demo_preview_ready = status == AUTONOMOUS_DEMO_READY_PREVIEW_ONLY

    return {
        "status": status,
        "ready": demo_preview_ready,
        "demo_preparation_ready": demo_preparation_ready,
        "demo_preview_ready": demo_preview_ready,
        "broker_gate_status": broker_result.get("status"),
        "evidence_depth_status": evidence_result.get("status"),
        "risk_policy_status": risk_result.get("status"),
        "order_intent_preview_status": preview_result.get("status") if isinstance(preview_result, Mapping) else None,
        "supervisor_status": supervisor_status,
        "candidate_id": candidate_id,
        "strategy_id": strategy_id,
        "instrument": instrument,
        "direction": direction,
        "blockers": list(dict.fromkeys(blockers)),
        "warnings": list(dict.fromkeys(warnings)),
        "next_safe_action": _next_safe_action(status),
        "execution_allowed": False,
        "ready_to_execute": False,
        "demo_order_allowed": False,
        "live_autonomy_allowed": False,
        "short_side_enabled": False,
        "broker_mutation_allowed": False,
        "order_execution_allowed": False,
        "safety_summary": _safety_summary(),
    }
