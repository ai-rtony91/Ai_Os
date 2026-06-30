from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

import pytest

from scripts.forex_delivery import run_forex_live_micro_evidence_review_v1 as review

ACCOUNT_ID = "101-222-333333-001"
TOKEN = "TOK_SECRET_123"
SESSION = "BW_SESSION_TOKEN_ABC"
ENDPOINT = review.EXPECTED_ENDPOINT
INSTRUMENT = "EUR_USD"


def _read_bw_item_ok(**overrides: str) -> tuple[dict[str, str], bool]:
    base = {
        "broker_api_token": TOKEN,
        "broker_account_id": ACCOUNT_ID,
        "endpoint": ENDPOINT,
        "environment": "live",
        "allowed_mode": "controlled_micro_live_exception_only",
    }
    base.update(overrides)
    return base, True


def _safe_http_call_map(payload_by_path: dict[str, tuple[dict, int]]) -> review.SafeGet:
    def _call(url: str, _headers: dict[str, str]) -> tuple[dict | None, int | None]:
        path = urlparse(url).path
        if path in payload_by_path:
            return payload_by_path[path]
        return {"unexpected": {"url": url}}, 200

    return _call


def _run_default(**kwargs) -> dict:
    payload_path = kwargs["state_output"]
    report_path = kwargs["report_output"]
    if payload_path.exists():
        payload_path.unlink()
    if report_path.exists():
        report_path.unlink()
    return review.run_forex_live_micro_evidence_review_v1(**kwargs)


def test_default_mode_returns_owner_runtime_required_no_calls(monkeypatch, tmp_path):
    monkeypatch.delenv("BW_SESSION", raising=False)
    monkeypatch.setattr(review, "shutil", review.shutil)
    state = tmp_path / "state.json"
    report = tmp_path / "report.md"
    called = {"bw": False, "http": False}

    def read_bw_called() -> tuple[dict[str, str], bool]:
        called["bw"] = True
        return _read_bw_item_ok(), True

    def safe_http_called(*_args: object, **_kwargs: object) -> tuple[dict, int]:
        called["http"] = True
        return {"x": 1}, 200

    _run_default(
        owner_approved_readonly_live_micro_evidence_review=False,
        state_output=state,
        report_output=report,
        write_report=False,
        _read_bw_item=read_bw_called,
        _safe_http_request=safe_http_called,
    )
    payload = json.loads(state.read_text(encoding="utf-8"))
    assert payload["result"]["evidence_status"] == review.OWNER_RUNTIME_REQUIRED
    assert called["bw"] is False
    assert called["http"] is False


def test_missing_bw_session_returns_credential_access_required(monkeypatch, tmp_path):
    monkeypatch.delenv("BW_SESSION", raising=False)
    state = tmp_path / "state.json"
    report = tmp_path / "report.md"
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: "/bin/bw")

    called = {"bw": False}

    def read_bw_item() -> tuple[dict[str, str], bool]:
        called["bw"] = True
        return _read_bw_item_ok(), True

    _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=state,
        report_output=report,
        write_report=False,
        _read_bw_item=read_bw_item,
    )
    payload = json.loads(state.read_text(encoding="utf-8"))
    assert payload["result"]["evidence_status"] == review.CREDENTIAL_ACCESS_REQUIRED
    assert called["bw"] is False


def test_bitwarden_unavailable_returns_credential_access_required(monkeypatch, tmp_path):
    monkeypatch.setenv("BW_SESSION", SESSION)
    state = tmp_path / "state.json"
    report = tmp_path / "report.md"
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: None)

    _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=state,
        report_output=report,
        write_report=False,
    )
    payload = json.loads(state.read_text(encoding="utf-8"))
    assert payload["result"]["evidence_status"] == review.CREDENTIAL_ACCESS_REQUIRED
    assert payload["input"]["bitwarden_cli_available"] is False


