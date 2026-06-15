from __future__ import annotations

from pathlib import Path

from automation.orchestration.aios_self_build_one_action_local_apply_executor import (
    DEFAULT_WORKING_DIRECTORY,
    LOCAL_EXECUTOR_MODE,
    ONE_ACTION_APPLY_MODE,
    SCHEMA,
    build_self_build_one_action_local_apply_executor,
)


ACTION_ID = "build_self_build_one_action_local_apply_executor"


def _allowed_paths():
    return [
        "automation/orchestration/aios_self_build_one_action_local_apply_executor.py",
        "tests/orchestration/test_aios_self_build_one_action_local_apply_executor.py",
        "docs/orchestration/AIOS_SELF_BUILD_ONE_ACTION_LOCAL_APPLY_EXECUTOR.md",
    ]


def _validators():
    return [
        "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_self_build_one_action_local_apply_executor.py",
    ]


def _command():
    return (
        "python automation/orchestration/aios_productive_bounded_executor.py "
        "--goal self-build-core --action build_self_build_one_action_local_apply_executor --apply --max-repairs 1"
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
        "safety": {"commands_executed": False, "files_written": False, "reports_written": False},
    }
    runner.update(overrides)
    return runner


def _gate(**overrides):
    gate = {
        "schema": "AIOS_SELF_BUILD_ONE_ACTION_EXECUTE_GATE.v1",
        "gate_status": "armed",
        "execution_gate_decision": "one_action_execution_armed",
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
        "safety": {"commands_executed": False, "command_executed": False},
    }
    gate.update(overrides)
    return gate


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


def _local_executor_request(**overrides):
    request = {
        "requested": True,
        "mode": LOCAL_EXECUTOR_MODE,
        "requested_action": ACTION_ID,
        "approved_by": "Anthony Meza",
        "approval_token_present": True,
        "requested_write_paths": _allowed_paths(),
    }
    request.update(overrides)
    return request


def _options(**overrides):
    options = {"execute": False}
    options.update(overrides)
    return options


def _build(command_runner=None, **overrides):
    payload = {
        "selected_queue_item": _queue_item(),
        "apply_approval": _approval(),
        "local_apply_executor_bridge": _bridge(),
        "single_action_executor": _executor(),
        "one_action_execution_controller": _controller(),
        "one_action_apply_runner": _runner(),
        "one_action_execute_gate": _gate(),
        "apply_result_verifier": _verifier(),
        "execution_request": _execution_request(),
        "local_executor_request": _local_executor_request(),
        "executor_options": _options(),
        "command_runner": command_runner,
    }
    payload.update(overrides)
    return build_self_build_one_action_local_apply_executor(**payload)


def test_import_and_required_schema_fields():
    result = build_self_build_one_action_local_apply_executor()

    assert result["schema"] == SCHEMA
    assert set(result) >= {
        "schema",
        "executor_status",
        "executor_mode",
        "selected_action",
        "command_to_run",
        "command_execution_allowed",
        "command_executed",
        "command_returncode",
        "command_stdout_preview",
        "command_stderr_preview",
        "allowed_paths",
        "validators",
        "max_repairs",
        "max_files_changed",
        "pre_execution_checks",
        "post_execution_evidence",
        "rejection_reasons",
        "next_safe_action",
        "safety",
    }
    assert result["executor_status"] == "blocked"
    assert result["command_executed"] is False


def test_safe_approved_chain_with_execute_false_returns_dry_run_ready():
    result = _build()

    assert result["executor_status"] == "dry_run_ready"
    assert result["executor_mode"] == "DRY_RUN"
    assert result["selected_action"] == ACTION_ID
    assert result["command_to_run"] == _command()
    assert result["command_execution_allowed"] is True
    assert result["command_executed"] is False
    assert result["command_returncode"] is None
    assert result["allowed_paths"] == _allowed_paths()
    assert result["validators"] == _validators()
    assert result["max_repairs"] == 1
    assert result["max_files_changed"] == 3
    assert result["rejection_reasons"] == []


def test_default_execute_false_does_not_call_command_runner():
    calls = []

    def fake_runner(command: str, cwd: str):
        calls.append((command, cwd))
        return {"returncode": 0, "stdout": "ok", "stderr": "", "changed_files": []}

    result = _build(command_runner=fake_runner)

    assert result["executor_status"] == "dry_run_ready"
    assert calls == []
    assert result["post_execution_evidence"]["command_runner_called"] is False


