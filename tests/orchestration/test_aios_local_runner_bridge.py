from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_local_runner_bridge.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_local_runner_bridge", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def handoff() -> dict[str, object]:
    return {
        "schema": "AIOS_BOUNDED_EXECUTOR_HANDOFF.v1",
        "handoff_status": "ready",
        "allowed_action": "build_forex_risk_controls",
        "validators": [
            "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_wake_continue.py",
        ],
        "next_safe_action": "Prepare the bounded handoff for review.",
    }


def execution_simulator_handoff() -> dict[str, object]:
    return {
        "schema": "AIOS_BOUNDED_EXECUTOR_HANDOFF.v1",
        "handoff_status": "ready",
        "allowed_action": "build_forex_paper_execution_simulator",
        "validators": [
            "python -m pytest -p no:cacheprovider tests/trading_lab/test_forex_paper_execution_simulator.py",
        ],
        "next_safe_action": "Prepare the bounded paper execution simulator handoff for review.",
    }


def test_local_runner_bridge_imports():
    module = load_module()
    assert module.SCHEMA == "AIOS_LOCAL_RUNNER_BRIDGE.v1"
    assert callable(module.build_local_runner_bridge)


def test_forex_handoff_produces_command_preview_only():
    module = load_module()
    bridge = module.build_local_runner_bridge(handoff())
    assert bridge["schema"] == "AIOS_LOCAL_RUNNER_BRIDGE.v1"
    assert bridge["runner_status"] == "preview_ready"
    assert bridge["working_directory"] == r"C:\Dev\Ai.Os"
    assert bridge["command_preview"][0] == "Set-Location -LiteralPath 'C:\\Dev\\Ai.Os'"
    assert bridge["validation_commands"] == handoff()["validators"]
    assert bridge["safety"]["command_execution"] is False
    assert bridge["approval_required"]["human_review_before_execution"] is True


def test_execution_simulator_handoff_produces_command_preview_only():
    module = load_module()
    bridge = module.build_local_runner_bridge(execution_simulator_handoff())
    assert bridge["runner_status"] == "preview_ready"
    assert bridge["working_directory"] == r"C:\Dev\Ai.Os"
    assert bridge["command_preview"][0] == "Set-Location -LiteralPath 'C:\\Dev\\Ai.Os'"
    assert bridge["validation_commands"] == execution_simulator_handoff()["validators"]
    assert bridge["safety"]["command_execution"] is False


def test_unsupported_or_stopped_handoff_does_not_preview_execution():
    module = load_module()
    blocked = module.build_local_runner_bridge({"handoff_status": "ready", "allowed_action": "unknown"})
    stopped = module.build_local_runner_bridge({"handoff_status": "stopped", "allowed_action": "none"})
    assert blocked["runner_status"] == "blocked"
    assert blocked["command_preview"] == []
    assert stopped["runner_status"] == "stopped_for_human_review"
    assert stopped["command_preview"] == []


def test_no_runtime_or_network_usage_in_source():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["subprocess", "requests", "socket", "urllib", "http.client"]:
        assert forbidden not in source
