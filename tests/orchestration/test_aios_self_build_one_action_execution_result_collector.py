from __future__ import annotations

from pathlib import Path

from automation.orchestration.aios_self_build_one_action_execution_result_collector import (
    SCHEMA,
    build_self_build_one_action_execution_result_collector,
)


ACTION_ID = "build_self_build_one_action_execution_result_collector"


def _allowed_paths():
    return [
        "automation/orchestration/aios_self_build_one_action_execution_result_collector.py",
        "tests/orchestration/test_aios_self_build_one_action_execution_result_collector.py",
        "docs/orchestration/AIOS_SELF_BUILD_ONE_ACTION_EXECUTION_RESULT_COLLECTOR.md",
    ]


def _validators():
    return [
        "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_self_build_one_action_execution_result_collector.py",
    ]


def _command():
    return (
        "python automation/orchestration/aios_productive_bounded_executor.py "
        "--goal self-build-core --action build_self_build_one_action_execution_result_collector --apply --max-repairs 1"
    )


def _queue_item(**overrides):
    item = {
        "schema": "AIOS_SELF_BUILD_WORK_QUEUE_ITEM.v1",
        "action_id": ACTION_ID,
        "goal": "self-build-core",
        "allowed_paths": _allowed_paths(),
        "validators": _validators(),
        "max_repairs": 1,
        "max_files_changed": 3,
        "protected_action_flags": {
            "git_add": False,
            "git_commit": False,
            "git_push": False,
            "merge": False,
            "scheduler_activation": False,
            "daemon_activation": False,
            "worker_dispatch": False,
            "queue_mutation": False,
            "approval_mutation": False,
            "broker_live_trading": False,
            "credentials": False,
            "real_orders": False,
            "real_webhooks": False,
            "destructive_cleanup": False,
        },
    }
    item.update(overrides)
    return item


def _approval(**overrides):
    approval = {
        "schema": "AIOS_SELF_BUILD_APPLY_APPROVAL_GATE.v1",
        "approval_status": "approved",
        "requested_action": ACTION_ID,
        "selected_queue_action": ACTION_ID,
        "approved_by": "Anthony Meza",
        "approval_token_present": True,
        "allowed_paths_match": True,
        "validators_present": True,
        "local_allowlisted_apply_allowed": True,
        "can_apply_without_human": False,
        "rejection_reasons": [],
        "safety": {"protected_action_requested": False},
    }
    approval.update(overrides)
    return approval


def _bridge(**overrides):
    bridge = {
        "schema": "AIOS_SELF_BUILD_LOCAL_APPLY_EXECUTOR_BRIDGE.v1",
        "bridge_status": "ready",
        "selected_action": ACTION_ID,
        "command_to_run": _command(),
        "allowed_paths": _allowed_paths(),
        "validators": _validators(),
        "max_repairs": 1,
        "max_files_changed": 3,
        "execution_status": "prepared_not_executed",
        "safety": {"commands_executed": False},
    }
    bridge.update(overrides)
    return bridge


def _executor(**overrides):
    executor = {
        "schema": "AIOS_SELF_BUILD_SINGLE_ACTION_EXECUTOR.v1",
        "executor_status": "ready",
        "selected_action": ACTION_ID,
        "command_to_run": _command(),
        "command_would_run": True,
        "command_executed": False,
        "allowed_paths": _allowed_paths(),
        "validators": _validators(),
        "max_repairs": 1,
        "max_files_changed": 3,
        "rejection_reasons": [],
        "safety": {"commands_executed": False},
    }
    executor.update(overrides)
    return executor


def _controller(**overrides):
    controller = {
        "schema": "AIOS_SELF_BUILD_ONE_ACTION_EXECUTION_CONTROLLER.v1",
        "controller_status": "ready",
        "selected_action": ACTION_ID,
        "command_to_run": _command(),
        "command_execution_allowed": True,
        "command_executed": False,
        "allowed_paths": _allowed_paths(),
        "validators": _validators(),
        "max_repairs": 1,
        "max_files_changed": 3,
        "rejection_reasons": [],
        "safety": {"commands_executed": False},
    }
    controller.update(overrides)
    return controller


def _runner(**overrides):
    runner = {
        "schema": "AIOS_SELF_BUILD_ONE_ACTION_APPLY_RUNNER.v1",
        "runner_status": "preview_ready",
        "selected_action": ACTION_ID,
        "command_to_run": _command(),
        "command_execution_allowed": True,
        "command_executed": False,
        "commands_executed": False,
        "allowed_paths": _allowed_paths(),
        "validators": _validators(),
        "max_repairs": 1,
        "max_files_changed": 3,
        "rejection_reasons": [],
        "safety": {"commands_executed": False, "files_written": False, "reports_written": False},
    }
    runner.update(overrides)
    return runner


