from __future__ import annotations

import sys

sys.dont_write_bytecode = True

from automation.orchestration.validators.aios_validator_evidence_router import (
    SCHEMA,
    build_router_result,
    classify_surface,
    sanitize_command_field,
)


def _payload(**overrides: object) -> dict:
    payload = {
        "generated_utc": "2026-06-13T00:00:00Z",
        "repo_state": {
            "branch": "feature/governed-self-development-closure-v1",
            "expected_branch": "feature/governed-self-development-closure-v1",
            "branch_matches_expected": True,
            "dirty": False,
            "dirty_allowed_for_validator_evidence_router_validation": False,
            "fail_on_dirty_worktree": True,
        },
        "authority_context": {
            "all_required_loaded": True,
            "files": [],
        },
        "source_packet_router_result": {
            "schema": "AIOS_SELF_DEVELOPMENT_PACKET_ROUTER_RESULT.v1",
        },
        "surface_inventory": [],
        "action_recommendation": {
            "recommended_command": "git add -- unsafe && git commit -m unsafe",
        },
        "no_write_proof": {
            "changed": False,
            "git_state_changed": False,
            "forbidden_surface_changed": False,
        },
    }
    payload.update(overrides)
    return payload


def _by_path(items: list[dict]) -> dict[str, dict]:
    return {item["path"]: item for item in items}


def test_python_logic_emits_validator_evidence_router_schema() -> None:
    result = build_router_result(_payload())

    assert result["schema"] == SCHEMA
    assert result["mode"] == "DRY_RUN_READ_ONLY"
    assert result["source_packet_router_schema"] == "AIOS_SELF_DEVELOPMENT_PACKET_ROUTER_RESULT.v1"
    assert result["safety"]["status"] == "PASS"


def test_safe_read_only_validators_are_classified_correctly() -> None:
    result = build_router_result(_payload())
    validators = _by_path(result["validator_catalog"])

    assert validators[
        "automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1"
    ]["classification"] == "SAFE_READ_ONLY_VALIDATOR"
    assert validators[
        "automation/orchestration/validators/Test-ApprovalInboxIntegrity.DRY_RUN.ps1"
    ]["safe_to_use_as_evidence"] is True


def test_safe_evidence_surfaces_are_classified_correctly() -> None:
    result = build_router_result(_payload())
    evidence = _by_path(result["evidence_sources"])

    assert evidence[
        "automation/orchestration/campaign_registry/Get-AiOsCampaignNoReadyStageDiscovery.DRY_RUN.ps1"
    ]["classification"] == "SAFE_READ_ONLY_EVIDENCE"
    assert evidence[
        "automation/orchestration/relay_bus/Get-AiOsRelayBusState.DRY_RUN.ps1"
    ]["classification"] == "SAFE_READ_ONLY_EVIDENCE"


def test_recommendation_command_surfaces_are_sanitized() -> None:
    result = build_router_result(_payload())
    evidence = _by_path(result["evidence_sources"])
    command = result["safety"]["action_recommendation_command"]

    assert evidence[
        "automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1"
    ]["classification"] == "SAFE_WITH_SANITIZATION"
    assert command["safe_to_surface"] is False
    assert "git add" not in command["display_text"].lower()
    assert "git commit" not in command["display_text"].lower()


def test_commit_package_preview_is_protected_action_preview_only() -> None:
    result = build_router_result(_payload())
    validators = _by_path(result["validator_catalog"])

    assert validators[
        "automation/orchestration/validators/New-CommitPackagePreview.DRY_RUN.ps1"
    ]["classification"] == "PROTECTED_ACTION_PREVIEW_ONLY"


def test_exact_commit_helper_is_blocked_as_write_protected_surface() -> None:
    classified = classify_surface("automation/orchestration/commit_packages/Invoke-AiOsExactCommitPackage.ps1")

    assert classified["classification"] == "WRITE_OR_MUTATION_SURFACE_BLOCKED"
    assert classified["blocked"] is True


def test_relay_writer_is_blocked() -> None:
    classified = classify_surface("automation/orchestration/relay_bus/New-AiOsRelayMessage.DRY_RUN.ps1")

    assert classified["classification"] == "WRITE_OR_MUTATION_SURFACE_BLOCKED"
    assert classified["blocked"] is True


def test_lock_claim_and_release_are_blocked() -> None:
    for path in (
        "automation/orchestration/locks/Claim-AiOsFileLock.DRY_RUN.ps1",
        "automation/orchestration/locks/Release-AiOsFileLock.DRY_RUN.ps1",
    ):
        classified = classify_surface(path)
        assert classified["classification"] == "WRITE_OR_MUTATION_SURFACE_BLOCKED"
        assert classified["blocked"] is True


def test_runtime_worker_scheduler_daemon_surfaces_are_blocked() -> None:
    paths = [
        "automation/orchestration/runtime/Start-AiOsPersistentRuntimeSupervisor.ps1",
        "automation/orchestration/runtime/Invoke-AiOsRuntimeSelfRoute.ps1",
        "automation/orchestration/workers/daemon/Start-AiOsWorkerDaemon.DRY_RUN.ps1",
        "automation/orchestration/workers/launcher/Open-AiOsWorkerWindow.DRY_RUN.ps1",
    ]

    for path in paths:
        classified = classify_surface(path)
        assert classified["classification"] == "RUNTIME_OR_WORKER_BLOCKED"
        assert classified["blocked"] is True


def test_secret_env_paths_are_blocked() -> None:
    for path in (".env", ".env.local", "secrets/api_key.txt"):
        classified = classify_surface(path)
        assert classified["classification"] == "SECRET_OR_ENV_BLOCKED"
        assert classified["blocked"] is True


def test_broker_oanda_webhook_order_live_trading_paths_are_blocked() -> None:
    paths = [
        "automation/trading/broker/live_order.py",
        "automation/trading/oanda/client.py",
        "automation/trading/webhooks/order_route.ps1",
        "automation/trading/live-trading/runner.ps1",
    ]

    for path in paths:
        classified = classify_surface(path)
        assert classified["classification"] == "BROKER_OR_LIVE_TRADING_BLOCKED"
        assert classified["blocked"] is True


def test_recommended_chains_include_planning_apply_pre_commit_and_post_commit() -> None:
    result = build_router_result(_payload())
    chain_ids = {item["chain_id"] for item in result["recommended_chains"]}

    assert "planning_review_chain" in chain_ids
    assert "apply_packet_chain" in chain_ids
    assert "pre_commit_chain" in chain_ids
    assert "post_commit_chain" in chain_ids


def test_no_write_proof_blocks_forbidden_delta() -> None:
    result = build_router_result(
        _payload(
            no_write_proof={
                "changed": True,
                "git_state_changed": False,
                "forbidden_surface_changed": True,
            }
        )
    )

    assert result["safety"]["status"] == "BLOCKED_BY_WRITE_SURFACE_RISK"
    assert "WRITE_SURFACE_RISK" in result["stop_conditions"]


def test_command_sanitizer_blocks_protected_commands() -> None:
    command = sanitize_command_field("powershell -File helper.ps1 -Mode APPLY; git push")

    assert command["safe_to_surface"] is False
    assert "git push" not in command["display_text"].lower()
