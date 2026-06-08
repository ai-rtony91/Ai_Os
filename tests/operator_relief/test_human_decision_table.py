import json
from pathlib import Path

from automation.operator_relief.human_decision_table import (
    STATUS_DO_NOT_TOUCH,
    STATUS_PARKED_CONFLICT,
    build_human_decision_table,
    write_reports,
)


ROOT = "Reports/operator_relief"
PACKET_ROOT = f"{ROOT}/decision_packets"


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _packet(group_key: str, packet_file: str, protected: bool = True) -> dict:
    return {
        "rank": 99,
        "group_key": group_key,
        "bucket": "PROTECTED_HUMAN_REVIEW" if protected else "CANONICALIZATION_REVIEW_CANDIDATE",
        "packet_file": packet_file,
        "protected_review_required": protected,
        "recommended_next_action": "review only",
        "executable": False,
    }


def _decision_packet(group_key: str, paths: list[str], protected: bool = True) -> dict:
    return {
        "report_type": "operator_relief_canonical_decision_packet_v1",
        "executable": False,
        "group_key": group_key,
        "bucket": "PROTECTED_HUMAN_REVIEW" if protected else "CANONICALIZATION_REVIEW_CANDIDATE",
        "paths": paths,
        "current_canonical_candidate": None,
        "duplicate_candidates": paths,
        "dependencies": [],
        "protected_review_required": protected,
        "recommended_next_action": "review only",
    }


def _registry() -> dict:
    return {
        "report_type": "operator_relief_protected_authority_registry_v1",
        "executable": False,
        "source_decision_packet_index": f"{PACKET_ROOT}/canonical_decision_packet_index.json",
        "source_decision_diff_reports": [
            f"{PACKET_ROOT}/worker_branch_lane_rules_decision_diff.json",
            f"{PACKET_ROOT}/parallel_codex_workflow_decision_diff.json",
            f"{PACKET_ROOT}/apply_routing_chain_decision_diff.json",
        ],
        "parked_workflow_authority_conflicts": [
            {
                "group_key": "worker branch and lane rules",
                "likely_canonical_candidate": "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md",
                "duplicate_candidate": "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md",
                "paths": [
                    "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md",
                    "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md",
                    "docs/audits/phase-5c-narrow-merge-plan.md",
                ],
                "source_decision_diff_report": f"{PACKET_ROOT}/worker_branch_lane_rules_decision_diff.json",
                "apply_ready": False,
            },
            {
                "group_key": "parallel codex workflow",
                "likely_canonical_candidate": "docs/workflows/PARALLEL_CODEX_WORKFLOW.md",
                "duplicate_candidate": "docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md",
                "paths": [
                    "docs/workflows/PARALLEL_CODEX_WORKFLOW.md",
                    "docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md",
                ],
                "source_decision_diff_report": f"{PACKET_ROOT}/parallel_codex_workflow_decision_diff.json",
                "apply_ready": False,
            },
            {
                "group_key": "apply routing chain",
                "likely_canonical_candidate": "docs/workflows/APPLY_ROUTING_CHAIN.md",
                "duplicate_candidate": "docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md",
                "paths": [
                    "docs/workflows/APPLY_ROUTING_CHAIN.md",
                    "docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md",
                    "docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_REGIME_SIGNAL_RULES.md",
                ],
                "source_decision_diff_report": f"{PACKET_ROOT}/apply_routing_chain_decision_diff.json",
                "apply_ready": False,
            },
        ],
        "protected_authorities": [
            {
                "group_key": "file placement rules",
                "paths": [
                    "docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md",
                    "docs/governance/FILE_PLACEMENT_RULES.md",
                ],
                "source_decision_packet": f"{PACKET_ROOT}/canonical_decision_packet_04_file_placement_rules.json",
            },
            {
                "group_key": "repo folder ownership map",
                "paths": [
                    "docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md",
                    "docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md",
                ],
                "source_decision_packet": f"{PACKET_ROOT}/canonical_decision_packet_05_repo_folder_ownership_map.json",
            },
            {
                "group_key": "portal zone model",
                "paths": [
                    "docs/AI_OS/security/phase_15_secure_access/AIOS_PORTAL_ZONE_MODEL.md",
                    "docs/AI_OS/security/secure_access/AIOS_PORTAL_ZONE_MODEL.md",
                ],
                "source_decision_packet": f"{PACKET_ROOT}/canonical_decision_packet_06_portal_zone_model.json",
            },
        ],
        "dependency_only_documents": [
            {
                "path": "docs/audits/phase-5c-narrow-merge-plan.md",
                "source_group": "worker branch and lane rules",
                "source_decision_diff_report": f"{PACKET_ROOT}/worker_branch_lane_rules_decision_diff.json",
            }
        ],
        "non_canonical_dependencies": [
            {
                "path": "docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_REGIME_SIGNAL_RULES.md",
                "source_group": "apply routing chain",
                "classification": "DEPENDENCY_NOT_CANONICAL",
            }
        ],
        "safe_cleanup_paths": [],
        "apply_ready_paths": [],
    }


