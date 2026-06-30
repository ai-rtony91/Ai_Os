"""Runner for the integrated Forex live execution program packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.forex_live_execution_program_v1 import (  # noqa: E402
    EXECUTION_PATH,
    LIVE_22H_6D_EXECUTION_PROGRAM_READY,
    RUNTIME_MODE_DRY_RUN,
    build_default_live_execution_program_input,
    evaluate_live_execution_program,
    input_as_dict,
    result_as_dict,
)

STATE_JSON_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_LIVE_EXECUTION_PROGRAM_V1_STATE.json",
)
REPORT_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_LIVE_EXECUTION_PROGRAM_V1_REPORT.md",
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate the integrated Forex live execution program contract.",
        allow_abbrev=False,
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
        help="Skip writing report markdown output.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = run_forex_live_execution_program_v1(
        state_output=Path(args.state_output),
        report_output=Path(args.report_output),
        write_report=not args.no_report,
    )
    print(json.dumps(payload["result"], sort_keys=True))
    return 0


def run_forex_live_execution_program_v1(
    *,
    state_output: Path = STATE_JSON_PATH,
    report_output: Path = REPORT_PATH,
    write_report: bool = True,
) -> dict[str, Any]:
    program_input = build_default_live_execution_program_input()
    result = evaluate_live_execution_program(program_input)
    payload = {
        "packet_id": "PKT-FOREX-LIVE-EXECUTION-PROGRAM-V1",
        "module": "forex_live_execution_program_v1",
        "input": input_as_dict(program_input),
        "result": result_as_dict(result),
        "program_summary": _build_summary(input_as_dict(program_input), result_as_dict(result)),
    }
    return _write_artifacts(
        payload=payload,
        state_output=state_output,
        report_output=report_output,
        write_report=write_report,
    )


def _build_summary(
    program_input: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "default_mode": RUNTIME_MODE_DRY_RUN,
        "runtime_mode": result["runtime_mode"],
        "current_stage": result["current_stage"],
        "next_stage": result["next_stage"],
        "program_status": result["program_status"],
        "target": "live 22hr/day 6day/week autonomous execution",
        "session_window_hours": program_input["session_window_hours"],
        "session_window_days_per_week": program_input["session_window_days_per_week"],
        "execution_path": result["execution_path"],
    }


def _write_artifacts(
    *,
    payload: dict[str, Any],
    state_output: Path,
    report_output: Path,
    write_report: bool,
) -> dict[str, Any]:
    state_output.parent.mkdir(parents=True, exist_ok=True)
    state_output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if write_report:
        report_output.parent.mkdir(parents=True, exist_ok=True)
        report_output.write_text(_build_report(payload), encoding="utf-8")

    return payload


def _build_report(payload: dict[str, Any]) -> str:
    result = payload["result"]
    blockers = "\n".join(f"- {blocker}" for blocker in result["blockers"]) or "- none"
    return (
        "# AIOS Forex Live Execution Program V1 Report\n\n"
        "## Packet evaluation\n"
        f"- program_status: {result['program_status']}\n"
        f"- current_stage: {result['current_stage']}\n"
        f"- next_stage: {result['next_stage']}\n"
        f"- runtime_mode: {result['runtime_mode']}\n"
        f"- safe_next_action: {result['safe_next_action']}\n"
        "- blockers:\n"
        f"{blockers}\n\n"
        "## Execution path\n"
        f"- execution_path: {' -> '.join(result['execution_path'])}\n"
        f"- complete_path: {' -> '.join(EXECUTION_PATH)}\n\n"
        "## Runtime gate state\n"
        "- demo_order_execution: false\n"
        "- micro_live_order_execution: false\n"
        "- live_order_execution: false\n"
        "- money_movement: false\n"
        "- autonomous_22h_6d_authorized: false\n"
        "- broker_api_called: false\n"
        "- bitwarden_cli_called: false\n"
        "- credentials_read: false\n"
        "- env_file_read: false\n"
        "- scheduler_started: false\n"
        "- daemon_started: false\n"
        "- webhook_started: false\n"
        f"- target: {payload['program_summary']['target']}\n"
        f"- session_window_hours: {payload['program_summary']['session_window_hours']}\n"
        f"- session_window_days_per_week: {payload['program_summary']['session_window_days_per_week']}\n"
        f"- ready_status: {str(result['program_status'] == LIVE_22H_6D_EXECUTION_PROGRAM_READY).lower()}\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
