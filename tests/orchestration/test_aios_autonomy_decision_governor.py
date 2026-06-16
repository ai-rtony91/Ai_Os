from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE = REPO_ROOT / "automation" / "orchestration" / "aios_autonomy_decision_governor.py"
SCHEMA = REPO_ROOT / "schemas" / "orchestration" / "aios_autonomy_decision_governor.schema.json"
FIXED_NOW = "2026-06-14T12:00:00Z"


def _load():
    spec = importlib.util.spec_from_file_location("aios_autonomy_decision_governor", MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _evidence(**signals):
    base = {
        "repo_state": "clean",
        "safe_status_artifact_present": True,
        "validator_status": "pass",
        "approval_required": False,
        "approval_status": "approved",
        "queue_present": True,
        "queue_backlog_present": False,
        "queue_item_count": 0,
        "queue_blocked_count": 0,
        "self_build_status_present": True,
        "self_build_pending": False,
        "autonomy_status_present": True,
        "decision_output_present": True,
        "trading_lab_paper_only_confirmed": False,
        "unsafe_scope_detected": False,
        "active_blockers": [],
        "active_blocker_count": 0,
    }
    base.update(signals)
    return {
        "signals": base,
        "evidence_inputs": [
            {"path": "fixture/status.json", "status": "present", "summary": "fixture evidence"}
        ],
    }


def _required_fields():
    return {
        "schema_version",
        "system",
        "component",
        "mode",
        "decision_id",
        "generated_at_utc",
        "next_highest_value_task",
        "decision_category",
        "why_this_task",
        "risk_level",
        "allowed_lane",
        "required_validators",
        "stop_conditions",
        "blocked",
        "blocked_reason",
        "evidence_inputs",
        "safety_boundaries",
        "confidence",
        "recommended_packet_scope",
        "ranked_candidates",
        "selected_candidate_id",
        "selection_reason",
    }


def _assert_schema_valid(decision: dict) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert set(schema["required"]) == _required_fields()
    assert _required_fields().issubset(decision.keys())
    assert decision["schema_version"] == "1.0"
    assert decision["system"] == "AI_OS"
    assert decision["component"] == "autonomy_decision_governor"
    assert decision["mode"] == "APPLY_SAFE_DECISION_OUTPUT"
    assert decision["decision_category"] in schema["properties"]["decision_category"]["enum"]
    assert decision["risk_level"] in schema["properties"]["risk_level"]["enum"]
    assert decision["allowed_lane"] in schema["properties"]["allowed_lane"]["enum"]
    assert isinstance(decision["why_this_task"], list) and decision["why_this_task"]
    assert isinstance(decision["required_validators"], list) and decision["required_validators"]
    assert isinstance(decision["stop_conditions"], list) and decision["stop_conditions"]
    assert isinstance(decision["blocked"], bool)
    assert decision["blocked_reason"] is None or isinstance(decision["blocked_reason"], str)
    assert 0 <= decision["confidence"] <= 1
    for key in ("live_trading", "broker_execution", "credential_use", "unapproved_mutation"):
        assert decision["safety_boundaries"][key] == "blocked"
    for item in decision["evidence_inputs"]:
        assert set(item) == {"path", "status", "summary"}
        assert item["status"] in {"present", "missing", "unknown"}
    scope = decision["recommended_packet_scope"]
    assert scope["mode"] in {"DRY_RUN", "APPLY"}
    assert isinstance(scope["files_allowed"], list)
    assert isinstance(scope["files_forbidden"], list)
    assert isinstance(decision["ranked_candidates"], list) and decision["ranked_candidates"]
    candidate_ids = {candidate["task_id"] for candidate in decision["ranked_candidates"]}
    assert decision["selected_candidate_id"] in candidate_ids
    assert isinstance(decision["selection_reason"], str) and decision["selection_reason"]
    candidate_required = set(schema["properties"]["ranked_candidates"]["items"]["required"])
    for candidate in decision["ranked_candidates"]:
        assert set(candidate) == candidate_required
        assert candidate["category"] in schema["properties"]["ranked_candidates"]["items"]["properties"]["category"]["enum"]
        assert candidate["allowed_lane"] in schema["properties"]["ranked_candidates"]["items"]["properties"]["allowed_lane"]["enum"]
        assert isinstance(candidate["blocked"], bool)
        for score_key in (
            "value_score",
            "urgency_score",
            "risk_score",
            "blocker_score",
            "validation_score",
            "autonomy_leverage_score",
            "total_score",
        ):
            assert isinstance(candidate[score_key], int)
            assert candidate[score_key] >= 0


def test_governor_emits_all_required_fields() -> None:
    m = _load()
    decision = m.choose_next_decision(_evidence(decision_output_present=False), generated_at_utc=FIXED_NOW)

    assert _required_fields().issubset(decision.keys())
    _assert_schema_valid(decision)


def test_missing_evidence_produces_conservative_status_recon() -> None:
    m = _load()
    decision = m.choose_next_decision({"signals": {}, "evidence_inputs": []}, generated_at_utc=FIXED_NOW)

    assert decision["decision_category"] == "STATUS_RECON"
    assert decision["blocked"] is True
    assert decision["allowed_lane"] == "READ_ONLY"
    assert decision["blocked_reason"] == "repo_state_unknown"


def test_governor_consumes_strong_clean_repo_state_evidence(tmp_path: Path) -> None:
    m = _load()
    report_dir = tmp_path / "Reports" / "repo_state"
    report_dir.mkdir(parents=True)
    (report_dir / "AIOS_REPO_STATE_LATEST.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "system": "AI_OS",
                "component": "repo_state_evidence",
                "generated_at_utc": FIXED_NOW,
                "repo_root": str(tmp_path),
                "branch": "main",
                "git_available": True,
                "inside_worktree": True,
                "is_clean": True,
                "status_short": ["## main...origin/main"],
                "tracked_dirty_files": [],
                "untracked_files": [],
                "staged_files": [],
                "ahead_behind": {"ahead": None, "behind": None, "raw": "## main...origin/main"},
                "safe_for_apply": True,
                "blocked_reason": None,
                "evidence_quality": "strong",
            }
        ),
        encoding="utf-8",
    )

    evidence = m.discover_evidence(tmp_path)
    decision = m.choose_next_decision(evidence, generated_at_utc=FIXED_NOW)

    assert decision["blocked_reason"] != "repo_state_unknown"
    assert decision["decision_category"] == "VALIDATOR_REPAIR"


