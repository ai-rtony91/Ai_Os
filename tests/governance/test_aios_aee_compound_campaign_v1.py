from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from automation.governance.aios_aee_campaign_state_classifier_v1 import (
    TARGET_BRANCH,
    classify_campaign_state,
    classify_dirty_files,
    classify_forbidden_paths,
    classify_prompt_interruption,
    classify_staged_files,
    result_to_markdown as classifier_to_markdown,
    result_to_operator_text as classifier_to_text,
)
from automation.governance.aios_aee_campaign_metrics_v1 import (
    build_campaign_metrics,
    classify_campaign_depth,
    result_to_markdown as metrics_to_markdown,
    result_to_operator_text as metrics_to_text,
    summarize_artifacts,
)
from automation.governance.aios_aee_owner_handoff_builder_v1 import (
    build_handoff,
    reject_broad_git_add,
    reject_placeholder_commands,
    validate_explicit_file_list,
    validate_handoff_blocks,
    result_to_markdown as handoff_to_markdown,
    result_to_jsonable_dict as handoff_to_json,
    build_publish_check_block,
)
from automation.governance.aios_aee_static_ci_guard_v1 import (
    scan_static_ci_guard,
    scan_sensitive_assignment_names,
    scan_report_checkpoint_contradiction,
    result_to_markdown as guard_to_markdown,
)
from automation.governance.aios_aee_validator_execution_planner_v1 import (
    build_validation_plan,
    apply_1312_result,
    classify_command,
    plan_owner_deferred_commands,
    result_to_markdown as planner_to_markdown,
)
from automation.governance.aios_aee_validator_execution_planner_v1 import _normalise  # type: ignore[attr-defined]

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "tests/fixtures/governance/aee_compound_campaign_v1"
CAMPAIGN_SCRIPT = REPO_ROOT / "scripts/governance/run_aios_aee_compound_campaign_v1.py"
REPORT_PATH = "Reports/core_delivery/AIOS_AEE_COMPOUND_SPARK_LONGRUN_CAMPAIGN_V1_REPORT_TEST.md"


def _fixture_status(name: str) -> str:
    data = {}
    for line in (FIXTURE_DIR / name).read_text(encoding="utf-8").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data.get("status", "")


def test_phase_0_checkpoint_created() -> None:
    checkpoint = REPO_ROOT / "Reports/core_delivery/AIOS_AEE_COMPOUND_SPARK_LONGRUN_CAMPAIGN_V1_CHECKPOINT.md"
    assert checkpoint.exists()
    text = checkpoint.read_text(encoding="utf-8")
    assert "Clean-main preflight is intentionally bypassed" in text


def test_fixture_count_reaches_minimum() -> None:
    assert len(list(FIXTURE_DIR.iterdir())) >= 40


def test_approved_compound_carryover_continues() -> None:
    result = classify_campaign_state(
        branch=TARGET_BRANCH,
        dirty_files=[
            "automation/governance/aios_aee_campaign_state_classifier_v1.py",
            "automation/governance/aios_aee_governance_validator_v1.py",
        ],
    )
    assert result.continuation_status == "APPROVED_COMPOUND_CARRYOVER_CONTINUATION"


def test_clean_main_wrong_packet_returns_wrong_packet() -> None:
    result = classify_campaign_state(
        branch="main",
        dirty_files=["automation/governance/aios_aee_governance_validator_v1.py"],
    )
    assert result.continuation_status == "WRONG_PACKET_FOR_CLEAN_MAIN"


def test_wrong_branch_dirty_hard_stop() -> None:
    result = classify_campaign_state(
        branch="feature/other",
        dirty_files=["automation/governance/aios_aee_campaign_state_classifier_v1.py"],
    )
    assert result.continuation_status == "HARD_STOP"


def test_staged_files_hard_stop() -> None:
    result = classify_campaign_state(
        branch=TARGET_BRANCH,
        dirty_files=["automation/governance/aios_aee_campaign_state_classifier_v1.py"],
        staged_files=["automation/governance/aios_aee_campaign_state_classifier_v1.py"],
    )
    assert result.continuation_status == "HARD_STOP"


