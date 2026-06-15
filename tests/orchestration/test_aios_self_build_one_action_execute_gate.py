from __future__ import annotations

from pathlib import Path

from automation.orchestration.aios_self_build_one_action_execute_gate import (
    EXECUTE_GATE_MODE,
    ONE_ACTION_APPLY_MODE,
    SCHEMA,
    build_self_build_one_action_execute_gate,
)


ACTION_ID = "build_self_build_one_action_execute_gate"


def _allowed_paths():
    return [
        "automation/orchestration/aios_self_build_one_action_execute_gate.py",
        "tests/orchestration/test_aios_self_build_one_action_execute_gate.py",
        "docs/orchestration/AIOS_SELF_BUILD_ONE_ACTION_EXECUTE_GATE.md",
    ]


def _validators():
    return [
        "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_self_build_one_action_execute_gate.py",
    ]


def _command():
    return (
        "python automation/orchestration/aios_productive_bounded_executor.py "
        "--goal self-build-core --action build_self_build_one_action_execute_gate --apply --max-repairs 1"
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
        "safety": {"commands_executed": False, "command_executed": False},
    }
    controller.update(overrides)
    return controller


def _runner(**overrides):
    runner = {
        "schema": "AIOS_SELF_BUILD_ONE_ACTION_APPLY_RUNNER.v1",
        "runner_status": "preview_ready",
        "runner_mode": "DRY_RUN",
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
        "safety": {
            "commands_executed": False,
            "command_executed": False,
            "files_written": False,
            "reports_written": False,
        },
    }
    runner.update(overrides)
    return runner


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


def _execution_request(**overrides):
    request = {
        "requested": True,
        "mode": ONE_ACTION_APPLY_MODE,
        "requested_action": ACTION_ID,
        "requested_write_paths": _allowed_paths(),
    }
    request.update(overrides)
    return request


def _execute_gate_request(**overrides):
    request = {
        "requested": True,
        "mode": EXECUTE_GATE_MODE,
        "requested_action": ACTION_ID,
        "approved_by": "Anthony Meza",
        "approval_token_present": True,
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
        "one_action_execution_controller": _controller(),
        "one_action_apply_runner": _runner(),
        "apply_result_verifier": _verifier(),
        "execution_request": _execution_request(),
        "execute_gate_request": _execute_gate_request(),
    }
    payload.update(overrides)
    return build_self_build_one_action_execute_gate(**payload)


def test_import_and_schema_default_blocks_without_execution():
    result = build_self_build_one_action_execute_gate()

    assert result["schema"] == SCHEMA
    assert result["gate_status"] == "blocked"
    assert result["execution_gate_decision"] == "blocked"
    assert result["command_execution_allowed"] is False
    assert result["command_executed"] is False
    assert result["safety"]["commands_executed"] is False


def test_approved_full_chain_arms_gate_without_executing_command():
    result = _build()

    assert result["gate_status"] == "armed"
    assert result["execution_gate_decision"] == "one_action_execution_armed"
    assert result["selected_action"] == ACTION_ID
    assert result["command_to_run"] == _command()
    assert result["command_execution_allowed"] is True
    assert result["command_executed"] is False
    assert result["allowed_paths"] == _allowed_paths()
    assert result["validators"] == _validators()
    assert result["max_repairs"] == 1
    assert result["max_files_changed"] == 3
    assert result["rejection_reasons"] == []
    assert result["safety"]["command_execution_allowed_by_gate"] is True
    assert result["safety"]["commands_executed"] is False
    assert result["safety"]["files_written"] is False
    assert result["safety"]["reports_written"] is False


def test_missing_execute_gate_request_blocks():
    result = _build(execute_gate_request=None)

    assert result["gate_status"] == "blocked"
    assert result["command_execution_allowed"] is False
    assert "execute_gate_request_missing" in result["rejection_reasons"]


def test_wrong_execute_gate_request_mode_blocks():
    result = _build(execute_gate_request=_execute_gate_request(mode="ONE_ACTION_APPLY"))

    assert result["gate_status"] == "blocked"
    assert "execute_gate_request_mode_not_explicit_execute_gate" in result["rejection_reasons"]


def test_missing_approval_token_blocks():
    result = _build(execute_gate_request=_execute_gate_request(approval_token_present=False))

    assert result["gate_status"] == "blocked"
    assert "execute_gate_request_approval_token_missing" in result["rejection_reasons"]


def test_rejected_approval_blocks():
    result = _build(apply_approval=_approval(approval_status="rejected"))

    assert result["gate_status"] == "blocked"
    assert "apply_approval_not_approved" in result["rejection_reasons"]


def test_bridge_not_ready_blocks():
    result = _build(local_apply_executor_bridge=_bridge(bridge_status="blocked"))

    assert result["gate_status"] == "blocked"
    assert "local_apply_bridge_not_ready" in result["rejection_reasons"]


def test_single_action_executor_not_ready_blocks():
    result = _build(single_action_executor=_executor(executor_status="blocked"))

    assert result["gate_status"] == "blocked"
    assert "single_action_executor_not_ready" in result["rejection_reasons"]


