from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_pr_landing_preview.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_pr_landing_preview", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def pr_evidence(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "pr_number": 240,
        "pr_state": "OPEN",
        "mergeable": True,
        "draft": False,
        "checks_status": "success",
        "changed_files": [
            "automation/orchestration/aios_pr_landing_preview.py",
            "tests/orchestration/test_aios_pr_landing_preview.py",
            "docs/orchestration/AIOS_PR_LANDING_PREVIEW.md",
        ],
        "additions": 220,
        "deletions": 0,
        "base_branch": "main",
        "head_branch": "lane/pr-landing-preview",
        "validation_summary": "pytest passed",
        "safety_summary": "safe preview-only no protected action",
        "local_branch_status": "clean and synced with origin/main",
    }
    payload.update(overrides)
    return payload


def assert_preview_only(preview: dict[str, object]) -> None:
    assert preview["merge_allowed_by_policy"] is False
    assert preview["required_human_approval"] is True
    assert preview["commands_executed"] == []
    assert preview["merges_performed"] is False
    assert preview["pushes_performed"] is False
    assert preview["branches_deleted"] is False
    assert preview["resets_performed"] is False

    safety = preview["safety"]
    assert isinstance(safety, dict)
    assert safety["preview_only"] is True
    assert safety["required_human_approval"] is True
    assert safety["gh_execution"] is False
    assert safety["git_execution"] is False
    for key, value in safety.items():
        if key in {"preview_only", "required_human_approval"}:
            assert value is True
        else:
            assert value is False


def test_green_mergeable_pr_returns_ready() -> None:
    module = load_module()

    preview = module.build_pr_landing_preview(pr_evidence())

    assert preview["schema"] == "AIOS_PR_LANDING_PREVIEW.v1"
    assert preview["landing_status"] == "ready"
    assert preview["pr_number"] == 240
    assert preview["checks_required"] is True
    assert preview["checks_passed"] is True
    assert preview["scope_status"] == "safe"
    assert preview["safety_status"] == "safe"
    assert preview["blocked_reasons"] == []
    assert "Merge-AiOsPullRequest.DRY_RUN.ps1" in " ".join(preview["proposed_landing_commands"])
    assert not any(str(command).startswith("gh pr merge") for command in preview["proposed_landing_commands"])
    assert_preview_only(preview)


def test_pending_checks_returns_blocked() -> None:
    module = load_module()

    preview = module.build_pr_landing_preview(pr_evidence(checks_status="pending"))

    assert preview["landing_status"] == "blocked"
    assert preview["checks_passed"] is False
    assert "checks_not_passed:pending" in preview["blocked_reasons"]
    assert_preview_only(preview)


def test_failing_checks_returns_rejected() -> None:
    module = load_module()

    preview = module.build_pr_landing_preview(pr_evidence(checks_status="failed"))

    assert preview["landing_status"] == "rejected"
    assert preview["checks_passed"] is False
    assert "checks_failed" in preview["blocked_reasons"]
    assert_preview_only(preview)


def test_draft_pr_returns_blocked() -> None:
    module = load_module()

    preview = module.build_pr_landing_preview(pr_evidence(draft=True))

    assert preview["landing_status"] == "blocked"
    assert "draft_pr" in preview["blocked_reasons"]
    assert_preview_only(preview)


def test_non_mergeable_pr_returns_blocked() -> None:
    module = load_module()

    preview = module.build_pr_landing_preview(pr_evidence(mergeable=False))

    assert preview["landing_status"] == "blocked"
    assert "pr_not_mergeable:blocked" in preview["blocked_reasons"]
    assert_preview_only(preview)


def test_unsafe_changed_file_scope_returns_blocked() -> None:
    module = load_module()

    preview = module.build_pr_landing_preview(
        pr_evidence(changed_files=[".github/workflows/ci.yml"])
    )

    assert preview["landing_status"] == "blocked"
    assert preview["scope_status"] == "blocked"
    assert any(str(reason).startswith("unsafe_changed_file_scope:") for reason in preview["blocked_reasons"])
    assert_preview_only(preview)


def test_missing_pr_returns_no_pr() -> None:
    module = load_module()

    preview = module.build_pr_landing_preview({})

    assert preview["landing_status"] == "no_pr"
    assert preview["pr_number"] is None
    assert "missing_pr_evidence" in preview["blocked_reasons"]
    assert preview["proposed_landing_commands"] == ["gh pr list --state open --base main"]
    assert_preview_only(preview)


def test_required_contract_fields_are_present() -> None:
    module = load_module()

    preview = module.build_pr_landing_preview(pr_evidence())

    assert set(preview) >= {
        "schema",
        "landing_status",
        "pr_number",
        "merge_allowed_by_policy",
        "required_human_approval",
        "checks_required",
        "checks_passed",
        "scope_status",
        "safety_status",
        "blocked_reasons",
        "proposed_landing_commands",
        "forbidden_actions",
        "commands_executed",
        "branches_deleted",
        "merges_performed",
        "pushes_performed",
        "resets_performed",
        "safety",
        "next_safe_action",
    }
    assert "gh pr merge" in preview["forbidden_actions"]


def test_source_does_not_import_execution_network_or_file_write_tools() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in [
        "subprocess",
        "popen",
        "requests",
        "socket",
        "urllib",
        "http.client",
        "open(",
        "write_text",
        "write_bytes",
        "with open",
        "os.",
        "pathlib",
        "system(",
        "run(",
    ]:
        assert forbidden not in source
