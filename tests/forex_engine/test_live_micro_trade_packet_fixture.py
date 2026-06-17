import json
from pathlib import Path

from automation.forex_engine import live_micro_trade_contract as contract


FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "automation"
    / "forex_engine"
    / "fixtures"
    / "live_micro_trade_packet_001.example.json"
)

FORBIDDEN_TERMS = {
    "credentials",
    "token",
    "tokens",
    "api_key",
    "password",
    "secret",
    "account_id",
    "account_identifier",
    "broker_order_id",
    "raw_live_payload",
    "live_payload",
    "private_account_data",
}


def load_fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def iter_keys_and_values(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key)
            yield from iter_keys_and_values(nested)
    elif isinstance(value, list):
        for item in value:
            yield from iter_keys_and_values(item)
    elif isinstance(value, str):
        yield value


def test_fixture_loads_and_validates_request_contract():
    fixture = load_fixture()

    result = contract.validate_micro_trade_request(fixture["trade_packet"])

    assert result["request_contract_valid"] is True
    assert result["live_mode"] is False
    assert result["one_order_only"] is True
    assert result["retry_allowed"] is False
    assert result["autonomous_reentry_allowed"] is False


def test_fixture_validates_approval_contract():
    fixture = load_fixture()

    result = contract.validate_micro_trade_approval(fixture["approval"])

    assert result["approval_contract_valid"] is True
    assert result["human_owner"] == "Anthony"
    assert result["generic_approval_booleans_sufficient"] is False
    assert result["validator_approval_sufficient"] is False
    assert result["dashboard_approval_sufficient"] is False
    assert result["router_approval_sufficient"] is False


def test_fixture_validates_evidence_bundle_and_audit_events():
    fixture = load_fixture()

    evidence = contract.validate_evidence_bundle(fixture["evidence_bundle"])
    audit_results = [
        contract.validate_audit_event(audit_event)
        for audit_event in fixture["audit_events"]
    ]

    assert evidence["evidence_bundle_contract_valid"] is True
    assert all(result["audit_event_contract_valid"] is True for result in audit_results)


def test_fixture_validates_arming_and_disarm_state():
    fixture = load_fixture()

    arming = contract.validate_arming_state(fixture["arming_state"])
    disarm = contract.validate_disarm_state(fixture["disarm_state"])

    assert arming["arming_contract_valid"] is True
    assert arming["execution_allowed"] is False
    assert disarm["disarm_contract_valid"] is True
    assert disarm["terminal"] is True
    assert disarm["execution_allowed"] is False


def test_fixture_has_no_forbidden_keys_or_terms():
    fixture = load_fixture()
    observed = {item.lower() for item in iter_keys_and_values(fixture)}

    assert not (FORBIDDEN_TERMS & observed)
    fixture_text = FIXTURE_PATH.read_text(encoding="utf-8").lower()
    for term in FORBIDDEN_TERMS:
        assert term not in fixture_text


def test_fixture_truth_statuses_are_sanitized_and_non_submitted():
    fixture = load_fixture()
    broker_truth = fixture["broker_truth_status"]

    assert broker_truth["account_balance_status"] == "SANITIZED_SNAPSHOT_PRESENT"
    assert broker_truth["available_margin_status"] == "SANITIZED_SNAPSHOT_PRESENT"
    assert broker_truth["open_positions_status"] == "SANITIZED_WITHIN_SCOPE_PROOF"
    assert broker_truth["current_exposure_status"] == "SANITIZED_WITHIN_LIMIT_PROOF"
    assert broker_truth["live_price_or_quote_status"] == "SANITIZED_QUOTE_PRESENT"
    assert broker_truth["spread_status"] == "SANITIZED_SPREAD_PRESENT"
    assert broker_truth["order_status"] == "NOT_SUBMITTED"
    assert broker_truth["fill_or_reject_status"] == "NOT_ATTEMPTED"
    assert broker_truth["daily_realized_pnl_status"] == "SANITIZED_WITHIN_CAP_PROOF"


def test_fixture_safety_flags_disable_execution_paths():
    fixture = load_fixture()
    flags = fixture["safety_flags"]

    assert flags["live_mode"] is False
    assert flags["one_order_only"] is True
    assert flags["retry_allowed"] is False
    assert flags["autonomous_reentry_allowed"] is False
    assert flags["credential_material_present"] is False
    assert flags["broker_api_enabled"] is False
    assert flags["live_execution_enabled"] is False
    assert flags["dashboard_authority"] is False
    assert flags["validator_authority"] is False
    assert flags["broker_sdk_allowed"] is False
    assert flags["network_allowed"] is False
    assert flags["runtime_context_access_allowed"] is False
    assert flags["subprocess_allowed"] is False
    assert flags["scheduler_allowed"] is False
    assert flags["daemon_allowed"] is False
    assert flags["order_submitted"] is False
    assert flags["paper_trade_simulated"] is False
    assert flags["real_trade_simulated"] is False


def test_fixture_contract_module_reports_no_execution_capabilities():
    summary = contract.assert_contract_module_has_no_execution_capabilities()

    assert summary["broker_sdk_allowed"] is False
    assert summary["network_allowed"] is False
    assert summary["credential_access_allowed"] is False
    assert summary["environment_secret_read_allowed"] is False
    assert summary["subprocess_allowed"] is False
    assert summary["scheduler_allowed"] is False
    assert summary["daemon_allowed"] is False
    assert summary["live_trading_enabled"] is False
    assert summary["orders_allowed"] is False
