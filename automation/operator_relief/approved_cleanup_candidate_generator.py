"""Generate DRY_RUN-only cleanup candidates from validated human decisions."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_TYPE = "operator_relief_approved_cleanup_candidate_generator_v1"
INTAKE_VALIDATION_PATH = Path("Reports/operator_relief/human_review_decisions/human_decision_intake_validation.json")
OUTPUT_PATH = Path("Reports/operator_relief/approved_cleanup_candidates/approved_cleanup_candidates.json")
CANDIDATE_DECISIONS = {"MERGE_DUPLICATE_INTO_CANONICAL_LATER"}
PROTECTED_ALLOWED_DECISIONS = {"PARK_UNTIL_GOVERNANCE_REVIEW", "KEEP_BOTH_WITH_SCOPE_NOTE"}


@dataclass(frozen=True)
class ApprovedCleanupCandidateResult:
    report_type: str
    generated_at: str
    executable: bool
    source_intake_validation: str
    intake_validation_present: bool
    accepted_decision_count: int
    accepted_decisions_reviewed: list[dict[str, Any]]
    approved_cleanup_candidates: list[dict[str, Any]]
    approved_cleanup_candidate_count: int
    rejected_candidates: list[dict[str, Any]]
    rejected_candidate_count: int
    protected_rejected_count: int
    dependency_rejected_count: int
    non_canonical_dependency_rejected_count: int
    no_candidate_decision_count: int
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


def _item_id(decision: dict[str, Any]) -> str:
    return str(decision.get("item_id") or "")


def _has_any(value: str, terms: tuple[str, ...]) -> bool:
    normalized = value.lower()
    return any(term in normalized for term in terms)


def _is_protected_authority(decision: dict[str, Any]) -> bool:
    text = " ".join(
        str(decision.get(key) or "")
        for key in ("item_id", "category", "authority_type", "bucket")
    )
    return _has_any(
        text,
        (
            "protected",
            "file_placement_rules",
            "repo_folder_ownership_map",
            "portal_zone_model",
            "governance",
            "security",
        ),
    )


def _is_dependency_only(decision: dict[str, Any]) -> bool:
    text = " ".join(
        str(decision.get(key) or "")
        for key in ("item_id", "category", "authority_type", "dependency_classification")
    )
    return _has_any(text, ("dependency_or_evidence", "dependency_only", "phase_5c_narrow_merge_plan"))


def _is_non_canonical_dependency(decision: dict[str, Any]) -> bool:
    text = " ".join(
        str(decision.get(key) or "")
        for key in ("item_id", "category", "authority_type", "dependency_classification")
    )
    return _has_any(text, ("non_canonical_dependency", "forex_engine_v1_sprint_4_regime_signal_rules"))


def _candidate_paths(decision: dict[str, Any]) -> list[str]:
    paths = decision.get("paths")
    if isinstance(paths, list):
        return [str(path) for path in paths if isinstance(path, str)]
    files = decision.get("files_involved")
    if isinstance(files, list):
        return [str(path) for path in files if isinstance(path, str)]
    path = decision.get("path")
    return [str(path)] if isinstance(path, str) else []


def _candidate_reason(decision: dict[str, Any]) -> str:
    rationale = decision.get("rationale")
    if isinstance(rationale, str) and rationale.strip():
        return rationale.strip()
    return "Validated human decision requested future cleanup review."


def build_candidates(repo_root: Path) -> ApprovedCleanupCandidateResult:
    root = repo_root.resolve()
    intake_path = root / INTAKE_VALIDATION_PATH
    intake = _load_json(intake_path)
    accepted_decisions = [
        decision
        for decision in intake.get("accepted_decisions", [])
        if isinstance(decision, dict) and decision.get("accepted") is True
    ]

    candidates: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    protected_rejected = 0
    dependency_rejected = 0
    non_canonical_dependency_rejected = 0
    no_candidate_decision = 0

    for decision in accepted_decisions:
        decision_value = str(decision.get("decision") or "")
        item_id = _item_id(decision)
        base_summary = {
            "item_id": item_id,
            "decision": decision_value,
            "reviewer": decision.get("reviewer"),
        }

        if _is_protected_authority(decision):
            protected_rejected += 1
            if decision_value not in PROTECTED_ALLOWED_DECISIONS:
                rejected.append(
                    {
                        **base_summary,
                        "reason": "protected authority item is not eligible as a cleanup candidate",
                        "classification": "PROTECTED_AUTHORITY_REJECTED",
                    }
                )
            else:
                rejected.append(
                    {
                        **base_summary,
                        "reason": "protected authority item remains parked for human review",
                        "classification": "PROTECTED_AUTHORITY_PARKED",
                    }
                )
            continue

        if _is_non_canonical_dependency(decision):
            non_canonical_dependency_rejected += 1
            rejected.append(
                {
                    **base_summary,
                    "reason": "non-canonical dependency is not eligible as a cleanup candidate",
                    "classification": "NON_CANONICAL_DEPENDENCY_REJECTED",
                }
            )
            continue

        if _is_dependency_only(decision):
            dependency_rejected += 1
            rejected.append(
                {
                    **base_summary,
                    "reason": "dependency-only document is not eligible as a cleanup candidate",
                    "classification": "DEPENDENCY_ONLY_REJECTED",
                }
            )
            continue

        if decision_value not in CANDIDATE_DECISIONS:
            no_candidate_decision += 1
            rejected.append(
                {
                    **base_summary,
                    "reason": "decision value does not request a cleanup or canonicalization review candidate",
                    "classification": "NO_CANDIDATE_DECISION",
                }
            )
            continue

        candidates.append(
            {
                **base_summary,
                "paths": _candidate_paths(decision),
                "reason": _candidate_reason(decision),
                "executable": False,
                "apply_ready": False,
                "recommended_next_action": "Review candidate manually before any future APPLY packet is considered.",
            }
        )

    return ApprovedCleanupCandidateResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        source_intake_validation=_normalize_path(INTAKE_VALIDATION_PATH),
        intake_validation_present=intake_path.exists(),
        accepted_decision_count=int(intake.get("accepted_decision_count", len(accepted_decisions)) or 0),
        accepted_decisions_reviewed=accepted_decisions,
        approved_cleanup_candidates=candidates,
        approved_cleanup_candidate_count=len(candidates),
        rejected_candidates=rejected,
        rejected_candidate_count=len(rejected),
        protected_rejected_count=protected_rejected,
        dependency_rejected_count=dependency_rejected,
        non_canonical_dependency_rejected_count=non_canonical_dependency_rejected,
        no_candidate_decision_count=no_candidate_decision,
        safe_cleanup_paths=[],
        apply_ready_paths=[],
        safety={
            "executable": False,
            "dry_run_only": True,
            "approvals_created": False,
            "approvals_inferred": False,
            "cleanup_performed": False,
            "canonicalization_performed": False,
            "apply_packet_generated": False,
            "safe_cleanup_paths_empty": True,
            "apply_ready_paths_empty": True,
        },
        recommended_next_action=(
            "Use this report only as a review queue; no cleanup, canonicalization, "
            "or APPLY action is authorized."
        ),
    )


def _output_path(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_PATH).resolve()
    allowed_root = (root / OUTPUT_PATH.parent).resolve()
    if not (output.parent == allowed_root and allowed_root in output.parents):
        raise ValueError("Approved cleanup candidates must be written under Reports/operator_relief/approved_cleanup_candidates/.")
    return output


def write_candidates(result: ApprovedCleanupCandidateResult, repo_root: Path) -> Path:
    path = _output_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build DRY_RUN-only approved cleanup candidate report.")
    parser.add_argument("--write-report", action="store_true", help="Write report under Reports/operator_relief/approved_cleanup_candidates/.")
    args = parser.parse_args(argv)
    result = build_candidates(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_report:
        payload["written_file"] = _normalize_path(write_candidates(result, Path.cwd()))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
