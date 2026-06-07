from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief import final_cleanup_safety_gate as gate


def _write_candidate_report(repo_root: Path, payload: dict) -> None:
    path = repo_root / gate.SOURCE_CANDIDATES_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _base_report(**overrides: object) -> dict:
    report = {
        "report_type": "operator_relief_approved_cleanup_candidate_generator_v1",
        "executable": False,
        "approved_cleanup_candidate_count": 0,
        "approved_cleanup_candidates": [],
        "safe_cleanup_paths": [],
        "apply_ready_paths": [],
    }
    report.update(overrides)
    return report


def _candidate(item_id: str = "HRQ-001-worker_branch_and_lane_rules", **overrides: object) -> dict:
    candidate = {
        "item_id": item_id,
        "decision": "MERGE_DUPLICATE_INTO_CANONICAL_LATER",
        "reviewer": "Anthony",
        "paths": ["docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md"],
        "executable": False,
        "apply_ready": False,
    }
    candidate.update(overrides)
    return candidate


def test_missing_candidate_report_blocks(tmp_path: Path) -> None:
    result = gate.build_gate(tmp_path).to_dict()

    assert result["final_status"] == "BLOCKED"
    assert "approved cleanup candidate report is missing" in result["block_reasons"]
    assert result["approved_cleanup_candidate_count"] == 0


def test_zero_candidates_blocks(tmp_path: Path) -> None:
    _write_candidate_report(tmp_path, _base_report())
    result = gate.build_gate(tmp_path).to_dict()

    assert result["final_status"] == "BLOCKED"
    assert "approved_cleanup_candidate_count is 0" in result["block_reasons"]
    assert result["safe_cleanup_paths"] == []
    assert result["apply_ready_paths"] == []


def test_executable_true_anywhere_blocks(tmp_path: Path) -> None:
    _write_candidate_report(
        tmp_path,
        _base_report(
            approved_cleanup_candidate_count=1,
            approved_cleanup_candidates=[_candidate(executable=True)],
        ),
    )
    result = gate.build_gate(tmp_path).to_dict()

    assert result["final_status"] == "BLOCKED"
    assert "executable=true found in candidate report" in result["block_reasons"]


def test_apply_ready_paths_without_candidates_blocks(tmp_path: Path) -> None:
    _write_candidate_report(tmp_path, _base_report(apply_ready_paths=["docs/workflows/example.md"]))
    result = gate.build_gate(tmp_path).to_dict()

    assert result["final_status"] == "BLOCKED"
    assert "apply_ready_paths is non-empty without valid candidates" in result["block_reasons"]
    assert result["apply_ready_paths"] == []


def test_safe_cleanup_paths_without_candidates_blocks(tmp_path: Path) -> None:
    _write_candidate_report(tmp_path, _base_report(safe_cleanup_paths=["docs/workflows/example.md"]))
    result = gate.build_gate(tmp_path).to_dict()

    assert result["final_status"] == "BLOCKED"
    assert "safe_cleanup_paths is non-empty without valid candidates" in result["block_reasons"]
    assert result["safe_cleanup_paths"] == []


def test_protected_authority_items_block(tmp_path: Path) -> None:
    _write_candidate_report(
        tmp_path,
        _base_report(
            approved_cleanup_candidate_count=1,
            approved_cleanup_candidates=[_candidate("HRQ-004-file_placement_rules")],
        ),
    )
    result = gate.build_gate(tmp_path).to_dict()

    assert result["final_status"] == "BLOCKED"
    assert "protected authority items are blocked from cleanup" in result["block_reasons"]
    assert result["protected_authority_items"][0]["item_id"] == "HRQ-004-file_placement_rules"


def test_valid_non_protected_candidates_are_review_only_ready(tmp_path: Path) -> None:
    _write_candidate_report(
        tmp_path,
        _base_report(
            approved_cleanup_candidate_count=1,
            approved_cleanup_candidates=[_candidate()],
        ),
    )
    result = gate.build_gate(tmp_path).to_dict()

    assert result["final_status"] == "REVIEW_ONLY_READY"
    assert result["block_reasons"] == []
    assert result["safe_cleanup_paths"] == []
    assert result["apply_ready_paths"] == []
    assert result["safety"]["apply_packet_generated"] is False


def test_write_report_writes_only_under_final_safety_gate(tmp_path: Path) -> None:
    result = gate.build_gate(tmp_path)
    written = gate.write_gate(result, tmp_path)

    assert written.resolve().parent == (tmp_path / gate.OUTPUT_PATH.parent).resolve()
    assert written.name == "final_cleanup_safety_gate.json"


def test_output_contract_is_not_executable_and_no_apply_packet(tmp_path: Path) -> None:
    _write_candidate_report(tmp_path, _base_report())
    result = gate.build_gate(tmp_path).to_dict()

    assert result["executable"] is False
    assert result["safe_cleanup_paths"] == []
    assert result["apply_ready_paths"] == []
    assert result["safety"]["approvals_created"] is False
    assert result["safety"]["approvals_inferred"] is False
    assert result["safety"]["cleanup_performed"] is False
    assert result["safety"]["canonicalization_performed"] is False
    assert result["safety"]["apply_packet_generated"] is False


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/final_cleanup_safety_gate.py").read_text(encoding="utf-8")
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
