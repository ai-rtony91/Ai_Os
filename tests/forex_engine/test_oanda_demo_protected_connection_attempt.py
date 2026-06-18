from __future__ import annotations

import json
from pathlib import Path

from automation.forex_engine import oanda_demo_protected_connection_attempt as attempt
from scripts.forex_delivery import run_oanda_demo_protected_connection_attempt


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "oanda_demo_protected_connection_attempt.py"
SCRIPT_PATH = REPO_ROOT / "scripts" / "forex_delivery" / "run_oanda_demo_protected_connection_attempt.py"
DOC_PATH = (
    REPO_ROOT
    / "docs"
    / "trading_lab"
    / "AIOS_FOREX_BUILDER_OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT.md"
)
REPORT_PATH = (
    REPO_ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_V1_REPORT.md"
)


class RecordingConnector:
    def __init__(self, result: dict | None = None, error: Exception | None = None) -> None:
        self.result = result or {"connected": True, "auth_proof": True, "status_code": 200}
        self.error = error
        self.calls: list[tuple[dict, int]] = []

    def attempt_connection(self, request: dict, *, timeout_seconds: int) -> dict:
        self.calls.append((dict(request), timeout_seconds))
        if self.error is not None:
            raise self.error
        return dict(self.result)


def _approved_attempt(**overrides):
    payload = attempt.build_example_oanda_demo_protected_connection_attempt_request()
    payload.update(overrides)
    return payload


def test_protected_connection_attempt_contract_docs_script_and_report_exist() -> None:
    contract_set = attempt.build_oanda_demo_protected_connection_attempt_contract_set()

    assert MODULE_PATH.exists()
    assert SCRIPT_PATH.exists()
    assert DOC_PATH.exists()
    assert REPORT_PATH.exists()
    assert contract_set["contracts_ready_for_protected_demo_connection_attempt"] is True
    assert contract_set["protected_connection_attempt_contract"]["mode"] == (
        "ONE_SHOT_PRACTICE_DEMO_CONNECT_ONLY"
    )
    assert contract_set["runtime_connector_boundary_contract"]["connector_call_limit"] == 1
    assert contract_set["connection_probe_contract"]["future_runtime_connector_required"] is True


def test_missing_human_owner_approval_rejected() -> None:
    connector = RecordingConnector()
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(human_owner_protected_demo_connection_approved=False),
        runtime_connector=connector,
    )

    assert result["status"] == "OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_BLOCKED"
    assert result["classification"] == "FAIL_CLOSED"
    assert "human_owner_protected_demo_connection_approval_required" in result["blockers"]
    assert result["connection_attempt_performed"] is False
    assert connector.calls == []


def test_missing_runtime_auth_reference_rejected() -> None:
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(runtime_auth_reference_present=False),
        runtime_connector=RecordingConnector(),
    )

    assert result["connection_attempt_preflight_passed"] is False
    assert "runtime_auth_reference_required" in result["blockers"]
    assert result["connection_attempt_performed"] is False
    assert result["credential_material_present"] is False


def test_missing_connector_fails_closed() -> None:
    result = attempt.run_oanda_demo_protected_connection_attempt(_approved_attempt())

    assert result["outcome"] == "RUNTIME_CONNECTOR_MISSING_SANITIZED"
    assert "external_runtime_connector_required" in result["blockers"]
    assert result["connection_attempt_performed"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False


def test_non_callable_connector_fails_closed() -> None:
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(),
        runtime_connector={"connector_label": "OANDA_PRACTICE_DEMO"},
    )

    assert result["outcome"] == "RUNTIME_CONNECTOR_HANDLE_REJECTED_SANITIZED"
    assert "runtime_connector_not_callable" in result["blockers"]
    assert result["connection_attempt_performed"] is False
    assert result["attempt_count"] == 0


def test_sensitive_connector_handle_payload_fails_closed_without_echoing_values() -> None:
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(),
        runtime_connector={
            "connector_label": "OANDA_PRACTICE_DEMO",
            "access_token": "SHOULD_NOT_PERSIST",
            "endpoint_url": "SHOULD_NOT_PERSIST",
        },
    )
    serialized = json.dumps(result)

    assert result["outcome"] == "RUNTIME_CONNECTOR_HANDLE_REJECTED_SANITIZED"
    assert "runtime_connector_not_callable" in result["blockers"]
    assert "runtime_connector_handle_forbidden_field:access_token" in result["blockers"]
    assert "runtime_connector_handle_forbidden_field:endpoint_url" in result["blockers"]
    assert "SHOULD_NOT_PERSIST" not in serialized
    assert result["connection_attempt_performed"] is False
    assert result["contains_real_credentials"] is False
    assert result["contains_account_identifier"] is False


def test_credential_like_input_rejected_without_persistence() -> None:
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(runtime_auth_value="Bearer NOT_A_REAL_VALUE"),
        runtime_connector=RecordingConnector(),
    )
    serialized = json.dumps(result)

    assert result["connection_attempt_preflight_passed"] is False
    assert "forbidden_field:runtime_auth_value" in result["blockers"]
    assert "credential_like_value:runtime_auth_value" in result["blockers"]
    assert "NOT_A_REAL_VALUE" not in serialized
    assert result["contains_real_credentials"] is False


