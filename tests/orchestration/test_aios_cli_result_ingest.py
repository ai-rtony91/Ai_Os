from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_cli_result_ingest.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_cli_result_ingest", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_cli_result_ingest_imports():
    module = load_module()
    assert module.SCHEMA == "AIOS_CLI_RESULT_INGEST.v1"
    assert callable(module.build_cli_result_ingest)


def test_ingests_success_text_and_protected_status():
    module = load_module()
    result = module.build_cli_result_ingest(
        """
        23 passed in 1.25s
        FILES CHANGED:
        - automation/orchestration/aios_wake_continue.py
        commit status: NO_COMMIT
        push status: NO_PUSH
        SAFE NEXT ACTION: Review the report.
        """
    )
    assert result["schema"] == "AIOS_CLI_RESULT_INGEST.v1"
    assert result["validation_passed"] is True
    assert result["tests_passed_count"] == 23
    assert result["tests_failed_count"] == 0
    assert result["files_changed"] == ["automation/orchestration/aios_wake_continue.py"]
    assert result["commit_status"] == "NO_COMMIT"
    assert result["push_status"] == "NO_PUSH"


def test_sandbox_1312_is_sandbox_blocker_not_direct_command_block():
    module = load_module()
    result = module.build_cli_result_ingest("windows sandbox: runner error: CreateProcessAsUserW failed: 1312")
    assert result["status"] == "SANDBOX_BLOCKED"
    assert result["sandbox_blocked"] is True
    assert result["direct_command_blocked"] is False
    assert result["validation_passed"] is False
    assert "sandbox_launcher_unavailable_1312" in result["blockers"]


def test_ingests_dict_without_file_writes():
    module = load_module()
    result = module.build_cli_result_ingest(
        {
            "status": "COMPLETE",
            "files_changed": ["docs/orchestration/AIOS_CLI_RESULT_INGEST.md"],
            "validation_passed": True,
            "tests_passed_count": 2,
            "tests_failed_count": 0,
            "next_safe_action": "Continue.",
        }
    )
    assert result["status"] == "COMPLETE"
    assert result["files_changed"] == ["docs/orchestration/AIOS_CLI_RESULT_INGEST.md"]
    assert result["safety_summary"]["broker"] is False


def test_no_runtime_or_network_usage_in_source():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["subprocess", "requests", "socket", "urllib", "http.client"]:
        assert forbidden not in source