def test_governor_consumes_dirty_repo_state_evidence_and_blocks_apply(tmp_path: Path) -> None:
    m = _load()
    report_dir = tmp_path / "Reports" / "repo_state"
    report_dir.mkdir(parents=True)
    (report_dir / "AIOS_REPO_STATE_LATEST.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "system": "AI_OS",
                "component": "repo_state_evidence",
                "generated_at_utc": FIXED_NOW,
                "repo_root": str(tmp_path),
                "branch": "main",
                "git_available": True,
                "inside_worktree": True,
                "is_clean": False,
                "status_short": ["## main...origin/main", " M file.py"],
                "tracked_dirty_files": ["file.py"],
                "untracked_files": [],
                "staged_files": [],
                "ahead_behind": {"ahead": None, "behind": None, "raw": "## main...origin/main"},
                "safe_for_apply": False,
                "blocked_reason": "dirty_working_tree",
                "evidence_quality": "strong",
            }
        ),
        encoding="utf-8",
    )

    evidence = m.discover_evidence(tmp_path)
    decision = m.choose_next_decision(evidence, generated_at_utc=FIXED_NOW)

    assert decision["decision_category"] == "STATUS_RECON"
    assert decision["blocked"] is True
    assert decision["blocked_reason"] == "dirty_working_tree"


def test_live_trading_or_broker_keywords_force_blocked_decision() -> None:
    m = _load()
    decision = m.choose_next_decision(
        _evidence(unsafe_scope_detected=True, requested_scope="add broker execution"),
        generated_at_utc=FIXED_NOW,
    )

    assert decision["decision_category"] == "BLOCKED_STOP_AND_REPORT"
    assert decision["risk_level"] == "blocked"
    assert decision["allowed_lane"] == "BLOCKED"
    assert decision["blocked_reason"] == "unsafe_scope_detected"


