from __future__ import annotations

import re
import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from automation.forex_engine.forex_controlled_micro_live_exception_runner_v1 import (
    CONTROLLED_MICRO_LIVE_EXCEPTION_READY,
    CURRENT_STAGE,
    KILL_SWITCH_BLOCKED,
    LIVE_BOUNDARY_REQUIRED,
    LIVE_RUNTIME_CREDENTIAL_ACCESS_REQUIRED,
    MICRO_LIVE_CONTROL_BLOCKED,
    OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED,
    OWNER_RUNTIME_LIVE_FLAG_REQUIRED,
    PROTECTED_BOUNDARY_VIOLATION,
    SUPERVISED_DEMO_EVIDENCE_REQUIRED,
    ControlledMicroLiveExceptionInput,
    NEXT_STAGE_OWNER_EXECUTE_ONE_CONTROLLED_MICRO_LIVE_ORDER,
    NEXT_STAGE_OWNER_REVIEW_REQUIRED,
    NEXT_STAGE_OWNER_RUN_CONTROLLED_MICRO_LIVE_EXCEPTION,
    NEXT_STAGE_OWNER_UNLOCK_BITWARDEN_LIVE_RUNTIME,
    NEXT_STAGE_REPAIR_LIVE_BOUNDARY,
    NEXT_STAGE_REPAIR_MICRO_LIVE_CONTROLS,
    NEXT_STAGE_STOP_AND_OWNER_REVIEW,
    build_default_input,
    evaluate_controlled_micro_live_exception,
)
from automation.forex_engine.forex_controlled_micro_live_exception_runner_v1 import (
    NEXT_STAGE_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL,
)
from scripts.forex_delivery import run_forex_controlled_micro_live_exception_runner_v1 as runtime_script

START_SESSION_HELPER = Path("scripts/security/Start-AiosBitwardenSession.ps1")
CLEAR_SESSION_HELPER = Path("scripts/security/Clear-AiosBitwardenSession.ps1")
SESSION_HELPER_DOC = Path("docs/security/AIOS_BITWARDEN_RUNTIME_SESSION_HARDENING_V1.md")


def _input(**changes: object) -> ControlledMicroLiveExceptionInput:
    return replace(build_default_input(), **changes)


def _runtime_ready_input(**changes: object) -> ControlledMicroLiveExceptionInput:
    base = {
        "owner_micro_live_exception_approval_granted": True,
        "supervised_demo_evidence_clean": True,
        "live_runtime_owner_flag": True,
        "bw_session_present": True,
        "bitwarden_cli_available": True,
        "bitwarden_item_read_success": True,
        "live_credential_values_available_to_runtime": True,
        "live_endpoint_is_oanda_fxtrade": True,
        "environment_is_live": True,
        "allowed_mode_is_micro_live_only": True,
        "kill_switch_enabled": True,
        "kill_switch_triggered": False,
        "daily_loss_cap_defined": True,
        "daily_loss_within_limit": True,
        "trade_risk_cap_defined": True,
        "proposed_trade_risk_within_limit": True,
        "duplicate_order_guard_enabled": True,
        "duplicate_order_detected": False,
        "audit_log_enabled": True,
        "audit_log_write_success": True,
        "max_one_live_order_enforced": True,
        "micro_size_only": True,
        "stop_loss_defined": True,
        "take_profit_defined": True,
    }
    base.update(changes)
    return _input(**base)



def test_default_returns_owner_runtime_flag_required():
    result = evaluate_controlled_micro_live_exception(_input())
    assert result.micro_live_status == OWNER_RUNTIME_LIVE_FLAG_REQUIRED
    assert result.current_stage == CURRENT_STAGE
    assert result.next_stage == NEXT_STAGE_OWNER_RUN_CONTROLLED_MICRO_LIVE_EXCEPTION


def test_missing_owner_approval_blocks():
    runtime_ready_input = _runtime_ready_input()
    runtime_ready_input = ControlledMicroLiveExceptionInput(
        **{**runtime_ready_input.__dict__, "owner_micro_live_exception_approval_granted": False},
    )
    result = evaluate_controlled_micro_live_exception(runtime_ready_input)
    assert result.micro_live_status == OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED
    assert result.next_stage == NEXT_STAGE_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL
    assert "owner_micro_live_exception_approval_granted is False" in result.blockers