def test_non_live_endpoint_or_environment_returns_repair_required(monkeypatch, tmp_path):
    monkeypatch.setenv("BW_SESSION", SESSION)
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: "/bin/bw")
    state = tmp_path / "state.json"
    report = tmp_path / "report.md"

    _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=state,
        report_output=report,
        write_report=False,
        _read_bw_item=lambda: _read_bw_item_ok(endpoint="https://example.com", environment="practice"),
    )
    payload = json.loads(state.read_text(encoding="utf-8"))
    assert payload["result"]["evidence_status"] == review.REPAIR_REQUIRED


def test_getonly_enforcement_blocks_post(monkeypatch):
    flags = review._initial_input(True)
    _, status, blocker = review._safe_oanda_request(
        "POST",
        f"{ENDPOINT}/v3/accounts/{ACCOUNT_ID}/summary",
        token=TOKEN,
        account_id=ACCOUNT_ID,
        runtime_input=flags,
        request_callable=lambda *_args, **_kwargs: ({"x": 1}, 200),
    )
    assert status is None
    assert blocker == "post_or_mutating_method_blocked"
    assert flags["post_request_called"] is True


def test_orders_endpoint_blocked(monkeypatch):
    flags = review._initial_input(True)
    _, _, blocker = review._safe_oanda_request(
        "GET",
        f"{ENDPOINT}/v3/accounts/{ACCOUNT_ID}/orders",
        token=TOKEN,
        account_id=ACCOUNT_ID,
        runtime_input=flags,
        request_callable=lambda *_args, **_kwargs: ({"x": 1}, 200),
    )
    assert blocker == "orders_endpoint_blocked"
    assert flags["order_endpoint_called"] is True


def test_trade_close_endpoint_blocked():
    flags = review._initial_input(True)
    _, _, blocker = review._safe_oanda_request(
        "GET",
        f"{ENDPOINT}/v3/accounts/{ACCOUNT_ID}/trades/111/close",
        token=TOKEN,
        account_id=ACCOUNT_ID,
        runtime_input=flags,
        request_callable=lambda *_args, **_kwargs: ({"x": 1}, 200),
    )
    assert blocker == "trade_or_position_close_endpoint_blocked"
    assert flags["trade_close_called"] is True


def test_position_close_endpoint_blocked():
    flags = review._initial_input(True)
    _, _, blocker = review._safe_oanda_request(
        "GET",
        f"{ENDPOINT}/v3/accounts/{ACCOUNT_ID}/positions/111/close",
        token=TOKEN,
        account_id=ACCOUNT_ID,
        runtime_input=flags,
        request_callable=lambda *_args, **_kwargs: ({"x": 1}, 200),
    )
    assert blocker == "trade_or_position_close_endpoint_blocked"
    assert flags["position_close_called"] is True


def _mock_open_evidence_payload(
    *,
    summary: dict | None = None,
    open_trades: list[dict] | None = None,
    open_positions: list[dict] | None = None,
    trades: list[dict] | None = None,
    transactions: list[dict] | None = None,
    summary_status: int = 200,
    open_trades_status: int = 200,
    open_positions_status: int = 200,
    trades_status: int = 200,
) -> review.SafeGet:
    payloads = {
        f"/v3/accounts/{ACCOUNT_ID}/summary": (summary or {"account": {"id": ACCOUNT_ID}}, summary_status),
        f"/v3/accounts/{ACCOUNT_ID}/openTrades": ({"trades": open_trades or []}, open_trades_status),
        f"/v3/accounts/{ACCOUNT_ID}/openPositions": ({"positions": open_positions or []}, open_positions_status),
        f"/v3/accounts/{ACCOUNT_ID}/trades": ({"trades": trades or []}, trades_status),
    }
    if transactions is not None:
        payloads[f"/v3/accounts/{ACCOUNT_ID}/transactions"] = ({"transactions": transactions}, 200)

    def _call(url: str, _headers: dict[str, str]) -> tuple[dict | None, int | None]:
        return payloads.get(urlparse(url).path, ({"unexpected": url}, 200))

    return _call


