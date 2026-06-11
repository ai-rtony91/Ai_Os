"""AI_OS runtime proof gate (observe-only).

This module consumes the connected dry-run proof spine and decides whether the
current proof chain is conservative enough to move to human execution gate
review. It does not execute runtime behavior, does not dispatch workers, does
not create scheduler or service actions, does not arm SOS, and does not claim
vacation mode completion.

Pure standard library. JSON CLI that can persist preview evidence. No
subprocess, no network, no runtime execution.
"""

from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
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
from automation.orchestration.runtime_closure.aios_runtime_execution_queue import (
    build_runtime_execution_queue,
    validate_runtime_execution_queue,
)
from automation.orchestration.runtime_closure.aios_soak_dry_run_proof import (
    build_soak_dry_run_proof,
    validate_soak_dry_run_proof,
)


SCHEMA = "AIOS_RUNTIME_PROOF_GATE.v1"
GATE_TYPE = "runtime_proof_gate"
GATE_VERSION = "v1"
MODE = "DRY_RUN_GATE"

FINAL_VERDICTS = {
    "READY_FOR_HUMAN_GATE",
    "ATTENTION",
    "BLOCKED",
    "INVALID",
}
FORBIDDEN_FINAL_VERDICTS = {
    "COMPLETE",
    "EXECUTE",
    "EXECUTE_NOW",
    "AUTONOMOUS",
    "VACATION_READY",
    "VACATION_MODE_COMPLETE",
    "SCHEDULER_READY",
    "SOS_READY",
    "LIVE_READY",
    "LIVE_TRADING_READY",
}

FORBIDDEN_STATUS_VALUES = FORBIDDEN_FINAL_VERDICTS | {
    "EXECUTED",
    "READY_FOR_EXECUTION",
}

STATUS_KEYS = {
    "status",
    "proof_status",
    "review_status",
    "final_verdict",
    "lane_status",
    "validation_status",
    "source_status",
    "gate_status",
}

STATUS_ACCEPTABLE_VALUES = {
    "PASS",
    "ATTENTION",
    "BLOCKED",
    "INVALID",
    "REVIEWABLE",
    "SELECTED",
    "PARTIAL",
    "READY_FOR_DRY_RUN",
    "DRY_RUN_PROVEN",
    "READY_FOR_STAGE_1",
    "SOAK_PROVEN",
    "RECOVERY_PROVEN",
    "HUMAN_CHECKLIST_READY",
    "READY_FOR_HUMAN_GATE",
    "BLOCKED_WAITING_FOR_APPROVAL_CHAIN",
    "BLOCKED_WAITING_FOR_RELAY_PROOF",
    "BLOCKED_WAITING_FOR_RESTART_PROOF",
    "BLOCKED_WAITING_FOR_RETENTION_PROOF",
    "BLOCKED_WAITING_FOR_SOAK_PROOF",
    "BLOCKED_WAITING_FOR_STOP_DRILL",
    "BLOCKED_WAITING_FOR_SOS",
    "BLOCKED_WAITING_FOR_RELAY",
    "BLOCKED_WAITING_FOR_HUMAN_REVIEW",
    "BLOCKED_WAITING_FOR_QUEUE",
    "BLOCKED_WAITING_FOR_APPROVAL",
    "BLOCKED_WAITING_FOR_PARENTS",
    "BLOCKED_WAITING_FOR_INPUTS",
    "READY_FOR_REVIEW",
    "READY_FOR_RECOVERY_PROOF",
    "BLOCKED_WAITING_FOR_NEXT_TARGET",
    "BLOCKED_WAITING_FOR_ACCEPTANCE",
}

HUMAN_GATE_NAME = "human_execution_gate_review"
RELAY_ACCEPTANCE_TARGET = "relay_proof_acceptance_packet"
PROOF_PLANNING_TARGETS = {
    "restart_timeouts_proof_planning",
    "retention_rotation_proof_planning",
    "soak_proof_planning",
    "stop_drill_proof_planning",
    "operator_dependency_next_report",
}

DEFAULT_GATE_POLICY = {
    "require_runtime_queue": True,
    "require_relay_processor": True,
    "require_relay_proof_review": True,
    "require_restart_timeouts_proof": True,
    "require_retention_rotation_proof": True,
    "require_soak_proof": True,
    "require_operator_dependency_ledger": True,
    "require_reduction_target_selector": True,
    "require_soak_pass": True,
    "allow_restart_attention": False,
    "allow_retention_attention": False,
    "allow_soak_attention": False,
    "require_all_execution_flags_false": True,
    "require_human_gate": True,
    "allow_scheduler": False,
    "allow_sos": False,
    "allow_live_trading": False,
    "allow_credentials_access": False,
    "allow_vacation_mode_complete": False,
    "allow_autonomy_claim": False,
}

UNSAFE_BOOL_KEYS = {
    "execution_allowed",
    "dispatch_allowed",
    "apply_allowed",
    "runtime_launch_allowed",
    "runtime_launched",
    "runtime_mutation_allowed",
    "telemetry_mutation_allowed",
    "file_mutation_allowed",
    "scheduler_creation_allowed",
    "service_creation_allowed",
    "scheduler_execution_allowed",
    "service_execution_allowed",
    "sos_allowed",
    "sos_execution_allowed",
    "live_trading_allowed",
    "live_broker_trading_enabled",
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
    "auto_apply",
    "auto_merge",
    "auto_scheduler",
    "active_packet_mutation_allowed",
}

DEFAULT_RESTART_INPUT = {
    "runtime_label": "aios-runtime",
    "runtime_expected": True,
    "checkpoint_expected": True,
    "last_heartbeat_utc": "2026-01-01T00:04:30Z",
    "last_checkpoint_utc": "2026-01-01T00:01:00Z",
}

DEFAULT_RETENTION_INPUT = [
    {
        "path": "reports/runtime/a.jsonl",
        "kind": "jsonl",
        "created_at_utc": "2026-01-29T00:00:00Z",
        "updated_at_utc": "2026-01-30T00:00:00Z",
        "size_bytes": 2048,
        "line_count": 25,
        "contains_jsonl": True,
        "required": True,
    }
]

DEFAULT_SOAK_INPUT = {
    "runtime_label": "aios-runtime",
    "window_start_utc": "2026-01-01T00:00:00Z",
    "window_end_utc": "2026-01-01T01:00:00Z",
    "heartbeat_samples_utc": [
        "2026-01-01T00:00:00Z",
        "2026-01-01T00:05:00Z",
        "2026-01-01T00:10:00Z",
        "2026-01-01T00:15:00Z",
        "2026-01-01T00:20:00Z",
        "2026-01-01T00:25:00Z",
        "2026-01-01T00:30:00Z",
        "2026-01-01T00:35:00Z",
        "2026-01-01T00:40:00Z",
        "2026-01-01T00:45:00Z",
        "2026-01-01T00:50:00Z",
        "2026-01-01T00:55:00Z",
        "2026-01-01T01:00:00Z",
    ],
    "checkpoint_samples_utc": [
        "2026-01-01T00:00:00Z",
        "2026-01-01T00:15:00Z",
        "2026-01-01T00:30:00Z",
        "2026-01-01T00:45:00Z",
        "2026-01-01T01:00:00Z",
    ],
}

