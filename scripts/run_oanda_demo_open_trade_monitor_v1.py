from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_open_trade_monitor_v1 import (  # noqa: E402
    BROKER_EVIDENCE_BLOCKED,
    INVALID_EVIDENCE,
    OWNER_RUN_TRADE_320_ANCHOR_EVIDENCE,
    REPORT_PATH,
    classify_oanda_demo_trade_state,
    write_oanda_demo_open_trade_monitor_report,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    evidence = _load_evidence(args)
    result = classify_oanda_demo_trade_state(
        evidence,
        expected_trade_id=args.expected_trade_id,
    )
    report_path = None
    if args.write_report:
        report_path = write_oanda_demo_open_trade_monitor_report(
            result,
            args.report_path,
            branch=_current_branch(),
        )

    payload = {
        "script_status": result["status_bucket"],
        "expected_trade_id": str(args.expected_trade_id),
        "report_path": str(report_path) if report_path else None,
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
    if args.json:
        _print_json(payload)
    else:
        _print_json(payload)
    return 1 if result["status_bucket"] in {INVALID_EVIDENCE, BROKER_EVIDENCE_BLOCKED} else 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description="AIOS OANDA demo open-trade read-only monitor V1.",
    )
    parser.add_argument("--evidence-file")
    parser.add_argument("--expected-trade-id", default="320")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--report-path", default=REPORT_PATH)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--owner-run-read-broker-now",
        action="store_true",
        help=(
            "Owner-only read-only broker capture path. Uses the existing OANDA "
            "demo read-only filled-trade helper and never places or closes orders."
        ),
    )
    return parser


def _load_evidence(args: argparse.Namespace) -> dict[str, Any]:
    if args.owner_run_read_broker_now:
        return _owner_run_read_only_broker_evidence()
    if args.evidence_file:
        path = Path(args.evidence_file)
        return _json_mapping(path.read_text(encoding="utf-8"))
    return dict(OWNER_RUN_TRADE_320_ANCHOR_EVIDENCE)


def _owner_run_read_only_broker_evidence() -> dict[str, Any]:
    try:
        from scripts.forex_delivery.run_oanda_demo_read_only_filled_trade_pl_capture_v1 import (  # noqa: E501
            main as read_only_capture_main,
        )
    except Exception as exc:  # pragma: no cover - defensive runtime boundary
        return {
            "status_bucket": BROKER_EVIDENCE_BLOCKED,
            "evidence_source": "owner_run_read_only_broker_helper_import",
            "blockers": [f"read_only_helper_import_failed_{type(exc).__name__}"],
        }

    command = [
        "--execute-read-only-filled-trade-pl-capture-from-vault",
        "--i-confirm-demo-only",
        "--i-confirm-read-only-pl-capture",
        "--i-confirm-windows-vault-only",
        "--i-confirm-no-env-file",
        "--i-confirm-no-repo-persistence",
        "--i-confirm-no-live-endpoint",
        "--i-confirm-no-order",
        "--i-confirm-no-close-trade",
        "--i-confirm-no-mutation",
        "--i-confirm-no-second-order",
        "--i-confirm-no-profit-claim",
    ]
    stream = StringIO()
    try:
        with redirect_stdout(stream):
            read_only_capture_main(command)
    except Exception as exc:  # pragma: no cover - defensive runtime boundary
        return {
            "status_bucket": BROKER_EVIDENCE_BLOCKED,
            "evidence_source": "owner_run_read_only_broker_helper",
            "blockers": [f"read_only_helper_execution_failed_{type(exc).__name__}"],
        }
    payload = _json_mapping(stream.getvalue())
    if payload.get("script_status") in {
        "BLOCKED_MISSING_REQUIRED_CONFIRMATIONS",
        "BLOCKED_BY_MISSING_VAULT_ADAPTER",
        "BLOCKED_BY_MISSING_TOKEN",
        "BLOCKED_BY_MISSING_ACCOUNT_ID",
        "BLOCKED_BY_UNSAFE_CONTEXT",
        "BLOCKED_BY_UNSAFE_ENDPOINT",
        "BLOCKED_BY_MISSING_HTTP_GET_ADAPTER",
    }:
        payload["is_broker_blocked"] = True
        payload["evidence_source"] = "owner_run_read_only_broker_helper"
    return payload


def _json_mapping(raw: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "status_bucket": INVALID_EVIDENCE,
            "evidence_source": "json_parse_failure",
            "blockers": ["evidence_file_must_contain_json_object"],
        }
    return parsed if isinstance(parsed, dict) else {
        "status_bucket": INVALID_EVIDENCE,
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
