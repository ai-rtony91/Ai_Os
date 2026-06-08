from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief import hrq001_executable_apply_packet_generator as generator


SAFE_DIFF = """--- docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md
+++ docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md (draft only)
@@ -16,6 +16,15 @@
+Legacy worker branch examples for human review:
+worker/work-intelligence/phase-21-branch-rules
+worker/operator-orchestration/phase-22-file-ownership
+worker/dashboard-ui/phase-15-centerpiece-review
@@ -135,6 +144,8 @@
+Worker reports should include planned files and validation commands. The integration lane checks those reports before any merge or APPLY review.
"""


def _write_inputs(repo_root: Path, *, approval_execution: bool = False, safety_status: str = "ACCEPTED", diff_text: str = SAFE_DIFF) -> None:
    approval_path = repo_root / generator.APPROVAL_PATH
    safety_path = repo_root / generator.PATCH_SAFETY_VALIDATION_PATH
    diff_path = repo_root / generator.DIFF_PATH
    approval_path.parent.mkdir(parents=True, exist_ok=True)
    approval_path.write_text(
        json.dumps(
            {
                "apply_packet_preparation_approved": True,
                "apply_execution_approved": approval_execution,
                "approved_candidate_ids": [generator.CANDIDATE_ID],
                "canonical_target": generator.CANONICAL_TARGET,
                "duplicate_source": generator.DUPLICATE_SOURCE,
                "approved_sections": generator.APPROVED_SECTIONS,
                "executable": False,
                "apply_ready_paths": [],
            }
        ),
        encoding="utf-8",
    )
    safety_path.write_text(
        json.dumps(
            {
                "patch_validation_status": safety_status,
                "accepted_count": 1 if safety_status == "ACCEPTED" else 0,
                "rejected_count": 0 if safety_status == "ACCEPTED" else 1,
                "executable": False,
                "apply_ready_paths": [],
            }
        ),
        encoding="utf-8",
    )
    diff_path.write_text(diff_text.replace("++++", "+++"), encoding="utf-8")


def test_generates_blocked_hrq001_packet_only(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = generator.build_packet(tmp_path).to_dict()
    packet = result["packet"]

    assert result["execution_status"] == "BLOCKED"
    assert packet["candidate_id"] == "HRQ-001-worker_branch_and_lane_rules"
    assert packet["canonical_target"] == "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md"
    assert packet["duplicate_source"] == "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md"
    assert packet["approved_candidate_ids"] == ["HRQ-001-worker_branch_and_lane_rules"]


def test_packet_includes_only_approved_sections(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    packet = generator.build_packet(tmp_path).to_dict()["packet"]

    assert packet["approved_sections"] == [
        {"source_section": "Branch Naming", "approved_content": "legacy worker branch examples"},
        {"source_section": "Report Rules", "approved_content": "concise integration-lane report check wording"},
    ]


def test_execution_remains_blocked_even_with_preparation_approval(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = generator.build_packet(tmp_path).to_dict()
    packet = result["packet"]

    assert result["executable"] is False
    assert packet["executable"] is False
    assert result["apply_execution_approved"] is False
    assert packet["apply_execution_approved"] is False
    assert result["apply_ready_paths"] == []
    assert packet["apply_ready_paths"] == []
    assert "apply execution has not been explicitly approved" in packet["blocked_reasons"]


def test_rejects_apply_execution_approval_in_input(tmp_path: Path) -> None:
    _write_inputs(tmp_path, approval_execution=True)
    result = generator.build_packet(tmp_path).to_dict()

    assert result["execution_status"] == "BLOCKED"
    assert "explicit approval does not match HRQ-001 preparation-only scope" in result["blocked_reasons"]
    assert "apply_execution_approved must remain false" in result["blocked_reasons"]


def test_blocks_when_patch_safety_validation_not_accepted(tmp_path: Path) -> None:
    _write_inputs(tmp_path, safety_status="REJECTED")
    result = generator.build_packet(tmp_path).to_dict()

    assert "HRQ-001 patch safety validation is not accepted" in result["blocked_reasons"]
    assert "HRQ-001 patch safety validation has rejections" in result["blocked_reasons"]


def test_blocks_hrq002_or_hrq003_scope_in_diff(tmp_path: Path) -> None:
    _write_inputs(tmp_path, diff_text=SAFE_DIFF + "\n+HRQ-002\n+HRQ-003\n")
    result = generator.build_packet(tmp_path).to_dict()

    assert "draft patch must not touch HRQ-002 or HRQ-003" in result["blocked_reasons"]


def test_write_packet_writes_only_under_hrq001_apply_packet_root(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = generator.build_packet(tmp_path)
    written = generator.write_packet(result, tmp_path)

    assert written.resolve().parent == (tmp_path / generator.OUTPUT_ROOT).resolve()
    assert written.name == "hrq001_executable_apply_packet.json"
    payload = json.loads(written.read_text(encoding="utf-8"))
    assert payload["execution_status"] == "BLOCKED"
    assert payload["executable"] is False


def test_safety_flags_block_source_mutation_and_execution(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    result = generator.build_packet(tmp_path).to_dict()
    safety = result["safety"]
    packet_safety = result["packet"]["safety"]

    assert safety["workflow_docs_modified"] is False
    assert safety["files_deleted"] is False
    assert safety["canonicalization_performed"] is False
    assert safety["protected_docs_modified"] is False
    assert safety["hrq002_touched"] is False
    assert safety["hrq003_touched"] is False
    assert packet_safety["workflow_docs_modified"] is False
    assert packet_safety["apply_execution_approved"] is False


def test_source_scan_blocks_forbidden_runtime_actions() -> None:
    source = Path("automation/operator_relief/hrq001_executable_apply_packet_generator.py").read_text(encoding="utf-8")
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
