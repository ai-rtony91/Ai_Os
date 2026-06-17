import json
from copy import deepcopy
from pathlib import Path

import pytest

from automation.orchestration.autonomy_chain import build_self_autonomy_chain_harness
import automation.orchestration.autonomy_chain.aios_self_autonomy_chain_harness as harness

NOW = "2026-01-01T00:00:00Z"
GOAL = "Inspect safe chain harness readiness."
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


def _safe_seed_evidence():
    allowed_paths = ["automation/orchestration/autonomy_chain/"]
    forbidden_paths = ["Reports/", ".github/", "automation/orchestration/autonomy_review_loop/"]
    validator_chain = [
        "git diff --check",
        "python -m pytest tests/orchestration/test_aios_self_autonomy_chain_harness.py -q",
    ]
    return {
        "readiness_evidence": {
            "task": {
                "schema": "AIOS_TEST_TASK_SCOPE.v1",
                "task_id": "m16-fixture",
                "goal": GOAL,
                "mode": "DRY_RUN",
                "allowed_files": allowed_paths,
                "forbidden_files": forbidden_paths,
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
                {"name": validator_chain[0], "status": "PASS"},
                {"name": validator_chain[1], "status": "PASS"},
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
                    "files_allowed": allowed_paths,
                    "files_forbidden": forbidden_paths,
                },
            },
            "approval": {
                "status": "not_required",
                "explicit_approval_present": False,
            },
        },
        "planner_constraints": {
            "allowed_paths": allowed_paths,
            "forbidden_paths": forbidden_paths,
            "validator_chain": validator_chain,
            "rollback_note": "Restore reviewed files from the approved diff if needed.",
            "stop_point": "Stop after safe harness simulation summary.",
        },
    }


def _matching_approval(seed):
    return {
        "approval_status": "approved",
        "allowed_paths": list(seed["planner_constraints"]["allowed_paths"]),
        "validator_chain": list(seed["planner_constraints"]["validator_chain"]),
    }


def _assert_hard_safety_false(result):
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False


def test_no_approval_reaches_human_approval_required():
    result = build_self_autonomy_chain_harness(_safe_seed_evidence(), GOAL, now_utc=NOW)

    assert result["verdict"] == "CHAIN_HUMAN_APPROVAL_REQUIRED"
    assert result["apply_gate"]["verdict"] == "HUMAN_APPROVAL_REQUIRED"
    assert result["review_loop"]["verdict"] == "REVIEW_COMPLETE_RECOMMENDATIONS_ONLY"
    assert result["apply_review_ready"] is False
    _assert_hard_safety_false(result)


def test_matching_approval_reaches_apply_review_ready_without_apply_authority():
    seed = _safe_seed_evidence()
    result = build_self_autonomy_chain_harness(seed, GOAL, approval=_matching_approval(seed), now_utc=NOW)

    assert result["verdict"] == "CHAIN_APPLY_REVIEW_READY"
    assert result["apply_gate"]["verdict"] == "APPLY_REVIEW_READY"
    assert result["apply_review_ready"] is True
    assert result["apply_allowed"] is False
    _assert_hard_safety_false(result)


