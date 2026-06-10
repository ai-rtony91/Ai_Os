"""AI_OS operator dependency ledger (report-only).

This module measures what still depends on Anthony/Tony versus what AI_OS can
already remember, notice, decide, route, or recover from through repo-held
state. It is a pure-data reporting layer: no runtime execution, no APPLY, no
dispatch, no scheduler/SOS, no live operations, and no file writes by default.

Pure standard library. JSON-only CLI. Deterministic with injected state and
timestamp.
"""

from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from typing import Any

from automation.orchestration.runtime_closure.aios_relay_dry_run_proof_review import (
    build_relay_dry_run_proof_review,
    validate_relay_dry_run_proof_review,
)
from automation.orchestration.runtime_closure.aios_relay_runtime_processor import (
    build_relay_runtime_processor,
    validate_relay_runtime_processor,
)
from automation.orchestration.runtime_closure.aios_runtime_execution_queue import (
    build_runtime_execution_queue,
    validate_runtime_execution_queue,
)


SCHEMA = "AIOS_OPERATOR_DEPENDENCY_LEDGER.v1"
DEPENDENCY_CATEGORIES = ["remember", "notice", "decide", "route", "recover"]
COMPONENT_ORDER = [
    "runtime_execution_queue",
    "relay_runtime_processor",
    "relay_dry_run_proof_review",
]


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _deepcopy(obj: Any) -> Any:
    return copy.deepcopy(obj)


def _default_inputs(existing_state: dict[str, Any] | None = None) -> dict[str, Any]:
    return dict(existing_state or {})


def _queue_component(queue: dict[str, Any]) -> dict[str, Any]:
    validation = validate_runtime_execution_queue(queue)
    queue_validation = _deepcopy(validation)
    remaining_blockers = list(queue.get("remaining_blockers") or [])
    human_only_gates = list(queue.get("hard_gate_summary", {}).get("human_only_lanes") or [])
    next_actions = [
        {
            "lane_id": lane.get("lane_id"),
            "title": lane.get("title"),
            "safe_next_command": lane.get("safe_next_command"),
        }
        for lane in list(queue.get("lanes") or [])
        if isinstance(lane, dict)
    ]
    categories = {
        "remember": {
            "tony": [
                "Remember the current queue still has proof blockers and human-only gates.",
            ],
            "ai_os": [
                "next_strict_serial_order",
                "proof_chain",
                "remaining_blockers",
                "human_only_gates",
            ],
        },
        "notice": {
            "tony": [
                "Notice the blocker list before asking for the next lane.",
            ],
            "ai_os": [
                "validation_status",
                "remaining_blockers",
                "hard_gate_summary",
            ],
        },
        "decide": {
            "tony": [
                "Decide whether to release the next lane after reviewing the queue.",
            ],
            "ai_os": [
                "safe_next_action",
                "validation_status",
            ],
        },
        "route": {
            "tony": [
                "Route the work to the next strict serial lane.",
            ],
            "ai_os": [
                "next_lane",
                "queue_consumer",
                "next_strict_serial_order",
            ],
        },
        "recover": {
            "tony": [
                "Recover from stale or missing proof state if the queue becomes inconsistent.",
            ],
            "ai_os": [
                "assert_no_hard_gate_bypass",
                "remaining_blockers",
                "validation_status",
            ],
        },
    }
    ai_os_items = [
        "next_strict_serial_order",
        "proof_chain",
        "remaining_blockers",
        "human_only_gates",
        "safe_next_action",
        "validation_status",
        "queue_consumer",
    ]
    remaining = [item for bucket in categories.values() for item in bucket["tony"]]
    reduced = [item for bucket in categories.values() for item in bucket["ai_os"]]
    return {
        "component_id": "runtime_execution_queue",
        "component_name": "Runtime execution queue",
        "source_schema": queue.get("schema_version"),
        "validation_status": validation.get("status"),
        "proof_status": queue_validation.get("status"),
        "next_lane": next_actions[0] if next_actions else None,
        "blocked_human_gates": human_only_gates,
        "safe_next_action": queue.get("hard_gate_summary", {}).get("global", [None])[-1] if queue.get("hard_gate_summary") else None,
        "dependency_categories": categories,
        "operator_dependency_items": [
            {"component_id": "runtime_execution_queue", "category": category, "tony": data["tony"], "ai_os": data["ai_os"]}
            for category, data in categories.items()
        ],
        "ai_os_owned_items": ai_os_items,
        "remaining_human_burdens": remaining,
        "reduced_burdens": reduced,
        "human_required_count": len(remaining),
        "ai_os_owned_count": len(ai_os_items),
        "reduced_dependency_count": len(reduced),
        "remaining_dependency_count": len(remaining),
        "autonomy_shift": "PARTIAL",
        "review_status": validation.get("status"),
        "missing_proofs": list(queue.get("remaining_blockers") or []),
    }


