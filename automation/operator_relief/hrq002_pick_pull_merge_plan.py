"""Build a DRY_RUN-only pick-and-pull merge plan for HRQ-002."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_TYPE = "operator_relief_hrq002_pick_pull_merge_plan_v1"
CANDIDATE_ID = "HRQ-002-parallel_codex_workflow"
CANONICAL_FILE = Path("docs/workflows/PARALLEL_CODEX_WORKFLOW.md")
DUPLICATE_FILE = Path("docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md")
DECISION_DIFF_PATH = Path("Reports/operator_relief/decision_packets/parallel_codex_workflow_decision_diff.json")
OUTPUT_ROOT = Path("Reports/operator_relief/hrq002_pick_pull_merge_plan")
JSON_OUTPUT_PATH = OUTPUT_ROOT / "hrq002_pick_pull_merge_plan.json"
MARKDOWN_OUTPUT_PATH = OUTPUT_ROOT / "hrq002_pick_pull_merge_plan.md"
BLOCKED_ACTIONS = [
    "modify workflow docs",
    "delete files",
    "canonicalize",
    "generate executable APPLY packets",
    "touch HRQ-001",
    "touch HRQ-003",
    "modify protected governance/security docs",
    "stage files",
    "commit",
    "push",
]


@dataclass(frozen=True)
class HRQ002PickPullMergePlanResult:
    report_type: str
    generated_at: str
    executable: bool
    apply_ready_paths: list[str]
    candidate_id: str
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


def _repo_relative_path(path: Path, repo_root: Path) -> str:
    try:
        return _normalize_path(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return _normalize_path(path)


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
    return " ".join(sections.get(heading, "").split())[:260]


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
                    "reason": conflict.get("reason") or "Shared section has materially different content.",
                    "human_review_required": True,
                }
            )
    return result


def _unique_pull_candidates(duplicate_sections: dict[str, str]) -> list[dict[str, Any]]:
    candidates = [
        (
            "Worker Lanes",
            "Lane Model",
            "8-window worker lane table and scope mapping",
            "Duplicate contains concrete worker-number, lane, and scope mapping that may be useful as an example or appendix.",
        ),
        (
            "Start DRY_RUN Crew",
            "Lane Model or Worker Report Contract",
            "launcher behavior, fallback mode, registry config, and instruction-window guidance",
            "Duplicate contains launcher and registry behavior that should be preserved if still current.",
        ),
        (
            "Validate Worker Reports",
            "Validation",
            "parallel worker report validator checklist",
            "Duplicate includes concrete validator expectations such as registry, queue example, eight workers, launch config, and overlap checks.",
        ),
        (
            "Controlled APPLY Lane",
            "Lane Model or Safety Rules",
            "controlled serial APPLY lane procedure",
            "Duplicate includes serial APPLY procedure and human prompts that should not be lost without review.",
        ),
        (
            "Git Rules",
            "Safety Rules",
            "explicit file-path staging, batch-clean commit, and final push approval rules",
            "Duplicate has concise git rules that reinforce no git add dot and no push until operator approval.",
        ),
        (
            "Standard Batch Validation",
            "Validation",
            "standard batch validation command block",
            "Duplicate has a concrete validation command sequence that may complement the canonical validation section.",
        ),
    ]
    return [
        {
            "source_section": source,
            "target_section": target,
            "pull_candidate": label,
            "reason": reason,
            "content_preview": _section_preview(duplicate_sections, source),
            "human_review_required": True,
        }
        for source, target, label, reason in candidates
        if source in duplicate_sections
    ]


def build_plan(repo_root: Path) -> HRQ002PickPullMergePlanResult:
    root = repo_root.resolve()
    duplicate_sections = _extract_sections(_load_text(root / DUPLICATE_FILE))
    diff = _load_json(root / DECISION_DIFF_PATH)
    return HRQ002PickPullMergePlanResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        apply_ready_paths=[],
        candidate_id=CANDIDATE_ID,
        canonical_file=_normalize_path(CANONICAL_FILE),
        duplicate_file=_normalize_path(DUPLICATE_FILE),
        source_decision_diff=_normalize_path(DECISION_DIFF_PATH),
        sections_already_covered=[
            {
                "duplicate_section": "Purpose",
                "covered_aspect": "supervised parallel DRY_RUN plus controlled serial APPLY pattern",
                "canonical_coverage": "Purpose",
                "reason": "Canonical already states the supervised parallel DRY_RUN and controlled serial APPLY pattern with stronger no-permission language.",
            },
            {
                "duplicate_section": "Safety Rules",
                "covered_aspect": "core safety boundaries",
                "canonical_coverage": "Safety Rules",
                "reason": "Canonical safety rules preserve no secrets, live trading, overlap, commit/push, and external service limits with newer wording.",
            },
        ],
        unique_sections_to_pull_into_canonical=_unique_pull_candidates(duplicate_sections),
        conflicting_sections_needing_human_review=_conflicts(diff),
        obsolete_sections_to_prune_later=[
            {
                "duplicate_section": "Historical/reference-only legacy preamble",
                "reason": "Preserve as archive context only; do not promote into canonical workflow text.",
            },
            {
                "duplicate_section": "Purpose",
                "reason": "Canonical Purpose is newer and more explicit that the workflow is not permission to launch, commit, push, merge, or run live systems.",
            },
            {
                "duplicate_section": "Safety Rules",
                "reason": "Canonical Safety Rules are broader and include package install and external service connection constraints.",
            },
        ],
        recommended_merge_order=[
            "Review Worker Lanes table and decide whether to add it as an example appendix or leave it historical.",
            "Review Start DRY_RUN Crew launcher guidance against current automation before any canonical merge.",
            "Review Validate Worker Reports checklist and pull only current validator expectations.",
            "Review Controlled APPLY Lane procedure and keep it subordinate to current protected-action gates.",
            "Review Git Rules for concise wording, without creating new commit or push authority.",
            "Review Standard Batch Validation command block and keep only currently valid commands.",
            "Prepare a separate explicitly approved APPLY packet only after exact text and target sections are selected.",
        ],
        validation_commands=[
            "python -m py_compile automation/operator_relief/hrq002_pick_pull_merge_plan.py",
            "python -m pytest tests/operator_relief/test_hrq002_pick_pull_merge_plan.py",
            "python -m automation.operator_relief.hrq002_pick_pull_merge_plan --write-report",
            "git diff --check",
            "git status --short --branch",
        ],
        rollback_plan=[
            "No rollback needed for this DRY_RUN report because workflow docs are not modified.",
            "A future APPLY packet must record pre-change canonical and duplicate evidence before editing.",
            "A future APPLY packet must stop before staging if selected text or target insertion point expands beyond HRQ-002.",
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
            "hrq001_touched": False,
            "hrq003_touched": False,
            "apply_ready_paths_empty": True,
        },
        recommended_next_action="Human review should select exact HRQ-002 text, if any, before a future APPLY packet is drafted.",
    )


def render_markdown(result: HRQ002PickPullMergePlanResult) -> str:
    lines = [
        "# HRQ-002 Pick-and-Pull Merge Plan",
        "",
        "```json",
        '{ "executable": false, "apply_ready_paths": [] }',
        "```",
        "",
        f"- Candidate: `{result.candidate_id}`",
        f"- Canonical file: `{result.canonical_file}`",
        f"- Duplicate file: `{result.duplicate_file}`",
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
        raise ValueError("HRQ-002 pick-and-pull plan must be written under Reports/operator_relief/hrq002_pick_pull_merge_plan/.")
    return output


def write_reports(result: HRQ002PickPullMergePlanResult, repo_root: Path) -> list[Path]:
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
    parser = argparse.ArgumentParser(description="Build DRY_RUN-only HRQ-002 pick-and-pull merge plan.")
    parser.add_argument("--write-report", action="store_true", help="Write JSON and markdown reports.")
    args = parser.parse_args(argv)
    result = build_plan(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_report:
        repo_root = Path.cwd()
        payload["written_files"] = [_repo_relative_path(path, repo_root) for path in write_reports(result, repo_root)]
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
