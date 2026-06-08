from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief import workflow_cleanup_apply_packet_draft as draft


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _plan_item(item_id: str, canonical: str, duplicate: str, dependencies: list[str] | None = None) -> dict:
    return {
        "item_id": item_id,
        "canonical_file": canonical,
        "duplicate_file": duplicate,
        "dependency_only_files": dependencies or [],
        "sections_that_conflict": ["Purpose / Purpose"],
        "sections_that_must_be_preserved": ["Canonical Safety"],
        "sections_that_need_merge_review": ["Duplicate Guidance"],
        "blocked_actions": ["modify workflow docs", "perform cleanup", "generate APPLY packet"],
        "required_evidence_before_apply": ["Read source docs."],
        "review_only": True,
        "executable": False,
    }


def _write_inputs(repo_root: Path) -> None:
    _write_json(
        repo_root / draft.REVIEW_PLAN_PATH,
        {
            "final_gate_status": "REVIEW_ONLY_READY",
            "candidates_included": [
                _plan_item(
                    "HRQ-001-worker_branch_and_lane_rules",
                    "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md",
                    "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md",
                    ["docs/audits/phase-5c-narrow-merge-plan.md"],
                ),
                _plan_item(
                    "HRQ-002-parallel_codex_workflow",
                    "docs/workflows/PARALLEL_CODEX_WORKFLOW.md",
                    "docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md",
                ),
                _plan_item(
                    "HRQ-003-apply_routing_chain",
                    "docs/workflows/APPLY_ROUTING_CHAIN.md",
                    "docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md",
                    ["docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_REGIME_SIGNAL_RULES.md"],
                ),
            ],
            "safe_cleanup_paths": [],
            "apply_ready_paths": [],
            "executable": False,
        },
    )
    _write_json(repo_root / draft.FINAL_GATE_PATH, {"final_status": "REVIEW_ONLY_READY", "executable": False})
    _write_json(repo_root / draft.CANDIDATES_PATH, {"approved_cleanup_candidate_count": 3, "executable": False})


def test_generates_three_review_only_drafts(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = draft.build_drafts(tmp_path).to_dict()

    assert result["draft_packets_generated_count"] == 3
    assert result["candidates_covered"] == draft.REQUIRED_CANDIDATES
    for item in result["draft_packets"]:
        assert item["executable"] is False
        assert item["review_only"] is True


def test_draft_packet_contains_required_fields(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = draft.build_drafts(tmp_path).to_dict()
    packet = result["draft_packets"][0]["draft_packet"]

    assert packet["candidate_id"] == "HRQ-001-worker_branch_and_lane_rules"
    assert packet["canonical_file"] == "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md"
    assert packet["duplicate_files"] == ["docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md"]
    assert packet["dependency_files"] == ["docs/audits/phase-5c-narrow-merge-plan.md"]
    assert packet["conflicting_sections"] == ["Purpose / Purpose"]
    assert packet["preserved_sections"] == ["Canonical Safety"]
    assert packet["sections_that_need_merge_review"] == ["Duplicate Guidance"]
    assert packet["proposed_merge_sequence"]
    assert packet["validation_requirements"]
    assert packet["rollback_requirements"]
    assert packet["human_approval_requirements"]


def test_draft_packets_are_not_executable_or_apply_ready(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = draft.build_drafts(tmp_path).to_dict()

    for item in result["draft_packets"]:
        packet = item["draft_packet"]
        assert packet["executable"] is False
        assert packet["review_only"] is True
        assert packet["safe_cleanup_paths"] == []
        assert packet["apply_ready_paths"] == []


def test_blocked_actions_include_source_mutations(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = draft.build_drafts(tmp_path).to_dict()

    assert "modify workflow docs" in result["blocked_actions"]
    assert "perform cleanup" in result["blocked_actions"]
    assert "canonicalize" in result["blocked_actions"]
    assert "generate executable APPLY packet" in result["blocked_actions"]
    for item in result["draft_packets"]:
        assert "modify workflow docs" in item["draft_packet"]["blocked_actions"]


def test_index_safety_contract_is_dry_run_review_only(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = draft.build_drafts(tmp_path).to_dict()

    assert result["executable"] is False
    assert result["review_only"] is True
    assert result["safe_cleanup_paths"] == []
    assert result["apply_ready_paths"] == []
    assert result["safety"]["draft_packets_only"] is True
    assert result["safety"]["workflow_docs_modified"] is False
    assert result["safety"]["cleanup_performed"] is False
    assert result["safety"]["canonicalization_performed"] is False
    assert result["safety"]["executable_apply_packet_generated"] is False
    assert result["safety"]["protected_docs_modified"] is False


def test_write_reports_writes_index_and_three_packets_under_output_root(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = draft.build_drafts(tmp_path)
    written = draft.write_reports(result, tmp_path)

    assert [path.name for path in written] == [
        "workflow_cleanup_apply_packet_draft_index.json",
        "workflow_cleanup_apply_packet_001.json",
        "workflow_cleanup_apply_packet_002.json",
        "workflow_cleanup_apply_packet_003.json",
    ]
    for path in written:
        assert path.resolve().parent == (tmp_path / draft.OUTPUT_ROOT).resolve()


def test_missing_review_plan_still_emits_non_executable_placeholders(tmp_path: Path) -> None:
    result = draft.build_drafts(tmp_path).to_dict()

    assert result["draft_packets_generated_count"] == 3
    for item in result["draft_packets"]:
        assert item["draft_packet"]["candidate_id"] in draft.REQUIRED_CANDIDATES
        assert item["draft_packet"]["executable"] is False
        assert item["draft_packet"]["review_only"] is True


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/workflow_cleanup_apply_packet_draft.py").read_text(encoding="utf-8")
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
