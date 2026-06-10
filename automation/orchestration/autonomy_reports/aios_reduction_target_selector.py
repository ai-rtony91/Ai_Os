"""AI_OS reduction target selector (report-only).

This module consumes the Operator Dependency Ledger and selects the next
operator-dependency reduction target. It does not execute runtime tasks,
dispatch workers, perform APPLY, create scheduler or service actions, arm SOS,
touch credentials, call brokers, or mutate live runtime state.

Pure standard library. JSON-only CLI. Deterministic with injected ledger and
timestamp.
"""

from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from typing import Any

from automation.orchestration.autonomy_reports.aios_operator_dependency_ledger import (
    DEPENDENCY_CATEGORIES,
    build_operator_dependency_ledger,
    validate_operator_dependency_ledger,
)


SCHEMA = "AIOS_REDUCTION_TARGET_SELECTOR.v1"
REPORT_MODE = "REPORT_ONLY"

TARGETS = [
    "relay_proof_acceptance_packet",
    "restart_timeouts_proof_planning",
    "retention_rotation_proof_planning",
    "soak_proof_planning",
    "stop_drill_proof_planning",
    "sos_arming_checklist_review",
    "scheduler_registration_checklist_review",
    "operator_dependency_next_report",
]


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _deepcopy(value: Any) -> Any:
    return copy.deepcopy(value)


def _ledger_components(ledger: dict[str, Any]) -> dict[str, dict[str, Any]]:
    components = ledger.get("evaluated_components") if isinstance(ledger, dict) else []
    index: dict[str, dict[str, Any]] = {}
    for component in components if isinstance(components, list) else []:
        if isinstance(component, dict) and isinstance(component.get("component_id"), str):
            index[component["component_id"]] = component
    return index