def test_missing_supervised_demo_evidence_blocks():
    result = evaluate_controlled_micro_live_exception(_runtime_ready_input(supervised_demo_evidence_clean=False))
    assert result.micro_live_status == SUPERVISED_DEMO_EVIDENCE_REQUIRED
    assert result.next_stage == "supervised_demo_evidence_review"
    assert "supervised_demo_evidence_clean is False" in result.blockers


def test_protected_boundary_flags_block_in_dry_run():
    for field_name in [
        "broker_api_called",
        "bitwarden_cli_called",
        "credentials_read",
        "env_file_read",
        "live_order_execution",
        "demo_order_execution",
        "money_movement",
        "scheduler_started",
        "daemon_started",
        "webhook_started",
    ]:
        result = evaluate_controlled_micro_live_exception(
            _input(
                owner_micro_live_exception_approval_granted=True,
                live_runtime_owner_flag=False,
                **{field_name: True},
            ),
        )
        assert result.micro_live_status == PROTECTED_BOUNDARY_VIOLATION
        assert result.next_stage == NEXT_STAGE_STOP_AND_OWNER_REVIEW
        assert result.live_order_execution is False
        assert result.money_movement is False
        assert result.scheduler_started is False


def test_missing_runtime_credentials_blocks_owner_mode():
    base = _runtime_ready_input()
    for field_name in [
        "bw_session_present",
        "bitwarden_cli_available",
        "bitwarden_item_read_success",
        "live_credential_values_available_to_runtime",
    ]:
        kwargs = base.__dict__.copy()
        kwargs[field_name] = False
        result = evaluate_controlled_micro_live_exception(ControlledMicroLiveExceptionInput(**kwargs))
        assert result.micro_live_status == LIVE_RUNTIME_CREDENTIAL_ACCESS_REQUIRED
        assert result.next_stage == NEXT_STAGE_OWNER_UNLOCK_BITWARDEN_LIVE_RUNTIME
        assert "owner_" in result.next_stage


def test_non_live_boundary_blocks():
    for field_name in [
        "live_endpoint_is_oanda_fxtrade",
        "environment_is_live",
        "allowed_mode_is_micro_live_only",
    ]:
        result = evaluate_controlled_micro_live_exception(
            _runtime_ready_input(**{field_name: False}),
        )
        assert result.micro_live_status == LIVE_BOUNDARY_REQUIRED
        assert result.next_stage == NEXT_STAGE_REPAIR_LIVE_BOUNDARY


def test_kill_switch_blocks():
    result = evaluate_controlled_micro_live_exception(
        _runtime_ready_input(kill_switch_enabled=False),
    )
    assert result.micro_live_status == KILL_SWITCH_BLOCKED
    assert result.next_stage == NEXT_STAGE_OWNER_REVIEW_REQUIRED

    result = evaluate_controlled_micro_live_exception(
        _runtime_ready_input(kill_switch_triggered=True),
    )
    assert result.micro_live_status == KILL_SWITCH_BLOCKED
    assert result.next_stage == NEXT_STAGE_OWNER_REVIEW_REQUIRED


def test_controls_block_runtime_ready():
    for field_name in [
        "daily_loss_cap_defined",
        "daily_loss_within_limit",
        "trade_risk_cap_defined",
        "proposed_trade_risk_within_limit",
        "duplicate_order_guard_enabled",
        "audit_log_enabled",
        "audit_log_write_success",
        "max_one_live_order_enforced",
        "micro_size_only",
        "stop_loss_defined",
        "take_profit_defined",
    ]:
        kwargs = _runtime_ready_input().__dict__.copy()
        kwargs[field_name] = False
        if field_name == "duplicate_order_guard_enabled":
            kwargs["duplicate_order_detected"] = False
        result = evaluate_controlled_micro_live_exception(
            ControlledMicroLiveExceptionInput(**kwargs),
        )
        assert result.micro_live_status == MICRO_LIVE_CONTROL_BLOCKED
        assert result.next_stage == NEXT_STAGE_REPAIR_MICRO_LIVE_CONTROLS

    result = evaluate_controlled_micro_live_exception(
        _runtime_ready_input(duplicate_order_detected=True),
    )
    assert result.micro_live_status == MICRO_LIVE_CONTROL_BLOCKED
    assert result.next_stage == NEXT_STAGE_REPAIR_MICRO_LIVE_CONTROLS


