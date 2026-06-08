from pathlib import Path

from automation.operator_relief.human_review_decision_schema import (
    build_schema,
    validate_decision,
    write_schema,
)
from automation.operator_relief.human_review_packet_exporter import DECISION_OPTIONS


def _valid_payload() -> dict:
    return {
        "item_id": "HRQ-001-worker_branch_and_lane_rules",
        "reviewer": "Anthony",
        "decision": "KEEP_CANONICAL_AS_IS",
        "executable": False,
        "cleanup_approved": False,
        "canonicalization_approved": False,
        "apply_packet_generated": False,
        "safe_cleanup_paths": [],
        "apply_ready_paths": [],
    }


def test_schema_supports_only_allowed_decisions(tmp_path: Path) -> None:
    result = build_schema(tmp_path)

    assert result.allowed_decisions == list(DECISION_OPTIONS)
    assert result.schema["properties"]["decision"]["enum"] == list(DECISION_OPTIONS)


def test_valid_decision_has_no_errors() -> None:
    assert validate_decision(_valid_payload()) == []


def test_rejects_unknown_decision_value() -> None:
    payload = _valid_payload()
    payload["decision"] = "DELETE_DUPLICATE"

    assert any("unknown decision value" in error for error in validate_decision(payload))


def test_rejects_missing_reviewer_field() -> None:
    payload = _valid_payload()
    del payload["reviewer"]

    errors = validate_decision(payload)
    assert any("missing required field: reviewer" in error for error in errors)
    assert any("reviewer field is required" in error for error in errors)


def test_rejects_executable_true() -> None:
    payload = _valid_payload()
    payload["executable"] = True

    assert "executable=true is rejected" in validate_decision(payload)


def test_rejects_cleanup_approved_true() -> None:
    payload = _valid_payload()
    payload["cleanup_approved"] = True

    assert "cleanup_approved=true is rejected" in validate_decision(payload)


def test_rejects_canonicalization_approved_true() -> None:
    payload = _valid_payload()
    payload["canonicalization_approved"] = True

    assert "canonicalization_approved=true is rejected" in validate_decision(payload)


def test_rejects_apply_packet_generated_true() -> None:
    payload = _valid_payload()
    payload["apply_packet_generated"] = True

    assert "apply_packet_generated=true is rejected" in validate_decision(payload)


def test_rejects_non_empty_safe_cleanup_paths() -> None:
    payload = _valid_payload()
    payload["safe_cleanup_paths"] = ["docs/example.md"]

    assert "safe_cleanup_paths must be empty" in validate_decision(payload)


def test_rejects_non_empty_apply_ready_paths() -> None:
    payload = _valid_payload()
    payload["apply_ready_paths"] = ["docs/example.md"]

    assert "apply_ready_paths must be empty" in validate_decision(payload)


def test_write_schema_writes_only_under_human_review_decisions(tmp_path: Path) -> None:
    result = build_schema(tmp_path)

    written = write_schema(result, tmp_path)

    assert written == tmp_path / "Reports/operator_relief/human_review_decisions/human_review_decision_schema.json"
    assert written.exists()


def test_executable_false_and_paths_empty(tmp_path: Path) -> None:
    result = build_schema(tmp_path)

    assert result.executable is False
    assert result.safe_cleanup_paths == []
    assert result.apply_ready_paths == []
    assert result.safety["executable"] is False
    assert result.safety["records_real_approval"] is False


def test_source_scan_proves_no_forbidden_execution_paths() -> None:
    source = Path("automation/operator_relief/human_review_decision_schema.py").read_text(encoding="utf-8")
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
