"""Build a DRY_RUN-only duplicate retirement plan for HRQ-001."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_TYPE = "operator_relief_hrq001_duplicate_retirement_plan_v1"
CANONICAL_FILE = Path("docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md")
DUPLICATE_FILE = Path("docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md")
PICK_PULL_PLAN_PATH = Path("Reports/operator_relief/hrq001_pick_pull_merge_plan/hrq001_pick_pull_merge_plan.json")
DRAFT_PATCH_PATH = Path("Reports/operator_relief/hrq001_apply_draft_patch/hrq001_apply_draft_patch.json")
OUTPUT_ROOT = Path("Reports/operator_relief/hrq001_duplicate_retirement_plan")
JSON_OUTPUT_PATH = OUTPUT_ROOT / "hrq001_duplicate_retirement_plan.json"
MARKDOWN_OUTPUT_PATH = OUTPUT_ROOT / "hrq001_duplicate_retirement_plan.md"
RETIREMENT_OPTIONS = [
    "KEEP_AS_REFERENCE_ONLY",
    "REPLACE_WITH_DEPRECATION_NOTICE_LATER",
    "ARCHIVE_AFTER_REFERENCE_UPDATE",
    "DELETE_AFTER_REFERENCE_UPDATE",
]
BLOCKED_ACTIONS = [
    "delete files",
    "modify workflow docs",
    "modify duplicate file",
    "canonicalize further",
    "touch HRQ-002",
    "touch HRQ-003",
    "modify protected governance/security docs",
    "stage files",
    "commit",
    "push",
]


@dataclass(frozen=True)
class HRQ001DuplicateRetirementPlanResult:
    report_type: str
    generated_at: str
    executable: bool
    delete_ready: bool
    apply_ready_paths: list[str]
    canonical_path: str
    duplicate_path: str
    source_pick_pull_merge_plan: str
    source_apply_draft_patch: str
    unique_content_remaining_in_duplicate: list[dict[str, Any]]
    content_already_absorbed_into_canonical: list[dict[str, Any]]
    content_safe_to_prune_later: list[dict[str, Any]]
    references_that_point_to_duplicate: list[dict[str, str]]
    references_found_count: int
    references_that_must_be_updated_before_retirement: list[dict[str, str]]
    retirement_options: list[str]
    recommended_option: str
    required_validation_before_retire_or_delete_action: list[str]
    rollback_plan: list[str]
    blocked_actions: list[str]
    safety: dict[str, Any]
    recommended_next_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _extract_sections(markdown: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_heading = ""
    current_lines: list[str] = []
    for line in markdown.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            if current_heading:
                sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = match.group(1).strip()
            current_lines = []
        elif current_heading:
            current_lines.append(line)
    if current_heading:
        sections[current_heading] = "\n".join(current_lines).strip()
    return sections


def _compact(text: str) -> str:
    return " ".join(text.split()).lower()


def _preview(text: str, limit: int = 220) -> str:
    return " ".join(text.split())[:limit]


def _reference_scan(repo_root: Path) -> list[dict[str, str]]:
    duplicate_path = _normalize_path(DUPLICATE_FILE)
    references: list[dict[str, str]] = []
    skipped_dirs = {".git", ".venv", "node_modules", "__pycache__"}
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        relative_parts = set(path.relative_to(repo_root).parts)
        if relative_parts & skipped_dirs:
            continue
        relative = _normalize_path(path.relative_to(repo_root))
        if relative == duplicate_path:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if duplicate_path in text or str(DUPLICATE_FILE).replace("/", "\\") in text:
            references.append(
                {
                    "path": relative,
                    "reference": duplicate_path,
                    "required_update": "Review whether this reference should point to the canonical workflow or remain historical evidence.",
                }
            )
    return references


def _absorbed_content(canonical_text: str, duplicate_sections: dict[str, str]) -> list[dict[str, Any]]:
    canonical_compact = _compact(canonical_text)
    absorbed = []
    branch_examples = [
        "worker/work-intelligence/phase-21-branch-rules",
        "worker/operator-orchestration/phase-22-file-ownership",
        "worker/dashboard-ui/phase-15-centerpiece-review",
    ]
    if all(example in canonical_text for example in branch_examples):
        absorbed.append(
            {
                "duplicate_section": "Branch Naming",
                "canonical_section": "Branch Naming",
                "absorbed_content": "legacy worker branch examples",
                "evidence": branch_examples,
            }
        )
    report_sentence = "Worker reports should include planned files and validation commands. The integration lane checks those reports before any merge or APPLY review."
    if _compact(report_sentence) in canonical_compact:
        absorbed.append(
            {
                "duplicate_section": "Report Rules",
                "canonical_section": "Collision Handling",
                "absorbed_content": "concise integration-lane report check wording",
                "evidence": [report_sentence],
            }
        )
    if not absorbed and duplicate_sections:
        absorbed.append(
            {
                "duplicate_section": "UNKNOWN",
                "canonical_section": "UNKNOWN",
                "absorbed_content": "No known HRQ-001 snippets detected in canonical.",
                "evidence": [],
            }
        )
    return absorbed


def _remaining_content(canonical_text: str, duplicate_sections: dict[str, str]) -> list[dict[str, Any]]:
    canonical_compact = _compact(canonical_text)
    remaining: list[dict[str, Any]] = []
    for heading, text in duplicate_sections.items():
        section_compact = _compact(text)
        if not section_compact:
            continue
        if heading in {"Branch Naming", "Report Rules"}:
            remaining.append(
                {
                    "section": heading,
                    "status": "PARTIALLY_ABSORBED_REVIEW_REMAINDER",
                    "reason": "Approved snippets were absorbed, but full duplicate section contains older wording that should remain review-only.",
                    "preview": _preview(text),
                }
            )
        elif section_compact not in canonical_compact:
            remaining.append(
                {
                    "section": heading,
                    "status": "LEGACY_CONTENT_REMAINING",
                    "reason": "Duplicate section is not identical to canonical text and may be historical, superseded, or reference-only.",
                    "preview": _preview(text),
                }
            )
    return remaining


def _prune_candidates() -> list[dict[str, Any]]:
    return [
        {
            "section": "Required Worker Metadata",
            "reason": "Superseded by canonical Required Lane Metadata.",
            "safe_to_prune_later": False,
            "condition": "Only after references are updated and human review approves duplicate retirement.",
        },
        {
            "section": "Allowed Worker Lanes",
            "reason": "Duplicate list is narrower than the current canonical lane list.",
            "safe_to_prune_later": False,
            "condition": "Only after references are updated and human review approves duplicate retirement.",
        },
        {
            "section": "Path Rules",
            "reason": "Superseded by canonical Path Ownership.",
            "safe_to_prune_later": False,
            "condition": "Only after references are updated and human review approves duplicate retirement.",
        },
        {
            "section": "Safety",
            "reason": "Superseded by canonical Purpose and Validation safety language.",
            "safe_to_prune_later": False,
            "condition": "Only after references are updated and human review approves duplicate retirement.",
        },
    ]


def build_plan(repo_root: Path) -> HRQ001DuplicateRetirementPlanResult:
    root = repo_root.resolve()
    canonical_text = _load_text(root / CANONICAL_FILE)
    duplicate_text = _load_text(root / DUPLICATE_FILE)
    duplicate_sections = _extract_sections(duplicate_text)
    references = _reference_scan(root)
    recommended = "REPLACE_WITH_DEPRECATION_NOTICE_LATER" if references else "KEEP_AS_REFERENCE_ONLY"
    return HRQ001DuplicateRetirementPlanResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        delete_ready=False,
        apply_ready_paths=[],
        canonical_path=_normalize_path(CANONICAL_FILE),
        duplicate_path=_normalize_path(DUPLICATE_FILE),
        source_pick_pull_merge_plan=_normalize_path(PICK_PULL_PLAN_PATH),
        source_apply_draft_patch=_normalize_path(DRAFT_PATCH_PATH),
        unique_content_remaining_in_duplicate=_remaining_content(canonical_text, duplicate_sections),
        content_already_absorbed_into_canonical=_absorbed_content(canonical_text, duplicate_sections),
        content_safe_to_prune_later=_prune_candidates(),
        references_that_point_to_duplicate=references,
        references_found_count=len(references),
        references_that_must_be_updated_before_retirement=references,
        retirement_options=list(RETIREMENT_OPTIONS),
        recommended_option=recommended,
        required_validation_before_retire_or_delete_action=[
            "Confirm all references to docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md are intentionally updated or preserved as historical evidence.",
            "Confirm the duplicate file still contains a historical/reference-only notice if retained.",
            "Run git diff -- docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md.",
            "Run git diff --check.",
            "Run python -m pytest tests/operator_relief/test_hrq001_duplicate_retirement_plan.py.",
            "Require a separate explicit APPLY packet before any duplicate-file edit, archive, or deletion.",
        ],
        rollback_plan=[
            "No rollback is needed for this DRY_RUN plan because source docs are not modified.",
            "A future retirement APPLY packet must preserve pre-change copies in git history and show exact diff before staging.",
            "If validation fails or references remain unresolved, keep the duplicate as reference-only.",
        ],
        blocked_actions=list(BLOCKED_ACTIONS),
        safety={
            "executable": False,
            "dry_run_only": True,
            "review_plan_only": True,
            "workflow_docs_modified": False,
            "duplicate_file_modified": False,
            "files_deleted": False,
            "canonicalization_performed": False,
            "protected_docs_modified": False,
            "hrq002_touched": False,
            "hrq003_touched": False,
            "delete_ready": False,
            "apply_ready_paths_empty": True,
        },
        recommended_next_action="Review duplicate references and decide whether a later deprecation-notice APPLY packet is warranted.",
    )


def render_markdown(result: HRQ001DuplicateRetirementPlanResult) -> str:
    lines = [
        "# HRQ-001 Duplicate Retirement Plan",
        "",
        "```json",
        '{ "executable": false, "delete_ready": false, "apply_ready_paths": [] }',
        "```",
        "",
        f"- Canonical path: `{result.canonical_path}`",
        f"- Duplicate path: `{result.duplicate_path}`",
        f"- Recommended option: `{result.recommended_option}`",
        f"- References found: `{len(result.references_that_point_to_duplicate)}`",
        "",
        "## Content Already Absorbed",
    ]
    for item in result.content_already_absorbed_into_canonical:
        lines.append(f"- {item['duplicate_section']} -> {item['canonical_section']}: {item['absorbed_content']}")
    lines.extend(["", "## Unique Content Remaining"])
    for item in result.unique_content_remaining_in_duplicate:
        lines.append(f"- {item['section']}: {item['status']}")
    lines.extend(["", "## References To Duplicate"])
    for item in result.references_that_point_to_duplicate:
        lines.append(f"- `{item['path']}`")
    lines.extend(["", "## Retirement Options"])
    for option in result.retirement_options:
        lines.append(f"- {option}")
    lines.extend(["", "## Blocked Actions"])
    for action in result.blocked_actions:
        lines.append(f"- {action}")
    return "\n".join(lines).rstrip() + "\n"


def _output_root(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_ROOT).resolve()
    allowed = (root / OUTPUT_ROOT).resolve()
    if not (output == allowed or allowed in output.parents):
        raise ValueError("HRQ-001 duplicate retirement plan must be written under Reports/operator_relief/hrq001_duplicate_retirement_plan/.")
    return output


def write_reports(result: HRQ001DuplicateRetirementPlanResult, repo_root: Path) -> list[Path]:
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
    parser = argparse.ArgumentParser(description="Build DRY_RUN-only HRQ-001 duplicate retirement plan.")
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
