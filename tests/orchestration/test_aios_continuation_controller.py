from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTROLLER_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_continuation_controller.py"
REGISTRY_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_mode_capability_registry.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def registry():
    return load_module(REGISTRY_PATH, "aios_mode_capability_registry").build_mode_capability_registry()


def ready_handoff(action: str = "build_forex_paper_execution_simulator") -> dict[str, object]:
    return {
        "handoff_status": "ready",
        "next_component": "forex_paper_execution_simulator",
        "allowed_action": action,
    }


def test_imports():
    module = load_module(CONTROLLER_PATH, "aios_continuation_controller")
    assert module.SCHEMA == "AIOS_CONTINUATION_CONTROLLER.v1"


def test_execution_simulator_requires_packet_when_executor_support_missing():
    module = load_module(CONTROLLER_PATH, "aios_continuation_controller")
    controller = module.build_continuation_controller(
        resume_state={"goal": "forex-paper-bot"},
        control_plane_status={"current_goal": "forex-paper-bot", "next_component": "forex_paper_execution_simulator"},
        bounded_executor_handoff=ready_handoff(),
        bounded_executor_ready={"status": "ready_for_human_review"},
        mode_registry=registry(),
        user_goal="forex-paper-bot",
    )
    assert controller["continuation_status"] == "ready_to_prepare_packet"
    assert controller["action_type"] == "build_executor_support_packet"
    assert controller["codex_packet_required"] is True
    assert controller["productive_executor_available"] is False
    assert controller["next_action"] == "build executor support for build_forex_paper_execution_simulator"


def test_supported_productive_executor_action_waits_for_human_approval():
    module = load_module(CONTROLLER_PATH, "aios_continuation_controller")
    controller = module.build_continuation_controller(
        resume_state={"goal": "forex-paper-bot"},
        control_plane_status={"current_goal": "forex-paper-bot", "next_component": "forex_risk_controls"},
        bounded_executor_handoff=ready_handoff("build_forex_risk_controls"),
        bounded_executor_ready={"status": "ready_for_human_review"},
        mode_registry=registry(),
        user_goal="forex-paper-bot",
    )
    assert controller["action_type"] == "execute_existing_tool_after_human_approval"
    assert controller["productive_executor_available"] is True
    assert controller["codex_packet_required"] is False


def test_stopped_route_is_human_review():
    module = load_module(CONTROLLER_PATH, "aios_continuation_controller")
    controller = module.build_continuation_controller(
        resume_state={"goal": "forex-paper-bot"},
        control_plane_status={"next_component": "none"},
        bounded_executor_handoff={"handoff_status": "stopped", "allowed_action": "none"},
        bounded_executor_ready={"status": "not_ready"},
        mode_registry=registry(),
        user_goal="forex-paper-bot",
    )
    assert controller["action_type"] == "human_review"
    assert controller["reason_code"] == "route_stopped"


def test_safety_blocker_routes_to_sos_stop():
    module = load_module(CONTROLLER_PATH, "aios_continuation_controller")
    controller = module.build_continuation_controller(
        resume_state={"goal": "forex-paper-bot", "safety": {"broker": True}},
        control_plane_status={"next_component": "forex_paper_execution_simulator"},
        bounded_executor_handoff=ready_handoff(),
        bounded_executor_ready={"status": "ready_for_human_review"},
        mode_registry=registry(),
        user_goal="forex-paper-bot",
    )
    assert controller["action_type"] == "sos_stop"
    assert controller["sos_required"] is True
