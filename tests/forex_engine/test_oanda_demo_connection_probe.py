from __future__ import annotations

import json
from pathlib import Path

from automation.forex_engine import oanda_demo_connection_probe
from scripts.forex_delivery import run_oanda_demo_connection_probe


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "oanda_demo_connection_probe.py"
SCRIPT_PATH = REPO_ROOT / "scripts" / "forex_delivery" / "run_oanda_demo_connection_probe.py"
DOC_PATH = (
    REPO_ROOT
    / "docs"
    / "trading_lab"
    / "AIOS_FOREX_BUILDER_OANDA_DEMO_CONNECTION_PROBE.md"
)
REPORT_PATH = (
    REPO_ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_OANDA_DEMO_CONNECTION_FIRST_PROBE_V1_REPORT.md"
)


def _approved_probe(**overrides):
    payload = oanda_demo_connection_probe.build_example_oanda_demo_connection_probe_request()
    payload.update(overrides)
    return payload


def test_probe_contract_docs_script_and_report_exist() -> None:
    contract = oanda_demo_connection_probe.build_oanda_demo_connection_probe_contract()

    assert MODULE_PATH.exists()
    assert SCRIPT_PATH.exists()
    assert DOC_PATH.exists()
    assert REPORT_PATH.exists()
    assert contract["schema"] == "AIOS_OANDA_DEMO_CONNECTION_PROBE_CONTRACT.v1"
    assert contract["mode"] == "PROBE_VALIDATE_ONLY"
    assert contract["probe_command_validate_only"] is True
    assert contract["future_runtime_connector_required"] is True
    assert contract["runtime_handoff_intake_required"] is True
    assert contract["runtime_handoff_contract_set"][
        "contracts_ready_for_future_runtime_handoff"
    ] is True
    assert contract["runtime_handoff_contract_set"]["runtime_handoff_intake_contract_set"][
        "contracts_ready_for_future_runtime_handoff_intake"
    ] is True


def test_no_approval_blocks_probe() -> None:
    result = oanda_demo_connection_probe.evaluate_oanda_demo_connection_probe()

    assert result["status"] == "OANDA_DEMO_CONNECTION_PROBE_BLOCKED"
    assert result["classification"] == "FAIL_CLOSED"
    assert result["probe_ready"] is False
    assert "demo_probe_approval_flag_required" in result["blockers"]
    assert "network_broker_call_gate_approval_required" in result["blockers"]
    assert result["connection_attempt_allowed_now"] is False
    assert result["connection_attempt_performed"] is False


def test_live_endpoint_blocks_probe() -> None:
    result = oanda_demo_connection_probe.evaluate_oanda_demo_connection_probe(
        _approved_probe(endpoint_classification="OANDA_LIVE")
    )

    assert result["probe_ready"] is False
    assert "unsupported_endpoint_classification" in result["blockers"]
    assert "live_endpoint_blocked" in result["blockers"]
    assert result["live_endpoint_allowed"] is False
    assert result["live_execution_allowed"] is False


def test_account_id_blocks_probe() -> None:
    result = oanda_demo_connection_probe.evaluate_oanda_demo_connection_probe(
        _approved_probe(account_identifier_present=True, account_id="DO_NOT_STORE")
    )

    assert result["probe_ready"] is False
    assert "account_identifier_not_allowed" in result["blockers"]
    assert "forbidden_field:account_id" in result["blockers"]
    assert result["audit_event"]["contains_account_identifier"] is False
    assert result["account_access_allowed"] is False


def test_credential_like_value_blocks_probe() -> None:
    result = oanda_demo_connection_probe.evaluate_oanda_demo_connection_probe(
        _approved_probe(runtime_auth_value="Bearer NOT_A_REAL_VALUE")
    )

    assert result["probe_ready"] is False
    assert "forbidden_field:runtime_auth_value" in result["blockers"]
    assert "credential_like_value:runtime_auth_value" in result["blockers"]
    assert result["audit_event"]["contains_real_credentials"] is False
    assert result["credentials_used"] is False


def test_order_route_attempt_blocks_probe() -> None:
    result = oanda_demo_connection_probe.evaluate_oanda_demo_connection_probe(
        _approved_probe(order_route_attempted=True)
    )

    assert result["probe_ready"] is False
    assert "order_route_attempt_blocked" in result["blockers"]
    assert "unauthorized_execution_attempt" in result["blockers"]
    assert result["order_route_allowed"] is False
    assert result["order_placed"] is False


def test_missing_runtime_auth_reference_blocks_probe() -> None:
    result = oanda_demo_connection_probe.evaluate_oanda_demo_connection_probe(
        _approved_probe(runtime_auth_reference_present=False)
    )

    assert result["probe_ready"] is False
    assert "runtime_auth_reference_required" in result["blockers"]
    assert result["credential_material_present"] is False
    assert result["connection_attempt_allowed_now"] is False


def test_timeout_exists_and_is_bounded() -> None:
    result = oanda_demo_connection_probe.evaluate_oanda_demo_connection_probe(
        _approved_probe(timeout_seconds=120)
    )
    contract = oanda_demo_connection_probe.build_oanda_demo_connection_probe_contract()

    assert contract["timeout_min_seconds"] == 1
    assert contract["timeout_max_seconds"] == 30
    assert "timeout_seconds_out_of_bounds" in result["blockers"]
    assert result["network_used"] is False