def test_missing_seed_evidence_blocks():
    result = build_self_autonomy_chain_harness(None, GOAL, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_CHAIN_INPUT_MISSING"
    assert result["first_blocking_component"] is None
    _assert_hard_safety_false(result)


def test_unsafe_terms_block_input():
    seed = _safe_seed_evidence()
    seed["note"] = "unsafe secret scope"

    result = build_self_autonomy_chain_harness(seed, GOAL, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_CHAIN_UNSAFE_INPUT"
    _assert_hard_safety_false(result)


def test_codex_marker_blocks_executable_input():
    seed = _safe_seed_evidence()
    seed["note"] = "CODEX-ONLY PROMPT"

    result = build_self_autonomy_chain_harness(seed, GOAL, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_CHAIN_EXECUTABLE_INPUT"


def test_execution_token_blocks_executable_input():
    seed = _safe_seed_evidence()
    seed["note"] = "AI_OS EXECUTION TOKEN"

    result = build_self_autonomy_chain_harness(seed, GOAL, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_CHAIN_EXECUTABLE_INPUT"


def test_executable_true_blocks_executable_input():
    seed = _safe_seed_evidence()
    seed["executable"] = True

    result = build_self_autonomy_chain_harness(seed, GOAL, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_CHAIN_EXECUTABLE_INPUT"


def test_readiness_blocker_surfaces_first_blocking_component():
    seed = _safe_seed_evidence()
    seed["readiness_evidence"]["security"]["overall_state"] = "STOP"

    result = build_self_autonomy_chain_harness(seed, GOAL, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_CHAIN_COMPONENT_FAILURE"
    assert result["first_blocking_component"] == "readiness"
    assert result["component_verdicts"]["readiness"].startswith("BLOCKED")


def test_planner_blocker_surfaces_first_blocking_component():
    seed = _safe_seed_evidence()
    seed["planner_constraints"].pop("allowed_paths")

    result = build_self_autonomy_chain_harness(seed, GOAL, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_CHAIN_COMPONENT_FAILURE"
    assert result["first_blocking_component"] == "plan"
    assert result["component_verdicts"]["plan"].startswith("BLOCKED")


def test_dry_run_blocker_surfaces_first_blocking_component(monkeypatch):
    def fake_dry_run(plan, now_utc=None):
        return {
            "schema": "AIOS_SELF_AUTONOMY_DRY_RUN_EXECUTION.v1",
            "verdict": "BLOCKED_SCOPE_UNKNOWN",
            "execution_state": "BLOCKED",
            "blockers": ["fixture_dry_run_block"],
        }

    monkeypatch.setattr(harness, "build_self_autonomy_dry_run_execution", fake_dry_run)

    result = harness.build_self_autonomy_chain_harness(_safe_seed_evidence(), GOAL, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_CHAIN_COMPONENT_FAILURE"
    assert result["first_blocking_component"] == "dry_run_execution"


def test_apply_gate_blocker_surfaces_first_blocking_component(monkeypatch):
    def fake_apply_gate(dry_run_execution, approval=None, now_utc=None):
        return {
            "schema": "AIOS_SELF_AUTONOMY_APPLY_GATE.v1",
            "verdict": "BLOCKED_SCOPE_UNKNOWN",
            "gate_state": "BLOCKED",
            "blockers": ["fixture_apply_gate_block"],
        }

    monkeypatch.setattr(harness, "build_self_autonomy_apply_gate", fake_apply_gate)

    result = harness.build_self_autonomy_chain_harness(_safe_seed_evidence(), GOAL, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_CHAIN_COMPONENT_FAILURE"
    assert result["first_blocking_component"] == "apply_gate"


def test_review_loop_output_is_included():
    result = build_self_autonomy_chain_harness(_safe_seed_evidence(), GOAL, now_utc=NOW)

    assert result["review_loop"]["schema"] == "AIOS_SELF_IMPROVEMENT_REVIEW_LOOP.v1"


def test_component_verdicts_contains_all_components():
    result = build_self_autonomy_chain_harness(_safe_seed_evidence(), GOAL, now_utc=NOW)

    assert set(result["component_verdicts"]) == {
        "readiness",
        "plan",
        "dry_run_execution",
        "apply_gate",
        "review_loop",
    }


def test_output_contains_no_executable_markers():
    result = build_self_autonomy_chain_harness(_safe_seed_evidence(), GOAL, now_utc=NOW)
    rendered = json.dumps(result, sort_keys=True)

    assert "CODEX-ONLY PROMPT" not in rendered
    assert "AI_OS EXECUTION TOKEN" not in rendered


def test_component_outputs_do_not_emit_executable_packet_text():
    seed = _safe_seed_evidence()
    result = build_self_autonomy_chain_harness(seed, GOAL, approval=_matching_approval(seed), now_utc=NOW)
    rendered = json.dumps(
        {
            "readiness": result["readiness"],
            "plan": result["plan"],
            "dry_run_execution": result["dry_run_execution"],
            "apply_gate": result["apply_gate"],
            "review_loop": result["review_loop"],
        },
        sort_keys=True,
    )

    assert "CODEX-ONLY PROMPT" not in rendered
    assert "AI_OS EXECUTION TOKEN" not in rendered
    assert result["executable_packet_emitted"] is False


@pytest.mark.parametrize(
    "seed,approval,expected",
    [
        (_safe_seed_evidence(), None, "CHAIN_HUMAN_APPROVAL_REQUIRED"),
        (None, None, "BLOCKED_CHAIN_INPUT_MISSING"),
    ],
)
def test_hard_safety_booleans_remain_false_for_every_verdict(seed, approval, expected):
    result = build_self_autonomy_chain_harness(seed, GOAL, approval=approval, now_utc=NOW)

    assert result["verdict"] == expected
    _assert_hard_safety_false(result)


def test_chain_id_is_deterministic_for_same_input():
    seed = _safe_seed_evidence()
    result_one = build_self_autonomy_chain_harness(deepcopy(seed), GOAL, now_utc=NOW)
    result_two = build_self_autonomy_chain_harness(deepcopy(seed), GOAL, now_utc=NOW)

    assert result_one["chain_id"] == result_two["chain_id"]


def test_schema_contains_required_top_level_fields():
    schema = json.loads(
        Path("schemas/aios/orchestration/AIOS_SELF_AUTONOMY_CHAIN_HARNESS.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    required = set(schema["required"])

    for field in (
        "schema",
        "generated_at_utc",
        "component",
        "mode",
        "chain_id",
        "verdict",
        "chain_state",
        "goal",
        "first_blocking_component",
        "readiness",
        "plan",
        "dry_run_execution",
        "apply_gate",
        "review_loop",
        "component_verdicts",
        "component_states",
        "human_approval_required",
        "explicit_human_approval_present",
        "apply_review_ready",
        "blockers",
        "evidence_inputs",
        "next_safe_action",
        "safety",
    ):
        assert field in required


def test_no_approval_path_never_sets_apply_review_ready_true():
    result = build_self_autonomy_chain_harness(_safe_seed_evidence(), GOAL, now_utc=NOW)

    assert result["apply_review_ready"] is False


def test_matching_approval_sets_apply_review_ready_but_not_apply_allowed():
    seed = _safe_seed_evidence()
    result = build_self_autonomy_chain_harness(seed, GOAL, approval=_matching_approval(seed), now_utc=NOW)

    assert result["apply_review_ready"] is True
    assert result["apply_allowed"] is False
