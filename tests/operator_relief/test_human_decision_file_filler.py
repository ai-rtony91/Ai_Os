from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief import human_decision_file_filler as filler


ITEM_IDS = [
    "HRQ-001-worker_branch_and_lane_rules",
    "HRQ-002-parallel_codex_workflow",
    "HRQ-003-apply_routing_chain",
    "HRQ-004-file_placement_rules",
    "HRQ-005-repo_folder_ownership_map",
    "HRQ-006-portal_zone_model",
    "HRQ-007-docs_audits_phase_5c_narrow_merge_plan_md",
    "HRQ-008-docs_ai_os_trading_forex_engine_v1_sprint_4_regime_signal_rules_md",
    "HRQ-009-docs_ai_os_trading_forex_engine_v1_sprint_4_regime_signal_rules_md",
]


def _template(item_id: str) -> dict:
    return {
        "packet_id": item_id,
        "item_id": item_id,
        "reviewer": "",
        "decision": "",
        "rationale": "",
        "allowed_decisions": [
            "KEEP_CANONICAL_AS_IS",
            "MERGE_DUPLICATE_INTO_CANONICAL_LATER",
            "KEEP_BOTH_WITH_SCOPE_NOTE",
            "PARK_UNTIL_GOVERNANCE_REVIEW",
            "MARK_DEPENDENCY_ONLY",
        ],
        "cleanup_approved": False,
        "canonicalization_approved": False,
        "apply_packet_generated": False,
        "executable": False,
        "safe_cleanup_paths": [],
        "apply_ready_paths": [],
    }


def _write_inputs(repo_root: Path, item_ids: list[str] = ITEM_IDS) -> None:
    template_root = repo_root / filler.TEMPLATE_ROOT
    packet_root = repo_root / filler.PACKET_ROOT
    template_root.mkdir(parents=True, exist_ok=True)
    packet_root.mkdir(parents=True, exist_ok=True)
    for item_id in item_ids:
        (template_root / f"{item_id}.json").write_text(json.dumps(_template(item_id)), encoding="utf-8")
        (packet_root / f"{item_id}.md").write_text("# Human Review Packet\n", encoding="utf-8")


def test_fills_nine_decision_files_when_nine_templates_exist(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = filler.build_decisions(tmp_path).to_dict()

    assert result["decision_files_generated_count"] == 9
    assert result["filled_validation_accepted_count"] == 9
    assert result["filled_validation_rejected_count"] == 0


def test_applies_operator_intent_by_category(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = filler.build_decisions(tmp_path).to_dict()
    decisions = {item["item_id"]: item["decision"] for item in result["decisions"]}

    assert decisions["HRQ-001-worker_branch_and_lane_rules"] == "MERGE_DUPLICATE_INTO_CANONICAL_LATER"
    assert decisions["HRQ-002-parallel_codex_workflow"] == "MERGE_DUPLICATE_INTO_CANONICAL_LATER"
    assert decisions["HRQ-003-apply_routing_chain"] == "MERGE_DUPLICATE_INTO_CANONICAL_LATER"
    assert decisions["HRQ-004-file_placement_rules"] == "PARK_UNTIL_GOVERNANCE_REVIEW"
    assert decisions["HRQ-005-repo_folder_ownership_map"] == "PARK_UNTIL_GOVERNANCE_REVIEW"
    assert decisions["HRQ-006-portal_zone_model"] == "PARK_UNTIL_GOVERNANCE_REVIEW"
    assert decisions["HRQ-007-docs_audits_phase_5c_narrow_merge_plan_md"] == "MARK_DEPENDENCY_ONLY"
    assert decisions["HRQ-008-docs_ai_os_trading_forex_engine_v1_sprint_4_regime_signal_rules_md"] == "MARK_DEPENDENCY_ONLY"
    assert decisions["HRQ-009-docs_ai_os_trading_forex_engine_v1_sprint_4_regime_signal_rules_md"] == "MARK_DEPENDENCY_ONLY"


def test_decisions_include_reviewer_and_non_empty_rationale(tmp_path: Path) -> None:
    _write_inputs(tmp_path, ["HRQ-001-worker_branch_and_lane_rules"])
    result = filler.build_decisions(tmp_path).to_dict()
    decision_file = result["decisions"][0]["decision_file"]

    assert decision_file["reviewer"] == "operator"
    assert decision_file["rationale"]
    assert decision_file["executable"] is False
    assert decision_file["cleanup_approved"] is False
    assert decision_file["canonicalization_approved"] is False
    assert decision_file["apply_packet_generated"] is False
    assert decision_file["safe_cleanup_paths"] == []
    assert decision_file["apply_ready_paths"] == []


def test_counts_decisions_by_category(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = filler.build_decisions(tmp_path).to_dict()

    assert result["decisions_applied_by_category"] == {
        "workflow_conflict": 3,
        "protected_authority": 3,
        "dependency_or_non_canonical_dependency": 3,
    }


def test_rejects_unknown_packet_id(tmp_path: Path) -> None:
    template_root = tmp_path / filler.TEMPLATE_ROOT
    template_root.mkdir(parents=True, exist_ok=True)
    (template_root / "HRQ-999-missing.json").write_text(json.dumps(_template("HRQ-999-missing")), encoding="utf-8")

    result = filler.build_decisions(tmp_path).to_dict()

    assert result["filled_validation_accepted_count"] == 0
    assert result["filled_validation_rejected_count"] == 1
    assert "unknown packet item id: HRQ-999-missing" in result["filled_validation_rejections"][0]["errors"]


def test_write_decisions_writes_only_under_filled_root(tmp_path: Path) -> None:
    _write_inputs(tmp_path, ["HRQ-001-worker_branch_and_lane_rules"])
    result = filler.build_decisions(tmp_path)
    written = filler.write_decisions(result, tmp_path)

    assert len(written) == 1
    assert written[0].resolve().parent == (tmp_path / filler.OUTPUT_ROOT).resolve()
    assert written[0].name == "HRQ-001-worker_branch_and_lane_rules.json"


def test_reads_existing_approved_cleanup_candidate_count(tmp_path: Path) -> None:
    _write_inputs(tmp_path, ["HRQ-001-worker_branch_and_lane_rules"])
    path = tmp_path / filler.APPROVED_CANDIDATE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"approved_cleanup_candidate_count": 2}), encoding="utf-8")

    result = filler.build_decisions(tmp_path).to_dict()

    assert result["approved_cleanup_candidate_count"] == 2


def test_output_contract_is_not_executable_and_not_apply_ready(tmp_path: Path) -> None:
    _write_inputs(tmp_path, ["HRQ-001-worker_branch_and_lane_rules"])
    result = filler.build_decisions(tmp_path).to_dict()

    assert result["executable"] is False
    assert result["safe_cleanup_paths"] == []
    assert result["apply_ready_paths"] == []
    assert result["safety"]["approvals_created"] is False
    assert result["safety"]["approvals_inferred"] is False
    assert result["safety"]["cleanup_approved"] is False
    assert result["safety"]["canonicalization_approved"] is False
    assert result["safety"]["apply_packet_generated"] is False


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/human_decision_file_filler.py").read_text(encoding="utf-8")
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
