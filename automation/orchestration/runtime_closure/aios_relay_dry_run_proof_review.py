"""AI_OS relay dry-run proof review (observe-only).

This module consumes the relay runtime processor readout and decides whether the
relay dry-run proof is reviewable, blocked, or invalid. It does not dispatch
workers, mutate runtime state, create scheduler or service actions, arm SOS, or
claim vacation mode completion.

Pure standard library. JSON-only CLI. No subprocess, no network, no file
writes.
"""

from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from typing import Any

from automation.orchestration.runtime_closure.aios_relay_runtime_processor import (
    build_relay_runtime_processor,
    validate_relay_runtime_processor,
)


SCHEMA = "AIOS_RELAY_DRY_RUN_PROOF_REVIEW.v1"
REVIEWABLE_STATUSES = {"READY_FOR_DRY_RUN", "DRY_RUN_PROVEN"}
HUMAN_ONLY_GATES = [
    "human_sos_arming",
    "human_scheduler_registration",
]


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _deepcopy(value: Any) -> Any:
    return copy.deepcopy(value)


def _missing_fields(readout: dict[str, Any], required_fields: list[str]) -> list[str]:
    return [field for field in required_fields if field not in readout]


def _blocked_human_gates(readout: dict[str, Any]) -> list[str]:
    gates = list(readout.get("blocked_human_gates") or [])
    for gate in HUMAN_ONLY_GATES:
        if gate not in gates:
            gates.append(gate)
    return gates


