"""Generate a blocked HRQ-001 executable APPLY packet draft."""

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
    OUTPUT_PATH as APPROVAL_PATH,
)
from automation.operator_relief.hrq001_patch_safety_validator import (
    CANONICAL_TARGET,
    DIFF_PATH,
    DUPLICATE_SOURCE,
    OUTPUT_PATH as PATCH_SAFETY_VALIDATION_PATH,
)


REPORT_TYPE = "operator_relief_hrq001_executable_apply_packet_generator_v1"
OUTPUT_ROOT = Path("Reports/operator_relief/hrq001_apply_packet")
OUTPUT_PATH = OUTPUT_ROOT / "hrq001_executable_apply_packet.json"
PACKET_ID = "HRQ-001-executable-apply-packet-draft"
BLOCKED_ACTIONS = [
    "execute APPLY packet",
    "modify workflow docs",
    "delete duplicate file",
    "canonicalize",
    "touch HRQ-002",
    "touch HRQ-003",
    "modify protected docs",
    "stage files",
    "commit",
    "push",
]


@dataclass(frozen=True)
class HRQ001ExecutableApplyPacketResult:
    report_type: str
    generated_at: str
    executable: bool
    source_explicit_apply_approval: str
    source_patch_safety_validation: str
    source_draft_patch_diff: str
    packet_output_path: str
    packet: dict[str, Any]
    execution_status: str
    blocked_reasons: list[str]
    apply_execution_approved: bool
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


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _approval_allows_packet_preparation(approval: dict[str, Any]) -> bool:
    return (
        approval.get("apply_packet_preparation_approved") is True
        and approval.get("apply_execution_approved") is False
        and approval.get("approved_candidate_ids") == [CANDIDATE_ID]
        and approval.get("canonical_target") == CANONICAL_TARGET
        and approval.get("duplicate_source") == DUPLICATE_SOURCE
    )


def _blocked_reasons(approval: dict[str, Any], safety_validation: dict[str, Any], diff_text: str) -> list[str]:
    reasons: list[str] = []
    if not approval:
        reasons.append("explicit HRQ-001 apply preparation approval is missing")
    elif not _approval_allows_packet_preparation(approval):
        reasons.append("explicit approval does not match HRQ-001 preparation-only scope")
    if approval.get("apply_execution_approved") is not False:
        reasons.append("apply_execution_approved must remain false")
    if safety_validation.get("patch_validation_status") != "ACCEPTED":
        reasons.append("HRQ-001 patch safety validation is not accepted")
    if safety_validation.get("rejected_count") not in (0, None):
        reasons.append("HRQ-001 patch safety validation has rejections")
    if not diff_text.strip():
        reasons.append("HRQ-001 draft patch diff is missing")
    if DUPLICATE_SOURCE in diff_text:
        reasons.append("draft patch must not modify duplicate source file")
    if "HRQ-002" in diff_text or "HRQ-003" in diff_text:
        reasons.append("draft patch must not touch HRQ-002 or HRQ-003")
    return reasons


def _build_packet(approval: dict[str, Any], safety_validation: dict[str, Any], diff_text: str, blockers: list[str]) -> dict[str, Any]:
    return {
        "report_type": "operator_relief_hrq001_executable_apply_packet_draft_v1",
        "packet_id": PACKET_ID,
        "candidate_id": CANDIDATE_ID,
        "mode": "APPLY_PACKET_DRAFT",
        "execution_status": "BLOCKED",
        "executable": False,
        "apply_execution_approved": False,
        "apply_packet_preparation_approved": approval.get("apply_packet_preparation_approved") is True,
        "canonical_target": CANONICAL_TARGET,
        "duplicate_source": DUPLICATE_SOURCE,
        "delete_duplicate_approved": False,
        "canonicalization_approved": False,
        "approved_sections": list(APPROVED_SECTIONS),
        "approved_candidate_ids": [CANDIDATE_ID],
        "source_explicit_apply_approval": _normalize_path(APPROVAL_PATH),
        "source_patch_safety_validation": _normalize_path(PATCH_SAFETY_VALIDATION_PATH),
        "source_draft_patch_diff": _normalize_path(DIFF_PATH),
        "patch_diff": diff_text,
        "validation_evidence": {
            "patch_validation_status": safety_validation.get("patch_validation_status", "UNKNOWN"),
            "accepted_count": safety_validation.get("accepted_count", 0),
            "rejected_count": safety_validation.get("rejected_count", 0),
        },
        "blocked_actions": list(BLOCKED_ACTIONS),
        "blocked_reasons": list(blockers) or ["apply execution has not been explicitly approved"],
        "human_approval_requirements": [
            "A separate exact APPLY execution approval is required before source edits.",
            "The duplicate file must not be deleted by this packet.",
            "HRQ-002 and HRQ-003 must remain out of scope.",
        ],
        "apply_ready_paths": [],
        "safe_cleanup_paths": [],
        "safety": {
            "dry_run_only": True,
            "packet_generation_only": True,
            "workflow_docs_modified": False,
            "files_deleted": False,
            "canonicalization_performed": False,
            "protected_docs_modified": False,
            "hrq002_touched": False,
            "hrq003_touched": False,
            "apply_execution_approved": False,
            "apply_ready_paths_empty": True,
        },
        "recommended_next_action": "Review this packet only; do not execute until separate APPLY execution approval exists.",
    }


def build_packet(repo_root: Path) -> HRQ001ExecutableApplyPacketResult:
    root = repo_root.resolve()
    approval = _load_json(root / APPROVAL_PATH)
    safety_validation = _load_json(root / PATCH_SAFETY_VALIDATION_PATH)
    diff_text = _load_text(root / DIFF_PATH)
    blockers = _blocked_reasons(approval, safety_validation, diff_text)
    packet = _build_packet(approval, safety_validation, diff_text, blockers)
    return HRQ001ExecutableApplyPacketResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        source_explicit_apply_approval=_normalize_path(APPROVAL_PATH),
        source_patch_safety_validation=_normalize_path(PATCH_SAFETY_VALIDATION_PATH),
        source_draft_patch_diff=_normalize_path(DIFF_PATH),
        packet_output_path=_normalize_path(OUTPUT_PATH),
        packet=packet,
        execution_status="BLOCKED",
        blocked_reasons=packet["blocked_reasons"],
        apply_execution_approved=False,
        apply_ready_paths=[],
        safety={
            "executable": False,
            "dry_run_only": True,
            "packet_generation_only": True,
            "workflow_docs_modified": False,
            "files_deleted": False,
            "canonicalization_performed": False,
            "protected_docs_modified": False,
            "hrq002_touched": False,
            "hrq003_touched": False,
            "apply_execution_approved": False,
            "apply_ready_paths_empty": True,
        },
        recommended_next_action="Stop here unless the operator provides separate HRQ-001 APPLY execution approval.",
    )


def _output_path(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_PATH).resolve()
    allowed_root = (root / OUTPUT_ROOT).resolve()
    if not (output.parent == allowed_root and allowed_root in output.parents):
        raise ValueError("HRQ-001 executable APPLY packet must be written under Reports/operator_relief/hrq001_apply_packet/.")
    return output


def write_packet(result: HRQ001ExecutableApplyPacketResult, repo_root: Path) -> Path:
    path = _output_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result.packet, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate blocked HRQ-001 executable APPLY packet draft.")
    parser.add_argument("--write-report", action="store_true", help="Write blocked HRQ-001 APPLY packet draft.")
    args = parser.parse_args(argv)
    result = build_packet(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_report:
        payload["written_file"] = _normalize_path(write_packet(result, Path.cwd()))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
