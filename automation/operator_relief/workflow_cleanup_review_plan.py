"""Build a DRY_RUN-only review plan for workflow cleanup candidates."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_TYPE = "operator_relief_workflow_cleanup_review_plan_v1"
CANDIDATES_PATH = Path("Reports/operator_relief/approved_cleanup_candidates/approved_cleanup_candidates.json")
FINAL_GATE_PATH = Path("Reports/operator_relief/final_safety_gate/final_cleanup_safety_gate.json")
DECISION_PACKET_ROOT = Path("Reports/operator_relief/decision_packets")
OUTPUT_ROOT = Path("Reports/operator_relief/workflow_cleanup_review_plan")
JSON_OUTPUT_PATH = OUTPUT_ROOT / "workflow_cleanup_review_plan.json"
MARKDOWN_OUTPUT_PATH = OUTPUT_ROOT / "workflow_cleanup_review_plan.md"
REQUIRED_WORKFLOW_ITEMS = {
    "HRQ-001-worker_branch_and_lane_rules": {
        "label": "worker branch and lane rules",
        "diff_file": "worker_branch_lane_rules_decision_diff.json",
    },
    "HRQ-002-parallel_codex_workflow": {
        "label": "parallel codex workflow",
        "diff_file": "parallel_codex_workflow_decision_diff.json",
    },
    "HRQ-003-apply_routing_chain": {
        "label": "apply routing chain",
        "diff_file": "apply_routing_chain_decision_diff.json",
    },
}
BLOCKED_ACTIONS = [
    "modify workflow docs",
    "perform cleanup",
    "canonicalize",
    "generate APPLY packet",
    "modify protected governance/security docs",
    "stage files",
    "commit",
    "push",
]


@dataclass(frozen=True)
class WorkflowCleanupReviewPlanResult:
    report_type: str
    generated_at: str
    executable: bool
    source_approved_cleanup_candidates: str
    source_final_safety_gate: str
    source_decision_packet_root: str
    final_gate_status: str
    candidates_included: list[dict[str, Any]]
    candidates_included_count: int
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


def _headings(sections: Any) -> list[str]:
    if not isinstance(sections, list):
        return []
    headings: list[str] = []
    for section in sections:
        if isinstance(section, dict) and isinstance(section.get("heading"), str):
            headings.append(section["heading"])
        elif isinstance(section, dict) and isinstance(section.get("canonical_heading"), str):
            headings.append(section["canonical_heading"])
    return headings


def _conflict_headings(sections: Any) -> list[str]:
    if not isinstance(sections, list):
        return []
    headings: list[str] = []
    for section in sections:
        if isinstance(section, dict):
            canonical = section.get("canonical_heading")
            duplicate = section.get("duplicate_heading")
            if isinstance(canonical, str) and isinstance(duplicate, str):
                headings.append(f"{canonical} / {duplicate}")
            elif isinstance(canonical, str):
                headings.append(canonical)
    return headings


def _candidate_ids(candidates_payload: dict[str, Any]) -> set[str]:
    candidates = candidates_payload.get("approved_cleanup_candidates", [])
    if not isinstance(candidates, list):
        return set()
    return {str(item.get("item_id")) for item in candidates if isinstance(item, dict)}


def _plan_item(item_id: str, repo_root: Path, candidate_ids: set[str]) -> dict[str, Any]:
    config = REQUIRED_WORKFLOW_ITEMS[item_id]
    diff_path = repo_root / DECISION_PACKET_ROOT / config["diff_file"]
    diff = _load_json(diff_path)
    duplicate_unique = diff.get("duplicate_unique_authority") or diff.get("duplicate_only_sections") or []
    dependency_unique = diff.get("dependency_unique_authority") or []
    canonical_only = diff.get("canonical_only_sections") or []
    conflicts = diff.get("conflicting_sections") or []
    dependency_paths = diff.get("dependency_paths")
    if not isinstance(dependency_paths, list):
        dependency_paths = []
    return {
        "item_id": item_id,
        "label": config["label"],
        "candidate_present": item_id in candidate_ids,
        "source_decision_diff": _normalize_path(DECISION_PACKET_ROOT / config["diff_file"]),
        "canonical_file": diff.get("canonical_candidate"),
        "duplicate_file": diff.get("duplicate_candidate"),
        "dependency_only_files": [str(path) for path in dependency_paths],
        "sections_that_need_merge_review": _headings(duplicate_unique),
        "sections_that_conflict": _conflict_headings(conflicts),
        "sections_that_must_be_preserved": _headings(canonical_only) + _headings(dependency_unique),
        "blocked_actions": list(BLOCKED_ACTIONS),
        "required_evidence_before_apply": [
            "Read the canonical file and duplicate file directly.",
            "Read the decision diff report for this candidate.",
            "Confirm no protected governance/security file is in scope.",
            "Confirm dependency-only files remain evidence and are not canonicalized.",
            "Confirm a future APPLY packet names exact files and validators.",
            "Confirm human approval before any source document edit.",
        ],
        "recommended_next_human_decision": diff.get("recommended_human_decision") or "NEEDS_HUMAN_REVIEW",
        "safe_to_generate_apply_packet_later": bool(diff.get("safe_to_generate_apply_packet_later", False)),
        "review_only": True,
        "executable": False,
    }


def build_plan(repo_root: Path) -> WorkflowCleanupReviewPlanResult:
    root = repo_root.resolve()
    candidates_payload = _load_json(root / CANDIDATES_PATH)
    final_gate = _load_json(root / FINAL_GATE_PATH)
    candidate_ids = _candidate_ids(candidates_payload)
    plan_items = [_plan_item(item_id, root, candidate_ids) for item_id in REQUIRED_WORKFLOW_ITEMS]
    return WorkflowCleanupReviewPlanResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        source_approved_cleanup_candidates=_normalize_path(CANDIDATES_PATH),
        source_final_safety_gate=_normalize_path(FINAL_GATE_PATH),
        source_decision_packet_root=_normalize_path(DECISION_PACKET_ROOT),
        final_gate_status=str(final_gate.get("final_status") or "UNKNOWN"),
        candidates_included=plan_items,
        candidates_included_count=len(plan_items),
        blocked_actions=list(BLOCKED_ACTIONS),
        safe_cleanup_paths=[],
        apply_ready_paths=[],
        safety={
            "executable": False,
            "dry_run_only": True,
            "review_plan_only": True,
            "workflow_docs_modified": False,
            "cleanup_performed": False,
            "canonicalization_performed": False,
            "apply_packet_generated": False,
            "protected_docs_modified": False,
            "safe_cleanup_paths_empty": True,
            "apply_ready_paths_empty": True,
        },
        recommended_next_action="Use this plan for manual review only; it does not authorize cleanup, canonicalization, or APPLY.",
    )


def render_markdown(result: WorkflowCleanupReviewPlanResult) -> str:
    lines = [
        "# Workflow Cleanup Review Plan",
        "",
        "```json",
        '{ "executable": false }',
        "```",
        "",
        f"- Final gate status: `{result.final_gate_status}`",
        f"- Candidates included: `{result.candidates_included_count}`",
        "- Safe cleanup paths: `[]`",
        "- Apply ready paths: `[]`",
        "",
    ]
    for item in result.candidates_included:
        lines.extend(
            [
                f"## {item['item_id']}",
                "",
                f"- Canonical file: `{item.get('canonical_file')}`",
                f"- Duplicate file: `{item.get('duplicate_file')}`",
                f"- Dependency-only files: `{', '.join(item['dependency_only_files']) or 'none'}`",
                f"- Recommended human decision: `{item['recommended_next_human_decision']}`",
                "",
                "### Sections That Need Merge Review",
                *[f"- {heading}" for heading in item["sections_that_need_merge_review"]],
                "",
                "### Sections That Conflict",
                *[f"- {heading}" for heading in item["sections_that_conflict"]],
                "",
                "### Sections That Must Be Preserved",
                *[f"- {heading}" for heading in item["sections_that_must_be_preserved"]],
                "",
                "### Blocked Actions",
                *[f"- {action}" for action in item["blocked_actions"]],
                "",
                "### Required Evidence Before APPLY",
                *[f"- {evidence}" for evidence in item["required_evidence_before_apply"]],
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _output_root(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_ROOT).resolve()
    allowed = (root / OUTPUT_ROOT).resolve()
    if not (output == allowed or allowed in output.parents):
        raise ValueError("Workflow cleanup review plan must be written under Reports/operator_relief/workflow_cleanup_review_plan/.")
    return output


def write_reports(result: WorkflowCleanupReviewPlanResult, repo_root: Path) -> list[Path]:
    output = _output_root(repo_root)
    output.mkdir(parents=True, exist_ok=True)
    json_path = repo_root.resolve() / JSON_OUTPUT_PATH
    markdown_path = repo_root.resolve() / MARKDOWN_OUTPUT_PATH
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(result.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    markdown_path.write_text(render_markdown(result), encoding="utf-8")
    return [json_path, markdown_path]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build DRY_RUN-only workflow cleanup review plan.")
    parser.add_argument("--write-report", action="store_true", help="Write JSON and markdown reports.")
    args = parser.parse_args(argv)
    result = build_plan(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_report:
        payload["written_files"] = [_normalize_path(path) for path in write_reports(result, Path.cwd())]
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
