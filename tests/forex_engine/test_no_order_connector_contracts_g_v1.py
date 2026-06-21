import pytest

from automation.forex_engine.no_order_connector_contracts_g_v1 import (
    EndpointMode,
    GovernanceStatus,
    KillSwitchState,
    NoOrderConnectorContract,
    assert_no_order_connector_ready,
    build_demo_no_order_contract,
    evaluate_no_order_connector,
)


def test_demo_no_order_connector_passes_planning_readiness():
    contract = build_demo_no_order_contract("demo-paper-connector")
    result = evaluate_no_order_connector(contract)

    assert result.ready is True
    assert result.blocked_reasons == ()


def test_live_endpoint_is_rejected():
    contract = NoOrderConnectorContract(
        connector_id="bad-live",
        connector_mode="NO_ORDER_CONNECTOR_CONTRACT",
        endpoint_mode=EndpointMode.LIVE.value,
        capabilities=("read_only_planning", "no_order_planning"),
    )

    result = evaluate_no_order_connector(contract)

    assert result.ready is False
    assert "endpoint_mode_not_demo" in result.blocked_reasons


@pytest.mark.parametrize(
    "capability",
    [
        "network_transport",
        "broker_sdk",
        "credential_access",
        "account_identifier_access",
        "order_place",
        "order_modify",
        "order_cancel",
        "position_mutate",
        "live_trading",
        "demo_trading_execution",
    ],
)
def test_prohibited_capabilities_are_rejected(capability):
    contract = build_demo_no_order_contract("blocked-capability", capabilities=[capability])

    result = evaluate_no_order_connector(contract)

    assert result.ready is False
    assert f"prohibited_capability:{capability}" in result.blocked_reasons


def test_missing_endpoint_mode_is_rejected():
    contract = NoOrderConnectorContract(
        connector_id="missing-endpoint",
        connector_mode="NO_ORDER_CONNECTOR_CONTRACT",
        endpoint_mode="",
        capabilities=("read_only_planning", "no_order_planning"),
    )

    result = evaluate_no_order_connector(contract)

    assert result.ready is False
    assert "endpoint_mode_missing" in result.blocked_reasons


def test_kill_switch_active_blocks_readiness():
    contract = build_demo_no_order_contract(
        "kill-switch-active",
        kill_switch_state=KillSwitchState.ACTIVE.value,
    )

    result = evaluate_no_order_connector(contract)

    assert result.ready is False
    assert "kill_switch_active" in result.blocked_reasons


def test_credential_boundary_not_clear_blocks_readiness():
    contract = build_demo_no_order_contract(
        "credential-blocked",
        credential_boundary_clear=False,
    )

    result = evaluate_no_order_connector(contract)

    assert result.ready is False
    assert "credential_boundary_not_clear" in result.blocked_reasons


def test_account_boundary_not_clear_blocks_readiness():
    contract = build_demo_no_order_contract(
        "account-blocked",
        account_boundary_clear=False,
    )

    result = evaluate_no_order_connector(contract)

    assert result.ready is False
    assert "account_boundary_not_clear" in result.blocked_reasons


def test_governance_not_approved_blocks_readiness():
    contract = build_demo_no_order_contract(
        "governance-blocked",
        governance_status=GovernanceStatus.NOT_APPROVED.value,
    )

    result = evaluate_no_order_connector(contract)

    assert result.ready is False
    assert "governance_not_approved" in result.blocked_reasons


def test_blocked_reasons_are_replayable_and_deduped():
    contract = NoOrderConnectorContract(
        connector_id="",
        connector_mode="NO_ORDER_CONNECTOR_CONTRACT",
        endpoint_mode=EndpointMode.LIVE.value,
        capabilities=("order_place", "order_place"),
        blocked_reasons=("manual_block", "manual_block"),
    )

    result = evaluate_no_order_connector(contract)

    assert result.ready is False
    assert result.blocked_reasons.count("manual_block") == 1
    assert "connector_id_missing" in result.blocked_reasons
    assert "endpoint_mode_not_demo" in result.blocked_reasons
    assert "prohibited_capability:order_place" in result.blocked_reasons


def test_assert_ready_returns_contract_when_ready():
    contract = build_demo_no_order_contract("ready-contract")

    assert assert_no_order_connector_ready(contract) == contract


def test_assert_ready_raises_with_blocked_reasons_when_not_ready():
    contract = build_demo_no_order_contract("not-ready", capabilities=["order_cancel"])

    with pytest.raises(ValueError) as exc:
        assert_no_order_connector_ready(contract)

    assert "prohibited_capability:order_cancel" in str(exc.value)