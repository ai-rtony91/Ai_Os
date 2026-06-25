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

from automation.forex_engine.oanda_demo_trade_320_owner_run_read_only_refresh_gate_v1 import (  # noqa: E402
    BROKER_EVIDENCE_BLOCKED,
    INVALID_GATE_EVIDENCE,
    OWNER_RUN_READ_ONLY_BROKER_REQUESTED,
    PACKET_NAME,
    REPORT_PATH,
    SECRET_RISK_DETECTED,
    evaluate_trade_320_owner_run_read_only_refresh_gate,
    write_trade_320_owner_run_read_only_refresh_gate_report,
)


def main(
    argv: Sequence[str] | None = None,
    *,
    owner_run_helper: object | None = None,
) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    evidence = _load_gate_evidence(args, owner_run_helper=owner_run_helper)
    result = evaluate_trade_320_owner_run_read_only_refresh_gate(evidence)
    report_path = None
    if args.write_report:
        report_path = write_trade_320_owner_run_read_only_refresh_gate_report(
            result,
            args.report_path,
            branch=_current_branch(),
        )

    payload = {
        "script_status": result["gate_status"],
        "packet_name": PACKET_NAME,
        "report_path": str(report_path) if report_path else None,
        "broker_read_allowed_now": result["broker_read_allowed_now"],
        "owner_run_flag_required": result["owner_run_flag_required"],
        "broker_read_mode": result["broker_read_mode"],
        "dashboard_real_broker_telemetry_goal": result[
            "dashboard_real_broker_telemetry_goal"
        ],
        "dashboard_fake_numbers_allowed": result["dashboard_fake_numbers_allowed"],
        "dashboard_mock_numbers_allowed": result["dashboard_mock_numbers_allowed"],
        "broker_data_source_required": result["broker_data_source_required"],
        "bank_data_source_required": result["bank_data_source_required"],
        "withdrawal_allowed_now": result["withdrawal_allowed_now"],
        "transfer_allowed_now": result["transfer_allowed_now"],
        "money_movement_allowed_now": result["money_movement_allowed_now"],
        "profit_reserve_bucket_mode": result["profit_reserve_bucket_mode"],
        "profit_reserve_bucket_money_movement_requires_future_owner_gate": result[
            "profit_reserve_bucket_money_movement_requires_future_owner_gate"
        ],
        "broker_network_call_performed": bool(
            isinstance(evidence, Mapping)
            and evidence.get("broker_network_call_performed") is True
        ),
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
    return 1 if result["gate_status"] in _FAILURE_STATUSES else 0


_FAILURE_STATUSES = {
    BROKER_EVIDENCE_BLOCKED,
    SECRET_RISK_DETECTED,
    INVALID_GATE_EVIDENCE,
}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description=(
            "AIOS OANDA demo trade 320 owner-run read-only broker refresh gate V1."
        ),
    )
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--report-path", default=REPORT_PATH)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--owner-run-read-broker-now",
        action="store_true",
        help=(
            "Owner-only read-only broker refresh gate. This path never places, "
            "closes, or mutates orders."
        ),
    )
    return parser


def _load_gate_evidence(
    args: argparse.Namespace,
    *,
    owner_run_helper: object | None,
) -> dict[str, Any] | None:
    if not args.owner_run_read_broker_now:
        return None
    return _owner_run_read_only_helper_evidence(owner_run_helper=owner_run_helper)