def test_paper_only_trading_lab_evidence_can_recommend_paper_improvement() -> None:
    m = _load()
    decision = m.choose_next_decision(
        _evidence(trading_lab_paper_only_confirmed=True, decision_output_present=True),
        generated_at_utc=FIXED_NOW,
    )

    assert decision["decision_category"] == "TRADING_LAB_PAPER_ONLY_IMPROVEMENT"
    assert decision["risk_level"] == "low"
    assert decision["blocked"] is False
    assert "paper-only" in " ".join(decision["why_this_task"]).lower()


def test_validator_missing_recommends_validator_repair() -> None:
    m = _load()
    decision = m.choose_next_decision(
        _evidence(validator_status="missing"),
        generated_at_utc=FIXED_NOW,
    )

    assert decision["decision_category"] == "VALIDATOR_REPAIR"
    assert decision["allowed_lane"] == "DRY_RUN"
    assert decision["blocked"] is False


def test_validator_failure_recommends_validator_repair() -> None:
    m = _load()
    decision = m.choose_next_decision(
        _evidence(validator_status="failed"),
        generated_at_utc=FIXED_NOW,
    )

    assert decision["decision_category"] == "VALIDATOR_REPAIR"
    assert decision["allowed_lane"] == "DRY_RUN"
    assert decision["blocked"] is False


def test_queue_backlog_recommends_queue_consolidation() -> None:
    m = _load()
    decision = m.choose_next_decision(
        _evidence(queue_backlog_present=True, queue_item_count=3),
        generated_at_utc=FIXED_NOW,
    )

    assert decision["decision_category"] == "QUEUE_CONSOLIDATION"
    assert decision["allowed_lane"] == "DRY_RUN"
    assert decision["blocked"] is False
    assert "3 pending item" in " ".join(decision["why_this_task"])


def test_approval_missing_apply_evidence_blocks_apply() -> None:
    m = _load()
    decision = m.choose_next_decision(
        _evidence(approval_required=True, approval_status="pending_review"),
        generated_at_utc=FIXED_NOW,
    )

    assert decision["decision_category"] == "APPROVAL_GATE_REPAIR"
    assert decision["allowed_lane"] == "BLOCKED"
    assert decision["blocked"] is True
    assert decision["blocked_reason"] == "apply_approval_missing"


def test_self_build_pending_recommends_self_build_evidence_repair() -> None:
    m = _load()
    decision = m.choose_next_decision(
        _evidence(self_build_pending=True),
        generated_at_utc=FIXED_NOW,
    )

    assert decision["decision_category"] == "SELF_BUILD_LOOP_WIRING"
    assert decision["allowed_lane"] == "DRY_RUN"
    assert decision["blocked"] is False


def test_active_blocker_evidence_blocks_next_action_selection() -> None:
    m = _load()
    decision = m.choose_next_decision(
        _evidence(active_blockers=["runtime queue blocker"], active_blocker_count=1),
        generated_at_utc=FIXED_NOW,
    )

    assert decision["decision_category"] == "BLOCKED_STOP_AND_REPORT"
    assert decision["allowed_lane"] == "BLOCKED"
    assert decision["blocked"] is True
    assert decision["blocked_reason"] == "active_blockers_present"


def test_validator_failure_ranks_above_queue_work() -> None:
    m = _load()
    candidates = m.rank_candidates(
        _evidence(validator_status="failed", queue_backlog_present=True, queue_item_count=4)
    )

    assert candidates[0]["task_id"] == "validator_evidence_repair"
    assert candidates[0]["category"] == "VALIDATOR_REPAIR"
    assert candidates[0]["total_score"] > next(
        candidate["total_score"] for candidate in candidates if candidate["task_id"] == "runtime_queue_backlog_consolidation"
    )