def test_summary_with_eur_usd_trade_returns_open_trade_found(monkeypatch, tmp_path):
    monkeypatch.setenv("BW_SESSION", SESSION)
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: "/bin/bw")
    state = tmp_path / "state.json"
    report = tmp_path / "report.md"
    mock_http = _mock_open_evidence_payload(
        open_trades=[
            {
                "id": "trade-111",
                "instrument": INSTRUMENT,
                "currentUnits": "1",
            }
        ],
        open_positions=[],
    )
    payload = _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=state,
        report_output=report,
        write_report=False,
        _read_bw_item=_read_bw_item_ok,
        _safe_http_request=mock_http,
    )
    assert payload["result"]["evidence_status"] == review.OPEN_TRADE_FOUND
    assert payload["runtime_summary"]["open_trade_found"] is True
    assert payload["runtime_summary"]["trade_fingerprints"]
    assert all(fp.startswith("sha256:") for fp in payload["runtime_summary"]["trade_fingerprints"])


@pytest.mark.parametrize(
    ("pl", "expected"),
    [
        ("12.34", review.PROFIT_POSITIVE),
        ("0.00", review.PROFIT_FLAT),
        ("-1.23", review.PROFIT_NEGATIVE),
    ],
)
def test_open_trade_with_pl_classification(
    monkeypatch,
    tmp_path,
    pl: str,
    expected: str,
):
    monkeypatch.setenv("BW_SESSION", SESSION)
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: "/bin/bw")
    mock_http = _mock_open_evidence_payload(
        open_trades=[
            {
                "id": "trade-222",
                "instrument": INSTRUMENT,
                "currentUnits": "1",
                "unrealizedPL": pl,
            }
        ],
        open_positions=[],
    )
    payload = _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        write_report=False,
        _read_bw_item=_read_bw_item_ok,
        _safe_http_request=mock_http,
    )
    assert payload["result"]["evidence_status"] == expected
    assert payload["runtime_summary"]["unrealized_pl_available"] is True
    assert payload["runtime_summary"]["unrealized_pl_value"] == float(pl)

    assert payload["runtime_summary"]["pnl_classification"] in {"positive", "flat", "negative"}


def test_open_positions_returns_open_position_found(monkeypatch, tmp_path):
    monkeypatch.setenv("BW_SESSION", SESSION)
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: "/bin/bw")
    mock_http = _mock_open_evidence_payload(
        open_trades=[],
        open_positions=[
            {
                "instrument": INSTRUMENT,
                "long": {"units": "1", "unrealizedPL": "0.03"},
                "short": {"units": "0", "unrealizedPL": "0"},
            }
        ],
    )
    payload = _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        write_report=False,
        _read_bw_item=_read_bw_item_ok,
        _safe_http_request=mock_http,
    )
    assert payload["result"]["evidence_status"] == review.PROFIT_POSITIVE
    assert payload["runtime_summary"]["open_position_found"] is True


def test_no_open_trade_or_position_with_prior_created_status(monkeypatch, tmp_path):
    monkeypatch.setenv("BW_SESSION", SESSION)
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: "/bin/bw")
    prior = {
        "order_status": "created",
        "order_status_code": 201,
        "instrument": INSTRUMENT,
        "side": "buy",
        "units": 1,
        "time_in_force": "FOK",
        "runtime_summary": {
            "order_status": "created",
            "order_status_code": 201,
            "instrument": INSTRUMENT,
            "side": "buy",
            "units": 1,
            "time_in_force": "FOK",
        },
    }
    prior_state = tmp_path / "prior.json"
    prior_state.write_text(json.dumps(prior, indent=2), encoding="utf-8")
    mock_http = _mock_open_evidence_payload(open_trades=[], open_positions=[])
    payload = _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        prior_runner_state_path=prior_state,
        write_report=False,
        _safe_http_request=mock_http,
        _read_bw_item=_read_bw_item_ok,
    )
    assert payload["runtime_summary"]["prior_order_status"] == "created"
    assert payload["result"]["evidence_status"] in {
        review.ORDER_CREATED_NO_OPEN_TRADE_FOUND,
        review.CLOSED_OR_NOT_VISIBLE,
    }


