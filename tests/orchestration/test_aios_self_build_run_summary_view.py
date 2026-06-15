from __future__ import annotations

from pathlib import Path

from automation.orchestration.aios_self_build_run_summary_view import (
    SCHEMA,
    build_self_build_run_summary_view,
)


def _core_status(**overrides):
    status = {
        "schema": "AIOS_SELF_BUILD_CORE_STATUS_READER.v1",
        "current_goal": "forex-paper-bot",
        "current_mode": "platform",
        "wake_validation_passed": True,
        "tests_passed_count": 17,
        "readiness_status": "ready",
        "selected_next_action": "build_self_build_run_summary_view",
        "selected_queue_item": {"action_id": "build_self_build_run_summary_view"},
        "packet_ready": True,
        "local_apply_preview_ready": True,
        "stop_reason": "none",
        "sos_required": False,
        "wake_anthony": False,
        "protected_actions_blocked": {
            "git_add": True,
            "git_commit": True,
            "git_push": True,
            "merge": True,
            "scheduler_activation": True,
            "daemon_activation": True,
            "worker_dispatch": True,
            "queue_mutation": True,
            "approval_mutation": True,
            "broker_live_trading": True,
            "credentials": True,
            "real_orders": True,
            "real_webhooks": True,
            "destructive_cleanup": True,
        },
        "can_continue_preview": True,
        "can_apply_without_human": False,
        "next_safe_action": "Continue preview only for the selected bounded DRY_RUN queue item.",
        "safety": {
            "command_execution": False,
            "network_access": False,
            "broker": False,
            "live_trading": False,
            "credentials": False,
        },
    }
    status.update(overrides)
    return status


def test_import_and_schema():
    summary = build_self_build_run_summary_view({})

    assert summary["schema"] == SCHEMA
    assert summary["can_apply_without_human"] is False
    assert summary["protected_actions_summary"]["all_protected_actions_blocked"] is True


def test_builds_compact_preview_ready_summary_from_core_status():
    summary = build_self_build_run_summary_view({"core_status": _core_status()})

    assert summary["headline"] == "AIOS self-build preview ready"
    assert summary["current_goal"] == "forex-paper-bot"
    assert summary["selected_next_action"] == "build_self_build_run_summary_view"
    assert summary["readiness_status"] == "ready"
    assert summary["tests_passed_count"] == 17
    assert summary["packet_ready"] is True
    assert summary["local_apply_preview_ready"] is True
    assert summary["can_continue_preview"] is True
    assert summary["can_apply_without_human"] is False


def test_review_required_is_not_failure():
    summary = build_self_build_run_summary_view(
        _core_status(
            readiness_status="review_required",
            can_continue_preview=False,
            stop_reason="review_required",
        )
    )

    assert summary["headline"] == "AIOS self-build review required"
    assert summary["sos_required"] is False
    assert summary["wake_anthony"] is False
    assert "not a code failure" in summary["next_safe_action"]


def test_sandbox_1312_is_runner_blocker_not_code_failure():
    summary = build_self_build_run_summary_view(
        {
            "core_status": _core_status(can_continue_preview=False),
            "stderr": "windows sandbox: runner error: CreateProcessAsUserW failed: 1312",
        }
    )

    assert summary["headline"] == "AIOS self-build blocked by local runner sandbox"
    assert summary["stop_reason"] == "sandbox_1312_blocker"
    assert summary["sos_required"] is False
    assert summary["wake_anthony"] is False
    assert summary["safety"]["sandbox_1312_blocker"] is True
    assert "not a code failure" in summary["next_safe_action"]


def test_protected_action_attempt_blocks_preview_and_wakes_anthony():
    summary = build_self_build_run_summary_view(
        {
            "core_status": _core_status(),
            "git_commit_attempted": True,
        }
    )

    assert summary["headline"] == "AIOS self-build stopped: SOS review required"
    assert summary["can_continue_preview"] is False
    assert summary["can_apply_without_human"] is False
    assert summary["sos_required"] is True
    assert summary["wake_anthony"] is True
    assert summary["safety"]["git_commit"] is True
    assert summary["protected_actions_summary"]["protected_action_attempt"] is True


def test_protected_actions_remain_blocked():
    summary = build_self_build_run_summary_view(_core_status())

    assert summary["protected_actions_summary"]["unblocked_actions"] == []
    assert "git_commit" in summary["protected_actions_summary"]["blocked_actions"]
    assert "broker_live_trading" in summary["protected_actions_summary"]["blocked_actions"]


def test_module_has_no_command_network_or_file_write_usage():
    source = Path("automation/orchestration/aios_self_build_run_summary_view.py").read_text()

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