def test_evidence_is_sanitized() -> None:
    result = oanda_demo_connection_probe.evaluate_oanda_demo_connection_probe(_approved_probe())
    audit_event = result["audit_event"]
    evidence_schema = result["evidence_schema"]

    assert result["status"] == "OANDA_DEMO_CONNECTION_PROBE_READY"
    assert result["outcome"] == "PROBE_VALIDATED_NO_CONNECTION"
    assert result["runtime_handoff"]["status"] == "OANDA_DEMO_RUNTIME_HANDOFF_READY"
    assert result["runtime_handoff_ready"] is True
    assert result["runtime_handoff_intake_ready"] is True
    assert result["runtime_handoff"]["runtime_handoff_intake"]["metadata_accepted"] is True
    assert evidence_schema["contains_real_credentials"] is False
    assert evidence_schema["contains_account_identifier"] is False
    assert audit_event["sanitized"] is True
    assert audit_event["credential_values_recorded"] is False
    assert audit_event["account_identifiers_recorded"] is False
    assert audit_event["broker_payloads_recorded"] is False


def test_one_shot_stop_behavior_exists() -> None:
    result = oanda_demo_connection_probe.evaluate_oanda_demo_connection_probe(_approved_probe())

    assert result["one_shot_only"] is True
    assert result["stop_after_result"] is True
    assert result["probe_final_state"] == "STOPPED_AFTER_VALIDATION"
    assert result["connection_attempt_allowed_now"] is False
    assert result["connection_attempt_performed"] is False


def test_probe_blocks_when_runtime_handoff_boundary_fails() -> None:
    result = oanda_demo_connection_probe.evaluate_oanda_demo_connection_probe(
        _approved_probe(runtime_auth_boundary_confirmed=False)
    )

    assert result["probe_ready"] is False
    assert "runtime_handoff_required" in result["blockers"]
    assert (
        "runtime_handoff_blocker:runtime_boundary_confirmation_required"
        in result["blockers"]
    )
    assert result["runtime_handoff_ready"] is False
    assert result["connection_attempt_allowed_now"] is False


def test_probe_blocks_when_runtime_handoff_intake_fails() -> None:
    result = oanda_demo_connection_probe.evaluate_oanda_demo_connection_probe(
        _approved_probe(metadata_intake_authorized=False)
    )

    assert result["probe_ready"] is False
    assert "runtime_handoff_required" in result["blockers"]
    assert (
        "runtime_handoff_blocker:runtime_handoff_intake_required"
        in result["blockers"]
    )
    assert (
        "runtime_handoff_blocker:runtime_handoff_intake_blocker:metadata_intake_authorization_required"
        in result["blockers"]
    )
    assert result["runtime_handoff_intake_ready"] is False
    assert result["connection_attempt_allowed_now"] is False


def test_probe_cli_blocks_sensitive_args_without_echoing_values(capsys) -> None:
    exit_code = run_oanda_demo_connection_probe.main(["--account-id", "DO_NOT_STORE"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["status"] == "OANDA_DEMO_CONNECTION_PROBE_BLOCKED"
    assert "cli_sensitive_argument_rejected" in payload["blockers"]
    assert "DO_NOT_STORE" not in json.dumps(payload)
    assert payload["contains_account_identifier"] is False
    assert payload["connection_attempt_performed"] is False


def test_probe_cli_approved_path_validates_without_connection(capsys) -> None:
    exit_code = run_oanda_demo_connection_probe.main(
        [
            "--demo-probe-approved",
            "--network-broker-call-approved",
            "--runtime-auth-reference-present",
            "--runtime-auth-boundary-confirmed",
            "--repo-storage-confirmed-absent",
            "--one-shot-only",
            "--stop-on-success-or-failure",
            "--no-order-route-confirmed",
            "--no-account-id-logging-confirmed",
            "--audit-logging-acknowledged",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "OANDA_DEMO_CONNECTION_PROBE_READY"
    assert payload["probe_ready"] is True
    assert payload["connection_attempt_allowed_now"] is False
    assert payload["connection_attempt_performed"] is False
    assert payload["broker_request_sent"] is False
    assert payload["network_used"] is False
    assert payload["order_placed"] is False


def test_module_and_script_have_no_oanda_sdk_network_env_or_file_write_behavior() -> None:
    for path in (MODULE_PATH, SCRIPT_PATH):
        source = path.read_text(encoding="utf-8").lower()
        import_lines = "\n".join(
            line.strip()
            for line in source.splitlines()
            if line.startswith("import ") or line.startswith("from ")
        )

        for forbidden_import in ("requests", "socket", "urllib", "subprocess", "dotenv", "mt5", "ibkr"):
            assert forbidden_import not in import_lines
        for line in import_lines.splitlines():
            assert not line.startswith("import broker")
            assert not line.startswith("from broker")
            assert not line.startswith("import oanda")
            assert not line.startswith("from oanda")
        for forbidden_call in (
            "os.environ",
            "getenv",
            "open(",
            "write_text(",
            "write_bytes(",
            "start-process",
            "schedule.every",
            "daemon.daemoncontext",
        ):
            assert forbidden_call not in source
