from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "forex_delivery" / "Invoke-AiOsDemoDayEvidenceRun.ps1"


def script_text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_script_exists() -> None:
    assert SCRIPT.exists()


def test_script_contains_checked_native_guard_and_duplicate_block_markers() -> None:
    text = script_text()
    lowered = text.lower()

    assert "function invoke-checkednative" in lowered
    assert 'psobject.properties["record_type"]' in lowered
    assert "day_evidence_append_blocked=duplicate_real_demo_day" in lowered
    assert "action=verdict_only" in lowered


def test_script_avoids_unsafe_direct_record_type_access_and_enforces_post_apply_scope() -> None:
    text = script_text()
    lowered = text.lower()

    assert ".record_type" not in lowered
    assert "git status --short --untracked-files=all" in lowered
    assert "git diff --cached --name-only" in lowered
    assert "no_git_diff_after_demo_append" in lowered


def test_script_does_not_attempt_push_or_pr_creation() -> None:
    lowered = script_text().lower()

    assert "git push" not in lowered
    assert "gh pr create" not in lowered
