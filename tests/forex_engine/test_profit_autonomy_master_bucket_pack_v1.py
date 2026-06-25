from __future__ import annotations

import ast
import inspect
import io
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import automation.forex_engine.profit_autonomy_master_bucket_pack_v1 as bucket  # noqa: E402
from automation.forex_engine.profit_autonomy_master_bucket_pack_v1 import (  # noqa: E402
    BUCKET_STATUS_BLOCKED_BY_MISSING_CANDIDATE_SELECTOR,
    BUCKET_STATUS_GOVERNED_DEMO_AUTONOMY_REVIEW_PATH_DEFINED,
    BUCKET_STATUS_NEXT_ACTION_PROOF_BUCKET_REQUIRED,
    BUCKET_STATUS_NEXT_ACTION_SELECTOR_COMMIT_PR_MERGE_REQUIRED,
    REQUIRED_PROOF_CATEGORIES,
    build_current_state_demo_review_path_ready,
    build_current_state_no_selector,
    build_current_state_selector_landed,
    build_current_state_selector_local_only,
    build_master_bucket_stages,
    bucket_to_markdown,
    evaluate_master_bucket,
    next_stage_to_operator_packet_text,
    result_to_jsonable_dict,
    result_to_operator_text,
    validate_bucket_integrity,
)
from scripts.forex_delivery.run_profit_autonomy_master_bucket_pack_v1 import (  # noqa: E402
    main,
)


def sample_results():
    return (
        evaluate_master_bucket(build_current_state_selector_local_only()),
        evaluate_master_bucket(build_current_state_no_selector()),
        evaluate_master_bucket(build_current_state_selector_landed()),
        evaluate_master_bucket(build_current_state_demo_review_path_ready()),
    )


def test_build_master_bucket_stages_returns_at_least_twenty_stages() -> None:
    assert len(build_master_bucket_stages()) >= 20


def test_stages_are_deterministically_ordered_by_stage_id() -> None:
    stage_ids = [stage.stage_id for stage in build_master_bucket_stages()]

    assert stage_ids == sorted(stage_ids)


def test_all_required_stage_ids_exist_from_00_through_19() -> None:
    stage_ids = {stage.stage_id for stage in build_master_bucket_stages()}

    for index in range(20):
        assert any(stage_id.startswith(f"FX-BUCKET-{index:02d}") for stage_id in stage_ids)


def test_every_stage_has_entry_criteria() -> None:
    assert all(stage.entry_criteria for stage in build_master_bucket_stages())


def test_every_stage_has_exit_criteria() -> None:
    assert all(stage.exit_criteria for stage in build_master_bucket_stages())


def test_every_stage_has_validators() -> None:
    assert all(stage.validators for stage in build_master_bucket_stages())


def test_every_stage_has_blocked_actions() -> None:
    assert all(stage.blocked_actions for stage in build_master_bucket_stages())


def test_every_stage_has_stop_point() -> None:
    assert all(stage.stop_point for stage in build_master_bucket_stages())


def test_every_stage_has_evidence_required() -> None:
    assert all(stage.evidence_required for stage in build_master_bucket_stages())


def test_every_stage_has_codex_packet_intent() -> None:
    assert all(stage.codex_packet_intent for stage in build_master_bucket_stages())


def test_validate_bucket_integrity_passes_for_default_bucket() -> None:
    assert validate_bucket_integrity() is True


def test_selector_missing_state_returns_missing_selector_status() -> None:
    result = evaluate_master_bucket(build_current_state_no_selector())

    assert result.current_status == BUCKET_STATUS_BLOCKED_BY_MISSING_CANDIDATE_SELECTOR


def test_selector_local_only_state_returns_protected_landing_status() -> None:
    result = evaluate_master_bucket(build_current_state_selector_local_only())

    assert result.current_status == BUCKET_STATUS_NEXT_ACTION_SELECTOR_COMMIT_PR_MERGE_REQUIRED


def test_selector_landed_state_returns_proof_bucket_required() -> None:
    result = evaluate_master_bucket(build_current_state_selector_landed())

    assert result.current_status == BUCKET_STATUS_NEXT_ACTION_PROOF_BUCKET_REQUIRED


def test_demo_review_path_ready_state_returns_review_path_defined() -> None:
    result = evaluate_master_bucket(build_current_state_demo_review_path_ready())

    assert result.current_status == BUCKET_STATUS_GOVERNED_DEMO_AUTONOMY_REVIEW_PATH_DEFINED


def test_candidate_review_allowed_only_when_selector_supports_review() -> None:
    missing = evaluate_master_bucket(build_current_state_no_selector())
    local_only = evaluate_master_bucket(build_current_state_selector_local_only())
    landed = evaluate_master_bucket(build_current_state_selector_landed())

    assert missing.permissions.candidate_review_allowed is False
    assert local_only.permissions.candidate_review_allowed is True
    assert landed.permissions.candidate_review_allowed is True


def test_next_demo_trade_allowed_remains_false_in_selector_local_only_state() -> None:
    result = evaluate_master_bucket(build_current_state_selector_local_only())

    assert result.permissions.next_demo_trade_allowed is False


def test_broker_action_allowed_false_in_every_builtin_sample() -> None:
    assert all(result.permissions.broker_action_allowed is False for result in sample_results())


