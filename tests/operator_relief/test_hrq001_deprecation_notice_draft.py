from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief import hrq001_deprecation_notice_draft as draft


def test_draft_targets_duplicate_and_canonical_replacement(tmp_path: Path) -> None:
    result = draft.build_draft(tmp_path).to_dict()

    assert result["duplicate_path"] == "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md"
    assert result["canonical_replacement"] == "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md"
    assert result["report_type"] == "operator_relief_hrq001_deprecation_notice_draft_v1"


def test_notice_text_marks_duplicate_reference_only(tmp_path: Path) -> None:
    result = draft.build_draft(tmp_path).to_dict()
    notice = result["notice_markdown"]

    assert "Deprecated duplicate / reference-only HRQ-001 document" in notice
    assert "Current canonical workflow authority lives in `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md`" in notice
    assert "Do not treat this file as active workflow authority" in notice


def test_notice_does_not_authorize_delete_or_archive(tmp_path: Path) -> None:
    notice = draft.build_draft(tmp_path).to_dict()["notice_markdown"]

    assert "Do not delete or archive this file without a separate approved retirement APPLY packet" in notice


def test_output_contract_is_dry_run_and_draft_only(tmp_path: Path) -> None:
    result = draft.build_draft(tmp_path).to_dict()
    safety = result["safety"]

    assert result["executable"] is False
    assert result["draft_only"] is True
    assert safety["duplicate_file_modified"] is False
    assert safety["files_deleted"] is False
    assert safety["references_updated"] is False
    assert safety["canonicalization_performed"] is False
    assert safety["hrq002_touched"] is False
    assert safety["hrq003_touched"] is False


def test_blocked_actions_include_required_boundaries(tmp_path: Path) -> None:
    actions = draft.build_draft(tmp_path).to_dict()["blocked_actions"]

    assert "modify duplicate file" in actions
    assert "delete files" in actions
    assert "update references" in actions
    assert "touch HRQ-002" in actions
    assert "touch HRQ-003" in actions


def test_write_reports_writes_only_under_duplicate_retirement_root(tmp_path: Path) -> None:
    result = draft.build_draft(tmp_path)
    written = draft.write_reports(result, tmp_path)

    assert [path.name for path in written] == ["hrq001_deprecation_notice_draft.json", "hrq001_deprecation_notice_draft.md"]
    assert all(path.resolve().parent == (tmp_path / draft.OUTPUT_ROOT).resolve() for path in written)
    payload = json.loads(written[0].read_text(encoding="utf-8"))
    assert payload["executable"] is False
    assert payload["notice_markdown"] == result.notice_markdown


def test_render_markdown_contains_notice_and_safety_header(tmp_path: Path) -> None:
    result = draft.build_draft(tmp_path)
    markdown = draft.render_markdown(result)

    assert "# HRQ-001 Deprecation Notice Draft" in markdown
    assert '{ "executable": false, "draft_only": true }' in markdown
    assert result.notice_markdown in markdown


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/hrq001_deprecation_notice_draft.py").read_text(encoding="utf-8")
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
