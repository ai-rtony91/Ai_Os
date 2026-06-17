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
    / "autonomy_dry_run_executor"
    / "aios_self_autonomy_dry_run_executor.py"
)
SCHEMA = (
    REPO_ROOT
    / "schemas"
    / "aios"
    / "orchestration"
    / "AIOS_SELF_AUTONOMY_DRY_RUN_EXECUTION.v1.schema.json"
)
FIXED_NOW = "2026-06-16T18:00:00Z"
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
    "execution_id",
    "inherited_plan_id",
    "inherited_plan_verdict",
    "inherited_plan_state",
    "verdict",
    "execution_state",
    "simulated",
    "commands_executed",
    "files_written",
    "mutations_performed",
    "executable_packet_emitted",
    "execution_token_emitted",
    "codex_prompt_emitted",
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
    "preview_valid",
    "preview_executable",
    "allowed_paths",
    "forbidden_paths",
    "validator_chain",
    "simulated_steps",
    "simulated_findings",
    "blockers",
    "evidence_inputs",
    "next_safe_action",
    "safety",
}
SIMULATED_STEPS = [
    "inspect_allowed_paths",
    "verify_forbidden_paths_absent",
    "verify_non_executable_preview",
    "verify_validator_chain_present",
    "simulate_validator_plan",
    "produce_dry_run_summary",
    "stop_before_mutation",
]


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("aios_self_autonomy_dry_run_executor", MODULE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_plan() -> dict[str, Any]:
    allowed_paths = ["automation/orchestration/autonomy_dry_run_executor/"]
    forbidden_paths = ["Reports/", ".github/", "automation/orchestration/autonomy_planner/"]
    validator_chain = [
        "git diff --check",
        "python -m pytest tests/orchestration/test_aios_self_autonomy_dry_run_executor.py -q",
    ]
    return {
        "schema": "AIOS_SELF_AUTONOMY_PLAN.v1",
        "generated_at_utc": FIXED_NOW,
        "component": "self_autonomy_planner",
        "mode": "READ_ONLY_NON_EXECUTABLE_PLANNER",
        "goal": "Inspect safe dry-run executor readiness.",
        "normalized_goal": "Inspect safe dry-run executor readiness.",
        "plan_id": "plan-fixture-001",
        "verdict": "PLAN_READY_DRY_RUN_PREVIEW",
        "plan_state": "DRY_RUN_PREVIEW_READY",
        "inherited_readiness_verdict": "READY_FOR_DRY_RUN_ONLY",
        "inherited_readiness_state": "DRY_RUN_READY",
        "planning_allowed": True,
        "dry_run_preview_allowed": True,
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
        "risk_level": "LOW",
        "blockers": [],
        "required_human_approval": True,
        "non_executable_packet_preview": {
            "executable": False,
            "execution_token_present": False,
            "codex_prompt_present": False,
            "mode": "DRY_RUN",
            "lane": "DRY_RUN",
            "packet_id_suggestion": "AIOS-M12-PLAN-PREVIEW-FIXTURE",
            "mission_summary": "Inspect safe dry-run executor readiness.",
            "allowed_paths": allowed_paths,
            "forbidden_paths": forbidden_paths,
            "validator_chain": validator_chain,
            "stop_point": "Stop after simulation summary.",
            "rollback_note": "No mutation is allowed in this simulation.",
            "final_report_fields": ["SUMMARY", "VALIDATORS", "STATUS"],
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
        },
        "evidence_inputs": [{"name": "readiness_gate", "status": "present", "schema": "fixture"}],
        "next_safe_action": "Human review is required before executable work.",
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


def build(plan: dict[str, Any] | None) -> dict[str, Any]:
    module = load_module()
    return module.build_self_autonomy_dry_run_execution(plan, now_utc=FIXED_NOW)


def assert_hard_safety_false(result: dict[str, Any]) -> None:
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
    assert result["commands_executed"] is False
    assert result["files_written"] is False
    assert result["mutations_performed"] is False
    assert result["executable_packet_emitted"] is False
    assert result["execution_token_emitted"] is False
    assert result["codex_prompt_emitted"] is False


def test_valid_m12_plan_ready_preview_returns_simulation_complete() -> None:
    plan = valid_plan()

    result = build(plan)

    assert result["schema"] == "AIOS_SELF_AUTONOMY_DRY_RUN_EXECUTION.v1"
    assert result["verdict"] == "DRY_RUN_SIMULATION_COMPLETE"
    assert result["execution_state"] == "SIMULATED"
    assert result["simulated"] is True
    assert result["preview_valid"] is True
    assert result["preview_executable"] is False
    assert result["allowed_paths"] == plan["non_executable_packet_preview"]["allowed_paths"]
    assert result["forbidden_paths"] == plan["non_executable_packet_preview"]["forbidden_paths"]
    assert result["validator_chain"] == plan["non_executable_packet_preview"]["validator_chain"]
    assert result["simulated_steps"] == SIMULATED_STEPS
    assert result["simulated_findings"]["would_inspect_files"] == result["allowed_paths"]
    assert result["simulated_findings"]["would_avoid_files"] == result["forbidden_paths"]
    assert result["simulated_findings"]["validators_required"] == result["validator_chain"]
    assert result["simulated_findings"]["mutation_intent"] is False
    assert result["simulated_findings"]["protected_action_intent"] is False
    assert result["simulated_findings"]["human_approval_required_before_execution"] is True
    assert_hard_safety_false(result)
    assert plan == valid_plan()


def test_missing_plan_returns_blocked_plan_missing() -> None:
    result = build(None)

    assert result["verdict"] == "BLOCKED_PLAN_MISSING"
    assert "plan_missing_or_non_object" in result["blockers"]
    assert result["simulated"] is False
    assert_hard_safety_false(result)


def test_blocked_m12_plan_returns_blocked_plan_not_ready() -> None:
    plan = valid_plan()
    plan["verdict"] = "BLOCKED_SCOPE_UNKNOWN"
    plan["plan_state"] = "BLOCKED"
    plan["blockers"] = ["allowed_paths_unknown"]

    result = build(plan)

    assert result["verdict"] == "BLOCKED_PLAN_NOT_READY"
    assert "allowed_paths_unknown" in result["blockers"]
    assert_hard_safety_false(result)


def test_missing_preview_returns_blocked_preview_missing() -> None:
    plan = valid_plan()
    plan["non_executable_packet_preview"] = None

    result = build(plan)

    assert result["verdict"] == "BLOCKED_PREVIEW_MISSING"
    assert "preview_missing_or_malformed" in result["blockers"]
    assert_hard_safety_false(result)


def test_executable_preview_returns_blocked_executable_preview() -> None:
    plan = valid_plan()
    plan["non_executable_packet_preview"]["executable"] = True

    result = build(plan)

    assert result["verdict"] == "BLOCKED_EXECUTABLE_PREVIEW"
    assert result["preview_executable"] is True
    assert_hard_safety_false(result)


def test_execution_token_present_true_returns_blocked_executable_preview() -> None:
    plan = valid_plan()
    plan["non_executable_packet_preview"]["execution_token_present"] = True

    result = build(plan)

    assert result["verdict"] == "BLOCKED_EXECUTABLE_PREVIEW"
    assert result["execution_token_emitted"] is False
    assert_hard_safety_false(result)


def test_codex_prompt_present_true_returns_blocked_executable_preview() -> None:
    plan = valid_plan()
    plan["non_executable_packet_preview"]["codex_prompt_present"] = True

    result = build(plan)

    assert result["verdict"] == "BLOCKED_EXECUTABLE_PREVIEW"
    assert result["codex_prompt_emitted"] is False
    assert_hard_safety_false(result)


def test_unsafe_terms_return_blocked_unsafe_scope() -> None:
    plan = valid_plan()
    plan["goal"] = "Review broker live trading secret scheduler commit push merge path."
    plan["normalized_goal"] = plan["goal"]

    result = build(plan)

    assert result["verdict"] == "BLOCKED_UNSAFE_SCOPE"
    assert "unsafe_scope_detected" in result["blockers"]
    assert_hard_safety_false(result)


def test_missing_allowed_or_forbidden_paths_returns_blocked_scope_unknown() -> None:
    plan = valid_plan()
    plan["non_executable_packet_preview"]["allowed_paths"] = []

    result = build(plan)

    assert result["verdict"] == "BLOCKED_SCOPE_UNKNOWN"
    assert "allowed_or_forbidden_paths_missing" in result["blockers"]
    assert_hard_safety_false(result)


def test_missing_validator_chain_returns_blocked_validators_unknown() -> None:
    plan = valid_plan()
    plan["non_executable_packet_preview"]["validator_chain"] = []

    result = build(plan)

    assert result["verdict"] == "BLOCKED_VALIDATORS_UNKNOWN"
    assert "validator_chain_missing" in result["blockers"]
    assert_hard_safety_false(result)


def test_non_dry_run_mode_or_lane_returns_blocked_not_dry_run() -> None:
    plan = valid_plan()
    plan["non_executable_packet_preview"]["mode"] = "APPLY"

    result = build(plan)

    assert result["verdict"] == "BLOCKED_NOT_DRY_RUN"
    assert "preview_not_dry_run" in result["blockers"]
    assert_hard_safety_false(result)


def test_output_never_contains_executable_prompt_or_token_text() -> None:
    result = build(valid_plan())
    output_text = json.dumps(result, sort_keys=True)

    assert "CODEX-ONLY PROMPT" not in output_text
    assert "AI_OS EXECUTION TOKEN" not in output_text
    assert result["executable_packet_emitted"] is False
    assert result["execution_token_emitted"] is False
    assert result["codex_prompt_emitted"] is False


def test_commands_files_and_mutations_remain_false() -> None:
    result = build(valid_plan())

    assert result["commands_executed"] is False
    assert result["files_written"] is False
    assert result["mutations_performed"] is False
    assert result["safety"]["commands_executed"] is False
    assert result["safety"]["files_written"] is False
    assert result["safety"]["reports_written"] is False
    assert result["safety"]["runtime_mutation"] is False


def test_hard_safety_booleans_remain_false_in_every_verdict() -> None:
    blocked_plan = valid_plan()
    blocked_plan["verdict"] = "BLOCKED_SCOPE_UNKNOWN"
    no_preview = valid_plan()
    no_preview["non_executable_packet_preview"] = {}
    executable_preview = valid_plan()
    executable_preview["non_executable_packet_preview"]["executable"] = True
    unsafe_plan = valid_plan()
    unsafe_plan["goal"] = "touch secret credential and push"
    unknown_scope = valid_plan()
    unknown_scope["non_executable_packet_preview"]["forbidden_paths"] = []
    no_validators = valid_plan()
    no_validators["non_executable_packet_preview"]["validator_chain"] = []
    not_dry_run = valid_plan()
    not_dry_run["non_executable_packet_preview"]["lane"] = "APPLY"

    results = [
        build(valid_plan()),
        build(None),
        build(blocked_plan),
        build(no_preview),
        build(executable_preview),
        build(unsafe_plan),
        build(unknown_scope),
        build(no_validators),
        build(not_dry_run),
    ]

    verdicts = {result["verdict"] for result in results}
    assert {
        "DRY_RUN_SIMULATION_COMPLETE",
        "BLOCKED_PLAN_MISSING",
        "BLOCKED_PLAN_NOT_READY",
        "BLOCKED_PREVIEW_MISSING",
        "BLOCKED_EXECUTABLE_PREVIEW",
        "BLOCKED_UNSAFE_SCOPE",
        "BLOCKED_SCOPE_UNKNOWN",
        "BLOCKED_VALIDATORS_UNKNOWN",
        "BLOCKED_NOT_DRY_RUN",
    }.issubset(verdicts)
    for result in results:
        assert_hard_safety_false(result)


def test_execution_id_is_deterministic_for_same_input() -> None:
    first = build(valid_plan())
    second = build(valid_plan())

    assert first["execution_id"] == second["execution_id"]


def test_schema_contains_required_top_level_fields() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    result = build(valid_plan())

    assert set(schema["required"]) == REQUIRED_FIELDS
    assert REQUIRED_FIELDS.issubset(result)
    assert result["generated_at_utc"] == FIXED_NOW
    assert schema["properties"]["schema"]["const"] == "AIOS_SELF_AUTONOMY_DRY_RUN_EXECUTION.v1"


def test_input_plan_is_not_mutated() -> None:
    plan = valid_plan()
    before = copy.deepcopy(plan)

    result = build(plan)

    assert result["verdict"] == "DRY_RUN_SIMULATION_COMPLETE"
    assert plan == before
