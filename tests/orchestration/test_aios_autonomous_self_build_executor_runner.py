from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "automation/orchestration/self_development/Start-AiOsAutonomousSelfBuildExecutor.APPLY.ps1"
RECOMMENDATION = REPO_ROOT / "automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1"


def _param_block() -> str:
    text = RUNNER.read_text(encoding="utf-8")
    match = re.search(r"param\((.*?)\)\s*Set-StrictMode", text, flags=re.DOTALL)
    assert match is not None
    return match.group(1)


def test_runner_has_required_parameters() -> None:
    param_block = _param_block()

    for required in (
        "$RepoRoot",
        "$ExpectedBranch",
        "$OutputJson",
        "$Mode",
        "$HumanOwnerSelfBuildApproval",
        "$SupervisorMode",
        "$MaxSupervisorCycles",
        "$MaxRepairAttempts",
        "$MaxRuntimeMinutes",
        "$StopOnFirstFailure",
        "$AllowLocalCommit",
        "$OutputRoot",
        "$NowUtc",
        "$FailOnDirtyWorktree",
        "$TimeoutSeconds",
    ):
        assert required in param_block


def test_runner_has_no_forbidden_runtime_or_mutation_parameters() -> None:
    param_block = _param_block()

    for forbidden in (
        "$StartRuntime",
        "$LaunchWorker",
        "$Schedule",
        "$Commit",
        "$Push",
        "$Merge",
        "$Approve",
        "$EnableScheduler",
        "$StartDaemon",
        "$MutateQueue",
        "$MutateLocks",
        "$MutateApprovals",
        "$MutateRegistry",
        "$OutputPath",
    ):
        assert forbidden not in param_block


def test_runner_output_json_branch_is_json_only_surface() -> None:
    text = RUNNER.read_text(encoding="utf-8")

    assert "if ($OutputJson)" in text
    assert "$result | ConvertTo-Json -Depth 90" in text
    assert "Write-ConsoleReport -Result $result" in text


def test_runner_sets_repo_root_working_directory_and_pythonpath() -> None:
    text = RUNNER.read_text(encoding="utf-8")

    assert "$psi.WorkingDirectory = $resolvedRepoRoot" in text
    assert "PYTHONPATH" in text
    assert "aios_autonomous_self_build_executor.py" in text
    assert "Start-Process" not in text


def test_runner_console_summary_includes_decision_and_next_action() -> None:
    text = RUNNER.read_text(encoding="utf-8")

    assert "supervisor_mode:" in text
    assert "candidate_id:" in text
    assert "repair_status:" in text
    assert "ledger_written:" in text
    assert "next_safe_action:" in text


def test_recommendation_surfaces_autonomous_self_build_without_apply() -> None:
    text = RECOMMENDATION.read_text(encoding="utf-8")

    assert "AUTONOMOUS SELF-BUILD" in text
    assert "Get-AutonomousSelfBuildAvailabilityState" in text
    assert "can_apply_local_self_build" in text
    assert "push_pr_merge_allowed" in text
    assert "Start-AiOsAutonomousSelfBuildExecutor.APPLY.ps1 -Mode APPLY" not in text
