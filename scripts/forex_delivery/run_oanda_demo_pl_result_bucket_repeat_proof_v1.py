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

from automation.forex_engine.oanda_demo_pl_result_bucket_repeat_proof_v1 import (  # noqa: E402
    INVALID_EVIDENCE,
    OWNER_PACKET_01_OPEN_NEGATIVE_EVIDENCE,
    REPORT_PATH,
    classify_pl_result_and_repeat_proof_lane,
    write_pl_result_bucket_repeat_proof_report,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    evidence = _load_evidence(args.evidence_file)
    result = classify_pl_result_and_repeat_proof_lane(evidence)
    report_path = None
    if args.write_report:
        report_path = write_pl_result_bucket_repeat_proof_report(
            result,
            args.report_path,
            branch=_current_branch(),
        )

    payload = {
        "script_status": result["result_bucket"],
        "report_path": str(report_path) if report_path else None,
        "broker_network_call_performed": False,
        "order_placement_performed": False,
        "order_close_performed": False,
        "order_mutation_performed": False,
        "trade_mutation_performed": False,
        "position_mutation_performed": False,
        "live_endpoint_used": False,
        "secrets_written": False,
        "result": result,
    }
    if args.json:
        _print_json(payload)
    else:
        _print_json(payload)
    return 1 if result["result_bucket"] == INVALID_EVIDENCE else 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description="AIOS OANDA demo P/L result bucket repeat-proof classifier.",
    )
    parser.add_argument("--evidence-file")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--report-path", default=REPORT_PATH)
    parser.add_argument("--json", action="store_true")
    return parser


def _load_evidence(evidence_file: str | None) -> dict[str, Any]:
    if not evidence_file:
        return dict(OWNER_PACKET_01_OPEN_NEGATIVE_EVIDENCE)
    path = Path(evidence_file)
    return _json_mapping(path.read_text(encoding="utf-8"))


def _json_mapping(raw: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "status_bucket": INVALID_EVIDENCE,
            "blockers": ["evidence_file_must_contain_json_object"],
        }
    if isinstance(parsed, dict):
        return parsed
    return {
        "status_bucket": INVALID_EVIDENCE,
        "blockers": ["evidence_json_root_must_be_object"],
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
