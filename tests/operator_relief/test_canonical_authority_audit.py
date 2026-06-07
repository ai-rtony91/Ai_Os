import json
from pathlib import Path

from automation.operator_relief.canonical_authority_audit import (
    REQUIRED_REPORT_FIELDS,
    run_canonical_authority_audit,
    write_canonical_authority_audit_report,
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def _sample_repo(tmp_path: Path) -> Path:
    _write(
        tmp_path / "Reports/operator_relief/audits/repo_audit_20260607T015736Z.json",
        json.dumps(
            {
                "duplicate_sections": [
                    {
                        "source_files": [
                            "docs/workflows/APPLY_ROUTING_CHAIN.md",
                            "docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md",
                        ]
                    }
                ],
                "document_drift": [
                    {
                        "files_involved": [
                            "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md",
                            "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md",
                        ]
                    }
                ],
                "workflow_duplicates": [],
                "source_of_truth_conflicts": [],
                "duplicate_headings": [],
                "orphan_documents": [],
                "broken_references": [],
                "audit_summary": {"files_scanned": 10, "headings_scanned": 20, "sections_scanned": 12},
            }
        ),
    )
    _write(
        tmp_path / "docs/workflows/APPLY_ROUTING_CHAIN.md",
        """
# Apply Routing Chain
This is the official apply routing workflow router and execution authority.
        """,
    )
    _write(
        tmp_path / "docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md",
        """
# Apply Routing Chain
This is a canonical apply routing workflow router and approval boundary.
        """,
    )
    _write(
        tmp_path / "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md",
        """
# Worker Branch And Lane Rules
Required branch rules, worker lanes, and protected root policy.
        """,
    )
    _write(
        tmp_path / "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md",
        """
# Worker Branch And Lane Rules
Primary branch rules and worker lanes standard.
        """,
    )
    _write(
        tmp_path / "docs/AI_OS/security/phase_15_secure_access/AIOS_PORTAL_ZONE_MODEL.md",
        """
# Portal Zone Model
Canonical access control boundary and approval requirements.
        """,
    )
    _write(
        tmp_path / "docs/AI_OS/security/secure_access/AIOS_PORTAL_ZONE_MODEL.md",
        """
# Portal Zone Model
Official access control boundary and protected file policy.
        """,
    )
    _write(
        tmp_path / "docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md",
        """
# File Placement Rules
Canonical governance authority for protected root placement.
        """,
    )
    _write(
        tmp_path / "docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES_DRY_RUN.md",
        """
# File Placement Rules
DRY_RUN governance authority preview and no touch policy.
        """,
    )
    _write(
        tmp_path / "docs/AI_OS/04_INVENTORY/AIOS_stage2_classification_summary_2026-05-04_16-21-31.md",
        """
# Stage 2 Classification Summary
Historical report evidence for authority classification.
        """,
    )
    _write(
        tmp_path / "docs/AI_OS/05_CLASSIFICATION/AIOS_stage2_classification_summary_2026-05-04_16-21-31.md",
        """
# Stage 2 Classification Summary
Historical report evidence for authority classification.
        """,
    )
    _write(
        tmp_path / "docs/AI_OS/AGENTS.md",
        """
# AGENTS
Required protected file and approval boundary.
        """,
    )
    _write(
        tmp_path / "docs/AI_OS/codex/AGENTS_MD_BACKUP_PHASE15_2_20260513.md",
        """
# AGENTS Backup
Backup historical authority copy. No touch without review.
        """,
    )
    _write(
        tmp_path / "docs/workflows/generic-boundary.md",
        """
# Boundary
Small note.
        """,
    )
    return tmp_path


def test_detects_competing_workflow_authority_pair(tmp_path: Path) -> None:
    report = run_canonical_authority_audit(_sample_repo(tmp_path)).to_dict()

    assert any(
        "docs/workflows/APPLY_ROUTING_CHAIN.md" in group["paths"]
        and "docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md" in group["paths"]
        and group["reason"] == "competing workflow authority"
        for group in report["duplicate_authority_groups"]
    )


def test_detects_competing_worker_lane_rules_pair(tmp_path: Path) -> None:
    report = run_canonical_authority_audit(_sample_repo(tmp_path)).to_dict()

    assert any(
        "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md" in group["paths"]
        and "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md" in group["paths"]
        for group in report["duplicate_authority_groups"]
    )


def test_detects_competing_portal_zone_security_pair(tmp_path: Path) -> None:
    report = run_canonical_authority_audit(_sample_repo(tmp_path)).to_dict()

    match = next(
        group
        for group in report["duplicate_authority_groups"]
        if "docs/AI_OS/security/phase_15_secure_access/AIOS_PORTAL_ZONE_MODEL.md" in group["paths"]
    )
    assert match["protected_review_required"] is True
    assert match["reason"] == "competing security-access authority"


def test_classifies_timestamped_reports_as_likely_valid_duplicates(tmp_path: Path) -> None:
    report = run_canonical_authority_audit(_sample_repo(tmp_path)).to_dict()

    assert any(
        "HISTORICAL_REPORT_LIKELY" in group["classifications"]
        for group in report["likely_valid_duplicates"]
    )


def test_classifies_backups_as_protected_historical_review(tmp_path: Path) -> None:
    report = run_canonical_authority_audit(_sample_repo(tmp_path)).to_dict()

    backup = next(
        item
        for item in report["protected_review_required"]
        if item["path"] == "docs/AI_OS/codex/AGENTS_MD_BACKUP_PHASE15_2_20260513.md"
    )
    assert backup["classification"] == "DO_NOT_TOUCH_WITHOUT_HUMAN_REVIEW"


def test_classifies_governance_dry_run_duplicates_as_protected_review_required(tmp_path: Path) -> None:
    report = run_canonical_authority_audit(_sample_repo(tmp_path)).to_dict()

    match = next(
        group
        for group in report["duplicate_authority_groups"]
        if "docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES_DRY_RUN.md" in group["paths"]
    )
    assert match["protected_review_required"] is True
    assert match["reason"] == "competing governance authority"


def test_generic_boundary_heading_alone_does_not_become_cleanup_recommendation(tmp_path: Path) -> None:
    report = run_canonical_authority_audit(_sample_repo(tmp_path)).to_dict()

    assert not any(
        "docs/workflows/generic-boundary.md" in item.get("paths", [])
        for item in report["top_cleanup_candidates"]
    )


def test_output_report_contains_required_fields(tmp_path: Path) -> None:
    report = run_canonical_authority_audit(_sample_repo(tmp_path)).to_dict()

    assert all(field in report for field in REQUIRED_REPORT_FIELDS)
    assert report["executable"] is False


def test_write_report_writes_only_under_reports_operator_relief_audits(tmp_path: Path) -> None:
    repo = _sample_repo(tmp_path)
    report = run_canonical_authority_audit(repo)

    output_path = write_canonical_authority_audit_report(report, repo)

    assert output_path.parent == repo / "Reports/operator_relief/audits"
    assert output_path.name.startswith("canonical_authority_audit_")
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["executable"] is False


def test_source_scan_proves_no_forbidden_execution_paths() -> None:
    source = Path("automation/operator_relief/canonical_authority_audit.py").read_text(encoding="utf-8")
    forbidden_markers = [
        "subprocess",
        "os.system",
        "Popen",
        "git add",
        "git commit",
        "git push",
        "git merge",
        "git reset",
        "OpenAI(",
        "openai.",
        "Codex(",
        "Start-Process",
        "HTTPServer",
        ".listen(",
        ".bind(",
    ]
    assert not any(marker in source for marker in forbidden_markers)
