from pathlib import Path

from automation.orchestration.adapters.chatgpt_to_orchestration.cli import run_preview
from automation.orchestration.adapters.chatgpt_to_orchestration.models import RepoState

FIXTURE_ROOT = Path("tests/fixtures/chatgpt_to_orchestration")
REPO_STATE = RepoState(branch="feature/full-operator-relief-closed-loop-v1")


def test_work_packet_preview_is_present_for_valid_packet_and_preview_only():
    envelope = run_preview((FIXTURE_ROOT / "pass_report_only_packet.txt").read_text(encoding="utf-8"), REPO_STATE)
    preview = envelope["canonical_work_packet_preview"]

    assert preview["schema"] == "AIOS_CANONICAL_WORK_PACKET_PREVIEW.v1"
    assert preview["queue_owner"] == "automation/orchestration/work_packets/"
    assert preview["approval_owner"] == "automation/orchestration/approval_inbox/"
    assert preview["preview_only"] is True
    assert preview["executable"] is False


def test_work_packet_preview_absent_for_blocked_packet():
    envelope = run_preview((FIXTURE_ROOT / "fail_placeholder_packet.txt").read_text(encoding="utf-8"), REPO_STATE)

    assert envelope["status"] == "BLOCKED"
    assert envelope["canonical_work_packet_preview"] is None
