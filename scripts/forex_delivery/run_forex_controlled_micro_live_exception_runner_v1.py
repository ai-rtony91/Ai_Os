"""Runner for the AIOS controlled micro-live exception packet."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import replace
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine import forex_controlled_micro_live_exception_runner_v1 as module

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

PACKET_ID = "AIOS-FOREX-CONTROLLED-MICRO-LIVE-EXCEPTION-RUNNER-V1"
STATE_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER_V1_STATE.json",
)
REPORT_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER_V1_REPORT.md",
)
DEFAULT_STATE_NEXT_SAFE_ORDER_LIMIT = 1
RUNTIME_OWNER_FLAG = "--owner-approved-controlled-micro-live-exception"
BROKER_ITEM_NAME = "AIOS / OANDA / Live / Broker Runtime"
OANDA_LIVE_ENDPOINT = "https://api-fxtrade.oanda.com"
OANDA_LIVE_ENDPOINT_HOST = f"{OANDA_LIVE_ENDPOINT}/v3/accounts"
REDACTED_TOKEN = "REDACTED_TOKEN"
REDACTED_ACCOUNT_ID = "REDACTED_ACCOUNT_ID"

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


def _build_order_payload(input_data: module.ControlledMicroLiveExceptionInput) -> dict[str, Any]:
    units = _normalize_units(input_data.units, input_data.side)
    return {
        "order": {
            "instrument": input_data.instrument,
            "units": str(units),
            "type": str(input_data.order_type or "MARKET").upper(),
            "timeInForce": input_data.time_in_force or "FOK",
            "positionFill": "DEFAULT",
            "stopLossOnFill": {"distance": "0.0010"},
            "takeProfitOnFill": {"distance": "0.0020"},
        },
    }


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
        if not isinstance(name, str) or value is None:
            continue
        parsed[name] = str(value)
    return parsed


def _read_broker_runtime_item() -> dict[str, str]:
    bw_session = os.getenv("BW_SESSION")
    command = ["bw", "get", "item", BROKER_ITEM_NAME]
    if bw_session:
        command.extend(["--session", bw_session])
    process_env = os.environ.copy()
    if bw_session:
        process_env["BW_SESSION"] = bw_session

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        env=process_env,
    )
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
    request_headers = {"Content-Type": "application/json"}
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


def _redact_runtime_state(value: Any, *, _parent_key: str | None = None) -> Any:
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
            if (
                isinstance(nested, str)
                and _parent_key is not None
                and "account" in _parent_key
            ):
                redacted[key] = REDACTED_ACCOUNT_ID
                continue
            redacted[key] = _redact_runtime_state(
                nested,
                _parent_key=key_normalized,
            )
        return redacted
    if isinstance(value, list):
        return [
            _redact_runtime_state(item, _parent_key=_parent_key)
            for item in value
        ]
    if isinstance(value, str):
        return _redact_string(value)
    return value


def _build_runtime_input(
    *,
    owner_approved_controlled_micro_live_exception: bool,
) -> tuple[module.ControlledMicroLiveExceptionInput, dict[str, str]]:
    runtime_item: dict[str, str] = {}
    if owner_approved_controlled_micro_live_exception:
        base = replace(module.build_default_input(), owner_micro_live_exception_approval_granted=True)
        bw_session_present = bool(os.getenv("BW_SESSION"))
        bitwarden_cli_available = bool(shutil.which("bw"))
        runtime_item = _read_broker_runtime_item() if bitwarden_cli_available else {}
        required_item_fields = [
            "broker_api_token",
            "broker_account_id",
            "endpoint",
            "environment",
            "allowed_mode",
        ]
        input_data = replace(
            base,
            live_runtime_owner_flag=True,
            bw_session_present=bw_session_present,
            bitwarden_cli_available=bitwarden_cli_available,
            bitwarden_cli_called=bitwarden_cli_available,
            bitwarden_item_read_success=bool(runtime_item),
            live_credential_values_available_to_runtime=all(
                runtime_item.get(field_name)
                for field_name in required_item_fields
            ),
            live_endpoint_is_oanda_fxtrade=(runtime_item.get("endpoint", OANDA_LIVE_ENDPOINT) == OANDA_LIVE_ENDPOINT),
            environment_is_live=(runtime_item.get("environment", "live") == "live"),
            allowed_mode_is_micro_live_only=(
                runtime_item.get("allowed_mode") == "controlled_micro_live_exception_only"
            ),
        )
    else:
        input_data = module.build_default_input()
    return input_data, runtime_item


def _build_runtime_summary(
    *,
    input_data: module.ControlledMicroLiveExceptionInput,
    result_dict: dict[str, Any],
    runtime_item: dict[str, str],
    order_attempt_requested: bool,
    order_attempted: bool,
    order_attempt_count: int,
    order_attempt_success: bool,
    order_status: str,
    order_status_code: int,
    order_endpoint: str | None,
    order_payload: dict[str, Any] | None,
    order_response: dict[str, Any] | None,
) -> dict[str, Any]:
    live_item_ref = "AIOS / OANDA / Live / Broker Runtime"
    return {
        "runtime_enabled": bool(input_data.live_runtime_owner_flag),
        "runtime_flag": RUNTIME_OWNER_FLAG,
        "runtime_mode": result_dict.get("runtime_mode"),
        "owner_approved_controlled_micro_live_exception": input_data.live_runtime_owner_flag,
        "supervised_demo_evidence_clean": input_data.supervised_demo_evidence_clean,
        "owner_micro_live_exception_approval_granted": input_data.owner_micro_live_exception_approval_granted,
        "runtime_item_reference_payload": {
            "broker": "OANDA",
            "broker_api_token": runtime_item.get("broker_api_token"),
            "broker_account_id": runtime_item.get("broker_account_id"),
            "endpoint": runtime_item.get("endpoint", OANDA_LIVE_ENDPOINT),
            "environment": runtime_item.get("environment"),
            "allowed_mode": runtime_item.get("allowed_mode"),
        },
        "live_item_ref": live_item_ref,
        "broker_item_reference_payload": {
            "broker": "OANDA",
            "broker_api_token": runtime_item.get("broker_api_token"),
            "broker_account_id": runtime_item.get("broker_account_id"),
            "endpoint": runtime_item.get("endpoint", OANDA_LIVE_ENDPOINT),
            "environment": runtime_item.get("environment"),
            "allowed_mode": runtime_item.get("allowed_mode"),
        },
        "bw_session_present": input_data.bw_session_present,
        "bitwarden_cli_available": input_data.bitwarden_cli_available,
        "bitwarden_item_read_success": input_data.bitwarden_item_read_success,
        "credential_values_available_to_runtime": input_data.live_credential_values_available_to_runtime,
        "live_endpoint_is_oanda_fxtrade": input_data.live_endpoint_is_oanda_fxtrade,
        "environment_is_live": input_data.environment_is_live,
        "allowed_mode_is_micro_live_only": input_data.allowed_mode_is_micro_live_only,
        "kill_switch_enabled": input_data.kill_switch_enabled,
        "kill_switch_triggered": input_data.kill_switch_triggered,
        "daily_loss_cap_defined": input_data.daily_loss_cap_defined,
        "daily_loss_within_limit": input_data.daily_loss_within_limit,
        "trade_risk_cap_defined": input_data.trade_risk_cap_defined,
        "proposed_trade_risk_within_limit": input_data.proposed_trade_risk_within_limit,
        "duplicate_order_guard_enabled": input_data.duplicate_order_guard_enabled,
        "duplicate_order_detected": input_data.duplicate_order_detected,
        "audit_log_enabled": input_data.audit_log_enabled,
        "audit_log_write_success": input_data.audit_log_write_success,
        "max_orders_per_run": DEFAULT_STATE_NEXT_SAFE_ORDER_LIMIT,
        "micro_size_only": input_data.micro_size_only,
        "max_one_live_order_enforced": input_data.max_one_live_order_enforced,
        "stop_loss_defined": input_data.stop_loss_defined,
        "take_profit_defined": input_data.take_profit_defined,
        "time_in_force": input_data.time_in_force,
        "order_attempt_requested": order_attempt_requested,
        "order_attempted": order_attempted,
        "order_attempt_count": order_attempt_count,
        "order_attempt_success": order_attempt_success,
        "order_status": order_status,
        "order_status_code": order_status_code,
        "order_endpoint": order_endpoint,
        "order_payload": order_payload,
        "order_response": order_response,
        "order_intent_summary": result_dict.get("order_intent_summary"),
        "safe_next_action": result_dict.get("safe_next_action"),
        "next_stage": result_dict.get("next_stage"),
        "current_stage": result_dict.get("current_stage"),
        "next_stage_after_success": "micro_live_evidence_review",
    }


def run_forex_controlled_micro_live_exception_runner_v1(
    *,
    owner_approved_controlled_micro_live_exception: bool = False,
    state_output: Path = STATE_PATH,
    report_output: Path = REPORT_PATH,
    write_report: bool = True,
) -> dict[str, Any]:
    input_data, runtime_item = _build_runtime_input(
        owner_approved_controlled_micro_live_exception=owner_approved_controlled_micro_live_exception,
    )
    result = module.evaluate_controlled_micro_live_exception(input_data)
    result_dict = module.result_as_dict(result)

    order_attempt_requested = False
    order_attempted = False
    order_attempt_count = 0
    order_attempt_success = False
    order_status = "not_attempted"
    order_status_code = 0
    order_response: dict[str, Any] | None = None
    order_payload: dict[str, Any] | None = None
    order_endpoint = None

    if (
        owner_approved_controlled_micro_live_exception
        and result.micro_live_status == module.CONTROLLED_MICRO_LIVE_EXCEPTION_READY
        and input_data.max_one_live_order_enforced
    ):
        order_attempt_requested = True
        order_payload = _build_order_payload(input_data)
        token = runtime_item.get("broker_api_token")
        account_id = runtime_item.get("broker_account_id")
        endpoint = runtime_item.get("endpoint", OANDA_LIVE_ENDPOINT)
        if endpoint != OANDA_LIVE_ENDPOINT:
            order_response = {"error": "Invalid live endpoint for controlled micro-live runner."}
            order_status = "not_created"
            order_status_code = 0
        elif account_id and token:
            final_order_endpoint = (
                f"{OANDA_LIVE_ENDPOINT.rstrip('/')}/v3/accounts/{account_id}/orders"
            )
            request_payload = {
                "order_endpoint": final_order_endpoint,
                "headers": {"Authorization": f"Bearer {token}"},
                "order_payload": order_payload,
            }
            order_endpoint = final_order_endpoint
            order_response, order_status_code, order_attempt_success = _post_json_request(
                request_payload,
            )
            order_attempted = True
            order_attempt_count = 1
            order_status = "created" if order_attempt_success else "not_created"
        else:
            order_response = {"error": "Missing live broker runtime credentials"}
            order_status = "not_created"
        if order_attempted:
            result_dict["broker_api_called"] = True
            result_dict["live_order_execution"] = order_attempt_success

    runtime_summary = _build_runtime_summary(
        input_data=input_data,
        result_dict=result_dict,
        runtime_item=runtime_item,
        order_attempt_requested=order_attempt_requested,
        order_attempted=order_attempted,
        order_attempt_count=order_attempt_count,
        order_attempt_success=order_attempt_success,
        order_status=order_status,
        order_status_code=order_status_code,
        order_payload=order_payload,
        order_endpoint=order_endpoint,
        order_response=order_response,
    )

    payload = {
        "module": "forex_controlled_micro_live_exception_runner_v1",
        "packet_id": PACKET_ID,
        "input": module.input_as_dict(input_data),
        "result": result_dict,
        "runtime_summary": runtime_summary,
        "runner_summary": {
            "owner_flag_present": owner_approved_controlled_micro_live_exception,
            "runtime_item_reference": BROKER_ITEM_NAME,
            "next_stage_after_success": "micro_live_evidence_review",
        },
    }

    if write_report:
        _write_outputs(payload, state_output, report_output)

    return payload


def _write_outputs(payload: dict[str, Any], state_output: Path, report_output: Path) -> None:
    sanitized = _redact_runtime_state(payload)
    state_output.parent.mkdir(parents=True, exist_ok=True)
    state_output.write_text(
        json.dumps(sanitized, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(_build_report_text(sanitized), encoding="utf-8")


def _build_report_text(payload: dict[str, Any]) -> str:
    result = payload["result"]
    runtime = payload["runtime_summary"]
    blockers = "\n".join(f"- {item}" for item in result["blockers"]) or "- (none)"
    return (
        "# AIOS Forex Controlled Micro-Live Exception Runner V1 Report\n\n"
        "## Packet evaluation\n"
        f"- micro_live_status: {result['micro_live_status']}\n"
        f"- current_stage: {result['current_stage']}\n"
        f"- next_stage: {result['next_stage']}\n"
        f"- runtime_mode: {result['runtime_mode']}\n"
        f"- safe_next_action: {result['safe_next_action']}\n"
        "- blockers:\n"
        f"{blockers}\n\n"
        "## Repo-safe gate state\n"
        f"- live_order_execution: {str(result['live_order_execution']).lower()}\n"
        f"- demo_order_execution: {str(result['demo_order_execution']).lower()}\n"
        f"- money_movement: {str(result['money_movement']).lower()}\n"
        f"- broker_api_called: {str(result['broker_api_called']).lower()}\n"
        f"- bitwarden_cli_called: {str(result['bitwarden_cli_called']).lower()}\n"
        f"- credentials_read: {str(result['credentials_read']).lower()}\n"
        f"- env_file_read: {str(result['env_file_read']).lower()}\n"
        f"- scheduler_started: {str(result['scheduler_started']).lower()}\n"
        f"- daemon_started: {str(result['daemon_started']).lower()}\n"
        f"- webhook_started: {str(result['webhook_started']).lower()}\n"
        f"- runtime_item_ref: {result['live_item_ref']}\n"
        f"- order_intent_summary: {runtime['order_intent_summary']}\n"
        f"- order_attempt_requested: {str(runtime['order_attempt_requested']).lower()}\n"
        f"- order_attempted: {str(runtime['order_attempted']).lower()}\n"
        f"- order_attempt_count: {runtime['order_attempt_count']}\n"
        f"- order_status: {runtime['order_status']}\n"
        f"- order_status_code: {runtime['order_status_code']}\n"
    )


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--owner-approved-controlled-micro-live-exception",
        action="store_true",
        default=False,
    )
    parser.add_argument("--state-output", type=Path, default=STATE_PATH)
    parser.add_argument("--report-output", type=Path, default=REPORT_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> dict[str, Any]:
    args = _parse_args(argv)
    payload = run_forex_controlled_micro_live_exception_runner_v1(
        owner_approved_controlled_micro_live_exception=args.owner_approved_controlled_micro_live_exception,
        state_output=args.state_output,
        report_output=args.report_output,
        write_report=True,
    )
    print(json.dumps(_redact_runtime_state(payload), indent=2))
    return payload


if __name__ == "__main__":
    main()
    raise SystemExit(0)


__all__ = [
    "run_forex_controlled_micro_live_exception_runner_v1",
    "_build_order_payload",
    "_redact_runtime_state",
    "_post_json_request",
]
