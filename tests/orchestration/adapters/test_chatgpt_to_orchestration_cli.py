import json
from pathlib import Path

from automation.orchestration.adapters.chatgpt_to_orchestration.cli import main

FIXTURE_ROOT = Path("tests/fixtures/chatgpt_to_orchestration")


def test_cli_prints_preview_json_to_stdout(capsys):
    exit_code = main(
        [
            "--input-packet",
            str(FIXTURE_ROOT / "pass_report_only_packet.txt"),
            "--branch",
            "feature/full-operator-relief-closed-loop-v1",
            "--git-status-short-branch",
            "## feature/full-operator-relief-closed-loop-v1",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["status"] == "PREVIEW"
    assert payload["executable"] is False
