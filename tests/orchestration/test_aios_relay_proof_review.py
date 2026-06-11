from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PREDECESSOR_PATH = REPO_ROOT / "automation" / "orchestration" / "relay_proof" / "aios_relay_predecessor_proof.py"
REVIEW_PATH = REPO_ROOT / "automation" / "orchestration" / "relay_proof" / "aios_relay_proof_review.py"


def _load(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _predecessor_bundle(**kwargs):
    predecessor_mod = _load(PREDECESSOR_PATH, "aios_relay_predecessor_proof_for_review_tests")
    return predecessor_mod.build_relay_predecessor_proof_bundle(repo_root=REPO_ROOT, now="2026-06-10T15:20:28Z", **kwargs)


def test_review_refreshed_from_predecessor_bundle_is_reviewable(tmp_path):
    review_mod = _load(REVIEW_PATH, "aios_relay_proof_review_for_review_tests")
    bundle = _predecessor_bundle()
    report = review_mod.build_relay_proof_review_report(
        repo_root=REPO_ROOT,
        predecessor_bundle=bundle,
        now="2026-06-10T15:20:28Z",
    )

    assert report["review_status"] == "REVIEWABLE"
    assert report["proof_reviewable"] is True
    assert report["missing_proofs"] == []
    assert report["blocked_human_gates"] == ["human_sos_arming", "human_scheduler_registration"]
    assert report["unsafe_autonomy_claim"] is False
    assert report["relay_predecessor_status"] == "PASS"
    assert report["relay_review_validation"]["status"] == "PASS"
    assert report["runtime_queue_readout"]
    assert report["relay_processor_readout"]
    assert report["operator_dependency_ledger"]
    assert report["reduction_target_selector"]

    outdir = tmp_path / "Reports" / "relay_proof_review"
    written = review_mod.write_relay_proof_review_reports(report, repo_root=REPO_ROOT, output_dir=outdir)
    json_path = outdir / review_mod.REPORT_JSON_NAME
    md_path = outdir / review_mod.REPORT_MD_NAME
    assert json_path.exists()
    assert md_path.exists()
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["summary"]["review_status"] == "REVIEWABLE"
    assert written["report_paths"] == [json_path.as_posix(), md_path.as_posix()]
    assert "relay proof review" in md_path.read_text(encoding="utf-8").lower()


def test_review_becomes_blocked_when_predecessor_missing_proof():
    review_mod = _load(REVIEW_PATH, "aios_relay_proof_review_for_blocked_review_tests")
    bundle = _predecessor_bundle(
        state_overrides={"approval_card_present": False},
        proof_overrides={"approval_card_present": False},
    )
    report = review_mod.build_relay_proof_review_report(
        repo_root=REPO_ROOT,
        predecessor_bundle=bundle,
        now="2026-06-10T15:20:28Z",
    )

    assert report["review_status"] == "BLOCKED"
    assert report["proof_reviewable"] is False
    assert "approval_card_present" in report["relay_predecessor_missing_proofs"]
    assert report["safe_next_action"].startswith("Resolve the missing predecessor proofs")
    assert report["unsafe_autonomy_claim"] is False
    assert report["dispatch_allowed"] is False
    assert report["apply_allowed"] is False
    assert report["runtime_mutation_allowed"] is False
    assert report["vacation_mode_complete"] is False
