from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief import hrq001_patch_safety_validator as validator


SAFE_DIFF = """--- docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md
+++ docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md (draft only)
@@ -16,6 +16,15 @@
 ```text
 worker/<lane>/<phase>-<short-task>
 ```
+
+Legacy worker branch examples for human review:
+
+```text
+worker/work-intelligence/phase-21-branch-rules
+worker/operator-orchestration/phase-22-file-ownership
+worker/dashboard-ui/phase-15-centerpiece-review
+```
+
@@ -135,6 +144,8 @@
 ## Collision Handling
 
+Worker reports should include planned files and validation commands. The integration lane checks those reports before any merge or APPLY review.
+ 
"""


def _safe_json(**overrides: object) -> dict:
    payload = {
        "canonical_target": validator.CANONICAL_TARGET,
        "duplicate_source": validator.DUPLICATE_SOURCE,
        "executable": False,
        "apply_ready_paths": [],
        "sections_included": [
            {"source_section": "Branch Naming"},
            {"source_section": "Report Rules"},
        ],
        "recommended_next_action": "Human review must approve exact text before any future APPLY packet is created.",
        "safety": {
            "workflow_docs_modified": False,
            "files_deleted": False,
            "canonicalization_performed": False,
            "executable_apply_packet_generated": False,
            "protected_docs_modified": False,
            "hrq002_touched": False,
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


def test_accepts_safe_hrq001_patch(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = validator.build_validation(tmp_path).to_dict()

    assert result["patch_validation_status"] == "ACCEPTED"
    assert result["accepted_count"] == 1
    assert result["rejected_count"] == 0
    assert result["rejection_reasons"] == []


def test_rejects_wrong_patch_target(tmp_path: Path) -> None:
    _write_inputs(tmp_path, SAFE_DIFF.replace(validator.CANONICAL_TARGET, "docs/workflows/PARALLEL_CODEX_WORKFLOW.md", 1))
    result = validator.build_validation(tmp_path).to_dict()

    assert result["patch_validation_status"] == "REJECTED"
    assert "patch must target only docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md" in result["rejection_reasons"]


def test_rejects_duplicate_source_modification(tmp_path: Path) -> None:
    diff_text = SAFE_DIFF + f"\n--- {validator.DUPLICATE_SOURCE}\n+++ {validator.DUPLICATE_SOURCE} (draft only)\n"
    _write_inputs(tmp_path, diff_text)
    result = validator.build_validation(tmp_path).to_dict()

    assert "patch must not modify duplicate source file" in result["rejection_reasons"]


def test_rejects_deletions(tmp_path: Path) -> None:
    _write_inputs(tmp_path, SAFE_DIFF + "-removed line\n")
    result = validator.build_validation(tmp_path).to_dict()

    assert "patch must not delete files or remove lines" in result["rejection_reasons"]


def test_rejects_missing_allowed_text(tmp_path: Path) -> None:
    _write_inputs(tmp_path, SAFE_DIFF.replace("worker/dashboard-ui/phase-15-centerpiece-review", ""))
    result = validator.build_validation(tmp_path).to_dict()

    assert any("worker/dashboard-ui/phase-15-centerpiece-review" in reason for reason in result["rejection_reasons"])


def test_rejects_protected_or_hrq002_hrq003_scope(tmp_path: Path) -> None:
    _write_inputs(tmp_path, SAFE_DIFF + "+HRQ-002 docs/governance/example.md\n")
    result = validator.build_validation(tmp_path).to_dict()

    assert "disallowed scope term found: HRQ-002" in result["rejection_reasons"]
    assert "disallowed scope term found: docs/governance/" in result["rejection_reasons"]


def test_rejects_unsafe_patch_json_metadata(tmp_path: Path) -> None:
    unsafe = _safe_json(
        executable=True,
        apply_ready_paths=["docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md"],
        safety={**_safe_json()["safety"], "workflow_docs_modified": True},
    )
    _write_inputs(tmp_path, patch_json=unsafe)
    result = validator.build_validation(tmp_path).to_dict()

    assert "patch json executable=true is rejected" in result["rejection_reasons"]
    assert "apply_ready_paths must be empty" in result["rejection_reasons"]
    assert "safety.workflow_docs_modified must be false" in result["rejection_reasons"]


def test_rejects_wrong_sections_included(tmp_path: Path) -> None:
    patch_json = _safe_json(sections_included=[{"source_section": "Allowed Worker Lanes"}])
    _write_inputs(tmp_path, patch_json=patch_json)
    result = validator.build_validation(tmp_path).to_dict()

    assert "sections_included must be exactly Branch Naming and Report Rules" in result["rejection_reasons"]


def test_write_validation_writes_only_under_patch_root(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = validator.build_validation(tmp_path)
    written = validator.write_validation(result, tmp_path)

    assert written.resolve().parent == (tmp_path / validator.PATCH_ROOT).resolve()
    assert written.name == "hrq001_patch_safety_validation.json"


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
    assert result["safety"]["hrq002_touched"] is False
    assert result["safety"]["hrq003_touched"] is False


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/hrq001_patch_safety_validator.py").read_text(encoding="utf-8")
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
