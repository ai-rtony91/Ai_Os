"""Read-only classifier for OANDA live 403 outcomes."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import re

PACKET_ID = "AIOS-FOREX-OANDA-LIVE-403-READONLY-CLASSIFIER-V1"
MODULE = "run_forex_oanda_live_403_readonly_classifier_v1"
SCRIPT_STATE_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_OANDA_LIVE_403_READONLY_CLASSIFIER_V1_STATE.json",
)
SCRIPT_REPORT_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_OANDA_LIVE_403_READONLY_CLASSIFIER_V1_REPORT.md",
)

OWNER_RUNTIME_FLAG = "--owner-approved-readonly-live-403-classifier"
LIVEOFX_ITEM_REF = "AIOS / OANDA / Live / Broker Runtime"
OANDA_LIVE_ENDPOINT = "https://api-fxtrade.oanda.com"
ENV_LIVE = "live"
ALLOWED_MODE = "controlled_micro_live_exception_only"
READ_ONLY_METHOD = "GET"

REDACTED_TOKEN = "REDACTED_TOKEN"
REDACTED_ACCOUNT_ID = "REDACTED_ACCOUNT_ID"
REDACTED_SESSION = "REDACTED_SESSION"

CURRENT_STAGE = "oanda_live_403_readonly_classifier_v1"

OWNER_RUNTIME_REQUIRED = "OANDA_LIVE_403_CLASSIFIER_OWNER_RUNTIME_REQUIRED"
CREDENTIAL_ACCESS_REQUIRED = "OANDA_LIVE_403_CLASSIFIER_CREDENTIAL_ACCESS_REQUIRED"
READONLY_PROBE_READY = "OANDA_LIVE_403_CLASSIFIER_READONLY_PROBE_READY"
ACCOUNT_LIST_FORBIDDEN = "OANDA_LIVE_403_CLASSIFIER_ACCOUNT_LIST_FORBIDDEN"
ACCOUNT_SUMMARY_FORBIDDEN = "OANDA_LIVE_403_CLASSIFIER_ACCOUNT_SUMMARY_FORBIDDEN"
ACCOUNT_NOT_VISIBLE_TO_TOKEN = "OANDA_LIVE_403_CLASSIFIER_ACCOUNT_NOT_VISIBLE_TO_TOKEN"
ACCOUNT_VISIBLE_SUMMARY_OK_ORDER_FORBIDDEN = (
    "OANDA_LIVE_403_CLASSIFIER_ACCOUNT_VISIBLE_SUMMARY_OK_ORDER_FORBIDDEN"
)
BROKER_UNAVAILABLE = "OANDA_LIVE_403_CLASSIFIER_BROKER_UNAVAILABLE"
REPAIR_REQUIRED = "OANDA_LIVE_403_CLASSIFIER_REPAIR_REQUIRED"


HttpGetCallable = Callable[[str, Mapping[str, str]], tuple[dict[str, Any] | None, int | None]]


def run_forex_oanda_live_403_readonly_classifier_v1(
    *,
    owner_approved_readonly_live_403_classifier: bool = False,
    state_output: Path = SCRIPT_STATE_PATH,
    report_output: Path = SCRIPT_REPORT_PATH,
    write_report: bool = True,
    _read_bw_item: Callable[[], tuple[dict[str, str], bool]] | None = None,
    _http_get: HttpGetCallable | None = None,
) -> dict[str, Any]:
    runtime_input = _initial_input(owner_approved_readonly_live_403_classifier)
    runtime_summary: dict[str, Any] = _initial_summary()
    status, blockers, safe_action = _run_defaults(runtime_input, runtime_summary)

    if not owner_approved_readonly_live_403_classifier:
        result = _result_payload(
            classifier_status=OWNER_RUNTIME_REQUIRED,
            current_stage=CURRENT_STAGE,
            next_stage="owner_runtime_flag_required",
            blockers=[CREDENTIAL_ACCESS_REQUIRED],
            safe_next_action="Run with --owner-approved-readonly-live-403-classifier.",
        )
        payload = _compose_payload(runtime_input, result, runtime_summary)
        payload["result"]["safe_next_action"] = safe_action
        payload["runtime_summary"]["safe_next_action"] = safe_action
        return _write_artifacts(payload, state_output, report_output, write_report)

    runtime_input["bitwarden_cli_available"] = shutil.which("bw") is not None
    if not runtime_input["bitwarden_cli_available"]:
        runtime_input["bw_session_present"] = bool(_current_bw_session())
        result = _result_payload(
            classifier_status=CREDENTIAL_ACCESS_REQUIRED,
            current_stage=CURRENT_STAGE,
            next_stage="install_or_unlock_bitwarden_cli",
            blockers=["bitwarden_cli_available must be true"],
            safe_next_action="Install Bitwarden CLI and set BW_SESSION for this shell.",
        )
        payload = _compose_payload(runtime_input, result, runtime_summary)
        payload["runtime_summary"]["safe_next_action"] = "Install Bitwarden CLI and set BW_SESSION for this shell."
        return _write_artifacts(payload, state_output, report_output, write_report)

    runtime_input["bw_session_present"] = bool(_current_bw_session())
    if not runtime_input["bw_session_present"]:
        result = _result_payload(
            classifier_status=CREDENTIAL_ACCESS_REQUIRED,
            current_stage=CURRENT_STAGE,
            next_stage="set_bw_session",
            blockers=["env:BW_SESSION is required"],
            safe_next_action="Set BW_SESSION and rerun with owner runtime flag.",
        )
        payload = _compose_payload(runtime_input, result, runtime_summary)
        payload["runtime_summary"]["safe_next_action"] = "Set BW_SESSION and rerun with owner runtime flag."
        return _write_artifacts(payload, state_output, report_output, write_report)

    read_item = _read_bw_item or _read_broker_runtime_item
    broker_item, runtime_input["bitwarden_item_read_success"] = read_item()
    if not runtime_input["bitwarden_item_read_success"]:
        result = _result_payload(
            classifier_status=CREDENTIAL_ACCESS_REQUIRED,
            current_stage=CURRENT_STAGE,
            next_stage="read_live_broker_runtime_item",
            blockers=["bitwarden runtime item read failed"],
            safe_next_action="Read and validate the Bitwarden runtime item.",
        )
        payload = _compose_payload(runtime_input, result, runtime_summary)
        payload["runtime_summary"]["safe_next_action"] = "Read and validate the Bitwarden runtime item."
        return _write_artifacts(payload, state_output, report_output, write_report)

    runtime_input["live_credential_values_available_to_runtime"] = bool(
        bool(broker_item.get("broker_api_token"))
        and bool(broker_item.get("broker_account_id"))
        and bool(broker_item.get("endpoint"))
        and bool(broker_item.get("environment"))
        and bool(broker_item.get("allowed_mode")),
    )

    runtime_input["endpoint_is_oanda_fxtrade"] = (
        broker_item.get("endpoint") == OANDA_LIVE_ENDPOINT
    )
    runtime_input["environment_is_live"] = (
        broker_item.get("environment") == ENV_LIVE
    )
    runtime_input["allowed_mode_is_micro_live_only"] = (
        broker_item.get("allowed_mode") == ALLOWED_MODE
    )
    runtime_summary["redacted_account_id"] = (
        REDACTED_ACCOUNT_ID
        if broker_item.get("broker_account_id")
        else "REDACTED_ACCOUNT_ID"
    )
    runtime_summary["redacted_endpoint"] = _redact_text(
        broker_item.get("endpoint", ""),
        token=broker_item.get("broker_api_token", ""),
        account_id=broker_item.get("broker_account_id", ""),
        bw_session=_current_bw_session(),
    )
    runtime_summary["forbidden_reason_guess"] = ""

    if not runtime_input["live_credential_values_available_to_runtime"]:
        result = _result_payload(
            classifier_status=CREDENTIAL_ACCESS_REQUIRED,
            current_stage=CURRENT_STAGE,
            next_stage="repair_runtime_item_fields",
            blockers=["missing broker_api_token_or_account_or_contract_fields"],
            safe_next_action=(
                "Fix the Bitwarden item fields "
                "broker_api_token/broker_account_id/endpoint/environment/allowed_mode."
            ),
        )
        payload = _compose_payload(runtime_input, result, runtime_summary)
        payload["runtime_summary"]["safe_next_action"] = result["safe_next_action"]
        return _write_artifacts(payload, state_output, report_output, write_report)

    if (
        not runtime_input["endpoint_is_oanda_fxtrade"]
        or not runtime_input["environment_is_live"]
        or not runtime_input["allowed_mode_is_micro_live_only"]
    ):
        runtime_summary["forbidden_reason_guess"] = "oanda_live_runtime_contract_mismatch"
        result = _result_payload(
            classifier_status=REPAIR_REQUIRED,
            current_stage=CURRENT_STAGE,
            next_stage="repair_runtime_contract",
            blockers=[
                "runtime contract must match live endpoint, live environment and allowed mode",
            ],
            safe_next_action=(
                "Repair runtime item contract to live endpoint, live env, and controlled mode."
            ),
        )
        payload = _compose_payload(runtime_input, result, runtime_summary)
        payload["runtime_summary"]["safe_next_action"] = result["safe_next_action"]
        return _write_artifacts(payload, state_output, report_output, write_report)

    status = READONLY_PROBE_READY
    safe_next_action = "Run read-only probes."
    runtime_summary["forbidden_reason_guess"] = ""

    token = broker_item["broker_api_token"]
    account_id = broker_item["broker_account_id"]
    endpoint = broker_item["endpoint"]

    accounts_payload, accounts_status, accounts_blocker = _safe_oanda_request(
        "GET",
        f"{endpoint}/v3/accounts",
        token,
        runtime_summary["redacted_account_id"],
        request_callable=_http_get,
    )
    if accounts_blocker:
        status = REPAIR_REQUIRED
        blockers = [f"accounts_probe_blocked:{accounts_blocker}"]
        safe_next_action = "Repair accounts probe guardrail violation."
        runtime_summary["forbidden_reason_guess"] = accounts_blocker
        runtime_input["accounts_probe_called"] = False
        runtime_summary["accounts_status_code"] = None
        runtime_summary["account_list_count"] = 0
        result = _result_payload(
            classifier_status=status,
            current_stage=CURRENT_STAGE,
            next_stage="repair_probe_guardrails",
            blockers=blockers,
            safe_next_action=safe_next_action,
        )
        payload = _compose_payload(runtime_input, result, runtime_summary)
        payload["runtime_summary"]["safe_next_action"] = safe_next_action
        return _write_artifacts(payload, state_output, report_output, write_report)

    runtime_input["broker_api_called"] = True
    runtime_input["accounts_probe_called"] = True
    runtime_input["read_only_probe_count"] = runtime_summary["read_only_probe_count"] + 1
    runtime_summary["accounts_status_code"] = accounts_status

    if accounts_status in (401, 403):
        status = ACCOUNT_LIST_FORBIDDEN
        blockers = ["accounts endpoint returned 401 or 403"]
        safe_next_action = (
            "Review Bitwarden token audience and scope before any owner trade action."
        )
        runtime_summary["configured_account_visible"] = False
        runtime_summary["account_list_count"] = 0
        result = _result_payload(
            classifier_status=status,
            current_stage=CURRENT_STAGE,
            next_stage="fix_token_list_permission",
            blockers=blockers,
            safe_next_action=safe_next_action,
        )
        payload = _compose_payload(runtime_input, result, runtime_summary)
        payload["runtime_summary"]["safe_next_action"] = safe_next_action
        return _write_artifacts(payload, state_output, report_output, write_report)

    if accounts_status is None or accounts_status >= 500:
        status = BROKER_UNAVAILABLE
        blockers = ["accounts endpoint unavailable"]
        safe_next_action = "Retry once network or broker endpoint is available."
        runtime_summary["configured_account_visible"] = False
        runtime_summary["account_list_count"] = 0
        result = _result_payload(
            classifier_status=status,
            current_stage=CURRENT_STAGE,
            next_stage="retry_readonly_probe",
            blockers=blockers,
            safe_next_action=safe_next_action,
        )
        payload = _compose_payload(runtime_input, result, runtime_summary)
        payload["runtime_summary"]["safe_next_action"] = safe_next_action
        return _write_artifacts(payload, state_output, report_output, write_report)

    if not isinstance(accounts_payload, dict):
        status = REPAIR_REQUIRED
        blockers = ["accounts payload malformed"]
        safe_next_action = "Repair broker response shape handling for account list."
        result = _result_payload(
            classifier_status=status,
            current_stage=CURRENT_STAGE,
            next_stage="repair_payload_parser",
            blockers=blockers,
            safe_next_action=safe_next_action,
        )
        payload = _compose_payload(runtime_input, result, runtime_summary)
        payload["runtime_summary"]["safe_next_action"] = safe_next_action
        return _write_artifacts(payload, state_output, report_output, write_report)

    accounts_data = accounts_payload.get("accounts", [])
    if not isinstance(accounts_data, list):
        status = REPAIR_REQUIRED
        blockers = ["accounts payload must expose an accounts list"]
        safe_next_action = "Repair parser for OANDA accounts payload shape."
        result = _result_payload(
            classifier_status=status,
            current_stage=CURRENT_STAGE,
            next_stage="repair_payload_parser",
            blockers=blockers,
            safe_next_action=safe_next_action,
        )
        payload = _compose_payload(runtime_input, result, runtime_summary)
        payload["runtime_summary"]["safe_next_action"] = safe_next_action
        return _write_artifacts(payload, state_output, report_output, write_report)

    runtime_summary["account_list_count"] = len(accounts_data)
    runtime_summary["configured_account_visible"] = any(
        isinstance(account, Mapping)
        and str(account.get("id", "")).strip() == str(account_id).strip()
        for account in accounts_data
    )

    if not runtime_summary["configured_account_visible"]:
        status = ACCOUNT_NOT_VISIBLE_TO_TOKEN
        blockers = ["configured account is not visible to token"]
        safe_next_action = (
            "Use the credential bound to the configured account or update item account id."
        )
        result = _result_payload(
            classifier_status=status,
            current_stage=CURRENT_STAGE,
            next_stage="repair_runtime_account_binding",
            blockers=blockers,
            safe_next_action=safe_next_action,
        )
        payload = _compose_payload(runtime_input, result, runtime_summary)
        payload["runtime_summary"]["safe_next_action"] = safe_next_action
        return _write_artifacts(payload, state_output, report_output, write_report)

    summary_payload, summary_status, summary_blocker = _safe_oanda_request(
        "GET",
        f"{endpoint}/v3/accounts/{account_id}/summary",
        token,
        runtime_summary["redacted_account_id"],
        request_callable=_http_get,
    )
    if summary_blocker:
        status = REPAIR_REQUIRED
        blockers = [f"summary_probe_blocked:{summary_blocker}"]
        safe_next_action = "Repair summary guardrail violation."
        runtime_input["summary_probe_called"] = False
        runtime_summary["summary_status_code"] = None
        result = _result_payload(
            classifier_status=status,
            current_stage=CURRENT_STAGE,
            next_stage="repair_probe_guardrails",
            blockers=blockers,
            safe_next_action=safe_next_action,
        )
        payload = _compose_payload(runtime_input, result, runtime_summary)
        payload["runtime_summary"]["safe_next_action"] = safe_next_action
        return _write_artifacts(payload, state_output, report_output, write_report)

    runtime_input["summary_probe_called"] = True
    runtime_input["read_only_probe_count"] = runtime_summary["read_only_probe_count"] + 1
    runtime_summary["summary_status_code"] = summary_status

    if summary_status in (401, 403):
        status = ACCOUNT_SUMMARY_FORBIDDEN
        blockers = ["account summary endpoint returned 401 or 403"]
        safe_next_action = (
            "Token can list accounts but has no permission to account summary."
        )
    elif summary_status is None or summary_status >= 500:
        status = BROKER_UNAVAILABLE
        blockers = ["account summary endpoint unavailable"]
        safe_next_action = "Retry when broker endpoint/network is available."
    elif summary_status == 200 and isinstance(summary_payload, dict):
        status = ACCOUNT_VISIBLE_SUMMARY_OK_ORDER_FORBIDDEN
        blockers = []
        safe_next_action = (
            "Order placement is likely blocked; do not retry order. Review token scopes."
        )
    else:
        status = REPAIR_REQUIRED
        blockers = ["summary payload malformed or empty"]
        safe_next_action = "Repair summary response shape."

    runtime_summary["forbidden_reason_guess"] = "" if not blockers else blockers[0]
    runtime_input["read_only_probe_count"] = runtime_summary["read_only_probe_count"]
    result = _result_payload(
        classifier_status=status,
        current_stage=CURRENT_STAGE,
        next_stage=_next_stage_for_status(status),
        blockers=blockers,
        safe_next_action=safe_next_action,
    )
    payload = _compose_payload(runtime_input, result, runtime_summary)
    payload["runtime_summary"]["safe_next_action"] = safe_next_action
    payload["input"]["read_only_probe_count"] = runtime_summary["read_only_probe_count"]
    payload["runtime_summary"]["read_only_probe_count"] = runtime_summary["read_only_probe_count"]
    payload["runtime_summary"]["safe_next_action"] = safe_next_action
    payload["input"]["broker_api_called"] = runtime_input["broker_api_called"]

    return _write_artifacts(
        payload,
        state_output,
        report_output,
        write_report,
        redact_token=token,
        redact_account_id=account_id,
        redact_session=_current_bw_session(),
    )


def _initial_input(owner_present: bool) -> dict[str, Any]:
    return {
        "owner_flag_present": owner_present,
        "bw_session_present": False,
        "bitwarden_cli_available": False,
        "bitwarden_item_read_success": False,
        "live_credential_values_available_to_runtime": False,
        "endpoint_is_oanda_fxtrade": False,
        "environment_is_live": False,
        "allowed_mode_is_micro_live_only": False,
        "readonly_get_only_enforced": True,
        "orders_endpoint_blocked": True,
        "broker_api_called": False,
        "accounts_probe_called": False,
        "summary_probe_called": False,
        "order_endpoint_called": False,
        "post_request_called": False,
        "live_order_execution": False,
        "money_movement": False,
        "scheduler_started": False,
        "daemon_started": False,
        "webhook_started": False,
        "read_only_probe_count": 0,
    }


def _initial_summary() -> dict[str, Any]:
    return {
        "accounts_status_code": None,
        "summary_status_code": None,
        "configured_account_visible": False,
        "account_list_count": 0,
        "read_only_probe_count": 0,
        "forbidden_reason_guess": "",
        "redacted_account_id": REDACTED_ACCOUNT_ID,
        "redacted_endpoint": OANDA_LIVE_ENDPOINT,
        "safe_next_action": "Run classifier.",
    }


def _run_defaults(
    runtime_input: dict[str, Any], runtime_summary: dict[str, Any]
) -> tuple[str, list[str], str]:
    return "", [], "Run with owner runtime flag."


def _result_payload(
    *,
    classifier_status: str,
    current_stage: str,
    next_stage: str,
    blockers: list[str],
    safe_next_action: str,
) -> dict[str, Any]:
    return {
        "classifier_status": classifier_status,
        "current_stage": current_stage,
        "next_stage": next_stage,
        "blockers": list(blockers),
        "safe_next_action": safe_next_action,
    }


def _next_stage_for_status(classifier_status: str) -> str:
    return {
        ACCOUNT_LIST_FORBIDDEN: "owner_fix_broker_account_acl",
        ACCOUNT_SUMMARY_FORBIDDEN: "owner_fix_broker_summary_acl",
        ACCOUNT_NOT_VISIBLE_TO_TOKEN: "owner_confirm_runtime_item_account",
        ACCOUNT_VISIBLE_SUMMARY_OK_ORDER_FORBIDDEN: "owner_review_403_classification",
        BROKER_UNAVAILABLE: "owner_retry_when_broker_available",
        CREDENTIAL_ACCESS_REQUIRED: "owner_unlock_bitwarden_session",
        REPAIR_REQUIRED: "owner_repair_runtime_item_or_parser",
        READONLY_PROBE_READY: "owner_run_readonly_probes",
        OWNER_RUNTIME_REQUIRED: "owner_run_with_runtime_flag",
    }.get(classifier_status, "owner_review_403_classification")


def _compose_payload(
    input_payload: Mapping[str, Any],
    result_payload: Mapping[str, Any],
    summary_payload: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "module": MODULE,
        "packet_id": PACKET_ID,
        "input": dict(input_payload),
        "result": dict(result_payload),
        "runtime_summary": dict(summary_payload),
    }


def _write_artifacts(
    payload: dict[str, Any],
    state_output: Path,
    report_output: Path,
    write_report: bool,
    *,
    redact_token: str = "",
    redact_account_id: str = "",
    redact_session: str = "",
) -> dict[str, Any]:
    payload = _redact_payload(
        payload,
        token=redact_token,
        account_id=redact_account_id,
        bw_session=redact_session,
    )

    state_output = Path(state_output)
    report_output = Path(report_output)
    state_output.parent.mkdir(parents=True, exist_ok=True)
    state_output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if write_report:
        report_output.parent.mkdir(parents=True, exist_ok=True)
        report_output.write_text(_build_report(payload), encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return payload


def _read_broker_runtime_item() -> tuple[dict[str, str], bool]:
    command = ["bw", "get", "item", LIVEOFX_ITEM_REF]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError:
        return {}, False

    if completed.returncode != 0 or not completed.stdout:
        return {}, False

    raw = completed.stdout.strip()
    if not raw:
        return {}, False
    return _parse_broker_runtime_item(raw), True


def _parse_broker_runtime_item(raw: str) -> dict[str, str]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    fields = _flatten_bitwarden_fields(parsed)
    return {
        "broker_api_token": fields.get("broker_api_token", "").strip(),
        "broker_account_id": fields.get("broker_account_id", "").strip(),
        "endpoint": fields.get("endpoint", "").strip(),
        "environment": fields.get("environment", "").strip(),
        "allowed_mode": fields.get("allowed_mode", "").strip(),
    }


def _flatten_bitwarden_fields(raw_item: Mapping[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    raw_fields = raw_item.get("fields", [])
    if isinstance(raw_fields, list):
        for entry in raw_fields:
            if not isinstance(entry, Mapping):
                continue
            key = str(entry.get("name", "")).strip()
            if not key:
                continue
            result[key] = str(entry.get("value", "")).strip()
    elif isinstance(raw_fields, Mapping):
        for key, value in raw_fields.items():
            result[str(key).strip()] = str(value).strip()
    for key in ("broker_api_token", "broker_account_id", "endpoint", "environment", "allowed_mode"):
        if key not in result and key in raw_item:
            result[key] = str(raw_item.get(key, "")).strip()
    return result


def _safe_oanda_request(
    method: str,
    url: str,
    api_token: str,
    redacted_account_id: str,
    request_callable: HttpGetCallable | None = None,
) -> tuple[dict[str, Any] | None, int | None, str | None]:
    method_upper = str(method or "").strip().upper()
    parsed = urlparse(url)
    clean_path = (parsed.path or "").lower()

    if method_upper != READ_ONLY_METHOD:
        return None, None, "post_or_mutating_method_blocked"
    if parsed.scheme.lower() != "https" or f"{parsed.scheme}://{parsed.netloc}".lower() != OANDA_LIVE_ENDPOINT:
        return None, None, "unsafe_endpoint_blocked"
    if "/orders" in clean_path:
        return None, None, "orders_endpoint_blocked"

    headers = {"Accept": "application/json", "Authorization": f"Bearer {api_token}"}
    getter = request_callable or _default_http_get
    try:
        payload, status = getter(url, headers)
    except Exception as exc:  # noqa: BLE001
        return None, None, str(exc)
    if status is not None and status >= 500:
        return payload if isinstance(payload, dict) else None, status, None
    return payload if isinstance(payload, dict) else None, status, None

def _default_http_get(url: str, headers: Mapping[str, str]) -> tuple[dict[str, Any] | None, int | None]:
    request = Request(url, headers=dict(headers), method="GET")
    try:
        with urlopen(request, timeout=10) as response:
            raw = response.read().decode("utf-8")
            status_code = getattr(response, "status", None)
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        status_code = getattr(exc, "code", None)
    except URLError:
        return None, None

    try:
        payload = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return None, status_code

    if not isinstance(payload, dict):
        return None, status_code
    return payload, status_code


def _current_bw_session() -> str:
    session = os.environ.get("BW_SESSION", "")
    if session is None:
        return ""
    return str(session)


def _redact_text(text: Any, *, token: str = "", account_id: str = "", bw_session: str = "") -> Any:
    if not isinstance(text, str):
        return text
    redacted = text
    if token:
        redacted = redacted.replace(token, REDACTED_TOKEN)
        redacted = re.sub(rf"(?i)bearer\\s+{re.escape(token)}", f"Bearer {REDACTED_TOKEN}", redacted)
        redacted = redacted.replace(f"Bearer {token}", f"Bearer {REDACTED_TOKEN}")
    if account_id:
        redacted = redacted.replace(account_id, REDACTED_ACCOUNT_ID)
    if bw_session:
        redacted = redacted.replace(bw_session, REDACTED_SESSION)
    return redacted


def _redact_payload(
    payload: Mapping[str, Any],
    *, token: str, account_id: str, bw_session: str,
) -> dict[str, Any]:
    def _redact(value: Any) -> Any:
        if isinstance(value, str):
            return _redact_text(
                value,
                token=token,
                account_id=account_id,
                bw_session=bw_session,
            )
        if isinstance(value, list):
            return [_redact(item) for item in value]
        if isinstance(value, dict):
            new_value: dict[str, Any] = {}
            for key, child in value.items():
                lowered_key = str(key).lower()
                if lowered_key == "authorization":
                    new_value[key] = "REDACTED_TOKEN"
                else:
                    new_value[key] = _redact(child)
            return new_value
        return value

    return _redact(dict(payload))


def _build_report(payload: Mapping[str, Any]) -> str:
    result = payload["result"]
    input_payload = payload["input"]
    summary = payload["runtime_summary"]
    blockers = "\n".join(f"- {item}" for item in result.get("blockers", [])) or "- (none)"
    allowed_actions = (
        "- GET https://api-fxtrade.oanda.com/v3/accounts\n"
        "- GET https://api-fxtrade.oanda.com/v3/accounts/{account_id}/summary\n"
    )
    return (
        "# Forex OANDA Live 403 Read-Only Classifier V1 Report\n\n"
        f"- module: {payload['module']}\n"
        f"- packet_id: {payload['packet_id']}\n"
        f"- classifier_status: {result['classifier_status']}\n"
        f"- current_stage: {result['current_stage']}\n"
        f"- next_stage: {result['next_stage']}\n"
        f"- safe_next_action: {result['safe_next_action']}\n"
        "- blockers:\n"
        f"{blockers}\n\n"
        "## Input booleans\n"
        f"- owner_flag_present: {input_payload.get('owner_flag_present')}\n"
        f"- bw_session_present: {input_payload.get('bw_session_present')}\n"
        f"- bitwarden_cli_available: {input_payload.get('bitwarden_cli_available')}\n"
        f"- bitwarden_item_read_success: {input_payload.get('bitwarden_item_read_success')}\n"
        f"- live_credential_values_available_to_runtime: {input_payload.get('live_credential_values_available_to_runtime')}\n"
        f"- endpoint_is_oanda_fxtrade: {input_payload.get('endpoint_is_oanda_fxtrade')}\n"
        f"- environment_is_live: {input_payload.get('environment_is_live')}\n"
        f"- allowed_mode_is_micro_live_only: {input_payload.get('allowed_mode_is_micro_live_only')}\n"
        f"- readonly_get_only_enforced: {input_payload.get('readonly_get_only_enforced')}\n"
        f"- orders_endpoint_blocked: {input_payload.get('orders_endpoint_blocked')}\n"
        f"- broker_api_called: {input_payload.get('broker_api_called')}\n"
        f"- accounts_probe_called: {input_payload.get('accounts_probe_called')}\n"
        f"- summary_probe_called: {input_payload.get('summary_probe_called')}\n"
        f"- order_endpoint_called: {input_payload.get('order_endpoint_called')}\n"
        f"- post_request_called: {input_payload.get('post_request_called')}\n"
        f"- live_order_execution: {input_payload.get('live_order_execution')}\n"
        f"- money_movement: {input_payload.get('money_movement')}\n"
        f"- scheduler_started: {input_payload.get('scheduler_started')}\n"
        f"- daemon_started: {input_payload.get('daemon_started')}\n"
        f"- webhook_started: {input_payload.get('webhook_started')}\n\n"
        "## Allowed probes\n"
        f"{allowed_actions}\n"
        "## Forbidden actions\n"
        "- POST requests\n"
        "- endpoints outside api-fxtrade\n"
        "- PUT/PATCH/DELETE\n"
        "- /orders endpoint\n"
        "- any live order or money movement\n"
        "- scheduler / daemon / webhook startup\n\n"
        "## Status taxonomy\n"
        f"- {OWNER_RUNTIME_REQUIRED}\n"
        f"- {CREDENTIAL_ACCESS_REQUIRED}\n"
        f"- {READONLY_PROBE_READY}\n"
        f"- {ACCOUNT_LIST_FORBIDDEN}\n"
        f"- {ACCOUNT_SUMMARY_FORBIDDEN}\n"
        f"- {ACCOUNT_NOT_VISIBLE_TO_TOKEN}\n"
        f"- {ACCOUNT_VISIBLE_SUMMARY_OK_ORDER_FORBIDDEN}\n"
        f"- {BROKER_UNAVAILABLE}\n"
        f"- {REPAIR_REQUIRED}\n\n"
        "## Runtime summary\n"
        f"- accounts_status_code: {summary.get('accounts_status_code')}\n"
        f"- summary_status_code: {summary.get('summary_status_code')}\n"
        f"- configured_account_visible: {summary.get('configured_account_visible')}\n"
        f"- account_list_count: {summary.get('account_list_count')}\n"
        f"- read_only_probe_count: {summary.get('read_only_probe_count')}\n"
        f"- forbidden_reason_guess: {summary.get('forbidden_reason_guess')}\n"
        f"- redacted_account_id: {summary.get('redacted_account_id')}\n"
        f"- redacted_endpoint: {summary.get('redacted_endpoint')}\n\n"
        "## Validators\n"
        "- python -m py_compile scripts/forex_delivery/run_forex_oanda_live_403_readonly_classifier_v1.py\n"
        "- python -m pytest tests/forex_engine/test_forex_oanda_live_403_readonly_classifier_v1.py -q\n"
        "- python scripts/forex_delivery/run_forex_oanda_live_403_readonly_classifier_v1.py\n"
    )


def _parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description="AIOS OANDA live 403 read-only classifier.",
    )
    parser.add_argument(OWNER_RUNTIME_FLAG, action="store_true")
    parser.add_argument(
        "--state-output",
        default=str(SCRIPT_STATE_PATH),
    )
    parser.add_argument(
        "--report-output",
        default=str(SCRIPT_REPORT_PATH),
    )
    parser.add_argument("--no-report", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_arguments(argv)
    run_forex_oanda_live_403_readonly_classifier_v1(
        owner_approved_readonly_live_403_classifier=args.__dict__.get(
            OWNER_RUNTIME_FLAG.lstrip("-").replace("-", "_")
        )
        or False,
        state_output=Path(args.state_output),
        report_output=Path(args.report_output),
        write_report=not args.no_report,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
