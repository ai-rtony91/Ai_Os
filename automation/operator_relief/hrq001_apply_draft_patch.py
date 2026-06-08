"""Generate a DRY_RUN-only draft patch for HRQ-001."""

from __future__ import annotations

import argparse
import difflib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_TYPE = "operator_relief_hrq001_apply_draft_patch_v1"
CANONICAL_FILE = Path("docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md")
DUPLICATE_FILE = Path("docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md")
OUTPUT_ROOT = Path("Reports/operator_relief/hrq001_apply_draft_patch")
DIFF_OUTPUT_PATH = OUTPUT_ROOT / "hrq001_apply_draft_patch.diff"
JSON_OUTPUT_PATH = OUTPUT_ROOT / "hrq001_apply_draft_patch.json"
MARKDOWN_OUTPUT_PATH = OUTPUT_ROOT / "hrq001_apply_draft_patch.md"
BRANCH_SECTION = "Branch Naming"
REPORT_SECTION = "Report Rules"


@dataclass(frozen=True)
class HRQ001ApplyDraftPatchResult:
    report_type: str
    generated_at: str
    executable: bool
    canonical_target: str
    duplicate_source: str
    sections_included: list[dict[str, Any]]
    proposed_insertions: list[dict[str, Any]]
    diff_output_path: str
    json_output_path: str
    markdown_output_path: str
    patch_diff: str
    apply_ready_paths: list[str]
    safety: dict[str, Any]
    recommended_next_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _extract_section(markdown: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(markdown)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+.+$", markdown[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(markdown)
    return markdown[start:end].strip()


def _extract_legacy_branch_examples(duplicate_text: str) -> str:
    branch_section = _extract_section(duplicate_text, BRANCH_SECTION)
    match = re.search(r"Examples:\s*\n\s*```text\n(?P<examples>.*?)\n```", branch_section, re.DOTALL)
    if not match:
        return ""
    examples = match.group("examples").strip()
    return (
        "Legacy worker branch examples for human review:\n\n"
        "```text\n"
        f"{examples}\n"
        "```\n"
    )


def _report_rules_sentence(duplicate_text: str) -> str:
    section = _extract_section(duplicate_text, REPORT_SECTION)
    sentence = "The integration lane checks those reports before any merge or APPLY review."
    if sentence not in section:
        return ""
    return (
        "Worker reports should include planned files and validation commands. "
        f"{sentence}\n"
    )


def _insert_after_worker_pattern(canonical_text: str, insertion: str) -> str:
    marker = "```text\nworker/<lane>/<phase>-<short-task>\n```\n"
    if not insertion or insertion in canonical_text or marker not in canonical_text:
        return canonical_text
    return canonical_text.replace(marker, f"{marker}\n{insertion}\n", 1)


def _insert_after_collision_heading(canonical_text: str, insertion: str) -> str:
    marker = "## Collision Handling\n\n"
    if not insertion or insertion in canonical_text or marker not in canonical_text:
        return canonical_text
    return canonical_text.replace(marker, f"{marker}{insertion}\n", 1)


def _proposed_text(canonical_text: str, duplicate_text: str) -> tuple[str, list[dict[str, Any]]]:
    branch_examples = _extract_legacy_branch_examples(duplicate_text)
    report_sentence = _report_rules_sentence(duplicate_text)
    proposed = _insert_after_worker_pattern(canonical_text, branch_examples)
    proposed = _insert_after_collision_heading(proposed, report_sentence)
    insertions = [
        {
            "source_section": BRANCH_SECTION,
            "target_section": BRANCH_SECTION,
            "description": "legacy worker branch examples",
            "content": branch_examples,
            "included": bool(branch_examples),
        },
        {
            "source_section": REPORT_SECTION,
            "target_section": "Collision Handling",
            "description": "concise integration-lane report check wording",
            "content": report_sentence,
            "included": bool(report_sentence),
        },
    ]
    return proposed, insertions


def _diff(original: str, proposed: str) -> str:
    lines = difflib.unified_diff(
        original.splitlines(keepends=True),
        proposed.splitlines(keepends=True),
        fromfile=_normalize_path(CANONICAL_FILE),
        tofile=f"{_normalize_path(CANONICAL_FILE)} (draft only)",
    )
    return "".join(lines)


def build_patch(repo_root: Path) -> HRQ001ApplyDraftPatchResult:
    root = repo_root.resolve()
    canonical_text = _load_text(root / CANONICAL_FILE)
    duplicate_text = _load_text(root / DUPLICATE_FILE)
    proposed_text, insertions = _proposed_text(canonical_text, duplicate_text)
    patch_diff = _diff(canonical_text, proposed_text)
    return HRQ001ApplyDraftPatchResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        canonical_target=_normalize_path(CANONICAL_FILE),
        duplicate_source=_normalize_path(DUPLICATE_FILE),
        sections_included=[
            {
                "source_section": BRANCH_SECTION,
                "target_section": BRANCH_SECTION,
                "purpose": "Add practical legacy worker branch examples for review.",
            },
            {
                "source_section": REPORT_SECTION,
                "target_section": "Collision Handling",
                "purpose": "Add concise integration-lane report check wording for review.",
            },
        ],
        proposed_insertions=insertions,
        diff_output_path=_normalize_path(DIFF_OUTPUT_PATH),
        json_output_path=_normalize_path(JSON_OUTPUT_PATH),
        markdown_output_path=_normalize_path(MARKDOWN_OUTPUT_PATH),
        patch_diff=patch_diff,
        apply_ready_paths=[],
        safety={
            "executable": False,
            "dry_run_only": True,
            "patch_diff_only": True,
            "workflow_docs_modified": False,
            "files_deleted": False,
            "canonicalization_performed": False,
            "executable_apply_packet_generated": False,
            "protected_docs_modified": False,
            "hrq002_touched": False,
            "hrq003_touched": False,
            "apply_ready_paths_empty": True,
        },
        recommended_next_action="Human review must approve exact text before any future APPLY packet is created.",
    )


