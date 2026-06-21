from automation.forex_engine.broker_bridge_runtime_validator_h_v1 import (
    validate_broker_bridge_runtime,
)
from automation.forex_engine.no_order_connector_contracts_g_v1 import (
    build_demo_no_order_contract,
)


def test_clean_broker_bridge_runtime_is_ready():
    result = validate_broker_bridge_runtime(
        endpoint_mode="DEMO",
        credential_metadata={},
        account_metadata={"replay_reference": "replay-001"},
        governance_approved=True,
        kill_switch_active=False,
        no_order_connector=build_demo_no_order_contract("connector-001"),
    )

    assert result.ready is True
    assert result.blocked_reasons == ()
    assert result.sanitized_account_metadata["replay_reference"] == "replay-001"


def test_live_endpoint_blocks_runtime():
    result = validate_broker_bridge_runtime(
        endpoint_mode="LIVE",
        credential_metadata={},
        account_metadata={},
        governance_approved=True,
        kill_switch_active=False,
        no_order_connector=build_demo_no_order_contract("connector-001"),
    )

    assert result.ready is False
    assert "live_endpoint_prohibited" in result.blocked_reasons


def test_credential_leak_blocks_runtime():
    result = validate_broker_bridge_runtime(
        endpoint_mode="DEMO",
        credential_metadata={"api_key": "example"},
        account_metadata={},
        governance_approved=True,
        kill_switch_active=False,
        no_order_connector=build_demo_no_order_contract("connector-001"),
    )

    assert result.ready is False
    assert "credential_key_prohibited:api_key" in result.blocked_reasons


def test_account_metadata_is_sanitized_and_blocks_readiness():
    result = validate_broker_bridge_runtime(
        endpoint_mode="DEMO",
        credential_metadata={},
        account_metadata={"account_id": "real-account", "replay_reference": "safe"},
        governance_approved=True,
        kill_switch_active=False,
        no_order_connector=build_demo_no_order_contract("connector-001"),
    )

    assert result.ready is False
    assert "account_metadata_sanitized" in result.blocked_reasons
    assert "account_id" not in result.sanitized_account_metadata
    assert result.sanitized_account_metadata["replay_reference"] == "safe"


def test_governance_not_approved_blocks_runtime():
    result = validate_broker_bridge_runtime(
        endpoint_mode="DEMO",
        credential_metadata={},
        account_metadata={},
        governance_approved=False,
        kill_switch_active=False,
        no_order_connector=build_demo_no_order_contract("connector-001"),
    )

    assert result.ready is False
    assert "governance_not_approved" in result.blocked_reasons


def test_kill_switch_blocks_runtime():
    result = validate_broker_bridge_runtime(
        endpoint_mode="DEMO",
        credential_metadata={},
        account_metadata={},
        governance_approved=True,
        kill_switch_active=True,
        no_order_connector=build_demo_no_order_contract("connector-001"),
    )

    assert result.ready is False
    assert "kill_switch_active" in result.blocked_reasons


def test_no_order_connector_block_reason_propagates():
    connector = build_demo_no_order_contract("connector-001", capabilities=["order_place"])

    result = validate_broker_bridge_runtime(
        endpoint_mode="DEMO",
        credential_metadata={},
        account_metadata={},
        governance_approved=True,
        kill_switch_active=False,
        no_order_connector=connector,
    )

    assert result.ready is False
    assert "prohibited_capability:order_place" in result.blocked_reasons