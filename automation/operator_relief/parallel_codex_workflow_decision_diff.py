"""Build a review-only diff for Parallel Codex Workflow authority."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_TYPE = "operator_relief_parallel_codex_workflow_decision_diff_v1"
SOURCE_DECISION_PACKET = Path(
    "Reports/operator_relief/decision_packets/canonical_decision_packet_02_parallel_codex_workflow.json"
)
REPORT_PATH = Path("Reports/operator_relief/decision_packets/parallel_codex_workflow_decision_diff.json")
CANONICAL_CANDIDATE = Path("docs/workflows/PARALLEL_CODEX_WORKFLOW.md")
DUPLICATE_CANDIDATE = Path("docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md")

KEEP_WORKFLOWS_AS_CANONICAL = "KEEP_WORKFLOWS_AS_CANONICAL"
MERGE_UNIQUE_CONTENT_FIRST = "MERGE_UNIQUE_CONTENT_FIRST"
KEEP_BOTH_FOR_NOW = "KEEP_BOTH_FOR_NOW"
NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"

WEAK_SECTION_TITLES = {
    "purpose",
    "status",
    "summary",
    "validation",
    "safety rules",
}
AUTHORITY_TERMS = (
    "worker",
    "lane",
    "allowed paths",
    "blocked paths",
    "validation",
    "validator",
    "apply",
    "commit",
    "push",
    "registry",
    "launcher",
    "must",
    "do not",
    "required",
    "operator approval",
)


@dataclass(frozen=True)
class DecisionDiffResult:
    report_type: str
    generated_at: str
    executable: bool
    source_decision_packet: str
    canonical_candidate: str
    duplicate_candidate: str
    identical: bool
    canonical_only_sections: list[dict[str, Any]]
    duplicate_only_sections: list[dict[str, Any]]
    shared_sections: list[dict[str, Any]]
    conflicting_sections: list[dict[str, Any]]
    duplicate_unique_authority: list[dict[str, Any]]
    recommended_human_decision: str
    risks: list[str]
    safe_to_generate_apply_packet_later: bool
    reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _strip_historical_banner(text: str) -> str:
    lines = text.splitlines()
    while lines and (lines[0].startswith(">") or not lines[0].strip()):
        lines.pop(0)
    return "\n".join(lines).strip()


def _normalize_text(text: str) -> str:
    text = _strip_historical_banner(text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def _section_key(title: str) -> str:
    title = re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()
    return title or "document"


def _parse_sections(text: str) -> dict[str, dict[str, str]]:
    sections: dict[str, dict[str, str]] = {}
    current_title = "Document"
    current_lines: list[str] = []

    def flush() -> None:
        content = "\n".join(current_lines).strip()
        key = _section_key(current_title)
        if content or key != "document":
            sections[key] = {
                "heading": current_title,
                "content": content,
                "normalized": _normalize_text(content),
            }

    for line in _strip_historical_banner(text).splitlines():
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            flush()
            current_title = match.group(2).strip()
            current_lines = []
        else:
            current_lines.append(line)
    flush()
    return sections


def _preview(content: str, limit: int = 260) -> str:
    compact = re.sub(r"\s+", " ", content).strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def _section_entry(section: dict[str, str]) -> dict[str, str]:
    return {
        "heading": section["heading"],
        "content_preview": _preview(section["content"]),
    }


def _shared_entry(key: str, canonical: dict[str, str], duplicate: dict[str, str]) -> dict[str, Any]:
    return {
        "section_key": key,
        "canonical_heading": canonical["heading"],
        "duplicate_heading": duplicate["heading"],
        "content_matches": canonical["normalized"] == duplicate["normalized"],
    }


def _conflict_entry(key: str, canonical: dict[str, str], duplicate: dict[str, str]) -> dict[str, Any]:
    return {
        "section_key": key,
        "canonical_heading": canonical["heading"],
        "duplicate_heading": duplicate["heading"],
        "canonical_preview": _preview(canonical["content"]),
        "duplicate_preview": _preview(duplicate["content"]),
        "reason": "Shared heading has materially different content.",
    }


def _is_weak_unique_section(section: dict[str, str]) -> bool:
    key = _section_key(section["heading"])
    content = section["normalized"]
    return key in WEAK_SECTION_TITLES and len(content) < 120


def _duplicate_authority(section: dict[str, str]) -> dict[str, Any] | None:
    normalized = section["normalized"]
    if not normalized:
        return None
    if not any(term in normalized for term in AUTHORITY_TERMS):
        return None
    return {
        "heading": section["heading"],
        "content_preview": _preview(section["content"], limit=320),
        "reason": "Duplicate section contains worker-lane, APPLY, launcher, registry, validation, git, or approval guidance.",
    }


def _reasons(
    identical: bool,
    canonical_only: list[dict[str, Any]],
    duplicate_only: list[dict[str, Any]],
    conflicts: list[dict[str, Any]],
    duplicate_authority: list[dict[str, Any]],
) -> list[str]:
    reasons: list[str] = []
    if identical:
        reasons.append("Canonical and duplicate workflow docs are text-identical after normalization.")
    else:
        reasons.append("Canonical and duplicate workflow docs are not identical.")
    if canonical_only:
        reasons.append("Canonical candidate contains sections not present in the duplicate candidate.")
    if duplicate_only:
        reasons.append("Duplicate candidate contains sections not present in the canonical candidate.")
    if conflicts:
        reasons.append("Shared headings contain different rule text and require review.")
    if duplicate_authority:
        reasons.append("Duplicate candidate contains unique authority or operating guidance that should not be lost.")
    if not duplicate_only and not conflicts and not duplicate_authority:
        reasons.append("Differences appear limited to canonical framing, metadata, or path references.")
    return reasons


def _recommended_decision(
    duplicate_only: list[dict[str, Any]],
    conflicts: list[dict[str, Any]],
    duplicate_authority: list[dict[str, Any]],
) -> str:
    if conflicts:
        return NEEDS_HUMAN_REVIEW
    if duplicate_only or duplicate_authority:
        return MERGE_UNIQUE_CONTENT_FIRST
    return KEEP_WORKFLOWS_AS_CANONICAL


def _risks(
    duplicate_only: list[dict[str, Any]],
    conflicts: list[dict[str, Any]],
    duplicate_authority: list[dict[str, Any]],
) -> list[str]:
    risks = [
        "This report is review-only and does not authorize source document edits.",
        "A later APPLY packet still requires explicit human approval and exact file scope.",
    ]
    if duplicate_only or duplicate_authority:
        risks.append("Duplicate candidate may contain unique operating rules that need extraction before any later deprecation review.")
    if conflicts:
        risks.append("Conflicting shared sections may hide rule drift between active and historical workflow text.")
    return risks


def build_decision_diff(repo_root: Path) -> DecisionDiffResult:
    root = repo_root.resolve()
    canonical_text = _read_text(root / CANONICAL_CANDIDATE)
    duplicate_text = _read_text(root / DUPLICATE_CANDIDATE)
    canonical_sections = _parse_sections(canonical_text)
    duplicate_sections = _parse_sections(duplicate_text)

    canonical_keys = set(canonical_sections)
    duplicate_keys = set(duplicate_sections)
    shared_keys = sorted(canonical_keys & duplicate_keys)

    canonical_only = [
        _section_entry(canonical_sections[key])
        for key in sorted(canonical_keys - duplicate_keys)
        if not _is_weak_unique_section(canonical_sections[key])
    ]
    duplicate_only = [
        _section_entry(duplicate_sections[key])
        for key in sorted(duplicate_keys - canonical_keys)
        if not _is_weak_unique_section(duplicate_sections[key])
    ]
    shared = [_shared_entry(key, canonical_sections[key], duplicate_sections[key]) for key in shared_keys]
    conflicts = [
        _conflict_entry(key, canonical_sections[key], duplicate_sections[key])
        for key in shared_keys
        if canonical_sections[key]["normalized"] != duplicate_sections[key]["normalized"]
    ]
    duplicate_authority = [
        authority
        for key in sorted(duplicate_keys - canonical_keys)
        if (authority := _duplicate_authority(duplicate_sections[key])) is not None
    ]

    identical = _normalize_text(canonical_text) == _normalize_text(duplicate_text)
    decision = _recommended_decision(duplicate_only, conflicts, duplicate_authority)

    return DecisionDiffResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        source_decision_packet=_normalize_path(SOURCE_DECISION_PACKET),
        canonical_candidate=_normalize_path(CANONICAL_CANDIDATE),
        duplicate_candidate=_normalize_path(DUPLICATE_CANDIDATE),
        identical=identical,
        canonical_only_sections=canonical_only,
        duplicate_only_sections=duplicate_only,
        shared_sections=shared,
        conflicting_sections=conflicts,
        duplicate_unique_authority=duplicate_authority,
        recommended_human_decision=decision,
        risks=_risks(duplicate_only, conflicts, duplicate_authority),
        safe_to_generate_apply_packet_later=decision == KEEP_WORKFLOWS_AS_CANONICAL,
        reasons=_reasons(identical, canonical_only, duplicate_only, conflicts, duplicate_authority),
    )


def _output_path(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / REPORT_PATH).resolve()
    allowed_root = (root / REPORT_PATH.parent).resolve()
    if not (output.parent == allowed_root and allowed_root in output.parents):
        raise ValueError("Decision diff must be written under Reports/operator_relief/decision_packets/.")
    return output


def write_report(result: DecisionDiffResult, repo_root: Path) -> Path:
    path = _output_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Parallel Codex Workflow decision diff.")
    parser.add_argument("--write-report", action="store_true", help="Write the review-only decision diff report.")
    args = parser.parse_args(argv)

    result = build_decision_diff(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_report:
        payload["written_file"] = _normalize_path(write_report(result, Path.cwd()))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
