"""Authority-aware dual-review bridge evidence for Operator Relief."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.operator_relief.adb_escalation import plan_adb_escalation
from automation.operator_relief.pi_yubikey_approval_station import (
    DECISION_HOLD_FOR_REVIEW,
    MODE_DRY_RUN,
    build_yubikey_approval_report,
)
from automation.operator_relief.protected_authority_registry import build_registry


REPORT_TYPE = "operator_relief_authority_aware_dual_review_bridge_v1"
OUTPUT_ROOT = Path("Reports/operator_relief/bridge_reviews")

CLASS_SAFE_WORKFLOW = "SAFE_WORKFLOW"
CLASS_PARKED_CONFLICT = "PARKED_CONFLICT"
CLASS_PROTECTED_AUTHORITY = "PROTECTED_AUTHORITY"
CLASS_NON_CANONICAL_DEPENDENCY = "NON_CANONICAL_DEPENDENCY"
CLASS_AUTHORITY_REVIEW_REQUIRED = "AUTHORITY_REVIEW_REQUIRED"

PROTECTED_AUTHORITY_PATHS = {
    "AGENTS.md",
}
PROTECTED_PREFIXES = (
    "docs/governance/",
    "docs/security/",
    "docs/AI_OS/governance/",
    "docs/AI_OS/security/",
)


@dataclass(frozen=True)
class AuthorityBridgeReview:
    report_type: str
    generated_at: str
    executable: bool
    bridge_goal: str
    codex_report_summary: str
    chatgpt_review_summary: str
    claude_review_summary: str
    reconciled_instruction: str
    authority_classification: str
    protected_paths_detected: list[str]
    parked_conflicts_detected: list[str]
    non_canonical_dependencies_detected: list[str]
    yubikey_approval_required: bool
    adb_escalation_required: bool
    continue_allowed: bool
    blocked_reasons: list[str]
    yubikey_approval_evidence: dict[str, Any] | None
    adb_escalation_plan: dict[str, Any] | None
    safety: dict[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def _safe_timestamp(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _summary(value: str, limit: int = 1200) -> str:
    text = re.sub(r"\s+", " ", value or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _safety() -> dict[str, bool]:
    return {
        "commit_authorized": False,
        "push_authorized": False,
        "merge_authorized": False,
        "cleanup_authorized": False,
        "canonicalization_authorized": False,
        "protected_mutation_authorized": False,
        "source_files_mutated": False,
        "external_reviewer_called": False,
        "worker_launched": False,
        "executable": False,
    }


def _text_pool(*items: str) -> str:
    return "\n".join(item for item in items if item)


def _mentioned_paths(corpus: str, paths: list[str]) -> list[str]:
    lower_corpus = corpus.lower()
    hits: list[str] = []
    for path in paths:
        normalized = _normalize_path(path)
        if normalized.lower() in lower_corpus:
            hits.append(normalized)
    return sorted(set(hits))


def _protected_paths_from_registry(registry: dict[str, Any]) -> list[str]:
    paths = list(PROTECTED_AUTHORITY_PATHS)
    paths.extend(str(path) for path in registry.get("do_not_touch_paths", []) if isinstance(path, str))
    for item in registry.get("protected_authorities", []):
        if isinstance(item, dict):
            paths.extend(str(path) for path in item.get("paths", []) if isinstance(path, str))
    return sorted(set(_normalize_path(path) for path in paths))


def _parked_conflicts_from_registry(registry: dict[str, Any], corpus: str) -> list[str]:
    hits: list[str] = []
    for item in registry.get("parked_workflow_authority_conflicts", []):
        if not isinstance(item, dict):
            continue
        group_key = str(item.get("group_key", ""))
        paths = [
            str(path)
            for path in (item.get("likely_canonical_candidate"), item.get("duplicate_candidate"))
            if isinstance(path, str)
        ]
        if group_key and group_key.lower() in corpus.lower():
            hits.append(group_key)
            continue
        if _mentioned_paths(corpus, paths):
            hits.append(group_key)
    return sorted(set(hit for hit in hits if hit))


def _non_canonical_dependencies_from_registry(registry: dict[str, Any], corpus: str) -> list[str]:
    paths = [
        str(item.get("path"))
        for item in registry.get("non_canonical_dependencies", [])
        if isinstance(item, dict) and item.get("path")
    ]
    return _mentioned_paths(corpus, paths)


def _prefix_protected_paths(corpus: str) -> list[str]:
    tokens = sorted(set(re.findall(r"(?:AGENTS\.md|docs/[A-Za-z0-9_./-]+)", corpus, flags=re.IGNORECASE)))
    protected: list[str] = []
    for token in tokens:
        normalized = _normalize_path(token)
        lower = normalized.lower()
        if normalized == "AGENTS.md" or any(lower.startswith(prefix.lower()) for prefix in PROTECTED_PREFIXES):
            protected.append(normalized)
    return sorted(set(protected))


def _classification(
    protected_paths: list[str],
    parked_conflicts: list[str],
    non_canonical_dependencies: list[str],
) -> str:
    protected = bool(protected_paths)
    parked = bool(parked_conflicts)
    if protected and parked:
        return CLASS_AUTHORITY_REVIEW_REQUIRED
    if protected:
        return CLASS_PROTECTED_AUTHORITY
    if parked:
        return CLASS_PARKED_CONFLICT
    if non_canonical_dependencies:
        return CLASS_NON_CANONICAL_DEPENDENCY
    return CLASS_SAFE_WORKFLOW


def build_authority_bridge_review(
    repo_root: Path,
    bridge_goal: str,
    codex_report_summary: str,
    chatgpt_review_summary: str,
    claude_review_summary: str,
    reconciled_instruction: str,
    now: datetime | None = None,
) -> AuthorityBridgeReview:
    root = repo_root.resolve()
    moment = now or datetime.now(timezone.utc)
    registry = build_registry(root).to_dict()
    corpus = _text_pool(
        bridge_goal,
        codex_report_summary,
        chatgpt_review_summary,
        claude_review_summary,
        reconciled_instruction,
    )

    protected_paths = sorted(
        set(_mentioned_paths(corpus, _protected_paths_from_registry(registry)) + _prefix_protected_paths(corpus))
    )
    parked_conflicts = _parked_conflicts_from_registry(registry, corpus)
    non_canonical_dependencies = _non_canonical_dependencies_from_registry(registry, corpus)
    classification = _classification(protected_paths, parked_conflicts, non_canonical_dependencies)

    authority_review_required = classification in {
        CLASS_AUTHORITY_REVIEW_REQUIRED,
        CLASS_PROTECTED_AUTHORITY,
        CLASS_PARKED_CONFLICT,
    }
    yubikey_required = authority_review_required
    adb_required = authority_review_required
    continue_allowed = not authority_review_required

    blocked_reasons: list[str] = []
    if protected_paths:
        blocked_reasons.append("PROTECTED_AUTHORITY detected; bridge must stop before operator approval.")
    if parked_conflicts:
        blocked_reasons.append("PARKED_CONFLICT detected; human decision table review is required.")
    if non_canonical_dependencies:
        blocked_reasons.append("NON_CANONICAL_DEPENDENCY detected; do not treat dependency evidence as canonical authority.")
    if yubikey_required:
        blocked_reasons.append("YubiKey approval path is required before any continuation decision.")

    requested_action = f"Authority bridge review for {bridge_goal or 'AI_OS task'}"
    yubikey_evidence = None
    adb_plan = None
    if yubikey_required:
        yubikey_evidence = build_yubikey_approval_report(
            task_id="AUTHORITY_BRIDGE_REVIEW",
            decision=DECISION_HOLD_FOR_REVIEW,
            mode=MODE_DRY_RUN,
            requested_action=requested_action,
            protected_paths=protected_paths,
            now=moment,
        ).to_dict()
    if adb_required:
        adb_plan = plan_adb_escalation("approval_required").to_dict()

    return AuthorityBridgeReview(
        report_type=REPORT_TYPE,
        generated_at=moment.isoformat(),
        executable=False,
        bridge_goal=_summary(bridge_goal),
        codex_report_summary=_summary(codex_report_summary),
        chatgpt_review_summary=_summary(chatgpt_review_summary),
        claude_review_summary=_summary(claude_review_summary),
        reconciled_instruction=_summary(reconciled_instruction),
        authority_classification=classification,
        protected_paths_detected=protected_paths,
        parked_conflicts_detected=parked_conflicts,
        non_canonical_dependencies_detected=non_canonical_dependencies,
        yubikey_approval_required=yubikey_required,
        adb_escalation_required=adb_required,
        continue_allowed=continue_allowed,
        blocked_reasons=blocked_reasons,
        yubikey_approval_evidence=yubikey_evidence,
        adb_escalation_plan=adb_plan,
        safety=_safety(),
    )


def _resolve_output_path(repo_root: Path, generated_at: str) -> Path:
    root = repo_root.resolve()
    timestamp = _safe_timestamp(datetime.fromisoformat(generated_at))
    output = (root / OUTPUT_ROOT / f"authority_bridge_review_{timestamp}.json").resolve()
    allowed_root = (root / OUTPUT_ROOT).resolve()
    if not (output.parent == allowed_root and allowed_root in output.parents):
        raise ValueError("Authority bridge reviews must be written under Reports/operator_relief/bridge_reviews/.")
    return output


def write_authority_bridge_review(result: AuthorityBridgeReview, repo_root: Path) -> Path:
    path = _resolve_output_path(repo_root, result.generated_at)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate an authority-aware dual-review bridge report.")
    parser.add_argument("--goal", required=True)
    parser.add_argument("--codex-report-summary", default="")
    parser.add_argument("--chatgpt-review-summary", default="")
    parser.add_argument("--claude-review-summary", default="")
    parser.add_argument("--reconciled-instruction", required=True)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args(argv)

    result = build_authority_bridge_review(
        repo_root=Path.cwd(),
        bridge_goal=args.goal,
        codex_report_summary=args.codex_report_summary,
        chatgpt_review_summary=args.chatgpt_review_summary,
        claude_review_summary=args.claude_review_summary,
        reconciled_instruction=args.reconciled_instruction,
    )
    payload: dict[str, Any] = result.to_dict()
    if args.write_report:
        payload["written_file"] = _normalize_path(write_authority_bridge_review(result, Path.cwd()))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
