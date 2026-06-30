"""Read-only post-live micro-trade evidence review for one controlled live-lane order."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

PACKET_ID = "PKT-FOREX-LIVE-MICRO-EVIDENCE-REVIEW-V1"
MODULE = "run_forex_live_micro_evidence_review_v1"

STATE_PATH = Path("Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_EVIDENCE_REVIEW_V1_STATE.json")
REPORT_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_EVIDENCE_REVIEW_V1_REPORT.md",
)
PRIOR_STATE_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER_V1_STATE.json",
)

OWNER_RUNTIME_FLAG = "--owner-approved-readonly-live-micro-evidence-review"
OWNER_RUNTIME_REQUIRED = "LIVE_MICRO_EVIDENCE_OWNER_RUNTIME_REQUIRED"
CREDENTIAL_ACCESS_REQUIRED = "LIVE_MICRO_EVIDENCE_CREDENTIAL_ACCESS_REQUIRED"
READONLY_REVIEW_READY = "LIVE_MICRO_EVIDENCE_READONLY_REVIEW_READY"
ORDER_CREATED_NO_OPEN_TRADE_FOUND = "LIVE_MICRO_EVIDENCE_ORDER_CREATED_NO_OPEN_TRADE_FOUND"
CLOSED_OR_NOT_VISIBLE = "LIVE_MICRO_EVIDENCE_CLOSED_OR_NOT_VISIBLE"
OPEN_TRADE_FOUND = "LIVE_MICRO_EVIDENCE_OPEN_TRADE_FOUND"
OPEN_POSITION_FOUND = "LIVE_MICRO_EVIDENCE_OPEN_POSITION_FOUND"
PROFIT_POSITIVE = "LIVE_MICRO_EVIDENCE_PROFIT_POSITIVE"
PROFIT_FLAT = "LIVE_MICRO_EVIDENCE_PROFIT_FLAT"
PROFIT_NEGATIVE = "LIVE_MICRO_EVIDENCE_PROFIT_NEGATIVE"
BROKER_UNAVAILABLE = "LIVE_MICRO_EVIDENCE_BROKER_UNAVAILABLE"
REPAIR_REQUIRED = "LIVE_MICRO_EVIDENCE_REPAIR_REQUIRED"

BITWARDEN_RUNTIME_ITEM = "AIOS / OANDA / Live / Broker Runtime"
ALLOWED_MODE = "controlled_micro_live_exception_only"
EXPECTED_ENVIRONMENT = "live"
EXPECTED_ENDPOINT = "https://api-fxtrade.oanda.com"
READONLY_METHOD = "GET"
INSTRUMENT = "EUR_USD"

CURRENT_STAGE = "live_micro_evidence_review"
NEXT_STAGE_MAP = {
    OWNER_RUNTIME_REQUIRED: "owner_enable_readonly_runtime",
    CREDENTIAL_ACCESS_REQUIRED: "owner_repair_broker_runtime_access",
    READONLY_REVIEW_READY: "owner_build_repeatability_evidence_loop",
    ORDER_CREATED_NO_OPEN_TRADE_FOUND: "owner_build_repeatability_evidence_loop",
    CLOSED_OR_NOT_VISIBLE: "owner_build_repeatability_evidence_loop",
    OPEN_TRADE_FOUND: "owner_continue_repeatability",
    OPEN_POSITION_FOUND: "owner_continue_repeatability",
    PROFIT_POSITIVE: "owner_continue_repeatability",
    PROFIT_FLAT: "owner_continue_repeatability",
    PROFIT_NEGATIVE: "owner_continue_repeatability",
    BROKER_UNAVAILABLE: "owner_retry_when_broker_available",
    REPAIR_REQUIRED: "owner_repair_runtime_contract",
}

REDACTED_TOKEN = "REDACTED_TOKEN"
REDACTED_ACCOUNT_ID = "REDACTED_ACCOUNT_ID"
REDACTED_SESSION = "REDACTED_SESSION"
FINGERPRINT_PREFIX = "sha256:"
SAFE_TIMEOUT_SECONDS = 10

RuntimeInput = dict[str, Any]
RuntimeSummary = dict[str, Any]
ResultPayload = dict[str, Any]

ReadBwItem = Callable[[], tuple[dict[str, str], bool]]
SafeGet = Callable[[str, Mapping[str, str]], tuple[dict[str, Any] | None, int | None]]


def run_forex_live_micro_evidence_review_v1(
    *,
    owner_approved_readonly_live_micro_evidence_review: bool = False,
    state_output: Path = STATE_PATH,
    report_output: Path = REPORT_PATH,
    prior_runner_state_path: Path = PRIOR_STATE_PATH,
    write_report: bool = True,
    _read_bw_item: ReadBwItem | None = None,
    _safe_http_request: SafeGet | None = None,
) -> dict[str, Any]:
    runtime_input = _initial_input(
        owner_approved_readonly_live_micro_evidence_review,
    )
    runtime_summary = _initial_runtime_summary()
    prior_state = _read_prior_runner_state(prior_runner_state_path)
    runtime_input["prior_live_order_created_evidence_present"] = bool(
        str(prior_state.get("order_status", "")).strip().lower() == "created"
        and _as_int(prior_state.get("order_status_code")) == 201,
    )
    runtime_summary["prior_order_status"] = prior_state.get("order_status", "not_found")
    runtime_summary["prior_order_status_code"] = _as_int(prior_state.get("order_status_code"))
    runtime_summary["instrument"] = prior_state.get("instrument", INSTRUMENT)
    runtime_summary["units"] = str(prior_state.get("units", ""))
    runtime_summary["side"] = str(prior_state.get("side", "buy") or "buy")
    runtime_summary["time_in_force"] = str(prior_state.get("time_in_force", "FOK"))
    runtime_summary["risk_controls_observed"] = _risk_controls_observed(prior_state)
    runtime_summary["sl_tp_observed"] = runtime_summary["risk_controls_observed"]
    runtime_summary["sl_observed"] = runtime_summary["risk_controls_observed"]
    runtime_summary["tp_observed"] = runtime_summary["risk_controls_observed"]

    if not owner_approved_readonly_live_micro_evidence_review:
        return _build_result(
            runtime_input=runtime_input,
            runtime_summary=runtime_summary,
            owner_flag=False,
            evidence_status=OWNER_RUNTIME_REQUIRED,
            blockers=["owner runtime flag is required"],
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
        )

    runtime_input["bitwarden_cli_available"] = shutil.which("bw") is not None
    runtime_input["bw_session_present"] = bool(os.environ.get("BW_SESSION"))
    if not runtime_input["bitwarden_cli_available"] or not runtime_input["bw_session_present"]:
        return _build_result(
            runtime_input=runtime_input,
            runtime_summary=runtime_summary,
            owner_flag=True,
            evidence_status=CREDENTIAL_ACCESS_REQUIRED,
            blockers=["BW_SESSION and Bitwarden CLI are required"],
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
        )

    read_bw_item = _read_bw_item or _read_broker_runtime_item
    broker_item, runtime_input["bitwarden_item_read_success"] = read_bw_item()
    runtime_input["live_credential_values_available_to_runtime"] = bool(
        broker_item.get("broker_api_token")
        and broker_item.get("broker_account_id")
        and broker_item.get("endpoint")
        and broker_item.get("environment")
        and broker_item.get("allowed_mode"),
    )
    runtime_input["endpoint_is_oanda_fxtrade"] = (
        str(broker_item.get("endpoint", "")).strip() == EXPECTED_ENDPOINT
    )
    runtime_input["environment_is_live"] = (
        str(broker_item.get("environment", "")).strip().lower() == EXPECTED_ENVIRONMENT
    )
    runtime_input["allowed_mode_is_micro_live_only"] = (
        str(broker_item.get("allowed_mode", "")).strip()
        == ALLOWED_MODE
    )
    runtime_summary["redacted_account_id"] = REDACTED_ACCOUNT_ID
    runtime_summary["time_in_force"] = str(broker_item.get("time_in_force", runtime_summary["time_in_force"]))

    token = str(broker_item.get("broker_api_token", "")).strip()
    account_id = str(broker_item.get("broker_account_id", "")).strip()
    endpoint = str(broker_item.get("endpoint", "")).strip().rstrip("/")
    bw_session = str(os.environ.get("BW_SESSION") or "")
    redacted_session = _maybe_redact(bw_session)

    if not runtime_input["bitwarden_item_read_success"]:
        return _build_result(
            runtime_input=runtime_input,
            runtime_summary=runtime_summary,
            owner_flag=True,
            evidence_status=CREDENTIAL_ACCESS_REQUIRED,
            blockers=["Bitwarden runtime item read failed"],
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            token=token,
            account_id=account_id,
            bw_session=bw_session,
        )

    if not runtime_input["live_credential_values_available_to_runtime"]:
        return _build_result(
            runtime_input=runtime_input,
            runtime_summary=runtime_summary,
            owner_flag=True,
            evidence_status=CREDENTIAL_ACCESS_REQUIRED,
            blockers=["runtime item missing one of token/account/endpoint/environment/allowed mode"],
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            token=token,
            account_id=account_id,
            bw_session=bw_session,
        )

    if (
        not runtime_input["endpoint_is_oanda_fxtrade"]
        or not runtime_input["environment_is_live"]
        or not runtime_input["allowed_mode_is_micro_live_only"]
    ):
        return _build_result(
            runtime_input=runtime_input,
            runtime_summary=runtime_summary,
            owner_flag=True,
            evidence_status=REPAIR_REQUIRED,
            blockers=["runtime contract must be live endpoint, live environment, controlled micro mode"],
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            token=token,
            account_id=account_id,
            bw_session=bw_session,
        )

    summary_payload, runtime_summary["summary_status_code"], blocker = _safe_oanda_request(
        "GET",
        f"{endpoint}/v3/accounts/{account_id}/summary",
        token=token,
        account_id=account_id,
        request_callable=_safe_http_request,
        runtime_input=runtime_input,
    )
    if blocker:
        return _build_result(
            runtime_input=runtime_input,
            runtime_summary=runtime_summary,
            owner_flag=True,
            evidence_status=BROKER_UNAVAILABLE if blocker == "network_error" else REPAIR_REQUIRED,
            blockers=[blocker],
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            token=token,
            account_id=account_id,
            bw_session=bw_session,
        )
    if runtime_summary["summary_status_code"] in (401, 403):
        return _build_result(
            runtime_input=runtime_input,
            runtime_summary=runtime_summary,
            owner_flag=True,
            evidence_status=CREDENTIAL_ACCESS_REQUIRED,
            blockers=["summary endpoint returned 401/403"],
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            token=token,
            account_id=account_id,
            bw_session=bw_session,
        )
    if _as_int(runtime_summary["summary_status_code"]) is None or _as_int(
        runtime_summary["summary_status_code"],
    ) >= 500:
        return _build_result(
            runtime_input=runtime_input,
            runtime_summary=runtime_summary,
            owner_flag=True,
            evidence_status=BROKER_UNAVAILABLE,
            blockers=["summary endpoint unavailable"],
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            token=token,
            account_id=account_id,
            bw_session=bw_session,
        )
    if not isinstance(summary_payload, Mapping):
        return _build_result(
            runtime_input=runtime_input,
            runtime_summary=runtime_summary,
            owner_flag=True,
            evidence_status=REPAIR_REQUIRED,
            blockers=["summary payload malformed"],
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            token=token,
            account_id=account_id,
            bw_session=bw_session,
        )
    runtime_input["summary_probe_called"] = True
    runtime_input["broker_api_called"] = True

    open_trades_payload, runtime_summary["open_trades_status_code"], blocker = _safe_oanda_request(
        "GET",
        f"{endpoint}/v3/accounts/{account_id}/openTrades",
        token=token,
        account_id=account_id,
        request_callable=_safe_http_request,
        runtime_input=runtime_input,
    )
    if blocker:
        return _build_blocker_result(
            runtime_input=runtime_input,
            runtime_summary=runtime_summary,
            owner_flag=True,
            blocker=blocker,
            token=token,
            account_id=account_id,
            bw_session=bw_session,
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
        )
    if runtime_summary["open_trades_status_code"] in (401, 403):
        return _build_result(
            runtime_input=runtime_input,
            runtime_summary=runtime_summary,
            owner_flag=True,
            evidence_status=CREDENTIAL_ACCESS_REQUIRED,
            blockers=["openTrades endpoint returned 401/403"],
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            token=token,
            account_id=account_id,
            bw_session=bw_session,
        )
    if _as_int(runtime_summary["open_trades_status_code"]) is None or _as_int(
        runtime_summary["open_trades_status_code"],
    ) >= 500:
        return _build_result(
            runtime_input=runtime_input,
            runtime_summary=runtime_summary,
            owner_flag=True,
            evidence_status=BROKER_UNAVAILABLE,
            blockers=["openTrades endpoint unavailable"],
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            token=token,
            account_id=account_id,
            bw_session=bw_session,
        )
    if not isinstance(open_trades_payload, Mapping):
        return _build_result(
            runtime_input=runtime_input,
            runtime_summary=runtime_summary,
            owner_flag=True,
            evidence_status=REPAIR_REQUIRED,
            blockers=["openTrades payload malformed"],
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            token=token,
            account_id=account_id,
            bw_session=bw_session,
        )
    runtime_input["open_trades_probe_called"] = True

    open_positions_payload, runtime_summary["open_positions_status_code"], blocker = (
        _safe_oanda_request(
            "GET",
            f"{endpoint}/v3/accounts/{account_id}/openPositions",
            token=token,
            account_id=account_id,
            request_callable=_safe_http_request,
            runtime_input=runtime_input,
        )
    )
    if blocker:
        return _build_blocker_result(
            runtime_input=runtime_input,
            runtime_summary=runtime_summary,
            owner_flag=True,
            blocker=blocker,
            token=token,
            account_id=account_id,
            bw_session=bw_session,
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
        )
    if runtime_summary["open_positions_status_code"] in (401, 403):
        return _build_result(
            runtime_input=runtime_input,
            runtime_summary=runtime_summary,
            owner_flag=True,
            evidence_status=CREDENTIAL_ACCESS_REQUIRED,
            blockers=["openPositions endpoint returned 401/403"],
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            token=token,
            account_id=account_id,
            bw_session=bw_session,
        )
    if _as_int(runtime_summary["open_positions_status_code"]) is None or _as_int(
        runtime_summary["open_positions_status_code"],
    ) >= 500:
        return _build_result(
            runtime_input=runtime_input,
            runtime_summary=runtime_summary,
            owner_flag=True,
            evidence_status=BROKER_UNAVAILABLE,
            blockers=["openPositions endpoint unavailable"],
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            token=token,
            account_id=account_id,
            bw_session=bw_session,
        )
    if not isinstance(open_positions_payload, Mapping):
        return _build_result(
            runtime_input=runtime_input,
            runtime_summary=runtime_summary,
            owner_flag=True,
            evidence_status=REPAIR_REQUIRED,
            blockers=["openPositions payload malformed"],
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            token=token,
            account_id=account_id,
            bw_session=bw_session,
        )
    runtime_input["open_positions_probe_called"] = True

    trades_payload, runtime_summary["trades_status_code"], blocker = _safe_oanda_request(
        "GET",
        f"{endpoint}/v3/accounts/{account_id}/trades",
        token=token,
        account_id=account_id,
        request_callable=_safe_http_request,
        runtime_input=runtime_input,
    )
    runtime_input["trades_probe_called"] = True
    if blocker and blocker not in {"network_error", "unsafe_endpoint_blocked"}:
        runtime_summary["trades_status_code"] = None
        runtime_summary["trades_probe_called"] = False
    open_trades = _extract_items(open_trades_payload, "trades")
    open_positions = _extract_items(open_positions_payload, "positions")
    runtime_summary["trade_count"] = len(open_trades)
    runtime_summary["position_count"] = len(open_positions)

    maybe_tx_id = _extract_safe_transaction_id(prior_state)
    if maybe_tx_id:
        tx_payload, runtime_summary["transactions_status_code"], blocker = _safe_oanda_request(
            "GET",
            f"{endpoint}/v3/accounts/{account_id}/transactions/sinceid?id={maybe_tx_id}",
            token=token,
            account_id=account_id,
            request_callable=_safe_http_request,
            runtime_input=runtime_input,
        )
        if blocker:
            runtime_summary["transactions_status_code"] = None
            runtime_input["transactions_probe_called"] = False
        else:
            runtime_input["transactions_probe_called"] = True

    open_trade = _find_matching_euro_trade(open_trades, runtime_summary["side"])
    open_position = _find_matching_euro_position(open_positions, runtime_summary["side"])

    trade_fingerprints: list[str] = []
    for trade in open_trades:
        trade_id = str(trade.get("id", trade.get("tradeID", "")))
        if trade_id:
            trade_fingerprints.append(_fingerprint(trade_id))
    position_fingerprints: list[str] = []
    for position in open_positions:
        position_id = str(position.get("id", position.get("positionID", "")))
        if not position_id:
            position_id = f"{position.get('instrument', INSTRUMENT)}"
        position_fingerprints.append(_fingerprint(position_id))
    runtime_summary["trade_fingerprints"] = trade_fingerprints
    runtime_summary["position_fingerprints"] = position_fingerprints

    runtime_summary["open_trade_found"] = open_trade is not None
    runtime_summary["open_position_found"] = (
        not runtime_summary["open_trade_found"] and open_position is not None
    )
    runtime_summary["unrealized_pl_available"] = False
    runtime_summary["unrealized_pl_value"] = None
    runtime_summary["pnl_classification"] = "unavailable"

    evidence_status: str = READONLY_REVIEW_READY
    if open_trade is not None:
        runtime_summary["open_trade_found"] = True
        runtime_summary["trade_fingerprints"] = [
            _fingerprint(str(open_trade.get("id", open_trade.get("tradeID", ""))))
        ]
        realized = _to_float(_as_text(open_trade.get("unrealizedPL")))
        if realized is not None:
            runtime_summary["unrealized_pl_available"] = True
            runtime_summary["unrealized_pl_value"] = realized
            runtime_summary["pnl_classification"] = _classify_pnl(realized)
            evidence_status = {
                "positive": PROFIT_POSITIVE,
                "flat": PROFIT_FLAT,
                "negative": PROFIT_NEGATIVE,
            }[runtime_summary["pnl_classification"]]
        else:
            evidence_status = OPEN_TRADE_FOUND
    elif open_position is not None:
        runtime_summary["open_position_found"] = True
        long_units = _to_float(_as_text(open_position.get("long", {}).get("units")))
        short_units = _to_float(_as_text(open_position.get("short", {}).get("units")))
        if long_units not in (None, 0.0) or short_units not in (None, 0.0):
            pl = _to_float(_as_text(open_position.get("long", {}).get("unrealizedPL")))
            if pl is None:
                pl = _to_float(_as_text(open_position.get("short", {}).get("unrealizedPL")))
            if pl is not None:
                runtime_summary["unrealized_pl_available"] = True
                runtime_summary["unrealized_pl_value"] = pl
                runtime_summary["pnl_classification"] = _classify_pnl(pl)
                evidence_status = {
                    "positive": PROFIT_POSITIVE,
                    "flat": PROFIT_FLAT,
                    "negative": PROFIT_NEGATIVE,
                }[runtime_summary["pnl_classification"]]
            else:
                evidence_status = OPEN_POSITION_FOUND
        else:
            open_position = None

    if not runtime_summary["open_trade_found"] and not runtime_summary["open_position_found"]:
        if (
            runtime_summary["prior_order_status"] == "created"
            and runtime_summary["prior_order_status_code"] == 201
        ):
            evidence_status = (
                CLOSED_OR_NOT_VISIBLE
                if runtime_summary["summary_status_code"] == 200
                else ORDER_CREATED_NO_OPEN_TRADE_FOUND
            )
        else:
            evidence_status = READONLY_REVIEW_READY

    runtime_summary["safe_next_action"] = _safe_next_action_for_status(evidence_status)
    result = {
        "evidence_status": evidence_status,
        "current_stage": CURRENT_STAGE,
        "next_stage": NEXT_STAGE_MAP.get(evidence_status, "owner_review_readonly_evidence"),
        "blockers": [],
        "safe_next_action": runtime_summary["safe_next_action"],
    }
    payload = {
        "module": MODULE,
        "packet_id": PACKET_ID,
        "input": runtime_input,
        "result": result,
        "runtime_summary": runtime_summary,
    }
    return _write_artifacts(
        payload,
        state_output=state_output,
        report_output=report_output,
        write_report=write_report,
        token=token,
        account_id=account_id,
        bw_session=bw_session,
    )


def _build_blocker_result(
    *,
    runtime_input: RuntimeInput,
    runtime_summary: RuntimeSummary,
    owner_flag: bool,
    blocker: str,
    state_output: Path,
    report_output: Path,
    write_report: bool,
    token: str,
    account_id: str,
    bw_session: str,
) -> dict[str, Any]:
    if blocker in {"post_or_mutating_method_blocked", "orders_endpoint_blocked", "trade_or_position_close_endpoint_blocked"}:
        evidence_status = REPAIR_REQUIRED
        safe_next_action = "Refine request guardrails; only GET read-only evidence probes are allowed."
    else:
        evidence_status = BROKER_UNAVAILABLE if blocker == "network_error" else REPAIR_REQUIRED
        safe_next_action = "Retry with a reachable broker endpoint or fixed guardrails."
    runtime_summary["safe_next_action"] = safe_next_action
    runtime_summary["trade_fingerprints"] = runtime_summary.get("trade_fingerprints", [])
    runtime_summary["position_fingerprints"] = runtime_summary.get("position_fingerprints", [])
    result: ResultPayload = {
        "evidence_status": evidence_status,
        "current_stage": CURRENT_STAGE,
        "next_stage": NEXT_STAGE_MAP.get(evidence_status, "owner_review_readonly_evidence"),
        "blockers": [f"probe_blocker:{blocker}"],
        "safe_next_action": safe_next_action,
    }
    payload: dict[str, Any] = {
        "module": MODULE,
        "packet_id": PACKET_ID,
        "input": runtime_input,
        "result": result,
        "runtime_summary": runtime_summary,
    }
    return _write_artifacts(
        payload,
        state_output=state_output,
        report_output=report_output,
        write_report=write_report,
        token=token,
        account_id=account_id,
        bw_session=bw_session,
    )


def _build_result(
    *,
    runtime_input: RuntimeInput,
    runtime_summary: RuntimeSummary,
    owner_flag: bool,
    evidence_status: str,
    blockers: list[str],
    state_output: Path,
    report_output: Path,
    write_report: bool,
    token: str = "",
    account_id: str = "",
    bw_session: str = "",
) -> dict[str, Any]:
    del owner_flag
    safe_next_action = _safe_next_action_for_status(evidence_status)
    runtime_summary["safe_next_action"] = safe_next_action
    result = {
        "evidence_status": evidence_status,
        "current_stage": CURRENT_STAGE,
        "next_stage": NEXT_STAGE_MAP.get(evidence_status, "owner_review_readonly_evidence"),
        "blockers": blockers,
        "safe_next_action": safe_next_action,
    }
    runtime_summary.setdefault("trade_fingerprints", [])
    runtime_summary.setdefault("position_fingerprints", [])
    runtime_summary.setdefault("unrealized_pl_value", None)
    runtime_summary.setdefault("pnl_classification", "unavailable")
    runtime_summary.setdefault("prior_order_status", runtime_summary.get("prior_order_status", "not_found"))
    runtime_summary.setdefault("prior_order_status_code", runtime_summary.get("prior_order_status_code"))
    payload = {
        "module": MODULE,
        "packet_id": PACKET_ID,
        "input": runtime_input,
        "result": result,
        "runtime_summary": runtime_summary,
    }
    return _write_artifacts(
        payload,
        state_output=state_output,
        report_output=report_output,
        write_report=write_report,
        token=token,
        account_id=account_id,
        bw_session=bw_session,
    )


def _safe_oanda_request(
    method: str,
    url: str,
    *,
    token: str,
    account_id: str,
    runtime_input: RuntimeInput,
    request_callable: SafeGet | None = None,
) -> tuple[dict[str, Any] | None, int | None, str | None]:
    method_upper = str(method or "").upper()
    parsed = urlparse(url)
    path = (parsed.path or "").lower()
    if method_upper != READONLY_METHOD:
        runtime_input["post_request_called"] = True
        return None, None, "post_or_mutating_method_blocked"
    if parsed.scheme.lower() != "https" or f"{parsed.scheme}://{parsed.netloc}".lower() != EXPECTED_ENDPOINT:
        return None, None, "unsafe_endpoint_blocked"

    normalized_path = path.lower()
    if "/orders" in normalized_path:
        runtime_input["order_endpoint_called"] = True
        return None, None, "orders_endpoint_blocked"
    if "/trades/" in normalized_path and normalized_path.endswith("/close"):
        runtime_input["trade_close_called"] = True
        return None, None, "trade_or_position_close_endpoint_blocked"
    if "/positions/" in normalized_path and normalized_path.endswith("/close"):
        runtime_input["position_close_called"] = True
        return None, None, "trade_or_position_close_endpoint_blocked"

    expected_account = str(account_id).strip().lower()
    safe_paths = (
        f"/v3/accounts/{expected_account}/summary",
        f"/v3/accounts/{expected_account}/opentrades",
        f"/v3/accounts/{expected_account}/openpositions",
        f"/v3/accounts/{expected_account}/trades",
        f"/v3/accounts/{expected_account}/transactions",
    )
    if normalized_path not in safe_paths:
        return None, None, "unsafe_endpoint_blocked"
    if normalized_path == f"/v3/accounts/{expected_account}/transactions":
        qs = parse_qs(parsed.query or "")
        transaction_id = (qs.get("id") or [""])[0]
        if not transaction_id or not transaction_id.isdigit():
            return None, None, "unsafe_endpoint_blocked"

    getter = request_callable or _default_http_get
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    try:
        payload, status = getter(url, headers)
    except HTTPError as exc:  # pragma: no cover - exercised through monkeypatch in tests
        payload_raw = None
        try:
            raw = exc.read().decode("utf-8", errors="replace")
            payload_raw = json.loads(raw)
        except Exception:
            payload_raw = None
        status = getattr(exc, "code", None)
        if _as_int(status) is not None and _as_int(status) >= 500:
            return payload_raw if isinstance(payload_raw, dict) else None, status, "network_error"
        if _as_int(status) in (401, 403):
            return payload_raw if isinstance(payload_raw, dict) else None, status, None
        return payload_raw if isinstance(payload_raw, dict) else None, status, None
    except URLError:
        return None, None, "network_error"
    except Exception as exc:  # pragma: no cover
        return None, None, str(exc)
    if not isinstance(payload, dict):
        return None, status, None
    return payload, status, None


def _default_http_get(url: str, headers: Mapping[str, str]) -> tuple[dict[str, Any] | None, int | None]:
    request = Request(url, headers=dict(headers), method="GET")
    try:
        with urlopen(request, timeout=SAFE_TIMEOUT_SECONDS) as response:
            raw = response.read().decode("utf-8", errors="replace")
            status = getattr(response, "status", None)
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        status = getattr(exc, "code", None)
        try:
            payload = json.loads(raw or "{}")
            return payload if isinstance(payload, dict) else None, status
        except json.JSONDecodeError:
            return None, status
    except URLError:
        return None, None

    try:
        payload = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return None, status
    return payload if isinstance(payload, dict) else None, status


def _read_broker_runtime_item() -> tuple[dict[str, str], bool]:
    command = ["bw", "get", "item", BITWARDEN_RUNTIME_ITEM]
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return {}, False
    if completed.returncode != 0 or not completed.stdout:
        return {}, False
    return _parse_broker_runtime_item(completed.stdout), True


def _parse_broker_runtime_item(raw_output: str) -> dict[str, str]:
    try:
        payload = json.loads(raw_output)
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    fields: dict[str, str] = {}
    raw_fields = payload.get("fields")
    if isinstance(raw_fields, list):
        for field in raw_fields:
            if not isinstance(field, Mapping):
                continue
            name = str(field.get("name", "")).strip()
            if not name:
                continue
            fields[name] = str(field.get("value", "")).strip()
    elif isinstance(raw_fields, Mapping):
        for key, value in raw_fields.items():
            fields[str(key).strip()] = str(value).strip()
    for key in ("broker_api_token", "broker_account_id", "endpoint", "environment", "allowed_mode"):
        if key not in fields and key in payload:
            value = payload.get(key, "")
            if isinstance(value, str):
                fields[key] = value
    return {
        "broker_api_token": fields.get("broker_api_token", ""),
        "broker_account_id": fields.get("broker_account_id", ""),
        "endpoint": fields.get("endpoint", ""),
        "environment": fields.get("environment", ""),
        "allowed_mode": fields.get("allowed_mode", ""),
    }


def _read_prior_runner_state(state_path: Path) -> dict[str, Any]:
    if not state_path.exists():
        return {}
    try:
        raw_text = state_path.read_text(encoding="utf-8")
        raw_data = json.loads(raw_text)
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw_data, Mapping):
        return {}
    runtime_summary = raw_data.get("runtime_summary")
    if isinstance(runtime_summary, Mapping):
        if "order_status" in runtime_summary:
            order_status = runtime_summary.get("order_status")
            order_status_code = runtime_summary.get("order_status_code")
            instrument = runtime_summary.get("instrument", INSTRUMENT)
            units = runtime_summary.get("units", "")
            side = runtime_summary.get("side", "buy")
            time_in_force = runtime_summary.get("time_in_force", "FOK")
        else:
            order_status = raw_data.get("order_status", "")
            order_status_code = raw_data.get("order_status_code", None)
            instrument = raw_data.get("instrument", INSTRUMENT)
            units = raw_data.get("units", "")
            side = raw_data.get("side", "buy")
            time_in_force = raw_data.get("time_in_force", "FOK")
    else:
        order_status = raw_data.get("order_status", "")
        order_status_code = raw_data.get("order_status_code", None)
        instrument = raw_data.get("instrument", INSTRUMENT)
        units = raw_data.get("units", "")
        side = raw_data.get("side", "buy")
        time_in_force = raw_data.get("time_in_force", "FOK")

    return {
        "order_status": order_status,
        "order_status_code": order_status_code,
        "instrument": instrument,
        "units": units,
        "side": side,
        "time_in_force": time_in_force,
        "runtime_summary": runtime_summary if isinstance(runtime_summary, Mapping) else {},
        "order_payload": _first_mapping(raw_data.get("order_payload"), ("runtime_summary", "order_payload")),
        "order_response": _first_mapping(raw_data.get("order_response"), ("runtime_summary", "order_response")),
    }


def _first_mapping(raw: Any, fallback_path: tuple[str, str]) -> dict[str, Any]:
    if isinstance(raw, Mapping):
        return dict(raw)
    if isinstance(fallback_path, tuple):
        # keep compatibility with malformed prior state structures
        first, second = fallback_path
        if isinstance(raw, dict):
            value = raw.get(first, {})
            if isinstance(value, Mapping):
                return dict(value)
        _ = second
    return {}


def _extract_safe_transaction_id(state: Mapping[str, Any]) -> str | None:
    candidates = [
        _lookup_nested(state, ("order_payload", "orderFillTransaction", "requestID")),
        _lookup_nested(state, ("order_response", "orderFillTransaction", "requestID")),
        _lookup_nested(state, ("order_payload", "orderCreateTransaction", "requestID")),
        _lookup_nested(state, ("runtime_summary", "order_payload", "orderFillTransaction", "requestID")),
        _lookup_nested(state, ("runtime_summary", "order_response", "orderFillTransaction", "requestID")),
        _lookup_nested(state, ("runtime_summary", "order_status", "requestID")),
    ]
    for candidate in candidates:
        if candidate is None:
            continue
        text = str(candidate).strip()
        if text.isdigit():
            return text
    return None


def _risk_controls_observed(prior_state: dict[str, Any]) -> bool:
    order_payload = prior_state.get("order_payload")
    if not isinstance(order_payload, Mapping):
        return False
    order = order_payload.get("order")
    if isinstance(order, Mapping):
        return bool(order.get("stopLossOnFill") or order.get("takeProfitOnFill"))
    return (
        str(order_payload).lower().find("stoploss") >= 0
        or str(order_payload).lower().find("takeprofit") >= 0
    )


def _extract_items(payload: Any, key: str) -> list[dict[str, Any]]:
    if not isinstance(payload, Mapping):
        return []
    raw = payload.get(key, [])
    if not isinstance(raw, list):
        return []
    return [entry for entry in raw if isinstance(entry, Mapping)]


def _find_matching_euro_trade(
    trades: list[dict[str, Any]],
    side_hint: str,
) -> dict[str, Any] | None:
    for trade in trades:
        if str(trade.get("instrument", "")).strip().upper() != INSTRUMENT:
            continue
        units = _to_float(trade.get("currentUnits"))
        if units is None:
            return trade
        if side_hint.lower() == "sell" and units < 0:
            return trade
        if side_hint.lower() != "sell" and units > 0:
            return trade
    return None


def _find_matching_euro_position(
    positions: list[dict[str, Any]],
    side_hint: str,
) -> dict[str, Any] | None:
    for position in positions:
        if str(position.get("instrument", "")).strip().upper() != INSTRUMENT:
            continue
        long_units = _to_float(_as_text(position.get("long", {}).get("units")))
        short_units = _to_float(_as_text(position.get("short", {}).get("units")))
        if side_hint.lower() == "sell":
            if short_units and short_units < 0:
                return position
            if long_units and long_units > 0:
                continue
        else:
            if long_units and long_units > 0:
                return position
            if short_units and short_units < 0:
                continue
    return positions[0] if positions else None


def _classify_pnl(value: float) -> str:
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "flat"


def _safe_next_action_for_status(status: str) -> str:
    if status == OWNER_RUNTIME_REQUIRED:
        return "Run with --owner-approved-readonly-live-micro-evidence-review."
    if status == CREDENTIAL_ACCESS_REQUIRED:
        return "Repair Bitwarden BW_SESSION/runtime item access and retry."
    if status == REPAIR_REQUIRED:
        return "Repair runtime contract and rerun."
    if status in (BROKER_UNAVAILABLE,):
        return "Retry when broker endpoint/network returns 2xx."
    if status in (PROFIT_POSITIVE, PROFIT_FLAT, PROFIT_NEGATIVE, OPEN_TRADE_FOUND, OPEN_POSITION_FOUND):
        return "Capture post-live evidence persistence across sessions and continue repeatability testing."
    if status in (ORDER_CREATED_NO_OPEN_TRADE_FOUND, CLOSED_OR_NOT_VISIBLE, READONLY_REVIEW_READY):
        return "Continue supervised repeatability/evidence loop and run again in owner-approved mode."
    return "Collect read-only evidence and proceed to next packet."


def _as_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return None


def _to_float(value: Any) -> float | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return float(str(value))
    except (TypeError, ValueError):
        return None


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _lookup_nested(payload: Mapping[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def _fingerprint(value: str) -> str:
    return f"{FINGERPRINT_PREFIX}{hashlib.sha256(value.encode('utf-8')).hexdigest()[:12]}"


def _initial_input(owner_flag_present: bool) -> RuntimeInput:
    return {
        "owner_flag_present": owner_flag_present,
        "bw_session_present": False,
        "bitwarden_cli_available": False,
        "bitwarden_item_read_success": False,
        "live_credential_values_available_to_runtime": False,
        "endpoint_is_oanda_fxtrade": False,
        "environment_is_live": False,
        "allowed_mode_is_micro_live_only": False,
        "readonly_get_only_enforced": True,
        "summary_probe_called": False,
        "open_trades_probe_called": False,
        "open_positions_probe_called": False,
        "trades_probe_called": False,
        "transactions_probe_called": False,
        "order_endpoint_called": False,
        "post_request_called": False,
        "trade_close_called": False,
        "position_close_called": False,
        "broker_api_called": False,
        "live_order_execution": False,
        "demo_order_execution": False,
        "money_movement": False,
        "scheduler_started": False,
        "daemon_started": False,
        "webhook_started": False,
        "prior_live_order_created_evidence_present": False,
    }


def _initial_runtime_summary() -> RuntimeSummary:
    return {
        "summary_status_code": None,
        "open_trades_status_code": None,
        "open_positions_status_code": None,
        "trades_status_code": None,
        "transactions_status_code": None,
        "prior_order_status_code": None,
        "prior_order_status": "not_found",
        "instrument": INSTRUMENT,
        "units": "",
        "side": "buy",
        "time_in_force": "FOK",
        "open_trade_found": False,
        "open_position_found": False,
        "trade_count": 0,
        "position_count": 0,
        "trade_fingerprints": [],
        "position_fingerprints": [],
        "unrealized_pl_available": False,
        "unrealized_pl_value": None,
        "pnl_classification": "unavailable",
        "risk_controls_observed": False,
        "sl_tp_observed": False,
        "sl_observed": False,
        "tp_observed": False,
        "redacted_account_id": REDACTED_ACCOUNT_ID,
        "safe_next_action": "Run evidence review.",
    }


def _maybe_redact(value: str) -> str:
    if value:
        return REDACTED_SESSION
    return ""


def _write_artifacts(
    payload: dict[str, Any],
    state_output: Path,
    report_output: Path,
    *,
    write_report: bool,
    token: str = "",
    account_id: str = "",
    bw_session: str = "",
) -> dict[str, Any]:
    payload = _redact_payload(
        payload,
        token=token,
        account_id=account_id,
        bw_session=bw_session,
    )
    state_output.parent.mkdir(parents=True, exist_ok=True)
    state_output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if write_report:
        report_output.parent.mkdir(parents=True, exist_ok=True)
        report_output.write_text(_build_report(payload), encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return payload


def _redact_payload(
    payload: Mapping[str, Any],
    *,
    token: str = "",
    account_id: str = "",
    bw_session: str = "",
) -> dict[str, Any]:
    def _redact_value(value: Any) -> Any:
        if isinstance(value, str):
            return _redact_text(value, token=token, account_id=account_id, bw_session=bw_session)
        if isinstance(value, list):
            return [_redact_value(item) for item in value]
        if isinstance(value, dict):
            redacted: dict[str, Any] = {}
            for k, v in value.items():
                lowered = str(k).lower()
                if lowered == "authorization":
                    redacted[k] = REDACTED_TOKEN
                else:
                    redacted[k] = _redact_value(v)
            return redacted
        return value

    return _redact_value(dict(payload))


def _redact_text(
    value: str,
    *,
    token: str,
    account_id: str,
    bw_session: str,
) -> str:
    result = value
    if token:
        result = result.replace(token, REDACTED_TOKEN)
        result = re.sub(
            rf"(?i)bearer\\s+{re.escape(token)}",
            f"Bearer {REDACTED_TOKEN}",
            result,
        )
        result = result.replace(f"Bearer {token}", f"Bearer {REDACTED_TOKEN}")
    if account_id:
        result = result.replace(account_id, REDACTED_ACCOUNT_ID)
    if bw_session:
        result = result.replace(bw_session, REDACTED_SESSION)
    return result


def _build_report(payload: Mapping[str, Any]) -> str:
    input_payload = payload["input"]
    result = payload["result"]
    runtime_summary = payload["runtime_summary"]
    blockers = "\n".join(f"- {item}" for item in result["blockers"]) or "- none"
    return (
        "# AIOS Forex Live Micro Evidence Review V1\n\n"
        "## Purpose\n"
        "Post-live-proof evidence review for one controlled micro-live order. This packet does not place a trade.\n\n"
        "## Input\n"
        f"- owner_flag_present: {input_payload.get('owner_flag_present')}\n"
        f"- bw_session_present: {input_payload.get('bw_session_present')}\n"
        f"- bitwarden_cli_available: {input_payload.get('bitwarden_cli_available')}\n"
        f"- bitwarden_item_read_success: {input_payload.get('bitwarden_item_read_success')}\n"
        f"- live_credential_values_available_to_runtime: {input_payload.get('live_credential_values_available_to_runtime')}\n"
        f"- endpoint_is_oanda_fxtrade: {input_payload.get('endpoint_is_oanda_fxtrade')}\n"
        f"- environment_is_live: {input_payload.get('environment_is_live')}\n"
        f"- allowed_mode_is_micro_live_only: {input_payload.get('allowed_mode_is_micro_live_only')}\n"
        f"- readonly_get_only_enforced: {input_payload.get('readonly_get_only_enforced')}\n"
        f"- summary_probe_called: {input_payload.get('summary_probe_called')}\n"
        f"- open_trades_probe_called: {input_payload.get('open_trades_probe_called')}\n"
        f"- open_positions_probe_called: {input_payload.get('open_positions_probe_called')}\n"
        f"- trades_probe_called: {input_payload.get('trades_probe_called')}\n"
        f"- transactions_probe_called: {input_payload.get('transactions_probe_called')}\n"
        f"- order_endpoint_called: {input_payload.get('order_endpoint_called')}\n"
        f"- post_request_called: {input_payload.get('post_request_called')}\n"
        f"- trade_close_called: {input_payload.get('trade_close_called')}\n"
        f"- position_close_called: {input_payload.get('position_close_called')}\n"
        f"- live_order_execution: {input_payload.get('live_order_execution')}\n"
        f"- demo_order_execution: {input_payload.get('demo_order_execution')}\n"
        f"- money_movement: {input_payload.get('money_movement')}\n"
        f"- scheduler_started: {input_payload.get('scheduler_started')}\n"
        f"- daemon_started: {input_payload.get('daemon_started')}\n"
        f"- webhook_started: {input_payload.get('webhook_started')}\n"
        f"- prior_live_order_created_evidence_present: {input_payload.get('prior_live_order_created_evidence_present')}\n\n"
        "## Result\n"
        f"- evidence_status: {result['evidence_status']}\n"
        f"- current_stage: {result['current_stage']}\n"
        f"- next_stage: {result['next_stage']}\n"
        f"- safe_next_action: {result['safe_next_action']}\n"
        "## Blockers\n"
        f"{blockers}\n\n"
        "## Runtime summary\n"
        f"- summary_status_code: {runtime_summary.get('summary_status_code')}\n"
        f"- open_trades_status_code: {runtime_summary.get('open_trades_status_code')}\n"
        f"- open_positions_status_code: {runtime_summary.get('open_positions_status_code')}\n"
        f"- trades_status_code: {runtime_summary.get('trades_status_code')}\n"
        f"- transactions_status_code: {runtime_summary.get('transactions_status_code')}\n"
        f"- prior_order_status_code: {runtime_summary.get('prior_order_status_code')}\n"
        f"- prior_order_status: {runtime_summary.get('prior_order_status')}\n"
        f"- instrument: {runtime_summary.get('instrument')}\n"
        f"- units: {runtime_summary.get('units')}\n"
        f"- side: {runtime_summary.get('side')}\n"
        f"- time_in_force: {runtime_summary.get('time_in_force')}\n"
        f"- open_trade_found: {runtime_summary.get('open_trade_found')}\n"
        f"- open_position_found: {runtime_summary.get('open_position_found')}\n"
        f"- trade_count: {runtime_summary.get('trade_count')}\n"
        f"- position_count: {runtime_summary.get('position_count')}\n"
        f"- trade_fingerprints: {runtime_summary.get('trade_fingerprints')}\n"
        f"- position_fingerprints: {runtime_summary.get('position_fingerprints')}\n"
        f"- unrealized_pl_available: {runtime_summary.get('unrealized_pl_available')}\n"
        f"- unrealized_pl_value: {runtime_summary.get('unrealized_pl_value')}\n"
        f"- pnl_classification: {runtime_summary.get('pnl_classification')}\n"
        f"- risk_controls_observed: {runtime_summary.get('risk_controls_observed')}\n"
        f"- sl_tp_observed: {runtime_summary.get('sl_tp_observed')}\n"
        f"- sl_observed: {runtime_summary.get('sl_observed')}\n"
        f"- tp_observed: {runtime_summary.get('tp_observed')}\n"
        f"- redacted_account_id: {runtime_summary.get('redacted_account_id')}\n"
        f"- safe_next_action: {runtime_summary.get('safe_next_action')}\n\n"
        "## Allowed probes\n"
        "- GET https://api-fxtrade.oanda.com/v3/accounts/{account_id}/summary\n"
        "- GET https://api-fxtrade.oanda.com/v3/accounts/{account_id}/openTrades\n"
        "- GET https://api-fxtrade.oanda.com/v3/accounts/{account_id}/openPositions\n"
        "- GET https://api-fxtrade.oanda.com/v3/accounts/{account_id}/trades\n"
        "- GET https://api-fxtrade.oanda.com/v3/accounts/{account_id}/transactions/sinceid?id=<safe transaction id>\n\n"
        "## Forbidden actions\n"
        "- Any order/mutation endpoint, non-GET method, /orders path, trade close, position close\n"
        "- Any endpoint outside https://api-fxtrade.oanda.com\n"
        "- Broker money movement, scheduler, daemon, webhook\n\n"
        "## Status taxonomy\n"
        f"- {OWNER_RUNTIME_REQUIRED}\n"
        f"- {CREDENTIAL_ACCESS_REQUIRED}\n"
        f"- {READONLY_REVIEW_READY}\n"
        f"- {ORDER_CREATED_NO_OPEN_TRADE_FOUND}\n"
        f"- {CLOSED_OR_NOT_VISIBLE}\n"
        f"- {OPEN_TRADE_FOUND}\n"
        f"- {OPEN_POSITION_FOUND}\n"
        f"- {PROFIT_POSITIVE}\n"
        f"- {PROFIT_FLAT}\n"
        f"- {PROFIT_NEGATIVE}\n"
        f"- {BROKER_UNAVAILABLE}\n"
        f"- {REPAIR_REQUIRED}\n\n"
        "## Safe next action\n"
        f"{runtime_summary.get('safe_next_action')}\n"
        "## Validators\n"
        "- python -m py_compile scripts/forex_delivery/run_forex_live_micro_evidence_review_v1.py\n"
        "- python -m pytest tests/forex_engine/test_forex_live_micro_evidence_review_v1.py -q\n"
        "- python scripts/forex_delivery/run_forex_live_micro_evidence_review_v1.py\n"
    )


def _parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only micro-live evidence review for one controlled live micro order.",
        allow_abbrev=False,
    )
    parser.add_argument(OWNER_RUNTIME_FLAG, action="store_true")
    parser.add_argument(
        "--state-output",
        default=str(STATE_PATH),
        help="Path for JSON state output.",
    )
    parser.add_argument(
        "--report-output",
        default=str(REPORT_PATH),
        help="Path for Markdown report output.",
    )
    parser.add_argument("--no-report", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_arguments(argv)
    run_forex_live_micro_evidence_review_v1(
        owner_approved_readonly_live_micro_evidence_review=bool(
            getattr(args, OWNER_RUNTIME_FLAG.lstrip("-").replace("-", "_")),
        ),
        state_output=Path(args.state_output),
        report_output=Path(args.report_output),
        write_report=not args.no_report,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "run_forex_live_micro_evidence_review_v1",
    "_safe_oanda_request",
    "_safe_next_action_for_status",
]