REPORT_DIR = Path("Reports") / "runtime_proof_gate"
REPORT_JSON_NAME = "runtime_proof_gate_preview.json"
REPORT_MD_NAME = "runtime_proof_gate_summary.md"


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _deepcopy(value: Any) -> Any:
    return copy.deepcopy(value)


def _normalize_status(value: Any) -> str:
    if not isinstance(value, str):
        return "UNKNOWN"
    normalized = value.strip().upper().replace("-", "_").replace(" ", "_")
    return normalized or "UNKNOWN"


def classify_proof_status(value: Any) -> str:
    """Return a normalized status token for proof/readout comparison."""
    return _normalize_status(value)


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


def _find_forbidden_claims(obj: Any, *, input_name: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for path, value, key in _walk(obj):
        if key not in STATUS_KEYS:
            continue
        if not isinstance(value, str):
            continue
        token = _normalize_status(value)
        if token in FORBIDDEN_STATUS_VALUES:
            matches.append({"input": input_name, "path": path, "key": key, "value": value})
    return matches


def detect_forbidden_claims(obj: Any, *, input_name: str = "input") -> list[dict[str, Any]]:
    return _find_forbidden_claims(obj, input_name=input_name)


def collect_unsafe_flags(obj: Any, *, input_name: str) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    for path, value, key in _walk(obj):
        if key.lower() in UNSAFE_BOOL_KEYS and value is True:
            flags.append({"input": input_name, "path": path, "key": key, "value": value})
    return flags


def _is_dict(value: Any) -> bool:
    return isinstance(value, dict)


def _missing_required(obj: dict[str, Any] | None, required_fields: list[str]) -> list[str]:
    if not isinstance(obj, dict):
        return list(required_fields)
    return [field for field in required_fields if field not in obj]


def summarize_prerequisite(name: str, readout: dict[str, Any] | None) -> dict[str, Any]:
    readout = readout if isinstance(readout, dict) else {}
    summary: dict[str, Any] = {
        "component": name,
        "source_schema": readout.get("schema") or readout.get("schema_version"),
        "proof_status": readout.get("proof_status"),
        "validation_status": readout.get("validation_status"),
        "review_status": readout.get("review_status"),
        "safe_next_action": readout.get("safe_next_action"),
        "unsafe_autonomy_claim": readout.get("unsafe_autonomy_claim"),
        "vacation_mode_complete": readout.get("vacation_mode_complete"),
    }
    if name == "runtime_queue":
        next_lane = None
        lanes = readout.get("lanes")
        if isinstance(lanes, list) and lanes:
            first = lanes[0]
            if isinstance(first, dict):
                next_lane = {
                    "lane_id": first.get("lane_id"),
                    "title": first.get("title"),
                    "owner_type": first.get("owner_type"),
                    "human_required": first.get("human_required"),
                    "automation_allowed": first.get("automation_allowed"),
                    "vacation_mode_blocker": first.get("vacation_mode_blocker"),
                }
        summary.update(
            {
                "blockers": list(readout.get("remaining_blockers") or []),
                "human_gate_required": True,
                "human_gate_ready": not bool(readout.get("remaining_blockers")),
                "next_lane": next_lane,
                "remaining_blockers": list(readout.get("remaining_blockers") or []),
                "vacation_mode_complete": readout.get("vacation_mode_complete"),
            }
        )
    elif name == "relay_processor":
        summary.update(
            {
                "lane_status": readout.get("lane_status"),
                "blocked_human_gates": list(readout.get("blocked_human_gates") or []),
                "missing_proofs": list(readout.get("missing_proofs") or []),
                "observe_only": readout.get("observe_only"),
            }
        )
    elif name == "relay_review":
        summary.update(
            {
                "review_status": readout.get("review_status"),
                "proof_reviewable": readout.get("proof_reviewable"),
                "blocked_human_gates": list(readout.get("blocked_human_gates") or []),
                "missing_proofs": list(readout.get("missing_proofs") or []),
            }
        )
    elif name == "restart_timeouts":
        summary.update(
            {
                "restart_required": readout.get("restart_required"),
                "restart_executed": readout.get("restart_executed"),
                "timeout_triggered": readout.get("timeout_triggered"),
                "timeout_executed": readout.get("timeout_executed"),
            }
        )
    elif name == "retention_rotation":
        summary.update(
            {
                "rotation_required": readout.get("rotation_required"),
                "rotation_executed": readout.get("rotation_executed"),
                "archive_required": readout.get("archive_required"),
                "archive_executed": readout.get("archive_executed"),
                "delete_required": readout.get("delete_required"),
                "delete_executed": readout.get("delete_executed"),
                "truncate_required": readout.get("truncate_required"),
                "truncate_executed": readout.get("truncate_executed"),
            }
        )
    elif name == "soak":
        summary.update(
            {
                "soak_pass": readout.get("soak_pass"),
                "soak_executed": readout.get("soak_executed"),
                "runtime_launched": readout.get("runtime_launched"),
                "duration_sufficient": readout.get("duration_sufficient"),
                "heartbeat_continuity_ok": readout.get("heartbeat_continuity_ok"),
                "checkpoint_continuity_ok": readout.get("checkpoint_continuity_ok"),
                "restart_timeouts_proof_status": readout.get("restart_timeouts_proof_status"),
                "retention_rotation_proof_status": readout.get("retention_rotation_proof_status"),
            }
        )
    elif name == "operator_dependency_ledger":
        scorecard = readout.get("autonomy_scorecard") if isinstance(readout.get("autonomy_scorecard"), dict) else {}
        summary.update(
            {
                "autonomy_shift": scorecard.get("autonomy_shift"),
                "remaining_human_burdens_count": len(list(readout.get("remaining_human_burdens") or [])),
                "reduced_burdens_count": len(list(readout.get("reduced_burdens") or [])),
                "next_reduction_target": readout.get("next_reduction_target"),
                "operator_dependency_categories": [
                    item.get("category")
                    for item in list(readout.get("operator_dependency_items") or [])
                    if isinstance(item, dict)
                ],
            }
        )
    elif name == "reduction_target_selector":
        summary.update(
            {
                "selected_target": readout.get("selected_target"),
                "selected_category": readout.get("selected_category"),
                "selected_reason": readout.get("selected_reason"),
                "source_autonomy_shift": readout.get("source_autonomy_shift"),
                "remaining_human_burdens_count": len(list(readout.get("remaining_human_burdens") or [])),
            }
        )
    return summary


def _default_restart_input() -> dict[str, Any]:
    return _deepcopy(DEFAULT_RESTART_INPUT)


def _default_retention_input() -> list[dict[str, Any]]:
    return _deepcopy(DEFAULT_RETENTION_INPUT)


def _default_soak_input() -> dict[str, Any]:
    return _deepcopy(DEFAULT_SOAK_INPUT)


def _build_default_inputs() -> dict[str, Any]:
    return {
        "restart_timeouts_proof": build_restart_timeouts_dry_run_proof(_default_restart_input(), now="2026-01-01T00:05:00Z"),
        "retention_rotation_proof": build_retention_rotation_dry_run_proof(_default_retention_input(), now="2026-01-31T00:00:00Z"),
    }


def _status_of(readout: dict[str, Any] | None, *, keys: list[str]) -> str:
    if not isinstance(readout, dict):
        return "UNKNOWN"
    for key in keys:
        value = readout.get(key)
        if isinstance(value, str) and value.strip():
            return classify_proof_status(value)
    return "UNKNOWN"


def _proof_consistency(
    *,
    queue: dict[str, Any] | None,
    relay_processor: dict[str, Any] | None,
    relay_review: dict[str, Any] | None,
    restart: dict[str, Any] | None,
    retention: dict[str, Any] | None,
    soak: dict[str, Any] | None,
    ledger: dict[str, Any] | None,
    selector: dict[str, Any] | None,
    policy: dict[str, Any],
) -> dict[str, Any]:
    restart_status = _status_of(restart, keys=["proof_status"])
    retention_status = _status_of(retention, keys=["proof_status"])
    soak_status = _status_of(soak, keys=["proof_status"])
    relay_review_status = _status_of(relay_review, keys=["review_status", "proof_status"])
    queue_status = _status_of(queue, keys=["validation_status", "proof_status"])
    ledger_status = _status_of(ledger, keys=["validation_status", "proof_status", "review_status"])
    selector_status = _status_of(selector, keys=["validation_status"])

    contradictions: list[str] = []
    attention_reasons: list[str] = []
    blockers: list[str] = []
    invalid_reasons: list[str] = []

    if queue_status == "INVALID":
        invalid_reasons.append("runtime queue validation is INVALID")
    if relay_review_status == "INVALID":
        invalid_reasons.append("relay review is INVALID")
    if restart_status == "INVALID":
        invalid_reasons.append("restart/timeouts proof is INVALID")
    if retention_status == "INVALID":
        invalid_reasons.append("retention/rotation proof is INVALID")
    if soak_status == "INVALID":
        invalid_reasons.append("soak proof is INVALID")
    if ledger_status == "INVALID":
        invalid_reasons.append("operator dependency ledger is INVALID")
    if selector_status == "INVALID":
        invalid_reasons.append("reduction target selector is INVALID")

    if soak_status == "PASS":
        if restart_status == "BLOCKED":
            invalid_reasons.append("soak PASS contradicts blocked restart/timeouts proof")
        if retention_status == "BLOCKED":
            invalid_reasons.append("soak PASS contradicts blocked retention/rotation proof")
        if not isinstance(soak, dict) or soak.get("soak_pass") is not True:
            invalid_reasons.append("soak PASS requires soak_pass true")
        if restart_status == "INVALID" or retention_status == "INVALID":
            invalid_reasons.append("soak PASS cannot depend on invalid prerequisite proofs")
    if restart_status == "PASS" and isinstance(restart, dict) and restart.get("restart_executed") is True:
        invalid_reasons.append("restart/timeouts PASS contradicts restart_executed true")
    if retention_status == "PASS" and isinstance(retention, dict) and (retention.get("rotation_executed") is True or retention.get("delete_executed") is True):
        invalid_reasons.append("retention/rotation PASS contradicts executed file mutation")
    if isinstance(soak, dict) and soak.get("soak_executed") is True:
        invalid_reasons.append("soak_executed true contradicts dry-run gate")
    if isinstance(soak, dict) and soak.get("runtime_launched") is True:
        invalid_reasons.append("runtime_launched true contradicts dry-run gate")

    if restart_status == "ATTENTION":
        attention_reasons.append("restart/timeouts proof is ATTENTION")
        if not policy.get("allow_restart_attention", False):
            blockers.append("restart/timeouts attention not allowed by policy")
    if retention_status == "ATTENTION":
        attention_reasons.append("retention/rotation proof is ATTENTION")
        if not policy.get("allow_retention_attention", False):
            blockers.append("retention/rotation attention not allowed by policy")
    if soak_status == "ATTENTION":
        attention_reasons.append("soak proof is ATTENTION")
        if not policy.get("allow_soak_attention", False):
            blockers.append("soak attention not allowed by policy")
    if relay_review_status != "REVIEWABLE":
        if relay_review_status == "BLOCKED":
            blockers.append(f"relay review is {relay_review_status}")
        else:
            blockers.append("relay review is not REVIEWABLE")
    if queue_status == "BLOCKED":
        blockers.append("runtime queue validation is BLOCKED")
    if ledger_status == "BLOCKED":
        blockers.append("operator dependency ledger validation is BLOCKED")
    if selector_status == "BLOCKED":
        blockers.append("reduction target selector validation is BLOCKED")

    if isinstance(queue, dict) and list(queue.get("remaining_blockers") or []):
        blockers.append("runtime queue still lists remaining blockers")
    if isinstance(selector, dict):
        selected_target = str(selector.get("selected_target") or "")
        if selected_target in PROOF_PLANNING_TARGETS:
            attention_reasons.append("reduction target selector still points to a proof-planning target")
        if selected_target and selected_target != RELAY_ACCEPTANCE_TARGET and relay_review_status == "REVIEWABLE":
            attention_reasons.append("reduction target selector has not selected the relay acceptance packet")
    if isinstance(ledger, dict):
        scorecard = ledger.get("autonomy_scorecard") if isinstance(ledger.get("autonomy_scorecard"), dict) else {}
        if scorecard.get("autonomy_shift") == "NONE":
            attention_reasons.append("operator dependency ledger reports no autonomy shift")

    return {
        "restart_timeouts_status": restart_status,
        "retention_rotation_status": retention_status,
        "soak_status": soak_status,
        "relay_review_status": relay_review_status,
        "runtime_queue_status": queue_status,
        "operator_dependency_status": ledger_status,
        "reduction_target_status": selector_status,
        "attention_reasons": list(dict.fromkeys(attention_reasons)),
        "blockers": list(dict.fromkeys(blockers)),
        "invalid_reasons": list(dict.fromkeys(invalid_reasons)),
        "contradictions": list(dict.fromkeys(contradictions)),
    }


def _component_input(
    provided: Any,
    built: Any,
    *,
    required: bool,
    name: str,
    missing: list[str],
    invalid: list[str],
) -> Any:
    if provided is None:
        if required:
            missing.append(name)
        return built
    if not isinstance(provided, dict):
        invalid.append(f"{name} must be an object")
        return None
    return _deepcopy(provided)


def build_runtime_proof_gate(
    *,
    runtime_queue_readout: dict[str, Any] | None = None,
    relay_processor_readout: dict[str, Any] | None = None,
    relay_proof_review: dict[str, Any] | None = None,
    restart_timeouts_proof: dict[str, Any] | None = None,
    retention_rotation_proof: dict[str, Any] | None = None,
    soak_proof: dict[str, Any] | None = None,
    operator_dependency_ledger: dict[str, Any] | None = None,
    reduction_target_selector: dict[str, Any] | None = None,
    gate_policy: dict[str, Any] | None = None,
    now: str | None = None,
    source_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    policy = {**DEFAULT_GATE_POLICY, **(gate_policy or {})}
    generated_at = _now(now)

    built_defaults = _build_default_inputs()
    missing_inputs: list[str] = []
    invalid_inputs: list[str] = []

    queue = _component_input(
        runtime_queue_readout,
        build_runtime_execution_queue(),
        required=bool(policy.get("require_runtime_queue", True)),
        name="runtime_queue_readout",
        missing=missing_inputs,
        invalid=invalid_inputs,
    )
    relay = _component_input(
        relay_processor_readout,
        build_relay_runtime_processor(queue=queue if isinstance(queue, dict) else build_runtime_execution_queue(), now=generated_at),
        required=bool(policy.get("require_relay_processor", True)),
        name="relay_processor_readout",
        missing=missing_inputs,
        invalid=invalid_inputs,
    )
    review = _component_input(
        relay_proof_review,
        build_relay_dry_run_proof_review(relay_readout=relay if isinstance(relay, dict) else None, queue=queue if isinstance(queue, dict) else None, now=generated_at),
        required=bool(policy.get("require_relay_proof_review", True)),
        name="relay_proof_review",
        missing=missing_inputs,
        invalid=invalid_inputs,
    )
    restart = _component_input(
        restart_timeouts_proof,
        built_defaults["restart_timeouts_proof"],
        required=bool(policy.get("require_restart_timeouts_proof", True)),
        name="restart_timeouts_proof",
        missing=missing_inputs,
        invalid=invalid_inputs,
    )
    retention = _component_input(
        retention_rotation_proof,
        built_defaults["retention_rotation_proof"],
        required=bool(policy.get("require_retention_rotation_proof", True)),
        name="retention_rotation_proof",
        missing=missing_inputs,
        invalid=invalid_inputs,
    )
    soak = _component_input(
        soak_proof,
        build_soak_dry_run_proof(
            _default_soak_input(),
            restart_timeouts_proof=restart if isinstance(restart, dict) else built_defaults["restart_timeouts_proof"],
            retention_rotation_proof=retention if isinstance(retention, dict) else built_defaults["retention_rotation_proof"],
            now="2026-01-01T01:00:00Z",
        ),
        required=bool(policy.get("require_soak_proof", True)),
        name="soak_proof",
        missing=missing_inputs,
        invalid=invalid_inputs,
    )
    ledger = _component_input(
        operator_dependency_ledger,
        build_operator_dependency_ledger(queue=queue if isinstance(queue, dict) else None, relay_readout=relay if isinstance(relay, dict) else None, relay_review=review if isinstance(review, dict) else None, now=generated_at),
        required=bool(policy.get("require_operator_dependency_ledger", True)),
        name="operator_dependency_ledger",
        missing=missing_inputs,
        invalid=invalid_inputs,
    )
    selector = _component_input(
        reduction_target_selector,
        build_reduction_target_selector(ledger=ledger if isinstance(ledger, dict) else None, now=generated_at),
        required=bool(policy.get("require_reduction_target_selector", True)),
        name="reduction_target_selector",
        missing=missing_inputs,
        invalid=invalid_inputs,
    )

    queue_validation = validate_runtime_execution_queue(queue) if isinstance(queue, dict) else {"status": "BLOCK", "blockers": ["runtime queue missing"], "unsafe_flags": []}
    relay_validation = validate_relay_runtime_processor(relay) if isinstance(relay, dict) else {"status": "BLOCK", "blockers": ["relay processor missing"], "unsafe_flags": []}
    review_validation = validate_relay_dry_run_proof_review(review) if isinstance(review, dict) else {"status": "BLOCK", "blockers": ["relay review missing"], "unsafe_flags": []}
    restart_validation = validate_restart_timeouts_dry_run_proof(restart) if isinstance(restart, dict) else {"status": "BLOCK", "blockers": ["restart proof missing"], "unsafe_flags": []}
    retention_validation = validate_retention_rotation_dry_run_proof(retention) if isinstance(retention, dict) else {"status": "BLOCK", "blockers": ["retention proof missing"], "unsafe_flags": []}
    soak_validation = validate_soak_dry_run_proof(soak) if isinstance(soak, dict) else {"status": "BLOCK", "blockers": ["soak proof missing"], "unsafe_flags": []}
    ledger_validation = validate_operator_dependency_ledger(ledger) if isinstance(ledger, dict) else {"status": "BLOCK", "blockers": ["operator ledger missing"], "unsafe_flags": []}
    selector_validation = validate_reduction_target_selector(selector) if isinstance(selector, dict) else {"status": "BLOCK", "blockers": ["reduction selector missing"], "unsafe_flags": []}

    prerequisite_inputs = {
        "runtime_queue_readout": queue,
        "relay_processor_readout": relay,
        "relay_proof_review": review,
        "restart_timeouts_proof": restart,
        "retention_rotation_proof": retention,
        "soak_proof": soak,
        "operator_dependency_ledger": ledger,
        "reduction_target_selector": selector,
    }
    prerequisite_statuses = {
        "runtime_queue": queue_validation.get("status"),
        "relay_processor": relay_validation.get("status"),
        "relay_proof_review": review_validation.get("status"),
        "restart_timeouts_proof": restart_validation.get("status"),
        "retention_rotation_proof": retention_validation.get("status"),
        "soak_proof": soak_validation.get("status"),
        "operator_dependency_ledger": ledger_validation.get("status"),
        "reduction_target_selector": selector_validation.get("status"),
    }

    unsafe_flags_detected: list[dict[str, Any]] = []
    forbidden_claims_detected: list[dict[str, Any]] = []
    for input_name, readout in prerequisite_inputs.items():
        if isinstance(readout, dict):
            unsafe_flags_detected.extend(collect_unsafe_flags(readout, input_name=input_name))
            forbidden_claims_detected.extend(detect_forbidden_claims(readout, input_name=input_name))

    if isinstance(queue, dict) and queue.get("vacation_mode_complete") is True:
        unsafe_flags_detected.append({"input": "runtime_queue_readout", "path": "vacation_mode_complete", "key": "vacation_mode_complete", "value": True})
    if isinstance(review, dict) and review.get("vacation_mode_complete") is True:
        unsafe_flags_detected.append({"input": "relay_proof_review", "path": "vacation_mode_complete", "key": "vacation_mode_complete", "value": True})
    if isinstance(restart, dict) and restart.get("vacation_mode_complete") is True:
        unsafe_flags_detected.append({"input": "restart_timeouts_proof", "path": "vacation_mode_complete", "key": "vacation_mode_complete", "value": True})
    if isinstance(retention, dict) and retention.get("vacation_mode_complete") is True:
        unsafe_flags_detected.append({"input": "retention_rotation_proof", "path": "vacation_mode_complete", "key": "vacation_mode_complete", "value": True})
    if isinstance(soak, dict) and soak.get("vacation_mode_complete") is True:
        unsafe_flags_detected.append({"input": "soak_proof", "path": "vacation_mode_complete", "key": "vacation_mode_complete", "value": True})
    if isinstance(ledger, dict) and ledger.get("vacation_mode_complete") is True:
        unsafe_flags_detected.append({"input": "operator_dependency_ledger", "path": "vacation_mode_complete", "key": "vacation_mode_complete", "value": True})
    if isinstance(selector, dict) and selector.get("vacation_mode_complete") is True:
        unsafe_flags_detected.append({"input": "reduction_target_selector", "path": "vacation_mode_complete", "key": "vacation_mode_complete", "value": True})

    cross = _proof_consistency(
        queue=queue,
        relay_processor=relay,
        relay_review=review,
        restart=restart,
        retention=retention,
        soak=soak,
        ledger=ledger,
        selector=selector,
        policy=policy,
    )

    if isinstance(ledger, dict):
        autonomy_shift = str((ledger.get("autonomy_scorecard") or {}).get("autonomy_shift") or "NONE")
    else:
        autonomy_shift = "NONE"
    if isinstance(selector, dict):
        selected_target = str(selector.get("selected_target") or "")
        selected_category = str(selector.get("selected_category") or "")
        selected_reason = str(selector.get("selected_reason") or "")
    else:
        selected_target = ""
        selected_category = ""
        selected_reason = ""

    human_gate_required = bool(policy.get("require_human_gate", True))
    execution_allowed = False
    dispatch_allowed = False
    apply_allowed = False
    runtime_launch_allowed = False
    runtime_mutation_allowed = False
    telemetry_mutation_allowed = False
    scheduler_creation_allowed = False
    service_creation_allowed = False
    sos_allowed = False
    live_trading_allowed = False
    credentials_accessed = False
    approval_granted = False
    vacation_mode_complete = False
    unsafe_autonomy_claim = False

    blocker_reasons: list[str] = []
    invalid_reasons: list[str] = list(dict.fromkeys(cross["invalid_reasons"]))
    attention_reasons: list[str] = list(dict.fromkeys(cross["attention_reasons"]))
    blocker_reasons.extend(cross["blockers"])

    if invalid_inputs:
        invalid_reasons.extend(invalid_inputs)
    if missing_inputs:
        blocker_reasons.extend(missing_inputs)

    if queue_validation.get("status") == "BLOCK":
        blocker_reasons.extend(list(queue_validation.get("blockers") or []))
    if relay_validation.get("status") == "BLOCK":
        blocker_reasons.extend(list(relay_validation.get("blockers") or []))
    if review_validation.get("status") == "BLOCK":
        blocker_reasons.extend(list(review_validation.get("blockers") or []))
    if restart_validation.get("status") == "BLOCK":
        blocker_reasons.extend(list(restart_validation.get("blockers") or []))
    if retention_validation.get("status") == "BLOCK":
        blocker_reasons.extend(list(retention_validation.get("blockers") or []))
    if soak_validation.get("status") == "BLOCK":
        blocker_reasons.extend(list(soak_validation.get("blockers") or []))
    if ledger_validation.get("status") == "BLOCK":
        blocker_reasons.extend(list(ledger_validation.get("blockers") or []))
    if selector_validation.get("status") == "BLOCK":
        blocker_reasons.extend(list(selector_validation.get("blockers") or []))

    if unsafe_flags_detected:
        blocker_reasons.append("unsafe flags detected in prerequisite inputs")

    if forbidden_claims_detected:
        invalid_reasons.append("forbidden final verdict or status detected in prerequisite inputs")

    if any(flag.get("key") in {"execution_allowed", "dispatch_allowed", "apply_allowed", "runtime_launch_allowed", "scheduler_creation_allowed", "service_creation_allowed", "sos_allowed", "live_trading_allowed", "credentials_accessed", "approval_granted", "unsafe_autonomy_claim"} and flag.get("value") is True for flag in unsafe_flags_detected):
        blocker_reasons.append("execution, approval, or live-operation flag was true in an input")

    if any(flag.get("key") in {"vacation_mode_complete"} and flag.get("value") is True for flag in unsafe_flags_detected):
        blocker_reasons.append("vacation_mode_complete must remain false")

    if isinstance(restart, dict) and restart.get("proof_status") == "PASS" and restart.get("restart_executed") is True:
        invalid_reasons.append("restart/timeouts proof claims PASS while restart_executed is true")
    if isinstance(retention, dict) and retention.get("proof_status") == "PASS" and (retention.get("rotation_executed") is True or retention.get("delete_executed") is True):
        invalid_reasons.append("retention/rotation proof claims PASS while file mutation executed")
    if isinstance(soak, dict) and soak.get("proof_status") == "PASS" and (soak.get("soak_executed") is True or soak.get("runtime_launched") is True):
        invalid_reasons.append("soak proof claims PASS while soak or runtime launch executed")

    relay_reviewable = isinstance(review, dict) and review.get("review_status") == "REVIEWABLE"
    restart_pass = isinstance(restart, dict) and restart.get("proof_status") == "PASS"
    retention_pass = isinstance(retention, dict) and retention.get("proof_status") == "PASS"
    soak_pass = isinstance(soak, dict) and soak.get("proof_status") == "PASS" and soak.get("soak_pass") is True

    if policy.get("require_soak_pass", True) and not soak_pass:
        blocker_reasons.append("soak proof must pass for human gate readiness")
    if not relay_reviewable:
        blocker_reasons.append("relay proof review must be REVIEWABLE")
    if not restart_pass:
        blocker_reasons.append("restart/timeouts proof must pass")
    if not retention_pass:
        blocker_reasons.append("retention/rotation proof must pass")

    human_gate_ready = False
    final_verdict = "BLOCKED"

    if forbidden_claims_detected or invalid_reasons:
        final_verdict = "INVALID"
    elif blocker_reasons:
        final_verdict = "BLOCKED"
    elif attention_reasons:
        final_verdict = "ATTENTION"
    else:
        target_acceptance = selected_target == RELAY_ACCEPTANCE_TARGET
        if not target_acceptance:
            attention_reasons.append("reduction target selector has not advanced to human acceptance")
            final_verdict = "ATTENTION"
        else:
            final_verdict = "READY_FOR_HUMAN_GATE"
            human_gate_ready = True

    if final_verdict == "READY_FOR_HUMAN_GATE":
        if not human_gate_required:
            invalid_reasons.append("human gate is required")
            final_verdict = "INVALID"
            human_gate_ready = False
        if any(
            [
                execution_allowed,
                dispatch_allowed,
                apply_allowed,
                runtime_launch_allowed,
                runtime_mutation_allowed,
                telemetry_mutation_allowed,
                scheduler_creation_allowed,
                service_creation_allowed,
                sos_allowed,
                live_trading_allowed,
                credentials_accessed,
                approval_granted,
                vacation_mode_complete,
                unsafe_autonomy_claim,
            ]
        ):
            invalid_reasons.append("execution flags must remain false for human gate readiness")
            final_verdict = "INVALID"
            human_gate_ready = False

    if final_verdict == "READY_FOR_HUMAN_GATE":
        safe_next_action = "Present the connected dry-run proof chain for human gate review only."
        stop_condition = "Stop before execution; human gate review only."
    elif final_verdict == "ATTENTION":
        safe_next_action = "Resolve the attention reasons before presenting the proof chain for human gate review."
        stop_condition = "Stop after reviewing attention reasons; no execution."
    elif final_verdict == "BLOCKED":
        safe_next_action = "Fix the blockers before the proof chain can reach human gate review."
        stop_condition = "Stop until blockers are cleared; no execution."
    else:
        safe_next_action = "Repair invalid proof inputs before any human gate review."
        stop_condition = "Stop until invalid inputs are repaired; no execution."

    gate = {
        "schema": SCHEMA,
        "generated_at_utc": generated_at,
        "mode": MODE,
        "gate_type": GATE_TYPE,
        "gate_version": GATE_VERSION,
        "final_verdict": final_verdict,
        "final_verdict_reason": (
            "All connected dry-run proofs are safe enough for human gate review."
            if final_verdict == "READY_FOR_HUMAN_GATE"
            else "The connected dry-run proofs are not yet safe enough for human gate review."
        ),
        "human_gate_required": human_gate_required,
        "human_gate_ready": human_gate_ready,
        "execution_allowed": execution_allowed,
        "dispatch_allowed": dispatch_allowed,
        "apply_allowed": apply_allowed,
        "runtime_launch_allowed": runtime_launch_allowed,
        "runtime_mutation_allowed": runtime_mutation_allowed,
        "telemetry_mutation_allowed": telemetry_mutation_allowed,
        "scheduler_creation_allowed": scheduler_creation_allowed,
        "service_creation_allowed": service_creation_allowed,
        "sos_allowed": sos_allowed,
        "live_trading_allowed": live_trading_allowed,
        "credentials_accessed": credentials_accessed,
        "approval_granted": approval_granted,
        "vacation_mode_complete": vacation_mode_complete,
        "unsafe_autonomy_claim": unsafe_autonomy_claim,
        "prerequisite_inputs_present": [name for name, value in prerequisite_inputs.items() if isinstance(value, dict)],
        "prerequisite_inputs_missing": list(missing_inputs),
        "prerequisite_statuses": prerequisite_statuses,
        "accepted_prerequisites": [
            name for name, status in prerequisite_statuses.items() if name != "runtime_queue" and status == "PASS"
        ]
        + (["relay_proof_review"] if relay_reviewable else []),
        "rejected_prerequisites": [
            name for name, status in prerequisite_statuses.items() if status in {"BLOCK", "INVALID"}
        ],
        "attention_reasons": list(dict.fromkeys(attention_reasons)),
        "blockers": list(dict.fromkeys(blocker_reasons)),
        "invalid_reasons": list(dict.fromkeys(invalid_reasons)),
        "unsafe_flags_detected": _deepcopy(unsafe_flags_detected),
        "forbidden_claims_detected": _deepcopy(forbidden_claims_detected),
        "cross_proof_consistency": cross,
        "proof_chain_summary": {
            "runtime_queue": summarize_prerequisite("runtime_queue", queue),
            "relay_processor": summarize_prerequisite("relay_processor", relay),
            "relay_review": summarize_prerequisite("relay_review", review),
            "restart_timeouts": summarize_prerequisite("restart_timeouts", restart),
            "retention_rotation": summarize_prerequisite("retention_rotation", retention),
            "soak": summarize_prerequisite("soak", soak),
        },
        "operator_dependency_summary": summarize_prerequisite("operator_dependency_ledger", ledger),
        "reduction_target_summary": summarize_prerequisite("reduction_target_selector", selector),
        "runtime_queue_summary": summarize_prerequisite("runtime_queue", queue),
        "relay_summary": summarize_prerequisite("relay_processor", relay),
        "restart_timeouts_summary": summarize_prerequisite("restart_timeouts", restart),
        "retention_rotation_summary": summarize_prerequisite("retention_rotation", retention),
        "soak_summary": summarize_prerequisite("soak", soak),
        "gate_policy": _deepcopy(policy),
        "safe_next_action": safe_next_action,
        "stop_condition": stop_condition,
        "source_metadata": _deepcopy(source_metadata) if source_metadata is not None else {},
    }
    return gate


def validate_runtime_proof_gate(gate: dict[str, Any]) -> dict[str, object]:
    blockers: list[str] = []
    unsafe_flags: list[str] = []
    forbidden_claims: list[dict[str, Any]] = []
    checked_fields: list[str] = []

    if not isinstance(gate, dict):
        return {
            "status": "BLOCK",
            "blockers": ["gate must be an object"],
            "checked_fields": [],
            "unsafe_flags": ["gate_not_object"],
            "forbidden_claims": [],
            "final_verdict": None,
        }

    required_fields = [
        "schema",
        "generated_at_utc",
        "mode",
        "gate_type",
        "gate_version",
        "final_verdict",
        "final_verdict_reason",
        "human_gate_required",
        "human_gate_ready",
        "execution_allowed",
        "dispatch_allowed",
        "apply_allowed",
        "runtime_launch_allowed",
        "runtime_mutation_allowed",
        "telemetry_mutation_allowed",
        "scheduler_creation_allowed",
        "service_creation_allowed",
        "sos_allowed",
        "live_trading_allowed",
        "credentials_accessed",
        "approval_granted",
        "vacation_mode_complete",
        "unsafe_autonomy_claim",
        "prerequisite_inputs_present",
        "prerequisite_inputs_missing",
        "prerequisite_statuses",
        "accepted_prerequisites",
        "rejected_prerequisites",
        "attention_reasons",
        "blockers",
        "invalid_reasons",
        "unsafe_flags_detected",
        "forbidden_claims_detected",
        "cross_proof_consistency",
        "proof_chain_summary",
        "operator_dependency_summary",
        "reduction_target_summary",
        "runtime_queue_summary",
        "relay_summary",
        "restart_timeouts_summary",
        "retention_rotation_summary",
        "soak_summary",
        "gate_policy",
        "safe_next_action",
        "stop_condition",
    ]
    checked_fields = list(required_fields)
    missing = [field for field in required_fields if field not in gate]
    if missing:
        blockers.append(f"missing fields: {', '.join(sorted(missing))}")
        unsafe_flags.append("missing_fields")

    if gate.get("mode") != MODE:
        blockers.append("mode must be DRY_RUN_GATE")
        unsafe_flags.append("mode_invalid")

    final_verdict = str(gate.get("final_verdict") or "")
    if final_verdict not in FINAL_VERDICTS:
        if final_verdict in FORBIDDEN_FINAL_VERDICTS:
            blockers.append(f"final verdict must never be {final_verdict}")
            unsafe_flags.append("final_verdict_forbidden")
        else:
            blockers.append("final_verdict must be READY_FOR_HUMAN_GATE, ATTENTION, BLOCKED, or INVALID")
            unsafe_flags.append("final_verdict_invalid")

    recursive_unsafe = collect_unsafe_flags(gate, input_name="runtime_proof_gate")
    recursive_forbidden = detect_forbidden_claims(gate, input_name="runtime_proof_gate")
    if recursive_unsafe:
        blockers.append("unsafe flags detected in gate output")
        unsafe_flags.extend([f"{item['input']}:{item['path']}:{item['key']}" for item in recursive_unsafe])
    if recursive_forbidden:
        blockers.append("forbidden final verdict or status detected in gate output")
        forbidden_claims.extend(recursive_forbidden)

    if gate.get("human_gate_required") is not True:
        blockers.append("human_gate_required must be true")
        unsafe_flags.append("human_gate_required_false")
    if gate.get("execution_allowed") is True:
        blockers.append("execution_allowed must be false")
        unsafe_flags.append("execution_allowed_true")
    if gate.get("dispatch_allowed") is True:
        blockers.append("dispatch_allowed must be false")
        unsafe_flags.append("dispatch_allowed_true")
    if gate.get("apply_allowed") is True:
        blockers.append("apply_allowed must be false")
        unsafe_flags.append("apply_allowed_true")
    if gate.get("runtime_launch_allowed") is True:
        blockers.append("runtime_launch_allowed must be false")
        unsafe_flags.append("runtime_launch_allowed_true")
    if gate.get("runtime_mutation_allowed") is True:
        blockers.append("runtime_mutation_allowed must be false")
        unsafe_flags.append("runtime_mutation_allowed_true")
    if gate.get("telemetry_mutation_allowed") is True:
        blockers.append("telemetry_mutation_allowed must be false")
        unsafe_flags.append("telemetry_mutation_allowed_true")
    if gate.get("scheduler_creation_allowed") is True:
        blockers.append("scheduler_creation_allowed must be false")
        unsafe_flags.append("scheduler_creation_allowed_true")
    if gate.get("service_creation_allowed") is True:
        blockers.append("service_creation_allowed must be false")
        unsafe_flags.append("service_creation_allowed_true")
    if gate.get("sos_allowed") is True:
        blockers.append("sos_allowed must be false")
        unsafe_flags.append("sos_allowed_true")
    if gate.get("live_trading_allowed") is True:
        blockers.append("live_trading_allowed must be false")
        unsafe_flags.append("live_trading_allowed_true")
    if gate.get("credentials_accessed") is True:
        blockers.append("credentials_accessed must be false")
        unsafe_flags.append("credentials_accessed_true")
    if gate.get("approval_granted") is True:
        blockers.append("approval_granted must be false")
        unsafe_flags.append("approval_granted_true")
    if gate.get("vacation_mode_complete") is True:
        blockers.append("vacation_mode_complete must be false")
        unsafe_flags.append("vacation_mode_complete_true")
    if gate.get("unsafe_autonomy_claim") is True:
        blockers.append("unsafe_autonomy_claim must be false")
        unsafe_flags.append("unsafe_autonomy_claim_true")

    if not isinstance(gate.get("safe_next_action"), str) or not gate["safe_next_action"].strip():
        blockers.append("safe_next_action must be a non-empty string")
        unsafe_flags.append("safe_next_action_missing")
    if not isinstance(gate.get("stop_condition"), str) or not gate["stop_condition"].strip():
        blockers.append("stop_condition must be a non-empty string")
        unsafe_flags.append("stop_condition_missing")

    if not isinstance(gate.get("prerequisite_statuses"), dict):
        blockers.append("prerequisite_statuses must be an object")
        unsafe_flags.append("prerequisite_statuses_invalid")
    if not isinstance(gate.get("proof_chain_summary"), dict):
        blockers.append("proof_chain_summary must be an object")
        unsafe_flags.append("proof_chain_summary_invalid")
    if not isinstance(gate.get("cross_proof_consistency"), dict):
        blockers.append("cross_proof_consistency must be an object")
        unsafe_flags.append("cross_proof_consistency_invalid")

    if isinstance(gate.get("final_verdict"), str) and gate["final_verdict"] in FORBIDDEN_FINAL_VERDICTS:
        blockers.append(f"final_verdict must not be {gate['final_verdict']}")
        unsafe_flags.append("final_verdict_forbidden")

    if gate.get("final_verdict") == "READY_FOR_HUMAN_GATE":
        if gate.get("human_gate_ready") is not True:
            blockers.append("READY_FOR_HUMAN_GATE requires human_gate_ready true")
            unsafe_flags.append("human_gate_ready_false")
        if list(gate.get("prerequisite_inputs_missing") or []):
            blockers.append("READY_FOR_HUMAN_GATE cannot have missing prerequisites")
            unsafe_flags.append("ready_with_missing_prerequisites")
        if list(gate.get("blockers") or []):
            blockers.append("READY_FOR_HUMAN_GATE cannot have blockers")
            unsafe_flags.append("ready_with_blockers")
        if list(gate.get("attention_reasons") or []):
            blockers.append("READY_FOR_HUMAN_GATE cannot have attention reasons")
            unsafe_flags.append("ready_with_attention_reasons")
        if list(gate.get("invalid_reasons") or []):
            blockers.append("READY_FOR_HUMAN_GATE cannot have invalid reasons")
            unsafe_flags.append("ready_with_invalid_reasons")
        if list(gate.get("unsafe_flags_detected") or []):
            blockers.append("READY_FOR_HUMAN_GATE cannot have unsafe flags")
            unsafe_flags.append("ready_with_unsafe_flags")
        if list(gate.get("forbidden_claims_detected") or []):
            blockers.append("READY_FOR_HUMAN_GATE cannot have forbidden claims")
            unsafe_flags.append("ready_with_forbidden_claims")
        if gate.get("approval_granted") is True:
            blockers.append("READY_FOR_HUMAN_GATE cannot have approval_granted true")
            unsafe_flags.append("approval_granted_true")
        selector_summary = gate.get("reduction_target_summary") if isinstance(gate.get("reduction_target_summary"), dict) else {}
        if selector_summary.get("selected_target") != RELAY_ACCEPTANCE_TARGET:
            blockers.append("READY_FOR_HUMAN_GATE requires relay acceptance target selection")
            unsafe_flags.append("ready_without_relay_acceptance_target")
        if gate.get("human_gate_ready") is not True:
            blockers.append("READY_FOR_HUMAN_GATE must be human gate ready")
            unsafe_flags.append("human_gate_ready_false")

    safe_next_action = gate.get("safe_next_action")
    stop_condition = gate.get("stop_condition")
    if isinstance(safe_next_action, str) and isinstance(stop_condition, str):
        serialized = json.dumps({"safe_next_action": safe_next_action, "stop_condition": stop_condition}).lower()
        command_patterns = [
            "git push",
            "git commit",
            "git merge",
            "gh pr merge",
            "gh pr create",
            "register-scheduledtask",
            "new-service",
            "start-job",
            "start-process",
            "start-service",
            "subprocess",
            "shell=true",
        ]
        for pattern in command_patterns:
            if pattern in serialized:
                blockers.append("command string detected in gate output")
                unsafe_flags.append(f"command_string:{pattern}")
                break

        source_text = json.dumps(gate, sort_keys=True).lower()
        secret_patterns = [
            "secret" + "=",
            "token" + "=",
            "pass" + "word" + "=",
            "api" + "_key" + "=",
            "api" + "key" + "=",
            "bear" + "er ",
            "sk" + "-",
        ]
        for pattern in secret_patterns:
            if pattern in source_text:
                blockers.append("obvious secret assignment string detected in gate output")
                unsafe_flags.append(f"secret_pattern:{pattern}")
                break

    validation_status = "PASS" if not blockers else "BLOCK"
    return {
        "status": validation_status,
        "blockers": list(dict.fromkeys(blockers)),
        "checked_fields": checked_fields,
        "unsafe_flags": list(dict.fromkeys(unsafe_flags)),
        "forbidden_claims": forbidden_claims,
        "final_verdict": gate.get("final_verdict"),
    }


def summarize_runtime_proof_gate(gate: dict[str, Any]) -> dict[str, object]:
    if not isinstance(gate, dict):
        return {
            "final_verdict": None,
            "human_gate_ready": None,
            "human_gate_required": None,
            "execution_allowed": None,
            "dispatch_allowed": None,
            "apply_allowed": None,
            "runtime_launch_allowed": None,
            "scheduler_creation_allowed": None,
            "sos_allowed": None,
            "live_trading_allowed": None,
            "approval_granted": None,
            "vacation_mode_complete": None,
            "prerequisite_missing_count": 0,
            "blocker_count": 0,
            "attention_count": 0,
            "invalid_reason_count": 0,
            "unsafe_flag_count": 0,
            "forbidden_claim_count": 0,
            "restart_timeouts_status": None,
            "retention_rotation_status": None,
            "soak_status": None,
            "soak_pass": None,
            "relay_review_status": None,
            "runtime_queue_status": None,
            "safe_next_action": None,
            "stop_condition": None,
        }

    attention = list(gate.get("attention_reasons") or [])
    blockers = list(gate.get("blockers") or [])
    invalid = list(gate.get("invalid_reasons") or [])
    unsafe = list(gate.get("unsafe_flags_detected") or [])
    forbidden = list(gate.get("forbidden_claims_detected") or [])
    prereq_missing = list(gate.get("prerequisite_inputs_missing") or [])
    cross = gate.get("cross_proof_consistency") if isinstance(gate.get("cross_proof_consistency"), dict) else {}
    soak_summary = gate.get("soak_summary") if isinstance(gate.get("soak_summary"), dict) else {}
    relay_summary = gate.get("relay_summary") if isinstance(gate.get("relay_summary"), dict) else {}
    restart_summary = gate.get("restart_timeouts_summary") if isinstance(gate.get("restart_timeouts_summary"), dict) else {}
    retention_summary = gate.get("retention_rotation_summary") if isinstance(gate.get("retention_rotation_summary"), dict) else {}
    queue_summary = gate.get("runtime_queue_summary") if isinstance(gate.get("runtime_queue_summary"), dict) else {}
    return {
        "final_verdict": gate.get("final_verdict"),
        "human_gate_ready": gate.get("human_gate_ready"),
        "human_gate_required": gate.get("human_gate_required"),
        "execution_allowed": gate.get("execution_allowed"),
        "dispatch_allowed": gate.get("dispatch_allowed"),
        "apply_allowed": gate.get("apply_allowed"),
        "runtime_launch_allowed": gate.get("runtime_launch_allowed"),
        "scheduler_creation_allowed": gate.get("scheduler_creation_allowed"),
        "sos_allowed": gate.get("sos_allowed"),
        "live_trading_allowed": gate.get("live_trading_allowed"),
        "approval_granted": gate.get("approval_granted"),
        "vacation_mode_complete": gate.get("vacation_mode_complete"),
        "prerequisite_missing_count": len(prereq_missing),
        "blocker_count": len(blockers),
        "attention_count": len(attention),
        "invalid_reason_count": len(invalid),
        "unsafe_flag_count": len(unsafe),
        "forbidden_claim_count": len(forbidden),
        "restart_timeouts_status": restart_summary.get("proof_status"),
        "retention_rotation_status": retention_summary.get("proof_status"),
        "soak_status": soak_summary.get("proof_status"),
        "soak_pass": soak_summary.get("soak_pass"),
        "relay_review_status": relay_summary.get("review_status"),
        "runtime_queue_status": queue_summary.get("validation_status"),
        "safe_next_action": gate.get("safe_next_action"),
        "stop_condition": gate.get("stop_condition"),
        "cross_proof_consistency": cross,
    }


def build_runtime_proof_gate_markdown_summary(gate: dict[str, Any]) -> str:
    summary = summarize_runtime_proof_gate(gate)
    blockers = list(gate.get("blockers") or [])
    attention = list(gate.get("attention_reasons") or [])
    invalid = list(gate.get("invalid_reasons") or [])
    lines = [
        "# AI_OS Runtime Proof Gate",
        "",
        f"- final_verdict: `{summary.get('final_verdict')}`",
        f"- human_gate_ready: `{summary.get('human_gate_ready')}`",
        f"- human_gate_required: `{summary.get('human_gate_required')}`",
        f"- execution_allowed: `{summary.get('execution_allowed')}`",
        f"- dispatch_allowed: `{summary.get('dispatch_allowed')}`",
        f"- apply_allowed: `{summary.get('apply_allowed')}`",
        f"- runtime_launch_allowed: `{summary.get('runtime_launch_allowed')}`",
        f"- scheduler_creation_allowed: `{summary.get('scheduler_creation_allowed')}`",
        f"- sos_allowed: `{summary.get('sos_allowed')}`",
        f"- live_trading_allowed: `{summary.get('live_trading_allowed')}`",
        f"- blocker_count: `{summary.get('blocker_count')}`",
        f"- attention_count: `{summary.get('attention_count')}`",
        f"- invalid_reason_count: `{summary.get('invalid_reason_count')}`",
        f"- unsafe_flag_count: `{summary.get('unsafe_flag_count')}`",
        f"- safe_next_action: {summary.get('safe_next_action')}",
        f"- stop_condition: {summary.get('stop_condition')}",
        "",
        "## Blockers",
    ]
    if blockers:
        lines.extend(f"- {item}" for item in blockers)
    else:
        lines.append("- none")
    lines.extend(["", "## Attention"])
    if attention:
        lines.extend(f"- {item}" for item in attention)
    else:
        lines.append("- none")
    lines.extend(["", "## Invalid Reasons"])
    if invalid:
        lines.extend(f"- {item}" for item in invalid)
    else:
        lines.append("- none")
    lines.extend(["", "## Safety", "- This gate never launches runtime, mutates protected paths, or enables trading."])
    if gate.get("report_paths"):
        lines.extend(["", "## Report Paths"])
        lines.extend(f"- {item}" for item in gate.get("report_paths", []))
    return "\n".join(lines) + "\n"


def write_runtime_proof_gate_reports(
    gate: dict[str, Any],
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    out_dir = Path(output_dir) if output_dir is not None else root / REPORT_DIR
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / REPORT_JSON_NAME
    md_path = out_dir / REPORT_MD_NAME
    report = _deepcopy(gate)
    report["report_paths"] = [json_path.as_posix(), md_path.as_posix()]
    report.update(summarize_runtime_proof_gate(report))
    report["runtime_execution_allowed"] = report.get("execution_allowed")
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(build_runtime_proof_gate_markdown_summary(report), encoding="utf-8")
    return report


def run_runtime_proof_gate(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    write_report: bool = True,
    **kwargs: Any,
) -> dict[str, Any]:
    gate = build_runtime_proof_gate(**kwargs)
    if write_report:
        gate = write_runtime_proof_gate_reports(gate, repo_root=repo_root, output_dir=output_dir)
    return gate


def _cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI_OS runtime proof gate")
    parser.add_argument("--repo-root", default=".", help="repository root for output resolution")
    parser.add_argument("--output-dir", default=None, help="optional report output directory")
    parser.add_argument("--no-write", action="store_true", help="build the gate without writing report files")
    parser.add_argument("--runtime-queue-json")
    parser.add_argument("--relay-processor-json")
    parser.add_argument("--relay-proof-review-json")
    parser.add_argument("--restart-timeouts-proof-json")
    parser.add_argument("--retention-rotation-proof-json")
    parser.add_argument("--soak-proof-json")
    parser.add_argument("--operator-dependency-ledger-json")
    parser.add_argument("--reduction-target-selector-json")
    parser.add_argument("--gate-policy-json")
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
    root = Path(args.repo_root)
    gate = run_runtime_proof_gate(
        repo_root=root,
        output_dir=args.output_dir,
        write_report=not args.no_write,
        runtime_queue_readout=_load_json_arg(args.runtime_queue_json),
        relay_processor_readout=_load_json_arg(args.relay_processor_json),
        relay_proof_review=_load_json_arg(args.relay_proof_review_json),
        restart_timeouts_proof=_load_json_arg(args.restart_timeouts_proof_json),
        retention_rotation_proof=_load_json_arg(args.retention_rotation_proof_json),
        soak_proof=_load_json_arg(args.soak_proof_json),
        operator_dependency_ledger=_load_json_arg(args.operator_dependency_ledger_json),
        reduction_target_selector=_load_json_arg(args.reduction_target_selector_json),
        gate_policy=_load_json_arg(args.gate_policy_json),
        now=args.now,
    )
    validation = validate_runtime_proof_gate(gate)
    output = {
        "gate": gate,
        "validation": validation,
        "summary": summarize_runtime_proof_gate(gate),
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
