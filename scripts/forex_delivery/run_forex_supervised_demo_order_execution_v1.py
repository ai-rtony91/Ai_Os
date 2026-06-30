"""Runner for the AI OS supervised demo order execution packet."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.request
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.forex_supervised_demo_order_execution_v1 import (
    DEFAULT_RUNTIME_ALLOWED_MODES,
    OWNER_RUNTIME_ORDER_FLAG_REQUIRED,
    OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED,
    RUNTIME_CREDENTIAL_ACCESS_REQUIRED,
    RUNTIME_MODE_DRY_RUN,
    RUNTIME_MODE_OWNER_APPROVED_SUPERVISED_DEMO_ORDER,
    SUPERVISED_DEMO_ORDER_READY,
    SupervisedDemoOrderInput,
    build_default_input,
    evaluate_supervised_demo_order_execution,
    input_as_dict,
    result_as_dict,
)


PACKET_ID = "PKT-FOREX-SUPERVISED-DEMO-ORDER-EXECUTION-V1"
STATE_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_ORDER_EXECUTION_V1_STATE.json",
)
REPORT_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_ORDER_EXECUTION_V1_REPORT.md",
)
OANDA_PRACTICE_ENDPOINT = "https://api-fxpractice.oanda.com"
BROKER_ITEM_NAME = "AIOS / OANDA / Practice Demo / Broker Runtime"
DEFAULT_MAX_ORDERS_PER_RUN = 1
REDACTED_ACCOUNT_ID = "REDACTED_ACCOUNT_ID"
REDACTED_TOKEN = "REDACTED_TOKEN"

_ACCOUNT_ID_PATH_PATTERN = re.compile(
    r"(?P<prefix>/v3/accounts/)(?P<account>[^/]+)(?P<suffix>/orders)",
    re.IGNORECASE,
)
_BEARER_PATTERN = re.compile(r"(?i)Bearer\s+[A-Za-z0-9._~+/=\-]+")


def _coerce_int(value: Any, default: int = 1) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    if parsed == 0:
        return default
    return parsed


def _normalize_units(units: int, side: str) -> int:
    resolved_units = max(_coerce_int(units), 1)
    if str(side or "").strip().lower() == "sell":
        return -resolved_units
    return resolved_units


def _build_order_payload(input_data: SupervisedDemoOrderInput) -> dict[str, Any]:
    units = _normalize_units(input_data.units, input_data.side)
    return {
        "order": {
            "instrument": input_data.instrument,
            "units": str(units),
            "type": str(input_data.order_type or "MARKET").upper(),
            "timeInForce": input_data.time_in_force or "FOK",
            "positionFill": "DEFAULT",
            "stopLossOnFill": {"distance": "0.0050"},
            "takeProfitOnFill": {"distance": "0.0100"},
        },
    }


def _redact_authorization(value: Any) -> Any:
    if not isinstance(value, str):
        return REDACTED_TOKEN
    if value.lower().startswith("bearer "):
        return REDACTED_TOKEN
    return REDACTED_TOKEN


def _redact_string(value: str) -> str:
    redacted = _ACCOUNT_ID_PATH_PATTERN.sub(
        r"\g<prefix>" + REDACTED_ACCOUNT_ID + r"\g<suffix>",
        value,
    )
    redacted = _BEARER_PATTERN.sub(REDACTED_TOKEN, redacted)
    return redacted


def _redact_runtime_state(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, nested in value.items():
            key_normalized = str(key).lower()
            if key_normalized == "bw_session":
                continue
            if key_normalized == "broker_api_token":
                redacted[key] = REDACTED_TOKEN
                continue
            if key_normalized in {"broker_account_id", "accountid", "account_id", "accountid"}:
                redacted[key] = REDACTED_ACCOUNT_ID
                continue
            if key_normalized == "authorization":
                redacted[key] = _redact_authorization(nested)
                continue
            redacted[key] = _redact_runtime_state(nested)
        return redacted
    if isinstance(value, list):
        return [_redact_runtime_state(item) for item in value]
    if isinstance(value, str):
        return _redact_string(value)
    return value


def _parse_bitwarden_item_fields(raw_output: str) -> dict[str, str]:
    try:
        payload = json.loads(raw_output)
    except json.JSONDecodeError:
        return {}

    fields: list[dict[str, Any]] = payload.get("fields", [])
    parsed: dict[str, str] = {}
    for field in fields:
        if not isinstance(field, dict):
            continue
        name = field.get("name")
        value = field.get("value")
        if not isinstance(name, str):
            continue
        if value is None:
            continue
        parsed[name] = str(value)
    return parsed


def _read_broker_runtime_item() -> dict[str, str]:
    try:
        result = subprocess.run(
            ["bw", "get", "item", BROKER_ITEM_NAME],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return {}
    if result.returncode != 0:
        return {}
    return _parse_bitwarden_item_fields(result.stdout or "")

def _post_json_request(
    request_payload: dict[str, Any],
) -> tuple[dict[str, Any], int, bool]:
    order_endpoint = request_payload.get("order_endpoint")
    order_payload = request_payload.get("order_payload", {})
    headers = request_payload.get("headers", {})
    if not isinstance(order_endpoint, str):
        return {"error": "Missing order endpoint"}, 0, False
    if not isinstance(order_payload, dict):
        return {"error": "Invalid order payload"}, 0, False

    request_headers = {
        "Content-Type": "application/json",
    }
    if isinstance(headers, dict):
        request_headers.update(
            {str(k): str(v) for k, v in headers.items() if k is not None and v is not None},
        )

    request_data = json.dumps({"order": order_payload["order"]}).encode("utf-8")
    request = urllib.request.Request(
        order_endpoint,
        data=request_data,
        method="POST",
        headers=request_headers,
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:  # nosec B310
            status_code = int(response.status)
            body = response.read().decode("utf-8")
            if not body:
                return {}, status_code, 200 <= status_code < 300
            try:
                return json.loads(body), status_code, 200 <= status_code < 300
            except json.JSONDecodeError:
                return {"response_text": body}, status_code, 200 <= status_code < 300
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            body = ""
        if body:
            try:
                return json.loads(body), exc.code, False
            except json.JSONDecodeError:
                return {"response_text": body}, exc.code, False
        return {"error": exc.reason}, int(exc.code), False
    except Exception as exc:  # pragma: no cover - runtime only, never in unit tests
        return {"error": str(exc)}, 0, False


def _build_runtime_input(
    *,
    owner_approved_supervised_demo_order: bool,
) -> SupervisedDemoOrderInput:
    runtime_mode = (
        RUNTIME_MODE_OWNER_APPROVED_SUPERVISED_DEMO_ORDER
        if owner_approved_supervised_demo_order
        else RUNTIME_MODE_DRY_RUN
    )
    base_input = build_default_input(
        owner_supervised_demo_approval=owner_approved_supervised_demo_order,
        owner_runtime_order_flag=owner_approved_supervised_demo_order,
        runtime_mode=runtime_mode,
    )

    if not owner_approved_supervised_demo_order:
        return base_input

    bw_session_present = bool(os.getenv("BW_SESSION"))
    bitwarden_cli_available = bool(shutil.which("bw"))
    item_fields = _read_broker_runtime_item() if bitwarden_cli_available else {}
    required_item_fields = [
        "broker_api_token",
        "broker_account_id",
        "endpoint",
        "environment",
        "allowed_mode",
    ]
    parsed_item_fields = {name: name in item_fields for name in required_item_fields}
    credential_values_available_to_runtime = all(
        item_fields.get(field_name) for field_name in required_item_fields
    )

    endpoint = item_fields.get("endpoint", OANDA_PRACTICE_ENDPOINT)
    environment = item_fields.get("environment", "practice_demo")
    allowed_mode = item_fields.get("allowed_mode", "read_only_until_owner_demo_approval")

    return replace(
        base_input,
        bw_session_present=bw_session_present,
        bitwarden_cli_available=bitwarden_cli_available,
        bitwarden_item_read_success=bool(item_fields),
        credential_values_available_to_runtime=credential_values_available_to_runtime,
        endpoint_is_oanda_practice=("api-fxpractice.oanda.com" in (endpoint or "")),
        environment_is_practice_demo=(environment == "practice_demo"),
        allowed_mode_is_demo_only=base_input.allowed_mode_is_demo_only,
        # Keep this for debug/compatibility with existing report fields.
        demo_order_execution=False,
        live_order_execution=False,
        money_movement=False,
        scheduler_started=False,
        daemon_started=False,
        webhook_started=False,
    )


def _build_runtime_summary(
    *,
    input_data: SupervisedDemoOrderInput,
    result_dict: dict[str, Any],
    runtime_item: dict[str, str],
    order_attempt_requested: bool,
    order_attempt_count: int,
    order_attempted: bool,
    order_attempt_success: bool,
    order_status: str,
    order_status_code: int,
    order_response: dict[str, Any] | None,
    order_payload: dict[str, Any] | None,
    order_endpoint: str | None,
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "allowed_modes": list(DEFAULT_RUNTIME_ALLOWED_MODES),
        "current_stage": "supervised_demo_order_execution",
        "runtime_enabled": bool(input_data.owner_runtime_order_flag),
        "runtime_mode": input_data.runtime_mode,
        "runtime_flag": "--owner-approved-supervised-demo-order",
        "owner_approved_supervised_demo_order": input_data.owner_supervised_demo_approval,
        "broker": "OANDA",
        "runtime_stage": "supervised_demo_order_execution",
        "runtime_order_blockers": result_dict.get("blockers", []),
        "next_safe_action": result_dict.get("safe_next_action", ""),
        "allowed_mode_is_demo_only": input_data.allowed_mode_is_demo_only,
        "endpoint_is_oanda_practice": input_data.endpoint_is_oanda_practice,
        "environment_is_practice_demo": input_data.environment_is_practice_demo,
        "next_stage": result_dict.get("next_stage"),
        "demo_order_status": result_dict.get("demo_order_status"),
        "order_status": order_status,
        "order_status_code": order_status_code,
        "runtime_endpoint": runtime_item.get("endpoint", OANDA_PRACTICE_ENDPOINT),
        "runtime_item_reference_payload": {
            "broker": "OANDA",
            "broker_account_id": runtime_item.get("broker_account_id"),
            "broker_api_token": runtime_item.get("broker_api_token"),
            "endpoint": runtime_item.get("endpoint", OANDA_PRACTICE_ENDPOINT),
            "environment": runtime_item.get("environment"),
            "owner": runtime_item.get("owner"),
            "allowed_mode": runtime_item.get("allowed_mode"),
        },
        "broker_item_reference_payload": {
            "broker": "OANDA",
            "broker_account_id": runtime_item.get("broker_account_id"),
            "broker_api_token": runtime_item.get("broker_api_token"),
            "endpoint": runtime_item.get("endpoint", OANDA_PRACTICE_ENDPOINT),
            "environment": runtime_item.get("environment"),
            "owner": runtime_item.get("owner"),
            "allowed_mode": runtime_item.get("allowed_mode"),
        },
        "broker_runtime_item_ref": BROKER_ITEM_NAME,
        "bitwarden_cli_required": True,
        "bw_session_required": True,
        "bw_session_present": bool(input_data.bw_session_present),
        "bitwarden_cli_available": bool(input_data.bitwarden_cli_available),
        "bitwarden_cli_called": bool(input_data.bitwarden_cli_called),
        "bitwarden_item_read_success": bool(input_data.bitwarden_item_read_success),
        "credential_values_available_to_runtime": bool(
            input_data.credential_values_available_to_runtime,
        ),
        "broker_api_called": bool(result_dict.get("broker_api_called")),
        "demo_order_execution": bool(result_dict.get("demo_order_execution")),
        "demo_order_status_ready": result_dict.get("demo_order_status"),
        "live_order_execution": bool(result_dict.get("live_order_execution")),
        "money_movement": bool(result_dict.get("money_movement")),
        "scheduler_started": bool(result_dict.get("scheduler_started")),
        "daemon_started": bool(result_dict.get("daemon_started")),
        "webhook_started": bool(result_dict.get("webhook_started")),
        "order_attempt_requested": order_attempt_requested,
        "order_attempted": order_attempted,
        "order_attempt_count": order_attempt_count,
        "order_attempt_success": order_attempt_success,
        "order_endpoint": order_endpoint,
        "order_payload": order_payload,
        "order_response": order_response,
        "order_intent_summary": result_dict.get("order_intent_summary"),
        "side": input_data.side,
        "order_type": input_data.order_type,
        "instrument": input_data.instrument,
        "parsed_item_fields": {
            "broker_api_token": bool(runtime_item.get("broker_api_token")),
            "broker_account_id": bool(runtime_item.get("broker_account_id")),
            "endpoint": bool(runtime_item.get("endpoint")),
            "environment": bool(runtime_item.get("environment")),
            "allowed_mode": bool(runtime_item.get("allowed_mode")),
        },
        "required_item_fields": [
            "broker_api_token",
            "broker_account_id",
            "endpoint",
            "environment",
            "allowed_mode",
        ],
        "max_orders_per_run": DEFAULT_MAX_ORDERS_PER_RUN,
        "session_window_hours": 22,
        "session_window_days_per_week": 6,
        "next_stage_after_success": "supervised_demo_evidence_review",
        "live_order_execution_by_this_packet": False,
        "scheduler_started_by_this_packet": False,
        "daemon_started_by_this_packet": False,
        "webhook_started_by_this_packet": False,
        "target": "live 22hr/day 6day/week autonomous execution",
    }
    return summary


def run_forex_supervised_demo_order_execution_v1(
    *,
    owner_approved_supervised_demo_order: bool = False,
    state_output: Path = STATE_PATH,
    report_output: Path = REPORT_PATH,
    write_report: bool = True,
) -> dict[str, Any]:
    input_data = _build_runtime_input(
        owner_approved_supervised_demo_order=owner_approved_supervised_demo_order,
    )
    result = evaluate_supervised_demo_order_execution(input_data)
    result_dict = result_as_dict(result)

    runtime_item = {}
    if owner_approved_supervised_demo_order:
        runtime_item = _read_broker_runtime_item() if input_data.bitwarden_cli_available else {}

    order_attempt_requested = False
    order_attempted = False
    order_attempt_count = 0
    order_attempt_success = False
    order_status = "not_attempted"
    order_status_code = 0
    order_response: dict[str, Any] | None = None
    order_payload: dict[str, Any] | None = None
    order_endpoint = None

    if result.demo_order_status == SUPERVISED_DEMO_ORDER_READY:
        order_attempt_requested = True
        order_payload = _build_order_payload(input_data)
        endpoint = runtime_item.get("endpoint", OANDA_PRACTICE_ENDPOINT)
        account_id = runtime_item.get("broker_account_id")
        token = runtime_item.get("broker_api_token")
        if account_id and token and endpoint:
            order_endpoint = f"{endpoint.rstrip('/')}/v3/accounts/{account_id}/orders"
            request_payload = {
                "order_endpoint": order_endpoint,
                "headers": {"Authorization": f"Bearer {token}"},
                "order_payload": order_payload,
            }
            order_response, order_status_code, order_attempt_success = _post_json_request(
                request_payload,
            )
            order_attempted = True
            order_attempt_count = 1
            order_status = "created" if order_attempt_success else "not_created"
        else:
            order_response = {"error": "Missing broker runtime credentials"}
            order_status = "not_created"
        if order_attempted:
            result_dict["broker_api_called"] = True
            result_dict["demo_order_execution"] = True

    runtime_summary = _build_runtime_summary(
        input_data=input_data,
        result_dict=result_dict,
        runtime_item=runtime_item,
        order_attempt_requested=order_attempt_requested,
        order_attempt_count=order_attempt_count,
        order_attempted=order_attempted,
        order_attempt_success=order_attempt_success,
        order_status=order_status,
        order_status_code=order_status_code,
        order_response=order_response or {},
        order_payload=order_payload,
        order_endpoint=order_endpoint,
    )

    payload = {
        "module": "forex_supervised_demo_order_execution_v1",
        "packet_id": PACKET_ID,
        "input": input_as_dict(input_data),
        "result": result_dict,
        "runtime_summary": runtime_summary,
    }

    if write_report:
        _write_outputs(payload, state_output, report_output)

    return payload


def _write_outputs(payload: dict[str, Any], state_output: Path, report_output: Path) -> None:
    sanitized_payload = _redact_runtime_state(payload)
    state_output.parent.mkdir(parents=True, exist_ok=True)
    state_output.write_text(
        json.dumps(sanitized_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    report_text = _build_report_text(sanitized_payload)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(report_text, encoding="utf-8")


def _build_report_line(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value).lower() if isinstance(value, (int, float)) else str(value)


def _build_report_text(payload: dict[str, Any]) -> str:
    result = payload.get("result", {})
    summary = payload.get("runtime_summary", {})
    lines = [
        "# AIOS Forex Supervised Demo Order Execution V1 Report",
        "",
        "## Packet evaluation",
        f"- demo_order_status: {_build_report_line(result.get('demo_order_status'))}",
        f"- current_stage: {result.get('current_stage', 'supervised_demo_order_execution')}",
        f"- next_stage: {result.get('next_stage')}",
        f"- runtime_mode: {result.get('runtime_mode')}",
        f"- safe_next_action: {result.get('safe_next_action')}",
        "- blockers:",
    ]
    blockers = result.get("blockers", [])
    if blockers:
        lines.extend(f"  - {item}" for item in blockers)
    else:
        lines.append("- (none)")
    lines.extend(
        [
            "",
            "## Runtime gate state",
            f"- runtime_enabled: {_build_report_line(summary.get('runtime_enabled'))}",
            f"- runtime_flag: {summary.get('runtime_flag')}",
            f"- live_order_execution: {_build_report_line(summary.get('live_order_execution'))}",
            f"- money_movement: {_build_report_line(summary.get('money_movement'))}",
            f"- scheduler_started: {_build_report_line(summary.get('scheduler_started'))}",
            f"- daemon_started: {_build_report_line(summary.get('daemon_started'))}",
            f"- webhook_started: {_build_report_line(summary.get('webhook_started'))}",
            f"- owner_approved_supervised_demo_order: {_build_report_line(summary.get('owner_approved_supervised_demo_order'))}",
            f"- broker: {summary.get('broker')}",
            f"- endpoint: {summary.get('runtime_endpoint')}",
            f"- broker_account_id: {summary.get('broker_item_reference_payload', {}).get('broker_account_id')}",
            f"- broker_api_token: {summary.get('broker_item_reference_payload', {}).get('broker_api_token')}",
            f"- order_attempt_requested: {_build_report_line(summary.get('order_attempt_requested'))}",
            f"- order_attempted: {_build_report_line(summary.get('order_attempted'))}",
            f"- order_attempt_count: {summary.get('order_attempt_count')}",
            f"- order_attempt_success: {_build_report_line(summary.get('order_attempt_success'))}",
            f"- order_endpoint: {summary.get('order_endpoint')}",
            "",
            "## Order intent",
            f"- order_intent_summary: {summary.get('order_intent_summary')}",
            f"- max_orders_per_run: {summary.get('max_orders_per_run')}",
            f"- side: {summary.get('side')}",
            f"- order_type: {summary.get('order_type')}",
            f"- instrument: {summary.get('instrument')}",
        ],
    )
    return "\n".join(lines) + "\n"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--owner-approved-supervised-demo-order",
        action="store_true",
        default=False,
    )
    parser.add_argument("--state-output", type=Path, default=STATE_PATH)
    parser.add_argument("--report-output", type=Path, default=REPORT_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> dict[str, Any]:
    parsed = _parse_args(argv)
    return run_forex_supervised_demo_order_execution_v1(
        owner_approved_supervised_demo_order=parsed.owner_approved_supervised_demo_order,
        state_output=parsed.state_output,
        report_output=parsed.report_output,
        write_report=True,
    )


if __name__ == "__main__":
    main()


__all__ = [
    "run_forex_supervised_demo_order_execution_v1",
    "_build_order_payload",
    "_redact_runtime_state",
    "_post_json_request",
]
