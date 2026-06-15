from __future__ import annotations

from pathlib import Path

from automation.orchestration.aios_self_build_local_apply_executor_bridge import (
    SCHEMA,
    build_self_build_local_apply_executor_bridge,
)


def _queue_item(**overrides):
    item = {
        "schema": "AIOS_SELF_BUILD_WORK_QUEUE_ITEM.v1",
        "action_id": "build_self_build_local_apply_executor_bridge",
        "goal": "self-build-core",
        "allowed_paths": [
            "automation/orchestration/aios_self_build_local_apply_executor_bridge.py",
            "tests/orchestration/test_aios_self_build_local_apply_executor_bridge.py",
            "docs/orchestration/AIOS_SELF_BUILD_LOCAL_APPLY_EXECUTOR_BRIDGE.md",
        ],
        "validators": [
            "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_self_build_local_apply_executor_bridge.py",
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


def _local_preview(**overrides):
    preview = {
        "schema": "AIOS_BOUNDED_LOCAL_APPLY_RUNNER.v1",
        "runner_mode": "DRY_RUN",
        "runner_status": "preview_only",
        "command_preview": [
            (
                "python automation/orchestration/aios_productive_bounded_executor.py "
                "--goal self-build-core --action build_self_build_local_apply_executor_bridge --apply --max-repairs 1"
            )
        ],
        "allowed_paths": _queue_item()["allowed_paths"],
        "validators": _queue_item()["validators"],
        "max_repairs": 1,
        "max_files_changed": 3,
        "commands_executed": False,
    }
    preview.update(overrides)
    return preview


def _approval(**overrides):
    approval = {
        "schema": "AIOS_SELF_BUILD_APPLY_APPROVAL_GATE.v1",
        "approval_status": "approved",
        "requested_action": "build_self_build_local_apply_executor_bridge",
        "selected_queue_action": "build_self_build_local_apply_executor_bridge",
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


def _core(**overrides):
    core = {
        "schema": "AIOS_SELF_BUILD_CORE_STATUS_READER.v1",
        "selected_next_action": "build_self_build_local_apply_executor_bridge",
        "can_apply_without_human": False,
    }
    core.update(overrides)
    return core


def test_import_and_schema():
    result = build_self_build_local_apply_executor_bridge({}, {}, {}, {}, {})

    assert result["schema"] == SCHEMA
    assert result["execution_status"] == "prepared_not_executed"
    assert result["safety"]["commands_executed"] is False


def test_ready_when_approved_and_safe():
    result = build_self_build_local_apply_executor_bridge(
        _queue_item(),
        _local_preview(),
        _approval(),
        _core(),
        {},
    )

    assert result["bridge_status"] == "ready"
    assert result["selected_action"] == "build_self_build_local_apply_executor_bridge"
    assert result["working_directory"] == "C:\\Dev\\Ai.Os"
    assert result["command_to_run"].startswith("python automation/orchestration/aios_productive_bounded_executor.py")
    assert result["allowed_paths"] == _queue_item()["allowed_paths"]
    assert result["validators"] == _queue_item()["validators"]
    assert result["max_repairs"] == 1
    assert result["max_files_changed"] == 3
    assert result["approval_status"] == "approved"
    assert result["local_allowlisted_apply_allowed"] is True
    assert result["execution_status"] == "prepared_not_executed"
    assert result["rejection_reasons"] == []
    assert result["safety"]["commands_executed"] is False


def test_blocks_when_approval_not_approved():
    result = build_self_build_local_apply_executor_bridge(
        _queue_item(),
        _local_preview(),
        _approval(approval_status="review_required", local_allowlisted_apply_allowed=False),
        _core(),
        {},
    )

    assert result["bridge_status"] == "blocked"
    assert "apply_approval_not_approved" in result["rejection_reasons"]
    assert "local_allowlisted_apply_not_allowed" in result["rejection_reasons"]


def test_rejects_selected_action_mismatch():
    result = build_self_build_local_apply_executor_bridge(
        _queue_item(),
        _local_preview(),
        _approval(),
        _core(selected_next_action="build_different_item"),
        {},
    )

    assert result["bridge_status"] == "rejected"
    assert "selected_action_mismatch" in result["rejection_reasons"]


def test_rejects_path_outside_allowed_paths():
    result = build_self_build_local_apply_executor_bridge(
        _queue_item(),
        _local_preview(allowed_paths=_queue_item()["allowed_paths"] + ["automation/orchestration/outside_scope.py"]),
        _approval(),
        _core(),
        {},
    )

    assert result["bridge_status"] == "rejected"
    assert "requested_paths_outside_allowed_paths" in result["rejection_reasons"]


def test_rejects_missing_validators():
    result = build_self_build_local_apply_executor_bridge(
        _queue_item(validators=[]),
        _local_preview(validators=[]),
        _approval(),
        _core(),
        {},
    )

    assert result["bridge_status"] == "rejected"
    assert "validators_missing" in result["rejection_reasons"]


def test_rejects_protected_action_request():
    result = build_self_build_local_apply_executor_bridge(
        _queue_item(protected_action_flags={"git_commit": True}),
        _local_preview(),
        _approval(),
        _core(),
        {},
    )

    assert result["bridge_status"] == "rejected"
    assert "protected_action_requested" in result["rejection_reasons"]
    assert result["safety"]["protected_action_requested"] is True


def test_sandbox_1312_is_runner_blocker_not_code_failure():
    result = build_self_build_local_apply_executor_bridge(
        _queue_item(),
        _local_preview(),
        _approval(),
        _core(),
        {"stderr": "windows sandbox: runner error: CreateProcessAsUserW failed: 1312"},
    )

    assert result["bridge_status"] == "blocked"
    assert "sandbox_1312_runner_blocker" in result["rejection_reasons"]
    assert result["safety"]["sandbox_1312_blocker"] is True
    assert "not a code failure" in result["next_safe_action"]


def test_module_has_no_command_network_or_file_write_usage():
    source = Path("automation/orchestration/aios_self_build_local_apply_executor_bridge.py").read_text()

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