def test_no_live_order_execution_money_or_scheduler_daemon_webhook(monkeypatch, tmp_path):
    monkeypatch.setenv("BW_SESSION", SESSION)
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: "/bin/bw")
    mock_http = _mock_open_evidence_payload(open_trades=[{"id": "111", "instrument": INSTRUMENT, "currentUnits": "0"}])
    payload = _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        write_report=False,
        _read_bw_item=_read_bw_item_ok,
        _safe_http_request=mock_http,
    )
    input_data = payload["input"]
    assert input_data["live_order_execution"] is False
    assert input_data["demo_order_execution"] is False
    assert input_data["money_movement"] is False
    assert input_data["scheduler_started"] is False
    assert input_data["daemon_started"] is False
    assert input_data["webhook_started"] is False


def test_stdout_and_state_and_report_are_redacted(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("BW_SESSION", SESSION)
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: "/bin/bw")
    state = tmp_path / "state.json"
    report = tmp_path / "report.md"
    mock_http = _mock_open_evidence_payload(
        open_trades=[{"id": "111", "instrument": INSTRUMENT, "currentUnits": "1", "unrealizedPL": "0.1"}],
        open_positions=[],
    )
    _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=state,
        report_output=report,
        write_report=True,
        _read_bw_item=_read_bw_item_ok,
        _safe_http_request=mock_http,
    )
    stdout = capsys.readouterr().out
    state_text = state.read_text(encoding="utf-8")
    report_text = report.read_text(encoding="utf-8")
    assert TOKEN not in stdout
    assert ACCOUNT_ID not in stdout
    assert SESSION not in stdout
    assert "Bearer " + TOKEN not in stdout
    assert review.REDACTED_ACCOUNT_ID in state_text
    assert "sha256:" in stdout
    assert "sha256:" in state_text
    assert TOKEN not in state_text
    assert ACCOUNT_ID not in state_text
    assert SESSION not in state_text
    assert TOKEN not in report_text
    assert ACCOUNT_ID not in report_text
    assert SESSION not in report_text
    assert "sha256:" in report_text


def _write_prior_state(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def test_prior_order_payload_stoploss_on_fill_marks_sl_observed(monkeypatch, tmp_path):
    monkeypatch.setenv("BW_SESSION", SESSION)
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: "/bin/bw")
    prior = {
        "order_payload": {
            "order": {
                "stopLossOnFill": {
                    "price": "1.2345",
                },
            },
        },
    }
    prior_state = tmp_path / "prior.json"
    _write_prior_state(prior_state, prior)
    payload = _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        prior_runner_state_path=prior_state,
        write_report=False,
        _read_bw_item=_read_bw_item_ok,
        _safe_http_request=_mock_open_evidence_payload(open_trades=[], open_positions=[]),
    )
    runtime_summary = payload["runtime_summary"]
    assert runtime_summary["sl_observed"] is True
    assert runtime_summary["sl_source"] == "prior_order_payload"
    assert runtime_summary["sl_tp_observed"] is True
    assert runtime_summary["tp_observed"] is False
    assert runtime_summary["sl_fingerprint"].startswith("sha256:")


def test_prior_order_payload_takeprofit_on_fill_marks_tp_observed(monkeypatch, tmp_path):
    monkeypatch.setenv("BW_SESSION", SESSION)
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: "/bin/bw")
    prior = {
        "order_payload": {
            "order": {
                "takeProfitOnFill": {
                    "price": "1.3456",
                },
            },
        },
    }
    prior_state = tmp_path / "prior.json"
    _write_prior_state(prior_state, prior)
    payload = _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        prior_runner_state_path=prior_state,
        write_report=False,
        _read_bw_item=_read_bw_item_ok,
        _safe_http_request=_mock_open_evidence_payload(open_trades=[], open_positions=[]),
    )
    runtime_summary = payload["runtime_summary"]
    assert runtime_summary["tp_observed"] is True
    assert runtime_summary["tp_source"] == "prior_order_payload"
    assert runtime_summary["tp_fingerprint"].startswith("sha256:")


