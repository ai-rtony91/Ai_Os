"""Orchestrator for final review decision lane in Forex closure workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

from . import forex_closure_gap_router_v1 as gap_router_lib
from . import forex_final_review_decision_evidence_loader_v1 as evidence_loader_lib
from . import forex_final_review_decision_gate_v1 as gate_lib
from . import forex_demo_readiness_handoff_builder_v1 as handoff_lib
from . import forex_owner_decision_authority_gate_v1 as authority_lib
from . import forex_owner_evidence_return_orchestrator_v1 as return_orchestrator_lib
from . import forex_protected_action_boundary_verifier_v1 as boundary_lib
from . import forex_readiness_checkpoint_ledger_v1 as ledger_lib

FINAL_REVIEW_DECISION_ORCHESTRATOR_VERSION = "1.0"

ORCHESTRATOR_FINAL_REVIEW_READY = "ORCHESTRATOR_FINAL_REVIEW_READY"
ORCHESTRATOR_LOCAL_REPAIR_REQUIRED = "ORCHESTRATOR_LOCAL_REPAIR_REQUIRED"
ORCHESTRATOR_OWNER_EVIDENCE_REQUIRED = "ORCHESTRATOR_OWNER_EVIDENCE_REQUIRED"
ORCHESTRATOR_EXTERNAL_EVIDENCE_REQUIRED = "ORCHESTRATOR_EXTERNAL_EVIDENCE_REQUIRED"
ORCHESTRATOR_PROTECTED_AUTHORITY_REQUIRED = "ORCHESTRATOR_PROTECTED_AUTHORITY_REQUIRED"
ORCHESTRATOR_SAFETY_BLOCKED = "ORCHESTRATOR_SAFETY_BLOCKED"
ORCHESTRATOR_DEFERRED_OWNER_VALIDATION = "ORCHESTRATOR_DEFERRED_OWNER_VALIDATION"

PACKET_ID = "AIOS-FOREX-FINAL-REVIEW-DECISION-ORCHESTRATOR-V1"
LANE = "forex_final_review_decision_orchestrator_v1"


def _default_fixture_path(repo_root: Path) -> Path:
    return repo_root / "tests\\fixtures\\forex_delivery\\final_review_decision_gate_v1"


def _status_from_gate(gate_status: str) -> str:
    mapping = {
        gate_lib.FINAL_REVIEW_READY: ORCHESTRATOR_FINAL_REVIEW_READY,
        gate_lib.FINAL_REVIEW_LOCAL_REPAIR_REQUIRED: ORCHESTRATOR_LOCAL_REPAIR_REQUIRED,
        gate_lib.FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED: ORCHESTRATOR_OWNER_EVIDENCE_REQUIRED,
        gate_lib.FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED: ORCHESTRATOR_EXTERNAL_EVIDENCE_REQUIRED,
        gate_lib.FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED: ORCHESTRATOR_PROTECTED_AUTHORITY_REQUIRED,
        gate_lib.FINAL_REVIEW_SAFETY_BLOCKED: ORCHESTRATOR_SAFETY_BLOCKED,
        gate_lib.FINAL_REVIEW_DEFERRED_OWNER_VALIDATION: ORCHESTRATOR_DEFERRED_OWNER_VALIDATION,
    }
    return mapping.get(gate_status, ORCHESTRATOR_DEFERRED_OWNER_VALIDATION)


def _build_default_inputs(repo_root: Path, *, strict: bool) -> dict[str, Any]:
    owner_result = return_orchestrator_lib.orchestrate_owner_evidence_return(
        repo_root=repo_root,
        strict=strict,
    )
    return {
        "owner_evidence_return_payload": owner_result,
        "closure_gap_route_payload": owner_result.get("route_payload", {}),
        "final_owner_review_packet_payload": owner_result.get("packet_payload", {}),
        "readiness_checkpoint_payload": owner_result.get("checkpoint_ledger", {}),
    }


def run_final_review_decision_orchestration(
    *,
    repo_root: str | Path | None = None,
    evidence_paths: Iterable[str | Path] | None = None,
    strict: bool = False,
    owner_evidence_return_payload: Mapping[str, Any] | None = None,
    closure_gap_route_payload: Mapping[str, Any] | None = None,
    final_owner_review_packet_payload: Mapping[str, Any] | None = None,
    readiness_checkpoint_payload: Mapping[str, Any] | None = None,
    protected_boundary_payload: Mapping[str, Any] | None = None,
    protected_boundary_paths: Iterable[str | Path] | None = None,
    branch: str = "lane/forex-final-review-decision-gate-v1",
    ) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[2]
    default_paths = (str(_default_fixture_path(root)),)
    evidence_payload = evidence_loader_lib.load_final_review_evidence_paths(
        evidence_paths if evidence_paths is not None else default_paths,
        strict=strict,
        source_family="final_review_decision_gate_v1",
    )

    default_owner_inputs = _build_default_inputs(root, strict=strict)
    owner_payload = dict(owner_evidence_return_payload or {})
    if not owner_payload:
        owner_payload = default_owner_inputs["owner_evidence_return_payload"]
    route_payload = dict(closure_gap_route_payload or {})
    if not route_payload:
        route_payload = default_owner_inputs["closure_gap_route_payload"]
    packet_payload = dict(final_owner_review_packet_payload or {})
    if not packet_payload:
        packet_payload = default_owner_inputs["final_owner_review_packet_payload"]
    checkpoint_payload = dict(readiness_checkpoint_payload or {})
    if not checkpoint_payload:
        checkpoint_payload = default_owner_inputs["readiness_checkpoint_payload"]

    boundary_input = (
        dict(protected_boundary_payload)
        if isinstance(protected_boundary_payload, Mapping)
        else {}
    )
    boundary_payload = boundary_input or {}
    boundary_payload["owner_evidence_return_payload"] = owner_payload
    boundary_payload["final_review_evidence_summary"] = evidence_payload

    boundary_result = (
        boundary_lib.verify_protected_action_boundaries_payload(boundary_payload, strict=strict)
        if not protected_boundary_paths
        else boundary_lib.verify_protected_action_boundaries_files(
            [str(p) for p in protected_boundary_paths],
            strict=strict,
        )
    )

    decision_payload = gate_lib.decide_final_review_status(
        evidence_payload=evidence_payload,
        owner_evidence_return_payload=owner_payload,
        closure_gap_route_payload=route_payload,
        final_owner_review_packet_payload=packet_payload,
        readiness_checkpoint_payload=checkpoint_payload,
        strict=strict,
    )
    handoff_payload = handoff_lib.build_demo_readiness_handoff(
        decision_payload,
        strict=strict,
    )
    authority_payload = authority_lib.evaluate_owner_decision_authority(
        decision_payload,
        demo_readiness_handoff=handoff_payload,
        strict=strict,
    )

    boundary_status_override = (
        str(boundary_input.get("status", "")) if isinstance(boundary_input, Mapping) else ""
    )
    if boundary_status_override in {
        gate_lib.FINAL_REVIEW_READY,
        gate_lib.FINAL_REVIEW_LOCAL_REPAIR_REQUIRED,
        gate_lib.FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED,
        gate_lib.FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED,
        gate_lib.FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED,
        gate_lib.FINAL_REVIEW_SAFETY_BLOCKED,
        gate_lib.FINAL_REVIEW_DEFERRED_OWNER_VALIDATION,
    }:
        orchestrator_status = _status_from_gate(boundary_status_override)
    else:
        orchestrator_status = _status_from_gate(decision_payload.get("status", ""))
    if authority_payload.get("status") == authority_lib.OWNER_AUTHORITY_BLOCKED_BY_PROTECTED_DEPENDENCY:
        orchestrator_status = ORCHESTRATOR_PROTECTED_AUTHORITY_REQUIRED
    if authority_payload.get("status") == authority_lib.OWNER_AUTHORITY_BLOCKED_BY_MISSING_EVIDENCE:
        orchestrator_status = ORCHESTRATOR_OWNER_EVIDENCE_REQUIRED
    if authority_payload.get("status") == authority_lib.OWNER_AUTHORITY_SAFETY_BLOCKED:
        orchestrator_status = ORCHESTRATOR_SAFETY_BLOCKED
    if authority_payload.get("status") == authority_lib.OWNER_AUTHORITY_DEFERRED:
        orchestrator_status = ORCHESTRATOR_DEFERRED_OWNER_VALIDATION

    ledger = ledger_lib.build_readiness_checkpoint_ledger(
        PACKET_ID,
        branch=branch,
        worktree=str(root),
        lane=LANE,
    )
    ledger = ledger_lib.append_checkpoint_event(
        ledger,
        stage="evidence_loader",
        status=evidence_payload.get("most_critical_status"),
        route=None,
        blockers=evidence_payload.get("most_critical_status", "") and [f"loader_status:{evidence_payload.get('most_critical_status')}"] or [],
        notes=["loaded final review evidence"],
        metadata={"record_count": evidence_payload.get("record_count", 0)},
    )
    ledger = ledger_lib.append_checkpoint_event(
        ledger,
        stage="protected_boundary_verification",
        status=boundary_result.get("status"),
        route=route_payload.get("route"),
        blockers=[item["label"] for item in boundary_result.get("findings", [])],
        notes=[f"boundary_verification:{boundary_result.get('status')}"],
        metadata={"match_count": boundary_result.get("match_count", 0)},
    )
    ledger = ledger_lib.append_checkpoint_event(
        ledger,
        stage="final_review_gate",
        status=orchestrator_status,
        route=route_payload.get("route"),
        blockers=decision_payload.get("owner_gaps", []),
        notes=[f"final_review_status:{decision_payload.get('status')}"],
        metadata={"next_safe_actions": decision_payload.get("next_safe_actions", [])},
    )
    ledger = ledger_lib.append_checkpoint_event(
        ledger,
        stage="demo_readiness_handoff",
        status=handoff_payload.get("status"),
        notes=[f"handoff_status:{handoff_payload.get('status')}"],
    )
    ledger = ledger_lib.append_checkpoint_event(
        ledger,
        stage="owner_authority_gate",
        status=authority_payload.get("status"),
        notes=[f"authority_status:{authority_payload.get('status')}"],
    )

    return {
        "orchestrator_version": FINAL_REVIEW_DECISION_ORCHESTRATOR_VERSION,
        "generated_at": ledger.get("generated_at"),
        "strict_mode": bool(strict),
        "branch": branch,
        "worktree": str(root),
        "repo_root": str(root),
        "status": orchestrator_status,
        "evidence_payload": evidence_payload,
        "boundary_result": boundary_result,
        "gate_result": decision_payload,
        "handoff_result": handoff_payload,
        "authority_result": authority_payload,
        "checkpoint_ledger": ledger,
        "safety": {
            "local_only": True,
            "repo_mutation": False,
            "broker_api_calls": False,
            "credential_access": False,
            "demo_live_execution": False,
            "money_movement": False,
            "production_activation": False,
        },
    }


def summarize_final_review_decision_orchestration(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": result.get("status"),
        "worktree": result.get("worktree"),
        "branch": result.get("branch"),
        "evidence_critical_status": result.get("evidence_payload", {})
        .get("most_critical_status"),
        "boundary_status": result.get("boundary_result", {}).get("status"),
        "gate_status": result.get("gate_result", {}).get("status"),
        "handoff_status": result.get("handoff_result", {}).get("status"),
        "authority_status": result.get("authority_result", {}).get("status"),
        "checkpoint_event_count": result.get("checkpoint_ledger", {}).get("event_count"),
        "safe_for_review_only": all(
            [
                not result.get("gate_result", {}).get("blocked_by_protected_authority", False),
                not result.get("gate_result", {}).get("no_execution_safety_flags", {}).get("broker_api_calls", False),
                not result.get("safety", {}).get("money_movement", False),
            ],
        ),
    }


def final_review_decision_orchestration_to_markdown(result: Mapping[str, Any]) -> str:
    summary = summarize_final_review_decision_orchestration(result)
    lines = [
        "# Forex Final Review Decision Orchestrator V1",
        f"Generated: {result.get('generated_at')}",
        f"Status: {summary.get('status')}",
        f"Branch: {summary.get('branch')}",
        f"Worktree: {summary.get('worktree')}",
        f"Evidence critical status: {summary.get('evidence_critical_status')}",
        f"Boundary status: {summary.get('boundary_status')}",
        f"Gate status: {summary.get('gate_status')}",
        f"Handoff status: {summary.get('handoff_status')}",
        f"Authority status: {summary.get('authority_status')}",
        f"Checkpoint events: {summary.get('checkpoint_event_count')}",
    ]
    return "\n".join(lines)


def final_review_decision_orchestration_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "orchestrator_version": result.get("orchestrator_version", FINAL_REVIEW_DECISION_ORCHESTRATOR_VERSION),
        "generated_at": result.get("generated_at"),
        "status": result.get("status"),
        "strict_mode": bool(result.get("strict_mode", False)),
        "branch": result.get("branch"),
        "worktree": result.get("worktree"),
        "repo_root": result.get("repo_root"),
        "evidence_payload": dict(result.get("evidence_payload", {})),
        "boundary_result": dict(result.get("boundary_result", {})),
        "gate_result": dict(result.get("gate_result", {})),
        "handoff_result": dict(result.get("handoff_result", {})),
        "authority_result": dict(result.get("authority_result", {})),
        "checkpoint_ledger": result.get("checkpoint_ledger"),
        "safety": dict(result.get("safety", {})),
    }


__all__ = [
    "ORCHESTRATOR_DEFERRED_OWNER_VALIDATION",
    "ORCHESTRATOR_EXTERNAL_EVIDENCE_REQUIRED",
    "ORCHESTRATOR_FINAL_REVIEW_READY",
    "ORCHESTRATOR_LOCAL_REPAIR_REQUIRED",
    "ORCHESTRATOR_OWNER_EVIDENCE_REQUIRED",
    "ORCHESTRATOR_PROTECTED_AUTHORITY_REQUIRED",
    "ORCHESTRATOR_SAFETY_BLOCKED",
    "FINAL_REVIEW_DECISION_ORCHESTRATOR_VERSION",
    "run_final_review_decision_orchestration",
    "summarize_final_review_decision_orchestration",
    "final_review_decision_orchestration_to_markdown",
    "final_review_decision_orchestration_to_jsonable_dict",
]
