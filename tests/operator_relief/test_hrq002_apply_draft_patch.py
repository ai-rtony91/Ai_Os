from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief import hrq002_apply_draft_patch as patch


CANONICAL_TEXT = """# AI_OS Parallel Codex Workflow

## Purpose

This workflow defines supervised parallel DRY_RUN lanes and a controlled serial APPLY lane.

## Lane Model

- DRY_RUN workers may inspect and plan in parallel when their scopes do not overlap.
- APPLY work must be serialized for overlapping files.

## Worker Report Contract

Worker reports should include planned files.

## Safety Rules

- No secrets.

## Validation

Run targeted validators.
"""


DUPLICATE_TEXT = """# AI_OS Parallel Codex Crew Workflow

## Purpose

This stale purpose must not be pulled.

## Worker Lanes

| Worker | Lane | Scope |
| --- | --- | --- |
| 1 | Dashboard UI | `apps/dashboard` |

## Start DRY_RUN Crew

The launcher opens 8 labeled PowerShell windows and uses fallback mode when disabled.

## Worker Report Contract

This duplicate report contract must not be pulled by this draft.

## Validate Worker Reports

The validator checks registry, queue example, exactly 8 workers, fallback mode, no overlaps, and no deletes.

## Controlled APPLY Lane

The controlled lane asks before each APPLY and validates after each APPLY.

## Git Rules

Do not use `git add .`. Use explicit file paths only.

## Safety Rules

This duplicate safety section must not be pulled.

## Standard Batch Validation

Run `git diff --check` and `git status --short --branch`.
"""


def _write_inputs(repo_root: Path) -> None:
    canonical = repo_root / patch.CANONICAL_FILE
    duplicate = repo_root / patch.DUPLICATE_FILE
    canonical.parent.mkdir(parents=True, exist_ok=True)
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    canonical.write_text(CANONICAL_TEXT, encoding="utf-8")
    duplicate.write_text(DUPLICATE_TEXT, encoding="utf-8")


def test_build_patch_reports_target_and_source_paths(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = patch.build_patch(tmp_path).to_dict()

    assert result["canonical_target"] == "docs/workflows/PARALLEL_CODEX_WORKFLOW.md"
    assert result["duplicate_source"] == "docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md"


def test_patch_includes_only_requested_sections(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = patch.build_patch(tmp_path).to_dict()
    included = [item["source_section"] for item in result["sections_included"]]

    assert included == [
        "Worker Lanes",
        "Start DRY_RUN Crew",
        "Validate Worker Reports",
        "Controlled APPLY Lane",
        "Git Rules",
        "Standard Batch Validation",
    ]
    assert "This stale purpose must not be pulled" not in result["patch_diff"]
    assert "This duplicate report contract must not be pulled" not in result["patch_diff"]
    assert "This duplicate safety section must not be pulled" not in result["patch_diff"]


def test_patch_adds_review_only_operational_details_after_lane_model(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    diff = patch.build_patch(tmp_path).to_dict()["patch_diff"]

    assert "## HRQ-002 Operational Details For Review" in diff
    assert "It is not active authority unless a future approved APPLY packet promotes exact text." in diff
    assert "### Worker Lanes" in diff
    assert "### Start DRY_RUN Crew" in diff
    assert "### Validate Worker Reports" in diff
    assert "### Controlled APPLY Lane" in diff
    assert "### Git Rules" in diff
    assert "### Standard Batch Validation" in diff


def test_patch_preserves_selected_content(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    diff = patch.build_patch(tmp_path).to_dict()["patch_diff"]

    assert "| 1 | Dashboard UI | `apps/dashboard` |" in diff
    assert "The launcher opens 8 labeled PowerShell windows" in diff
    assert "exactly 8 workers" in diff
    assert "asks before each APPLY" in diff
    assert "Do not use `git add .`" in diff
    assert "Run `git diff --check` and `git status --short --branch`." in diff


def test_draft_does_not_modify_canonical_file(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    before = (tmp_path / patch.CANONICAL_FILE).read_text(encoding="utf-8")
    patch.build_patch(tmp_path)
    after = (tmp_path / patch.CANONICAL_FILE).read_text(encoding="utf-8")

    assert after == before


def test_output_contract_is_not_executable_or_apply_ready(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = patch.build_patch(tmp_path).to_dict()
    safety = result["safety"]

    assert result["executable"] is False
    assert result["apply_ready_paths"] == []
    assert safety["patch_diff_only"] is True
    assert safety["workflow_docs_modified"] is False
    assert safety["files_deleted"] is False
    assert safety["canonicalization_performed"] is False
    assert safety["executable_apply_packet_generated"] is False
    assert safety["protected_docs_modified"] is False
    assert safety["hrq001_touched"] is False
    assert safety["hrq003_touched"] is False


def test_write_reports_writes_diff_json_and_markdown_under_output_root(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = patch.build_patch(tmp_path)
    written = patch.write_reports(result, tmp_path)

    assert [path.name for path in written] == [
        "hrq002_apply_draft_patch.diff",
        "hrq002_apply_draft_patch.json",
        "hrq002_apply_draft_patch.md",
    ]
    for path in written:
        assert path.resolve().parent == (tmp_path / patch.OUTPUT_ROOT).resolve()
    payload = json.loads(written[1].read_text(encoding="utf-8"))
    assert payload["executable"] is False
    assert payload["apply_ready_paths"] == []


def test_markdown_contains_diff_fence(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    markdown = patch.render_markdown(patch.build_patch(tmp_path))

    assert "# HRQ-002 Apply Draft Patch" in markdown
    assert '"executable": false' in markdown
    assert '"apply_ready_paths": []' in markdown
    assert "```diff" in markdown


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/hrq002_apply_draft_patch.py").read_text(encoding="utf-8")
    forbidden_terms = [
        "subprocess",
        "os.system",
        "Popen",
        "rmtree",
        "shutil.move",
        ".rename(",
        "Path.unlink",
        "git merge",
        "git rebase",
        "OpenAI(",
        "openai.",
        "Codex(",
        "Start-Process",
        "watchdog",
        "HTTPServer",
        ".listen(",
        ".bind(",
    ]

    for term in forbidden_terms:
        assert term not in source
