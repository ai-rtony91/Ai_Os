from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_control_plane_status.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_control_plane_status", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def resume_state(**safety_overrides: bool) -> dict[str, object]:
    safety = {
        "broker": False,
        "live_trading": False,
        "scheduler": False,
        "daemon": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "worker_dispatch": False,
        **safety_overrides,
    }
    return {
        "schema": "AIOS_RESUME_STATE.v1",
        "goal": "forex-paper-bot",
        "resume_ready": True,
        "next_build_plan": {"next_component": "forex_risk_controls"},
        "next_safe_action": "Prepare bounded risk controls packet.",
        "approval_required": {"commit": True, "push": True},
        "safety": safety,
    }


def runner_bridge() -> dict[str, object]:
    return {
        "schema": "AIOS_LOCAL_RUNNER_BRIDGE.v1",
        "runner_status": "preview_ready",
        "next_safe_action": "Prepare bounded risk controls packet.",
        "approval_required": {"human_review_before_execution": True},
        "safety": {"command_execution": False},
    }


def ready_state() -> dict[str, object]:
    return {
        "schema": "AIOS_BOUNDED_EXECUTOR_READY.v1",
        "status": "ready_for_human_review",
        "reason_code": "bounded_handoff_ready",
        "approval_required": {"human_review_before_local_apply": True},
        "safety": {"command_execution": False},
    }


def test_control_plane_status_imports():
    module = load_module()
    assert module.SCHEMA == "AIOS_CONTROL_PLANE_STATUS.v1"
    assert callable(module.build_control_plane_status)


def test_dashboard_ready_true_for_safe_ready_state():
    module = load_module()
    status = module.build_control_plane_status(
        resume_state=resume_state(),
        cli_result_ingest={"blockers": [], "safety_summary": {"broker": False}},
        operator_relay={"next_safe_action": "Continue.", "safety": {"worker_dispatch": False}},
        local_runner_bridge=runner_bridge(),
        bounded_executor_ready=ready_state(),
    )
    assert status["schema"] == "AIOS_CONTROL_PLANE_STATUS.v1"
    assert status["current_goal"] == "forex-paper-bot"
    assert status["next_component"] == "forex_risk_controls"
    assert status["dashboard_ready"] is True
    assert status["loop_status"] == "dashboard_ready"


def test_dashboard_ready_false_for_broker_live_scheduler_or_daemon_flags():
    module = load_module()
    for flag in ["broker", "live_trading", "scheduler", "daemon"]:
        status = module.build_control_plane_status(
            resume_state=resume_state(**{flag: True}),
            cli_result_ingest={"blockers": []},
            operator_relay={},
            local_runner_bridge=runner_bridge(),
            bounded_executor_ready=ready_state(),
        )
        assert status["dashboard_ready"] is False
        assert f"safety_{flag}_blocked" in status["blockers"]


def test_dashboard_ready_false_when_bounded_executor_not_ready():
    module = load_module()
    status = module.build_control_plane_status(
        resume_state=resume_state(),
        cli_result_ingest={"blockers": []},
        local_runner_bridge=runner_bridge(),
        bounded_executor_ready={"status": "blocked", "reason_code": "scope_not_bounded"},
    )
    assert status["dashboard_ready"] is False
    assert "scope_not_bounded" in status["blockers"]


def test_write_control_plane_status_is_bounded(tmp_path):
    module = load_module()
    status = module.build_control_plane_status(
        resume_state=resume_state(),
        cli_result_ingest={"blockers": []},
        local_runner_bridge=runner_bridge(),
        bounded_executor_ready=ready_state(),
    )
    written = module.write_control_plane_status(tmp_path, status)
    assert written["control_plane_status_path"] == "Reports/aios_control_plane/AIOS_CONTROL_PLANE_STATUS_latest.json"
    assert (tmp_path / written["control_plane_status_path"]).exists()


def test_control_plane_status_rejects_path_traversal(tmp_path):
    module = load_module()
    try:
        module.write_control_plane_status(tmp_path, {"schema": module.SCHEMA}, output_dir=tmp_path / "Reports" / "other")
    except ValueError as exc:
        assert str(exc) == "control_plane_dir_outside_allowed_root"
    else:
        raise AssertionError("unsafe output dir was accepted")


def test_no_runtime_or_network_usage_in_source():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["subprocess", "requests", "socket", "urllib", "http.client"]:
        assert forbidden not in source
