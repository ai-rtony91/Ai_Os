from __future__ import annotations

import importlib.util
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_operator_relay.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_operator_relay", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def resume_state() -> dict[str, object]:
    return {
        "schema": "AIOS_RESUME_STATE.v1",
        "goal": "forex-paper-bot",
        "resume_ready": True,
        "next_build_plan": {"next_component": "forex_risk_controls"},
        "approval_required": {"commit": True, "push": True},
        "next_safe_action": "Prepare bounded risk controls packet.",
    }


def test_operator_relay_imports():
    module = load_module()
    assert module.SCHEMA == "AIOS_OPERATOR_RELAY.v1"
    assert callable(module.build_operator_relay)


def test_ready_resume_state_makes_codex_prompt_ready_without_api_calls():
    module = load_module()
    relay = module.build_operator_relay(resume_state(), {"blockers": []})
    assert relay["schema"] == "AIOS_OPERATOR_RELAY.v1"
    assert relay["relay_status"] == "ready_for_operator_copy_paste"
    assert relay["human_action_required"] is True
    assert relay["codex_prompt_ready"] is True
    assert relay["safety"]["api_call"] is False
    assert relay["safety"]["codex_launch"] is False


def test_cli_blocker_keeps_relay_waiting():
    module = load_module()
    relay = module.build_operator_relay(resume_state(), {"blockers": ["sandbox_launcher_unavailable_1312"]})
    assert relay["relay_status"] == "waiting_for_review"
    assert relay["codex_prompt_ready"] is False
    assert relay["human_action_required"] is True


def test_write_operator_relay_is_bounded_to_reports_relay(tmp_path):
    module = load_module()
    relay = module.build_operator_relay(resume_state(), {"blockers": []})
    written = module.write_operator_relay(
        tmp_path,
        relay,
        generated_at_utc=datetime(2026, 6, 14, 13, 0, 0, tzinfo=timezone.utc),
    )
    timestamped = tmp_path / written["relay_paths"]["timestamped"]
    latest = tmp_path / written["relay_paths"]["latest"]
    assert timestamped.exists()
    assert latest.exists()
    assert written["relay_paths"]["timestamped"].startswith("Reports/aios_relay/")


def test_operator_relay_rejects_path_traversal(tmp_path):
    module = load_module()
    relay = module.build_operator_relay(resume_state(), {"blockers": []})
    try:
        module.write_operator_relay(tmp_path, relay, output_dir=tmp_path / "Reports" / "other")
    except ValueError as exc:
        assert str(exc) == "operator_relay_dir_outside_allowed_root"
    else:
        raise AssertionError("unsafe output dir was accepted")


def test_no_runtime_or_network_usage_in_source():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["subprocess", "requests", "socket", "urllib", "http.client"]:
        assert forbidden not in source
