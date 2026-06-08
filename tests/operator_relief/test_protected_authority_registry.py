import json
from pathlib import Path

from automation.operator_relief.protected_authority_registry import (
    DO_NOT_TOUCH,
    build_registry,
    write_report,
)


ROOT = "Reports/operator_relief/decision_packets"


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _workflow_diff(
    canonical: str,
    duplicate: str,
    group_decision: str = "NEEDS_HUMAN_REVIEW",
    dependencies: list[str] | None = None,
    dependency_classification: str | None = None,
) -> dict:
    payload = {
        "report_type": "decision_diff",
        "executable": False,
        "canonical_candidate": canonical,
        "duplicate_candidate": duplicate,
        "dependency_paths": dependencies or [],
        "recommended_human_decision": group_decision,
        "safe_to_generate_apply_packet_later": False,
        "reasons": ["needs review"],
    }
    if dependency_classification:
        payload["dependency_classification"] = dependency_classification
    return payload


def _protected_packet(group_key: str, paths: list[str]) -> dict:
    return {
        "report_type": "operator_relief_canonical_decision_packet_v1",
        "executable": False,
        "group_key": group_key,
        "bucket": "PROTECTED_HUMAN_REVIEW",
        "paths": paths,
        "protected_review_required": True,
        "current_canonical_candidate": None,
        "recommended_next_action": "DO_NOT_TOUCH_WITHOUT_HUMAN_REVIEW",
    }


def _sample_repo(tmp_path: Path) -> Path:
    _write(
        tmp_path / f"{ROOT}/canonical_decision_packet_index.json",
        {"report_type": "index", "executable": False, "packets": []},
    )
    _write(
        tmp_path / f"{ROOT}/worker_branch_lane_rules_decision_diff.json",
        _workflow_diff(
            "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md",
            "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md",
            dependencies=["docs/audits/phase-5c-narrow-merge-plan.md"],
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
            dependencies=["docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_REGIME_SIGNAL_RULES.md"],
            dependency_classification="DEPENDENCY_NOT_CANONICAL",
        ),
    )
    _write(
        tmp_path / f"{ROOT}/canonical_decision_packet_04_file_placement_rules.json",
        _protected_packet(
            "file placement rules",
            [
                "docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md",
                "docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES_DRY_RUN.md",
                "docs/governance/FILE_PLACEMENT_RULES.md",
            ],
        ),
    )
    _write(
        tmp_path / f"{ROOT}/canonical_decision_packet_05_repo_folder_ownership_map.json",
        _protected_packet(
            "repo folder ownership map",
            [
                "docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md",
                "docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP_DRY_RUN.md",
                "docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md",
            ],
        ),
    )
    _write(
        tmp_path / f"{ROOT}/canonical_decision_packet_06_portal_zone_model.json",
        _protected_packet(
            "portal zone model",
            [
                "docs/AI_OS/security/phase_15_secure_access/AIOS_PORTAL_ZONE_MODEL.md",
                "docs/AI_OS/security/secure_access/AIOS_PORTAL_ZONE_MODEL.md",
            ],
        ),
    )
    return tmp_path


def _registry(tmp_path: Path) -> dict:
    return build_registry(_sample_repo(tmp_path)).to_dict()


def test_registry_includes_worker_branch_lane_parked_conflict(tmp_path: Path) -> None:
    registry = _registry(tmp_path)

    assert any(item["group_key"] == "worker branch and lane rules" for item in registry["parked_workflow_authority_conflicts"])


def test_registry_includes_parallel_codex_parked_conflict(tmp_path: Path) -> None:
    registry = _registry(tmp_path)

    assert any(item["group_key"] == "parallel codex workflow" for item in registry["parked_workflow_authority_conflicts"])


def test_registry_includes_apply_routing_parked_conflict(tmp_path: Path) -> None:
    registry = _registry(tmp_path)

    assert any(item["group_key"] == "apply routing chain" for item in registry["parked_workflow_authority_conflicts"])


def test_registry_includes_file_placement_rules_protected_authority(tmp_path: Path) -> None:
    registry = _registry(tmp_path)

    entry = next(item for item in registry["protected_authorities"] if item["group_key"] == "file placement rules")
    assert entry["action"] == DO_NOT_TOUCH


def test_registry_includes_repo_folder_ownership_map_protected_authority(tmp_path: Path) -> None:
    registry = _registry(tmp_path)

    assert any(item["group_key"] == "repo folder ownership map" for item in registry["protected_authorities"])


def test_registry_includes_portal_zone_model_protected_authority(tmp_path: Path) -> None:
    registry = _registry(tmp_path)

    assert any(item["group_key"] == "portal zone model" for item in registry["protected_authorities"])


def test_safe_cleanup_paths_is_empty(tmp_path: Path) -> None:
    assert _registry(tmp_path)["safe_cleanup_paths"] == []


def test_apply_ready_paths_is_empty(tmp_path: Path) -> None:
    assert _registry(tmp_path)["apply_ready_paths"] == []


def test_do_not_touch_paths_includes_protected_governance_security_paths(tmp_path: Path) -> None:
    registry = _registry(tmp_path)

    assert "docs/governance/FILE_PLACEMENT_RULES.md" in registry["do_not_touch_paths"]
    assert "docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md" in registry["do_not_touch_paths"]
    assert "docs/AI_OS/security/secure_access/AIOS_PORTAL_ZONE_MODEL.md" in registry["do_not_touch_paths"]


def test_human_review_required_paths_includes_all_parked_and_protected_paths(tmp_path: Path) -> None:
    registry = _registry(tmp_path)

    assert "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md" in registry["human_review_required_paths"]
    assert "docs/workflows/PARALLEL_CODEX_WORKFLOW.md" in registry["human_review_required_paths"]
    assert "docs/workflows/APPLY_ROUTING_CHAIN.md" in registry["human_review_required_paths"]
    assert "docs/governance/FILE_PLACEMENT_RULES.md" in registry["human_review_required_paths"]


def test_dependency_only_documents_includes_phase_5c_when_present(tmp_path: Path) -> None:
    registry = _registry(tmp_path)

    assert any(item["path"] == "docs/audits/phase-5c-narrow-merge-plan.md" for item in registry["dependency_only_documents"])


def test_non_canonical_dependencies_includes_forex_rules_when_present(tmp_path: Path) -> None:
    registry = _registry(tmp_path)

    assert any(
        item["path"] == "docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_REGIME_SIGNAL_RULES.md"
        and "PAPER_ONLY signal-rule authority" in item["reason"]
        for item in registry["non_canonical_dependencies"]
    )


def test_write_report_writes_only_under_authority_registry(tmp_path: Path) -> None:
    repo = _sample_repo(tmp_path)
    result = build_registry(repo)

    written = write_report(result, repo)

    assert written == repo / "Reports/operator_relief/authority_registry/protected_authority_registry.json"
    assert written.exists()


def test_executable_false(tmp_path: Path) -> None:
    registry = _registry(tmp_path)

    assert registry["executable"] is False
    assert registry["safety"]["executable"] is False


def test_source_scan_proves_no_forbidden_execution_paths() -> None:
    source = Path("automation/operator_relief/protected_authority_registry.py").read_text(encoding="utf-8")
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
