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
    / "autonomy_review_loop"
    / "aios_self_improvement_review_loop.py"
)
SCHEMA = (
    REPO_ROOT
    / "schemas"
    / "aios"
    / "orchestration"
    / "AIOS_SELF_IMPROVEMENT_REVIEW_LOOP.v1.schema.json"
)
FIXED_NOW = "2026-06-16T22:00:00Z"
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
REQUIRED_FIELDS = {
    "schema",
    "generated_at_utc",
    "component",
    "mode",
    "review_id",
    "verdict",
    "review_state",
    "outcome_count",
    "success_count",
    "blocker_count",
    "dominant_pattern",
    "recommendations",
    "non_executable_recommendations_only",
    "human_approval_required_before_action",
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
    "blockers",
    "evidence_inputs",
    "next_safe_action",
    "safety",
}
REQUIRED_BLOCKED_ACTIONS = {"APPLY", "worker_launch", "scheduler", "broker_live_trading", "commit_push_merge"}


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("aios_self_improvement_review_loop", MODULE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build(outcomes: dict[str, Any] | None) -> dict[str, Any]:
    module = load_module()
    return module.build_self_improvement_review_loop(outcomes, now_utc=FIXED_NOW)


def clean_outcomes() -> dict[str, Any]:
    return {
        "readiness": {
            "schema": "AIOS_SELF_AUTONOMY_READINESS_GATE.v1",
            "verdict": "READY_FOR_DRY_RUN_ONLY",
            "readiness_state": "DRY_RUN_READY",
            "blockers": [],
        },
        "plan": {
            "schema": "AIOS_SELF_AUTONOMY_PLAN.v1",
            "verdict": "PLAN_READY_DRY_RUN_PREVIEW",
            "plan_state": "DRY_RUN_PREVIEW_READY",
            "blockers": [],
        },
        "dry_run_execution": {
            "schema": "AIOS_SELF_AUTONOMY_DRY_RUN_EXECUTION.v1",
            "verdict": "DRY_RUN_SIMULATION_COMPLETE",
            "execution_state": "SIMULATED",
            "blockers": [],
        },
        "apply_gate": {
            "schema": "AIOS_SELF_AUTONOMY_APPLY_GATE.v1",
            "verdict": "APPLY_REVIEW_READY",
            "gate_state": "READY_FOR_HUMAN_APPLY_REVIEW",
            "blockers": [],
        },
    }


def blocked_outcomes(verdict: str, blocker: str, state_key: str = "gate_state") -> dict[str, Any]:
    outcomes = clean_outcomes()
    outcomes["apply_gate"] = {
        "schema": "AIOS_SELF_AUTONOMY_APPLY_GATE.v1",
        "verdict": verdict,
        state_key: "BLOCKED",
        "blockers": [blocker],
    }
    return outcomes


def categories(result: dict[str, Any]) -> set[str]:
    return {item["category"] for item in result["recommendations"]}


def assert_hard_safety_false(result: dict[str, Any]) -> None:
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
    assert result["safety"]["self_approval_allowed"] is False
    assert result["safety"]["commands_executed"] is False
    assert result["safety"]["files_written"] is False
    assert result["safety"]["reports_written"] is False
    assert result["safety"]["runtime_mutation"] is False
    assert result["safety"]["approval_mutation"] is False
    assert result["safety"]["queue_mutation"] is False


def assert_recommendations_non_executable(result: dict[str, Any]) -> None:
    for item in result["recommendations"]:
        assert item["executable"] is False
        assert REQUIRED_BLOCKED_ACTIONS.issubset(set(item["blocked_actions"]))
        if item["category"] != "no_improvement_needed":
            assert item["human_approval_required"] is True


def test_blocked_validator_outcomes_produce_validator_recommendation() -> None:
    result = build(blocked_outcomes("BLOCKED_VALIDATORS_UNKNOWN", "validator_chain_missing"))

    assert result["verdict"] == "REVIEW_COMPLETE_RECOMMENDATIONS_ONLY"
    assert result["dominant_pattern"] == "validator_blocker"
    assert "add_missing_validators" in categories(result)
    assert_recommendations_non_executable(result)
    assert_hard_safety_false(result)


def test_blocked_security_outcomes_produce_security_review_recommendation() -> None:
    result = build(blocked_outcomes("BLOCKED_SECURITY", "security_review_required"))

    assert result["verdict"] == "REVIEW_COMPLETE_RECOMMENDATIONS_ONLY"
    assert "stop_for_security_review" in categories(result)
    assert_hard_safety_false(result)


def test_blocked_scope_outcomes_produce_scope_tightening_recommendation() -> None:
    result = build(blocked_outcomes("BLOCKED_SCOPE_UNKNOWN", "scope_boundary_unknown"))

    assert result["verdict"] == "REVIEW_COMPLETE_RECOMMENDATIONS_ONLY"
    assert "tighten_allowed_paths" in categories(result)
    assert_hard_safety_false(result)


def test_blocked_approval_outcomes_produce_human_approval_recommendation() -> None:
    result = build(blocked_outcomes("HUMAN_APPROVAL_REQUIRED", "approval_missing"))

    assert result["verdict"] == "REVIEW_COMPLETE_RECOMMENDATIONS_ONLY"
    assert "request_human_approval" in categories(result)
    assert_hard_safety_false(result)


def test_blocked_rollback_outcomes_produce_rollback_recommendation() -> None:
    result = build(blocked_outcomes("BLOCKED_ROLLBACK_MISSING", "rollback_note_missing"))

    assert result["verdict"] == "REVIEW_COMPLETE_RECOMMENDATIONS_ONLY"
    assert "add_rollback_note" in categories(result)
    assert_hard_safety_false(result)


def test_clean_path_outcomes_produce_no_action() -> None:
    result = build(clean_outcomes())

    assert result["verdict"] == "REVIEW_COMPLETE_NO_ACTION"
    assert result["dominant_pattern"] == "clean_path"
    assert categories(result) == {"no_improvement_needed"}
    assert result["recommendations"][0]["human_approval_required"] is False
    assert_hard_safety_false(result)


def test_missing_outcomes_return_blocked_outcomes_missing() -> None:
    result = build(None)

    assert result["verdict"] == "BLOCKED_OUTCOMES_MISSING"
    assert "outcomes_missing_or_non_object" in result["blockers"]
    assert_hard_safety_false(result)


def test_malformed_outcomes_return_blocked_outcomes_malformed() -> None:
    result = build({"readiness": {"schema": "fixture"}})

    assert result["verdict"] == "BLOCKED_OUTCOMES_MALFORMED"
    assert "outcome_0_missing_verdict" in result["blockers"]
    assert_hard_safety_false(result)


def test_unsafe_terms_return_blocked_unsafe_content() -> None:
    outcomes = clean_outcomes()
    outcomes["history"] = [{"verdict": "BLOCKED_SECURITY", "gate_state": "BLOCKED", "note": "broker live trading secret scheduler commit push merge"}]

    result = build(outcomes)

    assert result["verdict"] == "BLOCKED_UNSAFE_CONTENT"
    assert "unsafe_content_detected" in result["blockers"]
    assert_hard_safety_false(result)


def test_codex_only_prompt_in_input_returns_blocked_executable_content() -> None:
    outcomes = clean_outcomes()
    outcomes["history"] = [{"verdict": "BLOCKED", "gate_state": "BLOCKED", "note": "CODEX-ONLY PROMPT"}]

    result = build(outcomes)

    assert result["verdict"] == "BLOCKED_EXECUTABLE_CONTENT"
    assert_hard_safety_false(result)


def test_execution_token_in_input_returns_blocked_executable_content() -> None:
    outcomes = clean_outcomes()
    outcomes["history"] = [{"verdict": "BLOCKED", "gate_state": "BLOCKED", "note": "AI_OS EXECUTION TOKEN"}]

    result = build(outcomes)

    assert result["verdict"] == "BLOCKED_EXECUTABLE_CONTENT"
    assert_hard_safety_false(result)


def test_executable_true_in_input_returns_blocked_executable_content() -> None:
    outcomes = clean_outcomes()
    outcomes["plan"]["executable"] = True

    result = build(outcomes)

    assert result["verdict"] == "BLOCKED_EXECUTABLE_CONTENT"
    assert_hard_safety_false(result)


def test_executable_packet_emitted_true_returns_blocked_executable_content() -> None:
    outcomes = clean_outcomes()
    outcomes["dry_run_execution"]["executable_packet_emitted"] = True

    result = build(outcomes)

    assert result["verdict"] == "BLOCKED_EXECUTABLE_CONTENT"
    assert_hard_safety_false(result)


def test_recommendations_are_non_executable() -> None:
    result = build(blocked_outcomes("BLOCKED_SCOPE_UNKNOWN", "scope_boundary_unknown"))

    assert_recommendations_non_executable(result)
    assert result["non_executable_recommendations_only"] is True


def test_self_approval_allowed_is_always_false() -> None:
    for outcomes in (clean_outcomes(), blocked_outcomes("BLOCKED_VALIDATORS_UNKNOWN", "validator_chain_missing"), None):
        result = build(outcomes)
        assert result["self_approval_allowed"] is False


def test_hard_safety_booleans_remain_false_in_every_verdict() -> None:
    malformed = {"readiness": {"schema": "fixture"}}
    unsafe = clean_outcomes()
    unsafe["history"] = [{"verdict": "BLOCKED", "gate_state": "BLOCKED", "note": "secret merge"}]
    executable = clean_outcomes()
    executable["plan"]["executable"] = True
    results = [
        build(clean_outcomes()),
        build(blocked_outcomes("BLOCKED_VALIDATORS_UNKNOWN", "validator_chain_missing")),
        build(None),
        build(malformed),
        build(unsafe),
        build(executable),
    ]

    verdicts = {result["verdict"] for result in results}
    assert {
        "REVIEW_COMPLETE_NO_ACTION",
        "REVIEW_COMPLETE_RECOMMENDATIONS_ONLY",
        "BLOCKED_OUTCOMES_MISSING",
        "BLOCKED_OUTCOMES_MALFORMED",
        "BLOCKED_UNSAFE_CONTENT",
        "BLOCKED_EXECUTABLE_CONTENT",
    }.issubset(verdicts)
    for result in results:
        assert_hard_safety_false(result)


def test_review_id_is_deterministic_for_same_input() -> None:
    first = build(blocked_outcomes("BLOCKED_VALIDATORS_UNKNOWN", "validator_chain_missing"))
    second = build(blocked_outcomes("BLOCKED_VALIDATORS_UNKNOWN", "validator_chain_missing"))

    assert first["review_id"] == second["review_id"]


def test_schema_contains_required_top_level_fields() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    result = build(clean_outcomes())

    assert set(schema["required"]) == REQUIRED_FIELDS
    assert REQUIRED_FIELDS.issubset(result)
    assert result["generated_at_utc"] == FIXED_NOW
    assert schema["properties"]["schema"]["const"] == "AIOS_SELF_IMPROVEMENT_REVIEW_LOOP.v1"


def test_review_never_emits_prompt_or_token_text() -> None:
    result = build(blocked_outcomes("BLOCKED_SCOPE_UNKNOWN", "scope_boundary_unknown"))
    text = json.dumps(result, sort_keys=True)

    assert "CODEX-ONLY PROMPT" not in text
    assert "AI_OS EXECUTION TOKEN" not in text


def test_review_never_emits_executable_packet_text() -> None:
    result = build(blocked_outcomes("BLOCKED_APPROVAL_SCOPE_MISMATCH", "approval_scope_mismatch"))

    assert result["executable_packet_emitted"] is False
    assert result["execution_token_emitted"] is False
    assert result["codex_prompt_emitted"] is False
    for item in result["recommendations"]:
        assert item["executable"] is False
