from automation.forex_engine.final_demo_readiness_validator_i_v1 import validate_final_demo_readiness
from automation.forex_engine.no_order_connector_contracts_g_v1 import build_demo_no_order_contract
from automation.forex_engine.read_only_probe_skeleton_i_v1 import ReadOnlyProbeSkeleton


def test_final_demo_readiness_ready_path():
    result = validate_final_demo_readiness(
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

    assert result.status == "READY"
    assert result.blocked_reasons == ()
    assert result.replay_references == ("replay-001",)
    assert result.evidence_references == ("evidence-001",)


def test_final_demo_readiness_missing_endpoint_fails():
    result = validate_final_demo_readiness(
        endpoint_mode=None,
        credential_metadata={},
        account_metadata={},
        governance_approved=True,
        kill_switch_active=False,
        no_order_connector=build_demo_no_order_contract("connector-001"),
        read_only_probe=ReadOnlyProbeSkeleton(probe_id="probe-001"),
    )

    assert result.status == "NOT_READY"
    assert "endpoint_mode_missing" in result.blocked_reasons


def test_final_demo_readiness_governance_failure_fails():
    result = validate_final_demo_readiness(
        endpoint_mode="DEMO",
        credential_metadata={},
        account_metadata={},
        governance_approved=False,
        kill_switch_active=False,
        no_order_connector=build_demo_no_order_contract("connector-001"),
        read_only_probe=ReadOnlyProbeSkeleton(probe_id="probe-001"),
    )

    assert result.status == "NOT_READY"
    assert "governance_not_approved" in result.blocked_reasons


def test_final_demo_readiness_kill_switch_failure_fails():
    result = validate_final_demo_readiness(
        endpoint_mode="DEMO",
        credential_metadata={},
        account_metadata={},
        governance_approved=True,
        kill_switch_active=True,
        no_order_connector=build_demo_no_order_contract("connector-001"),
        read_only_probe=ReadOnlyProbeSkeleton(probe_id="probe-001"),
    )

    assert result.status == "NOT_READY"
    assert "kill_switch_active" in result.blocked_reasons


def test_final_demo_readiness_connector_failure_fails():
    result = validate_final_demo_readiness(
        endpoint_mode="DEMO",
        credential_metadata={},
        account_metadata={},
        governance_approved=True,
        kill_switch_active=False,
        no_order_connector=build_demo_no_order_contract("connector-001", capabilities=["order_place"]),
        read_only_probe=ReadOnlyProbeSkeleton(probe_id="probe-001"),
    )

    assert result.status == "NOT_READY"
    assert "prohibited_capability:order_place" in result.blocked_reasons


def test_final_demo_readiness_probe_failure_fails():
    result = validate_final_demo_readiness(
        endpoint_mode="DEMO",
        credential_metadata={},
        account_metadata={},
        governance_approved=True,
        kill_switch_active=False,
        no_order_connector=build_demo_no_order_contract("connector-001"),
        read_only_probe=ReadOnlyProbeSkeleton(probe_id=""),
    )

    assert result.status == "NOT_READY"
    assert "probe_id_missing" in result.blocked_reasons