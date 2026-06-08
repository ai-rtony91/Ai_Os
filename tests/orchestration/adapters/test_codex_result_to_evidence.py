import json
from pathlib import Path

from automation.orchestration.adapters.codex_result_to_evidence.cli import main
from automation.orchestration.adapters.codex_result_to_evidence.evidence import run_preview
from automation.orchestration.adapters.codex_result_to_evidence.parser import parse_result

FIXTURE_ROOT = Path("tests/fixtures/codex_result_to_evidence")


def fixture(name: str) -> str:
    return (FIXTURE_ROOT / name).read_text(encoding="utf-8")


def test_parser_extracts_codex_final_sections():
    parsed = parse_result(fixture("success_complete.txt"))

    assert parsed.sections["SUMMARY"] == "Created the mapping report."
    assert "Reports/bridge_audit" in parsed.sections["FILES CHANGED"]
    assert parsed.sections["STATUS"] == "COMPLETE, NO COMMIT, NO PUSH"


def test_success_result_maps_to_aios_cli_evidence_and_executable_false():
    evidence = run_preview(fixture("success_complete.txt"))

    assert evidence["schema"] == "AIOS_CLI_EVIDENCE.v1"
    assert evidence["adapter_schema"] == "AIOS_CODEX_RESULT_EVIDENCE.v1"
    assert evidence["status"] == "COMPLETE"
    assert evidence["files_changed"] == ["Reports/bridge_audit/CODEX_RESULT_TO_EVIDENCE_ADAPTER_MAPPING.md"]
    assert evidence["commit_status"] == "NO_COMMIT"
    assert evidence["push_status"] == "NO_PUSH"
    assert evidence["approval_required"] is False
    assert evidence["display_alert"] is True
    assert evidence["sos_wake_required"] is False
    assert evidence["freshness_status"] == "ADAPTER_PARSE_TIME_ONLY"
    assert evidence["executable"] is False


def test_protected_action_requires_approval_and_sos():
    evidence = run_preview(fixture("blocked_protected_action.txt"))

    assert evidence["status"] == "NEEDS_APPROVAL"
    assert evidence["approval_required"] is True
    assert evidence["approval_status"] == "MISSING"
    assert evidence["protected_action_requested"] is True
    assert "GIT_COMMIT" in evidence["protected_actions"]
    assert evidence["sos_wake_required"] is True
    assert evidence["executable"] is False


def test_validation_failure_maps_to_failed_and_dirty_unknown():
    evidence = run_preview(fixture("validation_failed.txt"))

    assert evidence["status"] == "FAILED"
    assert "VALIDATION_FAILED" in evidence["blocked_reasons"]
    assert evidence["validator_results"][0]["status"] == "FAIL"
    assert evidence["dirty_files"] == ["scripts/backup/Start-AiOsT9SnapshotBackup.ps1"]
    assert evidence["dirty_state_class"] == "DIRTY_UNKNOWN"
    assert evidence["sos_wake_required"] is True


def test_missing_status_maps_to_unknown_without_sos():
    evidence = run_preview(fixture("missing_status.txt"))

    assert evidence["status"] == "UNKNOWN"
    assert evidence["status_impact"] == "OPERATOR_REVIEW"
    assert evidence["display_alert"] is True
    assert evidence["sos_wake_required"] is False
    assert evidence["executable"] is False


def test_secret_and_broker_risk_blocks_and_redacts():
    evidence = run_preview(fixture("secret_risk.txt"))

    assert evidence["status"] == "BLOCKED"
    assert "SECRET_OR_CREDENTIAL_RISK" in evidence["blocked_reasons"]
    assert "BROKER_OR_LIVE_TRADING_RISK" in evidence["blocked_reasons"]
    assert evidence["redaction_status"] == "SECRET_RISK_BLOCKED"
    assert evidence["sos_wake_required"] is True


def test_cli_prints_preview_json_to_stdout(capsys):
    exit_code = main(["--input-result", str(FIXTURE_ROOT / "success_complete.txt")])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["status"] == "COMPLETE"
    assert payload["executable"] is False
