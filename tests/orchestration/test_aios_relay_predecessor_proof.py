from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "relay_proof" / "aios_relay_predecessor_proof.py"


def _load():
    spec = importlib.util.spec_from_file_location("aios_relay_predecessor_proof_test_module", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_module_exports():
    mod = _load()
    assert mod.SCHEMA == "AIOS_RELAY_PREDECESSOR_PROOF.v1"
    assert mod.MODE == "DRY_RUN_PROOF"


def test_bundle_closes_predecessor_proofs_and_writes_reports(tmp_path):
    mod = _load()
    report = mod.build_relay_predecessor_proof_bundle(repo_root=REPO_ROOT, now="2026-06-10T15:20:28Z")

    assert report["status"] == "PASS"
    assert report["approval_card_present"] is True
    assert report["completeness_ready"] is True
    assert report["path_guard_pass"] is True
    assert report["apply_inventory_target_selected"] is True
    assert report["protected_mutation_detected"] is False
    assert report["relay_review_status"] == "REVIEWABLE"
    assert report["relay_reviewable"] is True
    assert report["runtime_queue_validation"]["status"] == "PASS"
    assert report["relay_processor_validation"]["status"] == "PASS"
    assert report["relay_review_validation"]["status"] == "PASS"
    assert report["operator_dependency_validation"]["status"] == "PASS"
    assert report["reduction_target_validation"]["status"] == "PASS"
    assert report["relay_processor_readout"]["proof_status"] == "READY_FOR_DRY_RUN"
    assert report["apply_inventory_selection"]["selected_target"] == "relay_proof_review"
    assert report["runtime_queue_remaining_blockers"]
    assert all(item["dirty"] is False for item in report["protected_path_fingerprints"])
    assert report["approval_card"]["requires_human"] is True
    assert report["approval_card"]["approves_protected_action"] is False
    assert report["completeness_review"]["verdict"] == "READY_FOR_HUMAN_REVIEW"
    assert report["completeness_review"]["promotion_ready"] is True

    outdir = tmp_path / "Reports" / "relay_predecessor_proof"
    written = mod.write_relay_predecessor_proof_reports(report, repo_root=REPO_ROOT, output_dir=outdir)
    json_path = outdir / mod.REPORT_JSON_NAME
    md_path = outdir / mod.REPORT_MD_NAME
    assert json_path.exists()
    assert md_path.exists()
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["summary"]["status"] == "PASS"
    assert written["report_paths"] == [json_path.as_posix(), md_path.as_posix()]
    assert "approval_card_present" in md_path.read_text(encoding="utf-8")


def test_bundle_reports_named_missing_proof_when_overridden():
    mod = _load()
    report = mod.build_relay_predecessor_proof_bundle(
        repo_root=REPO_ROOT,
        now="2026-06-10T15:20:28Z",
        state_overrides={"approval_card_present": False},
        proof_overrides={"approval_card_present": False},
    )

    assert report["status"] == "BLOCKED_WITH_REAL_REASON"
    assert "approval_card_present" in report["missing_proofs"]
    assert report["relay_review_status"] == "BLOCKED"
    assert report["relay_reviewable"] is False
    assert report["protected_mutation_detected"] is False
    assert report["blockers"]
    assert "approval_card_present" in "\n".join(report["blockers"])
