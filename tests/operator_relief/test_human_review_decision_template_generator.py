from __future__ import annotations

from pathlib import Path

from automation.operator_relief import human_review_decision_template_generator as generator


def _write_packet(repo_root: Path, item_id: str) -> None:
    packet_root = repo_root / generator.PACKET_ROOT
    packet_root.mkdir(parents=True, exist_ok=True)
    (packet_root / f"{item_id}.md").write_text("# Human Review Packet\n", encoding="utf-8")


def test_builds_blank_template_for_each_packet(tmp_path: Path) -> None:
    _write_packet(tmp_path, "HRQ-001-worker_branch_and_lane_rules")
    _write_packet(tmp_path, "HRQ-002-parallel_codex_workflow")

    result = generator.build_templates(tmp_path).to_dict()

    assert result["templates_generated_count"] == 2
    item_ids = [item["template"]["item_id"] for item in result["templates"]]
    assert item_ids == [
        "HRQ-001-worker_branch_and_lane_rules",
        "HRQ-002-parallel_codex_workflow",
    ]


def test_template_fields_are_blank_and_not_approved(tmp_path: Path) -> None:
    _write_packet(tmp_path, "HRQ-001-worker_branch_and_lane_rules")
    result = generator.build_templates(tmp_path).to_dict()
    template = result["templates"][0]["template"]

    assert template["packet_id"] == "HRQ-001-worker_branch_and_lane_rules"
    assert template["item_id"] == "HRQ-001-worker_branch_and_lane_rules"
    assert template["reviewer"] == ""
    assert template["decision"] == ""
    assert template["rationale"] == ""
    assert template["cleanup_approved"] is False
    assert template["canonicalization_approved"] is False
    assert template["apply_packet_generated"] is False
    assert template["executable"] is False
    assert template["safe_cleanup_paths"] == []
    assert template["apply_ready_paths"] == []


def test_template_includes_allowed_decisions(tmp_path: Path) -> None:
    _write_packet(tmp_path, "HRQ-001-worker_branch_and_lane_rules")
    result = generator.build_templates(tmp_path).to_dict()
    template = result["templates"][0]["template"]

    assert "KEEP_CANONICAL_AS_IS" in template["allowed_decisions"]
    assert "MERGE_DUPLICATE_INTO_CANONICAL_LATER" in template["allowed_decisions"]
    assert "MARK_DEPENDENCY_ONLY" in template["allowed_decisions"]


def test_missing_packet_directory_generates_zero_templates(tmp_path: Path) -> None:
    result = generator.build_templates(tmp_path).to_dict()

    assert result["templates_generated_count"] == 0
    assert result["templates"] == []
    assert result["safe_cleanup_paths"] == []
    assert result["apply_ready_paths"] == []


def test_write_templates_writes_only_under_templates_root(tmp_path: Path) -> None:
    _write_packet(tmp_path, "HRQ-001-worker_branch_and_lane_rules")
    result = generator.build_templates(tmp_path)
    written = generator.write_templates(result, tmp_path)

    assert len(written) == 1
    assert written[0].resolve().parent == (tmp_path / generator.OUTPUT_ROOT).resolve()
    assert written[0].name == "HRQ-001-worker_branch_and_lane_rules.json"


def test_output_contract_is_not_executable_and_no_apply_packet(tmp_path: Path) -> None:
    _write_packet(tmp_path, "HRQ-001-worker_branch_and_lane_rules")
    result = generator.build_templates(tmp_path).to_dict()

    assert result["executable"] is False
    assert result["safe_cleanup_paths"] == []
    assert result["apply_ready_paths"] == []
    assert result["safety"]["blank_templates_only"] is True
    assert result["safety"]["decisions_selected"] is False
    assert result["safety"]["approvals_created"] is False
    assert result["safety"]["approvals_inferred"] is False
    assert result["safety"]["cleanup_approved"] is False
    assert result["safety"]["canonicalization_approved"] is False
    assert result["safety"]["apply_packet_generated"] is False


def test_written_template_content_is_blank(tmp_path: Path) -> None:
    _write_packet(tmp_path, "HRQ-001-worker_branch_and_lane_rules")
    result = generator.build_templates(tmp_path)
    written = generator.write_templates(result, tmp_path)
    content = written[0].read_text(encoding="utf-8")

    assert '"reviewer": ""' in content
    assert '"decision": ""' in content
    assert '"rationale": ""' in content
    assert '"executable": false' in content


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/human_review_decision_template_generator.py").read_text(encoding="utf-8")
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
