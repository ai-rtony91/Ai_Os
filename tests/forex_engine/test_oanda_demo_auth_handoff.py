from __future__ import annotations

from pathlib import Path

from automation.forex_engine import oanda_demo_auth_handoff


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "oanda_demo_auth_handoff.py"
DOC_PATH = (
    REPO_ROOT
    / "docs"
    / "trading_lab"
    / "AIOS_FOREX_BUILDER_OANDA_DEMO_AUTH_HANDOFF.md"
)


def _example_handoff(**overrides):
    payload = oanda_demo_auth_handoff.build_example_sanitized_demo_auth_handoff()
    payload.update(overrides)
    return payload


def test_auth_handoff_contracts_exist_and_block_broker_live_side_effects() -> None:
    contract_set = oanda_demo_auth_handoff.build_oanda_demo_auth_contract_set()

    assert MODULE_PATH.exists()
    assert DOC_PATH.exists()
    assert contract_set["contracts_ready_for_future_external_handoff"] is True
    for section in (
        "external_auth_handoff_contract",
        "credential_boundary_contract",
        "demo_account_validation_contract",
        "runtime_handoff_contract_set",
        "evidence_requirements",
        "audit_logging_requirements",
    ):
        contract = contract_set[section]
        assert contract["broker_id"] == "OANDA"
        assert contract["broker_sdk_allowed"] is False
        assert contract["network_api_allowed"] is False
        assert contract["credentials_allowed"] is False
        assert contract["broker_request_sent"] is False
        assert contract["live_execution_allowed"] is False
        assert contract["live_orders_allowed"] is False
    assert contract_set["runtime_handoff_required_before_connection_probe"] is True


def test_missing_credential_rejection_fails_closed() -> None:
    result = oanda_demo_auth_handoff.evaluate_oanda_demo_auth_handoff_readiness()

    assert result["status"] == "OANDA_DEMO_AUTH_HANDOFF_BLOCKED"
    assert result["auth_handoff_ready"] is False
    assert "missing_external_auth_reference" in result["blockers"]
    assert "MISSING_CREDENTIALS" in result["failure_states"]
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["credentials_used"] is False
    assert result["live_execution_allowed"] is False


def test_malformed_credential_rejection_fails_closed() -> None:
    result = oanda_demo_auth_handoff.evaluate_oanda_demo_auth_handoff_readiness(
        _example_handoff(
            external_auth_reference_format="RAW_AUTH_VALUE",
            auth_material_location="REPO_FILE",
            api_key="EXAMPLE_NOT_A_REAL_VALUE",
        )
    )

    assert result["status"] == "OANDA_DEMO_AUTH_HANDOFF_BLOCKED"
    assert result["auth_handoff_ready"] is False
    assert "malformed_external_auth_reference" in result["blockers"]
    assert "malformed_auth_material_location" in result["blockers"]
    assert "forbidden_field:api_key" in result["blockers"]
    assert "MALFORMED_CREDENTIALS" in result["failure_states"]
    assert result["contains_real_credentials"] is False
    assert result["credentials_used"] is False


def test_unsupported_account_rejection_fails_closed() -> None:
    result = oanda_demo_auth_handoff.evaluate_oanda_demo_auth_handoff_readiness(
        _example_handoff(account_mode="STANDARD_DEMO")
    )

    assert result["auth_handoff_ready"] is False
    assert "unsupported_account_type" in result["blockers"]
    assert "UNSUPPORTED_ACCOUNT_TYPE" in result["failure_states"]
    assert result["live_account_access_allowed"] is False
    assert result["real_money_routing_allowed"] is False


def test_live_account_rejection_fails_closed() -> None:
    result = oanda_demo_auth_handoff.evaluate_oanda_demo_auth_handoff_readiness(
        _example_handoff(account_mode="LIVE", environment="OANDA_LIVE")
    )

    assert result["auth_handoff_ready"] is False
    assert "live_account_attempt_blocked" in result["blockers"]
    assert "LIVE_ACCOUNT_ATTEMPT" in result["failure_states"]
    assert result["live_execution_allowed"] is False
    assert result["live_orders_allowed"] is False
    assert result["broker_request_sent"] is False


def test_sanitized_demo_auth_handoff_passes_readiness_without_execution() -> None:
    result = oanda_demo_auth_handoff.evaluate_oanda_demo_auth_handoff_readiness(
        _example_handoff()
    )
    summary = oanda_demo_auth_handoff.summarize_oanda_demo_auth_handoff_readiness(result)

    assert result["status"] == "OANDA_DEMO_AUTH_HANDOFF_READY"
    assert result["auth_handoff_ready"] is True
    assert result["authentication_readiness_passed"] is True
    assert result["credential_boundary_passed"] is True
    assert result["account_validation_passed"] is True
    assert result["blockers"] == []
    assert result["failure_states"] == []
    assert summary["auth_handoff_ready"] is True
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["order_placed"] is False
    assert result["live_execution_allowed"] is False


def test_auth_audit_evidence_generation_is_sanitized() -> None:
    result = oanda_demo_auth_handoff.evaluate_oanda_demo_auth_handoff_readiness(
        _example_handoff()
    )
    audit_event = result["audit_event"]

    assert audit_event["schema"] == "AIOS_OANDA_DEMO_AUTH_AUDIT_EVENT.v1"
    assert audit_event["event"] == "oanda_demo_auth_handoff_readiness_evaluated"
    assert audit_event["sanitized"] is True
    assert audit_event["contains_real_credentials"] is False
    assert audit_event["contains_account_identifier"] is False
    assert audit_event["credential_values_recorded"] is False
    assert audit_event["account_identifiers_recorded"] is False
    assert result["evidence_requirements"]["audit_log_required"] is True


def test_unauthorized_execution_attempt_fails_closed() -> None:
    result = oanda_demo_auth_handoff.evaluate_oanda_demo_auth_handoff_readiness(
        _example_handoff(
            execution_requested=True,
            broker_request_requested=True,
            network_api_allowed=True,
        )
    )

    assert result["status"] == "OANDA_DEMO_AUTH_HANDOFF_BLOCKED"
    assert "unauthorized_execution_attempt" in result["blockers"]
    assert "UNAUTHORIZED_EXECUTION_ATTEMPT" in result["failure_states"]
    assert "unauthorized_execution_field:execution_requested" in result["blockers"]
    assert "unauthorized_execution_field:broker_request_requested" in result["blockers"]
    assert "unauthorized_execution_field:network_api_allowed" in result["blockers"]
    assert result["execution_allowed"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["order_placed"] is False


def test_no_credential_persistence_in_readiness_result() -> None:
    result = oanda_demo_auth_handoff.evaluate_oanda_demo_auth_handoff_readiness(
        _example_handoff()
    )

    assert result["repo_stored_auth_material_present"] is False
    assert result["credential_material_present"] is False
    assert result["auth_material_persisted"] is False
    assert result["contains_real_credentials"] is False
    assert result["contains_account_identifier"] is False
    assert result["audit_event"]["repo_stored_auth_material_present"] is False


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

