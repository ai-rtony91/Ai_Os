"""Final review decision gate for Forex closure handoff readiness."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from . import forex_closure_gap_router_v1 as gap_router_lib
from . import forex_final_owner_review_packet_composer_v1 as packet_lib
from . import forex_owner_evidence_return_orchestrator_v1 as orchestrator_lib
from . import forex_readiness_checkpoint_ledger_v1 as ledger_lib
from .forex_final_review_decision_evidence_loader_v1 import (
    EVIDENCE_MISSING,
    EVIDENCE_READY,
    EVIDENCE_REPAIR_REQUIRED,
    EXTERNAL_EVIDENCE_REQUIRED,
    OWNER_EVIDENCE_REQUIRED,
    PROTECTED_AUTHORITY_REQUIRED,
    SAFETY_REJECTED,
    summarize_final_review_evidence,
)

FINAL_REVIEW_GATE_VERSION = "1.0"

FINAL_REVIEW_READY = "FINAL_REVIEW_READY"
FINAL_REVIEW_LOCAL_REPAIR_REQUIRED = "FINAL_REVIEW_LOCAL_REPAIR_REQUIRED"
FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED = "FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED"
FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED = "FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED"
FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED = "FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED"
FINAL_REVIEW_SAFETY_BLOCKED = "FINAL_REVIEW_SAFETY_BLOCKED"
FINAL_REVIEW_DEFERRED_OWNER_VALIDATION = "FINAL_REVIEW_DEFERRED_OWNER_VALIDATION"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _evidence_summary_statuses(evidence_summary: Mapping[str, Any] | None) -> tuple[str, dict[str, int]]:
    summary = summarize_final_review_evidence(evidence_summary or {})
    counts = summary.get("status_counts", {})
    return summary.get("most_critical_status", EVIDENCE_MISSING), counts


def _first_non_empty_text(*items: Any) -> str:
    for item in items:
        if isinstance(item, str) and item.strip():
            return item.strip()
    return ""


def _collect_owner_checklist(decision_payload: Mapping[str, Any]) -> list[str]:
    checklist = [
        "Evidence loader status reviewed",
        "Closure route and owner return payload reviewed",
        "Final owner packet safety flags inspected",
        "Readiness checkpoint events inspected",
        "No trade execution was authorized",
    ]
    if decision_payload.get("status") == FINAL_REVIEW_READY:
        checklist.append("Owner checklist complete: no unresolved blockers")
    else:
        checklist.append("Owner final signature required before ownership handoff")
    return checklist


def _collect_next_safe_actions(status: str) -> list[str]:
    if status == FINAL_REVIEW_SAFETY_BLOCKED:
        return [
            "Remove sensitive assignment text and command references",
            "Re-run evidence loading and decision gate",
        ]
    if status == FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED:
        return [
            "Collect explicit owner-approved evidence for protected authority requirements",
            "Route blockers to protected authority workflow",
        ]
    if status == FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED:
        return [
            "Collect external broker/API evidence in a redacted and approved format",
            "Rerun lane in review mode only",
        ]
    if status == FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED:
        return [
            "Collect owner evidence payloads for missing families",
            "Keep review-only boundaries enabled",
        ]
    if status == FINAL_REVIEW_LOCAL_REPAIR_REQUIRED:
        return [
            "Repair local evidence payload shape and missing sections",
            "Increase validated sample depth where required",
        ]
    if status == FINAL_REVIEW_DEFERRED_OWNER_VALIDATION:
        return [
            "Record owner review hold reasons",
            "Resume in owner governance lane",
        ]
    return [
        "Route is ready for owner review",
        "No trade execution authorization at this stage",
    ]


def _collect_safety_flags(decision_inputs: Mapping[str, Any]) -> dict[str, bool]:
    evidence_summary = decision_inputs.get("evidence_summary", {})
    owner_packet = decision_inputs.get("final_owner_review_packet", {})
    route_payload = decision_inputs.get("closure_gap_route_payload", {})
    checkpoint = decision_inputs.get("readiness_checkpoint_payload", {})

    owner_packet_safety = owner_packet.get("safety", {}) if isinstance(owner_packet, Mapping) else {}
    latest_event = ledger_lib.latest_checkpoint_event(checkpoint)

    checks = {
        "broker_api_calls": bool(
            owner_packet_safety.get("broker_api")
            or owner_packet_safety.get("broker_execution")
            or owner_packet_safety.get("broker_api_calls")
        ),
        "credential_access": bool(owner_packet_safety.get("credential_access") or owner_packet_safety.get("credential_read")),
        "demo_trade_authorized": bool(owner_packet_safety.get("demo_trading") or owner_packet_safety.get("demo_trade")),
        "live_trading_authorized": bool(owner_packet_safety.get("live_trading")),
        "money_movement": bool(owner_packet_safety.get("money_movement")),
        "production_activation": bool(owner_packet_safety.get("production_activation")),
        "route_indicates_safety_block": route_payload.get("route") == gap_router_lib.ROUTE_BLOCKED_BY_SAFETY,
        "checkpoint_route_safety_block": bool(
            latest_event and latest_event.route == "ROUTE_BLOCKED_BY_SAFETY"
        ),
        "env_reads": False,
        "github_or_git_commands": False,
    }
    return checks


def decide_final_review_status(
    *,
    evidence_payload: Mapping[str, Any] | None = None,
    owner_evidence_return_payload: Mapping[str, Any] | None = None,
    closure_gap_route_payload: Mapping[str, Any] | None = None,
    final_owner_review_packet_payload: Mapping[str, Any] | None = None,
    readiness_checkpoint_payload: Mapping[str, Any] | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    evidence_summary, evidence_counts = _evidence_summary_statuses(evidence_payload)
    route = _first_non_empty_text(
        closure_gap_route_payload.get("route") if isinstance(closure_gap_route_payload, Mapping) else None
    )
    packet_status = _first_non_empty_text(
        final_owner_review_packet_payload.get("status") if isinstance(final_owner_review_packet_payload, Mapping) else None
    )
    orchestrator_status = _first_non_empty_text(
        owner_evidence_return_payload.get("route_payload", {}).get("route")
        if isinstance(owner_evidence_return_payload, Mapping)
        else None
    )

    owner_gaps = list(owner_evidence_return_payload.get("validator_payload", {}).get("blockers", [])) if isinstance(owner_evidence_return_payload, Mapping) else []
    if not isinstance(owner_gaps, list):
        owner_gaps = []
    protected_flags = False
    protected_sources: list[str] = []
    if owner_evidence_return_payload:
        safety = owner_evidence_return_payload.get("packet_payload", {}).get("safety", {})
        if isinstance(safety, Mapping):
            for key in ("broker_api", "broker_execution", "credential_access", "live_trading", "money_movement", "production_activation"):
                if _safe_bool(safety.get(key), False):
                    protected_flags = True
                    protected_sources.append(key)
        route_payload = owner_evidence_return_payload.get("route_payload", {})
        if isinstance(route_payload, Mapping) and route_payload.get("route") == orchestrator_lib.FINAL_PACKET_PENDING_OWNER_RETURN if hasattr(orchestrator_lib, "FINAL_PACKET_PENDING_OWNER_RETURN") else False:
            protected_flags = protected_flags

    if evidence_summary == SAFETY_REJECTED:
        final_status = FINAL_REVIEW_SAFETY_BLOCKED
    elif route == gap_router_lib.ROUTE_BLOCKED_BY_SAFETY:
        final_status = FINAL_REVIEW_SAFETY_BLOCKED
    elif packet_status == packet_lib.FINAL_PACKET_BLOCKED:
        final_status = FINAL_REVIEW_SAFETY_BLOCKED
    elif evidence_summary == PROTECTED_AUTHORITY_REQUIRED:
        final_status = FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED
    elif evidence_summary == EXTERNAL_EVIDENCE_REQUIRED:
        final_status = FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED
    elif protected_flags or any(
        marker in _first_non_empty_text(closure_gap_route_payload.get("route") if isinstance(closure_gap_route_payload, Mapping) else None).upper()
        for marker in (gap_router_lib.ROUTE_BLOCKED_BY_SAFETY,)
    ):
        final_status = FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED
    elif (
        evidence_summary == OWNER_EVIDENCE_REQUIRED
        or route == gap_router_lib.ROUTE_OWNER_EVIDENCE_REQUIRED
        or owner_evidence_return_payload is not None
        and owner_evidence_return_payload.get("route_payload", {}).get("status") == "owner_return"
        or orchestrator_status == gap_router_lib.ROUTE_OWNER_EVIDENCE_REQUIRED
    ):
        final_status = FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED
    elif (
        evidence_summary == EVIDENCE_REPAIR_REQUIRED
        or route == gap_router_lib.ROUTE_LOCAL_REPAIR
        or packet_status == packet_lib.FINAL_PACKET_PENDING_LOCAL_REPAIR
    ):
        final_status = FINAL_REVIEW_LOCAL_REPAIR_REQUIRED
    elif evidence_summary == EVIDENCE_MISSING and strict:
        final_status = FINAL_REVIEW_DEFERRED_OWNER_VALIDATION
    elif packet_status == packet_lib.FINAL_PACKET_PENDING_OWNER_RETURN:
        final_status = FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED
    elif packet_status == packet_lib.FINAL_PACKET_PENDING_LOCAL_REPAIR:
        final_status = FINAL_REVIEW_LOCAL_REPAIR_REQUIRED
    elif (
        evidence_summary == EVIDENCE_READY
        and route == gap_router_lib.ROUTE_READY_FOR_REVIEW
        and packet_status == packet_lib.FINAL_PACKET_READY
        and not protected_flags
    ):
        final_status = FINAL_REVIEW_READY
    elif route == gap_router_lib.ROUTE_READY_FOR_REVIEW and packet_status in {packet_lib.FINAL_PACKET_PENDING_OWNER_RETURN, packet_lib.FINAL_PACKET_PENDING_LOCAL_REPAIR}:
        final_status = FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED if packet_status == packet_lib.FINAL_PACKET_PENDING_OWNER_RETURN else FINAL_REVIEW_LOCAL_REPAIR_REQUIRED
    elif evidence_summary in {PROTECTED_AUTHORITY_REQUIRED, EXTERNAL_EVIDENCE_REQUIRED, OWNER_EVIDENCE_REQUIRED, EVIDENCE_REPAIR_REQUIRED}:
        final_status = {
            PROTECTED_AUTHORITY_REQUIRED: FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED,
            EXTERNAL_EVIDENCE_REQUIRED: FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED,
            OWNER_EVIDENCE_REQUIRED: FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED,
            EVIDENCE_REPAIR_REQUIRED: FINAL_REVIEW_LOCAL_REPAIR_REQUIRED,
        }[evidence_summary]
    elif evidence_summary == EVIDENCE_MISSING:
        final_status = FINAL_REVIEW_DEFERRED_OWNER_VALIDATION
    else:
        final_status = FINAL_REVIEW_DEFERRED_OWNER_VALIDATION

    decision_inputs = {
        "evidence_payload": evidence_payload or {},
        "owner_evidence_return_payload": owner_evidence_return_payload or {},
        "closure_gap_route_payload": closure_gap_route_payload or {},
        "final_owner_review_packet_payload": final_owner_review_packet_payload or {},
        "readiness_checkpoint_payload": readiness_checkpoint_payload or {},
        "strict": strict,
    }
    next_safe_actions = _collect_next_safe_actions(final_status)
    owner_checklist = _collect_owner_checklist(
        {
            "status": final_status,
            "evidence_summary": evidence_summary,
            "route": route,
        },
    )

    return {
        "decision_gate_version": FINAL_REVIEW_GATE_VERSION,
        "generated_at": _now_iso(),
        "status": final_status,
        "status_reason": _first_non_empty_text(
            final_owner_review_packet_payload.get("status", ""),
            closure_gap_route_payload.get("route", ""),
            orchestrator_status,
            "",
        ) or final_status,
        "evidence_summary": summarize_final_review_evidence(evidence_payload or {}),
        "owner_evidence_packet_status": packet_status,
        "closure_route_status": route,
        "readiness_checkpoint_status": readiness_checkpoint_payload.get("checkpoint_event", readiness_checkpoint_payload.get("event", "NOT_READY")) if isinstance(readiness_checkpoint_payload, Mapping) else "NOT_READY",
        "evidence_counts": evidence_counts,
        "blocked_by_protected_authority": protected_flags,
        "protected_blocks": list(dict.fromkeys(protected_sources)),
        "owner_gaps": list(owner_gaps),
        "next_safe_actions": next_safe_actions,
        "owner_decision_checklist": owner_checklist,
        "owner_input_blockers": list(owner_gaps),
        "decision_input_keys": sorted(decision_inputs.keys()),
        "no_execution_safety_flags": _collect_safety_flags(decision_inputs),
    }


def summarize_final_review_decision(decision_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    payload = dict(decision_payload or {})
    safe_flags = payload.get("no_execution_safety_flags", {})
    return {
        "decision_status": payload.get("status"),
        "status_reason": payload.get("status_reason"),
        "ready_for_owner_review": payload.get("status") == FINAL_REVIEW_READY,
        "safety_blocked": payload.get("status") == FINAL_REVIEW_SAFETY_BLOCKED,
        "protected_authority_required": payload.get("status") == FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED,
        "external_evidence_required": payload.get("status") == FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED,
        "owner_evidence_required": payload.get("status") == FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED,
        "local_repair_required": payload.get("status") == FINAL_REVIEW_LOCAL_REPAIR_REQUIRED,
        "deferred_owner_validation": payload.get("status") == FINAL_REVIEW_DEFERRED_OWNER_VALIDATION,
        "broker_api_calls": bool(safe_flags.get("broker_api_calls", False)),
        "credential_access": bool(safe_flags.get("credential_access", False)),
        "money_movement": bool(safe_flags.get("money_movement", False)),
        "production_activation": bool(safe_flags.get("production_activation", False)),
        "demo_live_authorized": bool(
            safe_flags.get("demo_trade_authorized", False) or safe_flags.get("live_trading_authorized", False),
        ),
    }


def final_review_decision_to_markdown(payload: Mapping[str, Any]) -> str:
    lines = [
        "# Forex Final Review Decision Gate V1",
        f"Generated: {payload.get('generated_at')}",
        f"Status: {payload.get('status')}",
        f"Reason: {payload.get('status_reason')}",
        "",
        f"Evidence summary status: {payload.get('evidence_summary', {}).get('most_critical_status')}",
        f"Closure route: {payload.get('closure_route_status')}",
        f"Packet status: {payload.get('owner_evidence_packet_status')}",
        "",
        "## No-Execution Safety Flags",
    ]
    for key, value in payload.get("no_execution_safety_flags", {}).items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Owner Decision Checklist")
    for item in payload.get("owner_decision_checklist", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Next Safe Actions")
    for item in payload.get("next_safe_actions", []):
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Owner Publish Handoff",
            "- Owner publish remains Human Owner authority only.",
            "- Codex must not run git add, git commit, git push, gh pr create, gh pr checks, or gh pr merge.",
            "- Human Owner may publish only after local py_compile, pytest, CLI write-report, and git diff --check pass.",
            "",
            "## Merge Handoff",
            "- Merge is separate from owner publish.",
            "- Human Owner may run PR checks and merge only after GitHub reports all required checks successful.",
            "- Use PR_NUMBER only after the Human Owner creates the PR.",
            "- This artifact does not authorize broker/API access, credential access, demo/live trading, order placement, money movement, or production activation.",
        ],
    )
    return "\n".join(lines)


def final_review_decision_to_jsonable_dict(payload: Mapping[str, Any]) -> dict[str, Any]:
    evidence_summary = payload.get("evidence_summary")
    if not isinstance(evidence_summary, Mapping):
        evidence_summary = {}

    return {
        "decision_gate_version": payload.get("decision_gate_version", FINAL_REVIEW_GATE_VERSION),
        "generated_at": payload.get("generated_at"),
        "status": payload.get("status"),
        "status_reason": payload.get("status_reason"),
        "evidence_summary": evidence_summary,
        "owner_evidence_packet_status": payload.get("owner_evidence_packet_status"),
        "closure_route_status": payload.get("closure_route_status"),
        "ready_for_owner_review": payload.get("status") == FINAL_REVIEW_READY,
        "safe_actions": list(payload.get("next_safe_actions", [])),
        "owner_decision_checklist": list(payload.get("owner_decision_checklist", [])),
        "no_execution_safety_flags": dict(payload.get("no_execution_safety_flags", {})),
        "evidence_counts": dict(payload.get("evidence_counts", {})),
    }


__all__ = [
    "FINAL_REVIEW_DEFERRED_OWNER_VALIDATION",
    "FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED",
    "FINAL_REVIEW_LOCAL_REPAIR_REQUIRED",
    "FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED",
    "FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED",
    "FINAL_REVIEW_READY",
    "FINAL_REVIEW_SAFETY_BLOCKED",
    "decide_final_review_status",
    "final_review_decision_to_jsonable_dict",
    "final_review_decision_to_markdown",
    "summarize_final_review_decision",
]