def test_account_id_input_rejected_without_persistence() -> None:
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(account_identifier_present=True, account_id="DO_NOT_STORE"),
        runtime_connector=RecordingConnector(),
    )
    serialized = json.dumps(result)

    assert result["connection_attempt_preflight_passed"] is False
    assert "account_identifier_not_allowed" in result["blockers"]
    assert "forbidden_field:account_id" in result["blockers"]
    assert "DO_NOT_STORE" not in serialized
    assert result["contains_account_identifier"] is False


def test_live_endpoint_rejected() -> None:
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(endpoint_classification="OANDA_LIVE"),
        runtime_connector=RecordingConnector(),
    )

    assert result["connection_attempt_preflight_passed"] is False
    assert "unsupported_endpoint_classification" in result["blockers"]
    assert "live_endpoint_blocked" in result["blockers"]
    assert result["live_endpoint_used"] is False
    assert result["live_execution_allowed"] is False


def test_order_route_rejected() -> None:
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(order_route_requested=True),
        runtime_connector=RecordingConnector(),
    )

    assert result["connection_attempt_preflight_passed"] is False
    assert "order_route_attempt_blocked" in result["blockers"]
    assert "unauthorized_connection_attempt" in result["blockers"]
    assert result["order_route_allowed"] is False
    assert result["order_placed"] is False


def test_account_state_request_rejected() -> None:
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(account_state_requested=True),
        runtime_connector=RecordingConnector(),
    )

    assert result["connection_attempt_preflight_passed"] is False
    assert "account_state_request_blocked" in result["blockers"]
    assert "unauthorized_execution_field:account_state_requested" in result["blockers"]
    assert result["account_access_allowed"] is False


def test_market_data_request_rejected() -> None:
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(market_data_requested=True),
        runtime_connector=RecordingConnector(),
    )

    assert result["connection_attempt_preflight_passed"] is False
    assert "market_data_request_blocked" in result["blockers"]
    assert "unauthorized_execution_field:market_data_requested" in result["blockers"]
    assert result["market_data_allowed"] is False


def test_retry_loop_rejected() -> None:
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(retry_loop_requested=True, max_attempts=2),
        runtime_connector=RecordingConnector(),
    )

    assert result["connection_attempt_preflight_passed"] is False
    assert "retry_loop_blocked" in result["blockers"]
    assert "max_attempts_must_equal_one" in result["blockers"]
    assert result["attempt_count"] == 0
    assert result["retry_loop_used"] is False


def test_timeout_required() -> None:
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(timeout_seconds=None),
        runtime_connector=RecordingConnector(),
    )

    assert result["connection_attempt_preflight_passed"] is False
    assert "timeout_seconds_required" in result["blockers"]
    assert result["network_used"] is False


def test_sanitized_success_evidence() -> None:
    connector = RecordingConnector({"connected": True, "auth_proof": True, "status_code": 200})
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(),
        runtime_connector=connector,
    )
    serialized = json.dumps(result)
    connector_request = connector.calls[0][0]

    assert result["status"] == "OANDA_DEMO_PROTECTED_CONNECTION_CONNECTED_SANITIZED"
    assert result["outcome"] == "CONNECTED_SANITIZED"
    assert result["connection_attempt_preflight_passed"] is True
    assert result["connection_attempt_performed"] is True
    assert result["attempt_count"] == 1
    assert result["stop_after_result"] is True
    assert result["live_endpoint_used"] is False
    assert result["contains_real_credentials"] is False
    assert result["contains_account_identifier"] is False
    assert result["raw_broker_payload_persisted"] is False
    assert "raw_response" not in serialized
    assert "account_id" not in connector_request
    assert "endpoint_url" not in connector_request
    assert "runtime_auth_value" not in connector_request


def test_sanitized_failure_evidence() -> None:
    connector = RecordingConnector({"connected": False, "auth_rejected": True, "status_code": 401})
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(),
        runtime_connector=connector,
    )

    assert result["status"] == "OANDA_DEMO_PROTECTED_CONNECTION_FAILED_SANITIZED"
    assert result["outcome"] == "AUTH_REJECTED_SANITIZED"
    assert "auth_rejected_sanitized" in result["blockers"]
    assert result["status_family"] == "401"
    assert result["broker_payloads_recorded"] is False
    assert result["account_identifiers_recorded"] is False


def test_no_credential_persistence_from_connector_result() -> None:
    connector = RecordingConnector(
        {"connected": True, "auth_proof": True, "access_token": "SHOULD_NOT_PERSIST"}
    )
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(),
        runtime_connector=connector,
    )
    serialized = json.dumps(result)

    assert result["outcome"] == "RUNTIME_CONNECTOR_HANDLE_REJECTED_SANITIZED"
    assert "runtime_connector_handle_forbidden_field:result.access_token" in result["blockers"]
    assert "SHOULD_NOT_PERSIST" not in serialized
    assert connector.calls == []
    assert result["connection_attempt_performed"] is False
    assert result["contains_real_credentials"] is False


