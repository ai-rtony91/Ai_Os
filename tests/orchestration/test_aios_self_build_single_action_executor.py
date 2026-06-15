from __future__ import annotations

from pathlib import Path

from automation.orchestration.aios_self_build_single_action_executor import (
    SCHEMA,
    build_self_build_single_action_executor,
)


def _queue_item(**overrides):
    item = {
        "schema": "AIOS_SELF_BUILD_WORK_QUEUE_ITEM.v1",
        "action_id": "build_self_build_single_action_executor",
        "allowed_paths": [
            "automation/orchestration/aios_self_build_single_action_executor.py",
            "tests/orchestration/test_aios_self_build_single_action_executor.py",
            "docs/orchestration/AIOS_SELF_BUILD_SINGLE_ACTION_EXECUTOR.md",
        ],
        "validators": [
            "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_self_build_single_action_executor.py",
        ],
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
        "local_allowlisted_apply_allowed": True,
        "can_apply_without_human": False,
        "safety": {"protected_action_requested": False},
    }
    approval.update(overrides)
    return approval


def _bridge(**overrides):
    bridge = {
        "schema": "AIOS_SELF_BUILD_LOCAL_APPLY_EXECUTOR_BRIDGE.v1",
        "bridge_status": "ready",
        "selected_action": "build_self_build_single_action_executor",
        "command_to_run": (
            "python automation/orchestration/aios_productive_bounded_executor.py "
            "--goal self-build-core --action build_self_build_single_action_executor --apply --max-repairs 1"
        ),
        "allowed_paths": _queue_item()["allowed_paths"],
        "validators": _queue_item()["validators"],
        "max_repairs": 1,
        "max_files_changed": 3,
        "execution_status": "prepared_not_executed",
        "safety": {"commands_executed": False},
    }
    bridge.update(overrides)
    return bridge


def _core(**overrides):
    core = {
        "schema": "AIOS_SELF_BUILD_CORE_STATUS_READER.v1",
        "selected_next_action": "build_self_build_single_action_executor",
        "can_apply_without_human": False,
    }
    core.update(overrides)
    return core


def test_import_and_schema():
    result = build_self_build_single_action_executor({}, {}, {}, {}, {})

    assert result["schema"] == SCHEMA
    assert result["command_executed"] is False
    assert result["safety"]["commands_executed"] is False


def test_ready_would_run_when_approved_and_bridge_ready():
    result = build_self_build_single_action_executor(_queue_item(), _approval(), _bridge(), _core(), {})

    assert result["executor_status"] == "ready"
    assert result["execution_mode"] == "APPLY_ALLOWED_NOT_RUN"
    assert result["selected_action"] == "build_self_build_single_action_executor"
    assert result["command_to_run"]
    assert result["command_would_run"] is True
    assert result["command_executed"] is False
    assert result["allowed_paths"] == _queue_item()["allowed_paths"]
    assert result["validators"] == _queue_item()["validators"]
    assert result["max_repairs"] == 1
    assert result["max_files_changed"] == 3
    assert result["approval_status"] == "approved"
    assert result["bridge_status"] == "ready"
    assert result["rejection_reasons"] == []


def test_missing_approval_blocks():
    result = build_self_build_single_action_executor(
        _queue_item(),
        _approval(approval_status="review_required", local_allowlisted_apply_allowed=False),
        _bridge(),
        _core(),
        {},
    )

    assert result["executor_status"] == "blocked"
    assert result["execution_mode"] == "APPLY_PREVIEW"
    assert result["command_would_run"] is False
    assert result["command_executed"] is False
    assert "apply_approval_not_approved" in result["rejection_reasons"]


def test_bridge_not_ready_blocks():
    result = build_self_build_single_action_executor(
        _queue_item(),
        _approval(),
        _bridge(bridge_status="blocked"),
        _core(),
        {},
    )

    assert result["executor_status"] == "blocked"
    assert "local_apply_bridge_not_ready" in result["rejection_reasons"]


def test_selected_action_mismatch_rejects():
    result = build_self_build_single_action_executor(
        _queue_item(),
        _approval(),
        _bridge(selected_action="build_different_item"),
        _core(),
        {},
    )

    assert result["executor_status"] == "rejected"
    assert result["command_would_run"] is False
    assert "selected_action_mismatch" in result["rejection_reasons"]


def test_path_outside_allowed_scope_rejects():
    result = build_self_build_single_action_executor(
        _queue_item(),
        _approval(),
        _bridge(allowed_paths=_queue_item()["allowed_paths"] + ["automation/orchestration/outside_scope.py"]),
        _core(),
        {},
    )

    assert result["executor_status"] == "rejected"
    assert "requested_paths_outside_allowed_scope" in result["rejection_reasons"]


def test_missing_validators_rejects():
    result = build_self_build_single_action_executor(
        _queue_item(validators=[]),
        _approval(),
        _bridge(validators=[]),
        _core(),
        {},
    )

    assert result["executor_status"] == "rejected"
    assert "validators_missing" in result["rejection_reasons"]


def test_protected_action_request_rejects():
    result = build_self_build_single_action_executor(
        _queue_item(protected_action_flags={"git_commit": True}),
        _approval(),
        _bridge(),
        _core(),
        {},
    )

    assert result["executor_status"] == "rejected"
    assert "protected_action_requested" in result["rejection_reasons"]
    assert result["safety"]["protected_action_requested"] is True


def test_sandbox_1312_is_runner_blocker_not_code_failure():
    result = build_self_build_single_action_executor(
        _queue_item(),
        _approval(),
        _bridge(),
        _core(),
        {"stderr": "windows sandbox: runner error: CreateProcessAsUserW failed: 1312"},
    )

    assert result["executor_status"] == "blocked"
    assert result["command_would_run"] is False
    assert result["command_executed"] is False
    assert result["safety"]["sandbox_1312_blocker"] is True
    assert "sandbox_1312_runner_blocker" in result["rejection_reasons"]
    assert "not a code failure" in result["next_safe_action"]


def test_module_has_no_command_network_or_file_write_usage():
    source = Path("automation/orchestration/aios_self_build_single_action_executor.py").read_text()

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
