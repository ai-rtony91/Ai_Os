import sys

sys.dont_write_bytecode = True

from automation.orchestration.self_audit.aios_self_audit_loop import (
    SCHEMA,
    build_self_audit_result,
    rank_candidate_packets,
    sanitize_recommendation,
)


def _payload(**overrides):
    payload = {
        "generated_utc": "2026-06-13T00:00:00Z",
        "repo_state": {
            "branch": "main",
            "expected_branch": "main",
            "branch_matches_expected": True,
            "dirty": False,
            "dirty_allowed_for_self_validation": False,
        },
        "authority_context": {
            "all_required_loaded": True,
            "files": [],
        },
        "evidence": {
            "no_ready_stage_discovery": {
                "overall_readiness": "NO_READY_STAGE",
                "no_ready_stage_detected": True,
                "no_ready_stage_classification": "COMPLETE_IDLE",
                "idle_allowed": True,
                "next_stage_planning_required": False,
                "registry_inconsistency_detected": False,
                "no_ready_stage_classification_reason": "No READY stage is available.",
            },
            "campaign_next_task": {
                "overall_readiness": "NO_READY_STAGE",
                "next_packet_candidate": None,
            },
            "action_recommendation": {
                "mode": "READ_ONLY",
                "packet_status": "no_active_packet",
                "recommended_command": "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/campaign_registry/Get-AiOsCampaignNoReadyStageDiscovery.DRY_RUN.ps1 -OutputJson",
            },
        },
        "surface_inventory": {
            "profile": "Core",
        },
        "blocked_surfaces": [],
        "safe_surfaces_used": [
            "automation/orchestration/campaign_registry/Get-AiOsCampaignNoReadyStageDiscovery.DRY_RUN.ps1",
        ],
        "no_write_proof": {
            "changed": False,
            "git_state_changed": False,
            "forbidden_surface_changed": False,
        },
        "max_candidate_packets": 5,
        "candidate_packet_ids": [
            "AIOS-SELF-DEVELOPMENT-PACKET-ROUTER-DRYRUN-V1",
            "AIOS-VALIDATOR-EVIDENCE-ROUTER-DRYRUN-V1",
            "AIOS-DAY-NIGHT-SUPERVISOR-READINESS-DRYRUN-V1",
            "AIOS-DASHBOARD-DATA-CONTRACT-REVIEW-DRYRUN-V1",
            "AIOS-DASHBOARD-LAYER-TAXONOMY-DOCS-APPLY-V1",
        ],
    }
    payload.update(overrides)
    return payload


def test_python_logic_emits_self_audit_schema() -> None:
    result = build_self_audit_result(_payload())

    assert result["schema"] == SCHEMA
    assert result["mode"] == "DRY_RUN_READ_ONLY"
    assert result["safety"]["status"] == "PASS"


def test_python_logic_ranks_self_development_dry_run_before_dashboard_ui() -> None:
    ranked = rank_candidate_packets(
        [
            "AIOS-DASHBOARD-DATA-CONTRACT-REVIEW-DRYRUN-V1",
            "AIOS-SELF-DEVELOPMENT-PACKET-ROUTER-DRYRUN-V1",
        ]
    )

    assert ranked[0]["packet_id"] == "AIOS-SELF-DEVELOPMENT-PACKET-ROUTER-DRYRUN-V1"
    assert ranked[0]["blocked"] is False


def test_protected_live_write_candidates_are_blocked() -> None:
    ranked = rank_candidate_packets(
        [
            "AIOS-BROKER-LIVE-ORDER-APPLY-V1",
            "AIOS-DASHBOARD-LAYER-TAXONOMY-DOCS-APPLY-V1",
            "AIOS-VALIDATOR-EVIDENCE-ROUTER-DRYRUN-V1",
        ]
    )
    by_id = {item["packet_id"]: item for item in ranked}

    assert by_id["AIOS-BROKER-LIVE-ORDER-APPLY-V1"]["blocked"] is True
    assert by_id["AIOS-DASHBOARD-LAYER-TAXONOMY-DOCS-APPLY-V1"]["blocked"] is True
    assert by_id["AIOS-VALIDATOR-EVIDENCE-ROUTER-DRYRUN-V1"]["blocked"] is False


def test_complete_idle_is_represented_correctly() -> None:
    result = build_self_audit_result(_payload())

    assert result["complete_idle_state"]["classification"] == "COMPLETE_IDLE"
    assert result["complete_idle_state"]["idle_allowed"] is True
    assert any(item["classification"] == "COMPLETE_IDLE" for item in result["findings"])


def test_recommended_commands_are_sanitized_when_protected() -> None:
    sanitized = sanitize_recommendation("git add -- file && git commit -m unsafe")

    assert sanitized["safe_to_surface"] is False
    assert "git add" not in sanitized["display_text"].lower()
    assert "git commit" not in sanitized["display_text"].lower()


def test_no_write_proof_blocks_on_forbidden_delta() -> None:
    result = build_self_audit_result(
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