def test_runtime_ready_status():
    result = evaluate_controlled_micro_live_exception(_runtime_ready_input())
    assert result.micro_live_status == CONTROLLED_MICRO_LIVE_EXCEPTION_READY
    assert result.current_stage == CURRENT_STAGE
    assert result.next_stage == NEXT_STAGE_OWNER_EXECUTE_ONE_CONTROLLED_MICRO_LIVE_ORDER
    assert result.demo_order_execution is False
    assert result.live_order_execution is False
    assert result.money_movement is False
    assert result.scheduler_started is False
    assert result.daemon_started is False
    assert result.webhook_started is False


def test_runtime_ready_requires_live_endpoint():
    result = evaluate_controlled_micro_live_exception(_runtime_ready_input(live_endpoint_is_oanda_fxtrade=False))
    assert result.micro_live_status == LIVE_BOUNDARY_REQUIRED


def test_practice_endpoint_is_rejected(monkeypatch, tmp_path: Path):
    fake_item = {
        "broker_api_token": "token",
        "broker_account_id": "acct",
        "endpoint": "https://api-fxpractice.oanda.com",
        "environment": "live",
        "allowed_mode": "controlled_micro_live_exception_only",
    }

    monkeypatch.setattr(runtime_script.shutil, "which", lambda _: "bw")
    monkeypatch.setattr(runtime_script, "_read_broker_runtime_item", lambda: fake_item)
    monkeypatch.setenv("BW_SESSION", "session-token")
    called = {"count": 0}

    def reject_post_request(request_payload: dict) -> tuple[dict, int, bool]:
        called["count"] += 1
        return {"error": "should_not_call"}, 0, False

    monkeypatch.setattr(runtime_script, "_post_json_request", reject_post_request)
    payload = runtime_script.run_forex_controlled_micro_live_exception_runner_v1(
        owner_approved_controlled_micro_live_exception=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        write_report=True,
    )

    assert called["count"] == 0
    assert payload["runtime_summary"]["order_attempt_requested"] is False
    assert payload["runtime_summary"]["order_attempted"] is False
    assert payload["runtime_summary"]["order_status"] == "not_attempted"


def test_owner_runtime_uses_active_bw_session_for_bitwarden_item_read(
    monkeypatch,
    tmp_path: Path,
) -> None:
    fake_bw_item = json.dumps(
        {
            "fields": [
                {"name": "broker_api_token", "value": "live-token-1"},
                {"name": "broker_account_id", "value": "acct-1"},
                {"name": "endpoint", "value": "https://api-fxtrade.oanda.com"},
                {"name": "environment", "value": "live"},
                {"name": "allowed_mode", "value": "controlled_micro_live_exception_only"},
            ],
        },
    )
    captured: dict[str, object] = {}

    def fake_run(command: list[str], **kwargs: object) -> object:
        captured["command"] = command
        captured["env"] = kwargs.get("env")
        return SimpleNamespace(returncode=0, stdout=fake_bw_item, stderr="")

    monkeypatch.setattr(runtime_script.shutil, "which", lambda _: "bw")
    monkeypatch.setenv("BW_SESSION", "session-token")
    monkeypatch.setattr(runtime_script.subprocess, "run", fake_run)
    monkeypatch.setattr(
        runtime_script,
        "_post_json_request",
        lambda request_payload: ({}, 200, True),
    )

    payload = runtime_script.run_forex_controlled_micro_live_exception_runner_v1(
        owner_approved_controlled_micro_live_exception=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        write_report=True,
    )

    command = captured.get("command")
    env = captured.get("env")
    assert isinstance(command, list)
    assert isinstance(env, dict)
    assert command == [
        "bw",
        "get",
        "item",
        "AIOS / OANDA / Live / Broker Runtime",
        "--session",
        "session-token",
    ]
    assert env.get("BW_SESSION") == "session-token"
    assert payload["input"]["bitwarden_item_read_success"] is True
    assert payload["result"]["micro_live_status"] == CONTROLLED_MICRO_LIVE_EXCEPTION_READY


