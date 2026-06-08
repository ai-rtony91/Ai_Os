"""Fill human review decision files from explicit operator decision intent."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.operator_relief.human_decision_intake_validator import PACKET_ROOT
from automation.operator_relief.human_review_decision_schema import validate_decision


REPORT_TYPE = "operator_relief_human_decision_file_filler_v1"
TEMPLATE_ROOT = Path("Reports/operator_relief/human_review_decisions/templates")
OUTPUT_ROOT = Path("Reports/operator_relief/human_review_decisions/filled")
APPROVED_CANDIDATE_PATH = Path("Reports/operator_relief/approved_cleanup_candidates/approved_cleanup_candidates.json")
REVIEWER = "operator"
WORKFLOW_DECISION = "MERGE_DUPLICATE_INTO_CANONICAL_LATER"
PROTECTED_DECISION = "PARK_UNTIL_GOVERNANCE_REVIEW"
DEPENDENCY_DECISION = "MARK_DEPENDENCY_ONLY"


@dataclass(frozen=True)
class HumanDecisionFileFillerResult:
    report_type: str
    generated_at: str
    executable: bool
    source_templates: str
    source_packets: str
    output_root: str
    reviewer: str
    decisions: list[dict[str, Any]]
    decision_files_generated_count: int
    decisions_applied_by_category: dict[str, int]
    filled_validation_accepted_count: int
    filled_validation_rejected_count: int
    filled_validation_rejections: list[dict[str, Any]]
    approved_cleanup_candidate_count: int
    safe_cleanup_paths: list[str]
    apply_ready_paths: list[str]
    safety: dict[str, Any]
    recommended_next_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return _load_json(path)


def _template_files(repo_root: Path) -> list[Path]:
    template_root = repo_root / TEMPLATE_ROOT
    if not template_root.exists():
        return []
    return sorted(path for path in template_root.glob("*.json") if path.is_file())


def _known_packet_ids(repo_root: Path) -> set[str]:
    packet_root = repo_root / PACKET_ROOT
    if not packet_root.exists():
        return set()
    return {path.stem for path in packet_root.glob("*.md") if path.is_file()}


def _category_for_item(item_id: str) -> str:
    if item_id.startswith(("HRQ-001-", "HRQ-002-", "HRQ-003-")):
        return "workflow_conflict"
    if item_id.startswith(("HRQ-004-", "HRQ-005-", "HRQ-006-")):
        return "protected_authority"
    return "dependency_or_non_canonical_dependency"


def _decision_for_category(category: str) -> str:
    if category == "workflow_conflict":
        return WORKFLOW_DECISION
    if category == "protected_authority":
        return PROTECTED_DECISION
    return DEPENDENCY_DECISION


def _rationale_for_category(category: str) -> str:
    if category == "workflow_conflict":
        return "Operator approved future merge review for workflow conflict items 1-3; this does not authorize cleanup or APPLY."
    if category == "protected_authority":
        return "Operator approved parking protected authority items 4-6 until governance review; this does not authorize cleanup."
    return "Operator marked dependency-only or non-canonical dependency item as dependency-only; this does not authorize cleanup."


def _filled_decision(template: dict[str, Any]) -> dict[str, Any]:
    item_id = str(template.get("item_id") or template.get("packet_id") or "")
    category = _category_for_item(item_id)
    return {
        **template,
        "packet_id": item_id,
        "item_id": item_id,
        "reviewer": REVIEWER,
        "decision": _decision_for_category(category),
        "rationale": _rationale_for_category(category),
        "cleanup_approved": False,
        "canonicalization_approved": False,
        "apply_packet_generated": False,
        "executable": False,
        "safe_cleanup_paths": [],
        "apply_ready_paths": [],
    }


def _validate_filled_decision(decision: dict[str, Any], known_packet_ids: set[str]) -> list[str]:
    errors = validate_decision(decision)
    rationale = decision.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        errors.append("rationale field is required")
    item_id = decision.get("item_id")
    if not isinstance(item_id, str) or item_id not in known_packet_ids:
        errors.append(f"unknown packet item id: {item_id}")
    return errors


def _approved_candidate_count(repo_root: Path) -> int:
    payload = _optional_json(repo_root / APPROVED_CANDIDATE_PATH)
    return int(payload.get("approved_cleanup_candidate_count", 0) or 0)


def build_decisions(repo_root: Path) -> HumanDecisionFileFillerResult:
    root = repo_root.resolve()
    known_packet_ids = _known_packet_ids(root)
    decisions: list[dict[str, Any]] = []
    rejections: list[dict[str, Any]] = []
    counts = {
        "workflow_conflict": 0,
        "protected_authority": 0,
        "dependency_or_non_canonical_dependency": 0,
    }

    for template_file in _template_files(root):
        template = _load_json(template_file)
        decision = _filled_decision(template)
        item_id = str(decision.get("item_id") or "")
        category = _category_for_item(item_id)
        counts[category] += 1
        errors = _validate_filled_decision(decision, known_packet_ids)
        output_path = OUTPUT_ROOT / f"{item_id}.json"
        decisions.append(
            {
                "item_id": item_id,
                "category": category,
                "decision": decision["decision"],
                "source_template": _normalize_path(template_file.relative_to(root)),
                "output_path": _normalize_path(output_path),
                "valid": not errors,
                "decision_file": decision,
            }
        )
        if errors:
            rejections.append(
                {
                    "item_id": item_id,
                    "category": category,
                    "errors": errors,
                    "source_template": _normalize_path(template_file.relative_to(root)),
                }
            )

    return HumanDecisionFileFillerResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        source_templates=_normalize_path(TEMPLATE_ROOT),
        source_packets=_normalize_path(PACKET_ROOT),
        output_root=_normalize_path(OUTPUT_ROOT),
        reviewer=REVIEWER,
        decisions=decisions,
        decision_files_generated_count=len(decisions),
        decisions_applied_by_category=counts,
        filled_validation_accepted_count=len(decisions) - len(rejections),
        filled_validation_rejected_count=len(rejections),
        filled_validation_rejections=rejections,
        approved_cleanup_candidate_count=_approved_candidate_count(root),
        safe_cleanup_paths=[],
        apply_ready_paths=[],
        safety={
            "executable": False,
            "dry_run_only": True,
            "decision_files_only": True,
            "approvals_created": False,
            "approvals_inferred": False,
            "cleanup_approved": False,
            "canonicalization_approved": False,
            "apply_packet_generated": False,
            "safe_cleanup_paths_empty": True,
            "apply_ready_paths_empty": True,
        },
        recommended_next_action="Run the human decision intake validator before any later candidate generation step.",
    )


def _output_root(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_ROOT).resolve()
    allowed = (root / OUTPUT_ROOT).resolve()
    if not (output == allowed or allowed in output.parents):
        raise ValueError("Filled human decision files must be written under Reports/operator_relief/human_review_decisions/filled/.")
    return output


def write_decisions(result: HumanDecisionFileFillerResult, repo_root: Path) -> list[Path]:
    output = _output_root(repo_root)
    output.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for item in result.decisions:
        decision_file = item["decision_file"]
        path = output / f"{decision_file['item_id']}.json"
        with path.open("w", encoding="utf-8") as handle:
            json.dump(decision_file, handle, indent=2, sort_keys=True)
            handle.write("\n")
        written.append(path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fill DRY_RUN-only human decision files from operator intent.")
    parser.add_argument("--write-decisions", action="store_true", help="Write filled decision files under Reports/operator_relief/human_review_decisions/filled/.")
    args = parser.parse_args(argv)
    result = build_decisions(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_decisions:
        payload["written_files"] = [_normalize_path(path) for path in write_decisions(result, Path.cwd())]
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
