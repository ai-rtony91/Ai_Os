"""Tests for the forex continuation DRY_RUN recommender."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "automation"
    / "orchestration"
    / "recommendations"
    / "Get-AiOsForexNextBuildPacket.DRY_RUN.ps1"
)


def _load_recommendation():
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(SCRIPT),
        "-OutputJson",
    ]
    raw = subprocess.check_output(cmd, text=True)
    return json.loads(raw.strip())


def test_forex_continuation_recommender_reports_known_sprints_and_recommendation():
    res = _load_recommendation()

    assert res["schema"] == "AIOS_FOREX_CONTINUATION_RECOMMENDATION.v1"
    assert res["execution_allowed"] is False
    assert res["human_approval_required"] is True
    assert res["forex_readiness_gate_present"] is True
    assert res["forex_signal_intake_ledger_present"] is True
    assert res["forex_risk_decision_router_present"] is True
    assert res["forex_continuity_review_present"] is True
    assert res["forex_study_journal_present"] is True
    assert res["latest_forex_sprint_detected"] == "SPRINT_18"
    assert res["recommended_next_packet_id"] == "AIOS-FOREX-PAPER-LEARNING-ACTION-ROUTER-APPLY-V1"
    assert res["recommended_next_packet_title"] == "feat(forex): add paper learning action router"
    assert res["recommended_lane"] == "PAPER_LEARNING_ACTION_ROUTER"


def test_forex_continuation_recommendation_contains_files_and_validators_and_blocked_actions():
    res = _load_recommendation()

    expected_files = [
        "automation/forex_engine/paper_learning_action_router.py",
        "automation/forex_engine/run_paper_learning_action_router_demo.py",
        "tests/forex_engine/test_paper_learning_action_router.py",
        "docs/AI_OS/trading/FOREX_ENGINE_V1_PAPER_LEARNING_ACTION_ROUTER.md",
    ]
    assert res["recommended_files"] == expected_files

    expected_validators = [
        "git diff --check",
        "python -m pytest tests/forex_engine -q -p no:cacheprovider",
        ".\\aios.ps1 -Mode status",
        "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-WorkerClaimCollision.DRY_RUN.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-LockRegistryIntegrity.DRY_RUN.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1",
    ]
    assert res["required_validators"] == expected_validators

    blocked_actions = set(res["blocked_actions"])
    for blocked in (
        "live trading",
        "broker APIs",
        "OANDA",
        "real orders",
        "webhooks",
        "real market data",
        "API keys/secrets",
        "scheduler/daemon",
        "runtime mutation",
        "telemetry mutation",
        "dashboard mutation",
        "Cloudflare",
        "backup sync",
        "push/PR/merge automation",
    ):
        assert blocked in blocked_actions
