"""Tests for Get-AiOsActionRecommendation.DRY_RUN.ps1 relay SOS classification wiring."""

from pathlib import Path
import json
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[2]
ACTION_RECOMMENDATION_SCRIPT = REPO_ROOT / "automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1"
NEW_RELAY_MESSAGE_SCRIPT = REPO_ROOT / "automation/orchestration/relay_bus/New-AiOsRelayMessage.DRY_RUN.ps1"
RELAY_INBOX = REPO_ROOT / "control/relay_bus/messages/inbox"


def _run_script_json(script: Path, args: list[str]) -> dict:
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script),
        "-OutputJson",
        *args,
    ]
    raw = subprocess.check_output(cmd, cwd=str(REPO_ROOT), text=True)
    return json.loads(raw.strip())


def _clear_relay_inbox() -> None:
    for message_file in RELAY_INBOX.glob("*.json"):
        if message_file.name != ".gitkeep":
            message_file.unlink()


def _seed_relay_message(message_id: str, payload_text: str, message_type: str = "codex_final_report") -> None:
    subprocess.check_output(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(NEW_RELAY_MESSAGE_SCRIPT),
            "-Actor",
            "codex_cli",
            "-TargetActor",
            "powershell_operator",
            "-PacketId",
            message_id,
            "-Branch",
            "feature/action-recommendation-relay-sos-v1",
            "-MessageType",
            message_type,
            "-Intent",
            "handoff summary",
            "-Status",
            "pending",
            "-PayloadText",
            json.dumps(
                {
                    "message_id": message_id,
                    "content": payload_text,
                }
            ),
            "-Mode",
            "APPLY",
        ],
        cwd=str(REPO_ROOT),
    )


def _seed_relay_message_json(message_id: str, payload_text: str) -> Path:
    relay_file = RELAY_INBOX / f"{message_id}.json"
    relay_file.write_text(
        json.dumps(
            {
                "schema": "AIOS_RELAY_MESSAGE.v1",
                "message_id": message_id,
                "created_utc": "2026-06-13T00:00:00Z",
                "actor": "codex_cli",
                "target_actor": "powershell_operator",
                "packet_id": message_id,
                "branch": "feature/action-recommendation-relay-sos-v1",
                "message_type": "codex_final_report",
                "intent": "handoff summary",
                "status": "pending",
                "payload_text": payload_text,
                "requires_human_review": True,
                "execution_allowed": False,
                "can_continue_without_anthony": False,
                "next_action": "review needed",
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return relay_file


def _file_set(root: Path) -> set[str]:
    return {
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }


def test_action_recommendation_empty_relay_bus_keeps_default_no_active_packet_logic() -> None:
    _clear_relay_inbox()

    pre = _file_set(REPO_ROOT)
    out = _run_script_json(ACTION_RECOMMENDATION_SCRIPT, [])
    post = _file_set(REPO_ROOT)

    assert out["mode"] == "READ_ONLY"
    assert out["relay_sos_escalation_status"] in {"NOT_APPLICABLE", ""}
    assert out["relay_sos_anthony_required"] is False
    assert out["relay_sos_routine_review_allowed"] is False
    assert out["relay_sos_next_safe_action"] in {"", None, "No SOS escalation needed."}
    assert out["packet_status"] in {"no_active_packet", "campaign_ready"}
    assert pre == post


def test_action_recommendation_routine_relay_sos_classification() -> None:
    _clear_relay_inbox()
    try:
        _seed_relay_message(
            message_id="AIOS-RELAY-ACTION-ROUTINE",
            payload_text="Prepare routine Codex report handoff review.",
        )

        pre = _file_set(REPO_ROOT)
        out = _run_script_json(ACTION_RECOMMENDATION_SCRIPT, [])
        post = _file_set(REPO_ROOT)

        assert out["relay_sos_escalation_status"] == "ROUTINE_REVIEW"
        assert out["relay_sos_anthony_required"] is False
        assert out["relay_sos_routine_review_allowed"] is True
        assert "routine relay review" in out["orchestration_result_contract"]["next_safe_action"].lower()
        assert "wake an" not in out["orchestration_result_contract"]["next_safe_action"].lower()
        assert pre == post
    finally:
        _clear_relay_inbox()


def test_action_recommendation_sos_relay_classification_requires_anthony() -> None:
    _clear_relay_inbox()
    try:
        _seed_relay_message_json(
            message_id="AIOS-RELAY-ACTION-SOS",
            payload_text="credential token marker for test only",
        )

        pre = _file_set(REPO_ROOT)
        out = _run_script_json(ACTION_RECOMMENDATION_SCRIPT, [])
        post = _file_set(REPO_ROOT)

        assert out["relay_sos_escalation_status"] == "SOS_ESCALATION"
        assert out["relay_sos_anthony_required"] is True
        assert out["relay_sos_routine_review_allowed"] is False
        assert "STOP" in out["orchestration_result_contract"]["next_safe_action"].upper()
        assert "anthony" in out["orchestration_result_contract"]["next_safe_action"].lower()
        assert "no command recommended" in out["recommended_command"].lower()
        assert pre == post
    finally:
        _clear_relay_inbox()
