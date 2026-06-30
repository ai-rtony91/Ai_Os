from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import scripts.forex_delivery.run_forex_oanda_live_account_binding_repair_v1 as repair

ITEM_NAME = "AIOS / OANDA / Live / Broker Runtime"
TOKEN = "token-should-never-leak"
CONFIGURED_ACCOUNT = "acct-configured-should-never-leak"
VISIBLE_ACCOUNTS = ["acct-visible-1", "acct-visible-2"]
SESSION = "bw-session-should-never-leak"


def _raise() -> Any:
    raise AssertionError("No external call expected in default mode.")


def _run_repair(
    *,
    monkeypatch: Any,
    owner_inspect: bool = False,
    owner_update: bool = False,
    select_visible_account_index: int | None = None,
    accounts: list[str] | None = None,
    accounts_status_code: int = 200,
    raw_bw_item: dict[str, Any] | None = None,
    bw_cli_available: bool = True,
    update_result: bool = True,
    state_output: Path | None = None,
    report_output: Path | None = None,
    bw_session: str | None = SESSION,
) -> tuple[dict[str, Any], list[tuple[str, str, list[str]]]]:
    if accounts is None:
        accounts = VISIBLE_ACCOUNTS.copy()

    if raw_bw_item is None:
        raw_bw_item = {
            "fields": [
                {"name": "broker_api_token", "value": TOKEN},
                {"name": "broker_account_id", "value": CONFIGURED_ACCOUNT},
                {"name": "endpoint", "value": repair.OANDA_LIVE_ENDPOINT},
                {"name": "environment", "value": "live"},
            ],
        }

    def fake_read_bw_item() -> tuple[dict[str, Any], bool]:
        return raw_bw_item, True

    request_calls: list[tuple[str, str, list[str]]] = []

    def fake_http_get(url: str, headers: dict[str, str]):
        request_calls.append(("GET", url, list(headers.keys())))
        assert "/orders" not in url
        payload = {"accounts": [{"id": account_id} for account_id in accounts]}
        return payload, accounts_status_code

    write_calls: list[dict[str, Any]] = []

    def fake_write_bw_item(updated_item: dict[str, Any], _: int | None = None) -> bool:
        write_calls.append(updated_item)
        return update_result

    if state_output is None:
        state_output = Path("tmp_state.json")
    if report_output is None:
        report_output = Path("tmp_report.md")

    if bw_session is None:
        monkeypatch.delenv("BW_SESSION", raising=False)
    else:
        monkeypatch.setenv("BW_SESSION", bw_session)

    monkeypatch.setattr(repair.shutil, "which", lambda _: "bw" if bw_cli_available else None)

    payload = repair.run_forex_oanda_live_account_binding_repair_v1(
        owner_approved_readonly_account_binding_inspect=owner_inspect,
        owner_approved_update_bitwarden_account_binding=owner_update,
        select_visible_account_index=select_visible_account_index,
        _read_bw_item=fake_read_bw_item,
        _safe_http_get=fake_http_get,
        _write_bw_item=fake_write_bw_item if owner_update else lambda *_a, **_k: False,
        state_output=state_output,
        report_output=report_output,
        write_report=True,
    )

    return payload, request_calls, write_calls


def _read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_default_mode_no_broker_or_bitwarden_call(tmp_path, monkeypatch):
    payload = repair.run_forex_oanda_live_account_binding_repair_v1(
        owner_approved_readonly_account_binding_inspect=False,
        owner_approved_update_bitwarden_account_binding=False,
        _read_bw_item=lambda: (_raise(), False),  # type: ignore[call-arg]
        _safe_http_get=lambda _u, _h: (_raise(), 0),
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        write_report=True,
    )

    assert (
        payload["result"]["account_binding_repair_status"]
        == repair.ACCOUNT_BINDING_REPAIR_OWNER_RUNTIME_REQUIRED
    )
    assert payload["input"]["broker_api_called"] is False
    assert payload["input"]["accounts_probe_called"] is False
    assert payload["input"]["bitwarden_item_read_success"] is False
    assert payload["input"]["live_order_execution"] is False
    assert payload["input"]["money_movement"] is False


def _raise() -> Any:
    raise AssertionError("No external call expected in default mode.")


def test_inspect_without_bw_session_returns_credential_access_required(monkeypatch, tmp_path):
    payload, _, _ = _run_repair(
        monkeypatch=monkeypatch,
        owner_inspect=True,
        bw_session="",
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
    )

    assert (
        payload["result"]["account_binding_repair_status"]
        == repair.ACCOUNT_BINDING_REPAIR_CREDENTIAL_ACCESS_REQUIRED
    )
    assert payload["input"]["bw_session_present"] is False
    assert payload["input"]["bitwarden_cli_available"] is True
    assert payload["input"]["bitwarden_item_read_success"] is False


