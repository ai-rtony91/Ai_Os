from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief import executable_apply_packet_gate as gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_safety_validation(repo_root: Path, **overrides: object) -> None:
    payload = {
        "accepted_count": 3,
        "rejected_count": 0,
        "executable": False,
        "apply_ready_paths": [],
        "safe_cleanup_paths": [],
    }
    payload.update(overrides)
    _write_json(repo_root / gate.SAFETY_VALIDATION_PATH, payload)


def _write_approval(repo_root: Path, **overrides: object) -> None:
    payload = {
        "apply_approval": True,
        "approval_scope": gate.REQUIRED_APPROVAL_SCOPE,
        "approved_candidate_ids": list(gate.REQUIRED_CANDIDATE_IDS),
        "executable": False,
    }
    payload.update(overrides)
    _write_json(repo_root / gate.APPROVAL_PATH, payload)


def test_blocks_when_explicit_approval_missing(tmp_path: Path) -> None:
    _write_safety_validation(tmp_path)
    result = gate.build_gate(tmp_path).to_dict()

    assert result["gate_status"] == "BLOCKED"
    assert "explicit APPLY approval file is missing" in result["block_reasons"]
    assert result["approval_present"] is False


def test_blocks_when_safety_validation_missing(tmp_path: Path) -> None:
    result = gate.build_gate(tmp_path).to_dict()

    assert result["gate_status"] == "BLOCKED"
    assert "draft packet safety validation report is missing" in result["block_reasons"]


def test_blocks_when_not_all_drafts_are_accepted(tmp_path: Path) -> None:
    _write_safety_validation(tmp_path, accepted_count=2)
    _write_approval(tmp_path)
    result = gate.build_gate(tmp_path).to_dict()

    assert result["gate_status"] == "BLOCKED"
    assert "all 3 review-only draft packets must pass safety validation" in result["block_reasons"]


def test_blocks_when_safety_validation_has_rejections(tmp_path: Path) -> None:
    _write_safety_validation(tmp_path, rejected_count=1)
    _write_approval(tmp_path)
    result = gate.build_gate(tmp_path).to_dict()

    assert result["gate_status"] == "BLOCKED"
    assert "draft packet safety validation contains rejected drafts" in result["block_reasons"]


def test_blocks_when_safety_validation_is_executable_or_apply_ready(tmp_path: Path) -> None:
    _write_safety_validation(tmp_path, executable=True, apply_ready_paths=["docs/workflows/example.md"])
    _write_approval(tmp_path)
    result = gate.build_gate(tmp_path).to_dict()

    assert result["gate_status"] == "BLOCKED"
    assert "draft packet safety validation executable=true is rejected" in result["block_reasons"]
    assert "draft packet safety validation apply_ready_paths must be empty" in result["block_reasons"]


def test_blocks_when_apply_approval_not_true(tmp_path: Path) -> None:
    _write_safety_validation(tmp_path)
    _write_approval(tmp_path, apply_approval=False)
    result = gate.build_gate(tmp_path).to_dict()

    assert result["gate_status"] == "BLOCKED"
    assert "apply_approval=true is required" in result["block_reasons"]


def test_blocks_when_approval_scope_is_wrong(tmp_path: Path) -> None:
    _write_safety_validation(tmp_path)
    _write_approval(tmp_path, approval_scope="other_scope")
    result = gate.build_gate(tmp_path).to_dict()

    assert result["gate_status"] == "BLOCKED"
    assert 'approval_scope="workflow_cleanup_candidates" is required' in result["block_reasons"]


def test_blocks_when_candidate_ids_do_not_match(tmp_path: Path) -> None:
    _write_safety_validation(tmp_path)
    _write_approval(tmp_path, approved_candidate_ids=["HRQ-001-worker_branch_and_lane_rules"])
    result = gate.build_gate(tmp_path).to_dict()

    assert result["gate_status"] == "BLOCKED"
    assert "approved_candidate_ids must match the 3 review-only candidates" in result["block_reasons"]


def test_review_ready_only_when_explicit_approval_and_safety_match(tmp_path: Path) -> None:
    _write_safety_validation(tmp_path)
    _write_approval(tmp_path)
    result = gate.build_gate(tmp_path).to_dict()

    assert result["gate_status"] == "REVIEW_READY_WITH_EXPLICIT_APPROVAL"
    assert result["block_reasons"] == []
    assert result["apply_ready_paths"] == []
    assert result["safe_cleanup_paths"] == []


def test_write_gate_writes_only_under_draft_output_root(tmp_path: Path) -> None:
    result = gate.build_gate(tmp_path)
    written = gate.write_gate(result, tmp_path)

    assert written.resolve().parent == (tmp_path / gate.OUTPUT_ROOT).resolve()
    assert written.name == "executable_apply_packet_gate.json"


def test_output_contract_is_not_executable_and_generates_no_apply_packet(tmp_path: Path) -> None:
    _write_safety_validation(tmp_path)
    result = gate.build_gate(tmp_path).to_dict()

    assert result["executable"] is False
    assert result["safe_cleanup_paths"] == []
    assert result["apply_ready_paths"] == []
    assert result["safety"]["gate_only"] is True
    assert result["safety"]["workflow_docs_modified"] is False
    assert result["safety"]["cleanup_performed"] is False
    assert result["safety"]["canonicalization_performed"] is False
    assert result["safety"]["executable_apply_packet_generated"] is False
    assert result["safety"]["protected_docs_modified"] is False


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/executable_apply_packet_gate.py").read_text(encoding="utf-8")
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