def test_real_money_allowed_false_in_every_builtin_sample() -> None:
    assert all(result.permissions.real_money_allowed is False for result in sample_results())


def test_compounding_allowed_false_in_every_builtin_sample() -> None:
    assert all(result.permissions.compounding_allowed is False for result in sample_results())


def test_bank_movement_allowed_false_in_every_builtin_sample() -> None:
    assert all(result.permissions.bank_movement_allowed is False for result in sample_results())


def test_live_trading_allowed_false_in_every_builtin_sample() -> None:
    assert all(result.permissions.live_trading_allowed is False for result in sample_results())


def test_credential_access_allowed_false_in_every_builtin_sample() -> None:
    assert all(result.permissions.credential_access_allowed is False for result in sample_results())


def test_repo_commit_allowed_false_in_every_builtin_sample() -> None:
    assert all(result.permissions.repo_commit_allowed is False for result in sample_results())


def test_repo_push_allowed_false_in_every_builtin_sample() -> None:
    assert all(result.permissions.repo_push_allowed is False for result in sample_results())


def test_pr_creation_allowed_false_in_every_builtin_sample() -> None:
    assert all(result.permissions.pr_creation_allowed is False for result in sample_results())


def test_owner_approval_required_remains_true_in_builtin_samples() -> None:
    assert all(result.permissions.owner_approval_required is True for result in sample_results())


def test_guaranteed_profit_target_is_true() -> None:
    assert evaluate_master_bucket().guaranteed_profit_target is True


def test_guaranteed_profit_proven_false_in_every_builtin_sample() -> None:
    assert all(result.guaranteed_profit_proven is False for result in sample_results())


def test_proof_summary_includes_all_required_proof_categories() -> None:
    result = evaluate_master_bucket()

    assert set(REQUIRED_PROOF_CATEGORIES) <= set(result.proof_summary)


def test_result_to_jsonable_dict_contains_required_sections() -> None:
    parsed = result_to_jsonable_dict(evaluate_master_bucket())

    for key in (
        "bucket_id",
        "current_status",
        "stages",
        "stage_results",
        "permissions",
        "proof_summary",
        "next_safe_action",
        "operator_answer",
    ):
        assert key in parsed


def test_result_to_operator_text_includes_current_status_and_next_safe_action() -> None:
    text = result_to_operator_text(evaluate_master_bucket())

    assert "current_status:" in text
    assert "next_safe_action:" in text


def test_bucket_to_markdown_includes_all_twenty_stage_ids() -> None:
    markdown = bucket_to_markdown(evaluate_master_bucket())

    for index in range(20):
        assert f"FX-BUCKET-{index:02d}" in markdown


def test_next_stage_to_operator_packet_text_is_not_executable_when_child_fields_unknown() -> None:
    text = next_stage_to_operator_packet_text(evaluate_master_bucket())

    assert "next_codex_packet_intent" in text
    assert "CODEX-ONLY PROMPT" not in text


def test_module_imports_do_not_include_forbidden_runtime_modules() -> None:
    tree = ast.parse(inspect.getsource(bucket))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name.lower() for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module.lower())

    forbidden_fragments = (
        "oan" + "da",
        "bro" + "ker",
        "cred" + "ential",
        "dot" + "env",
        "ba" + "nk",
        "with" + "drawal",
        "dep" + "osit",
        "fund" + "ing",
        "live_" + "execution",
        "sec" + "ret",
    )
    assert not any(
        fragment in module_name
        for module_name in imported
        for fragment in forbidden_fragments
    )


def test_runner_json_output_is_valid_json_for_selector_local_only() -> None:
    stdout = io.StringIO()

    exit_code = main(["--selector-local-only", "--json"], stdout=stdout)
    parsed = json.loads(stdout.getvalue())

    assert exit_code == 0
    assert parsed["current_status"] == BUCKET_STATUS_NEXT_ACTION_SELECTOR_COMMIT_PR_MERGE_REQUIRED


def test_runner_markdown_output_includes_bucket_title() -> None:
    stdout = io.StringIO()

    exit_code = main(["--selector-local-only", "--markdown"], stdout=stdout)

    assert exit_code == 0
    assert "# AIOS Forex Profit Autonomy Master Bucket Pack V1" in stdout.getvalue()


def test_runner_next_packet_output_includes_intent_and_no_self_approval() -> None:
    stdout = io.StringIO()

    exit_code = main(["--selector-local-only", "--next-packet"], stdout=stdout)
    text = stdout.getvalue()

    assert exit_code == 0
    assert "next_codex_packet_intent" in text
    assert "self_approval: false" in text


def test_repeated_evaluation_produces_identical_json_for_same_input() -> None:
    left = json.dumps(result_to_jsonable_dict(evaluate_master_bucket()), sort_keys=True)
    right = json.dumps(result_to_jsonable_dict(evaluate_master_bucket()), sort_keys=True)

    assert left == right


def test_bucket_stage_dependencies_reference_existing_stage_ids_or_milestones() -> None:
    stages = build_master_bucket_stages()
    stage_ids = {stage.stage_id for stage in stages}
    allowed = stage_ids | set(bucket.LANDED_MILESTONES)

    for stage in stages:
        assert set(stage.depends_on) <= allowed