def _relay_processor_component(existing_state: dict[str, Any] | None, queue: dict[str, Any]) -> dict[str, Any]:
    readout = build_relay_runtime_processor(existing_state, queue=queue, now=None)
    validation = validate_relay_runtime_processor(readout)
    categories = {
        "remember": {
            "tony": [
                "Remember relay is DRY_RUN-only and vacation_mode_complete must stay false.",
            ],
            "ai_os": [
                "mode",
                "observe_only",
                "vacation_mode_complete",
            ],
        },
        "notice": {
            "tony": [
                "Notice missing predecessor proofs and blocked human-only gates.",
            ],
            "ai_os": [
                "missing_proofs",
                "blocked_human_gates",
            ],
        },
        "decide": {
            "tony": [
                "Decide whether the relay proof can be accepted for review.",
            ],
            "ai_os": [
                "proof_status",
                "ready_for_relay",
                "safe_next_action",
            ],
        },
        "route": {
            "tony": [
                "Route the relay output toward proof review or hold it for repair.",
            ],
            "ai_os": [
                "next_lane",
                "queue_consumer",
            ],
        },
        "recover": {
            "tony": [
                "Recover upstream proof gaps before advancing.",
            ],
            "ai_os": [
                "source_queue_validation",
                "proof_chain",
                "validation_status",
            ],
        },
    }
    ai_os_items = [
        "mode",
        "observe_only",
        "vacation_mode_complete",
        "missing_proofs",
        "blocked_human_gates",
        "proof_status",
        "ready_for_relay",
        "safe_next_action",
        "next_lane",
        "queue_consumer",
        "source_queue_validation",
    ]
    remaining = [item for bucket in categories.values() for item in bucket["tony"]]
    reduced = [item for bucket in categories.values() for item in bucket["ai_os"]]
    return {
        "component_id": "relay_runtime_processor",
        "component_name": "Relay runtime processor",
        "source_schema": readout.get("schema"),
        "validation_status": validation.get("status"),
        "proof_status": readout.get("proof_status"),
        "review_status": validation.get("status"),
        "next_lane": readout.get("next_lane"),
        "blocked_human_gates": list(readout.get("blocked_human_gates") or []),
        "safe_next_action": readout.get("safe_next_action"),
        "dependency_categories": categories,
        "operator_dependency_items": [
            {"component_id": "relay_runtime_processor", "category": category, "tony": data["tony"], "ai_os": data["ai_os"]}
            for category, data in categories.items()
        ],
        "ai_os_owned_items": ai_os_items,
        "remaining_human_burdens": remaining,
        "reduced_burdens": reduced,
        "human_required_count": len(remaining),
        "ai_os_owned_count": len(ai_os_items),
        "reduced_dependency_count": len(reduced),
        "remaining_dependency_count": len(remaining),
        "autonomy_shift": "PARTIAL",
        "missing_proofs": list(readout.get("missing_proofs") or []),
    }


