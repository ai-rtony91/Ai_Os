"""AI_OS relay runtime processor (observe-only).

This module consumes the existing runtime execution queue and emits a dry-run
relay proof/readout for the next strict lane. It does not dispatch workers, it
does not mutate runtime state, and it does not touch scheduler, SOS, broker, or
live operations.

Pure standard library. JSON-only CLI. No subprocess, no network, no file
writes.
"""

from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from typing import Any

from automation.orchestration.runtime_closure.aios_runtime_execution_queue import (
    build_runtime_execution_queue,
    summarize_next_actions,
    validate_runtime_execution_queue,
)


SCHEMA = "AIOS_RELAY_RUNTIME_PROCESSOR.v1"
RELAY_LANE_ID = "relay_runtime_processor"
HUMAN_ONLY_GATES = [
    "human_sos_arming",
    "human_scheduler_registration",
]
REQUIRED_RELAY_PREDECESSORS = [
    "approval_card_present",
    "completeness_ready",
    "path_guard_pass",
    "apply_inventory_target_selected",
]


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _deepcopy_queue(queue: dict[str, Any] | None) -> dict[str, Any]:
    if isinstance(queue, dict):
        return copy.deepcopy(queue)
    return {}


def _queue_state(queue: dict[str, Any]) -> dict[str, bool]:
    state = queue.get("state_snapshot")
    return copy.deepcopy(state) if isinstance(state, dict) else {}


def _blocked_human_gates(queue: dict[str, Any]) -> list[str]:
    lanes = queue.get("lanes", [])
    blocked: list[str] = []
    for lane in lanes if isinstance(lanes, list) else []:
        if not isinstance(lane, dict):
            continue
        if lane.get("human_required") is True and lane.get("automation_allowed") is False:
            lane_id = lane.get("lane_id")
            if isinstance(lane_id, str) and lane_id not in blocked:
                blocked.append(lane_id)
    for gate in HUMAN_ONLY_GATES:
        if gate not in blocked:
            blocked.append(gate)
    return blocked


def _next_lane(queue: dict[str, Any]) -> dict[str, Any]:
    summary = summarize_next_actions(queue)
    primary = summary.get("primary_lane")
    lanes = queue.get("lanes", [])
    if isinstance(primary, dict):
        lane_id = primary.get("lane_id")
        if isinstance(lane_id, str) and isinstance(lanes, list):
            for lane in lanes:
                if isinstance(lane, dict) and lane.get("lane_id") == lane_id:
                    return copy.deepcopy(lane)
        return copy.deepcopy(primary)
    if isinstance(lanes, list) and lanes and isinstance(lanes[0], dict):
        return copy.deepcopy(lanes[0])
    return {}


def _missing_predecessor_proofs(state: dict[str, bool], required: list[str]) -> list[str]:
    missing: list[str] = []
    for proof in required:
        if not state.get(proof, False):
            missing.append(proof)
    return missing


