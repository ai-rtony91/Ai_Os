"""Generate a blank explicit APPLY approval template."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.operator_relief.executable_apply_packet_gate import (
    OUTPUT_ROOT,
    OUTPUT_PATH as GATE_OUTPUT_PATH,
    REQUIRED_APPROVAL_SCOPE,
    REQUIRED_CANDIDATE_IDS,
)


REPORT_TYPE = "operator_relief_explicit_apply_approval_template_v1"
OUTPUT_PATH = OUTPUT_ROOT / "explicit_apply_approval_template.json"
BLOCKED_CATEGORIES = [
    "protected_authority",
    "dependency_only",
    "non_canonical_dependency",
]


@dataclass(frozen=True)
class ExplicitApplyApprovalTemplateResult:
    report_type: str
    generated_at: str
    executable: bool
    source_executable_apply_packet_gate: str
    template_output_path: str
    template: dict[str, Any]
    eligible_candidate_ids: list[str]
    default_approval_status: bool
    safe_cleanup_paths: list[str]
    apply_ready_paths: list[str]
    safety: dict[str, Any]
    recommended_next_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def build_template(repo_root: Path) -> ExplicitApplyApprovalTemplateResult:
    _ = repo_root.resolve()
    template = {
        "apply_approval": False,
        "approval_scope": "",
        "approved_candidate_ids": [],
        "reviewer": "",
        "rationale": "",
        "required_scope_value": REQUIRED_APPROVAL_SCOPE,
        "eligible_candidate_ids": list(REQUIRED_CANDIDATE_IDS),
        "blocked_candidate_ids": [],
        "blocked_categories": list(BLOCKED_CATEGORIES),
        "safety_acknowledgements": [
            "This template does not approve cleanup.",
            "This template does not approve canonicalization.",
            "This template does not generate executable APPLY packets.",
            "Protected governance/security docs remain blocked.",
            "Dependency-only and non-canonical dependency items remain blocked.",
            "A human reviewer must fill reviewer, rationale, approval_scope, and approved_candidate_ids before any later gate can pass.",
        ],
        "executable": False,
        "apply_ready_paths": [],
    }
    return ExplicitApplyApprovalTemplateResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        source_executable_apply_packet_gate=_normalize_path(GATE_OUTPUT_PATH),
        template_output_path=_normalize_path(OUTPUT_PATH),
        template=template,
        eligible_candidate_ids=list(REQUIRED_CANDIDATE_IDS),
        default_approval_status=False,
        safe_cleanup_paths=[],
        apply_ready_paths=[],
        safety={
            "executable": False,
            "dry_run_only": True,
            "template_only": True,
            "apply_approval_default_false": True,
            "approvals_created": False,
            "approvals_inferred": False,
            "workflow_docs_modified": False,
            "cleanup_performed": False,
            "canonicalization_performed": False,
            "executable_apply_packet_generated": False,
            "protected_docs_modified": False,
            "apply_ready_paths_empty": True,
        },
        recommended_next_action="A human may copy this template to explicit_apply_approval.json and fill it later; this template does not approve action.",
    )


def _output_path(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_PATH).resolve()
    allowed_root = (root / OUTPUT_ROOT).resolve()
    if not (output.parent == allowed_root and allowed_root in output.parents):
        raise ValueError("Explicit APPLY approval template must be written under Reports/operator_relief/workflow_cleanup_apply_packet_drafts/.")
    return output


def write_template(result: ExplicitApplyApprovalTemplateResult, repo_root: Path) -> Path:
    path = _output_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result.template, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a blank explicit APPLY approval template.")
    parser.add_argument("--write-template", action="store_true", help="Write blank approval template under workflow cleanup draft Reports.")
    args = parser.parse_args(argv)
    result = build_template(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_template:
        payload["written_file"] = _normalize_path(write_template(result, Path.cwd()))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
