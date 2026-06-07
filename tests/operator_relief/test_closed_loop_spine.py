from __future__ import annotations

from pathlib import Path


def test_closed_loop_spine_sources_have_no_forbidden_runtime_markers() -> None:
    files = [
        Path("automation/operator_relief/cli_bridge.py"),
        Path("automation/operator_relief/supervisor_loop.py"),
        Path("automation/operator_relief/packet_queue.py"),
        Path("automation/operator_relief/next_mission_engine.py"),
        Path("automation/operator_relief/engine_room_telemetry.py"),
    ]
    source = "\n".join(path.read_text(encoding="utf-8") for path in files)
    forbidden_markers = [
        "OPENAI_API_KEY",
        "OpenAI(",
        "openai.",
        "Codex(",
        "subprocess.run",
        "Popen",
        "os.system",
        "shell=True",
        "git push",
        "git merge",
        "git rebase",
        "send_adb_sos(",
        "live_trading = True",
        "broker_api = True",
        "secrets = True",
    ]
    for marker in forbidden_markers:
        assert marker not in source


def test_validator_pass_text_is_not_approval_in_spine_source() -> None:
    source = Path("automation/operator_relief/supervisor_loop.py").read_text(encoding="utf-8")
    assert "VALIDATOR_NOT_RUN_BY_SUPERVISOR" in source
    assert "APPROVAL_CLEAR" in source
    assert "validator PASS" not in source
