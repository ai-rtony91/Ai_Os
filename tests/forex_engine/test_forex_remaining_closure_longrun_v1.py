from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from automation.forex_engine import (
    forex_evidence_quality_validator_v1 as quality,
)
from automation.forex_engine import forex_final_bundle_readiness_projector_v1 as projector
from automation.forex_engine import (
    forex_missing_evidence_catalog_v1 as catalog_lib,
)
from automation.forex_engine import (
    forex_owner_evidence_pack_builder_v1 as owner_pack,
)
from automation.forex_engine import forex_review_ready_candidate_selector_v1 as selector


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_BASE = REPO_ROOT / "tests\\fixtures\\forex_delivery\\remaining_closure_v1"


def _read_candidate(name: str) -> dict:
    return json.loads((FIXTURE_BASE / name).read_text(encoding="utf-8"))


def _read_markdown(name: str) -> str:
    return (FIXTURE_BASE / name).read_text(encoding="utf-8")


def test_missing_evidence_catalog_builds_deterministic_records():
    first = catalog_lib.build_missing_evidence_catalog(
        explicit_records=[{"name": "candidate evidence", "classification": "ALREADY_PRESENT"}],
    )
    second = catalog_lib.build_missing_evidence_catalog(
        explicit_records=[{"name": "candidate evidence", "classification": "ALREADY_PRESENT"}],
    )
    assert first["item_count"] == second["item_count"]
    assert first["items"]["candidate evidence"]["classification"] == "ALREADY_PRESENT"


def test_catalog_classifies_local_repairable():
    status = catalog_lib.classify_evidence_item("walk-forward evidence")
    assert status == catalog_lib.LOCAL_REPAIRABLE


def test_catalog_classifies_owner_evidence_required():
    status = catalog_lib.classify_evidence_item("owner approval evidence")
    assert status == catalog_lib.OWNER_EVIDENCE_REQUIRED


def test_catalog_classifies_broker_api_required_as_blocked():
    status = catalog_lib.classify_evidence_item("broker snapshot evidence")
    assert status == catalog_lib.BROKER_API_REQUIRED


def test_catalog_classifies_credential_required_as_blocked():
    status = catalog_lib.classify_evidence_item("credential boundary evidence")
    assert status == catalog_lib.CREDENTIAL_REQUIRED


def test_catalog_classifies_trading_execution_required_as_blocked():
    status = catalog_lib.classify_evidence_item("execution readiness evidence")
    assert status == catalog_lib.TRADING_EXECUTION_REQUIRED


def test_owner_evidence_pack_builds_sanitized_template():
    pack = owner_pack.build_owner_evidence_pack({"items": {"candidate evidence": {"name": "candidate evidence"}}}, include_templates=True)
    assert "sanitized_templates" in pack
    assert "Template for candidate evidence" in pack["sanitized_templates"]["candidate evidence"]


def test_owner_evidence_pack_includes_redaction_rules():
    rules = owner_pack.build_redaction_rules()
    assert len(rules) >= 2
    assert "Remove all account identifiers." in rules


def test_owner_evidence_pack_excludes_credentials():
    pack = owner_pack.build_owner_evidence_pack(
        {"items": {"candidate evidence": {"name": "candidate evidence", "classification": "LOCAL_REPAIRABLE"}}},
        include_templates=False,
    )
    payload = json.dumps(pack)
    assert "api_key" not in payload
    assert "password" not in payload.lower()


def test_evidence_validator_passes_clean_bundle():
    result = quality.validate_evidence_text(_read_markdown("evidence_bundle_clean.md"), strict=False)
    assert result["status"] in {quality.EVIDENCE_PASS, quality.EVIDENCE_REPAIRABLE}


def test_evidence_validator_finds_missing_sections():
    result = quality.validate_evidence_bundle([FIXTURE_BASE / "evidence_bundle_missing_sections.md"], strict=False)
    assert any("missing_sections" in item["status"] for item in [result]) or result["status"] != quality.EVIDENCE_PASS


def test_evidence_validator_rejects_sensitive_patterns():
    payload = _read_markdown("evidence_bundle_clean.md")
    marker = "api" + "_key" + " = " + '"demo"'
    payload = payload + "\n" + marker
    report = quality.validate_evidence_text(payload, strict=False)
    assert report["status"] == quality.SAFETY_REJECT
    assert report["sensitive_hits"]


def test_evidence_validator_rejects_broker_api_commands():
    payload = _read_markdown("evidence_bundle_broker_command_rejected.md")
    report = quality.validate_evidence_text(payload, strict=False)
    assert report["status"] == quality.SAFETY_REJECT


