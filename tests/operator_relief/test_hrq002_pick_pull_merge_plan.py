from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief import hrq002_pick_pull_merge_plan as plan


DUPLICATE_TEXT = """# AI_OS Parallel Codex Crew Workflow

## Purpose

This workflow defines a supervised operator pattern for running 8 parallel DRY_RUN Codex worker lanes and 1 controlled serial APPLY lane.

## Worker Lanes

| Worker | Lane | Scope |
| --- | --- | --- |
| 1 | Dashboard UI | `apps/dashboard` |

## Start DRY_RUN Crew

The launcher opens 8 labeled PowerShell windows and uses fallback mode when disabled.

## Worker Report Contract

Each worker should produce a JSON report.

## Validate Worker Reports

The validator checks registry, queue example, exactly 8 workers, fallback mode, no overlaps, and no deletes.

## Controlled APPLY Lane

The controlled lane asks before each APPLY and validates after each APPLY.

## Git Rules

Do not use `git add .`. Do not push until the operator approves one final push.

## Safety Rules

No protected root files. No secrets. No commit from the scripts.

## Standard Batch Validation

Run `git diff --check` and `git status --short --branch`.
"""


def _write_inputs(repo_root: Path) -> None:
    duplicate = repo_root / plan.DUPLICATE_FILE
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(DUPLICATE_TEXT, encoding="utf-8")
    diff_path = repo_root / plan.DECISION_DIFF_PATH
    diff_path.parent.mkdir(parents=True, exist_ok=True)
    diff_path.write_text(
        json.dumps(
            {
                "conflicting_sections": [
                    {
                        "canonical_heading": "Purpose",
                        "duplicate_heading": "Purpose",
                        "reason": "Shared heading has materially different content.",
                    },
                    {
                        "canonical_heading": "Safety Rules",
                        "duplicate_heading": "Safety Rules",
                        "reason": "Shared heading has materially different content.",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )


def test_plan_identifies_candidate_and_paths(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()

    assert result["candidate_id"] == "HRQ-002-parallel_codex_workflow"
    assert result["canonical_file"] == "docs/workflows/PARALLEL_CODEX_WORKFLOW.md"
    assert result["duplicate_file"] == "docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md"


def test_plan_identifies_unique_sections_to_pull(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    sections = {item["source_section"] for item in plan.build_plan(tmp_path).to_dict()["unique_sections_to_pull_into_canonical"]}

    assert "Worker Lanes" in sections
    assert "Start DRY_RUN Crew" in sections
    assert "Validate Worker Reports" in sections
    assert "Controlled APPLY Lane" in sections
    assert "Git Rules" in sections
    assert "Standard Batch Validation" in sections


def test_plan_identifies_sections_already_covered(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    covered = {item["duplicate_section"] for item in plan.build_plan(tmp_path).to_dict()["sections_already_covered"]}

    assert "Purpose" in covered
    assert "Safety Rules" in covered
    assert "Worker Report Contract" not in covered


def test_plan_identifies_conflicts_from_decision_diff(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    conflicts = plan.build_plan(tmp_path).to_dict()["conflicting_sections_needing_human_review"]

    assert any(item["section"] == "Purpose / Purpose" for item in conflicts)
    assert any(item["section"] == "Safety Rules / Safety Rules" for item in conflicts)
    assert all(item["human_review_required"] is True for item in conflicts)


def test_plan_identifies_obsolete_sections_to_prune_later(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    obsolete = {item["duplicate_section"] for item in plan.build_plan(tmp_path).to_dict()["obsolete_sections_to_prune_later"]}

    assert "Historical/reference-only legacy preamble" in obsolete
    assert "Purpose" in obsolete
    assert "Safety Rules" in obsolete


def test_output_contract_blocks_apply_and_source_mutation(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()
    safety = result["safety"]

    assert result["executable"] is False
    assert result["apply_ready_paths"] == []
    assert safety["workflow_docs_modified"] is False
    assert safety["files_deleted"] is False
    assert safety["canonicalization_performed"] is False
    assert safety["executable_apply_packet_generated"] is False
    assert safety["hrq001_touched"] is False
    assert safety["hrq003_touched"] is False


def test_write_reports_writes_only_under_hrq002_root(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path)
    written = plan.write_reports(result, tmp_path)

    assert [path.name for path in written] == ["hrq002_pick_pull_merge_plan.json", "hrq002_pick_pull_merge_plan.md"]
    assert all(path.resolve().parent == (tmp_path / plan.OUTPUT_ROOT).resolve() for path in written)
    payload = json.loads(written[0].read_text(encoding="utf-8"))
    assert payload["executable"] is False


def test_markdown_contains_expected_sections(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    markdown = plan.render_markdown(plan.build_plan(tmp_path))

    assert "# HRQ-002 Pick-and-Pull Merge Plan" in markdown
    assert "## Unique Sections To Pull" in markdown
    assert "## Blocked Actions" in markdown


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/hrq002_pick_pull_merge_plan.py").read_text(encoding="utf-8")
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
