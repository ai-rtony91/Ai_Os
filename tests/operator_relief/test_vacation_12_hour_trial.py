from __future__ import annotations

from automation.operator_relief.vacation_12_hour_trial import (
    CLASSIFICATION_NON_SOS,
    CLASSIFICATION_OK,
    CLASSIFICATION_SOS,
    ValidatorResult,
    classify_validator_result,
    classify_dirty_scope,
    classify_trial_start,
    is_approved_trial_output,
)


def test_approved_trial_output_paths_are_allowed_dirty_state() -> None:
    status = [
        "## feature/full-operator-relief-closed-loop-v1...origin/feature/full-operator-relief-closed-loop-v1",
        "?? Reports/vacation_candidate/12_hour_trial/",
        "?? telemetry/operator_relief/12_hour_trial/",
    ]

    report = classify_dirty_scope(status)

    assert report.git_clean is False
    assert report.approved_evidence_only is True
    assert report.unauthorized_paths == ()
    assert report.approved_paths == (
        "Reports/vacation_candidate/12_hour_trial",
        "telemetry/operator_relief/12_hour_trial",
    )


def test_trial_start_with_approved_evidence_and_clean_diff_does_not_sos() -> None:
    heartbeat = classify_trial_start(
        status_lines=[
            "?? Reports/vacation_candidate/12_hour_trial/",
            "?? telemetry/operator_relief/12_hour_trial/",
        ],
        diff_check=ValidatorResult("git diff --check", 0),
        branch="feature/full-operator-relief-closed-loop-v1",
    )

    assert heartbeat["classification"] == CLASSIFICATION_NON_SOS
    assert heartbeat["sos_required"] is False
    assert heartbeat["approved_evidence_only"] is True
    assert heartbeat["validator_status"] == "PASS"
    assert heartbeat["do_not_wake_reason"]


def test_git_diff_check_exit_zero_with_empty_output_is_pass() -> None:
    result = classify_validator_result(
        name="git diff --check",
        exit_code=0,
        stdout="",
        stderr="",
    )

    assert result.passed is True
    assert result.output == ""


def test_git_diff_check_exit_zero_with_harmless_stdout_is_pass() -> None:
    result = classify_validator_result(
        name="git diff --check",
        exit_code=0,
        stdout="no whitespace errors",
        stderr="",
    )

    assert result.passed is True
    assert result.output == "no whitespace errors"


def test_git_diff_check_nonzero_exit_is_fail() -> None:
    result = classify_validator_result(
        name="git diff --check",
        exit_code=1,
        stdout="file.py:1: trailing whitespace.",
        stderr="",
    )

    assert result.passed is False


def test_validator_stderr_does_not_override_zero_exit() -> None:
    result = classify_validator_result(
        name="git diff --check",
        exit_code=0,
        stdout="",
        stderr="warning: harmless diagnostic",
    )

    assert result.passed is True
    assert result.stderr == "warning: harmless diagnostic"


def test_validator_wrapper_exception_is_fail() -> None:
    result = classify_validator_result(
        name="git diff --check",
        exit_code=0,
        stdout="",
        stderr="",
        wrapper_error="runner exception",
    )

    assert result.passed is False


def test_clean_trial_start_is_ok() -> None:
    heartbeat = classify_trial_start(
        status_lines=["## feature/full-operator-relief-closed-loop-v1...origin/feature/full-operator-relief-closed-loop-v1"],
        diff_check=ValidatorResult("git diff --check", 0),
        branch="feature/full-operator-relief-closed-loop-v1",
    )

    assert heartbeat["classification"] == CLASSIFICATION_OK
    assert heartbeat["sos_required"] is False
    assert heartbeat["git_clean"] is True


def test_unauthorized_source_dirty_state_stops_trial() -> None:
    heartbeat = classify_trial_start(
        status_lines=[
            "?? Reports/vacation_candidate/12_hour_trial/",
            " M automation/operator_relief/vacation_watchdog.py",
        ],
        diff_check=ValidatorResult("git diff --check", 0),
        branch="feature/full-operator-relief-closed-loop-v1",
    )

    assert heartbeat["classification"] == CLASSIFICATION_SOS
    assert heartbeat["sos_required"] is True
    assert heartbeat["unauthorized_dirty_paths"] == ["automation/operator_relief/vacation_watchdog.py"]


def test_unauthorized_test_dirty_state_stops_trial() -> None:
    heartbeat = classify_trial_start(
        status_lines=[" M tests/operator_relief/test_vacation_watchdog.py"],
        diff_check=ValidatorResult("git diff --check", 0),
        branch="feature/full-operator-relief-closed-loop-v1",
    )

    assert heartbeat["classification"] == CLASSIFICATION_SOS
    assert "dirty branch state outside approved trial evidence only" in heartbeat["sos_findings"]


def test_real_git_diff_check_failure_is_not_suppressed() -> None:
    heartbeat = classify_trial_start(
        status_lines=["?? Reports/vacation_candidate/12_hour_trial/"],
        diff_check=ValidatorResult("git diff --check", 1, output="file.py:1: trailing whitespace."),
        branch="feature/full-operator-relief-closed-loop-v1",
    )

    assert heartbeat["classification"] == CLASSIFICATION_SOS
    assert heartbeat["validator_status"] == "FAIL"
    assert "git diff --check failed" in heartbeat["sos_findings"]


def test_real_git_diff_check_failure_from_classified_result_is_not_suppressed() -> None:
    diff_check = classify_validator_result(
        name="git diff --check",
        exit_code=1,
        stdout="file.py:1: trailing whitespace.",
        stderr="",
    )

    heartbeat = classify_trial_start(
        status_lines=["?? Reports/vacation_candidate/12_hour_trial/"],
        diff_check=diff_check,
        branch="feature/full-operator-relief-closed-loop-v1",
    )

    assert heartbeat["classification"] == CLASSIFICATION_SOS
    assert heartbeat["validator_status"] == "FAIL"


def test_validator_wrapper_error_is_not_suppressed() -> None:
    heartbeat = classify_trial_start(
        status_lines=["?? Reports/vacation_candidate/12_hour_trial/"],
        diff_check=ValidatorResult("git diff --check", 0, wrapper_error="runner failed"),
        branch="feature/full-operator-relief-closed-loop-v1",
    )

    assert heartbeat["classification"] == CLASSIFICATION_SOS
    assert heartbeat["validator_status"] == "FAIL"


def test_branch_mismatch_stops_trial() -> None:
    heartbeat = classify_trial_start(
        status_lines=[],
        diff_check=ValidatorResult("git diff --check", 0),
        branch="main",
    )

    assert heartbeat["classification"] == CLASSIFICATION_SOS
    assert "main branch risk or branch mismatch" in heartbeat["sos_findings"]


def test_path_normalization_accepts_windows_style_approved_paths() -> None:
    assert is_approved_trial_output(r"telemetry\operator_relief\12_hour_trial\trial_status.json")
    assert is_approved_trial_output(r"Reports\vacation_candidate\12_hour_trial\AIOS_12_HOUR_TRIAL_REPORT.md")


def test_rename_status_uses_destination_path_for_scope() -> None:
    report = classify_dirty_scope(
        ["R  old.md -> Reports/vacation_candidate/12_hour_trial/AIOS_12_HOUR_TRIAL_REPORT.md"]
    )

    assert report.approved_evidence_only is True
    assert report.unauthorized_paths == ()
