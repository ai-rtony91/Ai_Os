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

from automation.forex_engine.oanda_demo_trade_320_read_only_broker_telemetry_repair_v1 import (  # noqa: E402
    PACKET_NAME,
    READ_ONLY_HELPER_MISSING,
    REPORT_PATH,
    diagnose_trade_320_read_only_broker_telemetry,
    write_trade_320_read_only_broker_telemetry_repair_report,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    evidence = _load_evidence(args)
    result = diagnose_trade_320_read_only_broker_telemetry(evidence)
    report_path = None
    if args.write_report:
        report_path = write_trade_320_read_only_broker_telemetry_repair_report(
            result,
            args.report_path,
            branch=_current_branch(),
        )

    payload = {
        "script_status": result["broker_evidence_status"],
        "packet_name": PACKET_NAME,
        "report_path": str(report_path) if report_path else None,
        "broker_network_call_performed": False,
        "owner_run_read_broker_now_requested": bool(args.owner_run_read_broker_now),
        "order_placement_performed": False,
        "order_close_performed": False,
        "order_mutation_performed": False,
        "trade_mutation_performed": False,
        "position_mutation_performed": False,
        "live_endpoint_used": False,
        "secrets_written": False,
        "result": result,
    }
    _print_json(payload)
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description=(
            "AIOS OANDA demo trade 320 read-only broker telemetry repair V1."
        ),
    )
    parser.add_argument("--evidence-file")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--report-path", default=REPORT_PATH)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--owner-run-read-broker-now",
        action="store_true",
        help=(
            "Owner-run diagnostic flag only. Packet 05 does not call the broker "
            "or invoke the read-only broker helper."
        ),
    )
    return parser


def _load_evidence(args: argparse.Namespace) -> dict[str, Any] | None:
    if args.evidence_file:
        path = Path(args.evidence_file)
        return _json_mapping(path.read_text(encoding="utf-8"))
    if args.owner_run_read_broker_now:
        return {
            "owner_run_read_broker_now": True,
            "broker_read_mode": "OWNER_RUN_READ_ONLY_BROKER_REQUESTED",
            "broker_read_method": "GET",
            "read_only_helper_missing": True,
            "helper_status": READ_ONLY_HELPER_MISSING,
            "sanitized_evidence_only": True,
            "no_new_order_placed": True,
            "no_live_trade_placed": True,
            "no_broker_state_modified": True,
            "no_secrets_written": True,
            "withdrawal_allowed_now": False,
            "transfer_allowed_now": False,
            "money_movement_allowed_now": False,
        }
    return None


def _json_mapping(raw: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "broker_evidence_status": "INVALID_TELEMETRY_EVIDENCE",
            "blockers": ["evidence_file_must_contain_json_object"],
            "sanitized_evidence_only": True,
        }
    if isinstance(parsed, dict):
        return parsed
    return {
        "broker_evidence_status": "INVALID_TELEMETRY_EVIDENCE",
        "blockers": ["evidence_json_root_must_be_object"],
        "sanitized_evidence_only": True,
    }


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