def render_markdown(result: HRQ001ApplyDraftPatchResult) -> str:
    included = "\n".join(
        f"- {item['source_section']} -> {item['target_section']}: {item['purpose']}"
        for item in result.sections_included
    )
    return (
        "# HRQ-001 Apply Draft Patch\n\n"
        "```json\n"
        '{ "executable": false }\n'
        "```\n\n"
        f"- Canonical target: `{result.canonical_target}`\n"
        f"- Duplicate source: `{result.duplicate_source}`\n"
        "- Apply ready paths: `[]`\n\n"
        "## Sections Included\n\n"
        f"{included}\n\n"
        "## Draft Diff\n\n"
        "```diff\n"
        f"{result.patch_diff}"
        "```\n"
    )


def _output_root(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_ROOT).resolve()
    allowed = (root / OUTPUT_ROOT).resolve()
    if not (output == allowed or allowed in output.parents):
        raise ValueError("HRQ-001 draft patch must be written under Reports/operator_relief/hrq001_apply_draft_patch/.")
    return output


def write_reports(result: HRQ001ApplyDraftPatchResult, repo_root: Path) -> list[Path]:
    output = _output_root(repo_root)
    output.mkdir(parents=True, exist_ok=True)
    diff_path = repo_root.resolve() / DIFF_OUTPUT_PATH
    json_path = repo_root.resolve() / JSON_OUTPUT_PATH
    markdown_path = repo_root.resolve() / MARKDOWN_OUTPUT_PATH
    diff_path.write_text(result.patch_diff, encoding="utf-8")
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(result.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    markdown_path.write_text(render_markdown(result), encoding="utf-8")
    return [diff_path, json_path, markdown_path]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build DRY_RUN-only HRQ-001 draft patch.")
    parser.add_argument("--write-report", action="store_true", help="Write diff, JSON, and markdown reports.")
    args = parser.parse_args(argv)
    result = build_patch(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_report:
        payload["written_files"] = [_normalize_path(path) for path in write_reports(result, Path.cwd())]
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
