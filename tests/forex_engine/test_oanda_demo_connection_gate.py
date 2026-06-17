from __future__ import annotations

from pathlib import Path

from automation.forex_engine import oanda_demo_connection_gate


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "oanda_demo_connection_gate.py"
DOC_PATH = (
    REPO_ROOT
    / "docs"
    / "trading_lab"
    / "AIOS_FOREX_BUILDER_OANDA_DEMO_CONNECTION_GATE.md"
)
REPORT_PATH = (
    REPO_ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_OANDA_DEMO_CONNECTION_GATE_SPEC_V1_REPORT.md"
)


def _approved_gate(**overrides):
    payload = oanda_demo_connection_gate.build_example_oanda_demo_connection_gate_approval()
    payload.update(overrides)
    return payload


def test_connection_gate_contract_and_docs_exist() -> None:
    contract_set = oanda_demo_connection_gate.build_oanda_demo_connection_gate_contract_set()

    assert MODULE_PATH.exists()
    assert DOC_PATH.exists()
    assert REPORT_PATH.exists()
    assert contract_set["contracts_ready_for_future_connection_packet_review"] is True
    assert contract_set["connection_gate_contract"]["mode"] == "CONNECTION_READINESS_ONLY"
    assert contract_set["connection_gate_contract"]["connection_readiness_only"] is True


def test_contract_blocks_broker_network_credentials_orders_and_live() -> None:
    contract = oanda_demo_connection_gate.build_oanda_demo_connection_gate_contract()

    for field in (
        "broker_connection_allowed",
        "connection_attempt_allowed",
        "connection_attempt_allowed_now",
        "connection_attempt_performed",
        "broker_sdk_allowed",
        "network_allowed",
        "network_api_allowed",
        "credentials_allowed",
        "broker_request_allowed",
        "broker_request_sent",
        "account_access_allowed",
        "order_route_allowed",
        "would_place_order",
        "order_placed",
        "live_endpoint_allowed",
        "live_orders_allowed",
        "live_execution_allowed",
        "network_used",
    ):
        assert contract[field] is False


