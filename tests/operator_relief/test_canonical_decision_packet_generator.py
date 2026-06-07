import json
from pathlib import Path

from automation.operator_relief.canonical_decision_packet_generator import (
    DECISION_OPTIONS,
    build_decision_packets,
    write_decision_packets,
)


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _entry(rank: int, group_key: str, bucket: str, paths: list[str], protected: bool = False) -> dict:
    return {
        "rank": rank,
        "group_key": group_key,
        "category": "duplicate_workflow_docs",
        "paths": paths,
        "bucket": bucket,
        "confidence": 0.9,
        "reason": "sample reason",
        "recommended_next_action": "sample action",
        "protected_review_required": protected,
        "executable": False,
    }


def _sample_repo(tmp_path: Path) -> Path:
    top = [
        _entry(
            1,
            "file placement rules",
            "PROTECTED_HUMAN_REVIEW",
            ["docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md", "docs/governance/FILE_PLACEMENT_RULES.md"],
            True,
        ),
        _entry(
            2,
            "repo folder ownership map",
            "PROTECTED_HUMAN_REVIEW",
            ["docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md", "docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md"],
            True,
        ),
        _entry(
            3,
            "portal zone model",
            "PROTECTED_HUMAN_REVIEW",
            [
                "docs/AI_OS/security/phase_15_secure_access/AIOS_PORTAL_ZONE_MODEL.md",
                "docs/AI_OS/security/secure_access/AIOS_PORTAL_ZONE_MODEL.md",
            ],
            True,
        ),
        _entry(
            4,
            "worker branch and lane rules",
            "CANONICALIZATION_REVIEW_CANDIDATE",
            ["docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md", "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md"],
        ),
        _entry(
            5,
            "parallel codex workflow",
            "CANONICALIZATION_REVIEW_CANDIDATE",
            ["docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md", "docs/workflows/PARALLEL_CODEX_WORKFLOW.md"],
        ),
        _entry(
            6,
            "apply routing chain",
            "CANONICALIZATION_REVIEW_CANDIDATE",
            [
                "docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md",
                "docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_REGIME_SIGNAL_RULES.md",
                "docs/workflows/APPLY_ROUTING_CHAIN.md",
            ],
        ),
    ]
    payload = {
        "report_type": "operator_relief_canonical_authority_triage_v1",
        "generated_at": "2026-06-07T02:39:51+00:00",
        "source_canonical_audit_report": "Reports/operator_relief/audits/canonical_authority_audit.json",
        "executable": False,
        "top_10_next_review_targets": top,
        "canonicalization_review_candidates": top[3:],
        "protected_human_review": top[:3],
    }
    _write(tmp_path / "Reports/operator_relief/audits/canonical_authority_triage_20260607T023951Z.json", payload)
    return tmp_path


def _packets(tmp_path: Path) -> list[dict]:
    return build_decision_packets(_sample_repo(tmp_path)).packets


def _packet_by_key(packets: list[dict], group_key: str) -> dict:
    return next(packet for packet in packets if packet["group_key"] == group_key)


def test_generates_packet_for_worker_branch_and_lane_rules(tmp_path: Path) -> None:
    packet = _packet_by_key(_packets(tmp_path), "worker branch and lane rules")

    assert packet["current_canonical_candidate"] == "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md"
    assert packet["human_decision_required"] is True


def test_generates_packet_for_parallel_codex_workflow(tmp_path: Path) -> None:
    packet = _packet_by_key(_packets(tmp_path), "parallel codex workflow")

    assert packet["current_canonical_candidate"] == "docs/workflows/PARALLEL_CODEX_WORKFLOW.md"


def test_generates_packet_for_apply_routing_chain(tmp_path: Path) -> None:
    packet = _packet_by_key(_packets(tmp_path), "apply routing chain")

    assert packet["current_canonical_candidate"] == "docs/workflows/APPLY_ROUTING_CHAIN.md"
    assert "docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_REGIME_SIGNAL_RULES.md" in packet["dependencies"]


def test_protected_governance_packet_requires_human_review(tmp_path: Path) -> None:
    packet = _packet_by_key(_packets(tmp_path), "file placement rules")

    assert packet["protected_review_required"] is True
    assert packet["current_canonical_candidate"] is None
    assert "DO_NOT_TOUCH_WITHOUT_HUMAN_REVIEW" in packet["recommended_next_action"]


def test_protected_security_packet_requires_human_review(tmp_path: Path) -> None:
    packet = _packet_by_key(_packets(tmp_path), "portal zone model")

    assert packet["protected_review_required"] is True
    assert packet["current_canonical_candidate"] is None


def test_index_includes_generated_packets(tmp_path: Path) -> None:
    result = build_decision_packets(_sample_repo(tmp_path))

    assert result.index["packet_count"] == len(result.packets)
    assert any(item["group_key"] == "apply routing chain" for item in result.index["packets"])


def test_writes_only_under_reports_operator_relief_decision_packets(tmp_path: Path) -> None:
    repo = _sample_repo(tmp_path)
    result = build_decision_packets(repo)

    written = write_decision_packets(result, repo)

    assert written
    assert all(path.parent == repo / "Reports/operator_relief/decision_packets" for path in written)
    assert (repo / "Reports/operator_relief/decision_packets/canonical_decision_packet_index.json").exists()


def test_executable_false(tmp_path: Path) -> None:
    result = build_decision_packets(_sample_repo(tmp_path))

    assert result.executable is False
    assert all(packet["executable"] is False for packet in result.packets)
    assert result.index["executable"] is False
    assert list(DECISION_OPTIONS) == result.packets[0]["recommended_decision_options"]


def test_no_source_mutation(tmp_path: Path) -> None:
    repo = _sample_repo(tmp_path)
    before = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())

    build_decision_packets(repo)

    after = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())
    assert after == before


def test_source_scan_proves_no_forbidden_execution_paths() -> None:
    source = Path("automation/operator_relief/canonical_decision_packet_generator.py").read_text(encoding="utf-8")
    forbidden_markers = [
        "subprocess",
        "os.system",
        "Popen",
        "git commit",
        "git push",
        "git merge",
        "git rebase",
        "force-push",
        "OpenAI(",
        "openai.",
        "Codex(",
        "Start-Process",
        "HTTPServer",
        ".listen(",
        ".bind(",
    ]
    assert not any(marker in source for marker in forbidden_markers)