def test_build_order_payload_emits_market_and_units_orientation():
    buy_input = _runtime_ready_input()
    buy_payload = runtime_script._build_order_payload(buy_input)
    assert buy_payload["order"]["type"] == "MARKET"
    assert int(buy_payload["order"]["units"]) > 0

    sell_input = _runtime_ready_input(side="sell")
    sell_payload = runtime_script._build_order_payload(sell_input)
    assert int(sell_payload["order"]["units"]) < 0

    zero_input = _runtime_ready_input(units=0)
    zero_payload = runtime_script._build_order_payload(zero_input)
    assert zero_payload["order"]["units"] == "1"


def test_report_and_state_do_not_write_raw_runtime_secrets(tmp_path: Path, monkeypatch) -> None:
    fake_item = {
        "broker_api_token": "very-secret-live-token",
        "broker_account_id": "very-secret-account-id",
        "endpoint": "https://api-fxtrade.oanda.com",
        "environment": "live",
        "allowed_mode": "controlled_micro_live_exception_only",
    }

    monkeypatch.setattr(runtime_script.shutil, "which", lambda _: "bw")
    monkeypatch.setenv("BW_SESSION", "session-token")
    monkeypatch.setattr(
        runtime_script,
        "_read_broker_runtime_item",
        lambda: fake_item,
    )
    monkeypatch.setattr(
        runtime_script,
        "_post_json_request",
        lambda request_payload: ({"orderId": "abc"}, 201, True),
    )

    state_path = tmp_path / "state.json"
    report_path = tmp_path / "report.md"
    payload = runtime_script.run_forex_controlled_micro_live_exception_runner_v1(
        owner_approved_controlled_micro_live_exception=True,
        state_output=state_path,
        report_output=report_path,
        write_report=True,
    )

    assert payload["result"]["micro_live_status"] == CONTROLLED_MICRO_LIVE_EXCEPTION_READY
    assert payload["runtime_summary"]["order_attempt_success"] is True

    state_text = state_path.read_text(encoding="utf-8")
    report_text = report_path.read_text(encoding="utf-8")
    state_payload = json.loads(state_text)
    assert "very-secret-live-token" not in state_text
    assert "very-secret-account-id" not in state_text
    assert "very-secret-live-token" not in report_text
    assert "very-secret-account-id" not in report_text
    assert "session-token" not in state_text
    assert "session-token" not in report_text
    assert "Authorization" not in state_text
    assert "Bearer" not in state_text
    assert "Authorization" not in report_text
    assert "Bearer" not in report_text
    assert state_payload["runtime_summary"]["order_endpoint"] == "https://api-fxtrade.oanda.com/v3/accounts/REDACTED_ACCOUNT_ID/orders"


def test_main_outputs_redacted_stdout_payload(monkeypatch, tmp_path: Path, capsys) -> None:
    fake_item = {
        "broker_api_token": "super-secret-live-token",
        "broker_account_id": "super-secret-account-id",
        "endpoint": "https://api-fxtrade.oanda.com",
        "environment": "live",
        "allowed_mode": "controlled_micro_live_exception_only",
    }

    monkeypatch.setattr(runtime_script.shutil, "which", lambda _: "bw")
    monkeypatch.setenv("BW_SESSION", "session-token-must-not-escape")
    monkeypatch.setattr(
        runtime_script,
        "_read_broker_runtime_item",
        lambda: fake_item,
    )
    monkeypatch.setattr(
        runtime_script,
        "_post_json_request",
        lambda request_payload: ({"orderId": "abc"}, 201, True),
    )

    payload = runtime_script.main(
        [
            "--owner-approved-controlled-micro-live-exception",
            "--state-output",
            str(tmp_path / "runner_state.json"),
            "--report-output",
            str(tmp_path / "runner_report.md"),
        ],
    )

    rendered = capsys.readouterr().out
    printed_payload = json.loads(rendered)
    state_payload = json.loads((tmp_path / "runner_state.json").read_text(encoding="utf-8"))
    report_text = (tmp_path / "runner_report.md").read_text(encoding="utf-8")

    assert printed_payload["runtime_summary"]["order_endpoint"] == "https://api-fxtrade.oanda.com/v3/accounts/REDACTED_ACCOUNT_ID/orders"
    assert printed_payload == state_payload
    assert "super-secret-live-token" not in rendered
    assert "super-secret-account-id" not in rendered
    assert "session-token-must-not-escape" not in rendered
    assert "Bearer super-secret-live-token" not in rendered
    assert "session-token-must-not-escape" not in json.dumps(state_payload, sort_keys=True)
    assert "Bearer" not in report_text
    assert "REDACTED_TOKEN" in rendered
    assert payload["result"]["micro_live_status"] == CONTROLLED_MICRO_LIVE_EXCEPTION_READY