def test_execute_true_with_fake_command_runner_returns_executed():
    calls = []

    def fake_runner(command: str, cwd: str):
        calls.append((command, cwd))
        return {
            "returncode": 0,
            "stdout": "ok",
            "stderr": "",
            "changed_files": ["automation/orchestration/aios_self_build_one_action_local_apply_executor.py"],
            "validators_run": _validators(),
        }

    result = _build(command_runner=fake_runner, executor_options=_options(execute=True))

    assert result["executor_status"] == "executed"
    assert result["executor_mode"] == "EXECUTE_ONE_ACTION"
    assert result["command_executed"] is True
    assert result["command_returncode"] == 0
    assert calls == [(_command(), DEFAULT_WORKING_DIRECTORY)]
    assert result["post_execution_evidence"]["command_runner_called"] is True
    assert result["post_execution_evidence"]["changed_files"] == [
        "automation/orchestration/aios_self_build_one_action_local_apply_executor.py",
    ]


def test_execute_true_without_command_runner_returns_blocked():
    result = _build(executor_options=_options(execute=True))

    assert result["executor_status"] == "blocked"
    assert result["executor_mode"] == "EXECUTE_ONE_ACTION"
    assert result["command_executed"] is False
    assert "command_runner_missing_for_execution" in result["rejection_reasons"]


def test_command_executed_false_in_dry_run():
    result = _build()

    assert result["command_executed"] is False
    assert result["safety"]["commands_executed"] is False


def test_command_executed_true_only_through_fake_command_runner():
    def fake_runner(_command: str, _cwd: str):
        return {"returncode": 0, "stdout": "", "stderr": "", "changed_files": []}

    dry_run = _build(command_runner=fake_runner)
    executed = _build(command_runner=fake_runner, executor_options=_options(execute=True))

    assert dry_run["command_executed"] is False
    assert executed["command_executed"] is True


def test_missing_local_executor_request_returns_blocked():
    result = _build(local_executor_request=None)

    assert result["executor_status"] == "blocked"
    assert "local_executor_request_missing" in result["rejection_reasons"]


def test_wrong_local_executor_request_mode_returns_blocked():
    result = _build(local_executor_request=_local_executor_request(mode="DRY_RUN"))

    assert result["executor_status"] == "blocked"
    assert "local_executor_request_mode_not_one_action_local_apply_executor" in result["rejection_reasons"]


def test_missing_approval_token_returns_blocked():
    result = _build(local_executor_request=_local_executor_request(approval_token_present=False))

    assert result["executor_status"] == "blocked"
    assert "local_executor_request_approval_token_missing" in result["rejection_reasons"]


def test_rejected_approval_returns_blocked():
    result = _build(apply_approval=_approval(approval_status="rejected"))

    assert result["executor_status"] == "blocked"
    assert "apply_approval_not_approved" in result["rejection_reasons"]


def test_bridge_not_ready_returns_blocked():
    result = _build(local_apply_executor_bridge=_bridge(bridge_status="blocked"))

    assert result["executor_status"] == "blocked"
    assert "local_apply_bridge_not_ready" in result["rejection_reasons"]


def test_single_action_executor_not_ready_returns_blocked():
    result = _build(single_action_executor=_executor(executor_status="blocked"))

    assert result["executor_status"] == "blocked"
    assert "single_action_executor_not_ready" in result["rejection_reasons"]


def test_one_action_execution_controller_not_ready_returns_blocked():
    result = _build(one_action_execution_controller=_controller(controller_status="blocked"))

    assert result["executor_status"] == "blocked"
    assert "one_action_execution_controller_not_ready" in result["rejection_reasons"]


def test_one_action_apply_runner_not_preview_ready_returns_blocked():
    result = _build(one_action_apply_runner=_runner(runner_status="blocked"))

    assert result["executor_status"] == "blocked"
    assert "one_action_apply_runner_not_preview_ready" in result["rejection_reasons"]


def test_execute_gate_not_armed_returns_blocked():
    result = _build(one_action_execute_gate=_gate(gate_status="blocked"))

    assert result["executor_status"] == "blocked"
    assert "one_action_execute_gate_not_armed" in result["rejection_reasons"]


def test_command_execution_allowed_false_returns_blocked():
    result = _build(one_action_execute_gate=_gate(command_execution_allowed=False))

    assert result["executor_status"] == "blocked"
    assert "one_action_execute_gate_not_allowed" in result["rejection_reasons"]


def test_action_mismatch_returns_rejected():
    result = _build(one_action_apply_runner=_runner(selected_action="build_different_item"))

    assert result["executor_status"] == "rejected"
    assert "selected_action_mismatch" in result["rejection_reasons"]


