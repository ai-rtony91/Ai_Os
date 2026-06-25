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

from automation.forex_engine.oanda_demo_owner_run_sanitized_broker_read_output_generator_v1 import (  # noqa: E402
    DEFAULT_JSON_PATH,
    PACKET_NAME,
    REPORT_PATH,
    generate_owner_run_sanitized_broker_read_output,
    write_owner_run_sanitized_broker_read_output_generator_report,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    owner_read_result = _load_owner_read_result(args.owner_read_result_file)
    result = generate_owner_run_sanitized_broker_read_output(
        owner_run_read_broker_now=args.owner_run_read_broker_now,
        write_json=args.write_json,
        json_path=args.json_path,
        owner_read_result=owner_read_result,
    )
    report_path = None
    if args.write_report:
        report_path = write_owner_run_sanitized_broker_read_output_generator_report(
            result,
            args.report_path,
            branch=_current_branch(),
        )

    payload = {
        "script_status": result["output_status"],
        "packet_name": PACKET_NAME,
        "report_path": str(report_path) if report_path else None,
        "output_status": result["output_status"],
        "json_written": result["json_written"],
        "json_path": result["json_path"],
        "sanitized_output_ready": result["sanitized_output_ready"],
        "required_fields_present": result["required_fields_present"],
        "missing_required_fields": result["missing_required_fields"],
        "rejected_forbidden_fields": result["rejected_forbidden_fields"],
        "unsafe_audit_flags": result["unsafe_audit_flags"],
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
        "result": result,
    }
    _print_json(payload)
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description=(
            "AIOS OANDA demo owner-run sanitized broker-read output generator V1."
        ),
    )
    parser.add_argument("--owner-run-read-broker-now", action="store_true")
    parser.add_argument("--owner-read-result-file")
    parser.add_argument("--write-json", action="store_true")
    parser.add_argument("--json-path", default=DEFAULT_JSON_PATH)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--report-path", default=REPORT_PATH)
    parser.add_argument("--json", action="store_true")
    return parser


def _load_owner_read_result(path_text: str | None) -> dict[str, Any] | None:
    if not path_text:
        return None
    path = Path(path_text)
    return _json_mapping(path.read_text(encoding="utf-8"))


def _json_mapping(raw: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "broker_evidence_status": "SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE",
            "evidence_source": "json_parse_failure",
        }
    if isinstance(parsed, dict):
        return parsed
    return {
        "broker_evidence_status": "SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE",
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
