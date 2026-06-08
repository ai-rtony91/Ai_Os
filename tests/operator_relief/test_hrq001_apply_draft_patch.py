from __future__ import annotations

from pathlib import Path

from automation.operator_relief import hrq001_apply_draft_patch as patch


CANONICAL_TEXT = """# AI_OS Worker Branch And Lane Rules

## Branch Naming

Recommended branch pattern:

```text
worker/<lane>/<phase>-<short-task>
```

Branch names must be lowercase.

## Collision Handling

If two workers declare the same planned file, the conflict is blocked.
"""


DUPLICATE_TEXT = """# AI_OS Worker Branch And Lane Rules

## Branch Naming

Recommended branch format:

```text
worker/<lane>/<phase>-<short-task>
```

Examples:

```text
worker/work-intelligence/phase-21-branch-rules
worker/operator-orchestration/phase-22-file-ownership
worker/dashboard-ui/phase-15-centerpiece-review
```

## Report Rules

Each worker report must include planned files and validation commands. The integration lane checks those reports before any merge or APPLY review.
"""


def _write_inputs(repo_root: Path) -> None:
    canonical = repo_root / patch.CANONICAL_FILE
    duplicate = repo_root / patch.DUPLICATE_FILE
    canonical.parent.mkdir(parents=True, exist_ok=True)
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    canonical.write_text(CANONICAL_TEXT, encoding="utf-8")
    duplicate.write_text(DUPLICATE_TEXT, encoding="utf-8")


def test_build_patch_reports_target_and_source_paths(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = patch.build_patch(tmp_path).to_dict()

    assert result["canonical_target"] == "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md"
    assert result["duplicate_source"] == "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md"


def test_patch_includes_only_requested_sections(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = patch.build_patch(tmp_path).to_dict()

    assert [item["source_section"] for item in result["sections_included"]] == ["Branch Naming", "Report Rules"]
    assert "Allowed Worker Lanes" not in result["patch_diff"]
    assert "Path Rules" not in result["patch_diff"]


def test_patch_adds_legacy_branch_examples(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = patch.build_patch(tmp_path).to_dict()

    assert "Legacy worker branch examples for human review" in result["patch_diff"]
    assert "worker/work-intelligence/phase-21-branch-rules" in result["patch_diff"]
    assert "worker/operator-orchestration/phase-22-file-ownership" in result["patch_diff"]
    assert "worker/dashboard-ui/phase-15-centerpiece-review" in result["patch_diff"]


def test_patch_adds_concise_report_rule_wording(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = patch.build_patch(tmp_path).to_dict()

    assert "Worker reports should include planned files and validation commands." in result["patch_diff"]
    assert "The integration lane checks those reports before any merge or APPLY review." in result["patch_diff"]


def test_draft_does_not_modify_canonical_file(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    before = (tmp_path / patch.CANONICAL_FILE).read_text(encoding="utf-8")
    patch.build_patch(tmp_path)
    after = (tmp_path / patch.CANONICAL_FILE).read_text(encoding="utf-8")

    assert after == before


def test_output_contract_is_not_executable_or_apply_ready(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = patch.build_patch(tmp_path).to_dict()

    assert result["executable"] is False
    assert result["apply_ready_paths"] == []
    assert result["safety"]["patch_diff_only"] is True
    assert result["safety"]["workflow_docs_modified"] is False
    assert result["safety"]["files_deleted"] is False
    assert result["safety"]["canonicalization_performed"] is False
    assert result["safety"]["executable_apply_packet_generated"] is False
    assert result["safety"]["protected_docs_modified"] is False
    assert result["safety"]["hrq002_touched"] is False
    assert result["safety"]["hrq003_touched"] is False


def test_write_reports_writes_diff_json_and_markdown_under_output_root(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = patch.build_patch(tmp_path)
    written = patch.write_reports(result, tmp_path)

    assert [path.name for path in written] == [
        "hrq001_apply_draft_patch.diff",
        "hrq001_apply_draft_patch.json",
        "hrq001_apply_draft_patch.md",
    ]
    for path in written:
        assert path.resolve().parent == (tmp_path / patch.OUTPUT_ROOT).resolve()


def test_markdown_contains_diff_fence(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    markdown = patch.render_markdown(patch.build_patch(tmp_path))

    assert "# HRQ-001 Apply Draft Patch" in markdown
    assert '"executable": false' in markdown
    assert "```diff" in markdown


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/hrq001_apply_draft_patch.py").read_text(encoding="utf-8")
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
