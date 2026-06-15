from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_bounded_local_apply_runner.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_bounded_local_apply_runner", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_imports_and_preview_schema():
    module = load_module()
    preview = module.build_bounded_local_apply_preview(
        {
            "goal": "forex-paper-bot",
            "action_id": "build_platform_status_reader",
            "allowed_paths": ["automation/orchestration/platform_status_reader.py"],
            "validators": ["python -m pytest tests/orchestration/test_platform_status_reader.py"],
        }
    )
    assert preview["schema"] == "AIOS_BOUNDED_LOCAL_APPLY_RUNNER.v1"
    assert preview["runner_mode"] == "DRY_RUN"
    assert preview["commands_executed"] is False
    assert preview["files_written"] == []
    assert preview["protected_actions_blocked"]["git_push"] is True


def test_preview_contains_command_allowed_paths_and_validators():
    module = load_module()
    preview = module.build_bounded_local_apply_preview(
        {
            "goal": "forex-paper-bot",
            "action_id": "build_platform_status_reader",
            "allowed_paths": ["automation/orchestration/platform_status_reader.py"],
            "validators": ["python -m pytest tests/orchestration/test_platform_status_reader.py"],
        },
        max_repairs=2,
        max_files_changed=3,
    )
    assert "build_platform_status_reader" in preview["command_preview"][0]
    assert preview["allowed_paths"] == ["automation/orchestration/platform_status_reader.py"]
    assert preview["validators"] == ["python -m pytest tests/orchestration/test_platform_status_reader.py"]
    assert preview["max_repairs"] == 2
    assert preview["max_files_changed"] == 3


def test_no_command_execution_implementation():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["subprocess", "start-process", "requests", "socket", "urllib", ".write_text", "open("]:
        assert forbidden not in source
