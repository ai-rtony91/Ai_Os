from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief import workflow_cleanup_review_plan as plan


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _diff_payload(canonical: str, duplicate: str, dependency_paths: list[str] | None = None) -> dict:
    return {
        "canonical_candidate": canonical,
        "duplicate_candidate": duplicate,
        "dependency_paths": dependency_paths or [],
        "duplicate_unique_authority": [{"heading": "Duplicate Unique Rule"}],
        "canonical_only_sections": [{"heading": "Canonical Rule"}],
        "conflicting_sections": [{"canonical_heading": "Purpose", "duplicate_heading": "Purpose"}],
        "dependency_unique_authority": [{"heading": "Dependency Evidence"}] if dependency_paths else [],
        "recommended_human_decision": "NEEDS_HUMAN_REVIEW",
        "safe_to_generate_apply_packet_later": False,
        "executable": False,
    }


def _write_inputs(repo_root: Path) -> None:
    _write_json(
        repo_root / plan.CANDIDATES_PATH,
        {
            "approved_cleanup_candidate_count": 3,
            "approved_cleanup_candidates": [
                {"item_id": "HRQ-001-worker_branch_and_lane_rules"},
                {"item_id": "HRQ-002-parallel_codex_workflow"},
                {"item_id": "HRQ-003-apply_routing_chain"},
            ],
            "safe_cleanup_paths": [],
            "apply_ready_paths": [],
            "executable": False,
        },
    )
    _write_json(
        repo_root / plan.FINAL_GATE_PATH,
        {
            "final_status": "REVIEW_ONLY_READY",
            "safe_cleanup_paths": [],
            "apply_ready_paths": [],
            "executable": False,
        },
    )
    diffs = {
        "worker_branch_lane_rules_decision_diff.json": _diff_payload(
            "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md",
            "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md",
            ["docs/audits/phase-5c-narrow-merge-plan.md"],
        ),
        "parallel_codex_workflow_decision_diff.json": _diff_payload(
            "docs/workflows/PARALLEL_CODEX_WORKFLOW.md",
            "docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md",
        ),
        "apply_routing_chain_decision_diff.json": _diff_payload(
            "docs/workflows/APPLY_ROUTING_CHAIN.md",
            "docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md",
            ["docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_REGIME_SIGNAL_RULES.md"],
        ),
    }
    for filename, payload in diffs.items():
        _write_json(repo_root / plan.DECISION_PACKET_ROOT / filename, payload)


def test_plan_includes_three_workflow_candidates(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()

    assert result["candidates_included_count"] == 3
    assert [item["item_id"] for item in result["candidates_included"]] == [
        "HRQ-001-worker_branch_and_lane_rules",
        "HRQ-002-parallel_codex_workflow",
        "HRQ-003-apply_routing_chain",
    ]


def test_plan_includes_files_and_dependency_only_files(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()
    worker = result["candidates_included"][0]
    apply = result["candidates_included"][2]

    assert worker["canonical_file"] == "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md"
    assert worker["duplicate_file"] == "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md"
    assert worker["dependency_only_files"] == ["docs/audits/phase-5c-narrow-merge-plan.md"]
    assert apply["dependency_only_files"] == ["docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_REGIME_SIGNAL_RULES.md"]


def test_plan_includes_merge_conflict_and_preserve_sections(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()
    item = result["candidates_included"][0]

    assert item["sections_that_need_merge_review"] == ["Duplicate Unique Rule"]
    assert item["sections_that_conflict"] == ["Purpose / Purpose"]
    assert item["sections_that_must_be_preserved"] == ["Canonical Rule", "Dependency Evidence"]


def test_plan_blocks_source_mutating_actions(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()

    assert "modify workflow docs" in result["blocked_actions"]
    assert "perform cleanup" in result["blocked_actions"]
    assert "generate APPLY packet" in result["blocked_actions"]
    for item in result["candidates_included"]:
        assert item["blocked_actions"] == result["blocked_actions"]


def test_plan_requires_evidence_before_apply(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()
    evidence = result["candidates_included"][0]["required_evidence_before_apply"]

    assert "Read the canonical file and duplicate file directly." in evidence
    assert "Confirm human approval before any source document edit." in evidence


def test_output_contract_is_review_only(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path).to_dict()

    assert result["executable"] is False
    assert result["safe_cleanup_paths"] == []
    assert result["apply_ready_paths"] == []
    assert result["safety"]["review_plan_only"] is True
    assert result["safety"]["workflow_docs_modified"] is False
    assert result["safety"]["cleanup_performed"] is False
    assert result["safety"]["canonicalization_performed"] is False
    assert result["safety"]["apply_packet_generated"] is False
    assert result["safety"]["protected_docs_modified"] is False


def test_write_reports_writes_json_and_markdown_under_output_root(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path)
    written = plan.write_reports(result, tmp_path)

    assert [path.name for path in written] == [
        "workflow_cleanup_review_plan.json",
        "workflow_cleanup_review_plan.md",
    ]
    for path in written:
        assert path.resolve().parent == (tmp_path / plan.OUTPUT_ROOT).resolve()


def test_render_markdown_contains_review_only_plan(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = plan.build_plan(tmp_path)
    markdown = plan.render_markdown(result)

    assert "# Workflow Cleanup Review Plan" in markdown
    assert '"executable": false' in markdown
    assert "HRQ-001-worker_branch_and_lane_rules" in markdown
    assert "### Blocked Actions" in markdown


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/workflow_cleanup_review_plan.py").read_text(encoding="utf-8")
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