def test_forbidden_path_hard_stop() -> None:
    result = classify_campaign_state(
        branch=TARGET_BRANCH,
        dirty_files=["automation/governance/aios_aee_campaign_state_classifier_v1.py", "secrets/config.env"],
    )
    assert result.continuation_status == "HARD_STOP"
    assert classify_forbidden_paths(["secrets/config.env"]) == ["secrets/config.env"]


def test_prompt_interruption_queued() -> None:
    assert classify_prompt_interruption("Please explain this codebase now") == "PROMPT_INTERRUPTION_REVIEW_QUEUE"


def test_cancel_prompt_hard_stop() -> None:
    assert classify_prompt_interruption("cancel this packet now") == "HARD_STOP"


def test_1312_readonly_classification() -> None:
    result = classify_campaign_state(
        branch=TARGET_BRANCH,
        dirty_files=["automation/governance/aios_aee_campaign_state_classifier_v1.py"],
        simulate_1312=True,
    )
    assert result.continuation_status in {"RECOVERABLE_LOCAL", "DEFERRED_OWNER_VALIDATION"}


def test_1312_strict_cli_after_targeted_tests_deferred() -> None:
    result = classify_campaign_state(
        branch=TARGET_BRANCH,
        dirty_files=["automation/governance/aios_aee_campaign_state_classifier_v1.py"],
        simulate_1312=True,
        targeted_tests_passed=True,
    )
    assert result.continuation_status == "DEFERRED_OWNER_VALIDATION"


def test_all_remaining_work_blocked_by_1312() -> None:
    result = classify_campaign_state(
        branch=TARGET_BRANCH,
        dirty_files=["automation/governance/aios_aee_campaign_state_classifier_v1.py"],
        simulate_1312=True,
        all_remaining_work_blocked=True,
    )
    assert result.continuation_status == "SANDBOX_LIMITATION"


def test_broad_scan_blocked_is_recoverable() -> None:
    result = classify_campaign_state(
        branch=TARGET_BRANCH,
        dirty_files=["automation/governance/aios_aee_campaign_state_classifier_v1.py"],
        broad_scan_blocked=True,
    )
    assert result.continuation_status == "MINOR_SCAN_BLOCKED_RECOVERABLE"


def test_classify_dirty_files_marks_approved_compound() -> None:
    status, carryover, allowed, noncarryover, forbidden = classify_dirty_files(
        [
            "automation/governance/aios_aee_governance_validator_v1.py",
            "automation/governance/aios_aee_campaign_state_classifier_v1.py",
        ],
        require_compound=True,
    )
    assert status == "APPROVED_COMPOUND_CARRYOVER_CONTINUATION"
    assert not noncarryover
    assert not forbidden
    assert carryover
    assert allowed


def test_validation_planner_marks_py_compile_safe() -> None:
    plan = build_validation_plan(REPO_ROOT, strict_cli=False, write_report=False)
    step = next(item for item in plan.plan if item.name == "safe_python_compile")
    assert step.risk == "SAFE_LOCAL"


def test_validation_planner_marks_targeted_pytest_safe() -> None:
    plan = build_validation_plan(REPO_ROOT, strict_cli=False, write_report=False)
    step = next(item for item in plan.plan if item.name == "targeted_pytest")
    assert step.risk == "SAFE_LOCAL"


def test_validation_planner_apply_1312_strict_cli_deferred_after_tests_pass() -> None:
    plan = build_validation_plan(REPO_ROOT, strict_cli=True, write_report=False)
    adapted = apply_1312_result(plan, simulate_1312=True, targeted_tests_passed=True)
    strict_step = next(item for item in adapted if item.name == "strict_cli")
    assert strict_step.risk == "DEFERRED_OWNER_IF_1312"


def test_validation_planner_marks_protected_owner_only_commands() -> None:
    assert classify_command("git push -u origin lane/aios-aee-governance-validator-v1") == "PROTECTED_OWNER_ONLY"
    assert classify_command("gh pr create --title test") == "PROTECTED_OWNER_ONLY"


