"""Tests for the routine relay review continuation gate."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import json
import re
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[2]
AIOS = REPO_ROOT / "aios.ps1"
ACTION_RECOMMENDATION_SCRIPT = REPO_ROOT / "automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1"
RELAY_STATE_SCRIPT = REPO_ROOT / "automation/orchestration/review_bridge/Get-AiOsRelayOperatorState.DRY_RUN.ps1"
RELAY_INBOX = REPO_ROOT / "control/relay_bus/messages/inbox"
ROUTINE_REVIEW_COMMAND = (
    "powershell -NoProfile -ExecutionPolicy Bypass -File "
    "automation/orchestration/relay_bus/Resolve-AiOsRelayHumanReview.DRY_RUN.ps1 -OutputJson"
)


def _run_json(script: Path, args: list[str] | None = None) -> dict:
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script),
        "-OutputJson",
        *(args or []),
    ]
    raw = subprocess.check_output(cmd, cwd=str(REPO_ROOT), text=True)
    return json.loads(raw.strip())


def _run_aios_status() -> str:
    return subprocess.check_output(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(AIOS),
            "-Mode",
            "status",
        ],
        cwd=str(REPO_ROOT),
        text=True,
    )


def _file_set(root: Path) -> set[str]:
    return {
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }


@contextmanager
def _isolated_relay_inbox():
    RELAY_INBOX.mkdir(parents=True, exist_ok=True)
    saved_messages = {path.name: path.read_bytes() for path in RELAY_INBOX.glob("*.json")}
    for path in RELAY_INBOX.glob("*.json"):
        path.unlink()

    try:
        yield
    finally:
        for path in RELAY_INBOX.glob("*.json"):
            path.unlink()
        for name, content in saved_messages.items():
            (RELAY_INBOX / name).write_bytes(content)


def _seed_relay_message(message_id: str, payload_text: str) -> Path:
    message_path = RELAY_INBOX / f"{message_id}.json"
    message_path.write_text(
        json.dumps(
            {
                "schema": "AIOS_RELAY_MESSAGE.v1",
                "message_id": message_id,
                "created_utc": "2026-06-13T00:00:00Z",
                "actor": "codex_cli",
                "target_actor": "powershell_operator",
                "packet_id": message_id,
                "branch": "feature/routine-review-continuation-gate-v1",
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
    return message_path


def test_empty_relay_bus_preserves_campaign_ready_recommendation() -> None:
    with _isolated_relay_inbox():
        out = _run_json(ACTION_RECOMMENDATION_SCRIPT)

    assert out["mode"] == "READ_ONLY"
    assert out["packet_status"] == "campaign_ready"
    assert out["relay_sos_escalation_status"] in {"NOT_APPLICABLE", ""}
    assert out["relay_sos_anthony_required"] is False
    assert out["relay_sos_routine_review_allowed"] is False
    assert out["routine_review_continuation_allowed"] is False
    assert "No command recommended" not in out["recommended_command"]


def test_routine_relay_review_allows_continuation_without_anthony() -> None:
    with _isolated_relay_inbox():
        _seed_relay_message(
            "AIOS-ROUTINE-REVIEW-CONTINUATION",
            "Prepare routine Codex report handoff review.",
        )

        relay_state = _run_json(RELAY_STATE_SCRIPT)
        recommendation = _run_json(ACTION_RECOMMENDATION_SCRIPT)

    assert relay_state["actor_relay_bus_status"] == "NEEDS_HUMAN_REVIEW"
    assert relay_state["sos_escalation_status"] == "ROUTINE_REVIEW"
    assert relay_state["sos_anthony_required"] is False
    assert relay_state["sos_routine_review_allowed"] is True
    assert relay_state["routine_review_continuation_allowed"] is True
    assert relay_state["routine_review_next_action"] == ROUTINE_REVIEW_COMMAND

    assert recommendation["relay_sos_escalation_status"] == "ROUTINE_REVIEW"
    assert recommendation["relay_sos_anthony_required"] is False
    assert recommendation["routine_review_continuation_allowed"] is True
    assert recommendation["recommended_command"] == ROUTINE_REVIEW_COMMAND
    assert recommendation["orchestration_result_contract"]["approval_required"] is False
    assert "routine relay review" in recommendation["orchestration_result_contract"]["next_safe_action"].lower()
    assert ROUTINE_REVIEW_COMMAND in recommendation["orchestration_result_contract"]["next_safe_action"]


def test_sos_relay_review_blocks_continuation_and_requires_anthony() -> None:
    with _isolated_relay_inbox():
        _seed_relay_message(
            "AIOS-ROUTINE-REVIEW-SOS",
            "credential token marker for test only",
        )

        relay_state = _run_json(RELAY_STATE_SCRIPT)
        recommendation = _run_json(ACTION_RECOMMENDATION_SCRIPT)

    assert relay_state["sos_escalation_status"] == "SOS_ESCALATION"
    assert relay_state["sos_anthony_required"] is True
    assert relay_state["routine_review_continuation_allowed"] is False
    assert "Anthony" in relay_state["next_safe_action"]
    assert "Resolve-AiOsRelayHumanReview" not in relay_state["next_safe_action"]

    assert recommendation["relay_sos_escalation_status"] == "SOS_ESCALATION"
    assert recommendation["relay_sos_anthony_required"] is True
    assert recommendation["routine_review_continuation_allowed"] is False
    assert "No command recommended" in recommendation["recommended_command"]
    assert "Anthony" in recommendation["orchestration_result_contract"]["next_safe_action"]


def test_routine_continuation_recommendation_is_dry_run_read_only() -> None:
    with _isolated_relay_inbox():
        _seed_relay_message(
            "AIOS-ROUTINE-REVIEW-READONLY",
            "Prepare routine workflow review for a Codex final report.",
        )

        relay_state = _run_json(RELAY_STATE_SCRIPT)
        recommendation = _run_json(ACTION_RECOMMENDATION_SCRIPT)

    assert relay_state["mode"] == "DRY_RUN_READ_ONLY"
    assert recommendation["mode"] == "READ_ONLY"
    assert recommendation["recommended_command"] == ROUTINE_REVIEW_COMMAND
    assert ".DRY_RUN.ps1" in recommendation["recommended_command"]
    assert "READ_ONLY" in recommendation["orchestration_result_contract"]["runtime_notes"]
    assert "No packet advancement, APPLY, commit, or push was performed." in recommendation["orchestration_result_contract"]["runtime_notes"]


def test_relay_status_and_recommendation_scripts_do_not_write_files() -> None:
    with _isolated_relay_inbox():
        _seed_relay_message(
            "AIOS-ROUTINE-REVIEW-NO-WRITES",
            "Prepare routine relay review for read-only continuation.",
        )
        before = _file_set(REPO_ROOT)

        _run_json(RELAY_STATE_SCRIPT)
        _run_json(ACTION_RECOMMENDATION_SCRIPT)
        _run_aios_status()

        after = _file_set(REPO_ROOT)

    assert before == after


def test_routine_continuation_next_actions_do_not_recommend_forbidden_work() -> None:
    with _isolated_relay_inbox():
        _seed_relay_message(
            "AIOS-ROUTINE-REVIEW-FORBIDDEN-WORDS",
            "Prepare routine Codex report handoff review.",
        )

        relay_state = _run_json(RELAY_STATE_SCRIPT)
        recommendation = _run_json(ACTION_RECOMMENDATION_SCRIPT)

    recommended_next_actions = " ".join(
        [
            relay_state["routine_review_next_action"],
            relay_state["next_safe_action"],
            recommendation["recommended_command"],
            recommendation["orchestration_result_contract"]["next_safe_action"],
        ]
    )

    forbidden_patterns = [
        r"\bcommit\b",
        r"\bpush\b",
        r"\bpr\b",
        r"\bmerge\b",
        r"\bapply\b",
        r"\bworker launch\b",
        r"\bruntime start\b",
        r"\bqueue mutation\b",
        r"\bapproval mutation\b",
        r"\bbroker\b",
        r"\boanda\b",
        r"\bwebhook\b",
        r"\border\b",
    ]
    for pattern in forbidden_patterns:
        assert re.search(pattern, recommended_next_actions, flags=re.IGNORECASE) is None
