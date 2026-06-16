"""Tests for the supervised continuation DRY_RUN control loop."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "automation"
    / "orchestration"
    / "continuation"
    / "Get-AiOsSupervisedContinuationPlan.DRY_RUN.ps1"
)


def _load_plan(extra_args=None, repo_root=None, campaign_script=None, forex_script=None):
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(SCRIPT),
        "-OutputJson",
    ]
    if repo_root is not None:
        cmd.extend(["-RepoRoot", str(repo_root)])
    if campaign_script is not None:
        cmd.extend(["-CampaignTaskScript", str(campaign_script)])
    if forex_script is not None:
        cmd.extend(["-ForexRecommenderScript", str(forex_script)])
    if extra_args:
        cmd.extend(extra_args)
    raw = subprocess.check_output(cmd, text=True)
    return json.loads(raw.strip())


def _write_fake_recommender(
    path: Path,
    packet_id: str = "AIOS-FOREX-PAPER-LEARNING-ACTION-ROUTER-APPLY-V1",
    lane: str = "PAPER_LEARNING_ACTION_ROUTER",
    title: str = "feat(forex): add paper learning action router",
    latest_sprint: str = "SPRINT_18",
) -> Path:
    script = path / "Get-AiOsForexNextBuildPacket.DRY_RUN.ps1"
    fake_payload = json.dumps(
        {
            "_aios_parse_error": None,
            "schema": "AIOS_FOREX_CONTINUATION_RECOMMENDATION.v1",
            "execution_allowed": False,
            "human_approval_required": True,
            "latest_forex_sprint_detected": latest_sprint,
            "recommended_next_packet_id": packet_id,
            "recommended_next_packet_title": title,
            "recommended_lane": lane,
            "recommended_files": [
                "automation/forex_engine/paper_learning_action_router.py",
                "automation/forex_engine/run_paper_learning_action_router_demo.py",
                "tests/forex_engine/test_paper_learning_action_router.py",
                "docs/AI_OS/trading/FOREX_ENGINE_V1_PAPER_LEARNING_ACTION_ROUTER.md",
            ],
            "required_validators": [
                "git diff --check",
                "python -m pytest tests/forex_engine -q -p no:cacheprovider",
                ".\\aios.ps1 -Mode status",
                "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-WorkerClaimCollision.DRY_RUN.ps1",
                "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-LockRegistryIntegrity.DRY_RUN.ps1",
                "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1",
                "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1",
            ],
            "blocked_actions": [
                "live trading",
                "broker/OANDA",
                "real orders",
                "real webhooks",
                "real market data",
                "API keys/secrets",
                "scheduler/daemon",
                "worker launch",
                "runtime mutation",
                "telemetry mutation",
                "dashboard mutation",
                "Cloudflare",
                "backup sync",
                "push/PR/merge automation",
            ],
            "reason": "test",
            "next_safe_action": "Approve packet generation for supervised continuation after review.",
        }
    )
    script.write_text(
        f"""