def test_dirty_repo_ranks_status_cleanup_above_apply_work() -> None:
    m = _load()
    decision = m.choose_next_decision(
        _evidence(repo_state="dirty", decision_output_present=False),
        generated_at_utc=FIXED_NOW,
    )

    assert decision["selected_candidate_id"] == "repo_status_recon"
    assert decision["decision_category"] == "STATUS_RECON"
    assert decision["allowed_lane"] == "READ_ONLY"
    assert decision["blocked"] is True


def test_safe_generated_dirty_does_not_select_status_recon() -> None:
    m = _load()
    decision = m.choose_next_decision(
        _evidence(
            repo_state="safe_dirty",
            dirty_tree_overall_classification="SAFE_DIRTY",
            dirty_tree_safe_for_dry_run=True,
            dirty_tree_safe_for_apply=False,
            dirty_tree_dirty_count=3,
            validator_status="missing",
        ),
        generated_at_utc=FIXED_NOW,
    )

    assert decision["selected_candidate_id"] != "repo_status_recon"
    assert decision["decision_category"] == "VALIDATOR_REPAIR"
    assert decision["allowed_lane"] == "DRY_RUN"
    assert decision["blocked"] is False


def test_safe_dirty_still_blocks_apply_candidates() -> None:
    m = _load()
    decision = m.choose_next_decision(
        _evidence(
            repo_state="safe_dirty",
            dirty_tree_overall_classification="SAFE_DIRTY",
            dirty_tree_safe_for_dry_run=True,
            dirty_tree_safe_for_apply=False,
            dirty_tree_dirty_count=2,
            decision_output_present=False,
        ),
        generated_at_utc=FIXED_NOW,
    )
    apply_candidate = next(
        candidate for candidate in decision["ranked_candidates"] if candidate["task_id"] == "self_build_decision_output_wiring"
    )

    assert apply_candidate["blocked"] is True
    assert decision["allowed_lane"] != "APPLY_CODE_SAFE"


def test_security_dirty_forces_blocked_decision() -> None:
    m = _load()
    decision = m.choose_next_decision(
        _evidence(
            repo_state="dirty",
            dirty_tree_overall_classification="SECURITY_SOS_DIRTY",
            dirty_tree_sos_required=True,
            dirty_tree_safe_for_dry_run=False,
            dirty_tree_dirty_count=1,
        ),
        generated_at_utc=FIXED_NOW,
    )

    assert decision["selected_candidate_id"] == "dirty_tree_security_sos"
    assert decision["decision_category"] == "BLOCKED_STOP_AND_REPORT"
    assert decision["allowed_lane"] == "BLOCKED"
    assert decision["blocked_reason"] == "security_sos_dirty"


def test_protected_authority_dirty_forces_blocked_decision() -> None:
    m = _load()
    decision = m.choose_next_decision(
        _evidence(
            repo_state="dirty",
            dirty_tree_overall_classification="PROTECTED_AUTHORITY_DIRTY",
            dirty_tree_protected_stop_required=True,
            dirty_tree_safe_for_dry_run=False,
            dirty_tree_dirty_count=1,
        ),
        generated_at_utc=FIXED_NOW,
    )

    assert decision["selected_candidate_id"] == "dirty_tree_protected_authority_stop"
    assert decision["decision_category"] == "BLOCKED_STOP_AND_REPORT"
    assert decision["allowed_lane"] == "BLOCKED"
    assert decision["blocked_reason"] == "protected_authority_dirty"


def test_approval_missing_blocks_apply_even_when_apply_value_is_high() -> None:
    m = _load()
    decision = m.choose_next_decision(
        _evidence(
            approval_required=True,
            approval_status="pending_review",
            decision_output_present=False,
        ),
        generated_at_utc=FIXED_NOW,
    )

    assert decision["selected_candidate_id"] == "approval_gate_repair"
    assert decision["allowed_lane"] == "BLOCKED"
    assert decision["blocked"] is True
    apply_candidate = next(
        candidate for candidate in decision["ranked_candidates"] if candidate["task_id"] == "self_build_decision_output_wiring"
    )
    assert apply_candidate["blocked"] is True


