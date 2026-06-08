from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief import human_decision_intake_validator as validator


KNOWN_ITEM_ID = "HRQ-001-test_packet"
VALID_DECISION = {
    "item_id": KNOWN_ITEM_ID,
    "reviewer": "Anthony",
    "decision": "KEEP_CANONICAL_AS_IS",
    "rationale": "Reviewed for future decision capture only.",
    "executable": False,
    "cleanup_approved": False,
    "canonicalization_approved": False,
    "apply_packet_generated": False,
    "safe_cleanup_paths": [],
    "apply_ready_paths": [],
}


def _write_packet(repo_root: Path, item_id: str = KNOWN_ITEM_ID) -> None:
    packet_root = repo_root / validator.PACKET_ROOT
    packet_root.mkdir(parents=True, exist_ok=True)
    (packet_root / f"{item_id}.md").write_text("# Review packet\n", encoding="utf-8")


def _write_decision(repo_root: Path, payload: object, filename: str = "decision.json") -> None:
    decision_root = repo_root / validator.DECISION_ROOT
    decision_root.mkdir(parents=True, exist_ok=True)
    (decision_root / filename).write_text(json.dumps(payload), encoding="utf-8")


def _write_filled_decision(repo_root: Path, payload: object, filename: str = "decision.json") -> None:
    decision_root = repo_root / validator.FILLED_DECISION_ROOT
    decision_root.mkdir(parents=True, exist_ok=True)
    (decision_root / filename).write_text(json.dumps(payload), encoding="utf-8")


def _build_with_decision(tmp_path: Path, payload: object) -> dict:
    _write_packet(tmp_path)
    _write_decision(tmp_path, payload)
    return validator.build_validation(tmp_path).to_dict()


def test_accepts_valid_decision_for_known_packet_id(tmp_path: Path) -> None:
    result = _build_with_decision(tmp_path, VALID_DECISION)

    assert result["accepted_decision_count"] == 1
    assert result["rejected_decision_count"] == 0
    assert result["accepted_decisions"][0]["item_id"] == KNOWN_ITEM_ID
    assert result["accepted_decisions"][0]["accepted_for_validation_only"] is True
    assert result["approved_cleanup_candidate_count"] == 0


def test_accepts_valid_filled_decision_for_known_packet_id(tmp_path: Path) -> None:
    _write_packet(tmp_path)
    _write_filled_decision(tmp_path, VALID_DECISION, "filled_decision.json")
    result = validator.build_validation(tmp_path).to_dict()

    assert result["accepted_decision_count"] == 1
    assert result["rejected_decision_count"] == 0
    assert result["accepted_decisions"][0]["item_id"] == KNOWN_ITEM_ID
    assert (
        "Reports/operator_relief/human_review_decisions/filled/filled_decision.json"
        in result["decision_files_scanned"]
    )


def test_scans_top_level_and_filled_decisions(tmp_path: Path) -> None:
    _write_packet(tmp_path)
    _write_decision(tmp_path, VALID_DECISION, "top_level_decision.json")
    _write_filled_decision(tmp_path, VALID_DECISION, "filled_decision.json")
    result = validator.build_validation(tmp_path).to_dict()

    assert result["accepted_decision_count"] == 2
    assert len(result["decision_files_scanned"]) == 2


def test_rejects_unknown_decision_value(tmp_path: Path) -> None:
    decision = {**VALID_DECISION, "decision": "APPROVE_CLEANUP_NOW"}
    result = _build_with_decision(tmp_path, decision)

    assert result["accepted_decision_count"] == 0
    assert "unknown decision value" in result["rejected_decisions"][0]["errors"][0]


def test_rejects_missing_reviewer(tmp_path: Path) -> None:
    decision = {**VALID_DECISION, "reviewer": ""}
    result = _build_with_decision(tmp_path, decision)

    assert result["accepted_decision_count"] == 0
    assert "reviewer field is required" in result["rejected_decisions"][0]["errors"]


def test_rejects_empty_rationale(tmp_path: Path) -> None:
    decision = {**VALID_DECISION, "rationale": " "}
    result = _build_with_decision(tmp_path, decision)

    assert result["accepted_decision_count"] == 0
    assert "rationale field is required" in result["rejected_decisions"][0]["errors"]


def test_rejects_safety_flags_that_grant_action(tmp_path: Path) -> None:
    for field in ("executable", "cleanup_approved", "canonicalization_approved", "apply_packet_generated"):
        decision = {**VALID_DECISION, field: True}
        result = _build_with_decision(tmp_path / field, decision)

        assert result["accepted_decision_count"] == 0
        assert f"{field}=true is rejected" in result["rejected_decisions"][0]["errors"]


def test_rejects_non_empty_safe_cleanup_paths(tmp_path: Path) -> None:
    decision = {**VALID_DECISION, "safe_cleanup_paths": ["docs/workflows/example.md"]}
    result = _build_with_decision(tmp_path, decision)

    assert result["accepted_decision_count"] == 0
    assert "safe_cleanup_paths must be empty" in result["rejected_decisions"][0]["errors"]


def test_rejects_non_empty_apply_ready_paths(tmp_path: Path) -> None:
    decision = {**VALID_DECISION, "apply_ready_paths": ["docs/workflows/example.md"]}
    result = _build_with_decision(tmp_path, decision)

    assert result["accepted_decision_count"] == 0
    assert "apply_ready_paths must be empty" in result["rejected_decisions"][0]["errors"]


def test_rejects_unknown_packet_item_id(tmp_path: Path) -> None:
    _write_packet(tmp_path, "HRQ-999-known")
    _write_decision(tmp_path, {**VALID_DECISION, "item_id": "HRQ-404-missing"})
    result = validator.build_validation(tmp_path).to_dict()

    assert result["accepted_decision_count"] == 0
    assert "unknown packet item id: HRQ-404-missing" in result["rejected_decisions"][0]["errors"]


def test_no_decision_files_produces_zero_cleanup_candidates(tmp_path: Path) -> None:
    _write_packet(tmp_path)
    result = validator.build_validation(tmp_path).to_dict()

    assert result["accepted_decision_count"] == 0
    assert result["rejected_decision_count"] == 0
    assert result["approved_cleanup_candidates"] == []
    assert result["approved_cleanup_candidate_count"] == 0
    assert result["safe_cleanup_paths"] == []
    assert result["apply_ready_paths"] == []


def test_write_report_writes_only_under_human_review_decisions(tmp_path: Path) -> None:
    result = validator.build_validation(tmp_path)
    written = validator.write_validation(result, tmp_path)

    expected_root = (tmp_path / validator.DECISION_ROOT).resolve()
    assert written.resolve().parent == expected_root
    assert written.name == "human_decision_intake_validation.json"


def test_output_contract_is_not_executable_and_does_not_authorize_cleanup(tmp_path: Path) -> None:
    result = _build_with_decision(tmp_path, VALID_DECISION)

    assert result["executable"] is False
    assert result["safe_cleanup_paths"] == []
    assert result["apply_ready_paths"] == []
    assert result["safety"]["approvals_created"] is False
    assert result["safety"]["approvals_inferred"] is False
    assert result["safety"]["cleanup_approved"] is False
    assert result["safety"]["canonicalization_approved"] is False
    assert result["safety"]["apply_packet_generated"] is False


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/human_decision_intake_validator.py").read_text(encoding="utf-8")
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
