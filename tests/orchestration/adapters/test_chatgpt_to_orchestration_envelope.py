from pathlib import Path

from automation.orchestration.adapters.chatgpt_to_orchestration.cli import run_preview
from automation.orchestration.adapters.chatgpt_to_orchestration.models import RepoState

FIXTURE_ROOT = Path("tests/fixtures/chatgpt_to_orchestration")
REPO_STATE = RepoState(
    branch="feature/full-operator-relief-closed-loop-v1",
    git_status_short_branch="## feature/full-operator-relief-closed-loop-v1",
)


def test_envelope_contains_required_preview_fields_and_executable_false():
    packet = (FIXTURE_ROOT / "pass_report_only_packet.txt").read_text(encoding="utf-8")
    envelope = run_preview(packet, REPO_STATE)

    assert envelope["schema"] == "AIOS_CHATGPT_TO_ORCHESTRATION_ENVELOPE.v1"
    assert envelope["packet_id"] == "PASS_REPORT_ONLY_PACKET_001"
    assert envelope["status"] == "PREVIEW"
    assert envelope["executable"] is False
    assert envelope["canonical_work_packet_preview"] is not None
    assert envelope["evidence_output"] is not None


def test_blocked_envelope_keeps_executable_false():
    packet = (FIXTURE_ROOT / "fail_branch_mismatch_packet.txt").read_text(encoding="utf-8")
    envelope = run_preview(packet, REPO_STATE)

    assert envelope["status"] == "BLOCKED"
    assert envelope["executable"] is False
    assert "AIOS-PROMPT-AUTH-STATE-MISMATCH" in envelope["blocked_reasons"]
