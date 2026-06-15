from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_bounded_executor_ready.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_bounded_executor_ready", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def handoff() -> dict[str, object]:
    return {
        "schema": "AIOS_BOUNDED_EXECUTOR_HANDOFF.v1",
        "handoff_status": "ready",
        "allowed_action": "build_forex_risk_controls",
        "allowed_paths": [
            "apps/trading_lab/trading_lab/forex_risk_controls.py",
            "tests/trading_lab/test_forex_risk_controls.py",
            "docs/orchestration/AIOS_FOREX_RISK_CONTROLS.md",
            "automation/orchestration/aios_autonomy_execute.py",
            "tests/orchestration/test_aios_autonomy_execute.py",
            "automation/orchestration/aios_wake_continue.py",
            "tests/orchestration/test_aios_wake_continue.py",
        ],
        "validators": [
            "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_autonomy_execute.py tests/orchestration/test_aios_wake_continue.py tests/trading_lab/test_forex_risk_controls.py",
        ],
    }


def test_bounded_executor_ready_imports():
    module = load_module()
    assert module.SCHEMA == "AIOS_BOUNDED_EXECUTOR_READY.v1"
    assert callable(module.build_bounded_executor_ready)


def test_forex_risk_controls_handoff_ready_for_human_review_only():
    module = load_module()
    ready = module.build_bounded_executor_ready(handoff())
    assert ready["schema"] == "AIOS_BOUNDED_EXECUTOR_READY.v1"
    assert ready["status"] == "ready_for_human_review"
    assert ready["allowed_action"] == "build_forex_risk_controls"
    assert ready["allowed_paths_bounded"] is True
    assert ready["validators_bounded"] is True
    assert ready["command_execution"] is False
    assert ready["executed"] is False


def test_unsupported_action_blocks_readiness():
    module = load_module()
    unsafe = handoff()
    unsafe["allowed_action"] = "unknown"
    ready = module.build_bounded_executor_ready(unsafe)
    assert ready["status"] == "blocked"
    assert ready["reason_code"] == "allowed_action_not_allowlisted"


def test_path_traversal_blocks_readiness():
    module = load_module()
    unsafe = handoff()
    unsafe["allowed_paths"] = ["../outside.py"]
    ready = module.build_bounded_executor_ready(unsafe)
    assert ready["status"] == "blocked"
    assert ready["reason_code"] == "handoff_scope_not_bounded"


def test_validator_shell_chaining_blocks_readiness():
    module = load_module()
    unsafe = handoff()
    unsafe["validators"] = ["python -m pytest -p no:cacheprovider tests/orchestration/test_aios_wake_continue.py && whoami"]
    ready = module.build_bounded_executor_ready(unsafe)
    assert ready["status"] == "blocked"
    assert ready["validators_bounded"] is False


def test_no_runtime_or_network_usage_in_source():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["subprocess", "requests", "socket", "urllib", "http.client"]:
        assert forbidden not in source