def _relay_review_component(existing_state: dict[str, Any] | None, queue: dict[str, Any], relay_readout: dict[str, Any]) -> dict[str, Any]:
    review = build_relay_dry_run_proof_review(existing_state, relay_readout=relay_readout, queue=queue, now=None)
    validation = validate_relay_dry_run_proof_review(review)
    categories = {
        "remember": {
            "tony": [
                "Remember the relay review is report-only and never means COMPLETE.",
            ],
            "ai_os": [
                "review_status",
                "proof_reviewable",
                "vacation_mode_complete",
            ],
        },
        "notice": {
            "tony": [
                "Notice invalid flags and missing proofs before accepting the proof.",
            ],
            "ai_os": [
                "safety_flags",
                "missing_proofs",
                "blocked_human_gates",
            ],
        },
        "decide": {
            "tony": [
                "Decide whether the proof is reviewable or still blocked.",
            ],
            "ai_os": [
                "review_status",
                "proof_reviewable",
                "safe_next_action",
            ],
        },
        "route": {
            "tony": [
                "Route reviewable proof toward the next planning step or hold for repair.",
            ],
            "ai_os": [
                "next_lane",
                "safe_next_action",
            ],
        },
        "recover": {
            "tony": [
                "Recover from invalid proof/readout before any downstream planning.",
            ],
            "ai_os": [
                "source_relay_validation",
                "validation_status",
                "invalid_reasons",
            ],
        },
    }
    ai_os_items = [
        "review_status",
        "proof_reviewable",
        "proof_status",
        "vacation_mode_complete",
        "safety_flags",
        "missing_proofs",
        "blocked_human_gates",
        "safe_next_action",
        "next_lane",
        "source_relay_validation",
    ]
    remaining = [item for bucket in categories.values() for item in bucket["tony"]]
    reduced = [item for bucket in categories.values() for item in bucket["ai_os"]]
    return {
        "component_id": "relay_dry_run_proof_review",
        "component_name": "Relay dry-run proof review",
        "source_schema": review.get("schema"),
        "validation_status": validation.get("status"),
        "review_status": review.get("review_status"),
        "proof_status": review.get("proof_status"),
        "proof_reviewable": review.get("proof_reviewable"),
        "next_lane": review.get("next_lane"),
        "blocked_human_gates": list(review.get("blocked_human_gates") or []),
        "safe_next_action": review.get("safe_next_action"),
        "dependency_categories": categories,
        "operator_dependency_items": [
            {"component_id": "relay_dry_run_proof_review", "category": category, "tony": data["tony"], "ai_os": data["ai_os"]}
            for category, data in categories.items()
        ],
        "ai_os_owned_items": ai_os_items,
        "remaining_human_burdens": remaining,
        "reduced_burdens": reduced,
        "human_required_count": len(remaining),
        "ai_os_owned_count": len(ai_os_items),
        "reduced_dependency_count": len(reduced),
        "remaining_dependency_count": len(remaining),
        "autonomy_shift": "PARTIAL",
        "missing_proofs": list(review.get("missing_proofs") or []),
    }


def _scorecard(components: list[dict[str, Any]]) -> dict[str, Any]:
    human_required_count = sum(int(component.get("human_required_count", 0)) for component in components)
    ai_os_owned_count = sum(int(component.get("ai_os_owned_count", 0)) for component in components)
    reduced_dependency_count = sum(int(component.get("reduced_dependency_count", 0)) for component in components)
    remaining_dependency_count = sum(int(component.get("remaining_dependency_count", 0)) for component in components)
    if ai_os_owned_count == 0:
        autonomy_shift = "NONE"
    elif remaining_dependency_count > 0:
        autonomy_shift = "PARTIAL"
    else:
        autonomy_shift = "MEANINGFUL"
    return {
        "human_required_count": human_required_count,
        "ai_os_owned_count": ai_os_owned_count,
        "reduced_dependency_count": reduced_dependency_count,
        "remaining_dependency_count": remaining_dependency_count,
        "autonomy_shift": autonomy_shift,
    }


