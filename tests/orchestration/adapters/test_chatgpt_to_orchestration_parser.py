from pathlib import Path

from automation.orchestration.adapters.chatgpt_to_orchestration.parser import parse_packet

FIXTURE_ROOT = Path("tests/fixtures/chatgpt_to_orchestration")


def test_parser_preserves_first_line_and_sections():
    packet = parse_packet((FIXTURE_ROOT / "pass_report_only_packet.txt").read_text(encoding="utf-8"))

    assert packet.first_line == "CODEX-ONLY PROMPT"
    assert "AI_OS EXECUTION TOKEN" in packet.markers
    assert packet.sections["PACKET ID"] == "PASS_REPORT_ONLY_PACKET_001"
    assert packet.sections["WORKTREE"] == "C:\\Dev\\Ai.Os"


def test_parser_keeps_placeholder_text_for_classifier():
    packet = parse_packet((FIXTURE_ROOT / "fail_placeholder_packet.txt").read_text(encoding="utf-8"))

    assert "@filename" in packet.raw_text
    assert "{feature}" in packet.raw_text
