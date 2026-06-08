from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief import hrq001_duplicate_retirement_plan as plan


CANONICAL_TEXT = """# AI_OS Worker Branch And Lane Rules

## Branch Naming

Recommended branch pattern:

```text
worker/<lane>/<phase>-<short-task>
```

Legacy worker branch examples for human review:

```text
worker/work-intelligence/phase-21-branch-rules
worker/operator-orchestration/phase-22-file-ownership
worker/dashboard-ui/phase-15-centerpiece-review
```

## Collision Handling

Worker reports should include planned files and validation commands. The integration lane checks those reports before any merge or APPLY review.
"""


DUPLICATE_TEXT = """> Historical/reference-only legacy AI_OS document.

# AI_OS Worker Branch And Lane Rules

## Branch Naming

Examples:

```text
worker/work-intelligence/phase-21-branch-rules
worker/operator-orchestration/phase-22-file-ownership
worker/dashboard-ui/phase-15-centerpiece-review
```

## Required Worker Metadata

Each worker lane should declare worker metadata before APPLY review.

## Allowed Worker Lanes

Allowed worker lanes are Work Intelligence, Operator Orchestration, and Dashboard UI.

## Path Rules

Workers must stay inside allowed paths.

## Report Rules

Each worker report must include planned files and validation commands. The integration lane checks those reports before any merge or APPLY review.

## Safety

This document does not create branches, worktrees, commits, or pushes.
"""


def _write_docs(repo_root: Path, with_reference: bool = True) -> None:
    canonical = repo_root / plan.CANONICAL_FILE
    duplicate = repo_root / plan.DUPLICATE_FILE
    canonical.parent.mkdir(parents=True, exist_ok=True)
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    canonical.write_text(CANONICAL_TEXT, encoding="utf-8")
    duplicate.write_text(DUPLICATE_TEXT, encoding="utf-8")
    if with_reference:
        ref = repo_root / "docs/workflows/reference.md"
        ref.parent.mkdir(parents=True, exist_ok=True)
        ref.write_text("See docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md", encoding="utf-8")


def test_plan_identifies_canonical_and_duplicate_paths(tmp_path: Path) -> None:
    _write_docs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()

    assert result["canonical_path"] == "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md"
    assert result["duplicate_path"] == "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md"
    assert result["report_type"] == "operator_relief_hrq001_duplicate_retirement_plan_v1"


def test_plan_detects_content_absorbed_into_canonical(tmp_path: Path) -> None:
    _write_docs(tmp_path)
    absorbed = plan.build_plan(tmp_path).to_dict()["content_already_absorbed_into_canonical"]

    absorbed_names = {item["absorbed_content"] for item in absorbed}
    assert "legacy worker branch examples" in absorbed_names
    assert "concise integration-lane report check wording" in absorbed_names


def test_plan_identifies_unique_content_remaining_in_duplicate(tmp_path: Path) -> None:
    _write_docs(tmp_path)
    remaining = plan.build_plan(tmp_path).to_dict()["unique_content_remaining_in_duplicate"]
    sections = {item["section"] for item in remaining}

    assert "Required Worker Metadata" in sections
    assert "Allowed Worker Lanes" in sections
    assert "Path Rules" in sections
    assert "Safety" in sections


def test_plan_marks_prune_candidates_as_later_only(tmp_path: Path) -> None:
    _write_docs(tmp_path)
    candidates = plan.build_plan(tmp_path).to_dict()["content_safe_to_prune_later"]

    assert candidates
    assert all(item["safe_to_prune_later"] is False for item in candidates)
    assert any(item["section"] == "Required Worker Metadata" for item in candidates)


def test_plan_finds_references_to_duplicate(tmp_path: Path) -> None:
    _write_docs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()

    references = result["references_that_point_to_duplicate"]
    assert references
    assert result["references_found_count"] == len(references)
    assert references == result["references_that_must_be_updated_before_retirement"]
    assert any(item["path"] == "docs/workflows/reference.md" for item in references)


def test_plan_recommends_deprecation_notice_when_references_exist(tmp_path: Path) -> None:
    _write_docs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()

    assert result["recommended_option"] == "REPLACE_WITH_DEPRECATION_NOTICE_LATER"


def test_plan_keeps_delete_and_apply_blocked(tmp_path: Path) -> None:
    _write_docs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()

    assert result["executable"] is False
    assert result["delete_ready"] is False
    assert result["apply_ready_paths"] == []
    assert result["safety"]["workflow_docs_modified"] is False
    assert result["safety"]["duplicate_file_modified"] is False
    assert result["safety"]["files_deleted"] is False
    assert result["safety"]["hrq002_touched"] is False
    assert result["safety"]["hrq003_touched"] is False


def test_retirement_options_include_required_values(tmp_path: Path) -> None:
    _write_docs(tmp_path)
    options = plan.build_plan(tmp_path).to_dict()["retirement_options"]

    assert options == [
        "KEEP_AS_REFERENCE_ONLY",
        "REPLACE_WITH_DEPRECATION_NOTICE_LATER",
        "ARCHIVE_AFTER_REFERENCE_UPDATE",
        "DELETE_AFTER_REFERENCE_UPDATE",
    ]


def test_write_reports_writes_only_under_duplicate_retirement_root(tmp_path: Path) -> None:
    _write_docs(tmp_path)
    result = plan.build_plan(tmp_path)
    written = plan.write_reports(result, tmp_path)

    assert [path.name for path in written] == ["hrq001_duplicate_retirement_plan.json", "hrq001_duplicate_retirement_plan.md"]
    assert all(path.resolve().parent == (tmp_path / plan.OUTPUT_ROOT).resolve() for path in written)
    payload = json.loads(written[0].read_text(encoding="utf-8"))
    assert payload["delete_ready"] is False


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/hrq001_duplicate_retirement_plan.py").read_text(encoding="utf-8")
    forbidden_terms = [
        "subprocess",
        "os.system",
        "Popen",
        "rmtree",
        "shutil.move",
        ".rename(",
        "Path.unlink",
        "git commit",
        "git push",
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
