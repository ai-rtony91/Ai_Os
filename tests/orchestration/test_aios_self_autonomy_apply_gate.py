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
    / "autonomy_apply_gate"
    / "aios_self_autonomy_apply_gate.py"
)
SCHEMA = REPO_ROOT / "schemas" / "aios" / "orchestration" / "AIOS_SELF_AUTONOMY_APPLY_GATE.v1.schema.json"
FIXED_NOW = "2026-06-16T21:00:00Z"
HARD_FALSE_FIELDS = (
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
REQUIRED_FIELDS = {
    "schema",
    "generated_at_utc",
    "component",
    "mode",
    "gate_id",
    "inherited_execution_id",
    "inherited_plan_id",
    "inherited_execution_verdict",
    "verdict",
    "gate_state",
    "dry_run_valid",
    "scope_valid",
    "validators_known",
    "rollback_path_known",
    "human_approval_required",
    "explicit_human_approval_present",
    "approval_scope_matches",
    "apply_review_ready",
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
    "allowed_paths",
    "forbidden_paths",
    "validator_chain",
    "rollback_note",
    "blockers",
    "evidence_inputs",
    "next_safe_action",
    "safety",
}


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("aios_self_autonomy_apply_gate", MODULE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_dry_run() -> dict[str, Any]:
    allowed_paths = ["automation/orchestration/autonomy_apply_gate/"]
    forbidden_paths = ["Reports/", ".github/", "automation/orchestration/autonomy_dry_run_executor/"]
    validator_chain = [
        "git diff --check",
        "python -m pytest tests/orchestration/test_aios_self_autonomy_apply_gate.py -q",
    ]
    return {
        "schema": "AIOS_SELF_AUTONOMY_DRY_RUN_EXECUTION.v1",
        "generated_at_utc": FIXED_NOW,
        "component": "self_autonomy_dry_run_executor",
        "mode": "READ_ONLY_DRY_RUN_SIMULATOR",
        "execution_id": "dryrun-fixture-001",
        "inherited_plan_id": "plan-fixture-001",
        "inherited_plan_verdict": "PLAN_READY_DRY_RUN_PREVIEW",
        "inherited_plan_state": "DRY_RUN_PREVIEW_READY",
        "verdict": "DRY_RUN_SIMULATION_COMPLETE",
        "execution_state": "SIMULATED",
        "simulated": True,
        "commands_executed": False,
        "files_written": False,
        "mutations_performed": False,
        "executable_packet_emitted": False,
        "execution_token_emitted": False,
        "codex_prompt_emitted": False,
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
        "preview_valid": True,
        "preview_executable": False,
        "allowed_paths": allowed_paths,
        "forbidden_paths": forbidden_paths,
        "validator_chain": validator_chain,
        "rollback_note": "Restore reviewed files from the approved diff if needed.",
        "simulated_steps": [
            "inspect_allowed_paths",
            "verify_forbidden_paths_absent",
            "verify_non_executable_preview",
            "verify_validator_chain_present",
            "simulate_validator_plan",
            "produce_dry_run_summary",
            "stop_before_mutation",
        ],
        "simulated_findings": {
            "would_inspect_files": allowed_paths,
            "would_avoid_files": forbidden_paths,
            "validators_required": validator_chain,
            "mutation_intent": False,
            "protected_action_intent": False,
            "human_approval_required_before_execution": True,
        },
        "blockers": [],
        "evidence_inputs": [{"name": "plan", "status": "present", "schema": "fixture"}],
        "next_safe_action": "Prepare separate human review for scoped APPLY.",
        "safety": {
            "read_only": True,
            "side_effect_free": True,
            "simulation_only": True,
            "commands_executed": False,
            "files_written": False,
            "reports_written": False,
            "network_access": False,
            "secrets_accessed": False,
            "runtime_mutation": False,
            "approval_mutation": False,
            "queue_mutation": False,
        },
    }


def matching_approval(execution: dict[str, Any] | None = None) -> dict[str, Any]:
    dry_run = valid_dry_run() if execution is None else execution
    return {
        "schema": "AIOS_HUMAN_APPROVAL.fixture",
        "approval_status": "approved",
        "allowed_paths": list(dry_run["allowed_paths"]),
        "validator_chain": list(dry_run["validator_chain"]),
    }


def build(dry_run_execution: dict[str, Any] | None, approval: dict[str, Any] | None = None) -> dict[str, Any]:
    module = load_module()
    return module.build_self_autonomy_apply_gate(dry_run_execution, approval=approval, now_utc=FIXED_NOW)


def assert_hard_safety_false(result: dict[str, Any]) -> None:
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
    assert result["safety"]["commands_executed"] is False
    assert result["safety"]["files_written"] is False
    assert result["safety"]["reports_written"] is False
    assert result["safety"]["runtime_mutation"] is False
    assert result["safety"]["approval_mutation"] is False
    assert result["safety"]["queue_mutation"] is False
    assert result["safety"]["apply_performed"] is False


def test_valid_dry_run_plus_matching_explicit_approval_returns_apply_review_ready() -> None:
    dry_run = valid_dry_run()
    result = build(dry_run, matching_approval(dry_run))

    assert result["schema"] == "AIOS_SELF_AUTONOMY_APPLY_GATE.v1"
    assert result["verdict"] == "APPLY_REVIEW_READY"
    assert result["gate_state"] == "READY_FOR_HUMAN_APPLY_REVIEW"
    assert result["dry_run_valid"] is True
    assert result["scope_valid"] is True
    assert result["validators_known"] is True
    assert result["rollback_path_known"] is True
    assert result["explicit_human_approval_present"] is True
    assert result["approval_scope_matches"] is True
    assert result["apply_review_ready"] is True
    assert result["allowed_paths"] == dry_run["allowed_paths"]
    assert result["validator_chain"] == dry_run["validator_chain"]
    assert_hard_safety_false(result)


def test_valid_dry_run_without_approval_returns_human_approval_required() -> None:
    result = build(valid_dry_run())

    assert result["verdict"] == "HUMAN_APPROVAL_REQUIRED"
    assert result["gate_state"] == "WAITING_FOR_HUMAN_APPROVAL"
    assert result["explicit_human_approval_present"] is False
    assert result["approval_scope_matches"] is False
    assert result["apply_review_ready"] is False
    assert "explicit_human_approval_missing" in result["blockers"]
    assert_hard_safety_false(result)


def test_missing_dry_run_execution_returns_blocked_dry_run_missing() -> None:
    result = build(None)

    assert result["verdict"] == "BLOCKED_DRY_RUN_MISSING"
    assert "dry_run_execution_missing_or_non_object" in result["blockers"]
    assert_hard_safety_false(result)


def test_blocked_m13_verdict_returns_blocked_dry_run_not_ready() -> None:
    dry_run = valid_dry_run()
    dry_run["verdict"] = "BLOCKED_SCOPE_UNKNOWN"
    dry_run["execution_state"] = "BLOCKED"
    dry_run["blockers"] = ["allowed_or_forbidden_paths_missing"]

    result = build(dry_run, matching_approval(dry_run))

    assert result["verdict"] == "BLOCKED_DRY_RUN_NOT_READY"
    assert "allowed_or_forbidden_paths_missing" in result["blockers"]
    assert_hard_safety_false(result)


def test_missing_allowed_or_forbidden_paths_returns_blocked_scope_unknown() -> None:
    dry_run = valid_dry_run()
    dry_run["allowed_paths"] = []

    result = build(dry_run, matching_approval(dry_run))

    assert result["verdict"] == "BLOCKED_SCOPE_UNKNOWN"
    assert "allowed_or_forbidden_paths_missing" in result["blockers"]
    assert_hard_safety_false(result)


def test_unsafe_protected_allowed_path_returns_blocked_scope_unsafe() -> None:
    dry_run = valid_dry_run()
    dry_run["allowed_paths"] = ["docs/governance/"]

    result = build(dry_run, matching_approval(dry_run))

    assert result["verdict"] == "BLOCKED_SCOPE_UNSAFE"
    assert "allowed_path_unsafe_or_protected" in result["blockers"]
    assert_hard_safety_false(result)


def test_overlapping_allowed_and_forbidden_paths_returns_blocked_scope_unsafe() -> None:
    dry_run = valid_dry_run()
    dry_run["forbidden_paths"] = list(dry_run["forbidden_paths"]) + [dry_run["allowed_paths"][0]]

    result = build(dry_run, matching_approval(dry_run))

    assert result["verdict"] == "BLOCKED_SCOPE_UNSAFE"
    assert "allowed_forbidden_path_overlap" in result["blockers"]
    assert_hard_safety_false(result)


def test_missing_validator_chain_returns_blocked_validators_unknown() -> None:
    dry_run = valid_dry_run()
    dry_run["validator_chain"] = []

    result = build(dry_run, matching_approval(dry_run))

    assert result["verdict"] == "BLOCKED_VALIDATORS_UNKNOWN"
    assert "validator_chain_missing" in result["blockers"]
    assert_hard_safety_false(result)


def test_missing_rollback_note_or_path_returns_blocked_rollback_missing() -> None:
    dry_run = valid_dry_run()
    dry_run["rollback_note"] = ""

    result = build(dry_run, matching_approval(dry_run))

    assert result["verdict"] == "BLOCKED_ROLLBACK_MISSING"
    assert "rollback_note_or_path_missing" in result["blockers"]
    assert_hard_safety_false(result)


def test_approval_with_mismatched_allowed_paths_returns_scope_mismatch() -> None:
    dry_run = valid_dry_run()
    approval = matching_approval(dry_run)
    approval["allowed_paths"] = ["automation/orchestration/other/"]

    result = build(dry_run, approval)

    assert result["verdict"] == "BLOCKED_APPROVAL_SCOPE_MISMATCH"
    assert "approval_scope_mismatch" in result["blockers"]
    assert_hard_safety_false(result)


def test_approval_with_mismatched_validator_chain_returns_scope_mismatch() -> None:
    dry_run = valid_dry_run()
    approval = matching_approval(dry_run)
    approval["validator_chain"] = ["python -m pytest tests/other.py -q"]

    result = build(dry_run, approval)

    assert result["verdict"] == "BLOCKED_APPROVAL_SCOPE_MISMATCH"
    assert "approval_scope_mismatch" in result["blockers"]
    assert_hard_safety_false(result)


def test_unsafe_terms_return_blocked_unsafe_scope() -> None:
    dry_run = valid_dry_run()
    approval = matching_approval(dry_run)
    approval["note"] = "broker live trading secret scheduler git commit git push merge"

    result = build(dry_run, approval)

    assert result["verdict"] == "BLOCKED_UNSAFE_SCOPE"
    assert "unsafe_scope_detected" in result["blockers"]
    assert_hard_safety_false(result)


def test_commands_executed_true_returns_execution_side_effect() -> None:
    dry_run = valid_dry_run()
    dry_run["commands_executed"] = True

    result = build(dry_run, matching_approval(dry_run))

    assert result["verdict"] == "BLOCKED_EXECUTION_SIDE_EFFECT"
    assert "dry_run_side_effect_or_authority_flag" in result["blockers"]
    assert_hard_safety_false(result)


def test_files_written_true_returns_execution_side_effect() -> None:
    dry_run = valid_dry_run()
    dry_run["files_written"] = True

    result = build(dry_run, matching_approval(dry_run))

    assert result["verdict"] == "BLOCKED_EXECUTION_SIDE_EFFECT"
    assert_hard_safety_false(result)


def test_mutations_performed_true_returns_execution_side_effect() -> None:
    dry_run = valid_dry_run()
    dry_run["mutations_performed"] = True

    result = build(dry_run, matching_approval(dry_run))

    assert result["verdict"] == "BLOCKED_EXECUTION_SIDE_EFFECT"
    assert_hard_safety_false(result)


def test_executable_packet_emitted_true_returns_execution_side_effect() -> None:
    dry_run = valid_dry_run()
    dry_run["executable_packet_emitted"] = True

    result = build(dry_run, matching_approval(dry_run))

    assert result["verdict"] == "BLOCKED_EXECUTION_SIDE_EFFECT"
    assert_hard_safety_false(result)


def test_execution_token_emitted_true_returns_execution_side_effect() -> None:
    dry_run = valid_dry_run()
    dry_run["execution_token_emitted"] = True

    result = build(dry_run, matching_approval(dry_run))

    assert result["verdict"] == "BLOCKED_EXECUTION_SIDE_EFFECT"
    assert_hard_safety_false(result)


def test_codex_prompt_emitted_true_returns_execution_side_effect() -> None:
    dry_run = valid_dry_run()
    dry_run["codex_prompt_emitted"] = True

    result = build(dry_run, matching_approval(dry_run))

    assert result["verdict"] == "BLOCKED_EXECUTION_SIDE_EFFECT"
    assert_hard_safety_false(result)


def test_output_never_contains_executable_prompt_or_token_text() -> None:
    result = build(valid_dry_run(), matching_approval())
    text = json.dumps(result, sort_keys=True)

    assert "CODEX-ONLY PROMPT" not in text
    assert "AI_OS EXECUTION TOKEN" not in text
    assert result["executable_packet_emitted"] is False
    assert result["execution_token_emitted"] is False
    assert result["codex_prompt_emitted"] is False


def test_hard_safety_booleans_remain_false_in_every_verdict() -> None:
    not_ready = valid_dry_run()
    not_ready["verdict"] = "BLOCKED_SCOPE_UNKNOWN"
    unknown_scope = valid_dry_run()
    unknown_scope["allowed_paths"] = []
    unsafe_scope = valid_dry_run()
    unsafe_scope["allowed_paths"] = ["docs/security/"]
    no_validators = valid_dry_run()
    no_validators["validator_chain"] = []
    no_rollback = valid_dry_run()
    no_rollback["rollback_note"] = ""
    approval_mismatch = valid_dry_run()
    side_effect = valid_dry_run()
    side_effect["commands_executed"] = True
    unsafe_input = valid_dry_run()
    unsafe_approval = matching_approval(unsafe_input)
    unsafe_approval["note"] = "secret credential merge"

    results = [
        build(valid_dry_run(), matching_approval()),
        build(valid_dry_run()),
        build(None),
        build(not_ready, matching_approval(not_ready)),
        build(unknown_scope, matching_approval(unknown_scope)),
        build(unsafe_scope, matching_approval(unsafe_scope)),
        build(no_validators, matching_approval(no_validators)),
        build(no_rollback, matching_approval(no_rollback)),
        build(approval_mismatch, {"status": "approved", "allowed_paths": ["automation/orchestration/other/"], "validator_chain": approval_mismatch["validator_chain"]}),
        build(unsafe_input, unsafe_approval),
        build(side_effect, matching_approval(side_effect)),
    ]

    verdicts = {result["verdict"] for result in results}
    assert {
        "APPLY_REVIEW_READY",
        "HUMAN_APPROVAL_REQUIRED",
        "BLOCKED_DRY_RUN_MISSING",
        "BLOCKED_DRY_RUN_NOT_READY",
        "BLOCKED_SCOPE_UNKNOWN",
        "BLOCKED_SCOPE_UNSAFE",
        "BLOCKED_VALIDATORS_UNKNOWN",
        "BLOCKED_ROLLBACK_MISSING",
        "BLOCKED_APPROVAL_SCOPE_MISMATCH",
        "BLOCKED_UNSAFE_SCOPE",
        "BLOCKED_EXECUTION_SIDE_EFFECT",
    }.issubset(verdicts)
    for result in results:
        assert_hard_safety_false(result)


def test_gate_id_is_deterministic_for_same_input() -> None:
    first = build(valid_dry_run(), matching_approval())
    second = build(valid_dry_run(), matching_approval())

    assert first["gate_id"] == second["gate_id"]


def test_schema_contains_required_top_level_fields() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    result = build(valid_dry_run(), matching_approval())

    assert set(schema["required"]) == REQUIRED_FIELDS
    assert REQUIRED_FIELDS.issubset(result)
    assert result["generated_at_utc"] == FIXED_NOW
    assert schema["properties"]["schema"]["const"] == "AIOS_SELF_AUTONOMY_APPLY_GATE.v1"


def test_inputs_are_not_mutated() -> None:
    dry_run = valid_dry_run()
    approval = matching_approval(dry_run)
    before_dry_run = copy.deepcopy(dry_run)
    before_approval = copy.deepcopy(approval)

    result = build(dry_run, approval)

    assert result["verdict"] == "APPLY_REVIEW_READY"
    assert dry_run == before_dry_run
    assert approval == before_approval
