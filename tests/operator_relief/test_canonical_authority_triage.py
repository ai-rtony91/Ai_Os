import json
from pathlib import Path

from automation.operator_relief.canonical_authority_triage import (
    BUCKET_CANONICALIZATION,
    BUCKET_NOISE,
    BUCKET_PROTECTED,
    BUCKET_TEMPLATE,
    REQUIRED_REPORT_FIELDS,
    run_canonical_authority_triage,
    write_canonical_authority_triage_report,
)


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _group(group_key: str, paths: list[str], reason: str, protected: bool = False, confidence: float = 0.9) -> dict:
    return {
        "group_key": group_key,
        "category": "duplicate_workflow_docs",
        "paths": paths,
        "classifications": ["DUPLICATE_CANONICAL_CANDIDATE"],
        "reason": reason,
        "protected_review_required": protected,
        "confidence": confidence,
        "recommended_next_action": "review competing authority",
        "executable": False,
    }


def _sample_repo(tmp_path: Path) -> Path:
    groups = [
        _group(
            "apply routing chain",
            ["docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md", "docs/workflows/APPLY_ROUTING_CHAIN.md"],
            "competing workflow authority",
        ),
        _group(
            "worker branch and lane rules",
            [
                "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md",
                "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md",
            ],
            "competing worker lane rules authority",
        ),
        _group(
            "file placement rules",
            ["docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md", "docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES_DRY_RUN.md"],
            "competing governance authority",
            protected=True,
        ),
        _group(
            "repo folder ownership map",
            [
                "docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md",
                "docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP_DRY_RUN.md",
            ],
            "competing governance authority",
            protected=True,
        ),
        _group(
            "portal zone model",
            [
                "docs/AI_OS/security/phase_15_secure_access/AIOS_PORTAL_ZONE_MODEL.md",
                "docs/AI_OS/security/secure_access/AIOS_PORTAL_ZONE_MODEL.md",
            ],
            "competing security-access authority",
            protected=True,
        ),
        _group(
            "README_FOLDER_PURPOSE",
            [
                "docs/AI_OS/a/README_FOLDER_PURPOSE.txt",
                "docs/AI_OS/b/README_FOLDER_PURPOSE.txt",
                "docs/AI_OS/c/README_FOLDER_PURPOSE.txt",
                "docs/AI_OS/d/README_FOLDER_PURPOSE.txt",
                "docs/AI_OS/e/README_FOLDER_PURPOSE.txt",
                "docs/AI_OS/f/README_FOLDER_PURPOSE.txt",
                "docs/AI_OS/g/README_FOLDER_PURPOSE.txt",
                "docs/AI_OS/h/README_FOLDER_PURPOSE.txt",
                "docs/AI_OS/i/README_FOLDER_PURPOSE.txt",
            ],
            "same normalized topic appears in multiple authority-like files",
            confidence=0.6,
        ),
        _group(
            "stage2 classification summary",
            [
                "docs/AI_OS/04_INVENTORY/AIOS_stage2_classification_summary_2026-05-04_16-21-31.md",
                "docs/AI_OS/05_CLASSIFICATION/AIOS_stage2_classification_summary_2026-05-04_16-21-31.md",
            ],
            "same normalized topic appears in multiple authority-like files",
            confidence=0.88,
        ),
        _group(
            "Boundary",
            ["docs/workflows/boundary-a.md"],
            "generic heading signal",
            confidence=0.5,
        ),
    ]
    payload = {
        "report_type": "operator_relief_canonical_authority_audit_v1",
        "generated_at": "2026-06-07T02:23:01+00:00",
        "executable": False,
        "duplicate_authority_groups": groups,
        "protected_review_required": [],
        "likely_duds": [],
    }
    _write(tmp_path / "Reports/operator_relief/audits/canonical_authority_audit_20260607T022301Z.json", payload)
    return tmp_path


def _report(tmp_path: Path) -> dict:
    return run_canonical_authority_triage(_sample_repo(tmp_path)).to_dict()


def test_classifies_apply_routing_chain_as_canonicalization_review_candidate(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert any(entry["group_key"] == "apply routing chain" for entry in report["canonicalization_review_candidates"])


def test_classifies_worker_branch_lane_rules_as_canonicalization_review_candidate(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert any(entry["group_key"] == "worker branch and lane rules" for entry in report["canonicalization_review_candidates"])


def test_classifies_file_placement_rules_as_protected_human_review(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert any(entry["group_key"] == "file placement rules" for entry in report["protected_human_review"])


def test_classifies_repo_folder_ownership_map_as_protected_human_review(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert any(entry["group_key"] == "repo folder ownership map" for entry in report["protected_human_review"])


def test_classifies_portal_zone_model_as_protected_human_review(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert any(entry["group_key"] == "portal zone model" for entry in report["protected_human_review"])


def test_classifies_readme_folder_purpose_mega_group_as_template_or_noise(tmp_path: Path) -> None:
    report = _report(tmp_path)
    found = [
        entry
        for bucket in (report["likely_template_or_example"], report["likely_false_positive_noise"])
        for entry in bucket
        if entry["group_key"] == "README_FOLDER_PURPOSE"
    ]

    assert found
    assert found[0]["bucket"] in {BUCKET_TEMPLATE, BUCKET_NOISE}


def test_classifies_timestamped_report_checkpoint_groups_as_likely_valid_archive_evidence(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert any(entry["group_key"] == "stage2 classification summary" for entry in report["likely_valid_archive_or_evidence"])


def test_generic_boundary_heading_alone_does_not_create_cleanup_candidate(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert not any(entry["group_key"] == "Boundary" for entry in report["cleanup_review_candidates"])


def test_top_10_next_review_targets_exists_and_is_sorted_by_priority(tmp_path: Path) -> None:
    report = _report(tmp_path)
    top = report["top_10_next_review_targets"]

    assert top
    assert top[0]["rank"] == 1
    assert top[0]["bucket"] in {BUCKET_CANONICALIZATION, BUCKET_PROTECTED}
    assert [item["rank"] for item in top] == list(range(1, len(top) + 1))


def test_output_contains_required_fields(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert all(field in report for field in REQUIRED_REPORT_FIELDS)
    assert report["executable"] is False


def test_write_report_writes_only_under_reports_operator_relief_audits(tmp_path: Path) -> None:
    repo = _sample_repo(tmp_path)
    report = run_canonical_authority_triage(repo)

    output_path = write_canonical_authority_triage_report(report, repo)

    assert output_path.parent == repo / "Reports/operator_relief/audits"
    assert output_path.name.startswith("canonical_authority_triage_")
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["executable"] is False


def test_executable_false(tmp_path: Path) -> None:
    report = _report(tmp_path)

    assert report["executable"] is False
    assert all(entry["executable"] is False for entry in report["top_10_next_review_targets"])


def test_source_scan_proves_no_forbidden_execution_paths() -> None:
    source = Path("automation/operator_relief/canonical_authority_triage.py").read_text(encoding="utf-8")
    forbidden_markers = [
        "subprocess",
        "os.system",
        "Popen",
        "git add",
        "git commit",
        "git push",
        "git merge",
        "git rebase",
        "force-push",
        "OpenAI(",
        "openai.",
        "Codex(",
        "Start-Process",
        "HTTPServer",
        ".listen(",
        ".bind(",
    ]
    assert not any(marker in source for marker in forbidden_markers)