def _owner_run_read_only_helper_evidence(
    *,
    owner_run_helper: object | None,
) -> dict[str, Any]:
    helper = owner_run_helper
    if helper is None:
        try:
            from scripts.forex_delivery.run_oanda_demo_trade_320_read_only_pl_refresh_v1 import (  # noqa: E501
                _owner_run_read_only_monitor_result as helper,
            )
        except Exception as exc:  # pragma: no cover - defensive runtime boundary
            return _blocked_helper_evidence(
                f"read_only_helper_import_failed_{type(exc).__name__}"
            )

    if not callable(helper):
        return _blocked_helper_evidence("read_only_helper_not_callable")

    stream = StringIO()
    try:
        with redirect_stdout(stream):
            helper_result = helper()  # type: ignore[misc]
    except Exception as exc:  # pragma: no cover - defensive runtime boundary
        return _blocked_helper_evidence(
            f"read_only_helper_execution_failed_{type(exc).__name__}"
        )

    if not isinstance(helper_result, Mapping):
        return {
            "owner_run_read_broker_now": True,
            "safe_read_only_helper_available": True,
            "sanitized_evidence_only": False,
            "broker_read_method": "GET",
            "broker_read_mode": OWNER_RUN_READ_ONLY_BROKER_REQUESTED,
            "helper_status": INVALID_GATE_EVIDENCE,
            "blockers": ["read_only_helper_result_must_be_mapping"],
        }

    return _gate_evidence_from_helper_result(helper_result)


def _blocked_helper_evidence(blocker: str) -> dict[str, Any]:
    return {
        "owner_run_read_broker_now": True,
        "safe_read_only_helper_available": False,
        "sanitized_evidence_only": True,
        "broker_read_method": "GET",
        "broker_read_mode": OWNER_RUN_READ_ONLY_BROKER_REQUESTED,
        "helper_status": BROKER_EVIDENCE_BLOCKED,
        "blockers": [_safe_blocker(blocker)],
        "broker_network_call_performed": False,
        "order_placement_performed": False,
        "order_close_performed": False,
        "order_mutation_performed": False,
        "trade_mutation_performed": False,
        "position_mutation_performed": False,
        "live_endpoint_used": False,
        "secrets_written": False,
    }


def _gate_evidence_from_helper_result(helper_result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "owner_run_read_broker_now": True,
        "safe_read_only_helper_available": True,
        "sanitized_evidence_only": True,
        "broker_read_method": "GET",
        "broker_read_mode": OWNER_RUN_READ_ONLY_BROKER_REQUESTED,
        "trade_id": _first_value(helper_result, ("trade_id", "expected_trade_id")),
        "instrument": _first_value(helper_result, ("instrument",)),
        "helper_status": _first_value(
            helper_result,
            (
                "gate_status",
                "broker_evidence_status",
                "result_bucket",
                "status_bucket",
                "script_status",
                "status",
            ),
        ),
        "broker_evidence_status": helper_result.get("broker_evidence_status"),
        "blockers": [_safe_blocker(item) for item in _sequence(helper_result.get("blockers"))],
        "broker_network_call_performed": bool(
            helper_result.get("broker_network_call_performed") is True
            or str(helper_result.get("broker_read_mode", "")).startswith("OWNER_RUN")
        ),
        "order_placement_performed": helper_result.get("order_placement_performed") is True,
        "order_close_performed": helper_result.get("order_close_performed") is True,
        "order_mutation_performed": helper_result.get("order_mutation_performed") is True,
        "trade_mutation_performed": helper_result.get("trade_mutation_performed") is True,
        "position_mutation_performed": helper_result.get("position_mutation_performed") is True,
        "live_endpoint_used": helper_result.get("live_endpoint_used") is True,
        "secrets_written": helper_result.get("secrets_written") is True,
    }


def _first_value(source: Mapping[str, Any], keys: Sequence[str]) -> Any:
    for key in keys:
        if source.get(key) is not None:
            return source.get(key)
    result = source.get("result")
    if isinstance(result, Mapping):
        for key in keys:
            if result.get(key) is not None:
                return result.get(key)
    return None


def _sequence(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return list(value)
    if value:
        return [value]
    return []


def _safe_blocker(value: Any) -> str:
    text = str(value).strip().lower()
    cleaned = "".join(char if char.isalnum() else "_" for char in text)
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_")[:100] or "unknown_read_only_helper_blocker"


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