param([switch]$OutputJson)
if ($OutputJson) {{
  Write-Output ('{fake_payload}')
}}
""",
        encoding="utf-8",
    )
    return script


def test_clean_repo_yields_ready_for_approval_with_recommendation(tmp_path):
    fake_repo = Path(tmp_path) / "workspace"
    fake_repo.mkdir()
    subprocess.check_call(["git", "init"], cwd=str(fake_repo), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.check_call(["git", "checkout", "-b", "main"], cwd=str(fake_repo), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    recommender_dir = Path(tmp_path) / "helpers"
    recommender_dir.mkdir()
    recommender_script = _write_fake_recommender(recommender_dir, latest_sprint="SPRINT_18")
    res = _load_plan(
        repo_root=fake_repo,
        forex_script=recommender_script,
        campaign_script="",
    )

    assert res["schema"] == "AIOS_SUPERVISED_CONTINUATION_PLAN.v1"
    assert res["mode"] == "DRY_RUN_READ_ONLY"
    assert res["execution_allowed"] is False
    assert res["human_approval_required"] is True
    assert res["can_continue_without_anthony"] is False
    assert res["autonomous_continuation_state"] in {"CONTINUE", "REVIEW_REQUIRED", "STOP", "SOS", "UNKNOWN"}
    assert res["autonomous_continuation_allowed"] is False
    assert res["continuation_status"] == "READY_FOR_APPROVAL"
    assert res["recommended_next_packet_id"] == "AIOS-FOREX-PAPER-LEARNING-ACTION-ROUTER-APPLY-V1"
    assert res["recommended_next_packet_title"] == "feat(forex): add paper learning action router"
    assert res["recommended_lane"] == "PAPER_LEARNING_ACTION_ROUTER"
    assert res["recommended_files"] == [
        "automation/forex_engine/paper_learning_action_router.py",
        "automation/forex_engine/run_paper_learning_action_router_demo.py",
        "tests/forex_engine/test_paper_learning_action_router.py",
        "docs/AI_OS/trading/FOREX_ENGINE_V1_PAPER_LEARNING_ACTION_ROUTER.md",
    ]
    assert any("git diff --check" == item for item in res["required_validators"])
    assert "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1" in res["required_validators"]


def test_clean_repo_exact_readiness_fields_and_blocked_actions(tmp_path):
    fake_repo = Path(tmp_path) / "workspace_supervised_readiness"
    fake_repo.mkdir()
    subprocess.check_call(["git", "init"], cwd=str(fake_repo), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.check_call(["git", "checkout", "-b", "main"], cwd=str(fake_repo), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    recommender_dir = Path(tmp_path) / "helpers_readiness"
    recommender_dir.mkdir()
    recommender_script = _write_fake_recommender(recommender_dir)
    res = _load_plan(
        repo_root=fake_repo,
        forex_script=recommender_script,
        campaign_script="",
    )

    assert isinstance(res["required_validators"], list) and res["required_validators"]
    assert isinstance(res["blocked_actions"], list) and res["blocked_actions"]
    for blocked in (
        "live trading",
        "broker/OANDA",
        "real orders",
        "real webhooks",
        "real market data",
        "API keys/secrets",
        "scheduler/daemon",
        "worker launch",
        "runtime mutation",
        "telemetry mutation",
        "dashboard mutation",
        "Cloudflare",
        "backup sync",
        "push/PR/merge automation",
    ):
        assert blocked in res["blocked_actions"]


def test_repo_dirty_state_transitions_to_review_required(tmp_path):
    root = Path(tmp_path)
    fake_repo = root / "workspace"
    fake_repo.mkdir()
    subprocess.check_call(["git", "init"], cwd=str(fake_repo), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.check_call(["git", "checkout", "-b", "main"], cwd=str(fake_repo), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Dirty and untracked marker files.
    (fake_repo / "dirty_file.txt").write_text("modify", encoding="utf-8")

    # Fake recommender output to keep domain logic deterministic without requiring full checkout.
    recommender_script = _write_fake_recommender(fake_repo)

    res = _load_plan(
        repo_root=fake_repo,
        forex_script=recommender_script,
        campaign_script="",
    )

    assert res["continuation_status"] in {"REVIEW_REQUIRED", "BLOCKED"}
    assert res["execution_allowed"] is False
    assert res["human_approval_required"] is True
    assert res["can_continue_without_anthony"] is False
    assert res["dirty_or_untracked_count"] >= 1


def test_safe_report_dirty_state_can_still_propose_dry_run_continuation(tmp_path):
    root = Path(tmp_path)
    fake_repo = root / "workspace_safe_report_dirty"
    fake_repo.mkdir()
    subprocess.check_call(["git", "init"], cwd=str(fake_repo), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.check_call(["git", "checkout", "-b", "main"], cwd=str(fake_repo), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    report_path = fake_repo / "Reports" / "sandbox" / "preview.json"
    report_path.parent.mkdir(parents=True)
    report_path.write_text('{"status":"preview"}', encoding="utf-8")

    recommender_dir = root / "helpers_safe_report_dirty"
    recommender_dir.mkdir()
    recommender_script = _write_fake_recommender(recommender_dir)

    res = _load_plan(
        repo_root=fake_repo,
        forex_script=recommender_script,
        campaign_script="",
    )

    assert res["continuation_status"] == "READY_FOR_APPROVAL"
    assert res["execution_allowed"] is False
    assert res["human_approval_required"] is True
    assert res["can_continue_without_anthony"] is False
    assert res["safe_dirty_continuation_allowed"] is True
    assert res["autonomous_job_continuation"]["schema"] == "AIOS_AUTONOMOUS_JOB_CONTINUATION_STATE.v1"
    assert res["dirty_tree_classification"]["overall_classification"] == "SAFE_DIRTY"
    assert res["dirty_tree_classification"]["safe_for_apply"] is False


def test_plan_command_is_read_only_for_current_repo():
    pre = subprocess.check_output(["git", "status", "--short", "--untracked-files=all"], text=True, cwd=str(SCRIPT.parents[2]))
    _ = _load_plan()
    post = subprocess.check_output(["git", "status", "--short", "--untracked-files=all"], text=True, cwd=str(SCRIPT.parents[2]))
    assert pre == post
