from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_SELF_AUTONOMY_PLAN.v1"
READINESS_SCHEMA = "AIOS_SELF_AUTONOMY_READINESS_GATE.v1"
COMPONENT = "self_autonomy_planner"
MODE = "READ_ONLY_NON_EXECUTABLE_PLANNER"

READY_VERDICTS = {"READY_FOR_PLANNING", "READY_FOR_DRY_RUN_ONLY"}
BLOCKED_READINESS_VERDICTS = {
    "BLOCKED_APPROVAL",
    "BLOCKED_SECURITY",
    "BLOCKED_VALIDATOR",
    "BLOCKED_DIRTY_TREE",
    "BLOCKED_EVIDENCE_MISSING",
    "BLOCKED_NO_SAFE_NEXT_ACTION",
}
LOW_RISK = {"LOW", "GREEN"}
UNSAFE_GOAL_TERMS = (
    "secret",
    "secrets",
    "credential",
    "credentials",
    "broker",
    "oanda",
    "live trading",
    "live-trading",
    "live order",
    "live orders",
    "real order",
    "real orders",
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
HARD_FALSE_FIELDS = (
    "apply_allowed",
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
FINAL_REPORT_FIELDS = (
    "SUMMARY",
    "FILES INSPECTED",
    "FINDINGS",
    "VALIDATORS",
    "NEXT SAFE ACTION",
    "STATUS",
)


def build_self_autonomy_plan(
    goal: str,
    readiness_gate: Mapping[str, Any] | None,
    constraints: Mapping[str, Any] | None = None,
    now_utc: str | None = None,
) -> dict[str, Any]:
    generated_at = now_utc or _utc_now()
    normalized_goal = _normalize_goal(goal)
    inherited_verdict = _text(readiness_gate.get("verdict")) if isinstance(readiness_gate, Mapping) else "MISSING"
    inherited_state = _text(readiness_gate.get("readiness_state")) if isinstance(readiness_gate, Mapping) else "MISSING"
    inherited_blockers = _string_list(readiness_gate.get("blockers")) if isinstance(readiness_gate, Mapping) else []
    risk_level = _risk_level(readiness_gate)
    plan_id = _plan_id(normalized_goal, readiness_gate, constraints)

    if not normalized_goal:
        return _result(
            generated_at_utc=generated_at,
            goal=str(goal or ""),
            normalized_goal=normalized_goal,
            plan_id=plan_id,
            verdict="BLOCKED_GOAL_MISSING",
            plan_state="BLOCKED",
            inherited_readiness_verdict=inherited_verdict,
            inherited_readiness_state=inherited_state,
            risk_level=risk_level,
            blockers=["goal_missing"],
            evidence_inputs=_evidence_inputs(readiness_gate, constraints),
            next_safe_action="Provide a non-empty human goal before planning.",
        )

    if _goal_is_unsafe(normalized_goal):
        return _result(
            generated_at_utc=generated_at,
            goal=str(goal or ""),
            normalized_goal=normalized_goal,
            plan_id=plan_id,
            verdict="BLOCKED_GOAL_UNSAFE",
            plan_state="BLOCKED",
            inherited_readiness_verdict=inherited_verdict,
            inherited_readiness_state=inherited_state,
            risk_level=risk_level,
            blockers=["unsafe_goal_scope"],
            evidence_inputs=_evidence_inputs(readiness_gate, constraints),
            next_safe_action="Remove unsafe scope before creating a non-executable plan preview.",
        )

    if not _readiness_shape_ok(readiness_gate):
        return _result(
            generated_at_utc=generated_at,
            goal=str(goal or ""),
            normalized_goal=normalized_goal,
            plan_id=plan_id,
            verdict="BLOCKED_READINESS_MISSING",
            plan_state="BLOCKED",
            inherited_readiness_verdict=inherited_verdict,
            inherited_readiness_state=inherited_state,
            risk_level=risk_level,
            blockers=["readiness_missing_or_malformed"],
            evidence_inputs=_evidence_inputs(readiness_gate, constraints),
            next_safe_action="Provide a valid M11 readiness gate payload.",
        )

    if _stale_looking(readiness_gate):
        return _result(
            generated_at_utc=generated_at,
            goal=str(goal or ""),
            normalized_goal=normalized_goal,
            plan_id=plan_id,
            verdict="BLOCKED_READINESS_MISSING",
            plan_state="BLOCKED",
            inherited_readiness_verdict=inherited_verdict,
            inherited_readiness_state=inherited_state,
            risk_level=risk_level,
            blockers=_dedupe([*inherited_blockers, "readiness_stale"]),
            evidence_inputs=_evidence_inputs(readiness_gate, constraints),
            next_safe_action="Refresh readiness evidence before planning.",
        )

    if readiness_gate.get("apply_review_allowed") is True or inherited_verdict == "APPLY_REVIEW_REQUIRED":
        return _result(
            generated_at_utc=generated_at,
            goal=str(goal or ""),
            normalized_goal=normalized_goal,
            plan_id=plan_id,
            verdict="BLOCKED_APPLY_REVIEW_NOT_PLANNER_SCOPE",
            plan_state="BLOCKED",
            inherited_readiness_verdict=inherited_verdict,
            inherited_readiness_state=inherited_state,
            risk_level=risk_level,
            blockers=_dedupe([*inherited_blockers, "apply_review_not_planner_scope"]),
            evidence_inputs=_evidence_inputs(readiness_gate, constraints),
            next_safe_action="Route APPLY review outside the self-autonomy planner.",
        )

    planning_ready = readiness_gate.get("planning_allowed") is True or readiness_gate.get("dry_run_allowed") is True
    if inherited_verdict in BLOCKED_READINESS_VERDICTS or inherited_verdict not in READY_VERDICTS or not planning_ready:
        return _result(
            generated_at_utc=generated_at,
            goal=str(goal or ""),
            normalized_goal=normalized_goal,
            plan_id=plan_id,
            verdict="BLOCKED_READINESS_NOT_READY",
            plan_state="BLOCKED",
            inherited_readiness_verdict=inherited_verdict,
            inherited_readiness_state=inherited_state,
            risk_level=risk_level,
            blockers=_dedupe(inherited_blockers or ["readiness_not_ready"]),
            evidence_inputs=_evidence_inputs(readiness_gate, constraints),
            next_safe_action="Resolve inherited M11 readiness blockers before planning.",
        )

    if risk_level not in LOW_RISK:
        return _result(
            generated_at_utc=generated_at,
            goal=str(goal or ""),
            normalized_goal=normalized_goal,
            plan_id=plan_id,
            verdict="BLOCKED_NO_SAFE_PLAN",
            plan_state="BLOCKED",
            inherited_readiness_verdict=inherited_verdict,
            inherited_readiness_state=inherited_state,
            risk_level=risk_level,
            blockers=_dedupe([*inherited_blockers, "risk_not_low_enough"]),
            evidence_inputs=_evidence_inputs(readiness_gate, constraints),
            next_safe_action="Lower or clarify risk before creating a plan preview.",
        )

    allowed_paths = _known_list("allowed_paths", readiness_gate, constraints)
    forbidden_paths = _known_list("forbidden_paths", readiness_gate, constraints)
    validator_chain = _known_list("validator_chain", readiness_gate, constraints)
    scope_blockers = []
    if not allowed_paths:
        scope_blockers.append("allowed_paths_unknown")
    if not forbidden_paths:
        scope_blockers.append("forbidden_paths_unknown")
    if not validator_chain:
        scope_blockers.append("validators_unknown")
    if scope_blockers:
        return _result(
            generated_at_utc=generated_at,
            goal=str(goal or ""),
            normalized_goal=normalized_goal,
            plan_id=plan_id,
            verdict="BLOCKED_SCOPE_UNKNOWN",
            plan_state="BLOCKED",
            inherited_readiness_verdict=inherited_verdict,
            inherited_readiness_state=inherited_state,
            risk_level=risk_level,
            blockers=_dedupe([*inherited_blockers, *scope_blockers]),
            evidence_inputs=_evidence_inputs(readiness_gate, constraints),
            next_safe_action="Provide allowed paths, forbidden paths, and validators before preview planning.",
        )

    preview = _preview(
        normalized_goal=normalized_goal,
        plan_id=plan_id,
        allowed_paths=allowed_paths,
        forbidden_paths=forbidden_paths,
        validator_chain=validator_chain,
        constraints=constraints,
    )
    return _result(
        generated_at_utc=generated_at,
        goal=str(goal or ""),
        normalized_goal=normalized_goal,
        plan_id=plan_id,
        verdict="PLAN_READY_DRY_RUN_PREVIEW",
        plan_state="DRY_RUN_PREVIEW_READY",
        inherited_readiness_verdict=inherited_verdict,
        inherited_readiness_state=inherited_state,
        risk_level=risk_level,
        blockers=[],
        evidence_inputs=_evidence_inputs(readiness_gate, constraints),
        next_safe_action="Human review is required before turning this preview into an executable packet.",
        planning_allowed=True,
        dry_run_preview_allowed=True,
        non_executable_packet_preview=preview,
    )


def _result(
    *,
    generated_at_utc: str,
    goal: str,
    normalized_goal: str,
    plan_id: str,
    verdict: str,
    plan_state: str,
    inherited_readiness_verdict: str,
    inherited_readiness_state: str,
    risk_level: str,
    blockers: list[str],
    evidence_inputs: list[dict[str, Any]],
    next_safe_action: str,
    planning_allowed: bool = False,
    dry_run_preview_allowed: bool = False,
    non_executable_packet_preview: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "generated_at_utc": generated_at_utc,
        "component": COMPONENT,
        "mode": MODE,
        "goal": goal,
        "normalized_goal": normalized_goal,
        "plan_id": plan_id,
        "verdict": verdict,
        "plan_state": plan_state,
        "inherited_readiness_verdict": inherited_readiness_verdict,
        "inherited_readiness_state": inherited_readiness_state,
        "planning_allowed": planning_allowed,
        "dry_run_preview_allowed": dry_run_preview_allowed,
        "apply_preview_allowed": False,
        "apply_allowed": False,
        "worker_launch_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_allowed": False,
        "live_trading_allowed": False,
        "production_allowed": False,
        "dashboard_mutation_allowed": False,
        "commit_allowed": False,
        "push_allowed": False,
        "merge_allowed": False,
        "risk_level": risk_level,
        "blockers": blockers,
        "required_human_approval": True,
        "non_executable_packet_preview": non_executable_packet_preview,
        "evidence_inputs": evidence_inputs,
        "next_safe_action": next_safe_action,
        "safety": {
            "read_only": True,
            "side_effect_free": True,
            "commands_executed": False,
            "files_written": False,
            "runtime_mutation": False,
            "approval_mutation": False,
            "queue_mutation": False,
            "executable_packet_emitted": False,
            "execution_token_emitted": False,
            "codex_prompt_emitted": False,
        },
    }
    return payload


def _preview(
    *,
    normalized_goal: str,
    plan_id: str,
    allowed_paths: list[str],
    forbidden_paths: list[str],
    validator_chain: list[str],
    constraints: Mapping[str, Any] | None,
) -> dict[str, Any]:
    return {
        "executable": False,
        "execution_token_present": False,
        "codex_prompt_present": False,
        "mode": "DRY_RUN",
        "lane": "DRY_RUN",
        "packet_id_suggestion": f"AIOS-M12-PLAN-PREVIEW-{plan_id[-10:].upper()}",
        "mission_summary": normalized_goal,
        "allowed_paths": allowed_paths,
        "forbidden_paths": forbidden_paths,
        "validator_chain": validator_chain,
        "stop_point": _text(_mapping_value(constraints, "stop_point"))
        or "Stop after DRY_RUN report; do not edit, commit, push, launch, or mutate runtime.",
        "rollback_note": _text(_mapping_value(constraints, "rollback_note"))
        or "No mutation is allowed in this preview; rollback is not applicable.",
        "final_report_fields": _string_list(_mapping_value(constraints, "final_report_fields")) or list(FINAL_REPORT_FIELDS),
        "protected_actions": {
            "git_add": False,
            "git_commit": False,
            "git_push": False,
            "pr_create": False,
            "merge": False,
            "scheduler_activation": False,
            "worker_launch": False,
            "runtime_mutation": False,
            "broker_or_live_trading": False,
        },
        "human_approval_required_before_execution": True,
    }


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_goal(goal: str) -> str:
    return " ".join(str(goal or "").strip().split())


def _goal_is_unsafe(normalized_goal: str) -> bool:
    lowered = normalized_goal.lower()
    return any(term in lowered for term in UNSAFE_GOAL_TERMS)


def _readiness_shape_ok(readiness_gate: Any) -> bool:
    return (
        isinstance(readiness_gate, Mapping)
        and readiness_gate.get("schema") == READINESS_SCHEMA
        and isinstance(readiness_gate.get("verdict"), str)
        and isinstance(readiness_gate.get("readiness_state"), str)
    )


def _stale_looking(readiness_gate: Mapping[str, Any]) -> bool:
    if readiness_gate.get("stale") is True or readiness_gate.get("is_stale") is True:
        return True
    for key in ("freshness", "freshness_state", "status"):
        if str(readiness_gate.get(key) or "").strip().upper() == "STALE":
            return True
    return False


def _risk_level(readiness_gate: Any) -> str:
    if not isinstance(readiness_gate, Mapping):
        return "UNKNOWN"
    value = str(readiness_gate.get("risk_level") or "UNKNOWN").strip().upper()
    if value in {"LOW", "GREEN", "MEDIUM", "HIGH", "BLOCKED"}:
        return value
    return "UNKNOWN"


def _known_list(name: str, readiness_gate: Mapping[str, Any], constraints: Mapping[str, Any] | None) -> list[str]:
    candidates: list[Any] = []
    if isinstance(constraints, Mapping):
        candidates.extend([constraints.get(name), constraints.get(_alternate_name(name))])
    candidates.extend([readiness_gate.get(name), readiness_gate.get(_alternate_name(name))])
    preview = readiness_gate.get("non_executable_packet_preview")
    if isinstance(preview, Mapping):
        candidates.extend([preview.get(name), preview.get(_alternate_name(name))])

    for candidate in candidates:
        values = _string_list(candidate)
        if values:
            return values
    return []


def _alternate_name(name: str) -> str:
    if name == "validator_chain":
        return "validators"
    if name == "allowed_paths":
        return "files_allowed"
    if name == "forbidden_paths":
        return "files_forbidden"
    return name


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _mapping_value(value: Mapping[str, Any] | None, key: str) -> Any:
    if not isinstance(value, Mapping):
        return None
    return value.get(key)


def _evidence_inputs(readiness_gate: Any, constraints: Any) -> list[dict[str, Any]]:
    return [
        {
            "name": "readiness_gate",
            "status": "present" if isinstance(readiness_gate, Mapping) else "missing_or_malformed",
            "schema": readiness_gate.get("schema") if isinstance(readiness_gate, Mapping) else None,
        },
        {
            "name": "constraints",
            "status": "present" if isinstance(constraints, Mapping) else "missing",
            "schema": constraints.get("schema") if isinstance(constraints, Mapping) else None,
        },
    ]


def _plan_id(normalized_goal: str, readiness_gate: Any, constraints: Any) -> str:
    seed = {
        "goal": normalized_goal,
        "readiness_verdict": readiness_gate.get("verdict") if isinstance(readiness_gate, Mapping) else "MISSING",
        "readiness_state": readiness_gate.get("readiness_state") if isinstance(readiness_gate, Mapping) else "MISSING",
        "constraints": constraints if isinstance(constraints, Mapping) else {},
    }
    digest = hashlib.sha256(json.dumps(seed, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:16]
    return f"plan-{digest}"


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


__all__ = ["build_self_autonomy_plan"]