def _sample_repo(tmp_path: Path) -> Path:
    _write(tmp_path / f"{ROOT}/authority_registry/protected_authority_registry.json", _registry())
    packets = [
        _packet("worker branch and lane rules", "canonical_decision_packet_01_worker_branch_and_lane_rules.json", False),
        _packet("parallel codex workflow", "canonical_decision_packet_02_parallel_codex_workflow.json", False),
        _packet("apply routing chain", "canonical_decision_packet_03_apply_routing_chain.json", False),
        _packet("file placement rules", "canonical_decision_packet_04_file_placement_rules.json"),
        _packet("repo folder ownership map", "canonical_decision_packet_05_repo_folder_ownership_map.json"),
        _packet("portal zone model", "canonical_decision_packet_06_portal_zone_model.json"),
        _packet("privacy compliance boundary", "canonical_decision_packet_07_privacy_compliance_boundary.json"),
    ]
    _write(
        tmp_path / f"{PACKET_ROOT}/canonical_decision_packet_index.json",
        {
            "report_type": "operator_relief_canonical_decision_packet_index_v1",
            "executable": False,
            "packets": packets,
        },
    )
    _write(
        tmp_path / f"{PACKET_ROOT}/canonical_decision_packet_07_privacy_compliance_boundary.json",
        _decision_packet("privacy compliance boundary", ["docs/governance/PRIVACY.md"]),
    )
    _write(
        tmp_path / f"{ROOT}/audits/canonical_authority_audit_20260607T022301Z.json",
        {"report_type": "audit", "executable": False},
    )
    _write(
        tmp_path / f"{ROOT}/audits/canonical_authority_triage_20260607T023951Z.json",
        {"report_type": "triage", "executable": False},
    )
    return tmp_path


def _table(tmp_path: Path) -> dict:
    return build_human_decision_table(_sample_repo(tmp_path)).to_dict()


def _row(table: dict, group: str) -> dict:
    return next(row for row in table["rows"] if row["Group"] == group)


def test_worker_branch_lane_rules_is_parked_conflict(tmp_path: Path) -> None:
    row = _row(_table(tmp_path), "Worker Branch And Lane Rules")

    assert row["Status"] == STATUS_PARKED_CONFLICT
    assert row["Apply Ready"] is False


def test_parallel_codex_workflow_is_parked_conflict(tmp_path: Path) -> None:
    row = _row(_table(tmp_path), "Parallel Codex Workflow")

    assert row["Status"] == STATUS_PARKED_CONFLICT


def test_apply_routing_chain_is_parked_conflict(tmp_path: Path) -> None:
    row = _row(_table(tmp_path), "Apply Routing Chain")

    assert row["Status"] == STATUS_PARKED_CONFLICT


def test_file_placement_rules_is_do_not_touch(tmp_path: Path) -> None:
    row = _row(_table(tmp_path), "File Placement Rules")

    assert row["Status"] == STATUS_DO_NOT_TOUCH
    assert row["Protected"] is True


def test_repo_folder_ownership_map_is_do_not_touch(tmp_path: Path) -> None:
    assert _row(_table(tmp_path), "Repo Folder Ownership Map")["Status"] == STATUS_DO_NOT_TOUCH


def test_portal_zone_model_is_do_not_touch(tmp_path: Path) -> None:
    assert _row(_table(tmp_path), "Portal Zone Model")["Status"] == STATUS_DO_NOT_TOUCH


def test_safe_cleanup_and_apply_ready_paths_remain_empty(tmp_path: Path) -> None:
    table = _table(tmp_path)

    assert table["safe_cleanup_paths"] == []
    assert table["apply_ready_paths"] == []
    assert table["counts"]["apply_ready_count"] == 0


def test_additional_packet_rows_are_included_from_index(tmp_path: Path) -> None:
    row = _row(_table(tmp_path), "Privacy Compliance Boundary")

    assert row["Status"] == "PROTECTED_HUMAN_REVIEW"
    assert row["Protected"] is True


def test_counts_include_required_operator_buckets(tmp_path: Path) -> None:
    counts = _table(tmp_path)["counts"]

    assert counts["parked_conflict_count"] == 3
    assert counts["do_not_touch_count"] == 3
    assert counts["protected_count"] == 4


def test_source_reports_include_audit_triage_registry_and_index(tmp_path: Path) -> None:
    source_reports = _table(tmp_path)["source_reports"]

    assert source_reports["protected_authority_registry"] == f"{ROOT}/authority_registry/protected_authority_registry.json"
    assert source_reports["canonical_authority_audit"] == f"{ROOT}/audits/canonical_authority_audit_20260607T022301Z.json"
    assert source_reports["canonical_authority_triage"] == f"{ROOT}/audits/canonical_authority_triage_20260607T023951Z.json"
    assert source_reports["canonical_decision_packet_index"] == f"{PACKET_ROOT}/canonical_decision_packet_index.json"


def test_write_reports_writes_only_under_decision_table(tmp_path: Path) -> None:
    repo = _sample_repo(tmp_path)
    result = build_human_decision_table(repo)

    written = write_reports(result, repo)

    assert written == [
        repo / f"{ROOT}/decision_table/human_decision_table.json",
        repo / f"{ROOT}/decision_table/human_decision_table.md",
    ]
    assert all(path.exists() for path in written)


def test_executable_false(tmp_path: Path) -> None:
    table = _table(tmp_path)

    assert table["executable"] is False
    assert table["safety"]["executable"] is False


def test_source_scan_proves_no_forbidden_execution_paths() -> None:
    source = Path("automation/operator_relief/human_decision_table.py").read_text(encoding="utf-8")
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
