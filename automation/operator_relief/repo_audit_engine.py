"""Audit-only repository analysis engine for Operator Relief v1."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


SCAN_ROOTS = (Path("docs"), Path("automation/operator_relief"), Path("Reports"), Path("control"))
REPORT_ROOT = Path("Reports/operator_relief/audits")
SUPPORTED_SUFFIXES = {".md", ".markdown", ".json", ".yaml", ".yml", ".txt"}
EXCLUDED_DIR_NAMES = {".git", "__pycache__", "node_modules", "venv", ".venv", "build", "dist"}
EXCLUDED_PREFIXES = ("Reports/operator_relief/",)
MAX_FILES_SCANNED = 5000
MAX_HEADINGS_SCANNED = 12000
MAX_SECTIONS_SCANNED = 12000
MAX_NEAR_HEADING_BUCKET_SIZE = 80
MAX_NEAR_SECTION_BUCKET_SIZE = 60
MAX_HEADING_COMPARISONS = 25000
MAX_SECTION_COMPARISONS = 20000
MAX_DRIFT_COMPARISONS = 20000
FORBIDDEN_PREFIXES = (
    "AGENTS.md",
    "docs/governance/",
    "docs/security/",
    "services/",
    "apps/",
    "secrets/",
    "credentials/",
    "broker/",
    "api/",
    "live-trading/",
    "live_trading/",
    "order_execution/",
)
AUTHORITY_TERMS = (
    "source of truth",
    "authority",
    "canonical",
    "owner",
)
WORKFLOW_TERMS = (
    "startup",
    "onboarding",
    "workflow",
    "approval",
    "execution",
    "operator",
)
REFERENCE_PATTERN = re.compile(
    r"(?P<path>(?:docs|automation|Reports|control)/[A-Za-z0-9_./() -]+\.(?:md|json|yaml|yml|txt|ps1|py))"
)


@dataclass(frozen=True)
class AuditFile:
    path: str
    suffix: str
    headings: list[dict[str, Any]]
    sections: list[dict[str, Any]]
    outbound_references: list[str]
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RepoAuditReport:
    audit_summary: dict[str, Any]
    total_files_scanned: int
    duplicate_headings: list[dict[str, Any]]
    duplicate_sections: list[dict[str, Any]]
    source_of_truth_conflicts: list[dict[str, Any]]
    orphan_documents: list[dict[str, Any]]
    broken_references: list[dict[str, Any]]
    workflow_duplicates: list[dict[str, Any]]
    document_drift: list[dict[str, Any]]
    top_cleanup_candidates: list[dict[str, Any]]
    top_human_review_candidates: list[dict[str, Any]]
    scanned_files: list[str]
    safety: dict[str, bool]
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: Path | str) -> str:
    return Path(path).as_posix().lstrip("./")


def _is_forbidden(relative_path: str) -> bool:
    normalized = _normalize_path(relative_path)
    return any(
        normalized == prefix.rstrip("/") or normalized.startswith(prefix)
        for prefix in FORBIDDEN_PREFIXES
    )


def _is_excluded(relative_path: str) -> bool:
    normalized = _normalize_path(relative_path)
    parts = set(Path(normalized).parts)
    return any(part in EXCLUDED_DIR_NAMES for part in parts) or any(
        normalized == prefix.rstrip("/") or normalized.startswith(prefix)
        for prefix in EXCLUDED_PREFIXES
    )


def _is_supported(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_SUFFIXES


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _token_similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, _slug(left), _slug(right)).ratio()


def _extract_headings(relative_path: str, text: str) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            headings.append(
                {
                    "text": match.group(2).strip(),
                    "normalized": _slug(match.group(2)),
                    "level": len(match.group(1)),
                    "file": relative_path,
                    "line": line_number,
                    "executable": False,
                }
            )
    return headings


def _extract_sections(relative_path: str, text: str) -> list[dict[str, Any]]:
    headings = _extract_headings(relative_path, text)
    if not headings:
        normalized_text = "\n".join(line.rstrip() for line in text.splitlines()).strip()
        if not normalized_text:
            return []
        return [
            {
                "title": "(document)",
                "file": relative_path,
                "line": 1,
                "content": normalized_text,
                "hash": hashlib.sha256(normalized_text.lower().encode("utf-8")).hexdigest(),
                "executable": False,
            }
        ]

    lines = text.splitlines()
    sections: list[dict[str, Any]] = []
    for index, heading in enumerate(headings):
        start = heading["line"]
        end = headings[index + 1]["line"] - 1 if index + 1 < len(headings) else len(lines)
        content = "\n".join(line.rstrip() for line in lines[start:end]).strip()
        if len(content) < 20:
            continue
        sections.append(
            {
                "title": heading["text"],
                "file": relative_path,
                "line": heading["line"],
                "content": content,
                "hash": hashlib.sha256(content.lower().encode("utf-8")).hexdigest(),
                "executable": False,
            }
        )
    return sections


def _extract_references(text: str) -> list[str]:
    return sorted({_normalize_path(match.group("path")) for match in REFERENCE_PATTERN.finditer(text)})


def _collect_files(repo_root: Path) -> list[Path]:
    root = repo_root.resolve()
    files: list[Path] = []
    for scan_root in SCAN_ROOTS:
        candidate_root = root / scan_root
        if not candidate_root.exists():
            continue
        for path in candidate_root.rglob("*"):
            if not path.is_file() or not _is_supported(path):
                continue
            relative = _normalize_path(path.relative_to(root))
            if _is_forbidden(relative) or _is_excluded(relative):
                continue
            files.append(path)
    return sorted(files, key=lambda item: _normalize_path(item.relative_to(root)))[:MAX_FILES_SCANNED]


def _analyze_files(repo_root: Path) -> list[AuditFile]:
    root = repo_root.resolve()
    analyzed: list[AuditFile] = []
    for path in _collect_files(root):
        relative = _normalize_path(path.relative_to(root))
        text = _read_text(path)
        analyzed.append(
            AuditFile(
                path=relative,
                suffix=path.suffix.lower(),
                headings=_extract_headings(relative, text),
                sections=_extract_sections(relative, text),
                outbound_references=_extract_references(text),
                executable=False,
            )
        )
    return analyzed


def _heading_bucket_key(normalized: str) -> str:
    tokens = normalized.split()
    if not tokens:
        return ""
    return f"{tokens[0]}:{len(tokens)}"


def _section_bucket_key(title: str) -> str:
    tokens = _slug(title).split()
    if not tokens:
        return ""
    return f"{tokens[0]}:{len(tokens)}"


def _duplicate_headings(files: list[AuditFile]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    headings_scanned = 0
    heading_limit_hit = False
    for file in files:
        for heading in file.headings:
            if headings_scanned >= MAX_HEADINGS_SCANNED:
                heading_limit_hit = True
                break
            grouped.setdefault(heading["normalized"], []).append(heading)
            headings_scanned += 1
        if heading_limit_hit:
            break

    duplicates = [
        {
            "heading_text": occurrences[0]["text"],
            "document_locations": [{"file": item["file"], "line": item["line"]} for item in occurrences],
            "occurrence_count": len(occurrences),
            "confidence_score": 1.0,
            "executable": False,
        }
        for occurrences in grouped.values()
        if len({item["file"] for item in occurrences}) > 1 or len(occurrences) > 2
    ]

    headings = sorted(
        [occurrences[0] for occurrences in grouped.values()],
        key=lambda item: (item["normalized"], item["file"], item["line"]),
    )
    buckets: dict[str, list[dict[str, Any]]] = {}
    for heading in headings:
        buckets.setdefault(_heading_bucket_key(heading["normalized"]), []).append(heading)

    near: list[dict[str, Any]] = []
    comparisons = 0
    comparison_cap_hit = False
    bucket_truncation_hit = False
    for bucket_key in sorted(buckets):
        bucket = buckets[bucket_key]
        if len(bucket) > MAX_NEAR_HEADING_BUCKET_SIZE:
            bucket = bucket[:MAX_NEAR_HEADING_BUCKET_SIZE]
            bucket_truncation_hit = True
        for index, left in enumerate(bucket):
            if comparison_cap_hit:
                break
            for right in bucket[index + 1 :]:
                if comparisons >= MAX_HEADING_COMPARISONS:
                    comparison_cap_hit = True
                    break
                comparisons += 1
                if left["normalized"] == right["normalized"]:
                    continue
                score = _token_similarity(left["text"], right["text"])
                if score < 0.86:
                    continue
                near.append(
                    {
                        "heading_text": left["text"],
                        "near_heading_text": right["text"],
                        "document_locations": [
                            {"file": left["file"], "line": left["line"]},
                            {"file": right["file"], "line": right["line"]},
                        ],
                        "occurrence_count": 2,
                        "confidence_score": round(score, 3),
                        "executable": False,
                    }
                )
        if comparison_cap_hit:
            break

    metadata = {
        "headings_scanned": headings_scanned,
        "unique_heading_slugs_scanned": len(grouped),
        "heading_comparisons_performed": comparisons,
        "heading_comparison_cap": MAX_HEADING_COMPARISONS,
        "comparison_cap_hit": comparison_cap_hit,
        "heading_limit_hit": heading_limit_hit,
        "near_heading_bucket_truncation_hit": bucket_truncation_hit,
        "executable": False,
    }
    return (
        sorted(duplicates + near, key=lambda item: (-item["confidence_score"], item["heading_text"]))[:100],
        metadata,
    )


def _duplicate_sections(files: list[AuditFile]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    all_sections = [section for file in files for section in file.sections]
    sections = all_sections[:MAX_SECTIONS_SCANNED]
    grouped: dict[str, list[dict[str, Any]]] = {}
    for section in sections:
        grouped.setdefault(section["hash"], []).append(section)

    duplicates: list[dict[str, Any]] = [
        {
            "section_title": occurrences[0]["title"],
            "source_files": sorted({item["file"] for item in occurrences}),
            "similarity_score": 1.0,
            "confidence": 1.0,
            "executable": False,
        }
        for occurrences in grouped.values()
        if len({item["file"] for item in occurrences}) > 1
    ]

    buckets: dict[str, list[dict[str, Any]]] = {}
    for section in sections:
        buckets.setdefault(_section_bucket_key(section["title"]), []).append(section)

    comparisons = 0
    comparison_cap_hit = False
    bucket_truncation_hit = False
    for bucket_key in sorted(buckets):
        bucket = sorted(buckets[bucket_key], key=lambda item: (item["title"], item["file"], item["line"]))
        if len(bucket) > MAX_NEAR_SECTION_BUCKET_SIZE:
            bucket = bucket[:MAX_NEAR_SECTION_BUCKET_SIZE]
            bucket_truncation_hit = True
        for index, left in enumerate(bucket):
            if comparison_cap_hit:
                break
            for right in bucket[index + 1 :]:
                if comparisons >= MAX_SECTION_COMPARISONS:
                    comparison_cap_hit = True
                    break
                comparisons += 1
                if left["file"] == right["file"] or left["hash"] == right["hash"]:
                    continue
                score = _token_similarity(left["content"], right["content"])
                if score >= 0.84:
                    duplicates.append(
                        {
                            "section_title": left["title"],
                            "near_section_title": right["title"],
                            "source_files": sorted({left["file"], right["file"]}),
                            "similarity_score": round(score, 3),
                            "confidence": round(score, 3),
                            "executable": False,
                        }
                    )
        if comparison_cap_hit:
            break

    metadata = {
        "sections_scanned": len(sections),
        "section_comparisons_performed": comparisons,
        "section_comparison_cap": MAX_SECTION_COMPARISONS,
        "section_comparison_cap_hit": comparison_cap_hit,
        "section_limit_hit": len(all_sections) > len(sections),
        "near_section_bucket_truncation_hit": bucket_truncation_hit,
        "executable": False,
    }
    return sorted(duplicates, key=lambda item: (-item["confidence"], item["section_title"]))[:100], metadata


def _source_of_truth_conflicts(files: list[AuditFile]) -> list[dict[str, Any]]:
    candidates: dict[str, list[str]] = {}
    for file in files:
        text = " ".join(heading["text"] for heading in file.headings).lower()
        section_text = " ".join(section["content"] for section in file.sections).lower()
        combined = f"{text} {section_text}"
        for term in AUTHORITY_TERMS:
            if term in combined:
                candidates.setdefault(term, []).append(file.path)

    conflicts = []
    for term, paths in candidates.items():
        unique = sorted(set(paths))
        if len(unique) > 1:
            conflicts.append(
                {
                    "authority_candidates": term,
                    "conflicting_files": unique,
                    "recommended_review_targets": unique[:5],
                    "confidence": 0.76,
                    "executable": False,
                }
            )
    return conflicts


def _dead_documents(files: list[AuditFile]) -> list[dict[str, Any]]:
    all_paths = {file.path for file in files}
    inbound: dict[str, set[str]] = {path: set() for path in all_paths}
    for file in files:
        for target in file.outbound_references:
            if target in inbound:
                inbound[target].add(file.path)
    orphans = []
    for file in files:
        if not inbound[file.path] and not file.outbound_references:
            orphans.append(
                {
                    "orphan_candidate": file.path,
                    "confidence": 0.72,
                    "reason": "No inbound or outbound references in scanned graph.",
                    "executable": False,
                }
            )
        elif not inbound[file.path]:
            orphans.append(
                {
                    "orphan_candidate": file.path,
                    "confidence": 0.58,
                    "reason": "No inbound references in scanned graph.",
                    "executable": False,
                }
            )
    return sorted(orphans, key=lambda item: (-item["confidence"], item["orphan_candidate"]))[:100]


def _broken_references(repo_root: Path, files: list[AuditFile]) -> list[dict[str, Any]]:
    root = repo_root.resolve()
    broken = []
    for file in files:
        for target in file.outbound_references:
            if _is_forbidden(target):
                continue
            if not (root / target).exists():
                broken.append(
                    {
                        "broken_reference": target,
                        "source_file": file.path,
                        "target_file": target,
                        "confidence": 0.95,
                        "executable": False,
                    }
                )
    return broken


def _workflow_duplicates(files: list[AuditFile]) -> list[dict[str, Any]]:
    groups: dict[str, list[str]] = {}
    for file in files:
        haystack = f"{file.path} {' '.join(heading['text'] for heading in file.headings)}".lower()
        for term in WORKFLOW_TERMS:
            if term in haystack:
                groups.setdefault(term, []).append(file.path)
    return [
        {
            "workflow_name": term,
            "duplicate_locations": sorted(set(paths)),
            "confidence": 0.67,
            "executable": False,
        }
        for term, paths in sorted(groups.items())
        if len(set(paths)) > 1
    ]


def _document_drift(files: list[AuditFile]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    sections = [section for file in files for section in file.sections][:MAX_SECTIONS_SCANNED]
    buckets: dict[str, list[dict[str, Any]]] = {}
    for section in sections:
        buckets.setdefault(_section_bucket_key(section["title"]), []).append(section)

    drift: list[dict[str, Any]] = []
    comparisons = 0
    comparison_cap_hit = False
    bucket_truncation_hit = False
    for bucket_key in sorted(buckets):
        bucket = sorted(buckets[bucket_key], key=lambda item: (item["title"], item["file"], item["line"]))
        if len(bucket) > MAX_NEAR_SECTION_BUCKET_SIZE:
            bucket = bucket[:MAX_NEAR_SECTION_BUCKET_SIZE]
            bucket_truncation_hit = True
        for index, left in enumerate(bucket):
            if comparison_cap_hit:
                break
            for right in bucket[index + 1 :]:
                if comparisons >= MAX_DRIFT_COMPARISONS:
                    comparison_cap_hit = True
                    break
                comparisons += 1
                if left["file"] == right["file"]:
                    continue
                title_score = _token_similarity(left["title"], right["title"])
                content_score = _token_similarity(left["content"], right["content"])
                if title_score >= 0.86 and 0.35 <= content_score <= 0.78:
                    drift.append(
                        {
                            "drift_group": left["title"],
                            "files_involved": sorted({left["file"], right["file"]}),
                            "confidence": round((title_score + (1 - content_score)) / 2, 3),
                            "executable": False,
                        }
                    )
        if comparison_cap_hit:
            break

    metadata = {
        "drift_comparisons_performed": comparisons,
        "drift_comparison_cap": MAX_DRIFT_COMPARISONS,
        "drift_comparison_cap_hit": comparison_cap_hit,
        "drift_bucket_truncation_hit": bucket_truncation_hit,
        "executable": False,
    }
    return sorted(drift, key=lambda item: (-item["confidence"], item["drift_group"]))[:100], metadata


def _top_candidates(*groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    combined: list[dict[str, Any]] = []
    for group in groups:
        combined.extend(group[:10])
    return combined[:25]


def _safety() -> dict[str, bool]:
    return {
        "files_deleted": False,
        "files_rewritten": False,
        "files_renamed": False,
        "files_moved": False,
        "commit_executed": False,
        "push_executed": False,
        "merge_executed": False,
        "rebase_executed": False,
        "force_push_executed": False,
        "openai_api_invoked": False,
        "recursive_ai_invoked": False,
        "daemon_started": False,
        "watcher_started": False,
        "service_started": False,
        "port_opened": False,
        "server_started": False,
    }


def run_repo_audit(repo_root: Path) -> RepoAuditReport:
    root = repo_root.resolve()
    files = _analyze_files(root)
    duplicate_headings, heading_metadata = _duplicate_headings(files)
    duplicate_sections, section_metadata = _duplicate_sections(files)
    source_conflicts = _source_of_truth_conflicts(files)
    orphan_documents = _dead_documents(files)
    broken_references = _broken_references(root, files)
    workflow_duplicates = _workflow_duplicates(files)
    document_drift, drift_metadata = _document_drift(files)
    cleanup_candidates = _top_candidates(orphan_documents, duplicate_sections, broken_references)
    review_candidates = _top_candidates(source_conflicts, document_drift, workflow_duplicates, duplicate_headings)

    return RepoAuditReport(
        audit_summary={
            "created_at": datetime.now(timezone.utc).isoformat(),
            "mode": "AUDIT_ONLY",
            "scan_roots": [root.as_posix() for root in SCAN_ROOTS],
            "forbidden_paths_ignored": list(FORBIDDEN_PREFIXES),
            "excluded_paths_ignored": list(EXCLUDED_PREFIXES),
            "excluded_directories_ignored": sorted(EXCLUDED_DIR_NAMES),
            "files_scanned": len(files),
            **heading_metadata,
            **section_metadata,
            **drift_metadata,
            "report_type": "operator_relief_repo_audit_engine_v1",
            "executable": False,
        },
        total_files_scanned=len(files),
        duplicate_headings=duplicate_headings,
        duplicate_sections=duplicate_sections,
        source_of_truth_conflicts=source_conflicts,
        orphan_documents=orphan_documents,
        broken_references=broken_references,
        workflow_duplicates=workflow_duplicates,
        document_drift=document_drift,
        top_cleanup_candidates=cleanup_candidates,
        top_human_review_candidates=review_candidates,
        scanned_files=[file.path for file in files],
        safety=_safety(),
        executable=False,
    )


def write_audit_report(report: RepoAuditReport, repo_root: Path, output_dir: Path | None = None) -> Path:
    root = repo_root.resolve()
    target_dir = (root / (output_dir or REPORT_ROOT)).resolve()
    allowed_root = (root / REPORT_ROOT).resolve()
    if not (target_dir == allowed_root or allowed_root in target_dir.parents):
        raise ValueError("Repo audit reports must be written under Reports/operator_relief/audits/.")
    target_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = target_dir / f"repo_audit_{timestamp}.json"
    with output_path.open("x", encoding="utf-8") as handle:
        json.dump(report.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Operator Relief repo audit engine.")
    parser.add_argument("--write-report", action="store_true", help="Write JSON report under Reports/operator_relief/audits/.")
    args = parser.parse_args(argv)
    report = run_repo_audit(Path.cwd())
    if args.write_report:
        output_path = write_audit_report(report, Path.cwd())
        payload = {"report_path": str(output_path), **report.to_dict()}
    else:
        payload = report.to_dict()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
