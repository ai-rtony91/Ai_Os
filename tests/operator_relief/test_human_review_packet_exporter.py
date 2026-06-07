import json
from pathlib import Path

from automation.operator_relief.human_review_packet_exporter import DECISION_OPTIONS, build_packets, write_packets


QUEUE_PATH = "Reports/operator_relief/human_review_queue/human_review_queue.json"


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _sample_repo(tmp_path: Path) -> Path:
    queue = {
        "report_type": "operator_relief_human_review_queue_v1",
        "executable": False,
        "safe_cleanup_paths": [],
        "apply_ready_paths": [],
        "queue_items": [
            {
                "rank": 1,
                "queue_type": "WORKFLOW_AUTHORITY_CONFLICT",
                "group_key": "worker branch and lane rules",
                "paths": [
                    "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md",
                    "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md",
                ],
                "reason": "shared sections conflict",
                "classification": None,
            },
            {
                "rank": 2,
                "queue_type": "NON_CANONICAL_DEPENDENCY",
                "path": "docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_REGIME_SIGNAL_RULES.md",
                "reason": "PAPER_ONLY signal-rule authority, not APPLY routing canonical authority.",
                "classification": "DEPENDENCY_NOT_CANONICAL",
            },
        ],
    }
    _write(tmp_path / QUEUE_PATH, queue)
    return tmp_path


def test_builds_packets_from_queue_items(tmp_path: Path) -> None:
    result = build_packets(_sample_repo(tmp_path))

    assert result.packet_count == 2
    assert result.packets[0]["item_id"].startswith("HRQ-001")


def test_markdown_contains_required_packet_content(tmp_path: Path) -> None:
    packet = build_packets(_sample_repo(tmp_path)).packets[0]
    markdown = packet["markdown"]

    assert "Item ID" in markdown
    assert "Category" in markdown
    assert "Severity" in markdown
    assert "Authority type" in markdown
    assert "Files Involved" in markdown
    assert "Reason Human Review Is Required" in markdown
    assert "Blocked Actions" in markdown
    assert "Safety Flags" in markdown


def test_markdown_contains_only_allowed_decision_options(tmp_path: Path) -> None:
    packet = build_packets(_sample_repo(tmp_path)).packets[0]
    markdown = packet["markdown"]

    for option in DECISION_OPTIONS:
        assert option in markdown
    assert "DELETE" not in markdown


def test_dependency_classification_is_included_when_present(tmp_path: Path) -> None:
    packet = build_packets(_sample_repo(tmp_path)).packets[1]

    assert "DEPENDENCY_NOT_CANONICAL" in packet["markdown"]


def test_executable_false(tmp_path: Path) -> None:
    result = build_packets(_sample_repo(tmp_path))

    assert result.executable is False
    assert all(packet["executable"] is False for packet in result.packets)
    assert result.safety["executable"] is False


def test_safe_cleanup_and_apply_ready_paths_remain_empty(tmp_path: Path) -> None:
    result = build_packets(_sample_repo(tmp_path))

    assert result.safe_cleanup_paths == []
    assert result.apply_ready_paths == []


def test_write_packets_writes_only_under_human_review_packets(tmp_path: Path) -> None:
    repo = _sample_repo(tmp_path)
    result = build_packets(repo)

    written = write_packets(result, repo)

    assert written
    assert all(path.parent == repo / "Reports/operator_relief/human_review_packets" for path in written)
    assert all(path.suffix == ".md" for path in written)


def test_packet_markdown_is_review_only(tmp_path: Path) -> None:
    packet = build_packets(_sample_repo(tmp_path)).packets[0]

    assert '"executable": false' in packet["markdown"]
    assert "generate APPLY packet" in packet["markdown"]


def test_source_scan_proves_no_forbidden_execution_paths() -> None:
    source = Path("automation/operator_relief/human_review_packet_exporter.py").read_text(encoding="utf-8")
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
