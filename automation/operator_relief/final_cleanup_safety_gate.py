"""Final DRY_RUN safety gate for cleanup and canonicalization work."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_TYPE = "operator_relief_final_cleanup_safety_gate_v1"
SOURCE_CANDIDATES_PATH = Path("Reports/operator_relief/approved_cleanup_candidates/approved_cleanup_candidates.json")
OUTPUT_PATH = Path("Reports/operator_relief/final_safety_gate/final_cleanup_safety_gate.json")
FINAL_STATUS_BLOCKED = "BLOCKED"
FINAL_STATUS_REVIEW_ONLY_READY = "REVIEW_ONLY_READY"


@dataclass(frozen=True)
class FinalCleanupSafetyGateResult:
    report_type: str
    generated_at: str
    executable: bool
    source_approved_cleanup_candidates: str
    source_candidates_present: bool
    approved_cleanup_candidate_count: int
    final_status: str
    block_reasons: list[str]
    approved_cleanup_candidates_reviewed: list[dict[str, Any]]
    protected_authority_items: list[dict[str, Any]]
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


def _has_any(value: str, terms: tuple[str, ...]) -> bool:
    normalized = value.lower()
    return any(term in normalized for term in terms)


def _is_protected_authority(item: dict[str, Any]) -> bool:
    text = " ".join(
        str(item.get(key) or "")
        for key in ("item_id", "category", "authority_type", "bucket", "classification")
    )
    paths = item.get("paths")
    if isinstance(paths, list):
        text = f"{text} {' '.join(str(path) for path in paths)}"
    return _has_any(
        text,
        (
            "protected",
            "governance",
            "security",
            "agents",
            "file_placement_rules",
            "repo_folder_ownership_map",
            "portal_zone_model",
        ),
    )


def _contains_executable_true(value: Any) -> bool:
    if isinstance(value, dict):
        return any((key == "executable" and item is True) or _contains_executable_true(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_executable_true(item) for item in value)
    return False


def _list_field(payload: dict[str, Any], field: str) -> list[Any]:
    value = payload.get(field)
    return value if isinstance(value, list) else []


def build_gate(repo_root: Path) -> FinalCleanupSafetyGateResult:
    root = repo_root.resolve()
    source_path = root / SOURCE_CANDIDATES_PATH
    payload = _load_json(source_path)
    candidates = [
        candidate
        for candidate in payload.get("approved_cleanup_candidates", [])
        if isinstance(candidate, dict)
    ]
    candidate_count = int(payload.get("approved_cleanup_candidate_count", len(candidates)) or 0)
    safe_cleanup_paths = _list_field(payload, "safe_cleanup_paths")
    apply_ready_paths = _list_field(payload, "apply_ready_paths")
    protected_items = [candidate for candidate in candidates if _is_protected_authority(candidate)]
    block_reasons: list[str] = []

    if not source_path.exists():
        block_reasons.append("approved cleanup candidate report is missing")
    if candidate_count == 0:
        block_reasons.append("approved_cleanup_candidate_count is 0")
    if _contains_executable_true(payload):
        block_reasons.append("executable=true found in candidate report")
    if apply_ready_paths and candidate_count == 0:
        block_reasons.append("apply_ready_paths is non-empty without valid candidates")
    if safe_cleanup_paths and candidate_count == 0:
        block_reasons.append("safe_cleanup_paths is non-empty without valid candidates")
    if protected_items:
        block_reasons.append("protected authority items are blocked from cleanup")

    final_status = FINAL_STATUS_BLOCKED if block_reasons else FINAL_STATUS_REVIEW_ONLY_READY
    return FinalCleanupSafetyGateResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        source_approved_cleanup_candidates=_normalize_path(SOURCE_CANDIDATES_PATH),
        source_candidates_present=source_path.exists(),
        approved_cleanup_candidate_count=candidate_count,
        final_status=final_status,
        block_reasons=block_reasons,
        approved_cleanup_candidates_reviewed=candidates,
        protected_authority_items=protected_items,
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
            "blocked": final_status == FINAL_STATUS_BLOCKED,
        },
        recommended_next_action=(
            "Do not clean up, canonicalize, or generate APPLY packets while this gate is BLOCKED."
            if final_status == FINAL_STATUS_BLOCKED
            else "Review candidates manually; this gate still does not authorize cleanup or APPLY execution."
        ),
    )


def _output_path(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_PATH).resolve()
    allowed_root = (root / OUTPUT_PATH.parent).resolve()
    if not (output.parent == allowed_root and allowed_root in output.parents):
        raise ValueError("Final safety gate output must be written under Reports/operator_relief/final_safety_gate/.")
    return output


def write_gate(result: FinalCleanupSafetyGateResult, repo_root: Path) -> Path:
    path = _output_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build final DRY_RUN cleanup safety gate report.")
    parser.add_argument("--write-report", action="store_true", help="Write report under Reports/operator_relief/final_safety_gate/.")
    args = parser.parse_args(argv)
    result = build_gate(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_report:
        payload["written_file"] = _normalize_path(write_gate(result, Path.cwd()))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
