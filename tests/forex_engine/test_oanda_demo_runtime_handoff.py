from __future__ import annotations

from pathlib import Path

from automation.forex_engine import oanda_demo_runtime_handoff


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "oanda_demo_runtime_handoff.py"
DOC_PATH = (
    REPO_ROOT
    / "docs"
    / "trading_lab"
    / "AIOS_FOREX_BUILDER_OANDA_DEMO_RUNTIME_HANDOFF.md"
)
REPORT_PATH = (
    REPO_ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_OANDA_DEMO_PROBE_RUNTIME_HANDOFF_V1_REPORT.md"
)


def _approved_handoff(**overrides):
    payload = oanda_demo_runtime_handoff.build_example_oanda_demo_runtime_handoff()
    payload.update(overrides)
    return payload


def test_runtime_handoff_contract_docs_and_report_exist() -> None:
    contract_set = oanda_demo_runtime_handoff.build_oanda_demo_runtime_handoff_contract_set()

    assert MODULE_PATH.exists()
    assert DOC_PATH.exists()
    assert REPORT_PATH.exists()
    assert contract_set["contracts_ready_for_future_runtime_handoff"] is True
    assert contract_set["runtime_handoff_intake_required_before_runtime_handoff"] is True
    assert contract_set["runtime_handoff_intake_contract_set"][
        "contracts_ready_for_future_runtime_handoff_intake"
    ] is True
    assert contract_set["runtime_handoff_contract"]["mode"] == "RUNTIME_HANDOFF_VALIDATE_ONLY"
    assert contract_set["runtime_auth_reference_validation_contract"][
        "runtime_reference_value_accepted"
    ] is False


def test_missing_runtime_reference_rejection_fails_closed() -> None:
    result = oanda_demo_runtime_handoff.evaluate_oanda_demo_runtime_handoff()

    assert result["status"] == "OANDA_DEMO_RUNTIME_HANDOFF_BLOCKED"
    assert result["classification"] == "FAIL_CLOSED"
    assert result["runtime_handoff_ready"] is False
    assert "runtime_reference_required" in result["blockers"]
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False


def test_malformed_runtime_reference_rejection_fails_closed() -> None:
    result = oanda_demo_runtime_handoff.evaluate_oanda_demo_runtime_handoff(
        _approved_handoff(
            runtime_reference_format="RAW_REFERENCE",
            auth_material_location="REPO_FILE",
        )
    )

    assert result["runtime_handoff_ready"] is False
    assert "malformed_runtime_reference" in result["blockers"]
    assert "malformed_auth_material_location" in result["blockers"]
    assert result["credential_material_present"] is False
    assert result["connection_attempt_allowed_now"] is False


def test_account_id_rejection_fails_closed() -> None:
    result = oanda_demo_runtime_handoff.evaluate_oanda_demo_runtime_handoff(
        _approved_handoff(account_identifier_present=True, account_id="DO_NOT_STORE")
    )

    assert result["runtime_handoff_ready"] is False
    assert "account_identifier_not_allowed" in result["blockers"]
    assert "forbidden_field:account_id" in result["blockers"]
    assert result["audit_event"]["contains_account_identifier"] is False
    assert result["account_access_allowed"] is False


def test_credential_value_rejection_fails_closed() -> None:
    result = oanda_demo_runtime_handoff.evaluate_oanda_demo_runtime_handoff(
        _approved_handoff(credential_value_present=True, runtime_auth_value="Bearer NOT_A_REAL_VALUE")
    )

    assert result["runtime_handoff_ready"] is False
    assert "credential_value_not_allowed" in result["blockers"]
    assert "forbidden_field:runtime_auth_value" in result["blockers"]
    assert "credential_like_value:runtime_auth_value" in result["blockers"]
    assert result["audit_event"]["contains_real_credentials"] is False
    assert result["credentials_used"] is False


def test_live_endpoint_rejection_fails_closed() -> None:
    result = oanda_demo_runtime_handoff.evaluate_oanda_demo_runtime_handoff(
        _approved_handoff(endpoint_classification="OANDA_LIVE")
    )

    assert result["runtime_handoff_ready"] is False
    assert "unsupported_endpoint_classification" in result["blockers"]
    assert "live_endpoint_reference_blocked" in result["blockers"]
    assert result["live_endpoint_allowed"] is False
    assert result["live_execution_allowed"] is False


def test_unauthorized_probe_rejection_fails_closed() -> None:
    result = oanda_demo_runtime_handoff.evaluate_oanda_demo_runtime_handoff(
        _approved_handoff(probe_attempt_requested=True, broker_request_requested=True)
    )

    assert result["runtime_handoff_ready"] is False
    assert "unauthorized_probe_attempt" in result["blockers"]
    assert "unauthorized_execution_field:probe_attempt_requested" in result["blockers"]
    assert "unauthorized_execution_field:broker_request_requested" in result["blockers"]
    assert result["connection_attempt_performed"] is False
    assert result["broker_request_sent"] is False


def test_sanitized_evidence_generation() -> None:
    result = oanda_demo_runtime_handoff.evaluate_oanda_demo_runtime_handoff(_approved_handoff())
    audit_event = result["audit_event"]
    evidence_schema = result["evidence_schema"]

    assert result["status"] == "OANDA_DEMO_RUNTIME_HANDOFF_READY"
    assert result["runtime_handoff_ready"] is True
    assert result["runtime_handoff_intake_ready"] is True
    assert result["runtime_handoff_intake"]["metadata_accepted"] is True
    assert result["runtime_boundary_enforced"] is True
    assert evidence_schema["contains_real_credentials"] is False
    assert evidence_schema["contains_account_identifier"] is False
    assert audit_event["sanitized"] is True
    assert audit_event["credential_values_recorded"] is False
    assert audit_event["account_identifiers_recorded"] is False
    assert audit_event["broker_payloads_recorded"] is False


def test_runtime_boundary_enforcement() -> None:
    result = oanda_demo_runtime_handoff.evaluate_oanda_demo_runtime_handoff(
        _approved_handoff(
            runtime_boundary_confirmed=False,
            repo_storage_confirmed_absent=False,
            no_account_id_storage_confirmed=False,
            no_auth_value_storage_confirmed=False,
        )
    )

    assert result["runtime_handoff_ready"] is False
    assert "runtime_boundary_confirmation_required" in result["blockers"]
    assert "repo_auth_material_must_be_absent" in result["blockers"]
    assert "no_account_id_storage_confirmation_required" in result["blockers"]
    assert "no_auth_value_storage_confirmation_required" in result["blockers"]
    assert result["repo_stored_auth_material_present"] is False


def test_runtime_handoff_blocks_when_intake_authorization_fails() -> None:
    result = oanda_demo_runtime_handoff.evaluate_oanda_demo_runtime_handoff(
        _approved_handoff(metadata_intake_authorized=False)
    )

    assert result["runtime_handoff_ready"] is False
    assert result["runtime_handoff_intake_ready"] is False
    assert "runtime_handoff_intake_required" in result["blockers"]
    assert (
        "runtime_handoff_intake_blocker:metadata_intake_authorization_required"
        in result["blockers"]
    )
    assert result["connection_attempt_allowed_now"] is False


def test_fail_closed_behavior_preserves_all_execution_blocks() -> None:
    result = oanda_demo_runtime_handoff.evaluate_oanda_demo_runtime_handoff(
        _approved_handoff(network_api_allowed=True, order_route_requested=True)
    )

    assert result["runtime_handoff_ready"] is False
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
