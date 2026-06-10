"""Tests for the AI_OS goal intake bridge preview (observe-only)."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BRIDGE = (
    REPO_ROOT / "automation" / "orchestration" / "goal_intake"
    / "aios_goal_intake_bridge.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("aios_goal_intake_bridge", BRIDGE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _assert_safety(preview: dict[str, object]) -> None:
    assert preview["mode"] == "DRY_RUN"
    assert preview["observe_only"] is True
    assert preview["approvals_performed"] == "NO"
    assert preview["approval_inbox_mutated"] == "NO"
    assert preview["work_packets_mutated"] == "NO"
    assert preview["relay_goals_mutated"] == "NO"
    assert preview["relay_inbox_mutated"] == "NO"
    assert preview["dispatch_performed"] == "NO"
    assert preview["apply_performed"] == "NO"
    assert preview["commit_performed"] == "NO"
    assert preview["push_performed"] == "NO"
    assert preview["merge_performed"] == "NO"


def test_no_input_returns_safe_preview() -> None:
    m = _load()
    preview = m.build_goal_intake_preview(None)
    assert preview["schema"] == "AIOS_GOAL_INTAKE_BRIDGE_PREVIEW.v1"
    assert preview["candidate_count"] == 0
    assert preview["proposal_count"] == 0
    assert preview["status"] == "NO_INPUT"
    assert preview["next_safe_action"] == "Provide inventory or classifier output to generate goal proposals."
    _assert_safety(preview)


def test_classifier_style_input_becomes_proposal() -> None:
    m = _load()
    payload = {
        "goals": [
            {
                "goal_id": "goal-001",
                "title": "Surface approval state",
                "reason": "approval output lacks consumer",
                "priority": "HIGH",
            }
        ],
        "candidate_count": 1,
    }
    preview = m.build_goal_intake_preview(payload, source_path="classifier.json")
    assert preview["proposal_count"] == 1
    proposal = preview["proposals"][0]
    assert proposal["source_goal_id"] == "goal-001"
    assert proposal["requires_human_review"] is True
    assert proposal["risk_level"] == "REVIEW_REQUIRED"
    assert proposal["recommended_lane"] == "HUMAN_REVIEW"
    assert proposal["provenance"]["source_path"] == "classifier.json"
    _assert_safety(preview)


def test_generic_candidates_input_becomes_proposals() -> None:
    m = _load()
    payload = {
        "candidates": [
            {
                "goal_id": "goal-a",
                "title": "Bridge candidate A",
                "summary": "Candidate A summary",
                "priority": "LOW",
                "risk_level": "LOW",
            },
            {
                "goal_id": "goal-b",
                "title": "Bridge candidate B",
                "summary": "Candidate B summary",
            },
        ]
    }
    preview = m.build_goal_intake_preview(payload, source_path="candidates.json")
    assert preview["proposal_count"] == 2
    assert [proposal["source_goal_id"] for proposal in preview["proposals"]] == ["goal-a", "goal-b"]
    assert preview["proposals"][0]["risk_level"] == "LOW"
    assert preview["proposals"][0]["recommended_lane"] == "PROPOSAL_REVIEW"
    _assert_safety(preview)


def test_self_build_evidence_goal_ids_are_normalized() -> None:
    m = _load()
    payload = {
        "schema": "AIOS_SELF_BUILD_CYCLE.v1",
        "evidence_bundle": {
            "gap_candidates": {
                "candidate_count": 2,
                "goal_ids": ["goal-a", "goal-b"],
            }
        },
    }
    preview = m.build_goal_intake_preview(payload, source_path="cycle.json")
    assert preview["candidate_count"] == 2
    assert preview["proposal_count"] == 2
    assert [proposal["source_goal_id"] for proposal in preview["proposals"]] == ["goal-a", "goal-b"]
    assert all(proposal["requires_human_review"] for proposal in preview["proposals"])
    _assert_safety(preview)


def test_default_output_path_is_under_reports_goal_intake() -> None:
    m = _load()
    paths = m.default_output_paths(REPO_ROOT)
    assert paths["json"].parent == REPO_ROOT / "Reports" / "goal_intake"
    assert paths["md"].parent == REPO_ROOT / "Reports" / "goal_intake"


def test_write_preview_skips_existing_without_overwrite(tmp_path: Path) -> None:
    m = _load()
    preview = m.build_goal_intake_preview(None)
    json_path = tmp_path / "preview.json"
    md_path = tmp_path / "preview.md"

    first = m.write_preview(preview, json_path, md_path, overwrite=False)
    second = m.write_preview(preview, json_path, md_path, overwrite=False)

    assert first["json_status"] == "WRITTEN"
    assert first["md_status"] == "WRITTEN"
    assert second["json_status"] == "SKIPPED_EXISTS"
    assert second["md_status"] == "SKIPPED_EXISTS"
    assert json_path.read_text(encoding="utf-8").startswith("{")


def test_write_preview_overwrite_replaces_output(tmp_path: Path) -> None:
    m = _load()
    preview = m.build_goal_intake_preview(None)
    json_path = tmp_path / "preview.json"
    md_path = tmp_path / "preview.md"

    m.write_preview(preview, json_path, md_path, overwrite=False)
    json_path.write_text('{"sentinel": 1}\n', encoding="utf-8")
    md_path.write_text("sentinel", encoding="utf-8")

    result = m.write_preview(preview, json_path, md_path, overwrite=True)
    assert result["json_status"] == "WRITTEN"
    assert result["md_status"] == "WRITTEN"
    assert "sentinel" not in json_path.read_text(encoding="utf-8")
    assert "sentinel" not in md_path.read_text(encoding="utf-8")


def test_cli_smoke_writes_files_and_prints_json(tmp_path: Path) -> None:
    payload_path = tmp_path / "input.json"
    payload_path.write_text(
        json.dumps(
            {
                "goals": [
                    {"goal_id": "goal-cli", "title": "CLI goal", "reason": "from test"}
                ]
            }
        ),
        encoding="utf-8",
    )
    output_json = tmp_path / "out" / "preview.json"
    output_md = tmp_path / "out" / "preview.md"

    proc = subprocess.run(
        [
            sys.executable,
            str(BRIDGE),
            "--input",
            str(payload_path),
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0
    stdout = json.loads(proc.stdout)
    assert stdout["schema"] == "AIOS_GOAL_INTAKE_BRIDGE_PREVIEW.v1"
    assert output_json.exists()
    assert output_md.exists()


def test_cli_malformed_json_returns_nonzero(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not-json", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(BRIDGE), "--input", str(bad)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 3
    stdout = json.loads(proc.stdout)
    assert stdout["status"] == "BLOCKED_MALFORMED_INPUT"
    assert stdout["source_path"] == str(bad)
    _assert_safety(stdout)
