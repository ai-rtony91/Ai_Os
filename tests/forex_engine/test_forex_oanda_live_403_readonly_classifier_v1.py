from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import scripts.forex_delivery.run_forex_oanda_live_403_readonly_classifier_v1 as classifier

START_HELPER_PATH = Path("scripts/security/Start-AiosBitwardenSession.ps1")
ITEM = {
    "broker_api_token": "token-should-never-leak",
    "broker_account_id": "account-should-never-leak",
    "endpoint": "https://api-fxtrade.oanda.com",
    "environment": "live",
    "allowed_mode": "controlled_micro_live_exception_only",
}


def _run_start_helper(env: dict[str, str]) -> str:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            f'. "{START_HELPER_PATH}"',
        ],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    return result.stdout.strip()


def _run_classifier(
    monkeypatch: Any,
    *,
    owner_flag: bool,
    tmp_path: Path,
    requests: list[tuple[str, int, dict[str, Any] | None]],
) -> dict[str, Any]:
    call_map = {
        "accounts": requests[0],
        "summary": requests[1],
    }

    def fake_read_bw_item() -> tuple[dict[str, str], bool]:
        return ITEM, True

    def fake_request(
        method: str,
        url: str,
        api_token: str,
        redacted_account_id: str,
        request_callable=None,
    ):
        endpoint = urlparse(url).path
        if endpoint.endswith("/v3/accounts"):
            status = call_map["accounts"][1]
            payload = call_map["accounts"][2]
        elif "/summary" in endpoint:
            status = call_map["summary"][1]
            payload = call_map["summary"][2]
        else:
            status = 500
            payload = None
        return payload, status, None

    monkeypatch.setattr(classifier, "_read_broker_runtime_item", fake_read_bw_item)
    monkeypatch.setattr(classifier, "_safe_oanda_request", fake_request)
    monkeypatch.setattr(classifier.shutil, "which", lambda _: "bw")
    monkeypatch.setenv("BW_SESSION", "session-for-tests")

    return classifier.run_forex_oanda_live_403_readonly_classifier_v1(
        owner_approved_readonly_live_403_classifier=owner_flag,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        write_report=True,
    )


def test_start_helper_uses_existing_bw_session(monkeypatch, tmp_path):
    env = os.environ.copy()
    env["BW_SESSION"] = "existing-session"
    output = _run_start_helper(env)
    lines = [line for line in output.splitlines() if line]
    assert lines == [
        "AIOS_BITWARDEN_SESSION_READY=true",
        "BW_SESSION_PRESENT=true",
    ]


def test_start_helper_missing_bw_session_uses_direct_assignment(monkeypatch, tmp_path):
    fake_bw = tmp_path / "bw.bat"
    fake_bw.write_text("@echo live-session-token", encoding="utf-8")
    env = os.environ.copy()
    env.pop("BW_SESSION", None)
    env["PATH"] = f"{tmp_path};{env.get('PATH', '')}"
    output = _run_start_helper(env)
    lines = [line for line in output.splitlines() if line]
    assert lines == [
        "AIOS_BITWARDEN_SESSION_READY=true",
        "BW_SESSION_PRESENT=true",
    ]


def test_start_helper_output_is_only_status_lines():
    text = START_HELPER_PATH.read_text(encoding="utf-8")
    assert "2>&1 | Out-String" not in text
    assert "ConvertFrom-Json" not in text
    assert "bw status" not in text


def test_default_run_returns_owner_runtime_required(tmp_path: Path):
    payload = classifier.run_forex_oanda_live_403_readonly_classifier_v1(
        owner_approved_readonly_live_403_classifier=False,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        write_report=True,
    )
    assert payload["result"]["classifier_status"] == classifier.OWNER_RUNTIME_REQUIRED
    assert payload["input"]["broker_api_called"] is False
    assert payload["input"]["live_order_execution"] is False
    assert payload["runtime_summary"]["accounts_status_code"] is None