def test_handoff_builder_accepts_explicit_files() -> None:
    handoff = build_handoff(
        changed_files=[
            "automation/governance/aios_aee_campaign_state_classifier_v1.py",
            "automation/governance/aios_aee_validator_execution_planner_v1.py",
            "scripts/governance/run_aios_aee_compound_campaign_v1.py",
        ]
    )
    assert "git add --" in handoff.publish_check_block
    assert "git commit -m" in handoff.publish_check_block
    assert "gh pr checks --watch" in handoff.publish_check_block
    assert handoff.validation == []


def test_handoff_builder_rejects_broad_git_add_dot() -> None:
    issues = reject_broad_git_add("git add .")
    assert "git add ." in issues[0]


def test_handoff_builder_rejects_broad_git_add_a() -> None:
    issues = reject_broad_git_add("git add -A")
    assert any("git add -A" in item for item in issues)


def test_handoff_builder_rejects_broad_git_add_all() -> None:
    issues = reject_broad_git_add("git add --all")
    assert any("git add -A is not allowed" in item for item in issues)


def test_handoff_builder_rejects_placeholder_command() -> None:
    issues = reject_placeholder_commands("python -m pytest {path}/test.py")
    assert issues


def test_handoff_builder_rejects_merge_in_publish_block() -> None:
    handoff = build_handoff(changed_files=["automation/governance/aios_aee_campaign_state_classifier_v1.py"])
    assert "gh pr merge" not in handoff.publish_check_block.lower()


def test_handoff_builder_rejects_merge_check_mix() -> None:
    pb = (
        "# Block 1\n"
        "git status --short --branch\n"
        "gh pr checks --watch\n"
        "git add -- automation/governance/aios_aee_campaign_state_classifier_v1.py\n"
        "gh pr merge --squash\n"
    )
    mb = (
        "# Block 2\n"
        "gh pr merge --squash\n"
        "git switch main\n"
        "git pull --ff-only origin main\n"
    )
    issues = validate_handoff_blocks(pb, mb)
    assert any("must not be in Block 1" in issue for issue in issues)


def test_handoff_builder_separates_blocks() -> None:
    handoff = build_handoff(changed_files=["automation/governance/aios_aee_campaign_state_classifier_v1.py"])
    assert handoff.publish_check_block.startswith("# Block 1")
    assert handoff.merge_sync_block.startswith("# Block 2")


def test_static_guard_rejects_sensitive_assignment() -> None:
    findings = scan_sensitive_assignment_names("api_key = 1234")
    assert findings
    assert findings[0].code == "AIOS-AEE-COMP-GUARD-1001"


def test_static_guard_rejects_forbidden_path() -> None:
    findings = scan_static_ci_guard(
        publish_block="# Block 1\ngit status --short --branch",
        merge_block="# Block 2",
        changed_files=["secrets/config.env", "automation/governance/aios_aee_campaign_state_classifier_v1.py"],
        report_text="x",
        checkpoint_text="y",
    )
    assert any(item.code == "AIOS-AEE-COMP-GUARD-1009" for item in findings)


def test_static_guard_rejects_missing_safety_boundary() -> None:
    findings = scan_static_ci_guard(
        publish_block="# Block 1",
        merge_block="# Block 2",
        changed_files=["automation/governance/aios_aee_campaign_state_classifier_v1.py"],
        report_text="# Report",
        checkpoint_text="current_phase: complete",
    )
    assert any(item.code == "AIOS-AEE-COMP-GUARD-1012" for item in findings)


def test_static_guard_detects_report_checkpoint_contradiction() -> None:
    findings = scan_report_checkpoint_contradiction("final_status: complete", "current_phase: running")
    assert findings
    assert findings[0].code == "AIOS-AEE-COMP-GUARD-1010"


def test_static_guard_does_not_treat_incomplete_as_complete() -> None:
    findings = scan_report_checkpoint_contradiction("final_status: complete", "current_phase: incomplete")
    assert findings
    assert findings[0].code == "AIOS-AEE-COMP-GUARD-1010"


def test_metrics_classifies_micro() -> None:
    metrics = build_campaign_metrics(created_files=["a.py"], modified_files=[], implementation_modules=["m1"], tests_written=1, fixtures_written=0, docs_written=0, validation_commands_attempted=0, validations_passed=0, validations_blocked=0, events_1312=0, repair_loops=0)
    assert metrics.campaign_depth == "MICRO_PACKET"


