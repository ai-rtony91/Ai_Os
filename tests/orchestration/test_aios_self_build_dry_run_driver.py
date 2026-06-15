from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_self_build_dry_run_driver.py"

COMPLETED_BEFORE_INTEGRATION = [
    "automation/orchestration/aios_self_build_core_status_reader.py",
    "tests/orchestration/test_aios_self_build_core_status_reader.py",
    "docs/orchestration/AIOS_SELF_BUILD_CORE_STATUS_READER.md",
    "automation/orchestration/aios_self_build_run_summary_view.py",
    "tests/orchestration/test_aios_self_build_run_summary_view.py",
    "docs/orchestration/AIOS_SELF_BUILD_RUN_SUMMARY_VIEW.md",
    "automation/orchestration/aios_self_build_apply_approval_gate.py",
    "tests/orchestration/test_aios_self_build_apply_approval_gate.py",
    "docs/orchestration/AIOS_SELF_BUILD_APPLY_APPROVAL_GATE.md",
    "automation/orchestration/aios_self_build_dry_run_driver.py",
    "tests/orchestration/test_aios_self_build_dry_run_driver.py",
    "docs/orchestration/AIOS_SELF_BUILD_DRY_RUN_DRIVER.md",
    "automation/orchestration/aios_self_build_local_apply_executor_bridge.py",
    "tests/orchestration/test_aios_self_build_local_apply_executor_bridge.py",
    "docs/orchestration/AIOS_SELF_BUILD_LOCAL_APPLY_EXECUTOR_BRIDGE.md",
]


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


def seed_completed_paths(repo_root: Path, paths: list[str] = COMPLETED_BEFORE_INTEGRATION) -> None:
    for relative_path in paths:
        target = repo_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("present", encoding="utf-8")


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
    assert report["apply_approval"]["schema"] == "AIOS_SELF_BUILD_APPLY_APPROVAL_GATE.v1"
    assert report["apply_approval"]["can_apply_without_human"] is False
    assert report["local_apply_executor_bridge"]["schema"] == "AIOS_SELF_BUILD_LOCAL_APPLY_EXECUTOR_BRIDGE.v1"
    assert report["local_apply_executor_bridge"]["execution_status"] == "prepared_not_executed"


def test_driver_previews_single_action_executor_with_approved_scope(tmp_path):
    module = load_module()
    seed_completed_paths(tmp_path)
    report = module.run_self_build_dry_run_driver(
        tmp_path,
        preview_approved_scope="self-build-core",
        wake_runner=fake_wake_runner,
    )
    assert report["wake_validation_passed"] is True
    assert report["readiness_status"] == "review_required"
    assert report["selected_queue_item"]["goal"] == "self-build-core"
    assert report["selected_next_action"] == "build_self_build_single_action_executor"
    assert report["codex_packet_preview"]["packet_ready"] is True
    assert "CODEX-ONLY PROMPT" in report["codex_packet_preview"]["codex_prompt_text"]
    assert report["local_apply_preview"]["runner_status"] == "preview_only"
    assert report["local_apply_preview"]["commands_executed"] is False
    assert all(value is False for value in report["selected_queue_item"]["protected_action_flags"].values())
    assert report["core_status"]["selected_next_action"] == "build_self_build_single_action_executor"
    assert report["core_status"]["can_continue_preview"] is True
    assert report["core_status"]["can_apply_without_human"] is False
    assert report["apply_approval"]["approval_status"] == "review_required"
    assert report["apply_approval"]["local_allowlisted_apply_allowed"] is False
    assert report["local_apply_executor_bridge"]["bridge_status"] == "blocked"
    assert report["local_apply_executor_bridge"]["execution_status"] == "prepared_not_executed"


def test_driver_never_executes_generated_codex_or_apply_commands(tmp_path):
    module = load_module()
    seed_completed_paths(tmp_path)
    report = module.run_self_build_dry_run_driver(
        tmp_path,
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
    assert report["apply_approval"]["can_apply_without_human"] is False


def test_valid_anthony_approval_prepares_bridge_but_executes_nothing(tmp_path):
    module = load_module()
    seed_completed_paths(tmp_path)
    report = module.run_self_build_dry_run_driver(
        tmp_path,
        preview_approved_scope="self-build-core",
        approved_by="Anthony Meza",
        approval_token="ANTHONY_APPROVED_LOCAL_APPLY",
        approve_action="build_self_build_single_action_executor",
        wake_runner=fake_wake_runner,
    )

    assert report["selected_next_action"] == "build_self_build_single_action_executor"
    assert report["apply_approval"]["approval_status"] == "approved"
    assert report["apply_approval"]["local_allowlisted_apply_allowed"] is True
    assert report["apply_approval"]["can_apply_without_human"] is False
    assert report["local_apply_executor_bridge"]["bridge_status"] == "ready"
    assert report["local_apply_executor_bridge"]["execution_status"] == "prepared_not_executed"
    assert report["local_apply_executor_bridge"]["command_to_run"]
    assert report["safety"]["local_apply_executed"] is False
    assert report["safety"]["generated_commands_executed"] is False
    assert report["safety"]["files_written"] is False


def test_mismatched_approve_action_is_rejected(tmp_path):
    module = load_module()
    seed_completed_paths(tmp_path)
    report = module.run_self_build_dry_run_driver(
        tmp_path,
        preview_approved_scope="self-build-core",
        approved_by="Anthony Meza",
        approval_token="ANTHONY_APPROVED_LOCAL_APPLY",
        approve_action="build_different_item",
        wake_runner=fake_wake_runner,
    )

    assert report["selected_next_action"] == "build_self_build_single_action_executor"
    assert report["apply_approval"]["approval_status"] == "rejected"
    assert "requested_action_mismatch" in report["apply_approval"]["rejection_reasons"]
    assert report["local_apply_executor_bridge"]["bridge_status"] == "blocked"
    assert report["safety"]["local_apply_executed"] is False


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
