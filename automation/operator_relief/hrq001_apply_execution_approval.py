"""Generate explicit HRQ-001 APPLY execution approval evidence."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.operator_relief.hrq001_explicit_apply_approval import (
    APPROVED_SECTIONS,
    CANDIDATE_ID,
)
from automation.operator_relief.hrq001_executable_apply_packet_generator import (
    OUTPUT_ROOT,
)
from automation.operator_relief.hrq001_patch_safety_validator import (
    CANONICAL_TARGET,
    DUPLICATE_SOURCE,
    OUTPUT_PATH as PATCH_SAFETY_VALIDATION_PATH,
)


REPORT_TYPE = "operator_relief_hrq001_apply_execution_approval_v1"
OUTPUT_PATH = OUTPUT_ROOT / "hrq001_apply_execution_approval.json"


@dataclass(frozen=True)
class HRQ001ApplyExecutionApprovalResult:
    report_type: str
    generated_at: str
    executable: bool
    source_patch_safety_validation: str
    approval_output_path: str
    approval: dict[str, Any]
    apply_execution_approved: bool
    approved_candidate_ids: list[str]
    approved_sections: list[dict[str, str]]
    apply_ready_paths: list[str]
    safety: dict[str, Any]
    recommended_next_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _approval_blockers(repo_root: Path) -> list[str]:
    safety_validation = _load_json(repo_root.resolve() / PATCH_SAFETY_VALIDATION_PATH)
    blockers: list[str] = []
    if safety_validation.get("patch_validation_status") != "ACCEPTED":
        blockers.append("HRQ-001 patch safety validation is not accepted")
    if safety_validation.get("rejected_count") not in (0, None):
        blockers.append("HRQ-001 patch safety validation has rejections")
    if safety_validation.get("canonical_target") not in (CANONICAL_TARGET, None):
        blockers.append("patch safety validation canonical target mismatch")
    if safety_validation.get("duplicate_source") not in (DUPLICATE_SOURCE, None):
        blockers.append("patch safety validation duplicate source mismatch")
    return blockers


def build_approval(repo_root: Path) -> HRQ001ApplyExecutionApprovalResult:
    blockers = _approval_blockers(repo_root)
    approval = {
        "approval_type": "HRQ001_APPLY_EXECUTION_PREPARATION_ONLY",
        "operator_approval_statement": "I explicitly approve HRQ-001 APPLY execution preparation only.",
        "scope": "apply the validated HRQ-001 patch to docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md",
        "reviewer": "operator",
        "approved_candidate_ids": [CANDIDATE_ID],
        "canonical_target": CANONICAL_TARGET,
        "duplicate_source": DUPLICATE_SOURCE,
        "approved_sections": list(APPROVED_SECTIONS),
        "apply_execution_approved": not blockers,
        "apply_packet_generation_approved": not blockers,
        "apply_patch_itself": False,
        "workflow_docs_modified": False,
        "delete_duplicate_approved": False,
        "canonicalization_approved": False,
        "hrq002_approved": False,
        "hrq003_approved": False,
        "protected_docs_approved": False,
        "blockers": blockers,
        "executable": False,
        "apply_ready_paths": [],
    }
    return HRQ001ApplyExecutionApprovalResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        source_patch_safety_validation=_normalize_path(PATCH_SAFETY_VALIDATION_PATH),
        approval_output_path=_normalize_path(OUTPUT_PATH),
        approval=approval,
        apply_execution_approved=not blockers,
        approved_candidate_ids=[CANDIDATE_ID],
        approved_sections=list(APPROVED_SECTIONS),
        apply_ready_paths=[],
        safety={
            "executable": False,
            "dry_run_only": True,
            "approval_file_only": True,
            "workflow_docs_modified": False,
            "files_deleted": False,
            "canonicalization_performed": False,
            "apply_patch_performed": False,
            "protected_docs_modified": False,
            "hrq002_touched": False,
            "hrq003_touched": False,
            "apply_ready_paths_empty": True,
        },
        recommended_next_action="Use this approval only as evidence for a later HRQ-001 APPLY packet; this step does not change source files.",
    )


def _output_path(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_PATH).resolve()
    allowed_root = (root / OUTPUT_ROOT).resolve()
    if not (output.parent == allowed_root and allowed_root in output.parents):
        raise ValueError("HRQ-001 apply execution approval must be written under Reports/operator_relief/hrq001_apply_packet/.")
    return output


def write_approval(result: HRQ001ApplyExecutionApprovalResult, repo_root: Path) -> Path:
    path = _output_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result.approval, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate explicit HRQ-001 APPLY execution approval evidence.")
    parser.add_argument("--write-approval", action="store_true", help="Write HRQ-001 execution approval file.")
    args = parser.parse_args(argv)
    result = build_approval(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_approval:
        payload["written_file"] = _normalize_path(write_approval(result, Path.cwd()))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
