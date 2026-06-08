import json
from pathlib import Path

from automation.operator_relief.worker_branch_lane_rules_decision_diff import (
    KEEP_WORKFLOWS_AS_CANONICAL,
    MERGE_UNIQUE_CONTENT_FIRST,
    NEEDS_HUMAN_REVIEW,
    build_decision_diff,
    write_report,
)


CANONICAL_PATH = "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md"
DUPLICATE_PATH = "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md"
DEPENDENCY_PATH = "docs/audits/phase-5c-narrow-merge-plan.md"
PACKET_PATH = "Reports/operator_relief/decision_packets/canonical_decision_packet_01_worker_branch_and_lane_rules.json"


BASE_DOC = """# AI_OS Worker Branch And Lane Rules

## Purpose

This document defines branch and lane metadata rules.

## Allowed Worker Lanes

- Work Intelligence
- Operator Orchestration

## Validation

Run `git diff --check`.
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_packet(repo: Path, dependencies: list[str] | None = None) -> None:
    payload = {
        "report_type": "operator_relief_canonical_decision_packet_v1",
        "executable": False,
        "current_canonical_candidate": CANONICAL_PATH,
        "duplicate_candidates": [DUPLICATE_PATH],
        "dependencies": dependencies or [DEPENDENCY_PATH],
    }
    _write(repo / PACKET_PATH, json.dumps(payload, indent=2))


def _sample_repo(
    tmp_path: Path,
    canonical: str = BASE_DOC,
    duplicate: str = BASE_DOC,
    dependency: str = "# Phase 5C Narrow Merge Plan\n\nHistorical evidence only.\n",
) -> Path:
    _write(tmp_path / CANONICAL_PATH, canonical)
    _write(tmp_path / DUPLICATE_PATH, duplicate)
    _write(tmp_path / DEPENDENCY_PATH, dependency)
    _write_packet(tmp_path)
    return tmp_path


def test_detects_identical_docs(tmp_path: Path) -> None:
    result = build_decision_diff(_sample_repo(tmp_path))

    assert result.identical is True
    assert result.recommended_human_decision == KEEP_WORKFLOWS_AS_CANONICAL


def test_detects_duplicate_only_section(tmp_path: Path) -> None:
    duplicate = BASE_DOC + "\n## Legacy Extra Rule\n\nWorkers must declare planned files.\n"

    result = build_decision_diff(_sample_repo(tmp_path, duplicate=duplicate))

    assert any(section["heading"] == "Legacy Extra Rule" for section in result.duplicate_only_sections)


def test_detects_canonical_only_section(tmp_path: Path) -> None:
    canonical = BASE_DOC + "\n## Safe 8-Window Parallel Map\n\nSix workers need non-overlap.\n"

    result = build_decision_diff(_sample_repo(tmp_path, canonical=canonical))

    assert any(section["heading"] == "Safe 8-Window Parallel Map" for section in result.canonical_only_sections)


def test_detects_conflicting_section(tmp_path: Path) -> None:
    duplicate = BASE_DOC.replace("Run `git diff --check`.", "Run a different validator command.")

    result = build_decision_diff(_sample_repo(tmp_path, duplicate=duplicate))

    assert any(section["section_key"] == "validation" for section in result.conflicting_sections)
    assert result.recommended_human_decision == NEEDS_HUMAN_REVIEW


def test_detects_dependency_unique_authority(tmp_path: Path) -> None:
    dependency = """# Phase 5C Narrow Merge Plan

## Candidate 2: Worker Allowed Lane List

Recommendation: promote the allowed worker lanes to the target canonical workflow.
User decision is needed before changing authority.
"""

    result = build_decision_diff(_sample_repo(tmp_path, dependency=dependency))

    assert result.dependency_unique_authority


def test_recommends_merge_unique_content_first_when_duplicate_has_unique_content(tmp_path: Path) -> None:
    duplicate = BASE_DOC + "\n## Report Rules\n\nWorker reports must include planned files.\n"

    result = build_decision_diff(_sample_repo(tmp_path, duplicate=duplicate))

    assert result.recommended_human_decision == MERGE_UNIQUE_CONTENT_FIRST


def test_recommends_needs_human_review_when_dependency_has_unique_authority(tmp_path: Path) -> None:
    duplicate = BASE_DOC + "\n## Report Rules\n\nWorker reports must include planned files.\n"
    dependency = """# Phase 5C Narrow Merge Plan

## User Decisions Needed

Should worker lane names live permanently in docs/workflows or move to a worker registry?
"""

    result = build_decision_diff(_sample_repo(tmp_path, duplicate=duplicate, dependency=dependency))

    assert result.recommended_human_decision == NEEDS_HUMAN_REVIEW
    assert result.safe_to_generate_apply_packet_later is False


def test_writes_only_under_reports_operator_relief_decision_packets(tmp_path: Path) -> None:
    repo = _sample_repo(tmp_path)
    result = build_decision_diff(repo)

    written = write_report(result, repo)

    assert written == repo / "Reports/operator_relief/decision_packets/worker_branch_lane_rules_decision_diff.json"
    assert written.exists()


def test_executable_false(tmp_path: Path) -> None:
    result = build_decision_diff(_sample_repo(tmp_path))

    assert result.executable is False
    assert result.to_dict()["executable"] is False


def test_source_scan_proves_no_forbidden_execution_paths() -> None:
    source = Path("automation/operator_relief/worker_branch_lane_rules_decision_diff.py").read_text(encoding="utf-8")
    forbidden_markers = [
        "subprocess",
        "os.system",
        "Popen",
        "shutil.rmtree",
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
    assert not any(marker in source for marker in forbidden_markers)
