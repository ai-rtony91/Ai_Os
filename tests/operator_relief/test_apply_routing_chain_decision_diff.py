import json
from pathlib import Path

from automation.operator_relief.apply_routing_chain_decision_diff import (
    AUTHORITY_CONFLICT,
    DEPENDENCY_NOT_CANONICAL,
    KEEP_WORKFLOWS_AS_CANONICAL,
    MERGE_UNIQUE_CONTENT_FIRST,
    NEEDS_HUMAN_REVIEW,
    build_decision_diff,
    write_report,
)


CANONICAL_PATH = "docs/workflows/APPLY_ROUTING_CHAIN.md"
DUPLICATE_PATH = "docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md"
DEPENDENCY_PATH = "docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_REGIME_SIGNAL_RULES.md"
PACKET_PATH = "Reports/operator_relief/decision_packets/canonical_decision_packet_03_apply_routing_chain.json"


BASE_DOC = """# AI_OS APPLY Routing Chain

## Purpose

The APPLY routing chain defines how a DRY_RUN item becomes an APPLY candidate.

## Chain

DRY_RUN -> validation -> approval request -> APPLY candidate -> exact-file evidence -> review package

## Required Evidence

- route ID
- next safe action
"""


TRADING_DEPENDENCY = """# Forex Signal Rules

## Signal Rule Flow

Local candles generate PAPER_ONLY Forex signals.

## Safety Boundary

No broker execution. No live trading. No credentials.
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_packet(repo: Path) -> None:
    payload = {
        "report_type": "operator_relief_canonical_decision_packet_v1",
        "executable": False,
        "current_canonical_candidate": CANONICAL_PATH,
        "duplicate_candidates": [DUPLICATE_PATH, DEPENDENCY_PATH],
        "dependencies": [DEPENDENCY_PATH],
    }
    _write(repo / PACKET_PATH, json.dumps(payload, indent=2))


def _sample_repo(
    tmp_path: Path,
    canonical: str = BASE_DOC,
    duplicate: str = BASE_DOC,
    dependency: str = TRADING_DEPENDENCY,
) -> Path:
    _write(tmp_path / CANONICAL_PATH, canonical)
    _write(tmp_path / DUPLICATE_PATH, duplicate)
    _write(tmp_path / DEPENDENCY_PATH, dependency)
    _write_packet(tmp_path)
    return tmp_path


def test_detects_identical_docs(tmp_path: Path) -> None:
    result = build_decision_diff(_sample_repo(tmp_path, dependency="Historical note only."))

    assert result.identical is True
    assert result.recommended_human_decision == KEEP_WORKFLOWS_AS_CANONICAL


def test_detects_duplicate_only_section(tmp_path: Path) -> None:
    duplicate = BASE_DOC + "\n## Blocked Conditions\n\nMissing approval blocks routing.\n"

    result = build_decision_diff(_sample_repo(tmp_path, duplicate=duplicate, dependency="Historical note only."))

    assert any(section["heading"] == "Blocked Conditions" for section in result.duplicate_only_sections)


def test_detects_canonical_only_section(tmp_path: Path) -> None:
    canonical = BASE_DOC + "\n## Non-Automation Statement\n\nThis chain does not commit or push.\n"

    result = build_decision_diff(_sample_repo(tmp_path, canonical=canonical, dependency="Historical note only."))

    assert any(section["heading"] == "Non-Automation Statement" for section in result.canonical_only_sections)


def test_detects_conflicting_section(tmp_path: Path) -> None:
    duplicate = BASE_DOC.replace("review package", "merge-ready package")

    result = build_decision_diff(_sample_repo(tmp_path, duplicate=duplicate, dependency="Historical note only."))

    assert any(section["section_key"] == "chain" for section in result.conflicting_sections)


def test_detects_duplicate_unique_authority(tmp_path: Path) -> None:
    duplicate = BASE_DOC + "\n## What This Does Not Automate\n\nThis chain does not stage files, commit, push, or merge.\n"

    result = build_decision_diff(_sample_repo(tmp_path, duplicate=duplicate, dependency="Historical note only."))

    assert any(section["heading"] == "What This Does Not Automate" for section in result.duplicate_unique_authority)


def test_classifies_trading_dependency_as_dependency_not_canonical_for_trading_only_authority(tmp_path: Path) -> None:
    result = build_decision_diff(_sample_repo(tmp_path))

    assert result.dependency_classification == DEPENDENCY_NOT_CANONICAL


def test_classifies_trading_dependency_as_authority_conflict_when_apply_routing_conflicts(tmp_path: Path) -> None:
    dependency = """# Trading Rules

## APPLY Routing Override

Trading evidence becomes a merge-ready package and can change APPLY route state transition rules.
"""

    result = build_decision_diff(_sample_repo(tmp_path, dependency=dependency))

    assert result.dependency_classification == AUTHORITY_CONFLICT
    assert result.recommended_human_decision == NEEDS_HUMAN_REVIEW


def test_recommends_merge_unique_content_first_when_duplicate_has_unique_content(tmp_path: Path) -> None:
    duplicate = BASE_DOC + "\n## Blocked Conditions\n\nMissing approval blocks routing.\n"

    result = build_decision_diff(_sample_repo(tmp_path, duplicate=duplicate, dependency="Historical note only."))

    assert result.recommended_human_decision == MERGE_UNIQUE_CONTENT_FIRST


def test_recommends_needs_human_review_when_conflicts_exist(tmp_path: Path) -> None:
    duplicate = BASE_DOC.replace("review package", "merge-ready package")

    result = build_decision_diff(_sample_repo(tmp_path, duplicate=duplicate, dependency="Historical note only."))

    assert result.recommended_human_decision == NEEDS_HUMAN_REVIEW
    assert result.safe_to_generate_apply_packet_later is False


def test_writes_only_under_reports_operator_relief_decision_packets(tmp_path: Path) -> None:
    repo = _sample_repo(tmp_path)
    result = build_decision_diff(repo)

    written = write_report(result, repo)

    assert written == repo / "Reports/operator_relief/decision_packets/apply_routing_chain_decision_diff.json"
    assert written.exists()


def test_executable_false(tmp_path: Path) -> None:
    result = build_decision_diff(_sample_repo(tmp_path))

    assert result.executable is False
    assert result.to_dict()["executable"] is False


def test_source_scan_proves_no_forbidden_execution_paths() -> None:
    source = Path("automation/operator_relief/apply_routing_chain_decision_diff.py").read_text(encoding="utf-8")
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
