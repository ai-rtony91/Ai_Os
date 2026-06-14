from automation.orchestration.self_development.aios_self_build_candidate_selector import (
    BLOCKED_SURFACES,
    select_self_build_candidate,
)


def test_selects_self_build_candidate_before_forex_candidate() -> None:
    result = select_self_build_candidate({"eligible_lanes": ["forex_research", "validator_repair"]})

    assert result["schema"] == "AIOS_SELF_BUILD_CANDIDATE_SELECTION.v1"
    assert result["candidate_lane"] == "validator_repair"
    assert result["candidate_id"] == "AIOS-SELF-BUILD-VALIDATOR-REPAIR-CANDIDATE"


def test_default_candidate_when_repo_idle_is_runner_hardening() -> None:
    result = select_self_build_candidate({})

    assert result["candidate_id"] == "AIOS-SELF-BUILD-RUNNER-HARDENING-CANDIDATE"
    assert result["candidate_title"] == "Harden AIOS autonomous self-build runners"
    assert result["candidate_lane"] == "runner_hardening"
    assert result["priority"] == "high"


def test_defers_dashboard_ui_unless_explicitly_requested() -> None:
    result = select_self_build_candidate({"requested_lane": "dashboard_ui"})

    assert result["candidate_lane"] == "runner_hardening"
    assert "Dashboard/UI is deferred" in result["reason"]
    assert result["safety"]["dashboard_ui_deferred"] is True


def test_emits_allowed_files_and_blocked_surfaces() -> None:
    result = select_self_build_candidate({})

    assert result["allowed_files"]
    assert result["required_validators"]
    for surface in (
        "secrets",
        ".env",
        "broker",
        "OANDA",
        "live trading",
        "webhook",
        "orders",
        "scheduler",
        "daemon",
        "queue mutation",
        "lock mutation",
        "approval mutation",
        "registry mutation",
        "push",
        "PR",
        "merge",
    ):
        assert surface in result["blocked_surfaces"]
        assert surface in BLOCKED_SURFACES


def test_selector_does_not_mutate_registry_or_create_ready_stage() -> None:
    result = select_self_build_candidate({})

    assert result["safety"]["writes_files"] is False
    assert result["safety"]["mutates_registry"] is False
    assert result["safety"]["creates_ready_stage"] is False
    assert result["safety"]["mutates_queue"] is False
    assert result["safety"]["mutates_locks"] is False
    assert result["safety"]["mutates_approval"] is False
