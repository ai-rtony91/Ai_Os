"""Generate a DRY_RUN-only draft patch for HRQ-002."""

from __future__ import annotations

import argparse
import difflib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_TYPE = "operator_relief_hrq002_apply_draft_patch_v1"
CANONICAL_FILE = Path("docs/workflows/PARALLEL_CODEX_WORKFLOW.md")
DUPLICATE_FILE = Path("docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md")
OUTPUT_ROOT = Path("Reports/operator_relief/hrq002_apply_draft_patch")
DIFF_OUTPUT_PATH = OUTPUT_ROOT / "hrq002_apply_draft_patch.diff"
JSON_OUTPUT_PATH = OUTPUT_ROOT / "hrq002_apply_draft_patch.json"
MARKDOWN_OUTPUT_PATH = OUTPUT_ROOT / "hrq002_apply_draft_patch.md"
SECTIONS_TO_PULL = [
    "Worker Lanes",
    "Start DRY_RUN Crew",
    "Validate Worker Reports",
    "Controlled APPLY Lane",
    "Git Rules",
    "Standard Batch Validation",
]


@dataclass(frozen=True)
class HRQ002ApplyDraftPatchResult:
    report_type: str
    generated_at: str
    executable: bool
    canonical_target: str
    duplicate_source: str
    sections_included: list[dict[str, Any]]
    proposed_insertion_heading: str
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


def _repo_relative_path(path: Path, repo_root: Path) -> str:
    try:
        return _normalize_path(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return _normalize_path(path)


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


def _section_block(heading: str, body: str) -> str:
    if not body:
        return ""
    return f"### {heading}\n\n{body.strip()}\n"


def _included_sections(duplicate_text: str) -> list[dict[str, Any]]:
    included: list[dict[str, Any]] = []
    for heading in SECTIONS_TO_PULL:
        body = _extract_section(duplicate_text, heading)
        included.append(
            {
                "source_section": heading,
                "target_section": "HRQ-002 Operational Details For Review",
                "included": bool(body),
                "content_preview": " ".join(body.split())[:260],
            }
        )
    return included


def _draft_operational_details(duplicate_text: str) -> str:
    blocks = [_section_block(heading, _extract_section(duplicate_text, heading)) for heading in SECTIONS_TO_PULL]
    content = "\n".join(block for block in blocks if block)
    if not content:
        return ""
    return (
        "## HRQ-002 Operational Details For Review\n\n"
        "The following review-only material is pulled from the historical duplicate workflow. "
        "It is not active authority unless a future approved APPLY packet promotes exact text.\n\n"
        f"{content}"
    ).rstrip() + "\n"


def _insert_after_lane_model(canonical_text: str, insertion: str) -> str:
    if not insertion or insertion in canonical_text:
        return canonical_text
    pattern = re.compile(r"(^##\s+Lane Model\s*$.*?)(?=^##\s+.+$)", re.MULTILINE | re.DOTALL)
    match = pattern.search(canonical_text)
    if not match:
        return canonical_text.rstrip() + "\n\n" + insertion
    lane_model = match.group(1).rstrip()
    replacement = f"{lane_model}\n\n{insertion}\n"
    return canonical_text[: match.start()] + replacement + canonical_text[match.end() :]


def _proposed_text(canonical_text: str, duplicate_text: str) -> tuple[str, str]:
    insertion = _draft_operational_details(duplicate_text)
    return _insert_after_lane_model(canonical_text, insertion), insertion


def _diff(original: str, proposed: str) -> str:
    lines = difflib.unified_diff(
        original.splitlines(keepends=True),
        proposed.splitlines(keepends=True),
        fromfile=_normalize_path(CANONICAL_FILE),
        tofile=f"{_normalize_path(CANONICAL_FILE)} (draft only)",
    )
    return "".join(lines)


def build_patch(repo_root: Path) -> HRQ002ApplyDraftPatchResult:
    root = repo_root.resolve()
    canonical_text = _load_text(root / CANONICAL_FILE)
    duplicate_text = _load_text(root / DUPLICATE_FILE)
    proposed_text, insertion = _proposed_text(canonical_text, duplicate_text)
    patch_diff = _diff(canonical_text, proposed_text)
    return HRQ002ApplyDraftPatchResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        canonical_target=_normalize_path(CANONICAL_FILE),
        duplicate_source=_normalize_path(DUPLICATE_FILE),
        sections_included=_included_sections(duplicate_text),
        proposed_insertion_heading="HRQ-002 Operational Details For Review" if insertion else "",
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
            "hrq001_touched": False,
            "hrq003_touched": False,
            "apply_ready_paths_empty": True,
        },
        recommended_next_action="Human review must approve exact HRQ-002 text before any future APPLY packet is created.",
    )


def render_markdown(result: HRQ002ApplyDraftPatchResult) -> str:
    included = "\n".join(
        f"- {item['source_section']}: included={str(item['included']).lower()}"
        for item in result.sections_included
    )
    return (
        "# HRQ-002 Apply Draft Patch\n\n"
        "```json\n"
        '{ "executable": false, "apply_ready_paths": [] }\n'
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
        raise ValueError("HRQ-002 draft patch must be written under Reports/operator_relief/hrq002_apply_draft_patch/.")
    return output


def write_reports(result: HRQ002ApplyDraftPatchResult, repo_root: Path) -> list[Path]:
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
    parser = argparse.ArgumentParser(description="Build DRY_RUN-only HRQ-002 draft patch.")
    parser.add_argument("--write-report", action="store_true", help="Write diff, JSON, and markdown reports.")
    args = parser.parse_args(argv)
    result = build_patch(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_report:
        repo_root = Path.cwd()
        payload["written_files"] = [_repo_relative_path(path, repo_root) for path in write_reports(result, repo_root)]
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
