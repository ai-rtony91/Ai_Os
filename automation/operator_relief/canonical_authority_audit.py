"""Audit-only canonical authority classifier for Operator Relief v1."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_ROOT = Path("Reports/operator_relief/audits")
SCAN_ROOTS = (Path("docs"), Path("automation/operator_relief"), Path("Reports"), Path("control"))
SUPPORTED_SUFFIXES = {".md", ".markdown", ".json", ".yaml", ".yml", ".txt"}
EXCLUDED_DIR_NAMES = {".git", "__pycache__", "node_modules", "venv", ".venv", "build", "dist"}
EXCLUDED_PREFIXES = ("Reports/operator_relief/audits/",)
REQUIRED_DETECTION_TERMS = (
    "canonical",
    "source of truth",
    "authority",
    "official",
    "master",
    "primary",
    "required",
    "bootstrap",
    "execution authority",
    "single source",
    "control",
    "policy",
    "standard",
    "boundary",
    "blocked actions",
    "approval boundary",
    "approval requirements",
    "worker lanes",
    "branch rules",
    "workflow router",
    "apply routing",
    "no touch",
    "protected file",
    "protected root",
)
PROTECTED_REVIEW_TERMS = (
    "agents",
    "approval",
    "no touch",
    "protected",
    "blocked actions",
    "approval boundary",
    "approval requirements",
)
GENERIC_WEAK_HEADINGS = {"purpose", "boundary", "blocked"}
REQUIRED_REPORT_FIELDS = (
    "report_type",
    "generated_at",
    "executable",
    "source_audit_report",
    "files_scanned",
    "canonical_candidates",
    "duplicate_authority_groups",
    "likely_valid_duplicates",
    "likely_duds",
    "protected_review_required",
    "top_cleanup_candidates",
    "top_human_review_candidates",
    "reasons",
    "confidence",
    "recommended_next_action",
)


@dataclass(frozen=True)
class ScannedDocument:
    path: str
    text: str
    headings: list[str]
    matched_terms: list[str]
    executable: bool = False


@dataclass(frozen=True)
class CanonicalAuthorityAuditReport:
    report_type: str
    generated_at: str
    executable: bool
    source_audit_report: str | None
    files_scanned: int
    canonical_candidates: list[dict[str, Any]]
    duplicate_authority_groups: list[dict[str, Any]]
    likely_valid_duplicates: list[dict[str, Any]]
    likely_duds: list[dict[str, Any]]
    protected_review_required: list[dict[str, Any]]
    top_cleanup_candidates: list[dict[str, Any]]
    top_human_review_candidates: list[dict[str, Any]]
    reasons: list[str]
    confidence: float
    recommended_next_action: str
    audit_signal_counts: dict[str, int]
    safety: dict[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _is_supported(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_SUFFIXES


def _is_excluded(relative_path: str) -> bool:
    normalized = _normalize_path(relative_path)
    parts = set(Path(normalized).parts)
    return any(part in EXCLUDED_DIR_NAMES for part in parts) or any(
        normalized == prefix.rstrip("/") or normalized.startswith(prefix)
        for prefix in EXCLUDED_PREFIXES
    )


def _extract_headings(text: str) -> list[str]:
    headings: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            headings.append(match.group(2).strip())
    return headings


def _matched_terms(path: str, text: str, headings: list[str]) -> list[str]:
    haystack = f"{path}\n{text}\n{' '.join(headings)}".lower()
    return [term for term in REQUIRED_DETECTION_TERMS if term in haystack]


def _collect_documents(repo_root: Path) -> list[ScannedDocument]:
    root = repo_root.resolve()
    documents: list[ScannedDocument] = []
    for scan_root in SCAN_ROOTS:
        candidate_root = root / scan_root
        if not candidate_root.exists():
            continue
        for path in candidate_root.rglob("*"):
            if not path.is_file() or not _is_supported(path):
                continue
            relative = _normalize_path(path.relative_to(root))
            if _is_excluded(relative):
                continue
            text = _read_text(path)
            headings = _extract_headings(text)
            terms = _matched_terms(relative, text, headings)
            documents.append(
                ScannedDocument(
                    path=relative,
                    text=text,
                    headings=headings,
                    matched_terms=terms,
                    executable=False,
                )
            )
    return sorted(documents, key=lambda item: item.path)


def find_latest_repo_audit_report(repo_root: Path) -> Path | None:
    report_root = repo_root.resolve() / REPORT_ROOT
    if not report_root.exists():
        return None
    candidates = sorted(report_root.glob("repo_audit_*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def _load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _basename_key(path: str) -> str:
    stem = Path(path).stem.lower()
    stem = re.sub(r"^aios[_-]?", "", stem)
    stem = re.sub(r"[_-]dry[_-]?run$", "", stem)
    stem = re.sub(r"[_-]draft$", "", stem)
    stem = re.sub(r"[_-]v\d+$", "", stem)
    stem = re.sub(r"[_-]backup.*$", "", stem)
    stem = re.sub(r"[_-]\d{4}[-_]\d{2}[-_]\d{2}.*$", "", stem)
    stem = re.sub(r"[_-]created[_-]\d{4}.*$", "", stem)
    return re.sub(r"[^a-z0-9]+", " ", stem).strip()


def _is_timestamped(path: str) -> bool:
    return bool(re.search(r"\d{4}[-_]\d{2}[-_]\d{2}|\d{8}T\d{6}Z|created[_-]\d{4}", path.lower()))


def _is_report_like(path: str) -> bool:
    lower = path.lower()
    return any(token in lower for token in ("report", "audit", "checkpoint", "summary", "evidence", "snapshot"))


def _is_template_or_example(path: str, text: str) -> bool:
    lower = f"{path}\n{text[:1000]}".lower()
    return any(token in lower for token in ("template", "example", "sample", "fixture", "placeholder"))


def _is_backup(path: str) -> bool:
    lower = path.lower()
    return "backup" in lower or "archive" in lower or "old_do_not_use" in lower


def _protected_review_needed(path: str, text: str) -> bool:
    lower = f"{path}\n{text[:2000]}".lower()
    return (
        path.startswith("docs/governance/")
        or path.startswith("docs/security/")
        or "agents.md" in path.lower()
        or any(term in lower for term in PROTECTED_REVIEW_TERMS)
    )


def _classification(path: str, text: str, group_paths: list[str] | None = None) -> str:
    lower = path.lower()
    paths = group_paths or [path]
    if _protected_review_needed(path, text):
        return "DO_NOT_TOUCH_WITHOUT_HUMAN_REVIEW"
    if _is_backup(path):
        return "ARCHIVE_OR_EVIDENCE_LIKELY"
    if _is_template_or_example(path, text):
        return "TEMPLATE_OR_EXAMPLE_LIKELY"
    if _is_timestamped(path) and _is_report_like(path):
        return "HISTORICAL_REPORT_LIKELY"
    if "draft" in lower:
        return "DRAFT_REVIEW_REQUIRED"
    if group_paths and len(set(paths)) > 1:
        return "DUPLICATE_CANONICAL_CANDIDATE"
    if any(token in lower for token in ("workflow", "standard", "rules", "policy", "authority", "canonical")):
        return "ACTIVE_CANONICAL_CANDIDATE"
    return "STALE_OR_DUD_CANDIDATE"


def _reason_for_group(paths: list[str]) -> str:
    joined = "\n".join(paths)
    if any(path.startswith("docs/workflows/") for path in paths) and any(
        path.startswith("docs/AI_OS/operator_workflows/") or path.startswith("docs/AI_OS/operator/")
        for path in paths
    ):
        return "competing workflow authority"
    if "phase_15_secure_access" in joined and "secure_access" in joined:
        return "competing security-access authority"
    if any(path.startswith("docs/AI_OS/governance/") for path in paths) and any("DRY_RUN" in path for path in paths):
        return "competing governance authority"
    if any("AGENTS.md" in path for path in paths) and any("BACKUP" in path.upper() or "backup" in path for path in paths):
        return "AGENTS backup or historical authority copy"
    if any("WORKER_BRANCH_AND_LANE_RULES" in path for path in paths):
        return "competing worker lane rules authority"
    if any("APPLY_ROUTING_CHAIN" in path for path in paths):
        return "competing apply routing authority"
    return "same normalized topic appears in multiple authority-like files"


def _group_priority(paths: list[str]) -> int:
    joined = "\n".join(paths)
    priority_terms = (
        "APPLY_ROUTING_CHAIN",
        "WORKER_BRANCH_AND_LANE_RULES",
        "AIOS_PORTAL_ZONE_MODEL",
        "AIOS_stage2_classification_summary",
        "SYSTEM_LEVEL_AI_WIZARDS",
        "AGENTS.md",
        "AIOS_FILE_PLACEMENT_RULES",
        "AIOS_REPO_FOLDER_OWNERSHIP_MAP",
    )
    return sum(1 for term in priority_terms if term in joined)


def _candidate_entry(document: ScannedDocument, classification: str | None = None) -> dict[str, Any]:
    result_classification = classification or _classification(document.path, document.text)
    return {
        "path": document.path,
        "classification": result_classification,
        "matched_terms": document.matched_terms,
        "reasons": _candidate_reasons(document, result_classification),
        "confidence": _confidence_for(document, result_classification),
        "recommended_next_action": _recommended_action(result_classification),
        "executable": False,
    }


def _candidate_reasons(document: ScannedDocument, classification: str) -> list[str]:
    reasons = []
    if document.matched_terms:
        reasons.append(f"matched authority terms: {', '.join(document.matched_terms[:6])}")
    if _protected_review_needed(document.path, document.text):
        reasons.append("protected/governance/security/approval language requires human review")
    if _is_timestamped(document.path) and _is_report_like(document.path):
        reasons.append("timestamped report/checkpoint/evidence pattern")
    if _is_template_or_example(document.path, document.text):
        reasons.append("template/example/sample/fixture pattern")
    if _is_backup(document.path):
        reasons.append("backup/archive pattern")
    if classification == "STALE_OR_DUD_CANDIDATE":
        reasons.append("weak authority signal and no clear active canonical path pattern")
    return reasons or ["authority-like filename or content signal"]


def _confidence_for(document: ScannedDocument, classification: str) -> float:
    score = 0.45 + min(len(document.matched_terms), 6) * 0.07
    if classification == "DO_NOT_TOUCH_WITHOUT_HUMAN_REVIEW":
        score += 0.12
    if classification in {"HISTORICAL_REPORT_LIKELY", "TEMPLATE_OR_EXAMPLE_LIKELY", "ARCHIVE_OR_EVIDENCE_LIKELY"}:
        score += 0.1
    return round(min(score, 0.95), 3)


def _recommended_action(classification: str) -> str:
    if classification == "ACTIVE_CANONICAL_CANDIDATE":
        return "review as canonicalize candidate"
    if classification == "DUPLICATE_CANONICAL_CANDIDATE":
        return "review competing authority before canonicalize candidate"
    if classification in {"ARCHIVE_OR_EVIDENCE_LIKELY", "HISTORICAL_REPORT_LIKELY", "TEMPLATE_OR_EXAMPLE_LIKELY"}:
        return "review as likely valid duplicate"
    if classification == "DO_NOT_TOUCH_WITHOUT_HUMAN_REVIEW":
        return "human review required before any deprecate candidate decision"
    if classification == "DRAFT_REVIEW_REQUIRED":
        return "review draft status before archive candidate decision"
    return "review as deprecate candidate"


def _build_groups(documents: list[ScannedDocument], source_report: dict[str, Any]) -> list[dict[str, Any]]:
    by_path = {document.path: document for document in documents}
    grouped: dict[str, set[str]] = {}
    for document in documents:
        key = _basename_key(document.path)
        if key and (document.matched_terms or key in {"apply routing chain", "worker branch and lane rules"}):
            grouped.setdefault(key, set()).add(document.path)

    for signal_name in ("duplicate_sections", "document_drift", "workflow_duplicates", "source_of_truth_conflicts"):
        for item in source_report.get(signal_name, []):
            paths = item.get("source_files") or item.get("files_involved") or item.get("duplicate_locations") or item.get(
                "conflicting_files"
            )
            if not isinstance(paths, list):
                continue
            normalized_paths = [_normalize_path(path) for path in paths if isinstance(path, str)]
            if signal_name == "workflow_duplicates" and len(normalized_paths) > 12:
                continue
            if len(normalized_paths) > 25:
                continue
            for path in normalized_paths:
                if path in by_path:
                    grouped.setdefault(_basename_key(path) or signal_name, set()).update(normalized_paths)
                    break

    groups: list[dict[str, Any]] = []
    for key, paths_set in grouped.items():
        paths = sorted(path for path in paths_set if path in by_path)
        if len(paths) < 2:
            continue
        reason = _reason_for_group(paths)
        classifications = sorted({_classification(path, by_path[path].text, paths) for path in paths})
        protected = any(classification == "DO_NOT_TOUCH_WITHOUT_HUMAN_REVIEW" for classification in classifications)
        if "competing" in reason and not protected:
            classifications.append("DUPLICATE_CANONICAL_CANDIDATE")
        groups.append(
            {
                "group_key": key,
                "paths": paths,
                "classifications": sorted(set(classifications)),
                "reason": reason,
                "protected_review_required": protected or "security-access" in reason or "governance authority" in reason,
                "confidence": round(min(0.68 + 0.06 * len(paths) + 0.08 * _group_priority(paths), 0.96), 3),
                "recommended_next_action": "review competing authority; choose canonicalize candidate before any deprecate candidate",
                "executable": False,
            }
        )
    return sorted(groups, key=lambda item: (-_group_priority(item["paths"]), -item["confidence"], item["group_key"]))[:100]


def _likely_valid(group: dict[str, Any]) -> bool:
    return any(
        classification in group["classifications"]
        for classification in ("ARCHIVE_OR_EVIDENCE_LIKELY", "TEMPLATE_OR_EXAMPLE_LIKELY", "HISTORICAL_REPORT_LIKELY")
    )


def _group_category(group: dict[str, Any]) -> str:
    reason = group["reason"]
    if "workflow" in reason or "routing" in reason:
        return "duplicate_workflow_docs"
    if "worker lane" in reason:
        return "duplicate_boundary_documents"
    if "security-access" in reason:
        return "duplicate_boundary_documents"
    if "approval" in "\n".join(group["paths"]).lower():
        return "duplicate_approval_chain_docs"
    if "blocked" in "\n".join(group["paths"]).lower():
        return "duplicate_blocked_action_docs"
    if "governance" in reason or "authority" in reason:
        return "duplicate_authority_chains"
    return "competing_source_of_truth_candidates"


def _cleanup_candidates(groups: list[dict[str, Any]], candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleanup: list[dict[str, Any]] = []
    for group in groups:
        if group["protected_review_required"] or _likely_valid(group):
            continue
        cleanup.append(
            {
                "paths": group["paths"],
                "reason": group["reason"],
                "confidence": group["confidence"],
                "recommended_next_action": "review as deprecate candidate or canonicalize candidate",
                "executable": False,
            }
        )
    for candidate in candidates:
        if candidate["classification"] != "STALE_OR_DUD_CANDIDATE":
            continue
        heading_slugs = {_slug(heading) for heading in _extract_headings(candidate.get("preview_text", ""))}
        if heading_slugs and heading_slugs <= GENERIC_WEAK_HEADINGS:
            continue
        cleanup.append(
            {
                "paths": [candidate["path"]],
                "reason": "weak authority signal and stale/dud pattern",
                "confidence": candidate["confidence"],
                "recommended_next_action": "review as deprecate candidate",
                "executable": False,
            }
        )
    return cleanup[:25]


def _audit_signal_counts(source_report: dict[str, Any]) -> dict[str, int]:
    keys = (
        "duplicate_headings",
        "duplicate_sections",
        "document_drift",
        "orphan_documents",
        "broken_references",
        "workflow_duplicates",
        "source_of_truth_conflicts",
    )
    counts = {}
    for key in keys:
        value = source_report.get(key, [])
        counts[key] = len(value) if isinstance(value, list) else 0
    metadata = source_report.get("audit_summary", {})
    if isinstance(metadata, dict):
        for key in ("files_scanned", "headings_scanned", "sections_scanned"):
            if isinstance(metadata.get(key), int):
                counts[f"metadata_{key}"] = metadata[key]
    return counts


def _safety() -> dict[str, bool]:
    return {
        "source_files_mutated": False,
        "cleanup_performed": False,
        "files_removed": False,
        "files_moved": False,
        "files_renamed": False,
        "commit_executed": False,
        "push_executed": False,
        "merge_executed": False,
        "openai_api_invoked": False,
        "codex_recursion_invoked": False,
        "daemon_started": False,
        "watcher_started": False,
        "service_started": False,
        "server_started": False,
        "port_opened": False,
        "executable": False,
    }


def run_canonical_authority_audit(repo_root: Path) -> CanonicalAuthorityAuditReport:
    root = repo_root.resolve()
    source_path = find_latest_repo_audit_report(root)
    source_report = _load_json(source_path)
    documents = _collect_documents(root)
    authority_documents = [document for document in documents if document.matched_terms]
    groups = _build_groups(documents, source_report)
    candidates = [_candidate_entry(document) for document in authority_documents]

    grouped_paths = {path for group in groups for path in group["paths"]}
    for path in sorted(grouped_paths):
        document = next((item for item in documents if item.path == path), None)
        if document is None:
            continue
        candidates.append(_candidate_entry(document, _classification(path, document.text, sorted(grouped_paths))))

    unique_candidates = {candidate["path"]: candidate for candidate in candidates}
    canonical_candidates = sorted(
        unique_candidates.values(),
        key=lambda item: (item["classification"] != "DO_NOT_TOUCH_WITHOUT_HUMAN_REVIEW", -item["confidence"], item["path"]),
    )[:200]
    protected = [candidate for candidate in canonical_candidates if candidate["classification"] == "DO_NOT_TOUCH_WITHOUT_HUMAN_REVIEW"]
    likely_valid = [group for group in groups if _likely_valid(group)]
    likely_duds = [candidate for candidate in canonical_candidates if candidate["classification"] == "STALE_OR_DUD_CANDIDATE"][:50]
    cleanup_candidates = _cleanup_candidates(groups, canonical_candidates)
    human_review = sorted(
        [*protected, *groups],
        key=lambda item: (-item.get("confidence", 0), item.get("path", item.get("group_key", ""))),
    )[:50]
    categorized_groups = [{**group, "category": _group_category(group)} for group in groups]

    reasons = [
        "Audit-only classification built from repo file scan and latest Repo Audit Engine JSON when available.",
        "Duplicate findings are review prompts, not cleanup approval.",
        "Governance, security, AGENTS, approval, no-touch, and protected-language files require human review.",
    ]
    if source_path:
        reasons.append(f"Loaded Repo Audit Engine report: {_normalize_path(source_path.relative_to(root))}")
    else:
        reasons.append("No Repo Audit Engine report found; used source scan only.")

    return CanonicalAuthorityAuditReport(
        report_type="operator_relief_canonical_authority_audit_v1",
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        source_audit_report=_normalize_path(source_path.relative_to(root)) if source_path else None,
        files_scanned=len(documents),
        canonical_candidates=canonical_candidates,
        duplicate_authority_groups=categorized_groups,
        likely_valid_duplicates=likely_valid[:50],
        likely_duds=likely_duds,
        protected_review_required=protected[:75],
        top_cleanup_candidates=cleanup_candidates,
        top_human_review_candidates=human_review,
        reasons=reasons,
        confidence=0.82 if source_path else 0.7,
        recommended_next_action="Human review should choose canonicalize candidates and archive/deprecate candidates; do not perform cleanup directly.",
        audit_signal_counts=_audit_signal_counts(source_report),
        safety=_safety(),
    )


def write_canonical_authority_audit_report(report: CanonicalAuthorityAuditReport, repo_root: Path) -> Path:
    root = repo_root.resolve()
    target_dir = (root / REPORT_ROOT).resolve()
    allowed_root = (root / REPORT_ROOT).resolve()
    if not (target_dir == allowed_root or allowed_root in target_dir.parents):
        raise ValueError("Canonical authority audit reports must be written under Reports/operator_relief/audits/.")
    target_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = target_dir / f"canonical_authority_audit_{timestamp}.json"
    with output_path.open("x", encoding="utf-8") as handle:
        json.dump(report.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Operator Relief canonical authority audit.")
    parser.add_argument("--write-report", action="store_true", help="Write JSON report under Reports/operator_relief/audits/.")
    args = parser.parse_args(argv)
    report = run_canonical_authority_audit(Path.cwd())
    payload = report.to_dict()
    if args.write_report:
        output_path = write_canonical_authority_audit_report(report, Path.cwd())
        payload = {"report_path": str(output_path), **payload}
    missing_fields = [field for field in REQUIRED_REPORT_FIELDS if field not in payload]
    if missing_fields:
        raise RuntimeError(f"Canonical authority audit report missing required fields: {missing_fields}")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
