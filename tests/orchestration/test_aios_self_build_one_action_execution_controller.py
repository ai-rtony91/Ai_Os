from __future__ import annotations

from pathlib import Path

from automation.orchestration.aios_self_build_one_action_execution_controller import (
    ONE_ACTION_APPLY_MODE,
    SCHEMA,
    build_self_build_one_action_execution_controller,
)


ACTION_ID = "build_self_build_one_action_execution_controller"


def _allowed_paths():
    return [
        "automation/orchestration/aios_self_build_one_action_execution_controller.py",
        "tests/orchestration/test_aios_self_build_one_action_execution_controller.py",
        "docs/orchestration/AIOS_SELF_BUILD_ONE_ACTION_EXECUTION_CONTROLLER.md",
    ]


def _validators():
    return [
        "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_self_build_one_action_execution_controller.py",
    ]


def _queue_item(**overrides):
    item = {
        "schema": "AIOS_SELF_BUILD_WORK_QUEUE_ITEM.v1",
        "action_id": ACTION_ID,
        "goal": "self-build-core",
        "allowed_paths": _allowed_paths(),
        "validators": _validators(),
        "protected_action_flags": {
            "git_add": False,
            "git_commit": False,
            "git_push": False,
            "merge": False,
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
        "command_to_run": (
            "python automation/orchestration/aios_productive_bounded_executor.py "
            "--goal self-build-core --action build_self_build_one_action_execution_controller --apply --max-repairs 1"
        ),
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
        "execution_mode": "APPLY_ALLOWED_NOT_RUN",
        "selected_action": ACTION_ID,
        "command_to_run": _bridge()["command_to_run"],
        "command_would_run": True,
        "command_executed": False,
        "allowed_paths": _allowed_paths(),
        "validators": _validators(),
        "max_repairs": 1,
        "max_files_changed": 3,
        "approval_status": "approved",
        "bridge_status": "ready",
        "rejection_reasons": [],
        "safety": {"commands_executed": False, "command_executed": False},
    }
    executor.update(overrides)
    return executor


def _verifier(**overrides):
    verifier = {
        "schema": "AIOS_SELF_BUILD_APPLY_RESULT_VERIFIER.v1",
        "verifier_status": "blocked",
        "selected_action": ACTION_ID,
        "changed_files": [],
        "allowed_paths": _allowed_paths(),
        "unexpected_files": [],
        "validators": [],
        "validators_passed": 0,
        "validators_failed": 0,
        "max_files_changed": 3,
        "file_count_ok": True,
        "allowed_paths_ok": True,
        "result_safe_to_report": True,
        "result_safe_to_package": False,
        "rejection_reasons": ["command_not_executed"],
        "safety": {"commands_executed": False},
    }
    verifier.update(overrides)
    return verifier


def _core(**overrides):
    core = {
        "schema": "AIOS_SELF_BUILD_CORE_STATUS_READER.v1",
        "selected_next_action": ACTION_ID,
        "can_apply_without_human": False,
    }
    core.update(overrides)
    return core


def _execution_request(**overrides):
    request = {
        "requested": True,
        "mode": ONE_ACTION_APPLY_MODE,
        "requested_action": ACTION_ID,
        "requested_write_paths": _allowed_paths(),
    }
    request.update(overrides)
    return request


def _build(**overrides):
    payload = {
        "selected_queue_item": _queue_item(),
        "apply_approval": _approval(),
        "local_apply_executor_bridge": _bridge(),
        "single_action_executor": _executor(),
        "apply_result_verifier": _verifier(),
        "core_status": _core(),
        "stop_report": {},
        "execution_request": _execution_request(),
    }
    payload.update(overrides)
    return build_self_build_one_action_execution_controller(**payload)


def test_import_and_schema():
    result = build_self_build_one_action_execution_controller()

    assert result["schema"] == SCHEMA
    assert result["controller_status"] == "blocked"
    assert result["command_execution_allowed"] is False
    assert result["command_executed"] is False
    assert result["safety"]["commands_executed"] is False


def test_ready_allows_exactly_one_action_without_executing_it():
    result = _build()

    assert result["controller_status"] == "ready"
    assert result["execution_decision"] == "execute_one_action_allowed"
    assert result["selected_action"] == ACTION_ID
    assert result["command_to_run"]
    assert result["command_execution_allowed"] is True
    assert result["command_executed"] is False
    assert result["allowed_paths"] == _allowed_paths()
    assert result["validators"] == _validators()
    assert result["max_repairs"] == 1
    assert result["max_files_changed"] == 3
    assert result["approval_status"] == "approved"
    assert result["bridge_status"] == "ready"
    assert result["executor_status"] == "ready"
    assert result["verifier_status"] == "blocked"
    assert result["rejection_reasons"] == []
    assert result["safety"]["command_execution_allowed_by_controller"] is True
    assert result["safety"]["command_executed"] is False


def test_missing_execution_request_blocks():
    result = _build(execution_request=None)

    assert result["controller_status"] == "blocked"
    assert result["execution_decision"] == "blocked"
    assert result["command_execution_allowed"] is False
    assert "execution_request_missing" in result["rejection_reasons"]


def test_wrong_execution_mode_blocks():
    result = _build(execution_request=_execution_request(mode="DRY_RUN_PLAN"))

    assert result["controller_status"] == "blocked"
    assert "execution_request_mode_not_one_action_apply" in result["rejection_reasons"]


def test_unrequested_execution_blocks():
    result = _build(execution_request=_execution_request(requested=False))

    assert result["controller_status"] == "blocked"
    assert "execution_request_not_requested" in result["rejection_reasons"]


def test_missing_or_rejected_approval_blocks():
    result = _build(apply_approval=_approval(approval_status="rejected"))

    assert result["controller_status"] == "blocked"
    assert "apply_approval_not_approved" in result["rejection_reasons"]


def test_bridge_not_ready_blocks():
    result = _build(local_apply_executor_bridge=_bridge(bridge_status="blocked"))

    assert result["controller_status"] == "blocked"
    assert "local_apply_bridge_not_ready" in result["rejection_reasons"]


def test_single_action_executor_not_ready_blocks():
    result = _build(single_action_executor=_executor(executor_status="blocked"))

    assert result["controller_status"] == "blocked"
    assert "single_action_executor_not_ready" in result["rejection_reasons"]


def test_command_would_run_false_blocks():
    result = _build(single_action_executor=_executor(command_would_run=False))

    assert result["controller_status"] == "blocked"
    assert "command_would_run_false" in result["rejection_reasons"]


def test_selected_action_mismatch_rejects():
    result = _build(local_apply_executor_bridge=_bridge(selected_action="build_different_item"))

    assert result["controller_status"] == "rejected"
    assert result["execution_decision"] == "rejected"
    assert result["command_execution_allowed"] is False
    assert "selected_action_mismatch" in result["rejection_reasons"]


def test_path_outside_allowed_paths_rejects():
    result = _build(
        execution_request=_execution_request(
            requested_write_paths=_allowed_paths() + ["automation/orchestration/outside_scope.py"]
        )
    )

    assert result["controller_status"] == "rejected"
    assert "requested_paths_outside_allowed_paths" in result["rejection_reasons"]


def test_unbounded_allowed_path_rejects():
    result = _build(selected_queue_item=_queue_item(allowed_paths=_allowed_paths() + ["../outside.py"]))

    assert result["controller_status"] == "rejected"
    assert "requested_paths_outside_allowed_paths" in result["rejection_reasons"]


def test_missing_validators_rejects():
    result = _build(
        selected_queue_item=_queue_item(validators=[]),
        local_apply_executor_bridge=_bridge(validators=[]),
        single_action_executor=_executor(validators=[]),
    )

    assert result["controller_status"] == "rejected"
    assert "validators_missing" in result["rejection_reasons"]


def test_protected_action_request_rejects():
    result = _build(selected_queue_item=_queue_item(protected_action_flags={"git_commit": True}))

    assert result["controller_status"] == "rejected"
    assert "protected_action_requested" in result["rejection_reasons"]
    assert result["safety"]["protected_action_requested"] is True


def test_core_apply_without_human_rejects():
    result = _build(core_status=_core(can_apply_without_human=True))

    assert result["controller_status"] == "rejected"
    assert "core_apply_without_human_not_allowed" in result["rejection_reasons"]


def test_verifier_blocked_only_for_command_not_executed_allows_pre_execution_readiness():
    result = _build(apply_result_verifier=_verifier(verifier_status="blocked", rejection_reasons=["command_not_executed"]))

    assert result["controller_status"] == "ready"
    assert result["command_execution_allowed"] is True


def test_verifier_blocked_for_other_reason_blocks():
    result = _build(
        apply_result_verifier=_verifier(
            verifier_status="blocked",
            rejection_reasons=["command_not_executed", "sandbox_1312_runner_blocker"],
        )
    )

    assert result["controller_status"] == "blocked"
    assert "apply_result_verifier_blocked" in result["rejection_reasons"]


def test_verifier_failed_rejects():
    result = _build(apply_result_verifier=_verifier(verifier_status="failed", rejection_reasons=["validators_failed"]))

    assert result["controller_status"] == "rejected"
    assert "apply_result_verifier_failed" in result["rejection_reasons"]


def test_sandbox_1312_is_runner_blocker_not_code_failure():
    result = _build(stop_report={"stderr": "CreateProcessAsUserW failed: 1312"})

    assert result["controller_status"] == "blocked"
    assert result["command_execution_allowed"] is False
    assert result["command_executed"] is False
    assert result["safety"]["sandbox_1312_blocker"] is True
    assert "sandbox_1312_runner_blocker" in result["rejection_reasons"]
    assert "not a code failure" in result["next_safe_action"]


def test_module_has_no_command_network_or_file_write_usage():
    source = Path("automation/orchestration/aios_self_build_one_action_execution_controller.py").read_text()

    forbidden = [
        "subprocess",
        "requests",
        "socket",
        "urllib",
        ".write_text",
        ".write_bytes",
        "open(",
    ]
    for token in forbidden:
        assert token not in source
