"""Generate one review-only human decision table for operator relief."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_TYPE = "operator_relief_human_decision_table_v1"
REGISTRY_PATH = Path("Reports/operator_relief/authority_registry/protected_authority_registry.json")
DECISION_PACKET_ROOT = Path("Reports/operator_relief/decision_packets")
DECISION_PACKET_INDEX_PATH = DECISION_PACKET_ROOT / "canonical_decision_packet_index.json"
AUDIT_ROOT = Path("Reports/operator_relief/audits")
OUTPUT_ROOT = Path("Reports/operator_relief/decision_table")
JSON_OUTPUT_PATH = OUTPUT_ROOT / "human_decision_table.json"
MD_OUTPUT_PATH = OUTPUT_ROOT / "human_decision_table.md"

PARKED_CONFLICT_GROUPS = {
    "worker branch and lane rules",
    "parallel codex workflow",
    "apply routing chain",
}
DO_NOT_TOUCH_GROUPS = {
    "file placement rules",
    "repo folder ownership map",
    "portal zone model",
}

STATUS_PROTECTED_HUMAN_REVIEW = "PROTECTED_HUMAN_REVIEW"
STATUS_NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"
STATUS_PARKED_CONFLICT = "PARKED_CONFLICT"
STATUS_DEPENDENCY_ONLY = "DEPENDENCY_ONLY"
STATUS_EVIDENCE_ONLY = "EVIDENCE_ONLY"
STATUS_CANONICALIZATION_CANDIDATE = "CANONICALIZATION_CANDIDATE"
STATUS_DO_NOT_TOUCH = "DO_NOT_TOUCH"

REVIEW_DECISION = "Review only; no APPLY packet, cleanup, commit, push, or merge is authorized."
DO_NOT_TOUCH_DECISION = "Do not touch unless a later protected-action packet is explicitly approved."
PARKED_DECISION = "Keep parked; human must resolve authority conflict before canonicalization."
DEPENDENCY_DECISION = "Keep as dependency-only evidence; do not canonicalize from this table."


@dataclass(frozen=True)
class HumanDecisionTableResult:
    report_type: str
    generated_at: str
    executable: bool
    source_reports: dict[str, Any]
    rows: list[dict[str, Any]]
    safe_cleanup_paths: list[str]
    apply_ready_paths: list[str]
    counts: dict[str, int]
    safety: dict[str, Any]
    recommended_next_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def _load_json(repo_root: Path, path: Path) -> dict[str, Any]:
    full_path = repo_root / path
    if not full_path.exists():
        return {}
    return json.loads(full_path.read_text(encoding="utf-8"))


def _latest_report(repo_root: Path, pattern: str) -> str | None:
    root = repo_root / AUDIT_ROOT
    if not root.exists():
        return None
    candidates = sorted(root.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    if not candidates:
        return None
    return _normalize_path(candidates[0].relative_to(repo_root))


def _unique(items: list[str]) -> list[str]:
    return sorted({item for item in items if item})


def _list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item]
    if isinstance(value, str) and value:
        return [value]
    return []


def _display_group(group_key: str) -> str:
    return " ".join(part.capitalize() for part in group_key.split())


def _row(
    rank: int,
    group: str,
    status: str,
    protected: bool,
    apply_ready: bool,
    canonical_candidate: str | None,
    duplicate_candidates: list[str],
    dependency_paths: list[str],
    recommended_decision: str,
    human_action_required: str,
    risk_level: str,
    source: str | None,
) -> dict[str, Any]:
    return {
        "Rank": rank,
        "Group": _display_group(group),
        "Status": status,
        "Protected": protected,
        "Apply Ready": apply_ready,
        "Canonical Candidate": canonical_candidate,
        "Duplicate Candidates": _unique(duplicate_candidates),
        "Dependency Paths": _unique(dependency_paths),
        "Recommended Decision": recommended_decision,
        "Human Action Required": human_action_required,
        "Risk Level": risk_level,
        "Source": source,
    }


def _workflow_rows(registry: dict[str, Any], start_rank: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rank = start_rank
    conflicts = registry.get("parked_workflow_authority_conflicts", [])
    for group_key in sorted(PARKED_CONFLICT_GROUPS):
        conflict = next(
            (item for item in conflicts if isinstance(item, dict) and item.get("group_key") == group_key),
            None,
        )
        if not conflict:
            continue
        rows.append(
            _row(
                rank=rank,
                group=group_key,
                status=STATUS_PARKED_CONFLICT,
                protected=False,
                apply_ready=False,
                canonical_candidate=conflict.get("likely_canonical_candidate"),
                duplicate_candidates=_list(conflict.get("duplicate_candidate")),
                dependency_paths=_list(conflict.get("paths"))
                + _list(conflict.get("dependency_paths")),
                recommended_decision=PARKED_DECISION,
                human_action_required="Human must choose what content survives before any later APPLY packet.",
                risk_level="HIGH",
                source=conflict.get("source_decision_diff_report"),
            )
        )
        rank += 1
    return rows


def _protected_rows(registry: dict[str, Any], start_rank: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rank = start_rank
    protected = registry.get("protected_authorities", [])
    for group_key in sorted(DO_NOT_TOUCH_GROUPS):
        authority = next(
            (item for item in protected if isinstance(item, dict) and item.get("group_key") == group_key),
            None,
        )
        if not authority:
            continue
        rows.append(
            _row(
                rank=rank,
                group=group_key,
                status=STATUS_DO_NOT_TOUCH,
                protected=True,
                apply_ready=False,
                canonical_candidate=None,
                duplicate_candidates=_list(authority.get("paths")),
                dependency_paths=[],
                recommended_decision=DO_NOT_TOUCH_DECISION,
                human_action_required="Human protected review is required before any file change.",
                risk_level="CRITICAL",
                source=authority.get("source_decision_packet"),
            )
        )
        rank += 1
    return rows


def _packet_rows(repo_root: Path, index: dict[str, Any], existing_groups: set[str], start_rank: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rank = start_rank
    for item in index.get("packets", []):
        if not isinstance(item, dict):
            continue
        group_key = str(item.get("group_key", ""))
        if not group_key or group_key in existing_groups:
            continue
        packet_file = str(item.get("packet_file", ""))
        packet_path = DECISION_PACKET_ROOT / packet_file
        packet = _load_json(repo_root, packet_path)
        protected = bool(item.get("protected_review_required")) or bool(packet.get("protected_review_required"))
        status = STATUS_PROTECTED_HUMAN_REVIEW if protected else STATUS_CANONICALIZATION_CANDIDATE
        rows.append(
            _row(
                rank=rank,
                group=group_key,
                status=status,
                protected=protected,
                apply_ready=False,
                canonical_candidate=packet.get("current_canonical_candidate"),
                duplicate_candidates=_list(packet.get("duplicate_candidates")) or _list(packet.get("paths")),
                dependency_paths=_list(packet.get("dependencies")),
                recommended_decision=REVIEW_DECISION,
                human_action_required="Human must review this packet and select a decision option.",
                risk_level="HIGH" if protected else "MEDIUM",
                source=_normalize_path(packet_path),
            )
        )
        rank += 1
    return rows


def _dependency_rows(registry: dict[str, Any], used_paths: set[str], start_rank: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rank = start_rank
    for item in registry.get("dependency_only_documents", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", ""))
        if not path or path in used_paths:
            continue
        used_paths.add(path)
        rows.append(
            _row(
                rank=rank,
                group=f"{item.get('source_group', 'dependency')} dependency",
                status=STATUS_DEPENDENCY_ONLY,
                protected=False,
                apply_ready=False,
                canonical_candidate=None,
                duplicate_candidates=[],
                dependency_paths=[path],
                recommended_decision=DEPENDENCY_DECISION,
                human_action_required="No immediate action; keep visible as dependency-only context.",
                risk_level="LOW",
                source=item.get("source_decision_diff_report"),
            )
        )
        rank += 1
    for item in registry.get("non_canonical_dependencies", []):
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", ""))
        if not path or path in used_paths:
            continue
        used_paths.add(path)
        rows.append(
            _row(
                rank=rank,
                group=f"{item.get('source_group', 'evidence')} evidence",
                status=STATUS_EVIDENCE_ONLY,
                protected=False,
                apply_ready=False,
                canonical_candidate=None,
                duplicate_candidates=[],
                dependency_paths=[path],
                recommended_decision="Keep as evidence-only; do not treat as workflow authority.",
                human_action_required="No immediate action; do not promote through this table.",
                risk_level="LOW",
                source=None,
            )
        )
        rank += 1
    return rows


def _counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "protected_count": sum(1 for row in rows if row["Protected"]),
        "parked_conflict_count": sum(1 for row in rows if row["Status"] == STATUS_PARKED_CONFLICT),
        "do_not_touch_count": sum(1 for row in rows if row["Status"] == STATUS_DO_NOT_TOUCH),
        "apply_ready_count": sum(1 for row in rows if row["Apply Ready"]),
        "row_count": len(rows),
    }


def build_human_decision_table(repo_root: Path) -> HumanDecisionTableResult:
    root = repo_root.resolve()
    registry = _load_json(root, REGISTRY_PATH)
    index = _load_json(root, DECISION_PACKET_INDEX_PATH)

    rows: list[dict[str, Any]] = []
    rows.extend(_workflow_rows(registry, 1))
    rows.extend(_protected_rows(registry, len(rows) + 1))
    existing_groups = {str(row["Group"]).lower() for row in rows}
    rows.extend(_packet_rows(root, index, existing_groups, len(rows) + 1))
    used_paths = {
        path
        for row in rows
        for path in row["Dependency Paths"] + row["Duplicate Candidates"]
        if isinstance(path, str)
    }
    rows.extend(_dependency_rows(registry, used_paths, len(rows) + 1))

    for rank, row in enumerate(rows, start=1):
        row["Rank"] = rank

    return HumanDecisionTableResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        source_reports={
            "protected_authority_registry": _normalize_path(REGISTRY_PATH),
            "canonical_authority_audit": _latest_report(root, "canonical_authority_audit_*.json"),
            "canonical_authority_triage": _latest_report(root, "canonical_authority_triage_*.json"),
            "canonical_decision_packet_index": _normalize_path(DECISION_PACKET_INDEX_PATH),
            "decision_diff_reports": registry.get("source_decision_diff_reports", []),
        },
        rows=rows,
        safe_cleanup_paths=[],
        apply_ready_paths=[],
        counts=_counts(rows),
        safety={
            "executable": False,
            "review_generation_only": True,
            "cleanup_approved": False,
            "apply_ready": False,
            "source_mutation": False,
            "commit_approved": False,
            "push_approved": False,
            "merge_approved": False,
        },
        recommended_next_action="Use this board as the operator review surface; generate no cleanup or APPLY packet until human decisions are recorded.",
    )


def _markdown_cell(value: Any) -> str:
    if isinstance(value, list):
        text = "<br>".join(str(item) for item in value) if value else ""
    elif value is None:
        text = ""
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>")


def render_markdown(result: HumanDecisionTableResult) -> str:
    lines = [
        "# Human Decision Table v1",
        "",
        f"Generated: {result.generated_at}",
        "",
        "Safety: executable=false; review generation only; no cleanup, apply packet, commit, push, or merge.",
        "",
        f"Protected count: {result.counts['protected_count']}",
        f"Parked conflict count: {result.counts['parked_conflict_count']}",
        f"DO_NOT_TOUCH count: {result.counts['do_not_touch_count']}",
        f"Apply ready count: {result.counts['apply_ready_count']}",
        "",
        "| Rank | Group | Status | Protected | Apply Ready | Canonical Candidate | Duplicate Candidates | Dependency Paths | Recommended Decision | Human Action Required | Risk Level |",
        "|---:|---|---|---|---|---|---|---|---|---|---|",
    ]
    columns = [
        "Rank",
        "Group",
        "Status",
        "Protected",
        "Apply Ready",
        "Canonical Candidate",
        "Duplicate Candidates",
        "Dependency Paths",
        "Recommended Decision",
        "Human Action Required",
        "Risk Level",
    ]
    for row in result.rows:
        lines.append("| " + " | ".join(_markdown_cell(row[column]) for column in columns) + " |")
    lines.extend(
        [
            "",
            "## Safe Next Action",
            "",
            result.recommended_next_action,
            "",
        ]
    )
    return "\n".join(lines)


def _resolve_output(repo_root: Path, path: Path) -> Path:
    root = repo_root.resolve()
    output = (root / path).resolve()
    allowed_root = (root / OUTPUT_ROOT).resolve()
    if not (output.parent == allowed_root and allowed_root in output.parents):
        raise ValueError("Human decision table reports must be written under Reports/operator_relief/decision_table/.")
    return output


def write_reports(result: HumanDecisionTableResult, repo_root: Path) -> list[Path]:
    json_path = _resolve_output(repo_root, JSON_OUTPUT_PATH)
    md_path = _resolve_output(repo_root, MD_OUTPUT_PATH)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(result.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    md_path.write_text(render_markdown(result), encoding="utf-8")
    return [json_path, md_path]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the operator-facing human decision table.")
    parser.add_argument("--write-report", action="store_true", help="Write JSON and Markdown decision table reports.")
    args = parser.parse_args(argv)

    result = build_human_decision_table(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_report:
        payload["written_files"] = [_normalize_path(path) for path in write_reports(result, Path.cwd())]
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
