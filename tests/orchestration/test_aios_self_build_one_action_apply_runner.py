from __future__ import annotations

from pathlib import Path

from automation.orchestration.aios_self_build_one_action_apply_runner import (
    ONE_ACTION_APPLY_MODE,
    RUNNER_MODE_APPLY_ARMED_NOT_EXECUTED,
    RUNNER_MODE_DRY_RUN,
    SCHEMA,
    build_self_build_one_action_apply_runner,
)


ACTION_ID = "build_self_build_one_action_apply_runner"


def _allowed_paths():
    return [
        "automation/orchestration/aios_self_build_one_action_apply_runner.py",
        "tests/orchestration/test_aios_self_build_one_action_apply_runner.py",
        "docs/orchestration/AIOS_SELF_BUILD_ONE_ACTION_APPLY_RUNNER.md",
    ]


def _validators():
    return [
        "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_self_build_one_action_apply_runner.py",
    ]


def _command():
    return (
        "python automation/orchestration/aios_productive_bounded_executor.py "
        "--goal self-build-core --action build_self_build_one_action_apply_runner --apply --max-repairs 1"
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
        "execution_mode": "APPLY_ALLOWED_NOT_RUN",
        "selected_action": ACTION_ID,
        "command_to_run": _command(),
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


def _controller(**overrides):
    controller = {
        "schema": "AIOS_SELF_BUILD_ONE_ACTION_EXECUTION_CONTROLLER.v1",
        "controller_status": "ready",
        "execution_decision": "execute_one_action_allowed",
        "selected_action": ACTION_ID,
        "command_to_run": _command(),
        "command_execution_allowed": True,
        "command_executed": False,
        "allowed_paths": _allowed_paths(),
        "validators": _validators(),
        "max_repairs": 1,
        "max_files_changed": 3,
        "rejection_reasons": [],
        "safety": {
            "command_execution_allowed_by_controller": True,
            "commands_executed": False,
            "command_executed": False,
        },
    }
    controller.update(overrides)
    return controller


def _execution_request(**overrides):
    request = {
        "requested": True,
        "mode": ONE_ACTION_APPLY_MODE,
        "requested_action": ACTION_ID,
        "requested_write_paths": _allowed_paths(),
    }
    request.update(overrides)
    return request


def _runner_options(**overrides):
    options = {
        "execute": False,
        "requested_action": ACTION_ID,
        "requested_write_paths": _allowed_paths(),
    }
    options.update(overrides)
    return options


def _build(**overrides):
    payload = {
        "selected_queue_item": _queue_item(),
        "apply_approval": _approval(),
        "local_apply_executor_bridge": _bridge(),
        "single_action_executor": _executor(),
        "apply_result_verifier": _verifier(),
        "one_action_execution_controller": _controller(),
        "execution_request": _execution_request(),
        "runner_options": _runner_options(),
    }
    payload.update(overrides)
    return build_self_build_one_action_apply_runner(**payload)


def test_import_and_schema_default_blocks_without_execution():
    result = build_self_build_one_action_apply_runner()

    assert result["schema"] == SCHEMA
    assert result["runner_status"] == "blocked"
    assert result["runner_mode"] == RUNNER_MODE_DRY_RUN
    assert result["command_execution_allowed"] is False
    assert result["command_executed"] is False
    assert result["safety"]["commands_executed"] is False


def test_preview_ready_defaults_to_dry_run_and_does_not_execute():
    result = _build(runner_options={})

    assert result["runner_status"] == "preview_ready"
    assert result["runner_mode"] == RUNNER_MODE_DRY_RUN
    assert result["selected_action"] == ACTION_ID
    assert result["command_to_run"] == _command()
    assert result["command_execution_allowed"] is True
    assert result["command_executed"] is False
    assert result["allowed_paths"] == _allowed_paths()
    assert result["validators"] == _validators()
    assert result["max_repairs"] == 1
    assert result["max_files_changed"] == 3
    assert result["rejection_reasons"] == []
    assert result["safety"]["commands_executed"] is False
    assert result["safety"]["files_written"] is False
    assert result["safety"]["reports_written"] is False


def test_execute_true_arms_runner_but_still_does_not_execute():
    result = _build(runner_options=_runner_options(execute=True))

    assert result["runner_status"] == "preview_ready"
    assert result["runner_mode"] == RUNNER_MODE_APPLY_ARMED_NOT_EXECUTED
    assert result["command_execution_allowed"] is True
    assert result["command_executed"] is False
    assert result["safety"]["apply_armed_not_executed"] is True
    assert result["safety"]["commands_executed"] is False


def test_missing_execution_request_blocks():
    result = _build(execution_request=None)

    assert result["runner_status"] == "blocked"
    assert result["command_execution_allowed"] is False
    assert "execution_request_missing" in result["rejection_reasons"]


def test_wrong_execution_mode_blocks():
    result = _build(execution_request=_execution_request(mode="DRY_RUN_PLAN"))

    assert result["runner_status"] == "blocked"
    assert "execution_request_mode_not_one_action_apply" in result["rejection_reasons"]


def test_unrequested_execution_blocks():
    result = _build(execution_request=_execution_request(requested=False))

    assert result["runner_status"] == "blocked"
    assert "execution_request_not_requested" in result["rejection_reasons"]


def test_missing_or_rejected_approval_blocks():
    result = _build(apply_approval=_approval(approval_status="rejected"))

    assert result["runner_status"] == "blocked"
    assert "apply_approval_not_approved" in result["rejection_reasons"]


def test_bridge_not_ready_blocks():
    result = _build(local_apply_executor_bridge=_bridge(bridge_status="blocked"))

    assert result["runner_status"] == "blocked"
    assert "local_apply_bridge_not_ready" in result["rejection_reasons"]


def test_single_action_executor_not_ready_blocks():
    result = _build(single_action_executor=_executor(executor_status="blocked"))

    assert result["runner_status"] == "blocked"
    assert "single_action_executor_not_ready" in result["rejection_reasons"]


def test_command_would_run_false_blocks():
    result = _build(single_action_executor=_executor(command_would_run=False))

    assert result["runner_status"] == "blocked"
    assert "command_would_run_false" in result["rejection_reasons"]


def test_controller_not_ready_blocks():
    result = _build(one_action_execution_controller=_controller(controller_status="blocked"))

    assert result["runner_status"] == "blocked"
    assert "one_action_execution_controller_not_ready" in result["rejection_reasons"]


def test_controller_not_allowing_execution_blocks():
    result = _build(one_action_execution_controller=_controller(command_execution_allowed=False))

    assert result["runner_status"] == "blocked"
    assert "one_action_execution_controller_not_allowed" in result["rejection_reasons"]


def test_missing_command_to_run_rejects_when_request_is_present():
    result = _build(
        local_apply_executor_bridge=_bridge(command_to_run=""),
        single_action_executor=_executor(command_to_run=""),
        one_action_execution_controller=_controller(command_to_run=""),
    )

    assert result["runner_status"] == "rejected"
    assert result["command_execution_allowed"] is False
    assert "command_to_run_missing" in result["rejection_reasons"]


def test_verifier_blocked_only_for_pre_execution_reasons_allows_preview():
    result = _build(apply_result_verifier=_verifier(rejection_reasons=["command_not_executed", "validators_missing"]))

    assert result["runner_status"] == "preview_ready"
    assert result["command_executed"] is False


def test_verifier_blocked_for_other_reason_blocks():
    result = _build(apply_result_verifier=_verifier(rejection_reasons=["validator_failed"]))

    assert result["runner_status"] == "blocked"
    assert "apply_result_verifier_blocked" in result["rejection_reasons"]


def test_verifier_failed_for_unexpected_files_rejects():
    result = _build(
        apply_result_verifier=_verifier(
            verifier_status="failed",
            unexpected_files=["Reports/outside.md"],
            rejection_reasons=["unexpected_files"],
        )
    )

    assert result["runner_status"] == "rejected"
    assert result["command_execution_allowed"] is False
    assert "apply_result_verifier_failed" in result["rejection_reasons"]


def test_selected_action_mismatch_rejects():
    result = _build(local_apply_executor_bridge=_bridge(selected_action="build_different_item"))

    assert result["runner_status"] == "rejected"
    assert result["command_execution_allowed"] is False
    assert "selected_action_mismatch" in result["rejection_reasons"]


def test_path_outside_allowed_paths_rejects():
    result = _build(execution_request=_execution_request(requested_write_paths=[*_allowed_paths(), "Reports/outside.md"]))

    assert result["runner_status"] == "rejected"
    assert result["command_execution_allowed"] is False
    assert "requested_paths_outside_allowed_paths" in result["rejection_reasons"]


def test_unbounded_allowed_path_rejects():
    result = _build(selected_queue_item=_queue_item(allowed_paths=[*_allowed_paths(), "../outside.py"]))

    assert result["runner_status"] == "rejected"
    assert "requested_paths_outside_allowed_paths" in result["rejection_reasons"]


def test_missing_validators_rejects():
    result = _build(
        selected_queue_item=_queue_item(validators=[]),
        local_apply_executor_bridge=_bridge(validators=[]),
        single_action_executor=_executor(validators=[]),
        one_action_execution_controller=_controller(validators=[]),
    )

    assert result["runner_status"] == "rejected"
    assert result["command_execution_allowed"] is False
    assert "validators_missing" in result["rejection_reasons"]


def test_protected_action_request_rejects():
    result = _build(runner_options=_runner_options(git_push_requested=True))

    assert result["runner_status"] == "rejected"
    assert result["command_execution_allowed"] is False
    assert result["command_executed"] is False
    assert "protected_action_requested" in result["rejection_reasons"]
    assert result["safety"]["protected_action_requested"] is True


def test_broker_live_trading_credentials_request_rejects():
    result = _build(
        runner_options=_runner_options(
            broker=True,
            live_trading=True,
            credentials=True,
            real_orders=True,
            real_webhooks=True,
        )
    )

    assert result["runner_status"] == "rejected"
    assert result["command_execution_allowed"] is False
    assert "protected_action_requested" in result["rejection_reasons"]
    assert result["safety"]["broker"] is False
    assert result["safety"]["live_trading"] is False
    assert result["safety"]["credentials"] is False


def test_max_files_changed_above_five_rejects():
    result = _build(one_action_execution_controller=_controller(max_files_changed=6))

    assert result["runner_status"] == "rejected"
    assert result["command_execution_allowed"] is False
    assert "max_files_changed_exceeds_five" in result["rejection_reasons"]


def test_missing_max_files_changed_rejects():
    queue_item = _queue_item()
    queue_item.pop("max_files_changed")
    controller = _controller()
    controller.pop("max_files_changed")
    executor = _executor()
    executor.pop("max_files_changed")
    bridge = _bridge()
    bridge.pop("max_files_changed")
    verifier = _verifier()
    verifier.pop("max_files_changed")

    result = _build(
        selected_queue_item=queue_item,
        local_apply_executor_bridge=bridge,
        single_action_executor=executor,
        apply_result_verifier=verifier,
        one_action_execution_controller=controller,
    )

    assert result["runner_status"] == "rejected"
    assert "max_files_changed_missing" in result["rejection_reasons"]


def test_max_repairs_above_one_rejects():
    result = _build(one_action_execution_controller=_controller(max_repairs=2))

    assert result["runner_status"] == "rejected"
    assert result["command_execution_allowed"] is False
    assert "max_repairs_exceeds_one" in result["rejection_reasons"]


def test_missing_max_repairs_rejects():
    queue_item = _queue_item()
    queue_item.pop("max_repairs")
    controller = _controller()
    controller.pop("max_repairs")
    executor = _executor()
    executor.pop("max_repairs")
    bridge = _bridge()
    bridge.pop("max_repairs")

    result = _build(
        selected_queue_item=queue_item,
        local_apply_executor_bridge=bridge,
        single_action_executor=executor,
        one_action_execution_controller=controller,
    )

    assert result["runner_status"] == "rejected"
    assert "max_repairs_missing" in result["rejection_reasons"]


def test_sandbox_1312_blocks_as_runner_blocker_not_code_failure():
    result = _build(runner_options=_runner_options(local_error="CreateProcessAsUserW failed: 1312"))

    assert result["runner_status"] == "blocked"
    assert result["command_execution_allowed"] is False
    assert result["command_executed"] is False
    assert "sandbox_1312_runner_blocker" in result["rejection_reasons"]
    assert "not a code failure" in result["next_safe_action"]


def test_runner_source_has_no_command_or_file_side_effect_apis():
    source = Path("automation/orchestration/aios_self_build_one_action_apply_runner.py").read_text()

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
