"""Tests for campaign registry readiness wiring for routine relay review continuation."""

from pathlib import Path
import json
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[2]
CAMPAIGN_REGISTRY = REPO_ROOT / "automation/orchestration/campaign_registry/AIOS_STRATEGIC_CAMPAIGN_REGISTRY.json"
CAMPAIGN_NEXT_TASK_SCRIPT = REPO_ROOT / "automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1"
ACTION_RECOMMENDATION_SCRIPT = REPO_ROOT / "automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1"
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


def _file_set(root: Path) -> set[str]:
    return {
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }


def _clear_relay_inbox() -> None:
    for message_file in RELAY_INBOX.glob("*.json"):
        if message_file.name != ".gitkeep":
            message_file.unlink()


def _ready_candidates_for_packet_id(registry: dict, packet_id: str) -> list[dict]:
    ready_stages: list[dict] = []
    for campaign in registry.get("campaigns", []):
        for stage in campaign.get("stages", []):
            if str(stage.get("status", "")).upper() == "READY" and str(
                stage.get("next_packet_candidate", "")
            ) == packet_id:
                ready_stages.append(stage)
    return ready_stages


def test_campaign_registry_has_single_ready_candidate_for_relay_routine_continuation_stage() -> None:
    with CAMPAIGN_REGISTRY.open("r", encoding="utf-8") as fh:
        registry = json.load(fh)

    ready_candidates = _ready_candidates_for_packet_id(
        registry, "AIOS-ROUTINE-REVIEW-CONTINUATION-GATE-APPLY-V1"
    )
    assert len(ready_candidates) == 1
    assert ready_candidates[0]["status"] == "READY"
    assert ready_candidates[0]["next_packet_candidate"] == "AIOS-ROUTINE-REVIEW-CONTINUATION-GATE-APPLY-V1"
    assert ready_candidates[0].get("next_packet_candidate") == "AIOS-ROUTINE-REVIEW-CONTINUATION-GATE-APPLY-V1"


def test_campaign_next_task_surfaces_routine_review_continuation_candidate() -> None:
    pre = _file_set(REPO_ROOT)
    out = _run_script_json(CAMPAIGN_NEXT_TASK_SCRIPT, [])
    post = _file_set(REPO_ROOT)

    assert out["schema"] == "AIOS_CAMPAIGN_NEXT_TASK_RECOMMENDATION.v1"
    assert out["overall_readiness"] == "READY_FOR_PACKET_PREVIEW"
    assert out["recommended_lane"] == "RELAY_ROUTINE_REVIEW_CONTINUATION"
    assert out["next_packet_candidate"] == "AIOS-ROUTINE-REVIEW-CONTINUATION-GATE-APPLY-V1"
    assert out["reason"].startswith("Selected highest-priority READY stage")
    assert pre == post


def test_action_recommendation_no_longer_reports_no_active_packet_when_ready_candidate_exists() -> None:
    _clear_relay_inbox()
    pre = _file_set(REPO_ROOT)
    out = _run_script_json(ACTION_RECOMMENDATION_SCRIPT, [])
    post = _file_set(REPO_ROOT)

    assert out["packet_status"] != "no_active_packet"
    assert "No command recommended" not in out["recommended_command"]
    assert out["mode"] == "READ_ONLY"
    assert pre == post
