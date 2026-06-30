"""Runner for the broker runtime read-only auth probe packet."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_read_only_client import OandaReadOnlyClient  # noqa: E402
from automation.forex_engine.forex_broker_runtime_read_only_auth_probe_v1 import (  # noqa: E402
    BROKER_RUNTIME_READ_ONLY_AUTH_PROBE_READY,
    BROKER_RUNTIME_READ_ONLY_AUTH_PROVEN,
    DEFAULT_ALLOWED_MODE,
    DEFAULT_BROKER_ACCOUNT_ID_FIELD_REF,
    DEFAULT_BROKER_API_TOKEN_FIELD_REF,
    DEFAULT_ENDPOINT,
    DEFAULT_ENDPOINT_FIELD_REF,
    DEFAULT_ENVIRONMENT,
    DEFAULT_ENVIRONMENT_FIELD_REF,
    DEFAULT_ALLOWED_MODE_FIELD_REF,
    DEFAULT_BROKER_RUNTIME_ITEM_REF,
    CURRENT_SESSION_WINDOW_DAYS_PER_WEEK,
    CURRENT_SESSION_WINDOW_HOURS,
    OANDA_PRACTICE_READ_ONLY_ACCOUNT_PROBE_REQUIRED,
    build_default_input,
    evaluate_broker_runtime_read_only_auth_probe,
    input_as_dict,
    result_as_dict,
    BrokerRuntimeReadOnlyAuthProbeInput,
    BrokerRuntimeReadOnlyAuthProbeResult,
    redact_sensitive_values,
)


STATE_JSON_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_BROKER_RUNTIME_READ_ONLY_AUTH_PROBE_V1_STATE.json",
)
REPORT_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_BROKER_RUNTIME_READ_ONLY_AUTH_PROBE_V1_REPORT.md",
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AIOS forex broker runtime read-only auth probe.",
        allow_abbrev=False,
    )
    parser.add_argument(
        "--owner-approved-read-only-probe",
        action="store_true",
        help="Enable owner-approved runtime probe using BW_SESSION and Bitwarden item read.",
    )
    parser.add_argument(
        "--state-output",
        default=str(STATE_JSON_PATH),
        help="State output file path.",
    )
    parser.add_argument(
        "--report-output",
        default=str(REPORT_PATH),
        help="Report output file path.",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip writing report markdown output.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Alias for compatibility; output is JSON regardless.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = run_probe(
        owner_approved_mode=args.owner_approved_read_only_probe,
        state_output=Path(args.state_output),
        report_output=Path(args.report_output),
        write_report=not args.no_report,
    )
    print(json.dumps(payload))
    return 0


def run_probe(
    *,
    owner_approved_mode: bool,
    state_output: Path = STATE_JSON_PATH,
    report_output: Path = REPORT_PATH,
    write_report: bool = True,
) -> dict[str, Any]:
    probe_input = build_default_input(
        runtime_probe_requested=owner_approved_mode,
        owner_approved_read_only_probe=owner_approved_mode,
    )

    runtime_summary: dict[str, Any] = {
        "default_mode": "dry_run",
        "owner_runtime_flag": "--owner-approved-read-only-probe",
        "runtime_mode": owner_approved_mode,
        "runtime_stage": "broker_runtime_read_only_auth_probe",
        "bw_session_required": True,
        "bitwarden_cli_required": True,
        "expected_broker_runtime_item_ref": probe_input.broker_runtime_item_ref,
        "broker_runtime_item_ref": probe_input.broker_runtime_item_ref,
        "field_refs": {
            "broker_api_token": probe_input.broker_api_token_field_ref,
            "broker_account_id": probe_input.broker_account_id_field_ref,
            "endpoint": probe_input.endpoint_field_ref,
            "environment": probe_input.environment_field_ref,
            "allowed_mode": probe_input.allowed_mode_field_ref,
        },
        "expected_endpoint": probe_input.expected_endpoint,
        "expected_environment": probe_input.expected_environment,
        "expected_allowed_mode": probe_input.expected_allowed_mode,
        "runtime_endpoints_allowed": [DEFAULT_ENDPOINT],
        "runtime_environment_allowed": DEFAULT_ENVIRONMENT,
        "runtime_allowed_mode_expected": DEFAULT_ALLOWED_MODE,
        "session_window_hours": CURRENT_SESSION_WINDOW_HOURS,
        "session_window_days_per_week": CURRENT_SESSION_WINDOW_DAYS_PER_WEEK,
        "bitwarden_cli_called": False,
        "bitwarden_cli_available": False,
        "bitwarden_vault_read": False,
        "credentials_read": False,
        "env_file_read": False,
        "bw_session_present": False,
        "broker_api_called": False,
        "order_endpoint_used": False,
        "live_endpoint_used": False,
        "order_execution": False,
        "demo_authorized": False,
        "live_authorized": False,
        "bitwarden_item_read_success": False,
        "oanda_account_summary_read_success": False,
    }

    if owner_approved_mode:
        probe_input = _run_owner_approved_probe(
            probe_input=probe_input,
            runtime_summary=runtime_summary,
        )

    result = evaluate_broker_runtime_read_only_auth_probe(probe_input)

    runtime_summary.update(
        {
            "bitwarden_cli_called": probe_input.bitwarden_cli_called,
            "bitwarden_vault_read": probe_input.bitwarden_vault_read,
            "credentials_read": probe_input.credentials_read,
            "bitwarden_item_read_success": probe_input.bitwarden_item_read_success,
            "oanda_account_summary_read_success": probe_input.broker_account_summary_read_success,
            "bw_session_present": probe_input.bw_session_present,
            "bitwarden_cli_available": probe_input.bitwarden_cli_available,
            "broker_api_called": probe_input.broker_api_called,
            "order_endpoint_used": probe_input.order_endpoint_used,
            "live_endpoint_used": probe_input.live_endpoint_used,
        },
    )

    if result.probe_status == BROKER_RUNTIME_READ_ONLY_AUTH_PROVEN:
        runtime_summary["runtime_probe_success"] = True

    runtime_summary["probe_status"] = result.probe_status
    runtime_summary["current_stage"] = result.current_stage
    runtime_summary["next_stage"] = result.next_stage

    return _write_artifacts(
        probe_input=probe_input,
        probe_result=result,
        runtime_summary=runtime_summary,
        state_output=state_output,
        report_output=report_output,
        write_report=write_report,
    )


def _run_owner_approved_probe(
    probe_input: BrokerRuntimeReadOnlyAuthProbeInput,
    runtime_summary: dict[str, Any],
) -> BrokerRuntimeReadOnlyAuthProbeInput:
    probe_input = _replace(
        probe_input,
        bw_session_present=False,
        bitwarden_cli_available=False,
        bitwarden_cli_called=False,
        bitwarden_vault_read=False,
        credentials_read=False,
        bitwarden_item_read_success=False,
        broker_account_summary_read_success=False,
        broker_api_called=False,
        order_endpoint_used=False,
        live_endpoint_used=False,
    )

    bw_session_present = os.environ.get("BW_SESSION") is not None
    probe_input = _replace(
        probe_input,
        bw_session_present=bw_session_present,
    )
    runtime_summary["bw_session_present"] = bw_session_present

    if not bw_session_present:
        return probe_input

    bw_path = shutil.which("bw")
    probe_input = _replace(probe_input, bitwarden_cli_available=bw_path is not None)
    runtime_summary["bitwarden_cli_available"] = bw_path is not None

    if not probe_input.bitwarden_cli_available:
        return probe_input

    raw_item, cli_called = _call_bitwarden_get_item(probe_input.broker_runtime_item_ref)
    probe_input = _replace(
        probe_input,
        bitwarden_cli_called=cli_called,
        bitwarden_vault_read=bool(cli_called and raw_item),
    )
    runtime_summary["bitwarden_cli_called"] = cli_called

    if not cli_called or not raw_item:
        return probe_input

    parsed_item = _parse_bitwarden_item(raw_item)
    token = parsed_item.get(DEFAULT_BROKER_API_TOKEN_FIELD_REF, "")
    account_id = parsed_item.get(DEFAULT_BROKER_ACCOUNT_ID_FIELD_REF, "")
    parsed_endpoint = parsed_item.get(DEFAULT_ENDPOINT_FIELD_REF, "")
    parsed_environment = parsed_item.get(DEFAULT_ENVIRONMENT_FIELD_REF, "")
    parsed_allowed_mode = parsed_item.get(DEFAULT_ALLOWED_MODE_FIELD_REF, "")

    runtime_summary["bitwarden_reference_payload"] = redact_sensitive_values(
        {
            "field_refs": parsed_item,
            "custom_ref": probe_input.broker_runtime_item_ref,
        },
        token=token,
        account_id=account_id,
    )
    runtime_summary["bitwarden_item_fields_found"] = {
        "broker_api_token": bool(token),
        "broker_account_id": bool(account_id),
        "endpoint": bool(parsed_endpoint),
        "environment": bool(parsed_environment),
        "allowed_mode": bool(parsed_allowed_mode),
    }

    probe_input = _replace(
        probe_input,
        credentials_read=bool(token and account_id),
        bitwarden_item_read_success=bool(
            token
            and account_id
            and probe_input.broker_runtime_item_ref == DEFAULT_BROKER_RUNTIME_ITEM_REF
            and parsed_endpoint == probe_input.expected_endpoint == DEFAULT_ENDPOINT
            and parsed_environment == probe_input.expected_environment == DEFAULT_ENVIRONMENT
            and parsed_allowed_mode == probe_input.expected_allowed_mode == DEFAULT_ALLOWED_MODE,
        ),
    )
    runtime_summary["credentials_read"] = bool(token and account_id)
    runtime_summary["bitwarden_vault_read"] = bool(cli_called and raw_item)
    runtime_summary["bitwarden_item_read_success"] = probe_input.bitwarden_item_read_success

    if not probe_input.bitwarden_item_read_success:
        return probe_input

    probe_input = _replace(probe_input, broker_api_called=True)
    runtime_summary["broker_api_called"] = True
    runtime_summary["endpoint_used"] = DEFAULT_ENDPOINT

    try:
        client = OandaReadOnlyClient(
            api_token=token,
            account_id=account_id,
            environment="practice",
        )
        summary = client.account_summary()
        runtime_summary["oanda_summary_read"] = True
        runtime_summary["oanda_summary"] = redact_sensitive_values(
            summary,
            token=token,
            account_id=account_id,
        )
        probe_input = _replace(probe_input, broker_account_summary_read_success=True)
        runtime_summary["oanda_account_summary_read_success"] = True
    except Exception:
        runtime_summary["oanda_summary_read"] = False
        runtime_summary["oanda_summary"] = {"error": OANDA_PRACTICE_READ_ONLY_ACCOUNT_PROBE_REQUIRED}
        probe_input = _replace(probe_input, broker_account_summary_read_success=False)
        runtime_summary["oanda_account_summary_read_success"] = False

    return probe_input


def _call_bitwarden_get_item(item_ref: str) -> tuple[str, bool]:
    try:
        completed = subprocess.run(
            ["bw", "get", "item", item_ref],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return "", False

    if completed.returncode != 0:
        return "", False
    return completed.stdout, True


def _parse_bitwarden_item(raw_item: str) -> dict[str, str]:
    if not raw_item:
        return {}

    try:
        payload = json.loads(raw_item)
    except json.JSONDecodeError:
        return {}

    if not isinstance(payload, dict):
        return {}

    parsed_fields: dict[str, str] = {}
    raw_fields = payload.get("fields") or []
    if isinstance(raw_fields, list):
        for entry in raw_fields:
            if not isinstance(entry, dict):
                continue
            key = str(entry.get("name", "")).strip()
            value = str(entry.get("value", "")).strip()
            if not key:
                continue
            parsed_fields[key] = value
    elif isinstance(raw_fields, dict):
        for key, value in raw_fields.items():
            parsed_fields[str(key).strip()] = str(value).strip()

    return {
        DEFAULT_BROKER_API_TOKEN_FIELD_REF: parsed_fields.get(DEFAULT_BROKER_API_TOKEN_FIELD_REF, ""),
        DEFAULT_BROKER_ACCOUNT_ID_FIELD_REF: parsed_fields.get(DEFAULT_BROKER_ACCOUNT_ID_FIELD_REF, ""),
        DEFAULT_ENDPOINT_FIELD_REF: parsed_fields.get(DEFAULT_ENDPOINT_FIELD_REF, ""),
        DEFAULT_ENVIRONMENT_FIELD_REF: parsed_fields.get(DEFAULT_ENVIRONMENT_FIELD_REF, ""),
        DEFAULT_ALLOWED_MODE_FIELD_REF: parsed_fields.get(DEFAULT_ALLOWED_MODE_FIELD_REF, ""),
    }


def _replace(
    probe_input: BrokerRuntimeReadOnlyAuthProbeInput,
    **changes: Any,
) -> BrokerRuntimeReadOnlyAuthProbeInput:
    return probe_input.__class__(**{**asdict(probe_input), **changes})  # type: ignore[arg-type]


def _write_artifacts(
    *,
    probe_input: BrokerRuntimeReadOnlyAuthProbeInput,
    probe_result: BrokerRuntimeReadOnlyAuthProbeResult,
    runtime_summary: dict[str, Any],
    state_output: Path,
    report_output: Path,
    write_report: bool,
) -> dict[str, Any]:
    input_payload = input_as_dict(probe_input)
    result_payload = result_as_dict(probe_result)
    summary_payload = redact_sensitive_values(
        runtime_summary,
        token="",
        account_id="",
    )

    payload = {
        "input": input_payload,
        "result": result_payload,
        "runtime_summary": summary_payload,
    }

    state_output.parent.mkdir(parents=True, exist_ok=True)
    state_output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if write_report:
        report_output.parent.mkdir(parents=True, exist_ok=True)
        report_output.write_text(
            _build_report_markdown(payload),
            encoding="utf-8",
        )

    return payload


def _build_report_markdown(payload: dict[str, Any]) -> str:
    result = payload["result"]
    input_data = payload["input"]
    summary = payload["runtime_summary"]
    blockers = result["blockers"]
    blocker_lines = "\n".join(f"- {blocker}" for blocker in blockers) or "- (none)"
    return (
        "# Forex Broker Runtime Read-Only Auth Probe V1 Report\n\n"
        "## Packet evaluation\n"
        f"- probe_status: {result['probe_status']}\n"
        f"- current_stage: {result['current_stage']}\n"
        f"- next_stage: {result['next_stage']}\n"
        f"- broker_runtime_item_ref: {result['broker_runtime_item_ref']}\n"
        f"- redaction_status: {result['redaction_status']}\n"
        f"- safe_next_action: {result['safe_next_action']}\n"
        "- blockers:\n"
        f"{blocker_lines}\n\n"
        "## Boundaries\n"
        f"- bitwarden_cli_called: {result['bitwarden_cli_called']}\n"
        f"- bitwarden_vault_read: {result['bitwarden_vault_read']}\n"
        f"- credentials_read: {result['credentials_read']}\n"
        f"- env_file_read: {result['env_file_read']}\n"
        f"- broker_api_called: {result['broker_api_called']}\n"
        f"- order_execution: {result['order_execution']}\n"
        f"- demo_authorized: {result['demo_authorized']}\n"
        f"- live_authorized: {result['live_authorized']}\n\n"
        "## Contract values\n"
        f"- default_mode: {summary['default_mode']}\n"
        f"- owner_runtime_flag: {summary['owner_runtime_flag']}\n"
        f"- runtime_mode: {'enabled' if summary['runtime_mode'] else 'disabled'}\n"
        f"- runtime_stage: {summary['runtime_stage']}\n"
        f"- bw_session_required: {summary['bw_session_required']}\n"
        f"- bitwarden_cli_required: {summary['bitwarden_cli_required']}\n"
        f"- expected_endpoint: {summary['expected_endpoint']}\n"
        f"- expected_environment: {summary['expected_environment']}\n"
        f"- expected_allowed_mode: {summary['expected_allowed_mode']}\n"
        f"- session_window_hours: {summary['session_window_hours']}\n"
        f"- session_window_days_per_week: {summary['session_window_days_per_week']}\n"
        f"- item_ref: {input_data['broker_runtime_item_ref']}\n"
        f"- next_stage_after_success: execution_control_stack\n\n"
        "## Scope checks\n"
        f"- bitwarden_cli_available: {summary['bitwarden_cli_available']}\n"
        f"- bw_session_present: {summary['bw_session_present']}\n"
        f"- bitwarden_item_read_success: {summary['bitwarden_item_read_success']}\n"
        f"- oanda_account_summary_read_success: {summary['oanda_account_summary_read_success']}\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