def test_open_trades_stoploss_order_marks_sl_observed_and_fingerprint(monkeypatch, tmp_path):
    monkeypatch.setenv("BW_SESSION", SESSION)
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: "/bin/bw")
    mock_http = _mock_open_evidence_payload(
        open_trades=[
            {
                "id": "trade-100",
                "instrument": INSTRUMENT,
                "currentUnits": "1",
                "stopLossOrder": {
                    "id": "SL-RAW-ID-100",
                    "price": "1.1000",
                },
            }
        ],
        open_positions=[],
    )
    payload = _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        write_report=False,
        _read_bw_item=_read_bw_item_ok,
        _safe_http_request=mock_http,
    )
    runtime_summary = payload["runtime_summary"]
    assert runtime_summary["open_trade_found"] is True
    assert runtime_summary["sl_observed"] is True
    assert runtime_summary["sl_source"] == "open_trades"
    assert runtime_summary["sl_fingerprint"].startswith("sha256:")
    assert runtime_summary["sl_fingerprint"] != "SL-RAW-ID-100"


def test_open_trades_takeprofit_order_marks_tp_observed_and_fingerprint(monkeypatch, tmp_path):
    monkeypatch.setenv("BW_SESSION", SESSION)
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: "/bin/bw")
    mock_http = _mock_open_evidence_payload(
        open_trades=[
            {
                "id": "trade-200",
                "instrument": INSTRUMENT,
                "currentUnits": "1",
                "takeProfitOrder": {
                    "id": "TP-RAW-ID-200",
                    "price": "1.3000",
                },
            }
        ],
        open_positions=[],
    )
    payload = _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        write_report=False,
        _read_bw_item=_read_bw_item_ok,
        _safe_http_request=mock_http,
    )
    runtime_summary = payload["runtime_summary"]
    assert runtime_summary["tp_observed"] is True
    assert runtime_summary["tp_source"] == "open_trades"
    assert runtime_summary["tp_fingerprint"].startswith("sha256:")
    assert runtime_summary["tp_fingerprint"] != "TP-RAW-ID-200"


def test_open_trades_order_id_signals_generate_fingerprints_not_raw_ids(monkeypatch, tmp_path):
    monkeypatch.setenv("BW_SESSION", SESSION)
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: "/bin/bw")
    raw_sl_id = "SL-ID-RAW-001"
    raw_tp_id = "TP-ID-RAW-001"
    mock_http = _mock_open_evidence_payload(
        open_trades=[
            {
                "id": "trade-300",
                "instrument": INSTRUMENT,
                "currentUnits": "1",
                "stopLossOrderID": raw_sl_id,
                "takeProfitOrderID": raw_tp_id,
            }
        ],
        open_positions=[],
    )
    payload = _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        write_report=False,
        _read_bw_item=_read_bw_item_ok,
        _safe_http_request=mock_http,
    )
    runtime_summary = payload["runtime_summary"]
    assert runtime_summary["sltp_evidence_complete"] is True
    assert runtime_summary["sl_observed"] is True
    assert runtime_summary["tp_observed"] is True
    assert runtime_summary["sl_fingerprint"] != raw_sl_id
    assert runtime_summary["tp_fingerprint"] != raw_tp_id
    assert runtime_summary["sl_fingerprint"].startswith("sha256:")
    assert runtime_summary["tp_fingerprint"].startswith("sha256:")


def test_trailing_stoploss_order_marks_trailing_sl_observed(monkeypatch, tmp_path):
    monkeypatch.setenv("BW_SESSION", SESSION)
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: "/bin/bw")
    mock_http = _mock_open_evidence_payload(
        open_trades=[
            {
                "id": "trade-400",
                "instrument": INSTRUMENT,
                "currentUnits": "1",
                "trailingStopLossOrder": {
                    "distance": "0.0015",
                },
            }
        ],
        open_positions=[],
    )
    payload = _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        write_report=False,
        _read_bw_item=_read_bw_item_ok,
        _safe_http_request=mock_http,
    )
    runtime_summary = payload["runtime_summary"]
    assert runtime_summary["trailing_sl_observed"] is True
    assert runtime_summary["sl_observed"] is True
    assert runtime_summary["trailing_sl_fingerprint"].startswith("sha256:")


