from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_self_build_dry_run_driver.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_self_build_dry_run_driver", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def wake_json() -> dict[str, object]:
    return {
        "schema": "AIOS_WAKE_CONTINUE.v1",
        "goal": "forex-paper-bot",
        "result": "REVIEW_REQUIRED",
        "selected_action": "validate_all_forex_with_session_controller",
        "validators_run": [
            {
                "name": "pytest",
                "command": "python -m pytest tests/orchestration/test_aios_wake_continue.py",
                "returncode": 0,
                "passed": True,
                "stdout": "23 passed in 0.42s",
                "stderr": "",
            }
        ],
        "self_build_loop_readiness": {
            "schema": "AIOS_SELF_BUILD_LOOP_READINESS.v1",
            "readiness_status": "review_required",
            "current_goal": "forex-paper-bot",
            "latest_validated_chain": "forex_paper_session_controller",
            "tests_passed_count": 23,
            "route_status": "stopped_for_review",
            "reason_code": "forex_session_chain_complete_review_required",
            "next_allowed_self_build_action": "self_build_loop_readiness_review",
            "codex_packet_required": False,
            "local_runner_available": False,
            "productive_executor_available": False,
            "sos_required": False,
        },
    }


def fake_wake_runner(command: list[str], _repo_root: Path) -> dict[str, object]:
    return {
        "command": " ".join(command),
        "returncode": 0,
        "stdout": json.dumps(wake_json()),
        "stderr": "",
    }


def test_imports_and_schema():
    module = load_module()
    assert module.SCHEMA == "AIOS_SELF_BUILD_DRY_RUN_DRIVER.v1"
    assert callable(module.run_self_build_dry_run_driver)


def test_driver_runs_wake_command_with_no_reports_flags():
    module = load_module()
    report = module.run_self_build_dry_run_driver(REPO_ROOT, wake_runner=fake_wake_runner)
    command = report["wake_command"]
    assert "aios_wake_continue.py" in " ".join(command)
    assert "--emit-continuation-controller" in command
    assert "--write-resume-state" not in command
    assert "--write-control-plane-status" not in command


def test_driver_parses_wake_json_and_stops_without_approved_scope():
    module = load_module()
    report = module.run_self_build_dry_run_driver(REPO_ROOT, wake_runner=fake_wake_runner)
    assert report["schema"] == "AIOS_SELF_BUILD_DRY_RUN_DRIVER.v1"
    assert report["driver_mode"] == "DRY_RUN"
    assert report["wake_validation_passed"] is True
    assert report["tests_passed_count"] == 23
    assert report["readiness_status"] == "review_required"
    assert report["selected_queue_item"] is None
    assert report["selected_next_action"] == "none"
    assert report["codex_packet_preview"]["packet_ready"] is False
    assert report["local_apply_preview"]["commands_executed"] is False
    assert report["stop_report"]["resume_ready"] is False
    assert report["sos"]["sos_required"] is False
    assert report["core_status"]["schema"] == "AIOS_SELF_BUILD_CORE_STATUS_READER.v1"
    assert report["core_status"]["can_apply_without_human"] is False
    assert report["core_status"]["can_continue_preview"] is False


def test_driver_previews_self_build_core_only_with_approved_scope():
    module = load_module()
    report = module.run_self_build_dry_run_driver(
        REPO_ROOT,
        preview_approved_scope="self-build-core",
        wake_runner=fake_wake_runner,
    )
    assert report["wake_validation_passed"] is True
    assert report["readiness_status"] == "review_required"
    assert report["selected_queue_item"]["goal"] == "self-build-core"
    assert report["selected_next_action"] == "build_self_build_run_summary_view"
    assert report["codex_packet_preview"]["packet_ready"] is True
    assert "CODEX-ONLY PROMPT" in report["codex_packet_preview"]["codex_prompt_text"]
    assert report["local_apply_preview"]["runner_status"] == "preview_only"
    assert report["local_apply_preview"]["commands_executed"] is False
    assert all(value is False for value in report["selected_queue_item"]["protected_action_flags"].values())
    assert report["core_status"]["selected_next_action"] == "build_self_build_run_summary_view"
    assert report["core_status"]["can_continue_preview"] is True
    assert report["core_status"]["can_apply_without_human"] is False


def test_driver_never_executes_generated_codex_or_apply_commands():
    module = load_module()
    report = module.run_self_build_dry_run_driver(
        REPO_ROOT,
        preview_approved_scope="self-build-core",
        wake_runner=fake_wake_runner,
    )
    assert report["safety"]["codex_launched"] is False
    assert report["safety"]["local_apply_executed"] is False
    assert report["safety"]["generated_commands_executed"] is False
    assert report["driver_mode"] == "DRY_RUN"
    assert report["local_apply_preview"]["runner_mode"] == "DRY_RUN"
    assert report["approval_required"]["commit"] is True
    assert report["approval_required"]["push"] is True
    assert report["approval_required"]["merge"] is True


def test_driver_handles_sandbox_1312_as_blocker_not_sos():
    module = load_module()

    def sandbox_runner(command: list[str], _repo_root: Path) -> dict[str, object]:
        return {
            "command": " ".join(command),
            "returncode": 1312,
            "stdout": "",
            "stderr": "CreateProcessAsUserW failed: 1312",
        }

    report = module.run_self_build_dry_run_driver(REPO_ROOT, wake_runner=sandbox_runner)
    assert report["wake_validation_passed"] is False
    assert report["sos"]["sos_required"] is False
    assert report["sos"]["reason_code"] == "sandbox_blocker"


def test_no_reports_writes_required_by_default():
    module = load_module()
    report = module.run_self_build_dry_run_driver(REPO_ROOT, wake_runner=fake_wake_runner)
    assert report["safety"]["reports_written"] is False
    assert report["stop_report"]["files_written"] is False


def test_no_generated_command_execution_or_external_api_usage():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    assert "start-process" not in source
    assert "openai" not in source
    assert "anthropic" not in source
    assert "requests" not in source
    assert ".write_text" not in source
