"""Tests for Get-AiOsSosEscalationPolicy.DRY_RUN.ps1."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SOS_POLICY_SCRIPT = (
    REPO_ROOT / "automation" / "orchestration" / "relay_bus" / "Get-AiOsSosEscalationPolicy.DRY_RUN.ps1"
)
NEW_MESSAGE_SCRIPT = (
    REPO_ROOT / "automation" / "orchestration" / "relay_bus" / "New-AiOsRelayMessage.DRY_RUN.ps1"
)
REGISTRY_SOURCE = REPO_ROOT / "control" / "relay_bus" / "actors" / "AIOS_RELAY_ACTORS.json"


def _run_script_json(script: Path, args: list[str], cwd: Path) -> dict:
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script),
        "-OutputJson",
    ] + args
    raw = subprocess.check_output(cmd, cwd=str(cwd), text=True)
    return json.loads(raw.strip())


def _init_relay_bus_root(root: Path) -> None:
    control_root = root / "control" / "relay_bus"
    (control_root / "actors").mkdir(parents=True, exist_ok=True)
    (control_root / "messages" / "inbox").mkdir(parents=True, exist_ok=True)
    (control_root / "messages" / "outbox").mkdir(parents=True, exist_ok=True)
    (control_root / "messages" / "archive").mkdir(parents=True, exist_ok=True)
    (control_root / "evidence").mkdir(parents=True, exist_ok=True)
    (control_root / "pasteback").mkdir(parents=True, exist_ok=True)
    for marker in (
        control_root / "messages" / "inbox" / ".gitkeep",
        control_root / "messages" / "outbox" / ".gitkeep",
        control_root / "messages" / "archive" / ".gitkeep",
        control_root / "evidence" / ".gitkeep",
        control_root / "pasteback" / ".gitkeep",
    ):
        marker.write_text("", encoding="utf-8")
    shutil.copy2(REGISTRY_SOURCE, control_root / "actors" / "AIOS_RELAY_ACTORS.json")


def _seed_relay_message(
    root: Path,
    payload: str,
    message_id: str = "AIOS-SOS-REVIEW-01",
    status: str = "pending",
) -> None:
    _run_script_json(
        NEW_MESSAGE_SCRIPT,
        [
            "-Actor",
            "codex_cli",
            "-TargetActor",
            "powershell_operator",
            "-PacketId",
            message_id,
            "-Branch",
            "feature/sos-escalation-policy-router-v1",
            "-MessageType",
            "codex_final_report",
            "-Intent",
            "handoff summary",
            "-Status",
            status,
            "-PayloadText",
            json.dumps({"message_id": message_id, "content": payload}),
            "-Mode",
            "APPLY",
        ],
        root,
    )


def _seed_raw_relay_message(
    root: Path,
    payload_text: str,
    message_id: str = "AIOS-SOS-REVIEW-SECRETS-01",
    status: str = "pending",
) -> None:
    message = {
        "schema": "AIOS_RELAY_MESSAGE.v1",
        "message_id": message_id,
        "created_utc": "2026-06-13T00:00:00Z",
        "actor": "codex_cli",
        "target_actor": "powershell_operator",
        "packet_id": message_id,
        "branch": "feature/sos-escalation-policy-router-v1",
        "message_type": "codex_final_report",
        "intent": "handoff summary",
        "status": status,
        "payload_text": payload_text,
        "evidence": {},
        "next_action": "Review this message in relay bus.",
        "requires_human_review": True,
        "execution_allowed": False,
        "can_continue_without_anthony": False,
    }
    path = root / "control" / "relay_bus" / "messages" / "inbox" / f"{message_id}.json"
    path.write_text(json.dumps(message), encoding="utf-8")


def _file_set(root: Path) -> set[str]:
    return {str(item.relative_to(root)) for item in root.rglob("*") if item.is_file()}


def test_empty_bus_is_no_review_needed_or_routine_and_read_only() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _init_relay_bus_root(root)

        pre = _file_set(root)
        out = _run_script_json(SOS_POLICY_SCRIPT, [], root)
        post = _file_set(root)

        assert out["schema"] == "AIOS_SOS_ESCALATION_POLICY.v1"
        assert out["mode"] == "DRY_RUN_READ_ONLY"
        assert out["writes_files"] is False
        assert out["execution_allowed"] is False
        assert out["can_continue_without_anthony"] is False
        assert out["escalation_status"] in {"NO_REVIEW_NEEDED", "ROUTINE_REVIEW"}
        assert isinstance(out["escalation_reasons"], list)
        assert out["safe_next_action"]
        assert pre == post


def test_ordinary_relay_review_becomes_routine_review() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _init_relay_bus_root(root)
        _seed_relay_message(root, payload="Prepare normal Codex report handoff for review.")

        out = _run_script_json(SOS_POLICY_SCRIPT, [], root)

        assert out["escalation_status"] == "ROUTINE_REVIEW"
        assert out["anthony_required"] is False
        assert out["routine_review_allowed"] is True
        assert out["writes_files"] is False
        assert out["execution_allowed"] is False


def test_secret_like_payload_becomes_sos_escalation() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _init_relay_bus_root(root)
        _seed_raw_relay_message(
            root,
            payload_text='{"message_id": "AIOS-SOS-REVIEW-SECRETS-01", "content": "Contains API credential: AIOS_TG_BOT_TOKEN=abc123 for sync flow."}',
        )

        out = _run_script_json(SOS_POLICY_SCRIPT, [], root)

        assert out["escalation_status"] == "SOS_ESCALATION"
        assert out["anthony_required"] is True
        assert out["routine_review_allowed"] is False
        assert out["writes_files"] is False
        assert out["execution_allowed"] is False
        assert any("token" in reason.lower() for reason in out["escalation_reasons"])


def test_broker_live_trading_language_becomes_sos_escalation() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _init_relay_bus_root(root)
        _seed_relay_message(
            root,
            payload="Request: use OANDA webhook to place a live trading order after checks.",
            message_id="AIOS-SOS-REVIEW-TRADING-01",
        )

        out = _run_script_json(SOS_POLICY_SCRIPT, [], root)

        assert out["escalation_status"] == "SOS_ESCALATION"
        assert out["anthony_required"] is True
        assert any("broker" in reason.lower() or "live" in reason.lower() for reason in out["escalation_reasons"])


def test_destructive_language_becomes_sos_escalation() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _init_relay_bus_root(root)
        _seed_relay_message(
            root,
            payload="Please force push the branch and delete stale relay history after reset.",
            message_id="AIOS-SOS-REVIEW-DESCTRUCT-01",
        )

        out = _run_script_json(SOS_POLICY_SCRIPT, [], root)

        assert out["escalation_status"] == "SOS_ESCALATION"
        assert out["anthony_required"] is True
        assert any("destructive" in reason.lower() for reason in out["escalation_reasons"])


def test_normal_pr_check_merge_sync_becomes_routine_not_sos() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _init_relay_bus_root(root)
        _seed_relay_message(
            root,
            payload="Normal PR check completed; run merge sync once checks pass.",
            message_id="AIOS-SOS-REVIEW-ROUTINE-01",
        )

        out = _run_script_json(SOS_POLICY_SCRIPT, [], root)

        assert out["escalation_status"] == "ROUTINE_REVIEW"
        assert out["anthony_required"] is False
        assert out["routine_review_allowed"] is True
        assert out["writes_files"] is False
        assert out["execution_allowed"] is False
        assert out["escalation_status"] != "SOS_ESCALATION"
