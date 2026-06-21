from automation.forex_engine.no_order_connector_contracts_g_v1 import build_demo_no_order_contract
from automation.forex_engine.read_only_probe_skeleton_i_v1 import ReadOnlyProbeSkeleton
from automation.forex_engine.runtime_orchestration_binding_i_v1 import bind_runtime_orchestration


def test_runtime_orchestration_ready_path():
    result = bind_runtime_orchestration(
        endpoint_mode="DEMO",
        credential_metadata={},
        account_metadata={"replay_reference": "safe"},
        governance_approved=True,
        kill_switch_active=False,
        no_order_connector=build_demo_no_order_contract("connector-001"),
        read_only_probe=ReadOnlyProbeSkeleton(
            probe_id="probe-001",
            replay_references=("replay-001",),
            evidence_references=("evidence-001",),
        ),
    )

    assert result.ready is True
    assert result.blocked_reasons == ()
    assert result.replay_references == ("replay-001",)
    assert result.evidence_references == ("evidence-001",)


def test_endpoint_failure_propagates():
    result = bind_runtime_orchestration(
        endpoint_mode="LIVE",
        credential_metadata={},
        account_metadata={},
        governance_approved=True,
        kill_switch_active=False,
        no_order_connector=build_demo_no_order_contract("connector-001"),
        read_only_probe=ReadOnlyProbeSkeleton(probe_id="probe-001"),
    )

    assert result.ready is False
    assert "live_endpoint_prohibited" in result.blocked_reasons


def test_credential_failure_propagates():
    result = bind_runtime_orchestration(
        endpoint_mode="DEMO",
        credential_metadata={"api_key": "example"},
        account_metadata={},
        governance_approved=True,
        kill_switch_active=False,
        no_order_connector=build_demo_no_order_contract("connector-001"),
        read_only_probe=ReadOnlyProbeSkeleton(probe_id="probe-001"),
    )

    assert result.ready is False
    assert "credential_key_prohibited:api_key" in result.blocked_reasons


def test_kill_switch_failure_propagates():
    result = bind_runtime_orchestration(
        endpoint_mode="DEMO",
        credential_metadata={},
        account_metadata={},
        governance_approved=True,
        kill_switch_active=True,
        no_order_connector=build_demo_no_order_contract("connector-001"),
        read_only_probe=ReadOnlyProbeSkeleton(probe_id="probe-001"),
    )

    assert result.ready is False
    assert "kill_switch_active" in result.blocked_reasons


def test_probe_failure_propagates():
    result = bind_runtime_orchestration(
        endpoint_mode="DEMO",
        credential_metadata={},
        account_metadata={},
        governance_approved=True,
        kill_switch_active=False,
        no_order_connector=build_demo_no_order_contract("connector-001"),
        read_only_probe=ReadOnlyProbeSkeleton(probe_id="", blocked_reasons=("manual_probe_block",)),
    )

    assert result.ready is False
    assert "probe_id_missing" in result.blocked_reasons
    assert "manual_probe_block" in result.blocked_reasons