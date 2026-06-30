"""OANDA live account binding repair utility."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

PACKET_ID = "AIOS-FOREX-OANDA-LIVE-ACCOUNT-BINDING-REPAIR-V1"
MODULE = "run_forex_oanda_live_account_binding_repair_v1"
STATE_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_OANDA_LIVE_ACCOUNT_BINDING_REPAIR_V1_STATE.json"
)
REPORT_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_OANDA_LIVE_ACCOUNT_BINDING_REPAIR_V1_REPORT.md"
)

LIVEOFX_ITEM_REF = "AIOS / OANDA / Live / Broker Runtime"
OANDA_LIVE_ENDPOINT = "https://api-fxtrade.oanda.com"
OANDA_ENDPOINT_ACCOUNTS = f"{OANDA_LIVE_ENDPOINT}/v3/accounts"
BROKER_ACCOUNT_ID_FIELD = "broker_account_id"
BROKER_TOKEN_FIELD = "broker_api_token"
FIELD_ENDPOINT = "endpoint"

ACCOUNT_BINDING_REPAIR_OWNER_RUNTIME_REQUIRED = (
    "ACCOUNT_BINDING_REPAIR_OWNER_RUNTIME_REQUIRED"
)
ACCOUNT_BINDING_REPAIR_CREDENTIAL_ACCESS_REQUIRED = (
    "ACCOUNT_BINDING_REPAIR_CREDENTIAL_ACCESS_REQUIRED"
)
ACCOUNT_BINDING_REPAIR_INSPECT_READY = "ACCOUNT_BINDING_REPAIR_INSPECT_READY"
ACCOUNT_BINDING_REPAIR_CONFIGURED_ACCOUNT_VISIBLE = (
    "ACCOUNT_BINDING_REPAIR_CONFIGURED_ACCOUNT_VISIBLE"
)
ACCOUNT_BINDING_REPAIR_CONFIGURED_ACCOUNT_NOT_VISIBLE = (
    "ACCOUNT_BINDING_REPAIR_CONFIGURED_ACCOUNT_NOT_VISIBLE"
)
ACCOUNT_BINDING_REPAIR_UPDATE_READY = "ACCOUNT_BINDING_REPAIR_UPDATE_READY"
ACCOUNT_BINDING_REPAIR_UPDATE_APPLIED = "ACCOUNT_BINDING_REPAIR_UPDATE_APPLIED"
ACCOUNT_BINDING_REPAIR_UPDATE_FAILED = "ACCOUNT_BINDING_REPAIR_UPDATE_FAILED"
ACCOUNT_BINDING_REPAIR_INDEX_INVALID = "ACCOUNT_BINDING_REPAIR_INDEX_INVALID"
ACCOUNT_BINDING_REPAIR_BROKER_UNAVAILABLE = "ACCOUNT_BINDING_REPAIR_BROKER_UNAVAILABLE"

UPDATE_STATUS_UPDATED = "UPDATED"
UPDATE_STATUS_FAILED = "FAILED"
UPDATE_STATUS_INDEX_INVALID = "INDEX_INVALID"

READONLY_INSPECT_FLAG = "--owner-approved-readonly-account-binding-inspect"
UPDATE_FLAG = "--owner-approved-update-bitwarden-account-binding"
INDEX_ARG = "--select-visible-account-index"

SAFE_OANDA_GET = "GET"
REDACTION_TOKEN = "REDACTED_TOKEN"
REDACTION_ACCOUNT = "REDACTED_ACCOUNT_ID"
REDACTION_SESSION = "REDACTED_SESSION"


HttpGetCallable = Callable[
    [str, Mapping[str, str]], tuple[dict[str, Any] | None, int | None]
]
ReadItemCallable = Callable[[], tuple[dict[str, Any], bool]]
UpdateItemCallable = Callable[[dict[str, Any], str], bool]


def run_forex_oanda_live_account_binding_repair_v1(
    *,
    owner_approved_readonly_account_binding_inspect: bool = False,
    owner_approved_update_bitwarden_account_binding: bool = False,
    select_visible_account_index: int | None = None,
    state_output: Path = STATE_PATH,
    report_output: Path = REPORT_PATH,
    write_report: bool = True,
    _safe_http_get: HttpGetCallable | None = None,
    _read_bw_item: ReadItemCallable | None = None,
    _write_bw_item: UpdateItemCallable | None = None,
) -> dict[str, Any]:
    runtime_input = _initial_input(
        owner_approved_readonly_account_binding_inspect
        or owner_approved_update_bitwarden_account_binding
    )
    runtime_summary = _initial_summary()

    if (
        not owner_approved_readonly_account_binding_inspect
        and not owner_approved_update_bitwarden_account_binding
    ):
        result = _build_result(
            status=ACCOUNT_BINDING_REPAIR_OWNER_RUNTIME_REQUIRED,
            safe_next_action=(
                "Run with "
                f"{READONLY_INSPECT_FLAG} for read-only inspection or "
                f"{UPDATE_FLAG} plus {INDEX_ARG} for live account binding repair."
            ),
            blockers=["owner runtime flag is required"],
        )
        payload = _compose_payload(runtime_input, result, runtime_summary)
        return _write_artifacts(
            payload=payload,
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
        )

    runtime_input["bitwarden_cli_available"] = shutil.which("bw") is not None
    runtime_input["bw_session_present"] = bool(os.environ.get("BW_SESSION"))
    runtime_summary["safe_next_action"] = "Set BW_SESSION and rerun with owner runtime flag."

    if not runtime_input["bw_session_present"]:
        result = _build_result(
            status=ACCOUNT_BINDING_REPAIR_CREDENTIAL_ACCESS_REQUIRED,
            safe_next_action="Set BW_SESSION and rerun the same owner runtime command.",
            blockers=["bw session is required"],
        )
        runtime_summary["safe_next_action"] = result["safe_next_action"]
        payload = _compose_payload(runtime_input, result, runtime_summary)
        payload["runtime_summary"]["safe_next_action"] = result["safe_next_action"]
        return _write_artifacts(
            payload=payload,
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
        )

    if not runtime_input["bitwarden_cli_available"]:
        result = _build_result(
            status=ACCOUNT_BINDING_REPAIR_CREDENTIAL_ACCESS_REQUIRED,
            safe_next_action="Install Bitwarden CLI and rerun with the owner runtime flag.",
            blockers=["bitwarden cli is required"],
        )
        runtime_summary["safe_next_action"] = result["safe_next_action"]
        payload = _compose_payload(runtime_input, result, runtime_summary)
        return _write_artifacts(
            payload=payload,
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
        )

    read_item = _read_bw_item or _read_broker_runtime_item
    broker_runtime_item, runtime_input["bitwarden_item_read_success"] = read_item()
    runtime_input["accounts_probe_called"] = bool(
        runtime_input["bw_session_present"]
        and runtime_input["bitwarden_cli_available"]
        and runtime_input["bitwarden_item_read_success"]
    )

    if not runtime_input["bitwarden_item_read_success"]:
        result = _build_result(
            status=ACCOUNT_BINDING_REPAIR_CREDENTIAL_ACCESS_REQUIRED,
            safe_next_action="Read Bitwarden item AIOS / OANDA / Live / Broker Runtime.",
            blockers=["bitwarden runtime item read failed"],
        )
        runtime_summary["safe_next_action"] = result["safe_next_action"]
        payload = _compose_payload(runtime_input, result, runtime_summary)
        return _write_artifacts(
            payload,
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
        )

    item_values = _extract_runtime_fields(broker_runtime_item)
    token = item_values.get(BROKER_TOKEN_FIELD, "")
    configured_account = item_values.get(BROKER_ACCOUNT_ID_FIELD, "")
    endpoint = item_values.get(FIELD_ENDPOINT, OANDA_LIVE_ENDPOINT)
    if not token or not configured_account or not endpoint:
        result = _build_result(
            status=ACCOUNT_BINDING_REPAIR_CREDENTIAL_ACCESS_REQUIRED,
            safe_next_action=(
                "Repair Bitwarden item to include broker_api_token, broker_account_id and endpoint."
            ),
            blockers=["runtime item is missing required field values"],
        )
        runtime_summary["safe_next_action"] = result["safe_next_action"]
        payload = _compose_payload(runtime_input, result, runtime_summary)
        return _write_artifacts(
            payload=payload,
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            redact_token=token,
            redact_account=configured_account,
            redact_session=os.environ.get("BW_SESSION", ""),
        )

    if owner_approved_update_bitwarden_account_binding:
        runtime_input["bitwarden_update_requested"] = True

    runtime_summary["safe_next_action"] = "Run read-only account list probe."
    accounts_payload, accounts_status, blocker = _safe_oanda_get_accounts(
        endpoint=endpoint,
        token=token,
        safe_http_get=_safe_http_get,
    )
    if blocker:
        status = ACCOUNT_BINDING_REPAIR_BROKER_UNAVAILABLE
        runtime_input["accounts_probe_called"] = False
        runtime_summary["accounts_status_code"] = None
        result = _build_result(
            status=status,
            safe_next_action="Retry read-only account probe when broker is reachable.",
            blockers=[f"accounts_probe_blocked:{blocker}"],
        )
        runtime_summary["safe_next_action"] = result["safe_next_action"]
        payload = _compose_payload(runtime_input, result, runtime_summary)
        return _write_artifacts(
            payload=payload,
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            redact_token=token,
            redact_account=configured_account,
            redact_session=os.environ.get("BW_SESSION", ""),
        )

    runtime_input["broker_api_called"] = True
    runtime_input["accounts_probe_called"] = True
    runtime_summary["accounts_status_code"] = accounts_status
    runtime_summary["safe_next_action"] = "Run read-only account list probe."

    if accounts_status != 200:
        status = (
            ACCOUNT_BINDING_REPAIR_BROKER_UNAVAILABLE
            if accounts_status is None or accounts_status >= 500
            else ACCOUNT_BINDING_REPAIR_CREDENTIAL_ACCESS_REQUIRED
        )
        safe_next_action = (
            "Fix token visibility and rerun with owner runtime flag."
            if status == ACCOUNT_BINDING_REPAIR_CREDENTIAL_ACCESS_REQUIRED
            else "Retry when OANDA live endpoint is available."
        )
        result = _build_result(
            status=status,
            safe_next_action=safe_next_action,
            blockers=[f"accounts_status_code:{accounts_status}"],
        )
        runtime_summary["safe_next_action"] = safe_next_action
        payload = _compose_payload(runtime_input, result, runtime_summary)
        return _write_artifacts(
            payload=payload,
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            redact_token=token,
            redact_account=configured_account,
            redact_session=os.environ.get("BW_SESSION", ""),
        )

    visible_accounts = _extract_visible_accounts(accounts_payload or {})
    runtime_summary["visible_account_fingerprints"] = [
        _account_fingerprint(account)
        for account in visible_accounts
    ]
    runtime_summary["account_list_count"] = len(visible_accounts)
    runtime_summary["configured_account_fingerprint"] = (
        _account_fingerprint(configured_account) if configured_account else None
    )
    runtime_summary["selected_visible_account_index"] = None
    runtime_summary["selected_account_fingerprint"] = None

    configured_account_visible = configured_account in visible_accounts
    runtime_summary["configured_account_visible"] = configured_account_visible

    if not owner_approved_update_bitwarden_account_binding:
        runtime_input["bitwarden_update_requested"] = False
        runtime_input["bitwarden_update_attempted"] = False
        runtime_input["bitwarden_update_success"] = False

        if configured_account_visible:
            status = ACCOUNT_BINDING_REPAIR_CONFIGURED_ACCOUNT_VISIBLE
            safe_next_action = "Configured account is visible. No update required."
        else:
            status = ACCOUNT_BINDING_REPAIR_CONFIGURED_ACCOUNT_NOT_VISIBLE
            safe_next_action = (
                "Run owner-approved update with selected visible account index when rerun."
            )
        result = _build_result(
            status=status,
            safe_next_action=safe_next_action,
            blockers=[],
        )
        runtime_summary["safe_next_action"] = safe_next_action
        return _write_artifacts(
            payload=_compose_payload(runtime_input, result, runtime_summary),
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            redact_token=token,
            redact_account=configured_account,
            redact_session=os.environ.get("BW_SESSION", ""),
        )

    # Update requested.
    if not visible_accounts:
        result = _build_result(
            status=ACCOUNT_BINDING_REPAIR_CONFIGURED_ACCOUNT_NOT_VISIBLE,
            safe_next_action=(
                "No visible accounts returned; confirm token contract and rerun inspect."
            ),
            blockers=["no accounts found"],
            update_status=UPDATE_STATUS_FAILED,
        )
        runtime_summary["safe_next_action"] = result["safe_next_action"]
        return _write_artifacts(
            payload=_compose_payload(runtime_input, result, runtime_summary),
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            redact_token=token,
            redact_account=configured_account,
            redact_session=os.environ.get("BW_SESSION", ""),
        )

    if select_visible_account_index is None:
        runtime_input["bitwarden_update_attempted"] = False
        result = _build_result(
            status=ACCOUNT_BINDING_REPAIR_INDEX_INVALID,
            safe_next_action=(
                "Provide a valid 1-based visible account index with --select-visible-account-index."
            ),
            blockers=["selected index is required"],
            update_status=UPDATE_STATUS_INDEX_INVALID,
        )
        return _write_artifacts(
            payload=_compose_payload(runtime_input, result, runtime_summary),
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            redact_token=token,
            redact_account=configured_account,
            redact_session=os.environ.get("BW_SESSION", ""),
        )

    if select_visible_account_index < 1 or select_visible_account_index > len(visible_accounts):
        runtime_input["bitwarden_update_attempted"] = True
        result = _build_result(
            status=ACCOUNT_BINDING_REPAIR_INDEX_INVALID,
            safe_next_action=(
                "Use a 1-based index within visible account list bounds."
            ),
            blockers=[f"selected index out of range: {select_visible_account_index}"],
            update_status=UPDATE_STATUS_INDEX_INVALID,
        )
        runtime_summary["selected_visible_account_index"] = select_visible_account_index
        payload = _compose_payload(runtime_input, result, runtime_summary)
        payload["result"]["safe_next_action"] = result["safe_next_action"]
        return _write_artifacts(
            payload=payload,
            state_output=state_output,
            report_output=report_output,
            write_report=write_report,
            redact_token=token,
            redact_account=configured_account,
            redact_session=os.environ.get("BW_SESSION", ""),
        )

    # Valid index path.
    runtime_summary["selected_visible_account_index"] = select_visible_account_index
    selected_account_id = visible_accounts[select_visible_account_index - 1]
    runtime_summary["selected_account_fingerprint"] = _account_fingerprint(
        selected_account_id
    )
    runtime_input["bitwarden_update_attempted"] = True
    updated_item = _apply_broker_account_id_update(
        raw_item=broker_runtime_item,
        new_account_id=selected_account_id,
    )
    update_callable = _write_bw_item if _write_bw_item is None else _write_bw_item
    runtime_input["bitwarden_update_success"] = bool(update_callable(updated_item, select_visible_account_index))

    if runtime_input["bitwarden_update_success"]:
        status = ACCOUNT_BINDING_REPAIR_UPDATE_APPLIED
        update_status = UPDATE_STATUS_UPDATED
        safe_next_action = (
            "Account binding updated. Rerun read-only 403 classifier again with "
            f"{READONLY_INSPECT_FLAG}."
        )
    else:
        status = ACCOUNT_BINDING_REPAIR_UPDATE_FAILED
        update_status = UPDATE_STATUS_FAILED
        safe_next_action = "Update command failed. Re-run with a valid BW_SESSION and retry."

    result = _build_result(
        status=status,
        safe_next_action=safe_next_action,
        blockers=[] if runtime_input["bitwarden_update_success"] else ["bitwarden update failed"],
        update_status=update_status,
    )
    runtime_summary["safe_next_action"] = safe_next_action
    return _write_artifacts(
        payload=_compose_payload(runtime_input, result, runtime_summary),
        state_output=state_output,
        report_output=report_output,
        write_report=write_report,
        redact_token=token,
        redact_account=configured_account,
        redact_session=os.environ.get("BW_SESSION", ""),
    )


def _initial_input(owner_flag_present: bool) -> dict[str, Any]:
    return {
        "owner_flag_present": owner_flag_present,
        "bw_session_present": False,
        "bitwarden_cli_available": False,
        "bitwarden_item_read_success": False,
        "broker_api_called": False,
        "accounts_probe_called": False,
        "bitwarden_update_requested": False,
        "bitwarden_update_attempted": False,
        "bitwarden_update_success": False,
        "order_endpoint_called": False,
        "post_request_called": False,
        "live_order_execution": False,
        "money_movement": False,
        "scheduler_started": False,
        "daemon_started": False,
        "webhook_started": False,
    }


def _initial_summary() -> dict[str, Any]:
    return {
        "accounts_status_code": None,
        "account_list_count": 0,
        "configured_account_visible": False,
        "configured_account_fingerprint": None,
        "visible_account_fingerprints": [],
        "selected_visible_account_index": None,
        "selected_account_fingerprint": None,
        "safe_next_action": "Run with owner runtime flag.",
    }


def _build_result(
    *,
    status: str,
    safe_next_action: str,
    blockers: list[str] | None = None,
    update_status: str = "",
) -> dict[str, Any]:
    return {
        "account_binding_repair_status": status,
        "account_binding_update_status": update_status,
        "safe_next_action": safe_next_action,
        "blockers": list(blockers or []),
    }


def _compose_payload(
    runtime_input: Mapping[str, Any],
    result: Mapping[str, Any],
    runtime_summary: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "module": MODULE,
        "packet_id": PACKET_ID,
        "input": dict(runtime_input),
        "result": dict(result),
        "runtime_summary": dict(runtime_summary),
    }


def _write_artifacts(
    *,
    payload: dict[str, Any],
    state_output: Path,
    report_output: Path,
    write_report: bool,
    redact_token: str = "",
    redact_account: str = "",
    redact_session: str = "",
) -> dict[str, Any]:
    sanitized_payload = _redact_payload(
        payload,
        token=redact_token,
        account_id=redact_account,
        bw_session=redact_session,
    )
    state_output.parent.mkdir(parents=True, exist_ok=True)
    state_output.write_text(
        json.dumps(sanitized_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if write_report:
        report_output.parent.mkdir(parents=True, exist_ok=True)
        report_output.write_text(
            _build_report(sanitized_payload),
            encoding="utf-8",
        )
    print(json.dumps(sanitized_payload, sort_keys=True))
    return sanitized_payload


def _safe_oanda_get_accounts(
    *,
    endpoint: str,
    token: str,
    safe_http_get: HttpGetCallable | None = None,
) -> tuple[dict[str, Any] | None, int | None, str | None]:
    getter = safe_http_get or _default_http_get
    return _safe_oanda_request(
        SAFE_OANDA_GET,
        f"{endpoint.rstrip('/')}/v3/accounts",
        token,
        getter= getter,
    )


def _safe_oanda_request(
    method: str,
    url: str,
    token: str,
    *,
    getter: HttpGetCallable,
) -> tuple[dict[str, Any] | None, int | None, str | None]:
    method_normalized = str(method or "").upper().strip()
    parsed = urlparse(url)
    target = f"{parsed.scheme}://{parsed.netloc}".lower()
    path = (parsed.path or "").lower()

    if method_normalized != SAFE_OANDA_GET:
        return None, None, "post_or_mutating_method_blocked"

    if not parsed.scheme or target != OANDA_LIVE_ENDPOINT.lower():
        return None, None, "unsafe_endpoint_blocked"

    if "/orders" in path:
        return None, None, "orders_endpoint_blocked"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "aios-oanda-account-binding-repair/1.0",
    }
    try:
        payload, status = getter(url, headers)
    except TypeError:
        # Defensive fallback if tests pass callables with a different signature.
        payload, status = getter(url, {})  # type: ignore[misc]

    return payload, status, None


def _default_http_get(url: str, headers: Mapping[str, str]) -> tuple[dict[str, Any] | None, int | None]:
    request = Request(url, headers=dict(headers), method="GET")
    try:
        with urlopen(request, timeout=10) as response:
            raw = response.read().decode("utf-8")
            status = getattr(response, "status", None)
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        status = getattr(exc, "code", None)
    except URLError:
        return None, None

    try:
        payload = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return None, status

    if not isinstance(payload, dict):
        return None, status
    return payload, status


def _extract_runtime_fields(item: Mapping[str, Any]) -> dict[str, str]:
    raw_fields: dict[str, str] = {}
    fields = item.get("fields")
    if isinstance(fields, list):
        for entry in fields:
            if not isinstance(entry, Mapping):
                continue
            key = str(entry.get("name", "")).strip()
            value = str(entry.get("value", "")).strip()
            if not key:
                continue
            raw_fields[key] = value
    elif isinstance(fields, Mapping):
        for key, value in fields.items():
            raw_fields[str(key).strip()] = str(value).strip()

    for key in (
        BROKER_TOKEN_FIELD,
        BROKER_ACCOUNT_ID_FIELD,
        FIELD_ENDPOINT,
    ):
        if not raw_fields.get(key):
            raw_fields[key] = str(item.get(key, "")).strip()

    return raw_fields


def _extract_visible_accounts(payload: Mapping[str, Any]) -> list[str]:
    accounts = payload.get("accounts")
    if not isinstance(accounts, list):
        return []
    visible: list[str] = []
    for account in accounts:
        if not isinstance(account, Mapping):
            continue
        account_id = str(account.get("id", "")).strip()
        if account_id:
            visible.append(account_id)
    return visible


def _account_fingerprint(account_id: str) -> str:
    digest = hashlib.sha256(account_id.encode("utf-8")).hexdigest()
    return f"sha256:{digest[:12]}"


def _apply_broker_account_id_update(
    *,
    raw_item: Mapping[str, Any],
    new_account_id: str,
) -> dict[str, Any]:
    updated = dict(raw_item)
    fields = updated.get("fields")
    updated_account = False

    if isinstance(fields, list):
        normalized_fields = list(fields)
        for field in normalized_fields:
            if isinstance(field, Mapping) and str(field.get("name", "")).strip() == BROKER_ACCOUNT_ID_FIELD:
                if isinstance(field, dict):
                    updated_value = dict(field)
                    updated_value["value"] = new_account_id
                    idx = normalized_fields.index(field)
                    normalized_fields[idx] = updated_value
                    updated_account = True
        if not updated_account:
            normalized_fields = normalized_fields + [{"name": BROKER_ACCOUNT_ID_FIELD, "value": new_account_id}]
        updated["fields"] = normalized_fields
    elif isinstance(fields, Mapping):
        normalized_fields = dict(fields)
        normalized_fields[BROKER_ACCOUNT_ID_FIELD] = new_account_id
        updated["fields"] = normalized_fields
    else:
        updated[BROKER_ACCOUNT_ID_FIELD] = new_account_id

    if not updated_account and isinstance(fields, list):
        updated[BROKER_ACCOUNT_ID_FIELD] = new_account_id

    return updated


def _read_broker_runtime_item() -> tuple[dict[str, Any], bool]:
    try:
        completed = subprocess.run(
            ["bw", "get", "item", LIVEOFX_ITEM_REF],
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError:
        return {}, False

    if completed.returncode != 0 or not completed.stdout:
        return {}, False
    return _parse_raw_json(completed.stdout), True


def _parse_raw_json(raw: str) -> dict[str, Any]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    return payload


def _write_bw_item(updated_item: Mapping[str, Any], select_visible_account_index: int) -> bool:
    payload = json.dumps(updated_item)
    try:
        completed = subprocess.run(
            ["bw", "edit", "item", LIVEOFX_ITEM_REF],
            input=payload,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return False
    return completed.returncode == 0


def _redact_payload(
    payload: Mapping[str, Any],
    *,
    token: str,
    account_id: str,
    bw_session: str,
) -> dict[str, Any]:
    def _redact_text(text: Any) -> Any:
        if not isinstance(text, str):
            return text
        redacted = text
        if token:
            redacted = redacted.replace(token, REDACTION_TOKEN)
        if account_id:
            redacted = redacted.replace(account_id, REDACTION_ACCOUNT)
        if bw_session:
            redacted = redacted.replace(bw_session, REDACTION_SESSION)
        return redacted

    def _visit(value: Any) -> Any:
        if isinstance(value, list):
            return [_visit(child) for child in value]
        if isinstance(value, dict):
            result: dict[str, Any] = {}
            for key, child in value.items():
                lowered_key = str(key).lower()
                if lowered_key == "authorization":
                    result[key] = ""
                else:
                    result[key] = _visit(child)
            return result
        if isinstance(value, str):
            return _redact_text(value)
        return value

    return _visit(dict(payload))


def _build_report(payload: Mapping[str, Any]) -> str:
    result = payload["result"]
    input_payload = payload["input"]
    runtime_summary = payload["runtime_summary"]
    blockers = "\n".join(f"- {item}" for item in result.get("blockers", [])) or "- (none)"

    return (
        "# Forex OANDA Live Account Binding Repair V1\n\n"
        f"- module: {payload['module']}\n"
        f"- packet_id: {payload['packet_id']}\n"
        "\n"
        "## Result\n"
        f"- account_binding_repair_status: {result['account_binding_repair_status']}\n"
        f"- account_binding_update_status: {result.get('account_binding_update_status', '')}\n"
        f"- safe_next_action: {result['safe_next_action']}\n"
        "- blockers:\n"
        f"{blockers}\n\n"
        "## Input booleans\n"
        f"- owner_flag_present: {input_payload.get('owner_flag_present')}\n"
        f"- bw_session_present: {input_payload.get('bw_session_present')}\n"
        f"- bitwarden_cli_available: {input_payload.get('bitwarden_cli_available')}\n"
        f"- bitwarden_item_read_success: {input_payload.get('bitwarden_item_read_success')}\n"
        f"- broker_api_called: {input_payload.get('broker_api_called')}\n"
        f"- accounts_probe_called: {input_payload.get('accounts_probe_called')}\n"
        f"- bitwarden_update_requested: {input_payload.get('bitwarden_update_requested')}\n"
        f"- bitwarden_update_attempted: {input_payload.get('bitwarden_update_attempted')}\n"
        f"- bitwarden_update_success: {input_payload.get('bitwarden_update_success')}\n"
        f"- order_endpoint_called: {input_payload.get('order_endpoint_called')}\n"
        f"- post_request_called: {input_payload.get('post_request_called')}\n"
        f"- live_order_execution: {input_payload.get('live_order_execution')}\n"
        f"- money_movement: {input_payload.get('money_movement')}\n"
        f"- scheduler_started: {input_payload.get('scheduler_started')}\n"
        f"- daemon_started: {input_payload.get('daemon_started')}\n"
        f"- webhook_started: {input_payload.get('webhook_started')}\n\n"
        "## Runtime summary\n"
        f"- accounts_status_code: {runtime_summary.get('accounts_status_code')}\n"
        f"- account_list_count: {runtime_summary.get('account_list_count')}\n"
        f"- configured_account_visible: {runtime_summary.get('configured_account_visible')}\n"
        f"- configured_account_fingerprint: {runtime_summary.get('configured_account_fingerprint')}\n"
        f"- visible_account_fingerprints: {runtime_summary.get('visible_account_fingerprints')}\n"
        f"- selected_visible_account_index: {runtime_summary.get('selected_visible_account_index')}\n"
        f"- selected_account_fingerprint: {runtime_summary.get('selected_account_fingerprint')}\n"
        f"- safe_next_action: {runtime_summary.get('safe_next_action')}\n\n"
        "## Allowed actions\n"
        "- default dry-run mode\n"
        f"- GET {OANDA_LIVE_ENDPOINT}/v3/accounts\n"
        "- optional Bitwarden item update of broker_account_id only\n\n"
        "## Forbidden actions\n"
        "- POST requests\n"
        "- /orders endpoint\n"
        "- live order execution\n"
        "- money movement\n"
        "- scheduler, daemon, or webhook startup\n\n"
        "## Validators\n"
        "- python -m py_compile scripts/forex_delivery/run_forex_oanda_live_account_binding_repair_v1.py\n"
        "- python -m pytest tests/forex_engine/test_forex_oanda_live_account_binding_repair_v1.py -q\n"
        "- python scripts/forex_delivery/run_forex_oanda_live_account_binding_repair_v1.py\n"
    )


def _parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Repair OANDA live account binding when configured account is not visible.",
        allow_abbrev=False,
    )
    parser.add_argument(READONLY_INSPECT_FLAG, action="store_true")
    parser.add_argument(UPDATE_FLAG, action="store_true")
    parser.add_argument(INDEX_ARG, type=int, default=None)
    parser.add_argument("--state-output", default=str(STATE_PATH))
    parser.add_argument("--report-output", default=str(REPORT_PATH))
    parser.add_argument("--no-report", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_arguments(argv)
    run_forex_oanda_live_account_binding_repair_v1(
        owner_approved_readonly_account_binding_inspect=args.__dict__.get(
            READONLY_INSPECT_FLAG.lstrip("-").replace("-", "_"),
            False,
        ),
        owner_approved_update_bitwarden_account_binding=args.__dict__.get(
            UPDATE_FLAG.lstrip("-").replace("-", "_"),
            False,
        ),
        select_visible_account_index=args.select_visible_account_index,
        state_output=Path(args.state_output),
        report_output=Path(args.report_output),
        write_report=not args.no_report,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
