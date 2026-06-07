"""Validate future human review decisions without granting cleanup authority."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.operator_relief.human_review_decision_schema import validate_decision


REPORT_TYPE = "operator_relief_human_decision_intake_validation_v1"
SCHEMA_PATH = Path("Reports/operator_relief/human_review_decisions/human_review_decision_schema.json")
PACKET_ROOT = Path("Reports/operator_relief/human_review_packets")
DECISION_ROOT = Path("Reports/operator_relief/human_review_decisions")
OUTPUT_PATH = DECISION_ROOT / "human_decision_intake_validation.json"
IGNORED_DECISION_FILES = {
    "human_review_decision_schema.json",
    "human_decision_intake_validation.json",
}


@dataclass(frozen=True)
class IntakeValidationResult:
    report_type: str
    generated_at: str
    executable: bool
    source_schema: str
    source_packet_root: str
    decision_files_scanned: list[str]
    known_packet_item_ids: list[str]
    accepted_decisions: list[dict[str, Any]]
    rejected_decisions: list[dict[str, Any]]
    accepted_decision_count: int
    rejected_decision_count: int
    approved_cleanup_candidates: list[str]
    approved_cleanup_candidate_count: int
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


def _known_packet_item_ids(repo_root: Path) -> list[str]:
    packet_root = repo_root / PACKET_ROOT
    if not packet_root.exists():
        return []
    return sorted(path.stem for path in packet_root.glob("*.md") if path.is_file())


def _decision_files(repo_root: Path) -> list[Path]:
    decision_root = repo_root / DECISION_ROOT
    if not decision_root.exists():
        return []
    return sorted(
        path
        for path in decision_root.glob("*.json")
        if path.is_file() and path.name not in IGNORED_DECISION_FILES
    )


def _records_from_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [record for record in payload if isinstance(record, dict)]
    if isinstance(payload, dict):
        decisions = payload.get("decisions")
        if isinstance(decisions, list):
            return [record for record in decisions if isinstance(record, dict)]
        return [payload]
    return []


def _validate_intake_record(record: dict[str, Any], known_item_ids: set[str]) -> list[str]:
    errors = validate_decision(record)
    rationale = record.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        errors.append("rationale field is required")
    item_id = record.get("item_id")
    if not isinstance(item_id, str) or item_id not in known_item_ids:
        errors.append(f"unknown packet item id: {item_id}")
    return errors


def build_validation(repo_root: Path) -> IntakeValidationResult:
    root = repo_root.resolve()
    known_ids = _known_packet_item_ids(root)
    known_id_set = set(known_ids)
    decision_files = _decision_files(root)
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for decision_file in decision_files:
        relative_file = _normalize_path(decision_file.relative_to(root))
        try:
            payload = _load_json(decision_file)
        except json.JSONDecodeError as exc:
            rejected.append(
                {
                    "decision_file": relative_file,
                    "item_id": None,
                    "accepted": False,
                    "errors": [f"invalid json: {exc.msg}"],
                }
            )
            continue

        records = _records_from_payload(payload)
        if not records:
            rejected.append(
                {
                    "decision_file": relative_file,
                    "item_id": None,
                    "accepted": False,
                    "errors": ["no decision records found"],
                }
            )
            continue

        for index, record in enumerate(records):
            errors = _validate_intake_record(record, known_id_set)
            decision_summary = {
                "decision_file": relative_file,
                "record_index": index,
                "item_id": record.get("item_id"),
                "decision": record.get("decision"),
                "reviewer": record.get("reviewer"),
                "accepted": not errors,
            }
            if errors:
                rejected.append({**decision_summary, "errors": errors})
            else:
                accepted.append(
                    {
                        **decision_summary,
                        "accepted_for_validation_only": True,
                        "approval_created": False,
                    }
                )

    return IntakeValidationResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        source_schema=_normalize_path(SCHEMA_PATH),
        source_packet_root=_normalize_path(PACKET_ROOT),
        decision_files_scanned=[_normalize_path(path.relative_to(root)) for path in decision_files],
        known_packet_item_ids=known_ids,
        accepted_decisions=accepted,
        rejected_decisions=rejected,
        accepted_decision_count=len(accepted),
        rejected_decision_count=len(rejected),
        approved_cleanup_candidates=[],
        approved_cleanup_candidate_count=0,
        safe_cleanup_paths=[],
        apply_ready_paths=[],
        safety={
            "executable": False,
            "dry_run_only": True,
            "validation_only": True,
            "approvals_created": False,
            "approvals_inferred": False,
            "cleanup_approved": False,
            "canonicalization_approved": False,
            "apply_packet_generated": False,
            "safe_cleanup_paths_empty": True,
            "apply_ready_paths_empty": True,
        },
        recommended_next_action=(
            "Review rejected decisions or submit schema-compliant decision records; "
            "no cleanup, canonicalization, or APPLY action is authorized."
        ),
    )


def _output_path(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_PATH).resolve()
    allowed_root = (root / DECISION_ROOT).resolve()
    if not (output.parent == allowed_root and allowed_root in output.parents):
        raise ValueError("Human decision intake validation must be written under Reports/operator_relief/human_review_decisions/.")
    return output


def write_validation(result: IntakeValidationResult, repo_root: Path) -> Path:
    path = _output_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate DRY_RUN-only human decision intake records.")
    parser.add_argument("--write-report", action="store_true", help="Write validation under Reports/operator_relief/human_review_decisions/.")
    args = parser.parse_args(argv)
    result = build_validation(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_report:
        payload["written_file"] = _normalize_path(write_validation(result, Path.cwd()))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
