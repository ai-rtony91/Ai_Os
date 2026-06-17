"""Validate the guarded OANDA practice/demo connection probe path.

This command is validation-only in this packet. It rejects auth values, account
identifiers, live labels, order routing, and unsafe CLI arguments before building
sanitized in-memory probe evidence. It does not connect to OANDA.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine import oanda_demo_connection_probe  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    raw_args = list(sys.argv[1:] if argv is None else argv)
    cli_blockers = oanda_demo_connection_probe.scan_probe_cli_args(raw_args)
    if cli_blockers:
        print(json.dumps(oanda_demo_connection_probe.build_blocked_cli_result(cli_blockers), indent=2, sort_keys=True))
        return 2

    parser = argparse.ArgumentParser(description="Validate OANDA demo connection probe readiness.")
    parser.add_argument("--account-mode", default="PRACTICE_DEMO")
    parser.add_argument("--environment", default="OANDA_PRACTICE_DEMO")
    parser.add_argument("--endpoint-classification", default="OANDA_PRACTICE_DEMO")
    parser.add_argument("--demo-probe-approved", action="store_true")
    parser.add_argument("--network-broker-call-approved", action="store_true")
    parser.add_argument("--runtime-auth-reference-present", action="store_true")
    parser.add_argument("--runtime-auth-reference-format", default="SANITIZED_REFERENCE_ONLY")
    parser.add_argument(
        "--auth-material-location",
        default="EXTERNAL_OPERATOR_CONTROLLED_RUNTIME_ONLY",
    )
    parser.add_argument("--runtime-auth-boundary-confirmed", action="store_true")
    parser.add_argument("--repo-storage-confirmed-absent", action="store_true")
    parser.add_argument("--one-shot-only", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=10)
    parser.add_argument("--stop-on-success-or-failure", action="store_true")
    parser.add_argument("--no-order-route-confirmed", action="store_true")
    parser.add_argument("--no-account-id-logging-confirmed", action="store_true")
    parser.add_argument("--audit-logging-acknowledged", action="store_true")
    args, unknown = parser.parse_known_args(raw_args)

    if unknown:
        result = oanda_demo_connection_probe.build_blocked_cli_result(
            ["unknown_cli_argument_rejected"]
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2

    request = {
        "broker_id": "OANDA",
        "account_mode": args.account_mode,
        "environment": args.environment,
        "endpoint_classification": args.endpoint_classification,
        "probe_scope": oanda_demo_connection_probe.PROBE_SCOPE,
        "probe_mode": oanda_demo_connection_probe.PROBE_MODE,
        "demo_probe_approval_flag": args.demo_probe_approved,
        "network_broker_call_gate_approved": args.network_broker_call_approved,
        "runtime_auth_reference_present": args.runtime_auth_reference_present,
        "runtime_auth_reference_format": args.runtime_auth_reference_format,
        "auth_material_location": args.auth_material_location,
        "runtime_auth_boundary_confirmed": args.runtime_auth_boundary_confirmed,
        "repo_storage_confirmed_absent": args.repo_storage_confirmed_absent,
        "account_identifier_present": False,
        "one_shot_only": args.one_shot_only,
        "timeout_seconds": args.timeout_seconds,
        "stop_on_success_or_failure": args.stop_on_success_or_failure,
        "no_order_route_confirmed": args.no_order_route_confirmed,
        "no_account_id_logging_confirmed": args.no_account_id_logging_confirmed,
        "audit_logging_acknowledged": args.audit_logging_acknowledged,
    }
    result = oanda_demo_connection_probe.evaluate_oanda_demo_connection_probe(request)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["probe_ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
