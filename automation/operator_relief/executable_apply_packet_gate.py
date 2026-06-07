"""Gate executable APPLY packet generation for workflow cleanup drafts."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.operator_relief.workflow_cleanup_apply_packet_draft import OUTPUT_ROOT


REPORT_TYPE = "operator_relief_executable_apply_packet_gate_v1"
SAFETY_VALIDATION_PATH = OUTPUT_ROOT / "draft_packet_safety_validation.json"
APPROVAL_PATH = OUTPUT_ROOT / "explicit_apply_approval.json"
OUTPUT_PATH = OUTPUT_ROOT / "executable_apply_packet_gate.json"
REQUIRED_APPROVAL_SCOPE = "workflow_cleanup_candidates"
REQUIRED_CANDIDATE_IDS = [
    "HRQ-001-worker_branch_and_lane_rules",
    "HRQ-002-parallel_codex_workflow",
    "HRQ-003-apply_routing_chain",
]
STATUS_BLOCKED = "BLOCKED"
STATUS_REVIEW_READY_WITH_EXPLICIT_APPROVAL = "REVIEW_READY_WITH_EXPLICIT_APPROVAL"


@dataclass(frozen=True)
class ExecutableApplyPacketGateResult:
    report_type: str
    generated_at: str
    executable: bool
    source_draft_packet_root: str
    source_draft_packet_safety_validation: str
    source_apply_approval: str
    gate_status: str
    block_reasons: list[str]
    accepted_draft_count: int
    rejected_draft_count: int
    required_approval: dict[str, Any]
    approval_present: bool
    approved_candidate_ids: list[str]
    safe_cleanup_paths: list[str]
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


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str)]


def _approval_errors(approval: dict[str, Any], approval_present: bool) -> list[str]:
    errors: list[str] = []
    if not approval_present:
        errors.append("explicit APPLY approval file is missing")
        return errors
    if approval.get("apply_approval") is not True:
        errors.append("apply_approval=true is required")
    if approval.get("approval_scope") != REQUIRED_APPROVAL_SCOPE:
        errors.append('approval_scope="workflow_cleanup_candidates" is required')
    approved_ids = sorted(_string_list(approval.get("approved_candidate_ids")))
    if approved_ids != sorted(REQUIRED_CANDIDATE_IDS):
        errors.append("approved_candidate_ids must match the 3 review-only candidates")
    if approval.get("executable") is True:
        errors.append("approval file executable=true is rejected")
    return errors


def build_gate(repo_root: Path) -> ExecutableApplyPacketGateResult:
    root = repo_root.resolve()
    safety_validation_path = root / SAFETY_VALIDATION_PATH
    approval_path = root / APPROVAL_PATH
    safety_validation = _load_json(safety_validation_path)
    approval = _load_json(approval_path)
    approval_present = approval_path.exists()
    block_reasons: list[str] = []

    accepted_count = int(safety_validation.get("accepted_count", 0) or 0)
    rejected_count = int(safety_validation.get("rejected_count", 0) or 0)
    if not safety_validation_path.exists():
        block_reasons.append("draft packet safety validation report is missing")
    if accepted_count != len(REQUIRED_CANDIDATE_IDS):
        block_reasons.append("all 3 review-only draft packets must pass safety validation")
    if rejected_count:
        block_reasons.append("draft packet safety validation contains rejected drafts")
    if safety_validation.get("executable") is True:
        block_reasons.append("draft packet safety validation executable=true is rejected")
    if _string_list(safety_validation.get("apply_ready_paths")):
        block_reasons.append("draft packet safety validation apply_ready_paths must be empty")

    block_reasons.extend(_approval_errors(approval, approval_present))
    approved_candidate_ids = _string_list(approval.get("approved_candidate_ids"))
    gate_status = STATUS_BLOCKED if block_reasons else STATUS_REVIEW_READY_WITH_EXPLICIT_APPROVAL
    return ExecutableApplyPacketGateResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        source_draft_packet_root=_normalize_path(OUTPUT_ROOT),
        source_draft_packet_safety_validation=_normalize_path(SAFETY_VALIDATION_PATH),
        source_apply_approval=_normalize_path(APPROVAL_PATH),
        gate_status=gate_status,
        block_reasons=block_reasons,
        accepted_draft_count=accepted_count,
        rejected_draft_count=rejected_count,
        required_approval={
            "apply_approval": True,
            "approval_scope": REQUIRED_APPROVAL_SCOPE,
            "approved_candidate_ids": list(REQUIRED_CANDIDATE_IDS),
        },
        approval_present=approval_present,
        approved_candidate_ids=approved_candidate_ids,
        safe_cleanup_paths=[],
        apply_ready_paths=[],
        safety={
            "executable": False,
            "dry_run_only": True,
            "gate_only": True,
            "workflow_docs_modified": False,
            "cleanup_performed": False,
            "canonicalization_performed": False,
            "executable_apply_packet_generated": False,
            "protected_docs_modified": False,
            "safe_cleanup_paths_empty": True,
            "apply_ready_paths_empty": True,
            "blocked": gate_status == STATUS_BLOCKED,
        },
        recommended_next_action=(
            "Do not generate executable APPLY packets while this gate is BLOCKED."
            if gate_status == STATUS_BLOCKED
            else "Explicit approval is present, but this gate still does not generate executable APPLY packets."
        ),
    )


def _output_path(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_PATH).resolve()
    allowed_root = (root / OUTPUT_ROOT).resolve()
    if not (output.parent == allowed_root and allowed_root in output.parents):
        raise ValueError("Executable APPLY packet gate must be written under Reports/operator_relief/workflow_cleanup_apply_packet_drafts/.")
    return output


def write_gate(result: ExecutableApplyPacketGateResult, repo_root: Path) -> Path:
    path = _output_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gate executable APPLY packet generation for workflow cleanup drafts.")
    parser.add_argument("--write-report", action="store_true", help="Write gate report under workflow cleanup draft Reports.")
    args = parser.parse_args(argv)
    result = build_gate(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_report:
        payload["written_file"] = _normalize_path(write_gate(result, Path.cwd()))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
