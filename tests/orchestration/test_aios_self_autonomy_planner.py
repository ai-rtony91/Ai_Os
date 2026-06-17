from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "autonomy_planner"
    / "aios_self_autonomy_planner.py"
)
SCHEMA = REPO_ROOT / "schemas" / "aios" / "orchestration" / "AIOS_SELF_AUTONOMY_PLAN.v1.schema.json"
FIXED_NOW = "2026-06-16T15:00:00Z"
SAFE_GOAL = "Inspect M12 planner readiness and produce a dry-run report."
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
    "goal",
    "normalized_goal",
    "plan_id",
    "verdict",
    "plan_state",
    "inherited_readiness_verdict",
    "inherited_readiness_state",
    "planning_allowed",
    "dry_run_preview_allowed",
    "apply_preview_allowed",
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
    "risk_level",
    "blockers",
    "required_human_approval",
    "non_executable_packet_preview",
    "evidence_inputs",
    "next_safe_action",
    "safety",
}


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("aios_self_autonomy_planner", MODULE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ready_gate() -> dict[str, Any]:
    return {
        "schema": "AIOS_SELF_AUTONOMY_READINESS_GATE.v1",
        "generated_at_utc": FIXED_NOW,
        "component": "self_autonomy_readiness_gate",
        "mode": "READ_ONLY_EVIDENCE_AGGREGATE",
        "verdict": "READY_FOR_DRY_RUN_ONLY",
        "readiness_state": "DRY_RUN_READY",
        "planning_allowed": True,
        "dry_run_allowed": True,
        "apply_review_allowed": False,
        "risk_level": "LOW",
        "goal_clear": True,
        "allowed_files_known": True,
        "forbidden_files_known": True,
        "validators_known": True,
        "rollback_path_known": True,
        "blockers": [],
        "evidence_inputs": [{"name": "fixture", "status": "present", "schema": "fixture"}],
    }


def constraints() -> dict[str, Any]:
    return {
        "schema": "AIOS_SELF_AUTONOMY_PLANNER_CONSTRAINTS.fixture",
        "allowed_paths": ["automation/orchestration/autonomy_planner/"],
        "forbidden_paths": ["Reports/", ".github/", "automation/orchestration/autonomy_readiness/"],
        "validator_chain": [
            "git diff --check",
            "python -m pytest tests/orchestration/test_aios_self_autonomy_planner.py -q",
        ],
        "stop_point": "Stop after DRY_RUN preview and validation summary.",
        "rollback_note": "No mutation is allowed in this dry-run preview.",
    }


def build(goal: str, readiness_gate: dict[str, Any] | None, plan_constraints: dict[str, Any] | None = None) -> dict[str, Any]:
    module = load_module()
    return module.build_self_autonomy_plan(
        goal,
        readiness_gate,
        constraints=constraints() if plan_constraints is None else plan_constraints,
        now_utc=FIXED_NOW,
    )


def assert_hard_safety_false(result: dict[str, Any]) -> None:
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
    assert result["apply_preview_allowed"] is False


def test_clean_m11_ready_for_dry_run_plus_clear_goal_returns_preview() -> None:
    result = build(SAFE_GOAL, ready_gate())
    preview = result["non_executable_packet_preview"]

    assert result["schema"] == "AIOS_SELF_AUTONOMY_PLAN.v1"
    assert result["verdict"] == "PLAN_READY_DRY_RUN_PREVIEW"
    assert result["plan_state"] == "DRY_RUN_PREVIEW_READY"
    assert result["planning_allowed"] is True
    assert result["dry_run_preview_allowed"] is True
    assert preview["mode"] == "DRY_RUN"
    assert preview["lane"] == "DRY_RUN"
    assert preview["allowed_paths"] == constraints()["allowed_paths"]
    assert preview["validator_chain"] == constraints()["validator_chain"]
    assert preview["human_approval_required_before_execution"] is True
    assert_hard_safety_false(result)


def test_empty_goal_returns_blocked_goal_missing() -> None:
    result = build("   ", ready_gate())

    assert result["verdict"] == "BLOCKED_GOAL_MISSING"
    assert "goal_missing" in result["blockers"]
    assert result["non_executable_packet_preview"] is None
    assert_hard_safety_false(result)


def test_unsafe_goal_returns_blocked_goal_unsafe() -> None:
    result = build("Create broker live trading credentials and git push the scheduler.", ready_gate())

    assert result["verdict"] == "BLOCKED_GOAL_UNSAFE"
    assert "unsafe_goal_scope" in result["blockers"]
    assert result["non_executable_packet_preview"] is None
    assert_hard_safety_false(result)


def test_missing_readiness_returns_blocked_readiness_missing() -> None:
    result = build(SAFE_GOAL, None)

    assert result["verdict"] == "BLOCKED_READINESS_MISSING"
    assert "readiness_missing_or_malformed" in result["blockers"]
    assert result["non_executable_packet_preview"] is None
    assert_hard_safety_false(result)


def test_blocked_m11_readiness_returns_not_ready_and_preserves_blockers() -> None:
    readiness = ready_gate()
    readiness["verdict"] = "BLOCKED_SECURITY"
    readiness["readiness_state"] = "BLOCKED"
    readiness["planning_allowed"] = False
    readiness["dry_run_allowed"] = False
    readiness["blockers"] = ["unsafe_scope_or_security_blocker"]

    result = build(SAFE_GOAL, readiness)

    assert result["verdict"] == "BLOCKED_READINESS_NOT_READY"
    assert "unsafe_scope_or_security_blocker" in result["blockers"]
    assert result["non_executable_packet_preview"] is None
    assert_hard_safety_false(result)


def test_apply_review_required_readiness_is_not_planner_scope() -> None:
    readiness = ready_gate()
    readiness["verdict"] = "APPLY_REVIEW_REQUIRED"
    readiness["readiness_state"] = "APPLY_REVIEW"
    readiness["planning_allowed"] = False
    readiness["dry_run_allowed"] = False
    readiness["apply_review_allowed"] = True

    result = build(SAFE_GOAL, readiness)

    assert result["verdict"] == "BLOCKED_APPLY_REVIEW_NOT_PLANNER_SCOPE"
    assert "apply_review_not_planner_scope" in result["blockers"]
    assert result["non_executable_packet_preview"] is None
    assert_hard_safety_false(result)


def test_missing_allowed_paths_or_validators_returns_blocked_scope_unknown() -> None:
    plan_constraints = constraints()
    plan_constraints.pop("allowed_paths")
    plan_constraints.pop("validator_chain")

    result = build(SAFE_GOAL, ready_gate(), plan_constraints)

    assert result["verdict"] == "BLOCKED_SCOPE_UNKNOWN"
    assert "allowed_paths_unknown" in result["blockers"]
    assert "validators_unknown" in result["blockers"]
    assert result["non_executable_packet_preview"] is None
    assert_hard_safety_false(result)


def test_preview_never_contains_executable_prompt_or_token_text() -> None:
    result = build(SAFE_GOAL, ready_gate())
    preview_text = json.dumps(result["non_executable_packet_preview"], sort_keys=True)

    assert "CODEX-ONLY PROMPT" not in preview_text
    assert "AI_OS EXECUTION TOKEN" not in preview_text
    assert result["safety"]["executable_packet_emitted"] is False
    assert result["safety"]["execution_token_emitted"] is False
    assert result["safety"]["codex_prompt_emitted"] is False


def test_preview_executable_is_false() -> None:
    result = build(SAFE_GOAL, ready_gate())
    preview = result["non_executable_packet_preview"]

    assert preview["executable"] is False
    assert preview["execution_token_present"] is False
    assert preview["codex_prompt_present"] is False
    assert all(value is False for value in preview["protected_actions"].values())


def test_hard_safety_booleans_remain_false_in_every_verdict() -> None:
    blocked_gate = ready_gate()
    blocked_gate["verdict"] = "BLOCKED_VALIDATOR"
    blocked_gate["planning_allowed"] = False
    blocked_gate["dry_run_allowed"] = False
    blocked_gate["blockers"] = ["validators_unknown"]
    apply_gate = ready_gate()
    apply_gate["verdict"] = "APPLY_REVIEW_REQUIRED"
    apply_gate["apply_review_allowed"] = True
    medium_risk_gate = ready_gate()
    medium_risk_gate["risk_level"] = "MEDIUM"

    results = [
        build(SAFE_GOAL, ready_gate()),
        build("", ready_gate()),
        build("touch secret credential and merge", ready_gate()),
        build(SAFE_GOAL, None),
        build(SAFE_GOAL, blocked_gate),
        build(SAFE_GOAL, apply_gate),
        build(SAFE_GOAL, ready_gate(), {}),
        build(SAFE_GOAL, medium_risk_gate),
    ]

    verdicts = {result["verdict"] for result in results}
    assert {
        "PLAN_READY_DRY_RUN_PREVIEW",
        "BLOCKED_GOAL_MISSING",
        "BLOCKED_GOAL_UNSAFE",
        "BLOCKED_READINESS_MISSING",
        "BLOCKED_READINESS_NOT_READY",
        "BLOCKED_APPLY_REVIEW_NOT_PLANNER_SCOPE",
        "BLOCKED_SCOPE_UNKNOWN",
        "BLOCKED_NO_SAFE_PLAN",
    }.issubset(verdicts)
    for result in results:
        assert_hard_safety_false(result)


def test_plan_id_is_deterministic_for_same_goal_and_readiness() -> None:
    first = build(SAFE_GOAL, ready_gate())
    second = build(SAFE_GOAL, ready_gate())

    assert first["plan_id"] == second["plan_id"]
    assert first["non_executable_packet_preview"]["packet_id_suggestion"] == second["non_executable_packet_preview"][
        "packet_id_suggestion"
    ]


def test_schema_contains_required_top_level_fields() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    result = build(SAFE_GOAL, ready_gate())

    assert set(schema["required"]) == REQUIRED_FIELDS
    assert REQUIRED_FIELDS.issubset(result)
    assert result["generated_at_utc"] == FIXED_NOW
    assert schema["properties"]["schema"]["const"] == "AIOS_SELF_AUTONOMY_PLAN.v1"