def _next_reduction_target(components: list[dict[str, Any]]) -> dict[str, Any]:
    review = next((c for c in components if c["component_id"] == "relay_dry_run_proof_review"), None)
    relay = next((c for c in components if c["component_id"] == "relay_runtime_processor"), None)
    queue = next((c for c in components if c["component_id"] == "runtime_execution_queue"), None)
    if review and review.get("review_status") != "REVIEWABLE":
        return {
            "component_id": review["component_id"],
            "component_name": review["component_name"],
            "dependency_category": "recover",
            "target_status": "REVIEWABLE",
            "reason": "The relay proof review is still the closest operator dependency bottleneck.",
            "safe_next_action": "Resolve missing relay predecessor proofs and keep SOS/scheduler blocked in repo-held state.",
        }
    if relay and relay.get("proof_status") != "DRY_RUN_PROVEN":
        return {
            "component_id": relay["component_id"],
            "component_name": relay["component_name"],
            "dependency_category": "decide",
            "target_status": "DRY_RUN_PROVEN",
            "reason": "The relay processor still needs a proven dry-run readout before downstream planning can shrink operator burden.",
            "safe_next_action": "Supply the missing relay predecessor proofs and preserve human-only gates.",
        }
    if queue and queue.get("validation_status") != "PASS":
        return {
            "component_id": queue["component_id"],
            "component_name": queue["component_name"],
            "dependency_category": "notice",
            "target_status": "PASS",
            "reason": "Queue validation still gates every downstream lane.",
            "safe_next_action": "Repair the runtime queue blockers before any downstream reduction is credited.",
        }
    return {
        "component_id": "restart_supervisor_timeouts",
        "component_name": "Restart supervisor + bounded timeouts",
        "dependency_category": "route",
        "target_status": "DRY_RUN_PLAN",
        "reason": "The current report stack has already reduced queue/relay review dependency; the next reduction target is the restart/timeouts lane.",
        "safe_next_action": "Draft the restart/timeouts proof plan without touching scheduler, service, or SOS paths.",
    }