def build_relay_runtime_processor(
    existing_state: dict[str, Any] | None = None,
    *,
    queue: dict[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, object]:
    """Build a dry-run relay proof/readout for the next strict lane."""
    source_queue = _deepcopy_queue(queue) if queue is not None else build_runtime_execution_queue(existing_state)
    source_state = _queue_state(source_queue)
    queue_validation = validate_runtime_execution_queue(source_queue)
    next_lane = _next_lane(source_queue)
    lane_id = str(next_lane.get("lane_id") or RELAY_LANE_ID)
    lane_status = str(next_lane.get("current_status") or "UNKNOWN")
    predecessor_requirements = list(next_lane.get("required_inputs") or [])
    missing_proofs = _missing_predecessor_proofs(source_state, predecessor_requirements)
    blocked_human_gates = _blocked_human_gates(source_queue)
    vacation_mode_complete = False
    ready_for_relay = (
        queue_validation.get("status") == "PASS"
        and lane_id == RELAY_LANE_ID
        and not missing_proofs
    )

    if queue_validation.get("status") != "PASS":
        proof_status = "BLOCKED"
    elif missing_proofs:
        proof_status = "BLOCKED"
    elif source_state.get("runtime_dry_run_pass", False):
        proof_status = "DRY_RUN_PROVEN"
    else:
        proof_status = "READY_FOR_DRY_RUN"

    if missing_proofs:
        safe_next_action = (
            "Collect the missing predecessor proofs before any relay runtime review; "
            "do not dispatch, apply, or mutate runtime state."
        )
    elif proof_status == "DRY_RUN_PROVEN":
        safe_next_action = (
            "Present the relay dry-run proof for human review; the queue remains "
            "observe-only and no runtime mutation is allowed."
        )
    elif proof_status == "READY_FOR_DRY_RUN":
        safe_next_action = (
            "Prepare the relay dry-run proof review; keep the queue observe-only and "
            "hold all human-gated lanes."
        )
    else:
        safe_next_action = (
            "Repair the runtime execution queue blockers before any relay review can proceed."
        )

    readout = {
        "schema": SCHEMA,
        "generated_at_utc": _now(now),
        "mode": "DRY_RUN",
        "observe_only": True,
        "source_queue_schema": source_queue.get("schema_version"),
        "source_queue_validation": copy.deepcopy(queue_validation),
        "next_lane": copy.deepcopy(next_lane),
        "lane_status": lane_status,
        "predecessor_requirements": predecessor_requirements,
        "missing_proofs": missing_proofs,
        "blocked_human_gates": blocked_human_gates,
        "human_only_gates": list(HUMAN_ONLY_GATES),
        "dispatch_allowed": False,
        "apply_allowed": False,
        "runtime_mutation_allowed": False,
        "vacation_mode_complete": vacation_mode_complete,
        "proof_status": proof_status,
        "proof_chain": list(source_queue.get("proof_chain", [])),
        "queue_consumer": source_queue.get("queue_consumer", "operator_final_readout"),
        "ready_for_relay": ready_for_relay,
        "safe_next_action": safe_next_action,
    }
    return readout


def validate_relay_runtime_processor(readout: dict[str, Any]) -> dict[str, object]:
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
        "observe_only",
        "source_queue_schema",
        "source_queue_validation",
        "next_lane",
        "lane_status",
        "predecessor_requirements",
        "missing_proofs",
        "blocked_human_gates",
        "dispatch_allowed",
        "apply_allowed",
        "runtime_mutation_allowed",
        "vacation_mode_complete",
        "proof_status",
        "safe_next_action",
    ]
    checked_fields = list(required_fields)
    missing = [field for field in required_fields if field not in readout]
    if missing:
        blockers.append(f"missing fields: {', '.join(sorted(missing))}")
        unsafe_flags.append("missing_fields")

    if readout.get("mode") != "DRY_RUN":
        blockers.append("mode must be DRY_RUN")
        unsafe_flags.append("mode_not_dry_run")
    if readout.get("observe_only") is not True:
        blockers.append("observe_only must be true")
        unsafe_flags.append("observe_only_false")
    if readout.get("dispatch_allowed") is True:
        blockers.append("dispatch must remain blocked")
        unsafe_flags.append("dispatch_allowed_true")
    if readout.get("apply_allowed") is True:
        blockers.append("APPLY must remain blocked")
        unsafe_flags.append("apply_allowed_true")
    if readout.get("runtime_mutation_allowed") is True:
        blockers.append("runtime mutation must remain blocked")
        unsafe_flags.append("runtime_mutation_allowed_true")
    if readout.get("vacation_mode_complete") is True:
        blockers.append("vacation_mode_complete must remain false in relay preview")
        unsafe_flags.append("vacation_mode_complete_true")

    next_lane = readout.get("next_lane")
    if not isinstance(next_lane, dict):
        blockers.append("next_lane must be an object")
        unsafe_flags.append("next_lane_not_object")
    else:
        if next_lane.get("lane_id") != RELAY_LANE_ID:
            blockers.append("relay processor must point at the relay_runtime_processor lane")
            unsafe_flags.append("next_lane_wrong_lane")

    blocked_human_gates = list(readout.get("blocked_human_gates") or [])
    for gate in HUMAN_ONLY_GATES:
        if gate not in blocked_human_gates:
            blockers.append(f"missing human-only gate: {gate}")
            unsafe_flags.append(f"missing_{gate}")

    missing_proofs = list(readout.get("missing_proofs") or [])
    if readout.get("proof_status") == "BLOCKED" and not missing_proofs:
        blockers.append("BLOCKED proof status requires at least one missing predecessor proof or queue blocker")
        unsafe_flags.append("blocked_without_missing_proofs")

    if not isinstance(readout.get("safe_next_action"), str) or not readout["safe_next_action"].strip():
        blockers.append("safe_next_action must be a non-empty string")
        unsafe_flags.append("safe_next_action_missing")

    source_queue_validation = readout.get("source_queue_validation")
    if not isinstance(source_queue_validation, dict):
        blockers.append("source_queue_validation must be an object")
        unsafe_flags.append("source_queue_validation_not_object")

    status = "PASS" if not blockers else "BLOCK"
    return {
        "status": status,
        "blockers": blockers,
        "checked_fields": checked_fields,
        "unsafe_flags": unsafe_flags,
    }


def summarize_relay_runtime_processor(readout: dict[str, Any]) -> dict[str, object]:
    lane = readout.get("next_lane") if isinstance(readout, dict) else {}
    next_lane = lane if isinstance(lane, dict) else {}
    return {
        "status": "OK",
        "schema": readout.get("schema") if isinstance(readout, dict) else None,
        "next_lane_id": next_lane.get("lane_id"),
        "next_lane_title": next_lane.get("title"),
        "proof_status": readout.get("proof_status") if isinstance(readout, dict) else None,
        "safe_next_action": readout.get("safe_next_action") if isinstance(readout, dict) else None,
        "blocked_human_gates": list(readout.get("blocked_human_gates") or []) if isinstance(readout, dict) else [],
        "proof_chain": list(readout.get("proof_chain") or []) if isinstance(readout, dict) else [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the AI_OS relay runtime processor readout (JSON only).")
    parser.add_argument("--state-json", default=None, help="optional JSON string containing queue proof state booleans")
    parser.add_argument("--queue-json", default=None, help="optional JSON string with a prebuilt runtime execution queue")
    parser.add_argument("--now", default=None, help="optional ISO-8601 timestamp for deterministic output")
    args = parser.parse_args()

    state = json.loads(args.state_json) if args.state_json else None
    queue = json.loads(args.queue_json) if args.queue_json else None
    readout = build_relay_runtime_processor(state, queue=queue, now=args.now)
    payload = {
        "readout": readout,
        "validation": validate_relay_runtime_processor(readout),
        "summary": summarize_relay_runtime_processor(readout),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["validation"]["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
