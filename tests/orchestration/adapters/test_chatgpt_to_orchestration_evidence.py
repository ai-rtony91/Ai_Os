from pathlib import Path

from automation.orchestration.adapters.chatgpt_to_orchestration.cli import run_preview
from automation.orchestration.adapters.chatgpt_to_orchestration.models import RepoState

FIXTURE_ROOT = Path("tests/fixtures/chatgpt_to_orchestration")
REPO_STATE = RepoState(
    branch="feature/full-operator-relief-closed-loop-v1",
    git_status_short_branch="## feature/full-operator-relief-closed-loop-v1",
    dirty_state_class="REPORT_ONLY_UNTRACKED",
)


def test_evidence_is_aios_cli_evidence_compatible_and_non_executable():
    envelope = run_preview((FIXTURE_ROOT / "pass_report_only_packet.txt").read_text(encoding="utf-8"), REPO_STATE)
    evidence = envelope["evidence_output"]

    assert evidence["schema"] == "AIOS_CLI_EVIDENCE.v1"
    assert evidence["packet_id"] == "PASS_REPORT_ONLY_PACKET_001"
    assert evidence["branch"] == "feature/full-operator-relief-closed-loop-v1"
    assert evidence["dirty_state_class"] == "REPORT_ONLY_UNTRACKED"
    assert evidence["executable"] is False
    assert evidence["approval_status"] == "NOT_REQUIRED"


def test_evidence_records_blocked_secret_risk():
    envelope = run_preview((FIXTURE_ROOT / "fail_secret_risk_packet.txt").read_text(encoding="utf-8"), REPO_STATE)
    evidence = envelope["evidence_output"]

    assert evidence["status"] == "BLOCKED"
    assert evidence["redaction_status"] == "SECRET_RISK_BLOCKED"
    assert "SECRET_OR_CREDENTIAL_RISK" in evidence["blocked_reasons"]
