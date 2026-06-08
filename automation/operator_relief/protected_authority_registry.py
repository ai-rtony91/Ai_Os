"""Generate a review-only protected authority registry."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_TYPE = "operator_relief_protected_authority_registry_v1"
DECISION_PACKET_ROOT = Path("Reports/operator_relief/decision_packets")
OUTPUT_PATH = Path("Reports/operator_relief/authority_registry/protected_authority_registry.json")
INDEX_PATH = DECISION_PACKET_ROOT / "canonical_decision_packet_index.json"

WORKFLOW_DIFFS = {
    "worker branch and lane rules": DECISION_PACKET_ROOT / "worker_branch_lane_rules_decision_diff.json",
    "parallel codex workflow": DECISION_PACKET_ROOT / "parallel_codex_workflow_decision_diff.json",
    "apply routing chain": DECISION_PACKET_ROOT / "apply_routing_chain_decision_diff.json",
}
PROTECTED_PACKETS = {
    "file placement rules": DECISION_PACKET_ROOT / "canonical_decision_packet_04_file_placement_rules.json",
    "repo folder ownership map": DECISION_PACKET_ROOT / "canonical_decision_packet_05_repo_folder_ownership_map.json",
    "portal zone model": DECISION_PACKET_ROOT / "canonical_decision_packet_06_portal_zone_model.json",
}

DO_NOT_TOUCH = "DO_NOT_TOUCH_WITHOUT_HUMAN_REVIEW"
NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"
PROTECTED_HUMAN_REVIEW = "PROTECTED_HUMAN_REVIEW"
DEPENDENCY_NOT_CANONICAL = "DEPENDENCY_NOT_CANONICAL"


@dataclass(frozen=True)
class AuthorityRegistryResult:
    report_type: str
    generated_at: str
    executable: bool
    source_decision_packet_index: str
    source_decision_diff_reports: list[str]
    protected_authorities: list[dict[str, Any]]
    parked_workflow_authority_conflicts: list[dict[str, Any]]
    dependency_only_documents: list[dict[str, Any]]
    non_canonical_dependencies: list[dict[str, Any]]
    do_not_touch_paths: list[str]
    human_review_required_paths: list[str]
    safe_cleanup_paths: list[str]
    apply_ready_paths: list[str]
    blocked_apply_reasons: list[str]
    recommended_next_action: str
    safety: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def _load_json(repo_root: Path, path: Path) -> dict[str, Any]:
    full_path = repo_root / path
    if not full_path.exists():
        return {}
    return json.loads(full_path.read_text(encoding="utf-8"))


def _unique(items: list[str]) -> list[str]:
    return sorted({item for item in items if item})


def _workflow_reason(group_key: str, diff: dict[str, Any]) -> str:
    if group_key == "worker branch and lane rules":
        return (
            "Canonical has newer sections, duplicate has unique legacy sections, shared sections conflict, "
            "and audit dependency has unique authority."
        )
    if group_key == "parallel codex workflow":
        return "Duplicate has unique launcher, worker-lane, validation, controlled APPLY, and git-rule guidance."
    if group_key == "apply routing chain":
        return (
            "Duplicate has unique non-automation authority; trading file is PAPER_ONLY signal-rule authority, "
            "not APPLY routing canonical authority."
        )
    return "; ".join(str(reason) for reason in diff.get("reasons", []))


def _workflow_paths(diff: dict[str, Any]) -> list[str]:
    paths = [
        str(diff.get("canonical_candidate", "")),
        str(diff.get("duplicate_candidate", "")),
    ]
    paths.extend(str(path) for path in diff.get("dependency_paths", []) if isinstance(path, str))
    return _unique(paths)


def _build_workflow_conflicts(repo_root: Path) -> tuple[list[dict[str, Any]], list[str], list[dict[str, Any]], list[dict[str, Any]]]:
    conflicts: list[dict[str, Any]] = []
    review_paths: list[str] = []
    dependency_only: list[dict[str, Any]] = []
    non_canonical: list[dict[str, Any]] = []

    for group_key, path in WORKFLOW_DIFFS.items():
        diff = _load_json(repo_root, path)
        if not diff:
            continue
        paths = _workflow_paths(diff)
        review_paths.extend(paths)
        entry = {
            "group_key": group_key,
            "status": diff.get("recommended_human_decision", NEEDS_HUMAN_REVIEW),
            "safe_to_generate_apply_packet_later": bool(diff.get("safe_to_generate_apply_packet_later", False)),
            "likely_canonical_candidate": diff.get("canonical_candidate"),
            "duplicate_candidate": diff.get("duplicate_candidate"),
            "paths": paths,
            "source_decision_diff_report": _normalize_path(path),
            "apply_ready": False,
            "reason": _workflow_reason(group_key, diff),
        }
        if group_key == "apply routing chain":
            entry["dependency_classification"] = diff.get("dependency_classification")
        conflicts.append(entry)

        for dependency in diff.get("dependency_paths", []):
            if not isinstance(dependency, str):
                continue
            dependency_only.append(
                {
                    "path": dependency,
                    "source_group": group_key,
                    "source_decision_diff_report": _normalize_path(path),
                    "status": "DEPENDENCY_OR_EVIDENCE_ONLY",
                    "reason": "Dependency/evidence only; not cleanup approval.",
                }
            )
        if diff.get("dependency_classification") == DEPENDENCY_NOT_CANONICAL:
            for dependency in diff.get("dependency_paths", []):
                if isinstance(dependency, str):
                    non_canonical.append(
                        {
                            "path": dependency,
                            "source_group": group_key,
                            "classification": DEPENDENCY_NOT_CANONICAL,
                            "reason": "PAPER_ONLY signal-rule authority, not APPLY routing canonical authority.",
                        }
                    )
    return conflicts, review_paths, dependency_only, non_canonical


def _build_protected_authorities(repo_root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    protected: list[dict[str, Any]] = []
    paths: list[str] = []
    for group_key, packet_path in PROTECTED_PACKETS.items():
        packet = _load_json(repo_root, packet_path)
        if not packet:
            continue
        packet_paths = [str(path) for path in packet.get("paths", []) if isinstance(path, str)]
        paths.extend(packet_paths)
        protected.append(
            {
                "group_key": group_key,
                "status": PROTECTED_HUMAN_REVIEW,
                "action": DO_NOT_TOUCH,
                "paths": packet_paths,
                "protected_review_required": True,
                "source_decision_packet": _normalize_path(packet_path),
                "canonical_owner_selected": False,
                "reason": "Protected governance/security authority requires human review before any APPLY packet.",
            }
        )
    return protected, paths


def build_registry(repo_root: Path) -> AuthorityRegistryResult:
    root = repo_root.resolve()
    workflow_conflicts, workflow_review_paths, dependency_only, non_canonical = _build_workflow_conflicts(root)
    protected_authorities, protected_paths = _build_protected_authorities(root)

    all_review_paths = _unique(workflow_review_paths + protected_paths)
    do_not_touch_paths = _unique(protected_paths)
    blocked_reasons = [
        "No cleanup is approved by this registry.",
        "No APPLY packet is ready because workflow authority conflicts remain parked.",
        "Protected governance/security groups require human review and no canonical owner is selected.",
    ]
    for conflict in workflow_conflicts:
        blocked_reasons.append(f"{conflict['group_key']}: {conflict['reason']}")

    return AuthorityRegistryResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        source_decision_packet_index=_normalize_path(INDEX_PATH),
        source_decision_diff_reports=[_normalize_path(path) for path in WORKFLOW_DIFFS.values()],
        protected_authorities=protected_authorities,
        parked_workflow_authority_conflicts=workflow_conflicts,
        dependency_only_documents=dependency_only,
        non_canonical_dependencies=non_canonical,
        do_not_touch_paths=do_not_touch_paths,
        human_review_required_paths=all_review_paths,
        safe_cleanup_paths=[],
        apply_ready_paths=[],
        blocked_apply_reasons=blocked_reasons,
        recommended_next_action="Review protected authorities and parked workflow conflicts; generate no cleanup or APPLY packet until human decisions are recorded.",
        safety={
            "executable": False,
            "registry_generation_only": True,
            "cleanup_approved": False,
            "apply_ready": False,
            "commit_approved": False,
            "push_approved": False,
            "source_mutation": False,
        },
    )


def _output_path(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_PATH).resolve()
    allowed_root = (root / OUTPUT_PATH.parent).resolve()
    if not (output.parent == allowed_root and allowed_root in output.parents):
        raise ValueError("Authority registry must be written under Reports/operator_relief/authority_registry/.")
    return output


def write_report(result: AuthorityRegistryResult, repo_root: Path) -> Path:
    path = _output_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate protected authority registry.")
    parser.add_argument("--write-report", action="store_true", help="Write registry under Reports/operator_relief/authority_registry/.")
    args = parser.parse_args(argv)

    result = build_registry(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_report:
        payload["written_file"] = _normalize_path(write_report(result, Path.cwd()))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
