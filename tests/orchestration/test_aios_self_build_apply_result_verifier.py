from __future__ import annotations

from pathlib import Path

from automation.orchestration.aios_self_build_apply_result_verifier import (
    SCHEMA,
    build_self_build_apply_result_verifier,
)


def _allowed_paths():
    return [
        "automation/orchestration/aios_self_build_apply_result_verifier.py",
        "tests/orchestration/test_aios_self_build_apply_result_verifier.py",
        "docs/orchestration/AIOS_SELF_BUILD_APPLY_RESULT_VERIFIER.md",
    ]


def _queue_item(**overrides):
    item = {
        "schema": "AIOS_SELF_BUILD_WORK_QUEUE_ITEM.v1",
        "action_id": "build_self_build_apply_result_verifier",
        "allowed_paths": _allowed_paths(),
        "validators": [
            "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_self_build_apply_result_verifier.py",
        ],
    }
    item.update(overrides)
    return item


def _executor(**overrides):
    executor = {
        "schema": "AIOS_SELF_BUILD_SINGLE_ACTION_EXECUTOR.v1",
        "selected_action": "build_self_build_apply_result_verifier",
        "command_would_run": True,
        "command_executed": True,
        "allowed_paths": _allowed_paths(),
        "max_files_changed": 3,
    }
    executor.update(overrides)
    return executor


def _validators(*, passed: bool = True):
    return [
        {
            "name": "pytest",
            "command": "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_self_build_apply_result_verifier.py",
            "returncode": 0 if passed else 1,
            "passed": passed,
        }
    ]


def test_import_and_schema():
    result = build_self_build_apply_result_verifier()

    assert result["schema"] == SCHEMA
    assert result["verifier_status"] == "blocked"
    assert result["safety"]["commands_executed"] is False


def test_blocks_when_command_not_executed():
    result = build_self_build_apply_result_verifier(
        _queue_item(),
        _executor(command_executed=False),
        "",
        " M automation/orchestration/aios_self_build_apply_result_verifier.py",
        _validators(),
        _allowed_paths(),
        3,
    )

    assert result["verifier_status"] == "blocked"
    assert "command_not_executed" in result["rejection_reasons"]
    assert result["result_safe_to_package"] is False


def test_passes_when_changed_files_are_allowed_and_validators_pass():
    result = build_self_build_apply_result_verifier(
        _queue_item(),
        _executor(),
        "",
        "\n".join(
            [
                " M automation/orchestration/aios_self_build_apply_result_verifier.py",
                "?? tests/orchestration/test_aios_self_build_apply_result_verifier.py",
                "?? docs/orchestration/AIOS_SELF_BUILD_APPLY_RESULT_VERIFIER.md",
            ]
        ),
        _validators(),
        _allowed_paths(),
        3,
    )

    assert result["verifier_status"] == "passed"
    assert result["changed_files"] == sorted(_allowed_paths())
    assert result["unexpected_files"] == []
    assert result["validators_passed"] == 1
    assert result["validators_failed"] == 0
    assert result["file_count_ok"] is True
    assert result["allowed_paths_ok"] is True
    assert result["result_safe_to_report"] is True
    assert result["result_safe_to_package"] is True


def test_fails_for_unexpected_files():
    result = build_self_build_apply_result_verifier(
        _queue_item(),
        _executor(),
        "",
        " M automation/orchestration/outside_scope.py",
        _validators(),
        _allowed_paths(),
        3,
    )

    assert result["verifier_status"] == "failed"
    assert result["unexpected_files"] == ["automation/orchestration/outside_scope.py"]
    assert "unexpected_files_outside_allowed_paths" in result["rejection_reasons"]


def test_fails_when_file_count_exceeds_limit():
    result = build_self_build_apply_result_verifier(
        _queue_item(),
        _executor(),
        "",
        "\n".join(f" M {path}" for path in _allowed_paths()),
        _validators(),
        _allowed_paths(),
        2,
    )

    assert result["verifier_status"] == "failed"
    assert result["file_count_ok"] is False
    assert "max_files_changed_exceeded" in result["rejection_reasons"]


def test_fails_when_validator_fails():
    result = build_self_build_apply_result_verifier(
        _queue_item(),
        _executor(),
        "",
        " M automation/orchestration/aios_self_build_apply_result_verifier.py",
        _validators(passed=False),
        _allowed_paths(),
        3,
    )

    assert result["verifier_status"] == "failed"
    assert result["validators_passed"] == 0
    assert result["validators_failed"] == 1
    assert "validators_failed" in result["rejection_reasons"]


def test_fails_when_validators_are_missing():
    result = build_self_build_apply_result_verifier(
        _queue_item(),
        _executor(),
        "",
        " M automation/orchestration/aios_self_build_apply_result_verifier.py",
        [],
        _allowed_paths(),
        3,
    )

    assert result["verifier_status"] == "failed"
    assert result["validators"] == []
    assert "validators_missing" in result["rejection_reasons"]


def test_subtracts_before_status_from_after_status():
    result = build_self_build_apply_result_verifier(
        _queue_item(),
        _executor(),
        "?? Reports/sandbox/",
        "\n".join(
            [
                "?? Reports/sandbox/",
                " M automation/orchestration/aios_self_build_apply_result_verifier.py",
            ]
        ),
        _validators(),
        _allowed_paths(),
        3,
    )

    assert result["changed_files"] == ["automation/orchestration/aios_self_build_apply_result_verifier.py"]
    assert result["verifier_status"] == "passed"


def test_sandbox_1312_is_runner_blocker_not_code_failure():
    result = build_self_build_apply_result_verifier(
        _queue_item(),
        _executor(command_executed=False),
        "",
        "",
        [{"name": "pytest", "stderr": "CreateProcessAsUserW failed: 1312"}],
        _allowed_paths(),
        3,
    )

    assert result["verifier_status"] == "blocked"
    assert result["safety"]["sandbox_1312_blocker"] is True
    assert "sandbox_1312_runner_blocker" in result["rejection_reasons"]
    assert "not a code failure" in result["next_safe_action"]


def test_module_has_no_command_network_or_file_write_usage():
    source = Path("automation/orchestration/aios_self_build_apply_result_verifier.py").read_text()

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