def _gate(**overrides):
    gate = {
        "schema": "AIOS_SELF_BUILD_ONE_ACTION_EXECUTE_GATE.v1",
        "gate_status": "armed",
        "selected_action": ACTION_ID,
        "command_to_run": _command(),
        "command_execution_allowed": True,
        "command_executed": False,
        "commands_executed": False,
        "allowed_paths": _allowed_paths(),
        "validators": _validators(),
        "max_repairs": 1,
        "max_files_changed": 3,
        "rejection_reasons": [],
        "safety": {"commands_executed": False},
    }
    gate.update(overrides)
    return gate


def _local_executor(**overrides):
    local_executor = {
        "schema": "AIOS_SELF_BUILD_ONE_ACTION_LOCAL_APPLY_EXECUTOR.v1",
        "executor_status": "executed",
        "selected_action": ACTION_ID,
        "command_to_run": _command(),
        "command_execution_allowed": True,
        "command_executed": True,
        "command_returncode": 0,
        "command_stdout_preview": "ok",
        "command_stderr_preview": "",
        "allowed_paths": _allowed_paths(),
        "validators": _validators(),
        "max_repairs": 1,
        "max_files_changed": 3,
        "post_execution_evidence": {
            "command_runner_called": True,
            "working_directory": r"C:\Dev\Ai.Os",
            "returncode": 0,
            "changed_files": [
                "automation/orchestration/aios_self_build_one_action_execution_result_collector.py",
            ],
            "validators_run": _validators(),
            "stdout_preview": "ok",
            "stderr_preview": "",
        },
        "rejection_reasons": [],
        "safety": {"commands_executed": True, "command_executed": True},
    }
    local_executor.update(overrides)
    return local_executor


def _verifier(**overrides):
    verifier = {
        "schema": "AIOS_SELF_BUILD_APPLY_RESULT_VERIFIER.v1",
        "verifier_status": "passed",
        "selected_action": ACTION_ID,
        "changed_files": [
            "automation/orchestration/aios_self_build_one_action_execution_result_collector.py",
        ],
        "allowed_paths": _allowed_paths(),
        "unexpected_files": [],
        "validators": [
            {
                "name": "pytest",
                "command": _validators()[0],
                "passed": True,
                "returncode": 0,
            }
        ],
        "validators_passed": 1,
        "validators_failed": 0,
        "max_files_changed": 3,
        "file_count_ok": True,
        "allowed_paths_ok": True,
        "result_safe_to_report": True,
        "result_safe_to_package": True,
        "rejection_reasons": [],
        "safety": {"commands_executed": False},
    }
    verifier.update(overrides)
    return verifier


def _build(**overrides):
    payload = {
        "selected_queue_item": _queue_item(),
        "apply_approval": _approval(),
        "local_apply_executor_bridge": _bridge(),
        "single_action_executor": _executor(),
        "one_action_execution_controller": _controller(),
        "one_action_apply_runner": _runner(),
        "one_action_execute_gate": _gate(),
        "one_action_local_apply_executor": _local_executor(),
        "apply_result_verifier": _verifier(),
        "post_validation_results": [],
    }
    payload.update(overrides)
    return build_self_build_one_action_execution_result_collector(**payload)


def test_import_and_schema_default_blocks_without_execution():
    result = build_self_build_one_action_execution_result_collector()

    assert result["schema"] == SCHEMA
    assert result["collector_status"] == "blocked"
    assert result["result_decision"] == "blocked"
    assert result["command_executed"] is False
    assert result["result_safe_to_package"] is False
    assert result["safety"]["commands_executed"] is False
    assert result["files_written"] is False
    assert result["reports_written"] is False


def test_dry_run_local_executor_blocks_with_command_not_executed():
    result = _build(
        one_action_local_apply_executor=_local_executor(
            executor_status="dry_run_ready",
            command_executed=False,
            command_returncode=None,
            post_execution_evidence={"command_runner_called": False, "changed_files": [], "validators_run": []},
        ),
        apply_result_verifier=_verifier(
            verifier_status="blocked",
            changed_files=[],
            validators=[],
            validators_passed=0,
            result_safe_to_package=False,
            rejection_reasons=["command_not_executed", "validators_missing"],
        ),
    )

    assert result["collector_status"] == "blocked"
    assert result["command_executed"] is False
    assert "command_not_executed" in result["rejection_reasons"]
    assert result["result_safe_to_package"] is False
    assert result["safety"]["commands_executed"] is False


