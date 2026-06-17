"""Run the protected OANDA practice/demo connection-attempt boundary.

This CLI validates the one-shot protected attempt envelope and emits sanitized
JSON evidence. It does not accept auth values, account identifiers, endpoint
URLs, order routes, market-data requests, or account-state requests.

The actual runtime connector must remain external operator-controlled. If no
external connector is injected by a higher runtime layer, this command fails
closed before any connection attempt.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine import oanda_demo_protected_connection_attempt  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    raw_args = list(sys.argv[1:] if argv is None else argv)
    cli_blockers = oanda_demo_protected_connection_attempt.scan_attempt_cli_args(raw_args)
    if cli_blockers:
        result = oanda_demo_protected_connection_attempt.build_blocked_cli_result(cli_blockers)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2

    parser = argparse.ArgumentParser(
        description="Validate a protected one-shot OANDA practice/demo connection attempt."
    )
    parser.add_argument("--human-owner-protected-demo-connection-approved", action="store_true")
    parser.add_argument("--network-broker-call-approved", action="store_true")
    parser.add_argument("--runtime-handoff-intake-ready", action="store_true")
    parser.add_argument("--runtime-handoff-ready", action="store_true")
    parser.add_argument("--connection-gate-ready", action="store_true")
    parser.add_argument("--runtime-auth-reference-present", action="store_true")
    parser.add_argument("--runtime-auth-reference-format", default="SANITIZED_REFERENCE_ONLY")
    parser.add_argument(
        "--auth-material-location",
        default="EXTERNAL_OPERATOR_CONTROLLED_RUNTIME_ONLY",
    )
    parser.add_argument("--runtime-auth-boundary-confirmed", action="store_true")
    parser.add_argument("--repo-storage-confirmed-absent", action="store_true")
    parser.add_argument("--no-account-id-storage-confirmed", action="store_true")
    parser.add_argument("--no-auth-value-storage-confirmed", action="store_true")
    parser.add_argument("--one-shot-only", action="store_true")
    parser.add_argument("--timeout-seconds", type=int)
    parser.add_argument("--stop-on-success-or-failure", action="store_true")
    parser.add_argument("--no-order-route-confirmed", action="store_true")
    parser.add_argument("--no-account-id-logging-confirmed", action="store_true")
    parser.add_argument("--audit-logging-acknowledged", action="store_true")
    args, unknown = parser.parse_known_args(raw_args)

    if unknown:
        result = oanda_demo_protected_connection_attempt.build_blocked_cli_result(
            ["unknown_cli_argument_rejected"]
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2

    request = {
        "broker_id": "OANDA",
        "account_mode": "PRACTICE_DEMO",
        "environment": "OANDA_PRACTICE_DEMO",
        "endpoint_classification": "OANDA_PRACTICE_DEMO",
        "approval_scope": oanda_demo_protected_connection_attempt.ATTEMPT_SCOPE,
        "connection_attempt_mode": oanda_demo_protected_connection_attempt.ATTEMPT_MODE,
        "human_owner_protected_demo_connection_approved": (
            args.human_owner_protected_demo_connection_approved
        ),
        "network_broker_call_gate_approved": args.network_broker_call_approved,
        "runtime_handoff_intake_ready": args.runtime_handoff_intake_ready,
        "runtime_handoff_ready": args.runtime_handoff_ready,
        "connection_gate_ready": args.connection_gate_ready,
        "runtime_auth_reference_present": args.runtime_auth_reference_present,
        "runtime_auth_reference_format": args.runtime_auth_reference_format,
        "auth_material_location": args.auth_material_location,
        "runtime_auth_boundary_confirmed": args.runtime_auth_boundary_confirmed,
        "repo_storage_confirmed_absent": args.repo_storage_confirmed_absent,
        "account_identifier_present": False,
        "credential_value_present": False,
        "no_account_id_storage_confirmed": args.no_account_id_storage_confirmed,
        "no_auth_value_storage_confirmed": args.no_auth_value_storage_confirmed,
        "one_shot_only": args.one_shot_only,
        "timeout_seconds": args.timeout_seconds,
        "stop_on_success_or_failure": args.stop_on_success_or_failure,
        "no_order_route_confirmed": args.no_order_route_confirmed,
        "no_account_id_logging_confirmed": args.no_account_id_logging_confirmed,
        "audit_logging_acknowledged": args.audit_logging_acknowledged,
    }
    result = oanda_demo_protected_connection_attempt.run_oanda_demo_protected_connection_attempt(
        request
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["outcome"] == "CONNECTED_SANITIZED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