def test_self_build_wiring_ranks_above_dashboard_work() -> None:
    m = _load()
    candidates = m.rank_candidates(
        _evidence(self_build_pending=True, decision_output_present=True)
    )

    assert candidates[0]["task_id"] == "self_build_evidence_repair"
    dashboard = next(candidate for candidate in candidates if candidate["task_id"] == "dashboard_governor_decision_surfacing")
    assert candidates[0]["total_score"] > dashboard["total_score"]


def test_live_trading_candidate_is_blocked() -> None:
    m = _load()
    candidates = m.rank_candidates(_evidence(unsafe_scope_detected=True))

    assert candidates[0]["task_id"] == "safety_stop_unsafe_scope"
    assert candidates[0]["blocked"] is True
    assert candidates[0]["allowed_lane"] == "BLOCKED"


def test_ranking_is_deterministic_for_same_fixture_inputs() -> None:
    m = _load()
    fixture = _evidence(queue_backlog_present=True, queue_item_count=2, decision_output_present=True)

    assert m.rank_candidates(fixture) == m.rank_candidates(fixture)


def test_selected_candidate_matches_highest_safe_score() -> None:
    m = _load()
    decision = m.choose_next_decision(
        _evidence(queue_backlog_present=True, queue_item_count=2, decision_output_present=True),
        generated_at_utc=FIXED_NOW,
    )
    safe_candidates = [candidate for candidate in decision["ranked_candidates"] if not candidate["blocked"]]
    best_safe = max(safe_candidates, key=lambda candidate: candidate["total_score"])

    assert decision["selected_candidate_id"] == best_safe["task_id"]


def test_discovery_reads_queue_and_blocker_artifacts(tmp_path: Path) -> None:
    m = _load()
    repo_state_dir = tmp_path / "Reports" / "repo_state"
    queue_dir = tmp_path / "Reports" / "runtime_queue"
    blocker_dir = tmp_path / "Reports" / "runtime_queue_blocker_stack"
    repo_state_dir.mkdir(parents=True)
    queue_dir.mkdir(parents=True)
    blocker_dir.mkdir(parents=True)
    (repo_state_dir / "AIOS_REPO_STATE_LATEST.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "system": "AI_OS",
                "component": "repo_state_evidence",
                "generated_at_utc": FIXED_NOW,
                "repo_root": str(tmp_path),
                "branch": "main",
                "git_available": True,
                "inside_worktree": True,
                "is_clean": True,
                "status_short": ["## main...origin/main"],
                "tracked_dirty_files": [],
                "untracked_files": [],
                "staged_files": [],
                "ahead_behind": {"ahead": None, "behind": None, "raw": "## main...origin/main"},
                "safe_for_apply": True,
                "blocked_reason": None,
                "evidence_quality": "strong",
            }
        ),
        encoding="utf-8",
    )
    (queue_dir / "runtime_execution_queue_view.json").write_text(
        json.dumps({"item_count": 2, "state_counts": {"BLOCKED": 0}, "items": [{"id": "one"}, {"id": "two"}]}),
        encoding="utf-8",
    )
    (blocker_dir / "runtime_queue_blocker_stack.json").write_text(
        json.dumps({"status": "blocked", "blockers": ["approval evidence missing"]}),
        encoding="utf-8",
    )

    evidence = m.discover_evidence(tmp_path)

    assert evidence["signals"]["queue_backlog_present"] is True
    assert evidence["signals"]["queue_item_count"] == 2
    assert evidence["signals"]["active_blocker_count"] == 1
    assert evidence["signals"]["active_blockers"] == ["approval evidence missing"]


def test_output_json_validates_against_schema(tmp_path: Path) -> None:
    m = _load()
    decision = m.choose_next_decision(_evidence(), generated_at_utc=FIXED_NOW)
    output = m.write_decision_report(tmp_path, decision)
    parsed = json.loads(output.read_text(encoding="utf-8"))

    assert parsed == decision
    _assert_schema_valid(parsed)


def test_decision_is_deterministic_for_same_fixture_inputs() -> None:
    m = _load()
    fixture = _evidence(decision_output_present=False)

    first = m.choose_next_decision(fixture, generated_at_utc=FIXED_NOW)
    second = m.choose_next_decision(fixture, generated_at_utc=FIXED_NOW)

    assert first == second
