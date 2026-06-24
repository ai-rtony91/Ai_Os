from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_open_trade_monitor_v1 import (  # noqa: E402
    BROKER_EVIDENCE_BLOCKED as MONITOR_BROKER_EVIDENCE_BLOCKED,
    INVALID_EVIDENCE as MONITOR_INVALID_EVIDENCE,
)
from automation.forex_engine.oanda_demo_trade_320_read_only_pl_refresh_v1 import (  # noqa: E402
    OWNER_RUN_READ_ONLY_BROKER_MODE,
    PACKET_NAME,
    REPORT_PATH,
    refresh_trade_320_pl_result,
    write_trade_320_read_only_pl_refresh_report,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    evidence = _load_evidence(args)
    result = refresh_trade_320_pl_result(evidence)
    report_path = None
    if args.write_report:
        report_path = write_trade_320_read_only_pl_refresh_report(
            result,
            args.report_path,
            branch=_current_branch(),
        )

    payload = {
        "script_status": result["result_bucket"],
        "packet_name": PACKET_NAME,
        "report_path": str(report_path) if report_path else None,
        "broker_read_mode": result["broker_read_mode"],
        "broker_network_call_performed": bool(args.owner_run_read_broker_now),
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
    return 1 if result["result_bucket"] == MONITOR_INVALID_EVIDENCE else 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description="AIOS OANDA demo trade 320 read-only P/L refresh V1.",
    )
    parser.add_argument("--evidence-file")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--report-path", default=REPORT_PATH)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--owner-run-read-broker-now",
        action="store_true",
        help=(
            "Owner-only read-only broker refresh. This packet never places, "
            "closes, or mutates orders."
        ),
    )
    return parser


def _load_evidence(args: argparse.Namespace) -> dict[str, Any] | None:
    if args.owner_run_read_broker_now:
        return _owner_run_read_only_monitor_result()
    if args.evidence_file:
        path = Path(args.evidence_file)
        return _json_mapping(path.read_text(encoding="utf-8"))
    return None


def _owner_run_read_only_monitor_result() -> dict[str, Any]:
    try:
        from scripts.run_oanda_demo_open_trade_monitor_v1 import (  # noqa: E402
            main as monitor_main,
        )
    except Exception as exc:  # pragma: no cover - defensive runtime boundary
        return _broker_blocked(
            f"read_only_monitor_helper_import_failed_{type(exc).__name__}"
        )

    command = [
        "--owner-run-read-broker-now",
        "--expected-trade-id",
        "320",
        "--json",
    ]
    stream = StringIO()
    try:
        with redirect_stdout(stream):
            monitor_main(command)
    except Exception as exc:  # pragma: no cover - defensive runtime boundary
        return _broker_blocked(
            f"read_only_monitor_helper_execution_failed_{type(exc).__name__}"
        )

    payload = _json_mapping(stream.getvalue())
    result = payload.get("result")
    if isinstance(result, dict):
        result["broker_read_mode"] = OWNER_RUN_READ_ONLY_BROKER_MODE
        result.setdefault("evidence_source", "owner_run_read_only_monitor_helper")
        return result
    return _broker_blocked("read_only_monitor_helper_result_missing")


def _broker_blocked(blocker: str) -> dict[str, Any]:
    return {
        "status_bucket": MONITOR_BROKER_EVIDENCE_BLOCKED,
        "trade_id": "320",
        "instrument": "EUR_USD",
        "broker_read_mode": OWNER_RUN_READ_ONLY_BROKER_MODE,
        "evidence_source": "owner_run_read_only_monitor_helper",
        "blockers": [blocker],
        "is_broker_blocked": True,
        "order_placement_performed": False,
        "order_close_performed": False,
        "order_mutation_performed": False,
        "live_endpoint_used": False,
        "secrets_written": False,
    }


def _json_mapping(raw: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "status_bucket": MONITOR_INVALID_EVIDENCE,
            "evidence_source": "json_parse_failure",
            "blockers": ["evidence_file_must_contain_json_object"],
        }
    if isinstance(parsed, dict):
        return parsed
    return {
        "status_bucket": MONITOR_INVALID_EVIDENCE,
        "evidence_source": "json_shape_failure",
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
