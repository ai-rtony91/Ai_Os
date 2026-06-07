import json
from pathlib import Path

from automation.operator_relief.human_review_queue import build_queue, write_report


REGISTRY_PATH = "Reports/operator_relief/authority_registry/protected_authority_registry.json"


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _sample_repo(tmp_path: Path) -> Path:
    registry = {
        "report_type": "operator_relief_protected_authority_registry_v1",
        "executable": False,
        "source_decision_diff_reports": [
            "Reports/operator_relief/decision_packets/worker_branch_lane_rules_decision_diff.json",
            "Reports/operator_relief/decision_packets/parallel_codex_workflow_decision_diff.json",
            "Reports/operator_relief/decision_packets/apply_routing_chain_decision_diff.json",
        ],
        "parked_workflow_authority_conflicts": [
            {
                "group_key": "worker branch and lane rules",
                "likely_canonical_candidate": "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md",
                "paths": [
                    "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md",
                    "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md",
                ],
                "source_decision_diff_report": "Reports/operator_relief/decision_packets/worker_branch_lane_rules_decision_diff.json",
                "reason": "needs human review",
            },
            {
                "group_key": "parallel codex workflow",
                "likely_canonical_candidate": "docs/workflows/PARALLEL_CODEX_WORKFLOW.md",
                "paths": [
                    "docs/workflows/PARALLEL_CODEX_WORKFLOW.md",
                    "docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md",
                ],
                "source_decision_diff_report": "Reports/operator_relief/decision_packets/parallel_codex_workflow_decision_diff.json",
                "reason": "needs human review",
            },
            {
                "group_key": "apply routing chain",
                "likely_canonical_candidate": "docs/workflows/APPLY_ROUTING_CHAIN.md",
                "paths": [
                    "docs/workflows/APPLY_ROUTING_CHAIN.md",
                    "docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md",
                    "docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_REGIME_SIGNAL_RULES.md",
                ],
                "source_decision_diff_report": "Reports/operator_relief/decision_packets/apply_routing_chain_decision_diff.json",
                "reason": "needs human review",
            },
        ],
        "protected_authorities": [
            {
                "group_key": "file placement rules",
                "paths": ["docs/governance/FILE_PLACEMENT_RULES.md"],
                "source_decision_packet": "Reports/operator_relief/decision_packets/canonical_decision_packet_04_file_placement_rules.json",
                "reason": "protected",
            }
        ],
        "dependency_only_documents": [
            {
                "path": "docs/audits/phase-5c-narrow-merge-plan.md",
                "source_group": "worker branch and lane rules",
                "reason": "Dependency/evidence only; not cleanup approval.",
            }
        ],
        "non_canonical_dependencies": [
            {
                "path": "docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_REGIME_SIGNAL_RULES.md",
                "source_group": "apply routing chain",
                "classification": "DEPENDENCY_NOT_CANONICAL",
                "reason": "PAPER_ONLY signal-rule authority, not APPLY routing canonical authority.",
            }
        ],
        "human_review_required_paths": [
            "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md",
            "docs/workflows/PARALLEL_CODEX_WORKFLOW.md",
            "docs/workflows/APPLY_ROUTING_CHAIN.md",
            "docs/governance/FILE_PLACEMENT_RULES.md",
        ],
        "do_not_touch_paths": ["docs/governance/FILE_PLACEMENT_RULES.md"],
        "safe_cleanup_paths": [],
        "apply_ready_paths": [],
    }
    _write(tmp_path / REGISTRY_PATH, registry)
    return tmp_path


def _queue(tmp_path: Path) -> dict:
    return build_queue(_sample_repo(tmp_path)).to_dict()


def test_queue_includes_workflow_conflicts(tmp_path: Path) -> None:
    queue = _queue(tmp_path)

    keys = {item["group_key"] for item in queue["workflow_conflict_items"]}
    assert {"worker branch and lane rules", "parallel codex workflow", "apply routing chain"} <= keys


def test_queue_includes_protected_items(tmp_path: Path) -> None:
    queue = _queue(tmp_path)

    assert any(item["group_key"] == "file placement rules" for item in queue["protected_items"])


def test_queue_includes_dependency_only_items(tmp_path: Path) -> None:
    queue = _queue(tmp_path)

    assert any(item["path"] == "docs/audits/phase-5c-narrow-merge-plan.md" for item in queue["dependency_only_items"])


def test_queue_includes_non_canonical_dependencies(tmp_path: Path) -> None:
    queue = _queue(tmp_path)

    assert any(
        item["path"] == "docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_REGIME_SIGNAL_RULES.md"
        for item in queue["non_canonical_dependency_items"]
    )


def test_safe_cleanup_paths_remain_empty(tmp_path: Path) -> None:
    assert _queue(tmp_path)["safe_cleanup_paths"] == []


def test_apply_ready_paths_remain_empty(tmp_path: Path) -> None:
    assert _queue(tmp_path)["apply_ready_paths"] == []


def test_workflow_items_are_not_apply_ready(tmp_path: Path) -> None:
    queue = _queue(tmp_path)

    assert all(item["apply_ready"] is False for item in queue["workflow_conflict_items"])


def test_write_report_writes_only_under_human_review_queue(tmp_path: Path) -> None:
    repo = _sample_repo(tmp_path)
    result = build_queue(repo)

    written = write_report(result, repo)

    assert written == repo / "Reports/operator_relief/human_review_queue/human_review_queue.json"
    assert written.exists()


def test_executable_false(tmp_path: Path) -> None:
    queue = _queue(tmp_path)

    assert queue["executable"] is False
    assert queue["safety"]["executable"] is False


def test_source_scan_proves_no_forbidden_execution_paths() -> None:
    source = Path("automation/operator_relief/human_review_queue.py").read_text(encoding="utf-8")
    forbidden_markers = [
        "subprocess",
        "os.system",
        "Popen",
        "shutil.rmtree",
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
    assert not any(marker in source for marker in forbidden_markers)
