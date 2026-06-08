from __future__ import annotations

from pathlib import Path

from automation.operator_relief import explicit_apply_approval_template as template


def test_template_defaults_do_not_approve_anything(tmp_path: Path) -> None:
    result = template.build_template(tmp_path).to_dict()
    payload = result["template"]

    assert payload["apply_approval"] is False
    assert payload["approval_scope"] == ""
    assert payload["approved_candidate_ids"] == []
    assert payload["reviewer"] == ""
    assert payload["rationale"] == ""
    assert payload["executable"] is False
    assert payload["apply_ready_paths"] == []
    assert result["default_approval_status"] is False


def test_template_includes_required_scope_and_eligible_candidates(tmp_path: Path) -> None:
    result = template.build_template(tmp_path).to_dict()
    payload = result["template"]

    assert payload["required_scope_value"] == "workflow_cleanup_candidates"
    assert payload["eligible_candidate_ids"] == [
        "HRQ-001-worker_branch_and_lane_rules",
        "HRQ-002-parallel_codex_workflow",
        "HRQ-003-apply_routing_chain",
    ]
    assert result["eligible_candidate_ids"] == payload["eligible_candidate_ids"]


def test_template_includes_blocked_categories(tmp_path: Path) -> None:
    result = template.build_template(tmp_path).to_dict()
    payload = result["template"]

    assert "protected_authority" in payload["blocked_categories"]
    assert "dependency_only" in payload["blocked_categories"]
    assert "non_canonical_dependency" in payload["blocked_categories"]


def test_template_includes_safety_acknowledgements(tmp_path: Path) -> None:
    result = template.build_template(tmp_path).to_dict()
    acknowledgements = result["template"]["safety_acknowledgements"]

    assert any("does not approve cleanup" in item for item in acknowledgements)
    assert any("does not generate executable APPLY packets" in item for item in acknowledgements)
    assert any("Protected governance/security docs remain blocked" in item for item in acknowledgements)


def test_output_contract_is_template_only(tmp_path: Path) -> None:
    result = template.build_template(tmp_path).to_dict()

    assert result["executable"] is False
    assert result["safe_cleanup_paths"] == []
    assert result["apply_ready_paths"] == []
    assert result["safety"]["template_only"] is True
    assert result["safety"]["apply_approval_default_false"] is True
    assert result["safety"]["approvals_created"] is False
    assert result["safety"]["approvals_inferred"] is False
    assert result["safety"]["workflow_docs_modified"] is False
    assert result["safety"]["cleanup_performed"] is False
    assert result["safety"]["canonicalization_performed"] is False
    assert result["safety"]["executable_apply_packet_generated"] is False
    assert result["safety"]["protected_docs_modified"] is False


def test_write_template_writes_only_under_draft_output_root(tmp_path: Path) -> None:
    result = template.build_template(tmp_path)
    written = template.write_template(result, tmp_path)

    assert written.resolve().parent == (tmp_path / template.OUTPUT_ROOT).resolve()
    assert written.name == "explicit_apply_approval_template.json"
    assert '"apply_approval": false' in written.read_text(encoding="utf-8")


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/explicit_apply_approval_template.py").read_text(encoding="utf-8")
    forbidden_terms = [
        "subprocess",
        "os.system",
        "Popen",
        "rmtree",
        "shutil.move",
        ".rename(",
        "Path.unlink",
        "git commit",
        "git push",
        "git merge",
        "git rebase",
        "OpenAI(",
        "openai.",
        "Codex(",
        "Start-Process",
        "watchdog",
        "HTTPServer",
        ".listen(",
        ".bind(",
    ]

    for term in forbidden_terms:
        assert term not in source
