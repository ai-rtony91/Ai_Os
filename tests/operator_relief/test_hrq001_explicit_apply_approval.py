from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief import hrq001_explicit_apply_approval as approval


def _write_inputs(repo_root: Path, safety_status: str = "ACCEPTED") -> None:
    draft_path = repo_root / approval.PATCH_JSON_PATH
    safety_path = repo_root / approval.PATCH_SAFETY_VALIDATION_PATH
    draft_path.parent.mkdir(parents=True, exist_ok=True)
    draft_path.write_text(
        json.dumps(
            {
                "canonical_target": approval.CANONICAL_TARGET,
                "duplicate_source": approval.DUPLICATE_SOURCE,
                "executable": False,
                "apply_ready_paths": [],
            }
        ),
        encoding="utf-8",
    )
    safety_path.write_text(
        json.dumps(
            {
                "patch_validation_status": safety_status,
                "rejected_count": 0 if safety_status == "ACCEPTED" else 1,
                "executable": False,
                "apply_ready_paths": [],
            }
        ),
        encoding="utf-8",
    )


def test_approval_file_authorizes_hrq001_preparation_only(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = approval.build_approval(tmp_path).to_dict()
    payload = result["approval"]

    assert payload["apply_packet_preparation_approved"] is True
    assert payload["apply_execution_approved"] is False
    assert payload["approved_candidate_ids"] == ["HRQ-001-worker_branch_and_lane_rules"]
    assert payload["hrq002_approved"] is False
    assert payload["hrq003_approved"] is False


def test_approval_file_contains_exact_canonical_and_duplicate_scope(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    payload = approval.build_approval(tmp_path).to_dict()["approval"]

    assert payload["canonical_target"] == "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md"
    assert payload["duplicate_source"] == "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md"
    assert payload["delete_duplicate_approved"] is False


def test_approval_file_contains_only_two_approved_sections(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = approval.build_approval(tmp_path).to_dict()

    assert result["approved_sections"] == [
        {"source_section": "Branch Naming", "approved_content": "legacy worker branch examples"},
        {"source_section": "Report Rules", "approved_content": "concise integration-lane report check wording"},
    ]
    assert result["approval"]["approved_sections"] == result["approved_sections"]


def test_blocks_preparation_when_patch_safety_not_accepted(tmp_path: Path) -> None:
    _write_inputs(tmp_path, safety_status="REJECTED")
    result = approval.build_approval(tmp_path).to_dict()

    assert result["apply_packet_preparation_approved"] is False
    assert result["approval"]["apply_packet_preparation_approved"] is False
    assert "HRQ-001 patch safety validation is not accepted" in result["approval"]["blockers"]
    assert "HRQ-001 patch safety validation has rejections" in result["approval"]["blockers"]


def test_blocks_preparation_when_patch_scope_mismatch(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    draft_path = tmp_path / approval.PATCH_JSON_PATH
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    draft["canonical_target"] = "docs/workflows/PARALLEL_CODEX_WORKFLOW.md"
    draft_path.write_text(json.dumps(draft), encoding="utf-8")
    result = approval.build_approval(tmp_path).to_dict()

    assert result["apply_packet_preparation_approved"] is False
    assert "draft patch canonical target does not match HRQ-001 canonical target" in result["approval"]["blockers"]


def test_output_contract_does_not_authorize_execution_or_cleanup(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = approval.build_approval(tmp_path).to_dict()
    payload = result["approval"]

    assert result["executable"] is False
    assert result["apply_execution_approved"] is False
    assert result["apply_ready_paths"] == []
    assert payload["executable"] is False
    assert payload["apply_ready_paths"] == []
    assert payload["canonicalization_approved"] is False
    assert result["safety"]["workflow_docs_modified"] is False
    assert result["safety"]["files_deleted"] is False
    assert result["safety"]["executable_apply_packet_generated"] is False
    assert result["safety"]["protected_docs_modified"] is False


def test_write_approval_writes_only_under_hrq001_patch_root(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = approval.build_approval(tmp_path)
    written = approval.write_approval(result, tmp_path)

    assert written.resolve().parent == (tmp_path / approval.PATCH_ROOT).resolve()
    assert written.name == "hrq001_explicit_apply_approval.json"
    assert '"apply_execution_approved": false' in written.read_text(encoding="utf-8")


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/hrq001_explicit_apply_approval.py").read_text(encoding="utf-8")
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