def test_no_approval_blocks_connection_readiness() -> None:
    result = oanda_demo_connection_gate.evaluate_oanda_demo_connection_gate()

    assert result["status"] == "OANDA_DEMO_CONNECTION_GATE_BLOCKED"
    assert result["classification"] == "FAIL_CLOSED"
    assert result["connection_readiness_gate_ready"] is False
    assert result["future_connection_packet_ready_for_human_review"] is False
    assert "human_owner_connection_gate_approval_required" in result["blockers"]
    assert "network_broker_call_gate_approval_required" in result["blockers"]
    assert result["connection_attempt_allowed_now"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False


def test_missing_runtime_auth_proof_blocks_connection_readiness() -> None:
    result = oanda_demo_connection_gate.evaluate_oanda_demo_connection_gate(
        _approved_gate(runtime_auth_proof_present=False)
    )

    assert result["connection_readiness_gate_ready"] is False
    assert "runtime_auth_proof_required" in result["blockers"]
    assert result["credential_material_present"] is False
    assert result["connection_attempt_allowed_now"] is False


def test_account_id_presence_blocks_connection_readiness() -> None:
    result = oanda_demo_connection_gate.evaluate_oanda_demo_connection_gate(
        _approved_gate(account_identifier_present=True, account_id="DO_NOT_STORE")
    )

    assert result["connection_readiness_gate_ready"] is False
    assert "account_identifier_not_allowed" in result["blockers"]
    assert "forbidden_field:account_id" in result["blockers"]
    assert result["audit_event"]["contains_account_identifier"] is False
    assert result["broker_request_sent"] is False


def test_credential_like_values_block_connection_readiness() -> None:
    result = oanda_demo_connection_gate.evaluate_oanda_demo_connection_gate(
        _approved_gate(runtime_auth_proof="Bearer NOT_A_REAL_VALUE")
    )

    assert result["connection_readiness_gate_ready"] is False
    assert "credential_like_value_detected" in result["blockers"]
    assert "credential_like_value:runtime_auth_proof" in result["blockers"]
    assert result["audit_event"]["contains_real_credentials"] is False
    assert result["credentials_used"] is False


def test_live_endpoint_blocks_connection_readiness() -> None:
    result = oanda_demo_connection_gate.evaluate_oanda_demo_connection_gate(
        _approved_gate(endpoint_classification="OANDA_LIVE")
    )

    assert result["connection_readiness_gate_ready"] is False
    assert "unsupported_endpoint_classification" in result["blockers"]
    assert "live_endpoint_blocked" in result["blockers"]
    assert result["live_endpoint_allowed"] is False
    assert result["live_execution_allowed"] is False


def test_order_route_attempt_blocks_connection_readiness() -> None:
    result = oanda_demo_connection_gate.evaluate_oanda_demo_connection_gate(
        _approved_gate(order_route_requested=True)
    )

    assert result["connection_readiness_gate_ready"] is False
    assert "order_route_attempt_blocked" in result["blockers"]
    assert "unauthorized_execution_attempt" in result["blockers"]
    assert "unauthorized_execution_field:order_route_requested" in result["blockers"]
    assert result["order_route_allowed"] is False
    assert result["order_placed"] is False


def test_approved_gate_permits_connection_readiness_only() -> None:
    result = oanda_demo_connection_gate.evaluate_oanda_demo_connection_gate(_approved_gate())
    summary = oanda_demo_connection_gate.summarize_oanda_demo_connection_gate(result)

    assert result["status"] == "OANDA_DEMO_CONNECTION_GATE_READY"
    assert result["classification"] == "OANDA_DEMO_CONNECTION_GATE_READY"
    assert result["connection_readiness_gate_ready"] is True
    assert result["connection_readiness_only"] is True
    assert result["future_connection_packet_ready_for_human_review"] is True
    assert summary["connection_readiness_gate_ready"] is True
    assert result["connection_attempt_allowed_now"] is False
    assert result["connection_attempt_performed"] is False
    assert result["broker_connection_allowed"] is False
    assert result["network_api_allowed"] is False
    assert result["broker_request_sent"] is False
    assert result["order_placed"] is False
    assert result["live_execution_allowed"] is False


def test_sanitized_connection_evidence_schema_and_audit_event() -> None:
    result = oanda_demo_connection_gate.evaluate_oanda_demo_connection_gate(_approved_gate())
    evidence_schema = result["evidence_schema"]
    audit_event = result["audit_event"]

    assert evidence_schema["schema"] == "AIOS_OANDA_DEMO_CONNECTION_SANITIZED_EVIDENCE_SCHEMA.v1"
    assert evidence_schema["sanitized"] is True
    assert evidence_schema["contains_real_credentials"] is False
    assert evidence_schema["contains_account_identifier"] is False
    assert audit_event["schema"] == "AIOS_OANDA_DEMO_CONNECTION_GATE_AUDIT_EVENT.v1"
    assert audit_event["event"] == "oanda_demo_connection_gate_evaluated"
    assert audit_event["sanitized"] is True
    assert audit_event["credential_values_recorded"] is False
    assert audit_event["account_identifiers_recorded"] is False
    assert audit_event["broker_payloads_recorded"] is False


def test_timeout_and_stop_controls_fail_closed() -> None:
    result = oanda_demo_connection_gate.evaluate_oanda_demo_connection_gate(
        _approved_gate(timeout_seconds=120, stop_on_success_or_failure=False, one_shot_only=False)
    )

    assert result["connection_readiness_gate_ready"] is False
    assert "timeout_seconds_out_of_bounds" in result["blockers"]
    assert "stop_on_success_or_failure_required" in result["blockers"]
    assert "one_shot_only_required" in result["blockers"]
    assert result["network_used"] is False


def test_module_has_no_oanda_sdk_network_env_or_file_write_behavior() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
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
