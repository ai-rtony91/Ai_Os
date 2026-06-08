from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from automation.operator_relief.pi_yubikey_approval_station import (
    DECISION_APPROVE_CONTINUE,
    DECISION_DENY_STOP,
    DECISION_EXPIRE_REQUEST,
    DECISION_HOLD_FOR_REVIEW,
    MODE_DRY_RUN,
    MODE_HARDWARE_FIDO2,
    MODE_SIMULATED_TOUCH,
    build_yubikey_approval_report,
    write_report,
)


NOW = datetime(2026, 6, 7, 12, 0, tzinfo=timezone.utc)


def _report(
    decision: str = DECISION_APPROVE_CONTINUE,
    mode: str = MODE_DRY_RUN,
    protected_paths: list[str] | None = None,
    expires_minutes: int = 15,
    yubikey_present: bool | None = None,
    yubikey_touch_verified: bool | None = None,
) -> dict:
    return build_yubikey_approval_report(
        task_id="TEST001",
        decision=decision,
        mode=mode,
        requested_action="run bounded approval test",
        protected_paths=protected_paths,
        expires_minutes=expires_minutes,
        now=NOW,
        yubikey_present=yubikey_present,
        yubikey_touch_verified=yubikey_touch_verified,
    ).to_dict()


def test_approval_is_not_granted_in_dry_run_even_when_decision_approves() -> None:
    report = _report(DECISION_APPROVE_CONTINUE, MODE_DRY_RUN)

    assert report["approval_granted"] is False
    assert report["yubikey_touch_required"] is True
    assert report["executable"] is False


def test_approval_is_granted_in_simulated_touch_only_with_approve_continue() -> None:
    approve = _report(DECISION_APPROVE_CONTINUE, MODE_SIMULATED_TOUCH)
    hold = _report(DECISION_HOLD_FOR_REVIEW, MODE_SIMULATED_TOUCH)

    assert approve["approval_granted"] is True
    assert approve["yubikey_present"] is True
    assert approve["yubikey_touch_verified"] is True
    assert hold["approval_granted"] is False


def test_deny_stop_sets_approval_denied() -> None:
    report = _report(DECISION_DENY_STOP, MODE_SIMULATED_TOUCH)

    assert report["approval_denied"] is True
    assert report["approval_granted"] is False


def test_hold_for_review_sets_hold_for_review() -> None:
    report = _report(DECISION_HOLD_FOR_REVIEW, MODE_SIMULATED_TOUCH)

    assert report["hold_for_review"] is True
    assert report["approval_granted"] is False


def test_present_alone_does_not_grant_approval() -> None:
    report = _report(
        DECISION_APPROVE_CONTINUE,
        MODE_HARDWARE_FIDO2,
        yubikey_present=True,
        yubikey_touch_verified=False,
    )

    assert report["yubikey_present"] is True
    assert report["yubikey_touch_verified"] is False
    assert report["approval_granted"] is False
    assert any("presence alone is not approval" in reason for reason in report["blocked_reasons"])


def test_protected_path_sets_protected_review_required() -> None:
    report = _report(
        DECISION_HOLD_FOR_REVIEW,
        MODE_SIMULATED_TOUCH,
        protected_paths=["docs/governance/FILE_PLACEMENT_RULES.md"],
    )

    assert report["protected_review_required"] is True
    assert report["protected_paths"] == ["docs/governance/FILE_PLACEMENT_RULES.md"]
    assert report["safety"]["protected_mutation_authorized"] is False


def test_expired_request_blocks_approval() -> None:
    report = _report(DECISION_APPROVE_CONTINUE, MODE_SIMULATED_TOUCH, expires_minutes=0)

    assert report["expired"] is True
    assert report["approval_granted"] is False
    assert "Approval request is expired." in report["blocked_reasons"]


def test_expire_request_decision_marks_expired() -> None:
    report = _report(DECISION_EXPIRE_REQUEST, MODE_SIMULATED_TOUCH)

    assert report["expired"] is True
    assert report["approval_granted"] is False


def test_report_writes_only_under_reports_operator_relief_approvals(tmp_path: Path) -> None:
    result = build_yubikey_approval_report(
        task_id="TEST001",
        decision=DECISION_APPROVE_CONTINUE,
        mode=MODE_SIMULATED_TOUCH,
        now=NOW,
    )

    written = write_report(result, tmp_path)
    payload = json.loads(written.read_text(encoding="utf-8"))

    assert written.parent == tmp_path / "Reports/operator_relief/approvals"
    assert written.name.startswith("yubikey_approval_TEST001_")
    assert payload["task_id"] == "TEST001"
    assert payload["approval_granted"] is True


def test_executable_false() -> None:
    report = _report(DECISION_APPROVE_CONTINUE, MODE_SIMULATED_TOUCH)

    assert report["executable"] is False
    assert report["safety"]["executable"] is False


def test_safety_booleans_all_false_for_protected_actions_and_live_risks() -> None:
    safety = _report(DECISION_APPROVE_CONTINUE, MODE_SIMULATED_TOUCH)["safety"]

    for key in (
        "commit_authorized",
        "push_authorized",
        "merge_authorized",
        "protected_mutation_authorized",
        "cleanup_authorized",
        "live_trading_authorized",
        "broker_api_authorized",
        "secrets_authorized",
        "source_files_mutated",
    ):
        assert safety[key] is False


def test_hardware_fido2_placeholder_is_safe_without_hardware() -> None:
    report = _report(DECISION_APPROVE_CONTINUE, MODE_HARDWARE_FIDO2)

    assert report["approval_granted"] is False
    assert any("physical challenge is not implemented or available" in reason for reason in report["blocked_reasons"])


def test_source_scan_proves_no_forbidden_execution_paths() -> None:
    source = Path("automation/operator_relief/pi_yubikey_approval_station.py").read_text(encoding="utf-8")
    forbidden_markers = [
        "subprocess",
        "os.system",
        "Popen",
        "shutil.rmtree",
        "shutil.move",
        ".rename(",
        "Path.unlink",
        "os.remove",
        "git commit",
        "git push",
        "git merge",
        "git rebase",
        "force-push",
        "OpenAI(",
        "openai.",
        "Codex(",
        "Start-Process",
        "watchdog",
        "HTTPServer",
        "TCPServer",
        ".listen(",
        ".bind(",
        "socket.",
        "daemon",
        "service",
    ]
    assert not any(marker in source for marker in forbidden_markers)