def test_metrics_classifies_short() -> None:
    metrics = build_campaign_metrics(
        created_files=[f"c{i}.py" for i in range(4)],
        modified_files=[f"m{i}" for i in range(4)],
        implementation_modules=["m1"],
        tests_written=12,
        fixtures_written=2,
        docs_written=1,
        validation_commands_attempted=4,
        validations_passed=4,
        validations_blocked=0,
        events_1312=0,
        repair_loops=0,
    )
    assert metrics.campaign_depth in {"SHORT_PACKET", "MEDIUM_PACKET"}


def test_metrics_classifies_medium() -> None:
    assert classify_campaign_depth(95) == "MEDIUM_PACKET"


def test_metrics_classifies_longrun() -> None:
    assert classify_campaign_depth(250) == "LONGRUN_PACKET"


def test_metrics_classifies_compound_longrun() -> None:
    assert classify_campaign_depth(500) == "COMPOUND_LONGRUN_PACKET"


def test_cli_strict_zero_for_approved_compound_carryover() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(CAMPAIGN_SCRIPT),
            "--strict",
            "--branch",
            TARGET_BRANCH,
            "--dirty-file",
            "automation/governance/aios_aee_governance_validator_v1.py",
        ],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0


def test_cli_strict_zero_for_deferred_validation() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(CAMPAIGN_SCRIPT),
            "--strict",
            "--branch",
            TARGET_BRANCH,
            "--dirty-file",
            "automation/governance/aios_aee_campaign_state_classifier_v1.py",
            "--simulate-1312",
            "--simulate-targeted-tests-passed",
        ],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0


def test_cli_strict_zero_for_owner_handoff_ready() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(CAMPAIGN_SCRIPT),
            "--strict",
            "--branch",
            TARGET_BRANCH,
            "--dirty-file",
            "automation/governance/aios_aee_governance_validator_v1.py",
            "--local-work-complete",
        ],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0


def test_cli_strict_nonzero_for_hard_stop() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(CAMPAIGN_SCRIPT),
            "--strict",
            "--branch",
            "feature/other",
            "--dirty-file",
            "automation/governance/aios_aee_governance_validator_v1.py",
        ],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 1


def test_cli_writes_report() -> None:
    output_path = REPO_ROOT / REPORT_PATH
    if output_path.exists():
        output_path.unlink()

    completed = subprocess.run(
        [
            sys.executable,
            str(CAMPAIGN_SCRIPT),
            "--strict",
            "--write-report",
            "--report-path",
            REPORT_PATH,
            "--branch",
            TARGET_BRANCH,
            "--dirty-file",
            "automation/governance/aios_aee_governance_validator_v1.py",
        ],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    assert output_path.exists()
    assert completed.returncode == 0
    report_text = output_path.read_text(encoding="utf-8")
    assert "campaign_depth" in report_text or "campaign_depth:" in report_text


def test_cli_json_output_serializes() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(CAMPAIGN_SCRIPT),
            "--json",
            "--strict",
            "--branch",
            TARGET_BRANCH,
            "--dirty-file",
            "automation/governance/aios_aee_governance_validator_v1.py",
        ],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert "state" in payload
    assert "plan" in payload
    assert "guard" in payload
    assert "metrics" in payload


def test_markdown_output_includes_campaign_depth() -> None:
    assert "campaign_depth" in metrics_to_markdown(
        build_campaign_metrics(
            created_files=["a", "b", "c"],
            modified_files=["m1", "m2"],
            implementation_modules=["m1"],
            tests_written=25,
            fixtures_written=40,
            docs_written=1,
            validation_commands_attempted=6,
            validations_passed=6,
            validations_blocked=0,
            events_1312=1,
            repair_loops=0,
        )
    )


def test_operator_output_stable() -> None:
    result = classify_campaign_state(
        branch=TARGET_BRANCH,
        dirty_files=["automation/governance/aios_aee_governance_validator_v1.py"],
    )
    text = classifier_to_text(result)
    assert "status=" in text and "branch=" in text and "dirty=" in text


