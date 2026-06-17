from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_SELF_IMPROVEMENT_REVIEW_LOOP.v1"
COMPONENT = "self_improvement_review_loop"
MODE = "READ_ONLY_RECOMMENDATIONS_ONLY"
COMPONENT_KEYS = ("readiness", "plan", "dry_run_execution", "apply_gate")
SUCCESS_VERDICTS = {
    "READY_FOR_PLANNING",
    "READY_FOR_DRY_RUN_ONLY",
    "PLAN_READY_DRY_RUN_PREVIEW",
    "DRY_RUN_SIMULATION_COMPLETE",
    "APPLY_REVIEW_READY",
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
EXECUTABLE_TEXT_TERMS = ("codex-only prompt", "ai_os execution token")
EXECUTABLE_TRUE_KEYS = (
    "executable",
    "execution_token_present",
    "codex_prompt_present",
    "executable_packet_emitted",
)
HARD_FALSE_FIELDS = (
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
BLOCKED_ACTIONS = ["APPLY", "worker_launch", "scheduler", "broker_live_trading", "commit_push_merge"]


def build_self_improvement_review_loop(
    outcomes: Mapping[str, Any] | None,
    now_utc: str | None = None,
) -> dict[str, Any]:
    generated_at = now_utc or _utc_now()
    if not isinstance(outcomes, Mapping):
        return _result(
            generated_at_utc=generated_at,
            review_id=_review_id(outcomes),
            verdict="BLOCKED_OUTCOMES_MISSING",
            review_state="BLOCKED",
            outcome_count=0,
            success_count=0,
            blocker_count=1,
            dominant_pattern="outcomes_missing",
            recommendations=[],
            blockers=["outcomes_missing_or_non_object"],
            evidence_inputs=_evidence_inputs(outcomes, []),
            next_safe_action="Provide object-shaped M11-M14 outcome evidence.",
        )

    outcomes_list, malformed_blockers = _collect_outcomes(outcomes)
    review_id = _review_id(outcomes)
    if malformed_blockers:
        return _result(
            generated_at_utc=generated_at,
            review_id=review_id,
            verdict="BLOCKED_OUTCOMES_MALFORMED",
            review_state="BLOCKED",
            outcome_count=len(outcomes_list),
            success_count=0,
            blocker_count=len(malformed_blockers),
            dominant_pattern="malformed_evidence",
            recommendations=[],
            blockers=malformed_blockers,
            evidence_inputs=_evidence_inputs(outcomes, outcomes_list),
            next_safe_action="Provide interpretable object-shaped outcome records.",
        )

    if _contains_executable_content(outcomes):
        return _result(
            generated_at_utc=generated_at,
            review_id=review_id,
            verdict="BLOCKED_EXECUTABLE_CONTENT",
            review_state="BLOCKED",
            outcome_count=len(outcomes_list),
            success_count=0,
            blocker_count=1,
            dominant_pattern="executable_content",
            recommendations=[],
            blockers=["executable_content_detected"],
            evidence_inputs=_evidence_inputs(outcomes, outcomes_list),
            next_safe_action="Remove executable packet, token, prompt, or executable flags before review.",
        )

    if _contains_unsafe_content(outcomes):
        return _result(
            generated_at_utc=generated_at,
            review_id=review_id,
            verdict="BLOCKED_UNSAFE_CONTENT",
            review_state="BLOCKED",
            outcome_count=len(outcomes_list),
            success_count=0,
            blocker_count=1,
            dominant_pattern="unsafe_content",
            recommendations=[],
            blockers=["unsafe_content_detected"],
            evidence_inputs=_evidence_inputs(outcomes, outcomes_list),
            next_safe_action="Stop for safety review before self-improvement recommendations.",
        )

    if _stale_looking(outcomes) or any(_stale_looking(item) for item in outcomes_list):
        return _result(
            generated_at_utc=generated_at,
            review_id=review_id,
            verdict="BLOCKED_OUTCOMES_MALFORMED",
            review_state="BLOCKED",
            outcome_count=len(outcomes_list),
            success_count=0,
            blocker_count=1,
            dominant_pattern="stale_evidence",
            recommendations=[],
            blockers=["outcome_evidence_stale"],
            evidence_inputs=_evidence_inputs(outcomes, outcomes_list),
            next_safe_action="Refresh outcome evidence before review.",
        )

    pattern_counts = _classify_patterns(outcomes_list)
    outcome_count = len(outcomes_list)
    success_count = sum(1 for item in outcomes_list if _verdict(item) in SUCCESS_VERDICTS and not _string_list(item.get("blockers")))
    blocker_count = sum(1 for item in outcomes_list if _is_blocked(item))
    clean_path = outcome_count > 0 and success_count == outcome_count and blocker_count == 0

    if clean_path:
        recommendations = [_recommendation("no_action", "low")]
        return _result(
            generated_at_utc=generated_at,
            review_id=review_id,
            verdict="REVIEW_COMPLETE_NO_ACTION",
            review_state="COMPLETE",
            outcome_count=outcome_count,
            success_count=success_count,
            blocker_count=0,
            dominant_pattern="clean_path",
            recommendations=recommendations,
            blockers=[],
            evidence_inputs=_evidence_inputs(outcomes, outcomes_list),
            next_safe_action="No improvement recommendation is needed from the supplied clean path.",
        )

    recommendations = [_recommendation(pattern, _priority_for(pattern)) for pattern in _recommendation_patterns(pattern_counts)]
    if not recommendations:
        recommendations = [_recommendation("clarify_goal", "medium")]

    dominant_pattern = _dominant_pattern(pattern_counts)
    return _result(
        generated_at_utc=generated_at,
        review_id=review_id,
        verdict="REVIEW_COMPLETE_RECOMMENDATIONS_ONLY",
        review_state="COMPLETE",
        outcome_count=outcome_count,
        success_count=success_count,
        blocker_count=blocker_count,
        dominant_pattern=dominant_pattern,
        recommendations=recommendations,
        blockers=[],
        evidence_inputs=_evidence_inputs(outcomes, outcomes_list),
        next_safe_action="Review recommendations manually; no action is approved by this review loop.",
    )


def _result(
    *,
    generated_at_utc: str,
    review_id: str,
    verdict: str,
    review_state: str,
    outcome_count: int,
    success_count: int,
    blocker_count: int,
    dominant_pattern: str,
    recommendations: list[dict[str, Any]],
    blockers: list[str],
    evidence_inputs: list[dict[str, Any]],
    next_safe_action: str,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": generated_at_utc,
        "component": COMPONENT,
        "mode": MODE,
        "review_id": review_id,
        "verdict": verdict,
        "review_state": review_state,
        "outcome_count": outcome_count,
        "success_count": success_count,
        "blocker_count": blocker_count,
        "dominant_pattern": dominant_pattern,
        "recommendations": recommendations,
        "non_executable_recommendations_only": True,
        "human_approval_required_before_action": True,
        "self_approval_allowed": False,
        "apply_allowed": False,
        "apply_performed": False,
        "commands_executed": False,
        "files_written": False,
        "mutations_performed": False,
        "executable_packet_emitted": False,
        "execution_token_emitted": False,
        "codex_prompt_emitted": False,
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
        "blockers": blockers,
        "evidence_inputs": evidence_inputs,
        "next_safe_action": next_safe_action,
        "safety": {
            "read_only": True,
            "side_effect_free": True,
            "recommendations_only": True,
            "self_approval_allowed": False,
            "commands_executed": False,
            "files_written": False,
            "reports_written": False,
            "runtime_mutation": False,
            "approval_mutation": False,
            "queue_mutation": False,
        },
    }


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _collect_outcomes(outcomes: Mapping[str, Any]) -> tuple[list[Mapping[str, Any]], list[str]]:
    collected: list[Mapping[str, Any]] = []
    malformed: list[str] = []
    for key in COMPONENT_KEYS:
        value = outcomes.get(key)
        if value in (None, "", [], {}):
            continue
        if not isinstance(value, Mapping):
            malformed.append(f"{key}_malformed")
            continue
        collected.append(value)

    history = outcomes.get("history")
    if history not in (None, "", [], {}):
        if not isinstance(history, Sequence) or isinstance(history, (str, bytes, bytearray)):
            malformed.append("history_malformed")
        else:
            for index, item in enumerate(history):
                if not isinstance(item, Mapping):
                    malformed.append(f"history_{index}_malformed")
                else:
                    collected.append(item)

    if not collected and not malformed:
        malformed.append("no_interpretable_outcomes")
    for index, item in enumerate(collected):
        if not _outcome_shape_ok(item):
            malformed.append(f"outcome_{index}_missing_verdict")
    return collected, malformed


def _outcome_shape_ok(item: Mapping[str, Any]) -> bool:
    return any(str(item.get(key) or "").strip() for key in ("verdict", "readiness_state", "plan_state", "execution_state", "gate_state"))


def _classify_patterns(outcomes: list[Mapping[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for item in outcomes:
        text = _outcome_text(item)
        if "security" in text or "sos" in text:
            counts["security_blocker"] += 1
        if "validator" in text:
            counts["validator_blocker"] += 1
        if "scope" in text or "allowed_paths" in text or "forbidden_paths" in text:
            counts["scope_blocker"] += 1
        if "approval" in text or _verdict(item) == "HUMAN_APPROVAL_REQUIRED":
            counts["approval_blocker"] += 1
        if "rollback" in text:
            counts["rollback_blocker"] += 1
        if "missing" in text or "malformed" in text or "evidence" in text:
            counts["evidence_quality_blocker"] += 1
        if "unsafe" in text:
            counts["unsafe_goal_scope"] += 1
    return counts


def _recommendation_patterns(counts: Counter[str]) -> list[str]:
    ordered = (
        "security_blocker",
        "validator_blocker",
        "scope_blocker",
        "approval_blocker",
        "rollback_blocker",
        "evidence_quality_blocker",
        "unsafe_goal_scope",
    )
    return [pattern for pattern in ordered if counts.get(pattern, 0) > 0]


def _dominant_pattern(counts: Counter[str]) -> str:
    patterns = _recommendation_patterns(counts)
    if not patterns:
        return "review_needed"
    return max(patterns, key=lambda pattern: (counts[pattern], -_recommendation_patterns(counts).index(pattern)))


def _recommendation(pattern: str, priority: str) -> dict[str, Any]:
    templates = {
        "security_blocker": (
            "stop_for_security_review",
            "Stop for security review.",
            "Outcome evidence includes security blockers that must be reviewed by a human.",
            "security_review",
        ),
        "validator_blocker": (
            "add_missing_validators",
            "Add missing validator evidence.",
            "Validator blockers mean the next review needs clearer validator coverage.",
            "validator_review",
        ),
        "scope_blocker": (
            "tighten_allowed_paths",
            "Tighten allowed paths.",
            "Scope blockers indicate the path boundary needs clearer allowed and forbidden paths.",
            "scope_review",
        ),
        "approval_blocker": (
            "request_human_approval",
            "Request human approval.",
            "Approval blockers require explicit human approval before future action.",
            "approval_review",
        ),
        "rollback_blocker": (
            "add_rollback_note",
            "Add rollback note.",
            "Rollback blockers require a clear rollback or revert note before review can proceed.",
            "rollback_review",
        ),
        "evidence_quality_blocker": (
            "refresh_readiness_evidence",
            "Refresh readiness evidence.",
            "Missing or malformed evidence prevents reliable self-improvement review.",
            "evidence_review",
        ),
        "unsafe_goal_scope": (
            "clarify_goal",
            "Clarify goal and remove unsafe scope.",
            "Unsafe goal or scope language must be removed before further planning.",
            "goal_review",
        ),
        "clarify_goal": (
            "clarify_goal",
            "Clarify goal.",
            "The outcomes do not prove a specific safe improvement pattern.",
            "goal_review",
        ),
        "no_action": (
            "no_improvement_needed",
            "No improvement needed.",
            "The supplied outcomes show a clean path with no blockers.",
            "no_action",
        ),
    }
    category, summary, rationale, next_step = templates[pattern]
    return {
        "recommendation_id": _stable_id(category, summary),
        "category": category,
        "priority": priority,
        "summary": summary,
        "rationale": rationale,
        "human_approval_required": False if category == "no_improvement_needed" else True,
        "executable": False,
        "allowed_next_step_type": next_step,
        "blocked_actions": list(BLOCKED_ACTIONS),
    }


def _priority_for(pattern: str) -> str:
    if pattern == "security_blocker":
        return "high"
    if pattern in {"validator_blocker", "scope_blocker", "approval_blocker", "rollback_blocker"}:
        return "medium"
    return "low"


def _verdict(item: Mapping[str, Any]) -> str:
    return str(item.get("verdict") or "").strip().upper()


def _is_blocked(item: Mapping[str, Any]) -> bool:
    verdict = _verdict(item)
    return verdict.startswith("BLOCKED") or verdict == "HUMAN_APPROVAL_REQUIRED" or bool(_string_list(item.get("blockers")))


def _outcome_text(item: Mapping[str, Any]) -> str:
    payload = {
        "verdict": item.get("verdict"),
        "state": item.get("readiness_state") or item.get("plan_state") or item.get("execution_state") or item.get("gate_state"),
        "blockers": item.get("blockers"),
        "dominant_pattern": item.get("dominant_pattern"),
        "next_safe_action": item.get("next_safe_action"),
    }
    return json.dumps(payload, sort_keys=True, default=str).lower()


def _contains_unsafe_content(value: Any) -> bool:
    return any(_string_has_term(text, UNSAFE_TERMS) for text in _scan_strings(value))


def _contains_executable_content(value: Any) -> bool:
    if any(_string_has_term(text, EXECUTABLE_TEXT_TERMS) for text in _scan_strings(value)):
        return True

    def walk(item: Any) -> bool:
        if isinstance(item, Mapping):
            for key, value in item.items():
                if str(key) in EXECUTABLE_TRUE_KEYS and value is True:
                    return True
                if walk(value):
                    return True
        elif isinstance(item, Sequence) and not isinstance(item, (str, bytes, bytearray)):
            return any(walk(value) for value in item)
        return False

    return walk(value)


def _string_has_term(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def _scan_strings(value: Any) -> list[str]:
    if isinstance(value, Mapping):
        strings: list[str] = []
        for item in value.values():
            strings.extend(_scan_strings(item))
        return strings
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        strings: list[str] = []
        for item in value:
            strings.extend(_scan_strings(item))
        return strings
    if isinstance(value, str):
        return [value]
    return []


def _stale_looking(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False
    if value.get("stale") is True or value.get("is_stale") is True:
        return True
    for key in ("freshness", "freshness_state", "status"):
        if str(value.get(key) or "").strip().upper() == "STALE":
            return True
    return False


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _review_id(outcomes: Any) -> str:
    digest = hashlib.sha256(json.dumps(_safe_identity(outcomes), sort_keys=True, default=str).encode("utf-8")).hexdigest()[:16]
    return f"review-{digest}"


def _safe_identity(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _safe_identity(item)
            for key, item in value.items()
            if key in (*COMPONENT_KEYS, "history", "schema", "verdict", "blockers", "review_id")
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_safe_identity(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _stable_id(*parts: str) -> str:
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:12]


def _evidence_inputs(outcomes: Any, outcomes_list: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(outcomes, Mapping):
        return [{"name": "outcomes", "status": "missing_or_non_object", "schema": None}]
    inputs: list[dict[str, Any]] = []
    for key in COMPONENT_KEYS:
        value = outcomes.get(key)
        if isinstance(value, Mapping):
            inputs.append({"name": key, "status": "present", "schema": value.get("schema")})
        else:
            inputs.append({"name": key, "status": "missing", "schema": None})
    if "history" in outcomes:
        inputs.append({"name": "history", "status": "present", "schema": None})
    inputs.append({"name": "interpretable_outcomes", "status": str(len(outcomes_list)), "schema": None})
    return inputs


__all__ = ["build_self_improvement_review_loop"]
