from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_SELF_AUTONOMY_READINESS_GATE.v1"
COMPONENT = "self_autonomy_readiness_gate"
MODE = "READ_ONLY_EVIDENCE_AGGREGATE"

CORE_EVIDENCE = ("task", "security", "dirty_tree", "validators", "continuation", "governor")
READ_MODES = {"READ_ONLY", "DRY_RUN"}
APPLY_MODES = {"APPLY", "APPLY_CODE_SAFE", "APPLY_DOCS_ONLY", "APPLY_TESTS_ONLY"}
LOW_RISK = {"LOW", "GREEN"}
VALIDATOR_PASS = {"PASS", "PASSED", "OK", "SUCCESS", "GREEN"}
VALIDATOR_BLOCK = {"FAIL", "FAILED", "ERROR", "BLOCKED", "UNKNOWN", "MALFORMED", "MISSING"}
SECURITY_BLOCK = {"REVIEW_REQUIRED", "STOP", "SOS", "BLOCKED", "FAIL"}
DIRTY_BLOCK = {
    "PROTECTED_AUTHORITY_DIRTY",
    "SECURITY_SOS_DIRTY",
    "UNKNOWN_DIRTY",
    "REVIEW_REQUIRED_DIRTY",
    "UNSAFE_DIRTY",
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
    "live orders",
    "real order",
    "real orders",
    "webhook execution",
    "production",
    "scheduler",
    "daemon",
    "worker launch",
    "dashboard mutation",
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


def build_readiness_gate(evidence: Mapping[str, Any] | None = None, now_utc: str | None = None) -> dict[str, Any]:
    generated_at = now_utc or _utc_now()
    evidence_inputs = _evidence_inputs(evidence)
    blockers: list[str] = []

    if not isinstance(evidence, Mapping):
        blockers.append("evidence_missing_or_non_object")
        return _result(
            generated_at_utc=generated_at,
            verdict="BLOCKED_EVIDENCE_MISSING",
            readiness_state="BLOCKED",
            evidence_inputs=evidence_inputs,
            blockers=blockers,
            next_safe_action="Provide object-shaped readiness evidence from existing gates.",
        )

    core = {name: evidence.get(name) for name in CORE_EVIDENCE}
    missing = [
        name
        for name, value in core.items()
        if value in (None, "") or (name != "validators" and value in ([], {}))
    ]
    malformed = [name for name, value in core.items() if value not in (None, "", [], {}) and not _core_shape_ok(name, value)]
    if missing:
        blockers.extend(f"{name}_missing" for name in missing)
    if malformed:
        blockers.extend(f"{name}_malformed" for name in malformed)

    task = core["task"] if isinstance(core["task"], Mapping) else {}
    security = core["security"] if isinstance(core["security"], Mapping) else {}
    dirty_tree = core["dirty_tree"] if isinstance(core["dirty_tree"], Mapping) else {}
    continuation = core["continuation"] if isinstance(core["continuation"], Mapping) else {}
    governor = core["governor"] if isinstance(core["governor"], Mapping) else {}
    validators = core["validators"]

    stale_inputs = [name for name, value in core.items() if _is_stale(value)]
    if stale_inputs:
        blockers.extend(f"{name}_stale" for name in stale_inputs)

    positive_authority = _positive_authority(evidence)
    if positive_authority:
        blockers.extend(f"{field}_unsafe_true" for field in positive_authority)

    scope_mode = _scope_mode(task, governor, continuation)
    protected_requested = _protected_action_requested(task, governor, scope_mode)
    goal_clear = _goal_clear(task, governor)
    allowed_files_known = _non_empty_list(_first_present(task.get("allowed_files"), _scope_list(governor, "files_allowed")))
    forbidden_files_known = _non_empty_list(
        _first_present(task.get("forbidden_files"), _scope_list(governor, "files_forbidden"))
    )
    validators_known, validator_blockers = _validator_state(validators)
    if validator_blockers:
        blockers.extend(validator_blockers)

    risk_level = _risk_level(task, governor)
    risk_low_enough = risk_level in LOW_RISK
    rollback_path_known = _rollback_path_known(task, scope_mode)
    security_blocked = _security_blocked(security) or _contains_unsafe_scope(evidence) or bool(positive_authority)
    dirty_blocked = _dirty_tree_blocked(dirty_tree)
    approval_required = protected_requested or _bool_from_sources(task, governor, "approval_required")
    explicit_approval_present = _explicit_approval_present(evidence.get("approval"))
    dry_run_supported = _dry_run_supported(continuation, governor, scope_mode)

    if security_blocked:
        blockers.append("unsafe_scope_or_security_blocker")
    if dirty_blocked:
        blockers.append("dirty_tree_not_safe")
    if protected_requested and not rollback_path_known:
        blockers.append("rollback_path_missing")
    if not goal_clear:
        blockers.append("goal_not_clear")
    if not allowed_files_known:
        blockers.append("allowed_files_unknown")
    if not forbidden_files_known:
        blockers.append("forbidden_files_unknown")
    if not risk_low_enough:
        blockers.append("risk_not_low_enough")

    planning_safe = (
        goal_clear
        and allowed_files_known
        and forbidden_files_known
        and validators_known
        and risk_low_enough
        and rollback_path_known
        and not security_blocked
        and not dirty_blocked
    )

    if missing or malformed or stale_inputs:
        verdict = "BLOCKED_EVIDENCE_MISSING"
        readiness_state = "BLOCKED"
        next_safe_action = "Provide fresh object-shaped evidence for all core gates."
    elif security_blocked:
        verdict = "BLOCKED_SECURITY"
        readiness_state = "BLOCKED"
        next_safe_action = "Remove unsafe scope and run security review before continuing."
    elif not validators_known:
        verdict = "BLOCKED_VALIDATOR"
        readiness_state = "BLOCKED"
        next_safe_action = "Provide passing validator evidence before continuing."
    elif dirty_blocked:
        verdict = "BLOCKED_DIRTY_TREE"
        readiness_state = "BLOCKED"
        next_safe_action = "Review dirty-tree evidence before any continuation."
    elif protected_requested and not rollback_path_known:
        verdict = "BLOCKED_NO_SAFE_NEXT_ACTION"
        readiness_state = "BLOCKED"
        next_safe_action = "Add a rollback or revert path before APPLY review."
    elif approval_required and not explicit_approval_present:
        verdict = "BLOCKED_APPROVAL"
        readiness_state = "BLOCKED"
        next_safe_action = "Obtain explicit human approval before APPLY review."
    elif protected_requested and planning_safe:
        verdict = "APPLY_REVIEW_REQUIRED"
        readiness_state = "APPLY_REVIEW"
        next_safe_action = "Route the packet for human APPLY review; do not execute."
    elif planning_safe and dry_run_supported:
        verdict = "READY_FOR_DRY_RUN_ONLY"
        readiness_state = "DRY_RUN_READY"
        next_safe_action = "Continue with bounded READ_ONLY or DRY_RUN work only."
    elif planning_safe:
        verdict = "READY_FOR_PLANNING"
        readiness_state = "PLANNING_READY"
        next_safe_action = "Prepare the next bounded plan without mutation."
    else:
        verdict = "BLOCKED_NO_SAFE_NEXT_ACTION"
        readiness_state = "BLOCKED"
        next_safe_action = "Stop until the blockers prove one safe next task."

    return _result(
        generated_at_utc=generated_at,
        verdict=verdict,
        readiness_state=readiness_state,
        evidence_inputs=evidence_inputs,
        blockers=_dedupe(blockers),
        next_safe_action=next_safe_action,
        goal_clear=goal_clear,
        allowed_files_known=allowed_files_known,
        forbidden_files_known=forbidden_files_known,
        risk_level=risk_level,
        risk_low_enough=risk_low_enough,
        validators_known=validators_known,
        rollback_path_known=rollback_path_known,
        protected_action_requires_human=protected_requested,
        approval_required=approval_required,
        explicit_approval_present=explicit_approval_present,
        observe_allowed=verdict
        in {"READY_FOR_PLANNING", "READY_FOR_DRY_RUN_ONLY", "APPLY_REVIEW_REQUIRED", "BLOCKED_APPROVAL"},
        planning_allowed=verdict in {"READY_FOR_PLANNING", "READY_FOR_DRY_RUN_ONLY"},
        dry_run_allowed=verdict == "READY_FOR_DRY_RUN_ONLY",
        apply_review_allowed=verdict == "APPLY_REVIEW_REQUIRED",
    )


def _result(
    *,
    generated_at_utc: str,
    verdict: str,
    readiness_state: str,
    evidence_inputs: list[dict[str, Any]],
    blockers: list[str],
    next_safe_action: str,
    goal_clear: bool = False,
    allowed_files_known: bool = False,
    forbidden_files_known: bool = False,
    risk_level: str = "UNKNOWN",
    risk_low_enough: bool = False,
    validators_known: bool = False,
    rollback_path_known: bool = False,
    protected_action_requires_human: bool = False,
    approval_required: bool = True,
    explicit_approval_present: bool = False,
    observe_allowed: bool = False,
    planning_allowed: bool = False,
    dry_run_allowed: bool = False,
    apply_review_allowed: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "generated_at_utc": generated_at_utc,
        "component": COMPONENT,
        "mode": MODE,
        "verdict": verdict,
        "readiness_state": readiness_state,
        "observe_allowed": observe_allowed,
        "planning_allowed": planning_allowed,
        "dry_run_allowed": dry_run_allowed,
        "apply_allowed": False,
        "apply_review_allowed": apply_review_allowed,
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
        "goal_clear": goal_clear,
        "allowed_files_known": allowed_files_known,
        "forbidden_files_known": forbidden_files_known,
        "risk_level": risk_level,
        "risk_low_enough": risk_low_enough,
        "validators_known": validators_known,
        "rollback_path_known": rollback_path_known,
        "protected_action_requires_human": protected_action_requires_human,
        "approval_required": approval_required,
        "explicit_approval_present": explicit_approval_present,
        "blockers": blockers,
        "evidence_inputs": evidence_inputs,
        "next_safe_action": next_safe_action,
        "safety": {
            "read_only": True,
            "evidence_only": True,
            "side_effect_free": True,
            "commands_executed": False,
            "network_access": False,
            "secrets_accessed": False,
            "runtime_mutation": False,
            "second_autonomy_authority": False,
            "approval_mutation": False,
            "queue_mutation": False,
            "repo_mutation": False,
        },
    }
    return payload


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _evidence_inputs(evidence: Any) -> list[dict[str, Any]]:
    if not isinstance(evidence, Mapping):
        return [{"name": "root", "status": "missing_or_non_object", "schema": None}]
    inputs: list[dict[str, Any]] = []
    for name in (*CORE_EVIDENCE, "approval"):
        value = evidence.get(name)
        status = "missing" if value in (None, "", [], {}) else "present"
        if status == "present" and _is_stale(value):
            status = "stale"
        inputs.append({"name": name, "status": status, "schema": _schema_name(value)})
    return inputs


def _core_shape_ok(name: str, value: Any) -> bool:
    if name == "validators":
        return isinstance(value, (Mapping, Sequence)) and not isinstance(value, (str, bytes, bytearray))
    return isinstance(value, Mapping)


def _schema_name(value: Any) -> str | None:
    if isinstance(value, Mapping):
        schema = value.get("schema") or value.get("schema_version")
        return str(schema) if schema not in (None, "", [], {}) else None
    return None


def _is_stale(value: Any) -> bool:
    if isinstance(value, Mapping):
        if value.get("stale") is True or value.get("is_stale") is True:
            return True
        freshness = str(value.get("freshness") or value.get("freshness_state") or "").upper()
        status = str(value.get("status") or "").upper()
        return freshness == "STALE" or status == "STALE"
    return False


def _scope_mode(task: Mapping[str, Any], governor: Mapping[str, Any], continuation: Mapping[str, Any]) -> str:
    values = (
        task.get("mode"),
        _nested(task, "scope", "mode"),
        _nested(governor, "recommended_packet_scope", "mode"),
        governor.get("allowed_lane"),
        _nested(continuation, "selected_task", "mode"),
    )
    for value in values:
        text = str(value or "").strip().upper()
        if text:
            return text
    return "UNKNOWN"


def _goal_clear(task: Mapping[str, Any], governor: Mapping[str, Any]) -> bool:
    return any(str(value or "").strip() for value in (task.get("goal"), task.get("task_id"), governor.get("selected_candidate_id")))


def _scope_list(governor: Mapping[str, Any], key: str) -> Any:
    return _nested(governor, "recommended_packet_scope", key)


def _non_empty_list(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and any(str(item).strip() for item in value)


def _first_present(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None


def _validator_state(validators: Any) -> tuple[bool, list[str]]:
    entries: list[Any]
    if isinstance(validators, Mapping):
        raw = validators.get("items") or validators.get("validators")
        entries = raw if isinstance(raw, list) else [validators]
    elif isinstance(validators, Sequence) and not isinstance(validators, (str, bytes, bytearray)):
        entries = list(validators)
    else:
        return False, ["validators_malformed"]

    if not entries:
        return False, ["validators_missing"]

    blockers: list[str] = []
    for index, entry in enumerate(entries):
        status = _validator_status(entry)
        if status in VALIDATOR_BLOCK or status not in VALIDATOR_PASS:
            blockers.append(f"validator_{index}_{status.lower() or 'unknown'}")
    return not blockers, blockers


def _validator_status(entry: Any) -> str:
    if isinstance(entry, str):
        return entry.strip().upper()
    if not isinstance(entry, Mapping):
        return "MALFORMED"
    for key in ("status", "result", "validator_status", "normalized_status"):
        value = entry.get(key)
        if value not in (None, "", [], {}):
            return str(value).strip().upper()
    return "UNKNOWN"


def _risk_level(task: Mapping[str, Any], governor: Mapping[str, Any]) -> str:
    value = _first_present(task.get("risk_level"), governor.get("risk_level"))
    text = str(value or "UNKNOWN").strip().upper()
    if text == "BLOCKED":
        return "BLOCKED"
    if text in {"LOW", "GREEN"}:
        return text
    if text in {"MEDIUM", "YELLOW"}:
        return "MEDIUM"
    if text in {"HIGH", "RED"}:
        return "HIGH"
    return "UNKNOWN"


def _rollback_path_known(task: Mapping[str, Any], scope_mode: str) -> bool:
    mutation_performed = task.get("mutation_performed") is True
    if scope_mode in READ_MODES and not mutation_performed:
        return True
    for key in ("rollback", "rollback_path", "rollback_plan", "revert", "revert_plan"):
        value = task.get(key)
        if str(value or "").strip():
            return True
    return False


def _security_blocked(security: Mapping[str, Any]) -> bool:
    state = str(
        _first_present(
            security.get("overall_state"),
            security.get("security_state"),
            security.get("state"),
            security.get("status"),
        )
        or ""
    ).strip().upper()
    if state in SECURITY_BLOCK:
        return True
    events = security.get("events")
    if isinstance(events, Sequence) and not isinstance(events, (str, bytes, bytearray)):
        for event in events:
            if isinstance(event, Mapping):
                severity = str(_first_present(event.get("severity"), event.get("action")) or "").strip().upper()
                if severity in SECURITY_BLOCK:
                    return True
    return False


def _dirty_tree_blocked(dirty_tree: Mapping[str, Any]) -> bool:
    overall = str(dirty_tree.get("overall_classification") or dirty_tree.get("status") or "").strip().upper()
    return (
        overall in DIRTY_BLOCK
        or dirty_tree.get("sos_required") is True
        or dirty_tree.get("protected_stop_required") is True
        or dirty_tree.get("review_required") is True
    )


def _dry_run_supported(continuation: Mapping[str, Any], governor: Mapping[str, Any], scope_mode: str) -> bool:
    continuation_mode = str(_nested(continuation, "selected_task", "mode") or continuation.get("mode") or "").upper()
    continuation_state = str(continuation.get("state") or "").upper()
    governor_lane = str(governor.get("allowed_lane") or "").upper()
    governor_blocked = governor.get("blocked") is True
    return (
        scope_mode in READ_MODES
        and not governor_blocked
        and (continuation_mode in READ_MODES or continuation_state in {"CONTINUE", "DRY_RUN_EXECUTION", "VALIDATION"})
        and governor_lane in {"READ_ONLY", "DRY_RUN"}
    )


def _protected_action_requested(task: Mapping[str, Any], governor: Mapping[str, Any], scope_mode: str) -> bool:
    if scope_mode in APPLY_MODES or scope_mode.startswith("APPLY"):
        return True
    if task.get("protected_action_requested") is True:
        return True
    for key in ("commit_requested", "push_requested", "merge_requested"):
        if task.get(key) is True or governor.get(key) is True:
            return True
    return False


def _bool_from_sources(task: Mapping[str, Any], governor: Mapping[str, Any], key: str) -> bool:
    return task.get(key) is True or governor.get(key) is True


def _explicit_approval_present(approval: Any) -> bool:
    if not isinstance(approval, Mapping):
        return False
    if approval.get("explicit_approval_present") is True or approval.get("approved") is True:
        return True
    status = str(approval.get("status") or "").strip().upper()
    return status in {"APPROVED", "EXPLICITLY_APPROVED", "PASS", "PASSED"}


def _positive_authority(evidence: Mapping[str, Any]) -> list[str]:
    found: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, Mapping):
            for key, item in value.items():
                text_key = str(key)
                if text_key in HARD_FALSE_FIELDS and item is True:
                    found.append(text_key)
                walk(item)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            for item in value:
                walk(item)

    walk(evidence)
    return sorted(set(found))


def _contains_unsafe_scope(evidence: Mapping[str, Any]) -> bool:
    def clean(value: Any, parent_key: str = "") -> Any:
        lowered = parent_key.lower()
        if "forbidden" in lowered or "blocked_actions" in lowered:
            return None
        if isinstance(value, Mapping):
            return {str(key): clean(item, str(key)) for key, item in value.items()}
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return [clean(item, parent_key) for item in value]
        return value

    text = json.dumps(clean(evidence), sort_keys=True, default=str).lower()
    return any(term in text for term in UNSAFE_TERMS)


def _nested(value: Mapping[str, Any], *keys: str) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


__all__ = ["build_readiness_gate"]