def test_bitwarden_session_helper_scripts_and_documentation_are_safe() -> None:
    assert START_SESSION_HELPER.exists()
    assert CLEAR_SESSION_HELPER.exists()
    assert SESSION_HELPER_DOC.exists()

    start_text = START_SESSION_HELPER.read_text(encoding="utf-8")
    clear_text = CLEAR_SESSION_HELPER.read_text(encoding="utf-8")
    doc_text = SESSION_HELPER_DOC.read_text(encoding="utf-8")

    assert "bw status" in start_text.lower()
    assert "bw unlock --raw" in start_text.lower()
    assert "aios_bitwarden_session_ready" in start_text.lower()
    assert "bw_session_present" in start_text.lower()
    assert "AIOS_BITWARDEN_SESSION_READY" in start_text
    assert "BW_SESSION_PRESENT" in start_text
    assert "env:bw_session" in clear_text.lower()
    assert "bw lock" in clear_text.lower()
    assert not re.search(r"\b(super-secret|very-secret|api token|master password)\b", start_text.lower())
    assert "bw unlock --raw" in start_text
    assert "BW_SESSION_PRESENT" in doc_text
    assert "bitwarden master password" in doc_text.lower()
    assert "do not store bw_session in repo" in doc_text.lower()
    assert ". .\\scripts\\security\\start-aiosbitwardensession.ps1" in doc_text.lower()
    assert ". .\\scripts\\security\\clear-aiosbitwardensession.ps1" in doc_text.lower()
    assert "controlled micro-live runner must print redacted stdout only" in doc_text.lower()
    assert "rotate any token that was pasted to console" in doc_text.lower()


def test_max_one_order_attempt_is_enforced(monkeypatch, tmp_path: Path):
    fake_item = {
        "broker_api_token": "token",
        "broker_account_id": "acct",
        "endpoint": "https://api-fxtrade.oanda.com",
        "environment": "live",
        "allowed_mode": "controlled_micro_live_exception_only",
    }

    attempt = {"count": 0}

    def fake_bw_read() -> dict[str, str]:
        return fake_item

    def fake_post_json_request(request_payload: dict) -> tuple[dict, int, bool]:
        attempt["count"] += 1
        return {"orderId": "o1"}, 201, True

    monkeypatch.setattr(runtime_script.shutil, "which", lambda _: "bw")
    monkeypatch.setattr(runtime_script, "_read_broker_runtime_item", fake_bw_read)
    monkeypatch.setattr(runtime_script, "_post_json_request", fake_post_json_request)
    monkeypatch.setenv("BW_SESSION", "session-token")

    payload = runtime_script.run_forex_controlled_micro_live_exception_runner_v1(
        owner_approved_controlled_micro_live_exception=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        write_report=True,
    )

    assert attempt["count"] == 1
    assert payload["runtime_summary"]["order_attempt_count"] == 1
    assert payload["runtime_summary"]["order_attempt_success"] is True
    assert payload["runtime_summary"]["max_orders_per_run"] == 1