def build_relay_dry_run_proof_review(
    existing_state: dict[str, Any] | None = None,
    *,
    relay_readout: dict[str, Any] | None = None,
    queue: dict[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, object]:
    """Review a relay dry-run proof readout or build one from existing state."""
    source_readout = (
        _deepcopy(relay_readout)
        if isinstance(relay_readout, dict)
        else build_relay_runtime_processor(existing_state, queue=queue, now=now)
    )
    validation = validate_relay_runtime_processor(source_readout)
    missing = _missing_fields(
        source_readout,
        [
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
        ],
    )

    safety_flags = list(validation.get("unsafe_flags", []))
    if source_readout.get("mode") != "DRY_RUN":
        safety_flags.append("mode_not_dry_run")
    if source_readout.get("observe_only") is not True:
        safety_flags.append("observe_only_false")
    if source_readout.get("dispatch_allowed") is True:
        safety_flags.append("dispatch_allowed_true")
    if source_readout.get("apply_allowed") is True:
        safety_flags.append("apply_allowed_true")
    if source_readout.get("runtime_mutation_allowed") is True:
        safety_flags.append("runtime_mutation_allowed_true")
    if source_readout.get("vacation_mode_complete") is True:
        safety_flags.append("vacation_mode_complete_true")

    blocked_human_gates = _blocked_human_gates(source_readout)
    missing_proofs = list(source_readout.get("missing_proofs") or [])
    proof_status = str(source_readout.get("proof_status") or "UNKNOWN")

    invalid_reasons: list[str] = []
    if missing:
        invalid_reasons.append(f"missing fields: {', '.join(sorted(missing))}")
    if safety_flags:
        invalid_reasons.append("unsafe flags present: " + ", ".join(sorted(dict.fromkeys(safety_flags))))
    if source_readout.get("dispatch_allowed") is True:
        invalid_reasons.append("dispatch_allowed must be false")
    if source_readout.get("apply_allowed") is True:
        invalid_reasons.append("apply_allowed must be false")
    if source_readout.get("runtime_mutation_allowed") is True:
        invalid_reasons.append("runtime_mutation_allowed must be false")
    if source_readout.get("vacation_mode_complete") is True:
        invalid_reasons.append("vacation_mode_complete must remain false")

    if invalid_reasons:
        review_status = "INVALID"
    elif missing_proofs:
        review_status = "BLOCKED"
    elif proof_status in REVIEWABLE_STATUSES and source_readout.get("dispatch_allowed") is False:
        review_status = "REVIEWABLE"
    else:
        review_status = "BLOCKED"

    proof_reviewable = review_status == "REVIEWABLE"
    next_lane = _deepcopy(source_readout.get("next_lane")) if isinstance(source_readout.get("next_lane"), dict) else source_readout.get("next_lane")
    if review_status == "REVIEWABLE":
        safe_next_action = (
            "Surface the relay dry-run proof for human acceptance. After acceptance, "
            "the next safe planning step is restart/timeouts proof planning."
        )
    elif review_status == "BLOCKED":
        safe_next_action = (
            "Collect the missing predecessor proofs before human acceptance; the relay "
            "proof is not reviewable yet."
        )
    else:
        safe_next_action = (
            "Repair the relay proof readout before any human review or downstream proof work."
        )

    review = {
        "schema": SCHEMA,
        "generated_at_utc": _now(now or source_readout.get("generated_at_utc")),
        "mode": "DRY_RUN",
        "observe_only": True,
        "source_relay_schema": source_readout.get("schema"),
        "source_relay_validation": _deepcopy(validation),
        "review_status": review_status,
        "proof_reviewable": proof_reviewable,
        "proof_status": proof_status,
        "next_lane": next_lane,
        "missing_proofs": missing_proofs,
        "blocked_human_gates": blocked_human_gates,
        "safety_flags": list(dict.fromkeys(safety_flags)),
        "dispatch_allowed": False,
        "apply_allowed": False,
        "runtime_mutation_allowed": False,
        "vacation_mode_complete": False,
        "safe_next_action": safe_next_action,
        "invalid_reasons": invalid_reasons,
        "reviewable_statuses": list(REVIEWABLE_STATUSES),
        "human_only_gates": list(HUMAN_ONLY_GATES),
    }
    return review


def validate_relay_dry_run_proof_review(review: dict[str, Any]) -> dict[str, object]:
    blockers: list[str] = []
    unsafe_flags: list[str] = []
    checked_fields: list[str] = []

    if not isinstance(review, dict):
        return {
            "status": "INVALID",
            "blockers": ["review must be an object"],
            "checked_fields": [],
            "unsafe_flags": ["review_not_object"],
        }

    required_fields = [
        "schema",
        "generated_at_utc",
        "mode",
        "observe_only",
        "source_relay_schema",
        "source_relay_validation",
        "review_status",
        "proof_reviewable",
        "proof_status",
        "next_lane",
        "missing_proofs",
        "blocked_human_gates",
        "safety_flags",
        "dispatch_allowed",
        "apply_allowed",
        "runtime_mutation_allowed",
        "vacation_mode_complete",
        "safe_next_action",
    ]
    checked_fields = list(required_fields)
    missing = [field for field in required_fields if field not in review]
    if missing:
        blockers.append(f"missing fields: {', '.join(sorted(missing))}")
        unsafe_flags.append("missing_fields")

    if review.get("mode") != "DRY_RUN":
        blockers.append("mode must be DRY_RUN")
        unsafe_flags.append("mode_not_dry_run")
    if review.get("observe_only") is not True:
        blockers.append("observe_only must be true")
        unsafe_flags.append("observe_only_false")
    if review.get("dispatch_allowed") is True:
        blockers.append("dispatch must remain blocked")
        unsafe_flags.append("dispatch_allowed_true")
    if review.get("apply_allowed") is True:
        blockers.append("apply must remain blocked")
        unsafe_flags.append("apply_allowed_true")
    if review.get("runtime_mutation_allowed") is True:
        blockers.append("runtime mutation must remain blocked")
        unsafe_flags.append("runtime_mutation_allowed_true")
    if review.get("vacation_mode_complete") is True:
        blockers.append("vacation_mode_complete must remain false")
        unsafe_flags.append("vacation_mode_complete_true")

    if review.get("proof_status") == "BLOCKED" and not list(review.get("missing_proofs") or []):
        blockers.append("BLOCKED proof status requires at least one missing predecessor proof")
        unsafe_flags.append("blocked_without_missing_proofs")

    blocked_human_gates = list(review.get("blocked_human_gates") or [])
    for gate in HUMAN_ONLY_GATES:
        if gate not in blocked_human_gates:
            blockers.append(f"missing human-only gate: {gate}")
            unsafe_flags.append(f"missing_{gate}")

    source_validation = review.get("source_relay_validation")
    if not isinstance(source_validation, dict):
        blockers.append("source_relay_validation must be an object")
        unsafe_flags.append("source_relay_validation_not_object")
    else:
        source_status = source_validation.get("status")
        if source_status == "BLOCK":
            unsafe_flags.extend(list(source_validation.get("unsafe_flags", [])))
            if review.get("review_status") == "REVIEWABLE":
                blockers.append("reviewable relay proof cannot derive from a blocked relay validation")
                unsafe_flags.append("reviewable_from_blocked_relay")

    review_status = review.get("review_status")
    if review_status not in {"INVALID", "BLOCKED", "REVIEWABLE"}:
        blockers.append("review_status must be INVALID, BLOCKED, or REVIEWABLE")
        unsafe_flags.append("review_status_invalid")
    if review_status == "REVIEWABLE" and review.get("proof_reviewable") is not True:
        blockers.append("reviewable proof must set proof_reviewable true")
        unsafe_flags.append("proof_reviewable_false")
    if review_status != "REVIEWABLE" and review.get("proof_reviewable") is True:
        blockers.append("non-reviewable proof must not set proof_reviewable true")
        unsafe_flags.append("proof_reviewable_true_when_blocked")

    if not isinstance(review.get("safe_next_action"), str) or not review["safe_next_action"].strip():
        blockers.append("safe_next_action must be a non-empty string")
        unsafe_flags.append("safe_next_action_missing")

    if not isinstance(review.get("next_lane"), dict):
        blockers.append("next_lane must be an object")
        unsafe_flags.append("next_lane_not_object")

    if not isinstance(review.get("safety_flags"), list):
        blockers.append("safety_flags must be a list")
        unsafe_flags.append("safety_flags_not_list")

    status = "PASS" if not blockers and review_status in {"INVALID", "BLOCKED", "REVIEWABLE"} else "BLOCK"
    return {
        "status": status,
        "blockers": blockers,
        "checked_fields": checked_fields,
        "unsafe_flags": unsafe_flags,
    }


def summarize_relay_dry_run_proof_review(review: dict[str, Any]) -> dict[str, object]:
    next_lane = review.get("next_lane") if isinstance(review, dict) else {}
    lane = next_lane if isinstance(next_lane, dict) else {}
    return {
        "status": "OK",
        "schema": review.get("schema") if isinstance(review, dict) else None,
        "review_status": review.get("review_status") if isinstance(review, dict) else None,
        "proof_reviewable": review.get("proof_reviewable") if isinstance(review, dict) else None,
        "next_lane_id": lane.get("lane_id"),
        "safe_next_action": review.get("safe_next_action") if isinstance(review, dict) else None,
        "blocked_human_gates": list(review.get("blocked_human_gates") or []) if isinstance(review, dict) else [],
        "safety_flags": list(review.get("safety_flags") or []) if isinstance(review, dict) else [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the AI_OS relay dry-run proof review (JSON only).")
    parser.add_argument("--relay-json", default=None, help="optional JSON string containing a relay processor readout")
    parser.add_argument("--state-json", default=None, help="optional JSON string used to build a relay processor readout")
    parser.add_argument("--queue-json", default=None, help="optional JSON string with a prebuilt runtime execution queue")
    parser.add_argument("--now", default=None, help="optional ISO-8601 timestamp for deterministic output")
    args = parser.parse_args()

    relay = json.loads(args.relay_json) if args.relay_json else None
    state = json.loads(args.state_json) if args.state_json else None
    queue = json.loads(args.queue_json) if args.queue_json else None

    review = build_relay_dry_run_proof_review(state, relay_readout=relay, queue=queue, now=args.now)
    payload = {
        "review": review,
        "validation": validate_relay_dry_run_proof_review(review),
        "summary": summarize_relay_dry_run_proof_review(review),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["validation"]["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
