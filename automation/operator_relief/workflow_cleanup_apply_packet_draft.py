"""Generate review-only workflow cleanup APPLY packet drafts."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_TYPE = "operator_relief_workflow_cleanup_apply_packet_draft_v1"
REVIEW_PLAN_PATH = Path("Reports/operator_relief/workflow_cleanup_review_plan/workflow_cleanup_review_plan.json")
CANDIDATES_PATH = Path("Reports/operator_relief/approved_cleanup_candidates/approved_cleanup_candidates.json")
FINAL_GATE_PATH = Path("Reports/operator_relief/final_safety_gate/final_cleanup_safety_gate.json")
DECISION_PACKET_ROOT = Path("Reports/operator_relief/decision_packets")
OUTPUT_ROOT = Path("Reports/operator_relief/workflow_cleanup_apply_packet_drafts")
INDEX_OUTPUT_PATH = OUTPUT_ROOT / "workflow_cleanup_apply_packet_draft_index.json"
REQUIRED_CANDIDATES = [
    "HRQ-001-worker_branch_and_lane_rules",
    "HRQ-002-parallel_codex_workflow",
    "HRQ-003-apply_routing_chain",
]
DEFAULT_BLOCKED_ACTIONS = [
    "modify workflow docs",
    "perform cleanup",
    "canonicalize",
    "generate executable APPLY packet",
    "modify protected governance/security docs",
    "stage files",
    "commit",
    "push",
]


@dataclass(frozen=True)
class WorkflowCleanupApplyPacketDraftResult:
    report_type: str
    generated_at: str
    executable: bool
    review_only: bool
    source_review_plan: str
    source_approved_cleanup_candidates: str
    source_final_safety_gate: str
    source_decision_packet_root: str
    final_gate_status: str
    draft_packets: list[dict[str, Any]]
    draft_packets_generated_count: int
    candidates_covered: list[str]
    blocked_actions: list[str]
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


def _candidate_map(review_plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    candidates = review_plan.get("candidates_included", [])
    if not isinstance(candidates, list):
        return {}
    return {
        str(candidate.get("item_id")): candidate
        for candidate in candidates
        if isinstance(candidate, dict) and candidate.get("item_id")
    }


def _draft_filename(index: int) -> str:
    return f"workflow_cleanup_apply_packet_{index:03d}.json"


def _draft_packet(index: int, item: dict[str, Any]) -> dict[str, Any]:
    candidate_id = str(item.get("item_id") or "")
    blocked_actions = item.get("blocked_actions")
    if not isinstance(blocked_actions, list):
        blocked_actions = list(DEFAULT_BLOCKED_ACTIONS)
    dependency_files = item.get("dependency_only_files")
    if not isinstance(dependency_files, list):
        dependency_files = []
    return {
        "report_type": "operator_relief_workflow_cleanup_apply_packet_draft_item_v1",
        "draft_id": f"workflow_cleanup_apply_packet_{index:03d}",
        "candidate_id": candidate_id,
        "canonical_file": item.get("canonical_file"),
        "duplicate_files": [item.get("duplicate_file")] if item.get("duplicate_file") else [],
        "dependency_files": [str(path) for path in dependency_files],
        "conflicting_sections": list(item.get("sections_that_conflict") or []),
        "preserved_sections": list(item.get("sections_that_must_be_preserved") or []),
        "sections_that_need_merge_review": list(item.get("sections_that_need_merge_review") or []),
        "proposed_merge_sequence": [
            "Read canonical, duplicate, dependency, and decision diff evidence.",
            "Prepare a section-by-section merge proposal for human review.",
            "Keep dependency-only files as evidence and out of canonicalization scope.",
            "Request explicit human approval for exact source file edits before any future APPLY packet.",
            "Stop if protected governance/security scope appears.",
        ],
        "validation_requirements": [
            "Run exact-file diff review before any future APPLY.",
            "Run markdown or documentation validators assigned by the future APPLY packet.",
            "Run git diff --check only in a separately approved APPLY lane.",
            "Run targeted tests only if the future APPLY packet explicitly requires them.",
        ],
        "rollback_requirements": [
            "Future APPLY packet must name exact files and preserve pre-change evidence.",
            "Future APPLY packet must include a human-approved rollback or revert plan.",
            "Stop before staging if validation fails or scope expands.",
        ],
        "blocked_actions": [str(action) for action in blocked_actions],
        "human_approval_requirements": [
            "Human approval is required before any workflow document edit.",
            "Human approval is required before any canonicalization decision.",
            "Human approval is required before staging, committing, or pushing.",
            "This draft does not grant approval.",
        ],
        "executable": False,
        "review_only": True,
        "safe_cleanup_paths": [],
        "apply_ready_paths": [],
        "recommended_next_action": "Review this draft manually; do not execute it.",
    }


def build_drafts(repo_root: Path) -> WorkflowCleanupApplyPacketDraftResult:
    root = repo_root.resolve()
    review_plan = _load_json(root / REVIEW_PLAN_PATH)
    final_gate = _load_json(root / FINAL_GATE_PATH)
    candidates = _candidate_map(review_plan)
    drafts: list[dict[str, Any]] = []
    for index, candidate_id in enumerate(REQUIRED_CANDIDATES, start=1):
        item = candidates.get(candidate_id, {"item_id": candidate_id})
        draft = _draft_packet(index, item)
        drafts.append(
            {
                "candidate_id": candidate_id,
                "output_path": _normalize_path(OUTPUT_ROOT / _draft_filename(index)),
                "draft_packet": draft,
                "executable": False,
                "review_only": True,
            }
        )

    return WorkflowCleanupApplyPacketDraftResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        review_only=True,
        source_review_plan=_normalize_path(REVIEW_PLAN_PATH),
        source_approved_cleanup_candidates=_normalize_path(CANDIDATES_PATH),
        source_final_safety_gate=_normalize_path(FINAL_GATE_PATH),
        source_decision_packet_root=_normalize_path(DECISION_PACKET_ROOT),
        final_gate_status=str(final_gate.get("final_status") or review_plan.get("final_gate_status") or "UNKNOWN"),
        draft_packets=drafts,
        draft_packets_generated_count=len(drafts),
        candidates_covered=list(REQUIRED_CANDIDATES),
        blocked_actions=list(DEFAULT_BLOCKED_ACTIONS),
        safe_cleanup_paths=[],
        apply_ready_paths=[],
        safety={
            "executable": False,
            "dry_run_only": True,
            "draft_packets_only": True,
            "review_only": True,
            "workflow_docs_modified": False,
            "cleanup_performed": False,
            "canonicalization_performed": False,
            "executable_apply_packet_generated": False,
            "protected_docs_modified": False,
            "safe_cleanup_paths_empty": True,
            "apply_ready_paths_empty": True,
        },
        recommended_next_action="Review draft packets manually; they do not authorize source edits or APPLY execution.",
    )


def _output_root(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_ROOT).resolve()
    allowed = (root / OUTPUT_ROOT).resolve()
    if not (output == allowed or allowed in output.parents):
        raise ValueError("Workflow cleanup draft packets must be written under Reports/operator_relief/workflow_cleanup_apply_packet_drafts/.")
    return output


def write_reports(result: WorkflowCleanupApplyPacketDraftResult, repo_root: Path) -> list[Path]:
    output = _output_root(repo_root)
    output.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for index, item in enumerate(result.draft_packets, start=1):
        path = output / _draft_filename(index)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(item["draft_packet"], handle, indent=2, sort_keys=True)
            handle.write("\n")
        written.append(path)
    index_path = repo_root.resolve() / INDEX_OUTPUT_PATH
    with index_path.open("w", encoding="utf-8") as handle:
        json.dump(result.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    written.insert(0, index_path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build review-only workflow cleanup APPLY packet drafts.")
    parser.add_argument("--write-report", action="store_true", help="Write draft packet index and packet JSON files.")
    args = parser.parse_args(argv)
    result = build_drafts(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_report:
        payload["written_files"] = [_normalize_path(path) for path in write_reports(result, Path.cwd())]
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
