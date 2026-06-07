"""Validate review-only workflow cleanup draft packets."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.operator_relief.workflow_cleanup_apply_packet_draft import OUTPUT_ROOT


REPORT_TYPE = "operator_relief_draft_packet_safety_validator_v1"
OUTPUT_PATH = OUTPUT_ROOT / "draft_packet_safety_validation.json"
IGNORED_FILES = {
    "workflow_cleanup_apply_packet_draft_index.json",
    "draft_packet_safety_validation.json",
}
PROTECTED_TARGET_TERMS = (
    "docs/governance/",
    "docs/security/",
    "docs/AI_OS/governance/",
    "docs/AI_OS/security/",
    "AGENTS.md",
)


@dataclass(frozen=True)
class DraftPacketSafetyValidationResult:
    report_type: str
    generated_at: str
    executable: bool
    review_only: bool
    source_draft_packet_root: str
    draft_packets_scanned: list[str]
    accepted_draft_packets: list[dict[str, Any]]
    rejected_draft_packets: list[dict[str, Any]]
    accepted_count: int
    rejected_count: int
    safe_cleanup_paths: list[str]
    apply_ready_paths: list[str]
    safety: dict[str, Any]
    recommended_next_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _draft_files(repo_root: Path) -> list[Path]:
    output_root = repo_root / OUTPUT_ROOT
    if not output_root.exists():
        return []
    return sorted(
        path
        for path in output_root.glob("*.json")
        if path.is_file() and path.name not in IGNORED_FILES
    )


def _list_field(payload: dict[str, Any], field: str) -> list[Any]:
    value = payload.get(field)
    return value if isinstance(value, list) else []


def _editable_targets(payload: dict[str, Any]) -> list[str]:
    targets: list[str] = []
    canonical = payload.get("canonical_file")
    if isinstance(canonical, str):
        targets.append(canonical)
    for field in ("duplicate_files", "target_files", "editable_files", "files_to_modify"):
        for value in _list_field(payload, field):
            if isinstance(value, str):
                targets.append(value)
    return targets


def _has_protected_target(payload: dict[str, Any]) -> bool:
    for target in _editable_targets(payload):
        normalized = target.replace("\\", "/")
        if any(term in normalized for term in PROTECTED_TARGET_TERMS):
            return True
    return False


def validate_draft_packet(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("executable") is True:
        errors.append("executable=true is rejected")
    if payload.get("review_only") is not True:
        errors.append("review_only must be true")
    if _list_field(payload, "safe_cleanup_paths"):
        errors.append("safe_cleanup_paths must be empty")
    if _list_field(payload, "apply_ready_paths"):
        errors.append("apply_ready_paths must be empty")
    if _has_protected_target(payload):
        errors.append("protected governance/security docs appear as editable targets")
    for field in ("blocked_actions", "human_approval_requirements", "rollback_requirements", "validation_requirements"):
        if not _list_field(payload, field):
            errors.append(f"{field} is required")
    return errors


def build_validation(repo_root: Path) -> DraftPacketSafetyValidationResult:
    root = repo_root.resolve()
    draft_files = _draft_files(root)
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for draft_file in draft_files:
        relative_path = _normalize_path(draft_file.relative_to(root))
        try:
            payload = _load_json(draft_file)
        except json.JSONDecodeError as exc:
            rejected.append(
                {
                    "draft_packet": relative_path,
                    "candidate_id": None,
                    "accepted": False,
                    "errors": [f"invalid json: {exc.msg}"],
                }
            )
            continue
        if not isinstance(payload, dict):
            rejected.append(
                {
                    "draft_packet": relative_path,
                    "candidate_id": None,
                    "accepted": False,
                    "errors": ["draft packet must be a json object"],
                }
            )
            continue
        errors = validate_draft_packet(payload)
        summary = {
            "draft_packet": relative_path,
            "candidate_id": payload.get("candidate_id"),
            "accepted": not errors,
        }
        if errors:
            rejected.append({**summary, "errors": errors})
        else:
            accepted.append(
                {
                    **summary,
                    "review_only": True,
                    "executable": False,
                }
            )

    return DraftPacketSafetyValidationResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        review_only=True,
        source_draft_packet_root=_normalize_path(OUTPUT_ROOT),
        draft_packets_scanned=[_normalize_path(path.relative_to(root)) for path in draft_files],
        accepted_draft_packets=accepted,
        rejected_draft_packets=rejected,
        accepted_count=len(accepted),
        rejected_count=len(rejected),
        safe_cleanup_paths=[],
        apply_ready_paths=[],
        safety={
            "executable": False,
            "dry_run_only": True,
            "validation_only": True,
            "review_only": True,
            "workflow_docs_modified": False,
            "cleanup_performed": False,
            "canonicalization_performed": False,
            "executable_apply_packet_generated": False,
            "protected_docs_modified": False,
            "safe_cleanup_paths_empty": True,
            "apply_ready_paths_empty": True,
        },
        recommended_next_action="Review accepted draft packets manually; this validation does not authorize executable APPLY.",
    )


def _output_path(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_PATH).resolve()
    allowed_root = (root / OUTPUT_ROOT).resolve()
    if not (output.parent == allowed_root and allowed_root in output.parents):
        raise ValueError("Draft packet safety validation must be written under Reports/operator_relief/workflow_cleanup_apply_packet_drafts/.")
    return output


def write_validation(result: DraftPacketSafetyValidationResult, repo_root: Path) -> Path:
    path = _output_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate review-only workflow cleanup draft packets.")
    parser.add_argument("--write-report", action="store_true", help="Write validation report under workflow cleanup draft Reports.")
    args = parser.parse_args(argv)
    result = build_validation(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_report:
        payload["written_file"] = _normalize_path(write_validation(result, Path.cwd()))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
