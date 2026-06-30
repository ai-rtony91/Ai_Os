"""Runner for the AI OS supervised demo evidence review packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.forex_supervised_demo_evidence_review_v1 import (  # noqa: E402
    CURRENT_STAGE,
    RUNTIME_MODE_DRY_RUN,
    SUPERVISED_DEMO_EVIDENCE_CLEAN,
    SupervisedDemoEvidenceReviewResult,
    input_as_dict,
    result_as_dict,
    build_default_input,
    evaluate_supervised_demo_evidence_review_v1,
)


STATE_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_EVIDENCE_REVIEW_V1_STATE.json",
)
REPORT_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_EVIDENCE_REVIEW_V1_REPORT.md",
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate supervised demo evidence review readiness.",
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
    payload = run_forex_supervised_demo_evidence_review_v1(
        state_output=Path(args.state_output),
        report_output=Path(args.report_output),
        write_report=not args.no_report,
    )
    print(json.dumps(payload["result"], sort_keys=True))
    return 0


def run_forex_supervised_demo_evidence_review_v1(
    *,
    state_output: Path = STATE_PATH,
    report_output: Path = REPORT_PATH,
    write_report: bool = True,
) -> dict[str, Any]:
    review_input = build_default_input()
    result = evaluate_supervised_demo_evidence_review_v1(review_input)

    payload = {
        "packet_id": "PKT-FOREX-SUPERVISED-DEMO-EVIDENCE-REVIEW-V1",
        "module": "forex_supervised_demo_evidence_review_v1",
        "input": input_as_dict(review_input),
        "result": result_as_dict(result),
        "review_summary": _build_summary(result),
    }
    if write_report:
        _write_outputs(payload, state_output, report_output)
    return payload


def _build_summary(result: SupervisedDemoEvidenceReviewResult) -> dict[str, Any]:
    return {
        "current_stage": result.current_stage,
        "runtime_mode": RUNTIME_MODE_DRY_RUN,
        "evidence_status": result.evidence_status,
        "next_stage": result.next_stage,
        "next_stage_after_success": "owner_micro_live_exception_approval",
        "ready_for_micro_live_exception": result.evidence_status
        == SUPERVISED_DEMO_EVIDENCE_CLEAN,
        "demo_evidence_review_gate": True,
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
        "# AIOS Forex Supervised Demo Evidence Review V1 Report\n\n"
        "## Packet evaluation\n"
        f"- current_stage: {result['current_stage']}\n"
        f"- evidence_status: {result['evidence_status']}\n"
        f"- next_stage: {result['next_stage']}\n"
        f"- safe_next_action: {result['safe_next_action']}\n"
        "- blockers:\n"
        f"{blockers}\n\n"
        "## Evidence check summary\n"
        f"- supervised_demo_order_attempted: {str(result['supervised_demo_order_attempted']).lower()}\n"
        f"- supervised_demo_order_success: {str(result['supervised_demo_order_success']).lower()}\n"
        f"- order_status: {result['order_status']}\n"
        f"- order_status_code: {result['order_status_code']}\n"
        f"- state_report_present: {str(result['state_report_present']).lower()}\n"
        f"- max_one_order_verified: {str(result['max_one_order_verified']).lower()}\n"
        f"- redaction_verified: {str(result['redaction_verified']).lower()}\n"
        f"- order_endpoint_redacted: {str(result['order_endpoint_redacted']).lower()}\n"
        f"- token_redacted: {str(result['token_redacted']).lower()}\n"
        f"- account_id_redacted: {str(result['account_id_redacted']).lower()}\n\n"
        "## Runtime boundary state\n"
        f"- demo_order_execution: {str(result['demo_order_execution']).lower()}\n"
        f"- live_order_execution: {str(result['live_order_execution']).lower()}\n"
        f"- money_movement: {str(result['money_movement']).lower()}\n"
        f"- broker_api_called: {str(result['broker_api_called']).lower()}\n"
        f"- scheduler_started: {str(result['scheduler_started']).lower()}\n"
        f"- daemon_started: {str(result['daemon_started']).lower()}\n"
        f"- webhook_started: {str(result['webhook_started']).lower()}\n"
        f"- ready_for_micro_live_exception_approval: {str(result['next_stage'] == 'owner_micro_live_exception_approval').lower()}\n"
        f"- current_stage: {CURRENT_STAGE}\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "run_forex_supervised_demo_evidence_review_v1",
    "parse_args",
]
