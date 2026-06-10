"""Tests for the self-build cycle evidence persister (observe-only)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PERSISTER = (
    REPO_ROOT / "automation" / "orchestration" / "autonomy_reports"
    / "aios_self_build_evidence_persister.py"
)

EVIDENCE_FIELDS = {
    "schema", "cycle_id", "timestamp_utc", "mode", "decision", "safety_status",
    "requires_human", "evidence_bundle", "source_modules", "redaction_summary",
}


def _load():
    spec = importlib.util.spec_from_file_location("aios_self_build_evidence_persister", PERSISTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _cycle(**over):
    base = {
        "schema": "AIOS_SELF_BUILD_CYCLE.v1",
        "cycle_id": "sbc-test123",
        "mode": "DRY_RUN",
        "decision": {"action": "PROPOSE_NEXT_GOAL", "requires_human": False, "mode": "DRY_RUN", "reason": "ok"},
        "evidence_bundle": {
            "gap_candidates": {"candidate_count": 1, "goal_ids": ["g1"]},
            "completion": {"verdict": "COMPLETION_UNPROVEN", "reasons": []},
            "runtime": {"runtime_gate": "READY_TO_REPORT", "control_plane_status": "PASS"},
            "decision": {"action": "PROPOSE_NEXT_GOAL"},
        },
        "source_modules": [{"module": "next_action_decider", "ref": "#516", "available": True}],
        "safety_status": "SAFE",
        "requires_human": False,
    }
    base.update(over)
    return base


def test_json_write_and_schema_fields(tmp_path):
    m = _load()
    res = m.persist_cycle_evidence(_cycle(), output_dir=tmp_path, now="2026-01-01T00:00:00Z")
    assert res["written"] is True and res["status"] == "WRITTEN"
    p = Path(res["json_path"])
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert set(data.keys()) == EVIDENCE_FIELDS
    assert data["cycle_id"] == "sbc-test123"
    assert data["mode"] == "DRY_RUN"
    assert data["timestamp_utc"] == "2026-01-01T00:00:00Z"


def test_markdown_write(tmp_path):
    m = _load()
    res = m.persist_cycle_evidence(_cycle(), output_dir=tmp_path, write_markdown=True)
    md = Path(res["md_path"])
    assert md.exists()
    text = md.read_text(encoding="utf-8")
    assert "sbc-test123" in text and "PROPOSE_NEXT_GOAL" in text
    assert "No command emitted" in text


def test_no_markdown_when_disabled(tmp_path):
    m = _load()
    res = m.persist_cycle_evidence(_cycle(), output_dir=tmp_path, write_markdown=False)
    assert res["md_path"] is None
    assert not (tmp_path / "sbc-test123.md").exists()


def test_no_overwrite_by_default(tmp_path):
    m = _load()
    m.persist_cycle_evidence(_cycle(decision={"action": "A"}), output_dir=tmp_path)
    first = (tmp_path / "sbc-test123.json").read_text(encoding="utf-8")
    res2 = m.persist_cycle_evidence(_cycle(decision={"action": "B"}), output_dir=tmp_path)
    assert res2["written"] is False and res2["status"] == "SKIPPED_EXISTS"
    assert (tmp_path / "sbc-test123.json").read_text(encoding="utf-8") == first  # unchanged


def test_overwrite_true_replaces(tmp_path):
    m = _load()
    m.persist_cycle_evidence(_cycle(decision={"action": "A"}), output_dir=tmp_path)
    res2 = m.persist_cycle_evidence(_cycle(decision={"action": "B"}), output_dir=tmp_path, overwrite=True)
    assert res2["written"] is True
    data = json.loads((tmp_path / "sbc-test123.json").read_text(encoding="utf-8"))
    assert data["decision"]["action"] == "B"


def test_malformed_input_fails_closed_writes_nothing(tmp_path):
    m = _load()
    res = m.persist_cycle_evidence({"no_cycle_id": True}, output_dir=tmp_path)
    assert res["written"] is False and res["status"] == "BLOCKED_MALFORMED"
    assert list(tmp_path.iterdir()) == []  # nothing written


def test_redaction_by_key_and_value(tmp_path):
    m = _load()
    cycle = _cycle(evidence_bundle={
        "completion": {"verdict": "COMPLETION_VERIFIED"},
        "api_key": "AKIAIOSFODNN7EXAMPLE",          # redact by key name
        "notes": "token is ghp_abcdefghijklmnopqrstuvwxyz0123456789",  # redact by value pattern
        "runtime": {"runtime_gate": "READY_TO_REPORT"},
        "gap_candidates": {"candidate_count": 0, "goal_ids": []},
        "decision": {"action": "X"},
    })
    res = m.persist_cycle_evidence(cycle, output_dir=tmp_path)
    data = json.loads(Path(res["json_path"]).read_text(encoding="utf-8"))
    eb = data["evidence_bundle"]
    assert eb["api_key"] == "[REDACTED]"
    assert eb["notes"] == "[REDACTED]"
    assert data["redaction_summary"]["count"] >= 2
    # the raw secret must not survive anywhere in the file
    raw = Path(res["json_path"]).read_text(encoding="utf-8")
    assert "AKIAIOSFODNN7EXAMPLE" not in raw
    assert "ghp_abcdefghijklmnopqrstuvwxyz0123456789" not in raw


def test_atomic_no_temp_files_left(tmp_path):
    m = _load()
    m.persist_cycle_evidence(_cycle(), output_dir=tmp_path)
    leftovers = [p.name for p in tmp_path.iterdir() if p.name.endswith(".tmp") or p.name.startswith(".")]
    assert leftovers == []  # temp cleaned up / renamed away


def test_default_path_under_reports_self_build_cycle(tmp_path):
    m = _load()
    res = m.persist_cycle_evidence(_cycle(), repo_root=tmp_path)  # no output_dir -> default
    expected = tmp_path / "Reports" / "self_build_cycle" / "sbc-test123.json"
    assert Path(res["json_path"]) == expected
    assert expected.exists()


def test_custom_path(tmp_path):
    m = _load()
    custom = tmp_path / "my" / "evidence"
    res = m.persist_cycle_evidence(_cycle(), output_dir=custom)
    assert Path(res["json_path"]) == custom / "sbc-test123.json"
    assert (custom / "sbc-test123.json").exists()


def test_redact_helper_direct():
    m = _load()
    red, summary = m.redact({"password": "hunter2supersecret", "ok": "plain value"})
    assert red["password"] == "[REDACTED]"
    assert red["ok"] == "plain value"
    assert summary["count"] == 1
    assert "secret_key_name" in summary["by_reason"]