def test_recursive_redaction_covers_token_account_and_url():
    payload = {
        "broker_api_token": "super-secret",
        "broker_account_id": "abc-123",
        "order_endpoint": "https://api-fxtrade.oanda.com/v3/accounts/abc-123/orders",
        "request": {
            "Authorization": "Bearer abcdef",
            "AccountId": {
                "value": "nested-acc",
            },
        },
    }
    sanitized = runtime_script._redact_runtime_state(payload)
    assert sanitized["broker_api_token"] == "REDACTED_TOKEN"
    assert sanitized["broker_account_id"] == "REDACTED_ACCOUNT_ID"
    assert "abc-123" not in json.dumps(sanitized)
    assert "nested-acc" not in json.dumps(sanitized)
    assert sanitized["order_endpoint"] == "https://api-fxtrade.oanda.com/v3/accounts/REDACTED_ACCOUNT_ID/orders"
    assert sanitized["request"]["Authorization"] == "REDACTED_TOKEN"


def test_runner_dry_run_writes_state_and_report(tmp_path: Path):
    state_path = tmp_path / "AIOS_FOREX_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER_V1_STATE.json"
    report_path = tmp_path / "AIOS_FOREX_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER_V1_REPORT.md"
    payload = runtime_script.run_forex_controlled_micro_live_exception_runner_v1(
        owner_approved_controlled_micro_live_exception=False,
        state_output=state_path,
        report_output=report_path,
        write_report=True,
    )
    assert state_path.exists()
    assert report_path.exists()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["result"]["micro_live_status"] == OWNER_RUNTIME_LIVE_FLAG_REQUIRED
    assert payload["result"]["current_stage"] == CURRENT_STAGE
    assert payload["result"]["next_stage"] == NEXT_STAGE_OWNER_RUN_CONTROLLED_MICRO_LIVE_EXCEPTION
    assert payload["runtime_summary"]["runtime_mode"] == "dry_run"
    assert payload["runtime_summary"]["runtime_enabled"] is False


def test_config_json_valid_and_no_secrets():
    data = json.loads(
        Path(
            "configs/forex/AIOS_FOREX_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER_V1.example.json",
        ).read_text(encoding="utf-8"),
    )
    assert data["default_mode"] == "dry_run"
    assert data["runtime_flag"] == "--owner-approved-controlled-micro-live-exception"
    assert data["broker"] == "OANDA"
    assert data["environment"] == "live"
    assert data["endpoint"] == "https://api-fxtrade.oanda.com"
    assert data["live_item_ref"] == "AIOS / OANDA / Live / Broker Runtime"
    assert data["required_allowed_mode"] == "controlled_micro_live_exception_only"
    assert data["max_orders_per_run"] == 1
    assert data["micro_live_size_policy"] == "minimum_owner_approved_size_only"
    assert data["units"] == 1
    assert data["take_profit_required"] is True
    assert data["stop_loss_required"] is True
    assert data["live_order_execution_by_this_packet"] is False
    assert data["demo_order_execution_by_this_packet"] is False
    assert data["money_movement_by_this_packet"] is False
    assert data["scheduler_started_by_this_packet"] is False
    assert data["daemon_started_by_this_packet"] is False
    assert data["webhook_started_by_this_packet"] is False
    raw = json.dumps(data).lower()
    assert "token" not in raw
    assert "secret" not in raw


def test_script_entrypoint_prints_json_and_exits_zero(tmp_path: Path):
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "forex_delivery" / "run_forex_controlled_micro_live_exception_runner_v1.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--state-output",
            str(tmp_path / "runner_state.json"),
            "--report-output",
            str(tmp_path / "runner_report.md"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["result"]["micro_live_status"] == OWNER_RUNTIME_LIVE_FLAG_REQUIRED
    assert payload["result"]["next_stage"] == NEXT_STAGE_OWNER_RUN_CONTROLLED_MICRO_LIVE_EXCEPTION
    assert (tmp_path / "runner_state.json").exists()
    assert (tmp_path / "runner_report.md").exists()


def test_docs_mentions_risk_controls_and_no_autonomous_runtime():
    text = Path(
        "docs/trading_lab/forex/FOREX_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER_V1.md",
    ).read_text(encoding="utf-8").lower()
    required = (
        "micro-live means",
        "real-money",
        "--owner-approved-controlled-micro-live-exception",
        "at most one",
        "does not start a scheduler",
        "does not start a daemon",
        "does not start a webhook",
        "advance",
        "micro_live_evidence_review",
    )
    for phrase in required:
        assert phrase in text
