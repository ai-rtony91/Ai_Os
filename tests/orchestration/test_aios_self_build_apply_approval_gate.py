from __future__ import annotations

from pathlib import Path

from automation.orchestration.aios_self_build_apply_approval_gate import (
    SCHEMA,
    evaluate_apply_approval_gate,
)


def _queue_item(**overrides):
    item = {
        "schema": "AIOS_SELF_BUILD_WORK_QUEUE_ITEM.v1",
        "action_id": "build_self_build_apply_approval_gate",
        "allowed_paths": [
            "automation/orchestration/aios_self_build_apply_approval_gate.py",
            "tests/orchestration/test_aios_self_build_apply_approval_gate.py",
            "docs/orchestration/AIOS_SELF_BUILD_APPLY_APPROVAL_GATE.md",
        ],
        "validators": [
            "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_self_build_apply_approval_gate.py",
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


def _approval_request(**overrides):
    request = {
        "requested_action": "build_self_build_apply_approval_gate",
        "requested_write_paths": [
            "automation/orchestration/aios_self_build_apply_approval_gate.py",
            "tests/orchestration/test_aios_self_build_apply_approval_gate.py",
            "docs/orchestration/AIOS_SELF_BUILD_APPLY_APPROVAL_GATE.md",
        ],
        "approved_by": "Anthony Meza",
        "approval_token_present": True,
    }
    request.update(overrides)
    return request


def test_import_and_schema():
    result = evaluate_apply_approval_gate({}, {})

    assert result["schema"] == SCHEMA
    assert result["can_apply_without_human"] is False
    assert result["protected_actions_blocked"]["git_commit"] is True


def test_approved_local_allowlisted_apply_still_cannot_apply_without_human():
    result = evaluate_apply_approval_gate(_queue_item(), _approval_request())

    assert result["approval_status"] == "approved"
    assert result["approved_by"] == "Anthony Meza"
    assert result["approval_token_present"] is True
    assert result["allowed_paths_match"] is True
    assert result["validators_present"] is True
    assert result["local_allowlisted_apply_allowed"] is True
    assert result["can_apply_without_human"] is False
    assert result["rejection_reasons"] == []


def test_missing_approval_returns_review_required():
    result = evaluate_apply_approval_gate(
        _queue_item(),
        _approval_request(approved_by="", approval_token_present=False),
    )

    assert result["approval_status"] == "review_required"
    assert result["local_allowlisted_apply_allowed"] is False
    assert "approval_token_missing" in result["rejection_reasons"]
    assert "authorized_approver_missing" in result["rejection_reasons"]


def test_protected_action_request_is_rejected():
    result = evaluate_apply_approval_gate(
        _queue_item(),
        _approval_request(git_commit_requested=True),
    )

    assert result["approval_status"] == "rejected"
    assert result["local_allowlisted_apply_allowed"] is False
    assert "protected_action_requested" in result["rejection_reasons"]
    assert result["safety"]["protected_action_requested"] is True


def test_path_outside_allowed_scope_is_rejected():
    result = evaluate_apply_approval_gate(
        _queue_item(),
        _approval_request(requested_write_paths=["automation/orchestration/outside_scope.py"]),
    )

    assert result["approval_status"] == "rejected"
    assert result["allowed_paths_match"] is False
    assert "requested_paths_outside_queue_allowed_paths" in result["rejection_reasons"]


def test_requested_action_mismatch_is_rejected():
    result = evaluate_apply_approval_gate(
        _queue_item(),
        _approval_request(requested_action="build_different_item"),
    )

    assert result["approval_status"] == "rejected"
    assert "requested_action_mismatch" in result["rejection_reasons"]


def test_missing_validators_is_rejected():
    result = evaluate_apply_approval_gate(
        _queue_item(validators=[]),
        _approval_request(),
    )

    assert result["approval_status"] == "rejected"
    assert result["validators_present"] is False
    assert "validators_missing" in result["rejection_reasons"]


def test_sandbox_1312_is_runner_blocker_not_code_failure():
    result = evaluate_apply_approval_gate(
        _queue_item(),
        {
            **_approval_request(approved_by="", approval_token_present=False),
            "stderr": "windows sandbox: runner error: CreateProcessAsUserW failed: 1312",
        },
    )

    assert result["approval_status"] == "review_required"
    assert result["local_allowlisted_apply_allowed"] is False
    assert result["safety"]["sandbox_1312_blocker"] is True
    assert "sandbox_1312_runner_blocker" in result["rejection_reasons"]
    assert "not a code failure" in result["next_safe_action"]


def test_module_has_no_command_network_or_file_write_usage():
    source = Path("automation/orchestration/aios_self_build_apply_approval_gate.py").read_text()

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