def test_missing_validators_returns_rejected():
    result = _build(
        selected_queue_item=_queue_item(validators=[]),
        local_apply_executor_bridge=_bridge(validators=[]),
        single_action_executor=_executor(validators=[]),
        one_action_execution_controller=_controller(validators=[]),
        one_action_apply_runner=_runner(validators=[]),
        one_action_execute_gate=_gate(validators=[]),
    )

    assert result["executor_status"] == "rejected"
    assert "validators_missing" in result["rejection_reasons"]


def test_path_outside_allowed_scope_returns_rejected():
    result = _build(local_executor_request=_local_executor_request(requested_write_paths=[*_allowed_paths(), "Reports/outside.md"]))

    assert result["executor_status"] == "rejected"
    assert "requested_paths_outside_allowed_paths" in result["rejection_reasons"]


def test_max_files_changed_above_five_returns_rejected():
    result = _build(one_action_execute_gate=_gate(max_files_changed=6))

    assert result["executor_status"] == "rejected"
    assert "max_files_changed_exceeds_five" in result["rejection_reasons"]


def test_max_repairs_above_one_returns_rejected():
    result = _build(one_action_execute_gate=_gate(max_repairs=2))

    assert result["executor_status"] == "rejected"
    assert "max_repairs_exceeds_one" in result["rejection_reasons"]


def test_protected_git_action_request_returns_rejected():
    result = _build(local_executor_request=_local_executor_request(git_push_requested=True))

    assert result["executor_status"] == "rejected"
    assert "protected_action_requested" in result["rejection_reasons"]


def test_broker_live_trading_credentials_request_returns_rejected():
    result = _build(
        local_executor_request=_local_executor_request(
            broker=True,
            live_trading=True,
            credentials=True,
            real_orders=True,
            real_webhooks=True,
        )
    )

    assert result["executor_status"] == "rejected"
    assert "protected_action_requested" in result["rejection_reasons"]
    assert result["safety"]["broker"] is False
    assert result["safety"]["live_trading"] is False
    assert result["safety"]["credentials"] is False


def test_scheduler_daemon_worker_dispatch_request_returns_rejected():
    result = _build(
        local_executor_request=_local_executor_request(
            scheduler_activation_requested=True,
            daemon_activation_requested=True,
            worker_dispatch_requested=True,
        )
    )

    assert result["executor_status"] == "rejected"
    assert "protected_action_requested" in result["rejection_reasons"]
    assert result["safety"]["scheduler"] is False
    assert result["safety"]["daemon"] is False
    assert result["safety"]["worker_dispatch"] is False


def test_queue_or_approval_mutation_request_returns_rejected():
    result = _build(local_executor_request=_local_executor_request(queue_mutation_requested=True, approval_mutation_requested=True))

    assert result["executor_status"] == "rejected"
    assert "protected_action_requested" in result["rejection_reasons"]


def test_destructive_cleanup_request_returns_rejected():
    result = _build(local_executor_request=_local_executor_request(destructive_cleanup_requested=True))

    assert result["executor_status"] == "rejected"
    assert "protected_action_requested" in result["rejection_reasons"]


def test_fake_command_runner_changed_file_outside_allowed_paths_returns_rejected():
    def fake_runner(_command: str, _cwd: str):
        return {"returncode": 0, "stdout": "ok", "stderr": "", "changed_files": ["Reports/outside.md"]}

    result = _build(command_runner=fake_runner, executor_options=_options(execute=True))

    assert result["executor_status"] == "rejected"
    assert result["command_executed"] is True
    assert "command_runner_changed_files_outside_allowed_paths" in result["rejection_reasons"]


def test_safety_flags_prove_no_external_automation_in_dry_run():
    result = _build()
    safety = result["safety"]

    assert safety["direct_command_runner_used"] is False
    assert safety["commands_executed"] is False
    assert safety["git_add"] is False
    assert safety["git_commit"] is False
    assert safety["git_push"] is False
    assert safety["merge"] is False
    assert safety["reports_written"] is False
    assert safety["broker"] is False
    assert safety["network_access"] is False


def test_stdout_and_stderr_previews_are_bounded():
    def fake_runner(_command: str, _cwd: str):
        return {"returncode": 0, "stdout": "o" * 1000, "stderr": "e" * 1000, "changed_files": []}

    result = _build(command_runner=fake_runner, executor_options=_options(execute=True))

    assert len(result["command_stdout_preview"]) == 400
    assert len(result["command_stderr_preview"]) == 400
    assert len(result["post_execution_evidence"]["stdout_preview"]) == 400
    assert len(result["post_execution_evidence"]["stderr_preview"]) == 400


def test_source_has_no_direct_command_or_file_side_effect_apis():
    source = Path("automation/orchestration/aios_self_build_one_action_local_apply_executor.py").read_text()

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
