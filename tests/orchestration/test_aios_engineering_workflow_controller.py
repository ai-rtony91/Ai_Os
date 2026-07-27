from __future__ import annotations

from automation.orchestration.aios_engineering_workflow_controller import (
    build_engineering_workflow_report,
)


VALIDATOR = "python -m pytest tests/unit.py -q"


def _repo(*_args, **_kwargs):
    return {"branch": "feature/test", "is_clean": True, "safe_for_apply": True}


def _candidate():
    return {
        "packet_id": "PKT-TEST-001",
        "title": "Bounded test packet",
        "lane": "orchestration",
        "priority": "high",
        "milestone_value": 10,
        "risk_level": "low",
        "status": "ready",
        "required_files": ["automation/orchestration/example.py"],
        "blocked_files": [],
        "required_approvals": [],
        "validators": [VALIDATOR],
        "dependencies": [],
        "conflicts": [],
        "safety_flags": [],
    }


def test_composes_existing_components_into_owner_merge_review():
    report = build_engineering_workflow_report(
        [_candidate()],
        pr_evidence={
            "number": 42,
            "headRefName": "feature/test",
            "checks": [{"name": "validate", "conclusion": "SUCCESS"}],
        },
        validator_results={VALIDATOR: "PASS"},
        repo_state_collector=_repo,
    )

    assert report["selected_packet"]["packet_id"] == "PKT-TEST-001"
    assert report["validator_evidence"]["status"] == "PASS"
    assert report["pr_ci_state"]["merge_allowed"] is True
    assert report["next_task"] == "READY_FOR_OWNER_MERGE_REVIEW"
    assert report["owner_intervention_required"] is True
    assert not any(report["protected_actions"].values())


def test_missing_validator_evidence_routes_to_validator_work():
    report = build_engineering_workflow_report(
        [_candidate()], validator_results={}, repo_state_collector=_repo
    )
    assert report["validator_evidence"]["missing"] == [VALIDATOR]
    assert report["next_task"] == "RUN_OR_REPAIR_SELECTED_PACKET_VALIDATORS"
    assert report["owner_intervention_required"] is False


def test_dirty_repo_blocks_before_queue_or_pr_action():
    def dirty(*_args, **_kwargs):
        return {"branch": "feature/test", "is_clean": False, "safe_for_apply": False}

    report = build_engineering_workflow_report(
        [_candidate()], validator_results={VALIDATOR: "PASS"}, repo_state_collector=dirty
    )
    assert report["next_task"] == "REPAIR_REPOSITORY_STATE"
    assert report["workflow_status"] == "ACTION_REQUIRED"


def test_empty_input_reuses_adapter_canonical_fallback_candidate():
    report = build_engineering_workflow_report([], repo_state_collector=_repo)
    assert report["selected_packet"]["packet_id"] == (
        "PKT-AIOS-SELFROUTE-CANDIDATE-EVIDENCE-INTEGRATION"
    )
    assert report["next_task"] == "RUN_OR_REPAIR_SELECTED_PACKET_VALIDATORS"


def test_pr_absence_routes_to_single_pr_preparation():
    report = build_engineering_workflow_report(
        [_candidate()], validator_results={VALIDATOR: "PASS"}, repo_state_collector=_repo
    )
    assert report["next_task"] == "PREPARE_ONE_PULL_REQUEST"
    assert report["owner_intervention_required"] is True

def test_report_identifies_anchor_blocker_without_claiming_completion():
    report = build_engineering_workflow_report([_candidate()], repo_state_collector=_repo, anchor_evidence={})
    assert report["primary_anchor"]["anchor_complete"] is False
    assert report["next_verified_anchor_blocker"] == "PROVIDE_GENUINE_SANITIZED_REPRODUCIBLE_EVIDENCE"
