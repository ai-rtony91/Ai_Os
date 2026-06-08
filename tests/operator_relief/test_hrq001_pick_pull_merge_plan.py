from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief import hrq001_pick_pull_merge_plan as plan


CANONICAL_TEXT = """# AI_OS Worker Branch And Lane Rules

## Purpose

Canonical safety text.

## Branch Naming

Canonical branch naming.

## Required Lane Metadata

Canonical metadata.

## Allowed Worker Lanes

Canonical lanes.

## Path Ownership

Canonical path ownership.

## Collision Handling

Canonical collision handling.

## Validation

Canonical validation.
"""


DUPLICATE_TEXT = """# AI_OS Worker Branch And Lane Rules

## Purpose

Duplicate purpose.

## Branch Naming

Examples:

```text
worker/work-intelligence/phase-21-branch-rules
```

## Required Worker Metadata

Duplicate metadata.

## Allowed Worker Lanes

Legacy lanes.

## Path Rules

Duplicate path rules.

## Report Rules

The integration lane checks those reports before any merge or APPLY review.

## Safety

Duplicate safety.

## Validation

Duplicate validation.
"""


def _write_inputs(repo_root: Path) -> None:
    canonical = repo_root / plan.CANONICAL_FILE
    duplicate = repo_root / plan.DUPLICATE_FILE
    diff = repo_root / plan.DECISION_DIFF_PATH
    canonical.parent.mkdir(parents=True, exist_ok=True)
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    diff.parent.mkdir(parents=True, exist_ok=True)
    canonical.write_text(CANONICAL_TEXT, encoding="utf-8")
    duplicate.write_text(DUPLICATE_TEXT, encoding="utf-8")
    diff.write_text(
        json.dumps(
            {
                "conflicting_sections": [
                    {
                        "canonical_heading": "Purpose",
                        "duplicate_heading": "Purpose",
                        "reason": "Shared heading differs.",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def test_plan_reports_hrq001_canonical_and_duplicate_paths(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()

    assert result["canonical_file"] == "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md"
    assert result["duplicate_file"] == "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md"
    assert result["source_decision_diff"] == "Reports/operator_relief/decision_packets/worker_branch_lane_rules_decision_diff.json"


def test_plan_identifies_sections_already_covered(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()
    covered = {item["duplicate_section"]: item["canonical_coverage"] for item in result["sections_already_covered"]}

    assert covered["Required Worker Metadata"] == "Required Lane Metadata"
    assert covered["Path Rules"] == "Path Ownership"
    assert covered["Report Rules"] == "Required Lane Metadata and Collision Handling"
    assert covered["Safety"] == "Purpose and Validation"


def test_plan_identifies_unique_sections_to_pull(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()
    pull_sections = {item["source_section"]: item for item in result["unique_sections_to_pull_into_canonical"]}

    assert "Branch Naming" in pull_sections
    assert "worker/work-intelligence/phase-21-branch-rules" in pull_sections["Branch Naming"]["content_preview"]
    assert "Report Rules" in pull_sections
    assert pull_sections["Report Rules"]["human_review_required"] is True


def test_plan_identifies_conflicts_from_decision_diff(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()

    assert result["conflicting_sections_needing_human_review"] == [
        {
            "section": "Purpose / Purpose",
            "reason": "Shared heading differs.",
            "human_review_required": True,
        }
    ]


def test_plan_identifies_obsolete_sections_to_prune_later(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()
    prune_sections = [item["duplicate_section"] for item in result["obsolete_sections_to_prune_later"]]

    assert "Historical/reference-only legacy preamble" in prune_sections
    assert "Required Worker Metadata" in prune_sections
    assert "Path Rules" in prune_sections
    assert "Safety" in prune_sections


def test_plan_includes_merge_order_validation_and_rollback(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()

    assert result["recommended_merge_order"]
    assert "python -m pytest tests/operator_relief/test_hrq001_pick_pull_merge_plan.py" in result["validation_commands"]
    assert "No rollback needed for this DRY_RUN report because workflow docs are not modified." in result["rollback_plan"]


def test_output_contract_is_review_only_and_not_apply_ready(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()

    assert result["executable"] is False
    assert result["apply_ready_paths"] == []
    assert result["safety"]["review_plan_only"] is True
    assert result["safety"]["workflow_docs_modified"] is False
    assert result["safety"]["files_deleted"] is False
    assert result["safety"]["canonicalization_performed"] is False
    assert result["safety"]["executable_apply_packet_generated"] is False
    assert result["safety"]["protected_docs_modified"] is False
    assert result["safety"]["hrq002_touched"] is False
    assert result["safety"]["hrq003_touched"] is False


def test_write_reports_writes_json_and_markdown_under_output_root(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path)
    written = plan.write_reports(result, tmp_path)

    assert [path.name for path in written] == [
        "hrq001_pick_pull_merge_plan.json",
        "hrq001_pick_pull_merge_plan.md",
    ]
    for path in written:
        assert path.resolve().parent == (tmp_path / plan.OUTPUT_ROOT).resolve()


def test_markdown_contains_review_plan_sections(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    markdown = plan.render_markdown(plan.build_plan(tmp_path))

    assert "# HRQ-001 Pick-and-Pull Merge Plan" in markdown
    assert '"executable": false' in markdown
    assert "## Unique Sections To Pull" in markdown
    assert "## Obsolete Sections To Prune Later" in markdown


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/hrq001_pick_pull_merge_plan.py").read_text(encoding="utf-8")
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
