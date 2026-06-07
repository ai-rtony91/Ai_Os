from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from automation.operator_relief.dual_review_bridge import (
    CLASS_NON_CANONICAL_DEPENDENCY,
    CLASS_PARKED_CONFLICT,
    CLASS_PROTECTED_AUTHORITY,
    CLASS_SAFE_WORKFLOW,
    build_authority_bridge_review,
    write_authority_bridge_review,
)


NOW = datetime(2026, 6, 7, 13, 0, tzinfo=timezone.utc)
ROOT = "Reports/operator_relief/decision_packets"


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _workflow_diff(canonical: str, duplicate: str, dependencies: list[str] | None = None) -> dict:
    payload = {
        "report_type": "decision_diff",
        "executable": False,
        "canonical_candidate": canonical,
        "duplicate_candidate": duplicate,
        "dependency_paths": dependencies or [],
        "recommended_human_decision": "NEEDS_HUMAN_REVIEW",
        "safe_to_generate_apply_packet_later": False,
        "reasons": ["needs human review"],
    }
    if dependencies:
        payload["dependency_classification"] = "DEPENDENCY_NOT_CANONICAL"
    return payload


def _protected_packet(group_key: str, paths: list[str]) -> dict:
    return {
        "report_type": "operator_relief_canonical_decision_packet_v1",
        "executable": False,
        "group_key": group_key,
        "bucket": "PROTECTED_HUMAN_REVIEW",
        "paths": paths,
        "protected_review_required": True,
    }


def _sample_repo(tmp_path: Path) -> Path:
    _write(tmp_path / f"{ROOT}/canonical_decision_packet_index.json", {"report_type": "index", "executable": False})
    _write(
        tmp_path / f"{ROOT}/worker_branch_lane_rules_decision_diff.json",
        _workflow_diff(
            "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md",
            "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md",
        ),
    )
    _write(
        tmp_path / f"{ROOT}/parallel_codex_workflow_decision_diff.json",
        _workflow_diff(
            "docs/workflows/PARALLEL_CODEX_WORKFLOW.md",
            "docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md",
        ),
    )
    _write(
        tmp_path / f"{ROOT}/apply_routing_chain_decision_diff.json",
        _workflow_diff(
            "docs/workflows/APPLY_ROUTING_CHAIN.md",
            "docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md",
            ["docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_REGIME_SIGNAL_RULES.md"],
        ),
    )
    _write(
        tmp_path / f"{ROOT}/canonical_decision_packet_04_file_placement_rules.json",
        _protected_packet("file placement rules", ["docs/governance/FILE_PLACEMENT_RULES.md"]),
    )
    _write(
        tmp_path / f"{ROOT}/canonical_decision_packet_05_repo_folder_ownership_map.json",
        _protected_packet("repo folder ownership map", ["docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md"]),
    )
    _write(
        tmp_path / f"{ROOT}/canonical_decision_packet_06_portal_zone_model.json",
        _protected_packet("portal zone model", ["docs/AI_OS/security/secure_access/AIOS_PORTAL_ZONE_MODEL.md"]),
    )
    return tmp_path


def _review(tmp_path: Path, instruction: str) -> dict:
    return build_authority_bridge_review(
        repo_root=_sample_repo(tmp_path),
        bridge_goal="review next instruction",
        codex_report_summary="completed bounded local test",
        chatgpt_review_summary="reviewed",
        claude_review_summary="reviewed",
        reconciled_instruction=instruction,
        now=NOW,
    ).to_dict()


def test_protected_authority_blocks_continuation(tmp_path: Path) -> None:
    report = _review(tmp_path, "Edit docs/governance/FILE_PLACEMENT_RULES.md")

    assert report["authority_classification"] == CLASS_PROTECTED_AUTHORITY
    assert report["continue_allowed"] is False
    assert "docs/governance/FILE_PLACEMENT_RULES.md" in report["protected_paths_detected"]


