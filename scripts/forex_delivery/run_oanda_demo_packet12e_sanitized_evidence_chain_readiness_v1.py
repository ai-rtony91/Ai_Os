from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_packet12e_sanitized_evidence_chain_readiness_v1 import (  # noqa: E402
    DEFAULT_OWNER_READ_OUTPUT_PATH,
    DEFAULT_PACKET09_EVIDENCE_PATH,
    DEFAULT_PACKET11_ACCEPTANCE_REPORT_PATH,
    PACKET_NAME,
    REPORT_PATH,
    render_packet12e_sanitized_evidence_chain_readiness_report,
    run_packet12e_sanitized_evidence_chain_readiness,
    write_packet12e_sanitized_evidence_chain_readiness_report,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    result = run_packet12e_sanitized_evidence_chain_readiness(
        owner_read_output_path=args.owner_read_output_path,
        packet09_evidence_path=args.packet09_evidence_path,
        packet11_acceptance_report_path=args.packet11_acceptance_report_path,
    )
    report_path = None
    branch = _current_branch()
    if args.write_report:
        report_path = write_packet12e_sanitized_evidence_chain_readiness_report(
            result,
            args.report_path,
            branch=branch,
        )

    payload = {
        "script_status": result["packet12e_status"],
        "packet_name": PACKET_NAME,
        "report_path": str(report_path) if report_path else None,
        "result": result,
        "packet12e_status": result["packet12e_status"],
        "status": result["packet12e_status"],
        "ready_to_advance": result["ready_to_advance"],
        "missing_files": result["missing_files"],
        "missing_required_files": result["missing_required_files"],
        "unsafe_evidence_found": result["unsafe_evidence_found"],
        "rejected_unsafe_evidence": result["rejected_unsafe_evidence"],
        "unsafe_findings": result["unsafe_findings"],
        "acceptance_confirmed": result["acceptance_confirmed"],
        "no_new_order_placed": result["no_new_order_placed"],
        "no_live_trade_placed": result["no_live_trade_placed"],
        "no_broker_state_modified": result["no_broker_state_modified"],
        "no_secrets_written": result["no_secrets_written"],
        "raw_broker_payload_persisted": result["raw_broker_payload_persisted"],
        "broker_network_call_performed": result["broker_network_call_performed"],
        "broker_helper_call_performed": result["broker_helper_call_performed"],
        "validator_broker_network_call_performed": result[
            "validator_broker_network_call_performed"
        ],
        "validator_broker_helper_call_performed": result[
            "validator_broker_helper_call_performed"
        ],
        "money_movement_allowed_now": result["money_movement_allowed_now"],
        "withdrawal_allowed_now": result["withdrawal_allowed_now"],
        "transfer_allowed_now": result["transfer_allowed_now"],
        "profit_reserve_bucket_mode": result["profit_reserve_bucket_mode"],
        "next_action": result["next_action"],
    }
    if args.json:
        _print_json(payload)
    else:
        print(
            render_packet12e_sanitized_evidence_chain_readiness_report(
                result,
                branch=branch,
            )
        )
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description=(
            "AIOS OANDA demo Packet 12E sanitized evidence chain readiness validator."
        ),
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--report-path", default=REPORT_PATH)
    parser.add_argument(
        "--owner-read-output-path",
        "--owner-run-broker-read-output-path",
        dest="owner_read_output_path",
        default=DEFAULT_OWNER_READ_OUTPUT_PATH,
    )
    parser.add_argument(
        "--packet09-evidence-path",
        default=DEFAULT_PACKET09_EVIDENCE_PATH,
    )
    parser.add_argument(
        "--packet11-acceptance-report-path",
        "--acceptance-report-path",
        dest="packet11_acceptance_report_path",
        default=DEFAULT_PACKET11_ACCEPTANCE_REPORT_PATH,
    )
    return parser


def _current_branch() -> str:
    try:
        completed = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return "UNKNOWN"
    branch = completed.stdout.strip()
    return branch or "UNKNOWN"


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