def test_inspect_200_configured_account_not_visible(monkeypatch, tmp_path):
    payload, request_calls, _ = _run_repair(
        monkeypatch=monkeypatch,
        owner_inspect=True,
        accounts=["other-account-1", "other-account-2"],
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        raw_bw_item={
            "fields": [
                {"name": "broker_api_token", "value": TOKEN},
                {"name": "broker_account_id", "value": CONFIGURED_ACCOUNT},
                {"name": "endpoint", "value": repair.OANDA_LIVE_ENDPOINT},
            ]
        },
    )

    assert (
        payload["result"]["account_binding_repair_status"]
        == repair.ACCOUNT_BINDING_REPAIR_CONFIGURED_ACCOUNT_NOT_VISIBLE
    )
    assert payload["runtime_summary"]["configured_account_visible"] is False
    assert payload["runtime_summary"]["account_list_count"] == 2
    assert payload["runtime_summary"]["selected_visible_account_index"] is None
    assert request_calls == [
        (
            "GET",
            f"{repair.OANDA_LIVE_ENDPOINT}/v3/accounts",
            ["Accept", "Authorization", "User-Agent"],
        )
    ]


def test_inspect_200_configured_account_visible(monkeypatch, tmp_path):
    payload, _, _ = _run_repair(
        monkeypatch=monkeypatch,
        owner_inspect=True,
        accounts=[CONFIGURED_ACCOUNT, "other-account"],
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        raw_bw_item={
            "fields": [
                {"name": "broker_api_token", "value": TOKEN},
                {"name": "broker_account_id", "value": CONFIGURED_ACCOUNT},
                {"name": "endpoint", "value": repair.OANDA_LIVE_ENDPOINT},
            ]
        },
    )

    assert (
        payload["result"]["account_binding_repair_status"]
        == repair.ACCOUNT_BINDING_REPAIR_CONFIGURED_ACCOUNT_VISIBLE
    )
    assert payload["runtime_summary"]["configured_account_visible"] is True
    assert payload["runtime_summary"]["configured_account_fingerprint"].startswith("sha256:")


def test_update_index_1_only_updates_broker_account_id(monkeypatch, tmp_path):
    monkeypatch.setenv("BW_SESSION", SESSION)
    payload, _, write_calls = _run_repair(
        monkeypatch=monkeypatch,
        owner_update=True,
        select_visible_account_index=1,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
    )

    assert (
        payload["result"]["account_binding_repair_status"]
        == repair.ACCOUNT_BINDING_REPAIR_UPDATE_APPLIED
    )
    assert payload["result"]["account_binding_update_status"] == repair.UPDATE_STATUS_UPDATED
    assert payload["runtime_summary"]["selected_visible_account_index"] == 1
    assert payload["runtime_summary"]["selected_account_fingerprint"] == (
        repair._account_fingerprint(VISIBLE_ACCOUNTS[0])
    )

    updated_item = write_calls[0]
    account_fields = [
        field
        for field in updated_item["fields"]
        if field["name"] == repair.BROKER_ACCOUNT_ID_FIELD
    ]
    assert account_fields == [{"name": repair.BROKER_ACCOUNT_ID_FIELD, "value": VISIBLE_ACCOUNTS[0]}]
    assert len(account_fields) == 1
    assert payload["input"]["bitwarden_update_success"] is True


def test_update_invalid_index_returns_index_invalid(monkeypatch, tmp_path):
    payload, _, write_calls = _run_repair(
        monkeypatch=monkeypatch,
        owner_update=True,
        select_visible_account_index=99,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
    )

    assert (
        payload["result"]["account_binding_repair_status"]
        == repair.ACCOUNT_BINDING_REPAIR_INDEX_INVALID
    )
    assert payload["result"]["account_binding_update_status"] == (
        repair.UPDATE_STATUS_INDEX_INVALID
    )
    assert write_calls == []


def test_no_orders_no_post_no_live_order_no_money_movement(monkeypatch, tmp_path):
    payload, request_calls, _ = _run_repair(
        monkeypatch=monkeypatch,
        owner_inspect=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
    )

    assert payload["input"]["order_endpoint_called"] is False
    assert payload["input"]["post_request_called"] is False
    assert payload["input"]["live_order_execution"] is False
    assert payload["input"]["money_movement"] is False
    assert payload["input"]["scheduler_started"] is False
    assert payload["input"]["daemon_started"] is False
    assert payload["input"]["webhook_started"] is False
    for method, url, _ in request_calls:
        assert method == "GET"
        assert "/orders" not in url


def test_artifacts_have_no_raw_sensitive_values(monkeypatch, tmp_path, capsys):
    state_output = tmp_path / "state.json"
    report_output = tmp_path / "report.md"
    monkeypatch.setenv("BW_SESSION", SESSION)
    payload, _, _ = _run_repair(
        monkeypatch=monkeypatch,
        owner_inspect=True,
        accounts=[CONFIGURED_ACCOUNT, VISIBLE_ACCOUNTS[1]],
        state_output=state_output,
        report_output=report_output,
    )
    rendered = capsys.readouterr().out

    assert TOKEN not in rendered
    assert CONFIGURED_ACCOUNT not in rendered
    assert SESSION not in rendered
    assert "Authorization" not in rendered
    assert "Bearer" not in rendered
    for candidate in [TOKEN, CONFIGURED_ACCOUNT, SESSION, VISIBLE_ACCOUNTS[0], VISIBLE_ACCOUNTS[1]]:
        assert candidate not in _read_file(state_output)
        assert candidate not in _read_file(report_output)

    assert payload["runtime_summary"]["configured_account_fingerprint"].startswith("sha256:")
    assert all(
        entry.startswith("sha256:")
        for entry in payload["runtime_summary"]["visible_account_fingerprints"]
    )
