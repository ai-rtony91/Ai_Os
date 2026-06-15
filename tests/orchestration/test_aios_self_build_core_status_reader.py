from __future__ import annotations

from pathlib import Path

from automation.orchestration.aios_self_build_core_status_reader import (
    SCHEMA,
    read_self_build_core_status,
)


def _queue_item(**overrides):
    item = {
        "schema": "AIOS_SELF_BUILD_WORK_QUEUE_ITEM.v1",
        "priority": 10,
        "mode": "platform",
        "goal": "self-build-core",
        "action_id": "build_self_build_core_status_reader",
        "allowed_paths": [
            "automation/orchestration/aios_self_build_core_status_reader.py",
            "tests/orchestration/test_aios_self_build_core_status_reader.py",
            "docs/orchestration/AIOS_SELF_BUILD_CORE_STATUS_READER.md",
        ],
        "validators": [
            "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_self_build_core_status_reader.py",
        ],
        "protected_action_flags": {
            "git_add": False,
            "git_commit": False,
            "git_push": False,
            "merge": False,
        },
        "status": "ready",
    }
    item.update(overrides)
    return item


def test_import_and_schema():
    status = read_self_build_core_status({})

    assert status["schema"] == SCHEMA
    assert status["can_apply_without_human"] is False
    assert status["protected_actions_blocked"]["git_commit"] is True


def test_review_required_is_not_failure():
    readiness = {
        "schema": "AIOS_SELF_BUILD_LOOP_READINESS.v1",
        "readiness_status": "review_required",
        "current_goal": "forex-paper-bot",
        "tests_passed_count": 12,
        "next_safe_action": "Stop for Anthony self-build readiness review.",
    }

    status = read_self_build_core_status(self_build_loop_readiness=readiness)

    assert status["readiness_status"] == "review_required"
    assert status["tests_passed_count"] == 12
    assert status["sos_required"] is False
    assert status["wake_anthony"] is False
    assert status["can_continue_preview"] is False
    assert "not a code failure" in status["next_safe_action"]


def test_preview_can_continue_only_for_bounded_dry_run_queue_item():
    item = _queue_item()
    selector = {
        "schema": "AIOS_NEXT_ACTION_SELECTOR.v1",
        "selector_status": "selected",
        "selected_queue_item": item,
        "selected_next_action": item["action_id"],
        "reason_code": "selected_bounded_dry_run_action",
    }
    packet = {
        "schema": "AIOS_CODEX_PACKET_FROM_QUEUE.v1",
        "packet_ready": True,
    }
    local_preview = {
        "schema": "AIOS_BOUNDED_LOCAL_APPLY_RUNNER.v1",
        "runner_mode": "DRY_RUN",
        "runner_status": "preview_only",
        "command_preview": ["python automation/orchestration/aios_productive_bounded_executor.py --preview"],
        "commands_executed": False,
    }

    status = read_self_build_core_status(
        self_build_loop_readiness={"readiness_status": "ready", "current_goal": "forex-paper-bot"},
        selector=selector,
        codex_packet_preview=packet,
        local_apply_preview=local_preview,
    )

    assert status["selected_next_action"] == "build_self_build_core_status_reader"
    assert status["selected_queue_item"]["action_id"] == "build_self_build_core_status_reader"
    assert status["packet_ready"] is True
    assert status["local_apply_preview_ready"] is True
    assert status["can_continue_preview"] is True
    assert status["can_apply_without_human"] is False


def test_sandbox_1312_is_blocker_not_code_failure():
    driver = {
        "schema": "AIOS_SELF_BUILD_DRY_RUN_DRIVER.v1",
        "driver_mode": "DRY_RUN",
        "wake_validation_passed": False,
        "stderr": "windows sandbox: runner error: CreateProcessAsUserW failed: 1312",
        "sos": {
            "schema": "AIOS_SOS_WAKE_POLICY.v1",
            "sos_required": False,
            "wake_anthony": False,
            "triggers": ["sandbox_1312_blocker"],
        },
    }

    status = read_self_build_core_status(driver)

    assert status["stop_reason"] == "sandbox_1312_blocker"
    assert status["sos_required"] is False
    assert status["wake_anthony"] is False
    assert status["safety"]["sandbox_1312_blocker"] is True
    assert "not a code failure" in status["next_safe_action"]


def test_protected_action_attempt_is_unsafe():
    status = read_self_build_core_status({"git_commit_attempted": True})

    assert status["sos_required"] is True
    assert status["wake_anthony"] is True
    assert status["safety"]["git_commit"] is True
    assert status["safety"]["protected_action_attempt"] is True
    assert status["can_continue_preview"] is False
    assert status["stop_reason"] == "protected_action_attempt"


def test_protected_queue_item_cannot_continue_preview():
    item = _queue_item(protected_action_flags={"git_push": True})
    selector = {
        "schema": "AIOS_NEXT_ACTION_SELECTOR.v1",
        "selector_status": "selected",
        "selected_queue_item": item,
        "selected_next_action": item["action_id"],
    }

    status = read_self_build_core_status(selector=selector)

    assert status["sos_required"] is True
    assert status["can_continue_preview"] is False
    assert status["safety"]["protected_action_attempt"] is True


def test_counts_wake_validator_passes():
    wake = {
        "schema": "AIOS_WAKE_CONTINUE.v1",
        "goal": "forex-paper-bot",
        "result": "REVIEW_REQUIRED",
        "validators_run": [
            {"passed": True, "stdout": "7 passed in 0.12s"},
            {"passed": True, "stdout": "1 passed"},
        ],
    }

    status = read_self_build_core_status(wake)

    assert status["wake_validation_passed"] is True
    assert status["tests_passed_count"] == 8
    assert status["current_goal"] == "forex-paper-bot"


def test_module_has_no_command_network_or_file_write_usage():
    source = Path("automation/orchestration/aios_self_build_core_status_reader.py").read_text()

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
