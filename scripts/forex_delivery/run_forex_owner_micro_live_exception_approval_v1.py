"""Runner for the AI OS owner micro-live exception approval gate packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.forex_owner_micro_live_exception_approval_v1 import (  # noqa: E402
    CURRENT_STAGE,
    NEXT_STAGE_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER,
    OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED,
    OwnerMicroLiveExceptionApprovalResult,
    build_default_input,
    evaluate_owner_micro_live_exception_approval_v1,
    input_as_dict,
    result_as_dict,
)


STATE_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_V1_STATE.json",
)
REPORT_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_V1_REPORT.md",
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate owner micro-live exception approval readiness.",
        allow_abbrev=False,
    )
    parser.add_argument(
        "--state-output",
        default=str(STATE_PATH),
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
    payload = run_forex_owner_micro_live_exception_approval_v1(
        state_output=Path(args.state_output),
        report_output=Path(args.report_output),
        write_report=not args.no_report,
    )
    print(json.dumps(payload["result"], sort_keys=True))
    return 0


def run_forex_owner_micro_live_exception_approval_v1(
    *,
    state_output: Path = STATE_PATH,
    report_output: Path = REPORT_PATH,
    write_report: bool = True,
) -> dict[str, Any]:
    input_data = build_default_input()
    result = evaluate_owner_micro_live_exception_approval_v1(input_data)
    payload = {
        "packet_id": "PKT-FOREX-OWNER-MICRO-LIVE-EXCEPTION-APPROVAL-V1",
        "module": "forex_owner_micro_live_exception_approval_v1",
        "input": input_as_dict(input_data),
        "result": result_as_dict(result),
        "approval_summary": _build_summary(result),
    }
    if write_report:
        _write_outputs(payload, state_output, report_output)
    return payload


def _build_summary(result: OwnerMicroLiveExceptionApprovalResult) -> dict[str, Any]:
    return {
        "default_mode": "dry_run",
        "current_stage": CURRENT_STAGE,
        "owner_approval_status": result.owner_approval_status,
        "next_stage": result.next_stage,
        "next_stage_after_success": NEXT_STAGE_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER,
        "ready_for_controlled_micro_live_exception_runner": (
            result.owner_approval_status == OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED
        ),
        "protected_boundaries_static":
            result.live_order_execution is False
            and result.money_movement is False
            and result.broker_api_called is False
            and result.bitwarden_cli_called is False
            and result.credentials_read is False
            and result.env_file_read is False
            and result.scheduler_started is False
            and result.daemon_started is False
            and result.webhook_started is False,
    }


def _write_outputs(
    payload: dict[str, Any],
    state_output: Path,
    report_output: Path,
) -> None:
    state_output.parent.mkdir(parents=True, exist_ok=True)
    state_output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(_build_report_text(payload), encoding="utf-8")


def _build_report_text(payload: dict[str, Any]) -> str:
    result = payload["result"]
    blockers = "\n".join(f"- {item}" for item in result["blockers"]) or "- none"
    return (
        "# AIOS Forex Owner Micro-Live Exception Approval V1 Report\n\n"
        "## Packet evaluation\n"
        f"- owner_approval_status: {result['owner_approval_status']}\n"
        f"- current_stage: {result['current_stage']}\n"
        f"- next_stage: {result['next_stage']}\n"
        "- blockers:\n"
        f"{blockers}\n"
        f"- safe_next_action: {result['safe_next_action']}\n\n"
        "## Evidence and owner confirmations\n"
        f"- supervised_demo_evidence_clean: {str(result['supervised_demo_evidence_clean']).lower()}\n"
        f"- supervised_demo_order_created: {str(result['supervised_demo_order_created']).lower()}\n"
        f"- demo_order_status_code: {result['demo_order_status_code']}\n"
        f"- demo_order_redaction_verified: {str(result['demo_order_redaction_verified']).lower()}\n"
        f"- max_one_demo_order_verified: {str(result['max_one_demo_order_verified']).lower()}\n"
        f"- owner_micro_live_exception_approval: {str(result['owner_micro_live_exception_approval']).lower()}\n"
        f"- owner_understands_live_money_risk: {str(result['owner_understands_live_money_risk']).lower()}\n"
        f"- owner_confirms_micro_size_only: {str(result['owner_confirms_micro_size_only']).lower()}\n"
        f"- owner_confirms_max_one_live_order: {str(result['owner_confirms_max_one_live_order']).lower()}\n"
        f"- owner_confirms_no_autonomous_runtime: {str(result['owner_confirms_no_autonomous_runtime']).lower()}\n"
        f"- owner_confirms_kill_switch_ready: {str(result['owner_confirms_kill_switch_ready']).lower()}\n"
        f"- owner_confirms_daily_loss_cap_ready: {str(result['owner_confirms_daily_loss_cap_ready']).lower()}\n"
        f"- owner_confirms_trade_risk_cap_ready: {str(result['owner_confirms_trade_risk_cap_ready']).lower()}\n"
        f"- owner_confirms_audit_log_ready: {str(result['owner_confirms_audit_log_ready']).lower()}\n\n"
        "## Repo-safe gate state\n"
        f"- live_order_execution: {str(result['live_order_execution']).lower()}\n"
        f"- money_movement: {str(result['money_movement']).lower()}\n"
        f"- broker_api_called: {str(result['broker_api_called']).lower()}\n"
        f"- bitwarden_cli_called: {str(result['bitwarden_cli_called']).lower()}\n"
        f"- credentials_read: {str(result['credentials_read']).lower()}\n"
        f"- env_file_read: {str(result['env_file_read']).lower()}\n"
        f"- scheduler_started: {str(result['scheduler_started']).lower()}\n"
        f"- daemon_started: {str(result['daemon_started']).lower()}\n"
        f"- webhook_started: {str(result['webhook_started']).lower()}\n"
        f"- ready_for_controlled_micro_live_exception_runner: {str(payload['approval_summary']['ready_for_controlled_micro_live_exception_runner']).lower()}\n"
        "- target: controlled_micro_live_exception_runner\n"
        "- micro_live_size_policy: minimum_owner_approved_size_only\n"
    )


def _build_report_boolean_list(values: dict[str, Any]) -> list[str]:
    lines = []
    return lines


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "run_forex_owner_micro_live_exception_approval_v1",
    "parse_args",
]
