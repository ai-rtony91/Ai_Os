from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief import hrq002_patch_safety_validator as validator


SAFE_DIFF = """--- docs/workflows/PARALLEL_CODEX_WORKFLOW.md
+++ docs/workflows/PARALLEL_CODEX_WORKFLOW.md (draft only)
@@ -15,6 +15,30 @@
 - The integration lane reviews reports before any APPLY, commit, push, or merge decision.
+
+## HRQ-002 Operational Details For Review
+
+### Worker Lanes
+
+| Worker | Lane | Scope |
+| --- | --- | --- |
+| 1 | Dashboard UI | `apps/dashboard` |
+
+### Start DRY_RUN Crew
+
+The launcher opens 8 labeled PowerShell windows.
+
+### Validate Worker Reports
+
+The validator checks registry, queue example, exactly 8 workers, fallback mode, no overlaps, and no deletes.
+
+### Controlled APPLY Lane
+
+The controlled lane asks before each APPLY and validates after each APPLY.
+
+### Git Rules
+
+Do not use `git add .`. Use explicit file paths only.
+
+### Standard Batch Validation
+
+Run `git diff --check` and `git status --short --branch`.
"""


def _safe_json(**overrides: object) -> dict:
    payload = {
        "canonical_target": validator.CANONICAL_TARGET,
        "duplicate_source": validator.DUPLICATE_SOURCE,
        "executable": False,
        "apply_ready_paths": [],
        "sections_included": [{"source_section": section} for section in validator.APPROVED_SECTIONS],
        "rollback_plan": ["Do not apply. Regenerate the draft from the canonical and duplicate source if needed."],
        "validation_commands": [
            "python -m py_compile automation/operator_relief/hrq002_apply_draft_patch.py",
            "python -m pytest tests/operator_relief/test_hrq002_apply_draft_patch.py",
        ],
        "safety": {
            "workflow_docs_modified": False,
            "files_deleted": False,
            "canonicalization_performed": False,
            "executable_apply_packet_generated": False,
            "protected_docs_modified": False,
            "hrq001_touched": False,
            "hrq003_touched": False,
        },
    }
    payload.update(overrides)
    return payload


def _write_inputs(repo_root: Path, diff_text: str = SAFE_DIFF, patch_json: dict | None = None) -> None:
    diff_path = repo_root / validator.DIFF_PATH
    json_path = repo_root / validator.PATCH_JSON_PATH
    diff_path.parent.mkdir(parents=True, exist_ok=True)
    diff_path.write_text(diff_text.replace("++++", "+++"), encoding="utf-8")
    json_path.write_text(json.dumps(patch_json or _safe_json()), encoding="utf-8")


def test_accepts_safe_hrq002_patch(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = validator.build_validation(tmp_path).to_dict()

    assert result["patch_validation_status"] == "ACCEPTED"
    assert result["accepted_count"] == 1
    assert result["rejected_count"] == 0
    assert result["rejection_reasons"] == []


def test_rejects_wrong_patch_target(tmp_path: Path) -> None:
    _write_inputs(tmp_path, SAFE_DIFF.replace(validator.CANONICAL_TARGET, "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md", 1))
    result = validator.build_validation(tmp_path).to_dict()

    assert "patch must target only docs/workflows/PARALLEL_CODEX_WORKFLOW.md" in result["rejection_reasons"]


def test_rejects_duplicate_source_modification(tmp_path: Path) -> None:
    diff_text = SAFE_DIFF + f"\n--- {validator.DUPLICATE_SOURCE}\n+++ {validator.DUPLICATE_SOURCE} (draft only)\n"
    _write_inputs(tmp_path, diff_text)
    result = validator.build_validation(tmp_path).to_dict()

    assert "patch must not modify duplicate source file" in result["rejection_reasons"]


def test_rejects_deletions(tmp_path: Path) -> None:
    _write_inputs(tmp_path, SAFE_DIFF + "-removed line\n")
    result = validator.build_validation(tmp_path).to_dict()

    assert "patch must not delete files or remove lines" in result["rejection_reasons"]


def test_rejects_missing_approved_section(tmp_path: Path) -> None:
    _write_inputs(tmp_path, SAFE_DIFF.replace("### Controlled APPLY Lane", "### Removed"))
    result = validator.build_validation(tmp_path).to_dict()

    assert "approved section missing from draft diff: Controlled APPLY Lane" in result["rejection_reasons"]


def test_rejects_wrong_sections_included(tmp_path: Path) -> None:
    patch_json = _safe_json(sections_included=[{"source_section": "Worker Lanes"}])
    _write_inputs(tmp_path, patch_json=patch_json)
    result = validator.build_validation(tmp_path).to_dict()

    assert "sections_included must be exactly the six approved HRQ-002 sections" in result["rejection_reasons"]


def test_rejects_protected_or_other_hrq_scope(tmp_path: Path) -> None:
    _write_inputs(tmp_path, SAFE_DIFF + "+HRQ-001 docs/governance/example.md\n")
    result = validator.build_validation(tmp_path).to_dict()

    assert "disallowed scope term found: HRQ-001" in result["rejection_reasons"]
    assert "disallowed scope term found: docs/governance/" in result["rejection_reasons"]


def test_rejects_unsafe_patch_json_metadata(tmp_path: Path) -> None:
    unsafe = _safe_json(
        executable=True,
        apply_ready_paths=["docs/workflows/PARALLEL_CODEX_WORKFLOW.md"],
        safety={**_safe_json()["safety"], "workflow_docs_modified": True},
    )
    _write_inputs(tmp_path, patch_json=unsafe)
    result = validator.build_validation(tmp_path).to_dict()

    assert "patch json executable=true is rejected" in result["rejection_reasons"]
    assert "apply_ready_paths must be empty" in result["rejection_reasons"]
    assert "safety.workflow_docs_modified must be false" in result["rejection_reasons"]


def test_rejects_missing_rollback_or_validation_commands(tmp_path: Path) -> None:
    patch_json = _safe_json(rollback_plan=[], validation_commands=[])
    _write_inputs(tmp_path, patch_json=patch_json)
    result = validator.build_validation(tmp_path).to_dict()

    assert "rollback_plan must exist and be non-empty" in result["rejection_reasons"]
    assert "validation_commands must exist and be non-empty" in result["rejection_reasons"]


def test_write_validation_writes_only_under_patch_root(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = validator.build_validation(tmp_path)
    written = validator.write_validation(result, tmp_path)

    assert written.resolve().parent == (tmp_path / validator.PATCH_ROOT).resolve()
    assert written.name == "hrq002_patch_safety_validation.json"


def test_output_contract_is_not_executable_or_apply_ready(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = validator.build_validation(tmp_path).to_dict()

    assert result["executable"] is False
    assert result["apply_ready_paths"] == []
    assert result["safety"]["validation_only"] is True
    assert result["safety"]["workflow_docs_modified"] is False
    assert result["safety"]["files_deleted"] is False
    assert result["safety"]["canonicalization_performed"] is False
    assert result["safety"]["executable_apply_packet_generated"] is False
    assert result["safety"]["protected_docs_modified"] is False
    assert result["safety"]["hrq001_touched"] is False
    assert result["safety"]["hrq003_touched"] is False


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/hrq002_patch_safety_validator.py").read_text(encoding="utf-8")
    forbidden_terms = [
        "subprocess",
        "os.system",
        "Popen",
        "rmtree",
        "shutil.move",
        ".rename(",
        "Path.unlink",
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
