"""Triage-only ranking layer for Canonical Authority Audit findings."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_ROOT = Path("Reports/operator_relief/audits")
BUCKET_ACTIVE_CONFLICT = "ACTIVE_CANONICAL_CONFLICT"
BUCKET_PROTECTED = "PROTECTED_HUMAN_REVIEW"
BUCKET_ARCHIVE = "LIKELY_VALID_ARCHIVE_OR_EVIDENCE"
BUCKET_TEMPLATE = "LIKELY_TEMPLATE_OR_EXAMPLE"
BUCKET_NOISE = "LIKELY_FALSE_POSITIVE_NOISE"
BUCKET_DUD = "LIKELY_DUD_OR_STALE_CANDIDATE"
BUCKET_CLEANUP_REVIEW = "CLEANUP_REVIEW_CANDIDATE"
BUCKET_CANONICALIZATION = "CANONICALIZATION_REVIEW_CANDIDATE"
REQUIRED_REPORT_FIELDS = (
    "report_type",
    "generated_at",
    "source_canonical_audit_report",
    "executable",
    "groups_reviewed",
    "active_canonical_conflicts",
    "protected_human_review",
    "likely_valid_archive_or_evidence",
    "likely_template_or_example",
    "likely_false_positive_noise",
    "cleanup_review_candidates",
    "canonicalization_review_candidates",
    "top_10_next_review_targets",
    "reasons",
    "confidence",
    "recommended_next_action",
)
GENERIC_HEADINGS = {
    "purpose",
    "boundary",
    "status",
    "summary",
    "validation",
    "blocked actions",
    "next steps",
}
KNOWN_PRIORITY_TERMS = (
    ("apply routing chain", 100),
    ("worker branch and lane rules", 96),
    ("file placement rules", 94),
    ("repo folder ownership map", 92),
    ("portal zone model", 90),
    ("parallel codex workflow", 86),
    ("privacy credential exclusion checklist", 84),
    ("stage 15 secure access front door", 82),
    ("agents", 80),
    ("bootstrap", 78),
    ("ai os overnight supervisor workflow", 76),
    ("safe repair and recovery standard", 74),
    ("validator execution standard", 72),
    ("worker output interface standard", 70),
    ("worker task lifecycle standard", 68),
    ("workflow router registry standard", 66),
)
PROTECTED_PATH_TOKENS = (
    "docs/governance/",
    "docs/security/",
    "docs/ai_os/governance/",
    "docs/ai_os/security/",
    "docs/ai_os/openai_api_bridge/",
    "docs/ai_os/brokers/",
)
PROTECTED_TEXT_TOKENS = ("agents", "protected", "no touch", "credential", "broker", "live order")
VALID_DUPLICATE_TOKENS = (
    "archive",
    "backup",
    "checkpoint",
    "report",
    "evidence",
    "snapshot",
    "history",
    "historical",
    "preview_outputs",
)
TEMPLATE_TOKENS = ("template", "example", "fixture", "sample", "readme_folder_purpose", "placeholder")


@dataclass(frozen=True)
class CanonicalAuthorityTriageReport:
    report_type: str
    generated_at: str
    source_canonical_audit_report: str | None
    executable: bool
    groups_reviewed: int
    active_canonical_conflicts: list[dict[str, Any]]
    protected_human_review: list[dict[str, Any]]
    likely_valid_archive_or_evidence: list[dict[str, Any]]
    likely_template_or_example: list[dict[str, Any]]
    likely_false_positive_noise: list[dict[str, Any]]
    likely_dud_or_stale_candidates: list[dict[str, Any]]
    cleanup_review_candidates: list[dict[str, Any]]
    canonicalization_review_candidates: list[dict[str, Any]]
    top_10_next_review_targets: list[dict[str, Any]]
    reasons: list[str]
    confidence: float
    recommended_next_action: str
    safety: dict[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _group_text(group: dict[str, Any]) -> str:
    values = [
        str(group.get("group_key", "")),
        str(group.get("category", "")),
        str(group.get("reason", "")),
        " ".join(str(item) for item in group.get("classifications", [])),
        " ".join(str(item) for item in group.get("paths", [])),
    ]
    return "\n".join(values).lower()


def find_latest_canonical_audit_report(repo_root: Path) -> Path | None:
    report_root = repo_root.resolve() / REPORT_ROOT
    if not report_root.exists():
        return None
    candidates = sorted(
        report_root.glob("canonical_authority_audit_*.json"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _is_timestamped(text: str) -> bool:
    return bool(re.search(r"\d{4}[-_]\d{2}[-_]\d{2}|\d{8}T\d{6}Z|20\d{6,}", text.lower()))


def _is_protected(group: dict[str, Any]) -> bool:
    text = _group_text(group)
    return any(token in text for token in PROTECTED_PATH_TOKENS) or any(
        token in text for token in PROTECTED_TEXT_TOKENS
    )


def _is_template(group: dict[str, Any]) -> bool:
    text = _group_text(group)
    paths = [str(path).lower() for path in group.get("paths", [])]
    return any(token in text for token in TEMPLATE_TOKENS) or (
        len(paths) > 8 and all("readme_folder_purpose" in path for path in paths)
    )


def _is_archive_or_evidence(group: dict[str, Any]) -> bool:
    text = _group_text(group)
    return any(token in text for token in VALID_DUPLICATE_TOKENS) or _is_timestamped(text)


def _is_noise(group: dict[str, Any]) -> bool:
    paths = [str(path).lower() for path in group.get("paths", [])]
    key = _slug(str(group.get("group_key", "")))
    if key in GENERIC_HEADINGS:
        return True
    if len(paths) > 12:
        return True
    return bool(paths) and all("readme_folder_purpose" in path for path in paths)


def _has_active_workflow_pair(group: dict[str, Any]) -> bool:
    paths = [str(path) for path in group.get("paths", [])]
    return any(path.startswith("docs/workflows/") for path in paths) and any(
        path.startswith("docs/AI_OS/operator_workflows/") or path.startswith("docs/AI_OS/operator/")
        for path in paths
    )


def _has_concrete_same_name_pair(group: dict[str, Any]) -> bool:
    stems: dict[str, int] = {}
    for path in group.get("paths", []):
        stem = _slug(Path(str(path)).stem)
        stem = re.sub(r"^aios ", "", stem)
        stems[stem] = stems.get(stem, 0) + 1
    return any(count > 1 for count in stems.values())


def _known_priority(group: dict[str, Any]) -> int:
    text = _slug(_group_text(group))
    priority = 0
    for term, score in KNOWN_PRIORITY_TERMS:
        if term in text:
            priority = max(priority, score)
    return priority


def _bucket_for_group(group: dict[str, Any]) -> str:
    if _is_protected(group):
        return BUCKET_PROTECTED
    if _known_priority(group) and (_has_active_workflow_pair(group) or "workflow" in str(group.get("reason", "")).lower()):
        return BUCKET_CANONICALIZATION
    if _is_template(group):
        return BUCKET_TEMPLATE
    if _is_archive_or_evidence(group):
        return BUCKET_ARCHIVE
    if _is_noise(group):
        return BUCKET_NOISE
    if _has_active_workflow_pair(group) or "competing workflow authority" in str(group.get("reason", "")):
        return BUCKET_CANONICALIZATION
    if _has_concrete_same_name_pair(group):
        return BUCKET_ACTIVE_CONFLICT
    if "STALE_OR_DUD_CANDIDATE" in group.get("classifications", []):
        return BUCKET_DUD
    return BUCKET_CLEANUP_REVIEW


def _bucket_reason(group: dict[str, Any], bucket: str) -> str:
    if bucket == BUCKET_PROTECTED:
        return "Protected, governance, security, AGENTS, approval, credential, broker, or live-order signal requires human review."
    if bucket == BUCKET_TEMPLATE:
        return "Template, example, fixture, sample, placeholder, or folder-purpose scaffold signal."
    if bucket == BUCKET_ARCHIVE:
        return "Timestamped report, checkpoint, backup, archive, evidence, snapshot, preview, or historical signal."
    if bucket == BUCKET_NOISE:
        return "Generic heading or large weak-signal group; not enough concrete authority overlap for cleanup review."
    if bucket == BUCKET_CANONICALIZATION:
        return "Concrete cross-location active workflow duplicate should be reviewed for canonicalization."
    if bucket == BUCKET_ACTIVE_CONFLICT:
        return "Concrete same-title active documents appear in more than one location."
    if bucket == BUCKET_DUD:
        return "Weak authority signal with stale/dud classification from source audit."
    return "Potential cleanup review candidate after human confirms canonical owner."


def _recommended_action(bucket: str) -> str:
    if bucket == BUCKET_PROTECTED:
        return "protected human review; do not mark safe cleanup"
    if bucket == BUCKET_CANONICALIZATION:
        return "review canonicalization target and deprecate candidate, without source mutation"
    if bucket == BUCKET_ACTIVE_CONFLICT:
        return "review active canonical conflict and choose source of truth"
    if bucket in {BUCKET_ARCHIVE, BUCKET_TEMPLATE, BUCKET_NOISE}:
        return "leave as likely valid duplicate or false positive unless human review says otherwise"
    return "review as cleanup candidate; never perform cleanup directly"


def _priority_score(group: dict[str, Any], bucket: str) -> float:
    score = float(group.get("confidence", 0.0)) * 10
    score += _known_priority(group)
    if _has_concrete_same_name_pair(group):
        score += 30
    if _has_active_workflow_pair(group):
        score += 28
    if bucket == BUCKET_PROTECTED:
        score += 20
    if "governance" in str(group.get("reason", "")).lower() or "security" in str(group.get("reason", "")).lower():
        score += 18
    if _is_archive_or_evidence(group):
        score -= 30
    if _is_template(group):
        score -= 35
    if _is_noise(group):
        score -= 40
    return round(score, 3)


def _triage_entry(group: dict[str, Any]) -> dict[str, Any]:
    bucket = _bucket_for_group(group)
    return {
        "group_key": group.get("group_key"),
        "category": group.get("category"),
        "paths": group.get("paths", []),
        "bucket": bucket,
        "confidence": group.get("confidence", 0.0),
        "priority_score": _priority_score(group, bucket),
        "reason": _bucket_reason(group, bucket),
        "source_reason": group.get("reason"),
        "recommended_next_action": _recommended_action(bucket),
        "protected_review_required": bucket == BUCKET_PROTECTED,
        "executable": False,
    }


def _candidate_to_entry(candidate: dict[str, Any], bucket: str) -> dict[str, Any]:
    return {
        "group_key": candidate.get("path"),
        "category": "candidate",
        "paths": [candidate.get("path")],
        "bucket": bucket,
        "confidence": candidate.get("confidence", 0.0),
        "priority_score": 0.0,
        "reason": "; ".join(candidate.get("reasons", [])) or "candidate inherited from canonical audit",
        "recommended_next_action": _recommended_action(bucket),
        "protected_review_required": bucket == BUCKET_PROTECTED,
        "executable": False,
    }


def _rank_top_targets(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    eligible = [
        entry
        for entry in entries
        if entry["bucket"] in {BUCKET_ACTIVE_CONFLICT, BUCKET_CANONICALIZATION, BUCKET_PROTECTED}
    ]
    ranked = sorted(
        eligible,
        key=lambda item: (-item["priority_score"], -float(item.get("confidence", 0.0)), str(item.get("group_key", ""))),
    )
    top = []
    for rank, entry in enumerate(ranked[:10], start=1):
        top.append(
            {
                "rank": rank,
                "group_key": entry["group_key"],
                "category": entry["category"],
                "paths": entry["paths"],
                "bucket": entry["bucket"],
                "confidence": entry["confidence"],
                "reason": entry["reason"],
                "recommended_next_action": entry["recommended_next_action"],
                "protected_review_required": entry["protected_review_required"],
                "executable": False,
            }
        )
    return top


def _safety() -> dict[str, bool]:
    return {
        "source_docs_edited": False,
        "audit_reports_edited": False,
        "triage_report_written": False,
        "cleanup_performed": False,
        "files_removed": False,
        "files_moved": False,
        "files_renamed": False,
        "commit_executed": False,
        "push_executed": False,
        "merge_executed": False,
        "rebase_executed": False,
        "force_push_executed": False,
        "openai_api_invoked": False,
        "codex_recursion_invoked": False,
        "daemon_started": False,
        "watcher_started": False,
        "service_started": False,
        "server_started": False,
        "port_opened": False,
        "executable": False,
    }


def run_canonical_authority_triage(repo_root: Path) -> CanonicalAuthorityTriageReport:
    root = repo_root.resolve()
    source_path = find_latest_canonical_audit_report(root)
    source_report = _load_json(source_path)
    groups = source_report.get("duplicate_authority_groups", [])
    entries = [_triage_entry(group) for group in groups if isinstance(group, dict)]

    protected_candidate_entries = [
        _candidate_to_entry(candidate, BUCKET_PROTECTED)
        for candidate in source_report.get("protected_review_required", [])
        if isinstance(candidate, dict)
    ]
    dud_candidate_entries = [
        _candidate_to_entry(candidate, BUCKET_DUD)
        for candidate in source_report.get("likely_duds", [])
        if isinstance(candidate, dict)
    ]

    all_entries = [*entries, *protected_candidate_entries, *dud_candidate_entries]
    by_bucket: dict[str, list[dict[str, Any]]] = {
        BUCKET_ACTIVE_CONFLICT: [],
        BUCKET_PROTECTED: [],
        BUCKET_ARCHIVE: [],
        BUCKET_TEMPLATE: [],
        BUCKET_NOISE: [],
        BUCKET_DUD: [],
        BUCKET_CLEANUP_REVIEW: [],
        BUCKET_CANONICALIZATION: [],
    }
    for entry in all_entries:
        by_bucket.setdefault(entry["bucket"], []).append(entry)

    for bucket, bucket_entries in by_bucket.items():
        by_bucket[bucket] = sorted(
            bucket_entries,
            key=lambda item: (-item["priority_score"], -float(item.get("confidence", 0.0)), str(item.get("group_key", ""))),
        )

    reasons = [
        "Triage-only ranking over Canonical Authority Audit duplicate groups.",
        "Cleanup language is review-only; no source files are changed.",
        "Protected, governance, security, AGENTS, credential, broker, and live-order signals are never marked safe cleanup.",
        "Timestamped reports, backups, archives, evidence, examples, fixtures, templates, and folder-purpose scaffolds are treated as usually valid duplicates.",
    ]
    if source_path:
        reasons.append(f"Loaded canonical authority audit report: {_normalize_path(source_path.relative_to(root))}")
    else:
        reasons.append("No canonical authority audit report found; triage produced empty buckets.")

    return CanonicalAuthorityTriageReport(
        report_type="operator_relief_canonical_authority_triage_v1",
        generated_at=datetime.now(timezone.utc).isoformat(),
        source_canonical_audit_report=_normalize_path(source_path.relative_to(root)) if source_path else None,
        executable=False,
        groups_reviewed=len(groups) if isinstance(groups, list) else 0,
        active_canonical_conflicts=by_bucket[BUCKET_ACTIVE_CONFLICT],
        protected_human_review=by_bucket[BUCKET_PROTECTED],
        likely_valid_archive_or_evidence=by_bucket[BUCKET_ARCHIVE],
        likely_template_or_example=by_bucket[BUCKET_TEMPLATE],
        likely_false_positive_noise=by_bucket[BUCKET_NOISE],
        likely_dud_or_stale_candidates=by_bucket[BUCKET_DUD],
        cleanup_review_candidates=by_bucket[BUCKET_CLEANUP_REVIEW],
        canonicalization_review_candidates=by_bucket[BUCKET_CANONICALIZATION],
        top_10_next_review_targets=_rank_top_targets(entries),
        reasons=reasons,
        confidence=0.84 if source_path else 0.4,
        recommended_next_action="Review top_10_next_review_targets manually; choose canonicalization candidates before any later cleanup packet.",
        safety=_safety(),
    )


def write_canonical_authority_triage_report(report: CanonicalAuthorityTriageReport, repo_root: Path) -> Path:
    root = repo_root.resolve()
    target_dir = (root / REPORT_ROOT).resolve()
    allowed_root = (root / REPORT_ROOT).resolve()
    if not (target_dir == allowed_root or allowed_root in target_dir.parents):
        raise ValueError("Canonical authority triage reports must be written under Reports/operator_relief/audits/.")
    target_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = target_dir / f"canonical_authority_triage_{timestamp}.json"
    with output_path.open("x", encoding="utf-8") as handle:
        payload = report.to_dict()
        payload["safety"]["triage_report_written"] = True
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Operator Relief canonical authority triage.")
    parser.add_argument("--write-report", action="store_true", help="Write JSON report under Reports/operator_relief/audits/.")
    args = parser.parse_args(argv)
    report = run_canonical_authority_triage(Path.cwd())
    payload = report.to_dict()
    if args.write_report:
        output_path = write_canonical_authority_triage_report(report, Path.cwd())
        payload = {"report_path": str(output_path), **payload}
        payload["safety"]["triage_report_written"] = True
    missing_fields = [field for field in REQUIRED_REPORT_FIELDS if field not in payload]
    if missing_fields:
        raise RuntimeError(f"Canonical authority triage report missing required fields: {missing_fields}")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
