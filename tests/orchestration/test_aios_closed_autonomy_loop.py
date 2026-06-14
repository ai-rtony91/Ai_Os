from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE = REPO_ROOT / "automation" / "orchestration" / "aios_closed_autonomy_loop.py"
SCHEMA = REPO_ROOT / "schemas" / "orchestration" / "aios_closed_autonomy_loop.schema.json"
FIXED_NOW = "2026-06-14T12:00:00Z"
LATEST_REPORT = Path("Reports") / "sandbox" / "closed_autonomy_loop" / "AIOS_CLOSED_AUTONOMY_LOOP_LATEST.json"


def _load():
    spec = importlib.util.spec_from_file_location("aios_closed_autonomy_loop", MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_json(root: Path, rel_path: str, payload: dict) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _governor_decision(
    *,
    task_id: str = "safe_dry_run",
    category: str = "QUEUE_CONSOLIDATION",
    lane: str = "DRY_RUN",
    scope_mode: str = "DRY_RUN",
    blocked: bool = False,
    blocked_reason: str | None = None,
    title: str = "Inspect queue evidence before worker routing.",
    allowed_paths: list[str] | None = None,
) -> dict:
    return {
        "schema_version": "1.0",
        "system": "AI_OS",
        "component": "autonomy_decision_governor",
        "mode": "APPLY_SAFE_DECISION_OUTPUT",
        "decision_id": "AIOS-ADG-fixture",
        "generated_at_utc": FIXED_NOW,
        "next_highest_value_task": title,
        "decision_category": category,
        "why_this_task": ["fixture"],
        "risk_level": "medium" if not blocked else "blocked",
        "allowed_lane": lane,
        "required_validators": ["Fixture validator"],
        "stop_conditions": ["Stop after fixture validation."],
        "blocked": blocked,
        "blocked_reason": blocked_reason,
        "evidence_inputs": [{"path": "fixture.json", "status": "present", "summary": "fixture"}],
        "safety_boundaries": {
            "live_trading": "blocked",
            "broker_execution": "blocked",
            "credential_use": "blocked",
            "unapproved_mutation": "blocked",
        },
        "confidence": 0.8,
        "recommended_packet_scope": {
            "packet_id_suggestion": f"AIOS-{task_id.upper()}",
            "mode": scope_mode,
            "lane": lane,
            "files_allowed": allowed_paths or ["automation/orchestration/"],
            "files_forbidden": ["AGENTS.md", "README.md", "secrets/", ".env"],
        },
        "ranked_candidates": [
            {
                "task_id": task_id,
                "title": title,
                "category": category,
                "value_score": 1,
                "urgency_score": 1,
                "risk_score": 1,
                "blocker_score": 1,
                "validation_score": 1,
                "autonomy_leverage_score": 1,
                "total_score": 6,
                "reason": "fixture",
                "required_validator": "Fixture validator",
                "allowed_lane": lane,
                "stop_condition": "Stop after fixture validation.",
                "blocked": blocked,
            }
        ],
        "selected_candidate_id": task_id,
        "selection_reason": "fixture",
    }


def _repo_state(clean: bool = True) -> dict:
    return {
        "schema_version": "1.0",
        "system": "AI_OS",
        "component": "repo_state_evidence",
        "generated_at_utc": FIXED_NOW,
        "repo_root": "fixture",
        "branch": "main",
        "git_available": True,
        "inside_worktree": True,
        "is_clean": clean,
        "status_short": ["## main...origin/main"] if clean else ["## main...origin/main", " M file.py"],
        "tracked_dirty_files": [] if clean else ["file.py"],
        "untracked_files": [],
        "staged_files": [],
        "ahead_behind": {"ahead": None, "behind": None, "raw": "## main...origin/main"},
        "safe_for_apply": clean,
        "blocked_reason": None if clean else "dirty_working_tree",
        "evidence_quality": "strong",
    }


def _inputs(decision: dict, *, repo_state: dict | None = None, validator_router: dict | None = None, approval_gate: dict | None = None) -> dict:
    payloads = {
        "governor_decision": decision,
        "repo_state": repo_state or _repo_state(True),
        "validator_router": validator_router,
        "approval_gate": approval_gate,
        "approval_inbox": None,
        "queue_view": None,
        "blocker_stack": None,
        "self_build_cycle": None,
        "autonomy_status": None,
        "runtime_state": None,
    }
    return {
        "repo_root": "fixture",
        "inputs": [
            {"name": "repo_state", "path": "Reports/repo_state/AIOS_REPO_STATE_LATEST.json", "status": "present", "summary": "fixture"},
            {
                "name": "governor_decision_output",
                "path": "Reports/autonomy_decision_governor/AIOS_AUTONOMY_DECISION_GOVERNOR_LATEST.json",
                "status": "present",
                "summary": "fixture",
            },
        ],
        "payloads": payloads,
    }


def _required_top_level() -> set[str]:
    return {
        "schema_version",
        "system",
        "component",
        "mode",
        "loop_id",
        "generated_at_utc",
        "loop_phase_status",
        "inputs",
        "governor_decision",
        "proposed_cycle_action",
        "gate_result",
        "dispatch_recommendation",
        "safety_boundaries",
        "next_loop_requirement",
    }


def _seed_evidence(root: Path, decision: dict | None = None, repo_state: dict | None = None) -> None:
    _write_json(root, "Reports/repo_state/AIOS_REPO_STATE_LATEST.json", repo_state or _repo_state(True))
    _write_json(
        root,
        "Reports/autonomy_decision_governor/AIOS_AUTONOMY_DECISION_GOVERNOR_LATEST.json",
        decision or _governor_decision(),
    )
    _write_json(root, "Reports/validator_evidence_router/AIOS_VALIDATOR_EVIDENCE_ROUTER_LATEST.json", {"status": "pass"})


def _assert_schema_valid(report: dict) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert set(schema["required"]) == _required_top_level()
    assert _required_top_level().issubset(report.keys())
    assert report["schema_version"] == "1.0"
    assert report["system"] == "AI_OS"
    assert report["component"] == "closed_autonomy_loop"
    assert report["mode"] == "ONE_CYCLE_RECOMMENDATION_ONLY"
    assert report["gate_result"]["status"] in schema["properties"]["gate_result"]["properties"]["status"]["enum"]
    assert report["dispatch_recommendation"]["dispatch_authorized"] is False
    assert report["dispatch_recommendation"]["queue_mutation_authorized"] is False
    assert report["loop_phase_status"]["stop"] == "complete"
    for key in (
        "continuous_loop",
        "worker_dispatch",
        "queue_mutation",
        "live_trading",
        "broker_execution",
        "credential_use",
        "unapproved_mutation",
    ):
        assert key in report["safety_boundaries"]


def test_closed_loop_report_contains_all_required_top_level_fields(tmp_path: Path) -> None:
    m = _load()
    _seed_evidence(tmp_path)

    report = m.build_closed_loop_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert _required_top_level().issubset(report.keys())
    _assert_schema_valid(report)


def test_missing_evidence_produces_conservative_blocked_or_partial_state(tmp_path: Path) -> None:
    m = _load()

    report = m.build_closed_loop_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["loop_phase_status"]["observe"] in {"partial", "blocked"}
    assert report["gate_result"]["status"] in {
        "blocked",
        "requires_cleanup",
        "requires_validator_repair",
        "requires_human_approval",
    }
    assert report["dispatch_recommendation"]["dispatch_authorized"] is False
    assert report["dispatch_recommendation"]["queue_mutation_authorized"] is False


def test_dirty_repo_governor_decision_produces_cleanup_or_blocked_gate() -> None:
    m = _load()
    decision = _governor_decision(
        task_id="repo_status_recon",
        category="STATUS_RECON",
        lane="READ_ONLY",
        blocked=True,
        blocked_reason="dirty_working_tree",
    )
    state = m.build_loop_state(_inputs(decision, repo_state=_repo_state(False)))

    gate = m.evaluate_loop_gates(state)

    assert gate["status"] in {"requires_cleanup", "blocked"}
    assert gate["safe_to_dispatch"] is False


def test_validator_failure_routes_to_requires_validator_repair() -> None:
    m = _load()
    state = m.build_loop_state(_inputs(_governor_decision(), validator_router={"status": "failed"}))

    gate = m.evaluate_loop_gates(state)

    assert gate["status"] == "requires_validator_repair"
    assert gate["safe_to_dispatch"] is False


def test_approval_missing_apply_routes_to_human_or_blocked() -> None:
    m = _load()
    decision = _governor_decision(
        task_id="apply_candidate",
        category="SELF_BUILD_LOOP_WIRING",
        lane="APPLY_CODE_SAFE",
        scope_mode="APPLY",
    )
    state = m.build_loop_state(_inputs(decision, approval_gate=None))

    gate = m.evaluate_loop_gates(state)

    assert gate["status"] in {"requires_human_approval", "blocked"}
    assert gate["safe_to_dispatch"] is False


def test_safe_dry_run_recommendation_remains_recommendation_only() -> None:
    m = _load()
    state = m.build_loop_state(_inputs(_governor_decision()))
    gate = m.evaluate_loop_gates(state)
    state["gate_result"] = gate

    recommendation = m.recommend_next_cycle_action(state)

    assert gate["status"] == "ready_for_dry_run"
    assert recommendation["dispatch_authorized"] is False
    assert recommendation["queue_mutation_authorized"] is False
    assert recommendation["recommended_next_packet_type"] == "DRY_RUN_PACKET"


def test_live_trading_broker_credential_scope_is_blocked() -> None:
    m = _load()
    decision = _governor_decision(
        task_id="unsafe_scope",
        title="Add broker execution with credentials.",
        allowed_paths=["apps/trading_lab/live_trading/broker_credentials.py"],
    )
    state = m.build_loop_state(_inputs(decision))

    gate = m.evaluate_loop_gates(state)

    assert gate["status"] == "blocked"
    assert "blocked" in gate["reason"].lower()


def test_one_cycle_stop_is_always_complete(tmp_path: Path) -> None:
    m = _load()
    _seed_evidence(tmp_path)

    report = m.build_closed_loop_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["mode"] == "ONE_CYCLE_RECOMMENDATION_ONLY"
    assert report["loop_phase_status"]["stop"] == "complete"
    assert report["safety_boundaries"]["continuous_loop"] == "blocked"
    assert report["safety_boundaries"]["queue_mutation"] == "blocked"


def test_schema_validation_passes(tmp_path: Path) -> None:
    m = _load()
    _seed_evidence(tmp_path)

    report = m.build_closed_loop_report(tmp_path, generated_at_utc=FIXED_NOW)

    _assert_schema_valid(report)


def test_materializer_writes_latest_report_file(tmp_path: Path) -> None:
    m = _load()
    _seed_evidence(tmp_path)

    result = m.materialize_closed_loop_report(tmp_path, generated_at_utc=FIXED_NOW)
    output_path = tmp_path / LATEST_REPORT
    written = json.loads(output_path.read_text(encoding="utf-8"))

    assert result["output_path"] == LATEST_REPORT.as_posix()
    assert output_path.is_file()
    assert written["component"] == "closed_autonomy_loop"
    assert written["generated_at_utc"] == FIXED_NOW
    assert written["dispatch_recommendation"]["dispatch_authorized"] is False
    assert written["dispatch_recommendation"]["queue_mutation_authorized"] is False
    assert written["loop_phase_status"]["stop"] == "complete"
    _assert_schema_valid(written)


def test_output_is_deterministic_except_timestamp_and_loop_id(tmp_path: Path) -> None:
    m = _load()
    _seed_evidence(tmp_path)

    first = m.build_closed_loop_report(tmp_path, generated_at_utc="2026-06-14T12:00:00Z")
    second = m.build_closed_loop_report(tmp_path, generated_at_utc="2026-06-14T12:01:00Z")
    for report in (first, second):
        report.pop("generated_at_utc")
        report.pop("loop_id")

    assert first == second
