"""AI_OS human gate execution readiness packet (human-review only).

This module bridges the dry-run proof spine and the canonical runtime queue
spine into one conservative packet for Anthony/Tony to review manually. It does
not approve work, dispatch work, enqueue work, mutate queue sources, or launch
runtime. It only assembles evidence and a readiness verdict for human review.

Pure standard library. JSON-only CLI. No subprocess, no network, no file writes.
"""

from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from typing import Any, Iterable

from automation.orchestration.autonomy_reports.aios_operator_dependency_ledger import (
    build_operator_dependency_ledger,
    validate_operator_dependency_ledger,
)
from automation.orchestration.autonomy_reports.aios_reduction_target_selector import (
    build_reduction_target_selector,
    validate_reduction_target_selector,
)
from automation.orchestration.runtime_closure.aios_relay_dry_run_proof_review import (
    build_relay_dry_run_proof_review,
    validate_relay_dry_run_proof_review,
)
from automation.orchestration.runtime_closure.aios_relay_runtime_processor import (
    build_relay_runtime_processor,
    validate_relay_runtime_processor,
)
from automation.orchestration.runtime_closure.aios_restart_timeouts_dry_run_proof import (
    build_restart_timeouts_dry_run_proof,
    validate_restart_timeouts_dry_run_proof,
)
from automation.orchestration.runtime_closure.aios_retention_rotation_dry_run_proof import (
    build_retention_rotation_dry_run_proof,
    validate_retention_rotation_dry_run_proof,
)
from automation.orchestration.runtime_closure.aios_runtime_proof_gate import (
    build_runtime_proof_gate,
    validate_runtime_proof_gate,
)
from automation.orchestration.runtime_closure.aios_soak_dry_run_proof import (
    build_soak_dry_run_proof,
    validate_soak_dry_run_proof,
)
SCHEMA = "AIOS_HUMAN_GATE_EXECUTION_READINESS_PACKET.v1"
PACKET_TYPE = "execution_readiness"
PACKET_VERSION = "v1"
MODE = "HUMAN_GATE_PACKET"

FORBIDDEN_PACKET_STATUSES = {
    "APPROVED",
    "EXECUTE",
    "EXECUTE_NOW",
    "COMPLETE",
    "AUTONOMOUS",
    "VACATION_READY",
    "VACATION_MODE_COMPLETE",
    "SCHEDULER_READY",
    "SOS_READY",
    "LIVE_READY",
    "LIVE_TRADING_READY",
}

ALLOWED_PACKET_STATUSES = {
    "READY_FOR_HUMAN_REVIEW",
    "ATTENTION",
    "BLOCKED",
    "INVALID",
}

CANONICAL_STATES = {"QUEUED", "RUNNING", "DONE", "ERROR", "BLOCKED", "DEFERRED"}

DEFAULT_PACKET_POLICY = {
    "require_runtime_proof_gate": True,
    "require_canonical_queue_view": True,
    "require_queue_validation": True,
    "require_operator_dependency_ledger": True,
    "require_reduction_target_selector": True,
    "require_human_review": True,
    "allow_execution": False,
    "allow_dispatch": False,
    "allow_apply": False,
    "allow_runtime_launch": False,
    "allow_queue_mutation": False,
    "allow_scheduler": False,
    "allow_sos": False,
    "allow_live_trading": False,
    "allow_credentials_access": False,
    "allow_vacation_mode_complete": False,
    "allow_autonomy_claim": False,
    "block_on_protected_items": True,
    "block_on_duplicate_ids": True,
    "block_on_unknown_states": True,
    "block_on_queue_validation_block": True,
    "block_on_runtime_gate_blocked": True,
    "block_on_runtime_gate_invalid": True,
}

UNSAFE_BOOL_KEYS = {
    "execution_allowed",
    "dispatch_allowed",
    "apply_allowed",
    "runtime_launch_allowed",
    "runtime_launched",
    "runtime_mutation_allowed",
    "telemetry_mutation_allowed",
    "queue_mutation_allowed",
    "queue_mutated",
    "scheduler_creation_allowed",
    "service_creation_allowed",
    "sos_allowed",
    "live_trading_allowed",
    "credentials_accessed",
    "approval_granted",
    "vacation_mode_complete",
    "unsafe_autonomy_claim",
    "restart_executed",
    "timeout_executed",
    "rotation_executed",
    "archive_executed",
    "delete_executed",
    "truncate_executed",
    "soak_executed",
}

FORBIDDEN_STATUS_VALUES = {
    "APPROVED",
    "COMPLETE",
    "EXECUTE",
    "EXECUTE_NOW",
    "EXECUTED",
    "AUTONOMOUS",
    "VACATION_READY",
    "VACATION_MODE_COMPLETE",
    "SCHEDULER_READY",
    "SOS_READY",
    "LIVE_READY",
    "LIVE_TRADING_READY",
}

QUEUE_PLANNING_TARGETS = {
    "restart_timeouts_proof_planning",
    "retention_rotation_proof_planning",
    "soak_proof_planning",
    "stop_drill_proof_planning",
    "operator_dependency_next_report",
}


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _deepcopy(value: Any) -> Any:
    return copy.deepcopy(value)