def test_no_subprocess_in_core_modules() -> None:
    for path in [
        REPO_ROOT / "automation/governance/aios_aee_campaign_state_classifier_v1.py",
        REPO_ROOT / "automation/governance/aios_aee_validator_execution_planner_v1.py",
        REPO_ROOT / "automation/governance/aios_aee_owner_handoff_builder_v1.py",
        REPO_ROOT / "automation/governance/aios_aee_static_ci_guard_v1.py",
        REPO_ROOT / "automation/governance/aios_aee_campaign_metrics_v1.py",
    ]:
        text = path.read_text(encoding="utf-8")
        assert "import subprocess" not in text


def test_no_network_or_env_or_credential_or_broker_in_core_modules() -> None:
    for path in [
        REPO_ROOT / "automation/governance/aios_aee_campaign_state_classifier_v1.py",
        REPO_ROOT / "automation/governance/aios_aee_validator_execution_planner_v1.py",
        REPO_ROOT / "automation/governance/aios_aee_owner_handoff_builder_v1.py",
        REPO_ROOT / "automation/governance/aios_aee_static_ci_guard_v1.py",
        REPO_ROOT / "automation/governance/aios_aee_campaign_metrics_v1.py",
    ]:
        text = path.read_text(encoding="utf-8")
        assert "requests" not in text
        assert "socket" not in text
        assert "os.environ" not in text
        assert "openai.api_key" not in text.lower()
        assert "from secrets" not in text.lower()
        if "this artifact does not authorize trading execution." not in text.lower():
            assert "trading" not in text.lower()


def test_existing_aios_aee_validator_test_still_passes() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/governance/test_aios_aee_governance_validator_v1.py", "-q"],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0


def test_existing_aios_aee_stopgate_test_still_passes() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/governance/test_aios_aee_stopgate_inventory_v3.py", "-q"],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0


def test_integration_v1_v3_and_compound_state_agree() -> None:
    state_v1_v3 = classify_campaign_state(
        branch=TARGET_BRANCH,
        dirty_files=[
            "automation/governance/aios_aee_governance_validator_v1.py",
            "automation/governance/aios_aee_stopgate_inventory_v3.py",
        ],
    )
    fixture_status = _fixture_status("approved_v1_v3_carryover.md")
    if fixture_status:
        assert state_v1_v3.continuation_status in {"APPROVED_CARRYOVER_CONTINUATION", "APPROVED_COMPOUND_CARRYOVER_CONTINUATION"}
        assert fixture_status == state_v1_v3.continuation_status


def test_integration_planner_deferred_1312_is_not_hard_stop() -> None:
    plan = build_validation_plan(REPO_ROOT, strict_cli=True, write_report=False)
    adapted = apply_1312_result(plan, simulate_1312=True, targeted_tests_passed=True)
    strict_step = next(item for item in adapted if item.name == "strict_cli")
    assert strict_step.risk != "HARD_STOP"
    assert strict_step.risk == "DEFERRED_OWNER_IF_1312"


def test_handoff_file_list_contains_v1_v3_and_compound_artifacts() -> None:
    changed = [
        "automation/governance/aios_aee_governance_validator_v1.py",
        "automation/governance/aios_aee_stopgate_inventory_v3.py",
        "automation/governance/aios_aee_campaign_state_classifier_v1.py",
        "automation/governance/aios_aee_validator_execution_planner_v1.py",
        "automation/governance/aios_aee_owner_handoff_builder_v1.py",
        "automation/governance/aios_aee_static_ci_guard_v1.py",
        "automation/governance/aios_aee_campaign_metrics_v1.py",
    ]
    block = build_publish_check_block(changed)
    for expected in changed:
        assert expected in block


def test_handoff_json_serializable() -> None:
    handoff = build_handoff(changed_files=["automation/governance/aios_aee_campaign_state_classifier_v1.py"])
    payload = handoff_to_json(handoff)
    assert isinstance(payload, dict)
    assert payload["publish_check_block"]


def test_validator_owner_deferred_commands_present() -> None:
    commands = plan_owner_deferred_commands(branch=TARGET_BRANCH)
    assert any("gh pr checks --watch" in command for command in commands)
    assert any("git push -u origin" in command for command in commands)
    assert any("git commit -m" in command for command in commands)


