from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "autonomy_readiness"
    / "aios_self_autonomy_readiness_gate.py"
)
SCHEMA = REPO_ROOT / "schemas" / "aios" / "orchestration" / "AIOS_SELF_AUTONOMY_READINESS_GATE.v1.schema.json"
FIXED_NOW = "2026-06-16T12:00:00Z"
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
REQUIRED_FIELDS = {
    "schema",
    "generated_at_utc",
    "component",
    "mode",
    "verdict",
    "readiness_state",
    "observe_allowed",
    "planning_allowed",
    "dry_run_allowed",
    "apply_allowed",
    "apply_review_allowed",
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
    "goal_clear",
    "allowed_files_known",
    "forbidden_files_known",
    "risk_level",
    "risk_low_enough",
    "validators_known",
    "rollback_path_known",
    "protected_action_requires_human",
    "approval_required",
    "explicit_approval_present",
    "blockers",
    "evidence_inputs",
    "next_safe_action",
    "safety",
}


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("aios_self_autonomy_readiness_gate", MODULE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clean_dry_run_evidence() -> dict[str, Any]:
    return {
        "task": {
            "schema": "AIOS_TEST_TASK_SCOPE.v1",
            "task_id": "m11-fixture",
            "goal": "Inspect readiness and produce a DRY_RUN plan.",
            "mode": "DRY_RUN",
            "allowed_files": ["automation/orchestration/autonomy_readiness/"],
            "forbidden_files": ["Reports/", ".github/"],
            "risk_level": "LOW",
            "mutation_performed": False,
        },
        "security": {
            "schema": "AIOS_PREEMPTIVE_SECURITY_STATE.v1",
            "overall_state": "CLEAR",
            "events": [],
        },
        "dirty_tree": {
            "schema": "AIOS_DIRTY_TREE_CLASSIFIER_RESULT.v1",
            "overall_classification": "CLEAN",
            "dirty_count": 0,
            "safe_for_dry_run": True,
            "safe_for_apply": True,
            "review_required": False,
            "protected_stop_required": False,
            "sos_required": False,
        },
        "validators": [
            {"name": "git diff --check", "status": "PASS"},
            {"name": "targeted pytest", "status": "PASS"},
        ],
        "continuation": {
            "schema": "AIOS_AUTONOMOUS_JOB_CONTINUATION_STATE.v1",
            "state": "CONTINUE",
            "selected_task": {"mode": "DRY_RUN"},
        },
        "governor": {
            "schema": "AIOS_AUTONOMY_DECISION_GOVERNOR.v1",
            "allowed_lane": "DRY_RUN",
            "blocked": False,
            "risk_level": "LOW",
            "recommended_packet_scope": {
                "mode": "DRY_RUN",
                "files_allowed": ["automation/orchestration/autonomy_readiness/"],
                "files_forbidden": ["Reports/", ".github/"],
            },
        },
        "approval": {"status": "not_required", "explicit_approval_present": False},
    }


def build(evidence: Any) -> dict[str, Any]:
    module = load_module()
    return module.build_readiness_gate(evidence, now_utc=FIXED_NOW)


def assert_hard_safety_false(result: dict[str, Any]) -> None:
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False


def test_clean_low_risk_dry_run_evidence_returns_ready_for_dry_run_only() -> None:
    result = build(clean_dry_run_evidence())

    assert result["schema"] == "AIOS_SELF_AUTONOMY_READINESS_GATE.v1"
    assert result["verdict"] == "READY_FOR_DRY_RUN_ONLY"
    assert result["readiness_state"] == "DRY_RUN_READY"
    assert result["observe_allowed"] is True
    assert result["planning_allowed"] is True
    assert result["dry_run_allowed"] is True
    assert result["apply_allowed"] is False
    assert result["blockers"] == []
    assert_hard_safety_false(result)


def test_missing_evidence_fails_closed() -> None:
    result = build(None)

    assert result["verdict"] == "BLOCKED_EVIDENCE_MISSING"
    assert result["approval_required"] is True
    assert "evidence_missing_or_non_object" in result["blockers"]
    assert_hard_safety_false(result)


def test_unsafe_scope_terms_return_blocked_security() -> None:
    evidence = clean_dry_run_evidence()
    evidence["task"]["goal"] = "Enable broker live trading with credentials through scheduler."

    result = build(evidence)

    assert result["verdict"] == "BLOCKED_SECURITY"
    assert result["risk_level"] == "LOW"
    assert "unsafe_scope_or_security_blocker" in result["blockers"]
    assert_hard_safety_false(result)


def test_apply_like_candidate_never_sets_apply_allowed_true_and_requires_review() -> None:
    evidence = clean_dry_run_evidence()
    evidence["task"]["mode"] = "APPLY_CODE_SAFE"
    evidence["task"]["rollback_path"] = "restore approved scoped files from reviewed diff"
    evidence["governor"]["allowed_lane"] = "APPLY_CODE_SAFE"
    evidence["governor"]["recommended_packet_scope"]["mode"] = "APPLY"
    evidence["approval"] = {"status": "approved", "explicit_approval_present": True}

    result = build(evidence)

    assert result["verdict"] == "APPLY_REVIEW_REQUIRED"
    assert result["apply_allowed"] is False
    assert result["apply_review_allowed"] is True
    assert result["protected_action_requires_human"] is True
    assert result["approval_required"] is True
    assert_hard_safety_false(result)


def test_missing_validators_return_blocked_validator() -> None:
    evidence = clean_dry_run_evidence()
    evidence["validators"] = []

    result = build(evidence)

    assert result["verdict"] == "BLOCKED_VALIDATOR"
    assert result["validators_known"] is False
    assert "validators_missing" in result["blockers"]
    assert_hard_safety_false(result)


def test_dirty_protected_evidence_returns_blocked_dirty_tree() -> None:
    evidence = clean_dry_run_evidence()
    evidence["dirty_tree"]["overall_classification"] = "PROTECTED_AUTHORITY_DIRTY"
    evidence["dirty_tree"]["protected_stop_required"] = True

    result = build(evidence)

    assert result["verdict"] == "BLOCKED_DIRTY_TREE"
    assert "dirty_tree_not_safe" in result["blockers"]
    assert_hard_safety_false(result)


def test_rollback_missing_blocks_apply_review() -> None:
    evidence = clean_dry_run_evidence()
    evidence["task"]["mode"] = "APPLY_CODE_SAFE"
    evidence["governor"]["allowed_lane"] = "APPLY_CODE_SAFE"
    evidence["governor"]["recommended_packet_scope"]["mode"] = "APPLY"
    evidence["approval"] = {"status": "approved", "explicit_approval_present": True}

    result = build(evidence)

    assert result["verdict"] == "BLOCKED_NO_SAFE_NEXT_ACTION"
    assert result["rollback_path_known"] is False
    assert result["apply_review_allowed"] is False
    assert "rollback_path_missing" in result["blockers"]
    assert_hard_safety_false(result)


def test_read_only_or_dry_run_without_mutation_satisfies_rollback_path_known() -> None:
    evidence = clean_dry_run_evidence()

    result = build(evidence)

    assert result["verdict"] == "READY_FOR_DRY_RUN_ONLY"
    assert result["rollback_path_known"] is True
    assert_hard_safety_false(result)


def test_hard_safety_booleans_remain_false_in_every_verdict() -> None:
    cases = [
        clean_dry_run_evidence(),
        None,
        _with(clean_dry_run_evidence(), ("task", "goal"), "touch broker credentials"),
        _with(clean_dry_run_evidence(), ("validators",), []),
        _with(clean_dry_run_evidence(), ("dirty_tree", "overall_classification"), "UNKNOWN_DIRTY"),
        _apply_case(with_approval=True, with_rollback=True),
        _apply_case(with_approval=True, with_rollback=False),
        _apply_case(with_approval=False, with_rollback=True),
    ]

    verdicts = {build(case)["verdict"] for case in cases}

    assert {
        "READY_FOR_DRY_RUN_ONLY",
        "BLOCKED_EVIDENCE_MISSING",
        "BLOCKED_SECURITY",
        "BLOCKED_VALIDATOR",
        "BLOCKED_DIRTY_TREE",
        "APPLY_REVIEW_REQUIRED",
        "BLOCKED_NO_SAFE_NEXT_ACTION",
        "BLOCKED_APPROVAL",
    }.issubset(verdicts)
    for case in cases:
        assert_hard_safety_false(build(case))


def test_schema_contains_required_top_level_fields() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    result = build(clean_dry_run_evidence())

    assert set(schema["required"]) == REQUIRED_FIELDS
    assert REQUIRED_FIELDS.issubset(result)
    assert result["generated_at_utc"] == FIXED_NOW
    assert schema["properties"]["schema"]["const"] == "AIOS_SELF_AUTONOMY_READINESS_GATE.v1"


def test_evidence_input_is_not_mutated() -> None:
    evidence = clean_dry_run_evidence()
    before = copy.deepcopy(evidence)

    result = build(evidence)

    assert result["verdict"] == "READY_FOR_DRY_RUN_ONLY"
    assert evidence == before


def _with(evidence: Any, path: tuple[str, ...], value: Any) -> Any:
    if evidence is None:
        return None
    updated = copy.deepcopy(evidence)
    if len(path) == 1:
        updated[path[0]] = value
        return updated
    target = updated
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return updated


def _apply_case(*, with_approval: bool, with_rollback: bool) -> dict[str, Any]:
    evidence = clean_dry_run_evidence()
    evidence["task"]["mode"] = "APPLY_CODE_SAFE"
    evidence["governor"]["allowed_lane"] = "APPLY_CODE_SAFE"
    evidence["governor"]["recommended_packet_scope"]["mode"] = "APPLY"
    if with_rollback:
        evidence["task"]["rollback_path"] = "restore approved scoped files from reviewed diff"
    evidence["approval"] = {
        "status": "approved" if with_approval else "pending",
        "explicit_approval_present": with_approval,
    }
    return evidence
