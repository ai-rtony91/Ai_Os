"""Runner for the Forex execution control stack contract."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.forex_execution_control_stack_v1 import (  # noqa: E402
    SAFE_MODE,
    CURRENT_SESSION_WINDOW_DAYS_PER_WEEK,
    CURRENT_SESSION_WINDOW_HOURS,
    PACKET_ID,
    build_default_input,
    evaluate_execution_control_stack,
    input_as_dict,
    result_as_dict,
)


STATE_JSON_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_EXECUTION_CONTROL_STACK_V1_STATE.json",
)
REPORT_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_EXECUTION_CONTROL_STACK_V1_REPORT.md",
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AIOS forex execution control stack.",
        allow_abbrev=False,
    )
    parser.add_argument(
        "--owner-demo-approval",
        action="store_true",
        help="Owner supervised demo approval already granted.",
    )
    parser.add_argument(
        "--owner-live-approval",
        action="store_true",
        help="Owner live approval already granted (informational only).",
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
        help="Skip writing markdown report output.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = run_execution_control_stack(
        owner_demo_approval=args.owner_demo_approval,
        owner_live_approval=args.owner_live_approval,
        state_output=Path(args.state_output),
        report_output=Path(args.report_output),
        write_report=not args.no_report,
    )
    print(json.dumps(payload))
    return 0


def run_execution_control_stack(
    *,
    owner_demo_approval: bool = False,
    owner_live_approval: bool = False,
    state_output: Path = STATE_JSON_PATH,
    report_output: Path = REPORT_PATH,
    write_report: bool = True,
) -> dict[str, Any]:
    control_input = build_default_input(
        owner_demo_approval=owner_demo_approval,
        owner_live_approval=owner_live_approval,
    )
    result = evaluate_execution_control_stack(control_input)

    control_summary: dict[str, Any] = {
        "packet_id": PACKET_ID,
        "default_mode": SAFE_MODE,
        "current_stage": result.current_stage,
        "next_stage": result.next_stage,
        "session_window_hours": control_input.session_window_hours,
        "session_window_days_per_week": control_input.session_window_days_per_week,
    }

    payload = {
        "input": input_as_dict(control_input),
        "result": result_as_dict(result),
        "control_summary": control_summary,
    }

    return _write_artifacts(
        control_input=control_input,
        control_result=result,
        control_summary=control_summary,
        state_output=state_output,
        report_output=report_output,
        write_report=write_report,
    )


def _write_artifacts(
    *,
    control_input: Any,
    control_result: Any,
    control_summary: dict[str, Any],
    state_output: Path,
    report_output: Path,
    write_report: bool,
) -> dict[str, Any]:
    payload = {
        "input": asdict(control_input),
        "result": asdict(control_result),
        "control_summary": control_summary,
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
    summary = payload["control_summary"]
    blockers = result["blockers"]
    blocker_lines = "\n".join(f"- {blocker}" for blocker in blockers) or "- (none)"

    return (
        "# Forex Execution Control Stack V1 Report\n\n"
        "## Packet evaluation\n"
        f"- control_status: {result['control_status']}\n"
        f"- current_stage: {result['current_stage']}\n"
        f"- next_stage: {result['next_stage']}\n"
        f"- safe_next_action: {result['safe_next_action']}\n"
        "- blockers:\n"
        f"{blocker_lines}\n\n"
        "## Control output\n"
        f"- control_stage: {summary['current_stage']}\n"
        f"- next_stage_after_success: {summary['next_stage']}\n"
        f"- packet_id: {summary['packet_id']}\n"
        f"- default_mode: {summary['default_mode']}\n\n"
        "## Boundaries\n"
        f"- broker_api_called: {result['broker_api_called']}\n"
        f"- bitwarden_cli_called: {result['bitwarden_cli_called']}\n"
        f"- credentials_read: {result['credentials_read']}\n"
        f"- env_file_read: {result['env_file_read']}\n"
        f"- order_execution: {result['order_execution']}\n"
        f"- demo_authorized: {result['demo_authorized']}\n"
        f"- live_authorized: {result['live_authorized']}\n"
        f"- kill_switch_state: {result['kill_switch_state']}\n"
        f"- risk_state: {result['risk_state']}\n"
        f"- duplicate_guard_state: {result['duplicate_guard_state']}\n"
        f"- audit_state: {result['audit_state']}\n\n"
        "## Scope settings\n"
        f"- order_intent_id: {payload['input']['order_intent_id']}\n"
        f"- instrument: {payload['input']['instrument']}\n"
        f"- units: {payload['input']['units']}\n"
        f"- side: {payload['input']['side']}\n"
        f"- order_type: {payload['input']['order_type']}\n"
        f"- stop_loss_defined: {payload['input']['stop_loss_defined']}\n"
        f"- take_profit_defined: {payload['input']['take_profit_defined']}\n"
        f"- session_window_hours: {summary['session_window_hours']}\n"
        f"- session_window_days_per_week: {summary['session_window_days_per_week']}\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
