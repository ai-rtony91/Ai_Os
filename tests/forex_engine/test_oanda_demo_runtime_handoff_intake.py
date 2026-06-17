from __future__ import annotations

from pathlib import Path

from automation.forex_engine import oanda_demo_runtime_handoff_intake


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    REPO_ROOT
    / "automation"
    / "forex_engine"
    / "oanda_demo_runtime_handoff_intake.py"
)
DOC_PATH = (
    REPO_ROOT
    / "docs"
    / "trading_lab"
    / "AIOS_FOREX_BUILDER_OANDA_DEMO_RUNTIME_HANDOFF_INTAKE.md"
)
REPORT_PATH = (
    REPO_ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_OANDA_DEMO_RUNTIME_HANDOFF_INTAKE_V1_REPORT.md"
)


def _approved_intake(**overrides):
    payload = oanda_demo_runtime_handoff_intake.build_example_oanda_demo_runtime_handoff_intake()
    payload.update(overrides)
    return payload


def test_runtime_handoff_intake_contract_docs_and_report_exist() -> None:
    contract_set = (
        oanda_demo_runtime_handoff_intake.build_oanda_demo_runtime_handoff_intake_contract_set()
    )

    assert MODULE_PATH.exists()
    assert DOC_PATH.exists()
    assert REPORT_PATH.exists()
    assert contract_set["contracts_ready_for_future_runtime_handoff_intake"] is True
    assert contract_set["runtime_handoff_intake_contract"]["mode"] == "INTAKE_VALIDATE_ONLY"
    assert contract_set["metadata_acceptance_rules"]["accepted_auth_value"] is False
    assert contract_set["metadata_rejection_rules"]["reject_live_endpoint_references"] is True


def test_valid_intake_accepted() -> None:
    result = oanda_demo_runtime_handoff_intake.evaluate_oanda_demo_runtime_handoff_intake(
        _approved_intake()
    )

    assert result["status"] == "OANDA_DEMO_RUNTIME_HANDOFF_INTAKE_READY"
    assert result["classification"] == "OANDA_DEMO_RUNTIME_HANDOFF_INTAKE_READY"
    assert result["runtime_handoff_intake_ready"] is True
    assert result["metadata_accepted"] is True
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False


def test_malformed_intake_rejected() -> None:
    result = oanda_demo_runtime_handoff_intake.evaluate_oanda_demo_runtime_handoff_intake(
        _approved_intake(
            runtime_reference_format="RAW_REFERENCE",
            auth_material_location="REPO_FILE",
        )
    )

    assert result["runtime_handoff_intake_ready"] is False
    assert "malformed_runtime_reference" in result["blockers"]
    assert "malformed_auth_material_location" in result["blockers"]
    assert result["credential_material_present"] is False


def test_account_id_rejected() -> None:
    result = oanda_demo_runtime_handoff_intake.evaluate_oanda_demo_runtime_handoff_intake(
        _approved_intake(account_identifier_present=True, account_id="DO_NOT_STORE")
    )

    assert result["runtime_handoff_intake_ready"] is False
    assert "account_identifier_not_allowed" in result["blockers"]
    assert "forbidden_field:account_id" in result["blockers"]
    assert result["audit_event"]["contains_account_identifier"] is False
    assert result["account_access_allowed"] is False


def test_credential_like_value_rejected() -> None:
    result = oanda_demo_runtime_handoff_intake.evaluate_oanda_demo_runtime_handoff_intake(
        _approved_intake(credential_value_present=True, runtime_auth_value="Bearer NOT_A_REAL_VALUE")
    )

    assert result["runtime_handoff_intake_ready"] is False
    assert "credential_value_not_allowed" in result["blockers"]
    assert "forbidden_field:runtime_auth_value" in result["blockers"]
    assert "credential_like_value:runtime_auth_value" in result["blockers"]
    assert result["audit_event"]["contains_real_credentials"] is False
    assert result["credentials_used"] is False


def test_live_endpoint_rejected() -> None:
    result = oanda_demo_runtime_handoff_intake.evaluate_oanda_demo_runtime_handoff_intake(
        _approved_intake(endpoint_classification="OANDA_LIVE")
    )

    assert result["runtime_handoff_intake_ready"] is False
    assert "unsupported_endpoint_classification" in result["blockers"]
    assert "live_endpoint_reference_blocked" in result["blockers"]
    assert "live_reference:endpoint_classification" in result["blockers"]
    assert result["live_endpoint_allowed"] is False
    assert result["live_execution_allowed"] is False


def test_unauthorized_intake_rejected() -> None:
    result = oanda_demo_runtime_handoff_intake.evaluate_oanda_demo_runtime_handoff_intake(
        _approved_intake(
            metadata_intake_authorized=False,
            intake_execution_requested=True,
            broker_request_requested=True,
        )
    )

    assert result["runtime_handoff_intake_ready"] is False
    assert "metadata_intake_authorization_required" in result["blockers"]
    assert "unauthorized_intake_attempt" in result["blockers"]
    assert "unauthorized_execution_field:intake_execution_requested" in result["blockers"]
    assert "unauthorized_execution_field:broker_request_requested" in result["blockers"]
    assert result["connection_attempt_performed"] is False
    assert result["broker_request_sent"] is False


def test_sanitized_evidence_generated() -> None:
    result = oanda_demo_runtime_handoff_intake.evaluate_oanda_demo_runtime_handoff_intake(
        _approved_intake()
    )
    audit_event = result["audit_event"]
    evidence_schema = result["evidence_schema"]

    assert evidence_schema["contains_real_credentials"] is False
    assert evidence_schema["contains_account_identifier"] is False
    assert audit_event["sanitized"] is True
    assert audit_event["credential_values_recorded"] is False
    assert audit_event["account_identifiers_recorded"] is False
    assert audit_event["broker_payloads_recorded"] is False


def test_fail_closed_behavior_verified() -> None:
    result = oanda_demo_runtime_handoff_intake.evaluate_oanda_demo_runtime_handoff_intake(
        _approved_intake(network_api_allowed=True, order_route_requested=True)
    )

    assert result["runtime_handoff_intake_ready"] is False
    assert "unauthorized_intake_attempt" in result["blockers"]
    assert result["network_api_allowed"] is False
    assert result["broker_connection_allowed"] is False
    assert result["broker_request_sent"] is False
    assert result["order_route_allowed"] is False
    assert result["order_placed"] is False
    assert result["live_execution_allowed"] is False


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
