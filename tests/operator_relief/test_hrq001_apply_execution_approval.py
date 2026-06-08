from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief import hrq001_apply_execution_approval as approval


def _write_safety_validation(repo_root: Path, status: str = "ACCEPTED") -> None:
    path = repo_root / approval.PATCH_SAFETY_VALIDATION_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "patch_validation_status": status,
                "accepted_count": 1 if status == "ACCEPTED" else 0,
                "rejected_count": 0 if status == "ACCEPTED" else 1,
                "canonical_target": approval.CANONICAL_TARGET,
                "duplicate_source": approval.DUPLICATE_SOURCE,
                "executable": False,
                "apply_ready_paths": [],
            }
        ),
        encoding="utf-8",
    )


def test_approval_allows_hrq001_execution_preparation_only(tmp_path: Path) -> None:
    _write_safety_validation(tmp_path)
    result = approval.build_approval(tmp_path).to_dict()
    payload = result["approval"]

    assert result["apply_execution_approved"] is True
    assert payload["apply_execution_approved"] is True
    assert payload["approved_candidate_ids"] == ["HRQ-001-worker_branch_and_lane_rules"]
    assert payload["apply_patch_itself"] is False
    assert payload["workflow_docs_modified"] is False


def test_approval_contains_exact_scope_and_reviewer(tmp_path: Path) -> None:
    _write_safety_validation(tmp_path)
    payload = approval.build_approval(tmp_path).to_dict()["approval"]

    assert payload["reviewer"] == "operator"
    assert payload["canonical_target"] == "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md"
    assert payload["duplicate_source"] == "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md"
    assert payload["delete_duplicate_approved"] is False


def test_approval_contains_only_two_approved_sections(tmp_path: Path) -> None:
    _write_safety_validation(tmp_path)
    result = approval.build_approval(tmp_path).to_dict()

    assert result["approved_sections"] == [
        {"source_section": "Branch Naming", "approved_content": "legacy worker branch examples"},
        {"source_section": "Report Rules", "approved_content": "concise integration-lane report check wording"},
    ]
    assert result["approval"]["approved_sections"] == result["approved_sections"]


def test_blocks_execution_approval_when_patch_safety_not_accepted(tmp_path: Path) -> None:
    _write_safety_validation(tmp_path, status="REJECTED")
    result = approval.build_approval(tmp_path).to_dict()

    assert result["apply_execution_approved"] is False
    assert result["approval"]["apply_execution_approved"] is False
    assert "HRQ-001 patch safety validation is not accepted" in result["approval"]["blockers"]
    assert "HRQ-001 patch safety validation has rejections" in result["approval"]["blockers"]


def test_output_contract_does_not_apply_patch_or_modify_sources(tmp_path: Path) -> None:
    _write_safety_validation(tmp_path)
    result = approval.build_approval(tmp_path).to_dict()
    safety = result["safety"]

    assert result["executable"] is False
    assert result["apply_ready_paths"] == []
    assert safety["workflow_docs_modified"] is False
    assert safety["files_deleted"] is False
    assert safety["canonicalization_performed"] is False
    assert safety["apply_patch_performed"] is False
    assert safety["protected_docs_modified"] is False
    assert safety["hrq002_touched"] is False
    assert safety["hrq003_touched"] is False


def test_write_approval_writes_only_under_hrq001_apply_packet_root(tmp_path: Path) -> None:
    _write_safety_validation(tmp_path)
    result = approval.build_approval(tmp_path)
    written = approval.write_approval(result, tmp_path)

    assert written.resolve().parent == (tmp_path / approval.OUTPUT_ROOT).resolve()
    assert written.name == "hrq001_apply_execution_approval.json"
    payload = json.loads(written.read_text(encoding="utf-8"))
    assert payload["apply_execution_approved"] is True
    assert payload["executable"] is False


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/hrq001_apply_execution_approval.py").read_text(encoding="utf-8")
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
