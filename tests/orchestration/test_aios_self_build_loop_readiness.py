from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_self_build_loop_readiness.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_self_build_loop_readiness", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def complete_session_wake() -> dict[str, object]:
    return {
        "schema": "AIOS_WAKE_CONTINUE.v1",
        "goal": "forex-paper-bot",
        "result": "REVIEW_REQUIRED",
        "selected_action": "validate_all_forex_with_session_controller",
        "validators_run": [
            {
                "name": "pytest",
                "command": "python -m pytest tests/trading_lab/test_forex_paper_session_controller.py",
                "passed": True,
                "stdout": "8 passed in 0.06s",
            }
        ],
        "next_build_plan": {
            "route": "stop",
            "next_component": "none",
        },
        "bounded_executor_handoff": {
            "handoff_status": "stopped",
            "allowed_action": "none",
        },
        "bounded_executor_ready": {
            "status": "stopped",
        },
        "continuation_controller": {
            "codex_packet_required": False,
            "local_runner_available": False,
            "productive_executor_available": False,
            "sos_required": False,
        },
        "sos_escalation": {
            "sos_required": False,
        },
    }


def test_imports_and_schema():
    module = load_module()
    assert module.SCHEMA == "AIOS_SELF_BUILD_LOOP_READINESS.v1"
    assert callable(module.build_self_build_loop_readiness)


def test_complete_session_chain_routes_to_readiness_review():
    module = load_module()
    result = module.build_self_build_loop_readiness(complete_session_wake())
    assert result["readiness_status"] == "review_required"
    assert result["current_goal"] == "forex-paper-bot"
    assert result["latest_validated_chain"] == "forex_paper_session_controller"
    assert result["tests_passed_count"] == 8
    assert result["route_status"] == "stopped_for_review"
    assert result["reason_code"] == "forex_session_chain_complete_review_required"
    assert result["next_allowed_self_build_action"] == "self_build_loop_readiness_review"
    assert result["codex_packet_required"] is False
    assert result["local_runner_available"] is False
    assert result["productive_executor_available"] is False
    assert result["sos_required"] is False
    assert result["protected_actions_blocked"]["git_commit"] is True
    assert "approved_next_non_forex_build_scope" in result["missing_capabilities"]


def test_ready_when_bounded_next_component_is_available():
    module = load_module()
    wake = {
        "goal": "forex-paper-bot",
        "result": "DONE_FOR_CURRENT_GOAL",
        "selected_action": "validate_all_forex_with_portfolio_state",
        "validators_run": [{"passed": True, "stdout": ""}],
        "next_build_plan": {
            "route": "build_next_paper_component",
            "next_component": "forex_paper_session_controller",
        },
        "bounded_executor_handoff": {
            "handoff_status": "ready",
            "allowed_action": "build_forex_paper_session_controller",
        },
        "bounded_executor_ready": {
            "status": "ready_for_human_review",
        },
        "continuation_controller": {
            "local_runner_available": True,
            "productive_executor_available": True,
        },
    }
    result = module.build_self_build_loop_readiness(wake)
    assert result["readiness_status"] == "ready"
    assert result["route_status"] == "ready_for_bounded_self_build"
    assert result["next_allowed_self_build_action"] == "build_forex_paper_session_controller"
    assert result["tests_passed_count"] == 1


def test_safety_or_sos_blocks_readiness():
    module = load_module()
    wake = complete_session_wake()
    wake["sos_escalation"] = {"sos_required": True}
    result = module.build_self_build_loop_readiness(wake)
    assert result["readiness_status"] == "not_ready"
    assert result["route_status"] == "blocked"
    assert result["reason_code"] == "safety_blocker_present"
    assert result["sos_required"] is True


def test_blocked_wake_result_is_not_ready():
    module = load_module()
    wake = complete_session_wake()
    wake["result"] = "BLOCKED"
    wake["blocked_reason"] = "control_plane_not_dashboard_ready"
    result = module.build_self_build_loop_readiness(wake)
    assert result["readiness_status"] == "not_ready"
    assert result["reason_code"] == "wake_result_blocked"
    assert result["missing_capabilities"] == ["passing_wake_validation"]


def test_no_network_subprocess_or_file_write_usage():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["subprocess", "requests", "socket", "urllib", ".write_text", "open("]:
        assert forbidden not in source
