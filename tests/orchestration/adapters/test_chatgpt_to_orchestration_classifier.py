from pathlib import Path

from automation.orchestration.adapters.chatgpt_to_orchestration.classifier import classify_packet
from automation.orchestration.adapters.chatgpt_to_orchestration.models import RepoState, Status
from automation.orchestration.adapters.chatgpt_to_orchestration.parser import parse_packet
from automation.orchestration.adapters.chatgpt_to_orchestration.validator import validate_packet

FIXTURE_ROOT = Path("tests/fixtures/chatgpt_to_orchestration")
REPO_STATE = RepoState(branch="feature/full-operator-relief-closed-loop-v1")


def _classification(name: str):
    parsed = parse_packet((FIXTURE_ROOT / name).read_text(encoding="utf-8"))
    validation = validate_packet(parsed, REPO_STATE)
    return classify_packet(parsed, validation)


def test_valid_packet_classifies_as_preview():
    result = _classification("pass_report_only_packet.txt")

    assert result.status == Status.PREVIEW
    assert result.approval_required is False
    assert result.protected_action_requested is False


def test_placeholder_packet_fails_closed():
    result = _classification("fail_placeholder_packet.txt")

    assert result.status == Status.BLOCKED
    assert "PLACEHOLDER_PRESENT" in result.blocked_reasons
    assert "@filename" in result.placeholder_findings


def test_secret_risk_packet_fails_closed_and_redacts():
    result = _classification("fail_secret_risk_packet.txt")

    assert result.status == Status.BLOCKED
    assert "SECRET_OR_CREDENTIAL_RISK" in result.blocked_reasons
    assert result.redaction_status == "SECRET_RISK_BLOCKED"
