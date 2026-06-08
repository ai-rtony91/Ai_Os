"""Generate a DRY_RUN-only HRQ-001 duplicate deprecation notice draft."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.operator_relief.hrq001_duplicate_retirement_plan import (
    CANONICAL_FILE,
    DUPLICATE_FILE,
    OUTPUT_ROOT,
)


REPORT_TYPE = "operator_relief_hrq001_deprecation_notice_draft_v1"
JSON_OUTPUT_PATH = OUTPUT_ROOT / "hrq001_deprecation_notice_draft.json"
MARKDOWN_OUTPUT_PATH = OUTPUT_ROOT / "hrq001_deprecation_notice_draft.md"
BLOCKED_ACTIONS = [
    "modify duplicate file",
    "delete files",
    "update references",
    "canonicalize further",
    "touch HRQ-002",
    "touch HRQ-003",
    "stage files",
    "commit",
    "push",
]


@dataclass(frozen=True)
class HRQ001DeprecationNoticeDraftResult:
    report_type: str
    generated_at: str
    executable: bool
    draft_only: bool
    duplicate_path: str
    canonical_replacement: str
    notice_markdown: str
    notice_output_paths: list[str]
    blocked_actions: list[str]
    safety: dict[str, Any]
    recommended_next_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def build_notice_text() -> str:
    return "\n".join(
        [
            "> Deprecated duplicate / reference-only HRQ-001 document.",
            ">",
            f"> Current canonical workflow authority lives in `{_normalize_path(CANONICAL_FILE)}`.",
            f"> This file `{_normalize_path(DUPLICATE_FILE)}` is retained only as historical/source evidence until references are reviewed.",
            "> Do not treat this file as active workflow authority.",
            "> Do not delete or archive this file without a separate approved retirement APPLY packet.",
        ]
    )


def build_draft(repo_root: Path) -> HRQ001DeprecationNoticeDraftResult:
    _ = repo_root
    notice = build_notice_text()
    return HRQ001DeprecationNoticeDraftResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        draft_only=True,
        duplicate_path=_normalize_path(DUPLICATE_FILE),
        canonical_replacement=_normalize_path(CANONICAL_FILE),
        notice_markdown=notice,
        notice_output_paths=[
            _normalize_path(JSON_OUTPUT_PATH),
            _normalize_path(MARKDOWN_OUTPUT_PATH),
        ],
        blocked_actions=list(BLOCKED_ACTIONS),
        safety={
            "executable": False,
            "dry_run_only": True,
            "draft_only": True,
            "duplicate_file_modified": False,
            "files_deleted": False,
            "references_updated": False,
            "canonicalization_performed": False,
            "hrq002_touched": False,
            "hrq003_touched": False,
        },
        recommended_next_action="Review this notice text before any separate APPLY packet edits the duplicate file.",
    )


def render_markdown(result: HRQ001DeprecationNoticeDraftResult) -> str:
    lines = [
        "# HRQ-001 Deprecation Notice Draft",
        "",
        "```json",
        '{ "executable": false, "draft_only": true }',
        "```",
        "",
        f"- Duplicate file: `{result.duplicate_path}`",
        f"- Canonical replacement: `{result.canonical_replacement}`",
        "",
        "## Draft Notice",
        "",
        result.notice_markdown,
        "",
        "## Blocked Actions",
    ]
    lines.extend(f"- {action}" for action in result.blocked_actions)
    return "\n".join(lines).rstrip() + "\n"


def _output_root(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_ROOT).resolve()
    allowed = (root / OUTPUT_ROOT).resolve()
    if not (output == allowed or allowed in output.parents):
        raise ValueError("HRQ-001 deprecation notice draft must be written under Reports/operator_relief/hrq001_duplicate_retirement_plan/.")
    return output


def write_reports(result: HRQ001DeprecationNoticeDraftResult, repo_root: Path) -> list[Path]:
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
    parser = argparse.ArgumentParser(description="Generate DRY_RUN-only HRQ-001 duplicate deprecation notice draft.")
    parser.add_argument("--write-report", action="store_true", help="Write JSON and markdown notice drafts.")
    args = parser.parse_args(argv)
    result = build_draft(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_report:
        payload["written_files"] = [_normalize_path(path) for path in write_reports(result, Path.cwd())]
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