def test_guard_markdown_is_printable() -> None:
    findings = scan_static_ci_guard(
        publish_block="# Block 1",
        merge_block="# Block 2",
        changed_files=["automation/governance/aios_aee_campaign_state_classifier_v1.py"],
        report_text="This artifact does not authorize broker/API access.\nThis artifact does not authorize credential access.\nThis artifact does not authorize trading execution.\nThis artifact does not authorize money movement.\nThis artifact does not authorize commit/push/merge without explicit Human Owner approval.",
        checkpoint_text="",
    )
    text = guard_to_markdown(findings)
    assert "# AIOS AEE Compound Campaign Static Guard" in text


def test_campaign_plan_markdown_has_sections() -> None:
    plan = build_validation_plan(REPO_ROOT, strict_cli=True, write_report=False)
    text = planner_to_markdown(plan)
    assert "AIOS AEE Compound Campaign Validation Planner" in text
    assert "|name|command_family|command|risk|retryable|deferred|" in text


def test_handoff_validate_explicit_file_list_rejects_forbidden() -> None:
    assert validate_explicit_file_list(["secrets/config.env"])


def test_handoff_validate_explicit_file_list_rejects_placeholder() -> None:
    issues = validate_explicit_file_list(["automation/governance/{filename}"])
    assert issues


def test_classifier_markdown_printable() -> None:
    result = classify_campaign_state(
        branch=TARGET_BRANCH,
        dirty_files=["automation/governance/aios_aee_campaign_state_classifier_v1.py"],
    )
    text = classifier_to_markdown(result)
    assert "AIOS AEE Campaign State Classifier" in text


def test_summary_artifact_counts() -> None:
    summary = summarize_artifacts(
        [
            "automation/a.py",
            "scripts/b.py",
            "tests/c.py",
            "tests/fixtures/governance/a.md",
            "docs/workflows/d.md",
            "Reports/core_delivery/e.md",
        ]
    )
    assert summary["automation"] == 1
    assert summary["scripts"] == 1
    assert summary["tests"] == 1
    assert summary["fixtures"] == 1


def test_campaign_metrics_text_operator() -> None:
    metrics = build_campaign_metrics(
        created_files=["a", "b", "c", "d", "e", "f"],
        modified_files=["m1"],
        implementation_modules=["m1", "m2", "m3", "m4", "m5"],
        tests_written=20,
        fixtures_written=40,
        docs_written=2,
        validation_commands_attempted=6,
        validations_passed=6,
        validations_blocked=0,
        events_1312=1,
        repair_loops=2,
    )
    text = metrics_to_text(metrics)
    assert "work_units" in text


def test_handoff_markdown_contains_blocks() -> None:
    handoff = build_handoff(changed_files=["automation/governance/aios_aee_campaign_state_classifier_v1.py"])
    text = handoff_to_markdown(handoff)
    assert "publish/check" in text.lower()
    assert "merge/sync" in text.lower()


def test_classify_dirty_helper() -> None:
    status, carryover, allowed, noncarryover, forbidden = classify_dirty_files(["tests/governance/test_aios_aee_governance_validator_v1.py"])
    assert status in {"RECOVERABLE_LOCAL", "APPROVED_CARRYOVER_CONTINUATION"}
    assert not forbidden
    assert carryover == ["tests/governance/test_aios_aee_governance_validator_v1.py"]
    assert allowed
    assert noncarryover == []


def test_staged_helper() -> None:
    status, files = classify_staged_files(["scripts/governance/run_aios_aee_compound_campaign_v1.py"])
    assert status == "HARD_STOP"
    assert files == ["scripts/governance/run_aios_aee_compound_campaign_v1.py"]


def test_plan_normaliser_ignores_empty() -> None:
    assert _normalise(["", "automation/governance/aios_aee_campaign_state_classifier_v1.py"]) == [
        "automation/governance/aios_aee_campaign_state_classifier_v1.py"
    ]


def test_report_checkpoint_guard_conflict() -> None:
    findings = scan_report_checkpoint_contradiction(
        "final_status: complete",
        "current_phase: complete",
    )
    assert findings == []