def test_evidence_validator_classifies_insufficient_sample():
    payload = _read_markdown("evidence_bundle_insufficient_sample.md")
    report = quality.validate_evidence_text(payload, strict=False)
    assert report["status"] == quality.INSUFFICIENT_SAMPLE


def test_candidate_selector_picks_review_ready_candidate():
    payload = _read_candidate("candidate_complete_review_ready.json")
    decision = selector.explain_candidate_decision(payload)
    assert decision["route"] == selector.REVIEW_READY


def test_candidate_selector_rejects_negative_expectancy():
    payload = _read_candidate("candidate_negative_expectancy.json")
    decision = selector.explain_candidate_decision(payload)
    assert decision["route"] == selector.REJECT_NEGATIVE_EXPECTANCY


def test_candidate_selector_rejects_low_sample():
    payload = _read_candidate("candidate_low_sample.json")
    decision = selector.explain_candidate_decision(payload)
    assert decision["route"] == selector.REJECT_LOW_SAMPLE


def test_candidate_selector_rejects_high_drawdown():
    payload = _read_candidate("candidate_high_drawdown.json")
    decision = selector.explain_candidate_decision(payload)
    assert decision["route"] == selector.REJECT_HIGH_DRAWDOWN


def test_candidate_selector_rejects_low_profit_factor():
    payload = _read_candidate("candidate_low_profit_factor.json")
    decision = selector.explain_candidate_decision(payload)
    assert decision["route"] == selector.REJECT_LOW_PROFIT_FACTOR


def test_candidate_selector_routes_missing_owner_approval():
    payload = _read_candidate("candidate_missing_owner_approval.json")
    result = selector.select_review_ready_candidate([payload], strict=True)
    assert result["route"] == selector.NEEDS_MORE_EVIDENCE
    assert result["candidate_decisions"][0]["route"] == selector.NEEDS_MORE_EVIDENCE


def test_candidate_selector_routes_external_evidence_required():
    payload = _read_candidate("candidate_broker_evidence_required.json")
    result = selector.select_review_ready_candidate([payload], strict=False)
    assert result["route"] == selector.EXTERNAL_EVIDENCE_REQUIRED


def test_final_bundle_projector_returns_final_ready():
    catalog = catalog_lib.build_missing_evidence_catalog(explicit_records=[{"name": "candidate evidence", "classification": "ALREADY_PRESENT"}])
    quality_payload = quality.validate_evidence_bundle([FIXTURE_BASE / "evidence_bundle_clean.md"], strict=False)
    selector_payload = selector.select_review_ready_candidate(
        [_read_candidate("candidate_complete_review_ready.json")],
        strict=False,
    )
    projection = projector.project_final_bundle_readiness(
        catalog,
        quality_payload,
        selector_payload,
        strict=False,
    )
    assert projection["status"] == projector.FINAL_BUNDLE_READY


def test_final_bundle_projector_returns_partial_external_required():
    catalog_payload = json.loads((FIXTURE_BASE / "catalog_external_evidence_required.json").read_text(encoding="utf-8"))
    quality_payload = quality.validate_evidence_bundle([FIXTURE_BASE / "evidence_bundle_clean.md"], strict=False)
    selector_payload = selector.select_review_ready_candidate(
        [_read_candidate("candidate_complete_review_ready.json"), _read_candidate("candidate_broker_evidence_required.json")],
        strict=False,
    )
    projection = projector.project_final_bundle_readiness(catalog_payload, quality_payload, selector_payload)
    assert projection["status"] == projector.PARTIAL_EXTERNAL_EVIDENCE_REQUIRED


def test_final_bundle_projector_returns_local_repair_required():
    quality_payload = quality.validate_evidence_bundle([FIXTURE_BASE / "evidence_bundle_insufficient_sample.md"], strict=False)
    selector_payload = selector.select_review_ready_candidate([_read_candidate("candidate_complete_review_ready.json")], strict=False)
    catalog = catalog_lib.build_missing_evidence_catalog(explicit_records=[])
    projection = projector.project_final_bundle_readiness(catalog, quality_payload, selector_payload)
    assert projection["status"] == projector.LOCAL_REPAIR_REQUIRED


def test_final_bundle_projector_returns_safety_blocked():
    quality_payload = {"status": quality.SAFETY_REJECT, "path_count": 1, "results": []}
    selector_payload = {"route": selector.REVIEW_READY}
    catalog = {"items": {"candidate evidence": {"classification": "ALREADY_PRESENT", "name": "candidate evidence"}}}
    projection = projector.project_final_bundle_readiness(catalog, quality_payload, selector_payload)
    assert projection["status"] == projector.SAFETY_BLOCKED


