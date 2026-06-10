"""Tests for forex builder lane dry-run planning."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "automation/orchestration/forex_builder_lane/New-AiOsForexBuilderPlan.DRY_RUN.ps1"


def run_plan(goal: str, *, report_root: Path) -> subprocess.CompletedProcess[str]:
    json_path = report_root / "plan.json"
    md_path = report_root / "plan.md"
    return subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-GoalText",
            goal,
            "-OutputJsonPath",
            str(json_path),
            "-OutputMarkdownPath",
            str(md_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_forex_builder_plan_maps_safe_categories(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir(parents=True, exist_ok=True)
    result = run_plan("Build paper replay and latency ledger with regime filter and route preview", report_root=report_root)
    assert result.returncode == 0, result.stdout + result.stderr

    payload = json.loads(result.stdout.strip())
    assert payload["mode"] == "paper_only_plan"
    assert payload["paper_only"] is True
    assert "paper_replay" in payload["mapped_categories"]
    assert "latency_ledger" in payload["mapped_categories"]
    assert "regime_filter" in payload["mapped_categories"]
    assert "paper_route_preview" in payload["mapped_categories"]

    md = report_root / "plan.md"
    j = report_root / "plan.json"
    assert md.exists()
    assert j.exists()
    md_text = md.read_text(encoding="utf-8")
    assert "Paper-only" in md_text
    for token in ["merge", "apply", "live trading", "broker", "credential", "secret", "real order"]:
        for action in payload["next_actions"]:
            assert token not in action["safe_command"].lower()

    packet = payload["packet_metadata"]
    assert packet["packet_path"]
    assert "paper-only" in packet["packet_text"].lower()
    assert "no live trading" in packet["packet_text"].lower()


def test_forex_builder_plan_blocks_forbidden_terms(tmp_path: Path) -> None:
    report_root = tmp_path / "reports_block"
    report_root.mkdir(parents=True, exist_ok=True)
    result = run_plan("Enable live trading with real broker execution and real orders", report_root=report_root)
    assert result.returncode == 1
    payload = json.loads(result.stdout.strip())
    assert payload["can_progress"] is False
    assert payload["blocked_keywords"]
    assert any("live" in item.lower() for item in payload["blocked_keywords"])
