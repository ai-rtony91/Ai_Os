from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief import approved_cleanup_candidate_generator as generator


def _write_intake(repo_root: Path, accepted_decisions: list[dict]) -> None:
    path = repo_root / generator.INTAKE_VALIDATION_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "report_type": "operator_relief_human_decision_intake_validation_v1",
                "executable": False,
                "accepted_decision_count": len(accepted_decisions),
                "accepted_decisions": accepted_decisions,
                "safe_cleanup_paths": [],
                "apply_ready_paths": [],
            }
        ),
        encoding="utf-8",
    )


def _accepted_decision(item_id: str, decision: str = "MERGE_DUPLICATE_INTO_CANONICAL_LATER", **extra: object) -> dict:
    return {
        "item_id": item_id,
        "decision": decision,
        "reviewer": "Anthony",
        "accepted": True,
        "rationale": "Validated for future review candidate generation.",
        **extra,
    }


def test_missing_intake_report_produces_zero_candidates(tmp_path: Path) -> None:
    result = generator.build_candidates(tmp_path).to_dict()

    assert result["intake_validation_present"] is False
    assert result["accepted_decision_count"] == 0
    assert result["approved_cleanup_candidate_count"] == 0
    assert result["approved_cleanup_candidates"] == []
    assert result["safe_cleanup_paths"] == []
    assert result["apply_ready_paths"] == []


def test_zero_accepted_decisions_produces_zero_candidates(tmp_path: Path) -> None:
    _write_intake(tmp_path, [])
    result = generator.build_candidates(tmp_path).to_dict()

    assert result["intake_validation_present"] is True
    assert result["accepted_decision_count"] == 0
    assert result["approved_cleanup_candidate_count"] == 0
    assert result["rejected_candidate_count"] == 0


def test_generates_candidate_only_from_accepted_cleanup_decision(tmp_path: Path) -> None:
    _write_intake(tmp_path, [_accepted_decision("HRQ-001-worker_branch_and_lane_rules")])
    result = generator.build_candidates(tmp_path).to_dict()

    assert result["approved_cleanup_candidate_count"] == 1
    candidate = result["approved_cleanup_candidates"][0]
    assert candidate["item_id"] == "HRQ-001-worker_branch_and_lane_rules"
    assert candidate["executable"] is False
    assert candidate["apply_ready"] is False
    assert result["apply_ready_paths"] == []


def test_ignores_accepted_false_records(tmp_path: Path) -> None:
    decision = _accepted_decision("HRQ-001-worker_branch_and_lane_rules")
    decision["accepted"] = False
    _write_intake(tmp_path, [decision])
    result = generator.build_candidates(tmp_path).to_dict()

    assert result["accepted_decisions_reviewed"] == []
    assert result["approved_cleanup_candidate_count"] == 0


def test_rejects_protected_authority_without_allowed_park_decision(tmp_path: Path) -> None:
    _write_intake(tmp_path, [_accepted_decision("HRQ-004-file_placement_rules")])
    result = generator.build_candidates(tmp_path).to_dict()

    assert result["approved_cleanup_candidate_count"] == 0
    assert result["protected_rejected_count"] == 1
    assert result["rejected_candidates"][0]["classification"] == "PROTECTED_AUTHORITY_REJECTED"


def test_parks_protected_authority_with_allowed_decision(tmp_path: Path) -> None:
    _write_intake(
        tmp_path,
        [_accepted_decision("HRQ-006-portal_zone_model", decision="PARK_UNTIL_GOVERNANCE_REVIEW")],
    )
    result = generator.build_candidates(tmp_path).to_dict()

    assert result["approved_cleanup_candidate_count"] == 0
    assert result["protected_rejected_count"] == 1
    assert result["rejected_candidates"][0]["classification"] == "PROTECTED_AUTHORITY_PARKED"


def test_rejects_dependency_only_docs_as_cleanup_candidates(tmp_path: Path) -> None:
    _write_intake(tmp_path, [_accepted_decision("HRQ-007-docs_audits_phase_5c_narrow_merge_plan_md")])
    result = generator.build_candidates(tmp_path).to_dict()

    assert result["approved_cleanup_candidate_count"] == 0
    assert result["dependency_rejected_count"] == 1
    assert result["rejected_candidates"][0]["classification"] == "DEPENDENCY_ONLY_REJECTED"


def test_rejects_non_canonical_dependencies_as_cleanup_candidates(tmp_path: Path) -> None:
    _write_intake(
        tmp_path,
        [_accepted_decision("HRQ-008-docs_ai_os_trading_forex_engine_v1_sprint_4_regime_signal_rules_md")],
    )
    result = generator.build_candidates(tmp_path).to_dict()

    assert result["approved_cleanup_candidate_count"] == 0
    assert result["non_canonical_dependency_rejected_count"] == 1
    assert result["rejected_candidates"][0]["classification"] == "NON_CANONICAL_DEPENDENCY_REJECTED"


def test_non_candidate_decision_values_do_not_create_candidates(tmp_path: Path) -> None:
    _write_intake(tmp_path, [_accepted_decision("HRQ-002-parallel_codex_workflow", decision="KEEP_CANONICAL_AS_IS")])
    result = generator.build_candidates(tmp_path).to_dict()

    assert result["approved_cleanup_candidate_count"] == 0
    assert result["no_candidate_decision_count"] == 1
    assert result["rejected_candidates"][0]["classification"] == "NO_CANDIDATE_DECISION"


def test_write_report_writes_only_under_approved_cleanup_candidates(tmp_path: Path) -> None:
    result = generator.build_candidates(tmp_path)
    written = generator.write_candidates(result, tmp_path)

    assert written.resolve().parent == (tmp_path / generator.OUTPUT_PATH.parent).resolve()
    assert written.name == "approved_cleanup_candidates.json"


def test_output_contract_is_not_executable_and_not_apply_ready(tmp_path: Path) -> None:
    _write_intake(tmp_path, [_accepted_decision("HRQ-001-worker_branch_and_lane_rules")])
    result = generator.build_candidates(tmp_path).to_dict()

    assert result["executable"] is False
    assert result["safe_cleanup_paths"] == []
    assert result["apply_ready_paths"] == []
    assert result["safety"]["approvals_created"] is False
    assert result["safety"]["approvals_inferred"] is False
    assert result["safety"]["cleanup_performed"] is False
    assert result["safety"]["canonicalization_performed"] is False
    assert result["safety"]["apply_packet_generated"] is False


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/approved_cleanup_candidate_generator.py").read_text(encoding="utf-8")
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
