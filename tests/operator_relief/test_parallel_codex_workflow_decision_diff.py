import json
from pathlib import Path

from automation.operator_relief.parallel_codex_workflow_decision_diff import (
    KEEP_WORKFLOWS_AS_CANONICAL,
    MERGE_UNIQUE_CONTENT_FIRST,
    NEEDS_HUMAN_REVIEW,
    build_decision_diff,
    write_report,
)


CANONICAL_PATH = "docs/workflows/PARALLEL_CODEX_WORKFLOW.md"
DUPLICATE_PATH = "docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md"
PACKET_PATH = "Reports/operator_relief/decision_packets/canonical_decision_packet_02_parallel_codex_workflow.json"


BASE_DOC = """# AI_OS Parallel Codex Workflow

## Purpose

This workflow defines supervised parallel DRY_RUN lanes and a controlled serial APPLY lane.

## Lane Model

- DRY_RUN workers may inspect and plan in parallel.
- APPLY work must be serialized.

## Validation

Run `git diff --check`.
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_packet(repo: Path) -> None:
    payload = {
        "report_type": "operator_relief_canonical_decision_packet_v1",
        "executable": False,
        "current_canonical_candidate": CANONICAL_PATH,
        "duplicate_candidates": [DUPLICATE_PATH],
        "dependencies": [],
    }
    _write(repo / PACKET_PATH, json.dumps(payload, indent=2))


def _sample_repo(tmp_path: Path, canonical: str = BASE_DOC, duplicate: str = BASE_DOC) -> Path:
    _write(tmp_path / CANONICAL_PATH, canonical)
    _write(tmp_path / DUPLICATE_PATH, duplicate)
    _write_packet(tmp_path)
    return tmp_path


def test_detects_identical_docs(tmp_path: Path) -> None:
    result = build_decision_diff(_sample_repo(tmp_path))

    assert result.identical is True
    assert result.recommended_human_decision == KEEP_WORKFLOWS_AS_CANONICAL


def test_detects_duplicate_only_section(tmp_path: Path) -> None:
    duplicate = BASE_DOC + "\n## Worker Lanes\n\nEach worker has a lane and scope.\n"

    result = build_decision_diff(_sample_repo(tmp_path, duplicate=duplicate))

    assert any(section["heading"] == "Worker Lanes" for section in result.duplicate_only_sections)


def test_detects_canonical_only_section(tmp_path: Path) -> None:
    canonical = BASE_DOC + "\n## Worker Report Contract\n\nReports should include planned files.\n"

    result = build_decision_diff(_sample_repo(tmp_path, canonical=canonical))

    assert any(section["heading"] == "Worker Report Contract" for section in result.canonical_only_sections)


def test_detects_conflicting_section(tmp_path: Path) -> None:
    duplicate = BASE_DOC.replace("APPLY work must be serialized.", "APPLY work may run in parallel.")

    result = build_decision_diff(_sample_repo(tmp_path, duplicate=duplicate))

    assert any(section["section_key"] == "lane model" for section in result.conflicting_sections)


def test_detects_duplicate_unique_authority(tmp_path: Path) -> None:
    duplicate = BASE_DOC + "\n## Controlled APPLY Lane\n\nThe operator must approve before git commit or push.\n"

    result = build_decision_diff(_sample_repo(tmp_path, duplicate=duplicate))

    assert any(section["heading"] == "Controlled APPLY Lane" for section in result.duplicate_unique_authority)


def test_recommends_merge_unique_content_first_when_duplicate_has_unique_content(tmp_path: Path) -> None:
    duplicate = BASE_DOC + "\n## Worker Lanes\n\nEach worker must declare allowed paths and blocked paths.\n"

    result = build_decision_diff(_sample_repo(tmp_path, duplicate=duplicate))

    assert result.recommended_human_decision == MERGE_UNIQUE_CONTENT_FIRST


def test_recommends_needs_human_review_when_conflicts_exist(tmp_path: Path) -> None:
    duplicate = BASE_DOC.replace("APPLY work must be serialized.", "APPLY work may run in parallel.")

    result = build_decision_diff(_sample_repo(tmp_path, duplicate=duplicate))

    assert result.recommended_human_decision == NEEDS_HUMAN_REVIEW
    assert result.safe_to_generate_apply_packet_later is False


def test_writes_only_under_reports_operator_relief_decision_packets(tmp_path: Path) -> None:
    repo = _sample_repo(tmp_path)
    result = build_decision_diff(repo)

    written = write_report(result, repo)

    assert written == repo / "Reports/operator_relief/decision_packets/parallel_codex_workflow_decision_diff.json"
    assert written.exists()


def test_executable_false(tmp_path: Path) -> None:
    result = build_decision_diff(_sample_repo(tmp_path))

    assert result.executable is False
    assert result.to_dict()["executable"] is False


def test_source_scan_proves_no_forbidden_execution_paths() -> None:
    source = Path("automation/operator_relief/parallel_codex_workflow_decision_diff.py").read_text(encoding="utf-8")
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