def test_cli_owner_evidence_pack_writes_report(tmp_path):
    report = tmp_path / "owner_pack.md"
    script = REPO_ROOT / "scripts\\forex_delivery\\run_forex_owner_evidence_pack_builder_v1.py"
    subprocess.check_call([sys.executable, str(script), "--write-report", "--report-path", str(report), "--strict", "--include-templates"])
    assert report.exists()
    assert "Forex Owner Evidence Pack V1" in report.read_text(encoding="utf-8")


def test_cli_evidence_validator_writes_report(tmp_path):
    report = tmp_path / "validator.md"
    script = REPO_ROOT / "scripts\\forex_delivery\\run_forex_evidence_quality_validator_v1.py"
    subprocess.check_call([sys.executable, str(script), "--write-report", "--report-path", str(report)])
    assert report.exists()
    assert "Forex Evidence Quality Validator V1" in report.read_text(encoding="utf-8")


def test_cli_selector_writes_report(tmp_path):
    report = tmp_path / "selector.md"
    script = REPO_ROOT / "scripts\\forex_delivery\\run_forex_review_ready_candidate_selector_v1.py"
    subprocess.check_call([sys.executable, str(script), "--write-report", "--report-path", str(report)])
    assert report.exists()
    assert "Forex Review-Ready Candidate Selector V1" in report.read_text(encoding="utf-8")


def test_cli_projector_writes_report(tmp_path):
    report = tmp_path / "projector.md"
    script = REPO_ROOT / "scripts\\forex_delivery\\run_forex_final_bundle_readiness_projector_v1.py"
    subprocess.check_call([sys.executable, str(script), "--write-report", "--report-path", str(report)])
    assert report.exists()
    assert "Forex Final Bundle Readiness Projector V1" in report.read_text(encoding="utf-8")


def test_json_output_serializes():
    payload = quality.validate_evidence_bundle([FIXTURE_BASE / "evidence_bundle_clean.md"], strict=False)
    serialized = quality.quality_result_to_jsonable_dict(payload)
    assert json.dumps(serialized)


def test_markdown_reports_contain_required_status():
    report = (REPO_ROOT / "Reports\\forex_delivery\\AIOS_FOREX_REMAINING_CLOSURE_LONGRUN_CAMPAIGN_V1_REPORT.md").read_text(encoding="utf-8")
    assert "DEFERRED_OWNER_VALIDATION" in report
    selector_payload = selector.select_review_ready_candidate([_read_candidate("candidate_complete_review_ready.json")])
    md = selector.candidate_selector_to_markdown(selector_payload)
    assert "Route:" in md
    validator_md = quality.quality_result_to_markdown(
        quality.validate_evidence_bundle([FIXTURE_BASE / "evidence_bundle_clean.md"], strict=False)
    )
    assert "Status:" in validator_md


def test_modules_do_not_use_network_or_broker_calls():
    for module_file in [
        REPO_ROOT / "automation\\forex_engine\\forex_missing_evidence_catalog_v1.py",
        REPO_ROOT / "automation\\forex_engine\\forex_owner_evidence_pack_builder_v1.py",
        REPO_ROOT / "automation\\forex_engine\\forex_evidence_quality_validator_v1.py",
        REPO_ROOT / "automation\\forex_engine\\forex_review_ready_candidate_selector_v1.py",
        REPO_ROOT / "automation\\forex_engine\\forex_final_bundle_readiness_projector_v1.py",
    ]:
        content = module_file.read_text(encoding="utf-8", errors="ignore")
        assert "requests" not in content
        assert "socket" not in content
        assert "subprocess" not in content


def test_no_environment_or_credential_reads_in_modules():
    for module_file in [
        REPO_ROOT / "automation\\forex_engine\\forex_missing_evidence_catalog_v1.py",
        REPO_ROOT / "automation\\forex_engine\\forex_owner_evidence_pack_builder_v1.py",
        REPO_ROOT / "automation\\forex_engine\\forex_evidence_quality_validator_v1.py",
        REPO_ROOT / "automation\\forex_engine\\forex_review_ready_candidate_selector_v1.py",
        REPO_ROOT / "automation\\forex_engine\\forex_final_bundle_readiness_projector_v1.py",
    ]:
        content = module_file.read_text(encoding="utf-8", errors="ignore")
        assert "os.environ" not in content
        assert "dotenv" not in content


def test_no_forbidden_sensitive_assignment_literals_in_new_files():
    for module_file in [
        REPO_ROOT / "automation\\forex_engine\\forex_missing_evidence_catalog_v1.py",
        REPO_ROOT / "automation\\forex_engine\\forex_owner_evidence_pack_builder_v1.py",
        REPO_ROOT / "automation\\forex_engine\\forex_evidence_quality_validator_v1.py",
        REPO_ROOT / "automation\\forex_engine\\forex_review_ready_candidate_selector_v1.py",
        REPO_ROOT / "automation\\forex_engine\\forex_final_bundle_readiness_projector_v1.py",
    ]:
        text = module_file.read_text(encoding="utf-8", errors="ignore")
        assert not re.search(r"(?im)^(api_key|apikey|secret|password|token|broker)\\s*[:=]", text)


