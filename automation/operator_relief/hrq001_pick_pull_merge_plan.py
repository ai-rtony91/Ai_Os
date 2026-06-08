"""Build a DRY_RUN-only pick-and-pull merge plan for HRQ-001."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_TYPE = "operator_relief_hrq001_pick_pull_merge_plan_v1"
CANONICAL_FILE = Path("docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md")
DUPLICATE_FILE = Path("docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md")
DECISION_DIFF_PATH = Path("Reports/operator_relief/decision_packets/worker_branch_lane_rules_decision_diff.json")
OUTPUT_ROOT = Path("Reports/operator_relief/hrq001_pick_pull_merge_plan")
JSON_OUTPUT_PATH = OUTPUT_ROOT / "hrq001_pick_pull_merge_plan.json"
MARKDOWN_OUTPUT_PATH = OUTPUT_ROOT / "hrq001_pick_pull_merge_plan.md"
BLOCKED_ACTIONS = [
    "modify workflow docs",
    "delete files",
    "canonicalize",
    "generate executable APPLY packets",
    "modify protected governance/security docs",
]


@dataclass(frozen=True)
class HRQ001PickPullMergePlanResult:
    report_type: str
    generated_at: str
    executable: bool
    apply_ready_paths: list[str]
    canonical_file: str
    duplicate_file: str
    source_decision_diff: str
    sections_already_covered: list[dict[str, Any]]
    unique_sections_to_pull_into_canonical: list[dict[str, Any]]
    conflicting_sections_needing_human_review: list[dict[str, Any]]
    obsolete_sections_to_prune_later: list[dict[str, Any]]
    recommended_merge_order: list[str]
    validation_commands: list[str]
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


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


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


def _section_preview(sections: dict[str, str], heading: str) -> str:
    text = " ".join(sections.get(heading, "").split())
    return text[:240]


def _conflicts(diff: dict[str, Any]) -> list[dict[str, Any]]:
    conflicts = diff.get("conflicting_sections")
    if not isinstance(conflicts, list):
        return []
    result: list[dict[str, Any]] = []
    for conflict in conflicts:
        if isinstance(conflict, dict):
            result.append(
                {
                    "section": f"{conflict.get('canonical_heading')} / {conflict.get('duplicate_heading')}",
                    "reason": conflict.get("reason") or "Shared section has different content.",
                    "human_review_required": True,
                }
            )
    return result


def build_plan(repo_root: Path) -> HRQ001PickPullMergePlanResult:
    root = repo_root.resolve()
    canonical_text = _load_text(root / CANONICAL_FILE)
    duplicate_text = _load_text(root / DUPLICATE_FILE)
    canonical_sections = _extract_sections(canonical_text)
    duplicate_sections = _extract_sections(duplicate_text)
    diff = _load_json(root / DECISION_DIFF_PATH)

    sections_already_covered = [
        {
            "duplicate_section": "Required Worker Metadata",
            "canonical_coverage": "Required Lane Metadata",
            "reason": "Canonical metadata is broader and includes supervisor, zone, packet, lock, approval, validators, and stop point.",
        },
        {
            "duplicate_section": "Path Rules",
            "canonical_coverage": "Path Ownership",
            "reason": "Canonical path ownership preserves the no-secrets, no-protected-root, no-trading-execution boundary with newer wording.",
        },
        {
            "duplicate_section": "Report Rules",
            "canonical_coverage": "Required Lane Metadata and Collision Handling",
            "reason": "Canonical rules already require report path, validation commands, planned ownership, collision blocking, and operator assignment.",
        },
        {
            "duplicate_section": "Safety",
            "canonical_coverage": "Purpose and Validation",
            "reason": "Canonical document already states it does not create branches, worktrees, commits, pushes, merges, or runtime changes.",
        },
        {
            "duplicate_section": "Allowed Worker Lanes",
            "canonical_coverage": "Allowed Worker Lanes",
            "reason": "Canonical lane list includes the legacy lanes and adds current Codex East, Claude Code West, command, validator, and worker lanes.",
        },
    ]
    unique_sections_to_pull = [
        {
            "source_section": "Branch Naming",
            "target_section": "Branch Naming",
            "pull_candidate": "Legacy worker branch examples",
            "reason": "Duplicate contains practical examples for worker/work-intelligence, operator-orchestration, and dashboard-ui branch names that may improve operator readability.",
            "content_preview": _section_preview(duplicate_sections, "Branch Naming"),
            "human_review_required": True,
        },
        {
            "source_section": "Report Rules",
            "target_section": "Required Lane Metadata or Collision Handling",
            "pull_candidate": "Concise integration-lane report check wording",
            "reason": "Duplicate states that integration checks worker reports before merge or APPLY review; canonical covers the mechanics but may benefit from this concise review phrase.",
            "content_preview": _section_preview(duplicate_sections, "Report Rules"),
            "human_review_required": True,
        },
    ]
    obsolete_sections_to_prune = [
        {
            "duplicate_section": "Historical/reference-only legacy preamble",
            "reason": "Preserve as archive context only; do not promote into canonical workflow text.",
        },
        {
            "duplicate_section": "Required Worker Metadata",
            "reason": "Superseded by canonical Required Lane Metadata.",
        },
        {
            "duplicate_section": "Path Rules",
            "reason": "Superseded by canonical Path Ownership.",
        },
        {
            "duplicate_section": "Safety",
            "reason": "Superseded by canonical Purpose and Validation safety language.",
        },
        {
            "duplicate_section": "Allowed Worker Lanes",
            "reason": "Legacy list is narrower than the current canonical lane list.",
        },
    ]

    return HRQ001PickPullMergePlanResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        apply_ready_paths=[],
        canonical_file=_normalize_path(CANONICAL_FILE),
        duplicate_file=_normalize_path(DUPLICATE_FILE),
        source_decision_diff=_normalize_path(DECISION_DIFF_PATH),
        sections_already_covered=sections_already_covered,
        unique_sections_to_pull_into_canonical=unique_sections_to_pull,
        conflicting_sections_needing_human_review=_conflicts(diff),
        obsolete_sections_to_prune_later=obsolete_sections_to_prune,
        recommended_merge_order=[
            "Review Branch Naming examples and decide whether to add a short examples block.",
            "Review Report Rules wording and decide whether any concise report-check sentence improves canonical clarity.",
            "Do not copy legacy Allowed Worker Lanes because canonical lane list is newer.",
            "Do not copy Required Worker Metadata, Path Rules, or Safety wholesale because canonical sections already supersede them.",
            "Prepare a separate explicitly approved APPLY packet only if human review selects exact text and target insertion points.",
        ],
        validation_commands=[
            "python -m py_compile automation/operator_relief/hrq001_pick_pull_merge_plan.py",
            "python -m pytest tests/operator_relief/test_hrq001_pick_pull_merge_plan.py",
            "git diff --check",
            "git status --short --branch",
        ],
        rollback_plan=[
            "No rollback needed for this DRY_RUN report because workflow docs are not modified.",
            "A future APPLY packet must record pre-change canonical and duplicate evidence before editing.",
            "A future APPLY packet must stop before staging if selected text or target insertion point expands beyond HRQ-001.",
        ],
        blocked_actions=list(BLOCKED_ACTIONS),
        safety={
            "executable": False,
            "dry_run_only": True,
            "review_plan_only": True,
            "workflow_docs_modified": False,
            "files_deleted": False,
            "canonicalization_performed": False,
            "executable_apply_packet_generated": False,
            "protected_docs_modified": False,
            "hrq002_touched": False,
            "hrq003_touched": False,
            "apply_ready_paths_empty": True,
        },
        recommended_next_action="Human review should select exact HRQ-001 text, if any, before a future APPLY packet is drafted.",
    )


def render_markdown(result: HRQ001PickPullMergePlanResult) -> str:
    lines = [
        "# HRQ-001 Pick-and-Pull Merge Plan",
        "",
        "```json",
        '{ "executable": false }',
        "```",
        "",
        f"- Canonical file: `{result.canonical_file}`",
        f"- Duplicate file: `{result.duplicate_file}`",
        "- Apply ready paths: `[]`",
        "",
        "## Unique Sections To Pull",
    ]
    for item in result.unique_sections_to_pull_into_canonical:
        lines.append(f"- {item['source_section']} -> {item['target_section']}: {item['pull_candidate']}")
    lines.extend(["", "## Obsolete Sections To Prune Later"])
    for item in result.obsolete_sections_to_prune_later:
        lines.append(f"- {item['duplicate_section']}: {item['reason']}")
    lines.extend(["", "## Conflicts"])
    for item in result.conflicting_sections_needing_human_review:
        lines.append(f"- {item['section']}: {item['reason']}")
    lines.extend(["", "## Blocked Actions"])
    for action in result.blocked_actions:
        lines.append(f"- {action}")
    return "\n".join(lines).rstrip() + "\n"


def _output_root(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_ROOT).resolve()
    allowed = (root / OUTPUT_ROOT).resolve()
    if not (output == allowed or allowed in output.parents):
        raise ValueError("HRQ-001 pick-and-pull plan must be written under Reports/operator_relief/hrq001_pick_pull_merge_plan/.")
    return output


def write_reports(result: HRQ001PickPullMergePlanResult, repo_root: Path) -> list[Path]:
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
    parser = argparse.ArgumentParser(description="Build DRY_RUN-only HRQ-001 pick-and-pull merge plan.")
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