def build_operator_dependency_ledger(
    existing_state: dict[str, Any] | None = None,
    *,
    queue: dict[str, Any] | None = None,
    relay_readout: dict[str, Any] | None = None,
    relay_review: dict[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, object]:
    state = _default_inputs(existing_state)
    built_queue = _deepcopy(queue) if isinstance(queue, dict) else build_runtime_execution_queue(state)
    built_relay = _deepcopy(relay_readout) if isinstance(relay_readout, dict) else build_relay_runtime_processor(state, queue=built_queue, now=now)
    built_review = _deepcopy(relay_review) if isinstance(relay_review, dict) else build_relay_dry_run_proof_review(state, relay_readout=built_relay, queue=built_queue, now=now)

    components = [
        _queue_component(built_queue),
        _relay_processor_component(state, built_queue),
        _relay_review_component(state, built_queue, built_relay),
    ]
    scorecard = _scorecard(components)
    operator_dependency_items = []
    ai_os_owned_items = []
    remaining_human_burdens = []
    reduced_burdens = []
    for component in components:
        for item in component["operator_dependency_items"]:
            operator_dependency_items.append(
                {
                    "component_id": component["component_id"],
                    "component_name": component["component_name"],
                    "category": item["category"],
                    "tony": list(item["tony"]),
                    "ai_os": list(item["ai_os"]),
                }
            )
        ai_os_owned_items.extend(
            {
                "component_id": component["component_id"],
                "component_name": component["component_name"],
                "item": item,
            }
            for item in component["ai_os_owned_items"]
        )
        remaining_human_burdens.extend(
            {
                "component_id": component["component_id"],
                "component_name": component["component_name"],
                "burden": burden,
            }
            for burden in component["remaining_human_burdens"]
        )
        reduced_burdens.extend(
            {
                "component_id": component["component_id"],
                "component_name": component["component_name"],
                "reduction": reduction,
            }
            for reduction in component["reduced_burdens"]
        )

    dependency_category_totals = {
        category: sum(
            len([item for item in component["operator_dependency_items"] if item["category"] == category])
            for component in components
        )
        for category in DEPENDENCY_CATEGORIES
    }
    unsafe_autonomy_claim = False
    vacation_mode_complete = False
    next_target = _next_reduction_target(components)
    ledger = {
        "schema": SCHEMA,
        "generated_at_utc": _now(now),
        "mode": "REPORT_ONLY",
        "scope": list(COMPONENT_ORDER),
        "evaluated_components": components,
        "operator_dependency_items": operator_dependency_items,
        "ai_os_owned_items": ai_os_owned_items,
        "remaining_human_burdens": remaining_human_burdens,
        "reduced_burdens": reduced_burdens,
        "autonomy_scorecard": scorecard,
        "dependency_category_totals": dependency_category_totals,
        "next_reduction_target": next_target,
        "unsafe_autonomy_claim": unsafe_autonomy_claim,
        "vacation_mode_complete": vacation_mode_complete,
        "review_status": built_review.get("review_status"),
        "proof_status": built_relay.get("proof_status"),
        "next_lane": built_queue.get("lanes", [{}])[0].get("lane_id") if list(built_queue.get("lanes") or []) else None,
        "proof_chain": list(built_queue.get("proof_chain") or []),
        "blockers": list(built_queue.get("remaining_blockers") or []),
        "human_gates": list(built_queue.get("hard_gate_summary", {}).get("human_only_lanes") or []),
        "validation_status": {
            "runtime_execution_queue": validate_runtime_execution_queue(built_queue).get("status"),
            "relay_runtime_processor": validate_relay_runtime_processor(built_relay).get("status"),
            "relay_dry_run_proof_review": validate_relay_dry_run_proof_review(built_review).get("status"),
        },
        "safe_next_action": (
            "Measure the next reduction target and keep vacation_mode_complete false; "
            "do not treat report-only dependency reduction as runtime autonomy."
        ),
    }
    return ledger


def validate_operator_dependency_ledger(ledger: dict[str, Any]) -> dict[str, object]:
    blockers: list[str] = []
    unsafe_flags: list[str] = []
    checked_fields: list[str] = []

    if not isinstance(ledger, dict):
        return {
            "status": "BLOCK",
            "blockers": ["ledger must be an object"],
            "checked_fields": [],
            "unsafe_flags": ["ledger_not_object"],
        }

    required_fields = [
        "schema",
        "generated_at_utc",
        "mode",
        "scope",
        "evaluated_components",
        "operator_dependency_items",
        "ai_os_owned_items",
        "remaining_human_burdens",
        "reduced_burdens",
        "autonomy_scorecard",
        "next_reduction_target",
        "unsafe_autonomy_claim",
        "vacation_mode_complete",
        "safe_next_action",
    ]
    checked_fields = list(required_fields)
    missing = [field for field in required_fields if field not in ledger]
    if missing:
        blockers.append(f"missing fields: {', '.join(sorted(missing))}")
        unsafe_flags.append("missing_fields")

    if ledger.get("mode") != "REPORT_ONLY":
        blockers.append("mode must be REPORT_ONLY")
        unsafe_flags.append("mode_not_report_only")
    if ledger.get("unsafe_autonomy_claim") is not False:
        blockers.append("unsafe_autonomy_claim must be false")
        unsafe_flags.append("unsafe_autonomy_claim_true")
    if ledger.get("vacation_mode_complete") is True:
        blockers.append("vacation_mode_complete must remain false")
        unsafe_flags.append("vacation_mode_complete_true")

    scorecard = ledger.get("autonomy_scorecard")
    if not isinstance(scorecard, dict):
        blockers.append("autonomy_scorecard must be an object")
        unsafe_flags.append("scorecard_not_object")
    else:
        for key in ["human_required_count", "ai_os_owned_count", "reduced_dependency_count", "remaining_dependency_count", "autonomy_shift"]:
            if key not in scorecard:
                blockers.append(f"autonomy_scorecard missing {key}")
                unsafe_flags.append(f"scorecard_missing_{key}")
        if scorecard.get("autonomy_shift") not in {"NONE", "PARTIAL", "MEANINGFUL"}:
            blockers.append("autonomy_shift must be NONE, PARTIAL, or MEANINGFUL")
            unsafe_flags.append("autonomy_shift_invalid")

    if not isinstance(ledger.get("evaluated_components"), list) or not ledger["evaluated_components"]:
        blockers.append("evaluated_components must be a non-empty list")
        unsafe_flags.append("evaluated_components_invalid")
    else:
        component_ids = [component.get("component_id") for component in ledger["evaluated_components"] if isinstance(component, dict)]
        if component_ids != COMPONENT_ORDER:
            blockers.append("evaluated_components must be in the expected order")
            unsafe_flags.append("component_order_mismatch")
        for component in ledger["evaluated_components"]:
            if not isinstance(component, dict):
                blockers.append("each evaluated component must be an object")
                unsafe_flags.append("component_not_object")
                continue
            for field in [
                "component_id",
                "component_name",
                "dependency_categories",
                "operator_dependency_items",
                "ai_os_owned_items",
                "remaining_human_burdens",
                "reduced_burdens",
                "human_required_count",
                "ai_os_owned_count",
                "reduced_dependency_count",
                "remaining_dependency_count",
                "autonomy_shift",
            ]:
                if field not in component:
                    blockers.append(f"{component.get('component_id', '<unknown>')} missing {field}")
                    unsafe_flags.append(f"component_missing_{field}")

    if not isinstance(ledger.get("operator_dependency_items"), list) or not ledger["operator_dependency_items"]:
        blockers.append("operator_dependency_items must be a non-empty list")
        unsafe_flags.append("operator_dependency_items_invalid")
    else:
        categories_seen = {item.get("category") for item in ledger["operator_dependency_items"] if isinstance(item, dict)}
        if categories_seen != set(DEPENDENCY_CATEGORIES):
            blockers.append("operator_dependency_items must cover all dependency categories")
            unsafe_flags.append("dependency_categories_missing")

    if not isinstance(ledger.get("safe_next_action"), str) or not ledger["safe_next_action"].strip():
        blockers.append("safe_next_action must be a non-empty string")
        unsafe_flags.append("safe_next_action_missing")
    if not isinstance(ledger.get("next_reduction_target"), dict):
        blockers.append("next_reduction_target must be an object")
        unsafe_flags.append("next_reduction_target_invalid")

    status = "PASS" if not blockers else "BLOCK"
    return {
        "status": status,
        "blockers": blockers,
        "checked_fields": checked_fields,
        "unsafe_flags": unsafe_flags,
    }


def summarize_operator_dependency_ledger(ledger: dict[str, Any]) -> dict[str, object]:
    scorecard = ledger.get("autonomy_scorecard") if isinstance(ledger, dict) else {}
    return {
        "status": "OK",
        "schema": ledger.get("schema") if isinstance(ledger, dict) else None,
        "autonomy_shift": scorecard.get("autonomy_shift") if isinstance(scorecard, dict) else None,
        "next_reduction_target": ledger.get("next_reduction_target") if isinstance(ledger, dict) else None,
        "safe_next_action": ledger.get("safe_next_action") if isinstance(ledger, dict) else None,
        "dependency_categories": list(DEPENDENCY_CATEGORIES),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the AI_OS operator dependency ledger (JSON only).")
    parser.add_argument("--state-json", default=None, help="optional JSON string for component state")
    parser.add_argument("--queue-json", default=None, help="optional JSON string with a runtime execution queue")
    parser.add_argument("--relay-json", default=None, help="optional JSON string with a relay processor readout")
    parser.add_argument("--review-json", default=None, help="optional JSON string with a relay proof review readout")
    parser.add_argument("--now", default=None, help="optional ISO-8601 timestamp for deterministic output")
    args = parser.parse_args()

    state = json.loads(args.state_json) if args.state_json else None
    queue = json.loads(args.queue_json) if args.queue_json else None
    relay = json.loads(args.relay_json) if args.relay_json else None
    review = json.loads(args.review_json) if args.review_json else None
    ledger = build_operator_dependency_ledger(state, queue=queue, relay_readout=relay, relay_review=review, now=args.now)
    payload = {
        "ledger": ledger,
        "validation": validate_operator_dependency_ledger(ledger),
        "summary": summarize_operator_dependency_ledger(ledger),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["validation"]["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
