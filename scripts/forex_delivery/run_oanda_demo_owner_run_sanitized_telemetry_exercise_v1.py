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

from automation.forex_engine.oanda_demo_owner_run_sanitized_telemetry_exercise_v1 import (  # noqa: E402
    PACKET_NAME,
    REPORT_PATH,
    run_owner_run_sanitized_telemetry_exercise,
    write_owner_run_sanitized_telemetry_exercise_report,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    evidence = _load_evidence(args)
    result = run_owner_run_sanitized_telemetry_exercise(
        owner_run_read_broker_now=args.owner_run_read_broker_now,
        evidence=evidence,
    )
    report_path = None
    if args.write_report:
        report_path = write_owner_run_sanitized_telemetry_exercise_report(
            result,
            args.report_path,
            branch=_current_branch(),
        )

    payload = {
        "script_status": result["exercise_status"],
        "packet_name": PACKET_NAME,
        "report_path": str(report_path) if report_path else None,
        "exercise_status": result["exercise_status"],
        "capture_status": result["capture_status"],
        "adapter_status": result["adapter_status"],
        "sanitized_broker_telemetry_ready": result[
            "sanitized_broker_telemetry_ready"
        ],
        "owner_run_read_broker_now": result["owner_run_read_broker_now"],
        "broker_read_performed": result["broker_read_performed"],
        "broker_network_call_performed": result["broker_network_call_performed"],
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "order_placement_performed": False,
        "order_close_performed": False,
        "order_mutation_performed": False,
        "trade_mutation_performed": False,
        "position_mutation_performed": False,
        "live_endpoint_used": False,
        "secrets_written": False,
        "raw_broker_payload_persisted": False,
        "sanitized_evidence_persisted": result["sanitized_evidence_persisted"],
        "result": result,
    }
    _print_json(payload)
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description=(
            "AIOS OANDA demo owner-run sanitized telemetry exercise V1."
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
            "Owner-only read-only OANDA demo telemetry exercise through "
            "Packet 08. This never places, closes, or mutates orders."
        ),
    )
    return parser


def _load_evidence(args: argparse.Namespace) -> dict[str, Any] | None:
    if not args.evidence_file:
        return None
    path = Path(args.evidence_file)
    return _json_mapping(path.read_text(encoding="utf-8"))


def _json_mapping(raw: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "capture_status": "OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_INVALID_SHAPE",
            "adapter_status": "SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE",
            "sanitized_broker_telemetry_ready": False,
            "evidence_source": "json_parse_failure",
        }
    if isinstance(parsed, dict):
        return parsed
    return {
        "capture_status": "OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_INVALID_SHAPE",
        "adapter_status": "SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE",
        "sanitized_broker_telemetry_ready": False,
        "evidence_source": "json_shape_failure",
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