def _remaining_human_burdens(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    burdens = ledger.get("remaining_human_burdens") if isinstance(ledger, dict) else []
    return [item for item in burdens if isinstance(item, dict)] if isinstance(burdens, list) else []


def _reduced_burdens(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    burdens = ledger.get("reduced_burdens") if isinstance(ledger, dict) else []
    return [item for item in burdens if isinstance(item, dict)] if isinstance(burdens, list) else []


def _ai_os_owned_inputs_used(ledger: dict[str, Any]) -> list[str]:
    return [
        "schema",
        "autonomy_scorecard",
        "next_reduction_target",
        "review_status",
        "proof_status",
        "proof_chain",
        "blockers",
        "human_gates",
        "safe_next_action",
        "remaining_human_burdens",
        "reduced_burdens",
        "validation_status",
        "evaluated_components",
    ]


def _candidate(
    *,
    target_id: str,
    category: str,
    reason: str,
    supported_by: list[str],
    requires_human: bool = True,
    scheduler_required: bool = False,
    sos_required: bool = False,
    live_required: bool = False,
) -> dict[str, Any]:
    return {
        "target_id": target_id,
        "category": category,
        "reason": reason,
        "supported_by": supported_by,
        "requires_human": requires_human,
        "scheduler_required": scheduler_required,
        "sos_required": sos_required,
        "live_required": live_required,
    }


def _selected_from_ledger(ledger: dict[str, Any]) -> dict[str, Any]:
    scorecard = ledger.get("autonomy_scorecard") if isinstance(ledger, dict) else {}
    autonomy_shift = str(scorecard.get("autonomy_shift") or "NONE")
    review_status = str(ledger.get("review_status") or "UNKNOWN")
    proof_status = str(ledger.get("proof_status") or "UNKNOWN")
    next_reduction_target = ledger.get("next_reduction_target") if isinstance(ledger, dict) else {}
    next_target_id = next_reduction_target.get("component_id") if isinstance(next_reduction_target, dict) else None
    blockers = list(ledger.get("blockers") or [])
    human_gates = list(ledger.get("human_gates") or [])
    safe_next_action = str(ledger.get("safe_next_action") or "")

    candidates: list[dict[str, Any]] = []
    rejected_targets: list[dict[str, Any]] = []
    selected_target = ""
    selected_category = ""
    selected_reason = ""
    operator_burden_addressed: list[str] = []

    if review_status == "REVIEWABLE":
        candidates = [
            _candidate(
                target_id="relay_proof_acceptance_packet",
                category="route",
                reason="Relay proof review is reviewable, but human acceptance is still required before any downstream plan.",
                supported_by=["review_status", "proof_status", "safe_next_action", "human_gates"],
            ),
            _candidate(
                target_id="restart_timeouts_proof_planning",
                category="recover",
                reason="If acceptance pauses, the next dependency to reduce is the planning burden for restart/timeouts proof work.",
                supported_by=["review_status", "blockers", "safe_next_action"],
            ),
            _candidate(
                target_id="operator_dependency_next_report",
                category="notice",
                reason="Fallback report target for dependency measurement continuity.",
                supported_by=["autonomy_shift", "remaining_human_burdens", "reduced_burdens"],
            ),
        ]
        selected_target = "relay_proof_acceptance_packet"
        selected_category = "route"
        selected_reason = (
            "The relay proof review is REVIEWABLE, so the next safe reduction target is the human acceptance packet. "
            "This still requires a human decision and does not auto-accept anything."
        )
        operator_burden_addressed = ["decide", "route"]
    elif review_status == "BLOCKED":
        candidates = [
            _candidate(
                target_id="restart_timeouts_proof_planning",
                category="recover",
                reason="Relay proof review is still blocked, so the next dependency reduction is to plan the next proof gate instead of pretending acceptance is ready.",
                supported_by=["review_status", "proof_status", "blockers", "human_gates", "safe_next_action"],
            ),
            _candidate(
                target_id="operator_dependency_next_report",
                category="notice",
                reason="If planning is not yet useful, keep the dependency report current so Tony does not have to rediscover the blocker manually.",
                supported_by=["remaining_human_burdens", "reduced_burdens", "safe_next_action"],
            ),
            _candidate(
                target_id="relay_proof_acceptance_packet",
                category="route",
                reason="Rejected because the relay proof is not reviewable yet.",
                supported_by=["review_status", "missing_proofs"],
            ),
        ]
        selected_target = "restart_timeouts_proof_planning"
        selected_category = "recover"
        selected_reason = (
            "The relay proof review is BLOCKED, so the next reduction target is the restart/timeouts proof planning lane. "
            "This keeps Tony from having to remember the next blocker while leaving scheduler, SOS, and live paths out of scope."
        )
        operator_burden_addressed = ["remember", "notice", "recover"]
    elif autonomy_shift == "NONE":
        candidates = [
            _candidate(
                target_id="operator_dependency_next_report",
                category="notice",
                reason="The ledger does not show a meaningful autonomy shift yet, so keep the next step at measurement/reporting.",
                supported_by=["autonomy_shift", "remaining_human_burdens", "reduced_burdens"],
            ),
            _candidate(
                target_id="restart_timeouts_proof_planning",
                category="recover",
                reason="Planning is the next safe dependency-reduction lever if the report-only measurement layer is all that exists.",
                supported_by=["autonomy_shift", "safe_next_action"],
            ),
        ]
        selected_target = "operator_dependency_next_report"
        selected_category = "notice"
        selected_reason = (
            "The ledger shows no autonomy shift yet, so the safest next target is another dependency report. "
            "That reduces the need to remember the system state before choosing a functional lane."
        )
        operator_burden_addressed = ["remember", "notice"]
    else:
        candidates = [
            _candidate(
                target_id="restart_timeouts_proof_planning",
                category="recover",
                reason="Partial or meaningful autonomy shift still leaves downstream proof work unresolved; the next safe reduction is planning restart/timeouts proof work.",
                supported_by=["autonomy_shift", "blockers", "safe_next_action", "proof_chain"],
            ),
            _candidate(
                target_id="relay_proof_acceptance_packet" if review_status == "REVIEWABLE" else "operator_dependency_next_report",
                category="route" if review_status == "REVIEWABLE" else "notice",
                reason="Kept as a comparison target, but not the selected one unless the ledger says relay proof is reviewable.",
                supported_by=["review_status", "proof_status"],
            ),
            _candidate(
                target_id="operator_dependency_next_report",
                category="notice",
                reason="Fallback measurement target if proof planning does not yet reduce the next burden.",
                supported_by=["remaining_human_burdens", "reduced_burdens"],
            ),
        ]
        selected_target = "restart_timeouts_proof_planning"
        selected_category = "recover"
        selected_reason = (
            "The ledger shows a partial or meaningful autonomy shift, but the current proof chain still leaves manual burden in place. "
            "The next conservative reduction target is restart/timeouts proof planning."
        )
        operator_burden_addressed = ["notice", "recover"]

    if selected_target == "relay_proof_acceptance_packet" and review_status != "REVIEWABLE":
        selected_target = "restart_timeouts_proof_planning"
        selected_category = "recover"
        selected_reason = (
            "Relay proof acceptance is not selected because the relay proof is not reviewable yet; choose restart/timeouts proof planning instead."
        )
        operator_burden_addressed = ["remember", "notice", "recover"]

    for candidate in candidates:
        if candidate["target_id"] != selected_target:
            rejected_targets.append(
                {
                    "target_id": candidate["target_id"],
                    "category": candidate["category"],
                    "reason": candidate["reason"],
                }
            )

    dependency_reduction_basis = {
        "source_review_status": review_status,
        "source_proof_status": proof_status,
        "source_autonomy_shift": autonomy_shift,
        "source_next_reduction_target": _deepcopy(next_reduction_target) if isinstance(next_reduction_target, dict) else None,
        "source_blockers": blockers,
        "source_human_gates": human_gates,
        "source_safe_next_action": safe_next_action,
        "selection_rule": (
            "REVIEWABLE -> relay_proof_acceptance_packet; BLOCKED -> restart_timeouts_proof_planning; "
            "NONE -> operator_dependency_next_report; otherwise conservative proof-planning fallback."
        ),
    }

    return {
        "candidate_targets": candidates,
        "rejected_targets": rejected_targets,
        "selected_target": selected_target,
        "selected_category": selected_category,
        "selected_reason": selected_reason,
        "dependency_reduction_basis": dependency_reduction_basis,
        "operator_burden_addressed": operator_burden_addressed,
    }


def build_reduction_target_selector(
    existing_state: dict[str, Any] | None = None,
    *,
    ledger: dict[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, object]:
    source_ledger = _deepcopy(ledger) if isinstance(ledger, dict) else build_operator_dependency_ledger(existing_state, now=now)
    ledger_validation = validate_operator_dependency_ledger(source_ledger)
    selection = _selected_from_ledger(source_ledger)

    selected_target = str(selection["selected_target"])
    selected_reason = str(selection["selected_reason"])
    selected_category = str(selection["selected_category"])
    source_autonomy_shift = str((source_ledger.get("autonomy_scorecard") or {}).get("autonomy_shift") or "NONE")
    ai_os_owned_inputs_used = _ai_os_owned_inputs_used(source_ledger)
    remaining_human_burdens = _remaining_human_burdens(source_ledger)
    reduced_burdens = _reduced_burdens(source_ledger)

    readout = {
        "schema": SCHEMA,
        "generated_at_utc": _now(now or source_ledger.get("generated_at_utc")),
        "mode": REPORT_MODE,
        "source_ledger_schema": source_ledger.get("schema"),
        "source_ledger_validation": _deepcopy(ledger_validation),
        "source_autonomy_shift": source_autonomy_shift,
        "evaluated_dependency_categories": list(DEPENDENCY_CATEGORIES),
        "candidate_targets": selection["candidate_targets"],
        "selected_target": selected_target,
        "selected_category": selected_category,
        "selected_reason": selected_reason,
        "rejected_targets": selection["rejected_targets"],
        "dependency_reduction_basis": selection["dependency_reduction_basis"],
        "operator_burden_addressed": selection["operator_burden_addressed"],
        "ai_os_owned_inputs_used": ai_os_owned_inputs_used,
        "remaining_human_burdens": remaining_human_burdens,
        "reduced_burdens": reduced_burdens,
        "unsafe_autonomy_claim": False,
        "vacation_mode_complete": False,
        "dispatch_allowed": False,
        "apply_allowed": False,
        "runtime_mutation_allowed": False,
        "scheduler_creation_allowed": False,
        "sos_allowed": False,
        "live_trading_allowed": False,
        "safe_next_action": (
            f"Use {selected_target} as the next dependency-reduction target; "
            "do not execute it automatically and keep all runtime and human-gate paths blocked."
        ),
    }
    return readout


def validate_reduction_target_selector(readout: dict[str, Any]) -> dict[str, object]:
    blockers: list[str] = []
    unsafe_flags: list[str] = []
    checked_fields: list[str] = []

    if not isinstance(readout, dict):
        return {
            "status": "BLOCK",
            "blockers": ["readout must be an object"],
            "checked_fields": [],
            "unsafe_flags": ["readout_not_object"],
        }

    required_fields = [
        "schema",
        "generated_at_utc",
        "mode",
        "source_ledger_schema",
        "source_autonomy_shift",
        "evaluated_dependency_categories",
        "candidate_targets",
        "selected_target",
        "selected_category",
        "selected_reason",
        "rejected_targets",
        "dependency_reduction_basis",
        "operator_burden_addressed",
        "ai_os_owned_inputs_used",
        "remaining_human_burdens",
        "reduced_burdens",
        "unsafe_autonomy_claim",
        "vacation_mode_complete",
        "dispatch_allowed",
        "apply_allowed",
        "runtime_mutation_allowed",
        "scheduler_creation_allowed",
        "sos_allowed",
        "live_trading_allowed",
        "safe_next_action",
    ]
    checked_fields = list(required_fields)
    missing = [field for field in required_fields if field not in readout]
    if missing:
        blockers.append(f"missing fields: {', '.join(sorted(missing))}")
        unsafe_flags.append("missing_fields")

    if readout.get("mode") != REPORT_MODE:
        blockers.append("mode must be REPORT_ONLY")
        unsafe_flags.append("mode_not_report_only")
    if readout.get("unsafe_autonomy_claim") is True:
        blockers.append("unsafe_autonomy_claim must remain false")
        unsafe_flags.append("unsafe_autonomy_claim_true")
    if readout.get("vacation_mode_complete") is True:
        blockers.append("vacation_mode_complete must remain false")
        unsafe_flags.append("vacation_mode_complete_true")
    if readout.get("dispatch_allowed") is True:
        blockers.append("dispatch must remain false")
        unsafe_flags.append("dispatch_allowed_true")
    if readout.get("apply_allowed") is True:
        blockers.append("apply must remain false")
        unsafe_flags.append("apply_allowed_true")
    if readout.get("runtime_mutation_allowed") is True:
        blockers.append("runtime mutation must remain false")
        unsafe_flags.append("runtime_mutation_allowed_true")
    if readout.get("scheduler_creation_allowed") is True:
        blockers.append("scheduler creation must remain false")
        unsafe_flags.append("scheduler_creation_allowed_true")
    if readout.get("sos_allowed") is True:
        blockers.append("SOS must remain false")
        unsafe_flags.append("sos_allowed_true")
    if readout.get("live_trading_allowed") is True:
        blockers.append("live trading must remain false")
        unsafe_flags.append("live_trading_allowed_true")

    if not isinstance(readout.get("selected_target"), str) or not readout["selected_target"].strip():
        blockers.append("selected_target must be a non-empty string")
        unsafe_flags.append("selected_target_missing")
    if not isinstance(readout.get("selected_reason"), str) or not readout["selected_reason"].strip():
        blockers.append("selected_reason must be a non-empty string")
        unsafe_flags.append("selected_reason_missing")

    categories = readout.get("evaluated_dependency_categories")
    if not isinstance(categories, list) or set(categories) != set(DEPENDENCY_CATEGORIES):
        blockers.append("evaluated_dependency_categories must include all five categories")
        unsafe_flags.append("dependency_categories_missing")

    if not isinstance(readout.get("candidate_targets"), list) or not readout["candidate_targets"]:
        blockers.append("candidate_targets must be a non-empty list")
        unsafe_flags.append("candidate_targets_missing")
    if not isinstance(readout.get("rejected_targets"), list):
        blockers.append("rejected_targets must be a list")
        unsafe_flags.append("rejected_targets_not_list")
    if not isinstance(readout.get("dependency_reduction_basis"), dict):
        blockers.append("dependency_reduction_basis must be an object")
        unsafe_flags.append("dependency_reduction_basis_not_object")
    if not isinstance(readout.get("ai_os_owned_inputs_used"), list) or not readout["ai_os_owned_inputs_used"]:
        blockers.append("ai_os_owned_inputs_used must be a non-empty list")
        unsafe_flags.append("ai_os_owned_inputs_missing")

    if not isinstance(readout.get("safe_next_action"), str) or not readout["safe_next_action"].strip():
        blockers.append("safe_next_action must be a non-empty string")
        unsafe_flags.append("safe_next_action_missing")

    selected_target = str(readout.get("selected_target") or "")
    if isinstance(readout.get("candidate_targets"), list):
        candidate_ids = [
            candidate.get("target_id")
            for candidate in readout["candidate_targets"]
            if isinstance(candidate, dict)
        ]
        if selected_target and selected_target not in candidate_ids:
            blockers.append("selected_target must appear in candidate_targets")
            unsafe_flags.append("selected_target_not_candidate")

    status = "PASS" if not blockers else "BLOCK"
    return {
        "status": status,
        "blockers": blockers,
        "checked_fields": checked_fields,
        "unsafe_flags": unsafe_flags,
    }


def summarize_reduction_target_selector(readout: dict[str, Any]) -> dict[str, object]:
    remaining = readout.get("remaining_human_burdens") if isinstance(readout, dict) else []
    return {
        "status": "OK",
        "schema": readout.get("schema") if isinstance(readout, dict) else None,
        "selected_target": readout.get("selected_target") if isinstance(readout, dict) else None,
        "selected_category": readout.get("selected_category") if isinstance(readout, dict) else None,
        "selected_reason": readout.get("selected_reason") if isinstance(readout, dict) else None,
        "safe_next_action": readout.get("safe_next_action") if isinstance(readout, dict) else None,
        "source_autonomy_shift": readout.get("source_autonomy_shift") if isinstance(readout, dict) else None,
        "remaining_human_burdens_count": len(remaining) if isinstance(remaining, list) else 0,
        "unsafe_autonomy_claim": readout.get("unsafe_autonomy_claim") if isinstance(readout, dict) else None,
        "vacation_mode_complete": readout.get("vacation_mode_complete") if isinstance(readout, dict) else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the AI_OS reduction target selector (JSON only).")
    parser.add_argument("--ledger-json", default=None, help="optional JSON string containing an operator dependency ledger")
    parser.add_argument("--state-json", default=None, help="optional JSON string used to build the source ledger")
    parser.add_argument("--now", default=None, help="optional ISO-8601 timestamp for deterministic output")
    args = parser.parse_args()

    ledger = json.loads(args.ledger_json) if args.ledger_json else None
    state = json.loads(args.state_json) if args.state_json else None
    readout = build_reduction_target_selector(state, ledger=ledger, now=args.now)
    payload = {
        "selector": readout,
        "validation": validate_reduction_target_selector(readout),
        "summary": summarize_reduction_target_selector(readout),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["validation"]["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
