"""Generate explicit HRQ-002 APPLY preparation approval evidence."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.operator_relief.hrq002_patch_safety_validator import (
    APPROVED_SECTIONS,
    CANONICAL_TARGET,
    DUPLICATE_SOURCE,
    OUTPUT_PATH as PATCH_SAFETY_VALIDATION_PATH,
    PATCH_JSON_PATH,
    PATCH_ROOT,
)


REPORT_TYPE = "operator_relief_hrq002_explicit_apply_approval_v1"
OUTPUT_PATH = PATCH_ROOT / "hrq002_explicit_apply_approval.json"
CANDIDATE_ID = "HRQ-002-parallel_codex_workflow"
APPROVED_SECTION_DETAILS = [
    {
        "source_section": section,
        "approved_content": "review-only operational detail for HRQ-002 APPLY packet preparation",
    }
    for section in APPROVED_SECTIONS
]


@dataclass(frozen=True)
class HRQ002ExplicitApplyApprovalResult:
    report_type: str
    generated_at: str
    executable: bool
    source_draft_patch: str
    source_patch_safety_validation: str
    approval_output_path: str
    approval: dict[str, Any]
    approved_candidate_ids: list[str]
    approved_sections: list[dict[str, str]]
    apply_packet_preparation_approved: bool
    apply_execution_approved: bool
    apply_ready_paths: list[str]
    safety: dict[str, Any]
    recommended_next_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def _repo_relative_path(path: Path, repo_root: Path) -> str:
    try:
        return _normalize_path(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return _normalize_path(path)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _approval_blockers(repo_root: Path) -> list[str]:
    root = repo_root.resolve()
    draft_patch = _load_json(root / PATCH_JSON_PATH)
    safety_validation = _load_json(root / PATCH_SAFETY_VALIDATION_PATH)
    blockers: list[str] = []
    if draft_patch.get("canonical_target") != CANONICAL_TARGET:
        blockers.append("draft patch canonical target does not match HRQ-002 canonical target")
    if draft_patch.get("duplicate_source") != DUPLICATE_SOURCE:
        blockers.append("draft patch duplicate source does not match HRQ-002 duplicate source")
    section_names = [
        item.get("source_section")
        for item in draft_patch.get("sections_included", [])
        if isinstance(item, dict)
    ]
    if section_names != APPROVED_SECTIONS:
        blockers.append("draft patch sections do not match the six approved HRQ-002 sections")
    if safety_validation.get("patch_validation_status") != "ACCEPTED":
        blockers.append("HRQ-002 patch safety validation is not accepted")
    if safety_validation.get("rejected_count") not in (0, None):
        blockers.append("HRQ-002 patch safety validation has rejections")
    return blockers


def build_approval(repo_root: Path) -> HRQ002ExplicitApplyApprovalResult:
    blockers = _approval_blockers(repo_root)
    preparation_approved = not blockers
    approval = {
        "approval_type": "HRQ002_APPLY_PREPARATION_ONLY",
        "operator_approval_statement": "I explicitly approve HRQ-002 APPLY packet preparation only.",
        "scope": "prepare an APPLY packet for the six approved HRQ-002 sections targeting docs/workflows/PARALLEL_CODEX_WORKFLOW.md",
        "reviewer": "operator",
        "approved_candidate_ids": [CANDIDATE_ID],
        "canonical_target": CANONICAL_TARGET,
        "duplicate_source": DUPLICATE_SOURCE,
        "approved_sections": list(APPROVED_SECTION_DETAILS),
        "apply_packet_preparation_approved": preparation_approved,
        "apply_execution_approved": False,
        "delete_duplicate_approved": False,
        "canonicalization_approved": False,
        "hrq001_approved": False,
        "hrq003_approved": False,
        "protected_docs_approved": False,
        "blockers": blockers,
        "executable": False,
        "apply_ready_paths": [],
    }
    return HRQ002ExplicitApplyApprovalResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        source_draft_patch=_normalize_path(PATCH_JSON_PATH),
        source_patch_safety_validation=_normalize_path(PATCH_SAFETY_VALIDATION_PATH),
        approval_output_path=_normalize_path(OUTPUT_PATH),
        approval=approval,
        approved_candidate_ids=[CANDIDATE_ID],
        approved_sections=list(APPROVED_SECTION_DETAILS),
        apply_packet_preparation_approved=preparation_approved,
        apply_execution_approved=False,
        apply_ready_paths=[],
        safety={
            "executable": False,
            "dry_run_only": True,
            "approval_file_only": True,
            "workflow_docs_modified": False,
            "files_deleted": False,
            "duplicate_file_delete_approved": False,
            "canonicalization_performed": False,
            "executable_apply_packet_generated": False,
            "apply_execution_approved": False,
            "protected_docs_modified": False,
            "hrq001_touched": False,
            "hrq003_touched": False,
            "apply_ready_paths_empty": True,
        },
        recommended_next_action="Use this approval only to draft a future HRQ-002 APPLY packet; it does not authorize execution.",
    )


def _output_path(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_PATH).resolve()
    allowed_root = (root / PATCH_ROOT).resolve()
    if not (output.parent == allowed_root and allowed_root in output.parents):
        raise ValueError("HRQ-002 explicit approval must be written under Reports/operator_relief/hrq002_apply_draft_patch/.")
    return output


def write_approval(result: HRQ002ExplicitApplyApprovalResult, repo_root: Path) -> Path:
    path = _output_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result.approval, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate explicit HRQ-002 APPLY preparation approval evidence.")
    parser.add_argument("--write-approval", action="store_true", help="Write HRQ-002 approval file.")
    args = parser.parse_args(argv)
    result = build_approval(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_approval:
        repo_root = Path.cwd()
        payload["written_file"] = _repo_relative_path(write_approval(result, repo_root), repo_root)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