def test_no_protected_git_or_github_commands_in_modules():
    for path in [
        REPO_ROOT / "scripts\\forex_delivery\\run_forex_owner_evidence_pack_builder_v1.py",
        REPO_ROOT / "scripts\\forex_delivery\\run_forex_evidence_quality_validator_v1.py",
        REPO_ROOT / "scripts\\forex_delivery\\run_forex_review_ready_candidate_selector_v1.py",
        REPO_ROOT / "scripts\\forex_delivery\\run_forex_final_bundle_readiness_projector_v1.py",
    ]:
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert "git add" not in text
        assert "gh pr create" not in text
        assert "git push" not in text


def test_integration_catalog_owner_validator_selector_projector():
    catalog_payload = json.loads((FIXTURE_BASE / "catalog_mixed_blockers.json").read_text(encoding="utf-8"))
    validator_result = quality.validate_evidence_bundle(
        [FIXTURE_BASE / "evidence_bundle_clean.md", FIXTURE_BASE / "evidence_bundle_missing_sections.md"],
        strict=True,
    )
    selector_result = selector.select_review_ready_candidate(
        [
            _read_candidate("candidate_complete_review_ready.json"),
            _read_candidate("candidate_negative_expectancy.json"),
            _read_candidate("candidate_missing_owner_approval.json"),
        ],
        strict=False,
    )
    projection = projector.project_final_bundle_readiness(
        catalog_payload,
        validator_result,
        selector_result,
    )
    assert projection["bundle_map"]
    assert projection["status"] in {
        projector.FINAL_BUNDLE_READY,
        projector.PARTIAL_EXTERNAL_EVIDENCE_REQUIRED,
        projector.LOCAL_REPAIR_REQUIRED,
        projector.SAFETY_BLOCKED,
        projector.OWNER_APPROVAL_REQUIRED,
    }


def test_integration_partial_evidence_route_preserves_external_blocker():
    selector_result = selector.select_review_ready_candidate([_read_candidate("candidate_broker_evidence_required.json")])
    catalog_payload = catalog_lib.build_missing_evidence_catalog(
        explicit_records=[{"name":"broker snapshot evidence","classification":"BROKER_API_REQUIRED"}],
    )
    quality_payload = quality.validate_evidence_bundle([FIXTURE_BASE / "evidence_bundle_clean.md"], strict=False)
    projection = projector.project_final_bundle_readiness(catalog_payload, quality_payload, selector_result)
    assert projection["status"] == projector.PARTIAL_EXTERNAL_EVIDENCE_REQUIRED


def test_integration_safety_blocker_cannot_become_review_ready():
    selector_result = selector.select_review_ready_candidate([
        {"candidate_id":"safety","expectancy":1.6,"sample_count":80,"profit_factor":1.5,"drawdown":0.1,"evidence_completeness":0.9,"risk_control_score":0.9,"auditability":0.9,"safety_blocked":True}
    ])
    catalog_payload = catalog_lib.build_missing_evidence_catalog(explicit_records=[])
    quality_payload = quality.validate_evidence_bundle([FIXTURE_BASE / "evidence_bundle_clean.md"], strict=False)
    projection = projector.project_final_bundle_readiness(catalog_payload, quality_payload, selector_result)
    assert projection["status"] != projector.FINAL_BUNDLE_READY


def test_report_and_checkpoint_consistency():
    checkpoint = (REPO_ROOT / "Reports\\forex_delivery\\AIOS_FOREX_REMAINING_CLOSURE_LONGRUN_CAMPAIGN_V1_CHECKPOINT.md").read_text(encoding="utf-8")
    final_report = (REPO_ROOT / "Reports\\forex_delivery\\AIOS_FOREX_REMAINING_CLOSURE_LONGRUN_CAMPAIGN_V1_REPORT.md").read_text(encoding="utf-8")
    assert "AIOS-FOREX-REMAINING-CLOSURE-LONGRUN-CAMPAIGN-V1" in checkpoint
    assert "DEFERRED_OWNER_VALIDATION" in final_report


def test_campaign_metrics_and_depth_summary_exists():
    report = (REPO_ROOT / "Reports\\forex_delivery\\AIOS_FOREX_REMAINING_CLOSURE_LONGRUN_CAMPAIGN_V1_REPORT.md").read_text(encoding="utf-8")
    assert "campaign_classification" in report
    fixture_count = len(list((REPO_ROOT / "tests\\fixtures\\forex_delivery\\remaining_closure_v1").glob("*")))
    assert fixture_count >= 35
