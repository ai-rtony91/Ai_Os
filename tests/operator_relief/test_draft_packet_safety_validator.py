from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief import draft_packet_safety_validator as validator


def _safe_packet(**overrides: object) -> dict:
    payload = {
        "candidate_id": "HRQ-001-worker_branch_and_lane_rules",
        "canonical_file": "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md",
        "duplicate_files": ["docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md"],
        "dependency_files": ["docs/audits/phase-5c-narrow-merge-plan.md"],
        "blocked_actions": ["modify workflow docs", "perform cleanup"],
        "human_approval_requirements": ["Human approval is required before any workflow document edit."],
        "rollback_requirements": ["Future APPLY packet must include rollback evidence."],
        "validation_requirements": ["Run exact-file diff review before any future APPLY."],
        "executable": False,
        "review_only": True,
        "safe_cleanup_paths": [],
        "apply_ready_paths": [],
    }
    payload.update(overrides)
    return payload


def _write_packet(repo_root: Path, payload: dict, filename: str = "workflow_cleanup_apply_packet_001.json") -> None:
    output_root = repo_root / validator.OUTPUT_ROOT
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / filename).write_text(json.dumps(payload), encoding="utf-8")


def test_accepts_safe_review_only_draft_packet(tmp_path: Path) -> None:
    _write_packet(tmp_path, _safe_packet())
    result = validator.build_validation(tmp_path).to_dict()

    assert result["accepted_count"] == 1
    assert result["rejected_count"] == 0
    assert result["accepted_draft_packets"][0]["candidate_id"] == "HRQ-001-worker_branch_and_lane_rules"


def test_rejects_executable_true(tmp_path: Path) -> None:
    _write_packet(tmp_path, _safe_packet(executable=True))
    result = validator.build_validation(tmp_path).to_dict()

    assert result["accepted_count"] == 0
    assert "executable=true is rejected" in result["rejected_draft_packets"][0]["errors"]


def test_rejects_review_only_not_true(tmp_path: Path) -> None:
    _write_packet(tmp_path, _safe_packet(review_only=False))
    result = validator.build_validation(tmp_path).to_dict()

    assert result["accepted_count"] == 0
    assert "review_only must be true" in result["rejected_draft_packets"][0]["errors"]


def test_rejects_non_empty_safe_cleanup_paths(tmp_path: Path) -> None:
    _write_packet(tmp_path, _safe_packet(safe_cleanup_paths=["docs/workflows/example.md"]))
    result = validator.build_validation(tmp_path).to_dict()

    assert result["accepted_count"] == 0
    assert "safe_cleanup_paths must be empty" in result["rejected_draft_packets"][0]["errors"]


def test_rejects_non_empty_apply_ready_paths(tmp_path: Path) -> None:
    _write_packet(tmp_path, _safe_packet(apply_ready_paths=["docs/workflows/example.md"]))
    result = validator.build_validation(tmp_path).to_dict()

    assert result["accepted_count"] == 0
    assert "apply_ready_paths must be empty" in result["rejected_draft_packets"][0]["errors"]


def test_rejects_protected_governance_or_security_editable_targets(tmp_path: Path) -> None:
    _write_packet(tmp_path, _safe_packet(canonical_file="docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md"))
    result = validator.build_validation(tmp_path).to_dict()

    assert result["accepted_count"] == 0
    assert "protected governance/security docs appear as editable targets" in result["rejected_draft_packets"][0]["errors"]


def test_rejects_missing_required_safety_sections(tmp_path: Path) -> None:
    _write_packet(
        tmp_path,
        _safe_packet(
            blocked_actions=[],
            human_approval_requirements=[],
            rollback_requirements=[],
            validation_requirements=[],
        ),
    )
    result = validator.build_validation(tmp_path).to_dict()
    errors = result["rejected_draft_packets"][0]["errors"]

    assert "blocked_actions is required" in errors
    assert "human_approval_requirements is required" in errors
    assert "rollback_requirements is required" in errors
    assert "validation_requirements is required" in errors


def test_ignores_index_and_prior_validation_reports(tmp_path: Path) -> None:
    _write_packet(tmp_path, _safe_packet(), "workflow_cleanup_apply_packet_001.json")
    _write_packet(tmp_path, {"executable": True}, "workflow_cleanup_apply_packet_draft_index.json")
    _write_packet(tmp_path, {"executable": True}, "draft_packet_safety_validation.json")
    result = validator.build_validation(tmp_path).to_dict()

    assert result["accepted_count"] == 1
    assert result["rejected_count"] == 0
    assert result["draft_packets_scanned"] == [
        "Reports/operator_relief/workflow_cleanup_apply_packet_drafts/workflow_cleanup_apply_packet_001.json"
    ]


def test_write_validation_writes_only_under_draft_output_root(tmp_path: Path) -> None:
    result = validator.build_validation(tmp_path)
    written = validator.write_validation(result, tmp_path)

    assert written.resolve().parent == (tmp_path / validator.OUTPUT_ROOT).resolve()
    assert written.name == "draft_packet_safety_validation.json"


def test_output_contract_is_not_executable_or_apply_ready(tmp_path: Path) -> None:
    _write_packet(tmp_path, _safe_packet())
    result = validator.build_validation(tmp_path).to_dict()

    assert result["executable"] is False
    assert result["review_only"] is True
    assert result["safe_cleanup_paths"] == []
    assert result["apply_ready_paths"] == []
    assert result["safety"]["validation_only"] is True
    assert result["safety"]["workflow_docs_modified"] is False
    assert result["safety"]["cleanup_performed"] is False
    assert result["safety"]["canonicalization_performed"] is False
    assert result["safety"]["executable_apply_packet_generated"] is False
    assert result["safety"]["protected_docs_modified"] is False


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/draft_packet_safety_validator.py").read_text(encoding="utf-8")
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