def _normalize_token(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().upper().replace("-", "_").replace(" ", "_")


def _walk(value: Any, *, path: str = "") -> Iterable[tuple[str, Any, str]]:
    if isinstance(value, dict):
        for key, item in value.items():
            next_path = f"{path}.{key}" if path else str(key)
            yield next_path, item, str(key)
            yield from _walk(item, path=next_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            next_path = f"{path}[{index}]"
            yield next_path, item, ""
            yield from _walk(item, path=next_path)


def collect_packet_unsafe_flags(obj: Any, *, input_name: str) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    for path, value, key in _walk(obj):
        if key.lower() in UNSAFE_BOOL_KEYS and value is True:
            flags.append({"input": input_name, "path": path, "key": key, "value": value})
    return flags


def detect_packet_forbidden_claims(obj: Any, *, input_name: str) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    for path, value, key in _walk(obj):
        if not isinstance(value, str):
            continue
        token = _normalize_token(value)
        key_token = _normalize_token(key)
        path_token = _normalize_token(path)
        if token in FORBIDDEN_STATUS_VALUES and any(
            fragment in key_token or fragment in path_token
            for fragment in (
                "STATUS",
                "VERDICT",
                "CLAIM",
                "STATE",
                "MODE",
                "RESULT",
                "DECISION",
                "FINAL",
                "TARGET",
                "APPROVAL",
                "EXECUTION",
            )
        ):
            claims.append({"input": input_name, "path": path, "key": key, "value": value})
    return claims


def _resolve_bundle_value(bundle: dict[str, Any] | None, name: str) -> Any:
    if not isinstance(bundle, dict):
        return None
    if name in bundle:
        return bundle.get(name)
    nested = bundle.get("proof_bundle")
    if isinstance(nested, dict) and name in nested:
        return nested.get(name)
    return None


def _resolve_input(
    direct: Any,
    bundle: dict[str, Any] | None,
    name: str,
    *,
    required: bool,
    missing: list[str],
    invalid: list[str],
) -> Any:
    value = direct if direct is not None else _resolve_bundle_value(bundle, name)
    if value is None:
        if required:
            missing.append(name)
        return None
    if not isinstance(value, dict):
        invalid.append(f"{name} must be an object")
        return None
    return _deepcopy(value)


def _resolve_optional_list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def summarize_runtime_gate_section(runtime_proof_gate: dict[str, Any] | None) -> dict[str, Any]:
    gate = runtime_proof_gate if isinstance(runtime_proof_gate, dict) else {}
    return {
        "runtime_proof_gate_present": isinstance(runtime_proof_gate, dict),
        "runtime_proof_gate_schema": gate.get("schema"),
        "runtime_proof_gate_verdict": gate.get("final_verdict"),
        "runtime_proof_gate_human_gate_ready": gate.get("human_gate_ready"),
        "runtime_proof_gate_reason": gate.get("final_verdict_reason"),
        "runtime_proof_gate_blockers": list(gate.get("blockers") or []),
        "runtime_proof_gate_attention_reasons": list(gate.get("attention_reasons") or []),
        "runtime_proof_gate_invalid_reasons": list(gate.get("invalid_reasons") or []),
        "runtime_proof_gate_unsafe_flags": list(gate.get("unsafe_flags_detected") or []),
        "runtime_proof_gate_forbidden_claims": list(gate.get("forbidden_claims_detected") or []),
    }


def summarize_canonical_queue_section(canonical_queue_view: dict[str, Any] | None) -> dict[str, Any]:
    queue = canonical_queue_view if isinstance(canonical_queue_view, dict) else {}
    items = list(queue.get("items") or []) if isinstance(queue.get("items"), list) else []
    collisions = list(queue.get("id_collisions") or []) if isinstance(queue.get("id_collisions"), list) else []
    protected_items = [item for item in items if isinstance(item, dict) and item.get("protected_action")]
    unknown_states = [
        item
        for item in items
        if isinstance(item, dict) and item.get("state") not in CANONICAL_STATES
    ]
    fail_soft_errors = []
    for field in ("sources_missing", "sources_malformed", "sources_index_only"):
        value = queue.get(field)
        if isinstance(value, list) and value:
            fail_soft_errors.extend(value)
    report_path = None
    report_data = queue.get("_report")
    if isinstance(report_data, dict):
        report_path = report_data.get("json_path") or report_data.get("md_path")
    elif isinstance(queue.get("report_path"), str):
        report_path = queue.get("report_path")
    return {
        "canonical_queue_present": isinstance(canonical_queue_view, dict),
        "canonical_queue_schema": queue.get("schema"),
        "canonical_queue_item_count": queue.get("item_count") if isinstance(queue.get("item_count"), int) else len(items),
        "canonical_queue_state_counts": dict(queue.get("state_counts") or {}),
        "canonical_queue_source_counts": dict(queue.get("source_map") or {}),
        "canonical_queue_duplicate_ids": [item.get("id") for item in collisions if isinstance(item, dict)],
        "canonical_queue_collisions": collisions,
        "canonical_queue_protected_items": protected_items,
        "canonical_queue_unknown_states": unknown_states,
        "canonical_queue_fail_soft_errors": list(dict.fromkeys(fail_soft_errors)),
        "canonical_queue_report_path": report_path,
        "canonical_queue_mutated": False,
        "canonical_queue_protected_item_count": len(protected_items),
        "canonical_queue_duplicate_id_count": len(collisions),
        "canonical_queue_unknown_state_count": len(unknown_states),
    }


def summarize_queue_validation_section(runtime_queue_validation: dict[str, Any] | None) -> dict[str, Any]:
    validation = runtime_queue_validation if isinstance(runtime_queue_validation, dict) else {}
    findings = list(validation.get("findings") or []) if isinstance(validation.get("findings"), list) else []
    checked_fields = [finding.get("check_id") for finding in findings if isinstance(finding, dict) and finding.get("check_id")]
    protected_count = 0
    duplicate_count = 0
    unknown_state_count = 0
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        check_id = str(finding.get("check_id") or "")
        evidence = finding.get("evidence")
        if check_id == "RQV-001-NO-DUPLICATE-IDS" and isinstance(evidence, list):
            duplicate_count = len(evidence)
        if check_id == "RQV-002-CANONICAL-STATES" and isinstance(evidence, list):
            unknown_state_count = len(evidence)
        if check_id == "RQV-003-NO-PROTECTED-ITEM" and isinstance(evidence, list):
            protected_count = len(evidence)
    return {
        "queue_validation_present": isinstance(runtime_queue_validation, dict),
        "queue_validation_status": validation.get("status"),
        "queue_validation_blockers": list(validation.get("blocking_findings") or []),
        "queue_validation_checked_fields": checked_fields,
        "queue_validation_protected_item_count": protected_count,
        "queue_validation_duplicate_id_count": duplicate_count,
        "queue_validation_unknown_state_count": unknown_state_count,
        "queue_validation_safe_next_action": validation.get("safe_next_action"),
    }


def summarize_operator_dependency_section(operator_dependency_ledger: dict[str, Any] | None) -> dict[str, Any]:
    ledger = operator_dependency_ledger if isinstance(operator_dependency_ledger, dict) else {}
    scorecard = ledger.get("autonomy_scorecard") if isinstance(ledger.get("autonomy_scorecard"), dict) else {}
    dependency_categories = [
        item.get("category")
        for item in list(ledger.get("operator_dependency_items") or [])
        if isinstance(item, dict) and isinstance(item.get("category"), str)
    ]
    tony_manual_review_items: list[str] = []
    tony_manual_approval_items: list[str] = []
    tony_manual_recovery_items: list[str] = []
    for item in list(ledger.get("operator_dependency_items") or []):
        if not isinstance(item, dict):
            continue
        category = str(item.get("category") or "")
        tonys = item.get("tony") if isinstance(item.get("tony"), list) else []
        if category in {"remember", "notice"}:
            tony_manual_review_items.extend(str(value) for value in tonys)
        elif category in {"decide", "route"}:
            tony_manual_approval_items.extend(str(value) for value in tonys)
        elif category == "recover":
            tony_manual_recovery_items.extend(str(value) for value in tonys)
    return {
        "operator_dependency_present": isinstance(operator_dependency_ledger, dict),
        "autonomy_shift": scorecard.get("autonomy_shift"),
        "remaining_human_burdens": list(ledger.get("remaining_human_burdens") or []),
        "reduced_burdens": list(ledger.get("reduced_burdens") or []),
        "next_reduction_target": ledger.get("next_reduction_target"),
        "dependency_categories": list(dict.fromkeys(dependency_categories)),
        "tony_manual_approval_items": list(dict.fromkeys(tony_manual_approval_items)),
        "tony_manual_review_items": list(dict.fromkeys(tony_manual_review_items)),
        "tony_manual_recovery_items": list(dict.fromkeys(tony_manual_recovery_items)),
        "operator_dependency_unsafe_autonomy_claim": ledger.get("unsafe_autonomy_claim"),
        "operator_dependency_vacation_mode_complete": ledger.get("vacation_mode_complete"),
    }


def summarize_reduction_selector_section(reduction_target_selector: dict[str, Any] | None) -> dict[str, Any]:
    selector = reduction_target_selector if isinstance(reduction_target_selector, dict) else {}
    selected_target = selector.get("selected_target")
    return {
        "reduction_selector_present": isinstance(reduction_target_selector, dict),
        "selected_target": selected_target,
        "selected_category": selector.get("selected_category"),
        "selected_reason": selector.get("selected_reason"),
        "safe_next_action_from_selector": selector.get("safe_next_action"),
        "selector_blocks_execution": True,
        "source_autonomy_shift": selector.get("source_autonomy_shift"),
        "candidate_targets": list(selector.get("candidate_targets") or []),
        "dependency_reduction_basis": selector.get("dependency_reduction_basis"),
    }


def build_human_review_questions(packet: dict[str, Any] | None) -> list[str]:
    packet = packet if isinstance(packet, dict) else {}
    questions = [
        "Does the runtime proof gate verdict match the evidence?",
        "Are any queue items protected and requiring manual approval?",
        "Are there duplicate ids or collisions?",
        "Are there deferred items that need review before execution?",
        "Are all unsafe flags false?",
        "Are any forbidden claims present?",
        "What exactly is Anthony/Tony being asked to approve?",
        "What remains explicitly forbidden after review?",
    ]
    if packet.get("packet_status") == "ATTENTION":
        questions.insert(0, "What attention items must be resolved before human review can continue?")
    if packet.get("packet_status") == "BLOCKED":
        questions.insert(0, "Which blockers must be cleared before this packet can move to human review?")
    return questions


def build_human_stop_conditions(packet: dict[str, Any] | None) -> list[str]:
    packet = packet if isinstance(packet, dict) else {}
    stop_conditions = [
        "stop if runtime proof gate is not READY_FOR_HUMAN_GATE",
        "stop if queue validation is not PASS",
        "stop if protected queue items remain uncleared",
        "stop if unsafe flags are detected",
        "stop if forbidden claims are detected",
        "stop if approval scope is ambiguous",
        "stop if execution would require scheduler, SOS, live trading, or credentials",
    ]
    if packet.get("packet_status") == "INVALID":
        stop_conditions.insert(0, "stop immediately; packet is invalid")
    elif packet.get("packet_status") == "BLOCKED":
        stop_conditions.insert(0, "stop; packet is blocked and not ready for human review")
    return stop_conditions


def _default_ready_next_action() -> str:
    return "Anthony/Tony reviews the packet only; no approval is granted and no execution is authorized."


def _default_stop_condition(packet_status: str) -> str:
    if packet_status == "READY_FOR_HUMAN_REVIEW":
        return "Stop after human review; do not execute, approve, dispatch, or mutate."
    if packet_status == "ATTENTION":
        return "Stop until attention items are resolved; do not execute or approve."
    if packet_status == "BLOCKED":
        return "Stop until blockers are cleared; do not execute or approve."
    return "Stop until invalid inputs are repaired; do not execute or approve."


def build_human_gate_execution_readiness_packet(
    *,
    runtime_proof_gate: dict[str, Any] | None = None,
    canonical_runtime_queue_view: dict[str, Any] | None = None,
    runtime_queue_validation: dict[str, Any] | None = None,
    operator_dependency_ledger: dict[str, Any] | None = None,
    reduction_target_selector: dict[str, Any] | None = None,
    runtime_queue_readout: dict[str, Any] | None = None,
    relay_processor_readout: dict[str, Any] | None = None,
    relay_proof_review: dict[str, Any] | None = None,
    restart_timeouts_proof: dict[str, Any] | None = None,
    retention_rotation_proof: dict[str, Any] | None = None,
    soak_proof: dict[str, Any] | None = None,
    packet_policy: dict[str, Any] | None = None,
    now: str | None = None,
    source_metadata: dict[str, Any] | None = None,
    proof_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    policy = {**DEFAULT_PACKET_POLICY, **(packet_policy or {})}
    generated_at = _now(now)

    missing_inputs: list[str] = []
    invalid_inputs: list[str] = []

    bundle = proof_bundle if isinstance(proof_bundle, dict) else {}

    runtime_gate = _resolve_input(
        runtime_proof_gate,
        bundle,
        "runtime_proof_gate",
        required=bool(policy.get("require_runtime_proof_gate", True)),
        missing=missing_inputs,
        invalid=invalid_inputs,
    )
    canonical_queue = _resolve_input(
        canonical_runtime_queue_view,
        bundle,
        "canonical_runtime_queue_view",
        required=bool(policy.get("require_canonical_queue_view", True)),
        missing=missing_inputs,
        invalid=invalid_inputs,
    )
    queue_validation = _resolve_input(
        runtime_queue_validation,
        bundle,
        "runtime_queue_validation",
        required=False,
        missing=missing_inputs,
        invalid=invalid_inputs,
    )
    operator_ledger = _resolve_input(
        operator_dependency_ledger,
        bundle,
        "operator_dependency_ledger",
        required=bool(policy.get("require_operator_dependency_ledger", True)),
        missing=missing_inputs,
        invalid=invalid_inputs,
    )
    reduction_selector = _resolve_input(
        reduction_target_selector,
        bundle,
        "reduction_target_selector",
        required=bool(policy.get("require_reduction_target_selector", True)),
        missing=missing_inputs,
        invalid=invalid_inputs,
    )

    # Optional proof-spine fields. If present, they are summarized for evidence only.
    runtime_queue_readout = _resolve_input(runtime_queue_readout, bundle, "runtime_queue_readout", required=False, missing=[], invalid=[])
    relay_processor_readout = _resolve_input(relay_processor_readout, bundle, "relay_processor_readout", required=False, missing=[], invalid=[])
    relay_proof_review = _resolve_input(relay_proof_review, bundle, "relay_proof_review", required=False, missing=[], invalid=[])
    restart_timeouts_proof = _resolve_input(restart_timeouts_proof, bundle, "restart_timeouts_proof", required=False, missing=[], invalid=[])
    retention_rotation_proof = _resolve_input(retention_rotation_proof, bundle, "retention_rotation_proof", required=False, missing=[], invalid=[])
    soak_proof = _resolve_input(soak_proof, bundle, "soak_proof", required=False, missing=[], invalid=[])

    if queue_validation is None and bool(policy.get("require_queue_validation", True)):
        missing_inputs.append("runtime_queue_validation")

    runtime_gate_section = summarize_runtime_gate_section(runtime_gate)
    canonical_queue_section = summarize_canonical_queue_section(canonical_queue)
    queue_validation_section = summarize_queue_validation_section(queue_validation)
    operator_section = summarize_operator_dependency_section(operator_ledger)
    selector_section = summarize_reduction_selector_section(reduction_selector)

    runtime_gate_validation = validate_runtime_proof_gate(runtime_gate) if isinstance(runtime_gate, dict) else {"status": "BLOCK", "blockers": ["runtime proof gate missing"], "unsafe_flags": []}
    ledger_validation = validate_operator_dependency_ledger(operator_ledger) if isinstance(operator_ledger, dict) else {"status": "BLOCK", "blockers": ["operator ledger missing"], "unsafe_flags": []}
    selector_validation = validate_reduction_target_selector(reduction_selector) if isinstance(reduction_selector, dict) else {"status": "BLOCK", "blockers": ["reduction selector missing"], "unsafe_flags": []}
    relay_validation = validate_relay_runtime_processor(relay_processor_readout) if isinstance(relay_processor_readout, dict) else None
    review_validation = validate_relay_dry_run_proof_review(relay_proof_review) if isinstance(relay_proof_review, dict) else None
    restart_validation = validate_restart_timeouts_dry_run_proof(restart_timeouts_proof) if isinstance(restart_timeouts_proof, dict) else None
    retention_validation = validate_retention_rotation_dry_run_proof(retention_rotation_proof) if isinstance(retention_rotation_proof, dict) else None
    soak_validation = validate_soak_dry_run_proof(soak_proof) if isinstance(soak_proof, dict) else None

    unsafe_flags_detected: list[dict[str, Any]] = []
    forbidden_claims_detected: list[dict[str, Any]] = []
    for input_name, readout in {
        "runtime_proof_gate": runtime_gate,
        "canonical_runtime_queue_view": canonical_queue,
        "runtime_queue_validation": queue_validation,
        "operator_dependency_ledger": operator_ledger,
        "reduction_target_selector": reduction_selector,
        "runtime_queue_readout": runtime_queue_readout,
        "relay_processor_readout": relay_processor_readout,
        "relay_proof_review": relay_proof_review,
        "restart_timeouts_proof": restart_timeouts_proof,
        "retention_rotation_proof": retention_rotation_proof,
        "soak_proof": soak_proof,
    }.items():
        if isinstance(readout, dict):
            unsafe_flags_detected.extend(collect_packet_unsafe_flags(readout, input_name=input_name))
            forbidden_claims_detected.extend(detect_packet_forbidden_claims(readout, input_name=input_name))

    runtime_gate_verdict = runtime_gate_section["runtime_proof_gate_verdict"]
    queue_validation_status = queue_validation_section["queue_validation_status"]
    canonical_queue_duplicate_id_count = canonical_queue_section["canonical_queue_duplicate_id_count"]
    canonical_queue_unknown_state_count = canonical_queue_section["canonical_queue_unknown_state_count"]
    canonical_queue_protected_item_count = canonical_queue_section["canonical_queue_protected_item_count"]

    packet_blockers: list[str] = []
    packet_attention_reasons: list[str] = []
    packet_invalid_reasons: list[str] = []

    # Missing / malformed required inputs.
    if invalid_inputs:
        packet_invalid_reasons.extend(invalid_inputs)
    if missing_inputs:
        packet_blockers.extend(missing_inputs)

    # Runtime gate rules.
    if runtime_gate is not None:
        if runtime_gate_verdict in {"BLOCKED", "INVALID"}:
            if runtime_gate_verdict == "INVALID" and policy.get("block_on_runtime_gate_invalid", True):
                packet_invalid_reasons.append("runtime proof gate is INVALID")
            elif runtime_gate_verdict == "BLOCKED" and policy.get("block_on_runtime_gate_blocked", True):
                packet_blockers.append("runtime proof gate is BLOCKED")
        elif runtime_gate_verdict == "ATTENTION":
            packet_attention_reasons.append("runtime proof gate is ATTENTION")
        elif runtime_gate_verdict == "READY_FOR_HUMAN_GATE":
            if runtime_gate_section["runtime_proof_gate_human_gate_ready"] is not True:
                packet_blockers.append("runtime proof gate is not human-gate ready")
            if runtime_gate_section["runtime_proof_gate_blockers"]:
                packet_blockers.extend(list(runtime_gate_section["runtime_proof_gate_blockers"]))
            if runtime_gate_section["runtime_proof_gate_invalid_reasons"]:
                packet_invalid_reasons.extend(list(runtime_gate_section["runtime_proof_gate_invalid_reasons"]))
            if runtime_gate_section["runtime_proof_gate_unsafe_flags"]:
                packet_blockers.append("runtime proof gate contains unsafe flags")
            if runtime_gate_section["runtime_proof_gate_forbidden_claims"]:
                packet_invalid_reasons.append("runtime proof gate contains forbidden claims")
        else:
            packet_invalid_reasons.append("runtime proof gate verdict is malformed")

    # Queue validation and canonical queue rules.
    if queue_validation is not None:
        if queue_validation_status == "BLOCK" and policy.get("block_on_queue_validation_block", True):
            packet_blockers.extend(list(queue_validation_section["queue_validation_blockers"]))
        elif queue_validation_status == "PASS":
            pass
        elif queue_validation_status is None:
            packet_invalid_reasons.append("queue validation status is missing")
        else:
            packet_invalid_reasons.append("queue validation status is malformed")

    if canonical_queue_section["canonical_queue_present"] is False and policy.get("require_canonical_queue_view", True):
        packet_blockers.append("canonical runtime queue view is missing")
    if canonical_queue_duplicate_id_count and policy.get("block_on_duplicate_ids", True):
        packet_blockers.append("canonical queue has duplicate ids or collisions")
    if canonical_queue_unknown_state_count and policy.get("block_on_unknown_states", True):
        packet_blockers.append("canonical queue has unknown states")
    if canonical_queue_protected_item_count and policy.get("block_on_protected_items", True):
        packet_blockers.append("canonical queue has protected items")
    if canonical_queue_section["canonical_queue_fail_soft_errors"]:
        packet_attention_reasons.append("canonical queue has fail-soft source warnings")

    # Operator dependency and selector rules.
    if operator_section["operator_dependency_present"] is False and policy.get("require_operator_dependency_ledger", True):
        packet_blockers.append("operator dependency ledger is missing")
    if selector_section["reduction_selector_present"] is False and policy.get("require_reduction_target_selector", True):
        packet_blockers.append("reduction target selector is missing")
    if str(operator_section.get("autonomy_shift") or "") == "NONE":
        packet_attention_reasons.append("operator dependency ledger shows no autonomy shift")
    if selector_section["selected_target"] in QUEUE_PLANNING_TARGETS:
        packet_attention_reasons.append("reduction selector still points to a proof-planning target")
    if selector_section["selected_target"] and selector_section["selected_target"] != "relay_proof_acceptance_packet":
        packet_attention_reasons.append("reduction selector has not selected the relay acceptance packet")

    # Unsafe flags and forbidden claims block or invalidate.
    if unsafe_flags_detected:
        packet_blockers.append("unsafe flags detected in packet inputs")
    if forbidden_claims_detected:
        packet_invalid_reasons.append("forbidden claims detected in packet inputs")

    # Pull in the proof-spine status warnings.
    for label, validation in [
        ("relay proof review", review_validation),
        ("restart/timeouts proof", restart_validation),
        ("retention/rotation proof", retention_validation),
        ("soak proof", soak_validation),
        ("operator dependency ledger", ledger_validation),
        ("reduction selector", selector_validation),
    ]:
        if isinstance(validation, dict) and validation.get("status") == "BLOCK":
            if label == "relay proof review":
                packet_blockers.append("relay proof review validation is BLOCK")
            elif label == "restart/timeouts proof":
                packet_blockers.append("restart/timeouts proof validation is BLOCK")
            elif label == "retention/rotation proof":
                packet_blockers.append("retention/rotation proof validation is BLOCK")
            elif label == "soak proof":
                packet_blockers.append("soak proof validation is BLOCK")
            elif label == "operator dependency ledger":
                packet_blockers.append("operator dependency ledger validation is BLOCK")
            elif label == "reduction selector":
                packet_blockers.append("reduction selector validation is BLOCK")
        elif isinstance(validation, dict) and validation.get("status") == "INVALID":
            if label == "relay proof review":
                packet_invalid_reasons.append("relay proof review validation is INVALID")
            elif label == "restart/timeouts proof":
                packet_invalid_reasons.append("restart/timeouts proof validation is INVALID")
            elif label == "retention/rotation proof":
                packet_invalid_reasons.append("retention/rotation proof validation is INVALID")
            elif label == "soak proof":
                packet_invalid_reasons.append("soak proof validation is INVALID")
            elif label == "operator dependency ledger":
                packet_invalid_reasons.append("operator dependency ledger validation is INVALID")
            elif label == "reduction selector":
                packet_invalid_reasons.append("reduction selector validation is INVALID")

    packet_blockers = list(dict.fromkeys(packet_blockers))
    packet_attention_reasons = list(dict.fromkeys(packet_attention_reasons))
    packet_invalid_reasons = list(dict.fromkeys(packet_invalid_reasons))

    human_review_required = bool(policy.get("require_human_review", True))
    approval_granted = False
    execution_allowed = False
    dispatch_allowed = False
    apply_allowed = False
    runtime_launch_allowed = False
    runtime_mutation_allowed = False
    telemetry_mutation_allowed = False
    queue_mutation_allowed = False
    scheduler_creation_allowed = False
    service_creation_allowed = False
    sos_allowed = False
    live_trading_allowed = False
    credentials_accessed = False
    unsafe_autonomy_claim = False
    vacation_mode_complete = False

    if invalid_inputs or packet_invalid_reasons:
        packet_status = "INVALID"
    elif runtime_gate_verdict == "READY_FOR_HUMAN_GATE" and queue_validation_status == "PASS":
        if not packet_blockers and not unsafe_flags_detected and not forbidden_claims_detected:
            if packet_attention_reasons:
                packet_status = "ATTENTION"
            else:
                packet_status = "READY_FOR_HUMAN_REVIEW"
        else:
            packet_status = "BLOCKED"
    elif runtime_gate_verdict == "ATTENTION":
        packet_status = "ATTENTION"
    elif runtime_gate_verdict in {"BLOCKED", "INVALID"}:
        packet_status = "BLOCKED" if runtime_gate_verdict == "BLOCKED" else "INVALID"
    elif missing_inputs or packet_blockers:
        packet_status = "BLOCKED"
    else:
        packet_status = "ATTENTION"

    if packet_status == "READY_FOR_HUMAN_REVIEW":
        packet_status_reason = "The proof gate and canonical queue are coherent enough for Anthony/Tony human review only."
        safe_next_action = _default_ready_next_action()
    elif packet_status == "ATTENTION":
        packet_status_reason = "The packet is structurally safe but still needs attention before human review readiness."
        safe_next_action = "Review the attention items, then re-run the human gate packet; no execution is authorized."
    elif packet_status == "BLOCKED":
        packet_status_reason = "The packet has blockers that must be cleared before human review readiness."
        safe_next_action = "Clear blockers and regenerate the packet; do not approve or execute."
    else:
        packet_status_reason = "The packet is invalid and must be repaired before any human review."
        safe_next_action = "Repair invalid packet inputs before any review; do not approve or execute."

    human_decision_required = True
    human_decision_type = "manual_review_and_scope_confirmation"
    human_approval_scope = "Human review of the packet only; no execution authority."
    human_must_confirm = [
        "The runtime proof gate verdict matches the evidence.",
        "The canonical queue has no unreviewed protected items.",
        "No unsafe flags are true.",
        "No forbidden claims are present.",
        "The packet does not grant approval or execution authority.",
    ]
    human_must_not_approve = [
        "Do not approve execution.",
        "Do not approve scheduler or SOS activation.",
        "Do not approve live trading or credentials access.",
    ]

    packet = {
        "schema": SCHEMA,
        "generated_at_utc": generated_at,
        "mode": MODE,
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "packet_status": packet_status,
        "packet_status_reason": packet_status_reason,
        "human_review_required": human_review_required,
        "human_reviewer": "Anthony/Tony",
        "approval_granted": approval_granted,
        "execution_allowed": execution_allowed,
        "dispatch_allowed": dispatch_allowed,
        "apply_allowed": apply_allowed,
        "runtime_launch_allowed": runtime_launch_allowed,
        "runtime_mutation_allowed": runtime_mutation_allowed,
        "telemetry_mutation_allowed": telemetry_mutation_allowed,
        "queue_mutation_allowed": queue_mutation_allowed,
        "scheduler_creation_allowed": scheduler_creation_allowed,
        "service_creation_allowed": service_creation_allowed,
        "sos_allowed": sos_allowed,
        "live_trading_allowed": live_trading_allowed,
        "credentials_accessed": credentials_accessed,
        "unsafe_autonomy_claim": unsafe_autonomy_claim,
        "vacation_mode_complete": vacation_mode_complete,
        "runtime_proof_gate_present": isinstance(runtime_gate, dict),
        "runtime_proof_gate_verdict": runtime_gate_verdict,
        "runtime_proof_gate_human_gate_ready": runtime_gate_section["runtime_proof_gate_human_gate_ready"],
        "runtime_proof_gate_reason": runtime_gate_section["runtime_proof_gate_reason"],
        "runtime_proof_gate_blockers": runtime_gate_section["runtime_proof_gate_blockers"],
        "runtime_proof_gate_attention_reasons": runtime_gate_section["runtime_proof_gate_attention_reasons"],
        "runtime_proof_gate_invalid_reasons": runtime_gate_section["runtime_proof_gate_invalid_reasons"],
        "runtime_proof_gate_unsafe_flags": runtime_gate_section["runtime_proof_gate_unsafe_flags"],
        "runtime_proof_gate_forbidden_claims": runtime_gate_section["runtime_proof_gate_forbidden_claims"],
        "canonical_queue_present": canonical_queue_section["canonical_queue_present"],
        "canonical_queue_schema": canonical_queue_section["canonical_queue_schema"],
        "canonical_queue_item_count": canonical_queue_section["canonical_queue_item_count"],
        "canonical_queue_state_counts": canonical_queue_section["canonical_queue_state_counts"],
        "canonical_queue_source_counts": canonical_queue_section["canonical_queue_source_counts"],
        "canonical_queue_duplicate_ids": canonical_queue_section["canonical_queue_duplicate_ids"],
        "canonical_queue_collisions": canonical_queue_section["canonical_queue_collisions"],
        "canonical_queue_protected_items": canonical_queue_section["canonical_queue_protected_items"],
        "canonical_queue_unknown_states": canonical_queue_section["canonical_queue_unknown_states"],
        "canonical_queue_fail_soft_errors": canonical_queue_section["canonical_queue_fail_soft_errors"],
        "canonical_queue_report_path": canonical_queue_section["canonical_queue_report_path"],
        "canonical_queue_mutated": canonical_queue_section["canonical_queue_mutated"],
        "queue_validation_present": queue_validation_section["queue_validation_present"],
        "queue_validation_status": queue_validation_status,
        "queue_validation_blockers": queue_validation_section["queue_validation_blockers"],
        "queue_validation_checked_fields": queue_validation_section["queue_validation_checked_fields"],
        "queue_validation_protected_item_count": queue_validation_section["queue_validation_protected_item_count"],
        "queue_validation_duplicate_id_count": queue_validation_section["queue_validation_duplicate_id_count"],
        "queue_validation_unknown_state_count": queue_validation_section["queue_validation_unknown_state_count"],
        "operator_dependency_present": operator_section["operator_dependency_present"],
        "autonomy_shift": operator_section["autonomy_shift"],
        "remaining_human_burdens": operator_section["remaining_human_burdens"],
        "reduced_burdens": operator_section["reduced_burdens"],
        "next_reduction_target": operator_section["next_reduction_target"],
        "dependency_categories": operator_section["dependency_categories"],
        "tony_manual_approval_items": operator_section["tony_manual_approval_items"],
        "tony_manual_review_items": operator_section["tony_manual_review_items"],
        "tony_manual_recovery_items": operator_section["tony_manual_recovery_items"],
        "reduction_selector_present": selector_section["reduction_selector_present"],
        "selected_target": selector_section["selected_target"],
        "selected_category": selector_section["selected_category"],
        "selected_reason": selector_section["selected_reason"],
        "safe_next_action_from_selector": selector_section["safe_next_action_from_selector"],
        "selector_blocks_execution": selector_section["selector_blocks_execution"],
        "evidence_items": [
            {"component": "runtime_proof_gate", "status": runtime_gate_verdict},
            {"component": "canonical_runtime_queue_view", "status": queue_validation_status},
            {"component": "operator_dependency_ledger", "status": operator_section["autonomy_shift"]},
            {"component": "reduction_target_selector", "status": selector_section["selected_target"]},
        ],
        "evidence_missing": list(missing_inputs),
        "evidence_blockers": list(packet_blockers),
        "evidence_attention": list(packet_attention_reasons),
        "evidence_ready": [] if packet_status != "READY_FOR_HUMAN_REVIEW" else ["runtime proof gate", "canonical queue", "queue validation", "operator dependency ledger", "reduction selector"],
        "evidence_forbidden": list(forbidden_claims_detected),
        "human_decision_required": human_decision_required,
        "human_decision_type": human_decision_type,
        "human_approval_scope": human_approval_scope,
        "human_must_confirm": human_must_confirm,
        "human_must_not_approve": human_must_not_approve,
        "human_review_questions": build_human_review_questions({"packet_status": packet_status, "packet_attention_reasons": packet_attention_reasons, "packet_blockers": packet_blockers}),
        "human_stop_conditions": build_human_stop_conditions({"packet_status": packet_status}),
        "readiness_summary": {
            "ready_items": [
                "runtime proof gate is READY_FOR_HUMAN_GATE",
                "canonical queue validation is PASS",
                "human review remains required",
            ] if packet_status == "READY_FOR_HUMAN_REVIEW" else [],
            "blocked_items": list(packet_blockers),
            "attention_items": list(packet_attention_reasons),
            "forbidden_items": [item["value"] for item in forbidden_claims_detected],
        },
        "ready_items": [
            "Human review only; no execution authority.",
        ] if packet_status == "READY_FOR_HUMAN_REVIEW" else [],
        "blocked_items": list(packet_blockers),
        "attention_items": list(packet_attention_reasons),
        "forbidden_items": [item["value"] for item in forbidden_claims_detected],
        "unsafe_flags_detected": list(unsafe_flags_detected),
        "forbidden_claims_detected": list(forbidden_claims_detected),
        "packet_blockers": list(packet_blockers),
        "packet_attention_reasons": list(packet_attention_reasons),
        "packet_invalid_reasons": list(packet_invalid_reasons),
        "safe_next_action": safe_next_action,
        "stop_condition": _default_stop_condition(packet_status),
        "source_metadata": _deepcopy(source_metadata) if source_metadata is not None else {},
        "packet_policy": _deepcopy(policy),
        "proof_spine_summary": {
            "relay_processor_present": isinstance(relay_processor_readout, dict),
            "relay_review_present": isinstance(relay_proof_review, dict),
            "restart_timeouts_present": isinstance(restart_timeouts_proof, dict),
            "retention_rotation_present": isinstance(retention_rotation_proof, dict),
            "soak_present": isinstance(soak_proof, dict),
            "runtime_queue_readout_present": isinstance(runtime_queue_readout, dict),
        },
    }
    return packet


def validate_human_gate_execution_readiness_packet(packet: dict[str, Any]) -> dict[str, object]:
    blockers: list[str] = []
    unsafe_flags: list[str] = []
    forbidden_claims: list[dict[str, Any]] = []
    checked_fields: list[str] = []

    if not isinstance(packet, dict):
        return {
            "status": "BLOCK",
            "blockers": ["packet must be an object"],
            "checked_fields": [],
            "unsafe_flags": ["packet_not_object"],
            "forbidden_claims": [],
            "packet_status": None,
        }

    required_fields = [
        "schema",
        "generated_at_utc",
        "mode",
        "packet_type",
        "packet_version",
        "packet_status",
        "packet_status_reason",
        "human_review_required",
        "human_reviewer",
        "approval_granted",
        "execution_allowed",
        "dispatch_allowed",
        "apply_allowed",
        "runtime_launch_allowed",
        "runtime_mutation_allowed",
        "telemetry_mutation_allowed",
        "queue_mutation_allowed",
        "scheduler_creation_allowed",
        "service_creation_allowed",
        "sos_allowed",
        "live_trading_allowed",
        "credentials_accessed",
        "unsafe_autonomy_claim",
        "vacation_mode_complete",
        "runtime_proof_gate_present",
        "runtime_proof_gate_verdict",
        "runtime_proof_gate_human_gate_ready",
        "runtime_proof_gate_reason",
        "runtime_proof_gate_blockers",
        "runtime_proof_gate_attention_reasons",
        "runtime_proof_gate_invalid_reasons",
        "runtime_proof_gate_unsafe_flags",
        "runtime_proof_gate_forbidden_claims",
        "canonical_queue_present",
        "canonical_queue_schema",
        "canonical_queue_item_count",
        "canonical_queue_state_counts",
        "canonical_queue_source_counts",
        "canonical_queue_duplicate_ids",
        "canonical_queue_collisions",
        "canonical_queue_protected_items",
        "canonical_queue_unknown_states",
        "canonical_queue_fail_soft_errors",
        "canonical_queue_mutated",
        "queue_validation_present",
        "queue_validation_status",
        "queue_validation_blockers",
        "queue_validation_checked_fields",
        "queue_validation_protected_item_count",
        "queue_validation_duplicate_id_count",
        "queue_validation_unknown_state_count",
        "operator_dependency_present",
        "autonomy_shift",
        "remaining_human_burdens",
        "reduced_burdens",
        "next_reduction_target",
        "dependency_categories",
        "tony_manual_approval_items",
        "tony_manual_review_items",
        "tony_manual_recovery_items",
        "reduction_selector_present",
        "selected_target",
        "selected_category",
        "selected_reason",
        "safe_next_action_from_selector",
        "selector_blocks_execution",
        "evidence_items",
        "evidence_missing",
        "evidence_blockers",
        "evidence_attention",
        "evidence_ready",
        "evidence_forbidden",
        "human_decision_required",
        "human_decision_type",
        "human_approval_scope",
        "human_must_confirm",
        "human_must_not_approve",
        "human_review_questions",
        "human_stop_conditions",
        "readiness_summary",
        "ready_items",
        "blocked_items",
        "attention_items",
        "forbidden_items",
        "unsafe_flags_detected",
        "forbidden_claims_detected",
        "packet_blockers",
        "packet_attention_reasons",
        "packet_invalid_reasons",
        "safe_next_action",
        "stop_condition",
        "packet_policy",
    ]
    checked_fields = list(required_fields)
    missing = [field for field in required_fields if field not in packet]
    if missing:
        blockers.append(f"missing fields: {', '.join(sorted(missing))}")
        unsafe_flags.append("missing_fields")

    if packet.get("mode") != MODE:
        blockers.append("mode must be HUMAN_GATE_PACKET")
        unsafe_flags.append("mode_invalid")

    packet_status = str(packet.get("packet_status") or "")
    if packet_status not in ALLOWED_PACKET_STATUSES:
        if packet_status in FORBIDDEN_PACKET_STATUSES:
            blockers.append(f"packet_status must never be {packet_status}")
            unsafe_flags.append("packet_status_forbidden")
        else:
            blockers.append("packet_status must be READY_FOR_HUMAN_REVIEW, ATTENTION, BLOCKED, or INVALID")
            unsafe_flags.append("packet_status_invalid")

    recursive_unsafe = collect_packet_unsafe_flags(packet, input_name="human_gate_packet")
    recursive_forbidden = detect_packet_forbidden_claims(packet, input_name="human_gate_packet")
    if recursive_unsafe:
        blockers.append("unsafe flags detected in packet output")
        unsafe_flags.extend([f"{item['input']}:{item['path']}:{item['key']}" for item in recursive_unsafe])
    if recursive_forbidden:
        blockers.append("forbidden claims detected in packet output")
        forbidden_claims.extend(recursive_forbidden)

    if packet.get("human_review_required") is not True:
        blockers.append("human_review_required must be true")
        unsafe_flags.append("human_review_required_false")
    if packet.get("approval_granted") is True:
        blockers.append("approval_granted must be false")
        unsafe_flags.append("approval_granted_true")
    if packet.get("execution_allowed") is True:
        blockers.append("execution_allowed must be false")
        unsafe_flags.append("execution_allowed_true")
    if packet.get("dispatch_allowed") is True:
        blockers.append("dispatch_allowed must be false")
        unsafe_flags.append("dispatch_allowed_true")
    if packet.get("apply_allowed") is True:
        blockers.append("apply_allowed must be false")
        unsafe_flags.append("apply_allowed_true")
    if packet.get("runtime_launch_allowed") is True:
        blockers.append("runtime_launch_allowed must be false")
        unsafe_flags.append("runtime_launch_allowed_true")
    if packet.get("runtime_mutation_allowed") is True:
        blockers.append("runtime_mutation_allowed must be false")
        unsafe_flags.append("runtime_mutation_allowed_true")
    if packet.get("telemetry_mutation_allowed") is True:
        blockers.append("telemetry_mutation_allowed must be false")
        unsafe_flags.append("telemetry_mutation_allowed_true")
    if packet.get("queue_mutation_allowed") is True:
        blockers.append("queue_mutation_allowed must be false")
        unsafe_flags.append("queue_mutation_allowed_true")
    if packet.get("scheduler_creation_allowed") is True:
        blockers.append("scheduler_creation_allowed must be false")
        unsafe_flags.append("scheduler_creation_allowed_true")
    if packet.get("service_creation_allowed") is True:
        blockers.append("service_creation_allowed must be false")
        unsafe_flags.append("service_creation_allowed_true")
    if packet.get("sos_allowed") is True:
        blockers.append("sos_allowed must be false")
        unsafe_flags.append("sos_allowed_true")
    if packet.get("live_trading_allowed") is True:
        blockers.append("live_trading_allowed must be false")
        unsafe_flags.append("live_trading_allowed_true")
    if packet.get("credentials_accessed") is True:
        blockers.append("credentials_accessed must be false")
        unsafe_flags.append("credentials_accessed_true")
    if packet.get("unsafe_autonomy_claim") is True:
        blockers.append("unsafe_autonomy_claim must be false")
        unsafe_flags.append("unsafe_autonomy_claim_true")
    if packet.get("vacation_mode_complete") is True:
        blockers.append("vacation_mode_complete must be false")
        unsafe_flags.append("vacation_mode_complete_true")

    if not isinstance(packet.get("safe_next_action"), str) or not packet["safe_next_action"].strip():
        blockers.append("safe_next_action must be a non-empty string")
        unsafe_flags.append("safe_next_action_missing")
    if not isinstance(packet.get("stop_condition"), str) or not packet["stop_condition"].strip():
        blockers.append("stop_condition must be a non-empty string")
        unsafe_flags.append("stop_condition_missing")

    runtime_gate_verdict = str(packet.get("runtime_proof_gate_verdict") or "")
    queue_validation_status = str(packet.get("queue_validation_status") or "")

    if packet_status == "READY_FOR_HUMAN_REVIEW":
        if packet.get("runtime_proof_gate_present") is not True:
            blockers.append("READY_FOR_HUMAN_REVIEW requires a runtime proof gate")
            unsafe_flags.append("runtime_proof_gate_missing")
        if runtime_gate_verdict != "READY_FOR_HUMAN_GATE":
            blockers.append("READY_FOR_HUMAN_REVIEW requires runtime proof gate verdict READY_FOR_HUMAN_GATE")
            unsafe_flags.append("runtime_gate_not_ready")
        if packet.get("runtime_proof_gate_human_gate_ready") is not True:
            blockers.append("READY_FOR_HUMAN_REVIEW requires runtime proof gate human_gate_ready true")
            unsafe_flags.append("runtime_gate_human_gate_not_ready")
        if packet.get("canonical_queue_present") is not True:
            blockers.append("READY_FOR_HUMAN_REVIEW requires canonical queue view")
            unsafe_flags.append("canonical_queue_missing")
        if packet.get("queue_validation_present") is not True:
            blockers.append("READY_FOR_HUMAN_REVIEW requires queue validation")
            unsafe_flags.append("queue_validation_missing")
        if queue_validation_status != "PASS":
            blockers.append("READY_FOR_HUMAN_REVIEW requires queue validation PASS")
            unsafe_flags.append("queue_validation_not_pass")
        if packet.get("packet_blockers"):
            blockers.append("READY_FOR_HUMAN_REVIEW cannot have packet blockers")
            unsafe_flags.append("packet_has_blockers")
        if packet.get("packet_invalid_reasons"):
            blockers.append("READY_FOR_HUMAN_REVIEW cannot have invalid reasons")
            unsafe_flags.append("packet_has_invalid_reasons")
        if packet.get("unsafe_flags_detected"):
            blockers.append("READY_FOR_HUMAN_REVIEW cannot have unsafe flags")
            unsafe_flags.append("packet_has_unsafe_flags")
        if packet.get("forbidden_claims_detected"):
            blockers.append("READY_FOR_HUMAN_REVIEW cannot have forbidden claims")
            unsafe_flags.append("packet_has_forbidden_claims")
        if packet.get("approval_granted") is True:
            blockers.append("READY_FOR_HUMAN_REVIEW cannot have approval granted")
            unsafe_flags.append("approval_granted_true")
        if any(
            packet.get(field) is True
            for field in [
                "execution_allowed",
                "dispatch_allowed",
                "apply_allowed",
                "runtime_launch_allowed",
                "queue_mutation_allowed",
                "scheduler_creation_allowed",
                "service_creation_allowed",
                "sos_allowed",
                "live_trading_allowed",
            ]
        ):
            blockers.append("READY_FOR_HUMAN_REVIEW cannot have execution or live-operation flags true")
            unsafe_flags.append("execution_flag_true")

    safe_next_action = packet.get("safe_next_action")
    stop_condition = packet.get("stop_condition")
    if isinstance(safe_next_action, str) and isinstance(stop_condition, str):
        serialized = json.dumps(packet, sort_keys=True).lower()
        command_fragments = [
            "".join(["git", " ", "push"]),
            "".join(["git", " ", "commit"]),
            "".join(["git", " ", "merge"]),
            "".join(["gh", " ", "pr", " ", "merge"]),
            "".join(["gh", " ", "pr", " ", "create"]),
            "".join(["register", "-", "scheduledtask"]),
            "".join(["new", "-", "service"]),
            "".join(["start", "-", "job"]),
            "".join(["start", "-", "process"]),
            "".join(["start", "-", "service"]),
            "".join(["sub", "process"]),
            "".join(["shell", "=", "true"]),
        ]
        for pattern in command_fragments:
            if pattern in serialized:
                blockers.append("command string detected in packet output")
                unsafe_flags.append(f"command_string:{pattern}")
                break
        secret_fragments = [
            "".join(["secret", "="]),
            "".join(["token", "="]),
            "".join(["pass", "word", "="]),
            "".join(["api", "_key", "="]),
            "".join(["api", "key", "="]),
            "".join(["bear", "er "]),
            "".join(["sk", "-"]),
        ]
        for pattern in secret_fragments:
            if pattern in serialized:
                blockers.append("obvious secret assignment string detected in packet output")
                unsafe_flags.append(f"secret_pattern:{pattern}")
                break

    status = "PASS" if not blockers else "BLOCK"
    return {
        "status": status,
        "blockers": list(dict.fromkeys(blockers)),
        "checked_fields": checked_fields,
        "unsafe_flags": list(dict.fromkeys(unsafe_flags)),
        "forbidden_claims": forbidden_claims,
        "packet_status": packet.get("packet_status"),
    }


def summarize_human_gate_execution_readiness_packet(packet: dict[str, Any]) -> dict[str, object]:
    if not isinstance(packet, dict):
        return {
            "packet_status": None,
            "human_review_required": None,
            "approval_granted": None,
            "execution_allowed": None,
            "dispatch_allowed": None,
            "apply_allowed": None,
            "runtime_launch_allowed": None,
            "queue_mutation_allowed": None,
            "scheduler_creation_allowed": None,
            "sos_allowed": None,
            "live_trading_allowed": None,
            "vacation_mode_complete": None,
            "runtime_proof_gate_verdict": None,
            "queue_validation_status": None,
            "canonical_queue_item_count": 0,
            "protected_item_count": 0,
            "duplicate_id_count": 0,
            "collision_count": 0,
            "unknown_state_count": 0,
            "blocker_count": 0,
            "attention_count": 0,
            "invalid_reason_count": 0,
            "unsafe_flag_count": 0,
            "forbidden_claim_count": 0,
            "human_review_question_count": 0,
            "human_stop_condition_count": 0,
            "safe_next_action": None,
            "stop_condition": None,
        }

    return {
        "packet_status": packet.get("packet_status"),
        "human_review_required": packet.get("human_review_required"),
        "approval_granted": packet.get("approval_granted"),
        "execution_allowed": packet.get("execution_allowed"),
        "dispatch_allowed": packet.get("dispatch_allowed"),
        "apply_allowed": packet.get("apply_allowed"),
        "runtime_launch_allowed": packet.get("runtime_launch_allowed"),
        "queue_mutation_allowed": packet.get("queue_mutation_allowed"),
        "scheduler_creation_allowed": packet.get("scheduler_creation_allowed"),
        "sos_allowed": packet.get("sos_allowed"),
        "live_trading_allowed": packet.get("live_trading_allowed"),
        "vacation_mode_complete": packet.get("vacation_mode_complete"),
        "runtime_proof_gate_verdict": packet.get("runtime_proof_gate_verdict"),
        "queue_validation_status": packet.get("queue_validation_status"),
        "canonical_queue_item_count": packet.get("canonical_queue_item_count") if isinstance(packet.get("canonical_queue_item_count"), int) else 0,
        "protected_item_count": packet.get("queue_validation_protected_item_count") if isinstance(packet.get("queue_validation_protected_item_count"), int) else 0,
        "duplicate_id_count": packet.get("queue_validation_duplicate_id_count") if isinstance(packet.get("queue_validation_duplicate_id_count"), int) else 0,
        "collision_count": len(list(packet.get("canonical_queue_collisions") or [])),
        "unknown_state_count": packet.get("queue_validation_unknown_state_count") if isinstance(packet.get("queue_validation_unknown_state_count"), int) else 0,
        "blocker_count": len(list(packet.get("packet_blockers") or [])),
        "attention_count": len(list(packet.get("packet_attention_reasons") or [])),
        "invalid_reason_count": len(list(packet.get("packet_invalid_reasons") or [])),
        "unsafe_flag_count": len(list(packet.get("unsafe_flags_detected") or [])),
        "forbidden_claim_count": len(list(packet.get("forbidden_claims_detected") or [])),
        "human_review_question_count": len(list(packet.get("human_review_questions") or [])),
        "human_stop_condition_count": len(list(packet.get("human_stop_conditions") or [])),
        "safe_next_action": packet.get("safe_next_action"),
        "stop_condition": packet.get("stop_condition"),
    }


def _cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the AI_OS human gate execution readiness packet.")
    parser.add_argument("--runtime-proof-gate-json")
    parser.add_argument("--canonical-runtime-queue-view-json")
    parser.add_argument("--runtime-queue-validation-json")
    parser.add_argument("--operator-dependency-ledger-json")
    parser.add_argument("--reduction-target-selector-json")
    parser.add_argument("--runtime-queue-readout-json")
    parser.add_argument("--relay-processor-readout-json")
    parser.add_argument("--relay-proof-review-json")
    parser.add_argument("--restart-timeouts-proof-json")
    parser.add_argument("--retention-rotation-proof-json")
    parser.add_argument("--soak-proof-json")
    parser.add_argument("--packet-policy-json")
    parser.add_argument("--proof-bundle-json")
    parser.add_argument("--now")
    return parser.parse_args()


def _load_json_arg(raw: str | None) -> dict[str, Any] | None:
    if raw is None:
        return None
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("JSON input must decode to an object")
    return value


def main() -> int:
    args = _cli_args()
    packet = build_human_gate_execution_readiness_packet(
        runtime_proof_gate=_load_json_arg(args.runtime_proof_gate_json),
        canonical_runtime_queue_view=_load_json_arg(args.canonical_runtime_queue_view_json),
        runtime_queue_validation=_load_json_arg(args.runtime_queue_validation_json),
        operator_dependency_ledger=_load_json_arg(args.operator_dependency_ledger_json),
        reduction_target_selector=_load_json_arg(args.reduction_target_selector_json),
        runtime_queue_readout=_load_json_arg(args.runtime_queue_readout_json),
        relay_processor_readout=_load_json_arg(args.relay_processor_readout_json),
        relay_proof_review=_load_json_arg(args.relay_proof_review_json),
        restart_timeouts_proof=_load_json_arg(args.restart_timeouts_proof_json),
        retention_rotation_proof=_load_json_arg(args.retention_rotation_proof_json),
        soak_proof=_load_json_arg(args.soak_proof_json),
        packet_policy=_load_json_arg(args.packet_policy_json),
        proof_bundle=_load_json_arg(args.proof_bundle_json),
        now=args.now,
    )
    validation = validate_human_gate_execution_readiness_packet(packet)
    output = {
        "packet": packet,
        "validation": validation,
        "summary": summarize_human_gate_execution_readiness_packet(packet),
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