def test_missing_bw_session_returns_credential_access_required(
    monkeypatch: Any,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(classifier.shutil, "which", lambda _: "bw")
    monkeypatch.setenv("BW_SESSION", "")
    payload = classifier.run_forex_oanda_live_403_readonly_classifier_v1(
        owner_approved_readonly_live_403_classifier=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        write_report=True,
    )
    assert payload["result"]["classifier_status"] == classifier.CREDENTIAL_ACCESS_REQUIRED
    assert payload["input"]["bw_session_present"] is False


def test_classifier_redacts_broker_credentials_in_outputs(
    monkeypatch: Any,
    tmp_path: Path,
    capsys: Any,
) -> None:
    def fake_request(method: str, url: str, api_token: str, redacted_account_id: str, request_callable=None):
        if url.endswith("/v3/accounts"):
            return {"accounts": [{"id": ITEM["broker_account_id"]}]}, 200, None
        if "/summary" in url:
            return {"account": {"id": ITEM["broker_account_id"]}}, 200, None
        return None, None, "unmatched_url"

    def fake_read_bw_item() -> tuple[dict[str, str], bool]:
        return ITEM, True

    monkeypatch.setattr(classifier.shutil, "which", lambda _: "bw")
    monkeypatch.setattr(classifier, "_safe_oanda_request", fake_request)
    monkeypatch.setattr(classifier, "_read_broker_runtime_item", fake_read_bw_item)
    monkeypatch.setenv("BW_SESSION", "session-token")

    payload = classifier.run_forex_oanda_live_403_readonly_classifier_v1(
        owner_approved_readonly_live_403_classifier=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        write_report=True,
    )
    rendered = capsys.readouterr().out
    assert ITEM["broker_api_token"] not in rendered
    assert ITEM["broker_account_id"] not in rendered
    assert "Bearer" not in rendered
    assert "Authorization" not in rendered

    state_text = (tmp_path / "state.json").read_text(encoding="utf-8")
    report_text = (tmp_path / "report.md").read_text(encoding="utf-8")
    for needle in [
        ITEM["broker_api_token"],
        ITEM["broker_account_id"],
        "session-token",
        "Bearer",
        "Authorization",
    ]:
        assert needle not in state_text
        assert needle not in report_text

    assert payload["runtime_summary"]["redacted_account_id"] == classifier.REDACTED_ACCOUNT_ID


def test_no_live_order_or_money_movement_when_running_classifier(
    monkeypatch: Any,
    tmp_path: Path,
) -> None:
    payload = _run_classifier(
        monkeypatch,
        owner_flag=True,
        tmp_path=tmp_path,
        requests=[("accounts", 403, None), ("summary", None, None)],
    )
    assert payload["input"]["live_order_execution"] is False
    assert payload["input"]["money_movement"] is False
    assert payload["input"]["scheduler_started"] is False
    assert payload["input"]["daemon_started"] is False
    assert payload["input"]["webhook_started"] is False
    assert payload["result"]["classifier_status"] == classifier.ACCOUNT_LIST_FORBIDDEN


def test_safe_oanda_request_blocks_post_requests():
    payload, status, blocker = classifier._safe_oanda_request(
        "POST",
        "https://api-fxtrade.oanda.com/v3/accounts",
        "token",
        "account",
    )
    assert payload is None
    assert status is None
    assert blocker == "post_or_mutating_method_blocked"


def test_safe_oanda_request_blocks_orders_endpoint():
    payload, status, blocker = classifier._safe_oanda_request(
        "GET",
        "https://api-fxtrade.oanda.com/v3/accounts/account-should-never-leak/orders",
        "token",
        "account",
    )
    assert payload is None
    assert status is None
    assert blocker == "orders_endpoint_blocked"


def test_accounts_403_returns_account_list_forbidden(monkeypatch: Any, tmp_path: Path) -> None:
    payload = _run_classifier(
        monkeypatch,
        owner_flag=True,
        tmp_path=tmp_path,
        requests=[("accounts", 403, None), ("summary", None, None)],
    )
    assert payload["result"]["classifier_status"] == classifier.ACCOUNT_LIST_FORBIDDEN
    assert payload["runtime_summary"]["summary_status_code"] is None
    assert payload["input"]["summary_probe_called"] is False


def test_accounts_visible_mismatch_returns_account_not_visible(
    monkeypatch: Any,
    tmp_path: Path,
) -> None:
    payload = _run_classifier(
        monkeypatch,
        owner_flag=True,
        tmp_path=tmp_path,
        requests=[
            ("accounts", 200, {"accounts": [{"id": "different-account"}]}),
            ("summary", 200, {"account": {"id": ITEM["broker_account_id"]}}),
        ],
    )
    assert payload["result"]["classifier_status"] == classifier.ACCOUNT_NOT_VISIBLE_TO_TOKEN
    assert payload["runtime_summary"]["configured_account_visible"] is False
    assert payload["input"]["summary_probe_called"] is False


def test_summary_403_returns_account_summary_forbidden(
    monkeypatch: Any,
    tmp_path: Path,
) -> None:
    payload = _run_classifier(
        monkeypatch,
        owner_flag=True,
        tmp_path=tmp_path,
        requests=[
            ("accounts", 200, {"accounts": [{"id": ITEM["broker_account_id"]}]}),
            ("summary", 403, None),
        ],
    )
    assert payload["result"]["classifier_status"] == classifier.ACCOUNT_SUMMARY_FORBIDDEN
    assert payload["runtime_summary"]["summary_status_code"] == 403


def test_summary_200_returns_order_forbidden_classification(
    monkeypatch: Any,
    tmp_path: Path,
) -> None:
    payload = _run_classifier(
        monkeypatch,
        owner_flag=True,
        tmp_path=tmp_path,
        requests=[
            ("accounts", 200, {"accounts": [{"id": ITEM["broker_account_id"]}]}),
            ("summary", 200, {"account": {"id": ITEM["broker_account_id"]}}),
        ],
    )
    assert (
        payload["result"]["classifier_status"]
        == classifier.ACCOUNT_VISIBLE_SUMMARY_OK_ORDER_FORBIDDEN
    )
    assert payload["runtime_summary"]["configured_account_visible"] is True