def test_controller_not_ready_blocks():
    result = _build(one_action_execution_controller=_controller(controller_status="blocked"))

    assert result["gate_status"] == "blocked"
    assert "one_action_execution_controller_not_ready" in result["rejection_reasons"]


def test_apply_runner_not_preview_ready_blocks():
    result = _build(one_action_apply_runner=_runner(runner_status="blocked"))

    assert result["gate_status"] == "blocked"
    assert "one_action_apply_runner_not_preview_ready" in result["rejection_reasons"]


def test_command_would_run_false_blocks():
    result = _build(single_action_executor=_executor(command_would_run=False))

    assert result["gate_status"] == "blocked"
    assert "command_would_run_false" in result["rejection_reasons"]


def test_controller_command_execution_allowed_false_blocks():
    result = _build(one_action_execution_controller=_controller(command_execution_allowed=False))

    assert result["gate_status"] == "blocked"
    assert "one_action_execution_controller_not_allowed" in result["rejection_reasons"]


def test_runner_command_execution_allowed_false_blocks():
    result = _build(one_action_apply_runner=_runner(command_execution_allowed=False))

    assert result["gate_status"] == "blocked"
    assert "one_action_apply_runner_not_allowed" in result["rejection_reasons"]


def test_action_mismatch_rejects():
    result = _build(one_action_apply_runner=_runner(selected_action="build_different_item"))

    assert result["gate_status"] == "rejected"
    assert result["command_execution_allowed"] is False
    assert "selected_action_mismatch" in result["rejection_reasons"]


def test_missing_validators_rejects():
    result = _build(
        selected_queue_item=_queue_item(validators=[]),
        local_apply_executor_bridge=_bridge(validators=[]),
        single_action_executor=_executor(validators=[]),
        one_action_execution_controller=_controller(validators=[]),
        one_action_apply_runner=_runner(validators=[]),
    )

    assert result["gate_status"] == "rejected"
    assert result["command_execution_allowed"] is False
    assert "validators_missing" in result["rejection_reasons"]


def test_path_outside_allowed_scope_rejects():
    result = _build(execute_gate_request=_execute_gate_request(requested_write_paths=[*_allowed_paths(), "Reports/outside.md"]))

    assert result["gate_status"] == "rejected"
    assert result["command_execution_allowed"] is False
    assert "requested_paths_outside_allowed_paths" in result["rejection_reasons"]


def test_max_files_changed_above_five_rejects():
    result = _build(one_action_apply_runner=_runner(max_files_changed=6))

    assert result["gate_status"] == "rejected"
    assert result["command_execution_allowed"] is False
    assert "max_files_changed_exceeds_five" in result["rejection_reasons"]


def test_max_repairs_above_one_rejects():
    result = _build(one_action_apply_runner=_runner(max_repairs=2))

    assert result["gate_status"] == "rejected"
    assert result["command_execution_allowed"] is False
    assert "max_repairs_exceeds_one" in result["rejection_reasons"]


def test_protected_git_action_request_rejects():
    result = _build(execute_gate_request=_execute_gate_request(git_push_requested=True))

    assert result["gate_status"] == "rejected"
    assert result["command_executed"] is False
    assert "protected_action_requested" in result["rejection_reasons"]
    assert result["safety"]["protected_action_requested"] is True


def test_broker_live_trading_credentials_request_rejects():
    result = _build(
        execute_gate_request=_execute_gate_request(
            broker=True,
            live_trading=True,
            credentials=True,
            real_orders=True,
            real_webhooks=True,
        )
    )

    assert result["gate_status"] == "rejected"
    assert result["command_execution_allowed"] is False
    assert "protected_action_requested" in result["rejection_reasons"]
    assert result["safety"]["broker"] is False
    assert result["safety"]["live_trading"] is False
    assert result["safety"]["credentials"] is False


def test_scheduler_daemon_worker_dispatch_request_rejects():
    result = _build(
        execute_gate_request=_execute_gate_request(
            scheduler_activation_requested=True,
            daemon_activation_requested=True,
            worker_dispatch_requested=True,
        )
    )

    assert result["gate_status"] == "rejected"
    assert result["command_execution_allowed"] is False
    assert "protected_action_requested" in result["rejection_reasons"]
    assert result["safety"]["scheduler"] is False
    assert result["safety"]["daemon"] is False
    assert result["safety"]["worker_dispatch"] is False


def test_safety_flags_prove_no_execution_or_automation():
    result = _build()
    safety = result["safety"]

    assert result["command_executed"] is False
    assert safety["command_executed"] is False
    assert safety["commands_executed"] is False
    assert safety["files_written"] is False
    assert safety["reports_written"] is False
    assert safety["git_add"] is False
    assert safety["git_commit"] is False
    assert safety["git_push"] is False
    assert safety["merge"] is False
    assert safety["network_access"] is False
    assert safety["broker"] is False


def test_verifier_failed_rejects():
    result = _build(apply_result_verifier=_verifier(verifier_status="failed", rejection_reasons=["unexpected_files"]))

    assert result["gate_status"] == "rejected"
    assert "apply_result_verifier_failed" in result["rejection_reasons"]


def test_execute_gate_source_has_no_command_or_file_side_effect_apis():
    source = Path("automation/orchestration/aios_self_build_one_action_execute_gate.py").read_text()

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
