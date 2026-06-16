from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE = REPO_ROOT / "automation" / "orchestration" / "continuation" / "aios_dirty_tree_classifier.py"
FIXED_NOW = "2026-06-14T12:00:00Z"


def _load():
    spec = importlib.util.spec_from_file_location("aios_dirty_tree_classifier", MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_safe_report_dirty_allows_dry_run_not_apply(tmp_path: Path) -> None:
    m = _load()

    result = m.build_dirty_tree_classification(
        status_lines=[
            "## main...origin/main",
            "?? Reports/aios_resume/state.json",
            "?? Reports/autonomy_decision_governor/latest.json",
            "?? Reports/forex_engine/.gitkeep",
        ],
        repo_root=tmp_path,
        generated_utc=FIXED_NOW,
    )

    assert result["overall_classification"] == "SAFE_DIRTY"
    assert result["safe_for_dry_run"] is True
    assert result["safe_for_apply"] is False
    assert {item["classification"] for item in result["dirty_files"]} == {"SAFE_REPORT_DIRTY"}


def test_safe_sandbox_preview_dirty_allows_dry_run(tmp_path: Path) -> None:
    m = _load()

    result = m.build_dirty_tree_classification(
        status_lines=[
            "?? Reports/sandbox/closed_autonomy_loop/latest.json",
            "?? automation/orchestration/work_packets/preview/PKT-EXAMPLE.txt",
        ],
        repo_root=tmp_path,
        generated_utc=FIXED_NOW,
    )

    assert result["overall_classification"] == "SAFE_DIRTY"
    assert result["safe_for_dry_run"] is True
    assert result["safe_for_apply"] is False
    assert {item["classification"] for item in result["dirty_files"]} == {"SAFE_SANDBOX_PREVIEW_DIRTY"}


def test_review_bridge_dirty_requires_review(tmp_path: Path) -> None:
    m = _load()

    result = m.build_dirty_tree_classification(
        status_lines=[
            "?? control/review_bridge/chatgpt_prompts/prompt.txt",
            "?? control/review_bridge/codex_reports/report.json",
        ],
        repo_root=tmp_path,
        generated_utc=FIXED_NOW,
    )

    assert result["overall_classification"] == "REVIEW_REQUIRED_DIRTY"
    assert result["review_required"] is True
    assert result["safe_for_dry_run"] is False
    assert {item["classification"] for item in result["dirty_files"]} == {"REVIEW_REQUIRED_DIRTY"}


def test_protected_authority_dirty_stops(tmp_path: Path) -> None:
    m = _load()

    result = m.build_dirty_tree_classification(
        status_lines=[" M AGENTS.md", "?? docs/governance/new-policy.md"],
        repo_root=tmp_path,
        generated_utc=FIXED_NOW,
    )

    assert result["overall_classification"] == "PROTECTED_AUTHORITY_DIRTY"
    assert result["protected_stop_required"] is True
    assert result["safe_for_dry_run"] is False
    assert {item["classification"] for item in result["dirty_files"]} == {"PROTECTED_AUTHORITY_DIRTY"}


def test_security_dirty_escalates_sos_without_values(tmp_path: Path) -> None:
    m = _load()
    key_name = "OPENAI_" + "API" + "_KEY"
    (tmp_path / "notes.txt").write_text(key_name + "=fake_value_for_scan", encoding="utf-8")

    result = m.build_dirty_tree_classification(
        status_lines=["?? notes.txt", "?? .env"],
        repo_root=tmp_path,
        generated_utc=FIXED_NOW,
    )
    dumped = json.dumps(result, sort_keys=True)

    assert result["overall_classification"] == "SECURITY_SOS_DIRTY"
    assert result["sos_required"] is True
    assert result["safe_for_dry_run"] is False
    assert "api_key_or_token_pattern" in dumped
    assert "env_file_or_env_pattern" in dumped
    assert "fake_value_for_scan" not in dumped


def test_unknown_dirty_requires_review(tmp_path: Path) -> None:
    m = _load()

    result = m.build_dirty_tree_classification(
        status_lines=["?? scratch/notes.md"],
        repo_root=tmp_path,
        generated_utc=FIXED_NOW,
    )

    assert result["overall_classification"] == "UNKNOWN_DIRTY"
    assert result["review_required"] is True
    assert result["dirty_files"][0]["path"] == "scratch/notes.md"


def test_clean_tree_is_apply_safe(tmp_path: Path) -> None:
    m = _load()

    result = m.build_dirty_tree_classification(
        status_lines=["## main...origin/main"],
        repo_root=tmp_path,
        generated_utc=FIXED_NOW,
    )

    assert result["overall_classification"] == "CLEAN"
    assert result["dirty_count"] == 0
    assert result["safe_for_dry_run"] is True
    assert result["safe_for_apply"] is True
