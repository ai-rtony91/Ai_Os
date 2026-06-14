from __future__ import annotations

from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "automation/orchestration/self_development/Start-AiOsApprovedAutonomyWorkerLaunch.APPLY.ps1"
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
        "$HumanOwnerWorkerLaunchApproval",
        "$WorkerPosture",
        "$OperatingProfile",
        "$WorkerCount",
        "$MaxParallelWorkers",
        "$AllowedLanes",
        "$TimeboxMinutes",
        "$StopOnFirstFailure",
        "$IdentitySpineStatus",
        "$ValidatorChainStatus",
        "$ApprovalSosStatus",
        "$PreflightDecision",
        "$LaunchGuardDecision",
        "$ResearchPlan",
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


def test_runner_console_summary_includes_launch_decision_and_next_safe_action() -> None:
    text = RUNNER.read_text(encoding="utf-8")

    assert "LAUNCH DECISION" in text
    assert "launch_decision:" in text
    assert "NEXT SAFE ACTION" in text


def test_runner_safety_text_never_starts_runtime_or_scheduler() -> None:
    text = RUNNER.read_text(encoding="utf-8")

    assert "starts_runtime" in text
    assert "launches_workers" in text
    assert "enables_scheduler" in text
    assert "starts_daemon" in text
    assert "Start-Process" not in text


def test_status_recommendation_surfaces_controller_availability_without_apply() -> None:
    text = RECOMMENDATION.read_text(encoding="utf-8")

    assert "FULL AUTONOMY WORKER LAUNCH" in text
    assert "approved_launch_controller" in text
    assert "forex_research_pipeline" in text
    assert "worker_launch_allowed_now = $false" in text
    assert "starts_apply = $false" in text
    assert "writes_ledger = $false" in text
    assert "launches_workers = $false" in text
