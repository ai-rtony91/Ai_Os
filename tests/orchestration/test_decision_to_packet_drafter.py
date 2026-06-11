"""Tests for the decision-to-packet drafter (observe-only)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DRAFTER = (
    REPO_ROOT / "automation" / "orchestration" / "autonomy_router"
    / "aios_decision_to_packet_drafter.py"
)
VALIDATOR = REPO_ROOT / "automation" / "validators" / "aios_governance_validator.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _drafter():
    return _load("aios_decision_to_packet_drafter", DRAFTER)


def _goal(**over):
    base = {
        "goal_id": "goal-gap-evidence-ledger-abc123",
        "objective": "Close autonomy gap: build the evidence ledger reader",
        "urgency": "HIGH",
        "target_area": "automation/orchestration/autonomy_reports",
        "allowed_paths": [],
        "worker_preference": "Claude Code West",
        "protected_action_expected": False,
        "source_gap": "build the evidence ledger reader",
    }
    base.update(over)
    return base


def _strict_request(**over):
    base = {
        "packet_id": "AIOS-STRICT-PACKET-DRAFT-TEST",
        "objective": "Draft a governed Codex packet for the next safe autonomy step",
        "allowed_paths": ["Reports/self_build_drafts/"],
        "forbidden_paths": ["automation/orchestration/work_packets/active/", "broker/", "live_trading/"],
        "approval_authority": "Anthony remains Human Owner.",
        "validator_chain": ["git diff --check"],
        "stop_point": "Stop after draft generation.",
        "mission": "Produce a review-only Codex packet draft.",
        "preflight": ["pwd", "git status --short --branch"],
        "final_report_format": ["SUMMARY:", "STATUS:"],
        "supervisor_identity": "ChatGPT Personal",
        "worker_identity": "Codex East",
    }
    base.update(over)
    return base


def test_scoped_draft_is_ready_and_governance_clean():
    m = _drafter()
    gov = _load("aios_governance_validator", VALIDATOR)
    res = m.build_packet_draft(_goal(), allowed_paths=["automation/orchestration/autonomy_reports/", "tests/orchestration/"])
    assert res["status"] == "DRAFT_READY_FOR_COMPLETENESS_REVIEW"
    assert res["path_status"] == "SCOPED"
    # the rendered draft passes governance SHAPE: no BLOCK and no FAIL errors
    verdict = gov.validate_packet_text(res["draft_text"], "<draft>")
    assert verdict["errors"] == []
    assert verdict["status"] in {"PASS", "WARN"}  # WARN because it correctly flags commit/push/merge need approval


def test_unscoped_draft_flags_path_confirmation():
    m = _drafter()
    res = m.build_packet_draft(_goal(allowed_paths=[]))
    assert res["status"] == "DRAFT_NEEDS_PATH_CONFIRMATION"
    assert res["path_status"] == "NEEDS_PATH_CONFIRMATION"
    assert res["missing"]  # records what is missing
    # derived paths are concrete strings, never unresolved <TOKEN> placeholders
    assert "{" not in res["draft_text"] and "path/to/" not in res["draft_text"]


def test_draft_first_line_and_required_markers():
    m = _drafter()
    res = m.build_packet_draft(_goal(), allowed_paths=["Reports/self_build_drafts/"])
    text = res["draft_text"]
    assert text.splitlines()[0] == "CODEX-ONLY PROMPT"
    for marker in [
        "AI_OS EXECUTION TOKEN",
        "AI_OS BOOTSTRAP REQUIRED",
        "IDENTITY MARKER",
        "SUPERVISOR IDENTITY",
        "PACKET ID",
        "MODE",
        "ZONE",
        "WORKER IDENTITY",
        "LANE",
        "WORKTREE",
        "BRANCH",
        "ALLOWED PATHS",
        "FORBIDDEN PATHS",
        "APPROVAL AUTHORITY",
        "VALIDATOR CHAIN",
        "STOP POINT",
        "MISSION",
        "PREFLIGHT",
        "FINAL REPORT FORMAT",
    ]:
        assert marker in text


def test_full_forbidden_paths_always_attached():
    m = _drafter()
    res = m.build_packet_draft(_goal(), allowed_paths=["Reports/"])
    joined = "\n".join(res["forbidden_paths"])
    for forbidden in ["broker/", "secrets/", "live_trading/", ".github/", "work_packets/"]:
        assert forbidden in joined  # present (possibly as a fuller path)
        assert forbidden in res["draft_text"]


def test_protected_gap_flagged():
    m = _drafter()
    res = m.build_packet_draft(_goal(protected_action_expected=True), allowed_paths=["Reports/"])
    assert res["protected_action_expected"] is True
    assert "PROTECTED ACTION EXPECTED: yes" in res["draft_text"]


def test_malformed_candidate_raises():
    m = _drafter()
    with pytest.raises(ValueError):
        m.build_packet_draft({"no_objective": True})


@pytest.mark.parametrize(
    "field",
    [
        "packet_id",
        "allowed_paths",
        "forbidden_paths",
        "approval_authority",
        "validator_chain",
        "stop_point",
        "mission",
        "preflight",
        "final_report_format",
    ],
)
def test_strict_request_missing_required_fields_fail_closed(field):
    m = _drafter()
    req = _strict_request()
    req[field] = [] if isinstance(req[field], list) else ""
    res = m.draft_codex_packet_from_request(req)
    assert res["status"] == "BLOCKED_MISSING_REQUIRED_INPUTS"
    assert field in res["missing"]
    assert res["draft_text"] == ""
    assert res["observe_only"] is True


def test_strict_request_generates_codex_bound_packet():
    m = _drafter()
    res = m.draft_codex_packet_from_request(_strict_request(), now="2026-01-01T00:00:00Z")
    text = res["draft_text"]
    assert res["status"] == "DRAFT_READY_FOR_COMPLETENESS_REVIEW"
    assert text.startswith("CODEX-ONLY PROMPT\n")
    assert "AI_OS EXECUTION TOKEN" in text
    assert "AI_OS BOOTSTRAP REQUIRED" in text
    assert "APPROVAL AUTHORITY" in text
    assert "VALIDATOR CHAIN" in text
    assert "STOP POINT" in text


def test_write_draft_atomic_no_overwrite(tmp_path):
    m = _drafter()
    res = m.build_packet_draft(_goal(), allowed_paths=["Reports/"])
    r1 = m.write_draft(res, output_dir=tmp_path)
    assert r1["written"] is True and r1["status"] == "WRITTEN"
    assert Path(r1["md_path"]).exists()
    leftovers = [p.name for p in tmp_path.iterdir() if p.name.endswith(".tmp") or p.name.startswith(".")]
    assert leftovers == []
    r2 = m.write_draft(res, output_dir=tmp_path)
    assert r2["written"] is False and r2["status"] == "SKIPPED_EXISTS"


def test_write_draft_refuses_work_packets_dir(tmp_path):
    m = _drafter()
    res = m.build_packet_draft(_goal(), allowed_paths=["Reports/"])
    forbidden_dir = tmp_path / "automation" / "orchestration" / "work_packets"
    r = m.write_draft(res, output_dir=forbidden_dir)
    assert r["written"] is False and r["status"] == "BLOCKED_FORBIDDEN_DIR"
    assert not forbidden_dir.exists()


@pytest.mark.parametrize(
    "parts",
    [
        ("automation", "orchestration", "work_packets", "active"),
        ("automation", "orchestration", "command_queue"),
        ("automation", "orchestration", "approval_inbox"),
        ("automation", "orchestration", "workers", "inbox"),
        ("telemetry", "runtime"),
        ("services", "runtime"),
        ("broker",),
        ("live_trading",),
        ("secrets",),
        ("credentials",),
    ],
)
def test_write_draft_refuses_protected_mutation_paths(tmp_path, parts):
    m = _drafter()
    res = m.build_packet_draft(_goal(), allowed_paths=["Reports/"])
    forbidden_dir = tmp_path.joinpath(*parts)
    r = m.write_draft(res, output_dir=forbidden_dir)
    assert r["written"] is False
    assert r["status"] == "BLOCKED_FORBIDDEN_DIR"
    assert not forbidden_dir.exists()


def test_consumes_classifier_output_shape():
    m = _drafter()
    # the drafter must accept a single goal pulled from classifier 'goals' list shape
    classifier_out = {"schema": "AIOS_GAP_TO_GOAL_CANDIDATES.v1", "goals": [_goal()]}
    goal = classifier_out["goals"][0]
    res = m.build_packet_draft(goal, allowed_paths=["Reports/"])
    assert res["packet_id"].startswith("AIOS-DRAFT-")
