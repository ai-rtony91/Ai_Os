import json
from pathlib import Path

from automation.operator_relief.repo_audit_engine import run_repo_audit, write_audit_report


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def _sample_repo(tmp_path: Path) -> Path:
    _write(
        tmp_path / "docs/workflows/startup-a.md",
        """
# Startup Procedure
Follow these steps to start AI_OS.
Step one: open the runtime bridge.
Step two: review approval.
See docs/workflows/missing-guide.md.

## Approval Chain
Human owner approves the execution workflow.
        """,
    )
    _write(
        tmp_path / "docs/workflows/startup-b.md",
        """
# Startup Procedure
Follow these steps to start AI_OS.
Step one: open the runtime bridge.
Step two: review approval.
See docs/workflows/startup-a.md.

## Approval Chain
Human owner approves the execution workflow.
        """,
    )
    _write(
        tmp_path / "docs/workflows/startup-drift.md",
        """
# Startup Procedure
Follow a different set of steps to start AI_OS.
Step one: open the manual checklist.
Step two: hold runtime automation.
        """,
    )
    _write(
        tmp_path / "docs/workflows/authority-a.md",
        """
# Source of Truth
This file is the canonical authority and workflow owner for startup.
        """,
    )
    _write(
        tmp_path / "docs/workflows/authority-b.md",
        """
# Source of Truth
This file is the canonical authority and workflow owner for execution.
        """,
    )
    _write(
        tmp_path / "docs/workflows/orphan.md",
        """
# Abandoned Report
This document has no inbound reference and no outbound reference.
        """,
    )
    _write(
        tmp_path / "docs/governance/forbidden.md",
        """
# Startup Procedure
This forbidden governance file must not be scanned.
        """,
    )
    _write(
        tmp_path / "Reports/operator_relief/audits/generated.md",
        """
# Startup Procedure
Generated runtime report output must not be scanned.
        """,
    )
    _write(
        tmp_path / "automation/operator_relief/audit_target.json",
        '{"name": "operator workflow", "reference": "docs/workflows/startup-a.md"}',
    )
    return tmp_path


def _report(tmp_path: Path) -> dict:
    return run_repo_audit(_sample_repo(tmp_path)).to_dict()


def test_duplicate_heading_detection(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert any(
        item["heading_text"] == "Startup Procedure" and item["occurrence_count"] >= 3
        for item in report["duplicate_headings"]
    )


def test_near_duplicate_heading_detection_for_small_candidate_groups(tmp_path: Path) -> None:
    repo = _sample_repo(tmp_path)
    _write(
        repo / "docs/workflows/near-heading.md",
        """
# Startup Procedures
This is close enough to the startup procedure heading to be reviewed.
        """,
    )

    report = run_repo_audit(repo).to_dict()

    assert any(
        item.get("near_heading_text") == "Startup Procedures"
        or item["heading_text"] == "Startup Procedures"
        for item in report["duplicate_headings"]
    )


def test_large_heading_set_uses_capped_comparisons(tmp_path: Path) -> None:
    repo = _sample_repo(tmp_path)
    large_headings = "\n".join(
        f"# Topic {index:04d}\nLarge heading body {index}."
        for index in range(300)
    )
    _write(repo / "docs/workflows/large-heading-set.md", large_headings)

    report = run_repo_audit(repo).to_dict()
    summary = report["audit_summary"]

    assert summary["headings_scanned"] >= 300
    assert summary["heading_comparisons_performed"] <= summary["heading_comparison_cap"]
    assert summary["heading_comparisons_performed"] < 300 * 299 / 2
    assert summary["near_heading_bucket_truncation_hit"] is True


def test_duplicate_section_detection(tmp_path: Path) -> None:
    report = _report(tmp_path)

    duplicate = next(
        item
        for item in report["duplicate_sections"]
        if item["section_title"] == "Approval Chain"
    )
    assert duplicate["similarity_score"] == 1.0
    assert sorted(duplicate["source_files"]) == [
        "docs/workflows/startup-a.md",
        "docs/workflows/startup-b.md",
    ]


def test_orphan_detection(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert any(
        item["orphan_candidate"] == "docs/workflows/orphan.md"
        for item in report["orphan_documents"]
    )


def test_broken_reference_detection(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert any(
        item["broken_reference"] == "docs/workflows/missing-guide.md"
        and item["source_file"] == "docs/workflows/startup-a.md"
        for item in report["broken_references"]
    )


def test_workflow_duplicate_detection(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert any(
        item["workflow_name"] == "startup" and len(item["duplicate_locations"]) >= 2
        for item in report["workflow_duplicates"]
    )


def test_drift_detection(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert any(
        item["drift_group"] == "Startup Procedure"
        and "docs/workflows/startup-drift.md" in item["files_involved"]
        for item in report["document_drift"]
    )


def test_authority_conflict_detection(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert any(
        "source of truth" in item["authority_candidates"]
        for item in report["source_of_truth_conflicts"]
    )


def test_json_report_generation(tmp_path: Path) -> None:
    repo = _sample_repo(tmp_path)
    report = run_repo_audit(repo)

    output_path = write_audit_report(report, repo)

    assert output_path.parent == repo / "Reports/operator_relief/audits"
    assert output_path.suffix == ".json"
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["executable"] is False
    assert payload["audit_summary"]["report_type"] == "operator_relief_repo_audit_engine_v1"


def test_forbidden_paths_ignored(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert "docs/governance/forbidden.md" not in report["scanned_files"]


def test_generated_reports_operator_relief_output_is_skipped(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert "Reports/operator_relief/audits/generated.md" not in report["scanned_files"]


def test_executable_false(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert report["executable"] is False
    assert report["audit_summary"]["executable"] is False
    assert all(value is False for value in report["safety"].values())


def test_run_repo_audit_does_not_mutate_files(tmp_path: Path) -> None:
    repo = _sample_repo(tmp_path)
    before = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())

    run_repo_audit(repo)

    after = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())
    assert after == before


def test_source_has_no_git_openai_codex_or_shell_execution_paths() -> None:
    source = Path("automation/operator_relief/repo_audit_engine.py").read_text(encoding="utf-8")

    forbidden_markers = [
        "subprocess",
        "os.system",
        "Popen",
        "git commit",
        "git push",
        "git merge",
        "git rebase",
        "OpenAI(",
        "openai.",
        "Codex(",
        "Start-Process",
        "HTTPServer",
        ".listen(",
        ".bind(",
    ]
    assert not any(marker in source for marker in forbidden_markers)