def test_agents_authority_blocks_continuation(tmp_path: Path) -> None:
    report = _review(tmp_path, "Update AGENTS.md approval law")

    assert report["authority_classification"] == CLASS_PROTECTED_AUTHORITY
    assert report["continue_allowed"] is False
    assert "AGENTS.md" in report["protected_paths_detected"]


def test_parked_conflict_blocks_continuation(tmp_path: Path) -> None:
    report = _review(tmp_path, "Continue work on docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md")

    assert report["authority_classification"] == CLASS_PARKED_CONFLICT
    assert report["continue_allowed"] is False
    assert "worker branch and lane rules" in report["parked_conflicts_detected"]


def test_non_canonical_dependency_is_flagged(tmp_path: Path) -> None:
    report = _review(tmp_path, "Reference docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_REGIME_SIGNAL_RULES.md")

    assert report["authority_classification"] == CLASS_NON_CANONICAL_DEPENDENCY
    assert report["continue_allowed"] is True
    assert "docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_REGIME_SIGNAL_RULES.md" in report[
        "non_canonical_dependencies_detected"
    ]


def test_safe_workflow_classified_correctly(tmp_path: Path) -> None:
    report = _review(tmp_path, "Run a local unit test for automation/operator_relief/runtime_bridge.py")

    assert report["authority_classification"] == CLASS_SAFE_WORKFLOW
    assert report["continue_allowed"] is True
    assert report["yubikey_approval_required"] is False
    assert report["adb_escalation_required"] is False


def test_yubikey_approval_required_for_authority_review(tmp_path: Path) -> None:
    report = _review(tmp_path, "Edit docs/AI_OS/security/secure_access/AIOS_PORTAL_ZONE_MODEL.md")

    assert report["yubikey_approval_required"] is True
    assert report["yubikey_approval_evidence"]["decision"] == "HOLD_FOR_REVIEW"
    assert report["yubikey_approval_evidence"]["approval_granted"] is False


def test_adb_escalation_generated_for_authority_review(tmp_path: Path) -> None:
    report = _review(tmp_path, "Edit docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md")

    assert report["adb_escalation_required"] is True
    assert report["adb_escalation_plan"]["status"] == "ADB_ALERT_PLANNED"
    assert report["adb_escalation_plan"]["command_result"] is None


def test_executable_false(tmp_path: Path) -> None:
    report = _review(tmp_path, "Edit AGENTS.md")

    assert report["executable"] is False
    assert report["safety"]["executable"] is False


def test_no_source_mutation(tmp_path: Path) -> None:
    repo = _sample_repo(tmp_path)
    before = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())

    build_authority_bridge_review(
        repo,
        "goal",
        "codex summary",
        "chatgpt summary",
        "claude summary",
        "safe instruction",
        now=NOW,
    )

    after = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())
    assert after == before


def test_report_writes_only_under_bridge_reviews(tmp_path: Path) -> None:
    repo = _sample_repo(tmp_path)
    result = build_authority_bridge_review(
        repo,
        "goal",
        "codex summary",
        "chatgpt summary",
        "claude summary",
        "Edit AGENTS.md",
        now=NOW,
    )

    written = write_authority_bridge_review(result, repo)

    assert written == repo / "Reports/operator_relief/bridge_reviews/authority_bridge_review_20260607T130000Z.json"
    assert written.exists()


def test_source_scan_proves_no_git_actions_or_recursive_review_paths() -> None:
    source = Path("automation/operator_relief/dual_review_bridge.py").read_text(encoding="utf-8")
    forbidden_markers = [
        "subprocess",
        "os.system",
        "Popen",
        "git commit",
        "git push",
        "git merge",
        "git rebase",
        "force-push",
        "shutil.rmtree",
        "shutil.move",
        ".rename(",
        "Path.unlink",
        "OpenAI(",
        "openai.",
        "Codex(",
        "codex exec",
        "urllib",
        "HTTPServer",
        "TCPServer",
        ".listen(",
        ".bind(",
        "socket.",
        "watchdog",
        "daemon",
        "service",
    ]
    assert not any(marker in source for marker in forbidden_markers)