def test_no_account_id_persistence_from_connector_result() -> None:
    connector = RecordingConnector(
        {"connected": True, "auth_proof": True, "account_id": "ACCOUNT_SHOULD_NOT_PERSIST"}
    )
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(),
        runtime_connector=connector,
    )
    serialized = json.dumps(result)

    assert result["outcome"] == "RUNTIME_CONNECTOR_HANDLE_REJECTED_SANITIZED"
    assert "runtime_connector_handle_forbidden_field:result.account_id" in result["blockers"]
    assert "ACCOUNT_SHOULD_NOT_PERSIST" not in serialized
    assert connector.calls == []
    assert result["connection_attempt_performed"] is False
    assert result["contains_account_identifier"] is False


def test_no_raw_broker_payload_persistence_from_connector_result() -> None:
    connector = RecordingConnector(
        {"connected": True, "auth_proof": True, "raw_response": "FULL_RAW_BODY"}
    )
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(),
        runtime_connector=connector,
    )
    serialized = json.dumps(result)

    assert result["outcome"] == "RUNTIME_CONNECTOR_HANDLE_REJECTED_SANITIZED"
    assert "runtime_connector_handle_forbidden_field:result.raw_response" in result["blockers"]
    assert "FULL_RAW_BODY" not in serialized
    assert connector.calls == []
    assert result["connection_attempt_performed"] is False
    assert result["raw_broker_payload_persisted"] is False


def test_live_endpoint_indicator_on_connector_handle_fails_closed() -> None:
    connector = RecordingConnector()
    connector.live_endpoint_requested = True

    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(),
        runtime_connector=connector,
    )

    assert result["outcome"] == "RUNTIME_CONNECTOR_HANDLE_REJECTED_SANITIZED"
    assert "runtime_connector_handle_unsafe_true_field:live_endpoint_requested" in result["blockers"]
    assert connector.calls == []
    assert result["live_endpoint_used"] is False


def test_one_shot_stop_behavior() -> None:
    connector = RecordingConnector({"connected": True, "auth_proof": True, "status_code": 200})
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(),
        runtime_connector=connector,
    )

    assert len(connector.calls) == 1
    assert result["attempt_count"] == 1
    assert result["retry_loop_used"] is False
    assert result["final_state"] == "STOPPED_AFTER_RESULT"


def test_timeout_result_is_sanitized_and_stops() -> None:
    result = attempt.run_oanda_demo_protected_connection_attempt(
        _approved_attempt(),
        runtime_connector=RecordingConnector(error=TimeoutError("raw timeout detail")),
    )
    serialized = json.dumps(result)

    assert result["outcome"] == "TIMEOUT_SANITIZED"
    assert "connection_attempt_timeout" in result["blockers"]
    assert "raw timeout detail" not in serialized
    assert result["attempt_count"] == 1
    assert result["final_state"] == "STOPPED_AFTER_RESULT"


def test_cli_blocks_sensitive_args_without_echoing_values(capsys) -> None:
    exit_code = run_oanda_demo_protected_connection_attempt.main(
        ["--account-id", "DO_NOT_STORE"]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["status"] == "OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_BLOCKED"
    assert "cli_sensitive_or_forbidden_argument_rejected" in payload["blockers"]
    assert "DO_NOT_STORE" not in json.dumps(payload)
    assert payload["connection_attempt_performed"] is False
    assert payload["contains_account_identifier"] is False


def test_cli_approved_envelope_fails_closed_without_external_connector(capsys) -> None:
    exit_code = run_oanda_demo_protected_connection_attempt.main(
        [
            "--human-owner-protected-demo-connection-approved",
            "--network-broker-call-approved",
            "--runtime-handoff-intake-ready",
            "--runtime-handoff-ready",
            "--connection-gate-ready",
            "--runtime-auth-reference-present",
            "--runtime-auth-boundary-confirmed",
            "--repo-storage-confirmed-absent",
            "--no-account-id-storage-confirmed",
            "--no-auth-value-storage-confirmed",
            "--one-shot-only",
            "--timeout-seconds",
            "10",
            "--stop-on-success-or-failure",
            "--no-order-route-confirmed",
            "--no-account-id-logging-confirmed",
            "--audit-logging-acknowledged",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["connection_attempt_preflight_passed"] is True
    assert payload["outcome"] == "RUNTIME_CONNECTOR_MISSING_SANITIZED"
    assert "external_runtime_connector_required" in payload["blockers"]
    assert payload["connection_attempt_performed"] is False
    assert payload["broker_request_sent"] is False
    assert payload["network_used"] is False
    assert payload["order_placed"] is False


def test_module_and_script_do_not_read_env_write_files_or_import_broker_sdk() -> None:
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
