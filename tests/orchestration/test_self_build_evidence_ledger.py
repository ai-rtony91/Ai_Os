"""Tests for the self-build evidence ledger (observe-only reader/aggregator)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = (
    REPO_ROOT / "automation" / "orchestration" / "autonomy_reports"
    / "aios_self_build_evidence_ledger.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("aios_self_build_evidence_ledger", LEDGER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _record(cycle_id, *, action="PROPOSE_NEXT_GOAL", safety="SAFE", mode="DRY_RUN",
            requires_human=False, ts="2026-01-01T00:00:00Z", redactions=0):
    return {
        "schema": "AIOS_SELF_BUILD_CYCLE_EVIDENCE.v1",
        "cycle_id": cycle_id,
        "timestamp_utc": ts,
        "mode": mode,
        "decision": {"action": action},
        "safety_status": safety,
        "requires_human": requires_human,
        "evidence_bundle": {"completion": {"verdict": "COMPLETION_UNPROVEN"}},
        "source_modules": [],
        "redaction_summary": {"count": redactions, "by_reason": {}, "events": []},
    }


def _seed(d: Path, records):
    d.mkdir(parents=True, exist_ok=True)
    for rec in records:
        (d / f"{rec['cycle_id']}.json").write_text(json.dumps(rec), encoding="utf-8")


def test_empty_dir_yields_no_evidence_posture(tmp_path):
    m = _load()
    digest = m.build_ledger(tmp_path)
    assert digest["total_cycles"] == 0
    assert digest["posture"] == "NO_EVIDENCE"
    assert digest["latest_cycle"] is None


def test_missing_dir_does_not_crash(tmp_path):
    m = _load()
    digest = m.build_ledger(tmp_path / "does_not_exist")
    assert digest["total_cycles"] == 0
    assert digest["posture"] == "NO_EVIDENCE"


def test_aggregates_counts_across_records(tmp_path):
    m = _load()
    _seed(tmp_path, [
        _record("c1", action="PROPOSE_NEXT_GOAL", safety="SAFE", requires_human=False, ts="2026-01-01T00:00:00Z"),
        _record("c2", action="HOLD_FOR_HUMAN", safety="HUMAN_REQUIRED", requires_human=True, ts="2026-01-02T00:00:00Z"),
        _record("c3", action="PROPOSE_NEXT_GOAL", safety="SAFE", requires_human=False, ts="2026-01-03T00:00:00Z", redactions=2),
    ])
    digest = m.build_ledger(tmp_path)
    assert digest["total_cycles"] == 3
    assert digest["decision_actions"] == {"PROPOSE_NEXT_GOAL": 2, "HOLD_FOR_HUMAN": 1}
    assert digest["safety_status_counts"] == {"SAFE": 2, "HUMAN_REQUIRED": 1}
    assert digest["requires_human_count"] == 1
    assert digest["redactions_total"] == 2
    assert digest["posture"] == "OBSERVE_ONLY_CLEAN"


def test_latest_cycle_is_highest_timestamp(tmp_path):
    m = _load()
    _seed(tmp_path, [
        _record("early", ts="2026-01-01T00:00:00Z"),
        _record("late", ts="2026-03-15T12:00:00Z"),
        _record("mid", ts="2026-02-01T00:00:00Z"),
    ])
    digest = m.build_ledger(tmp_path)
    assert digest["latest_cycle"]["cycle_id"] == "late"
    assert digest["first_cycle_utc"] == "2026-01-01T00:00:00Z"
    assert digest["last_cycle_utc"] == "2026-03-15T12:00:00Z"


def test_non_dry_run_triggers_needs_review(tmp_path):
    m = _load()
    _seed(tmp_path, [
        _record("ok", mode="DRY_RUN"),
        _record("hot", mode="APPLY"),
    ])
    digest = m.build_ledger(tmp_path)
    assert digest["non_dry_run_count"] == 1
    assert digest["posture"] == "NEEDS_REVIEW"


def test_blocked_cycle_triggers_needs_review(tmp_path):
    m = _load()
    _seed(tmp_path, [_record("b", safety="BLOCKED")])
    digest = m.build_ledger(tmp_path)
    assert digest["blocked_cycle_count"] == 1
    assert digest["posture"] == "NEEDS_REVIEW"


def test_malformed_files_are_skipped_not_fatal(tmp_path):
    m = _load()
    _seed(tmp_path, [_record("good")])
    (tmp_path / "broken.json").write_text("{ not json", encoding="utf-8")
    (tmp_path / "wrong_schema.json").write_text(json.dumps({"schema": "OTHER", "cycle_id": "x"}), encoding="utf-8")
    digest = m.build_ledger(tmp_path)
    assert digest["total_cycles"] == 1
    assert digest["read_error_count"] == 2
    reasons = {e["reason"] for e in digest["read_errors"]}
    assert "unreadable_or_invalid_json" in reasons
    assert "off_schema_or_missing_cycle_id" in reasons


def test_digest_never_copies_evidence_bundle_forward(tmp_path):
    m = _load()
    # even if a (hypothetical) raw value sat in evidence_bundle, the digest must not carry it
    rec = _record("c1")
    rec["evidence_bundle"]["leak_probe"] = "SHOULD_NOT_APPEAR_IN_DIGEST"
    _seed(tmp_path, [rec])
    digest = m.build_ledger(tmp_path)
    assert "SHOULD_NOT_APPEAR_IN_DIGEST" not in json.dumps(digest)


def test_write_digest_atomic_and_no_overwrite(tmp_path):
    m = _load()
    _seed(tmp_path, [_record("c1")])
    digest = m.build_ledger(tmp_path)
    out = tmp_path / "out" / "digest.json"
    res1 = m.write_digest(digest, out)
    assert res1["written"] is True and res1["status"] == "WRITTEN"
    assert out.exists()
    assert (tmp_path / "out" / "digest.md").exists()
    # no temp files left behind
    leftovers = [p.name for p in (tmp_path / "out").iterdir() if p.name.endswith(".tmp") or p.name.startswith(".")]
    assert leftovers == []
    # second write without overwrite is skipped
    res2 = m.write_digest(digest, out)
    assert res2["written"] is False and res2["status"] == "SKIPPED_EXISTS"


def test_write_digest_overwrite_true_replaces(tmp_path):
    m = _load()
    _seed(tmp_path, [_record("c1")])
    out = tmp_path / "digest.json"
    m.write_digest(m.summarize_records([], now="2026-01-01T00:00:00Z"), out)
    digest = m.build_ledger(tmp_path)
    res = m.write_digest(digest, out, overwrite=True)
    assert res["written"] is True
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["total_cycles"] == 1


def test_summarize_records_direct_empty():
    m = _load()
    digest = m.summarize_records([], now="2026-01-01T00:00:00Z")
    assert digest["schema"] == "AIOS_SELF_BUILD_EVIDENCE_LEDGER.v1"
    assert digest["total_cycles"] == 0
    assert digest["posture"] == "NO_EVIDENCE"
    assert digest["generated_at_utc"] == "2026-01-01T00:00:00Z"
