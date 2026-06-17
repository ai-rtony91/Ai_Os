"""Pure integration harness for the AI_OS self-autonomy ladder."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from automation.orchestration.autonomy_apply_gate.aios_self_autonomy_apply_gate import (
    build_self_autonomy_apply_gate,
)
from automation.orchestration.autonomy_dry_run_executor.aios_self_autonomy_dry_run_executor import (
    build_self_autonomy_dry_run_execution,
)
from automation.orchestration.autonomy_planner.aios_self_autonomy_planner import (
    build_self_autonomy_plan,
)
from automation.orchestration.autonomy_readiness.aios_self_autonomy_readiness_gate import (
    build_readiness_gate,
)
from automation.orchestration.autonomy_review_loop.aios_self_improvement_review_loop import (
    build_self_improvement_review_loop,
)

SCHEMA = "AIOS_SELF_AUTONOMY_CHAIN_HARNESS.v1"
COMPONENT = "self_autonomy_chain_harness"
MODE = "READ_ONLY_CHAIN_INTEGRATION_HARNESS"

EXECUTABLE_MARKERS = (
    "codex-only prompt",
    "ai_os execution token",
)

EXECUTABLE_TRUE_KEYS = {
    "executable",
    "execution_token_present",
    "codex_prompt_present",
    "executable_packet_emitted",
}

UNSAFE_TERMS = (
    "secret",
    "secrets",
    "credential",
    "credentials",
    "broker",
    "oanda",
    "live trading",
    "live-trading",
    "live order",
    "real order",
    "webhook execution",
    "production",
    "scheduler",
    "daemon",
    "worker launch",
    "dashboard mutation",
    "git add",
    "git commit",
    "git push",
    "commit",
    "push",
    "merge",
    "deployment",
    ".env",
)

HARD_SAFETY_FALSE_FIELDS = (
    "self_approval_allowed",
    "apply_allowed",
    "apply_performed",
    "commands_executed",
    "files_written",
    "mutations_performed",
    "executable_packet_emitted",
    "execution_token_emitted",
    "codex_prompt_emitted",
    "worker_launch_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "broker_allowed",
    "live_trading_allowed",
    "production_allowed",
    "dashboard_mutation_allowed",
    "commit_allowed",
    "push_allowed",
    "merge_allowed",
)

COMPONENTS = (
    "readiness",
    "plan",
    "dry_run_execution",
    "apply_gate",
    "review_loop",
)


def build_self_autonomy_chain_harness(
    seed_evidence: Mapping[str, Any] | None,
    goal: str,
    approval: Mapping[str, Any] | None = None,
    now_utc: str | None = None,
) -> dict[str, Any]:
    """Wire M11 through M15 with injected evidence only."""

    generated_at = now_utc or _utc_now()
    base: dict[str, Any] = {
        "generated_at_utc": generated_at,
        "goal": _string(goal),
    }

    if not isinstance(seed_evidence, Mapping):
        return _result(
            **base,
            chain_id=_chain_id(seed_evidence, goal, approval),
            verdict="BLOCKED_CHAIN_INPUT_MISSING",
            chain_state="BLOCKED",
            blockers=["seed_evidence_missing_or_non_object"],
            next_safe_action="Provide object-shaped fixture evidence before running the chain harness.",
        )

    if _contains_executable_content(seed_evidence) or _contains_executable_content(approval) or _contains_executable_content(
        goal
    ):
        return _result(
            **base,
            chain_id=_chain_id(seed_evidence, goal, approval),
            verdict="BLOCKED_CHAIN_EXECUTABLE_INPUT",
            chain_state="BLOCKED",
            blockers=["executable_input_detected"],
            next_safe_action="Remove executable prompt markers and token-bearing fields before review.",
        )

    if _contains_unsafe_terms(seed_evidence) or _contains_unsafe_terms(approval) or _contains_unsafe_terms(goal):
        return _result(
            **base,
            chain_id=_chain_id(seed_evidence, goal, approval),
            verdict="BLOCKED_CHAIN_UNSAFE_INPUT",
            chain_state="BLOCKED",
            blockers=["unsafe_input_scope_detected"],
            next_safe_action="Remove unsafe scope terms before running the chain harness.",
        )

    readiness_evidence = seed_evidence.get("readiness_evidence")
    planner_constraints = seed_evidence.get("planner_constraints")
    if not isinstance(readiness_evidence, Mapping) or not isinstance(planner_constraints, Mapping):
        return _result(
            **base,
            chain_id=_chain_id(seed_evidence, goal, approval),
            verdict="BLOCKED_CHAIN_INPUT_MISSING",
            chain_state="BLOCKED",
            blockers=["seed_evidence_missing_required_component_inputs"],
            next_safe_action="Provide readiness_evidence and planner_constraints fixture objects.",
        )

    readiness = build_readiness_gate(readiness_evidence, now_utc=generated_at)
    if _is_blocked_verdict(readiness):
        return _component_failure(
            base=base,
            chain_id=_chain_id(seed_evidence, goal, approval),
            first_blocking_component="readiness",
            readiness=readiness,
            blockers=_blockers_from(readiness, "readiness_blocked"),
        )

    plan = build_self_autonomy_plan(
        goal,
        readiness,
        constraints=planner_constraints,
        now_utc=generated_at,
    )
    if _is_blocked_verdict(plan):
        return _component_failure(
            base=base,
            chain_id=_chain_id(seed_evidence, goal, approval),
            first_blocking_component="plan",
            readiness=readiness,
            plan=plan,
            blockers=_blockers_from(plan, "plan_blocked"),
        )

    dry_run_execution = build_self_autonomy_dry_run_execution(plan, now_utc=generated_at)
    dry_run_execution = _with_rollback_note(dry_run_execution, plan)
    if _is_blocked_verdict(dry_run_execution):
        return _component_failure(
            base=base,
            chain_id=_chain_id(seed_evidence, goal, approval),
            first_blocking_component="dry_run_execution",
            readiness=readiness,
            plan=plan,
            dry_run_execution=dry_run_execution,
            blockers=_blockers_from(dry_run_execution, "dry_run_execution_blocked"),
        )

    apply_gate = build_self_autonomy_apply_gate(
        dry_run_execution,
        approval=approval,
        now_utc=generated_at,
    )
    if _is_blocked_verdict(apply_gate):
        return _component_failure(
            base=base,
            chain_id=_chain_id(seed_evidence, goal, approval),
            first_blocking_component="apply_gate",
            readiness=readiness,
            plan=plan,
            dry_run_execution=dry_run_execution,
            apply_gate=apply_gate,
            blockers=_blockers_from(apply_gate, "apply_gate_blocked"),
        )

    review_loop = build_self_improvement_review_loop(
        {
            "readiness": readiness,
            "plan": plan,
            "dry_run_execution": dry_run_execution,
            "apply_gate": apply_gate,
        },
        now_utc=generated_at,
    )
    if _is_blocked_verdict(review_loop):
        return _component_failure(
            base=base,
            chain_id=_chain_id(seed_evidence, goal, approval),
            first_blocking_component="review_loop",
            readiness=readiness,
            plan=plan,
            dry_run_execution=dry_run_execution,
            apply_gate=apply_gate,
            review_loop=review_loop,
            blockers=_blockers_from(review_loop, "review_loop_blocked"),
        )

    apply_gate_verdict = _verdict(apply_gate)
    review_loop_verdict = _verdict(review_loop)
    if apply_gate_verdict == "HUMAN_APPROVAL_REQUIRED" and review_loop_verdict == "REVIEW_COMPLETE_RECOMMENDATIONS_ONLY":
        verdict = "CHAIN_HUMAN_APPROVAL_REQUIRED"
        chain_state = "WAITING_FOR_HUMAN_APPROVAL"
        next_safe_action = "Request explicit human approval before any future APPLY review."
    elif apply_gate_verdict == "APPLY_REVIEW_READY" and review_loop_verdict in {
        "REVIEW_COMPLETE_RECOMMENDATIONS_ONLY",
        "REVIEW_COMPLETE_NO_ACTION",
    }:
        verdict = "CHAIN_APPLY_REVIEW_READY"
        chain_state = "HUMAN_APPLY_REVIEW_READY"
        next_safe_action = "Prepare a separate human-reviewed APPLY packet if Anthony approves."
    elif review_loop_verdict in {"REVIEW_COMPLETE_RECOMMENDATIONS_ONLY", "REVIEW_COMPLETE_NO_ACTION"}:
        verdict = "CHAIN_REVIEW_COMPLETE"
        chain_state = "REVIEW_COMPLETE"
        next_safe_action = "Review non-executable recommendations before choosing any future action."
    else:
        verdict = "BLOCKED_CHAIN_NO_SAFE_OUTCOME"
        chain_state = "BLOCKED"
        next_safe_action = "Stop until a safe final chain outcome is provable."

    blockers = [] if not verdict.startswith("BLOCKED") else ["safe_chain_outcome_not_provable"]
    return _result(
        **base,
        chain_id=_chain_id(seed_evidence, goal, approval),
        verdict=verdict,
        chain_state=chain_state,
        readiness=readiness,
        plan=plan,
        dry_run_execution=dry_run_execution,
        apply_gate=apply_gate,
        review_loop=review_loop,
        blockers=blockers,
        human_approval_required=bool(apply_gate.get("human_approval_required", True)),
        explicit_human_approval_present=bool(apply_gate.get("explicit_human_approval_present", False)),
        apply_review_ready=verdict == "CHAIN_APPLY_REVIEW_READY",
        next_safe_action=next_safe_action,
    )


def _component_failure(
    *,
    base: Mapping[str, Any],
    chain_id: str,
    first_blocking_component: str,
    blockers: list[str],
    readiness: Mapping[str, Any] | None = None,
    plan: Mapping[str, Any] | None = None,
    dry_run_execution: Mapping[str, Any] | None = None,
    apply_gate: Mapping[str, Any] | None = None,
    review_loop: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return _result(
        **dict(base),
        chain_id=chain_id,
        verdict="BLOCKED_CHAIN_COMPONENT_FAILURE",
        chain_state="BLOCKED",
        first_blocking_component=first_blocking_component,
        readiness=readiness,
        plan=plan,
        dry_run_execution=dry_run_execution,
        apply_gate=apply_gate,
        review_loop=review_loop,
        blockers=blockers,
        next_safe_action=f"Stop and review the {first_blocking_component} component evidence.",
    )


def _result(
    *,
    generated_at_utc: str,
    goal: str,
    chain_id: str,
    verdict: str,
    chain_state: str,
    readiness: Mapping[str, Any] | None = None,
    plan: Mapping[str, Any] | None = None,
    dry_run_execution: Mapping[str, Any] | None = None,
    apply_gate: Mapping[str, Any] | None = None,
    review_loop: Mapping[str, Any] | None = None,
    first_blocking_component: str | None = None,
    blockers: list[str] | None = None,
    human_approval_required: bool = True,
    explicit_human_approval_present: bool = False,
    apply_review_ready: bool = False,
    next_safe_action: str = "Stop until one safe next action is provable.",
) -> dict[str, Any]:
    components = {
        "readiness": readiness or _not_run("readiness"),
        "plan": plan or _not_run("plan"),
        "dry_run_execution": dry_run_execution or _not_run("dry_run_execution"),
        "apply_gate": apply_gate or _not_run("apply_gate"),
        "review_loop": review_loop or _not_run("review_loop"),
    }
    output: dict[str, Any] = {
        "schema": SCHEMA,
        "generated_at_utc": generated_at_utc,
        "component": COMPONENT,
        "mode": MODE,
        "chain_id": chain_id,
        "verdict": verdict,
        "chain_state": chain_state,
        "goal": goal,
        "first_blocking_component": first_blocking_component,
        **components,
        "component_verdicts": {name: _verdict(component) for name, component in components.items()},
        "component_states": {name: _state_for(name, component) for name, component in components.items()},
        "human_approval_required": human_approval_required,
        "explicit_human_approval_present": explicit_human_approval_present,
        "apply_review_ready": apply_review_ready,
        "blockers": list(blockers or []),
        "evidence_inputs": _evidence_inputs(components),
        "next_safe_action": next_safe_action,
        "safety": _safety(),
    }
    output.update({field: False for field in HARD_SAFETY_FALSE_FIELDS})
    return output


def _with_rollback_note(
    dry_run_execution: Mapping[str, Any],
    plan: Mapping[str, Any],
) -> dict[str, Any]:
    output = dict(dry_run_execution)
    if output.get("rollback_note"):
        return output
    preview = plan.get("non_executable_packet_preview")
    if isinstance(preview, Mapping):
        rollback_note = preview.get("rollback_note")
        if isinstance(rollback_note, str) and rollback_note.strip():
            output["rollback_note"] = rollback_note
    return output


def _contains_executable_content(value: Any) -> bool:
    for item in _walk_values(value):
        if isinstance(item, str) and any(marker in item.lower() for marker in EXECUTABLE_MARKERS):
            return True
    return _contains_true_key(value, EXECUTABLE_TRUE_KEYS)


def _contains_unsafe_terms(value: Any) -> bool:
    for item in _walk_values(value):
        if isinstance(item, str) and any(term in item.lower() for term in UNSAFE_TERMS):
            return True
    return False


def _walk_values(value: Any) -> list[Any]:
    if isinstance(value, Mapping):
        values: list[Any] = []
        for child in value.values():
            values.extend(_walk_values(child))
        return values
    if isinstance(value, (list, tuple, set)):
        values = []
        for child in value:
            values.extend(_walk_values(child))
        return values
    return [value]


def _contains_true_key(value: Any, names: set[str]) -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).lower() in names and child is True:
                return True
            if _contains_true_key(child, names):
                return True
    elif isinstance(value, (list, tuple, set)):
        return any(_contains_true_key(child, names) for child in value)
    return False


def _is_blocked_verdict(component: Mapping[str, Any]) -> bool:
    return _verdict(component).startswith("BLOCKED")


def _blockers_from(component: Mapping[str, Any], fallback: str) -> list[str]:
    blockers = component.get("blockers")
    if isinstance(blockers, list):
        cleaned = [str(item) for item in blockers if item not in (None, "", [], {})]
        return cleaned or [fallback]
    return [fallback]


def _verdict(component: Mapping[str, Any]) -> str:
    verdict = component.get("verdict")
    return str(verdict) if verdict not in (None, "", [], {}) else "UNKNOWN"


def _state_for(name: str, component: Mapping[str, Any]) -> str:
    field = {
        "readiness": "readiness_state",
        "plan": "plan_state",
        "dry_run_execution": "execution_state",
        "apply_gate": "gate_state",
        "review_loop": "review_state",
    }[name]
    state = component.get(field) or component.get("state")
    return str(state) if state not in (None, "", [], {}) else "UNKNOWN"


def _not_run(name: str) -> dict[str, Any]:
    return {
        "schema": "",
        "component": name,
        "verdict": "NOT_RUN",
        "state": "NOT_RUN",
        "blockers": [],
    }


def _evidence_inputs(components: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    inputs: list[dict[str, Any]] = []
    for name in COMPONENTS:
        component = components[name]
        inputs.append(
            {
                "name": name,
                "schema": _string(component.get("schema")),
                "verdict": _verdict(component),
                "state": _state_for(name, component),
            }
        )
    return inputs


def _safety() -> dict[str, Any]:
    safety = {
        "read_only": True,
        "side_effect_free": True,
        "injected_evidence_only": True,
        "commands_executed": False,
        "files_written": False,
        "mutations_performed": False,
        "self_approval_allowed": False,
    }
    safety.update({field: False for field in HARD_SAFETY_FALSE_FIELDS if field not in safety})
    return safety


def _chain_id(
    seed_evidence: Mapping[str, Any] | None,
    goal: str,
    approval: Mapping[str, Any] | None,
) -> str:
    payload = {
        "goal": goal,
        "seed_evidence": _jsonable(seed_evidence),
        "approval": _jsonable(approval),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return "chain-" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(child) for key, child in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_jsonable(child) for child in value]
    if isinstance(value, set):
        return sorted(_jsonable(child) for child in value)
    return value


def _string(value: Any) -> str:
    return value if isinstance(value, str) else str(value)


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