def test_executed_and_verified_result_is_collected():
    result = _build()

    assert result["collector_status"] == "collected"
    assert result["result_decision"] == "report_result"
    assert result["selected_action"] == ACTION_ID
    assert result["command_executed"] is True
    assert result["command_returncode"] == 0
    assert result["changed_files"] == [
        "automation/orchestration/aios_self_build_one_action_execution_result_collector.py",
    ]
    assert result["validators_passed"] == 1
    assert result["validators_failed"] == 0
    assert result["result_safe_to_report"] is True
    assert result["result_safe_to_package"] is True
    assert result["safety"]["commands_executed"] is False
    assert result["files_written"] is False
    assert result["reports_written"] is False


def test_nonzero_returncode_rejects():
    result = _build(one_action_local_apply_executor=_local_executor(command_returncode=1))

    assert result["collector_status"] == "rejected"
    assert "command_returncode_nonzero" in result["rejection_reasons"]
    assert result["result_safe_to_package"] is False


def test_verifier_failed_rejects():
    result = _build(apply_result_verifier=_verifier(verifier_status="failed", rejection_reasons=["validators_failed"]))

    assert result["collector_status"] == "rejected"
    assert "apply_result_verifier_failed" in result["rejection_reasons"]
    assert result["result_safe_to_package"] is False


def test_changed_file_outside_allowed_paths_rejects():
    result = _build(
        one_action_local_apply_executor=_local_executor(
            post_execution_evidence={
                "command_runner_called": True,
                "returncode": 0,
                "changed_files": ["Reports/outside.md"],
                "validators_run": _validators(),
            }
        )
    )

    assert result["collector_status"] == "rejected"
    assert "requested_paths_outside_allowed_paths" in result["rejection_reasons"]
    assert result["result_safe_to_package"] is False


def test_action_mismatch_rejects():
    result = _build(one_action_apply_runner=_runner(selected_action="build_different_item"))

    assert result["collector_status"] == "rejected"
    assert "selected_action_mismatch" in result["rejection_reasons"]


def test_protected_action_request_rejects():
    result = _build(one_action_local_apply_executor=_local_executor(git_push_requested=True))

    assert result["collector_status"] == "rejected"
    assert "protected_action_requested" in result["rejection_reasons"]
    assert result["safety"]["protected_action_requested"] is True
    assert result["safety"]["git_push"] is False


def test_sandbox_1312_is_runner_blocker_not_code_failure():
    result = _build(
        one_action_local_apply_executor=_local_executor(
            executor_status="blocked",
            command_executed=False,
            command_returncode=None,
            command_stderr_preview="CreateProcessAsUserW failed: 1312",
            post_execution_evidence={
                "command_runner_called": False,
                "returncode": None,
                "changed_files": [],
                "validators_run": [],
                "stderr_preview": "CreateProcessAsUserW failed: 1312",
            },
        ),
        apply_result_verifier=_verifier(
            verifier_status="blocked",
            changed_files=[],
            validators=[],
            validators_passed=0,
            result_safe_to_package=False,
            rejection_reasons=["command_not_executed"],
        ),
    )

    assert result["collector_status"] == "blocked"
    assert "sandbox_1312_runner_blocker" in result["rejection_reasons"]
    assert result["safety"]["sandbox_1312_blocker"] is True
    assert "not a code failure" in result["next_safe_action"]


def test_validator_failure_rejects():
    result = _build(
        apply_result_verifier=_verifier(
            verifier_status="passed",
            validators=[
                {
                    "name": "pytest",
                    "command": _validators()[0],
                    "passed": False,
                    "returncode": 1,
                }
            ],
            validators_passed=0,
            validators_failed=1,
        )
    )

    assert result["collector_status"] == "rejected"
    assert "validators_failed" in result["rejection_reasons"]


def test_source_has_no_direct_command_or_file_side_effect_apis():
    source = Path("automation/orchestration/aios_self_build_one_action_execution_result_collector.py").read_text()

    forbidden_terms = [
        "subprocess",
        "requests",
        "socket",
        "urllib",
        ".write_text",
        ".write_bytes",
        "open(",
        "os.system",
        "git add",
        "git commit",
        "git push",
        "git merge",
    ]
    assert all(term not in source for term in forbidden_terms)
