"""Runner for the supervised demo order execution packet."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import replace
from pathlib import Path
from typing import Any
from urllib import error, request

REPO_ROOT = Path(__file__).resolve().parents[2]

try:
    import sys

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
except Exception:
    pass

from automation.forex_engine.forex_supervised_demo_order_execution_v1 import (  # noqa: E402
    DEFAULT_RUNTIME_ALLOWED_MODES,
    RUNTIME_MODE_DRY_RUN,
    RUNTIME_MODE_OWNER_APPROVED_SUPERVISED_DEMO_ORDER,
    SupervisedDemoOrderInput,
    build_default_input,
    evaluate_supervised_demo_order_execution,
    input_as_dict,
    result_as_dict,
)

STATE_JSON_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_ORDER_EXECUTION_V1_STATE.json",
)
REPORT_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_ORDER_EXECUTION_V1_REPORT.md",
)

RUNTIME_FLAG = "--owner-approved-supervised-demo-order"
BROKER_ITEM_REF = "AIOS / OANDA / Practice Demo / Broker Runtime"
BROKER_API_BASE_ENDPOINT = "https://api-fxpractice.oanda.com"

DEFAULT_INSTRUMENT = "EUR_USD"
DEFAULT_SIDE = "buy"
DEFAULT_ORDER_TYPE = "market"
DEFAULT_TIME_IN_FORCE = "FOK"
DEFAULT_ORDER_ATTEMPTS = 1
DEFAULT_SESSION_WINDOW_HOURS = 22
DEFAULT_SESSION_WINDOW_DAYS_PER_WEEK = 6
ORDER_TIMEOUT_SECONDS = 10


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AIOS supervised demo order execution runner.",
        allow_abbrev=False,
    )
    parser.add_argument(
        "--owner-approved-supervised-demo-order",
        action="store_true",
        help="Enable owner approved supervised demo one-order execution.",
    )
    parser.add_argument(
        "--state-output",
        default=str(STATE_JSON_PATH),
        help="Path for JSON state output.",
    )
    parser.add_argument(
        "--report-output",
        default=str(REPORT_PATH),
        help="Path for markdown report output.",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip writing markdown report output.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = run_forex_supervised_demo_order_execution_v1(
        owner_approved_supervised_demo_order=args.owner_approved_supervised_demo_order,
        state_output=Path(args.state_output),
        report_output=Path(args.report_output),
        write_report=not args.no_report,
    )
    print(json.dumps(payload))
    return 0


def run_forex_supervised_demo_order_execution_v1(
    *,
    owner_approved_supervised_demo_order: bool = False,
    state_output: Path = STATE_JSON_PATH,
    report_output: Path = REPORT_PATH,
    write_report: bool = True,
) -> dict[str, Any]:
    runtime_credentials: dict[str, str] = {}
    runtime_mode = (
        RUNTIME_MODE_OWNER_APPROVED_SUPERVISED_DEMO_ORDER
        if owner_approved_supervised_demo_order
        else RUNTIME_MODE_DRY_RUN
    )
    demo_input = build_default_input(
        owner_supervised_demo_approval=owner_approved_supervised_demo_order,
        owner_runtime_order_flag=owner_approved_supervised_demo_order,
        runtime_mode=runtime_mode,
    )
    runtime_summary: dict[str, Any] = _runtime_summary_defaults(
        owner_approved_supervised_demo_order=owner_approved_supervised_demo_order,
        runtime_mode=runtime_mode,
    )

    if owner_approved_supervised_demo_order:
        demo_input, runtime_summary, runtime_credentials = _load_runtime_credentials(
            demo_input=demo_input,
            runtime_summary=runtime_summary,
        )

    result = evaluate_supervised_demo_order_execution(demo_input)
    runtime_summary.update(
        {
            "next_stage": result.next_stage,
            "next_safe_action": result.safe_next_action,
            "demo_order_status": result.demo_order_status,
            "current_stage": result.current_stage,
            "runtime_order_blockers": result.blockers,
        },
    )

    result_dict = result_as_dict(result)
    if (
        owner_approved_supervised_demo_order
        and result.demo_order_status == "SUPERVISED_DEMO_ORDER_READY"
    ):
        execution_summary = _execute_owner_runtime_order(
            demo_input=demo_input,
            runtime_summary=runtime_summary,
            runtime_credentials=runtime_credentials,
        )
        runtime_summary.update(execution_summary)
        result_dict["broker_api_called"] = bool(execution_summary["broker_api_called"])
        result_dict["demo_order_execution"] = bool(
            execution_summary["order_attempted"] and execution_summary["order_attempt_success"],
        )

    payload = {
        "packet_id": "PKT-FOREX-SUPERVISED-DEMO-ORDER-EXECUTION-V1",
        "module": "forex_supervised_demo_order_execution_v1",
        "input": input_as_dict(demo_input),
        "result": result_dict,
        "runtime_summary": runtime_summary,
    }
    return _write_artifacts(
        payload=payload,
        state_output=state_output,
        report_output=report_output,
        write_report=write_report,
    )


def _runtime_summary_defaults(
    *,
    owner_approved_supervised_demo_order: bool,
    runtime_mode: str,
) -> dict[str, Any]:
    return {
        "runtime_mode": runtime_mode,
        "default_mode": RUNTIME_MODE_DRY_RUN,
        "runtime_flag": RUNTIME_FLAG,
        "runtime_enabled": bool(owner_approved_supervised_demo_order),
        "owner_approved_supervised_demo_order": bool(
            owner_approved_supervised_demo_order,
        ),
        "runtime_stage": "supervised_demo_order_execution",
        "broker": "OANDA",
        "runtime_endpoint": BROKER_API_BASE_ENDPOINT,
        "session_window_hours": DEFAULT_SESSION_WINDOW_HOURS,
        "session_window_days_per_week": DEFAULT_SESSION_WINDOW_DAYS_PER_WEEK,
        "target": "live 22hr/day 6day/week autonomous execution",
        "bw_session_required": True,
        "bitwarden_cli_required": True,
        "bw_session_present": False,
        "bitwarden_cli_available": False,
        "bitwarden_cli_called": False,
        "bitwarden_item_read_success": False,
        "credential_values_available_to_runtime": False,
        "broker_runtime_item_ref": BROKER_ITEM_REF,
        "required_item_fields": [
            "broker_api_token",
            "broker_account_id",
            "endpoint",
            "environment",
            "allowed_mode",
        ],
        "allowed_modes": list(DEFAULT_RUNTIME_ALLOWED_MODES),
        "endpoint_is_oanda_practice": False,
        "environment_is_practice_demo": False,
        "allowed_mode_is_demo_only": False,
        "demo_order_status": "PENDING",
        "runtime_order_blockers": [],
        "order_attempt_requested": False,
        "order_attempted": False,
        "order_attempt_count": 0,
        "order_attempt_success": False,
        "broker_api_called": False,
        "order_payload": None,
        "order_endpoint": None,
    }


def _load_runtime_credentials(
    *,
    demo_input: SupervisedDemoOrderInput,
    runtime_summary: dict[str, Any],
) -> tuple[SupervisedDemoOrderInput, dict[str, Any], dict[str, str]]:
    bw_session_present = os.environ.get("BW_SESSION") is not None
    runtime_summary["bw_session_present"] = bw_session_present
    demo_input = replace(demo_input, bw_session_present=bw_session_present)

    if not bw_session_present:
        return demo_input, runtime_summary, {}

    bitwarden_path = shutil.which("bw")
    bitwarden_cli_available = bitwarden_path is not None
    runtime_summary["bitwarden_cli_available"] = bitwarden_cli_available
    demo_input = replace(demo_input, bitwarden_cli_available=bitwarden_cli_available)
    if not bitwarden_cli_available:
        return demo_input, runtime_summary, {}

    raw_item, cli_called = _call_bitwarden_item(BROKER_ITEM_REF)
    demo_input = replace(demo_input, bitwarden_cli_called=cli_called)
    runtime_summary["bitwarden_cli_called"] = cli_called
    if not cli_called:
        return demo_input, runtime_summary, {}

    parsed_fields = _parse_bitwarden_item_fields(raw_item)
    demo_input = replace(demo_input, bitwarden_item_read_success=bool(parsed_fields))
    runtime_summary["bitwarden_item_read_success"] = bool(parsed_fields)

    token = str(parsed_fields.get("broker_api_token", "")).strip()
    account_id = str(parsed_fields.get("broker_account_id", "")).strip()
    endpoint = str(parsed_fields.get("endpoint", "")).strip()
    environment = str(parsed_fields.get("environment", "")).strip()
    allowed_mode = str(parsed_fields.get("allowed_mode", "")).strip()

    credential_values_available_to_runtime = bool(token and account_id)
    demo_input = replace(
        demo_input,
        credential_values_available_to_runtime=credential_values_available_to_runtime,
        endpoint_is_oanda_practice=(endpoint == BROKER_API_BASE_ENDPOINT),
        environment_is_practice_demo=(environment == "practice_demo"),
        allowed_mode_is_demo_only=(allowed_mode in DEFAULT_RUNTIME_ALLOWED_MODES),
    )

    runtime_summary["credential_values_available_to_runtime"] = (
        credential_values_available_to_runtime
    )
    runtime_summary["parsed_item_fields"] = {
        "broker_api_token": bool(token),
        "broker_account_id": bool(account_id),
        "endpoint": bool(endpoint),
        "environment": bool(environment),
        "allowed_mode": bool(allowed_mode),
    }
    runtime_summary["broker_item_reference_payload"] = _redact_runtime_payload(
        parsed_fields
    )

    return (
        demo_input,
        runtime_summary,
        {
            "broker_api_token": token,
            "broker_account_id": account_id,
        },
    )


def _execute_owner_runtime_order(
    *,
    demo_input: SupervisedDemoOrderInput,
    runtime_summary: dict[str, Any],
    runtime_credentials: dict[str, str],
) -> dict[str, Any]:
    runtime_summary["order_attempt_requested"] = True
    token = runtime_credentials.get("broker_api_token", "")
    account_id = runtime_credentials.get("broker_account_id", "")

    if not token or not account_id or not demo_input.endpoint_is_oanda_practice:
        return {
            "order_attempted": False,
            "order_attempt_count": 0,
            "order_attempt_success": False,
            "broker_api_called": False,
            "order_status_code": None,
            "order_status": "skipped_runtime_credentials_or_boundary_failed",
            "order_response": None,
            "order_payload": None,
            "order_endpoint": None,
        }

    payload = _build_order_payload(demo_input)
    runtime_summary["order_payload"] = payload

    url = f"{BROKER_API_BASE_ENDPOINT}/v3/accounts/{account_id}/orders"
    runtime_summary["order_endpoint"] = url
    transport_request = _build_order_request(url, token=token, payload=payload)
    response, status_code, success = _post_json_request(transport_request)
    runtime_summary["order_status"] = "created" if success else "not_created"
    runtime_summary["order_status_code"] = status_code
    runtime_summary["order_response"] = response

    return {
        "order_attempted": True,
        "order_attempt_count": DEFAULT_ORDER_ATTEMPTS,
        "order_attempt_success": success,
        "broker_api_called": True,
        "order_status_code": status_code,
        "order_status": runtime_summary["order_status"],
        "order_response": response,
        "order_payload": payload,
        "order_endpoint": url,
    }


def _build_order_payload(demo_input: SupervisedDemoOrderInput) -> dict[str, Any]:
    return {
        "order": {
            "units": str(max(1, int(demo_input.units))),
            "instrument": demo_input.instrument,
            "type": demo_input.order_type,
            "timeInForce": demo_input.time_in_force,
            "positionFill": "DEFAULT",
            "stopLossOnFill": {
                "distance": "0.0050",
            },
            "takeProfitOnFill": {
                "distance": "0.0100",
            },
        },
    }


def _build_order_request(
    url: str,
    *,
    token: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "method": "POST",
        "url": url,
        "headers": {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        "json": payload,
        "timeout": ORDER_TIMEOUT_SECONDS,
    }


def _post_json_request(
    request_payload: dict[str, Any],
) -> tuple[dict[str, Any] | None, int | None, bool]:
    req = request.Request(
        url=request_payload["url"],
        method=request_payload["method"],
        headers={str(k): str(v) for k, v in request_payload["headers"].items()},
        data=json.dumps(request_payload["json"]).encode("utf-8"),
    )
    try:
        response = request.urlopen(req, timeout=request_payload.get("timeout", ORDER_TIMEOUT_SECONDS))
        with response:
            raw_body = response.read().decode("utf-8", errors="replace")
            status_code = response.getcode()
    except error.HTTPError as exc:
        status_code = int(exc.code or 0)
        raw_body = exc.read().decode("utf-8", errors="replace")
    except error.URLError as exc:
        return {
            "error": str(exc.reason),
        }, None, False
    try:
        parsed_body = json.loads(raw_body)
    except json.JSONDecodeError:
        parsed_body = raw_body
    return {"status_code": status_code, "body": parsed_body}, status_code, status_code in {200, 201}


def _call_bitwarden_item(item_ref: str) -> tuple[str, bool]:
    try:
        completed = subprocess.run(
            ["bw", "get", "item", item_ref],
            check=False,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, OSError):
        return "", False
    if completed.returncode != 0:
        return "", False
    return completed.stdout, True


def _parse_bitwarden_item_fields(raw_item: str) -> dict[str, str]:
    if not raw_item.strip():
        return {}
    try:
        payload = json.loads(raw_item)
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}

    field_values = payload.get("fields")
    if isinstance(field_values, list):
        parsed: dict[str, str] = {}
        for field in field_values:
            if not isinstance(field, dict):
                continue
            name = str(field.get("name", "")).strip()
            value = str(field.get("value", "")).strip()
            if name:
                parsed[name] = value
        return parsed
    if isinstance(field_values, dict):
        return {
            str(name).strip(): str(value).strip()
            for name, value in field_values.items()
            if str(name).strip()
        }
    return {}


def _redact_runtime_payload(payload: dict[str, Any]) -> dict[str, Any]:
    token = str(payload.get("broker_api_token", "")).strip()
    account_id = str(payload.get("broker_account_id", "")).strip()
    redacted_token = "REDACTED_TOKEN"
    redacted_account = "REDACTED_ACCOUNT_ID"
    output: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, str):
            redacted_value = value
            if token:
                redacted_value = redacted_value.replace(token, redacted_token)
            if account_id:
                redacted_value = redacted_value.replace(account_id, redacted_account)
            output[str(key)] = redacted_value
        else:
            output[str(key)] = value
    return output


def _write_artifacts(
    *,
    payload: dict[str, Any],
    state_output: Path,
    report_output: Path,
    write_report: bool,
) -> dict[str, Any]:
    state_output.parent.mkdir(parents=True, exist_ok=True)
    state_output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if write_report:
        report_output.parent.mkdir(parents=True, exist_ok=True)
        report_output.write_text(_build_report_markdown(payload), encoding="utf-8")
    return payload


def _build_report_markdown(payload: dict[str, Any]) -> str:
    result = payload["result"]
    blockers = "\n".join(f"- {blocker}" for blocker in result["blockers"]) or "- (none)"
    return (
        "# AIOS Forex Supervised Demo Order Execution V1 Report\n\n"
        "## Packet evaluation\n"
        f"- demo_order_status: {result['demo_order_status']}\n"
        f"- current_stage: {result['current_stage']}\n"
        f"- next_stage: {result['next_stage']}\n"
        f"- runtime_mode: {result['runtime_mode']}\n"
        f"- safe_next_action: {result['safe_next_action']}\n"
        "- blockers:\n"
        f"{blockers}\n\n"
        "## Runtime gate state\n"
        f"- runtime_enabled: {payload['runtime_summary']['runtime_enabled']}\n"
        f"- runtime_flag: {payload['runtime_summary']['runtime_flag']}\n"
        "- live_order_execution: false\n"
        "- money_movement: false\n"
        "- scheduler_started: false\n"
        "- daemon_started: false\n"
        "- webhook_started: false\n"
        f"- owner_approved_supervised_demo_order: "
        f"{str(payload['runtime_summary']['owner_approved_supervised_demo_order']).lower()}\n"
        f"- broker: {payload['runtime_summary']['broker']}\n"
        f"- endpoint: {payload['runtime_summary']['runtime_endpoint']}\n"
        f"- order_attempt_requested: {payload['runtime_summary']['order_attempt_requested']}\n"
        f"- order_attempted: {payload['runtime_summary']['order_attempted']}\n"
        f"- order_attempt_count: {payload['runtime_summary']['order_attempt_count']}\n"
        f"- order_attempt_success: {payload['runtime_summary']['order_attempt_success']}\n"
        "## Order intent\n"
        f"- order_intent_summary: {result['order_intent_summary']}\n"
        f"- max_orders_per_run: {DEFAULT_ORDER_ATTEMPTS}\n"
        f"- side: {DEFAULT_SIDE}\n"
        f"- order_type: {DEFAULT_ORDER_TYPE}\n"
        f"- instrument: {DEFAULT_INSTRUMENT}\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
