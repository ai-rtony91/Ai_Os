from __future__ import annotations

from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "automation/orchestration/self_development/Start-AiOsAutonomousForexResearchRun.APPLY.ps1"


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
        "$HumanOwnerResearchApproval",
        "$ResearchMode",
        "$Pair",
        "$Timeframe",
        "$StrategyProfile",
        "$BacktestWindow",
        "$SoakCycles",
        "$MaxRuntimeMinutes",
        "$StopOnFirstFailure",
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


def test_runner_console_summary_includes_mode_pair_timeframe_safety_and_next_action() -> None:
    text = RUNNER.read_text(encoding="utf-8")

    assert "research_mode:" in text
    assert "pair:" in text
    assert "timeframe:" in text
    assert "safety_status:" in text
    assert "next_safe_action:" in text


def test_runner_surface_blocks_live_broker_secret_paths() -> None:
    text = RUNNER.read_text(encoding="utf-8")

    assert "aios_autonomous_forex_research_pipeline.py" in text
    assert "Start-Process" not in text
    assert "OANDA" not in text
    assert "broker" not in text.lower()