def test_trades_payload_supplies_takeprofit_when_open_trades_has_no_sltp(monkeypatch, tmp_path):
    monkeypatch.setenv("BW_SESSION", SESSION)
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: "/bin/bw")
    mock_http = _mock_open_evidence_payload(
        open_trades=[
            {
                "id": "trade-500",
                "instrument": INSTRUMENT,
                "currentUnits": "1",
            }
        ],
        trades=[
            {
                "id": "trade-500",
                "instrument": INSTRUMENT,
                "currentUnits": "1",
                "takeProfitOrder": {
                    "price": "1.5000",
                },
            }
        ],
        open_positions=[],
    )
    payload = _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        write_report=False,
        _read_bw_item=_read_bw_item_ok,
        _safe_http_request=mock_http,
    )
    runtime_summary = payload["runtime_summary"]
    assert runtime_summary["open_trade_found"] is True
    assert runtime_summary["tp_observed"] is True
    assert runtime_summary["tp_source"] == "trades"
    assert runtime_summary["sl_observed"] is False


def test_open_positions_do_not_create_false_sltp_proof(monkeypatch, tmp_path):
    monkeypatch.setenv("BW_SESSION", SESSION)
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: "/bin/bw")
    mock_http = _mock_open_evidence_payload(
        open_trades=[],
        open_positions=[
            {
                "instrument": INSTRUMENT,
                "long": {
                    "units": "1",
                    "unrealizedPL": "1.0",
                },
                "short": {
                    "units": "0",
                    "unrealizedPL": "0",
                },
            }
        ],
        trades=[],
    )
    payload = _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        write_report=False,
        _read_bw_item=_read_bw_item_ok,
        _safe_http_request=mock_http,
    )
    runtime_summary = payload["runtime_summary"]
    assert payload["result"]["evidence_status"] == review.PROFIT_POSITIVE
    assert runtime_summary["open_position_found"] is True
    assert runtime_summary["sltp_evidence_complete"] is False
    assert runtime_summary["sl_observed"] is False
    assert runtime_summary["tp_observed"] is False


def test_sltp_evidence_complete_requires_both_stop_and_tp(monkeypatch, tmp_path):
    monkeypatch.setenv("BW_SESSION", SESSION)
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: "/bin/bw")
    mock_http = _mock_open_evidence_payload(
        open_trades=[
            {
                "id": "trade-700",
                "instrument": INSTRUMENT,
                "currentUnits": "1",
                "stopLossOrder": {"price": "1.1000"},
                "takeProfitOrder": {"price": "1.2000"},
            }
        ],
        open_positions=[],
    )
    payload = _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=tmp_path / "state.json",
        report_output=tmp_path / "report.md",
        write_report=False,
        _read_bw_item=_read_bw_item_ok,
        _safe_http_request=mock_http,
    )
    runtime_summary = payload["runtime_summary"]
    assert runtime_summary["sltp_evidence_complete"] is True
    assert runtime_summary["sltp_evidence_sources"] == ["open_trades"]


def test_raw_order_ids_not_in_stdout_state_or_report(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("BW_SESSION", SESSION)
    monkeypatch.setattr(review.shutil, "which", lambda *_args, **_kwargs: "/bin/bw")
    raw_sl_id = "SL-RAW-ID-REDACTION"
    raw_tp_id = "TP-RAW-ID-REDACTION"
    state = tmp_path / "state.json"
    report = tmp_path / "report.md"
    mock_http = _mock_open_evidence_payload(
        open_trades=[
            {
                "id": "trade-800",
                "instrument": INSTRUMENT,
                "currentUnits": "1",
                "stopLossOrderID": raw_sl_id,
                "takeProfitOrderID": raw_tp_id,
            }
        ],
        open_positions=[],
    )
    _run_default(
        owner_approved_readonly_live_micro_evidence_review=True,
        state_output=state,
        report_output=report,
        write_report=True,
        _read_bw_item=_read_bw_item_ok,
        _safe_http_request=mock_http,
    )
    stdout = capsys.readouterr().out
    state_text = state.read_text(encoding="utf-8")
    report_text = report.read_text(encoding="utf-8")
    assert raw_sl_id not in stdout
    assert raw_tp_id not in stdout
    assert raw_sl_id not in state_text
    assert raw_tp_id not in state_text
    assert raw_sl_id not in report_text
    assert raw_tp_id not in report_text
