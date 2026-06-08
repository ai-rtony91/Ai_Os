"""Build and validate the DRY_RUN-only human review decision schema."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.operator_relief.human_review_packet_exporter import DECISION_OPTIONS


REPORT_TYPE = "operator_relief_human_review_decision_schema_v1"
OUTPUT_PATH = Path("Reports/operator_relief/human_review_decisions/human_review_decision_schema.json")
PACKET_ROOT = Path("Reports/operator_relief/human_review_packets")
REQUIRED_FIELDS = (
    "item_id",
    "reviewer",
    "decision",
    "executable",
    "cleanup_approved",
    "canonicalization_approved",
    "apply_packet_generated",
    "safe_cleanup_paths",
    "apply_ready_paths",
)


@dataclass(frozen=True)
class DecisionSchemaResult:
    report_type: str
    generated_at: str
    executable: bool
    source_human_review_packets: str
    allowed_decisions: list[str]
    required_fields: list[str]
    schema: dict[str, Any]
    safe_cleanup_paths: list[str]
    apply_ready_paths: list[str]
    safety: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def build_schema(repo_root: Path) -> DecisionSchemaResult:
    _ = repo_root.resolve()
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "AI_OS Human Review Decision v1",
        "type": "object",
        "additionalProperties": False,
        "required": list(REQUIRED_FIELDS),
        "properties": {
            "item_id": {"type": "string", "minLength": 1},
            "reviewer": {"type": "string", "minLength": 1},
            "decision": {"type": "string", "enum": list(DECISION_OPTIONS)},
            "notes": {"type": "string"},
            "executable": {"type": "boolean", "const": False},
            "cleanup_approved": {"type": "boolean", "const": False},
            "canonicalization_approved": {"type": "boolean", "const": False},
            "apply_packet_generated": {"type": "boolean", "const": False},
            "safe_cleanup_paths": {"type": "array", "maxItems": 0},
            "apply_ready_paths": {"type": "array", "maxItems": 0},
        },
    }
    return DecisionSchemaResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        source_human_review_packets=_normalize_path(PACKET_ROOT),
        allowed_decisions=list(DECISION_OPTIONS),
        required_fields=list(REQUIRED_FIELDS),
        schema=schema,
        safe_cleanup_paths=[],
        apply_ready_paths=[],
        safety={
            "executable": False,
            "dry_run_only": True,
            "schema_only": True,
            "records_real_approval": False,
            "cleanup_approved": False,
            "canonicalization_approved": False,
            "apply_packet_generated": False,
            "safe_cleanup_paths_empty": True,
            "apply_ready_paths_empty": True,
        },
    )


def validate_decision(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in payload:
            errors.append(f"missing required field: {field}")
    decision = payload.get("decision")
    if decision not in DECISION_OPTIONS:
        errors.append(f"unknown decision value: {decision}")
    reviewer = payload.get("reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        errors.append("reviewer field is required")
    for field in ("executable", "cleanup_approved", "canonicalization_approved", "apply_packet_generated"):
        if payload.get(field) is True:
            errors.append(f"{field}=true is rejected")
    for field in ("safe_cleanup_paths", "apply_ready_paths"):
        value = payload.get(field)
        if value not in ([], None):
            errors.append(f"{field} must be empty")
    return errors


def _output_path(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_PATH).resolve()
    allowed_root = (root / OUTPUT_PATH.parent).resolve()
    if not (output.parent == allowed_root and allowed_root in output.parents):
        raise ValueError("Human review decision schema must be written under Reports/operator_relief/human_review_decisions/.")
    return output


def write_schema(result: DecisionSchemaResult, repo_root: Path) -> Path:
    path = _output_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build DRY_RUN-only human review decision schema.")
    parser.add_argument("--write-schema", action="store_true", help="Write schema under Reports/operator_relief/human_review_decisions/.")
    args = parser.parse_args(argv)
    result = build_schema(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_schema:
        payload["written_file"] = _normalize_path(write_schema(result, Path.cwd()))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
